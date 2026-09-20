from decimal import Decimal

import pytest

from ilc_core.economics import epoch_attribution_settle_runtime as settle_runtime
from ilc_core.economics.epoch_attribution_settle_runtime import (
    AttributionEvent,
    MAX_PROVENANCE_CHAIN_INPUT_LENGTH,
    settle_attribution_batch,
)
from ilc_core.encoding.cidv1 import node_id_from_obj
from ilc_core.types import EdgeType, EpochAttributionBatch, WeightParams


def _agent_id(index: int) -> str:
    return f"{index:096x}"


def _node_id(label: str) -> str:
    return node_id_from_obj({"phase": 1600, "label": label})


VALID_AGENT_ID = _agent_id(1)
VALID_REFUTING_ID = _agent_id(2)
VALID_NODE_ID = _node_id("valid")


def _sealed_batch(*events: AttributionEvent) -> EpochAttributionBatch:
    batch = EpochAttributionBatch(epoch=1)
    for event in events:
        batch.add_event(event)
    batch.seal()
    return batch


def _reuse_event(
    creator_id: object = VALID_AGENT_ID,
    star_node_id: str | None = VALID_NODE_ID,
) -> AttributionEvent:
    return AttributionEvent(
        edge_type=EdgeType.REUSE,
        target_creator_id=creator_id,  # type: ignore[arg-type]
        star_node_id=star_node_id,
        epoch=1,
    )


def _coauthor_event(star_node_id: object = VALID_NODE_ID) -> AttributionEvent:
    return AttributionEvent(
        edge_type=EdgeType.CO_AUTHORSHIP,
        target_creator_id=VALID_AGENT_ID,
        star_node_id=star_node_id,  # type: ignore[arg-type]
        epoch=1,
    )


def _refutation_event(refuting_agent_id: object = VALID_REFUTING_ID) -> AttributionEvent:
    return AttributionEvent(
        edge_type=EdgeType.REFUTATION,
        target_creator_id=VALID_AGENT_ID,
        star_node_id=None,
        epoch=1,
        refuting_agent_id=refuting_agent_id,  # type: ignore[arg-type]
    )


def _provenance_event(chain: object) -> AttributionEvent:
    return AttributionEvent(
        edge_type=EdgeType.PROVENANCE,
        target_creator_id=VALID_AGENT_ID,
        star_node_id=None,
        epoch=1,
        provenance_chain=chain,  # type: ignore[arg-type]
    )


def test_unsealed_batch_raises_stable_token() -> None:
    batch = EpochAttributionBatch(epoch=1)
    batch.add_event(_reuse_event())

    with pytest.raises(ValueError) as exc_info:
        settle_attribution_batch(batch, stake_map={})

    assert str(exc_info.value) == "epoch_attribution_batch_must_be_sealed_before_settlement"


@pytest.mark.parametrize("value", [-1, 1.0, True])
def test_epoch_node_mint_count_must_be_non_negative_int(value: object) -> None:
    with pytest.raises(ValueError) as exc_info:
        settle_attribution_batch(
            _sealed_batch(_reuse_event()),
            stake_map={},
            epoch_node_mint_count=value,  # type: ignore[arg-type]
        )

    assert str(exc_info.value) == "epoch_node_mint_count_must_be_non_negative"


@pytest.mark.parametrize(
    "creator_id",
    ["", " ", f" {VALID_AGENT_ID} ", "legacy", "A" * 96, "a" * 95, "a" * 97],
)
def test_reuse_rejects_empty_or_malformed_target_creator_id(creator_id: str) -> None:
    with pytest.raises(ValueError) as exc_info:
        settle_attribution_batch(_sealed_batch(_reuse_event(creator_id)), stake_map={})

    assert str(exc_info.value) == "target_creator_id_must_be_non_empty_string"


@pytest.mark.parametrize(
    "refuting_agent_id",
    ["", " ", f" {VALID_REFUTING_ID} ", "legacy", "B" * 96, "b" * 95, "b" * 97],
)
def test_refutation_rejects_empty_or_malformed_refuting_agent_id(
    refuting_agent_id: str,
) -> None:
    with pytest.raises(ValueError) as exc_info:
        settle_attribution_batch(
            _sealed_batch(_refutation_event(refuting_agent_id)),
            stake_map={},
        )

    assert str(exc_info.value) == "refuting_agent_id_must_be_non_empty_string"


def test_refutation_missing_refuting_agent_id_raises_stable_token() -> None:
    with pytest.raises(ValueError) as exc_info:
        settle_attribution_batch(_sealed_batch(_refutation_event(None)), stake_map={})

    assert str(exc_info.value) == "refutation_event_missing_refuting_agent_id"


@pytest.mark.parametrize("star_node_id", [None, "", " ", "star:legacy", VALID_AGENT_ID])
def test_coauthorship_rejects_missing_or_malformed_star_node_id(star_node_id: object) -> None:
    with pytest.raises(ValueError) as exc_info:
        settle_attribution_batch(_sealed_batch(_coauthor_event(star_node_id)), stake_map={})

    assert str(exc_info.value) == "co_authorship_star_node_id_must_be_cidv1_nodeid"


def test_coauthorship_rejects_non_dict_member_map() -> None:
    with pytest.raises(ValueError) as exc_info:
        settle_attribution_batch(
            _sealed_batch(_coauthor_event()),
            stake_map={VALID_NODE_ID: "not-a-dict"},  # type: ignore[dict-item]
        )

    assert str(exc_info.value) == "stake_map_members_must_be_dict"


@pytest.mark.parametrize(
    "member_id",
    ["", " ", f" {VALID_AGENT_ID} ", "legacy", "C" * 96, "c" * 95],
)
def test_coauthorship_rejects_malformed_member_agent_id(member_id: str) -> None:
    with pytest.raises(ValueError) as exc_info:
        settle_attribution_batch(
            _sealed_batch(_coauthor_event()),
            stake_map={VALID_NODE_ID: {member_id: Decimal("1")}},
        )

    assert str(exc_info.value) == "stake_map_member_id_must_be_non_empty_string"


@pytest.mark.parametrize(
    "stake,error_token",
    [
        (0.5, "stake_map_member_stake_must_be_decimal"),
        (Decimal("NaN"), "stake_map_member_stake_must_be_non_negative_finite_decimal"),
        (Decimal("Infinity"), "stake_map_member_stake_must_be_non_negative_finite_decimal"),
        (Decimal("-0.1"), "stake_map_member_stake_must_be_non_negative_finite_decimal"),
    ],
)
def test_coauthorship_rejects_invalid_member_stake(
    stake: object,
    error_token: str,
) -> None:
    with pytest.raises(ValueError) as exc_info:
        settle_attribution_batch(
            _sealed_batch(_coauthor_event()),
            stake_map={VALID_NODE_ID: {VALID_AGENT_ID: stake}},  # type: ignore[dict-item]
        )

    assert str(exc_info.value) == error_token


def test_settle_rejects_non_dict_stake_map_with_stable_token() -> None:
    with pytest.raises(ValueError) as exc_info:
        settle_attribution_batch(
            _sealed_batch(_coauthor_event()),
            stake_map=None,  # type: ignore[arg-type]
        )

    assert str(exc_info.value) == "stake_map_must_be_dict"


def test_settle_rejects_non_list_emitted_tokens_with_stable_token() -> None:
    with pytest.raises(ValueError) as exc_info:
        settle_attribution_batch(
            _sealed_batch(_coauthor_event()),
            stake_map={},
            emitted_tokens=(),  # type: ignore[arg-type]
        )

    assert str(exc_info.value) == "emitted_tokens_must_be_list"


def test_settle_rejects_non_attribution_event_batch_member_with_stable_token() -> None:
    batch = EpochAttributionBatch(epoch=1)
    batch.add_event(object())
    batch.seal()

    with pytest.raises(ValueError) as exc_info:
        settle_attribution_batch(batch, stake_map={})

    assert str(exc_info.value) == "attribution_event_must_be_attribution_event"


def test_coauthorship_all_zero_stake_emits_stable_skip_token() -> None:
    emitted_tokens: list[str] = []

    payouts = settle_attribution_batch(
        _sealed_batch(_coauthor_event()),
        stake_map={VALID_NODE_ID: {VALID_AGENT_ID: Decimal("0")}},
        emitted_tokens=emitted_tokens,
    )

    assert payouts == []
    assert emitted_tokens == ["cdl_081_zero_stake_commons_transition"]


@pytest.mark.parametrize(
    "chain,error_token",
    [
        (None, "provenance_event_missing_chain"),
        ([], "provenance_chain_must_be_tuple"),
        ((), "provenance_event_empty_chain"),
        ((("not-cidv1", VALID_AGENT_ID),), "provenance_chain_node_id_must_be_cidv1_nodeid"),
        (((VALID_NODE_ID, "legacy"),), "provenance_chain_creator_id_must_be_agent_id"),
        (((VALID_NODE_ID,),), "provenance_chain_entry_must_be_node_creator_pair"),
        (([VALID_NODE_ID, VALID_AGENT_ID],), "provenance_chain_entry_must_be_node_creator_pair"),
    ],
)
def test_provenance_rejects_malformed_chains(chain: object, error_token: str) -> None:
    with pytest.raises(ValueError) as exc_info:
        settle_attribution_batch(_sealed_batch(_provenance_event(chain)), stake_map={})

    assert str(exc_info.value) == error_token


def test_provenance_rejects_duplicate_node_id() -> None:
    chain = ((VALID_NODE_ID, _agent_id(10)), (VALID_NODE_ID, _agent_id(11)))

    with pytest.raises(ValueError) as exc_info:
        settle_attribution_batch(_sealed_batch(_provenance_event(chain)), stake_map={})

    assert str(exc_info.value) == "provenance_chain_contains_duplicate_node_id"


def test_provenance_rejects_chain_longer_than_input_bound() -> None:
    chain = tuple(
        (_node_id(f"long-{index}"), _agent_id(index + 10))
        for index in range(MAX_PROVENANCE_CHAIN_INPUT_LENGTH + 1)
    )

    with pytest.raises(ValueError) as exc_info:
        settle_attribution_batch(_sealed_batch(_provenance_event(chain)), stake_map={})

    assert str(exc_info.value) == "provenance_chain_exceeds_input_bound"


def test_provenance_phi_bound_token_deduplicates_across_suppressed_events() -> None:
    emitted_tokens: list[str] = []
    events = [
        _provenance_event(((_node_id(f"phi-{index}"), _agent_id(index + 20)),))
        for index in range(4)
    ]

    settle_attribution_batch(
        _sealed_batch(*events),
        stake_map={},
        emitted_tokens=emitted_tokens,
        epoch_node_mint_count=1,
    )

    assert emitted_tokens == ["edge_mint_phi_bound_exceeded"]


def test_passive_ecu_rejects_non_dict_centrality_state() -> None:
    with pytest.raises(ValueError) as exc_info:
        settle_attribution_batch(
            _sealed_batch(_reuse_event()),
            stake_map={},
            passive_ecu_centrality_state="not-a-dict",  # type: ignore[arg-type]
        )

    assert str(exc_info.value) == "passive_ecu_centrality_state_must_be_dict"


def test_passive_ecu_rejects_malformed_star_node_id_when_present() -> None:
    with pytest.raises(ValueError) as exc_info:
        settle_attribution_batch(
            _sealed_batch(_reuse_event(star_node_id="star:legacy")),
            stake_map={},
            passive_ecu_centrality_state={},
        )

    assert str(exc_info.value) == "passive_ecu_node_id_must_be_cidv1_nodeid"


@pytest.mark.parametrize("value", [Decimal("NaN"), Decimal("Infinity")])
def test_weight_params_non_finite_decay_rate_exact_token(value: Decimal) -> None:
    with pytest.raises(ValueError) as exc_info:
        WeightParams(
            stake=Decimal("1"),
            reuse_count=0,
            decay_rate=value,
            edge_type_coefficient=Decimal("1"),
        )

    assert str(exc_info.value) == "weight_decay_rate_invalid_non_finite"


@pytest.mark.parametrize("value", [Decimal("-0.1"), Decimal("1.1")])
def test_weight_params_decay_rate_range_guard(value: Decimal) -> None:
    with pytest.raises(ValueError) as exc_info:
        WeightParams(
            stake=Decimal("1"),
            reuse_count=0,
            decay_rate=value,
            edge_type_coefficient=Decimal("1"),
        )

    assert str(exc_info.value) == "weight_decay_rate_out_of_range"


@pytest.mark.parametrize("value", [Decimal("0"), Decimal("1")])
def test_weight_params_decay_rate_accepts_closed_interval_boundaries(value: Decimal) -> None:
    params = WeightParams(
        stake=Decimal("1"),
        reuse_count=0,
        decay_rate=value,
        edge_type_coefficient=Decimal("1"),
    )

    assert params.decay_rate == value


@pytest.mark.parametrize(
    "field,value,error_token",
    [
        ("stake", Decimal("NaN"), "weight_stake_invalid_non_finite"),
        ("stake", Decimal("Infinity"), "weight_stake_invalid_non_finite"),
        (
            "edge_type_coefficient",
            Decimal("NaN"),
            "weight_edge_type_coefficient_invalid_non_finite",
        ),
        (
            "edge_type_coefficient",
            Decimal("Infinity"),
            "weight_edge_type_coefficient_invalid_non_finite",
        ),
    ],
)
def test_weight_params_rejects_other_non_finite_decimal_fields(
    field: str,
    value: Decimal,
    error_token: str,
) -> None:
    kwargs = {
        "stake": Decimal("1"),
        "reuse_count": 0,
        "decay_rate": Decimal("0"),
        "edge_type_coefficient": Decimal("1"),
    }
    kwargs[field] = value

    with pytest.raises(ValueError) as exc_info:
        WeightParams(**kwargs)

    assert str(exc_info.value) == error_token


def test_ejected_stake_distribution_rejects_malformed_member_id() -> None:
    with pytest.raises(ValueError) as exc_info:
        settle_runtime._normalize_distribution_member_stakes({"legacy": Decimal("1")})

    assert str(exc_info.value) == "ejected_stake_member_id_must_be_non_empty_string"


@pytest.mark.parametrize(
    "stake,error_token",
    [
        (1, "ejected_stake_member_stake_must_be_decimal"),
        ("1", "ejected_stake_member_stake_must_be_decimal"),
        (0.5, "ejected_stake_member_stake_must_be_decimal"),
        (Decimal("NaN"), "ejected_stake_member_stake_must_be_non_negative_finite_decimal"),
        (Decimal("Infinity"), "ejected_stake_member_stake_must_be_non_negative_finite_decimal"),
        (Decimal("-1"), "ejected_stake_member_stake_must_be_non_negative_finite_decimal"),
    ],
)
def test_ejected_stake_distribution_rejects_invalid_member_stake_exact_tokens(
    stake: object,
    error_token: str,
) -> None:
    with pytest.raises(ValueError) as exc_info:
        settle_runtime._normalize_distribution_member_stakes({VALID_AGENT_ID: stake})  # type: ignore[dict-item]

    assert str(exc_info.value) == error_token
