# SPDX-License-Identifier: AGPL-3.0-only
"""Phase 908 — CDL-078 relay incentive: routing reputation runtime.

Bridges WANT-BLOCK serve events (CDL-077) to the CDL-060 centrality delta
gossip pipeline, constitutionally locking the reputation-implicit relay
incentive model.

Design:
    - Successful WANT-BLOCK serves are recorded in an in-process epoch buffer.
    - At epoch close, flush_epoch_serve_events() converts buffered counts to
      centrality delta calls via accumulate_centrality_delta() (CDL-060).
    - SERVE_CENTRALITY_DELTA: centrality credit per successful serve.
    - SERVE_CENTRALITY_MAX_PER_EPOCH: per-node cap per epoch (prevents gaming).
    - record_serve_event() is best-effort — never raises, never blocks.
    - No LMDB write. No per-hop ECU transfer. No negative delta.

Epoch definition: caller-supplied validation epoch integer. Earlier planning
described a wall-clock minute bucket as a caller convention; this module no
longer imports or reads wall-clock time. It buffers serve-count reputation
signals only and does not write settlement state, ECU balances, ILC balances,
or validator weights.
"""

from __future__ import annotations

from decimal import Decimal
import threading
from typing import Any

from ilc_core.network.d2d.centrality_delta_gossip_runtime import (
    CDL_060_GOSSIP_RUNTIME_VERSION as _CDL_060_CHECK,
    accumulate_centrality_delta,
)
from ilc_core.network.d2d.truth_primitive_fetch_runtime import (
    TRUTH_PRIMITIVE_FETCH_RUNTIME_VERSION as _CDL_077_CHECK,
)

ROUTING_REPUTATION_RUNTIME_VERSION = "routing_reputation_runtime_908.v0.1"
CDL_078_DEPENDENCY = "cdl_078_relay_incentive_constitutional_lock.v0.1"
CDL_060_DEPENDENCY = "cdl_060_ratified_541.v0.1"
CDL_077_DEPENDENCY = "cdl_077_want_have_want_block_fetch.v0.1"
ROUTING_REPUTATION_NO_SETTLEMENT_TOKEN = (
    "routing_reputation_wall_clock_not_settlement_input_phase_1575h_fix2"
)

SERVE_CENTRALITY_DELTA = Decimal("0.01")
SERVE_CENTRALITY_MAX_PER_EPOCH = Decimal("0.10")
MAX_REPUTATION_NODE_ID_CHARS = 256
MAX_SERVE_BUFFER_EPOCHS = 128
MAX_SERVE_BUFFER_NODES_PER_EPOCH = 10_000
MAX_SERVE_COUNT_PER_NODE = 1_000_000
MAX_FLUSH_LOG_ENTRIES = 10_000

# Dep-chain guards
if _CDL_060_CHECK != "centrality_delta_gossip_runtime_GAP_CDL060.v0.2":
    raise RuntimeError("routing_reputation_runtime_cdl_060_dep_mismatch")
if _CDL_077_CHECK != "truth_primitive_fetch_runtime_901.v0.1":
    raise RuntimeError("routing_reputation_runtime_cdl_077_dep_mismatch")

_state_lock = threading.Lock()


# ---------------------------------------------------------------------------
# State helpers
# ---------------------------------------------------------------------------


def new_reputation_state() -> dict[str, Any]:
    """Return a fresh routing reputation state dict."""
    return {
        "serve_buffer": {},   # {epoch: {node_id: count}}
        "flush_log": [],      # [{epoch, nodes_flushed, total_delta_emitted}]
    }


# Module-level singleton state — used by the wiring in truth_primitive_fetch_runtime.
# Tests may reset this by calling _reset_global_state() or passing their own state dict
# to the core functions directly.
_global_reputation_state: dict = new_reputation_state()


def _reset_global_state() -> None:
    """Reset the module-level singleton to a clean state (for testing)."""
    global _global_reputation_state
    with _state_lock:
        _global_reputation_state = new_reputation_state()


def _serve_buffer(state: dict) -> dict[int, dict[str, int]]:
    if "serve_buffer" not in state or not isinstance(state["serve_buffer"], dict):
        state["serve_buffer"] = {}
    return state["serve_buffer"]


def _flush_log(state: dict) -> list:
    if "flush_log" not in state or not isinstance(state["flush_log"], list):
        state["flush_log"] = []
    return state["flush_log"]


def _append_flush_receipt(state: dict, receipt: dict[str, Any]) -> None:
    log = _flush_log(state)
    log.append(receipt)
    if len(log) > MAX_FLUSH_LOG_ENTRIES:
        del log[:-MAX_FLUSH_LOG_ENTRIES]


# ---------------------------------------------------------------------------
# Core functions
# ---------------------------------------------------------------------------


def record_serve_event(node_id: str, epoch: int, state: dict) -> None:
    """Record a successful WANT-BLOCK serve event in the epoch buffer.

    Best-effort: never raises. Thread-safe via module lock.

    Args:
        node_id: CIDv1 of the node that was served.
        epoch:   Caller-supplied validation epoch.
        state:   Mutable reputation state dict (new_reputation_state()).
    """
    try:
        if not isinstance(node_id, str) or not node_id.strip():
            return
        clean_node_id = node_id.strip()
        if len(clean_node_id) > MAX_REPUTATION_NODE_ID_CHARS:
            return
        if not isinstance(epoch, int) or epoch < 0:
            return
        if not isinstance(state, dict):
            return
        with _state_lock:
            buf = _serve_buffer(state)
            if epoch not in buf and len(buf) >= MAX_SERVE_BUFFER_EPOCHS:
                return
            epoch_buf = buf.setdefault(epoch, {})
            if not isinstance(epoch_buf, dict):
                return
            if (
                clean_node_id not in epoch_buf
                and len(epoch_buf) >= MAX_SERVE_BUFFER_NODES_PER_EPOCH
            ):
                return
            current = epoch_buf.get(clean_node_id, 0)
            if not isinstance(current, int) or current < 0:
                current = 0
            epoch_buf[clean_node_id] = min(current + 1, MAX_SERVE_COUNT_PER_NODE)
    except Exception:  # noqa: BLE001
        pass  # best-effort — never propagate


def flush_epoch_serve_events(
    epoch: int,
    state: dict,
    centrality_state: dict,
) -> dict[str, Any]:
    """Convert accumulated serve events for one epoch into CDL-060 centrality deltas.

    For each (node_id, count) in serve_buffer[epoch]:
        raw_delta = min(count * SERVE_CENTRALITY_DELTA, SERVE_CENTRALITY_MAX_PER_EPOCH)
        accumulate_centrality_delta(node_id, raw_delta, epoch, centrality_state)

    Clears serve_buffer[epoch] after flush.
    Appends a flush receipt to flush_log.

    Returns:
        {"epoch": int, "nodes_flushed": int, "total_delta_emitted": str}
    """
    if not isinstance(epoch, int) or epoch < 0:
        raise ValueError("flush_epoch_invalid_epoch")
    if not isinstance(state, dict):
        raise ValueError("flush_epoch_invalid_state")
    if not isinstance(centrality_state, dict):
        raise ValueError("flush_epoch_invalid_centrality_state")

    with _state_lock:
        buf = _serve_buffer(state)
        epoch_buf = buf.get(epoch, {})
        if not isinstance(epoch_buf, dict):
            raise ValueError("serve_buffer_epoch_must_be_dict")
        if len(epoch_buf) > MAX_SERVE_BUFFER_NODES_PER_EPOCH:
            raise ValueError("serve_buffer_epoch_node_cap_exceeded")
        epoch_buf = buf.pop(epoch, {})

    nodes_flushed = 0
    total_delta = Decimal("0")

    for node_id, count in epoch_buf.items():
        if not isinstance(node_id, str) or not node_id.strip():
            continue
        clean_node_id = node_id.strip()
        if len(clean_node_id) > MAX_REPUTATION_NODE_ID_CHARS:
            continue
        if not isinstance(count, int) or count <= 0:
            continue
        effective_count = min(count, MAX_SERVE_COUNT_PER_NODE)
        raw_delta = min(
            effective_count * SERVE_CENTRALITY_DELTA,
            SERVE_CENTRALITY_MAX_PER_EPOCH,
        )
        accumulate_centrality_delta(clean_node_id, raw_delta, epoch, centrality_state)
        nodes_flushed += 1
        total_delta += raw_delta

    receipt = {
        "epoch": epoch,
        "nodes_flushed": nodes_flushed,
        "total_delta_emitted": format(total_delta.quantize(Decimal("0.000001")), "f"),
    }
    with _state_lock:
        _append_flush_receipt(state, receipt)

    return receipt
