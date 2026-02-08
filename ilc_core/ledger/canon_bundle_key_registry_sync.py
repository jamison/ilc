"""
Channel-aware sync workflow for registry bundles.

Bridges the channel file (Phase 125) with fetch (Phase 124) into an
operator-friendly sync command.
"""

import json
import time
from datetime import datetime, timezone
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

from ilc_core.ledger.canon_bundle_key_registry_channel import (
    load_channel_file,
    _atomic_write,
)
from ilc_core.ledger.canon_bundle_key_registry_channel_signing import (
    verify_channel_file_signature,
)
from ilc_core.ledger.canon_bundle_key_registry_fetch import (
    fetch_registry_bundle,
    _canonicalize_source,
)
from ilc_core.ledger.canon_bundle_key_registry_bundle import BUNDLE_DIR_NAME


def _now_iso8601() -> str:
    """Return current UTC time as strict ISO-8601 string."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


@dataclass
class LastSyncRecord:
    channel: Optional[str] = None
    source: Optional[str] = None
    ok: bool = False
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    source_attempts: List[Dict[str, Any]] = field(default_factory=list)
    selected_source_reason: Optional[str] = None
    bundle_hash: Optional[str] = None
    key_id: Optional[str] = None


def _record_last_sync(
    channel_file: Path,
    channel_data: dict,
    record: LastSyncRecord,
) -> None:
    """Best-effort write of last_sync metadata."""
    last_sync = {
        "channel": record.channel if record.channel is not None else "unknown",
        "source": record.source if record.source is not None else "unknown",
        "timestamp": _now_iso8601(),
        "bundle_hash": record.bundle_hash,
        "key_id": record.key_id,
        "ok": record.ok,
        "warnings": record.warnings,
        "errors": record.errors,
        "source_attempts": record.source_attempts,
    }
    if record.selected_source_reason is not None:
        last_sync["selected_source_reason"] = record.selected_source_reason
    try:
        channel_data["last_sync"] = last_sync
        channel_data["updated_at"] = _now_iso8601()
        content = json.dumps(channel_data, indent=2, sort_keys=True)
        _atomic_write(channel_file, content)
    except OSError:
        return


def _validate_sync_policy(
    channel_file: Path,
    channel_key: Optional[bytes],
    channel_sig_path: Optional[Path],
    require_signed: bool,
    warnings: list,
) -> tuple[bool, list, list]:
    """Validate channel signature policy. Returns (ok, errors, warnings)."""
    if channel_key:
        verify_result = verify_channel_file_signature(
            channel_file, channel_key, channel_sig_path
        )
        sig_missing = "channel_signature_missing" in verify_result.get("errors", [])
        
        if not verify_result["ok"]:
            if sig_missing and not require_signed:
                warnings.append("channel_signature_missing_unenforced")
                return True, [], warnings
            
            return False, verify_result["errors"], warnings + verify_result.get("warnings", [])
        
        warnings.extend(verify_result.get("warnings", []))
        return True, [], warnings

    if require_signed:
        return False, ["channel_key_missing_for_required_signature"], warnings
        
    return True, [], warnings


def _resolve_sync_window(
    channel_data: dict,
    channel: str,
    source_index: int,
    max_sources: Optional[int],
    failover: bool,
) -> tuple[list, list]:
    """Resolve attempt window sources. Returns (window, errors)."""
    sources_map = channel_data.get("sources")
    if sources_map is None:
        return [], ["sources_missing"]
        
    sources = sources_map.get(channel, [])
    if not sources:
        return [], [f"sources_missing:{channel}"]
        
    if source_index < 0 or source_index >= len(sources):
        return [], ["source_index_out_of_range"]
        
    if max_sources is not None and max_sources < 1:
        return [], ["max_sources_invalid"]
        
    start = source_index
    if not failover:
        end = start + 1
    elif max_sources is not None:
        end = min(len(sources), start + max_sources)
    else:
        end = len(sources)
        
    return sources[start:end], []


@dataclass
class SyncContext:
    channel_file: Path
    key: bytes
    dest_dir: Path
    channel: Optional[str] = None
    source_index: int = 0
    allow_network: bool = False
    strict: bool = True
    force: bool = False
    dry_run: bool = False
    keep_temp: bool = False
    timeout: int = 20
    failover: bool = True
    max_sources: Optional[int] = None
    channel_key: Optional[bytes] = None
    channel_sig_path: Optional[Path] = None
    require_signed_channel: bool = False


def _attempt_sync_from_window(
    window: List[str],
    source_index: int,
    ctx: SyncContext,
) -> tuple[Optional[dict], List[Dict[str, Any]]]:
    """Attempt sync from a window of sources. Returns (success_result, attempts)."""
    attempts = []
    success_result = None
    
    for idx_offset, source in enumerate(window):
        current_index = source_index + idx_offset
        canonical_source = _canonicalize_source(source)
        t0 = time.monotonic()
        
        parsed = urlparse(source)
        if parsed.scheme == "https" and not ctx.allow_network:
            res = {"ok": False, "errors": ["network_disabled"], "warnings": []}
        else:
            res = fetch_registry_bundle(
                source=source,
                key=ctx.key,
                dest_dir=ctx.dest_dir,
                force=ctx.force,
                allow_network=ctx.allow_network,
                timeout=ctx.timeout,
                keep_temp=ctx.keep_temp,
                strict=ctx.strict,
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
            break
            
    return success_result, attempts


def _finalize_sync(
    ctx: SyncContext,
    channel_data: dict,
    channel: str,
    channel_version: str,
    success_result: Optional[dict],
    attempts: List[Dict[str, Any]],
    warnings: List[str],
) -> dict:
    """Finalize sync result, record metadata and return statistics."""
    # Determine overall status and selection
    ok = success_result is not None
    selected_source = None
    selected_source_reason = None
    successful_source_index = None
    
    if ok:
        for att in attempts:
            if att["ok"]:
                selected_source = att["source"]
                successful_source_index = att["index"]
                if att["index"] == ctx.source_index:
                    selected_source_reason = "no_failover" if not ctx.failover else "first_success"
                else:
                    selected_source_reason = "failover_success"
                break
    else:
        selected_source = attempts[-1]["source"] if attempts else None
        selected_source_reason = "window_exhausted" if ctx.failover else "no_failover"
    
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
                    
    # Record result
    record = LastSyncRecord(
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
    _record_last_sync(ctx.channel_file, channel_data, record)
    
    last_sync = channel_data.get("last_sync")
    
    result = {
        "ok": ok,
        "errors": final_errors,
        "warnings": final_warnings,
        "channel": channel,
        "source": selected_source,
        "source_index": ctx.source_index,
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


def sync_channel_registry(ctx: SyncContext) -> dict:
    """
    Sync a channel's registry bundle with deterministic failover.
    
    Args:
        ctx: SyncContext containing all parameters.
    
    Returns:
        Dict with execution results and audit metadata.
    """
    warnings = []
    
    # Load channel file
    load_result = load_channel_file(ctx.channel_file)
    if not load_result["ok"]:
        return {"ok": False, "errors": [load_result["error"]], "warnings": warnings}
    
    channel_data = load_result["data"]
    channel_version = channel_data.get("channel_version", "v0.1")
    
    # Resolve channel audit name (for logging even if validation fails)
    audit_channel = ctx.channel if ctx.channel is not None else channel_data.get("current_channel")
    
    # Verify signature policy
    pol_ok, pol_errors, pol_warnings = _validate_sync_policy(
        ctx.channel_file, ctx.channel_key, ctx.channel_sig_path, ctx.require_signed_channel, warnings
    )
    warnings = pol_warnings
    
    if not pol_ok:
        _record_last_sync(
            ctx.channel_file, channel_data,
            LastSyncRecord(
                channel=audit_channel,
                ok=False,
                errors=pol_errors,
                warnings=warnings,
                selected_source_reason="signature_policy_failed"
            )
        )
        return {"ok": False, "errors": pol_errors, "warnings": warnings}
    
    # Resolve channel
    channel = ctx.channel
    if channel is None:
        channel = channel_data.get("current_channel")
        
    channels = channel_data.get("channels", [])
    
    if not channel:
        err = "channel_not_found"
    elif channel not in channels:
        err = f"channel_not_found:{channel}"
    else:
        err = None
    
    if err:
        _record_last_sync(
            ctx.channel_file, channel_data,
             LastSyncRecord(
                channel=channel,
                ok=False,
                errors=[err],
                warnings=warnings,
                selected_source_reason="window_exhausted" if ctx.failover else "no_failover"
            )
        )
        return {"ok": False, "errors": [err], "warnings": warnings}
        
    # Resolve sources window
    window, win_errors = _resolve_sync_window(
        channel_data, channel, ctx.source_index, ctx.max_sources, ctx.failover
    )
    if win_errors:
        _record_last_sync(
            ctx.channel_file, channel_data,
             LastSyncRecord(
                channel=channel,
                ok=False,
                errors=win_errors,
                warnings=warnings,
                selected_source_reason="window_exhausted" if ctx.failover else "no_failover"
            )
        )
        return {"ok": False, "errors": win_errors, "warnings": warnings}
        
    # Check dest exists
    dest_bundle = ctx.dest_dir / BUNDLE_DIR_NAME
    if dest_bundle.exists() and not ctx.force and not ctx.dry_run:
        selected = _canonicalize_source(window[0]) if window else None
        _record_last_sync(
            ctx.channel_file, channel_data,
             LastSyncRecord(
                channel=channel,
                source=selected,
                ok=False,
                errors=["dest_exists"],
                warnings=warnings,
                selected_source_reason="window_exhausted" if ctx.failover else "no_failover"
            )
        )
        return {"ok": False, "errors": ["dest_exists"], "warnings": warnings}
        
    if ctx.dry_run:
        return {
            "ok": True,
            "dry_run": True,
            "channel": channel,
            "sources_to_attempt": window,
            "dest": str(ctx.dest_dir),
            "channel_version": channel_version,
            "failover_enabled": ctx.failover,
            "actions": ["fetch", "verify", "install", "update_last_sync"],
            "errors": [],
            "warnings": warnings,
        }
        
    # Attempt sync from window
    success_result, attempts = _attempt_sync_from_window(window, ctx.source_index, ctx)
            
    return _finalize_sync(
        ctx, channel_data, channel, channel_version, success_result, attempts, warnings
    )
