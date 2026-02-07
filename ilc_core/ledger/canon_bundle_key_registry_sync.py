"""
Channel-aware sync workflow for registry bundles.

Bridges the channel file (Phase 125) with fetch (Phase 124) into an
operator-friendly sync command.
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

import os

from ilc_core.ledger.canon_bundle_key_registry_channel import (
    validate_channel_file,
    _atomic_write,
)
from ilc_core.ledger.canon_bundle_key_registry_fetch import fetch_registry_bundle
from ilc_core.ledger.canon_bundle_key_registry_bundle import BUNDLE_DIR_NAME


def _now_iso8601() -> str:
    """Return current UTC time as strict ISO-8601 string."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sync_channel_registry(
    channel_file: Path,
    key: bytes,
    dest_dir: Path,
    channel: Optional[str] = None,
    source_index: int = 0,
    allow_network: bool = False,
    strict: bool = True,
    force: bool = False,
    dry_run: bool = False,
    keep_temp: bool = False,
    timeout: int = 20,
) -> dict:
    """
    Sync a channel's registry bundle.
    
    Args:
        channel_file: Path to channel file.
        key: Verification key bytes.
        dest_dir: Destination directory for installed bundle.
        channel: Channel name (default: use current_channel).
        source_index: Index into sources list (default: 0).
        allow_network: Allow https:// sources.
        strict: Strict registry validation.
        force: Overwrite existing bundle.
        dry_run: Return plan without modifications.
        keep_temp: Keep temp directory on failure.
        timeout: Network timeout in seconds.
    
    Returns:
        Dict with {ok, errors, warnings, channel, source, bundle_hash, ...}.
    """
    errors = []
    warnings = []
    
    # Load + validate channel file
    validate_result = validate_channel_file(channel_file)
    if not validate_result["ok"]:
        return {"ok": False, "errors": validate_result["errors"], "warnings": []}
    
    channel_data = validate_result["data"]
    warnings.extend(validate_result.get("warnings", []))
    channel_version = channel_data.get("channel_version", "v0.1")
    
    # Resolve channel
    if channel is None:
        channel = channel_data.get("current_channel")
    
    if not channel:
        return {"ok": False, "errors": ["channel_not_found"], "warnings": warnings}
    
    channels = channel_data.get("channels", [])
    if channel not in channels:
        _record_last_sync(
            channel_file, channel_data, channel, None,
            errors=[f"channel_not_found:{channel}"],
            warnings=warnings,
        )
        return {"ok": False, "errors": [f"channel_not_found:{channel}"], "warnings": warnings}
    
    # Resolve sources
    sources_map = channel_data.get("sources")
    if sources_map is None:
        _record_last_sync(
            channel_file, channel_data, channel, None,
            errors=["sources_missing"],
            warnings=warnings,
        )
        return {"ok": False, "errors": ["sources_missing"], "warnings": warnings}
    
    sources = sources_map.get(channel, [])
    if not sources:
        _record_last_sync(
            channel_file, channel_data, channel, None,
            errors=[f"sources_missing:{channel}"],
            warnings=warnings,
        )
        return {"ok": False, "errors": [f"sources_missing:{channel}"], "warnings": warnings}
    
    if source_index < 0 or source_index >= len(sources):
        _record_last_sync(
            channel_file, channel_data, channel, None,
            errors=["source_index_out_of_range"],
            warnings=warnings,
        )
        return {"ok": False, "errors": ["source_index_out_of_range"], "warnings": warnings}
    
    source = sources[source_index]
    
    # Check network gate
    parsed = urlparse(source)
    if parsed.scheme == "https" and not allow_network:
        _record_last_sync(
            channel_file, channel_data, channel, source,
            errors=["network_disabled"],
            warnings=warnings,
        )
        return {"ok": False, "errors": ["network_disabled"], "warnings": warnings}

    # Check dest exists
    dest_bundle = dest_dir / BUNDLE_DIR_NAME
    if dest_bundle.exists() and not force and not dry_run:
        _record_last_sync(
            channel_file, channel_data, channel, source,
            errors=["dest_exists"],
            warnings=warnings,
        )
        return {"ok": False, "errors": ["dest_exists"], "warnings": warnings}

    # Check dest writable (non-dry-run only)
    if not dry_run:
        if dest_dir.exists():
            if not os.access(dest_dir, os.W_OK):
                _record_last_sync(
                    channel_file, channel_data, channel, source,
                    errors=["dest_not_writable"],
                    warnings=warnings,
                )
                return {"ok": False, "errors": ["dest_not_writable"], "warnings": warnings}
        else:
            if not os.access(dest_dir.parent, os.W_OK):
                _record_last_sync(
                    channel_file, channel_data, channel, source,
                    errors=["dest_not_writable"],
                    warnings=warnings,
                )
                return {"ok": False, "errors": ["dest_not_writable"], "warnings": warnings}
    
    # Dry run - return plan
    if dry_run:
        return {
            "ok": True,
            "dry_run": True,
            "channel": channel,
            "source": source,
            "source_index": source_index,
            "dest": str(dest_dir),
            "channel_version": channel_version,
            "actions": ["fetch", "verify", "install", "update_last_sync"],
            "errors": [],
            "warnings": warnings,
        }
    
    # Perform fetch
    fetch_result = fetch_registry_bundle(
        source=source,
        key=key,
        dest_dir=dest_dir,
        force=force,
        allow_network=allow_network,
        timeout=timeout,
        keep_temp=keep_temp,
        strict=strict,
    )
    
    # Build/update last_sync
    _record_last_sync(
        channel_file,
        channel_data,
        channel,
        source,
        errors=fetch_result.get("errors", []),
        warnings=fetch_result.get("warnings", []),
        ok=fetch_result.get("ok", False),
        bundle_hash=fetch_result.get("registry_hash"),
        key_id=fetch_result.get("key_id"),
    )
    
    if not fetch_result.get("ok"):
        return {
            "ok": False,
            "errors": fetch_result.get("errors", []) + errors,
            "warnings": fetch_result.get("warnings", []) + warnings,
            "channel": channel,
            "source": source,
            "source_index": source_index,
            "channel_version": channel_version,
        }
    
    return {
        "ok": True,
        "errors": errors,
        "warnings": fetch_result.get("warnings", []) + warnings,
        "channel": channel,
        "source": source,
        "source_index": source_index,
        "channel_version": channel_version,
        "bundle_hash": fetch_result.get("registry_hash"),
        "key_id": fetch_result.get("key_id"),
        "installed_path": str(dest_bundle),
    }


def _record_last_sync(
    channel_file: Path,
    channel_data: dict,
    channel: Optional[str],
    source: Optional[str],
    errors: list,
    warnings: list,
    ok: bool = False,
    bundle_hash: Optional[str] = None,
    key_id: Optional[str] = None,
) -> None:
    """Write last_sync into channel file (best-effort)."""
    last_sync = {
        "channel": channel or "unknown",
        "source": source or "unknown",
        "timestamp": _now_iso8601(),
        "ok": ok,
        "warnings": warnings,
        "errors": errors,
    }
    if bundle_hash is not None:
        last_sync["bundle_hash"] = bundle_hash
    if key_id is not None:
        last_sync["key_id"] = key_id
    try:
        channel_data["last_sync"] = last_sync
        channel_data["updated_at"] = _now_iso8601()
        content = json.dumps(channel_data, indent=2, sort_keys=True)
        _atomic_write(channel_file, content)
    except OSError:
        return
