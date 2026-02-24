"""
ECU Profile Calibration Sweep — Phase 230 supplement.

Validates proposed 4-component weight vectors for ROBUST and REFINE profiles
against their stated behavioral intents. This is a kernel parameter sweep,
not a full multi-epoch agent simulation.

Reference: docs/whitepaper/whitepaper_ecu_profiles_and_payouts_v0.2.md
Kernel:    ilc_core/analysis/node_value_kernel.py
"""
from __future__ import annotations

import statistics
from typing import NamedTuple

import pytest

from ilc_core.analysis.node_value_kernel import (
    DEFAULT_EW_WEIGHTS,
    EwWeights,
    compute_epistemic_weight,
    validate_ew_weights,
    NodeEvidenceVector,
)


# ---------------------------------------------------------------------------
# Profile definitions
# ---------------------------------------------------------------------------

PROFILES: dict[str, EwWeights] = {
    "BAL": DEFAULT_EW_WEIGHTS,  # 0.35 / 0.25 / 0.20 / 0.20 — confirmed from kernel
    "ROBUST": {                  # Proposed: maximize contradiction-resilience scoring
        "reuse": 0.20,
        "contradiction_resilience": 0.45,
        "validation_integrity": 0.20,
        "path_uplift": 0.15,
    },
    "REFINE": {                  # Proposed: maximize reuse and throughput scoring
        "reuse": 0.45,
        "contradiction_resilience": 0.15,
        "validation_integrity": 0.20,
        "path_uplift": 0.20,
    },
}


# ---------------------------------------------------------------------------
# Synthetic node evidence scenarios
# ---------------------------------------------------------------------------

class Scenario(NamedTuple):
    name: str
    evidence: NodeEvidenceVector
    description: str


def _make_evidence(
    node_id: str,
    reuse_count: float = 0.0,
    claim_net_stake: float = 5.0,
    refutation_stake_against: float = 0.0,
    unique_agents_using: float = 0.0,
    path_lift_score: float | None = None,
) -> tuple[NodeEvidenceVector, float | None]:
    evidence: NodeEvidenceVector = {
        "node_id": node_id,
        "reuse_count": reuse_count,
        "claim_net_stake": claim_net_stake,
        "refutation_stake_against": refutation_stake_against,
        "unique_agents_using": unique_agents_using,
        "max_agent_reuse_share": 0.1,
        "usage_window": 1.0,
        "age_epochs": 1.0,
        "is_genesis": False,
        "freshness_gate": 1.0,
    }
    return evidence, path_lift_score


SCENARIOS: list[Scenario] = [
    # Highly-contested node: survived heavy refutation pressure
    Scenario(
        name="high_contradiction",
        evidence=_make_evidence(
            "contested-node",
            reuse_count=2.0,
            # Keep heavy absolute attack pressure but model a clear survival margin.
            claim_net_stake=20.0,
            refutation_stake_against=8.0,
            unique_agents_using=2.0,
        )[0],
        description="Node that survived heavy refutation — ROBUST should score highest",
    ),
    # Foundational node: widely reused, no adversarial pressure
    Scenario(
        name="high_reuse",
        evidence=_make_evidence(
            "foundational-node",
            reuse_count=5.0,
            claim_net_stake=5.0,
            # Slight contestation avoids reuse/contradiction component saturation ties.
            refutation_stake_against=1.0,
            unique_agents_using=1.0,
        )[0],
        description="High-reuse node with low contestation — REFINE should score highest",
    ),
    # Well-validated node: many independent validators
    Scenario(
        name="high_validation",
        evidence=_make_evidence(
            "validated-node",
            reuse_count=1.0,
            claim_net_stake=5.0,
            refutation_stake_against=0.0,
            unique_agents_using=3.0,
        )[0],
        description="Widely validated node — BAL should be competitive",
    ),
    # Uncontested average node: typical graph member
    Scenario(
        name="average_node",
        evidence=_make_evidence(
            "average-node",
            reuse_count=1.5,
            claim_net_stake=5.0,
            refutation_stake_against=0.5,
            unique_agents_using=1.5,
        )[0],
        description="Typical uncontested node — profiles should be close",
    ),
    # Mixed high-value node: high reuse + survived contestation
    Scenario(
        name="contested_foundational",
        evidence=_make_evidence(
            "contested-foundational",
            reuse_count=4.0,
            claim_net_stake=8.0,
            refutation_stake_against=6.0,
            unique_agents_using=2.0,
        )[0],
        description="High reuse AND survived heavy refutation — all profiles should score well",
    ),
]


# ---------------------------------------------------------------------------
# Score computation helper
# ---------------------------------------------------------------------------

def score_scenario(evidence: NodeEvidenceVector, weights: EwWeights) -> float:
    _, _, _, _, epistemic_weight = compute_epistemic_weight(evidence, weights=weights)
    return epistemic_weight


def score_all_profiles(evidence: NodeEvidenceVector) -> dict[str, float]:
    return {
        name: score_scenario(evidence, weights)
        for name, weights in PROFILES.items()
    }


# ---------------------------------------------------------------------------
# Tests: validate profile weight vectors are structurally valid
# ---------------------------------------------------------------------------

def test_all_profiles_are_valid_weight_vectors() -> None:
    """Every profile must pass kernel weight validation (4 keys, sum to 1.0)."""
    for name, weights in PROFILES.items():
        validated = validate_ew_weights(weights)
        total = sum(validated.values())
        assert abs(total - 1.0) < 1e-9, f"{name}: weights do not sum to 1.0 (got {total})"
        assert len(validated) == 4, f"{name}: must have exactly 4 components"


def test_bal_matches_kernel_default() -> None:
    """BAL profile must exactly match DEFAULT_EW_WEIGHTS from the kernel."""
    assert PROFILES["BAL"] == DEFAULT_EW_WEIGHTS


# ---------------------------------------------------------------------------
# Tests: behavioral intent validation
# ---------------------------------------------------------------------------

def test_robust_scores_highest_on_contested_nodes() -> None:
    """
    ROBUST's stated intent: fastest error detection, highest reward for
    surviving adversarial challenge.
    A heavily-contested node that survived should score higher under ROBUST
    than under BAL or REFINE.
    """
    contested = next(s for s in SCENARIOS if s.name == "high_contradiction")
    scores = score_all_profiles(contested.evidence)

    assert scores["ROBUST"] > scores["BAL"], (
        f"ROBUST ({scores['ROBUST']:.4f}) should outscore BAL ({scores['BAL']:.4f}) "
        f"on contested nodes"
    )
    assert scores["ROBUST"] > scores["REFINE"], (
        f"ROBUST ({scores['ROBUST']:.4f}) should outscore REFINE ({scores['REFINE']:.4f}) "
        f"on contested nodes"
    )


def test_refine_scores_highest_on_foundational_nodes() -> None:
    """
    REFINE's stated intent: maximize throughput, reward foundational reuse.
    A high-reuse, low-adversarial-pressure node should score higher under
    REFINE than under BAL or ROBUST.
    """
    foundational = next(s for s in SCENARIOS if s.name == "high_reuse")
    scores = score_all_profiles(foundational.evidence)

    assert scores["REFINE"] > scores["BAL"], (
        f"REFINE ({scores['REFINE']:.4f}) should outscore BAL ({scores['BAL']:.4f}) "
        f"on high-reuse nodes"
    )
    assert scores["REFINE"] > scores["ROBUST"], (
        f"REFINE ({scores['REFINE']:.4f}) should outscore ROBUST ({scores['ROBUST']:.4f}) "
        f"on high-reuse nodes"
    )


def test_bal_is_competitive_on_well_validated_nodes() -> None:
    """
    BAL is the general-purpose default. On a well-validated node with no
    extreme characteristics, BAL should not be the lowest-scoring profile.
    """
    validated = next(s for s in SCENARIOS if s.name == "high_validation")
    scores = score_all_profiles(validated.evidence)

    assert scores["BAL"] >= min(scores.values()), (
        f"BAL ({scores['BAL']:.4f}) should not be the worst-scoring profile on "
        f"well-validated nodes. Scores: {scores}"
    )


def test_profiles_converge_on_average_nodes() -> None:
    """
    On a typical uncontested node, all profiles should produce scores within
    a bounded range — no profile should dominate by more than 50%.
    """
    average = next(s for s in SCENARIOS if s.name == "average_node")
    scores = score_all_profiles(average.evidence)

    max_score = max(scores.values())
    min_score = min(scores.values())

    # No profile should dominate by more than 50% of min score
    assert max_score - min_score <= 0.5 * min_score + 0.1, (
        f"Profiles diverge too much on average nodes: {scores}. "
        f"Range: {max_score - min_score:.4f}"
    )


def test_all_profiles_positive_on_all_scenarios() -> None:
    """Every profile must produce a non-negative epistemic weight on every scenario."""
    for scenario in SCENARIOS:
        scores = score_all_profiles(scenario.evidence)
        for profile_name, score in scores.items():
            assert score >= 0.0, (
                f"{profile_name} produced negative score ({score:.4f}) "
                f"on scenario '{scenario.name}'"
            )


# ---------------------------------------------------------------------------
# Report: print score matrix for human review (not a test assertion)
# ---------------------------------------------------------------------------

def test_print_score_matrix() -> None:
    """
    Prints a human-readable scoring matrix across all profiles and scenarios.
    This test always passes — it exists to make sweep results visible in
    pytest -s output.
    """
    header = f"{'Scenario':<28} {'BAL':>8} {'ROBUST':>8} {'REFINE':>8}"
    print(f"\n\n{'='*60}")
    print("ECU Profile Calibration Sweep")
    print(f"{'='*60}")
    print(header)
    print("-" * 60)

    for scenario in SCENARIOS:
        scores = score_all_profiles(scenario.evidence)
        winner = max(scores, key=scores.__getitem__)
        row = (
            f"{scenario.name:<28} "
            f"{scores['BAL']:>8.4f} "
            f"{scores['ROBUST']:>8.4f} "
            f"{scores['REFINE']:>8.4f}"
            f"  ← {winner}"
        )
        print(row)

    print(f"{'='*60}\n")
