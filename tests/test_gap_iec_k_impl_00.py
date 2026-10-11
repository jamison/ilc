from __future__ import annotations

from decimal import Decimal

import pytest

from ilc_core.consensus.attribution_batch_bridge import (
    AttributionBatchBridgeError,
    build_attribution_batch_from_claims,
)
from ilc_core.encoding.cidv1 import node_id_from_obj
from ilc_core.economics.iec_k_metrics import (
    AttributionRecord,
    IEC_K_DIAGNOSTIC_DECIMAL_QUANTUM,
    IEC_K_METRICS_VERSION,
    MAX_IEC_K_COEFFICIENT,
    MAX_IEC_K_COUNT,
    compute_elf,
    compute_iec,
    compute_k,
    compute_popperian_weight,
)


AGENT_A = "a" * 96
AGENT_B = "b" * 96
AGENT_C = "c" * 96
AGENT_D = "d" * 96


def _node_id(label: str) -> str:
    return node_id_from_obj({"label": label, "phase": "gap-iec-k-impl-00"})


def _claim_payload() -> dict[str, object]:
    return {
        "claims": [
            {
                "agent_id": AGENT_A,
                "amount": "1",
                "claim_id": "claim-iec-k",
                "epoch": 12,
            }
        ],
        "marker": "agent_loop_claims_ok",
    }


def _node(agent_id: str) -> dict[str, object]:
    return {
        "artifact_type": "claim",
        "created_epoch": 0,
        "novelty_score": "1",
        "recipient_agent_id": agent_id,
        "status_quality_weight": "1",
    }


def _edge(source: str, target: str) -> dict[str, object]:
    return {
        "edge_confidence": "1",
        "edge_type": "PROVENANCE",
        "source_node_id": source,
        "target_node_id": target,
    }


def _backward_context(**event_overrides: object) -> dict[str, object]:
    event: dict[str, object] = {
        "event_budget_ecu": "100",
        "event_epoch": 12,
        "event_id": "event-iec-k",
        "source_node_id": "source",
    }
    event.update(event_overrides)
    return {
        "edges": [_edge("source", "upstream")],
        "events": [event],
        "nodes": {
            "source": _node(AGENT_A),
            "upstream": _node(AGENT_B),
        },
    }


def _source_ref_context(
    *,
    source_refs: list[str],
    ref_creators: list[str],
    **event_overrides: object,
) -> dict[str, object]:
    source_id = _node_id("iec-k-source")
    nodes: dict[str, object] = {source_id: _node(AGENT_A)}
    for ref, creator in zip(source_refs, ref_creators, strict=True):
        nodes[ref] = _node(creator)
    event: dict[str, object] = {
        "event_budget_ecu": "100",
        "event_epoch": 12,
        "event_id": "event-iec-k-source-refs",
        "source_node_id": source_id,
        "source_refs": source_refs,
        "submitting_agent_id": AGENT_A,
    }
    event.update(event_overrides)
    return {
        "edges": [_edge(source_id, ref) for ref in source_refs],
        "events": [event],
        "nodes": nodes,
    }


def test_iec_counts_distinct_surviving_origins_and_ignores_unknown() -> None:
    records = [
        AttributionRecord("origin-a", "ctx-1", Decimal("1")),
        AttributionRecord("origin-a", "ctx-2", Decimal("1")),
        AttributionRecord("origin-b", "ctx-1", Decimal("1")),
        AttributionRecord("origin-c", "ctx-1", Decimal("1"), has_surviving_descendant=False),
        AttributionRecord(None, "ctx-1", Decimal("1")),
    ]

    assert compute_iec(records) == 2


def test_metric_functions_reject_single_use_iterators_before_silent_exhaustion() -> None:
    def _records():
        yield AttributionRecord("origin-a", "ctx-1", Decimal("1"), stance="accept")
        yield AttributionRecord("origin-b", "ctx-1", Decimal("1"), stance="accept")

    with pytest.raises(ValueError, match="iec_k_attribution_events_must_be_reiterable"):
        compute_iec(_records())
    with pytest.raises(ValueError, match="iec_k_attribution_events_must_be_reiterable"):
        compute_k(_records())


def test_metrics_empty_input_boundaries() -> None:
    assert compute_iec([]) == 0
    assert compute_k([]) == (0.0, 0.0)


def test_k_returns_two_component_context_agreement_tuple() -> None:
    records = [
        AttributionRecord("a", "ctx-1", Decimal("1"), stance="accept"),
        AttributionRecord("b", "ctx-1", Decimal("1"), stance="accept"),
        AttributionRecord("c", "ctx-2", Decimal("1"), stance="accept"),
        AttributionRecord("d", "ctx-2", Decimal("1"), stance="reject"),
    ]

    k = compute_k(records)

    assert isinstance(k, tuple)
    assert len(k) == 2
    assert k == (0.5, 0.5)


def test_k_single_context_has_no_between_context_component() -> None:
    records = [
        AttributionRecord("a", "ctx-1", Decimal("1"), stance="accept"),
        AttributionRecord("b", "ctx-1", Decimal("1"), stance="accept"),
        AttributionRecord("c", "ctx-1", Decimal("1"), stance="reject"),
    ]

    assert compute_k(records) == pytest.approx((1 / 3, 0.0))


def test_k_ignores_records_without_comparable_context_or_stance() -> None:
    records = [
        AttributionRecord("a", None, Decimal("1"), stance="accept"),
        AttributionRecord("b", "ctx-1", Decimal("1"), stance=None),
    ]

    assert compute_k(records) == (0.0, 0.0)


def test_elf_handles_zero_iec_and_uses_decimal_arithmetic() -> None:
    assert compute_elf(Decimal("12.5"), 0) is None
    assert compute_elf(Decimal("12.5"), 5) == Decimal("2.5")
    assert compute_elf(Decimal("1"), 3) == Decimal("0.333333333333")
    assert compute_elf(Decimal("1"), 3).as_tuple().exponent == (
        IEC_K_DIAGNOSTIC_DECIMAL_QUANTUM.as_tuple().exponent
    )


def test_rrw_values_must_be_non_negative() -> None:
    with pytest.raises(ValueError, match="iec_k_rrw_must_be_non_negative"):
        AttributionRecord("origin-a", "ctx-a", Decimal("-1"))
    with pytest.raises(ValueError, match="iec_k_rrw_must_be_non_negative"):
        compute_elf(Decimal("-1"), 1)


def test_popperian_weight_uses_provisional_half_coefficient() -> None:
    assert compute_popperian_weight(3, 4) == Decimal("5.0")
    assert compute_popperian_weight(0, 4) == Decimal("2.0")
    assert compute_popperian_weight(0, 0) == Decimal("0.0")


def test_popperian_weight_rejects_negative_coefficient() -> None:
    with pytest.raises(ValueError, match="iec_k_coefficient_must_be_non_negative"):
        compute_popperian_weight(1, 1, coefficient=Decimal("-0.1"))


def test_popperian_weight_rejects_unbounded_inputs() -> None:
    with pytest.raises(ValueError, match="iec_k_iec_exceeds_maximum"):
        compute_popperian_weight(MAX_IEC_K_COUNT + 1, 0)
    with pytest.raises(
        ValueError,
        match="iec_k_survived_refutation_attempts_exceeds_maximum",
    ):
        compute_popperian_weight(1, MAX_IEC_K_COUNT + 1)
    with pytest.raises(ValueError, match="iec_k_coefficient_exceeds_maximum"):
        compute_popperian_weight(
            1,
            1,
            coefficient=MAX_IEC_K_COEFFICIENT + Decimal("1"),
        )


def test_metrics_reject_float_inputs_for_weight_values() -> None:
    with pytest.raises(ValueError, match="iec_k_rrw_must_be_decimal"):
        AttributionRecord("origin-a", "ctx-a", 1.0)  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="iec_k_rrw_must_be_decimal"):
        compute_elf(1.0, 1)  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="iec_k_coefficient_must_be_decimal"):
        compute_popperian_weight(1, 1, coefficient=0.5)  # type: ignore[arg-type]


def test_laundered_single_origin_is_distinguished_from_independent_origins() -> None:
    laundered = [
        AttributionRecord("origin-a", None, Decimal("1")) for _ in range(10)
    ]
    objective = [
        AttributionRecord(f"origin-{index}", None, Decimal("1"))
        for index in range(10)
    ]

    assert compute_iec(laundered) == 1
    assert compute_iec(objective) == 10
    assert compute_iec(laundered) < compute_iec(objective)


def test_identifier_length_boundaries() -> None:
    max_identifier = "x" * 512
    too_long = "x" * 513

    record = AttributionRecord(max_identifier, max_identifier, Decimal("1"), stance=max_identifier)

    assert record.origin_id == max_identifier
    with pytest.raises(ValueError, match="iec_k_origin_id_must_be_non_empty_string"):
        AttributionRecord(too_long, "ctx", Decimal("1"))
    with pytest.raises(ValueError, match="iec_k_context_id_must_be_non_empty_string"):
        AttributionRecord("origin", too_long, Decimal("1"))
    with pytest.raises(ValueError, match="iec_k_stance_must_be_non_empty_string"):
        AttributionRecord("origin", "ctx", Decimal("1"), stance=too_long)


def test_stance_must_be_single_token() -> None:
    with pytest.raises(ValueError, match="iec_k_stance_must_be_single_token"):
        AttributionRecord("origin", "ctx", Decimal("1"), stance="accept reject")


def test_bridge_writes_iec_k_fields_only_to_python_event_log() -> None:
    batch = build_attribution_batch_from_claims(
        _claim_payload(),
        backward_attribution_graph_context=_backward_context(
            context_id="ctx-iec-k",
            has_surviving_descendant=True,
            origin_id="origin-iec-k",
            stance="accept",
        ),
    )

    event_log = batch["attribution_event_log"]
    assert event_log[0]["origin_id"] == "origin-iec-k"
    assert event_log[0]["context_id"] == "ctx-iec-k"
    assert event_log[0]["stance"] == "accept"
    assert event_log[0]["has_surviving_descendant"] is True
    assert all("origin_id" not in item for item in batch["attributions"])
    assert all("context_id" not in item for item in batch["attributions"])
    assert all("origin_id" not in item for item in batch["backward_attribution_entries"])
    assert all("context_id" not in item for item in batch["backward_attribution_entries"])


def test_bridge_omits_absent_iec_k_fields_for_backward_compatibility() -> None:
    batch = build_attribution_batch_from_claims(
        _claim_payload(),
        backward_attribution_graph_context=_backward_context(),
    )

    event_log = batch["attribution_event_log"]
    assert "origin_id" not in event_log[0]
    assert "context_id" not in event_log[0]
    assert "stance" not in event_log[0]
    assert "has_surviving_descendant" not in event_log[0]
    assert IEC_K_METRICS_VERSION == "iec_k_metrics_GAP_IEC_K_IMPL_00.v0.1"


def test_bridge_treats_null_optional_iec_k_fields_as_absent() -> None:
    batch = build_attribution_batch_from_claims(
        _claim_payload(),
        backward_attribution_graph_context=_backward_context(
            context_id=None,
            has_surviving_descendant=None,
            origin_id=None,
            stance=None,
        ),
    )

    event_log = batch["attribution_event_log"]
    assert "origin_id" not in event_log[0]
    assert "context_id" not in event_log[0]
    assert "stance" not in event_log[0]
    assert "has_surviving_descendant" not in event_log[0]


def test_bridge_records_false_survival_flag_as_diagnostic_field() -> None:
    batch = build_attribution_batch_from_claims(
        _claim_payload(),
        backward_attribution_graph_context=_backward_context(
            has_surviving_descendant=False,
        ),
    )

    assert batch["attribution_event_log"][0]["has_surviving_descendant"] is False


def test_iec_k_diagnostics_do_not_change_backward_batch_root() -> None:
    base = build_attribution_batch_from_claims(
        _claim_payload(),
        backward_attribution_graph_context=_backward_context(),
    )
    annotated = build_attribution_batch_from_claims(
        _claim_payload(),
        backward_attribution_graph_context=_backward_context(
            context_id="ctx-iec-k",
            has_surviving_descendant=True,
            origin_id="origin-iec-k",
            stance="accept",
        ),
    )

    assert annotated["attribution_event_log"][0]["origin_id"] == "origin-iec-k"
    assert annotated["backward_attribution_batch_root"] == base["backward_attribution_batch_root"]
    assert annotated["backward_attribution_entries"] == base["backward_attribution_entries"]


def test_iec_k_diagnostics_remain_event_log_only_on_cdl114_block_path() -> None:
    ref_1 = _node_id("iec-k-ref-1")
    ref_2 = _node_id("iec-k-ref-2")
    batch = build_attribution_batch_from_claims(
        _claim_payload(),
        backward_attribution_graph_context=_source_ref_context(
            source_refs=[ref_1, ref_2],
            ref_creators=[AGENT_B, AGENT_C],
            context_id="ctx-block",
            origin_id="origin-block",
            stance="accept",
        ),
    )

    event_log = batch["attribution_event_log"]
    assert batch["source_refs_cdl114_guard_block_count"] == 1
    assert batch["backward_attribution_entry_count"] == 0
    assert event_log[0]["origin_id"] == "origin-block"
    assert event_log[0]["context_id"] == "ctx-block"


def test_iec_k_diagnostics_remain_event_log_only_on_cdl084_dedup_path() -> None:
    batch = build_attribution_batch_from_claims(
        _claim_payload(),
        backward_attribution_graph_context=_backward_context(
            already_settled_by_cdl084=True,
            context_id="ctx-dedup",
            origin_id="origin-dedup",
            stance="accept",
        ),
    )

    event_log = batch["attribution_event_log"]
    assert batch["backward_attribution_entry_count"] == 0
    assert event_log[0]["dedup_reason"] == "cdl084_explicit_chain_already_settled"
    assert event_log[0]["origin_id"] == "origin-dedup"
    assert event_log[0]["context_id"] == "ctx-dedup"


@pytest.mark.parametrize(
    ("field_name", "bad_value", "token"),
    [
        ("origin_id", "", "iec_k_origin_id_must_be_non_empty_bridge_string"),
        ("context_id", " ctx ", "iec_k_context_id_must_be_non_empty_bridge_string"),
        ("context_id", "x" * 513, "iec_k_context_id_must_be_non_empty_bridge_string"),
        ("stance", 7, "iec_k_stance_must_be_non_empty_bridge_string"),
        (
            "stance",
            "accept reject",
            "iec_k_stance_must_be_single_token_bridge_string",
        ),
        (
            "has_surviving_descendant",
            "true",
            "iec_k_has_surviving_descendant_must_be_bool",
        ),
    ],
)
def test_bridge_validates_optional_iec_k_diagnostic_fields(
    field_name: str,
    bad_value: object,
    token: str,
) -> None:
    with pytest.raises(AttributionBatchBridgeError) as excinfo:
        build_attribution_batch_from_claims(
            _claim_payload(),
            backward_attribution_graph_context=_backward_context(**{field_name: bad_value}),
        )

    assert excinfo.value.token == token
