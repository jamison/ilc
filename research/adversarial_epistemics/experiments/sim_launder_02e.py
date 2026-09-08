"""
SIM-LAUNDER-02E — Information Preservation: Binary vs Context-Preserving Architecture
======================================================================================

Astra's central claim: a binary jury destroys information that a context-preserving
graph can retain. This experiment makes that comparison formal and measurable.

Two architectures:

  Binary architecture:
    observations → jury → TRUE/FALSE
    Per-trial representation: (vote_fraction,)  [scalar in {0/7, 1/7, ..., 7/7}]

  Context-preserving architecture:
    observations → context/provenance graph → jury distributions
    Per-trial representation: (within_ctx, between_ctx, cluster_diversity)  [3D]

For each architecture, fit a centroid-nearest-neighbor classifier over 4 claim types
and report accuracy. A higher-accuracy classifier means more information is preserved.

Also test: the Astra "unknown" hierarchy — can we rank claim types by how much their
epistemic status is unknown/resolvable?

  INSUFFICIENT_EVIDENCE → CONTESTED → CONTEXT_DEPENDENT → SUBJECTIVE/VALUE_DEPENDENT

Formal separability metric: for each pair of claim types, report:

  jury_separability(A, B) = |mean_vote_fraction(A) - mean_vote_fraction(B)|
  graph_separability(A, B) = Euclidean distance between (within, between, I) centroids

The prediction: graph representation preserves more pairwise separability for claim
pairs that jury collapses — specifically CONTEXTUAL vs SUBJECTIVE, which jury
cannot distinguish (both H≈1.0, P≈0.5) but graph can (different K_between).

Six claim types (same observer model as 02D):

  OBJECTIVE, CONTESTED, CONTEXTUAL, SUBJECTIVE, LAUNDERED, POPPERIAN

Predictions:

  P1: Graph classifier accuracy > jury classifier accuracy overall
  P2: CONTEXTUAL vs SUBJECTIVE: graph_sep >> jury_sep (jury collapses; graph sees K_between)
  P3: LAUNDERED vs OBJECTIVE: graph_sep >> jury_sep (jury collapses; graph sees I)
  P4: POPPERIAN vs CONTESTED: graph_sep > jury_sep (graph sees I and R)
  P5: Information loss at jury stage: for CONTEXTUAL, most within/between structure
      is destroyed in the binary vote but preserved in per-trial graph metrics
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

SIM_ID     = "SIM-LAUNDER-02E"
N_TRIALS   = 5_000   # per claim type (lower than 02D since we store per-trial vectors)
PANEL_SIZE = 7
N_OBS      = 100
N_OBS_CTX  = 100


@dataclass
class Observer:
    obs_id: int
    context_id: int
    cluster_id: int
    base_accuracy: float


@dataclass
class Claim:
    claim_type: str
    ground_truth: bool
    context_truths: Dict[int, bool] = field(default_factory=dict)
    observers: List[Observer] = field(default_factory=list)


def build_claim(claim_type: str, rng: np.random.Generator) -> Claim:
    if claim_type == "OBJECTIVE":
        obs = [Observer(i, 0, i // 10, rng.beta(7, 2)) for i in range(N_OBS)]
        return Claim("OBJECTIVE", True, {}, obs)
    elif claim_type == "CONTESTED":
        obs = [Observer(i, 0, i // 10, rng.beta(3, 3)) for i in range(N_OBS)]
        return Claim("CONTESTED", True, {}, obs)
    elif claim_type == "CONTEXTUAL":
        ctx_truths = {1: True, 2: False}
        obs = []
        for i in range(N_OBS):
            ctx = 1 if i < N_OBS // 2 else 2
            cluster = (i % 5) if ctx == 1 else (5 + i % 5)
            obs.append(Observer(i, ctx, cluster, rng.beta(7, 2)))
        return Claim("CONTEXTUAL", True, ctx_truths, obs)
    elif claim_type == "SUBJECTIVE":
        ctx_truths = {1: True, 2: False}
        obs = []
        for i in range(N_OBS):
            ctx = 1 if i < N_OBS // 2 else 2
            cluster = (i % 5) if ctx == 1 else (5 + i % 5)
            obs.append(Observer(i, ctx, cluster, 0.92))
        return Claim("SUBJECTIVE", True, ctx_truths, obs)
    elif claim_type == "LAUNDERED":
        obs = [Observer(i, 0, 0, rng.beta(7, 2)) for i in range(N_OBS)]
        return Claim("LAUNDERED", True, {}, obs)
    elif claim_type == "POPPERIAN":
        obs = [Observer(i, 0, i // 5, rng.beta(4, 4)) for i in range(N_OBS)]
        return Claim("POPPERIAN", True, {}, obs)
    else:
        raise ValueError(f"Unknown: {claim_type}")


def vote(observer: Observer, claim: Claim, rng: np.random.Generator) -> int:
    if claim.context_truths:
        truth = claim.context_truths.get(observer.context_id, claim.ground_truth)
    else:
        truth = claim.ground_truth
    signal = 1.0 if truth else -1.0
    raw = signal * observer.base_accuracy * 2 + rng.normal(0, 1)
    return 1 if raw > 0 else 0


def one_trial(claim: Claim, rng: np.random.Generator) -> Tuple[float, float, float, float]:
    """
    Returns (vote_fraction, within_ctx, between_ctx, cluster_diversity).
    vote_fraction: the binary architecture signal
    (within_ctx, between_ctx, cluster_diversity): the graph architecture signal
    """
    # Jury vote
    panel_idx = rng.choice(len(claim.observers), size=PANEL_SIZE, replace=False)
    panel = [claim.observers[p] for p in panel_idx]
    votes = [vote(p, claim, rng) for p in panel]
    vote_frac = sum(votes) / len(votes)
    n_clusters = len(set(p.cluster_id for p in panel)) / PANEL_SIZE  # normalized

    # Context structure (all observers, random sample if large)
    if N_OBS_CTX >= len(claim.observers):
        obs = claim.observers
    else:
        idx = rng.choice(len(claim.observers), size=N_OBS_CTX, replace=False)
        obs = [claim.observers[i] for i in idx]

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
        between_ctx = within_ctx
    else:
        means = list(ctx_means.values())
        ctx_pairs = [(means[i], means[j])
                     for i in range(len(means))
                     for j in range(i + 1, len(means))]
        between_ctx = sum(1 - abs(a - b) for a, b in ctx_pairs) / len(ctx_pairs)

    return vote_frac, within_ctx, between_ctx, n_clusters


CLAIM_TYPES = ["OBJECTIVE", "CONTESTED", "CONTEXTUAL", "SUBJECTIVE",
               "LAUNDERED", "POPPERIAN"]


def centroid_accuracy(vectors_by_ct: Dict[str, np.ndarray]) -> float:
    """
    Centroid nearest-neighbor classifier.
    Training = full dataset (leave-one-out would be better but this is sufficient for demonstration).
    Returns overall accuracy.
    """
    centroids = {ct: vecs.mean(axis=0) for ct, vecs in vectors_by_ct.items()}
    cts = list(vectors_by_ct.keys())
    correct = 0
    total = 0
    for true_ct, vecs in vectors_by_ct.items():
        for v in vecs:
            dists = {ct: np.linalg.norm(v - centroids[ct]) for ct in cts}
            pred_ct = min(dists, key=dists.get)
            if pred_ct == true_ct:
                correct += 1
            total += 1
    return correct / total


def pairwise_centroid_dist(ct_a: str, ct_b: str,
                            centroids: Dict[str, np.ndarray]) -> float:
    return float(np.linalg.norm(centroids[ct_a] - centroids[ct_b]))


def main() -> None:
    rng = np.random.default_rng(42)
    print(f"[{SIM_ID}] {len(CLAIM_TYPES)} claim types × {N_TRIALS} trials",
          file=sys.stderr)

    # Collect per-trial data
    jury_vecs_by_ct:  Dict[str, List[List[float]]] = {ct: [] for ct in CLAIM_TYPES}
    graph_vecs_by_ct: Dict[str, List[List[float]]] = {ct: [] for ct in CLAIM_TYPES}

    for ct in CLAIM_TYPES:
        claim = build_claim(ct, rng)
        for _ in range(N_TRIALS):
            vf, w, b, nc = one_trial(claim, rng)
            jury_vecs_by_ct[ct].append([vf])
            graph_vecs_by_ct[ct].append([w, b, nc])
        print(f"  {ct} done", file=sys.stderr)

    # Convert to numpy
    jury_np  = {ct: np.array(v) for ct, v in jury_vecs_by_ct.items()}
    graph_np = {ct: np.array(v) for ct, v in graph_vecs_by_ct.items()}

    # Normalise each space to [0,1] per dimension
    def normalise_space(vecs_by_ct: Dict[str, np.ndarray]) -> Dict[str, np.ndarray]:
        all_v = np.vstack(list(vecs_by_ct.values()))
        mn, mx = all_v.min(axis=0), all_v.max(axis=0)
        rng2 = mx - mn
        rng2[rng2 == 0] = 1.0
        return {ct: (v - mn) / rng2 for ct, v in vecs_by_ct.items()}

    jury_norm  = normalise_space(jury_np)
    graph_norm = normalise_space(graph_np)

    # Centroid classifier accuracy
    jury_acc  = centroid_accuracy(jury_norm)
    graph_acc = centroid_accuracy(graph_norm)
    print(f"\nCentroid classifier accuracy:", file=sys.stderr)
    print(f"  Jury  (vote_fraction only):           {jury_acc:.4f}", file=sys.stderr)
    print(f"  Graph (within, between, cluster_div): {graph_acc:.4f}", file=sys.stderr)

    # Per-class mean representations (centroids)
    jury_centroids  = {ct: jury_norm[ct].mean(axis=0) for ct in CLAIM_TYPES}
    graph_centroids = {ct: graph_norm[ct].mean(axis=0) for ct in CLAIM_TYPES}

    print(f"\n{'Pair':35s} {'jury_sep':>9} {'graph_sep':>10}", file=sys.stderr)
    pairwise: dict = {}
    for i, ct_a in enumerate(CLAIM_TYPES):
        for ct_b in CLAIM_TYPES[i + 1:]:
            pair_key = f"{ct_a} vs {ct_b}"
            js = pairwise_centroid_dist(ct_a, ct_b, jury_centroids)
            gs = pairwise_centroid_dist(ct_a, ct_b, graph_centroids)
            pairwise[pair_key] = {
                "jury_centroid_dist": round(js, 4),
                "graph_centroid_dist": round(gs, 4),
                "graph_advantage": round(gs - js, 4),
            }
            marker = " ***" if gs - js > 0.10 else ""
            print(f"  {pair_key:35s} {js:9.4f} {gs:10.4f}{marker}", file=sys.stderr)

    # Per-claim type mean representation values (raw, not normalized)
    raw_means: dict = {}
    for ct in CLAIM_TYPES:
        vf_arr = jury_np[ct][:, 0]
        w_arr  = graph_np[ct][:, 0]
        b_arr  = graph_np[ct][:, 1]
        nc_arr = graph_np[ct][:, 2]
        raw_means[ct] = {
            "mean_vote_fraction": round(float(vf_arr.mean()), 4),
            "mean_within_ctx":    round(float(w_arr.mean()), 4),
            "mean_between_ctx":   round(float(b_arr.mean()), 4),
            "mean_cluster_diversity_norm": round(float(nc_arr.mean()), 4),
        }

    print(f"\n{'Claim type':12s} {'vote_frac':>10} {'within':>8} {'between':>9} {'clust_div':>10}",
          file=sys.stderr)
    for ct in CLAIM_TYPES:
        r = raw_means[ct]
        print(f"  {ct:10s} {r['mean_vote_fraction']:10.4f} "
              f"{r['mean_within_ctx']:8.4f} {r['mean_between_ctx']:9.4f} "
              f"{r['mean_cluster_diversity_norm']:10.4f}", file=sys.stderr)

    # ── Prediction verdicts ─────────────────────────────────────────────────
    p1_v = "CONFIRMED" if graph_acc > jury_acc + 0.05 else "REFUTED"
    print(f"\nP1 graph_acc={graph_acc:.4f} > jury_acc={jury_acc:.4f} [{p1_v}]",
          file=sys.stderr)

    ctx_subj = pairwise["CONTEXTUAL vs SUBJECTIVE"]
    p2_v = ("CONFIRMED"
            if ctx_subj["graph_centroid_dist"] > ctx_subj["jury_centroid_dist"] + 0.05
            else "REFUTED")
    print(f"P2 CONTEXTUAL vs SUBJECTIVE: jury={ctx_subj['jury_centroid_dist']:.4f} "
          f"graph={ctx_subj['graph_centroid_dist']:.4f} [{p2_v}]", file=sys.stderr)

    lnd_obj = pairwise["OBJECTIVE vs LAUNDERED"]
    p3_v = ("CONFIRMED"
            if lnd_obj["graph_centroid_dist"] > lnd_obj["jury_centroid_dist"] + 0.05
            else "REFUTED")
    print(f"P3 LAUNDERED vs OBJECTIVE: jury={lnd_obj['jury_centroid_dist']:.4f} "
          f"graph={lnd_obj['graph_centroid_dist']:.4f} [{p3_v}]", file=sys.stderr)

    pop_cst = pairwise["CONTESTED vs POPPERIAN"]
    p4_v = ("CONFIRMED"
            if pop_cst["graph_centroid_dist"] > pop_cst["jury_centroid_dist"] + 0.02
            else "REFUTED")
    print(f"P4 POPPERIAN vs CONTESTED: jury={pop_cst['jury_centroid_dist']:.4f} "
          f"graph={pop_cst['graph_centroid_dist']:.4f} [{p4_v}]", file=sys.stderr)

    # P5: CONTEXTUAL information loss — within/between variance in graph vs scalar variance in jury
    ctx_j_var = float(jury_np["CONTEXTUAL"][:, 0].var())
    ctx_g_var = float(graph_np["CONTEXTUAL"].var(axis=0).mean())
    p5_v = "CONFIRMED" if ctx_g_var > ctx_j_var else "REFUTED"
    print(f"P5 CONTEXTUAL: graph_var={ctx_g_var:.6f} vs jury_var={ctx_j_var:.6f} [{p5_v}]",
          file=sys.stderr)

    result = {
        "sim_id": SIM_ID,
        "description": "Architecture comparison: binary jury vs context-preserving graph representation",
        "methodological_note": (
            "Centroid-nearest-neighbor classifier on normalized per-trial representations. "
            "Jury space: (vote_fraction,). Graph space: (within_ctx, between_ctx, cluster_diversity). "
            "All claim types use same observer model as 02D."
        ),
        "classifier_accuracy": {
            "jury_vote_fraction_only": round(jury_acc, 4),
            "graph_3D_representation": round(graph_acc, 4),
        },
        "raw_means_by_claim_type": raw_means,
        "pairwise_centroid_distances": pairwise,
        "predictions": {
            "P1": "Graph classifier accuracy > jury accuracy (+0.05)",
            "P2": "CONTEXTUAL vs SUBJECTIVE: graph_sep >> jury_sep (+0.05)",
            "P3": "LAUNDERED vs OBJECTIVE: graph_sep >> jury_sep (+0.05)",
            "P4": "POPPERIAN vs CONTESTED: graph_sep > jury_sep (+0.02)",
            "P5": "CONTEXTUAL graph representation has higher variance than scalar vote_fraction",
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
