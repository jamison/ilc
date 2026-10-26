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

MAX_UPGRADE_STATE_BYTES = 1_048_576
CURRENT_POLICY_HIGH_WATER_MARKS_KEY = "current_policy_high_water_marks"


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
        with state_path.open("rb") as handle:
            if os.fstat(handle.fileno()).st_size > MAX_UPGRADE_STATE_BYTES:
                raise ValueError("upgrade_state_corrupt")
            raw = handle.read(MAX_UPGRADE_STATE_BYTES + 1)
        if len(raw) > MAX_UPGRADE_STATE_BYTES:
            raise ValueError("upgrade_state_corrupt")
        payload = json.loads(raw.decode("utf-8"))
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
    if len(encoded) > MAX_UPGRADE_STATE_BYTES:
        raise ValueError("upgrade_state_payload_too_large")
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


def current_policy_high_water_mark_key(
    *, policy_id: str, network_id: str, channel: str
) -> str:
    """Return the unambiguous state key for one policy scope."""

    values = (policy_id, network_id, channel)
    if any(not isinstance(value, str) or not value or "\0" in value for value in values):
        raise ValueError("current_policy_scope_invalid")
    return "\0".join(values)


def read_current_policy_high_water_mark(
    state: Mapping[str, Any], *, policy_id: str, network_id: str, channel: str
) -> int:
    """Read a policy sequence without treating malformed state as sequence zero."""

    marks = state.get(CURRENT_POLICY_HIGH_WATER_MARKS_KEY, {})
    if not isinstance(marks, Mapping):
        raise ValueError("current_policy_high_water_marks_corrupt")
    value = marks.get(
        current_policy_high_water_mark_key(
            policy_id=policy_id, network_id=network_id, channel=channel
        ),
        0,
    )
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError("current_policy_high_water_mark_corrupt")
    return value


def advance_current_policy_high_water_mark(
    state: Mapping[str, Any], *, policy_id: str, network_id: str, channel: str,
    accepted_sequence: int
) -> dict[str, Any]:
    """Return copied state with a monotonic accepted policy sequence."""

    if isinstance(accepted_sequence, bool) or not isinstance(accepted_sequence, int) or accepted_sequence < 1:
        raise ValueError("current_policy_accepted_sequence_invalid")
    current = read_current_policy_high_water_mark(
        state, policy_id=policy_id, network_id=network_id, channel=channel
    )
    if accepted_sequence < current:
        raise ValueError("current_policy_sequence_rollback")
    result = dict(state)
    raw_marks = state.get(CURRENT_POLICY_HIGH_WATER_MARKS_KEY, {})
    marks = dict(raw_marks) if isinstance(raw_marks, Mapping) else {}
    marks[current_policy_high_water_mark_key(
        policy_id=policy_id, network_id=network_id, channel=channel
    )] = accepted_sequence
    result[CURRENT_POLICY_HIGH_WATER_MARKS_KEY] = marks
    return result


__all__ = [
    "default_upgrade_state_path",
    "CURRENT_POLICY_HIGH_WATER_MARKS_KEY",
    "MAX_UPGRADE_STATE_BYTES",
    "advance_current_policy_high_water_mark",
    "current_policy_high_water_mark_key",
    "read_current_policy_high_water_mark",
    "read_upgrade_state",
    "write_upgrade_state",
]
