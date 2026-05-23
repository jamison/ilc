# SPDX-License-Identifier: AGPL-3.0-or-later
"""Phase 1396 / J-006 — Default-off jury assignment quote runtime.

Implements a deterministic, auditable panel-quoting function using epoch-hash
selection (ADR-0040 §Assignment Source).  This is a *quote-only* primitive:

  - no ledger writes
  - no graph writes
  - no production reward activation
  - no VRF proof generation
  - epoch-hash shadow assignment remains available
    (epoch_hash_shadow_assignment_only_phase_j006)

For production high-value assignment:
  vrf_required_for_production_high_value_assignment (ADR-0040 §Assignment Source)

Required phase tokens:
  default_off_jury_assignment_quote_runtime_phase_j006
  jury_assignment_no_public_activation_phase_j006
  epoch_hash_shadow_assignment_only_phase_j006
  vrf_verifier_integrated_jury_assignment_phase_1412
  anti_capture_diversity_verified_phase_1419
  production_assignment_activated_phase_1429
  window_1429_1458_first_phase
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from dataclasses import dataclass, field
from typing import Any, List, Mapping, Optional

from ilc_core.consensus.diversity_floor_runtime import (
    compute_max_cluster_share,
)
from ilc_core.epistemic.vrf_proof_verifier import VRFVerificationError, vrf_beta_from_proof

JURY_ASSIGNMENT_RUNTIME_VERSION = "jury_assignment_runtime_phase_j006.v0.1"
ADR_0040_DEPENDENCY = "jury_eligibility_assignment_adr_accepted_phase_j002"

# Phase tokens — must appear in module source for test_spec_contains_token parity
_TOKEN_DEFAULT_OFF = "default_off_jury_assignment_quote_runtime_phase_j006"
_TOKEN_NO_ACTIVATION = "jury_assignment_no_public_activation_phase_j006"
_TOKEN_SHADOW_ONLY = "epoch_hash_shadow_assignment_only_phase_j006"
_TOKEN_VRF_INTEGRATED = "vrf_verifier_integrated_jury_assignment_phase_1412"
_TOKEN_ANTI_CAPTURE_VERIFIED = "anti_capture_diversity_verified_phase_1419"
_TOKEN_CDL_V3_CLUSTER_WIRED = "cdl_v3_cluster_diversity_wired_jury_assignment_phase_1419"
_TOKEN_VRF_OUTSIDER_VERIFIED = "vrf_outsider_selection_verified_phase_1419"
_TOKEN_OPERATOR_INDEPENDENCE_VERIFIED = (
    "same_operator_domain_independence_verified_phase_1419"
)
_TOKEN_ANTI_CAPTURE_PRODUCTION_NOT_ACTIVATED = (
    "anti_capture_production_not_activated_phase_1419"
)
_TOKEN_PRODUCTION_ASSIGNMENT_ACTIVATED = "production_assignment_activated_phase_1429"
_TOKEN_WINDOW_1429_FIRST_PHASE = "window_1429_1458_first_phase"

_DOMAIN_SEPARATOR = "ilc_jury_assignment_v1"
_VRF_DOMAIN_SEPARATOR = "ilc.vrf.jury_assignment.v1"

# Panel shape (ADM-003 via ADR-0040)
_PANEL_REGULAR: int = 7
_PANEL_OUTSIDER: int = 1
_PANEL_SIZE: int = _PANEL_REGULAR + _PANEL_OUTSIDER
_REVIEWER_QUORUM_K: int = 5  # k=5 of m=7 regular reviewers
_INDEPENDENCE_K: int = 3     # at least 3 reviewers must be from distinct operator domains

# Max agents from any single operator_domain in the regular panel.
# independence_k=3 means at most (_PANEL_REGULAR - _INDEPENDENCE_K) = 4 per domain,
# guaranteeing at least 3 come from different domains.
_MAX_PER_OPERATOR_DOMAIN: int = _PANEL_REGULAR - _INDEPENDENCE_K
JURY_CLUSTER_DIVERSITY_FLOOR: int = 4
JURY_MAX_CLUSTER_SHARE_CEILING: float = 0.40
JURY_MAX_CLUSTER_SHARE_CEILING_NUMERATOR: int = 2
JURY_MAX_CLUSTER_SHARE_CEILING_DENOMINATOR: int = 5

# Safety gate: Phase 1429 flips this after J-008 PASS and explicit GO Phase 1429.
PRODUCTION_ASSIGNMENT_NOT_ACTIVATED: bool = False


@dataclass(frozen=True)
class EligibleAgent:
    """Descriptor for an agent in the eligible pool for a given review epoch and lane.

    Fields mirror the canonical ADR-0040 assignment input:
      domain_separator, review_epoch, review_lane, claim_or_task_id are
      supplied at call time; these per-agent fields complete the hash input.
    """

    agent_id: str
    cluster_id: str
    operator_domain: str        # used for same_operator_domain_not_independent check
    identity_lineage_ref: str
    outsider_candidate_flag: bool
    capability_tier_or_lane_score: str  # canonical string — NOT a numeric reward value


@dataclass(frozen=True)
class JuryAssignmentQuote:
    """Deterministic panel quote.  No economic or protocol effect."""

    review_epoch: int
    review_lane: str
    claim_or_task_id: str
    regular_panel: List[str]    # agent_ids, len == _PANEL_REGULAR
    outsider_panel: List[str]   # agent_ids, len == _PANEL_OUTSIDER
    panel_size: int             # always _PANEL_SIZE
    reviewer_quorum_k: int      # always _REVIEWER_QUORUM_K
    independence_k: int         # always _INDEPENDENCE_K
    assignment_mode: str        # "epoch_hash_shadow" or "vrf_verified"
    runtime_version: str
    phase_tokens: List[str]
    production_activated: bool  # always False — never flip without J-008 gate
    cluster_diversity_distinct_clusters: int
    cluster_diversity_largest_cluster_slots: int
    cluster_diversity_total_panel_slots: int
    cluster_diversity_max_cluster_share: float
    cluster_diversity_floor: int
    cluster_diversity_max_cluster_share_ceiling: float
    cluster_diversity_verified: bool
    vrf_excluded_agents: List[str] = field(default_factory=list)
    vrf_exclusion_reasons: dict[str, str] = field(default_factory=dict)


class JuryAssignmentError(Exception):
    """Raised when panel construction fails due to insufficient eligible agents."""


@dataclass(frozen=True)
class ClusterDiversityEvidence:
    """Selected-panel CDL-V3 diversity evidence for Phase 1419."""

    distinct_clusters: int
    largest_cluster_slots: int
    total_panel_slots: int
    max_cluster_share: float
    cluster_diversity_floor: int
    max_cluster_share_ceiling: float
    verified: bool


def _agent_score(
    review_epoch: int,
    review_lane: str,
    claim_or_task_id: str,
    agent: EligibleAgent,
) -> bytes:
    """Deterministic per-agent hash score over ADR-0040 canonical input fields.

    Uses json.dumps with sort_keys=True (ILC CODING-SECURITY-STANDARD §1).
    No float values; capability_tier_or_lane_score is a canonical string.
    """
    payload = json.dumps(
        {
            "domain_separator": _DOMAIN_SEPARATOR,
            "review_epoch": review_epoch,
            "review_lane": review_lane,
            "claim_or_task_id": claim_or_task_id,
            "eligible_agent_id": agent.agent_id,
            "cluster_id": agent.cluster_id,
            "identity_lineage_ref": agent.identity_lineage_ref,
            "outsider_candidate_flag": agent.outsider_candidate_flag,
            "capability_tier_or_lane_score": agent.capability_tier_or_lane_score,
        },
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(payload.encode("utf-8")).digest()


def _canonical_vrf_alpha(
    *,
    review_epoch: int,
    review_lane: str,
    claim_or_task_id: str,
    assignment_nonce: str,
    agent: EligibleAgent,
) -> bytes:
    """Canonical ADR-0042 alpha bytes for candidate-specific VRF verification."""
    payload = json.dumps(
        {
            "assignment_nonce": assignment_nonce,
            "capability_tier_or_lane_score": agent.capability_tier_or_lane_score,
            "claim_or_task_id": claim_or_task_id,
            "cluster_id": agent.cluster_id,
            "domain_separator": _VRF_DOMAIN_SEPARATOR,
            "eligible_agent_id": agent.agent_id,
            "identity_lineage_ref": agent.identity_lineage_ref,
            "outsider_candidate_flag": agent.outsider_candidate_flag,
            "review_epoch": review_epoch,
            "review_lane": review_lane,
        },
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )
    return payload.encode("utf-8")


def _decode_b64u_unpadded(value: str) -> bytes:
    import base64
    import binascii

    if not isinstance(value, str) or not value:
        raise JuryAssignmentError("vrf_b64u_value_must_be_non_empty_string")

    padding = "=" * (-len(value) % 4)
    try:
        return base64.b64decode(value + padding, altchars=b"-_", validate=True)
    except (binascii.Error, ValueError) as exc:
        raise JuryAssignmentError("vrf_b64u_decode_failed_for_candidate") from exc


def _proof_bytes_from_record(
    agent_id: str,
    vrf_proofs: Mapping[str, Mapping[str, Any]],
) -> tuple[bytes, bytes]:
    record = vrf_proofs.get(agent_id)
    if record is None:
        raise JuryAssignmentError("vrf_proof_missing_for_candidate")
    if not isinstance(record, Mapping):
        raise JuryAssignmentError("vrf_proof_record_must_be_mapping_for_candidate")

    if "public_key" in record:
        public_key = record["public_key"]
    elif "public_key_b64u" in record:
        public_key = _decode_b64u_unpadded(record["public_key_b64u"])
    else:
        raise JuryAssignmentError("vrf_public_key_missing_for_candidate")

    if "pi" in record:
        pi = record["pi"]
    elif "pi_b64u" in record:
        pi = _decode_b64u_unpadded(record["pi_b64u"])
    else:
        raise JuryAssignmentError("vrf_pi_missing_for_candidate")

    if type(public_key) is not bytes:
        raise JuryAssignmentError("vrf_public_key_must_be_bytes_for_candidate")
    if type(pi) is not bytes:
        raise JuryAssignmentError("vrf_pi_must_be_bytes_for_candidate")
    return public_key, pi


def _agent_score_vrf(
    *,
    review_epoch: int,
    review_lane: str,
    claim_or_task_id: str,
    assignment_nonce: str,
    agent: EligibleAgent,
    vrf_proofs: Mapping[str, Mapping[str, Any]],
) -> bytes:
    public_key, pi = _proof_bytes_from_record(agent.agent_id, vrf_proofs)
    alpha = _canonical_vrf_alpha(
        review_epoch=review_epoch,
        review_lane=review_lane,
        claim_or_task_id=claim_or_task_id,
        assignment_nonce=assignment_nonce,
        agent=agent,
    )
    return vrf_beta_from_proof(pi=pi, public_key=public_key, alpha=alpha)


def _select_regular_panel(
    candidates: List[EligibleAgent],
    scores: dict,
    target_size: int,
    max_per_operator_domain: int,
) -> List[str]:
    """Greedy independence-constrained selection from hash-sorted candidates.

    Enforces:
      - no more than max_per_operator_domain agents from any single operator_domain
        (implements independence_k guarantee via same_operator_domain_not_independent)
    """
    sorted_candidates = sorted(candidates, key=lambda a: (scores[a.agent_id], a.agent_id))
    domain_counts: dict = {}
    panel: List[str] = []
    for agent in sorted_candidates:
        if len(panel) >= target_size:
            break
        count = domain_counts.get(agent.operator_domain, 0)
        if count >= max_per_operator_domain:
            continue
        domain_counts[agent.operator_domain] = count + 1
        panel.append(agent.agent_id)
    return panel


def _select_outsider(
    candidates: List[EligibleAgent],
    scores: dict,
    regular_panel_agent_ids: List[str],
    author_operator_domain: str,
    regular_panel_operator_domains: set,
) -> List[str]:
    """Select one outsider seat from outsider candidates.

    Outsider must not share an operator_domain with the claim author or the
    regular panel majority (best-effort: prioritise candidates from domains not
    already represented in the regular panel).
    """
    regular_set = set(regular_panel_agent_ids)

    # Partition: prefer agents outside all regular-panel operator domains
    preferred = [
        a for a in candidates
        if a.agent_id not in regular_set
        and a.operator_domain != author_operator_domain
        and a.operator_domain not in regular_panel_operator_domains
    ]
    fallback = [
        a for a in candidates
        if a.agent_id not in regular_set
        and a.operator_domain != author_operator_domain
        and a.operator_domain in regular_panel_operator_domains
    ]

    pool = preferred if preferred else fallback
    if not pool:
        return []

    sorted_pool = sorted(pool, key=lambda a: (scores[a.agent_id], a.agent_id))
    return [sorted_pool[0].agent_id]


def _max_cluster_slots_allowed(total_panel_slots: int) -> int:
    return (
        total_panel_slots
        * JURY_MAX_CLUSTER_SHARE_CEILING_NUMERATOR
        // JURY_MAX_CLUSTER_SHARE_CEILING_DENOMINATOR
    )


def _cluster_share_within_ceiling(
    *,
    largest_cluster_slots: int,
    total_panel_slots: int,
) -> bool:
    return (
        largest_cluster_slots * JURY_MAX_CLUSTER_SHARE_CEILING_DENOMINATOR
        <= total_panel_slots * JURY_MAX_CLUSTER_SHARE_CEILING_NUMERATOR
    )


def _operator_domains_for_panel(
    panel_agent_ids: List[str],
    agents_by_id: Mapping[str, EligibleAgent],
) -> set[str]:
    return {agents_by_id[agent_id].operator_domain for agent_id in panel_agent_ids}


def _select_regular_panel_diversity_aware(
    candidates: List[EligibleAgent],
    scores: dict[str, bytes],
    target_size: int,
    max_per_operator_domain: int,
) -> List[str]:
    """Deterministically retry regular selection with cluster limits in the loop."""

    sorted_candidates = sorted(candidates, key=lambda a: (scores[a.agent_id], a.agent_id))
    selected: List[str] = []
    selected_set: set[str] = set()
    domain_counts: Counter[str] = Counter()
    cluster_counts: Counter[str] = Counter()
    max_cluster_slots = _max_cluster_slots_allowed(_PANEL_SIZE)

    def can_add(agent: EligibleAgent) -> bool:
        if agent.agent_id in selected_set:
            return False
        if domain_counts[agent.operator_domain] >= max_per_operator_domain:
            return False
        if cluster_counts[agent.cluster_id] >= max_cluster_slots:
            return False
        return True

    def add(agent: EligibleAgent) -> None:
        selected.append(agent.agent_id)
        selected_set.add(agent.agent_id)
        domain_counts[agent.operator_domain] += 1
        cluster_counts[agent.cluster_id] += 1

    seen_clusters: set[str] = set()
    for agent in sorted_candidates:
        if len(selected) >= target_size:
            break
        if len(seen_clusters) >= min(JURY_CLUSTER_DIVERSITY_FLOOR, len({a.cluster_id for a in candidates})):
            break
        if agent.cluster_id in seen_clusters:
            continue
        if can_add(agent):
            add(agent)
            seen_clusters.add(agent.cluster_id)

    for agent in sorted_candidates:
        if len(selected) >= target_size:
            break
        if can_add(agent):
            add(agent)

    return selected


def _select_outsider_for_cluster_diversity(
    candidates: List[EligibleAgent],
    scores: dict[str, bytes],
    regular_panel_agent_ids: List[str],
    author_operator_domain: str,
    regular_panel_operator_domains: set[str],
    agents_by_id: Mapping[str, EligibleAgent],
) -> List[str]:
    """Select an outsider that makes the complete 7+1 panel satisfy CDL-V3."""

    regular_set = set(regular_panel_agent_ids)
    sorted_candidates = sorted(
        (
            agent
            for agent in candidates
            if agent.agent_id not in regular_set
            and agent.operator_domain != author_operator_domain
        ),
        key=lambda a: (
            a.operator_domain in regular_panel_operator_domains,
            scores[a.agent_id],
            a.agent_id,
        ),
    )
    for agent in sorted_candidates:
        trial = regular_panel_agent_ids + [agent.agent_id]
        try:
            _cluster_diversity_evidence(
                selected_agent_ids=trial,
                agents_by_id=agents_by_id,
            )
        except JuryAssignmentError:
            continue
        return [agent.agent_id]
    return []


def _cluster_diversity_evidence(
    *,
    selected_agent_ids: List[str],
    agents_by_id: Mapping[str, EligibleAgent],
) -> ClusterDiversityEvidence:
    """Evaluate CDL-V3 selected-panel cluster diversity for Phase 1419."""
    if len(selected_agent_ids) != _PANEL_SIZE:
        raise JuryAssignmentError("jury_cluster_diversity_panel_size_mismatch")

    cluster_ids: List[str] = []
    for agent_id in selected_agent_ids:
        agent = agents_by_id.get(agent_id)
        if agent is None:
            raise JuryAssignmentError("jury_cluster_diversity_agent_lookup_missing")
        if not isinstance(agent.cluster_id, str) or not agent.cluster_id.strip():
            raise JuryAssignmentError("jury_cluster_diversity_cluster_id_invalid")
        cluster_ids.append(agent.cluster_id)

    counts = Counter(cluster_ids)
    distinct_clusters = len(counts)
    if distinct_clusters < JURY_CLUSTER_DIVERSITY_FLOOR:
        raise JuryAssignmentError(
            "jury_cluster_diversity_floor_not_met: "
            f"distinct_clusters={distinct_clusters}, "
            f"required={JURY_CLUSTER_DIVERSITY_FLOOR}"
        )

    largest_cluster_slots = max(counts.values())
    max_cluster_share = compute_max_cluster_share(
        largest_cluster_slots=largest_cluster_slots,
        total_panel_slots=len(selected_agent_ids),
    )
    if not _cluster_share_within_ceiling(
        largest_cluster_slots=largest_cluster_slots,
        total_panel_slots=len(selected_agent_ids),
    ):
        raise JuryAssignmentError(
            "jury_max_cluster_share_ceiling_exceeded: "
            f"max_cluster_share={max_cluster_share}, "
            f"ceiling={JURY_MAX_CLUSTER_SHARE_CEILING}"
        )

    return ClusterDiversityEvidence(
        distinct_clusters=distinct_clusters,
        largest_cluster_slots=largest_cluster_slots,
        total_panel_slots=len(selected_agent_ids),
        max_cluster_share=max_cluster_share,
        cluster_diversity_floor=JURY_CLUSTER_DIVERSITY_FLOOR,
        max_cluster_share_ceiling=JURY_MAX_CLUSTER_SHARE_CEILING,
        verified=True,
    )


def quote_jury_assignment(
    *,
    review_epoch: int,
    review_lane: str,
    claim_or_task_id: str,
    author_agent_id: str,
    author_operator_domain: str,
    eligible_agents: List[EligibleAgent],
    is_high_value_slot: bool = False,
    assignment_nonce: Optional[str] = None,
    vrf_proofs: Optional[Mapping[str, Mapping[str, Any]]] = None,
    _audit_only: bool = False,
) -> JuryAssignmentQuote:
    """Compute a deterministic panel quote for a given review request.

    Args:
        review_epoch:         Protocol review epoch number (integer, not wall-clock).
        review_lane:          Lane identifier string (e.g. "objective", "refutation").
        claim_or_task_id:     Content-addressed claim or task identifier.
        author_agent_id:      Agent ID of the claim/task author — excluded from panel.
        author_operator_domain: Operator domain of the author — excluded from panel.
        eligible_agents:      Pool of agents satisfying eligibility gates for this lane.
        is_high_value_slot:   True only for VRF-required high-value audit/production slots.
        assignment_nonce:     Caller-supplied ratified nonce for ADR-0042 alpha bytes.
        vrf_proofs:           Externally supplied proof material keyed by agent_id.
        _audit_only:          Test/audit bypass for non-activated high-value quotes.

    Returns:
        JuryAssignmentQuote with regular_panel (7) + outsider_panel (1).

    Raises:
        JuryAssignmentError: if the eligible pool cannot fill the required panel.
        ValueError: if required argument types are invalid.
    """
    if not isinstance(review_epoch, int) or review_epoch < 0:
        raise ValueError("review_epoch must be a non-negative integer")
    if not review_lane:
        raise ValueError("review_lane must be a non-empty string")
    if not claim_or_task_id:
        raise ValueError("claim_or_task_id must be a non-empty string")
    if is_high_value_slot:
        if PRODUCTION_ASSIGNMENT_NOT_ACTIVATED and not _audit_only:
            raise JuryAssignmentError(
                "production_assignment_not_activated: "
                "must not call high_value_slot=True in non-production"
            )
        if not isinstance(assignment_nonce, str) or not assignment_nonce:
            raise ValueError(
                "assignment_nonce must be a non-empty string for high-value VRF assignment"
            )
        if vrf_proofs is None:
            raise JuryAssignmentError("vrf_proofs_required_for_high_value_slot")

    seen_ids: set[str] = set()
    duplicate_ids: List[str] = []
    for agent in eligible_agents:
        if agent.agent_id in seen_ids:
            duplicate_ids.append(agent.agent_id)
        seen_ids.add(agent.agent_id)
    if duplicate_ids:
        raise JuryAssignmentError(
            "jury_eligible_agents_duplicate_agent_id: "
            f"duplicate agent_id(s) in eligible_agents: {sorted(set(duplicate_ids))}"
        )

    # Step 1 — filter: remove conflicted agents (author, same operator domain as author)
    non_conflicted = [
        a for a in eligible_agents
        if a.agent_id != author_agent_id
        and a.operator_domain != author_operator_domain
    ]

    # Step 2 — compute per-agent scores. In VRF mode, candidates with missing
    # or invalid proof material are excluded and surfaced in the quote.
    scores: dict[str, bytes] = {}
    scored_candidates: List[EligibleAgent] = []
    vrf_exclusion_reasons: dict[str, str] = {}
    for agent in non_conflicted:
        try:
            if is_high_value_slot:
                scores[agent.agent_id] = _agent_score_vrf(
                    review_epoch=review_epoch,
                    review_lane=review_lane,
                    claim_or_task_id=claim_or_task_id,
                    assignment_nonce=assignment_nonce or "",
                    agent=agent,
                    vrf_proofs=vrf_proofs or {},
                )
            else:
                scores[agent.agent_id] = _agent_score(
                    review_epoch, review_lane, claim_or_task_id, agent
                )
        except (JuryAssignmentError, VRFVerificationError) as exc:
            vrf_exclusion_reasons[agent.agent_id] = str(exc)
            continue
        scored_candidates.append(agent)

    # Step 3 — split: regular candidates vs. outsider candidates
    regular_candidates = [a for a in scored_candidates if not a.outsider_candidate_flag]
    outsider_candidates = [a for a in scored_candidates if a.outsider_candidate_flag]
    agents_by_id = {agent.agent_id: agent for agent in scored_candidates}

    # Step 4 — build regular panel
    regular_panel = _select_regular_panel(
        regular_candidates,
        scores,
        _PANEL_REGULAR,
        _MAX_PER_OPERATOR_DOMAIN,
    )

    if len(regular_panel) < _PANEL_REGULAR:
        raise JuryAssignmentError(
            f"insufficient_regular_candidates: need {_PANEL_REGULAR}, "
            f"selected {len(regular_panel)} from {len(regular_candidates)} non-conflicted candidates; "
            f"same_operator_domain_not_independent constraint may have reduced the pool"
        )

    # Step 5 — build outsider panel
    regular_panel_operator_domains = {
        a.operator_domain
        for a in eligible_agents
        if a.agent_id in set(regular_panel)
    }

    outsider_panel = _select_outsider(
        outsider_candidates,
        scores,
        regular_panel,
        author_operator_domain,
        regular_panel_operator_domains,
    )

    initial_panel_error: JuryAssignmentError | None = None
    cluster_evidence: ClusterDiversityEvidence | None = None

    if len(outsider_panel) < _PANEL_OUTSIDER:
        initial_panel_error = JuryAssignmentError(
            "insufficient_outsider_candidates: no eligible outsider candidate found; "
            "outsider seat is required (ADM-003 7+1 panel shape)"
        )
    else:
        try:
            cluster_evidence = _cluster_diversity_evidence(
                selected_agent_ids=regular_panel + outsider_panel,
                agents_by_id=agents_by_id,
            )
        except JuryAssignmentError as exc:
            initial_panel_error = exc

    if initial_panel_error is not None:
        retry_regular_panel = _select_regular_panel_diversity_aware(
            regular_candidates,
            scores,
            _PANEL_REGULAR,
            _MAX_PER_OPERATOR_DOMAIN,
        )
        if len(retry_regular_panel) == _PANEL_REGULAR:
            retry_domains = _operator_domains_for_panel(retry_regular_panel, agents_by_id)
            retry_outsider_panel = _select_outsider_for_cluster_diversity(
                outsider_candidates,
                scores,
                retry_regular_panel,
                author_operator_domain,
                retry_domains,
                agents_by_id,
            )
            if len(retry_outsider_panel) == _PANEL_OUTSIDER:
                try:
                    retry_evidence = _cluster_diversity_evidence(
                        selected_agent_ids=retry_regular_panel + retry_outsider_panel,
                        agents_by_id=agents_by_id,
                    )
                except JuryAssignmentError:
                    retry_evidence = None
                if retry_evidence is not None:
                    regular_panel = retry_regular_panel
                    outsider_panel = retry_outsider_panel
                    cluster_evidence = retry_evidence

    if cluster_evidence is None:
        if initial_panel_error is None:
            initial_panel_error = JuryAssignmentError("jury_cluster_diversity_selection_failed")
        raise initial_panel_error

    phase_tokens = [
        _TOKEN_DEFAULT_OFF,
        _TOKEN_NO_ACTIVATION,
        _TOKEN_SHADOW_ONLY,
        _TOKEN_CDL_V3_CLUSTER_WIRED,
        _TOKEN_OPERATOR_INDEPENDENCE_VERIFIED,
        _TOKEN_ANTI_CAPTURE_PRODUCTION_NOT_ACTIVATED,
        _TOKEN_PRODUCTION_ASSIGNMENT_ACTIVATED,
        _TOKEN_WINDOW_1429_FIRST_PHASE,
    ]
    if is_high_value_slot:
        phase_tokens.extend(
            [
                _TOKEN_VRF_INTEGRATED,
                _TOKEN_VRF_OUTSIDER_VERIFIED,
                _TOKEN_ANTI_CAPTURE_VERIFIED,
            ]
        )

    return JuryAssignmentQuote(
        review_epoch=review_epoch,
        review_lane=review_lane,
        claim_or_task_id=claim_or_task_id,
        regular_panel=regular_panel,
        outsider_panel=outsider_panel,
        panel_size=_PANEL_SIZE,
        reviewer_quorum_k=_REVIEWER_QUORUM_K,
        independence_k=_INDEPENDENCE_K,
        assignment_mode="vrf_verified" if is_high_value_slot else "epoch_hash_shadow",
        runtime_version=JURY_ASSIGNMENT_RUNTIME_VERSION,
        phase_tokens=phase_tokens,
        production_activated=False,
        cluster_diversity_distinct_clusters=cluster_evidence.distinct_clusters,
        cluster_diversity_largest_cluster_slots=cluster_evidence.largest_cluster_slots,
        cluster_diversity_total_panel_slots=cluster_evidence.total_panel_slots,
        cluster_diversity_max_cluster_share=cluster_evidence.max_cluster_share,
        cluster_diversity_floor=cluster_evidence.cluster_diversity_floor,
        cluster_diversity_max_cluster_share_ceiling=cluster_evidence.max_cluster_share_ceiling,
        cluster_diversity_verified=cluster_evidence.verified,
        vrf_excluded_agents=sorted(vrf_exclusion_reasons),
        vrf_exclusion_reasons=vrf_exclusion_reasons,
    )
