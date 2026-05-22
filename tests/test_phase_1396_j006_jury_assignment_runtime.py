"""Phase 1396 / J-006 — Default-off jury assignment quote runtime tests.

Proves:
- module and ADR-0040 dependency exist
- required phase tokens present in source
- deterministic output for identical inputs
- different output for different epoch / lane / claim
- regular panel contains exactly 7 distinct agents
- outsider panel contains exactly 1 agent
- outsider agent is not in the regular panel
- same-operator-domain agents are not counted as independent (capped correctly)
- author and author's operator domain are excluded
- independence_k constraint: no single operator_domain dominates the regular panel
- PRODUCTION_ASSIGNMENT_NOT_ACTIVATED is False after Phase 1429 production assignment activation
- assignment_mode is "epoch_hash_shadow"
- production_activated is False in every quote
- JuryAssignmentError raised when pool is too small
- JuryAssignmentError raised when no outsider candidate available
"""

from __future__ import annotations

import importlib
from pathlib import Path

import pytest

REPO = Path(__file__).parent.parent
RUNTIME_MODULE = REPO / "ilc_core/epistemic/jury_assignment_runtime.py"

# ---------------------------------------------------------------------------
# Module / dependency existence
# ---------------------------------------------------------------------------

def test_runtime_module_exists():
    assert RUNTIME_MODULE.exists(), "jury_assignment_runtime.py must exist"


def test_adr_0040_dependency_token_in_source():
    src = RUNTIME_MODULE.read_text(encoding="utf-8")
    assert "jury_eligibility_assignment_adr_accepted_phase_j002" in src


# ---------------------------------------------------------------------------
# Required phase tokens in source
# ---------------------------------------------------------------------------

_REQUIRED_TOKENS = [
    "default_off_jury_assignment_quote_runtime_phase_j006",
    "jury_assignment_no_public_activation_phase_j006",
    "epoch_hash_shadow_assignment_only_phase_j006",
]


@pytest.mark.parametrize("token", _REQUIRED_TOKENS)
def test_source_contains_token(token):
    src = RUNTIME_MODULE.read_text(encoding="utf-8")
    assert token in src, f"jury_assignment_runtime.py must contain token: {token}"


# ---------------------------------------------------------------------------
# Import and constant checks
# ---------------------------------------------------------------------------

from ilc_core.epistemic.jury_assignment_runtime import (
    PRODUCTION_ASSIGNMENT_NOT_ACTIVATED,
    JURY_ASSIGNMENT_RUNTIME_VERSION,
    EligibleAgent,
    JuryAssignmentError,
    JuryAssignmentQuote,
    quote_jury_assignment,
    _PANEL_REGULAR,
    _PANEL_OUTSIDER,
    _INDEPENDENCE_K,
    _MAX_PER_OPERATOR_DOMAIN,
)


def test_production_assignment_activation_guard_flipped_after_phase_1429():
    """Phase 1429 flips the assignment guard after J-008 PASS."""
    assert PRODUCTION_ASSIGNMENT_NOT_ACTIVATED is False


def test_version_token_present():
    assert "jury_assignment_runtime_phase_j006" in JURY_ASSIGNMENT_RUNTIME_VERSION


# ---------------------------------------------------------------------------
# Helpers: build a standard pool
# ---------------------------------------------------------------------------

def _make_agent(
    agent_id: str,
    cluster_id: str = "c1",
    operator_domain: str = "op-a",
    outsider: bool = False,
    score: str = "tier1",
) -> EligibleAgent:
    return EligibleAgent(
        agent_id=agent_id,
        cluster_id=cluster_id,
        operator_domain=operator_domain,
        identity_lineage_ref=f"lineage-{agent_id}",
        outsider_candidate_flag=outsider,
        capability_tier_or_lane_score=score,
    )


def _standard_pool() -> list:
    """7 regular candidates from 3 operator domains + 2 outsider candidates."""
    return [
        # Regular candidates — 3 domains
        _make_agent("r1", cluster_id="c1", operator_domain="op-a"),
        _make_agent("r2", cluster_id="c1", operator_domain="op-a"),
        _make_agent("r3", cluster_id="c1", operator_domain="op-a"),
        _make_agent("r4", cluster_id="c2", operator_domain="op-b"),
        _make_agent("r5", cluster_id="c2", operator_domain="op-b"),
        _make_agent("r6", cluster_id="c3", operator_domain="op-c"),
        _make_agent("r7", cluster_id="c3", operator_domain="op-c"),
        # Outsider candidates — separate domain
        _make_agent("o1", cluster_id="c4", operator_domain="op-out", outsider=True),
        _make_agent("o2", cluster_id="c4", operator_domain="op-out", outsider=True),
    ]


def _call_standard(**overrides) -> JuryAssignmentQuote:
    kwargs = dict(
        review_epoch=100,
        review_lane="objective",
        claim_or_task_id="cid-abc123",
        author_agent_id="author-1",
        author_operator_domain="op-author",
        eligible_agents=_standard_pool(),
    )
    kwargs.update(overrides)
    return quote_jury_assignment(**kwargs)


# ---------------------------------------------------------------------------
# Panel structure
# ---------------------------------------------------------------------------

def test_regular_panel_size():
    quote = _call_standard()
    assert len(quote.regular_panel) == _PANEL_REGULAR


def test_outsider_panel_size():
    quote = _call_standard()
    assert len(quote.outsider_panel) == _PANEL_OUTSIDER


def test_no_overlap_between_regular_and_outsider():
    quote = _call_standard()
    assert not set(quote.regular_panel) & set(quote.outsider_panel)


def test_panel_size_constant():
    quote = _call_standard()
    assert quote.panel_size == _PANEL_REGULAR + _PANEL_OUTSIDER


def test_reviewer_quorum_k():
    quote = _call_standard()
    assert quote.reviewer_quorum_k == 5


def test_independence_k_field():
    quote = _call_standard()
    assert quote.independence_k == _INDEPENDENCE_K


# ---------------------------------------------------------------------------
# Determinism
# ---------------------------------------------------------------------------

def test_deterministic_same_inputs():
    q1 = _call_standard()
    q2 = _call_standard()
    assert q1.regular_panel == q2.regular_panel
    assert q1.outsider_panel == q2.outsider_panel


def test_different_epoch_changes_panel():
    q1 = _call_standard(review_epoch=100)
    q2 = _call_standard(review_epoch=101)
    # With a larger pool there's a chance they match by coincidence, but
    # with 9 agents and 7 selected, epoch change should produce a different ordering.
    # This is a probabilistic sanity check — a collision here would be alarming.
    assert (q1.regular_panel != q2.regular_panel) or (q1.outsider_panel != q2.outsider_panel)


def test_different_lane_changes_panel():
    q1 = _call_standard(review_lane="objective")
    q2 = _call_standard(review_lane="refutation")
    assert (q1.regular_panel != q2.regular_panel) or (q1.outsider_panel != q2.outsider_panel)


def test_different_claim_changes_panel():
    q1 = _call_standard(claim_or_task_id="cid-aaa")
    q2 = _call_standard(claim_or_task_id="cid-bbb")
    assert (q1.regular_panel != q2.regular_panel) or (q1.outsider_panel != q2.outsider_panel)


# ---------------------------------------------------------------------------
# Author / conflict exclusion
# ---------------------------------------------------------------------------

def test_author_excluded_from_panel():
    pool = _standard_pool()
    # Add author as a regular candidate
    pool.append(_make_agent("author-1", cluster_id="c9", operator_domain="op-author"))
    quote = quote_jury_assignment(
        review_epoch=100,
        review_lane="objective",
        claim_or_task_id="cid-abc123",
        author_agent_id="author-1",
        author_operator_domain="op-author",
        eligible_agents=pool,
    )
    assert "author-1" not in quote.regular_panel
    assert "author-1" not in quote.outsider_panel


def test_author_operator_domain_excluded():
    """All agents sharing author_operator_domain must not appear on the panel."""
    pool = _standard_pool()
    # Add two agents in author's operator domain
    pool.append(_make_agent("same-dom-1", cluster_id="c9", operator_domain="op-author"))
    pool.append(_make_agent("same-dom-2", cluster_id="c9", operator_domain="op-author"))
    quote = quote_jury_assignment(
        review_epoch=100,
        review_lane="objective",
        claim_or_task_id="cid-abc123",
        author_agent_id="author-1",
        author_operator_domain="op-author",
        eligible_agents=pool,
    )
    all_selected = set(quote.regular_panel) | set(quote.outsider_panel)
    assert "same-dom-1" not in all_selected
    assert "same-dom-2" not in all_selected


# ---------------------------------------------------------------------------
# same_operator_domain_not_independent — independence_k constraint
# ---------------------------------------------------------------------------

def test_independence_k_operator_domain_cap():
    """No single operator_domain may contribute more than _MAX_PER_OPERATOR_DOMAIN
    agents to the regular panel."""
    quote = _call_standard()
    # Count per operator domain in the regular panel
    pool_lookup = {a.agent_id: a for a in _standard_pool()}
    domain_counts: dict = {}
    for agent_id in quote.regular_panel:
        if agent_id in pool_lookup:
            dom = pool_lookup[agent_id].operator_domain
            domain_counts[dom] = domain_counts.get(dom, 0) + 1
    for dom, count in domain_counts.items():
        assert count <= _MAX_PER_OPERATOR_DOMAIN, (
            f"operator_domain '{dom}' contributed {count} agents to regular panel; "
            f"max allowed is {_MAX_PER_OPERATOR_DOMAIN} "
            f"(same_operator_domain_not_independent, independence_k={_INDEPENDENCE_K})"
        )


def test_single_domain_pool_raises_when_independence_not_satisfied():
    """If all regular candidates share one operator domain and the pool is too small
    to satisfy independence_k, JuryAssignmentError must be raised."""
    # 10 agents from a single domain — only _MAX_PER_OPERATOR_DOMAIN can be selected
    pool = [
        _make_agent(f"r{i}", cluster_id="c1", operator_domain="op-mono")
        for i in range(10)
    ]
    pool.append(_make_agent("o1", cluster_id="c2", operator_domain="op-out", outsider=True))
    with pytest.raises(JuryAssignmentError, match="insufficient_regular"):
        quote_jury_assignment(
            review_epoch=1,
            review_lane="objective",
            claim_or_task_id="cid-x",
            author_agent_id="non-existent",
            author_operator_domain="op-author",
            eligible_agents=pool,
        )


# ---------------------------------------------------------------------------
# Error conditions
# ---------------------------------------------------------------------------

def test_too_few_regular_candidates_raises():
    pool = [
        _make_agent("r1", operator_domain="op-a"),
        _make_agent("r2", operator_domain="op-b"),
        _make_agent("o1", outsider=True, operator_domain="op-out"),
    ]
    with pytest.raises(JuryAssignmentError, match="insufficient_regular"):
        quote_jury_assignment(
            review_epoch=1,
            review_lane="objective",
            claim_or_task_id="cid-x",
            author_agent_id="not-in-pool",
            author_operator_domain="op-author",
            eligible_agents=pool,
        )


def test_no_outsider_candidates_raises():
    # 7 diverse regular candidates but no outsider_candidate_flag=True agents
    pool = [
        _make_agent("r1", cluster_id="c1", operator_domain="op-a"),
        _make_agent("r2", cluster_id="c1", operator_domain="op-a"),
        _make_agent("r3", cluster_id="c2", operator_domain="op-b"),
        _make_agent("r4", cluster_id="c2", operator_domain="op-b"),
        _make_agent("r5", cluster_id="c3", operator_domain="op-c"),
        _make_agent("r6", cluster_id="c3", operator_domain="op-c"),
        _make_agent("r7", cluster_id="c4", operator_domain="op-d"),
    ]
    with pytest.raises(JuryAssignmentError, match="insufficient_outsider"):
        quote_jury_assignment(
            review_epoch=1,
            review_lane="objective",
            claim_or_task_id="cid-x",
            author_agent_id="not-in-pool",
            author_operator_domain="op-author",
            eligible_agents=pool,
        )


def test_invalid_epoch_raises():
    with pytest.raises(ValueError):
        quote_jury_assignment(
            review_epoch=-1,
            review_lane="objective",
            claim_or_task_id="cid-x",
            author_agent_id="a",
            author_operator_domain="op-a",
            eligible_agents=_standard_pool(),
        )


def test_empty_lane_raises():
    with pytest.raises(ValueError):
        quote_jury_assignment(
            review_epoch=1,
            review_lane="",
            claim_or_task_id="cid-x",
            author_agent_id="a",
            author_operator_domain="op-a",
            eligible_agents=_standard_pool(),
        )


# ---------------------------------------------------------------------------
# Non-activation guarantees
# ---------------------------------------------------------------------------

def test_assignment_mode_is_shadow():
    quote = _call_standard()
    assert quote.assignment_mode == "epoch_hash_shadow"


def test_production_activated_is_false():
    quote = _call_standard()
    assert quote.production_activated is False


def test_phase_tokens_in_quote():
    quote = _call_standard()
    assert "default_off_jury_assignment_quote_runtime_phase_j006" in quote.phase_tokens
    assert "jury_assignment_no_public_activation_phase_j006" in quote.phase_tokens
    assert "epoch_hash_shadow_assignment_only_phase_j006" in quote.phase_tokens


def test_no_random_import_in_source():
    """PRNG ban (ILC CODING-SECURITY-STANDARD §2): no import random in ilc_core/."""
    src = RUNTIME_MODULE.read_text(encoding="utf-8")
    assert "import random" not in src, "jury_assignment_runtime.py must not import random"


def test_no_float_for_ecu_in_source():
    """Float ban (ILC CODING-SECURITY-STANDARD §3): capability_tier_or_lane_score is str."""
    src = RUNTIME_MODULE.read_text(encoding="utf-8")
    # The score field must be typed as str, not float
    assert "capability_tier_or_lane_score: float" not in src


# ---------------------------------------------------------------------------
# Package export
# ---------------------------------------------------------------------------

def test_package_exports_quote_function():
    from ilc_core.epistemic import quote_jury_assignment as qja
    assert callable(qja)


def test_package_exports_eligible_agent():
    from ilc_core.epistemic import EligibleAgent as EA
    assert EA is not None


def test_package_exports_production_flag():
    from ilc_core.epistemic import PRODUCTION_ASSIGNMENT_NOT_ACTIVATED as flag
    assert flag is False
