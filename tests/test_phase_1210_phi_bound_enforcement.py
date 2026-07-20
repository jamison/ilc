from decimal import Decimal

import pytest

from ilc_core.economics.epoch_attribution_settle_runtime import (
    AttributionEvent,
    EPOCH_ATTRIBUTION_SETTLE_RUNTIME_VERSION,
    settle_attribution_batch,
)
from ilc_core.types import (
    EDGE_MINT_PHI_BOUND,
    EdgeType,
    EpochAttributionBatch,
    REUSE_ATTRIBUTION_RATE,
)


def _batch(events: list[AttributionEvent]) -> EpochAttributionBatch:
    batch = EpochAttributionBatch(epoch=1)
    for event in events:
        batch.add_event(event)
    batch.seal()
    return batch


def _provenance_event(index: int) -> AttributionEvent:
    return AttributionEvent(
        edge_type=EdgeType.PROVENANCE,
        target_creator_id="unused_target_creator",
        star_node_id=None,
        epoch=1,
        provenance_chain=((f"node_{index}", f"creator_{index}"),),
    )


def _reuse_event(index: int) -> AttributionEvent:
    return AttributionEvent(
        edge_type=EdgeType.REUSE,
        target_creator_id=f"reuse_creator_{index}",
        star_node_id=None,
        epoch=1,
    )


def _co_authorship_event() -> AttributionEvent:
    return AttributionEvent(
        edge_type=EdgeType.CO_AUTHORSHIP,
        target_creator_id="unused_target_creator",
        star_node_id="star:one",
        epoch=1,
    )


def test_phi_bound_skips_enforcement_when_node_mint_count_zero_emits_token() -> None:
    emitted_tokens: list[str] = []
    payouts = settle_attribution_batch(
        _batch([_provenance_event(1), _provenance_event(2)]),
        stake_map={},
        emitted_tokens=emitted_tokens,
        epoch_node_mint_count=0,
    )

    assert [amount for _, amount in payouts] == [Decimal("0.0900"), Decimal("0.0900")]
    assert "edge_mint_phi_bound_enforcement_skipped_no_node_mints" in emitted_tokens


def test_phi_bound_allows_events_below_threshold() -> None:
    payouts = settle_attribution_batch(
        _batch([_provenance_event(1), _provenance_event(2), _provenance_event(3)]),
        stake_map={},
        epoch_node_mint_count=5,
    )

    assert len(payouts) == 3
    assert all(amount == Decimal("0.0900") for _, amount in payouts)


def test_phi_bound_strips_ecu_at_threshold() -> None:
    emitted_tokens: list[str] = []
    payouts = settle_attribution_batch(
        _batch([
            _provenance_event(1),
            _provenance_event(2),
            _provenance_event(3),
            _provenance_event(4),
        ]),
        stake_map={},
        emitted_tokens=emitted_tokens,
        epoch_node_mint_count=5,
    )

    assert [amount for _, amount in payouts] == [
        Decimal("0.0900"),
        Decimal("0.0900"),
        Decimal("0.0900"),
    ]
    assert "edge_mint_phi_bound_exceeded" in emitted_tokens


def test_phi_bound_strips_ecu_above_threshold() -> None:
    payouts = settle_attribution_batch(
        _batch([_provenance_event(i) for i in range(1, 7)]),
        stake_map={},
        epoch_node_mint_count=5,
    )

    assert len(payouts) == 3
    assert all(amount == Decimal("0.0900") for _, amount in payouts)


def test_phi_bound_does_not_affect_reuse_events() -> None:
    payouts = settle_attribution_batch(
        _batch([_reuse_event(i) for i in range(1, 7)]),
        stake_map={},
        epoch_node_mint_count=1,
    )

    assert len(payouts) == 6
    assert all(amount == REUSE_ATTRIBUTION_RATE for _, amount in payouts)


def test_phi_bound_does_not_affect_co_authorship_events() -> None:
    payouts = settle_attribution_batch(
        _batch([_co_authorship_event(), _co_authorship_event()]),
        stake_map={"star:one": {"member_a": Decimal("1"), "member_b": Decimal("1")}},
        epoch_node_mint_count=1,
    )

    assert payouts == [
        ("member_a", Decimal("0.10")),
        ("member_b", Decimal("0.10")),
        ("member_a", Decimal("0.10")),
        ("member_b", Decimal("0.10")),
    ]


def test_phi_bound_uses_decimal_not_float() -> None:
    assert isinstance(EDGE_MINT_PHI_BOUND, Decimal)
    assert not isinstance(EDGE_MINT_PHI_BOUND, float)


def test_runtime_version_contains_1210() -> None:
    assert "1210" in EPOCH_ATTRIBUTION_SETTLE_RUNTIME_VERSION
    assert "v0.7" in EPOCH_ATTRIBUTION_SETTLE_RUNTIME_VERSION


def test_batch_settle_method_forwards_epoch_node_mint_count() -> None:
    emitted_tokens: list[str] = []
    payouts = _batch([
        _provenance_event(1),
        _provenance_event(2),
        _provenance_event(3),
        _provenance_event(4),
    ]).settle(
        stake_map={},
        emitted_tokens=emitted_tokens,
        epoch_node_mint_count=5,
    )

    assert ("creator_4", Decimal("0")) not in payouts
    assert [creator_id for creator_id, _ in payouts] == ["creator_1", "creator_2", "creator_3"]
    assert "edge_mint_phi_bound_exceeded" in emitted_tokens


def test_negative_epoch_node_mint_count_raises() -> None:
    with pytest.raises(ValueError, match="epoch_node_mint_count_must_be_non_negative"):
        settle_attribution_batch(
            _batch([_provenance_event(1)]),
            stake_map={},
            epoch_node_mint_count=-1,
        )
