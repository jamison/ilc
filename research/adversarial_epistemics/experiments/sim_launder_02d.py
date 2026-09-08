"""
SIM-LAUNDER-02D — Four-Dimensional Epistemic Profile
=====================================================

Tests Astra's proposed multi-axis epistemic coordinate system:

  E(x) = { C: consensus,
             I: provenance independence,
             R: test resistance,
             K: contextual structure (within, between) }

Design: 6 claim types with known latent properties. For each, measure all
four dimensions. Show which pairs of claim types are separable in:
  (a) jury-only space: C alone
  (b) full 4D space:   (C, I, R, K_within, K_between)

The key architectural hypothesis: two claim types may be identical in C (jury
verdict distribution) but distinguishable in (I, R, K). Specifically:

  LAUNDERED ≈ OBJECTIVE  by jury verdict  → different by (I, R)
  POPPERIAN ≈ CONTESTED  by jury verdict  → different by (I, R)

Observer model extension: each observer now has a cluster_id ∈ {0..N_CLUSTERS-1}.
Cluster diversity of a panel = number of distinct clusters represented.
This is the observer-level analogue of IEC in graph propagation.

Dimensions:

  C: verdict_entropy of 10,000 jury trials
  I: mean distinct clusters in panel (independent epistemic origins)
  R: P(True majority | 2 adversarial voters in panel of 7)
       adversarial voter = votes opposite of ground truth with P=0.9
  K: (mean_within_ctx, mean_between_ctx) at n_obs_used=100

Six claim types:

  OBJECTIVE:   truth=True, beta(7,2) accuracy, 10 clusters (uniform spread)
  CONTESTED:   truth=True, beta(3,3) accuracy, 10 clusters (uniform spread)
  CONTEXTUAL:  C1=True/C2=False, beta(7,2) accuracy, 10 clusters (5 per context)
  SUBJECTIVE:  C1-value/C2-value, 0.92 accuracy, 10 clusters (5 per context)
  LAUNDERED:   truth=True, beta(7,2) accuracy, 1 cluster (all same — correlated)
  POPPERIAN:   truth=True, beta(4,4) accuracy, 20 clusters (wide independence)

Predictions:

  P1: LAUNDERED and OBJECTIVE have similar verdict entropy (|diff| < 0.05)
      but different I (cluster_diversity: 1.0 vs ~5.5)
  P2: POPPERIAN and CONTESTED have similar verdict entropy (|diff| < 0.05)
      but different I (POPPERIAN higher)
  P3: LAUNDERED has lower R than OBJECTIVE (more vulnerable to adversarial probes)
  P4: CONTEXTUAL and SUBJECTIVE are similar in (C, K_sep) but differ in
      K_between (SUBJECTIVE more polarized → lower between_ctx)
  P5: 4D separability score > jury-only separability score
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

SIM_ID     = "SIM-LAUNDER-02D"
N_TRIALS   = 10_000
PANEL_SIZE = 7
N_OBS      = 100
N_OBS_CTX  = 100  # for context separation measurement


@dataclass
class Observer:
    obs_id: int
    context_id: int       # 0 = no context; 1, 2 = distinct contexts
    cluster_id: int       # epistemic independence proxy
    base_accuracy: float


@dataclass
class Claim:
    claim_type: str
    ground_truth: bool
    context_truths: Dict[int, bool] = field(default_factory=dict)
    observers: List[Observer] = field(default_factory=list)


def build_claim(claim_type: str, rng: np.random.Generator) -> Claim:
    if claim_type == "OBJECTIVE":
        # 10 clusters, uniform spread (10 observers each)
        obs = [Observer(i, 0, i // 10, rng.beta(7, 2)) for i in range(N_OBS)]
        return Claim("OBJECTIVE", True, {}, obs)

    elif claim_type == "CONTESTED":
        # 10 clusters, uniform spread, low accuracy
        obs = [Observer(i, 0, i // 10, rng.beta(3, 3)) for i in range(N_OBS)]
        return Claim("CONTESTED", True, {}, obs)

    elif claim_type == "CONTEXTUAL":
        # C1 observers in clusters 0-4, C2 observers in clusters 5-9
        ctx_truths = {1: True, 2: False}
        obs = []
        for i in range(N_OBS):
            ctx = 1 if i < N_OBS // 2 else 2
            cluster = (i % 5) if ctx == 1 else (5 + i % 5)
            obs.append(Observer(i, ctx, cluster, rng.beta(7, 2)))
        return Claim("CONTEXTUAL", True, ctx_truths, obs)

    elif claim_type == "SUBJECTIVE":
        # Value-driven: same cluster structure as CONTEXTUAL but 0.92 accuracy
        ctx_truths = {1: True, 2: False}
        obs = []
        for i in range(N_OBS):
            ctx = 1 if i < N_OBS // 2 else 2
            cluster = (i % 5) if ctx == 1 else (5 + i % 5)
            obs.append(Observer(i, ctx, cluster, 0.92))
        return Claim("SUBJECTIVE", True, ctx_truths, obs)

    elif claim_type == "LAUNDERED":
        # All observers in cluster 0 — correlated epistemic origin
        # High accuracy (looks like OBJECTIVE to jury) but no independence
        obs = [Observer(i, 0, 0, rng.beta(7, 2)) for i in range(N_OBS)]
        return Claim("LAUNDERED", True, {}, obs)

    elif claim_type == "POPPERIAN":
        # 20 clusters of 5 observers each — wide independence
        # Moderate accuracy (looks like CONTESTED to jury) but high diversity
        obs = [Observer(i, 0, i // 5, rng.beta(4, 4)) for i in range(N_OBS)]
        return Claim("POPPERIAN", True, {}, obs)

    else:
        raise ValueError(f"Unknown claim type: {claim_type}")


def vote(observer: Observer, claim: Claim, rng: np.random.Generator) -> int:
    if claim.context_truths:
        truth = claim.context_truths.get(observer.context_id, claim.ground_truth)
    else:
        truth = claim.ground_truth
    signal = 1.0 if truth else -1.0
    raw = signal * observer.base_accuracy * 2 + rng.normal(0, 1)
    return 1 if raw > 0 else 0


def vote_adversarial(ground_truth: bool, rng: np.random.Generator) -> int:
    """Adversarial voter: votes against ground_truth with P=0.90."""
    correct_vote = 1 if ground_truth else 0
    if rng.random() < 0.90:
        return 1 - correct_vote  # adversarial
    return correct_vote


def jury_trial(claim: Claim, panel_size: int,
               rng: np.random.Generator) -> Tuple[int, List[int], int]:
    """Returns (verdict, votes, n_distinct_clusters)."""
    panel_idx = rng.choice(len(claim.observers), size=panel_size, replace=False)
    panel = [claim.observers[p] for p in panel_idx]
    votes = [vote(p, claim, rng) for p in panel]
    verdict = 1 if sum(votes) > panel_size / 2 else 0
    n_clusters = len(set(p.cluster_id for p in panel))
    return verdict, votes, n_clusters


def adversarial_trial(claim: Claim, panel_size: int, n_adversarial: int,
                       rng: np.random.Generator) -> int:
    """
    Panel of panel_size; n_adversarial of them are adversarial voters.
    Returns 1 if True majority survives, 0 if adversarial reversal.
    """
    honest_count = panel_size - n_adversarial
    # Honest voters: drawn from claim observers
    honest_idx = rng.choice(len(claim.observers), size=honest_count, replace=False)
    honest_votes = [vote(claim.observers[i], claim, rng) for i in honest_idx]
    # Adversarial voters: vote against ground truth with P=0.9
    adv_votes = [vote_adversarial(claim.ground_truth, rng)
                 for _ in range(n_adversarial)]
    all_votes = honest_votes + adv_votes
    return 1 if sum(all_votes) > panel_size / 2 else 0


def context_separation(claim: Claim, rng: np.random.Generator,
                        n_obs_used: int = N_OBS_CTX) -> Tuple[float, float, float]:
    """Random sampling (fixed from 02B). Returns (within, between, sep)."""
    if n_obs_used >= len(claim.observers):
        obs = claim.observers
    else:
        indices = rng.choice(len(claim.observers), size=n_obs_used, replace=False)
        obs = [claim.observers[i] for i in indices]

    votes_by_ctx: Dict[int, List[int]] = {}
    for o in obs:
        v = vote(o, claim, rng)
        votes_by_ctx.setdefault(o.context_id, []).append(v)

    within_agreements = []
    for ctx_votes in votes_by_ctx.values():
        if len(ctx_votes) < 2:
            continue
        p = sum(ctx_votes) / len(ctx_votes)
        within_agreements.append(max(p, 1 - p))
    within_ctx = (sum(within_agreements) / len(within_agreements)
                  if within_agreements else 0.5)

    ctx_means = {c: sum(v) / len(v) for c, v in votes_by_ctx.items() if v}
    if len(ctx_means) < 2:
        return within_ctx, within_ctx, 0.0

    means = list(ctx_means.values())
    ctx_pairs = [(means[i], means[j])
                 for i in range(len(means))
                 for j in range(i + 1, len(means))]
    between_ctx = sum(1 - abs(a - b) for a, b in ctx_pairs) / len(ctx_pairs)
    return within_ctx, between_ctx, within_ctx - between_ctx


N_ADVERSARIAL = 2  # 2 of 7 panel members are adversarial


CLAIM_TYPES = ["OBJECTIVE", "CONTESTED", "CONTEXTUAL", "SUBJECTIVE",
               "LAUNDERED", "POPPERIAN"]


def main() -> None:
    rng = np.random.default_rng(42)
    print(f"[{SIM_ID}] {len(CLAIM_TYPES)} claim types × {N_TRIALS} trials",
          file=sys.stderr)

    profiles: dict = {}

    for ct in CLAIM_TYPES:
        claim = build_claim(ct, rng)
        verdicts, vote_fracs, cluster_divs = [], [], []
        adversarial_survivals = []
        within_list, between_list = [], []

        for _ in range(N_TRIALS):
            verdict, votes, n_clust = jury_trial(claim, PANEL_SIZE, rng)
            verdicts.append(verdict)
            vote_fracs.append(sum(votes) / len(votes))
            cluster_divs.append(n_clust)

            adv = adversarial_trial(claim, PANEL_SIZE, N_ADVERSARIAL, rng)
            adversarial_survivals.append(adv)

            w, b, _ = context_separation(claim, rng)
            within_list.append(w)
            between_list.append(b)

        p_true = sum(verdicts) / N_TRIALS
        h = -(p_true * math.log2(max(p_true, 1e-9))
              + (1 - p_true) * math.log2(max(1 - p_true, 1e-9)))
        mean_clust = sum(cluster_divs) / N_TRIALS
        mean_R = sum(adversarial_survivals) / N_TRIALS
        mean_w = sum(within_list) / N_TRIALS
        mean_b = sum(between_list) / N_TRIALS
        mean_sep = mean_w - mean_b

        profiles[ct] = {
            "C_verdict_entropy": round(h, 4),
            "C_p_verdict_true": round(p_true, 4),
            "I_mean_cluster_diversity": round(mean_clust, 4),
            "R_adversarial_survival": round(mean_R, 4),
            "K_within_ctx": round(mean_w, 4),
            "K_between_ctx": round(mean_b, 4),
            "K_ctx_sep": round(mean_sep, 4),
        }

        print(f"  {ct:12s}: C_H={h:.4f} I={mean_clust:.2f} "
              f"R={mean_R:.4f} K=({mean_w:.4f},{mean_b:.4f})",
              file=sys.stderr)

    # ── Pairwise separability ────────────────────────────────────────────────
    # Jury-only: (C_H, C_p) — 2D
    # Full 4D:   (C_H, I, R, K_within, K_between) — 5D
    def vec_jury(ct: str) -> np.ndarray:
        p = profiles[ct]
        return np.array([p["C_verdict_entropy"], p["C_p_verdict_true"]])

    def vec_4d(ct: str) -> np.ndarray:
        p = profiles[ct]
        return np.array([
            p["C_verdict_entropy"],
            p["I_mean_cluster_diversity"],
            p["R_adversarial_survival"],
            p["K_within_ctx"],
            p["K_between_ctx"],
        ])

    def normalize(vecs: List[np.ndarray]) -> List[np.ndarray]:
        arr = np.stack(vecs)
        mn, mx = arr.min(axis=0), arr.max(axis=0)
        rng2 = mx - mn
        rng2[rng2 == 0] = 1.0
        return [(v - mn) / rng2 for v in vecs]

    cts = CLAIM_TYPES
    jury_vecs = normalize([vec_jury(ct) for ct in cts])
    full_vecs  = normalize([vec_4d(ct)  for ct in cts])

    def mean_pairwise_dist(vecs: List[np.ndarray]) -> float:
        dists = []
        for i in range(len(vecs)):
            for j in range(i + 1, len(vecs)):
                dists.append(float(np.linalg.norm(vecs[i] - vecs[j])))
        return sum(dists) / len(dists) if dists else 0.0

    jury_sep = mean_pairwise_dist(jury_vecs)
    full_sep  = mean_pairwise_dist(full_vecs)

    print(f"\nPairwise separability (normalized):", file=sys.stderr)
    print(f"  Jury-only (C): {jury_sep:.4f}", file=sys.stderr)
    print(f"  Full 4D (C+I+R+K): {full_sep:.4f}", file=sys.stderr)

    # ── Prediction verdicts ─────────────────────────────────────────────────
    obj = profiles["OBJECTIVE"]
    lnd = profiles["LAUNDERED"]
    cst = profiles["CONTESTED"]
    pop = profiles["POPPERIAN"]
    ctx = profiles["CONTEXTUAL"]
    sbj = profiles["SUBJECTIVE"]

    # P1: LAUNDERED ≈ OBJECTIVE by jury (C), different by I
    p1_jury_same = abs(lnd["C_verdict_entropy"] - obj["C_verdict_entropy"]) < 0.05
    p1_I_diff    = lnd["I_mean_cluster_diversity"] < obj["I_mean_cluster_diversity"] - 0.5
    p1_v = "CONFIRMED" if p1_jury_same and p1_I_diff else "REFUTED"
    print(f"\nP1 LAUNDERED≈OBJECTIVE by jury: H_diff="
          f"{abs(lnd['C_verdict_entropy']-obj['C_verdict_entropy']):.4f} "
          f"I_diff={obj['I_mean_cluster_diversity']-lnd['I_mean_cluster_diversity']:.2f} [{p1_v}]",
          file=sys.stderr)

    # P2: POPPERIAN ≈ CONTESTED by jury, different by I
    p2_jury_same = abs(pop["C_verdict_entropy"] - cst["C_verdict_entropy"]) < 0.15
    p2_I_diff    = pop["I_mean_cluster_diversity"] > cst["I_mean_cluster_diversity"] + 0.3
    p2_v = "CONFIRMED" if p2_jury_same and p2_I_diff else "REFUTED"
    print(f"P2 POPPERIAN≈CONTESTED by jury: H_diff="
          f"{abs(pop['C_verdict_entropy']-cst['C_verdict_entropy']):.4f} "
          f"I_diff={pop['I_mean_cluster_diversity']-cst['I_mean_cluster_diversity']:.2f} [{p2_v}]",
          file=sys.stderr)

    # P3: LAUNDERED has lower R than OBJECTIVE
    p3_v = "CONFIRMED" if lnd["R_adversarial_survival"] < obj["R_adversarial_survival"] - 0.02 else "REFUTED"
    print(f"P3 LAUNDERED R={lnd['R_adversarial_survival']:.4f} vs "
          f"OBJECTIVE R={obj['R_adversarial_survival']:.4f} [{p3_v}]", file=sys.stderr)

    # P4: CONTEXTUAL and SUBJECTIVE differ in K_between (SUBJECTIVE more polarized)
    between_gap = ctx["K_between_ctx"] - sbj["K_between_ctx"]
    p4_v = "CONFIRMED" if between_gap > 0.05 else "REFUTED"
    print(f"P4 CONTEXTUAL between={ctx['K_between_ctx']:.4f} vs "
          f"SUBJECTIVE between={sbj['K_between_ctx']:.4f} gap={between_gap:.4f} [{p4_v}]",
          file=sys.stderr)

    # P5: 4D separability > jury-only
    p5_v = "CONFIRMED" if full_sep > jury_sep + 0.05 else "REFUTED"
    print(f"P5 4D sep={full_sep:.4f} > jury sep={jury_sep:.4f} [{p5_v}]",
          file=sys.stderr)

    # ── Summary table ────────────────────────────────────────────────────────
    print(f"\n{'Claim type':12s} {'C_H':>6} {'I_div':>6} {'R_surv':>7} "
          f"{'K_within':>9} {'K_between':>10} {'K_sep':>7}", file=sys.stderr)
    for ct in CLAIM_TYPES:
        p = profiles[ct]
        print(f"  {ct:10s} {p['C_verdict_entropy']:6.4f} "
              f"{p['I_mean_cluster_diversity']:6.2f} "
              f"{p['R_adversarial_survival']:7.4f} "
              f"{p['K_within_ctx']:9.4f} "
              f"{p['K_between_ctx']:10.4f} "
              f"{p['K_ctx_sep']:7.4f}", file=sys.stderr)

    result = {
        "sim_id": SIM_ID,
        "description": "Four-dimensional epistemic profile: (C, I, R, K) for 6 claim types",
        "methodological_note": (
            "C=consensus, I=cluster_diversity (IEC proxy), "
            "R=adversarial survival rate, K=(within_ctx, between_ctx). "
            "All are model results, not empirical ILC measurements."
        ),
        "profiles": profiles,
        "separability": {
            "jury_only_C_2D": round(jury_sep, 4),
            "full_4D_CIRK":   round(full_sep, 4),
        },
        "predictions": {
            "P1": "LAUNDERED ≈ OBJECTIVE by jury (H diff < 0.05) but different I",
            "P2": "POPPERIAN ≈ CONTESTED by jury (H diff < 0.15) but different I",
            "P3": "LAUNDERED R < OBJECTIVE R (more adversarially vulnerable)",
            "P4": "CONTEXTUAL and SUBJECTIVE differ in K_between (SUBJECTIVE more polarized)",
            "P5": "4D separability > jury-only separability (+0.05)",
        },
        "prediction_verdicts": {
            "P1": p1_v, "P2": p2_v, "P3": p3_v, "P4": p4_v, "P5": p5_v,
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
