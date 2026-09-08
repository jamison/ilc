"""
SIM-LAUNDER-02F — Adversarially Matched-RRW Populations
=========================================================

The architectural test: construct 5 populations with approximately identical
raw_reuse_weight (RRW ≈ constant, within ±5%) but radically different values
on the other epistemic dimensions (I, R, K).

Then ask two questions:
  (1) Can RRW classify these populations? — Must fail: RRW is matched by design.
  (2) Can (IEC, R, K) classify them? — Should succeed: these are the varying axes.

If (2) succeeds and (1) fails, that establishes that the failure is intrinsic to
RRW — not an unlucky parameterization — and that the (I, R, K) profile is a
necessary, non-redundant extension.

Five populations:
  A_strong:          I=high, R=high, K=present  (genuine corroboration, context-aware)
  B_laundered:       I=low,  R=high, K=absent   (single origin, cartel-protected)
  C_fragile:         I=high, R=low,  K=present  (diverse but easily refuted)
  D_decontextualized: I=high, R=high, K=absent  (diverse but no context metadata)
  E_adversarial_poor: I=low, R=low,  K=absent   (worst case)

RRW matching strategy:
  All populations are tuned toward a shared target mean RRW.
  High-survival populations: lower p_cite (fewer descendants needed).
  Low-survival populations: higher p_cite (compensate for refuted-node losses).
  Cartel population B: p_cite tuned to compensate for low IEC.

Metrics per run:
  RRW     = mean transitive descendant count across origin nodes
  IEC     = count of distinct origin_ids with at least 1 surviving node
  R_surv  = fraction of all nodes that were not refuted
  K       = 1 if origins span 2+ contexts, 0 if single context
  K_sep   = |frac_context1_surviving - frac_context2_surviving|

Classifier comparison:
  RRW-only: centroid nearest-neighbor on (mean_RRW,) — 1D
  Full 3D:  centroid nearest-neighbor on (IEC, R_surv, K_sep) — 3D

Prediction:
  P1: RRW-only classifier accuracy ≈ random (1/5 = 20%) — populations matched by design
  P2: 3D classifier accuracy >> 20% — (I, R, K) distinguish what RRW cannot
  P3: A_strong and B_laundered are indistinguishable by RRW, separable by I (IEC)
  P4: A_strong and D_decontextualized are indistinguishable by (RRW, I, R),
      separable only by K (context structure)
  P5: C_fragile and A_strong are indistinguishable by (RRW, I, K), separable by R
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

SIM_ID    = "SIM-LAUNDER-02F"
N_EPOCHS  = 60
N_RUNS    = 300     # per population
N_CONTEXTS = 2      # C1, C2 for context-aware populations

# ── Graph node model ─────────────────────────────────────────────────────────

@dataclass
class GNode:
    node_id: int
    origin_id: int      # which independent origin this node came from
    context_id: int     # 0 = no context, 1 = C1, 2 = C2
    refuted: bool = False
    n_descendants: int = 0  # running count of transitive descendants


# ── Population configurations ─────────────────────────────────────────────────
#
# Each entry: (n_origins, context_list, p_cite, p_refute, p_survive, cartel_suppress)
#   n_origins:      number of independent starting nodes
#   context_list:   list of context_ids to cycle across origins (0=single ctx)
#   p_cite:         probability per epoch that a surviving node spawns a citation
#   p_refute:       probability per epoch that a node is challenged
#   p_survive:      probability that a challenged node survives the challenge
#   cartel_suppress: fraction of refutation challenges suppressed (0.0 = none)
#
# RRW calibration target ≈ 5.0 ± 0.5

POP_CONFIGS: Dict[str, Tuple] = {
    # I=high (10 origins), R=high, K=present (C1+C2)
    "A_strong":          (10, [1, 2], 0.065, 0.010, 0.85, 0.00),
    # I=low (1 origin), apparent R=high (cartel suppresses 70% of refutations), K=absent
    "B_laundered":       (1,  [0],   0.080, 0.015, 0.85, 0.70),
    # I=high, R=low (p_survive=0.25), K=present; higher p_cite compensates
    "C_fragile":         (10, [1, 2], 0.095, 0.050, 0.25, 0.00),
    # I=high, R=high, K=absent (all context_id=0)
    "D_decontextualized":(10, [0],   0.065, 0.010, 0.85, 0.00),
    # I=low, R=low, K=absent
    "E_adversarial_poor":(1,  [0],   0.095, 0.050, 0.25, 0.00),
}

POPULATIONS = list(POP_CONFIGS.keys())


def simulate_one_run(
    n_origins: int,
    context_list: List[int],
    p_cite: float,
    p_refute: float,
    p_survive: float,
    cartel_suppress: float,
    n_epochs: int,
    rng: np.random.Generator,
) -> Tuple[float, int, float, float]:
    """
    Returns (mean_rrw, iec, r_surv, k_sep).

    mean_rrw: mean descendant count per origin at end
    iec:      number of distinct origin_ids with ≥1 surviving node
    r_surv:   fraction of all nodes that were not refuted
    k_sep:    |frac_surviving_C1 - frac_surviving_C2| (0 if single context)
    """
    # Initialise origin nodes
    nodes: List[GNode] = []
    for i in range(n_origins):
        ctx = context_list[i % len(context_list)]
        nodes.append(GNode(len(nodes), i, ctx))

    next_id = n_origins

    for _ in range(n_epochs):
        alive = [n for n in nodes if not n.refuted]
        if not alive:
            break

        # Citation phase: each alive node may spawn a child
        new_nodes: List[GNode] = []
        for node in alive:
            if rng.random() < p_cite:
                child = GNode(next_id, node.origin_id, node.context_id)
                new_nodes.append(child)
                # Propagate descendant count upward (simplified: credit origin only)
                # For simplicity we count all nodes per origin as descendants of origin
                next_id += 1
        nodes.extend(new_nodes)

        # Refutation phase
        for node in list(nodes):
            if node.refuted:
                continue
            if rng.random() < p_refute:
                # Cartel suppression: probability of challenge being suppressed
                if cartel_suppress > 0 and rng.random() < cartel_suppress:
                    continue  # challenge suppressed
                # Challenge not suppressed: node must survive
                if rng.random() >= p_survive:
                    node.refuted = True

    # ── Compute metrics ───────────────────────────────────────────────────────

    # RRW: for each origin, count all non-refuted nodes with that origin_id
    # (proxy for transitive descendant count — descendants = nodes that "cite" origin's claim)
    origin_counts: Dict[int, int] = {}
    for node in nodes:
        if not node.refuted:
            origin_counts[node.origin_id] = origin_counts.get(node.origin_id, 0) + 1
    mean_rrw = (sum(origin_counts.values()) / len(origin_counts)
                if origin_counts else 0.0)

    # IEC: distinct origin_ids with ≥1 surviving node
    iec = len(origin_counts)

    # R_surv: fraction of all nodes that survived
    total = len(nodes)
    survived = sum(1 for n in nodes if not n.refuted)
    r_surv = survived / total if total > 0 else 0.0

    # K_sep: context separation among surviving nodes
    ctx_counts: Dict[int, int] = {}
    for node in nodes:
        if not node.refuted:
            ctx_counts[node.context_id] = ctx_counts.get(node.context_id, 0) + 1

    if 0 in ctx_counts or len(set(n.context_id for n in nodes if not n.refuted)) < 2:
        k_sep = 0.0  # no context structure
    else:
        total_alive = sum(ctx_counts.values())
        ctx_ids = [k for k in ctx_counts if k != 0]
        fracs = [ctx_counts[c] / total_alive for c in ctx_ids]
        k_sep = abs(fracs[0] - fracs[1]) if len(fracs) >= 2 else 0.0

    return mean_rrw, iec, r_surv, k_sep


def centroid_classifier(vecs_by_pop: Dict[str, np.ndarray]) -> float:
    """Centroid nearest-neighbor accuracy."""
    centroids = {p: v.mean(axis=0) for p, v in vecs_by_pop.items()}
    pops = list(vecs_by_pop.keys())
    correct = 0
    total = 0
    for true_pop, vecs in vecs_by_pop.items():
        for v in vecs:
            dists = {p: float(np.linalg.norm(v - centroids[p])) for p in pops}
            pred = min(dists, key=dists.get)
            if pred == true_pop:
                correct += 1
            total += 1
    return correct / total


def normalise(vecs_by_pop: Dict[str, np.ndarray]) -> Dict[str, np.ndarray]:
    all_v = np.vstack(list(vecs_by_pop.values()))
    mn, mx = all_v.min(axis=0), all_v.max(axis=0)
    rng2 = mx - mn
    rng2[rng2 == 0] = 1.0
    return {p: (v - mn) / rng2 for p, v in vecs_by_pop.items()}


def main() -> None:
    rng = np.random.default_rng(42)
    print(f"[{SIM_ID}] {len(POPULATIONS)} populations × {N_RUNS} runs × {N_EPOCHS} epochs",
          file=sys.stderr)

    # Collect per-run data
    rrw_vecs:  Dict[str, List[List[float]]] = {p: [] for p in POPULATIONS}
    full_vecs: Dict[str, List[List[float]]] = {p: [] for p in POPULATIONS}
    mean_metrics: Dict[str, dict] = {}

    for pop in POPULATIONS:
        cfg = POP_CONFIGS[pop]
        n_orig, ctx_list, p_cite, p_refute, p_surv, cartel = cfg
        rrws, iecs, rsurv_list, ksep_list = [], [], [], []

        for _ in range(N_RUNS):
            rrw, iec, rs, ks = simulate_one_run(
                n_orig, ctx_list, p_cite, p_refute, p_surv, cartel,
                N_EPOCHS, rng,
            )
            rrws.append(rrw)
            iecs.append(iec)
            rsurv_list.append(rs)
            ksep_list.append(ks)
            rrw_vecs[pop].append([rrw])
            full_vecs[pop].append([iec, rs, ks])

        mean_metrics[pop] = {
            "mean_rrw": round(float(np.mean(rrws)), 3),
            "mean_iec": round(float(np.mean(iecs)), 2),
            "mean_r_surv": round(float(np.mean(rsurv_list)), 4),
            "mean_k_sep": round(float(np.mean(ksep_list)), 4),
            "config": {
                "n_origins": n_orig,
                "context_list": ctx_list,
                "p_cite": p_cite,
                "p_refute": p_refute,
                "p_survive": p_surv,
                "cartel_suppress": cartel,
            },
        }

        print(f"  {pop:24s}: RRW={np.mean(rrws):.3f} "
              f"IEC={np.mean(iecs):.2f} R={np.mean(rsurv_list):.3f} "
              f"K={np.mean(ksep_list):.4f}",
              file=sys.stderr)

    # ── RRW range check ───────────────────────────────────────────────────────
    rrw_values = [mean_metrics[p]["mean_rrw"] for p in POPULATIONS]
    rrw_range = max(rrw_values) - min(rrw_values)
    rrw_mean  = sum(rrw_values) / len(rrw_values)
    rrw_pct   = rrw_range / rrw_mean * 100
    print(f"\nRRW range: {min(rrw_values):.3f}–{max(rrw_values):.3f} "
          f"({rrw_pct:.1f}% spread)", file=sys.stderr)

    # ── Convert to numpy ─────────────────────────────────────────────────────
    rrw_np  = {p: np.array(v) for p, v in rrw_vecs.items()}
    full_np = {p: np.array(v) for p, v in full_vecs.items()}

    rrw_norm  = normalise(rrw_np)
    full_norm = normalise(full_np)

    rrw_acc  = centroid_classifier(rrw_norm)
    full_acc = centroid_classifier(full_norm)

    print(f"\nCentroid classifier accuracy:", file=sys.stderr)
    print(f"  RRW-only (1D):       {rrw_acc:.4f}", file=sys.stderr)
    print(f"  Full (IEC,R,K) (3D): {full_acc:.4f}", file=sys.stderr)

    # ── Pairwise centroid distances ───────────────────────────────────────────
    rrw_centroids  = {p: rrw_norm[p].mean(axis=0)  for p in POPULATIONS}
    full_centroids = {p: full_norm[p].mean(axis=0) for p in POPULATIONS}

    def cdist(ct_a: str, ct_b: str, centroids: Dict) -> float:
        return float(np.linalg.norm(centroids[ct_a] - centroids[ct_b]))

    print(f"\n{'Pair':45s} {'rrw_sep':>8} {'full_sep':>9}", file=sys.stderr)
    pairwise: dict = {}
    for i, pa in enumerate(POPULATIONS):
        for pb in POPULATIONS[i + 1:]:
            rs = cdist(pa, pb, rrw_centroids)
            fs = cdist(pa, pb, full_centroids)
            key = f"{pa} vs {pb}"
            pairwise[key] = {
                "rrw_sep": round(rs, 4),
                "full_sep": round(fs, 4),
                "full_advantage": round(fs - rs, 4),
            }
            marker = " ***" if fs - rs > 0.10 else ""
            print(f"  {key:45s} {rs:8.4f} {fs:9.4f}{marker}", file=sys.stderr)

    # ── Prediction verdicts ───────────────────────────────────────────────────
    # P1: RRW-only accuracy ≈ random (20%)
    p1_v = "CONFIRMED" if rrw_acc < 0.30 else "REFUTED"
    print(f"\nP1 RRW-only acc={rrw_acc:.4f} < 0.30 [{p1_v}]", file=sys.stderr)

    # P2: Full (I,R,K) accuracy >> random
    p2_v = "CONFIRMED" if full_acc > 0.60 else "REFUTED"
    print(f"P2 Full acc={full_acc:.4f} > 0.60 [{p2_v}]", file=sys.stderr)

    # P3: A vs B — indistinguishable by RRW, separable by I
    ab = pairwise["A_strong vs B_laundered"]
    p3_v = "CONFIRMED" if ab["rrw_sep"] < 0.10 and ab["full_sep"] > 0.20 else "REFUTED"
    print(f"P3 A_strong vs B_laundered: rrw={ab['rrw_sep']:.4f} full={ab['full_sep']:.4f} [{p3_v}]",
          file=sys.stderr)

    # P4: A vs D — separable only by K (context structure)
    ad = pairwise["A_strong vs D_decontextualized"]
    p4_v = "CONFIRMED" if ad["full_sep"] > ad["rrw_sep"] + 0.05 else "REFUTED"
    print(f"P4 A_strong vs D_decontextualized: rrw={ad['rrw_sep']:.4f} full={ad['full_sep']:.4f} [{p4_v}]",
          file=sys.stderr)

    # P5: A vs C — separable by R (fragility dimension)
    ac = pairwise["A_strong vs C_fragile"]
    p5_v = "CONFIRMED" if ac["full_sep"] > ac["rrw_sep"] + 0.05 else "REFUTED"
    print(f"P5 A_strong vs C_fragile: rrw={ac['rrw_sep']:.4f} full={ac['full_sep']:.4f} [{p5_v}]",
          file=sys.stderr)

    # Summary table
    print(f"\n{'Population':26s} {'RRW':>6} {'IEC':>5} {'R':>6} {'K':>7}", file=sys.stderr)
    for pop in POPULATIONS:
        m = mean_metrics[pop]
        print(f"  {pop:24s} {m['mean_rrw']:6.3f} {m['mean_iec']:5.2f} "
              f"{m['mean_r_surv']:6.4f} {m['mean_k_sep']:7.4f}", file=sys.stderr)

    result = {
        "sim_id": SIM_ID,
        "description": "Matched-RRW adversarial populations: (I,R,K) classifies what RRW cannot",
        "methodological_note": (
            "All populations tuned to target RRW ≈ 5.0 ± tolerance. "
            "RRW-only classifier tests the null hypothesis that citation count is sufficient. "
            "Full (IEC,R,K) classifier tests the alternative. "
            "Centroid nearest-neighbor on normalized vectors."
        ),
        "mean_metrics": mean_metrics,
        "rrw_spread_pct": round(rrw_pct, 2),
        "classifier_accuracy": {
            "rrw_only_1D": round(rrw_acc, 4),
            "full_IRK_3D": round(full_acc, 4),
        },
        "pairwise": pairwise,
        "predictions": {
            "P1": "RRW-only accuracy < 30% (≈ random for 5 classes)",
            "P2": "Full (I,R,K) accuracy > 60%",
            "P3": "A vs B indistinguishable by RRW (sep < 0.10), separable by (I,R,K) (sep > 0.20)",
            "P4": "A vs D: full_sep > rrw_sep + 0.05 (K dimension distinguishes)",
            "P5": "A vs C: full_sep > rrw_sep + 0.05 (R dimension distinguishes)",
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
