#!/usr/bin/env python3
"""Deterministic Phase 1623 sufficiency-attribution research simulation."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from decimal import Context, Decimal, InvalidOperation, ROUND_HALF_EVEN, localcontext
from pathlib import Path
from typing import Any, Mapping, Sequence

from ilc_core.economics.backward_attribution_traversal import (
    BACKWARD_ATTRIBUTION_BACKWARD_POOL_SHARE_BETA,
    BACKWARD_ATTRIBUTION_PER_AGENT_CAP,
    BACKWARD_ATTRIBUTION_PER_CLUSTER_CAP,
    BACKWARD_ATTRIBUTION_PER_NODE_CAP,
    BackwardAttributionTraversal,
)
from ilc_core.consensus.attribution_batch_bridge import _check_sybil_diversity_guard
from ilc_core.types import (
    EDGE_MINT_PHI_BOUND,
    PROVENANCE_DECAY_ALPHA,
    PROVENANCE_MAX_DEPTH,
    REUSE_ATTRIBUTION_RATE,
)


SCHEMA_VERSION = "sim_sufficiency_hyperedge_01.v1"
SCOPE = "bounded_local_fixture_only"
ECONOMIC_EFFECT = "simulated_quote_only"
CANONICAL_LINEAGE = "local_only_not_applicable"
MATERIALIZATION_STATUS = "unresolved"
MAX_OUTPUT_BYTES = 1_048_576
DECIMAL_CONTEXT = Context(prec=50, rounding=ROUND_HALF_EVEN, Emin=-64, Emax=64)
MAX_DECIMAL_DIGITS = 50
MAX_DECIMAL_EXPONENT = 18
MAX_DECIMAL_TEXT_LENGTH = 128
MAX_EVENT_ID_LENGTH = 256
SIM_SUBMITTER_AGENT_ID = "f" * 96
SIM_BACKWARD_CREATORS = (
    "1" * 96,
    "2" * 96,
    "3" * 96,
)

ASSESSMENT_KEYS = frozenset(
    {
        "structural_closure",
        "computational_contract",
        "historical_production_authority",
        "present_artifact_eligibility",
        "current_observer_permission",
        "use_time_readiness",
    }
)
ASSESSMENT_VALUES = {
    "structural_closure": frozenset(
        {"complete", "missing", "contradictory", "resource_exhausted"}
    ),
    "computational_contract": frozenset({"affirmative", "negative", "unresolved"}),
    "historical_production_authority": frozenset(
        {"affirmative", "negative", "unresolved"}
    ),
    "present_artifact_eligibility": frozenset(
        {"affirmative", "negative", "unresolved"}
    ),
    "current_observer_permission": frozenset(
        {"affirmative", "negative", "unresolved"}
    ),
    "use_time_readiness": frozenset({"ready", "not_ready", "unresolved"}),
}
INPUT_KEYS = frozenset(
    {"scenario_id", "event_id", "assessments", "repetitions", "event_budget_ecu"}
)
SCENARIO_IDS = (
    "useful_reduction",
    "costly_little_reuse",
    "stale_dependency",
    "valid_counterexample",
    "misleading_verification",
    "repeated_submissions",
    "genesis_ordinary_direct",
    "genesis_backward",
    "genesis_invite_fee_zero",
    "node0_authority_only",
    "genesis_governance_vs_productive",
    "no_duplicate_payment",
)

AUTHORITY_REFS = {
    "useful_reduction": ("CDL-081",),
    "costly_little_reuse": ("CDL-081",),
    "stale_dependency": ("CDL-081", "Phase-1620-readiness-boundary"),
    "valid_counterexample": ("CDL-083",),
    "misleading_verification": ("CDL-081", "Phase-1618-claim-boundary"),
    "repeated_submissions": ("CDL-081",),
    "genesis_ordinary_direct": ("CDL-081", "CDL-102"),
    "genesis_backward": ("CDL-102", "CDL-108", "CDL-114", "CDL-119"),
    "genesis_invite_fee_zero": ("CDL-102",),
    "node0_authority_only": ("ADR-0037", "CDL-102"),
    "genesis_governance_vs_productive": ("CDL-081", "CDL-108"),
    "no_duplicate_payment": ("CDL-081", "CDL-084", "CDL-108", "CDL-119"),
}

EVENT_CLASSES = {
    "useful_reduction": "REUSE",
    "costly_little_reuse": "NO_ELIGIBLE_EVENT",
    "stale_dependency": "REUSE_REJECTED_STALE",
    "valid_counterexample": "REFUTATION",
    "misleading_verification": "REUSE_REJECTED_SCOPE",
    "repeated_submissions": "REUSE",
    "genesis_ordinary_direct": "REUSE",
    "genesis_backward": "CDL108_BACKWARD",
    "genesis_invite_fee_zero": "INVITE_SPECIAL_FEE_REJECTED",
    "node0_authority_only": "AUTHORITY_ONLY_NO_ECONOMIC_EVENT",
    "genesis_governance_vs_productive": "GOVERNANCE_AND_REUSE",
    "no_duplicate_payment": "DISTINCT_CHANNELS_WITH_DEDUPLICATION",
}

BENCHMARK_REFS = {
    "useful_reduction": ("different_input_equivalent_operation_one_call_avoided",),
    "costly_little_reuse": ("low_reuse_no_semantic_hit",),
    "stale_dependency": ("changed_dependency_invalidates_cache",),
    "valid_counterexample": ("invalid_claim_rejected_before_computation",),
    "misleading_verification": ("changed_scope_invalidates_cache",),
    "repeated_submissions": ("cache_key_binds_contract_and_scope",),
    "genesis_ordinary_direct": ("type_does_not_create_performance_or_credit_multiplier",),
    "genesis_backward": ("performance_evidence_does_not_replace_attribution_authority",),
    "genesis_invite_fee_zero": ("no_benchmark_basis_for_referral_fee",),
    "node0_authority_only": ("authority_is_not_computational_utility",),
    "genesis_governance_vs_productive": ("usefulness_requires_separate_eligible_event",),
    "no_duplicate_payment": ("exact_caching_and_semantic_reuse_are_distinct_modes",),
}

NON_CLAIMS = (
    "no_live_ecu_accrual",
    "no_ilc_settlement",
    "no_canonical_sufficiency_node",
    "no_production_authority",
    "no_transferable_performance_claim",
)


def _decimal(value: object, token: str) -> Decimal:
    if isinstance(value, bool) or isinstance(value, float):
        raise ValueError(token)
    if isinstance(value, Decimal):
        number = value
    elif isinstance(value, int):
        number = Decimal(value)
    elif isinstance(value, str):
        if len(value) > MAX_DECIMAL_TEXT_LENGTH:
            raise ValueError(token)
        try:
            number = Decimal(value)
        except InvalidOperation as exc:
            raise ValueError(token) from exc
    else:
        raise ValueError(token)
    if not number.is_finite():
        raise ValueError(token)
    digits = number.as_tuple().digits
    exponent = number.as_tuple().exponent
    if len(digits) > MAX_DECIMAL_DIGITS or abs(exponent) > MAX_DECIMAL_EXPONENT:
        raise ValueError(token)
    return number


def _decimal_string(value: Decimal) -> str:
    if not isinstance(value, Decimal) or not value.is_finite():
        raise ValueError("sim_quote_must_be_finite_decimal")
    return format(value, "f")


def _eligible_assessments() -> dict[str, str]:
    return {
        "structural_closure": "complete",
        "computational_contract": "affirmative",
        "historical_production_authority": "affirmative",
        "present_artifact_eligibility": "affirmative",
        "current_observer_permission": "affirmative",
        "use_time_readiness": "ready",
    }


def _validate_assessments(value: object) -> dict[str, str]:
    if not isinstance(value, Mapping) or set(value) != ASSESSMENT_KEYS:
        raise ValueError("sim_assessments_schema_invalid")
    normalized: dict[str, str] = {}
    for key in sorted(ASSESSMENT_KEYS):
        item = value[key]
        if not isinstance(item, str) or item not in ASSESSMENT_VALUES[key]:
            raise ValueError("sim_assessment_value_invalid")
        normalized[key] = item
    return normalized


def _use_gate_decision(assessments: Mapping[str, str]) -> str | None:
    if assessments["structural_closure"] != "complete":
        return "unresolved_pending_evidence"
    if any(
        assessments[key] == "negative"
        for key in (
            "computational_contract",
            "historical_production_authority",
            "present_artifact_eligibility",
            "current_observer_permission",
        )
    ):
        return "rejected_use"
    if any(
        assessments[key] == "unresolved"
        for key in (
            "computational_contract",
            "historical_production_authority",
            "present_artifact_eligibility",
            "current_observer_permission",
        )
    ):
        return "unresolved_pending_evidence"
    if assessments["use_time_readiness"] != "ready":
        return "unresolved_pending_evidence"
    return None


def _validate_input(value: object) -> dict[str, Any]:
    if not isinstance(value, Mapping) or set(value) != INPUT_KEYS:
        raise ValueError("sim_scenario_schema_invalid")
    scenario_id = value["scenario_id"]
    if not isinstance(scenario_id, str) or scenario_id not in SCENARIO_IDS:
        raise ValueError("sim_scenario_id_invalid")
    event_id = value["event_id"]
    if (
        not isinstance(event_id, str)
        or not event_id
        or len(event_id) > MAX_EVENT_ID_LENGTH
        or event_id != event_id.strip()
    ):
        raise ValueError("sim_event_id_invalid")
    repetitions = value["repetitions"]
    if type(repetitions) is not int or repetitions < 1 or repetitions > 100:
        raise ValueError("sim_repetitions_invalid")
    budget = _decimal(value["event_budget_ecu"], "sim_event_budget_invalid")
    if budget <= Decimal("0"):
        raise ValueError("sim_event_budget_invalid")
    return {
        "scenario_id": scenario_id,
        "event_id": event_id,
        "assessments": _validate_assessments(value["assessments"]),
        "repetitions": repetitions,
        "event_budget_ecu": budget,
    }


def explicit_provenance_quote(hop: int) -> Decimal:
    """Return the CDL-084 quote for one one-indexed explicit-provenance hop."""
    if type(hop) is not int or hop < 1 or hop > PROVENANCE_MAX_DEPTH:
        raise ValueError("explicit_provenance_hop_invalid")
    with localcontext(DECIMAL_CONTEXT):
        return REUSE_ATTRIBUTION_RATE * (PROVENANCE_DECAY_ALPHA**hop)


def _quote(
    *,
    event_id: str,
    channel: str,
    contribution_basis: str,
    recipient_id: str,
    amount: Decimal,
    authority_ref: str,
) -> dict[str, str]:
    preimage = json.dumps(
        [event_id, channel, contribution_basis, recipient_id],
        ensure_ascii=False,
        allow_nan=False,
        separators=(",", ":"),
    ).encode("utf-8")
    deduplication_key = "sha256:" + hashlib.sha256(
        b"ilc.sufficiency.quote-dedup.v1\x00" + preimage
    ).hexdigest()
    return {
        "event_id": event_id,
        "channel": channel,
        "contribution_basis": contribution_basis,
        "recipient_id": recipient_id,
        "amount_ecu": _decimal_string(amount),
        "authority_ref": authority_ref,
        "deduplication_key": deduplication_key,
    }


def _deduplicate_quotes(quotes: Sequence[Mapping[str, str]]) -> list[dict[str, str]]:
    seen: set[str] = set()
    result: list[dict[str, str]] = []
    for quote in quotes:
        key = quote.get("deduplication_key")
        if not isinstance(key, str) or not key:
            raise ValueError("sim_quote_deduplication_key_invalid")
        if key in seen:
            continue
        seen.add(key)
        result.append(dict(quote))
    return result


def _backward_quotes(event_id: str, budget: Decimal) -> tuple[list[dict[str, str]], dict[str, str]]:
    nodes = {
        "work": {
            "artifact_type": "claim",
            "recipient_agent_id": "agent:worker",
            "created_epoch": 16,
            "status_quality_weight": "1",
            "novelty_score": "1",
        },
        "upstream_genesis": {
            "artifact_type": "method",
            "recipient_agent_id": SIM_BACKWARD_CREATORS[0],
            "created_epoch": 16,
            "status_quality_weight": "1",
            "novelty_score": "1",
        },
        "upstream_peer_a": {
            "artifact_type": "dataset",
            "recipient_agent_id": SIM_BACKWARD_CREATORS[1],
            "created_epoch": 16,
            "status_quality_weight": "1",
            "novelty_score": "1",
        },
        "upstream_peer_b": {
            "artifact_type": "evidence",
            "recipient_agent_id": SIM_BACKWARD_CREATORS[2],
            "created_epoch": 16,
            "status_quality_weight": "1",
            "novelty_score": "1",
        },
    }
    edges = [
        {
            "source_node_id": "work",
            "target_node_id": target,
            "edge_type": "REUSE",
            "edge_confidence": "1",
        }
        for target in ("upstream_genesis", "upstream_peer_a", "upstream_peer_b")
    ]
    guard_passed, guard_token, creator_count = _check_sybil_diversity_guard(
        list(SIM_BACKWARD_CREATORS), SIM_SUBMITTER_AGENT_ID
    )
    if not guard_passed:
        raise ValueError("sim_cdl114_sybil_diversity_guard_failed")
    with localcontext(DECIMAL_CONTEXT):
        result = BackwardAttributionTraversal(nodes, edges).traverse(
            "work",
            event_id=event_id,
            event_budget_ecu=budget,
            event_epoch=16,
            apply_antigaming_caps=True,
        )
    quotes = [
        _quote(
            event_id=event_id,
            channel="CDL108_BACKWARD",
            contribution_basis=f"upstream:{item.upstream_artifact_id}",
            recipient_id=item.recipient_agent_id,
            amount=item.final_credit_ecu,
            authority_ref="CDL-108",
        )
        for item in result.final_credits
    ]
    details = {
        "event_budget_ecu": _decimal_string(result.event_budget_ecu),
        "backward_pool_ecu": _decimal_string(result.backward_pool_ecu),
        "forward_retained_ecu": _decimal_string(result.forward_retained_ecu),
        "node_cap_amount_ecu": _decimal_string(result.node_cap_amount_ecu),
        "agent_cap_amount_ecu": _decimal_string(result.agent_cap_amount_ecu),
        "cluster_cap_amount_ecu": _decimal_string(result.cluster_cap_amount_ecu),
        "unissued_backward_pool_ecu": _decimal_string(result.unissued_backward_pool_ecu),
        "sybil_diversity_status": guard_token,
        "distinct_source_ref_creator_count": str(creator_count),
    }
    return quotes, details


def build_fixture_inputs() -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for scenario_id in SCENARIO_IDS:
        assessments = _eligible_assessments()
        repetitions = 5 if scenario_id in {"repeated_submissions", "no_duplicate_payment"} else 1
        if scenario_id == "stale_dependency":
            assessments["present_artifact_eligibility"] = "negative"
            assessments["use_time_readiness"] = "unresolved"
        elif scenario_id == "valid_counterexample":
            assessments["computational_contract"] = "negative"
        elif scenario_id == "misleading_verification":
            assessments["computational_contract"] = "negative"
        elif scenario_id in {
            "costly_little_reuse",
            "genesis_invite_fee_zero",
            "node0_authority_only",
        }:
            assessments["use_time_readiness"] = "not_ready"
        records.append(
            {
                "scenario_id": scenario_id,
                "event_id": f"event:phase1623:{scenario_id}",
                "assessments": assessments,
                "repetitions": repetitions,
                "event_budget_ecu": "1",
            }
        )
    return records


def evaluate_scenario(value: object) -> dict[str, Any]:
    item = _validate_input(value)
    scenario_id = item["scenario_id"]
    event_id = item["event_id"]
    quotes: list[dict[str, str]] = []
    details: dict[str, Any] = {}
    reasons: list[str] = []

    gated_scenarios = {
        "useful_reduction",
        "repeated_submissions",
        "genesis_ordinary_direct",
        "genesis_backward",
        "genesis_governance_vs_productive",
        "no_duplicate_payment",
    }
    gate_decision = _use_gate_decision(item["assessments"])
    if scenario_id == "valid_counterexample":
        required_refutation_state = _eligible_assessments()
        required_refutation_state["computational_contract"] = "negative"
        if item["assessments"] != required_refutation_state:
            return {
                "scenario_id": scenario_id,
                "authority_refs": list(AUTHORITY_REFS[scenario_id]),
                "modeled_event_class": EVENT_CLASSES[scenario_id],
                "assessments": item["assessments"],
                "canonical_genesis_lineage": CANONICAL_LINEAGE,
                "materialization_status": MATERIALIZATION_STATUS,
                "decision": gate_decision or "no_upheld_refutation_event",
                "quote_records": [],
                "total_quote_ecu": "0",
                "deduplication_key": event_id,
                "raw_quote_count": 0,
                "deduplicated_quote_count": 0,
                "reason_codes": ["upheld_refutation_assessments_not_satisfied"],
                "benchmark_finding_refs": list(BENCHMARK_REFS[scenario_id]),
                "details": {},
                "non_claims": list(NON_CLAIMS),
            }
    if scenario_id in gated_scenarios and gate_decision is not None:
        return {
            "scenario_id": scenario_id,
            "authority_refs": list(AUTHORITY_REFS[scenario_id]),
            "modeled_event_class": EVENT_CLASSES[scenario_id],
            "assessments": item["assessments"],
            "canonical_genesis_lineage": CANONICAL_LINEAGE,
            "materialization_status": MATERIALIZATION_STATUS,
            "decision": gate_decision,
            "quote_records": [],
            "total_quote_ecu": "0",
            "deduplication_key": event_id,
            "raw_quote_count": 0,
            "deduplicated_quote_count": 0,
            "reason_codes": ["six_assessment_use_gate_not_satisfied"],
            "benchmark_finding_refs": list(BENCHMARK_REFS[scenario_id]),
            "details": {},
            "non_claims": list(NON_CLAIMS),
        }

    if scenario_id == "useful_reduction":
        quotes.append(
            _quote(
                event_id=event_id,
                channel="CDL081_DIRECT",
                contribution_basis="eligible_reuse",
                recipient_id="agent:claim-author",
                amount=REUSE_ATTRIBUTION_RATE,
                authority_ref="CDL-081",
            )
        )
        decision = "authorized_reuse"
        reasons.append("eligible_reuse_event_not_usefulness_multiplier")
    elif scenario_id == "costly_little_reuse":
        decision = "no_eligible_attribution_event"
        reasons.append("verification_cost_alone_is_not_attribution")
    elif scenario_id == "stale_dependency":
        decision = "rejected_use"
        reasons.append("present_artifact_eligibility_negative")
    elif scenario_id == "valid_counterexample":
        quotes.append(
            _quote(
                event_id=event_id,
                channel="CDL083_REFUTATION",
                contribution_basis="upheld_refutation",
                recipient_id="agent:refuter",
                amount=REUSE_ATTRIBUTION_RATE,
                authority_ref="CDL-083",
            )
        )
        decision = "rejected_claim_refutation_credited"
        reasons.extend(("claim_reuse_rejected", "separate_upheld_refutation_event"))
    elif scenario_id == "misleading_verification":
        decision = "rejected_use"
        reasons.append("verification_scope_does_not_cover_claimed_operation")
    elif scenario_id == "repeated_submissions":
        quote = _quote(
            event_id=event_id,
            channel="CDL081_DIRECT",
            contribution_basis="eligible_reuse",
            recipient_id="agent:claim-author",
            amount=REUSE_ATTRIBUTION_RATE,
            authority_ref="CDL-081",
        )
        quotes.extend(dict(quote) for _ in range(item["repetitions"]))
        decision = "authorized_reuse"
        reasons.append("duplicate_event_quotes_collapsed")
    elif scenario_id == "genesis_ordinary_direct":
        quotes.append(
            _quote(
                event_id=event_id,
                channel="CDL081_DIRECT",
                contribution_basis="eligible_productive_reuse",
                recipient_id="agent:genesis",
                amount=REUSE_ATTRIBUTION_RATE,
                authority_ref="CDL-081",
            )
        )
        decision = "authorized_direct_attribution"
        reasons.append("genesis_uses_ordinary_rate_without_multiplier")
    elif scenario_id == "genesis_backward":
        quotes, details = _backward_quotes(event_id, item["event_budget_ecu"])
        decision = "authorized_backward_attribution"
        reasons.extend(("cdl108_caps_applied", "no_special_invite_amount"))
    elif scenario_id == "genesis_invite_fee_zero":
        decision = "no_special_referral_fee"
        reasons.append("cdl102_rejects_fixed_referral_fee")
    elif scenario_id == "node0_authority_only":
        decision = "no_eligible_attribution_event"
        reasons.append("authority_role_is_not_productive_event")
    elif scenario_id == "genesis_governance_vs_productive":
        quotes.append(
            _quote(
                event_id=event_id,
                channel="CDL081_DIRECT",
                contribution_basis="separate_productive_reuse",
                recipient_id="agent:genesis",
                amount=REUSE_ATTRIBUTION_RATE,
                authority_ref="CDL-081",
            )
        )
        decision = "authorized_direct_attribution"
        reasons.extend(("governance_control_quote_zero", "productive_event_quote_ordinary"))
    elif scenario_id == "no_duplicate_payment":
        direct = _quote(
            event_id=event_id,
            channel="CDL081_DIRECT",
            contribution_basis="eligible_reuse",
            recipient_id="agent:claim-author",
            amount=REUSE_ATTRIBUTION_RATE,
            authority_ref="CDL-081",
        )
        quotes.extend(dict(direct) for _ in range(item["repetitions"]))
        backward, details = _backward_quotes(
            f"{event_id}:distinct-backward-contribution",
            item["event_budget_ecu"],
        )
        quotes.extend(backward)
        details["separate_non_ecu_mechanism"] = "CDL-029_Genesis_ILC_tranche_not_counted"
        decision = "authorized_distinct_contributions_deduplicated"
        reasons.extend(("exact_duplicates_collapsed", "distinct_contributions_preserved"))
    else:  # pragma: no cover - validated above
        raise ValueError("sim_scenario_id_invalid")

    raw_quote_count = len(quotes)
    quotes = _deduplicate_quotes(quotes)
    with localcontext(DECIMAL_CONTEXT):
        total = sum(
            (_decimal(q["amount_ecu"], "sim_quote_amount_invalid") for q in quotes),
            Decimal("0"),
        )
    return {
        "scenario_id": scenario_id,
        "authority_refs": list(AUTHORITY_REFS[scenario_id]),
        "modeled_event_class": EVENT_CLASSES[scenario_id],
        "assessments": item["assessments"],
        "canonical_genesis_lineage": CANONICAL_LINEAGE,
        "materialization_status": MATERIALIZATION_STATUS,
        "decision": decision,
        "quote_records": quotes,
        "total_quote_ecu": _decimal_string(total),
        "deduplication_key": event_id,
        "raw_quote_count": raw_quote_count,
        "deduplicated_quote_count": len(quotes),
        "reason_codes": reasons,
        "benchmark_finding_refs": list(BENCHMARK_REFS[scenario_id]),
        "details": details,
        "non_claims": list(NON_CLAIMS),
    }


def build_results(inputs: Sequence[object] | None = None) -> dict[str, Any]:
    records = list(build_fixture_inputs() if inputs is None else inputs)
    if len(records) != len(SCENARIO_IDS):
        raise ValueError("sim_scenario_count_invalid")
    evaluated = [evaluate_scenario(item) for item in records]
    ids = [item["scenario_id"] for item in evaluated]
    if len(ids) != len(set(ids)) or set(ids) != set(SCENARIO_IDS):
        raise ValueError("sim_scenario_identity_set_invalid")
    return {
        "schema_version": SCHEMA_VERSION,
        "scope": SCOPE,
        "economic_effect": ECONOMIC_EFFECT,
        "authority_parameters": {
            "cdl081_direct_rate": _decimal_string(REUSE_ATTRIBUTION_RATE),
            "cdl084_provenance_decay_alpha": _decimal_string(PROVENANCE_DECAY_ALPHA),
            "cdl084_provenance_max_depth": PROVENANCE_MAX_DEPTH,
            "cdl085_phi_bound": _decimal_string(EDGE_MINT_PHI_BOUND),
            "cdl108_backward_pool_share": _decimal_string(
                BACKWARD_ATTRIBUTION_BACKWARD_POOL_SHARE_BETA
            ),
            "cdl108_per_node_cap_share": _decimal_string(BACKWARD_ATTRIBUTION_PER_NODE_CAP),
            "cdl108_per_agent_cap_share": _decimal_string(BACKWARD_ATTRIBUTION_PER_AGENT_CAP),
            "cdl108_per_cluster_cap_share": _decimal_string(BACKWARD_ATTRIBUTION_PER_CLUSTER_CAP),
            "explicit_provenance_hop_1_quote": _decimal_string(explicit_provenance_quote(1)),
        },
        "modeled_record_forms": [
            "SufficiencyClaim",
            "TranslationPassport",
            "TensorPayloadDescriptor",
        ],
        "scenarios": evaluated,
        "non_claims": list(NON_CLAIMS),
    }


def canonical_json_bytes(value: object) -> bytes:
    return (
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")


def _summary(results: Mapping[str, Any]) -> str:
    lines = [
        "<!-- PUBLIC_RC_EXCLUDE: generated_research_output -->",
        "",
        "# Phase 1623 Sufficiency Attribution SIM Summary",
        "",
        "All values are local simulated quotes. No ECU accrued and no CDL opened.",
        "",
        "| Scenario | Decision | Total simulated ECU quote |",
        "|---|---|---:|",
    ]
    for item in results["scenarios"]:
        lines.append(
            f"| `{item['scenario_id']}` | `{item['decision']}` | `{item['total_quote_ecu']}` |"
        )
    lines.extend(
        (
            "",
            "Candidate sufficiency materialization remains unresolved; this run uses local-only lineage.",
            "",
        )
    )
    return "\n".join(lines)


def _atomic_write(path: Path, payload: bytes) -> None:
    if len(payload) > MAX_OUTPUT_BYTES:
        raise ValueError("sim_output_exceeds_maximum_bytes")
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.")
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_name, path)
    except BaseException:
        try:
            os.unlink(temp_name)
        except FileNotFoundError:
            pass
        raise


def write_outputs(output_dir: Path) -> dict[str, Any]:
    results = build_results()
    result_bytes = canonical_json_bytes(results)
    summary_bytes = _summary(results).encode("utf-8")
    _atomic_write(output_dir / "sim_results.json", result_bytes)
    _atomic_write(output_dir / "sim_summary.md", summary_bytes)
    return results


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("out/sim_sufficiency_hyperedge_01"),
    )
    args = parser.parse_args()
    results = write_outputs(args.output_dir)
    print(f"scenario_count={len(results['scenarios'])}")
    print(f"results_path={args.output_dir / 'sim_results.json'}")
    print(f"summary_path={args.output_dir / 'sim_summary.md'}")
    print("economic_effect=simulated_quote_only")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
