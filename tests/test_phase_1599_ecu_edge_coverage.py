from decimal import Decimal

import pytest

from ilc_core.economics.epoch_attribution_settle_runtime import (
    AttributionEvent,
    settle_attribution_batch,
)
from ilc_core.types import (
    EdgeType,
    EpochAttributionBatch,
    PROVENANCE_DECAY_ALPHA,
    REUSE_ATTRIBUTION_RATE,
    WeightParams,
)


VALID_CREATOR_ID = "a" * 96
VALID_STAR_NODE_ID = "bafyreihqyyhtogvgz6ndvkkkurdhz45n5jv3ovtgo56oqcrpariwx46dji"
VALID_SOURCE_NODE_ID = "bafyreiavq66ph6u7c4tihdb7ym3lr4w3h5oskfzs3cafbykzghj2sy5wqa"


def _make_batch(*events: AttributionEvent, epoch: int = 1) -> EpochAttributionBatch:
    batch = EpochAttributionBatch(epoch=epoch)
    for event in events:
        batch.add_event(event)
    batch.seal()
    return batch


def _co_authorship_event(star_node_id: str = VALID_STAR_NODE_ID) -> AttributionEvent:
    return AttributionEvent(
        edge_type=EdgeType.CO_AUTHORSHIP,
        target_creator_id=VALID_CREATOR_ID,
        star_node_id=star_node_id,
        epoch=1,
    )


def _refutation_event(refuting_agent_id: str | None = "b" * 96) -> AttributionEvent:
    return AttributionEvent(
        edge_type=EdgeType.REFUTATION,
        target_creator_id=VALID_CREATOR_ID,
        star_node_id=None,
        epoch=1,
        refuting_agent_id=refuting_agent_id,
    )


def _provenance_event(
    chain: tuple[tuple[str, str], ...],
    *,
    target_creator_id: str = VALID_CREATOR_ID,
) -> AttributionEvent:
    return AttributionEvent(
        edge_type=EdgeType.PROVENANCE,
        target_creator_id=target_creator_id,
        star_node_id=None,
        epoch=1,
        provenance_chain=chain,
    )


def test_co_authorship_single_member_full_attribution() -> None:
    event = _co_authorship_event("star:single")
    payouts = settle_attribution_batch(
        _make_batch(event),
        stake_map={"star:single": {"c" * 96: Decimal("1")}},
    )

    assert payouts == [("c" * 96, REUSE_ATTRIBUTION_RATE)]


def test_co_authorship_proportional_split_two_members_conserves_total() -> None:
    event = _co_authorship_event("star:split")
    payouts = settle_attribution_batch(
        _make_batch(event),
        stake_map={"star:split": {"a" * 96: Decimal("3"), "b" * 96: Decimal("7")}},
    )
    payout_dict = dict(payouts)

    assert sum(payout_dict.values(), Decimal("0")) == REUSE_ATTRIBUTION_RATE
    assert payout_dict["a" * 96] == Decimal("0.060000000")
    assert payout_dict["b" * 96] == Decimal("0.140000000")
    assert payout_dict["b" * 96] > payout_dict["a" * 96]


def test_co_authorship_sorted_residual_is_deterministic() -> None:
    event = _co_authorship_event("star:residual")
    stake_map = {"star:residual": {"c" * 96: Decimal("1"), "a" * 96: Decimal("1"), "b" * 96: Decimal("1")}}

    payouts = settle_attribution_batch(_make_batch(event), stake_map=stake_map)

    assert [agent_id for agent_id, _ in payouts] == ["a" * 96, "b" * 96, "c" * 96]
    assert sum(amount for _, amount in payouts) == REUSE_ATTRIBUTION_RATE
    assert payouts[-1][1] == REUSE_ATTRIBUTION_RATE - payouts[0][1] - payouts[1][1]


def test_co_authorship_zero_members_no_payout_emits_commons_token() -> None:
    event = _co_authorship_event("star:empty")
    emitted_tokens: list[str] = []

    payouts = settle_attribution_batch(
        _make_batch(event),
        stake_map={},
        emitted_tokens=emitted_tokens,
    )

    assert payouts == []
    assert emitted_tokens == ["cdl_081_zero_member_commons_transition"]


def test_refutation_pays_refuting_agent() -> None:
    payouts = settle_attribution_batch(_make_batch(_refutation_event("d" * 96)), stake_map={})

    assert payouts == [("d" * 96, REUSE_ATTRIBUTION_RATE)]


def test_refutation_does_not_pay_target_creator() -> None:
    payouts = settle_attribution_batch(_make_batch(_refutation_event("d" * 96)), stake_map={})
    recipient_ids = [agent_id for agent_id, _ in payouts]

    assert "d" * 96 in recipient_ids
    assert VALID_CREATOR_ID not in recipient_ids


def test_refutation_missing_refuting_agent_raises() -> None:
    with pytest.raises(ValueError) as exc_info:
        settle_attribution_batch(_make_batch(_refutation_event(None)), stake_map={})

    assert str(exc_info.value) == "refutation_event_missing_refuting_agent_id"


def test_provenance_three_hop_geometric_decay() -> None:
    chain = (
        (f"{VALID_SOURCE_NODE_ID}:1", "a" * 96),
        (f"{VALID_SOURCE_NODE_ID}:2", "b" * 96),
        (f"{VALID_SOURCE_NODE_ID}:3", "c" * 96),
    )

    payouts = settle_attribution_batch(
        _make_batch(_provenance_event(chain)),
        stake_map={},
        epoch_node_mint_count=5,
    )
    payout_dict = dict(payouts)

    assert payout_dict["a" * 96] == (REUSE_ATTRIBUTION_RATE * PROVENANCE_DECAY_ALPHA**1).quantize(Decimal("0.000000001"))
    assert payout_dict["b" * 96] == (REUSE_ATTRIBUTION_RATE * PROVENANCE_DECAY_ALPHA**2).quantize(Decimal("0.000000001"))
    assert payout_dict["c" * 96] == (REUSE_ATTRIBUTION_RATE * PROVENANCE_DECAY_ALPHA**3).quantize(Decimal("0.000000001"))


def test_provenance_max_depth_hop4_not_paid_but_earlier_hops_are_paid() -> None:
    chain = (
        (f"{VALID_SOURCE_NODE_ID}:1", "a" * 96),
        (f"{VALID_SOURCE_NODE_ID}:2", "b" * 96),
        (f"{VALID_SOURCE_NODE_ID}:3", "c" * 96),
        (f"{VALID_SOURCE_NODE_ID}:4", "d" * 96),
    )

    payouts = settle_attribution_batch(
        _make_batch(_provenance_event(chain)),
        stake_map={},
        epoch_node_mint_count=5,
    )
    recipient_ids = [agent_id for agent_id, _ in payouts]

    assert recipient_ids == ["a" * 96, "b" * 96, "c" * 96]
    assert "d" * 96 not in recipient_ids


def test_provenance_duplicate_creator_nearest_hop_wins() -> None:
    chain = (
        (f"{VALID_SOURCE_NODE_ID}:1", "a" * 96),
        (f"{VALID_SOURCE_NODE_ID}:2", "a" * 96),
        (f"{VALID_SOURCE_NODE_ID}:3", "b" * 96),
    )

    payouts = settle_attribution_batch(
        _make_batch(_provenance_event(chain)),
        stake_map={},
        epoch_node_mint_count=5,
    )
    shared_payouts = [(agent_id, amount) for agent_id, amount in payouts if agent_id == "a" * 96]

    assert len(shared_payouts) == 1
    assert shared_payouts[0][1] == (
        REUSE_ATTRIBUTION_RATE * PROVENANCE_DECAY_ALPHA**1
    ).quantize(Decimal("0.000000001"))
    assert ("b" * 96, (REUSE_ATTRIBUTION_RATE * PROVENANCE_DECAY_ALPHA**3).quantize(Decimal("0.000000001"))) in payouts


def test_provenance_phi_bound_exceeded_suppresses_second_event() -> None:
    event_1 = _provenance_event(((f"{VALID_SOURCE_NODE_ID}:1", "a" * 96),))
    event_2 = _provenance_event(((f"{VALID_SOURCE_NODE_ID}:2", "b" * 96),))
    emitted_tokens: list[str] = []

    payouts = settle_attribution_batch(
        _make_batch(event_1, event_2),
        stake_map={},
        epoch_node_mint_count=1,
        emitted_tokens=emitted_tokens,
    )

    assert [agent_id for agent_id, _ in payouts] == ["a" * 96]
    assert "b" * 96 not in [agent_id for agent_id, _ in payouts]
    assert emitted_tokens == ["edge_mint_phi_bound_exceeded"]


def test_provenance_epoch_no_node_mints_phi_check_skipped() -> None:
    emitted_tokens: list[str] = []

    payouts = settle_attribution_batch(
        _make_batch(_provenance_event(((f"{VALID_SOURCE_NODE_ID}:1", "a" * 96),))),
        stake_map={},
        epoch_node_mint_count=0,
        emitted_tokens=emitted_tokens,
    )

    assert payouts == [("a" * 96, Decimal("0.090000000"))]
    assert emitted_tokens == ["edge_mint_phi_bound_enforcement_skipped_no_node_mints"]


def test_weight_params_old_float_decay_rate_rejection_token() -> None:
    with pytest.raises(ValueError) as exc_info:
        WeightParams(
            stake=Decimal("1"),
            reuse_count=0,
            decay_rate=0.95,
            edge_type_coefficient=Decimal("1.0"),
        )

    assert str(exc_info.value) == "weight_decay_rate_invalid"


def test_weight_params_old_float_edge_type_coefficient_rejection_token() -> None:
    with pytest.raises(ValueError) as exc_info:
        WeightParams(
            stake=Decimal("1"),
            reuse_count=0,
            decay_rate=Decimal("0.95"),
            edge_type_coefficient=1.0,
        )

    assert str(exc_info.value) == "weight_edge_type_coefficient_invalid"


@pytest.mark.parametrize("edge_type", [EdgeType.ATTESTATION, EdgeType.EPOCH_BOUNDARY])
def test_non_settlement_edge_types_silently_skip(edge_type: EdgeType) -> None:
    event = AttributionEvent(
        edge_type=edge_type,
        target_creator_id=VALID_CREATOR_ID,
        star_node_id=VALID_STAR_NODE_ID,
        epoch=1,
    )

    assert settle_attribution_batch(_make_batch(event), stake_map={}) == []


def test_reuse_direct_and_passive_routing_contract_preserved() -> None:
    event = AttributionEvent(
        edge_type=EdgeType.REUSE,
        target_creator_id=VALID_CREATOR_ID,
        star_node_id=VALID_STAR_NODE_ID,
        epoch=1,
    )

    payouts = settle_attribution_batch(
        _make_batch(event),
        stake_map={},
        passive_ecu_centrality_state={
            "_pending": {1: {VALID_STAR_NODE_ID: Decimal("0.15")}}
        },
    )

    assert payouts == [
        (VALID_CREATOR_ID, REUSE_ATTRIBUTION_RATE),
        (VALID_CREATOR_ID, Decimal("0.004000000000")),
    ]
