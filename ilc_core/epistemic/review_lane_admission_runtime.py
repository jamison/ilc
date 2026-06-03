# SPDX-License-Identifier: AGPL-3.0-only
"""Phase 1415 / review lane admission runtime.

Pure, default-off evaluator for ADR-0043 T0.5 -> T1+ admission decisions.
This module produces quote/evidence records only. It does not write graph,
ledger, treasury, wallet, registry, or CDL state.

Required phase tokens:
  review_lane_admission_runtime_committed_phase_1415
  review_lane_admission_runtime_phase_1415.v0.1
  review_lane_production_not_activated_phase_1415
  review_lane_wiring_not_complete_phase_1415
  review_lane_wiring_adr_accepted_phase_1414
"""

from __future__ import annotations

import json
from dataclasses import dataclass, replace
from typing import Mapping, Sequence

from .ingestion_shadow_harness import TaxonomyClass
from .jury_incentive_runtime import queue_reviewer_payment_stub

REVIEW_LANE_ADMISSION_VERSION = "review_lane_admission_runtime_phase_1415.v0.1"
REVIEW_LANE_ADMISSION_RUNTIME_TOKEN = "review_lane_admission_runtime_committed_phase_1415"
REVIEW_LANE_ADMISSION_IMPLEMENTED_TOKEN = "review_lane_admission_runtime_implemented_phase_1415"
ADR_0043_DEPENDENCY = "review_lane_wiring_adr_accepted_phase_1414"
ADR_0043_CONTRACT_TOKEN = "t0_5_to_t1_plus_admission_contract_defined_phase_1414"

REVIEW_LANE_PRODUCTION_NOT_ACTIVATED: bool = True
REVIEW_LANE_PRODUCTION_NOT_ACTIVATED_TOKEN = "review_lane_production_not_activated_phase_1415"
REVIEW_LANE_WIRING_NOT_COMPLETE_TOKEN = "review_lane_wiring_not_complete_phase_1415"
REVIEW_LANE_DEDUP_STUB_TOKEN = "review_lane_dedup_enforcement_stub_phase_1416"
REVIEW_LANE_DEDUP_IMPLEMENTED_TOKEN = "review_lane_dedup_enforcement_implemented_phase_1416"
REVIEW_LANE_DEDUP_READ_ONLY_TOKEN = "review_lane_dedup_read_only_phase_1416"
REVIEW_LANE_PAYMENT_STUB_TOKEN = "review_lane_payment_settlement_stub_phase_1416"
REVIEW_LANE_PAYMENT_STUB_WIRED_TOKEN = "review_lane_payment_stub_wired_phase_1416"
REVIEW_LANE_PAYMENT_NOT_ACTIVATED_TOKEN = "review_lane_payment_not_activated_phase_1416"
REVIEW_LANE_REVIEWER_PAYMENT_NOT_ACTIVATED_TOKEN = (
    "review_lane_reviewer_payment_not_activated_phase_1416"
)
REVIEW_LANE_WIRING_NOT_COMPLETE_PHASE_1416_TOKEN = "review_lane_wiring_not_complete_phase_1416"

REVIEW_LANE_PANEL_SIZE = 8
REVIEW_LANE_MIN_ASSIGNED_REVIEWERS = 5
REVIEW_LANE_APPROVAL_QUORUM = 5
REVIEW_LANE_OUTSIDER_REVIEWERS_REQUIRED_FOR_HIGH_VALUE = 1
MAX_DEDUP_LOOKUP_RECORDS = 10_000
_SHA256_PREFIX = "sha256:"
_HEX = frozenset("0123456789abcdef")

DEDUP_NO_DUPLICATE_FOUND = "no_duplicate_found"
DEDUP_ATTESTATION_TO_EXISTING = "attestation_to_existing"

ACTION_PROMOTE_NEW_PUBLIC_NODE = "promote_new_public_node"
ACTION_ATTEST_TO_EXISTING_NODE = "attest_to_existing_node"
ACTION_DENY = "deny"

VERDICT_APPROVE = "approve"
VERDICT_REJECT = "reject"
VERDICT_ABSTAIN = "abstain"

TARGET_T1_PLUS: frozenset[str] = frozenset(
    {
        TaxonomyClass.T1_PUBLIC_NON_REWARD_METADATA.value,
        TaxonomyClass.T2_REWARD_BEARING_OBJECTIVE_NODE.value,
        TaxonomyClass.T3_CONTESTED_HIGH_VALUE_OBJECTIVE_NODE.value,
        TaxonomyClass.T4_SUBJECTIVE_AESTHETIC_NODE.value,
        TaxonomyClass.T5_REFUTATION_PROVENANCE_STAKE_AFFECTING_CLAIM.value,
        TaxonomyClass.T6_VALIDATOR_CONSENSUS_CLAIM.value,
    }
)

HIGH_VALUE_TARGETS: frozenset[str] = frozenset(
    {
        TaxonomyClass.T3_CONTESTED_HIGH_VALUE_OBJECTIVE_NODE.value,
        TaxonomyClass.T5_REFUTATION_PROVENANCE_STAKE_AFFECTING_CLAIM.value,
        TaxonomyClass.T6_VALIDATOR_CONSENSUS_CLAIM.value,
    }
)

PHASE_TOKENS: tuple[str, ...] = (
    REVIEW_LANE_ADMISSION_RUNTIME_TOKEN,
    REVIEW_LANE_ADMISSION_IMPLEMENTED_TOKEN,
    REVIEW_LANE_ADMISSION_VERSION,
    ADR_0043_DEPENDENCY,
    ADR_0043_CONTRACT_TOKEN,
    REVIEW_LANE_PRODUCTION_NOT_ACTIVATED_TOKEN,
    REVIEW_LANE_WIRING_NOT_COMPLETE_TOKEN,
)

PHASE_1416_TOKENS: tuple[str, ...] = (
    REVIEW_LANE_DEDUP_STUB_TOKEN,
    REVIEW_LANE_DEDUP_IMPLEMENTED_TOKEN,
    REVIEW_LANE_DEDUP_READ_ONLY_TOKEN,
    REVIEW_LANE_PAYMENT_STUB_TOKEN,
    REVIEW_LANE_PAYMENT_STUB_WIRED_TOKEN,
    REVIEW_LANE_PAYMENT_NOT_ACTIVATED_TOKEN,
    REVIEW_LANE_REVIEWER_PAYMENT_NOT_ACTIVATED_TOKEN,
    REVIEW_LANE_WIRING_NOT_COMPLETE_PHASE_1416_TOKEN,
)


@dataclass(frozen=True)
class ReviewerAttestation:
    reviewer_agent_id: str
    verdict: str
    outsider_reviewer: bool = False


@dataclass(frozen=True)
class ReviewLaneAdmissionRequest:
    submission_id: str
    submission_content_hash: str
    current_taxonomy_class: str | TaxonomyClass
    target_taxonomy_class: str | TaxonomyClass
    submitter_agent_id: str
    review_epoch: int
    review_lane: str
    reviewer_attestations: Sequence[ReviewerAttestation]
    canonical_external_id: str | None = None
    dedup_result: str = DEDUP_NO_DUPLICATE_FOUND
    existing_node_id: str | None = None
    public_economics_firewall_passed: bool = True


@dataclass(frozen=True)
class ReviewLaneAdmissionDecision:
    admitted: bool
    admission_action: str
    failure_reasons: tuple[str, ...]
    runtime_version: str
    current_taxonomy_class: str
    target_taxonomy_class: str
    submission_id: str
    submission_content_hash: str
    review_epoch: int
    review_lane: str
    reviewer_count: int
    approval_count: int
    outsider_approval_count: int
    dedup_result: str
    canonical_external_id: str | None
    existing_node_id: str | None
    production_activated: bool
    graph_write_authorized: bool
    public_economics_authorized: bool
    reviewer_payment_authorized: bool
    phase_tokens: tuple[str, ...]


@dataclass(frozen=True)
class ReviewLaneDedupEvidence:
    dedup_result: str
    dedup_key_kind: str
    dedup_key: str
    existing_node_id: str | None
    graph_write_authorized: bool
    registry_write_authorized: bool
    phase_tokens: tuple[str, ...]


@dataclass(frozen=True)
class ReviewLaneSettlementStubQuote:
    admission_decision: ReviewLaneAdmissionDecision
    dedup_evidence: ReviewLaneDedupEvidence
    reviewer_payment_stubs: tuple[Mapping[str, object], ...]
    payment_stub_count: int
    payment_settlement_authorized: bool
    ledger_write_authorized: bool
    treasury_write_authorized: bool
    wallet_write_authorized: bool
    ecu_distribution_authorized: bool
    phase_tokens: tuple[str, ...]


def _taxonomy_value(value: str | TaxonomyClass, token: str) -> str:
    if isinstance(value, TaxonomyClass):
        return value.value
    if isinstance(value, str) and value:
        return value
    raise ValueError(token)


def _require_non_empty_string(value: str | None, token: str) -> None:
    if not isinstance(value, str) or not value:
        raise ValueError(token)


def _require_sha256_content_hash(value: str | None, token: str) -> str:
    _require_non_empty_string(value, token)
    if not isinstance(value, str):
        raise ValueError(token)
    digest = value[len(_SHA256_PREFIX) :] if value.startswith(_SHA256_PREFIX) else ""
    if (
        not value.startswith(_SHA256_PREFIX)
        or len(digest) != 64
        or any(char not in _HEX for char in digest)
    ):
        raise ValueError(token)
    return value


def _require_protocol_epoch(value: int) -> None:
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise ValueError("review_lane_invalid_review_epoch")


def _validate_request_shape(request: ReviewLaneAdmissionRequest) -> tuple[str, str]:
    if not isinstance(request, ReviewLaneAdmissionRequest):
        raise ValueError("review_lane_invalid_request_type")
    _require_non_empty_string(request.submission_id, "review_lane_invalid_submission_id")
    _require_non_empty_string(
        request.submission_content_hash,
        "review_lane_invalid_submission_content_hash",
    )
    _require_sha256_content_hash(
        request.submission_content_hash,
        "review_lane_invalid_submission_content_hash",
    )
    _require_non_empty_string(request.submitter_agent_id, "review_lane_invalid_submitter_agent_id")
    _require_non_empty_string(request.review_lane, "review_lane_invalid_review_lane")
    _require_protocol_epoch(request.review_epoch)
    if request.canonical_external_id is not None:
        _require_non_empty_string(
            request.canonical_external_id,
            "review_lane_invalid_canonical_external_id",
        )
    if request.existing_node_id is not None:
        _require_non_empty_string(request.existing_node_id, "review_lane_invalid_existing_node_id")
    if not isinstance(request.public_economics_firewall_passed, bool):
        raise ValueError("review_lane_invalid_public_economics_firewall_flag")
    return (
        _taxonomy_value(request.current_taxonomy_class, "review_lane_invalid_source_taxonomy_type"),
        _taxonomy_value(request.target_taxonomy_class, "review_lane_invalid_target_taxonomy_type"),
    )


def _reviewer_counts(attestations: Sequence[ReviewerAttestation]) -> tuple[int, int, int, bool, bool]:
    if not isinstance(attestations, Sequence) or isinstance(attestations, (str, bytes)):
        raise ValueError("review_lane_invalid_reviewer_attestations")
    if len(attestations) > REVIEW_LANE_PANEL_SIZE:
        return (len(attestations), 0, 0, False, True)
    reviewer_ids: set[str] = set()
    duplicate_found = False
    approval_ids: set[str] = set()
    outsider_approval_ids: set[str] = set()

    for attestation in attestations:
        if not isinstance(attestation, ReviewerAttestation):
            raise ValueError("review_lane_invalid_reviewer_attestation")
        _require_non_empty_string(
            attestation.reviewer_agent_id,
            "review_lane_invalid_reviewer_agent_id",
        )
        if attestation.verdict not in {VERDICT_APPROVE, VERDICT_REJECT, VERDICT_ABSTAIN}:
            raise ValueError("review_lane_invalid_reviewer_verdict")
        if not isinstance(attestation.outsider_reviewer, bool):
            raise ValueError("review_lane_invalid_outsider_reviewer_flag")
        if attestation.reviewer_agent_id in reviewer_ids:
            duplicate_found = True
        reviewer_ids.add(attestation.reviewer_agent_id)
        if attestation.verdict == VERDICT_APPROVE:
            approval_ids.add(attestation.reviewer_agent_id)
            if attestation.outsider_reviewer:
                outsider_approval_ids.add(attestation.reviewer_agent_id)

    return (
        len(reviewer_ids),
        len(approval_ids),
        len(outsider_approval_ids),
        duplicate_found,
        len(attestations) > REVIEW_LANE_PANEL_SIZE,
    )


def quote_review_lane_admission(
    request: ReviewLaneAdmissionRequest,
) -> ReviewLaneAdmissionDecision:
    """Return a default-off admission decision with no side effects."""

    current_taxonomy, target_taxonomy = _validate_request_shape(request)
    reviewer_count, approval_count, outsider_approval_count, duplicate_found, oversize = (
        _reviewer_counts(request.reviewer_attestations)
    )
    failure_reasons: list[str] = []

    if current_taxonomy != TaxonomyClass.T0_5_PENDING_PUBLIC_INGESTION.value:
        failure_reasons.append("review_lane_wrong_source_taxonomy")
    if target_taxonomy not in TARGET_T1_PLUS:
        failure_reasons.append("review_lane_invalid_target_taxonomy")
    if duplicate_found:
        failure_reasons.append("review_lane_duplicate_reviewer_attestation")
    if oversize:
        failure_reasons.append("review_lane_too_many_reviewer_attestations")
    if reviewer_count < REVIEW_LANE_MIN_ASSIGNED_REVIEWERS:
        failure_reasons.append("review_lane_insufficient_reviewer_count")
    if approval_count < REVIEW_LANE_APPROVAL_QUORUM:
        failure_reasons.append("review_lane_approval_quorum_not_met")
    if (
        target_taxonomy in HIGH_VALUE_TARGETS
        and outsider_approval_count < REVIEW_LANE_OUTSIDER_REVIEWERS_REQUIRED_FOR_HIGH_VALUE
    ):
        failure_reasons.append("review_lane_outsider_approval_missing")
    if request.dedup_result not in {DEDUP_NO_DUPLICATE_FOUND, DEDUP_ATTESTATION_TO_EXISTING}:
        failure_reasons.append("review_lane_duplicate_external_id_attestation_required")
    if (
        request.dedup_result == DEDUP_ATTESTATION_TO_EXISTING
        and request.existing_node_id is None
    ):
        failure_reasons.append("review_lane_existing_node_required_for_attestation")
    if not request.public_economics_firewall_passed:
        failure_reasons.append("review_lane_public_economics_firewall_required")

    admitted = not failure_reasons
    if not admitted:
        action = ACTION_DENY
    elif request.dedup_result == DEDUP_ATTESTATION_TO_EXISTING:
        action = ACTION_ATTEST_TO_EXISTING_NODE
    else:
        action = ACTION_PROMOTE_NEW_PUBLIC_NODE

    return ReviewLaneAdmissionDecision(
        admitted=admitted,
        admission_action=action,
        failure_reasons=tuple(failure_reasons),
        runtime_version=REVIEW_LANE_ADMISSION_VERSION,
        current_taxonomy_class=current_taxonomy,
        target_taxonomy_class=target_taxonomy,
        submission_id=request.submission_id,
        submission_content_hash=request.submission_content_hash,
        review_epoch=request.review_epoch,
        review_lane=request.review_lane,
        reviewer_count=reviewer_count,
        approval_count=approval_count,
        outsider_approval_count=outsider_approval_count,
        dedup_result=request.dedup_result,
        canonical_external_id=request.canonical_external_id,
        existing_node_id=request.existing_node_id,
        production_activated=False,
        graph_write_authorized=False,
        public_economics_authorized=False,
        reviewer_payment_authorized=False,
        phase_tokens=PHASE_TOKENS,
    )


def _validate_lookup(name: str, lookup: Mapping[str, str] | None) -> Mapping[str, str]:
    if lookup is None:
        return {}
    if not isinstance(lookup, Mapping):
        raise ValueError(f"review_lane_invalid_{name}_lookup")
    if len(lookup) > MAX_DEDUP_LOOKUP_RECORDS:
        raise ValueError(f"review_lane_{name}_lookup_too_large")
    for key, value in lookup.items():
        _require_non_empty_string(key, f"review_lane_invalid_{name}_lookup_key")
        _require_non_empty_string(value, f"review_lane_invalid_{name}_lookup_value")
    return lookup


def resolve_review_lane_dedup(
    *,
    canonical_external_id: str | None,
    submission_content_hash: str,
    known_external_ids: Mapping[str, str] | None = None,
    known_content_hashes: Mapping[str, str] | None = None,
) -> ReviewLaneDedupEvidence:
    """Resolve read-only dedup evidence without writing graph or registry state."""

    _require_sha256_content_hash(
        submission_content_hash,
        "review_lane_invalid_submission_content_hash",
    )
    if canonical_external_id is not None:
        _require_non_empty_string(
            canonical_external_id,
            "review_lane_invalid_canonical_external_id",
        )

    external_ids = _validate_lookup("external_id", known_external_ids)
    content_hashes = _validate_lookup("content_hash", known_content_hashes)

    if canonical_external_id is not None:
        existing_node_id = external_ids.get(canonical_external_id)
        return ReviewLaneDedupEvidence(
            dedup_result=(
                DEDUP_ATTESTATION_TO_EXISTING if existing_node_id else DEDUP_NO_DUPLICATE_FOUND
            ),
            dedup_key_kind="canonical_external_id",
            dedup_key=canonical_external_id,
            existing_node_id=existing_node_id,
            graph_write_authorized=False,
            registry_write_authorized=False,
            phase_tokens=PHASE_1416_TOKENS,
        )

    existing_node_id = content_hashes.get(submission_content_hash)
    return ReviewLaneDedupEvidence(
        dedup_result=DEDUP_ATTESTATION_TO_EXISTING if existing_node_id else DEDUP_NO_DUPLICATE_FOUND,
        dedup_key_kind="submission_content_hash",
        dedup_key=submission_content_hash,
        existing_node_id=existing_node_id,
        graph_write_authorized=False,
        registry_write_authorized=False,
        phase_tokens=PHASE_1416_TOKENS,
    )


def quote_review_lane_admission_with_stubs(
    request: ReviewLaneAdmissionRequest,
    *,
    known_external_ids: Mapping[str, str] | None = None,
    known_content_hashes: Mapping[str, str] | None = None,
) -> ReviewLaneSettlementStubQuote:
    """Quote admission plus default-off reviewer-payment stubs."""

    _validate_request_shape(request)
    dedup_evidence = resolve_review_lane_dedup(
        canonical_external_id=request.canonical_external_id,
        submission_content_hash=request.submission_content_hash,
        known_external_ids=known_external_ids,
        known_content_hashes=known_content_hashes,
    )
    request_with_dedup = replace(
        request,
        dedup_result=dedup_evidence.dedup_result,
        existing_node_id=dedup_evidence.existing_node_id,
    )
    decision = quote_review_lane_admission(request_with_dedup)

    payment_stubs: list[Mapping[str, object]] = []
    if decision.admitted:
        reviewer_ids = sorted(
            {
                attestation.reviewer_agent_id
                for attestation in request.reviewer_attestations
                if attestation.verdict == VERDICT_APPROVE
            }
        )
        for reviewer_id in reviewer_ids:
            stub = dict(
                queue_reviewer_payment_stub(
                    reviewer_id=reviewer_id,
                    task_id=request.submission_id,
                )
            )
            stub["wallet_write_authorized"] = False
            stub["settlement_authorized"] = False
            stub["phase_tokens"] = list(stub["phase_tokens"]) + list(PHASE_1416_TOKENS)
            payment_stubs.append(stub)

    return ReviewLaneSettlementStubQuote(
        admission_decision=decision,
        dedup_evidence=dedup_evidence,
        reviewer_payment_stubs=tuple(payment_stubs),
        payment_stub_count=len(payment_stubs),
        payment_settlement_authorized=False,
        ledger_write_authorized=False,
        treasury_write_authorized=False,
        wallet_write_authorized=False,
        ecu_distribution_authorized=False,
        phase_tokens=PHASE_TOKENS + PHASE_1416_TOKENS,
    )


def review_lane_decision_canonical_json(decision: ReviewLaneAdmissionDecision) -> str:
    """Return deterministic JSON for an admission decision."""
    if not isinstance(decision, ReviewLaneAdmissionDecision):
        raise ValueError("review_lane_invalid_decision_type")
    payload: Mapping[str, object] = {
        "admission_action": decision.admission_action,
        "admitted": decision.admitted,
        "approval_count": decision.approval_count,
        "canonical_external_id": decision.canonical_external_id,
        "current_taxonomy_class": decision.current_taxonomy_class,
        "dedup_result": decision.dedup_result,
        "existing_node_id": decision.existing_node_id,
        "failure_reasons": list(decision.failure_reasons),
        "graph_write_authorized": decision.graph_write_authorized,
        "outsider_approval_count": decision.outsider_approval_count,
        "phase_tokens": list(decision.phase_tokens),
        "production_activated": decision.production_activated,
        "public_economics_authorized": decision.public_economics_authorized,
        "review_epoch": decision.review_epoch,
        "review_lane": decision.review_lane,
        "reviewer_count": decision.reviewer_count,
        "reviewer_payment_authorized": decision.reviewer_payment_authorized,
        "runtime_version": decision.runtime_version,
        "submission_id": decision.submission_id,
        "submission_content_hash": decision.submission_content_hash,
        "target_taxonomy_class": decision.target_taxonomy_class,
    }
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False)


def require_production_review_lane_activation() -> None:
    """Fail closed until a later phase explicitly activates production review lane."""
    if REVIEW_LANE_PRODUCTION_NOT_ACTIVATED:
        raise ValueError("review_lane_production_not_activated")
