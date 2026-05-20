"""Phase 1396 / J-006 — Default-off jury assignment quote runtime.

Implements a deterministic, auditable panel-quoting function using epoch-hash
selection (ADR-0040 §Assignment Source).  This is a *quote-only* primitive:

  - no ledger writes
  - no graph writes
  - no production reward activation
  - no VRF proof
  - epoch-hash shadow assignment only (epoch_hash_shadow_assignment_only_phase_j006)

For production high-value assignment:
  vrf_required_for_production_high_value_assignment (ADR-0040 §Assignment Source)

Required phase tokens:
  default_off_jury_assignment_quote_runtime_phase_j006
  jury_assignment_no_public_activation_phase_j006
  epoch_hash_shadow_assignment_only_phase_j006
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import List, Optional

JURY_ASSIGNMENT_RUNTIME_VERSION = "jury_assignment_runtime_phase_j006.v0.1"
ADR_0040_DEPENDENCY = "jury_eligibility_assignment_adr_accepted_phase_j002"

# Phase tokens — must appear in module source for test_spec_contains_token parity
_TOKEN_DEFAULT_OFF = "default_off_jury_assignment_quote_runtime_phase_j006"
_TOKEN_NO_ACTIVATION = "jury_assignment_no_public_activation_phase_j006"
_TOKEN_SHADOW_ONLY = "epoch_hash_shadow_assignment_only_phase_j006"

_DOMAIN_SEPARATOR = "ilc_jury_assignment_v1"

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

# Safety gate: this flag must remain True until J-008 production activation gate passes.
PRODUCTION_ASSIGNMENT_NOT_ACTIVATED: bool = True


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
    assignment_mode: str        # always "epoch_hash_shadow"
    runtime_version: str
    phase_tokens: List[str]
    production_activated: bool  # always False — never flip without J-008 gate


class JuryAssignmentError(Exception):
    """Raised when panel construction fails due to insufficient eligible agents."""


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
    sorted_candidates = sorted(candidates, key=lambda a: scores[a.agent_id])
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

    sorted_pool = sorted(pool, key=lambda a: scores[a.agent_id])
    return [sorted_pool[0].agent_id]


def quote_jury_assignment(
    *,
    review_epoch: int,
    review_lane: str,
    claim_or_task_id: str,
    author_agent_id: str,
    author_operator_domain: str,
    eligible_agents: List[EligibleAgent],
) -> JuryAssignmentQuote:
    """Compute a deterministic panel quote for a given review request.

    Args:
        review_epoch:         Protocol review epoch number (integer, not wall-clock).
        review_lane:          Lane identifier string (e.g. "objective", "refutation").
        claim_or_task_id:     Content-addressed claim or task identifier.
        author_agent_id:      Agent ID of the claim/task author — excluded from panel.
        author_operator_domain: Operator domain of the author — excluded from panel.
        eligible_agents:      Pool of agents satisfying eligibility gates for this lane.

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

    # Step 1 — compute per-agent scores (deterministic, domain-separated)
    scores = {
        agent.agent_id: _agent_score(review_epoch, review_lane, claim_or_task_id, agent)
        for agent in eligible_agents
    }

    # Step 2 — filter: remove conflicted agents (author, same operator domain as author)
    non_conflicted = [
        a for a in eligible_agents
        if a.agent_id != author_agent_id
        and a.operator_domain != author_operator_domain
    ]

    # Step 3 — split: regular candidates vs. outsider candidates
    regular_candidates = [a for a in non_conflicted if not a.outsider_candidate_flag]
    outsider_candidates = [a for a in non_conflicted if a.outsider_candidate_flag]

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

    if len(outsider_panel) < _PANEL_OUTSIDER:
        raise JuryAssignmentError(
            "insufficient_outsider_candidates: no eligible outsider candidate found; "
            "outsider seat is required (ADM-003 7+1 panel shape)"
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
        assignment_mode="epoch_hash_shadow",
        runtime_version=JURY_ASSIGNMENT_RUNTIME_VERSION,
        phase_tokens=[_TOKEN_DEFAULT_OFF, _TOKEN_NO_ACTIVATION, _TOKEN_SHADOW_ONLY],
        production_activated=False,
    )
