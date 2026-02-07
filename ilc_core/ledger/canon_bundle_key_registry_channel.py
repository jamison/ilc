"""
Registry channel management for canon bundle key registry.

A channel file tracks available registry sources (e.g., main, test, experimental)
and the currently active channel.
"""

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


CHANNEL_VERSION = "v0.3"
CHANNEL_VERSION_V02 = "v0.2"
CHANNEL_VERSION_V01 = "v0.1"
CHANNEL_FILENAME = "canon_key_registry_channel.json"
CHANNEL_PATTERN = re.compile(r"^[a-z0-9-]{1,32}$")
STRICT_ISO8601_TZ_PATTERN = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})$"
)
ALLOWED_FIELDS = {
    "channel_version", "updated_at", "current_channel", "channels", "notes",
    "channel_order", "sources", "last_sync", "last_promotion",
}


def _now_iso8601() -> str:
    """Return current UTC time as strict ISO-8601 string."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _atomic_write(path: Path, content: str) -> None:
    """Write content atomically using temp file + rename."""
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(content, encoding="utf-8")
    tmp.replace(path)


def load_channel_file(path: Path) -> dict:
    """
    Load and parse a channel file.
    
    Returns:
        Dict with channel data, or error dict if load fails.
    """
    if not path.exists():
        return {"ok": False, "error": "file_not_found"}
    
    try:
        content = path.read_text(encoding="utf-8")
    except OSError as e:
        return {"ok": False, "error": f"file_read_error:{e}"}
    
    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        return {"ok": False, "error": "invalid_json"}
    
    return {"ok": True, "data": data}


def validate_channel_file(path: Path) -> dict:
    """
    Validate a channel file.
    
    Returns:
        Dict with {ok, errors, warnings, data}.
    """
    errors = []
    warnings = []
    
    load_result = load_channel_file(path)
    if not load_result["ok"]:
        return {"ok": False, "errors": [load_result["error"]], "warnings": []}
    
    data = load_result["data"]
    
    # Check for unknown fields
    for key in data:
        if key not in ALLOWED_FIELDS:
            errors.append(f"schema_violation:unknown_field:{key}")
    
    # Validate channel_version
    version = data.get("channel_version")
    if "channel_version" not in data:
        errors.append("schema_violation:missing_channel_version")
    elif version not in (CHANNEL_VERSION, CHANNEL_VERSION_V02, CHANNEL_VERSION_V01):
        errors.append("schema_violation:invalid_channel_version")
    elif version == CHANNEL_VERSION_V01:
        warnings.append("channel_version_v01_deprecated")
    
    # Validate updated_at
    if "updated_at" not in data:
        errors.append("schema_violation:missing_updated_at")
    elif not STRICT_ISO8601_TZ_PATTERN.match(str(data.get("updated_at", ""))):
        errors.append("schema_violation:invalid_updated_at")
    
    # Validate channels
    if "channels" not in data:
        errors.append("schema_violation:missing_channels")
    else:
        channels = data["channels"]
        if not isinstance(channels, list):
            errors.append("schema_violation:channels_not_list")
        elif len(channels) == 0:
            errors.append("empty_channels")
        else:
            # Check format
            for ch in channels:
                if not isinstance(ch, str) or not CHANNEL_PATTERN.match(ch):
                    errors.append(f"invalid_channel_format:{ch}")
            
            # Check duplicates
            if len(channels) != len(set(channels)):
                errors.append("duplicate_channels")
            
            # Check sorted
            if channels != sorted(channels):
                warnings.append("unsorted_channels")
    
    # Validate current_channel
    if "current_channel" not in data:
        errors.append("missing_current_channel")
    else:
        current = data["current_channel"]
        if not isinstance(current, str) or not CHANNEL_PATTERN.match(current):
            errors.append(f"invalid_channel_format:{current}")
        elif "channels" in data and isinstance(data["channels"], list):
            if current not in data["channels"]:
                errors.append("current_channel_not_in_channels")

    # Validate sources (v0.2 only)
    sources = data.get("sources")
    if version in (CHANNEL_VERSION, CHANNEL_VERSION_V02):
        if sources is not None:
            if not isinstance(sources, dict):
                errors.append("schema_violation:sources_not_object")
            else:
                for ch in channels if isinstance(channels, list) else []:
                    if ch not in sources or not sources[ch]:
                        errors.append(f"sources_missing:{ch}")
                        continue
                    if not isinstance(sources[ch], list):
                        errors.append(f"sources_not_list:{ch}")
                        continue
                    for src in sources[ch]:
                        if not isinstance(src, str) or not src:
                            errors.append(f"sources_invalid:{ch}")
                for ch in sources:
                    if isinstance(channels, list) and ch not in channels:
                        errors.append(f"sources_unknown_channel:{ch}")
    elif version == CHANNEL_VERSION_V01 and sources is not None:
        warnings.append("sources_ignored_v01")

    # Validate last_sync (v0.2 only)
    last_sync = data.get("last_sync")
    if version in (CHANNEL_VERSION, CHANNEL_VERSION_V02) and last_sync is not None:
        if not isinstance(last_sync, dict):
            errors.append("schema_violation:last_sync_not_object")
        else:
            required = ["channel", "source", "timestamp", "ok", "warnings", "errors"]
            for field in required:
                if field not in last_sync:
                    errors.append(f"last_sync_missing:{field}")
            if "channel" in last_sync:
                if not isinstance(last_sync["channel"], str) or not last_sync["channel"]:
                    errors.append("last_sync_invalid_channel")
                elif isinstance(channels, list) and last_sync["channel"] not in channels:
                    errors.append("last_sync_channel_not_in_channels")
            if "source" in last_sync:
                if not isinstance(last_sync["source"], str):
                    errors.append("last_sync_invalid_source")
            if "timestamp" in last_sync:
                if not STRICT_ISO8601_TZ_PATTERN.match(str(last_sync["timestamp"])):
                    errors.append("last_sync_invalid_timestamp")
            if "ok" in last_sync and not isinstance(last_sync["ok"], bool):
                errors.append("last_sync_invalid_ok")
            for list_field in ("warnings", "errors"):
                if list_field in last_sync and not isinstance(last_sync[list_field], list):
                    errors.append(f"last_sync_invalid_{list_field}")
            for opt_field in ("bundle_hash", "key_id"):
                if opt_field in last_sync and last_sync[opt_field] is not None:
                    if not isinstance(last_sync[opt_field], str):
                        errors.append(f"last_sync_invalid_{opt_field}")
    elif version == CHANNEL_VERSION_V01 and last_sync is not None:
        warnings.append("last_sync_ignored_v01")
    
    return {
        "ok": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "data": data if len(errors) == 0 else None,
    }


def set_current_channel(path: Path, channel: str, force: bool = False) -> dict:
    """
    Set the current channel in a channel file.
    
    Args:
        path: Path to channel file.
        channel: Channel name to set as current.
        force: If True, add channel to list if not present.
    
    Returns:
        Dict with {ok, warnings} or {ok, error}.
    """
    warnings = []
    
    # Validate channel format
    if not CHANNEL_PATTERN.match(channel):
        return {"ok": False, "error": f"invalid_channel_format:{channel}"}
    
    # Load existing file
    load_result = load_channel_file(path)
    if not load_result["ok"]:
        return {"ok": False, "error": load_result["error"]}
    
    data = load_result["data"]
    channels = data.get("channels", [])
    
    # Check if channel exists
    if channel not in channels:
        if not force:
            return {"ok": False, "error": "channel_not_found"}
        warnings.append("channel_set_forced")
        channels.append(channel)
        channels.sort()
        data["channels"] = channels
    
    # Update current channel and timestamp
    data["current_channel"] = channel
    data["updated_at"] = _now_iso8601()
    
    # Write atomically
    try:
        content = json.dumps(data, indent=2, sort_keys=True)
        _atomic_write(path, content)
    except OSError as e:
        return {"ok": False, "error": f"file_write_error:{e}"}
    
    return {"ok": True, "warnings": warnings, "current_channel": channel}


def list_channels(path: Path) -> dict:
    """
    List channels from a channel file.
    
    Returns:
        Dict with {ok, current_channel, channels} or {ok, error}.
    """
    load_result = load_channel_file(path)
    if not load_result["ok"]:
        return {"ok": False, "error": load_result["error"]}
    
    data = load_result["data"]
    return {
        "ok": True,
        "current_channel": data.get("current_channel"),
        "channels": data.get("channels", []),
    }


def create_channel_file(
    path: Path,
    channel: str,
    force: bool = False,
) -> dict:
    """
    Create a new channel file with initial channel.
    
    Args:
        path: Path to create channel file.
        channel: Initial channel name (becomes current).
        force: If True, overwrite existing file.
    
    Returns:
        Dict with {ok} or {ok, error}.
    """
    if path.exists() and not force:
        return {"ok": False, "error": "file_exists"}
    
    if not CHANNEL_PATTERN.match(channel):
        return {"ok": False, "error": f"invalid_channel_format:{channel}"}
    
    data = {
        "channel_version": CHANNEL_VERSION,
        "updated_at": _now_iso8601(),
        "current_channel": channel,
        "channels": [channel],
    }
    
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        content = json.dumps(data, indent=2, sort_keys=True)
        _atomic_write(path, content)
    except OSError as e:
        return {"ok": False, "error": f"file_write_error:{e}"}
    
    return {"ok": True, "path": str(path), "current_channel": channel}
