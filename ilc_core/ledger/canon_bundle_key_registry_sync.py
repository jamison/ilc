"""
Channel-aware sync workflow for registry bundles.

Bridges the channel file (Phase 125) with fetch (Phase 124) into an
operator-friendly sync command.
"""

import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, List, Dict, Any
from urllib.parse import urlparse

from ilc_core.ledger.canon_bundle_key_registry_channel import (
    load_channel_file,
    _atomic_write,
)
from ilc_core.ledger.canon_bundle_key_registry_channel_signing import (
    verify_channel_file_signature,
)
from ilc_core.ledger.canon_bundle_key_registry_fetch import fetch_registry_bundle
from ilc_core.ledger.canon_bundle_key_registry_bundle import BUNDLE_DIR_NAME


def _now_iso8601() -> str:
    """Return current UTC time as strict ISO-8601 string."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _canonicalize_source(source: str) -> str:
    """Canonicalize source string for audit log."""
    parsed = urlparse(source)
    if parsed.scheme == "file":
        try:
            return str(Path(parsed.path).resolve())
        except OSError:
            # If path doesn't exist, just return as is (will fail later)
            return parsed.path
    if parsed.scheme == "":
        try:
            return str(Path(source).resolve())
        except OSError:
            return source
    return source


def _record_last_sync(
    channel_file: Path,
    channel_data: dict,
    channel: Optional[str],
    source: Optional[str],
    ok: bool,
    errors: list,
    warnings: list,
    source_attempts: Optional[List[Dict[str, Any]]] = None,
    selected_source_reason: Optional[str] = None,
    bundle_hash: Optional[str] = None,
    key_id: Optional[str] = None,
) -> None:
    """Best-effort write of last_sync metadata."""
    last_sync = {
        "channel": channel if channel is not None else "unknown",
        "source": source if source is not None else "unknown",
        "timestamp": _now_iso8601(),
        "bundle_hash": bundle_hash,
        "key_id": key_id,
        "ok": ok,
        "warnings": warnings,
        "errors": errors,
        "source_attempts": source_attempts if source_attempts is not None else [],
    }
    if selected_source_reason is not None:
        last_sync["selected_source_reason"] = selected_source_reason
    try:
        channel_data["last_sync"] = last_sync
        channel_data["updated_at"] = _now_iso8601()
        content = json.dumps(channel_data, indent=2, sort_keys=True)
        _atomic_write(channel_file, content)
    except OSError:
        return


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
    failover: bool = True,
    max_sources: Optional[int] = None,
    channel_key: Optional[bytes] = None,
    channel_sig_path: Optional[Path] = None,
    require_signed_channel: bool = False,
) -> dict:
    """
    Sync a channel's registry bundle with deterministic failover.
    
    Args:
        channel_file: Path to channel file.
        key: Registry bundle verification key bytes.
        dest_dir: Destination directory for installed bundle.
        channel: Channel name (default: use current_channel).
        source_index: Start index in sources list (default: 0).
        allow_network: Allow https:// sources.
        strict: Strict registry validation.
        force: Overwrite existing bundle.
        dry_run: Return plan without modifications.
        keep_temp: Keep temp directory on failure.
        timeout: Network timeout in seconds.
        failover: If True, attempt subsequent sources on failure.
        max_sources: Max number of sources to attempt.
        channel_key: Optional key to verify channel file signature.
        channel_sig_path: Optional path to channel signature file.
        require_signed_channel: If True, fail if channel signature invalid or missing.
    
    Returns:
        Dict with execution results and audit metadata.
    """
    warnings = []

    # Load channel file first so policy failures can still be audited in last_sync
    load_result = load_channel_file(channel_file)
    if not load_result["ok"]:
        return {"ok": False, "errors": [load_result["error"]], "warnings": warnings}

    channel_data = load_result["data"]
    channel_version = channel_data.get("channel_version", "v0.1")

    # Verify channel signature policy before source resolution/attempts
    audit_channel = channel if channel is not None else channel_data.get("current_channel")
    if channel_key:
        verify_result = verify_channel_file_signature(
            channel_file, channel_key, channel_sig_path
        )

        sig_missing = "channel_signature_missing" in verify_result.get("errors", [])

        if not verify_result["ok"]:
            if sig_missing and not require_signed_channel:
                warnings.append("channel_signature_missing_unenforced")
            else:
                policy_warnings = warnings + verify_result.get("warnings", [])
                _record_last_sync(
                    channel_file=channel_file,
                    channel_data=channel_data,
                    channel=audit_channel,
                    source=None,
                    ok=False,
                    errors=verify_result["errors"],
                    warnings=policy_warnings,
                    selected_source_reason="signature_policy_failed",
                )
                return {
                    "ok": False,
                    "errors": verify_result["errors"],
                    "warnings": policy_warnings,
                }
        else:
            # Valid signature
            warnings.extend(verify_result.get("warnings", []))

    elif require_signed_channel:
        # Required but no key provided to verify with
        _record_last_sync(
            channel_file=channel_file,
            channel_data=channel_data,
            channel=audit_channel,
            source=None,
            ok=False,
            errors=["channel_key_missing_for_required_signature"],
            warnings=warnings,
            selected_source_reason="signature_policy_failed",
        )
        return {
            "ok": False,
            "errors": ["channel_key_missing_for_required_signature"],
            "warnings": warnings,
        }

    # Resolve channel
    if channel is None:
        channel = channel_data.get("current_channel")
    
    if not channel:
        _record_last_sync(
            channel_file=channel_file,
            channel_data=channel_data,
            channel=channel,
            source=None,
            ok=False,
            errors=["channel_not_found"],
            warnings=warnings,
            selected_source_reason="window_exhausted" if failover else "no_failover",
        )
        return {"ok": False, "errors": ["channel_not_found"], "warnings": warnings}
    
    channels = channel_data.get("channels", [])
    if channel not in channels:
        err = f"channel_not_found:{channel}"
        _record_last_sync(
            channel_file=channel_file,
            channel_data=channel_data,
            channel=channel,
            source=None,
            ok=False,
            errors=[err],
            warnings=warnings,
            selected_source_reason="window_exhausted" if failover else "no_failover",
        )
        return {"ok": False, "errors": [err], "warnings": warnings}
    
    # Resolve sources
    sources_map = channel_data.get("sources")
    if sources_map is None:
        _record_last_sync(
            channel_file=channel_file,
            channel_data=channel_data,
            channel=channel,
            source=None,
            ok=False,
            errors=["sources_missing"],
            warnings=warnings,
            selected_source_reason="window_exhausted" if failover else "no_failover",
        )
        return {"ok": False, "errors": ["sources_missing"], "warnings": warnings}
    
    sources = sources_map.get(channel, [])
    if not sources:
        err = f"sources_missing:{channel}"
        _record_last_sync(
            channel_file=channel_file,
            channel_data=channel_data,
            channel=channel,
            source=None,
            ok=False,
            errors=[err],
            warnings=warnings,
            selected_source_reason="window_exhausted" if failover else "no_failover",
        )
        return {"ok": False, "errors": [err], "warnings": warnings}
    
    # Validate indices
    if source_index < 0 or source_index >= len(sources):
        _record_last_sync(
            channel_file=channel_file,
            channel_data=channel_data,
            channel=channel,
            source=None,
            ok=False,
            errors=["source_index_out_of_range"],
            warnings=warnings,
            selected_source_reason="window_exhausted" if failover else "no_failover",
        )
        return {"ok": False, "errors": ["source_index_out_of_range"], "warnings": warnings}
    
    if max_sources is not None and max_sources < 1:
        _record_last_sync(
            channel_file=channel_file,
            channel_data=channel_data,
            channel=channel,
            source=None,
            ok=False,
            errors=["max_sources_invalid"],
            warnings=warnings,
            selected_source_reason="window_exhausted" if failover else "no_failover",
        )
        return {"ok": False, "errors": ["max_sources_invalid"], "warnings": warnings}
    
    # Determine attempt window
    start = source_index
    if not failover:
        end = start + 1
    elif max_sources is not None:
        end = min(len(sources), start + max_sources)
    else:
        end = len(sources)
    
    window = sources[start:end]
    
    # Check dest exists
    dest_bundle = dest_dir / BUNDLE_DIR_NAME
    if dest_bundle.exists() and not force and not dry_run:
        selected = _canonicalize_source(window[0]) if window else None
        _record_last_sync(
            channel_file=channel_file,
            channel_data=channel_data,
            channel=channel,
            source=selected,
            ok=False,
            errors=["dest_exists"],
            warnings=warnings,
            selected_source_reason="window_exhausted" if failover else "no_failover",
        )
        return {"ok": False, "errors": ["dest_exists"], "warnings": warnings}
    
    if dry_run:
        return {
            "ok": True,
            "dry_run": True,
            "channel": channel,
            "sources_to_attempt": window,
            "dest": str(dest_dir),
            "channel_version": channel_version,
            "failover_enabled": failover,
            "actions": ["fetch", "verify", "install", "update_last_sync"],
            "errors": [],
            "warnings": warnings,
        }
    
    # Failover loop
    attempts: List[Dict[str, Any]] = []
    success_result = None
    selected_source = None
    selected_source_reason = None
    successful_source_index = None
    
    for idx_offset, source in enumerate(window):
        current_index = start + idx_offset
        canonical_source = _canonicalize_source(source)
        t0 = time.monotonic()
        
        # Check network gate
        parsed = urlparse(source)
        if parsed.scheme == "https" and not allow_network:
            res = {"ok": False, "errors": ["network_disabled"], "warnings": []}
        else:
            res = fetch_registry_bundle(
                source=source,
                key=key,
                dest_dir=dest_dir,
                force=force,
                allow_network=allow_network,
                timeout=timeout,
                keep_temp=keep_temp,
                strict=strict,
            )
        
        duration_ms = int((time.monotonic() - t0) * 1000)
        
        attempts.append({
            "index": current_index,
            "source": canonical_source,
            "ok": res.get("ok", False),
            "errors": res.get("errors", []),
            "warnings": res.get("warnings", []),
            "attempt_duration_ms": duration_ms,
        })
        
        if res.get("ok"):
            success_result = res
            selected_source = canonical_source
            successful_source_index = current_index
            if current_index == start:
                selected_source_reason = "no_failover" if not failover else "first_success"
            else:
                selected_source_reason = "failover_success"
            break
            
    # Determine overall status
    ok = success_result is not None
    
    if not ok:
        selected_source = attempts[-1]["source"] if attempts else None
        if not failover:
            selected_source_reason = "no_failover"
        else:
            selected_source_reason = "window_exhausted"
    
    # Aggregate errors/warnings for return
    final_errors = []
    final_warnings = list(warnings)
    
    if not ok:
        final_errors.append("sync_failed_all_sources")
        # Collect unique errors from attempts
        seen_errors = set()
        for attempt in attempts:
            for err in attempt["errors"]:
                if err not in seen_errors:
                    final_errors.append(err)
                    seen_errors.add(err)
    
    # Build and update last_sync
    _record_last_sync(
        channel_file=channel_file,
        channel_data=channel_data,
        channel=channel,
        source=selected_source,
        ok=ok,
        errors=final_errors,
        warnings=final_warnings,
        source_attempts=attempts,
        selected_source_reason=selected_source_reason,
        bundle_hash=success_result.get("registry_hash") if success_result else None,
        key_id=success_result.get("key_id") if success_result else None,
    )

    last_sync = channel_data.get("last_sync")
    
    result = {
        "ok": ok,
        "errors": final_errors,
        "warnings": final_warnings,
        "channel": channel,
        "source": selected_source,
        "source_index": start, # Requested index
        "attempted_sources": len(attempts),
        "failed_sources": len([a for a in attempts if not a["ok"]]),
        "successful_source_index": successful_source_index,
        "channel_version": channel_version,
        "last_sync": last_sync,
    }
    
    if ok and success_result:
        result["bundle_hash"] = success_result.get("registry_hash")
        result["key_id"] = success_result.get("key_id")
        result["installed_path"] = success_result.get("installed_to")
        # Merge warnings from successful fetch
        result["warnings"].extend(success_result.get("warnings", []))
    
    return result
