from __future__ import annotations

from decimal import Decimal

import pytest

from ilc_core.economics import epoch_attribution_settle_runtime as settle_runtime
from ilc_core.economics import passive_ecu_attribution_runtime as passive_runtime
from ilc_core.network.d2d import centrality_delta_gossip_runtime as centrality_runtime
from ilc_core.types import EdgeType, EpochAttributionBatch


def _reuse_batch(node_id: str | None = "node-alpha") -> EpochAttributionBatch:
    batch = EpochAttributionBatch(epoch=1)
    batch.add_event(
        settle_runtime.AttributionEvent(
            edge_type=EdgeType.REUSE,
            target_creator_id="creator-alpha",
            star_node_id=node_id,
            epoch=1,
        )
    )
    batch.seal()
    return batch


def _assert_no_float_values(value: object) -> None:
    if isinstance(value, float):
        raise AssertionError("float_value_found_in_centrality_state")
    if isinstance(value, dict):
        for item in value.values():
            _assert_no_float_values(item)
    elif isinstance(value, (list, tuple, set)):
        for item in value:
            _assert_no_float_values(item)


def test_centrality_delta_gossip_decimal_accumulation() -> None:
    state: dict[str, object] = {}

    centrality_runtime.accumulate_centrality_delta("node-alpha", Decimal("0.2"), 1, state)

    assert state["_pending"][1]["node-alpha"] == Decimal("0.200000000000")
    assert isinstance(state["_pending"][1]["node-alpha"], Decimal)


@pytest.mark.parametrize("bad_delta", [float("nan"), float("inf"), Decimal("NaN")])
def test_centrality_delta_gossip_ingress_non_finite_rejected(bad_delta: object) -> None:
    with pytest.raises(ValueError, match="score_delta_must_be_non_negative_decimal"):
        centrality_runtime.validate_centrality_delta_message(
            {
                "cid": "bafycentralitydelta",
                "score_delta": bad_delta,
                "epoch": 1,
                "signature": "sig-alpha",
                "hop_count": 1,
                "fanout": 3,
                "channel": "cid:9f7a8c42bb11ddee99aa22cc33ff44aa",
            }
        )


def test_centrality_delta_gossip_no_float_in_buffer() -> None:
    state: dict[str, object] = {}

    centrality_runtime.accumulate_centrality_delta("node-alpha", Decimal("0.2"), 1, state)
    centrality_runtime.accumulate_centrality_delta("node-beta", "0.3", 1, state)

    _assert_no_float_values(state)


def test_centrality_delta_gossip_normalization_decimal() -> None:
    state: dict[str, object] = {}

    centrality_runtime.accumulate_centrality_delta("node-alpha", "0.1234567891239", 1, state)

    assert state["_pending"][1]["node-alpha"] == Decimal("0.123456789124")


def test_centrality_delta_gossip_cap_respected() -> None:
    state: dict[str, object] = {}

    centrality_runtime.accumulate_centrality_delta("node-cap", "0.75", 1, state)
    centrality_runtime.accumulate_centrality_delta("node-cap", "0.75", 1, state)

    assert state["_pending"][1]["node-cap"] == centrality_runtime.CENTRALITY_SCORE_CAP


def test_centrality_delta_gossip_rejects_finite_float_ingress() -> None:
    with pytest.raises(ValueError, match="score_delta_must_be_non_negative_decimal"):
        centrality_runtime.validate_centrality_delta_message(
            {
                "cid": "bafycentralitydelta",
                "score_delta": 0.2,
                "epoch": 1,
                "signature": "sig-alpha",
                "hop_count": 1,
                "fanout": 3,
                "channel": "cid:9f7a8c42bb11ddee99aa22cc33ff44aa",
            }
        )
    with pytest.raises(ValueError, match="delta_must_be_non_negative_decimal"):
        centrality_runtime.accumulate_centrality_delta("node-alpha", 0.2, 1, {})


def test_centrality_score_zero_for_unknown_node() -> None:
    assert settle_runtime._get_centrality_score("node-missing", 1, {}) == Decimal("0")


def test_centrality_score_is_capped_to_epoch_passive_ecu_bound() -> None:
    state = {"_pending": {1: {"node-alpha": Decimal("0.50")}}}

    assert settle_runtime._get_centrality_score("node-alpha", 1, state) == Decimal("0.100000000000")


def test_passive_ecu_guard_disabled_returns_zero() -> None:
    payouts = settle_runtime.settle_attribution_batch(
        _reuse_batch(),
        stake_map={},
        passive_ecu_centrality_state={"_pending": {1: {"node-alpha": Decimal("0.10")}}},
        passive_ecu_quality_scores={"node-alpha": Decimal("0.5")},
    )

    assert settle_runtime.PASSIVE_ECU_WIRING_NOT_ACTIVATED is True
    assert payouts == [("creator-alpha", Decimal("0.20"))]


def test_passive_ecu_wiring_active_nonzero(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settle_runtime, "PASSIVE_ECU_WIRING_NOT_ACTIVATED", False)

    payouts = settle_runtime.settle_attribution_batch(
        _reuse_batch(),
        stake_map={},
        passive_ecu_centrality_state={"_pending": {1: {"node-alpha": Decimal("0.10")}}},
        passive_ecu_quality_scores={"node-alpha": Decimal("0.5")},
    )

    assert payouts == [
        ("creator-alpha", Decimal("0.20")),
        ("creator-alpha", Decimal("0.004000000000")),
    ]


def test_passive_ecu_guard_retained_no_settlement_activation() -> None:
    assert settle_runtime.PASSIVE_ECU_WIRING_NOT_ACTIVATED is True
    assert settle_runtime.PASSIVE_ECU_WIRING_GUARD_TOKEN == (
        "passive_ecu_wiring_not_activated_phase_GAP_CDL060"
    )


def test_passive_ecu_base_reward_zero() -> None:
    assert passive_runtime.compute_passive_ecu(
        Decimal("0"),
        Decimal("0.10"),
        Decimal("0.5"),
    ) == Decimal("0")


def test_passive_ecu_centrality_zero() -> None:
    assert passive_runtime.compute_passive_ecu(
        Decimal("0.20"),
        Decimal("0"),
        Decimal("0.5"),
    ) == Decimal("0")


def test_passive_ecu_non_finite_base_reward_rejected() -> None:
    with pytest.raises(ValueError, match="base_reward_must_be_non_negative_float"):
        passive_runtime.compute_passive_ecu(
            Decimal("NaN"),
            Decimal("0.10"),
            Decimal("0.5"),
        )


def test_passive_ecu_quality_extremes_remain_bounded() -> None:
    assert passive_runtime.compute_passive_ecu(
        Decimal("0.20"),
        Decimal("0.10"),
        Decimal("0"),
    ) == Decimal("0.003400000000")
    assert passive_runtime.compute_passive_ecu(
        Decimal("0.20"),
        Decimal("0.10"),
        Decimal("1"),
    ) == Decimal("0.004600000000")


def test_passive_ecu_non_finite_centrality_rejected() -> None:
    with pytest.raises(ValueError, match="centrality_score_must_be_non_negative_float"):
        passive_runtime.compute_passive_ecu(
            Decimal("0.20"),
            Decimal("NaN"),
            Decimal("0.5"),
        )


def test_passive_ecu_cdl_dependency_tokens_present() -> None:
    assert settle_runtime.CDL_052_PASSIVE_ECU_DEPENDENCY == (
        "cdl_052_reuse_centrality_attribution_ratified"
    )
    assert settle_runtime.CDL_060_CENTRALITY_DELTA_DEPENDENCY == (
        "cdl_060_centrality_delta_gossip_ratified"
    )
    assert passive_runtime.CDL_060_GOSSIP_RUNTIME_DEPENDENCY == (
        "centrality_delta_gossip_runtime_GAP_CDL060.v0.2"
    )


def test_passive_ecu_version_token_updated() -> None:
    assert (
        settle_runtime.EPOCH_ATTRIBUTION_SETTLE_RUNTIME_VERSION
        == "epoch_attribution_settle_runtime_GAP_CDL060.v0.8"
    )


def test_epoch_attribution_batch_settle_forwards_passive_ecu_inputs(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settle_runtime, "PASSIVE_ECU_WIRING_NOT_ACTIVATED", False)

    payouts = _reuse_batch().settle(
        {},
        passive_ecu_centrality_state={"_pending": {1: {"node-alpha": Decimal("0.10")}}},
        passive_ecu_quality_scores={"node-alpha": Decimal("0.5")},
    )

    assert payouts[-1] == ("creator-alpha", Decimal("0.004000000000"))
