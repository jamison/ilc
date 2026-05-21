"""Post-1428 deterministic audit hardening regressions."""

from __future__ import annotations

from collections.abc import Iterator, Sequence

import pytest

from ilc_core.epistemic import review_lane_admission_runtime as review_runtime
from ilc_core.epistemic.jury_assignment_runtime import (
    EligibleAgent,
    JuryAssignmentError,
    quote_jury_assignment,
)
from ilc_core.epistemic.review_lane_admission_runtime import (
    ReviewLaneAdmissionRequest,
    ReviewerAttestation,
    TaxonomyClass,
    quote_review_lane_admission,
    quote_review_lane_admission_with_stubs,
    review_lane_decision_canonical_json,
)


def _approvals(count: int = 5) -> tuple[ReviewerAttestation, ...]:
    return tuple(
        ReviewerAttestation(reviewer_agent_id=f"reviewer-{index}", verdict="approve")
        for index in range(count)
    )


def _request(**overrides: object) -> ReviewLaneAdmissionRequest:
    values: dict[str, object] = {
        "submission_id": "submission-audit-hardening",
        "submission_content_hash": "sha256:" + "a" * 64,
        "current_taxonomy_class": TaxonomyClass.T0_5_PENDING_PUBLIC_INGESTION,
        "target_taxonomy_class": TaxonomyClass.T1_PUBLIC_NON_REWARD_METADATA,
        "submitter_agent_id": "agent-submit",
        "review_epoch": 1,
        "review_lane": "metadata",
        "reviewer_attestations": _approvals(),
    }
    values.update(overrides)
    return ReviewLaneAdmissionRequest(**values)


def test_review_lane_decision_canonical_json_binds_content_hash() -> None:
    first = quote_review_lane_admission(_request(submission_content_hash="sha256:" + "a" * 64))
    second = quote_review_lane_admission(_request(submission_content_hash="sha256:" + "b" * 64))

    assert first.submission_content_hash != second.submission_content_hash
    assert review_lane_decision_canonical_json(first) != review_lane_decision_canonical_json(second)


@pytest.mark.parametrize(
    "bad_hash",
    (
        "sha256:not-a-full-digest",
        "sha256:" + "A" * 64,
        "blake3:" + "a" * 64,
    ),
)
def test_review_lane_rejects_noncanonical_content_hashes(bad_hash: str) -> None:
    with pytest.raises(ValueError, match="review_lane_invalid_submission_content_hash"):
        quote_review_lane_admission(_request(submission_content_hash=bad_hash))
    with pytest.raises(ValueError, match="review_lane_invalid_submission_content_hash"):
        review_runtime.resolve_review_lane_dedup(
            canonical_external_id=None,
            submission_content_hash=bad_hash,
        )


def test_review_lane_stubs_validate_request_type_before_dedup_access() -> None:
    with pytest.raises(ValueError, match="review_lane_invalid_request_type"):
        quote_review_lane_admission_with_stubs(None)  # type: ignore[arg-type]


class OversizedBombSequence(Sequence[ReviewerAttestation]):
    def __len__(self) -> int:
        return review_runtime.REVIEW_LANE_PANEL_SIZE + 1

    def __getitem__(self, index: int) -> ReviewerAttestation:
        raise AssertionError("oversized reviewer sequence should not be iterated")

    def __iter__(self) -> Iterator[ReviewerAttestation]:
        raise AssertionError("oversized reviewer sequence should not be iterated")


def test_review_lane_oversized_attestations_fail_before_iteration() -> None:
    decision = quote_review_lane_admission(
        _request(reviewer_attestations=OversizedBombSequence())
    )

    assert decision.admitted is False
    assert "review_lane_too_many_reviewer_attestations" in decision.failure_reasons


def _agent(agent_id: str, cluster_id: str, operator_domain: str, *, outsider: bool = False) -> EligibleAgent:
    return EligibleAgent(
        agent_id=agent_id,
        cluster_id=cluster_id,
        operator_domain=operator_domain,
        identity_lineage_ref=f"lineage-{agent_id}",
        outsider_candidate_flag=outsider,
        capability_tier_or_lane_score="tier1",
    )


def test_jury_assignment_retries_valid_diverse_panel_after_greedy_cluster_failure() -> None:
    agents = [
        _agent("c1-agent-1533", "c1", "op-c1-1533"),
        _agent("c1-agent-708", "c1", "op-c1-708"),
        _agent("c2-agent-820", "c2", "op-c2-820"),
        _agent("c2-agent-710", "c2", "op-c2-710"),
        _agent("c3-agent-228", "c3", "op-c3-228"),
        _agent("c5-agent-947", "c5", "op-c5-947"),
        _agent("c5-agent-1480", "c5", "op-c5-1480"),
        _agent("c5-agent-1872", "c5", "op-c5-1872"),
        _agent("out-473", "c5", "op-out-473", outsider=True),
    ]

    quote = quote_jury_assignment(
        review_epoch=1,
        review_lane="objective",
        claim_or_task_id="cid-greedy-diversity-audit",
        author_agent_id="author",
        author_operator_domain="author-op",
        eligible_agents=agents,
    )

    assert quote.cluster_diversity_verified is True
    assert quote.cluster_diversity_distinct_clusters >= 4
    assert quote.cluster_diversity_largest_cluster_slots <= 3


def test_jury_assignment_malformed_vrf_record_fails_closed_not_raw_typeerror() -> None:
    agents = [
        _agent(f"r{index}", f"c{index}", f"op-{index}")
        for index in range(1, 8)
    ]
    agents.append(_agent("out", "c8", "op-out", outsider=True))

    with pytest.raises(JuryAssignmentError):
        quote_jury_assignment(
            review_epoch=1,
            review_lane="objective",
            claim_or_task_id="cid-vrf-record-shape",
            author_agent_id="author",
            author_operator_domain="author-op",
            eligible_agents=agents,
            is_high_value_slot=True,
            assignment_nonce="nonce",
            vrf_proofs={agent.agent_id: [] for agent in agents},  # type: ignore[dict-item]
            _audit_only=True,
        )
