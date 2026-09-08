"""
SIM-LAUNDER-02H — Observer → Graph → Jury: Staged Information Conservation
===========================================================================

Astra's request: formally measure information loss across compression stages.
Observer structure → graph metrics → jury verdict.

Three stages:

  Stage 0 — Observer (4D):
    (vf_ctx_A, vf_ctx_B, n_clusters_norm, within_cluster_agreement)
    Full panel-level detail. Captures context disaggregation and cluster
    structure before any aggregation.

  Stage 1 — Graph (3D):
    (within_ctx, between_ctx, cluster_diversity_norm)
    Aggregated from observer layer. Captures context structure and
    provenance diversity. Loses per-cluster vote detail.

  Stage 2 — Jury (1D):
    (vote_fraction,)
    Single scalar: fraction of panel votes for TRUE.
    Loses all context and cluster structure.

Six claim types (same observer model as 02D/02E):
  OBJECTIVE, CONTESTED, CONTEXTUAL, SUBJECTIVE, LAUNDERED, POPPERIAN

For each pair of claim types, compute centroid L2 distance at each stage.
Also compute rank correlation of pairwise separations across stages.

Formal compression loss metric:
  compression_loss(stage) = 1 - rank_corr(obs_sep, stage_sep)

Where rank_corr is Spearman rank correlation over all 15 claim-type pairs.

Predictions:

  P1: Jury accuracy < Graph accuracy (replicate 02E finding — sanity check)
  P2: OBJECTIVE vs LAUNDERED: graph_sep >> 0 and jury_sep ≈ 0
      Cluster structure in observer layer survives to graph, not to jury.
  P3: CONTEXTUAL vs SUBJECTIVE: graph_sep > 0 and jury_sep ≈ 0
      Context separation survives to graph (within, between asymmetry).
  P4: Rank correlation(obs, graph) > rank correlation(obs, jury)
      Graph preserves the pairwise ordering of claim types better than jury.
  P5: At least 3 pairs have jury_sep < 0.05 but graph_sep > 0.10
      (i.e., jury collapses distinctions that graph preserves for ≥3 pairs)
"""

from __future__ import annotations

import hashlib
import json
import sys
import os
from datetime import datetime, timezone
from dataclasses import dataclass, field
from typing import Dict, List, Tuple

import numpy as np

SIM_ID     = "SIM-LAUNDER-02H"
N_TRIALS   = 5_000   # per claim type
PANEL_SIZE = 7
N_OBS      = 100
N_OBS_CTX  = 100

CLAIM_TYPES = ["OBJECTIVE", "CONTESTED", "CONTEXTUAL", "SUBJECTIVE",
               "LAUNDERED", "POPPERIAN"]


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
    """Same observer model as 02D/02E for cross-experiment consistency."""
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
        raise ValueError(f"Unknown claim type: {claim_type}")


def vote_fn(observer: Observer, claim: Claim, rng: np.random.Generator) -> int:
    if claim.context_truths:
        truth = claim.context_truths.get(observer.context_id, claim.ground_truth)
    else:
        truth = claim.ground_truth
    signal = 1.0 if truth else -1.0
    raw = signal * observer.base_accuracy * 2 + rng.normal(0, 1)
    return 1 if raw > 0 else 0


def one_trial(claim: Claim, rng: np.random.Generator) -> Tuple[
        np.ndarray, np.ndarray, np.ndarray]:
    """
    Returns (obs_features, graph_features, jury_features) for one trial.

    Observer features (4D):
      [vf_ctx_A, vf_ctx_B, n_clusters_norm, within_cluster_agreement]

    Graph features (3D):
      [within_ctx, between_ctx, cluster_diversity_norm]

    Jury features (1D):
      [vote_fraction]
    """
    # ── Panel vote ──────────────────────────────────────────────────────────
    panel_idx = rng.choice(len(claim.observers), size=PANEL_SIZE, replace=False)
    panel = [claim.observers[p] for p in panel_idx]
    votes_panel = [vote_fn(p, claim, rng) for p in panel]
    vote_frac = sum(votes_panel) / len(votes_panel)

    # Cluster diversity from panel
    n_clusters_in_panel = len(set(p.cluster_id for p in panel))
    n_clusters_norm = n_clusters_in_panel / PANEL_SIZE

    # ── Full observer sample for context structure ───────────────────────────
    if N_OBS_CTX >= len(claim.observers):
        obs_sample = claim.observers
    else:
        idx = rng.choice(len(claim.observers), size=N_OBS_CTX, replace=False)
        obs_sample = [claim.observers[i] for i in idx]

    votes_by_ctx: Dict[int, List[int]] = {}
    votes_by_cluster: Dict[int, List[int]] = {}
    for o in obs_sample:
        v = vote_fn(o, claim, rng)
        votes_by_ctx.setdefault(o.context_id, []).append(v)
        votes_by_cluster.setdefault(o.cluster_id, []).append(v)

    # ── Observer-layer features ──────────────────────────────────────────────
    ctx_keys = sorted(votes_by_ctx.keys())

    # Per-context vote fractions (contexts A and B)
    vf_ctx_A = (sum(votes_by_ctx[ctx_keys[0]]) / len(votes_by_ctx[ctx_keys[0]])
                if len(ctx_keys) > 0 else 0.5)
    vf_ctx_B = (sum(votes_by_ctx[ctx_keys[1]]) / len(votes_by_ctx[ctx_keys[1]])
                if len(ctx_keys) > 1 else vf_ctx_A)

    # Within-cluster agreement: mean per-cluster max(p, 1-p) across clusters
    cluster_agreements = []
    for cl_votes in votes_by_cluster.values():
        if len(cl_votes) < 2:
            continue
        p = sum(cl_votes) / len(cl_votes)
        cluster_agreements.append(max(p, 1 - p))
    within_cluster_agreement = (sum(cluster_agreements) / len(cluster_agreements)
                                 if cluster_agreements else 0.5)

    obs_features = np.array([vf_ctx_A, vf_ctx_B, n_clusters_norm, within_cluster_agreement])

    # ── Graph-layer features ─────────────────────────────────────────────────
    # within_ctx: mean agreement within each context group
    within_agreements = []
    for ctx_votes in votes_by_ctx.values():
        if len(ctx_votes) < 2:
            continue
        p = sum(ctx_votes) / len(ctx_votes)
        within_agreements.append(max(p, 1 - p))
    within_ctx = (sum(within_agreements) / len(within_agreements)
                  if within_agreements else 0.5)

    # between_ctx: cross-context agreement (high = agree, low = disagree)
    ctx_means = {c: sum(v) / len(v) for c, v in votes_by_ctx.items() if v}
    if len(ctx_means) < 2:
        between_ctx = within_ctx
    else:
        means = list(ctx_means.values())
        ctx_pairs = [(means[i], means[j])
                     for i in range(len(means))
                     for j in range(i + 1, len(means))]
        between_ctx = sum(1 - abs(a - b) for a, b in ctx_pairs) / len(ctx_pairs)

    graph_features = np.array([within_ctx, between_ctx, n_clusters_norm])

    # ── Jury-layer features ──────────────────────────────────────────────────
    jury_features = np.array([vote_frac])

    return obs_features, graph_features, jury_features


def centroid_dist(arr_a: np.ndarray, arr_b: np.ndarray) -> float:
    """L2 distance between centroids of two sample arrays."""
    return float(np.linalg.norm(arr_a.mean(axis=0) - arr_b.mean(axis=0)))


def spearman_rank_corr(x: List[float], y: List[float]) -> float:
    """Spearman rank correlation (manual implementation, no scipy dependency)."""
    n = len(x)
    if n < 2:
        return 0.0
    rx = np.argsort(np.argsort(x)).astype(float) + 1
    ry = np.argsort(np.argsort(y)).astype(float) + 1
    d2 = np.sum((rx - ry) ** 2)
    return float(1 - 6 * d2 / (n * (n * n - 1)))


def centroid_accuracy(vecs_by_ct: Dict[str, np.ndarray]) -> float:
    """Centroid nearest-neighbor classifier accuracy."""
    centroids = {ct: v.mean(axis=0) for ct, v in vecs_by_ct.items()}
    cts = list(vecs_by_ct.keys())
    correct = total = 0
    for true_ct, vecs in vecs_by_ct.items():
        for v in vecs:
            dists = {ct: np.linalg.norm(v - centroids[ct]) for ct in cts}
            pred_ct = min(dists, key=dists.get)
            if pred_ct == true_ct:
                correct += 1
            total += 1
    return correct / total


def normalise_space(vecs_by_ct: Dict[str, np.ndarray]) -> Dict[str, np.ndarray]:
    all_v = np.vstack(list(vecs_by_ct.values()))
    mn, mx = all_v.min(axis=0), all_v.max(axis=0)
    rng2 = mx - mn
    rng2[rng2 == 0] = 1.0
    return {ct: (v - mn) / rng2 for ct, v in vecs_by_ct.items()}


def main() -> None:
    rng = np.random.default_rng(42)
    print(f"[{SIM_ID}] {len(CLAIM_TYPES)} claim types × {N_TRIALS} trials = "
          f"{len(CLAIM_TYPES) * N_TRIALS} total trials", file=sys.stderr)

    obs_by_ct:   Dict[str, List] = {ct: [] for ct in CLAIM_TYPES}
    graph_by_ct: Dict[str, List] = {ct: [] for ct in CLAIM_TYPES}
    jury_by_ct:  Dict[str, List] = {ct: [] for ct in CLAIM_TYPES}

    for ct in CLAIM_TYPES:
        claim = build_claim(ct, rng)
        for _ in range(N_TRIALS):
            of, gf, jf = one_trial(claim, rng)
            obs_by_ct[ct].append(of)
            graph_by_ct[ct].append(gf)
            jury_by_ct[ct].append(jf)
        print(f"  {ct} done ({N_TRIALS} trials)", file=sys.stderr)

    obs_np   = {ct: np.array(v) for ct, v in obs_by_ct.items()}
    graph_np = {ct: np.array(v) for ct, v in graph_by_ct.items()}
    jury_np  = {ct: np.array(v) for ct, v in jury_by_ct.items()}

    # Normalise each space independently before computing centroid distances
    obs_norm   = normalise_space(obs_np)
    graph_norm = normalise_space(graph_np)
    jury_norm  = normalise_space(jury_np)

    # Classifier accuracy (sanity check vs 02E)
    jury_acc  = centroid_accuracy(jury_norm)
    graph_acc = centroid_accuracy(graph_norm)
    obs_acc   = centroid_accuracy(obs_norm)

    print(f"\nCentroid classifier accuracy (normalised spaces):", file=sys.stderr)
    print(f"  Observer (4D): {obs_acc:.4f}", file=sys.stderr)
    print(f"  Graph    (3D): {graph_acc:.4f}", file=sys.stderr)
    print(f"  Jury     (1D): {jury_acc:.4f}", file=sys.stderr)

    # Pairwise centroid distances at each stage
    pairs = [(ct_a, ct_b) for i, ct_a in enumerate(CLAIM_TYPES)
             for ct_b in CLAIM_TYPES[i + 1:]]

    obs_seps   = []
    graph_seps = []
    jury_seps  = []
    pair_keys  = []

    print(f"\n{'Pair':<38} {'Obs':>8} {'Graph':>8} {'Jury':>8} {'G/O':>8} {'J/O':>8}",
          file=sys.stderr)

    pairwise: dict = {}
    for ct_a, ct_b in pairs:
        key = f"{ct_a} vs {ct_b}"
        pair_keys.append(key)

        os_ = centroid_dist(obs_norm[ct_a], obs_norm[ct_b])
        gs_ = centroid_dist(graph_norm[ct_a], graph_norm[ct_b])
        js_ = centroid_dist(jury_norm[ct_a], jury_norm[ct_b])

        obs_seps.append(os_)
        graph_seps.append(gs_)
        jury_seps.append(js_)

        g_over_o = gs_ / os_ if os_ > 1e-9 else 0.0
        j_over_o = js_ / os_ if os_ > 1e-9 else 0.0

        marker = " ***" if gs_ > 0.10 and js_ < 0.05 else ""
        print(f"  {key:<36} {os_:8.4f} {gs_:8.4f} {js_:8.4f} "
              f"{g_over_o:7.2f}x {j_over_o:7.2f}x{marker}", file=sys.stderr)

        pairwise[key] = {
            "obs_sep":    round(os_, 4),
            "graph_sep":  round(gs_, 4),
            "jury_sep":   round(js_, 4),
            "graph_over_obs": round(g_over_o, 3),
            "jury_over_obs":  round(j_over_o, 3),
        }

    # Rank correlations
    rc_graph_obs = spearman_rank_corr(obs_seps, graph_seps)
    rc_jury_obs  = spearman_rank_corr(obs_seps, jury_seps)

    print(f"\nRank correlations with observer stage:", file=sys.stderr)
    print(f"  Graph vs Observer: {rc_graph_obs:.4f}", file=sys.stderr)
    print(f"  Jury  vs Observer: {rc_jury_obs:.4f}", file=sys.stderr)

    # Mean preservation
    mean_g_ratio = float(np.mean([pairwise[k]["graph_over_obs"] for k in pair_keys]))
    mean_j_ratio = float(np.mean([pairwise[k]["jury_over_obs"]  for k in pair_keys]))

    print(f"\nMean preservation ratios:", file=sys.stderr)
    print(f"  Graph: {mean_g_ratio:.3f}x (vs observer centroid distance)", file=sys.stderr)
    print(f"  Jury:  {mean_j_ratio:.3f}x", file=sys.stderr)

    # Count pairs where jury collapses but graph preserves
    collapsed = [k for k in pair_keys
                 if pairwise[k]["jury_sep"] < 0.05 and pairwise[k]["graph_sep"] > 0.10]
    print(f"\nPairs where jury collapses (jury_sep<0.05) but graph preserves (graph_sep>0.10): "
          f"{len(collapsed)}", file=sys.stderr)
    for k in collapsed:
        print(f"  {k}: graph={pairwise[k]['graph_sep']:.4f}, jury={pairwise[k]['jury_sep']:.4f}",
              file=sys.stderr)

    # Observer-stage mean feature values per claim type
    obs_centroids: dict = {}
    for ct in CLAIM_TYPES:
        c = obs_np[ct].mean(axis=0)
        obs_centroids[ct] = {
            "vf_ctx_A":               round(float(c[0]), 4),
            "vf_ctx_B":               round(float(c[1]), 4),
            "n_clusters_norm":        round(float(c[2]), 4),
            "within_cluster_agreement": round(float(c[3]), 4),
        }

    print(f"\nObserver-stage centroids:", file=sys.stderr)
    print(f"  {'Claim':12s} {'vf_A':>8} {'vf_B':>8} {'n_clust':>8} {'wcl_agr':>8}",
          file=sys.stderr)
    for ct in CLAIM_TYPES:
        c = obs_centroids[ct]
        print(f"  {ct:12s} {c['vf_ctx_A']:8.4f} {c['vf_ctx_B']:8.4f} "
              f"{c['n_clusters_norm']:8.4f} {c['within_cluster_agreement']:8.4f}",
              file=sys.stderr)

    # ── Prediction verdicts ──────────────────────────────────────────────────
    print(f"\nPrediction verdicts:", file=sys.stderr)

    # P1: Jury accuracy < Graph accuracy (sanity check)
    p1_pass = graph_acc > jury_acc + 0.05
    p1_v = "CONFIRMED" if p1_pass else "REFUTED"
    print(f"P1 graph_acc={graph_acc:.4f} > jury_acc={jury_acc:.4f}+0.05 [{p1_v}]",
          file=sys.stderr)

    # P2: OBJECTIVE vs LAUNDERED: graph_sep >> 0, jury_sep ≈ 0
    ol = pairwise["OBJECTIVE vs LAUNDERED"]
    p2_pass = ol["graph_sep"] > 0.10 and ol["jury_sep"] < 0.05
    p2_v = "CONFIRMED" if p2_pass else "REFUTED"
    print(f"P2 OBJECTIVE vs LAUNDERED: graph={ol['graph_sep']:.4f} jury={ol['jury_sep']:.4f} [{p2_v}]",
          file=sys.stderr)

    # P3: CONTEXTUAL vs SUBJECTIVE: graph_sep > 0.05, jury_sep < 0.05
    cs = pairwise["CONTEXTUAL vs SUBJECTIVE"]
    p3_pass = cs["graph_sep"] > 0.05 and cs["jury_sep"] < 0.05
    p3_v = "CONFIRMED" if p3_pass else "REFUTED"
    print(f"P3 CONTEXTUAL vs SUBJECTIVE: graph={cs['graph_sep']:.4f} jury={cs['jury_sep']:.4f} [{p3_v}]",
          file=sys.stderr)

    # P4: Rank corr(obs, graph) > rank corr(obs, jury)
    p4_pass = rc_graph_obs > rc_jury_obs + 0.10
    p4_v = "CONFIRMED" if p4_pass else "REFUTED"
    print(f"P4 rank_corr(obs,graph)={rc_graph_obs:.4f} > rank_corr(obs,jury)={rc_jury_obs:.4f}+0.10 [{p4_v}]",
          file=sys.stderr)

    # P5: ≥3 pairs where jury collapses but graph preserves
    p5_pass = len(collapsed) >= 3
    p5_v = "CONFIRMED" if p5_pass else "REFUTED"
    print(f"P5 {len(collapsed)} pairs with jury_sep<0.05 and graph_sep>0.10 (threshold=3) [{p5_v}]",
          file=sys.stderr)

    # ── Result record ────────────────────────────────────────────────────────
    result = {
        "sim_id": SIM_ID,
        "n_trials_per_claim_type": N_TRIALS,
        "panel_size": PANEL_SIZE,
        "n_obs": N_OBS,
        "description": (
            "Staged compression: observer (4D) → graph (3D) → jury (1D). "
            "Measures what fraction of observer-level epistemic structure "
            "survives at each compression stage."
        ),
        "classifier_accuracy": {
            "observer_4D": round(obs_acc, 4),
            "graph_3D":    round(graph_acc, 4),
            "jury_1D":     round(jury_acc, 4),
        },
        "rank_correlation_with_observer_stage": {
            "graph_vs_observer": round(rc_graph_obs, 4),
            "jury_vs_observer":  round(rc_jury_obs, 4),
        },
        "mean_preservation_ratio": {
            "graph": round(mean_g_ratio, 3),
            "jury":  round(mean_j_ratio, 3),
        },
        "n_pairs_jury_collapses_graph_preserves": len(collapsed),
        "pairs_jury_collapses_graph_preserves": collapsed,
        "pairwise_centroid_distances": pairwise,
        "observer_stage_centroids": obs_centroids,
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
