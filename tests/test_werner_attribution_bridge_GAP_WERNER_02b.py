from __future__ import annotations

from decimal import Decimal
from pathlib import Path

import pytest

from ilc_core.consensus.attribution_batch_bridge import (
    AttributionBatchBridgeError,
    MAX_WERNER_CONTEXTS_PER_BATCH,
    _attribution_event_log_key,
    build_attribution_batch_from_claims,
)
from ilc_core.economics.backward_attribution_traversal import (
    BACKWARD_ATTRIBUTION_PER_NODE_CAP,
    BackwardAttributionTraversal,
)
from ilc_core.economics import werner_runtime
from ilc_core.economics.werner_attribution_bridge import (
    WERNER_APPLICATION_STAGE,
    WERNER_BRIDGE_VERSION,
    WERNER_BRIDGE_SCOPE,
    WERNER_CDL_109_VERSION,
    WERNER_CONTEXT_ABSENT_TOKEN,
    RUNTIME_POLICY_CAP,
    WernerAttributionContext,
    apply_werner_to_raw_score,
    compute_werner_multiplier,
)


ROOT = Path(__file__).resolve().parents[1]
AGENT_A = "a" * 96
AGENT_B = "b" * 96
AGENT_C = "c" * 96


def _node(agent_id: str) -> dict[str, object]:
    return {
        "artifact_type": "claim",
        "created_epoch": 0,
        "novelty_score": Decimal("1"),
        "recipient_agent_id": agent_id,
        "status_quality_weight": Decimal("1"),
    }


def _edge(source: str, target: str) -> dict[str, object]:
    return {
        "edge_confidence": Decimal("1"),
        "edge_type": "PROVENANCE",
        "source_node_id": source,
        "target_node_id": target,
    }


def _claim_payload() -> dict[str, object]:
    return {
        "claims": [
            {
                "agent_id": AGENT_B,
                "amount": "10",
                "claim_id": "claim-direct",
                "epoch": 7,
            }
        ],
        "marker": "agent_loop_claims_ok",
    }


def _graph_context(*, pressure: str | None = "0.10") -> dict[str, object]:
    context: dict[str, object] = {
        "edges": [_edge("source", "upstream-a"), _edge("source", "upstream-c")],
        "events": [
            {
                "event_budget_ecu": "100",
                "event_epoch": 7,
                "event_id": "event-werner",
                "source_node_id": "source",
            }
        ],
        "nodes": {
            "source": _node(AGENT_B),
            "upstream-a": _node(AGENT_A),
            "upstream-c": _node(AGENT_C),
        },
    }
    if pressure is not None:
        context["werner_context_by_agent_id"] = {
            AGENT_A: {
                "agent_id": AGENT_A,
                "epoch": 7,
                "raw_werner_pressure": pressure,
            }
        }
    return context


def _credits_by_agent(result) -> dict[str, Decimal]:
    return {
        credit.recipient_agent_id: credit.pre_cap_credit_ecu
        for credit in result.credits
    }


def test_guard_cleared_for_cdl109_bridge_scope_only() -> None:
    assert werner_runtime.WERNER_CREDIT_WIRING_NOT_ACTIVATED is False


def test_absent_context_is_identity_multiplier_with_token() -> None:
    multiplier = compute_werner_multiplier(
        None,
        recipient_agent_id=AGENT_A,
        event_epoch=7,
    )

    assert multiplier.multiplier == Decimal("1")
    assert multiplier.flow_budget == Decimal("0")
    assert multiplier.context_present is False
    assert multiplier.disposition_token == WERNER_CONTEXT_ABSENT_TOKEN


def test_present_context_clamps_to_cdl109_policy_cap() -> None:
    multiplier = compute_werner_multiplier(
        WernerAttributionContext(
            agent_id=AGENT_A,
            epoch=7,
            raw_werner_pressure=Decimal("123"),
        ),
        recipient_agent_id=AGENT_A,
        event_epoch=7,
    )

    assert multiplier.flow_budget == RUNTIME_POLICY_CAP
    assert multiplier.multiplier == Decimal("1.10")
    assert WERNER_BRIDGE_VERSION == "werner_attribution_bridge_02b.v0.1"
    assert multiplier.cdl_version == WERNER_CDL_109_VERSION
    assert multiplier.bridge_scope == WERNER_BRIDGE_SCOPE
    assert multiplier.application_stage == WERNER_APPLICATION_STAGE


def test_apply_werner_to_raw_score_is_decimal_exact() -> None:
    adjusted, multiplier = apply_werner_to_raw_score(
        Decimal("0.45"),
        WernerAttributionContext(
            agent_id=AGENT_A,
            epoch=7,
            raw_werner_pressure=Decimal("0.05"),
        ),
        recipient_agent_id=AGENT_A,
        event_epoch=7,
    )

    assert multiplier.multiplier == Decimal("1.050000000000")
    assert adjusted == Decimal("0.47250000000000")


def test_apply_werner_to_raw_score_rejects_negative_raw_score() -> None:
    with pytest.raises(ValueError, match="werner_raw_path_score_must_be_non_negative"):
        apply_werner_to_raw_score(
            Decimal("-0.01"),
            None,
            recipient_agent_id=AGENT_A,
            event_epoch=7,
        )


def test_rejects_binary64_raw_score() -> None:
    with pytest.raises(ValueError, match="werner_raw_path_score_must_be_decimal"):
        apply_werner_to_raw_score(
            0.45,  # type: ignore[arg-type]
            None,
            recipient_agent_id=AGENT_A,
            event_epoch=7,
        )


def test_nonfinite_context_pressure_fails_closed_without_raising() -> None:
    for pressure in (Decimal("NaN"), Decimal("Infinity")):
        multiplier = compute_werner_multiplier(
            WernerAttributionContext(
                agent_id=AGENT_A,
                epoch=7,
                raw_werner_pressure=pressure,
            ),
            recipient_agent_id=AGENT_A,
            event_epoch=7,
        )
        assert multiplier.multiplier == Decimal("1")
        assert multiplier.flow_budget == Decimal("0")
        assert multiplier.context_present is False
        assert multiplier.disposition_token == WERNER_CONTEXT_ABSENT_TOKEN


def test_negative_context_pressure_fails_closed_without_raising() -> None:
    multiplier = compute_werner_multiplier(
        WernerAttributionContext(
            agent_id=AGENT_A,
            epoch=7,
            raw_werner_pressure=Decimal("-0.01"),
        ),
        recipient_agent_id=AGENT_A,
        event_epoch=7,
    )

    assert multiplier.multiplier == Decimal("1")
    assert multiplier.flow_budget == Decimal("0")
    assert multiplier.context_present is False
    assert multiplier.disposition_token == WERNER_CONTEXT_ABSENT_TOKEN


def test_zero_pressure_context_is_present_identity_multiplier() -> None:
    multiplier = compute_werner_multiplier(
        WernerAttributionContext(
            agent_id=AGENT_A,
            epoch=7,
            raw_werner_pressure=Decimal("0"),
        ),
        recipient_agent_id=AGENT_A,
        event_epoch=7,
    )

    assert multiplier.multiplier == Decimal("1.000000000000")
    assert multiplier.flow_budget == Decimal("0E-12")
    assert multiplier.context_present is True
    assert multiplier.disposition_token is None


def test_runtime_policy_cap_must_match_cdl109() -> None:
    with pytest.raises(ValueError, match="werner_runtime_policy_cap_must_match_cdl109"):
        compute_werner_multiplier(
            None,
            recipient_agent_id=AGENT_A,
            event_epoch=7,
            runtime_policy_cap=Decimal("0.11"),
        )


def test_rejects_context_epoch_mismatch() -> None:
    with pytest.raises(ValueError, match="werner_context_epoch_must_match_event_epoch"):
        compute_werner_multiplier(
            WernerAttributionContext(
                agent_id=AGENT_A,
                epoch=6,
                raw_werner_pressure=Decimal("0.10"),
            ),
            recipient_agent_id=AGENT_A,
            event_epoch=7,
        )


def test_traversal_reweights_raw_scores_before_normalization() -> None:
    traversal = BackwardAttributionTraversal(
        {
            "source": _node(AGENT_B),
            "upstream-a": _node(AGENT_A),
            "upstream-c": _node(AGENT_C),
        },
        [_edge("source", "upstream-a"), _edge("source", "upstream-c")],
    )

    baseline = traversal.traverse(
        "source",
        event_id="event-baseline",
        event_budget_ecu="100",
        event_epoch=7,
    )
    reweighted = traversal.traverse(
        "source",
        event_id="event-werner",
        event_budget_ecu="100",
        event_epoch=7,
        werner_context_by_agent_id={
            AGENT_A: WernerAttributionContext(
                agent_id=AGENT_A,
                epoch=7,
                raw_werner_pressure=Decimal("0.10"),
            )
        },
    )

    assert _credits_by_agent(baseline)[AGENT_A] == Decimal("5.0")
    assert _credits_by_agent(reweighted)[AGENT_A] > Decimal("5.0")
    assert _credits_by_agent(reweighted)[AGENT_C] < Decimal("5.0")
    score_a = next(score for score in reweighted.path_scores if score.recipient_agent_id == AGENT_A)
    assert score_a.werner_context_present is True
    assert score_a.werner_multiplier == Decimal("1.10")
    assert score_a.pre_werner_raw_path_score * score_a.werner_multiplier == score_a.raw_path_score


def test_absent_context_preserves_baseline_scores() -> None:
    traversal = BackwardAttributionTraversal(
        {
            "source": _node(AGENT_B),
            "upstream-a": _node(AGENT_A),
            "upstream-c": _node(AGENT_C),
        },
        [_edge("source", "upstream-a"), _edge("source", "upstream-c")],
    )

    baseline = traversal.traverse(
        "source",
        event_id="event-baseline",
        event_budget_ecu="100",
        event_epoch=7,
    )
    absent = traversal.traverse(
        "source",
        event_id="event-absent",
        event_budget_ecu="100",
        event_epoch=7,
        werner_context_by_agent_id={},
    )

    assert [score.raw_path_score for score in absent.path_scores] == [
        score.raw_path_score for score in baseline.path_scores
    ]
    assert {score.werner_disposition_token for score in absent.path_scores} == {
        WERNER_CONTEXT_ABSENT_TOKEN
    }
    assert [score.pre_werner_raw_path_score for score in absent.path_scores] == [
        score.raw_path_score for score in absent.path_scores
    ]


def test_invalid_werner_context_does_not_wedge_zero_credit_intermediate() -> None:
    source = _node(AGENT_B)
    thin = _node(AGENT_A)
    thin["novelty_score"] = Decimal("0")
    upstream = _node(AGENT_C)
    result = BackwardAttributionTraversal(
        {
            "source": source,
            "thin": thin,
            "upstream-c": upstream,
        },
        [_edge("source", "thin"), _edge("thin", "upstream-c")],
    ).traverse(
        "source",
        event_id="event-transparent-route",
        event_budget_ecu="100",
        event_epoch=7,
        werner_context_by_agent_id={
            AGENT_A: WernerAttributionContext(
                agent_id=AGENT_A,
                epoch=7,
                raw_werner_pressure=Decimal("-1"),
            )
        },
    )

    assert [score.upstream_artifact_id for score in result.path_scores] == ["upstream-c"]
    assert result.path_scores[0].recipient_agent_id == AGENT_C


def test_cdl108_caps_apply_after_werner_reweighting() -> None:
    result = BackwardAttributionTraversal(
        {
            "source": _node(AGENT_B),
            "upstream-a": _node(AGENT_A),
            "upstream-c": _node(AGENT_C),
        },
        [_edge("source", "upstream-a"), _edge("source", "upstream-c")],
    ).traverse(
        "source",
        event_id="event-capped",
        event_budget_ecu="1000",
        event_epoch=7,
        apply_antigaming_caps=True,
        werner_context_by_agent_id={
            AGENT_A: WernerAttributionContext(
                agent_id=AGENT_A,
                epoch=7,
                raw_werner_pressure=Decimal("100"),
            )
        },
    )

    credit_a = next(credit for credit in result.final_credits if credit.recipient_agent_id == AGENT_A)
    assert credit_a.pre_cap_credit_ecu > result.node_cap_amount_ecu
    assert credit_a.final_credit_ecu == (
        result.backward_pool_ecu * BACKWARD_ATTRIBUTION_PER_NODE_CAP
    )
    assert credit_a.node_cap_applied is True
    assert credit_a.werner_context_present is True


def test_bridge_passes_werner_context_and_records_evidence_fields() -> None:
    batch = build_attribution_batch_from_claims(
        _claim_payload(),
        backward_attribution_graph_context=_graph_context(),
    )

    entries = {
        entry["recipient_agent_id"]: entry
        for entry in batch["backward_attribution_entries"]
    }
    assert batch["werner_context_count"] == 1
    assert batch["werner_attribution_bridge_scope"] == WERNER_BRIDGE_SCOPE
    assert batch["werner_attribution_bridge_version"] == WERNER_BRIDGE_VERSION
    assert batch["werner_cdl_authority_version"] == WERNER_CDL_109_VERSION
    assert entries[AGENT_A]["werner_context_present"] is True
    assert entries[AGENT_A]["werner_multiplier"] == "1.1"
    assert entries[AGENT_A]["pre_werner_raw_path_score"] == "0.45"
    assert Decimal(entries[AGENT_A]["pre_cap_credit_ecu"]) > Decimal(
        entries[AGENT_C]["pre_cap_credit_ecu"]
    )
    assert Decimal(entries[AGENT_A]["credit_amount"]) == Decimal("0.5")


def test_bridge_invalid_optional_werner_pressure_fails_closed() -> None:
    for pressure in ("NaN", "Infinity", "-0.01"):
        context = _graph_context(pressure=pressure)
        batch = build_attribution_batch_from_claims(
            _claim_payload(),
            backward_attribution_graph_context=context,
        )
        entries = {
            entry["recipient_agent_id"]: entry
            for entry in batch["backward_attribution_entries"]
        }
        assert entries[AGENT_A]["werner_context_present"] is False
        assert entries[AGENT_A]["werner_multiplier"] == "1"
        assert entries[AGENT_A]["werner_flow_budget"] == "0"


def test_bridge_rejects_werner_context_agent_mismatch() -> None:
    context = _graph_context()
    context["werner_context_by_agent_id"] = {
        AGENT_A: {
            "agent_id": AGENT_C,
            "epoch": 7,
            "raw_werner_pressure": "0.10",
        }
    }

    with pytest.raises(AttributionBatchBridgeError) as excinfo:
        build_attribution_batch_from_claims(
            _claim_payload(),
            backward_attribution_graph_context=context,
        )

    assert excinfo.value.token == "werner_context_agent_id_mismatch"


def test_bridge_rejects_binary64_werner_pressure() -> None:
    context = _graph_context()
    context["werner_context_by_agent_id"] = {
        AGENT_A: {
            "agent_id": AGENT_A,
            "epoch": 7,
            "raw_werner_pressure": 0.10,
        }
    }

    with pytest.raises(AttributionBatchBridgeError) as excinfo:
        build_attribution_batch_from_claims(
            _claim_payload(),
            backward_attribution_graph_context=context,
        )

    assert excinfo.value.token == "werner_raw_pressure_must_be_exact_decimal"


def test_bridge_rejects_werner_context_count_above_maximum() -> None:
    context = _graph_context()
    context["werner_context_by_agent_id"] = {
        f"{index:096x}": {
            "agent_id": f"{index:096x}",
            "epoch": 7,
            "raw_werner_pressure": "0",
        }
        for index in range(MAX_WERNER_CONTEXTS_PER_BATCH + 1)
    }

    with pytest.raises(AttributionBatchBridgeError) as excinfo:
        build_attribution_batch_from_claims(
            _claim_payload(),
            backward_attribution_graph_context=context,
        )

    assert excinfo.value.token == "werner_context_count_exceeds_maximum"


def test_deterministic_replay_with_werner_context() -> None:
    first = build_attribution_batch_from_claims(
        _claim_payload(),
        backward_attribution_graph_context=_graph_context(),
    )
    second = build_attribution_batch_from_claims(
        _claim_payload(),
        backward_attribution_graph_context=_graph_context(),
    )

    assert first == second


def test_conservation_residual_unissued_not_redistributed_after_caps() -> None:
    result = BackwardAttributionTraversal(
        {
            "source": _node(AGENT_B),
            "upstream-a": _node(AGENT_A),
            "upstream-c": _node(AGENT_C),
        },
        [_edge("source", "upstream-a"), _edge("source", "upstream-c")],
    ).traverse(
        "source",
        event_id="event-conservation",
        event_budget_ecu="1000",
        event_epoch=7,
        apply_antigaming_caps=True,
        werner_context_by_agent_id={
            AGENT_A: WernerAttributionContext(
                agent_id=AGENT_A,
                epoch=7,
                raw_werner_pressure=Decimal("0.10"),
            )
        },
    )

    issued = sum((credit.final_credit_ecu for credit in result.final_credits), Decimal("0"))
    residual = sum((credit.clipped_residual_ecu for credit in result.final_credits), Decimal("0"))
    assert issued + residual == result.backward_pool_ecu
    assert result.unissued_backward_pool_ecu == residual


def test_pre_cap_conservation_holds_before_caps() -> None:
    result = BackwardAttributionTraversal(
        {
            "source": _node(AGENT_B),
            "upstream-a": _node(AGENT_A),
            "upstream-c": _node(AGENT_C),
        },
        [_edge("source", "upstream-a"), _edge("source", "upstream-c")],
    ).traverse(
        "source",
        event_id="event-pre-cap-conservation",
        event_budget_ecu="1000",
        event_epoch=7,
        apply_antigaming_caps=True,
        werner_context_by_agent_id={
            AGENT_A: WernerAttributionContext(
                agent_id=AGENT_A,
                epoch=7,
                raw_werner_pressure=Decimal("0.10"),
            )
        },
    )

    assert sum((credit.pre_cap_credit_ecu for credit in result.credits), Decimal("0")) == (
        result.backward_pool_ecu
    )


def test_single_upstream_path_allocates_pool_then_records_cap_residual() -> None:
    result = BackwardAttributionTraversal(
        {
            "source": _node(AGENT_B),
            "upstream-a": _node(AGENT_A),
        },
        [_edge("source", "upstream-a")],
    ).traverse(
        "source",
        event_id="event-single-upstream",
        event_budget_ecu="1000",
        event_epoch=7,
        apply_antigaming_caps=True,
    )

    credit = result.credits[0]
    final = result.final_credits[0]
    assert credit.pre_cap_credit_ecu == result.backward_pool_ecu
    assert final.final_credit_ecu == result.node_cap_amount_ecu
    assert final.clipped_residual_ecu == result.backward_pool_ecu - result.node_cap_amount_ecu
    assert result.unissued_backward_pool_ecu == final.clipped_residual_ecu


def test_bridge_cap_value_reports_binding_credit_and_limit_separately() -> None:
    batch = build_attribution_batch_from_claims(
        _claim_payload(),
        backward_attribution_graph_context=_graph_context(pressure="100"),
    )

    entry = next(
        item
        for item in batch["backward_attribution_entries"]
        if item["recipient_agent_id"] == AGENT_A
    )

    assert entry["cap_value"] == entry["credit_amount"]
    assert entry["cap_limit_value"] == "0.5"


def test_attribution_event_log_key_is_big_endian_sortable() -> None:
    assert _attribution_event_log_key(1, 0) < _attribution_event_log_key(256, 0)
    assert _attribution_event_log_key(7, 1) < _attribution_event_log_key(7, 2)


def test_bridge_module_has_no_disallowed_economic_side_effect_surface() -> None:
    source = (ROOT / "ilc_core" / "economics" / "werner_attribution_bridge.py").read_text(
        encoding="utf-8"
    )

    for forbidden in ("wallet", "ledger.write", "ecu_balance", "settle", "mint", "passive_ecu"):
        assert forbidden not in source
