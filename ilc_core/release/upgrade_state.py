# SPDX-License-Identifier: AGPL-3.0-only
"""Atomic cached state for ``ilc upgrade`` commands."""

from __future__ import annotations

import json
import os
import stat
import tempfile
from pathlib import Path
from typing import Any, Mapping

from ilc_core.release.constants import ILC_UPGRADE_STATE_PATH_ENV


def default_upgrade_state_path() -> Path:
    override = os.environ.get(ILC_UPGRADE_STATE_PATH_ENV, "").strip()
    if override:
        return Path(override).expanduser()
    return Path.home() / ".ilc" / "upgrade_state.json"


def read_upgrade_state(path: Path | None = None) -> dict[str, Any]:
    state_path = path or default_upgrade_state_path()
    if not state_path.exists():
        raise ValueError("upgrade_state_missing")
    try:
        payload = json.loads(state_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise ValueError("upgrade_state_corrupt") from exc
    if not isinstance(payload, dict):
        raise ValueError("upgrade_state_corrupt")
    return dict(payload)


def write_upgrade_state(
    payload: Mapping[str, Any],
    path: Path | None = None,
) -> Path:
    if not isinstance(payload, Mapping):
        raise ValueError("upgrade_state_payload_invalid")
    state_path = path or default_upgrade_state_path()
    parent = state_path.parent
    parent.mkdir(parents=True, exist_ok=True)
    encoded = (
        json.dumps(dict(payload), sort_keys=True, separators=(",", ":"), allow_nan=False)
        + "\n"
    ).encode("utf-8")
    fd, temp_name = tempfile.mkstemp(
        prefix=f".{state_path.name}.",
        suffix=".tmp",
        dir=str(parent),
    )
    temp_path = Path(temp_name)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(encoded)
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(temp_path, stat.S_IRUSR | stat.S_IWUSR)
        os.replace(temp_path, state_path)
    except Exception:
        try:
            temp_path.unlink()
        except FileNotFoundError:
            pass
        raise
    return state_path


__all__ = [
    "default_upgrade_state_path",
    "read_upgrade_state",
    "write_upgrade_state",
]
