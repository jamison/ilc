"""Regression tests for Phase 1415 review lane admission runtime."""

from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

from ilc_core.epistemic import (
    REVIEW_LANE_ADMISSION_VERSION,
    REVIEW_LANE_PRODUCTION_NOT_ACTIVATED,
    REVIEW_LANE_PRODUCTION_NOT_ACTIVATED_TOKEN,
    ReviewLaneAdmissionRequest,
    ReviewerAttestation,
    TaxonomyClass,
    quote_review_lane_admission,
    require_production_review_lane_activation,
    review_lane_decision_canonical_json,
)
from ilc_core.epistemic import review_lane_admission_runtime as runtime

REPO_ROOT = Path(__file__).resolve().parents[1]
RUNTIME_PATH = REPO_ROOT / "ilc_core/epistemic/review_lane_admission_runtime.py"


def _approvals(count: int = 5, *, outsider: bool = False) -> list[ReviewerAttestation]:
    attestations = [
        ReviewerAttestation(
            reviewer_agent_id=f"reviewer-{index}",
            verdict="approve",
            outsider_reviewer=(outsider and index == count - 1),
        )
        for index in range(count)
    ]
    return attestations


def _request(**overrides: object) -> ReviewLaneAdmissionRequest:
    values: dict[str, object] = {
        "submission_id": "submission-1415",
        "submission_content_hash": "sha256:" + "a" * 64,
        "current_taxonomy_class": TaxonomyClass.T0_5_PENDING_PUBLIC_INGESTION,
        "target_taxonomy_class": TaxonomyClass.T1_PUBLIC_NON_REWARD_METADATA,
        "submitter_agent_id": "agent-submit",
        "review_epoch": 7,
        "review_lane": "metadata",
        "reviewer_attestations": _approvals(),
        "canonical_external_id": "doi:10.1234/phase1415",
    }
    values.update(overrides)
    return ReviewLaneAdmissionRequest(**values)


def test_runtime_tokens_and_default_off_guard_exported() -> None:
    assert REVIEW_LANE_ADMISSION_VERSION == "review_lane_admission_runtime_phase_1415.v0.1"
    assert runtime.REVIEW_LANE_ADMISSION_RUNTIME_TOKEN in runtime.PHASE_TOKENS
    assert runtime.ADR_0043_DEPENDENCY in runtime.PHASE_TOKENS
    assert REVIEW_LANE_PRODUCTION_NOT_ACTIVATED is True
    assert REVIEW_LANE_PRODUCTION_NOT_ACTIVATED_TOKEN == (
        "review_lane_production_not_activated_phase_1415"
    )


def test_valid_t0_5_to_t1_request_promotes_new_public_node_quote_only() -> None:
    decision = quote_review_lane_admission(_request())

    assert decision.admitted is True
    assert decision.admission_action == "promote_new_public_node"
    assert decision.failure_reasons == ()
    assert decision.reviewer_count == 5
    assert decision.approval_count == 5
    assert decision.production_activated is False
    assert decision.graph_write_authorized is False
    assert decision.public_economics_authorized is False
    assert decision.reviewer_payment_authorized is False


def test_wrong_source_taxonomy_is_denied() -> None:
    decision = quote_review_lane_admission(
        _request(current_taxonomy_class=TaxonomyClass.T0_PRIVATE_LOCAL_DRAFT)
    )

    assert decision.admitted is False
    assert decision.admission_action == "deny"
    assert "review_lane_wrong_source_taxonomy" in decision.failure_reasons


def test_invalid_target_taxonomy_is_denied() -> None:
    decision = quote_review_lane_admission(
        _request(target_taxonomy_class=TaxonomyClass.T0_5_PENDING_PUBLIC_INGESTION)
    )

    assert decision.admitted is False
    assert "review_lane_invalid_target_taxonomy" in decision.failure_reasons


def test_insufficient_reviewer_count_and_quorum_are_denied() -> None:
    decision = quote_review_lane_admission(_request(reviewer_attestations=_approvals(4)))

    assert decision.admitted is False
    assert "review_lane_insufficient_reviewer_count" in decision.failure_reasons
    assert "review_lane_approval_quorum_not_met" in decision.failure_reasons


def test_reject_votes_do_not_satisfy_approval_quorum() -> None:
    attestations = _approvals(4)
    attestations.append(ReviewerAttestation(reviewer_agent_id="reviewer-reject", verdict="reject"))

    decision = quote_review_lane_admission(_request(reviewer_attestations=attestations))

    assert decision.reviewer_count == 5
    assert decision.approval_count == 4
    assert decision.admitted is False
    assert "review_lane_approval_quorum_not_met" in decision.failure_reasons


def test_high_value_target_requires_outsider_approval() -> None:
    without_outsider = quote_review_lane_admission(
        _request(target_taxonomy_class=TaxonomyClass.T3_CONTESTED_HIGH_VALUE_OBJECTIVE_NODE)
    )
    with_outsider = quote_review_lane_admission(
        _request(
            target_taxonomy_class=TaxonomyClass.T3_CONTESTED_HIGH_VALUE_OBJECTIVE_NODE,
            reviewer_attestations=_approvals(5, outsider=True),
        )
    )

    assert "review_lane_outsider_approval_missing" in without_outsider.failure_reasons
    assert with_outsider.admitted is True
    assert with_outsider.outsider_approval_count == 1


def test_duplicate_reviewer_attestation_denied() -> None:
    attestations = _approvals(5)
    attestations.append(ReviewerAttestation(reviewer_agent_id="reviewer-0", verdict="approve"))

    decision = quote_review_lane_admission(_request(reviewer_attestations=attestations))

    assert decision.admitted is False
    assert "review_lane_duplicate_reviewer_attestation" in decision.failure_reasons


def test_attestation_to_existing_node_is_successful_non_new_node_action() -> None:
    decision = quote_review_lane_admission(
        _request(
            dedup_result="attestation_to_existing",
            existing_node_id="node-existing",
        )
    )

    assert decision.admitted is True
    assert decision.admission_action == "attest_to_existing_node"
    assert decision.existing_node_id == "node-existing"


def test_attestation_to_existing_requires_existing_node_id() -> None:
    decision = quote_review_lane_admission(_request(dedup_result="attestation_to_existing"))

    assert decision.admitted is False
    assert "review_lane_existing_node_required_for_attestation" in decision.failure_reasons


def test_public_economics_firewall_failure_denies_admission() -> None:
    decision = quote_review_lane_admission(_request(public_economics_firewall_passed=False))

    assert decision.admitted is False
    assert "review_lane_public_economics_firewall_required" in decision.failure_reasons


def test_canonical_decision_json_is_deterministic_and_sorted() -> None:
    decision = quote_review_lane_admission(_request())
    rendered = review_lane_decision_canonical_json(decision)

    assert rendered == review_lane_decision_canonical_json(decision)
    parsed = json.loads(rendered)
    assert list(parsed) == sorted(parsed)
    assert parsed["runtime_version"] == "review_lane_admission_runtime_phase_1415.v0.1"


def test_production_activation_requirement_fails_closed() -> None:
    with pytest.raises(ValueError, match="review_lane_production_not_activated"):
        require_production_review_lane_activation()


def test_runtime_source_has_no_random_assert_float_or_wall_clock() -> None:
    source = RUNTIME_PATH.read_text(encoding="utf-8")
    tree = ast.parse(source)

    assert "import random" not in source
    assert "float(" not in source
    assert "datetime.now" not in source
    assert "time.time" not in source
    assert not [node for node in ast.walk(tree) if isinstance(node, ast.Assert)]
    assert "sort_keys=True" in source
    assert "allow_nan=False" in source
