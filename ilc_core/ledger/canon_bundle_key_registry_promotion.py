"""
Promotion workflow for registry bundles between channels.

Enables controlled rollout: experimental -> test -> main
"""

import json
import os
import shutil
from datetime import datetime, timezone
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


def _now_iso8601() -> str:
    """Return current UTC time as strict ISO-8601 string."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


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
    errors = []
    warnings = []
    actions = []
    
    # Check same channel
    if src_channel == dest_channel:
        if not force:
            return {"ok": False, "errors": ["channel_same_as_source"], "warnings": []}
        warnings.append("channel_same_as_source_forced")
    
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
    channels = channel_data.get("channels", [])
    
    # Check source channel exists
    if src_channel not in channels:
        return {"ok": False, "errors": ["channel_not_found:" + src_channel], "warnings": []}
    
    # Check destination channel exists
    if dest_channel not in channels:
        if not force:
            return {"ok": False, "errors": ["channel_not_found:" + dest_channel], "warnings": []}
        warnings.append("channel_added_by_force")
        channels.append(dest_channel)
        channels.sort()
        channel_data["channels"] = channels
        actions.append(f"add_channel:{dest_channel}")
    
    # Check channel order
    channel_order = channel_data.get("channel_order")
    if channel_order:
        try:
            src_idx = channel_order.index(src_channel)
            dest_idx = channel_order.index(dest_channel)
            if dest_idx < src_idx:
                return {"ok": False, "errors": ["channel_order_violation"], "warnings": []}
        except ValueError:
            return {"ok": False, "errors": ["channel_order_incomplete"], "warnings": []}
    else:
        warnings.append("channel_order_missing")

    # Check directories are accessible
    if not src_dir.exists() or not os.access(src_dir, os.R_OK):
        return {"ok": False, "errors": ["src_not_readable"], "warnings": warnings}
    if dest_dir.exists():
        if not os.access(dest_dir, os.W_OK):
            return {"ok": False, "errors": ["dest_not_writable"], "warnings": warnings}
    else:
        if not os.access(dest_dir.parent, os.W_OK):
            return {"ok": False, "errors": ["dest_not_writable"], "warnings": warnings}
    
    # Build promotion log
    last_promotion = {
        "from": src_channel,
        "to": dest_channel,
        "timestamp": _now_iso8601(),
        "bundle_hash": verify_result.get("registry_hash"),
        "key_id": verify_result.get("key_id"),
    }
    
    actions.append(f"copy_bundle:{src_channel}->{dest_channel}")
    actions.append("update_last_promotion")
    if switch:
        actions.append(f"set_current_channel:{dest_channel}")
    
    # Dry run - return plan
    if dry_run:
        return {
            "ok": True,
            "errors": [],
            "warnings": warnings,
            "dry_run": True,
            "actions": actions,
            "last_promotion": last_promotion,
            "promoted": False,
        }
    
    # Perform promotion
    try:
        dest_bundle = dest_dir / BUNDLE_DIR_NAME
        dest_dir.mkdir(parents=True, exist_ok=True)
        
        # Atomic copy
        tmp_bundle = dest_dir / (BUNDLE_DIR_NAME + ".tmp")
        if tmp_bundle.exists():
            shutil.rmtree(tmp_bundle)
        shutil.copytree(src_bundle, tmp_bundle)
        
        if dest_bundle.exists():
            shutil.rmtree(dest_bundle)
        tmp_bundle.rename(dest_bundle)
        
    except OSError as e:
        return {"ok": False, "errors": [f"promotion_failed:{e}"], "warnings": warnings}
    
    # Update channel file
    try:
        channel_data["last_promotion"] = last_promotion
        channel_data["updated_at"] = _now_iso8601()
        if switch:
            channel_data["current_channel"] = dest_channel
        
        content = json.dumps(channel_data, indent=2, sort_keys=True)
        _atomic_write(channel_file, content)
        
    except OSError as e:
        return {"ok": False, "errors": [f"channel_update_failed:{e}"], "warnings": warnings}
    
    return {
        "ok": True,
        "errors": [],
        "warnings": warnings,
        "dry_run": False,
        "actions": actions,
        "last_promotion": last_promotion,
        "dest_bundle": str(dest_bundle),
        "promoted": True,
    }
