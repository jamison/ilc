"""Phase 1417 review lane integration tests.

Required tokens:
review_lane_wiring_complete_phase_1417
review_lane_integration_tests_complete_phase_1417
review_lane_production_not_activated_phase_1417
j008_review_lane_condition_evidence_phase_1417
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from ilc_core.epistemic import review_lane_admission_runtime as runtime
from ilc_core.epistemic.jury_activation_gate import (
    GateConditionStatus,
    evaluate_jury_activation_gate,
)
from ilc_core.epistemic.review_lane_admission_runtime import (
    ReviewLaneAdmissionRequest,
    ReviewerAttestation,
    TaxonomyClass,
    quote_review_lane_admission_with_stubs,
    require_production_review_lane_activation,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
RUNTIME_PATH = REPO_ROOT / "ilc_core/epistemic/review_lane_admission_runtime.py"

REVIEW_LANE_WIRING_COMPLETE_TOKEN = "review_lane_wiring_complete_phase_1417"
REVIEW_LANE_INTEGRATION_TESTS_COMPLETE_TOKEN = (
    "review_lane_integration_tests_complete_phase_1417"
)
REVIEW_LANE_PRODUCTION_NOT_ACTIVATED_PHASE_1417 = (
    "review_lane_production_not_activated_phase_1417"
)
J008_REVIEW_LANE_CONDITION_EVIDENCE_TOKEN = "j008_review_lane_condition_evidence_phase_1417"


def _approvals(count: int = 5, *, outsider: bool = False) -> list[ReviewerAttestation]:
    return [
        ReviewerAttestation(
            reviewer_agent_id=f"reviewer-{index}",
            verdict="approve",
            outsider_reviewer=(outsider and index == count - 1),
        )
        for index in range(count)
    ]


def _request(**overrides: object) -> ReviewLaneAdmissionRequest:
    values: dict[str, object] = {
        "submission_id": "submission-1417",
        "submission_content_hash": "sha256:" + "d" * 64,
        "current_taxonomy_class": TaxonomyClass.T0_5_PENDING_PUBLIC_INGESTION,
        "target_taxonomy_class": TaxonomyClass.T1_PUBLIC_NON_REWARD_METADATA,
        "submitter_agent_id": "agent-submit",
        "review_epoch": 9,
        "review_lane": "metadata",
        "reviewer_attestations": _approvals(),
        "canonical_external_id": "doi:10.1234/phase1417",
    }
    values.update(overrides)
    return ReviewLaneAdmissionRequest(**values)


def test_phase_1417_tokens_are_recorded_in_source() -> None:
    source = Path(__file__).read_text(encoding="utf-8")

    assert REVIEW_LANE_WIRING_COMPLETE_TOKEN in source
    assert REVIEW_LANE_INTEGRATION_TESTS_COMPLETE_TOKEN in source
    assert REVIEW_LANE_PRODUCTION_NOT_ACTIVATED_PHASE_1417 in source
    assert J008_REVIEW_LANE_CONDITION_EVIDENCE_TOKEN in source


def test_full_happy_path_t0_5_to_t1_plus_promotion() -> None:
    quote = quote_review_lane_admission_with_stubs(_request())

    assert quote.admission_decision.admitted is True
    assert quote.admission_decision.admission_action == "promote_new_public_node"
    assert quote.dedup_evidence.dedup_result == "no_duplicate_found"
    assert quote.payment_stub_count == 5
    assert quote.payment_settlement_authorized is False
    assert quote.ledger_write_authorized is False
    assert quote.treasury_write_authorized is False
    assert quote.wallet_write_authorized is False
    assert quote.ecu_distribution_authorized is False


def test_insufficient_reviewer_count_rejection() -> None:
    quote = quote_review_lane_admission_with_stubs(
        _request(reviewer_attestations=_approvals(4))
    )

    assert quote.admission_decision.admitted is False
    assert "review_lane_insufficient_reviewer_count" in quote.admission_decision.failure_reasons
    assert quote.payment_stub_count == 0


def test_approval_quorum_not_met_rejection() -> None:
    attestations = _approvals(4)
    attestations.append(ReviewerAttestation(reviewer_agent_id="reviewer-reject", verdict="reject"))

    quote = quote_review_lane_admission_with_stubs(
        _request(reviewer_attestations=attestations)
    )

    assert quote.admission_decision.admitted is False
    assert "review_lane_approval_quorum_not_met" in quote.admission_decision.failure_reasons


def test_wrong_source_taxonomy_rejection() -> None:
    quote = quote_review_lane_admission_with_stubs(
        _request(current_taxonomy_class=TaxonomyClass.T0_PRIVATE_LOCAL_DRAFT)
    )

    assert quote.admission_decision.admitted is False
    assert "review_lane_wrong_source_taxonomy" in quote.admission_decision.failure_reasons


def test_invalid_target_taxonomy_rejection() -> None:
    quote = quote_review_lane_admission_with_stubs(
        _request(target_taxonomy_class=TaxonomyClass.T0_5_PENDING_PUBLIC_INGESTION)
    )

    assert quote.admission_decision.admitted is False
    assert "review_lane_invalid_target_taxonomy" in quote.admission_decision.failure_reasons


def test_outsider_approval_missing_for_high_value_lane() -> None:
    quote = quote_review_lane_admission_with_stubs(
        _request(target_taxonomy_class=TaxonomyClass.T3_CONTESTED_HIGH_VALUE_OBJECTIVE_NODE)
    )

    assert quote.admission_decision.admitted is False
    assert "review_lane_outsider_approval_missing" in quote.admission_decision.failure_reasons


def test_high_value_lane_with_outsider_approval_passes() -> None:
    quote = quote_review_lane_admission_with_stubs(
        _request(
            target_taxonomy_class=TaxonomyClass.T3_CONTESTED_HIGH_VALUE_OBJECTIVE_NODE,
            reviewer_attestations=_approvals(5, outsider=True),
        )
    )

    assert quote.admission_decision.admitted is True
    assert quote.admission_decision.outsider_approval_count == 1


def test_duplicate_external_id_routes_to_attestation_to_existing() -> None:
    quote = quote_review_lane_admission_with_stubs(
        _request(),
        known_external_ids={"doi:10.1234/phase1417": "node-existing"},
    )

    assert quote.dedup_evidence.dedup_result == "attestation_to_existing"
    assert quote.admission_decision.admission_action == "attest_to_existing_node"
    assert quote.admission_decision.existing_node_id == "node-existing"


def test_content_hash_fallback_when_canonical_external_id_absent() -> None:
    content_hash = "sha256:" + "e" * 64
    quote = quote_review_lane_admission_with_stubs(
        _request(canonical_external_id=None, submission_content_hash=content_hash),
        known_content_hashes={content_hash: "node-content"},
    )

    assert quote.dedup_evidence.dedup_key_kind == "submission_content_hash"
    assert quote.dedup_evidence.dedup_result == "attestation_to_existing"
    assert quote.admission_decision.admission_action == "attest_to_existing_node"


def test_payment_stub_output_preserves_default_off_fields() -> None:
    quote = quote_review_lane_admission_with_stubs(_request())

    for stub in quote.reviewer_payment_stubs:
        assert stub["payment_enqueued"] is False
        assert stub["ledger_write_authorized"] is False
        assert stub["treasury_write_authorized"] is False
        assert stub["wallet_write_authorized"] is False
        assert stub["ecu_distribution_authorized"] is False
        assert stub["settlement_authorized"] is False


def test_production_not_activated_flag_and_fail_closed_check() -> None:
    assert runtime.REVIEW_LANE_PRODUCTION_NOT_ACTIVATED is True
    with pytest.raises(ValueError, match="review_lane_production_not_activated"):
        require_production_review_lane_activation()


def test_source_hygiene_for_review_lane_stack() -> None:
    source = RUNTIME_PATH.read_text(encoding="utf-8")
    tree = ast.parse(source)

    assert "import random" not in source
    assert "SIGNING_KEY" not in source
    assert "PRIVATE_KEY" not in source
    assert "float(" not in source
    assert not [node for node in ast.walk(tree) if isinstance(node, ast.Assert)]


def test_j008_review_lane_condition_evidence_recorded_but_gate_not_patched() -> None:
    report = evaluate_jury_activation_gate()
    condition_by_id = {condition.condition_id: condition for condition in report.conditions}

    condition = condition_by_id["REVIEW_LANE_WIRING_COMPLETE"]
    assert condition.status is GateConditionStatus.NOT_MET
    assert "REVIEW_LANE_WIRING_COMPLETE" in report.blocking_not_met
    assert report.verdict == "INCOMPLETE"
