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

Epoch definition: int(time.time() // 60) — 1-minute validation epoch
(CDL-071 Tier 2, Phase 851).
"""

from __future__ import annotations

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

SERVE_CENTRALITY_DELTA: float = 0.01
SERVE_CENTRALITY_MAX_PER_EPOCH: float = 0.10

# Dep-chain guards
if _CDL_060_CHECK != "cdl_060_gossip_runtime_548.v0.1":
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


# ---------------------------------------------------------------------------
# Core functions
# ---------------------------------------------------------------------------


def record_serve_event(node_id: str, epoch: int, state: dict) -> None:
    """Record a successful WANT-BLOCK serve event in the epoch buffer.

    Best-effort: never raises. Thread-safe via module lock.

    Args:
        node_id: CIDv1 of the node that was served.
        epoch:   Current validation epoch (int(time.time() // 60)).
        state:   Mutable reputation state dict (new_reputation_state()).
    """
    try:
        if not isinstance(node_id, str) or not node_id.strip():
            return
        if not isinstance(epoch, int) or epoch < 0:
            return
        if not isinstance(state, dict):
            return
        with _state_lock:
            buf = _serve_buffer(state)
            epoch_buf = buf.setdefault(epoch, {})
            epoch_buf[node_id] = epoch_buf.get(node_id, 0) + 1
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
        {"epoch": int, "nodes_flushed": int, "total_delta_emitted": float}
    """
    if not isinstance(epoch, int) or epoch < 0:
        raise ValueError("flush_epoch_invalid_epoch")
    if not isinstance(state, dict):
        raise ValueError("flush_epoch_invalid_state")
    if not isinstance(centrality_state, dict):
        raise ValueError("flush_epoch_invalid_centrality_state")

    with _state_lock:
        buf = _serve_buffer(state)
        epoch_buf = buf.pop(epoch, {})

    nodes_flushed = 0
    total_delta = 0.0

    for node_id, count in epoch_buf.items():
        if not isinstance(node_id, str) or not node_id.strip():
            continue
        if not isinstance(count, int) or count <= 0:
            continue
        raw_delta = min(count * SERVE_CENTRALITY_DELTA, SERVE_CENTRALITY_MAX_PER_EPOCH)
        accumulate_centrality_delta(node_id, raw_delta, epoch, centrality_state)
        nodes_flushed += 1
        total_delta += raw_delta

    receipt = {
        "epoch": epoch,
        "nodes_flushed": nodes_flushed,
        "total_delta_emitted": round(total_delta, 6),
    }
    with _state_lock:
        _flush_log(state).append(receipt)

    return receipt
