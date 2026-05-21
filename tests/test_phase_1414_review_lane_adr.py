"""Regression tests for Phase 1414 ADR-0043 review-lane wiring."""

from __future__ import annotations

from pathlib import Path

from ilc_core.epistemic.jury_activation_gate import (
    GateConditionStatus,
    evaluate_jury_activation_gate,
)
from ilc_core.epistemic import jury_incentive_runtime

REPO_ROOT = Path(__file__).resolve().parents[1]
ADR_PATH = REPO_ROOT / "docs/adr/ADR_0043_Review_Lane_T0_5_To_T1_Promotion.md"


def _adr_text() -> str:
    return ADR_PATH.read_text(encoding="utf-8")


def test_adr_0043_exists_with_required_phase_tokens() -> None:
    text = _adr_text()

    assert ADR_PATH.exists()
    assert "review_lane_wiring_adr_accepted_phase_1414" in text
    assert "t0_5_to_t1_plus_admission_contract_defined_phase_1414" in text
    assert "reviewer_payment_settlement_stub_contract_defined_phase_1414" in text
    assert "review_lane_runtime_not_implemented_phase_1414" in text
    assert "review_lane_wiring_not_complete_phase_1414" in text


def test_adr_records_admission_gate_constants() -> None:
    text = _adr_text()

    assert "REVIEW_LANE_PANEL_SIZE = 8" in text
    assert "REVIEW_LANE_MIN_ASSIGNED_REVIEWERS = 5" in text
    assert "REVIEW_LANE_APPROVAL_QUORUM = 5" in text
    assert "REVIEW_LANE_OUTSIDER_REVIEWERS_REQUIRED_FOR_HIGH_VALUE = 1" in text
    assert "REVIEW_LANE_PRODUCTION_NOT_ACTIVATED = True" in text


def test_adr_preserves_t0_5_zero_weight_boundary() -> None:
    text = _adr_text()

    assert "T0_5_PENDING_PUBLIC_INGESTION" in text
    assert "zero public weight" in text
    assert "does not itself construct an economic event" in text
    assert "review_lane_public_economics_firewall_required" in text


def test_adr_defines_external_identifier_dedup_contract() -> None:
    text = _adr_text()

    assert "canonical_external_id" in text
    assert "primary dedup key" in text
    assert "attestation_to_existing" in text
    assert "attest_to_existing_node" in text
    assert "Embedding similarity is not a Phase 1415/1416 dedup authority" in text


def test_adr_defines_default_off_payment_stub_contract() -> None:
    text = _adr_text()

    assert "queue_reviewer_payment_stub" in text
    assert "reviewer_payment_not_activated_phase_1401" in text
    assert "payment_enqueued = False" in text
    assert "ledger_write_authorized = False" in text
    assert "treasury_write_authorized = False" in text
    assert "wallet_write_authorized = False" in text
    assert "ecu_distribution_authorized = False" in text
    assert jury_incentive_runtime.REVIEWER_PAYMENT_NOT_ACTIVATED is True


def test_adr_routes_implementation_to_phases_1415_through_1417() -> None:
    text = _adr_text()

    assert "Phase 1415 implements the admission evaluator" in text
    assert "Phase 1416 wires dedup enforcement" in text
    assert "Phase 1417 adds integration tests" in text
    assert "review_lane_wiring_complete_phase_1417" in text


def test_adr_non_activation_section_forbids_runtime_and_gate_flip() -> None:
    text = _adr_text()

    assert "create `ilc_core/epistemic/review_lane_admission_runtime.py`" in text
    assert "mark J-008 `REVIEW_LANE_WIRING_COMPLETE` as MET" in text
    assert "activate reviewer payment" in text
    assert "mutate ledger, treasury, wallet, graph, or CDL state" in text


def test_j008_review_lane_condition_is_met_after_phase_1425_and_1427() -> None:
    report = evaluate_jury_activation_gate()
    condition_by_id = {condition.condition_id: condition for condition in report.conditions}

    condition = condition_by_id["REVIEW_LANE_WIRING_COMPLETE"]
    assert condition.status is GateConditionStatus.MET
    assert "REVIEW_LANE_WIRING_COMPLETE" not in report.blocking_not_met
    assert report.verdict == "PASS"
