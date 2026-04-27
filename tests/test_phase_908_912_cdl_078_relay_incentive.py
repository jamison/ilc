"""Phase 908–912 — CDL-078 relay incentive: routing reputation tests.

Covers all 8 hard pass conditions from the Window 906-912 sequence lock:
  1. routing_reputation_runtime.py exists
  2. ROUTING_REPUTATION_RUNTIME_VERSION and CDL-078/060/077 dep tokens
  3. SERVE_CENTRALITY_DELTA and SERVE_CENTRALITY_MAX_PER_EPOCH constants
  4. record_serve_event() accumulates in epoch buffer
  5. flush_epoch_serve_events() produces CDL-060 centrality delta calls
  6. handle_want_block_request() wired: 200 → serve event recorded
  7. No negative centrality delta introduced
  8. CDL-078 opened in CDL master log
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from ilc_core.network.d2d.routing_reputation_runtime import (
    CDL_060_DEPENDENCY,
    CDL_077_DEPENDENCY,
    CDL_078_DEPENDENCY,
    ROUTING_REPUTATION_RUNTIME_VERSION,
    SERVE_CENTRALITY_DELTA,
    SERVE_CENTRALITY_MAX_PER_EPOCH,
    _reset_global_state,
    flush_epoch_serve_events,
    new_reputation_state,
    record_serve_event,
)
from ilc_core.network.d2d.truth_primitive_fetch_runtime import (
    CDL_078_DEPENDENCY as FETCH_CDL_078_DEPENDENCY,
    FetchRateLimiter,
    handle_want_block_request,
)

PHASE_910_COMMIT_SUBJECT = "feat(g8): phase 906-910 cdl-078 relay incentive reputation-implicit model"
RUNTIME_PATH = Path("ilc_core/network/d2d/routing_reputation_runtime.py")
CDL_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")


# ---------------------------------------------------------------------------
# Group 1: Module existence + tokens
# ---------------------------------------------------------------------------


def test_routing_reputation_runtime_exists():
    assert RUNTIME_PATH.exists(), f"Missing: {RUNTIME_PATH}"


def test_routing_reputation_runtime_version_token():
    assert ROUTING_REPUTATION_RUNTIME_VERSION == "routing_reputation_runtime_908.v0.1"


def test_cdl_078_dependency_token():
    assert CDL_078_DEPENDENCY == "cdl_078_relay_incentive_constitutional_lock.v0.1"


def test_cdl_060_dependency_token():
    assert CDL_060_DEPENDENCY == "cdl_060_ratified_541.v0.1"


def test_cdl_077_dependency_token():
    assert CDL_077_DEPENDENCY == "cdl_077_want_have_want_block_fetch.v0.1"


def test_cdl_078_dependency_in_fetch_runtime():
    assert FETCH_CDL_078_DEPENDENCY == "cdl_078_relay_incentive_constitutional_lock.v0.1"


# ---------------------------------------------------------------------------
# Group 2: Constants
# ---------------------------------------------------------------------------


def test_serve_centrality_delta_value():
    assert isinstance(SERVE_CENTRALITY_DELTA, float)
    assert 0.0 < SERVE_CENTRALITY_DELTA <= 0.10


def test_serve_centrality_max_per_epoch_value():
    assert isinstance(SERVE_CENTRALITY_MAX_PER_EPOCH, float)
    assert SERVE_CENTRALITY_MAX_PER_EPOCH >= SERVE_CENTRALITY_DELTA


def test_serve_centrality_delta_is_0_01():
    assert SERVE_CENTRALITY_DELTA == 0.01


def test_serve_centrality_max_per_epoch_is_0_10():
    assert SERVE_CENTRALITY_MAX_PER_EPOCH == 0.10


# ---------------------------------------------------------------------------
# Group 3: record_serve_event
# ---------------------------------------------------------------------------


def test_record_serve_event_single():
    state = new_reputation_state()
    record_serve_event("bafytest001", 100, state)
    assert state["serve_buffer"][100]["bafytest001"] == 1


def test_record_serve_event_accumulates():
    state = new_reputation_state()
    record_serve_event("bafytest001", 100, state)
    record_serve_event("bafytest001", 100, state)
    assert state["serve_buffer"][100]["bafytest001"] == 2


def test_record_serve_event_different_nodes_independent():
    state = new_reputation_state()
    record_serve_event("bafytest001", 100, state)
    record_serve_event("bafytest002", 100, state)
    assert state["serve_buffer"][100]["bafytest001"] == 1
    assert state["serve_buffer"][100]["bafytest002"] == 1


def test_record_serve_event_different_epochs():
    state = new_reputation_state()
    record_serve_event("bafytest001", 100, state)
    record_serve_event("bafytest001", 101, state)
    assert state["serve_buffer"][100]["bafytest001"] == 1
    assert state["serve_buffer"][101]["bafytest001"] == 1


def test_record_serve_event_never_raises_on_bad_input():
    # Best-effort — must not raise on garbage input
    record_serve_event("", 100, {})
    record_serve_event("bafytest001", -1, {})
    record_serve_event("bafytest001", 100, None)  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# Group 4: flush_epoch_serve_events
# ---------------------------------------------------------------------------


def test_flush_single_serve_produces_correct_delta():
    state = new_reputation_state()
    centrality_state = {}
    record_serve_event("bafytest001", 100, state)

    with patch(
        "ilc_core.network.d2d.routing_reputation_runtime.accumulate_centrality_delta"
    ) as mock_acc:
        receipt = flush_epoch_serve_events(100, state, centrality_state)

    mock_acc.assert_called_once_with("bafytest001", SERVE_CENTRALITY_DELTA, 100, centrality_state)
    assert receipt["nodes_flushed"] == 1
    assert abs(receipt["total_delta_emitted"] - SERVE_CENTRALITY_DELTA) < 1e-9


def test_flush_cap_enforced():
    """Many serves for same node should be capped at SERVE_CENTRALITY_MAX_PER_EPOCH."""
    state = new_reputation_state()
    centrality_state = {}
    # 20 serves × 0.01 = 0.20, but cap is 0.10
    for _ in range(20):
        record_serve_event("bafytest001", 100, state)

    with patch(
        "ilc_core.network.d2d.routing_reputation_runtime.accumulate_centrality_delta"
    ) as mock_acc:
        flush_epoch_serve_events(100, state, centrality_state)

    args = mock_acc.call_args[0]
    assert args[1] == SERVE_CENTRALITY_MAX_PER_EPOCH


def test_flush_clears_epoch_buffer():
    state = new_reputation_state()
    centrality_state = {}
    record_serve_event("bafytest001", 100, state)
    with patch("ilc_core.network.d2d.routing_reputation_runtime.accumulate_centrality_delta"):
        flush_epoch_serve_events(100, state, centrality_state)
    assert 100 not in state["serve_buffer"]


def test_flush_writes_receipt_to_flush_log():
    state = new_reputation_state()
    centrality_state = {}
    record_serve_event("bafytest001", 100, state)
    with patch("ilc_core.network.d2d.routing_reputation_runtime.accumulate_centrality_delta"):
        flush_epoch_serve_events(100, state, centrality_state)
    assert len(state["flush_log"]) == 1
    assert state["flush_log"][0]["epoch"] == 100


def test_flush_empty_epoch_is_noop():
    state = new_reputation_state()
    centrality_state = {}
    with patch(
        "ilc_core.network.d2d.routing_reputation_runtime.accumulate_centrality_delta"
    ) as mock_acc:
        receipt = flush_epoch_serve_events(100, state, centrality_state)
    mock_acc.assert_not_called()
    assert receipt["nodes_flushed"] == 0


# ---------------------------------------------------------------------------
# Group 5: handle_want_block_request wiring
# ---------------------------------------------------------------------------


@pytest.fixture()
def mock_store_with_node():
    store = MagicMock()
    record = {"primitive": "assert.truth", "node_id": "bafytest001", "agent_id": "agent-001", "epoch": 1}
    store.get_node.side_effect = lambda nid: record if nid == "bafytest001" else None
    return store


@pytest.fixture()
def rate_limiter():
    return FetchRateLimiter()


def test_want_block_success_records_serve_event(mock_store_with_node, rate_limiter):
    """200 response → record_serve_event called."""
    _reset_global_state()
    body = json.dumps({"node_id": "bafytest001", "requester_id": "agent-001"}).encode()

    with patch(
        "ilc_core.network.d2d.routing_reputation_runtime.record_serve_event"
    ) as mock_record:
        status, _ = handle_want_block_request(body, mock_store_with_node, rate_limiter)

    assert status == 200
    mock_record.assert_called_once()
    call_args = mock_record.call_args[0]
    assert call_args[0] == "bafytest001"  # node_id


def test_want_block_404_no_serve_event(rate_limiter):
    """404 (node not found) → no serve event recorded."""
    store = MagicMock()
    store.get_node.return_value = None
    body = json.dumps({"node_id": "bafymissing", "requester_id": "agent-001"}).encode()

    with patch(
        "ilc_core.network.d2d.routing_reputation_runtime.record_serve_event"
    ) as mock_record:
        status, _ = handle_want_block_request(body, store, rate_limiter)

    assert status == 404
    mock_record.assert_not_called()


def test_want_block_429_no_serve_event(mock_store_with_node):
    """Rate-limited response → no serve event recorded."""
    limiter = FetchRateLimiter(limit_per_minute=1)
    body = json.dumps({"node_id": "bafytest001", "requester_id": "agent-throttled"}).encode()
    handle_want_block_request(body, mock_store_with_node, limiter)  # consume limit

    with patch(
        "ilc_core.network.d2d.routing_reputation_runtime.record_serve_event"
    ) as mock_record:
        status, _ = handle_want_block_request(body, mock_store_with_node, limiter)

    assert status == 429
    mock_record.assert_not_called()


def test_want_block_503_no_serve_event(rate_limiter):
    """Store absent → no serve event recorded."""
    body = json.dumps({"node_id": "bafytest001", "requester_id": "agent-001"}).encode()

    with patch(
        "ilc_core.network.d2d.routing_reputation_runtime.record_serve_event"
    ) as mock_record:
        status, _ = handle_want_block_request(body, None, rate_limiter)

    assert status == 503
    mock_record.assert_not_called()


# ---------------------------------------------------------------------------
# Group 6: No negative centrality delta
# ---------------------------------------------------------------------------


def test_flush_never_produces_negative_delta():
    """flush_epoch_serve_events must only call accumulate_centrality_delta with delta >= 0."""
    state = new_reputation_state()
    centrality_state = {}
    record_serve_event("bafytest001", 100, state)

    deltas_seen = []

    def capture_delta(_node_id, delta, _epoch, _c_state):
        deltas_seen.append(delta)

    with patch(
        "ilc_core.network.d2d.routing_reputation_runtime.accumulate_centrality_delta",
        side_effect=capture_delta,
    ):
        flush_epoch_serve_events(100, state, centrality_state)

    assert all(d >= 0.0 for d in deltas_seen), f"Negative delta found: {deltas_seen}"


# ---------------------------------------------------------------------------
# Group 7: No per-hop ECU in routing_reputation_runtime.py
# ---------------------------------------------------------------------------


def test_no_ecu_transfer_in_routing_reputation_runtime():
    source = RUNTIME_PATH.read_text(encoding="utf-8")
    # Confirm there is no ECU transfer or ledger write function call
    forbidden = ["transfer_ecu", "ledger_write", "ecu_transfer", "pay_ecu", "deduct_ecu"]
    for term in forbidden:
        assert term not in source, f"Forbidden term '{term}' found in routing_reputation_runtime.py"


# ---------------------------------------------------------------------------
# Group 8: CDL-078 in master log
# ---------------------------------------------------------------------------


def test_cdl_078_row_in_master_log():
    text = CDL_LOG_PATH.read_text(encoding="utf-8")
    assert "CDL-078" in text, "CDL-078 row not found in CDL master log"
    assert "opened_phase: 907" in text


# ---------------------------------------------------------------------------
# Group 9: Commit scope guard
# ---------------------------------------------------------------------------


def _resolve_phase_910_commit_ref() -> str | None:
    result = subprocess.run(
        ["git", "log", "--oneline", "--all"],
        capture_output=True, text=True, check=False,
    )
    for line in result.stdout.splitlines():
        if PHASE_910_COMMIT_SUBJECT in line:
            return line.split()[0]
    return None


def test_phase_910_commit_scope_guard():
    ref = _resolve_phase_910_commit_ref()
    if ref is None:
        pytest.skip("Phase 910 commit not yet present")

    result = subprocess.run(
        ["git", "diff-tree", "--no-commit-id", "-r", "--name-only", ref],
        capture_output=True, text=True, check=False,
    )
    changed = [f.strip() for f in result.stdout.splitlines() if f.strip()]
    allowed_prefixes = ("ilc_core/network/d2d/", "tests/", "docs/")
    forbidden = [f for f in changed if not any(f.startswith(p) for p in allowed_prefixes)]
    assert not forbidden, f"Phase 910 commit touches out-of-scope files: {forbidden}"
