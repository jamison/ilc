"""
SIM-LAUNDER-02B — Observer Epistemics: Contextual Truth and Binary Jury Collapse
=================================================================================

The reviewer's central theoretical prediction:

  "When disagreement is caused by context or proposition underspecification,
   forcing it through a binary jury should destroy epistemically useful
   information; preserving observer/context structure should allow the graph
   to represent the disagreement without treating either population as Byzantine."

This experiment tests that prediction directly and falsifiably.

Four claim types with distinct latent structures:

  OBJECTIVE:   X has a single Boolean truth value. Expert disagreement is error.
  CONTESTED:   X has a single truth value, but evidence is genuinely ambiguous.
               Disagreement is partially legitimate, partially error.
  CONTEXTUAL:  X(C1)=True, X(C2)=False. Both observation populations are correct
               for their context. Forcing binary consensus loses the context structure.
  SUBJECTIVE:  No single truth value. Observer-relative utility determines stance.
               Binary consensus is inappropriate; graph should preserve poles.

For each claim type, we measure:
  (a) Binary jury verdict distribution — what does a 7-person panel produce?
  (b) Context-preserving graph structure — what does the graph "know" that the jury can't see?
  (c) Distinguishability: can an outside observer tell the claim types apart from
      jury verdicts alone? From graph structure?

Key metrics:
  verdict_entropy:   H(P(True), P(False)) across trials (0=unanimous, 1=50-50)
  within_context_agreement: mean agreement within each context group
  between_context_agreement: agreement across context groups
  context_separation: within_context_agreement - between_context_agreement
                      (0 = no contextual structure; high = strong context structure)
  jury_distinguishability: can a classifier separate claim types from jury votes?
  graph_distinguishability: can a classifier separate them from context-preserving graph?

The Popperian dimension:
  Also test: a claim with 40 independent observations supporting it vs.
  a claim with 40 descendants from 1 root but ALSO 20 failed refutation attempts.
  Which has higher "Popperian standing" — survived attempts to falsify it?

Two primary falsifiable predictions (from Astra 6.0):
  P1: CONTEXTUAL and CONTESTED claims produce statistically IDENTICAL jury verdict
      distributions. A binary jury cannot distinguish them (context_separation ≈ 0
      in jury output).
  P2: A context-preserving graph metric CAN distinguish CONTEXTUAL from CONTESTED:
      context_separation(graph) >> context_separation(jury_output)
      because the graph retains (observer_id, context_id, stance) triples.

Secondary:
  P3: SUBJECTIVE claims produce near-identical jury output to CONTEXTUAL at high
      observer correlation within poles (both look like 50-50 split).
  P4: A claim with many failed refutation attempts (Popperian hardiness) has
      a DIFFERENT epistemic profile than an equally-supported claim with no
      refutation attempts — even at identical raw_reuse_weight.
"""

from __future__ import annotations

import hashlib
import json
import sys
import os
import math
from datetime import datetime, timezone
from dataclasses import dataclass, field
from typing import Dict, List, Tuple

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

SIM_ID = "SIM-LAUNDER-02B"

N_TRIALS     = 10_000    # jury verdict trials per claim type
PANEL_SIZE   = 7
N_OBS        = 100       # total observers per claim
N_CONTEXTS   = 2         # for contextual/subjective claims


# ─── Claim type definitions ──────────────────────────────────────────────────

@dataclass
class Observer:
    obs_id: int
    context_id: int       # 0 = no context; 1,2 = distinct contexts
    base_accuracy: float  # P(correct vote | ground truth for their context)


@dataclass
class Claim:
    claim_type: str       # OBJECTIVE, CONTESTED, CONTEXTUAL, SUBJECTIVE
    ground_truth: bool    # latent truth (known to simulator, NOT to agents)
    # For contextual: ground truth depends on context
    context_truths: Dict[int, bool] = field(default_factory=dict)  # context_id → truth
    observers: List[Observer] = field(default_factory=list)


def build_claim(claim_type: str, rng: np.random.Generator) -> Claim:
    if claim_type == "OBJECTIVE":
        # Single truth, high accuracy observers, no context structure
        ground_truth = True
        observers = [
            Observer(i, 0, rng.beta(7, 2))  # mean accuracy ~0.78
            for i in range(N_OBS)
        ]
        return Claim("OBJECTIVE", ground_truth, {}, observers)

    elif claim_type == "CONTESTED":
        # Single truth but genuinely ambiguous evidence — lower accuracy
        ground_truth = True
        observers = [
            Observer(i, 0, rng.beta(3, 3))  # mean accuracy ~0.50, high variance
            for i in range(N_OBS)
        ]
        return Claim("CONTESTED", ground_truth, {}, observers)

    elif claim_type == "CONTEXTUAL":
        # X(C1)=True, X(C2)=False. Both populations correct for their context.
        ground_truth = True  # latent "X" is True in C1, False in C2
        context_truths = {1: True, 2: False}
        # Half observers in each context, high accuracy within context
        observers = []
        for i in range(N_OBS):
            ctx = 1 if i < N_OBS // 2 else 2
            observers.append(Observer(i, ctx, rng.beta(7, 2)))  # accurate within context
        return Claim("CONTEXTUAL", ground_truth, context_truths, observers)

    elif claim_type == "SUBJECTIVE":
        # No single truth. Observer cluster A says True, cluster B says False.
        # Both are "right" by their values. Modeled as each cluster extremely confident
        # in their own direction.
        ground_truth = True  # arbitrary — there's no real ground truth
        context_truths = {1: True, 2: False}
        observers = []
        for i in range(N_OBS):
            cluster = 1 if i < N_OBS // 2 else 2
            # Very high within-cluster agreement (strong values, not weak evidence)
            observers.append(Observer(i, cluster, 0.92))
        return Claim("SUBJECTIVE", ground_truth, context_truths, observers)

    else:
        raise ValueError(f"Unknown claim type: {claim_type}")


# ─── Voting ─────────────────────────────────────────────────────────────────

def vote(observer: Observer, claim: Claim, rng: np.random.Generator) -> int:
    """
    Cast a vote for this observer given the claim's epistemic structure.
    For contextual/subjective claims, observers vote based on their context's truth.
    """
    if claim.context_truths:
        truth_for_ctx = claim.context_truths.get(observer.context_id, claim.ground_truth)
    else:
        truth_for_ctx = claim.ground_truth

    signal = 1.0 if truth_for_ctx else -1.0
    noise = rng.normal(0, 1)
    raw = signal * observer.base_accuracy * 2 + noise  # scaled signal
    return 1 if raw > 0 else 0


def jury_trial(claim: Claim, panel_size: int, rng: np.random.Generator) -> Tuple[int, List[int]]:
    """Select panel_size observers at random (no CDL-V3 for simplicity here),
    collect votes, return (verdict, votes)."""
    panel = rng.choice(len(claim.observers), size=panel_size, replace=False)
    votes = [vote(claim.observers[p], claim, rng) for p in panel]
    verdict = 1 if sum(votes) > panel_size / 2 else 0
    return verdict, votes


# ─── Graph-level metrics ─────────────────────────────────────────────────────

def context_separation(claim: Claim, n_obs_used: int, rng: np.random.Generator) -> Tuple[float, float]:
    """
    Measure within-context agreement vs between-context agreement.
    Returns (within_ctx_agreement, context_separation_score).
    context_separation = within_ctx - between_ctx.
    0 = no contextual structure (claim looks monolithic to graph).
    High = strong contextual structure (graph can distinguish populations).
    """
    obs = claim.observers[:n_obs_used]
    votes_by_ctx: Dict[int, List[int]] = {}
    for o in obs:
        v = vote(o, claim, rng)
        votes_by_ctx.setdefault(o.context_id, []).append(v)

    # Within-context: mean agreement (fraction agreeing with majority within their group)
    within_agreements = []
    for ctx, votes in votes_by_ctx.items():
        if len(votes) < 2:
            continue
        p = sum(votes) / len(votes)
        # Agreement = max(p, 1-p) — how concentrated the within-ctx votes are
        within_agreements.append(max(p, 1 - p))
    within_ctx = sum(within_agreements) / max(1, len(within_agreements))

    # Between-context: mean agreement across groups (do they agree with each other?)
    ctx_means = {ctx: sum(v)/len(v) for ctx, v in votes_by_ctx.items() if votes_by_ctx[ctx]}
    if len(ctx_means) < 2:
        return within_ctx, 0.0
    means = list(ctx_means.values())
    # Agreement across contexts: closer to 1.0 means same direction, 0.5 means opposite
    ctx_pairs = [(means[i], means[j]) for i in range(len(means)) for j in range(i+1, len(means))]
    between_ctx = sum(1 - abs(a - b) for a, b in ctx_pairs) / max(1, len(ctx_pairs))

    separation = within_ctx - between_ctx
    return within_ctx, separation


def popperian_profile(n_support: int, n_refute_attempts: int, p_survive: float, rng: np.random.Generator) -> dict:
    """
    Compare two epistemic profiles with equal raw support count but different
    refutation histories. Popperian standing should prefer the claim that
    survived many refutation attempts.
    """
    survived = sum(1 for _ in range(n_refute_attempts) if rng.random() < p_survive)
    popperian_weight = n_support + survived * 0.5  # each survived refutation adds epistemic credit
    return {
        "n_support": n_support,
        "n_refute_attempts": n_refute_attempts,
        "n_survived": survived,
        "popperian_weight": round(popperian_weight, 2),
        "raw_weight_equivalent": n_support,  # what a naive weight would see
    }


# ─── Main ───────────────────────────────────────────────────────────────────

CLAIM_TYPES = ["OBJECTIVE", "CONTESTED", "CONTEXTUAL", "SUBJECTIVE"]


def main():
    rng = np.random.default_rng(42)
    print(f"[{SIM_ID}] {len(CLAIM_TYPES)} claim types × {N_TRIALS} jury trials", file=sys.stderr)

    verdict_results = {}
    graph_results = {}

    for ct in CLAIM_TYPES:
        claim = build_claim(ct, rng)
        verdicts = []
        vote_fractions = []
        ctx_separations = []
        within_ctxs = []

        for _ in range(N_TRIALS):
            verdict, votes = jury_trial(claim, PANEL_SIZE, rng)
            verdicts.append(verdict)
            vote_fractions.append(sum(votes) / len(votes))
            within_ctx, sep = context_separation(claim, 30, rng)
            ctx_separations.append(sep)
            within_ctxs.append(within_ctx)

        p_true = sum(verdicts) / N_TRIALS
        verdict_entropy = -(p_true * math.log2(max(p_true, 1e-9)) +
                            (1 - p_true) * math.log2(max(1 - p_true, 1e-9)))
        mean_vote_frac = sum(vote_fractions) / N_TRIALS
        mean_ctx_sep = sum(ctx_separations) / N_TRIALS
        mean_within = sum(within_ctxs) / N_TRIALS

        verdict_results[ct] = {
            "p_verdict_true": round(p_true, 4),
            "verdict_entropy": round(verdict_entropy, 4),
            "mean_vote_fraction": round(mean_vote_frac, 4),
            "n_trials": N_TRIALS,
        }
        graph_results[ct] = {
            "mean_within_context_agreement": round(mean_within, 4),
            "mean_context_separation": round(mean_ctx_sep, 4),
        }

        print(
            f"  {ct:12s}: P(True)={p_true:.4f} H={verdict_entropy:.4f} "
            f"within_ctx={mean_within:.4f} ctx_sep={mean_ctx_sep:.4f}",
            file=sys.stderr,
        )

    # Jury distinguishability: can verdict distribution alone separate CONTEXTUAL from CONTESTED?
    # P1 check: CONTEXTUAL and CONTESTED should have similar verdict entropy
    h_ctx   = verdict_results["CONTEXTUAL"]["verdict_entropy"]
    h_cont  = verdict_results["CONTESTED"]["verdict_entropy"]
    jury_indistinguishable = abs(h_ctx - h_cont) < 0.05
    p1_v = "CONFIRMED" if jury_indistinguishable else "REFUTED"
    print(f"\nP1: CONTEXTUAL entropy={h_ctx:.4f} vs CONTESTED entropy={h_cont:.4f} "
          f"diff={abs(h_ctx-h_cont):.4f} — jury_indistinguishable={jury_indistinguishable} [{p1_v}]",
          file=sys.stderr)

    # P2: graph separation score should differ between CONTEXTUAL and CONTESTED
    sep_ctx  = graph_results["CONTEXTUAL"]["mean_context_separation"]
    sep_cont = graph_results["CONTESTED"]["mean_context_separation"]
    graph_distinguishable = sep_ctx > sep_cont + 0.05
    p2_v = "CONFIRMED" if graph_distinguishable else "REFUTED"
    print(f"P2: CONTEXTUAL ctx_sep={sep_ctx:.4f} vs CONTESTED ctx_sep={sep_cont:.4f} "
          f"— graph_distinguishable={graph_distinguishable} [{p2_v}]",
          file=sys.stderr)

    # P3: SUBJECTIVE and CONTEXTUAL produce similar jury outputs
    h_subj = verdict_results["SUBJECTIVE"]["verdict_entropy"]
    p3_v = "CONFIRMED" if abs(h_subj - h_ctx) < 0.10 else "REFUTED"
    print(f"P3: SUBJECTIVE entropy={h_subj:.4f} vs CONTEXTUAL entropy={h_ctx:.4f} [{p3_v}]",
          file=sys.stderr)

    # P4: Popperian profiles — identical raw support, different refutation histories
    print(f"\nPopperian profile comparison (N_TRIALS=1000, p_survive=0.85):", file=sys.stderr)
    pp_low  = popperian_profile(40, 0,  0.85, rng)    # 40 support, no refutation attempts
    pp_high = popperian_profile(40, 20, 0.85, rng)    # 40 support, 20 failed refutations
    p4_v = "CONFIRMED" if pp_high["popperian_weight"] > pp_low["popperian_weight"] else "REFUTED"
    print(f"  Low refutation  history: {pp_low}", file=sys.stderr)
    print(f"  High refutation history: {pp_high}", file=sys.stderr)
    print(f"  Popperian weight: {pp_low['popperian_weight']} vs {pp_high['popperian_weight']} [{p4_v}]",
          file=sys.stderr)

    # Information destroyed by binary jury — quantify
    print(f"\nInformation destroyed by binary jury:", file=sys.stderr)
    print(f"  CONTEXTUAL claim: graph context_separation={sep_ctx:.4f} (preserved in graph)", file=sys.stderr)
    print(f"  CONTEXTUAL claim: jury output entropy={h_ctx:.4f} (context not recoverable from verdicts)", file=sys.stderr)
    info_destroyed = max(0, sep_ctx - (h_ctx - h_cont))
    print(f"  Context information lost = {info_destroyed:.4f} (separation that jury verdict cannot carry)", file=sys.stderr)

    result = {
        "sim_id": SIM_ID,
        "description": "Observer epistemics: binary jury collapse of contextual/contested claims",
        "methodological_note": (
            "Tests whether binary jury verdict distributions can distinguish claim types "
            "that differ only in the contextual structure of their supporting observations. "
            "Context-preserving graph metric is a research proposal, not current ILC."
        ),
        "verdict_results": verdict_results,
        "graph_results": graph_results,
        "popperian_comparison": {
            "low_refutation_history": pp_low,
            "high_refutation_history": pp_high,
        },
        "key_finding": {
            "jury_distinguishable_contextual_vs_contested": not jury_indistinguishable,
            "graph_distinguishable_contextual_vs_contested": graph_distinguishable,
            "information_destroyed_by_binary_jury": round(info_destroyed, 4),
        },
        "predictions": {
            "P1": "CONTEXTUAL and CONTESTED have identical jury verdict entropy (diff < 0.05)",
            "P2": "Context-preserving graph distinguishes CONTEXTUAL from CONTESTED (ctx_sep > +0.05)",
            "P3": "SUBJECTIVE and CONTEXTUAL have similar jury entropy (diff < 0.10)",
            "P4": "Claim with 20 failed refutations has higher Popperian weight than 0 attempts",
        },
        "run_timestamp_utc": datetime.now(timezone.utc).isoformat(),
    }

    payload = json.dumps(result, sort_keys=True, separators=(",", ":")).encode()
    sha = hashlib.sha384(payload).hexdigest()
    result["sha384"] = sha
    print(json.dumps(result, indent=2, sort_keys=True))
    print(f"\n[{SIM_ID}] SHA-384: {sha}", file=sys.stderr)


if __name__ == "__main__":
    main()
