from decimal import Decimal

import pytest

from ilc_core.economics.epoch_attribution_settle_runtime import (
    AttributionEvent,
    MAX_PROVENANCE_CHAIN_INPUT_LENGTH,
    settle_attribution_batch,
)
from ilc_core.encoding.cidv1 import node_id_from_obj
from ilc_core.types import (
    EdgeType,
    EpochAttributionBatch,
    REUSE_ATTRIBUTION_RATE,
    WeightParams,
)


VALID_CREATOR_ID = "a" * 96
VALID_REFUTING_ID = "d" * 96
PAYOUT_QUANTUM = Decimal("0.000000001")


def _agent_id(index: int) -> str:
    return f"{index:096x}"


def _node_id(label: str) -> str:
    return node_id_from_obj({"phase": 1599, "label": label})


VALID_STAR_NODE_ID = _node_id("reuse-star")
VALID_SOURCE_NODE_ID = _node_id("source")
COAUTHOR_SINGLE_NODE_ID = _node_id("coauthor-single")
COAUTHOR_SPLIT_NODE_ID = _node_id("coauthor-split")
COAUTHOR_RESIDUAL_NODE_ID = _node_id("coauthor-residual")
COAUTHOR_EMPTY_NODE_ID = _node_id("coauthor-empty")
COAUTHOR_ZERO_STAKE_NODE_ID = _node_id("coauthor-zero-stake")


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


def _refutation_event(refuting_agent_id: str | None = VALID_REFUTING_ID) -> AttributionEvent:
    return AttributionEvent(
        edge_type=EdgeType.REFUTATION,
        target_creator_id=VALID_CREATOR_ID,
        star_node_id=None,
        epoch=1,
        refuting_agent_id=refuting_agent_id,
    )


def _reuse_event(
    target_creator_id: str = VALID_CREATOR_ID,
    star_node_id: str | None = VALID_STAR_NODE_ID,
) -> AttributionEvent:
    return AttributionEvent(
        edge_type=EdgeType.REUSE,
        target_creator_id=target_creator_id,
        star_node_id=star_node_id,
        epoch=1,
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
    event = _co_authorship_event(COAUTHOR_SINGLE_NODE_ID)
    payouts = settle_attribution_batch(
        _make_batch(event),
        stake_map={COAUTHOR_SINGLE_NODE_ID: {_agent_id(12): Decimal("1")}},
    )

    assert payouts == [(_agent_id(12), REUSE_ATTRIBUTION_RATE)]


def test_co_authorship_proportional_split_two_members_conserves_total() -> None:
    event = _co_authorship_event(COAUTHOR_SPLIT_NODE_ID)
    payouts = settle_attribution_batch(
        _make_batch(event),
        stake_map={COAUTHOR_SPLIT_NODE_ID: {_agent_id(10): Decimal("3"), _agent_id(11): Decimal("7")}},
    )
    payout_dict = dict(payouts)

    assert sum(payout_dict.values(), Decimal("0")) == REUSE_ATTRIBUTION_RATE
    assert payout_dict[_agent_id(10)] == Decimal("0.060000000")
    assert payout_dict[_agent_id(11)] == Decimal("0.140000000")
    assert payout_dict[_agent_id(11)] > payout_dict[_agent_id(10)]


def test_co_authorship_sorted_residual_is_deterministic() -> None:
    event = _co_authorship_event(COAUTHOR_RESIDUAL_NODE_ID)
    stake_map = {
        COAUTHOR_RESIDUAL_NODE_ID: {
            _agent_id(13): Decimal("1"),
            _agent_id(10): Decimal("1"),
            _agent_id(11): Decimal("1"),
        }
    }

    payouts = settle_attribution_batch(_make_batch(event), stake_map=stake_map)

    assert [agent_id for agent_id, _ in payouts] == [
        _agent_id(10),
        _agent_id(11),
        _agent_id(13),
    ]
    assert sum(amount for _, amount in payouts) == REUSE_ATTRIBUTION_RATE
    assert payouts[-1][1] == REUSE_ATTRIBUTION_RATE - payouts[0][1] - payouts[1][1]


@pytest.mark.parametrize("stake_map", [{}, {COAUTHOR_EMPTY_NODE_ID: {}}])
def test_co_authorship_zero_members_no_payout_emits_commons_token(
    stake_map: dict[str, dict[str, Decimal]],
) -> None:
    event = _co_authorship_event(COAUTHOR_EMPTY_NODE_ID)
    emitted_tokens: list[str] = []

    payouts = settle_attribution_batch(
        _make_batch(event),
        stake_map=stake_map,
        emitted_tokens=emitted_tokens,
    )

    assert payouts == []
    assert emitted_tokens == ["cdl_081_zero_member_commons_transition"]


def test_co_authorship_all_zero_member_stake_no_payout_emits_zero_stake_token() -> None:
    emitted_tokens: list[str] = []

    payouts = settle_attribution_batch(
        _make_batch(_co_authorship_event(COAUTHOR_ZERO_STAKE_NODE_ID)),
        stake_map={COAUTHOR_ZERO_STAKE_NODE_ID: {_agent_id(10): Decimal("0")}},
        emitted_tokens=emitted_tokens,
    )

    assert payouts == []
    assert emitted_tokens == ["cdl_081_zero_stake_commons_transition"]


@pytest.mark.parametrize("star_node_id", [None, "", " ", "star:legacy"])
def test_co_authorship_rejects_non_cidv1_star_node_id(star_node_id: str | None) -> None:
    with pytest.raises(ValueError) as exc_info:
        settle_attribution_batch(
            _make_batch(_co_authorship_event(star_node_id)),  # type: ignore[arg-type]
            stake_map={},
        )

    assert str(exc_info.value) == "co_authorship_star_node_id_must_be_cidv1_nodeid"


def test_refutation_pays_refuting_agent() -> None:
    payouts = settle_attribution_batch(
        _make_batch(_refutation_event(VALID_REFUTING_ID)),
        stake_map={},
    )

    assert payouts == [(VALID_REFUTING_ID, REUSE_ATTRIBUTION_RATE)]


def test_refutation_does_not_pay_target_creator() -> None:
    payouts = settle_attribution_batch(
        _make_batch(_refutation_event(VALID_REFUTING_ID)),
        stake_map={},
    )
    recipient_ids = [agent_id for agent_id, _ in payouts]

    assert VALID_REFUTING_ID in recipient_ids
    assert VALID_CREATOR_ID not in recipient_ids


def test_refutation_missing_refuting_agent_raises() -> None:
    with pytest.raises(ValueError) as exc_info:
        settle_attribution_batch(_make_batch(_refutation_event(None)), stake_map={})

    assert str(exc_info.value) == "refutation_event_missing_refuting_agent_id"


@pytest.mark.parametrize("agent_id", ["legacy-id", "A" * 96, "a" * 95, "a" * 97])
def test_refutation_rejects_malformed_refuting_agent_id(agent_id: str) -> None:
    with pytest.raises(ValueError) as exc_info:
        settle_attribution_batch(_make_batch(_refutation_event(agent_id)), stake_map={})

    assert str(exc_info.value) == "refuting_agent_id_must_be_non_empty_string"


def test_reuse_rejects_malformed_target_creator_id() -> None:
    with pytest.raises(ValueError) as exc_info:
        settle_attribution_batch(_make_batch(_reuse_event("legacy-creator")), stake_map={})

    assert str(exc_info.value) == "target_creator_id_must_be_non_empty_string"


def test_provenance_three_hop_geometric_decay_uses_locked_literals() -> None:
    chain = (
        (_node_id("prov-1"), _agent_id(1)),
        (_node_id("prov-2"), _agent_id(2)),
        (_node_id("prov-3"), _agent_id(3)),
    )

    payouts = settle_attribution_batch(
        _make_batch(_provenance_event(chain)),
        stake_map={},
        epoch_node_mint_count=5,
    )
    payout_dict = dict(payouts)

    assert payout_dict[_agent_id(1)] == Decimal("0.090000000")
    assert payout_dict[_agent_id(2)] == Decimal("0.040500000")
    assert payout_dict[_agent_id(3)] == Decimal("0.018225000")


def test_provenance_max_depth_hop4_not_paid_but_earlier_hops_are_paid() -> None:
    chain = (
        (_node_id("depth-1"), _agent_id(1)),
        (_node_id("depth-2"), _agent_id(2)),
        (_node_id("depth-3"), _agent_id(3)),
        (_node_id("depth-4"), _agent_id(4)),
    )

    payouts = settle_attribution_batch(
        _make_batch(_provenance_event(chain)),
        stake_map={},
        epoch_node_mint_count=5,
    )
    recipient_ids = [agent_id for agent_id, _ in payouts]

    assert recipient_ids == [_agent_id(1), _agent_id(2), _agent_id(3)]
    assert _agent_id(4) not in recipient_ids


def test_provenance_duplicate_creator_nearest_hop_wins_without_renumbering() -> None:
    chain = (
        (_node_id("duplicate-1"), _agent_id(1)),
        (_node_id("duplicate-2"), _agent_id(1)),
        (_node_id("duplicate-3"), _agent_id(2)),
    )

    payouts = settle_attribution_batch(
        _make_batch(_provenance_event(chain)),
        stake_map={},
        epoch_node_mint_count=5,
    )
    shared_payouts = [(agent_id, amount) for agent_id, amount in payouts if agent_id == _agent_id(1)]

    assert len(shared_payouts) == 1
    assert shared_payouts[0][1] == Decimal("0.090000000")
    # Duplicate creator suppression does not renumber later original-chain hops.
    assert (_agent_id(2), Decimal("0.018225000")) in payouts


def test_provenance_phi_bound_allows_events_below_threshold() -> None:
    payouts = settle_attribution_batch(
        _make_batch(
            _provenance_event(((_node_id("below-1"), _agent_id(1)),)),
            _provenance_event(((_node_id("below-2"), _agent_id(2)),)),
            _provenance_event(((_node_id("below-3"), _agent_id(3)),)),
        ),
        stake_map={},
        epoch_node_mint_count=5,
    )

    assert [agent_id for agent_id, _ in payouts] == [_agent_id(1), _agent_id(2), _agent_id(3)]


def test_provenance_phi_bound_exceeded_suppresses_once_per_batch() -> None:
    events = tuple(
        _provenance_event(((_node_id(f"phi-{index}"), _agent_id(index)),))
        for index in range(1, 5)
    )
    emitted_tokens: list[str] = []

    payouts = settle_attribution_batch(
        _make_batch(*events),
        stake_map={},
        epoch_node_mint_count=5,
        emitted_tokens=emitted_tokens,
    )

    assert [agent_id for agent_id, _ in payouts] == [_agent_id(1), _agent_id(2), _agent_id(3)]
    assert _agent_id(4) not in [agent_id for agent_id, _ in payouts]
    assert emitted_tokens == ["edge_mint_phi_bound_exceeded"]


def test_provenance_epoch_no_node_mints_phi_check_skipped_token_deduplicates() -> None:
    emitted_tokens: list[str] = []

    payouts = settle_attribution_batch(
        _make_batch(
            _provenance_event(((_node_id("zero-mints-1"), _agent_id(1)),)),
            _provenance_event(((_node_id("zero-mints-2"), _agent_id(2)),)),
        ),
        stake_map={},
        epoch_node_mint_count=0,
        emitted_tokens=emitted_tokens,
    )

    assert payouts == [
        (_agent_id(1), Decimal("0.090000000")),
        (_agent_id(2), Decimal("0.090000000")),
    ]
    assert emitted_tokens == ["edge_mint_phi_bound_enforcement_skipped_no_node_mints"]


def test_provenance_rejects_chain_longer_than_input_bound() -> None:
    chain = tuple(
        (_node_id(f"long-{index}"), _agent_id(index + 1))
        for index in range(MAX_PROVENANCE_CHAIN_INPUT_LENGTH + 1)
    )

    with pytest.raises(ValueError) as exc_info:
        settle_attribution_batch(
            _make_batch(_provenance_event(chain)),
            stake_map={},
        )

    assert str(exc_info.value) == "provenance_chain_exceeds_input_bound"


@pytest.mark.parametrize(
    "chain,error_token",
    [
        ((("legacy-node", _agent_id(1)),), "provenance_chain_node_id_must_be_non_empty_string"),
        (((_node_id("bad-agent"), "legacy-creator"),), "provenance_chain_creator_id_must_be_non_empty_string"),
    ],
)
def test_provenance_rejects_malformed_node_or_creator_ids(
    chain: tuple[tuple[str, str], ...],
    error_token: str,
) -> None:
    with pytest.raises(ValueError) as exc_info:
        settle_attribution_batch(_make_batch(_provenance_event(chain)), stake_map={})

    assert str(exc_info.value) == error_token


def test_provenance_max_payout_bound_stays_below_direct_reuse_rate() -> None:
    chain = (
        (_node_id("max-1"), _agent_id(1)),
        (_node_id("max-2"), _agent_id(2)),
        (_node_id("max-3"), _agent_id(3)),
    )

    payouts = settle_attribution_batch(
        _make_batch(_provenance_event(chain)),
        stake_map={},
        epoch_node_mint_count=5,
    )

    assert sum(amount for _, amount in payouts) == Decimal("0.148725000")
    assert sum(amount for _, amount in payouts) < REUSE_ATTRIBUTION_RATE


def test_mixed_edge_type_batch_preserves_independent_routing() -> None:
    coauthor_node = _node_id("mixed-coauthor")
    provenance_node = _node_id("mixed-provenance")
    events = (
        _reuse_event(_agent_id(1)),
        _co_authorship_event(coauthor_node),
        _refutation_event(_agent_id(4)),
        _provenance_event(((provenance_node, _agent_id(5)),)),
    )

    payouts = settle_attribution_batch(
        _make_batch(*events),
        stake_map={coauthor_node: {_agent_id(2): Decimal("1"), _agent_id(3): Decimal("1")}},
        epoch_node_mint_count=5,
    )

    assert payouts == [
        (_agent_id(1), Decimal("0.20")),
        (_agent_id(2), Decimal("0.100000000")),
        (_agent_id(3), Decimal("0.100000000")),
        (_agent_id(4), Decimal("0.20")),
        (_agent_id(5), Decimal("0.090000000")),
    ]


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


@pytest.mark.parametrize("value", [Decimal("NaN"), Decimal("Infinity")])
def test_weight_params_decay_rate_rejects_non_finite_with_exact_token(value: Decimal) -> None:
    with pytest.raises(ValueError) as exc_info:
        WeightParams(
            stake=Decimal("1"),
            reuse_count=0,
            decay_rate=value,
            edge_type_coefficient=Decimal("1.0"),
        )

    assert str(exc_info.value) == "weight_decay_rate_invalid_non_finite"


@pytest.mark.parametrize("value", [Decimal("-0.000000001"), Decimal("1.000000001")])
def test_weight_params_decay_rate_rejects_out_of_range_values(value: Decimal) -> None:
    with pytest.raises(ValueError) as exc_info:
        WeightParams(
            stake=Decimal("1"),
            reuse_count=0,
            decay_rate=value,
            edge_type_coefficient=Decimal("1.0"),
        )

    assert str(exc_info.value) == "weight_decay_rate_out_of_range"


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
    payouts = settle_attribution_batch(
        _make_batch(_reuse_event()),
        stake_map={},
        passive_ecu_centrality_state={
            "_pending": {1: {VALID_STAR_NODE_ID: "0.15"}}
        },
    )

    assert payouts == [
        (VALID_CREATOR_ID, REUSE_ATTRIBUTION_RATE),
        (VALID_CREATOR_ID, Decimal("0.004000000000")),
    ]
