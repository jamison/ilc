from __future__ import annotations

from decimal import Decimal

import pytest

from ilc_core.economics import passive_ecu_attribution_runtime as passive_runtime
from ilc_core.network.d2d import centrality_delta_gossip_runtime as centrality_runtime
from ilc_core.network.d2d import http_gossip_transport_runtime as http_runtime
from ilc_core.network.d2d import routing_reputation_runtime as reputation_runtime


def test_centrality_delta_is_authority_bearing_gossip_type() -> None:
    assert "centrality_delta" in http_runtime.AUTHORITY_BEARING_GOSSIP_TYPES
    assert (
        http_runtime._unverifiable_peer_rejection_token("centrality_delta")
        == http_runtime.UNVERIFIABLE_AUTHORITY_GOSSIP_REJECTED_TOKEN
    )


def test_below_floor_centrality_delta_does_not_allocate_pending_buffer() -> None:
    state: dict[str, object] = {}

    updated = centrality_runtime.accumulate_centrality_delta(
        "node-alpha",
        Decimal("0.000000000001"),
        7,
        state,
    )

    assert updated is state
    assert "_pending" not in state


def test_centrality_decimal_magnitude_rejected_before_quantize() -> None:
    with pytest.raises(
        ValueError,
        match=centrality_runtime.CENTRALITY_DECIMAL_MAGNITUDE_TOKEN,
    ):
        centrality_runtime.accumulate_centrality_delta(
            "node-alpha",
            Decimal("1e1000000"),
            1,
            {},
        )


def test_centrality_pending_epoch_node_cap_is_enforced() -> None:
    epoch_buffer = {
        f"node-{index}": Decimal("0.050000000000")
        for index in range(centrality_runtime.MAX_PENDING_NODES_PER_EPOCH)
    }
    state = {"_pending": {1: epoch_buffer}}

    with pytest.raises(ValueError, match="centrality_pending_epoch_node_cap_exceeded"):
        centrality_runtime.accumulate_centrality_delta(
            "node-overflow",
            Decimal("0.05"),
            1,
            state,
        )


def test_centrality_pending_epoch_cap_is_enforced() -> None:
    state = {
        "_pending": {
            epoch: {"node-alpha": Decimal("0.050000000000")}
            for epoch in range(centrality_runtime.MAX_PENDING_EPOCHS)
        }
    }

    with pytest.raises(ValueError, match="centrality_pending_epoch_cap_exceeded"):
        centrality_runtime.accumulate_centrality_delta(
            "node-alpha",
            Decimal("0.05"),
            centrality_runtime.MAX_PENDING_EPOCHS,
            state,
        )


def test_commit_epoch_buffer_preserves_oversized_buffer_on_rejection() -> None:
    state = {
        "_pending": {
            1: {
                f"node-{index}": Decimal("0.050000000000")
                for index in range(centrality_runtime.MAX_PENDING_NODES_PER_EPOCH + 1)
            }
        }
    }

    with pytest.raises(ValueError, match="centrality_pending_epoch_node_cap_exceeded"):
        centrality_runtime.commit_epoch_buffer(1, state)

    assert 1 in state["_pending"]
    assert len(state["_pending"][1]) == centrality_runtime.MAX_PENDING_NODES_PER_EPOCH + 1


def test_passive_ecu_decimal_magnitude_rejected_before_quantize() -> None:
    with pytest.raises(
        ValueError,
        match=passive_runtime.PASSIVE_ECU_DECIMAL_MAGNITUDE_TOKEN,
    ):
        passive_runtime.compute_passive_ecu(
            Decimal("1e1000000"),
            Decimal("0.5"),
            Decimal("0.5"),
        )


def test_passive_ecu_uses_decimal_error_tokens() -> None:
    with pytest.raises(ValueError, match=passive_runtime.Q_I_DECIMAL_INTERVAL_TOKEN):
        passive_runtime.quality_factor(Decimal("1.01"))
    with pytest.raises(ValueError, match=passive_runtime.BASE_REWARD_DECIMAL_TOKEN):
        passive_runtime.compute_passive_ecu(Decimal("-1"), Decimal("0.5"), Decimal("0.5"))
    with pytest.raises(ValueError, match=passive_runtime.CENTRALITY_SCORE_DECIMAL_TOKEN):
        passive_runtime.compute_passive_ecu(Decimal("1"), Decimal("1.01"), Decimal("0.5"))


def test_reputation_buffer_caps_epochs_and_nodes_without_raising() -> None:
    state = reputation_runtime.new_reputation_state()

    for epoch in range(reputation_runtime.MAX_SERVE_BUFFER_EPOCHS):
        reputation_runtime.record_serve_event("node-alpha", epoch, state)
    reputation_runtime.record_serve_event(
        "node-alpha",
        reputation_runtime.MAX_SERVE_BUFFER_EPOCHS,
        state,
    )

    assert len(state["serve_buffer"]) == reputation_runtime.MAX_SERVE_BUFFER_EPOCHS
    assert 0 in state["serve_buffer"]
    assert reputation_runtime.MAX_SERVE_BUFFER_EPOCHS not in state["serve_buffer"]

    crowded_epoch = max(state["serve_buffer"]) + 1
    state["serve_buffer"].pop(0)
    for index in range(reputation_runtime.MAX_SERVE_BUFFER_NODES_PER_EPOCH):
        reputation_runtime.record_serve_event(f"node-{index}", crowded_epoch, state)
    reputation_runtime.record_serve_event("node-overflow", crowded_epoch, state)

    assert len(state["serve_buffer"][crowded_epoch]) == (
        reputation_runtime.MAX_SERVE_BUFFER_NODES_PER_EPOCH
    )
    assert "node-overflow" not in state["serve_buffer"][crowded_epoch]


def test_reputation_flush_rejects_malicious_oversized_epoch_buffer() -> None:
    state = reputation_runtime.new_reputation_state()
    state["serve_buffer"][1] = {
        f"node-{index}": 1
        for index in range(reputation_runtime.MAX_SERVE_BUFFER_NODES_PER_EPOCH + 1)
    }

    with pytest.raises(ValueError, match="serve_buffer_epoch_node_cap_exceeded"):
        reputation_runtime.flush_epoch_serve_events(1, state, {})

    assert 1 in state["serve_buffer"]


def test_reputation_flush_log_is_bounded() -> None:
    state = reputation_runtime.new_reputation_state()

    for epoch in range(reputation_runtime.MAX_FLUSH_LOG_ENTRIES + 1):
        reputation_runtime.flush_epoch_serve_events(epoch, state, {})

    assert len(state["flush_log"]) == reputation_runtime.MAX_FLUSH_LOG_ENTRIES
    assert state["flush_log"][0]["epoch"] == 1
