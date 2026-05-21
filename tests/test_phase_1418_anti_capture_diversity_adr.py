"""Regression tests for Phase 1418 ADR-0044 anti-capture diversity design."""

from __future__ import annotations

from pathlib import Path

from ilc_core.consensus import diversity_floor_runtime
from ilc_core.epistemic import jury_assignment_runtime
from ilc_core.epistemic.jury_activation_gate import (
    GateConditionStatus,
    evaluate_jury_activation_gate,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
ADR_PATH = REPO_ROOT / "docs/adr/ADR_0044_Anti_Capture_Diversity_Verification.md"


def _adr_text() -> str:
    return ADR_PATH.read_text(encoding="utf-8")


def test_adr_0044_exists_with_required_phase_tokens() -> None:
    text = _adr_text()

    assert ADR_PATH.exists()
    assert "anti_capture_diversity_adr_accepted_phase_1418" in text
    assert "cdl_v3_jury_assignment_wiring_defined_phase_1418" in text
    assert "vrf_outsider_selection_contract_defined_phase_1418" in text
    assert "anti_capture_diversity_not_verified_phase_1418" in text


def test_adr_records_current_runtime_claims_from_repo() -> None:
    text = _adr_text()

    assert diversity_floor_runtime.CDL_V3_RUNTIME_VERSION == (
        "cdl_v3_diversity_floor_runtime_397.v0.1"
    )
    assert hasattr(jury_assignment_runtime.EligibleAgent, "__dataclass_fields__")
    assert "cluster_id" in jury_assignment_runtime.EligibleAgent.__dataclass_fields__
    assert jury_assignment_runtime._INDEPENDENCE_K == 3
    assert jury_assignment_runtime._MAX_PER_OPERATOR_DOMAIN == 4
    assert "compute_max_cluster_share(...)" in text
    assert "vrf_verifier_integrated_jury_assignment_phase_1412" in text


def test_adr_distinguishes_already_wired_from_phase_1419_required_work() -> None:
    text = _adr_text()

    assert "## Already-Wired Invariants" in text
    assert "## Phase 1419 CDL-V3 Wiring Contract" in text
    assert "These surfaces are necessary but not sufficient" in text
    assert "CDL-V3 cluster-level diversity floor" in text


def test_adr_defines_jury_cluster_diversity_constants() -> None:
    text = _adr_text()

    assert "JURY_CLUSTER_DIVERSITY_FLOOR = 4" in text
    assert "JURY_MAX_CLUSTER_SHARE_CEILING = 0.40" in text
    assert "This is a jury-panel anti-capture ceiling, not a validator-topology ceiling" in text


def test_adr_defines_selected_panel_evidence_contract() -> None:
    text = _adr_text()

    assert "selected_panel = regular_panel + outsider_panel" in text
    assert "distinct_clusters >= JURY_CLUSTER_DIVERSITY_FLOOR" in text
    assert "max_cluster_share <= JURY_MAX_CLUSTER_SHARE_CEILING" in text
    assert "jury_cluster_diversity_floor_not_met" in text
    assert "jury_max_cluster_share_ceiling_exceeded" in text
    assert "anti_capture_diversity_verified_phase_1419" in text


def test_adr_defines_vrf_outsider_selection_contract() -> None:
    text = _adr_text()

    assert "outsider_candidate_flag=True" in text
    assert "same VRF-derived score basis as regular selection" in text
    assert "must not silently fall back to epoch-hash shadow assignment" in text


def test_adr_phase_1419_evidence_requirements_are_complete() -> None:
    text = _adr_text()

    for phrase in (
        "Non-audit high-value assignment still fails closed",
        'assignment_mode="vrf_verified"',
        "at least 4 distinct clusters",
        "max cluster share no greater than `0.40`",
        "one-cluster or two-cluster candidate pool cannot produce a verified panel",
        "4 of 8 selected seats in one cluster fails closed",
        "J-008 gate source remains unchanged until Phase 1425",
    ):
        assert phrase in text


def test_adr_non_activation_section_forbids_runtime_and_gate_flip() -> None:
    text = _adr_text()

    assert "modify `jury_assignment_runtime.py`" in text
    assert "mark `ANTI_CAPTURE_DIVERSITY_VERIFIED` as MET" in text
    assert "modify `jury_activation_gate.py`" in text
    assert "activate production jury assignment" in text
    assert "mutate ledger, treasury, wallet, graph, or CDL state" in text


def test_j008_anti_capture_condition_met_after_phase_1425_and_1427() -> None:
    report = evaluate_jury_activation_gate()
    condition_by_id = {condition.condition_id: condition for condition in report.conditions}

    condition = condition_by_id["ANTI_CAPTURE_DIVERSITY_VERIFIED"]
    assert condition.status is GateConditionStatus.MET
    assert "ANTI_CAPTURE_DIVERSITY_VERIFIED" not in report.blocking_not_met
    assert report.verdict == "PASS"
