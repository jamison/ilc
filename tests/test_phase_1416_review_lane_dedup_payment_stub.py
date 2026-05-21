"""Regression tests for Phase 1416 review lane dedup and payment stubs."""

from __future__ import annotations

from ilc_core.epistemic import (
    REVIEW_LANE_ADMISSION_IMPLEMENTED_TOKEN,
    REVIEW_LANE_DEDUP_IMPLEMENTED_TOKEN,
    REVIEW_LANE_DEDUP_READ_ONLY_TOKEN,
    REVIEW_LANE_DEDUP_STUB_TOKEN,
    REVIEW_LANE_PAYMENT_NOT_ACTIVATED_TOKEN,
    REVIEW_LANE_PAYMENT_STUB_WIRED_TOKEN,
    REVIEW_LANE_PAYMENT_STUB_TOKEN,
    REVIEW_LANE_REVIEWER_PAYMENT_NOT_ACTIVATED_TOKEN,
    ReviewLaneAdmissionRequest,
    ReviewerAttestation,
    TaxonomyClass,
    quote_review_lane_admission_with_stubs,
    resolve_review_lane_dedup,
)
from ilc_core.epistemic import review_lane_admission_runtime as runtime


def _approvals(count: int = 5) -> list[ReviewerAttestation]:
    return [
        ReviewerAttestation(reviewer_agent_id=f"reviewer-{index}", verdict="approve")
        for index in range(count)
    ]


def _request(**overrides: object) -> ReviewLaneAdmissionRequest:
    values: dict[str, object] = {
        "submission_id": "submission-1416",
        "submission_content_hash": "sha256:" + "b" * 64,
        "current_taxonomy_class": TaxonomyClass.T0_5_PENDING_PUBLIC_INGESTION,
        "target_taxonomy_class": TaxonomyClass.T1_PUBLIC_NON_REWARD_METADATA,
        "submitter_agent_id": "agent-submit",
        "review_epoch": 8,
        "review_lane": "metadata",
        "reviewer_attestations": _approvals(),
        "canonical_external_id": "doi:10.1234/phase1416",
    }
    values.update(overrides)
    return ReviewLaneAdmissionRequest(**values)


def test_phase_1416_tokens_are_exported() -> None:
    assert REVIEW_LANE_ADMISSION_IMPLEMENTED_TOKEN == (
        "review_lane_admission_runtime_implemented_phase_1415"
    )
    assert REVIEW_LANE_DEDUP_STUB_TOKEN == "review_lane_dedup_enforcement_stub_phase_1416"
    assert REVIEW_LANE_DEDUP_IMPLEMENTED_TOKEN == (
        "review_lane_dedup_enforcement_implemented_phase_1416"
    )
    assert REVIEW_LANE_DEDUP_READ_ONLY_TOKEN == "review_lane_dedup_read_only_phase_1416"
    assert REVIEW_LANE_PAYMENT_STUB_TOKEN == "review_lane_payment_settlement_stub_phase_1416"
    assert REVIEW_LANE_PAYMENT_STUB_WIRED_TOKEN == "review_lane_payment_stub_wired_phase_1416"
    assert REVIEW_LANE_PAYMENT_NOT_ACTIVATED_TOKEN == "review_lane_payment_not_activated_phase_1416"
    assert REVIEW_LANE_REVIEWER_PAYMENT_NOT_ACTIVATED_TOKEN == (
        "review_lane_reviewer_payment_not_activated_phase_1416"
    )
    assert REVIEW_LANE_DEDUP_STUB_TOKEN in runtime.PHASE_1416_TOKENS
    assert REVIEW_LANE_DEDUP_IMPLEMENTED_TOKEN in runtime.PHASE_1416_TOKENS
    assert REVIEW_LANE_PAYMENT_STUB_TOKEN in runtime.PHASE_1416_TOKENS


def test_external_id_duplicate_takes_precedence_over_content_hash() -> None:
    evidence = resolve_review_lane_dedup(
        canonical_external_id="doi:10.1234/phase1416",
        submission_content_hash="sha256:" + "b" * 64,
        known_external_ids={"doi:10.1234/phase1416": "node-external"},
        known_content_hashes={"sha256:" + "b" * 64: "node-content"},
    )

    assert evidence.dedup_result == "attestation_to_existing"
    assert evidence.dedup_key_kind == "canonical_external_id"
    assert evidence.dedup_key == "doi:10.1234/phase1416"
    assert evidence.existing_node_id == "node-external"
    assert evidence.graph_write_authorized is False
    assert evidence.registry_write_authorized is False


def test_content_hash_fallback_used_only_without_external_id() -> None:
    evidence = resolve_review_lane_dedup(
        canonical_external_id=None,
        submission_content_hash="sha256:" + "c" * 64,
        known_external_ids={"doi:10.1234/other": "node-external"},
        known_content_hashes={"sha256:" + "c" * 64: "node-content"},
    )

    assert evidence.dedup_result == "attestation_to_existing"
    assert evidence.dedup_key_kind == "submission_content_hash"
    assert evidence.dedup_key == "sha256:" + "c" * 64
    assert evidence.existing_node_id == "node-content"


def test_no_duplicate_promotes_new_node_and_quotes_default_off_payment_stubs() -> None:
    quote = quote_review_lane_admission_with_stubs(
        _request(),
        known_external_ids={},
        known_content_hashes={},
    )

    assert quote.admission_decision.admitted is True
    assert quote.admission_decision.admission_action == "promote_new_public_node"
    assert quote.dedup_evidence.dedup_result == "no_duplicate_found"
    assert quote.payment_stub_count == 5
    assert quote.payment_settlement_authorized is False
    assert quote.ledger_write_authorized is False
    assert quote.treasury_write_authorized is False
    assert quote.wallet_write_authorized is False
    assert quote.ecu_distribution_authorized is False
    for stub in quote.reviewer_payment_stubs:
        assert stub["status"] == "not_activated"
        assert stub["payment_enqueued"] is False
        assert stub["settlement_authorized"] is False
        assert stub["wallet_write_authorized"] is False
        assert "reviewer_payment_not_activated_phase_1401" in stub["phase_tokens"]
        assert "review_lane_payment_settlement_stub_phase_1416" in stub["phase_tokens"]


def test_duplicate_external_id_admits_attestation_action_with_payment_stubs() -> None:
    quote = quote_review_lane_admission_with_stubs(
        _request(),
        known_external_ids={"doi:10.1234/phase1416": "node-existing"},
    )

    assert quote.admission_decision.admitted is True
    assert quote.admission_decision.admission_action == "attest_to_existing_node"
    assert quote.admission_decision.existing_node_id == "node-existing"
    assert quote.payment_stub_count == 5


def test_denied_admission_returns_no_payment_stubs() -> None:
    quote = quote_review_lane_admission_with_stubs(
        _request(reviewer_attestations=_approvals(4)),
        known_external_ids={},
    )

    assert quote.admission_decision.admitted is False
    assert quote.payment_stub_count == 0
    assert quote.reviewer_payment_stubs == ()


def test_dedup_lookup_mapping_size_is_bounded() -> None:
    too_large = {f"doi:10.1234/{index}": f"node-{index}" for index in range(10_001)}

    try:
        resolve_review_lane_dedup(
            canonical_external_id="doi:10.1234/phase1416",
            submission_content_hash="sha256:" + "b" * 64,
            known_external_ids=too_large,
        )
    except ValueError as exc:
        assert str(exc) == "review_lane_external_id_lookup_too_large"
    else:
        raise AssertionError("expected bounded dedup lookup failure")


def test_invalid_lookup_mapping_values_fail_closed() -> None:
    try:
        resolve_review_lane_dedup(
            canonical_external_id="doi:10.1234/phase1416",
            submission_content_hash="sha256:" + "b" * 64,
            known_external_ids={"": "node"},
        )
    except ValueError as exc:
        assert str(exc) == "review_lane_invalid_external_id_lookup_key"
    else:
        raise AssertionError("expected invalid lookup key failure")
