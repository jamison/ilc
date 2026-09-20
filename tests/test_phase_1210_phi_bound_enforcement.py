from decimal import Decimal

import pytest

from ilc_core.economics.epoch_attribution_settle_runtime import (
    AttributionEvent,
    EPOCH_ATTRIBUTION_SETTLE_RUNTIME_VERSION,
    settle_attribution_batch,
)
from ilc_core.encoding.cidv1 import node_id_from_obj
from ilc_core.types import (
    EDGE_MINT_PHI_BOUND,
    EdgeType,
    EpochAttributionBatch,
    REUSE_ATTRIBUTION_RATE,
)


def _agent_id(index: int) -> str:
    return f"{index:096x}"


def _node_id(label: str) -> str:
    return node_id_from_obj({"phase": 1210, "label": label})


COAUTHOR_NODE_ID = _node_id("coauthor")


def _batch(events: list[AttributionEvent]) -> EpochAttributionBatch:
    batch = EpochAttributionBatch(epoch=1)
    for event in events:
        batch.add_event(event)
    batch.seal()
    return batch


def _provenance_event(index: int) -> AttributionEvent:
    return AttributionEvent(
        edge_type=EdgeType.PROVENANCE,
        target_creator_id=_agent_id(900),
        star_node_id=None,
        epoch=1,
        provenance_chain=((_node_id(f"node-{index}"), _agent_id(index)),),
    )


def _reuse_event(index: int) -> AttributionEvent:
    return AttributionEvent(
        edge_type=EdgeType.REUSE,
        target_creator_id=_agent_id(index),
        star_node_id=None,
        epoch=1,
    )


def _co_authorship_event() -> AttributionEvent:
    return AttributionEvent(
        edge_type=EdgeType.CO_AUTHORSHIP,
        target_creator_id=_agent_id(900),
        star_node_id=COAUTHOR_NODE_ID,
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

    assert [amount for _, amount in payouts] == [Decimal("0.090000000"), Decimal("0.090000000")]
    assert emitted_tokens == ["edge_mint_phi_bound_enforcement_skipped_no_node_mints"]


def test_phi_bound_allows_events_below_threshold() -> None:
    payouts = settle_attribution_batch(
        _batch([_provenance_event(1), _provenance_event(2), _provenance_event(3)]),
        stake_map={},
        epoch_node_mint_count=5,
    )

    assert len(payouts) == 3
    assert all(amount == Decimal("0.090000000") for _, amount in payouts)


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
        Decimal("0.090000000"),
        Decimal("0.090000000"),
        Decimal("0.090000000"),
    ]
    assert emitted_tokens == ["edge_mint_phi_bound_exceeded"]


def test_phi_bound_strips_ecu_above_threshold() -> None:
    payouts = settle_attribution_batch(
        _batch([_provenance_event(i) for i in range(1, 7)]),
        stake_map={},
        epoch_node_mint_count=5,
    )

    assert len(payouts) == 3
    assert all(amount == Decimal("0.090000000") for _, amount in payouts)


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
        stake_map={COAUTHOR_NODE_ID: {_agent_id(101): Decimal("1"), _agent_id(102): Decimal("1")}},
        epoch_node_mint_count=1,
    )

    assert payouts == [
        (_agent_id(101), Decimal("0.100000000")),
        (_agent_id(102), Decimal("0.100000000")),
        (_agent_id(101), Decimal("0.100000000")),
        (_agent_id(102), Decimal("0.100000000")),
    ]


def test_phi_bound_uses_decimal_not_float() -> None:
    assert isinstance(EDGE_MINT_PHI_BOUND, Decimal)
    assert not isinstance(EDGE_MINT_PHI_BOUND, float)


def test_runtime_version_contains_1210() -> None:
    assert (
        EPOCH_ATTRIBUTION_SETTLE_RUNTIME_VERSION
        == "epoch_attribution_settle_runtime_GAP_CDL060.v0.8"
    )


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

    assert (_agent_id(4), Decimal("0")) not in payouts
    assert [creator_id for creator_id, _ in payouts] == [_agent_id(1), _agent_id(2), _agent_id(3)]
    assert emitted_tokens == ["edge_mint_phi_bound_exceeded"]


def test_negative_epoch_node_mint_count_raises() -> None:
    with pytest.raises(ValueError, match="epoch_node_mint_count_must_be_non_negative"):
        settle_attribution_batch(
            _batch([_provenance_event(1)]),
            stake_map={},
            epoch_node_mint_count=-1,
        )
