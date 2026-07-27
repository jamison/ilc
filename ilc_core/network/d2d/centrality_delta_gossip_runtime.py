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

from decimal import Decimal, InvalidOperation, localcontext
from typing import Any

from ilc_core.epistemic.reuse_centrality_runtime import CDL_052_DEPENDENCY as _CDL_052_CHECK

from .gossip import D2D_GOSSIP_DEPENDENCY as _D2D_GOSSIP_CHECK
from .gossip import validate_gossip_channel


CDL_060_GOSSIP_RUNTIME_VERSION = "centrality_delta_gossip_runtime_GAP_CDL060.v0.2"
CDL_060_DEPENDENCY = "cdl_060_ratified_541.v0.1"
D2D_GOSSIP_DEPENDENCY = "d2d_gossip_382.v0.1"
CDL_052_DEPENDENCY = "cdl_052_ratified_466.v0.1"
ACCUMULATION_MODEL = "epoch_boundary_atomic"
MAX_FANOUT = 3
U_FLOOR = Decimal("0.05")
CENTRALITY_SCORE_CAP = Decimal("1.000000000000")
CENTRALITY_QUANTUM = Decimal("0.000000000001")
MAX_CENTRALITY_NODE_ID_CHARS = 256
MAX_CENTRALITY_MESSAGE_TEXT_CHARS = 512
MAX_CENTRALITY_SIGNATURE_CHARS = 8192
MAX_PENDING_EPOCHS = 128
MAX_PENDING_NODES_PER_EPOCH = 10_000
MAX_CENTRALITY_DECIMAL_DIGITS = 80
MAX_CENTRALITY_DECIMAL_ADJUSTED_EXPONENT = 18
CENTRALITY_DECIMAL_MAGNITUDE_TOKEN = "centrality_decimal_magnitude_too_large"
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


def _require_non_empty_string(
    name: str,
    value: Any,
    *,
    max_chars: int | None = None,
) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name}_must_be_non_empty_string")
    normalized = value.strip()
    if max_chars is not None and len(normalized) > max_chars:
        raise ValueError(f"{name}_too_long")
    return normalized


def _require_non_negative_int(name: str, value: Any) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"{name}_must_be_non_negative_int")
    return value


def _require_non_negative_decimal(name: str, value: Any) -> Decimal:
    if isinstance(value, bool) or isinstance(value, float):
        raise ValueError(f"{name}_must_be_non_negative_decimal")
    if not isinstance(value, (Decimal, int, str)):
        raise ValueError(f"{name}_must_be_non_negative_decimal")
    try:
        number = value if isinstance(value, Decimal) else Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise ValueError(f"{name}_must_be_non_negative_decimal") from exc
    if not number.is_finite() or number < Decimal("0"):
        raise ValueError(f"{name}_must_be_non_negative_decimal")
    if (
        len(number.as_tuple().digits) > MAX_CENTRALITY_DECIMAL_DIGITS
        or number.adjusted() > MAX_CENTRALITY_DECIMAL_ADJUSTED_EXPONENT
    ):
        raise ValueError(CENTRALITY_DECIMAL_MAGNITUDE_TOKEN)
    return number


def _normalized_delta(delta: Decimal) -> Decimal:
    if delta < U_FLOOR:
        return Decimal("0")
    if delta > CENTRALITY_SCORE_CAP:
        raise ValueError("delta_exceeds_centrality_score_cap")
    try:
        return delta.quantize(CENTRALITY_QUANTUM)
    except InvalidOperation as exc:
        raise ValueError(CENTRALITY_DECIMAL_MAGNITUDE_TOKEN) from exc


def _bounded_centrality_total(current: Decimal, delta: Decimal) -> Decimal:
    with localcontext() as ctx:
        ctx.prec = 50
        total = min(CENTRALITY_SCORE_CAP, current + delta)
    try:
        return total.quantize(CENTRALITY_QUANTUM)
    except InvalidOperation as exc:
        raise ValueError(CENTRALITY_DECIMAL_MAGNITUDE_TOKEN) from exc


def _validate_channel(value: Any) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("cdl_060_channel_opacity_violation: channel_must_be_opaque")
    if len(value.strip()) > MAX_CENTRALITY_MESSAGE_TEXT_CHARS:
        raise ValueError("cdl_060_channel_opacity_violation: channel_too_long")
    try:
        return str(validate_gossip_channel(value))
    except ValueError as exc:  # pragma: no cover - normalized to the ratified token
        raise ValueError("cdl_060_channel_opacity_violation: channel_must_be_opaque") from exc


def _state_event_log(state: dict[str, Any]) -> list[dict[str, Any]]:
    event_log = state.setdefault("_event_log", [])
    if not isinstance(event_log, list):
        raise ValueError("state_event_log_must_be_list")
    return event_log


def _state_pending_map(state: dict[str, Any]) -> dict[int, dict[str, Decimal]]:
    pending = state.setdefault("_pending", {})
    if not isinstance(pending, dict):
        raise ValueError("state_pending_must_be_dict")
    return pending


def _require_pending_epoch_capacity(
    pending: dict[int, dict[str, Decimal]],
    epoch: int,
) -> None:
    if epoch not in pending and len(pending) >= MAX_PENDING_EPOCHS:
        raise ValueError("centrality_pending_epoch_cap_exceeded")


def _require_pending_node_capacity(
    epoch_buffer: dict[str, Decimal],
    node_id: str,
) -> None:
    if node_id not in epoch_buffer and len(epoch_buffer) >= MAX_PENDING_NODES_PER_EPOCH:
        raise ValueError("centrality_pending_epoch_node_cap_exceeded")


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
    _require_non_empty_string(
        "cid",
        msg_map.get("cid"),
        max_chars=MAX_CENTRALITY_NODE_ID_CHARS,
    )
    score_delta = _require_non_negative_decimal(
        "score_delta",
        msg_map.get("score_delta"),
    )
    if score_delta > CENTRALITY_SCORE_CAP:
        raise ValueError("score_delta_exceeds_centrality_score_cap")
    _require_non_negative_int("epoch", msg_map.get("epoch"))
    _require_non_empty_string(
        "signature",
        msg_map.get("signature"),
        max_chars=MAX_CENTRALITY_SIGNATURE_CHARS,
    )

    hop_count = _require_non_negative_int("hop_count", msg_map.get("hop_count"))
    if hop_count != 1:
        raise ValueError("cdl_060_hop_count_violation: single_hop_only")

    fanout = _require_non_negative_int("fanout", msg_map.get("fanout"))
    if fanout < 1 or fanout > MAX_FANOUT:
        raise ValueError("cdl_060_fanout_violation: exceeds_bounded_fanout")

    _validate_channel(msg_map.get("channel"))

    return True


def accumulate_centrality_delta(node_id: str, delta: object, epoch: int, state: dict) -> dict:
    """Accumulate a centrality delta using Decimal arithmetic after ingress."""

    normalized_node = _require_non_empty_string(
        "node_id",
        node_id,
        max_chars=MAX_CENTRALITY_NODE_ID_CHARS,
    )
    normalized_delta = _normalized_delta(_require_non_negative_decimal("delta", delta))
    normalized_epoch = _require_non_negative_int("epoch", epoch)
    state_map = _require_mapping("state", state)
    if normalized_delta == Decimal("0"):
        return state_map

    if ACCUMULATION_MODEL == "write_through":
        current = _require_non_negative_decimal(
            "state_value",
            state_map.get(normalized_node, Decimal("0")),
        )
        state_map[normalized_node] = _bounded_centrality_total(current, normalized_delta)
        return state_map

    pending = _state_pending_map(state_map)
    _require_pending_epoch_capacity(pending, normalized_epoch)
    epoch_buffer = pending.setdefault(normalized_epoch, {})
    if not isinstance(epoch_buffer, dict):
        raise ValueError("state_pending_epoch_buffer_must_be_dict")
    _require_pending_node_capacity(epoch_buffer, normalized_node)
    current = _require_non_negative_decimal(
        "state_pending_value",
            epoch_buffer.get(normalized_node, Decimal("0")),
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
    if len(epoch_buffer) > MAX_PENDING_NODES_PER_EPOCH:
        raise ValueError("centrality_pending_epoch_node_cap_exceeded")

    for node_id, delta in epoch_buffer.items():
        normalized_node = _require_non_empty_string(
            "node_id",
            node_id,
            max_chars=MAX_CENTRALITY_NODE_ID_CHARS,
        )
        normalized_delta = _require_non_negative_decimal("delta", delta)
        current = _require_non_negative_decimal(
            "state_value",
            state_map.get(normalized_node, Decimal("0")),
        )
        state_map[normalized_node] = _bounded_centrality_total(current, normalized_delta)

    return state_map
