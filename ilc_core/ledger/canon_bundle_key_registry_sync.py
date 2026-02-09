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
    validate_channel_file,
    _atomic_write,
)
from ilc_core.ledger.canon_bundle_key_registry_channel_signing import (
    verify_channel_file_signature,
)
from ilc_core.ledger.canon_bundle_key_registry_fetch import (
    fetch_registry_bundle,
    _canonicalize_source,
)
from ilc_core.ledger.canon_bundle_key_registry_sync_state import (
    load_sync_state,
    write_sync_state,
    evaluate_channel_freshness,
    ChannelFreshnessState,
    file_lock,
)
from ilc_core.ledger.canon_bundle_key_registry_bundle import (
    BUNDLE_DIR_NAME,
    verify_registry_bundle,
)


def _now_iso8601() -> str:
    """Return current UTC time as strict ISO-8601 string."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


@dataclass(frozen=True)
class VersionPolicyDecision:
    ok: bool
    policy: str
    errors: List[str]
    warnings: List[str]


def evaluate_channel_version_policy(
    version: Optional[str],
    *,
    prod: bool,
    allow_v03: bool,
    allow_legacy: bool,
    force: bool,
) -> VersionPolicyDecision:
    """
    Evaluate channel version against environment policy.
    
    Returns deterministic policy decision.
    """
    if version is None:
        return VersionPolicyDecision(False, "rejected", ["channel_version_missing"], [])

    if not isinstance(version, str):
        return VersionPolicyDecision(False, "rejected", ["channel_version_invalid"], [])

    version = version.strip()
    if not version:
        return VersionPolicyDecision(False, "rejected", ["channel_version_missing"], [])
        
    if version not in {"v0.4", "v0.3", "v0.2", "v0.1"}:
        return VersionPolicyDecision(False, "rejected", ["channel_version_invalid"], [])
        
    if version == "v0.4":
        return VersionPolicyDecision(True, "current", [], [])
        
    if version == "v0.3":
        if prod:
             # In prod, we reject v0.3 unless specific future break-glass is added.
             # For now, strict rejection.
             if allow_v03: # If user tries to override in prod
                 if not force:
                     return VersionPolicyDecision(False, "rejected", ["rollback_override_requires_force_in_prod"], [])
                 # Even with force, is it allowed? "channel_version_breakglass_forbidden_in_prod"
                 return VersionPolicyDecision(False, "rejected", ["channel_version_breakglass_forbidden_in_prod"], [])
             return VersionPolicyDecision(False, "rejected", ["channel_version_unsupported_in_prod"], [])
             
        if not allow_v03:
            return VersionPolicyDecision(False, "rejected", ["channel_version_legacy_not_allowed"], [])
            
        return VersionPolicyDecision(True, "compat_v03", [], ["channel_version_v03_compat_mode"])
        
    # v0.2 / v0.1
    if prod:
        return VersionPolicyDecision(False, "rejected", ["channel_version_breakglass_forbidden_in_prod"], [])
        
    if not allow_legacy:
        return VersionPolicyDecision(False, "rejected", ["channel_version_legacy_not_allowed"], [])
        
    return VersionPolicyDecision(True, "legacy_breakglass", [], ["channel_version_legacy_breakglass_used"])



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
    record: LastSyncRecord,
) -> dict:
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
        sidecar = channel_file.with_suffix(channel_file.suffix + ".last_sync.json")
        content = json.dumps(last_sync, indent=2, sort_keys=True)
        _atomic_write(sidecar, content)
    except OSError:
        pass
    return last_sync


def _fail_with_last_sync(
    ctx: "SyncContext",
    channel: Optional[str],
    errors: List[str],
    warnings: List[str],
    selected_source_reason: str,
    channel_version: Optional[str] = None,
    channel_version_policy: Optional[str] = None,
    source: Optional[str] = None,
) -> dict:
    """Create standardized sync failure result with sidecar last_sync."""
    last_sync = _record_last_sync(
        ctx.channel_file,
        LastSyncRecord(
            channel=channel,
            source=source,
            ok=False,
            errors=list(errors),
            warnings=list(warnings),
            selected_source_reason=selected_source_reason,
        ),
    )
    res = {
        "ok": False,
        "errors": list(errors),
        "warnings": list(warnings),
        "last_sync": last_sync,
    }
    if channel_version is not None:
        res["channel_version"] = channel_version
        
        if channel_version_policy is None:
            decision = evaluate_channel_version_policy(
                channel_version,
                prod=ctx.prod,
                allow_v03=ctx.allow_legacy_channel_v03,
                allow_legacy=ctx.allow_legacy_channel_v02_v01,
                force=ctx.force,
            )
            channel_version_policy = decision.policy

    if channel_version_policy is not None:
        res["channel_version_policy"] = channel_version_policy
        # Heuristic for override usage in failure/early-exit path
        if channel_version_policy in ("compat_v03", "legacy_breakglass"):
            res["channel_version_override_used"] = True
        else:
            res["channel_version_override_used"] = False
        
    return res


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
    allow_channel_rollback: bool = False
    sync_state_file: Optional[Path] = None
    prod: bool = False
    allow_legacy_channel_v03: bool = False
    allow_legacy_channel_v02_v01: bool = False



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
    channel: str,
    channel_version: str,
    success_result: Optional[dict],
    attempts: List[Dict[str, Any]],
    warnings: List[str],
    freshness_result: Optional[dict] = None,
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
    last_sync = _record_last_sync(ctx.channel_file, record)
    
    channel_version_policy = "current"
    channel_version_override_used = False
    
    # We need to re-evaluate the policy to get the correct classification
    # This is slightly redundant but ensures consistency without passing extra args
    # through all call layers.
    pol_decision = evaluate_channel_version_policy(
        channel_version,
        prod=ctx.prod,
        allow_v03=ctx.allow_legacy_channel_v03,
        allow_legacy=ctx.allow_legacy_channel_v02_v01,
        force=ctx.force,
    )
    # If fetch succeeded, the policy must have passed or been overridden
    channel_version_policy = pol_decision.policy
    
    # Heuristic for override usage: if policy is compatible/legacy and not current v0.4
    if channel_version_policy in ("compat_v03", "legacy_breakglass"):
        channel_version_override_used = True

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
        "channel_version_policy": channel_version_policy,
        "channel_version_override_used": channel_version_override_used,
        "last_sync": last_sync,
    }
    
    if freshness_result:
        result.update(freshness_result)
    
    if ok and success_result:
        result["bundle_hash"] = success_result.get("registry_hash")
        result["key_id"] = success_result.get("key_id")
        result["installed_path"] = success_result.get("installed_to")
        # Merge warnings from successful fetch
        result["warnings"].extend(success_result.get("warnings", []))
        
    return result




def _do_freshness_check(
    ctx: SyncContext,
    channel_data: dict,
    current_state: Optional[ChannelFreshnessState],
    warnings: list,
) -> tuple[Optional[dict], dict]:
    """Execute core freshness logic given loaded state."""
    freshness_result = {
        "rollback_check_applied": False,
        "freshness_decision": None,
        "rollback_override": False,
        "seen_seq": None,
        "seen_hash": None,
    }
    
    channel_version = channel_data.get("channel_version", "v0.1")
    
    if channel_version == "v0.3":
        warnings.append("channel_version_v03_no_rollback_protection")
        return None, freshness_result
        
    if channel_version != "v0.4":
        return None, freshness_result

    # v0.4 logic
    curr_seq = channel_data.get("channel_seq")
    if not isinstance(curr_seq, int):
        return None, freshness_result
        
    from ilc_core.ledger.canon_bundle_key_registry_channel_signing import canonical_channel_bytes
    import hashlib
    curr_bytes = canonical_channel_bytes(ctx.channel_file)
    curr_hash = hashlib.sha256(curr_bytes).hexdigest()
    
    seen_seq = current_state.seen_seq if current_state else None
    seen_hash = current_state.seen_hash if current_state else None
    
    freshness_result["seen_seq"] = seen_seq
    freshness_result["seen_hash"] = seen_hash
    freshness_result["rollback_check_applied"] = True

    is_fresh, code = evaluate_channel_freshness(seen_seq, seen_hash, curr_seq, curr_hash)
    freshness_result["freshness_decision"] = code
    
    if is_fresh:
        # Update state if not dry_run
        if not ctx.dry_run:
            new_state = ChannelFreshnessState(
                seen_seq=curr_seq,
                seen_hash=curr_hash,
                updated_at=_now_iso8601(),
            )
            # We need to signal that state should be updated.
            # But we are inside a function that doesn't have the file path or lock context effectively?
            # Actually, `_check_channel_freshness` passed `current_state`.
            # We need to return the NEW state to be written, or write it here?
            # We can't write it here easily without the path.
            # Let's return the new state object to be written by the caller.
            freshness_result["_new_state"] = new_state
        return None, freshness_result

    # Not fresh - handle failure/override
    if ctx.allow_channel_rollback:
        if ctx.prod and not ctx.force:
            err = "rollback_override_requires_force_in_prod"
            res = {"ok": False, "errors": [err], "warnings": list(warnings)}
            res.update(freshness_result)
            return res, freshness_result
        else:
            warnings.append("channel_rollback_override_used")
            freshness_result["rollback_override"] = True
            # Even if override, we should update state to the new (older) sequence so we don't warn again?
            # Yes, standard memory behavior: accept current state as new truth if override used.
            if not ctx.dry_run:
                new_state = ChannelFreshnessState(
                    seen_seq=curr_seq,
                    seen_hash=curr_hash,
                    updated_at=_now_iso8601(),
                )
                freshness_result["_new_state"] = new_state
            return None, freshness_result
    else:
        res = {"ok": False, "errors": [code], "warnings": list(warnings)}
        res.update(freshness_result)
        return res, freshness_result


def _check_channel_freshness(
    ctx: SyncContext,
    channel_data: dict,
    warnings: list,
) -> tuple[Optional[dict], Optional[dict]]:
    """
    Check channel freshness against local state.
    Returns (error_result, freshness_result).
    """
    sync_state_path = ctx.sync_state_file
    if sync_state_path is None:
        sync_state_path = ctx.channel_file.with_suffix(ctx.channel_file.suffix + ".sync_state.json")
    
    # Default empty result if we crash early
    freshness_result = {} 

    try:
        with file_lock(sync_state_path):
            current_state = load_sync_state(sync_state_path)
            
            err, freshness_result = _do_freshness_check(ctx, channel_data, current_state, warnings)
            
            if err:
                return err, freshness_result

            if (
                ctx.prod
                and channel_data.get("channel_version") == "v0.4"
                and not freshness_result.get("rollback_check_applied")
            ):
                return {
                    "ok": False,
                    "errors": ["rollback_check_not_applied"],
                    "warnings": list(warnings),
                }, freshness_result
            
            # Check if we need to write state
            new_state = freshness_result.pop("_new_state", None)
            if new_state:
                write_sync_state(sync_state_path, new_state)
                
    except Exception as e:
        if ctx.prod:
            return {"ok": False, "errors": [f"sync_state_error:{e}"], "warnings": list(warnings)}, freshness_result
        warnings.append(f"sync_state_error_ignored_nonprod:{e}")

    return None, freshness_result


def _prepare_sync_channel(
    ctx: SyncContext,
    channel_data: dict,
    warnings: List[str],
) -> tuple[Optional[dict], Optional[dict], List[str], Optional[str], Optional[str]]:
    """
    Validate channel schema/policy and return normalized sync inputs.
    Returns (error_result, channel_data, warnings, channel_version, audit_channel).
    """
    val_result = validate_channel_file(ctx.channel_file)
    audit_channel = ctx.channel if ctx.channel is not None else channel_data.get("current_channel")
    if not val_result["ok"]:
        errors = list(val_result.get("errors", []))
        return (
            _fail_with_last_sync(
                ctx,
                audit_channel,
                errors,
                warnings,
                selected_source_reason="channel_validation_failed",
            ),
            None,
            warnings,
            None,
            None,
        )

    channel_data = val_result["data"]
    warnings.extend(val_result.get("warnings", []))
    channel_version = channel_data.get("channel_version", "v0.1")

    # Evaluate version policy (Phase 132)
    decision = evaluate_channel_version_policy(
        channel_version,
        prod=ctx.prod,
        allow_v03=ctx.allow_legacy_channel_v03,
        allow_legacy=ctx.allow_legacy_channel_v02_v01,
        force=ctx.force,
    )
    
    if not decision.ok:
        return (
            _fail_with_last_sync(
                ctx,
                audit_channel,
                decision.errors,
                warnings + decision.warnings,
                selected_source_reason="channel_version_policy_failed",
                channel_version=channel_version,
                channel_version_policy=decision.policy,
            ),
            None,
            warnings,
            None,
            None,
        )
    
    warnings.extend(decision.warnings)

    require_signed = ctx.require_signed_channel or ctx.prod
    pol_ok, pol_errors, pol_warnings = _validate_sync_policy(
        ctx.channel_file, ctx.channel_key, ctx.channel_sig_path, require_signed, warnings
    )
    warnings = pol_warnings
    if not pol_ok:
        return (
            _fail_with_last_sync(
                ctx,
                audit_channel,
                pol_errors,
                warnings,
                selected_source_reason="signature_policy_failed",
                channel_version=channel_version,
            ),
            None,
            warnings,
            None,
            None,
        )

    return None, channel_data, warnings, channel_version, audit_channel



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
    prep_err, channel_data, warnings, channel_version, audit_channel = _prepare_sync_channel(
        ctx, channel_data, warnings
    )
    if prep_err:
        return prep_err
    
    # Freshness Check (Phase 131)
    fresh_err, freshness_result = _check_channel_freshness(ctx, channel_data, warnings)
    if fresh_err:
        err_result = _fail_with_last_sync(
            ctx,
            audit_channel,
            fresh_err.get("errors", []),
            fresh_err.get("warnings", warnings),
            selected_source_reason="freshness_check_failed",
        )
        for field in (
            "rollback_check_applied",
            "freshness_decision",
            "rollback_override",
            "seen_seq",
            "seen_hash",
        ):
            if field in fresh_err:
                err_result[field] = fresh_err[field]
        return err_result

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
        return _fail_with_last_sync(
            ctx,
            channel,
            [err],
            warnings,
            selected_source_reason="window_exhausted" if ctx.failover else "no_failover",
        )
        
    # Resolve sources window
    window, win_errors = _resolve_sync_window(
        channel_data, channel, ctx.source_index, ctx.max_sources, ctx.failover
    )
    if win_errors:
        return _fail_with_last_sync(
            ctx,
            channel,
            win_errors,
            warnings,
            selected_source_reason="window_exhausted" if ctx.failover else "no_failover",
            channel_version=channel_version,
        )
        
    # Check dest exists
    dest_bundle = ctx.dest_dir / BUNDLE_DIR_NAME
    if dest_bundle.exists() and not ctx.force and not ctx.dry_run:
        # Idempotency check: if channel is fresh (or legacy) and bundle is valid, treat as success
        is_fresh = freshness_result.get("freshness_decision") is None
        
        if is_fresh:
            verify = verify_registry_bundle(dest_bundle, ctx.key, strict=ctx.strict)
            if verify["ok"]:
                # Idempotent success
                warnings.extend(verify.get("warnings", []))
                success_result = {
                    "ok": True,
                    "errors": [],
                    "warnings": warnings,
                    "bundle_dir": str(dest_bundle),
                    "installed_to": str(ctx.dest_dir),
                    "registry_hash": verify.get("registry_hash"),
                    "key_id": verify.get("key_id"),
                }
                # No new fetch attempts made
                return _finalize_sync(
                    ctx, channel, channel_version, success_result, [], warnings, freshness_result
                )

        selected = _canonicalize_source(window[0]) if window else None
        return _fail_with_last_sync(
            ctx,
            channel,
            ["dest_exists"],
            warnings,
            selected_source_reason="window_exhausted" if ctx.failover else "no_failover",
            source=selected,
            channel_version=channel_version,
        )
        
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
        ctx, channel, channel_version, success_result, attempts, warnings, freshness_result
    )
