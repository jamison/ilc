# SPDX-License-Identifier: AGPL-3.0-only
"""CDL-060 centrality-delta gossip runtime.

This v1 runtime implements the ratified single-hop bounded-fanout lane under
`ACCUMULATION_MODEL = "epoch_boundary_atomic"`. Under the selected model,
committed centrality updates can lag inbound gossip by up to one validation
epoch because deltas are buffered and committed atomically at epoch boundary.

Crash recovery may choose graceful zeroing for a lost epoch buffer. Callers can
mark that condition by adding the epoch integer to `state["_zeroed_epochs"]`;
`commit_epoch_buffer()` will then append an explicit event-log record instead of
silently discarding the epoch.
"""

from __future__ import annotations

import math
from typing import Any

from ilc_core.epistemic.reuse_centrality_runtime import CDL_052_DEPENDENCY as _CDL_052_CHECK

from .gossip import D2D_GOSSIP_DEPENDENCY as _D2D_GOSSIP_CHECK
from .gossip import validate_gossip_channel


CDL_060_GOSSIP_RUNTIME_VERSION = "cdl_060_gossip_runtime_548.v0.1"
CDL_060_DEPENDENCY = "cdl_060_ratified_541.v0.1"
D2D_GOSSIP_DEPENDENCY = "d2d_gossip_382.v0.1"
CDL_052_DEPENDENCY = "cdl_052_ratified_466.v0.1"
ACCUMULATION_MODEL = "epoch_boundary_atomic"
MAX_FANOUT = 3
U_FLOOR = 0.05
CENTRALITY_SCORE_CAP = 1.0
EPOCH_BUFFER_ZEROED_EVENT = "epoch_buffer_zeroed"
EPOCH_BUFFER_ZEROED_REASON = "crash_recovery_graceful_zero"

if _CDL_052_CHECK != CDL_052_DEPENDENCY:
    import json as _json, sys as _sys
    _sys.stdout.write(
        _json.dumps(
            {
                "ok": False,
                "error": "centrality_delta_gossip_dep_chain_mismatch",
                "dependency": "cdl_052",
                "expected": CDL_052_DEPENDENCY,
                "got": _CDL_052_CHECK,
            },
            sort_keys=True,
        )
        + "\n"
    )
    _sys.stdout.flush()
    raise RuntimeError("centrality_delta_gossip_cdl_052_dependency_mismatch")

if _D2D_GOSSIP_CHECK != D2D_GOSSIP_DEPENDENCY:
    import json as _json, sys as _sys
    _sys.stdout.write(
        _json.dumps(
            {
                "ok": False,
                "error": "centrality_delta_gossip_dep_chain_mismatch",
                "dependency": "d2d_gossip",
                "expected": D2D_GOSSIP_DEPENDENCY,
                "got": _D2D_GOSSIP_CHECK,
            },
            sort_keys=True,
        )
        + "\n"
    )
    _sys.stdout.flush()
    raise RuntimeError("centrality_delta_gossip_d2d_gossip_dependency_mismatch")


def _require_mapping(name: str, value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{name}_must_be_dict")
    return value


def _require_non_empty_string(name: str, value: Any) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name}_must_be_non_empty_string")
    return value.strip()


def _require_non_negative_int(name: str, value: Any) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"{name}_must_be_non_negative_int")
    return value


def _require_non_negative_float(name: str, value: Any) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name}_must_be_non_negative_float")
    number = float(value)
    if not math.isfinite(number) or number < 0.0:
        raise ValueError(f"{name}_must_be_non_negative_float")
    return number


def _normalized_delta(delta: float) -> float:
    if delta < U_FLOOR:
        return 0.0
    return round(delta, 12)


def _bounded_centrality_total(current: float, delta: float) -> float:
    return round(min(CENTRALITY_SCORE_CAP, current + delta), 12)


def _validate_channel(value: Any) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("cdl_060_channel_opacity_violation: channel_must_be_opaque")
    try:
        return str(validate_gossip_channel(value))
    except ValueError as exc:  # pragma: no cover - normalized to the ratified token
        raise ValueError("cdl_060_channel_opacity_violation: channel_must_be_opaque") from exc


def _state_event_log(state: dict[str, Any]) -> list[dict[str, Any]]:
    event_log = state.setdefault("_event_log", [])
    if not isinstance(event_log, list):
        raise ValueError("state_event_log_must_be_list")
    return event_log


def _state_pending_map(state: dict[str, Any]) -> dict[int, dict[str, float]]:
    pending = state.setdefault("_pending", {})
    if not isinstance(pending, dict):
        raise ValueError("state_pending_must_be_dict")
    return pending


def _zeroed_epoch_markers(state: dict[str, Any]) -> set[int]:
    markers = state.setdefault("_zeroed_epochs", set())
    if isinstance(markers, set):
        if not all(isinstance(epoch, int) and epoch >= 0 for epoch in markers):
            raise ValueError("state_zeroed_epochs_invalid")
        return markers
    if isinstance(markers, list):
        if not all(isinstance(epoch, int) and epoch >= 0 for epoch in markers):
            raise ValueError("state_zeroed_epochs_invalid")
        converted = set(markers)
        state["_zeroed_epochs"] = converted
        return converted
    raise ValueError("state_zeroed_epochs_invalid")


def validate_centrality_delta_message(msg: dict) -> bool:
    """Validate the CDL-060 message envelope.

    Low deltas remain valid messages. The U_FLOOR suppression rule applies only
    during state accumulation, not during message validation.
    """

    msg_map = _require_mapping("msg", msg)
    _require_non_empty_string("cid", msg_map.get("cid"))
    _require_non_negative_float("score_delta", msg_map.get("score_delta"))
    _require_non_negative_int("epoch", msg_map.get("epoch"))
    _require_non_empty_string("signature", msg_map.get("signature"))

    hop_count = _require_non_negative_int("hop_count", msg_map.get("hop_count"))
    if hop_count != 1:
        raise ValueError("cdl_060_hop_count_violation: single_hop_only")

    fanout = _require_non_negative_int("fanout", msg_map.get("fanout"))
    if fanout < 1 or fanout > MAX_FANOUT:
        raise ValueError("cdl_060_fanout_violation: exceeds_bounded_fanout")

    _validate_channel(msg_map.get("channel"))

    return True


def accumulate_centrality_delta(node_id: str, delta: float, epoch: int, state: dict) -> dict:
    """Accumulate a centrality delta using the selected v1 accumulation model."""

    normalized_node = _require_non_empty_string("node_id", node_id)
    normalized_delta = _normalized_delta(_require_non_negative_float("delta", delta))
    normalized_epoch = _require_non_negative_int("epoch", epoch)
    state_map = _require_mapping("state", state)

    if ACCUMULATION_MODEL == "write_through":
        current = _require_non_negative_float(
            "state_value",
            state_map.get(normalized_node, 0.0),
        )
        state_map[normalized_node] = _bounded_centrality_total(current, normalized_delta)
        return state_map

    pending = _state_pending_map(state_map)
    epoch_buffer = pending.setdefault(normalized_epoch, {})
    if not isinstance(epoch_buffer, dict):
        raise ValueError("state_pending_epoch_buffer_must_be_dict")
    current = _require_non_negative_float(
        "state_pending_value",
        epoch_buffer.get(normalized_node, 0.0),
    )
    epoch_buffer[normalized_node] = _bounded_centrality_total(current, normalized_delta)
    return state_map


def commit_epoch_buffer(epoch: int, state: dict) -> dict:
    """Commit or clear the buffered deltas for one epoch."""

    normalized_epoch = _require_non_negative_int("epoch", epoch)
    state_map = _require_mapping("state", state)

    if ACCUMULATION_MODEL == "write_through":
        return state_map

    pending = _state_pending_map(state_map)
    zeroed_epochs = _zeroed_epoch_markers(state_map)
    event_log = _state_event_log(state_map)
    epoch_buffer = pending.pop(normalized_epoch, None)

    if normalized_epoch in zeroed_epochs:
        zeroed_epochs.remove(normalized_epoch)
        event_log.append(
            {
                "event": EPOCH_BUFFER_ZEROED_EVENT,
                "epoch": normalized_epoch,
                "reason": EPOCH_BUFFER_ZEROED_REASON,
            }
        )
        return state_map

    if epoch_buffer is None:
        return state_map
    if not isinstance(epoch_buffer, dict):
        raise ValueError("state_pending_epoch_buffer_must_be_dict")

    for node_id, delta in epoch_buffer.items():
        normalized_node = _require_non_empty_string("node_id", node_id)
        normalized_delta = _require_non_negative_float("delta", delta)
        current = _require_non_negative_float(
            "state_value",
            state_map.get(normalized_node, 0.0),
        )
        state_map[normalized_node] = _bounded_centrality_total(current, normalized_delta)

    return state_map
