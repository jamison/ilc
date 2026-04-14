"""
Promotion workflow for registry bundles between channels.

Enables controlled rollout: experimental -> test -> main
"""

import json
import os
import re
import shutil
from pathlib import Path
from typing import Optional

from ilc_core.ledger.canon_bundle_key_registry_bundle import (
    verify_registry_bundle,
    BUNDLE_DIR_NAME,
)
from ilc_core.ledger.canon_bundle_key_registry_channel import (
    load_channel_file,
    _atomic_write,
    ALLOWED_FIELDS as CHANNEL_ALLOWED_FIELDS,
)


ALLOWED_FIELDS = CHANNEL_ALLOWED_FIELDS | {"last_promotion", "channel_order"}
STRICT_ISO8601_TZ_PATTERN = r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})$"


def _resolve_promotion_timestamp(channel_data: dict, timestamp: str | None) -> str:
    if timestamp is not None:
        if not isinstance(timestamp, str) or not re.match(STRICT_ISO8601_TZ_PATTERN, timestamp):
            raise ValueError("invalid_promotion_timestamp")
        return timestamp

    updated_at = channel_data.get("updated_at")
    if isinstance(updated_at, str):
        if not re.match(STRICT_ISO8601_TZ_PATTERN, updated_at):
            raise ValueError("invalid_updated_at")
        return updated_at

    return "1970-01-01T00:00:00Z"


def _validate_promotion_inputs(
    src_dir: Path,
    dest_dir: Path,
    channel_data: dict,
    src_channel: str,
    dest_channel: str,
    force: bool
) -> tuple[list, list]:
    """Validate promotion inputs and permissions."""
    errors = []
    warnings = []
    
    # Check same channel
    if src_channel == dest_channel:
        if not force:
            errors.append("channel_same_as_source")
        else:
            warnings.append("channel_same_as_source_forced")
            
    channels = channel_data.get("channels", [])
    if src_channel not in channels:
        errors.append(f"channel_not_found:{src_channel}")
        
    if dest_channel not in channels:
        if not force:
            errors.append(f"channel_not_found:{dest_channel}")
        else:
            warnings.append("channel_added_by_force")
            
    # Check order
    channel_order = channel_data.get("channel_order")
    if channel_order:
        if src_channel not in channel_order or dest_channel not in channel_order:
            errors.append("channel_order_incomplete")
        else:
            src_idx = channel_order.index(src_channel)
            dest_idx = channel_order.index(dest_channel)
            if dest_idx < src_idx:
                errors.append("channel_order_violation")
    else:
        warnings.append("channel_order_missing")
        
    # Check paths
    if not src_dir.exists() or not os.access(src_dir, os.R_OK):
        errors.append("src_not_readable")
        
    if dest_dir.exists():
        if not os.access(dest_dir, os.W_OK):
             errors.append("dest_not_writable")
    elif not os.access(dest_dir.parent, os.W_OK):
         errors.append("dest_not_writable")
         
    return errors, warnings


def _perform_promotion(src_bundle: Path, dest_dir: Path) -> dict:
    """Perform atomic copy of bundle."""
    try:
        dest_bundle = dest_dir / BUNDLE_DIR_NAME
        dest_dir.mkdir(parents=True, exist_ok=True)
        
        tmp_bundle = dest_dir / (BUNDLE_DIR_NAME + ".tmp")
        if tmp_bundle.exists():
            shutil.rmtree(tmp_bundle)
        shutil.copytree(src_bundle, tmp_bundle)
        
        if dest_bundle.exists():
            shutil.rmtree(dest_bundle)
        tmp_bundle.rename(dest_bundle)
        
        return {"ok": True, "dest_bundle": dest_bundle}
    except OSError as e:
        return {"ok": False, "error": f"promotion_failed:{e}"}


def _update_channel_after_promotion(
    channel_file: Path,
    channel_data: dict,
    last_promotion: dict,
    dest_channel: str,
    switch: bool,
    updated_at: str,
) -> dict:
    """Update channel file with promotion metadata."""
    try:
        channel_data["last_promotion"] = last_promotion
        channel_data["updated_at"] = updated_at
        
        if switch:
            channel_data["current_channel"] = dest_channel
            
        # Ensure dest_channel is in channels list (if forced addition)
        channels = channel_data.get("channels", [])
        if dest_channel not in channels:
            channels.append(dest_channel)
            channels.sort()
            channel_data["channels"] = channels
            
        content = json.dumps(channel_data, indent=2, sort_keys=True, allow_nan=False)
        _atomic_write(channel_file, content)
        return {"ok": True}
    except OSError as e:
        return {"ok": False, "error": f"channel_update_failed:{e}"}


def promote_bundle(
    src_dir: Path,
    dest_dir: Path,
    channel_file: Path,
    src_channel: str,
    dest_channel: str,
    key: bytes,
    force: bool = False,
    dry_run: bool = False,
    switch: bool = False,
    timestamp: Optional[str] = None,
) -> dict:
    """
    Promote a bundle from one channel to another.
    
    Args:
        src_dir: Source directory containing bundle.
        dest_dir: Destination directory for promoted bundle.
        channel_file: Path to channel file.
        src_channel: Source channel name.
        dest_channel: Destination channel name.
        key: Verification key bytes.
        force: If True, allow same-channel promotion and missing dest channel.
        dry_run: If True, return plan without modifications.
        switch: If True, update current_channel to dest_channel.
    
    Returns:
        Dict with {ok, errors, warnings, last_promotion, actions}.
    """
    actions = []
    
    # Verify source bundle
    src_bundle = src_dir / BUNDLE_DIR_NAME
    if not src_bundle.exists():
        return {"ok": False, "errors": ["bundle_missing"], "warnings": []}
    
    verify_result = verify_registry_bundle(src_bundle, key, strict=True)
    if not verify_result["ok"]:
        return {
            "ok": False,
            "errors": ["bundle_verify_failed"] + verify_result.get("errors", []),
            "warnings": verify_result.get("warnings", []),
        }
    
    # Load channel file
    channel_result = load_channel_file(channel_file)
    if not channel_result["ok"]:
        return {"ok": False, "errors": [channel_result["error"]], "warnings": []}
    
    channel_data = channel_result["data"]
    
    # Validate inputs
    val_errors, val_warnings = _validate_promotion_inputs(
        src_dir, dest_dir, channel_data, src_channel, dest_channel, force
    )
    if val_errors:
        return {"ok": False, "errors": val_errors, "warnings": val_warnings}
    
    # Build promotion log
    try:
        resolved_timestamp = _resolve_promotion_timestamp(channel_data, timestamp)
    except ValueError as exc:
        return {"ok": False, "errors": [str(exc)], "warnings": val_warnings}

    last_promotion = {
        "from": src_channel,
        "to": dest_channel,
        "timestamp": resolved_timestamp,
        "bundle_hash": verify_result.get("registry_hash"),
        "key_id": verify_result.get("key_id"),
    }
    
    # Record actions
    if dest_channel not in channel_data.get("channels", []):
        actions.append(f"add_channel:{dest_channel}")
    actions.append(f"copy_bundle:{src_channel}->{dest_channel}")
    actions.append("update_last_promotion")
    if switch:
        actions.append(f"set_current_channel:{dest_channel}")
    
    # Dry run
    if dry_run:
        return {
            "ok": True,
            "errors": [],
            "warnings": val_warnings,
            "dry_run": True,
            "actions": actions,
            "last_promotion": last_promotion,
            "promoted": False,
        }
    
    # Perform promotion
    promote_result = _perform_promotion(src_bundle, dest_dir)
    if not promote_result["ok"]:
        return {"ok": False, "errors": [promote_result["error"]], "warnings": val_warnings}
    
    # Update channel file
    update_result = _update_channel_after_promotion(
        channel_file,
        channel_data,
        last_promotion,
        dest_channel,
        switch,
        resolved_timestamp,
    )
    if not update_result["ok"]:
        return {"ok": False, "errors": [update_result["error"]], "warnings": val_warnings}
    
    return {
        "ok": True,
        "errors": [],
        "warnings": val_warnings,
        "dry_run": False,
        "actions": actions,
        "last_promotion": last_promotion,
        "dest_bundle": str(promote_result["dest_bundle"]),
        "promoted": True,
    }
