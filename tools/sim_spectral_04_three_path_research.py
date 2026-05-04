#!/usr/bin/env python3
"""SIM-SPECTRAL-04 Three-Path Auto-Research.

PATH 1 — Alternative projection methodologies:
  Test structurally distinct graph topologies using the same 56 vertices
  but different edge structures (community-partitioned, bipartite, hierarchical,
  intra-dense).  Measures whether topology design rather than node count is the
  lever.

PATH 2 — Threshold calibration:
  Run 60 matched-size S3 random graphs and find the empirical S3/S1 ratio
  distribution.  Reports what threshold would make CDL-085 pass at various
  confidence levels, and where 0.6416 sits in the distribution.

PATH 3 — Alternative spectral discriminants:
  Compute 8 graph-theoretic statistics (Fiedler value, spectral gap, clustering
  coefficient, degree Gini, modularity, diameter, degree entropy, edge density)
  for S1 and 100 S3 samples.  Reports z-scores showing which statistics cleanly
  separate S1 from the random graph distribution — pointing to which structural
  property CDL-085 should be testing.

Usage:
  .venv/bin/python tools/sim_spectral_04_three_path_research.py
"""

from __future__ import annotations

import copy
import json
import math
import random
import sys
import tempfile
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent))
from tools.sim_spectral_02 import run_simulation  # noqa: E402

# ---------------------------------------------------------------------------
# Shared constants
# ---------------------------------------------------------------------------
PROJECTION_PATH = Path("out/genesis_claim_composition_projection_v0.1.json")
SEEDS = [42, 1337, 2026]
EPOCHS = 30
K = 0.3
WEIGHT_PROFILE = "uniform_available"
S3_S1_THRESHOLD = 0.6416011282246747
G2_S1_THRESHOLD = 0.8640456434014127

RNG = random.Random(9999)


# ---------------------------------------------------------------------------
# Gate runner (shared)
# ---------------------------------------------------------------------------

def _slope(tmp_path: Path, scenario: str, seed: int, n: int | None) -> float:
    return float(run_simulation(
        scenario=scenario, k=K, weight_profile=WEIGHT_PROFILE,
        seed=seed, epochs=EPOCHS,
        s1_projection_file=tmp_path if scenario == "S1" else None,
        node_count_override=n if scenario != "S1" else None,
    )["rolling_slope"])


def run_gate(proj: dict[str, Any]) -> dict[str, Any]:
    n = len(proj["vertices"])
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False,
                                     encoding="utf-8") as f:
        json.dump(proj, f, sort_keys=True, allow_nan=False)
        tmp = Path(f.name)
    per_seed = []
    try:
        for seed in SEEDS:
            s1 = _slope(tmp, "S1", seed, None)
            s3 = _slope(tmp, "S3", seed, n)
            g2 = _slope(tmp, "G2", seed, n)
            s3_s1 = abs(s3 / s1) if abs(s1) > 1e-9 else math.inf
            g2_s1 = abs(g2 / s1) if abs(s1) > 1e-9 else math.inf
            per_seed.append({"seed": seed, "s1": round(s1, 6),
                             "s3_s1": round(s3_s1, 6), "g2_s1": round(g2_s1, 6)})
    finally:
        tmp.unlink(missing_ok=True)
    s1_pos = all(r["s1"] > 0 for r in per_seed)
    s3_ok = all(r["s3_s1"] < S3_S1_THRESHOLD for r in per_seed)
    g2_ok = all(r["g2_s1"] < G2_S1_THRESHOLD for r in per_seed)
    return {
        "gate": "PASS" if (s1_pos and s3_ok and g2_ok) else "FAIL",
        "s1_pos": s1_pos, "s3_ok": s3_ok, "g2_ok": g2_ok,
        "max_s3_s1": round(max(r["s3_s1"] for r in per_seed), 6),
        "max_g2_s1": round(max(r["g2_s1"] for r in per_seed), 6),
        "per_seed": per_seed,
    }


# ---------------------------------------------------------------------------
# PATH 1 — Alternative projection methodologies
# ---------------------------------------------------------------------------

def _load_proj() -> dict[str, Any]:
    return json.loads(PROJECTION_PATH.read_text(encoding="utf-8"))


def _make_proj(vertices: list[dict], edges: list[dict]) -> dict[str, Any]:
    """Assemble a minimal valid projection dict."""
    return {"vertices": vertices, "edges": edges}


def _edge(src: str, tgt: str, reason: str = "derives_from", w: float = 1.0) -> dict:
    return {"edge_id": f"e:{src[-20:]}:{tgt[-20:]}", "source": src,
            "target": tgt, "reason": reason, "weight": w}


def _build_community_projection(
    vertices: list[dict],
    communities: list[list[str]],
    intra_density: float,
    inter_edges_per_pair: int,
    rng: random.Random,
) -> dict[str, Any]:
    """Build a projection with intra-community dense edges and sparse inter-community bridges."""
    edges = []
    # Intra-community edges
    for comm in communities:
        pairs = [(comm[i], comm[j]) for i in range(len(comm)) for j in range(i+1, len(comm))]
        n_intra = max(len(comm), int(len(pairs) * intra_density))
        chosen = rng.sample(pairs, min(n_intra, len(pairs)))
        for src, tgt in chosen:
            edges.append(_edge(src, tgt, "intra_community_composition"))
    # Inter-community edges (sparse bridges)
    for ci in range(len(communities)):
        for cj in range(ci+1, len(communities)):
            bridges = inter_edges_per_pair
            for _ in range(bridges):
                src = rng.choice(communities[ci])
                tgt = rng.choice(communities[cj])
                edges.append(_edge(src, tgt, "inter_community_bridge"))
    return _make_proj(vertices, edges)


def _build_bipartite_projection(
    vertices: list[dict],
    layer_a: list[str],
    layer_b: list[str],
    edges_per_b_node: int,
    rng: random.Random,
) -> dict[str, Any]:
    """Strict bipartite: each B-node connects to a small sample of A-nodes only."""
    edges = []
    for b in layer_b:
        targets = rng.sample(layer_a, min(edges_per_b_node, len(layer_a)))
        for a in targets:
            edges.append(_edge(b, a, "invokes_authority"))
    return _make_proj(vertices, edges)


def _build_hierarchical_projection(
    vertices: list[dict],
    roots: list[str],
    mid: list[str],
    leaves: list[str],
    rng: random.Random,
) -> dict[str, Any]:
    """3-level hierarchy: roots→mid (each root fans out), mid→leaves."""
    edges = []
    # root → mid
    mid_per_root = max(2, len(mid) // len(roots))
    for root in roots:
        targets = rng.sample(mid, min(mid_per_root, len(mid)))
        for t in targets:
            edges.append(_edge(root, t, "governs_claim_class"))
    # mid → leaves (each mid node fans into 2–4 leaves)
    leaves_per_mid = max(2, len(leaves) // len(mid))
    shuffled_leaves = list(leaves)
    rng.shuffle(shuffled_leaves)
    for i, m in enumerate(mid):
        start = (i * leaves_per_mid) % len(shuffled_leaves)
        for j in range(leaves_per_mid):
            leaf = shuffled_leaves[(start + j) % len(shuffled_leaves)]
            edges.append(_edge(m, leaf, "instantiates_claim"))
    # Some leaf-to-leaf edges (within-level composition)
    for _ in range(len(leaves) // 3):
        src, tgt = rng.sample(leaves, 2)
        edges.append(_edge(src, tgt, "composes_with"))
    return _make_proj(vertices, edges)


def _build_intra_dense_projection(
    proj: dict[str, Any],
    vertex_kind_map: dict[str, list[str]],
    extra_edges_per_community: int,
    rng: random.Random,
) -> dict[str, Any]:
    """Current projection + extra intra-vertex_kind edges."""
    p = copy.deepcopy(proj)
    existing = {(e["source"], e["target"]) for e in p["edges"]}
    for kind, vids in vertex_kind_map.items():
        pairs = [(vids[i], vids[j]) for i in range(len(vids)) for j in range(i+1, len(vids))]
        new_pairs = [pair for pair in pairs if pair not in existing and (pair[1], pair[0]) not in existing]
        rng.shuffle(new_pairs)
        for src, tgt in new_pairs[:extra_edges_per_community]:
            p["edges"].append(_edge(src, tgt, "intra_kind_composition"))
            existing.add((src, tgt))
    return p


def path1_experiments() -> list[tuple[str, dict[str, Any]]]:
    proj = _load_proj()
    verts = proj["vertices"]
    rng = random.Random(42)

    # Build vertex_kind map
    kind_map: dict[str, list[str]] = defaultdict(list)
    for v in verts:
        kind_map[v["vertex_kind"]].append(v["vertex_id"])

    claim_composite = kind_map["claim_composite"]       # 24
    primitive = kind_map["primitive"]                   # 10
    param_policy = kind_map["parameterized_policy"]     # 10
    runtime_pending = kind_map["runtime_binding_pending"]  # 6
    historical = kind_map["historical_artifact"]         # 6

    all_ids = [v["vertex_id"] for v in verts]

    experiments = [("P1 baseline", copy.deepcopy(proj))]

    # --- Variant A: 2 communities (claims vs authority) ---
    comm_a = claim_composite + param_policy + runtime_pending   # 40 "claim" nodes
    comm_b = primitive + historical                              # 16 "authority" nodes
    experiments.append((
        "P1-A: 2-community (claims 40 / authority 16), intra=0.4, bridges=3",
        _build_community_projection(verts, [comm_a, comm_b], 0.40, 3, random.Random(1)),
    ))

    # --- Variant B: 3 communities by vertex_kind ---
    comm1 = claim_composite                             # 24
    comm2 = primitive + param_policy                    # 20
    comm3 = runtime_pending + historical                # 12
    experiments.append((
        "P1-B: 3-community (composite 24 / prim+pol 20 / rt+hist 12), intra=0.3, bridges=2",
        _build_community_projection(verts, [comm1, comm2, comm3], 0.30, 2, random.Random(2)),
    ))
    experiments.append((
        "P1-B2: 3-community same, intra=0.5, bridges=1",
        _build_community_projection(verts, [comm1, comm2, comm3], 0.50, 1, random.Random(3)),
    ))
    experiments.append((
        "P1-B3: 3-community same, intra=0.7, bridges=1 (very dense intra)",
        _build_community_projection(verts, [comm1, comm2, comm3], 0.70, 1, random.Random(4)),
    ))

    # --- Variant C: 5 communities (all 5 vertex_kinds) ---
    comm5 = [claim_composite, primitive, param_policy, runtime_pending, historical]
    experiments.append((
        "P1-C: 5-community (all vertex_kinds), intra=0.4, bridges=1",
        _build_community_projection(verts, comm5, 0.40, 1, random.Random(5)),
    ))
    experiments.append((
        "P1-C2: 5-community, intra=0.6, bridges=0 (isolated communities)",
        _build_community_projection(verts, comm5, 0.60, 0, random.Random(6)),
    ))

    # --- Variant D: strict bipartite ---
    layer_a = primitive + historical                    # 16 authority nodes
    layer_b = claim_composite + param_policy + runtime_pending  # 40 claim nodes
    experiments.append((
        f"P1-D: bipartite (auth 16 / claims 40), 3 edges per claim node",
        _build_bipartite_projection(verts, layer_a, layer_b, 3, random.Random(7)),
    ))
    experiments.append((
        f"P1-D2: bipartite, 5 edges per claim node",
        _build_bipartite_projection(verts, layer_a, layer_b, 5, random.Random(8)),
    ))

    # --- Variant E: 3-level hierarchy ---
    experiments.append((
        "P1-E: hierarchical (roots=historical 6, mid=prim+pol 20, leaves=composite+rt 30)",
        _build_hierarchical_projection(verts, historical, primitive + param_policy,
                                       claim_composite + runtime_pending, random.Random(9)),
    ))

    # --- Variant F: current + extra intra-kind edges ---
    experiments.append((
        "P1-F: current + 5 extra intra-kind edges per kind",
        _build_intra_dense_projection(proj, dict(kind_map), 5, random.Random(10)),
    ))
    experiments.append((
        "P1-F2: current + 10 extra intra-kind edges per kind",
        _build_intra_dense_projection(proj, dict(kind_map), 10, random.Random(11)),
    ))
    experiments.append((
        "P1-F3: current + 20 extra intra-kind edges per kind",
        _build_intra_dense_projection(proj, dict(kind_map), 20, random.Random(12)),
    ))

    return experiments


# ---------------------------------------------------------------------------
# PATH 2 — Threshold calibration
# ---------------------------------------------------------------------------

def path2_threshold_calibration() -> dict[str, Any]:
    """Sample 60 S3 random graphs, build the empirical S3/S1 distribution,
    find what threshold CDL-085 would need to reliably pass."""
    proj = _load_proj()
    n = len(proj["vertices"])

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False,
                                     encoding="utf-8") as f:
        json.dump(proj, f, sort_keys=True, allow_nan=False)
        tmp = Path(f.name)

    # S1 slopes per seed (deterministic)
    s1_slopes = {}
    for seed in SEEDS:
        s1_slopes[seed] = _slope(tmp, "S1", seed, None)
    tmp.unlink(missing_ok=True)

    # S3 slopes: 60 independent samples per seed (different node_count_override seeds)
    # We vary seeds 0..59 to get 60 S3 samples
    N_SAMPLES = 60
    s3_ratios_all: list[float] = []  # all seeds × all samples
    s3_ratios_per_seed: dict[int, list[float]] = {s: [] for s in SEEDS}

    for sample_seed in range(N_SAMPLES):
        for seed in SEEDS:
            s3 = _slope(None, "S3", sample_seed * 100 + seed, n)  # type: ignore[arg-type]
            ratio = abs(s3 / s1_slopes[seed]) if abs(s1_slopes[seed]) > 1e-9 else math.inf
            s3_ratios_all.append(ratio)
            s3_ratios_per_seed[seed].append(ratio)

    s3_ratios_sorted = sorted(s3_ratios_all)
    total = len(s3_ratios_sorted)

    # What fraction of samples are BELOW each candidate threshold?
    # (Below = "indistinguishable from random" = bad for CDL-085)
    # We want the threshold to be ABOVE most of the S3/S1 distribution
    # (so random graphs fail the test) but BELOW S1 (so S1 passes).
    # Currently S1's max_S3/S1 ratio ≈ 0.864. The threshold 0.6416 is below that.
    # We need to find a threshold T such that S1 (ratio=0.864) would PASS, meaning
    # a threshold T > 0.864 where "random graphs also mostly have ratio > T".

    # Actually the framing is: CDL-085 PASSES if S3/S1 < T (S3 slope is SMALLER than T * S1 slope).
    # We want T such that the current graph (S3/S1 = 0.864) passes, i.e., T > 0.864.
    # But we also want T to be a meaningful threshold — not so high that everything passes.

    # Report: percentile of 0.864 in the S3/S1 distribution
    current_max = 0.864  # from baseline
    pct_below_current = sum(1 for r in s3_ratios_sorted if r < current_max) / total * 100

    # What threshold puts the baseline S1 in the top X%?
    pct_targets = [50, 75, 90, 95, 99]
    threshold_at_pct: dict[str, float] = {}
    for pct in pct_targets:
        idx = int(total * pct / 100)
        threshold_at_pct[f"p{pct}"] = round(s3_ratios_sorted[min(idx, total-1)], 4)

    # Mean and std of S3/S1 distribution
    mean_ratio = sum(s3_ratios_sorted) / total
    std_ratio = math.sqrt(sum((r - mean_ratio)**2 for r in s3_ratios_sorted) / total)

    return {
        "s1_slopes": s1_slopes,
        "s1_max_s3_s1": current_max,
        "n_samples": total,
        "s3_s1_mean": round(mean_ratio, 4),
        "s3_s1_std": round(std_ratio, 4),
        "s3_s1_min": round(s3_ratios_sorted[0], 4),
        "s3_s1_max": round(s3_ratios_sorted[-1], 4),
        "pct_s3_below_s1": round(pct_below_current, 1),
        "threshold_to_pass_at": threshold_at_pct,
        "current_threshold": S3_S1_THRESHOLD,
    }


# ---------------------------------------------------------------------------
# PATH 3 — Alternative spectral discriminants
# ---------------------------------------------------------------------------

def _build_adj(vertex_ids: list[str], edges: list[dict]) -> np.ndarray:
    idx = {v: i for i, v in enumerate(vertex_ids)}
    n = len(vertex_ids)
    A = np.zeros((n, n), dtype=float)
    for e in edges:
        s, t = e.get("source", ""), e.get("target", "")
        if s in idx and t in idx and s != t:
            A[idx[s], idx[t]] += 1.0
            A[idx[t], idx[s]] += 1.0
    return A


def _laplacian(A: np.ndarray) -> np.ndarray:
    D = np.diag(A.sum(axis=1))
    return D - A


def _eigenvalues(L: np.ndarray) -> np.ndarray:
    return np.sort(np.linalg.eigvalsh(L))


def _clustering_coeff(A: np.ndarray) -> float:
    """Global clustering coefficient (fraction of closed triangles)."""
    n = A.shape[0]
    A3 = A @ A @ A
    triangles_2 = np.trace(A3)  # 6 * triangles
    deg = A.sum(axis=1)
    potential = float(np.sum(deg * (deg - 1)))
    return float(triangles_2 / potential) if potential > 0 else 0.0


def _degree_gini(A: np.ndarray) -> float:
    """Gini coefficient of the degree distribution (0=uniform, 1=maximally unequal)."""
    degs = sorted(A.sum(axis=1))
    n = len(degs)
    if n == 0 or sum(degs) == 0:
        return 0.0
    cum = 0.0
    for i, d in enumerate(degs):
        cum += (2 * (i + 1) - n - 1) * d
    return float(cum / (n * sum(degs)))


def _modularity(A: np.ndarray, communities: list[list[int]]) -> float:
    """Newman-Girvan modularity given a partition."""
    m = A.sum() / 2.0
    if m == 0:
        return 0.0
    Q = 0.0
    degs = A.sum(axis=1)
    for comm in communities:
        for i in comm:
            for j in comm:
                Q += A[i, j] - degs[i] * degs[j] / (2 * m)
    return float(Q / (2 * m))


def _diameter(A: np.ndarray) -> int:
    """Approximate diameter via BFS from each node. Returns -1 if disconnected."""
    n = A.shape[0]
    max_dist = 0
    for start in range(n):
        visited = {start}
        frontier = [start]
        dist = 0
        while frontier:
            dist += 1
            next_f = []
            for u in frontier:
                for v in range(n):
                    if A[u, v] > 0 and v not in visited:
                        visited.add(v)
                        next_f.append(v)
            if next_f:
                max_dist = max(max_dist, dist)
            frontier = next_f
        if len(visited) < n:
            return -1
    return max_dist


def _degree_entropy(A: np.ndarray) -> float:
    """Shannon entropy of the degree distribution."""
    degs = [int(d) for d in A.sum(axis=1)]
    counts = Counter(degs)
    total = sum(counts.values())
    return float(-sum((c / total) * math.log2(c / total) for c in counts.values() if c > 0))


def _graph_stats(vertex_ids: list[str], edges: list[dict],
                 community_partition: list[list[int]] | None = None) -> dict[str, float]:
    A = _build_adj(vertex_ids, edges)
    L = _laplacian(A)
    eigs = _eigenvalues(L)
    n = len(vertex_ids)
    # λ₂ (Fiedler value) — skip λ₀ = 0
    lambda2 = float(eigs[1]) if n > 1 else 0.0
    lambda_max = float(eigs[-1]) if n > 1 else 0.0
    m = float(A.sum()) / 2
    clustering = _clustering_coeff(A)
    gini = _degree_gini(A)
    diam = _diameter(A)
    entropy = _degree_entropy(A)
    mod = _modularity(A, community_partition) if community_partition else 0.0
    return {
        "n": n,
        "m": m,
        "edge_density": round(2 * m / (n * (n - 1)), 4) if n > 1 else 0,
        "lambda2": round(lambda2, 4),
        "lambda_max": round(lambda_max, 4),
        "spectral_gap": round(lambda_max - lambda2, 4),
        "clustering": round(clustering, 4),
        "degree_gini": round(gini, 4),
        "diameter": diam,
        "degree_entropy": round(entropy, 4),
        "modularity": round(mod, 4),
    }


def _random_graph_erdos_renyi(n: int, m: int, rng: random.Random) -> list[dict]:
    """Generate m random edges on n nodes (Erdős-Rényi style)."""
    node_ids = [f"rg:n{i}" for i in range(n)]
    pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
    rng.shuffle(pairs)
    edges = []
    for i, j in pairs[:m]:
        edges.append({"source": node_ids[i], "target": node_ids[j],
                      "reason": "random", "weight": 1.0})
    return edges


def path3_discriminants(n_s3_samples: int = 100) -> dict[str, Any]:
    proj = _load_proj()
    vertex_ids = [v["vertex_id"] for v in proj["vertices"]]
    n = len(vertex_ids)
    m = len(proj["edges"])

    # Community partition by vertex_kind (for modularity)
    kind_map: dict[str, list[int]] = defaultdict(list)
    for i, v in enumerate(proj["vertices"]):
        kind_map[v["vertex_kind"]].append(i)
    community_partition = list(kind_map.values())

    # S1 stats
    s1_stats = _graph_stats(vertex_ids, proj["edges"], community_partition)

    # S3 samples
    s3_sample_stats: list[dict[str, float]] = []
    rng = random.Random(777)
    for _ in range(n_s3_samples):
        rg_edges = _random_graph_erdos_renyi(n, m, rng)
        rg_vids = [f"rg:n{i}" for i in range(n)]
        s3_sample_stats.append(_graph_stats(rg_vids, rg_edges, None))

    # Compute z-scores for each statistic
    stat_keys = ["lambda2", "lambda_max", "spectral_gap", "clustering",
                 "degree_gini", "diameter", "degree_entropy", "modularity"]
    analysis: dict[str, dict] = {}
    for key in stat_keys:
        s1_val = s1_stats[key]
        s3_vals = [s[key] for s in s3_sample_stats if s[key] != -1]
        if not s3_vals:
            continue
        mu = sum(s3_vals) / len(s3_vals)
        std = math.sqrt(sum((v - mu)**2 for v in s3_vals) / len(s3_vals))
        z = (s1_val - mu) / std if std > 1e-9 else 0.0
        # Percentile rank: what fraction of S3 samples is S1 more extreme than?
        pct_rank = sum(1 for v in s3_vals if v < s1_val) / len(s3_vals) * 100
        analysis[key] = {
            "s1": s1_val,
            "s3_mean": round(mu, 4),
            "s3_std": round(std, 4),
            "z_score": round(z, 3),
            "pct_rank": round(pct_rank, 1),
            "distinguishable": abs(z) > 2.0,
        }

    return {"s1_stats": s1_stats, "analysis": analysis,
            "n_s3_samples": n_s3_samples}


# ---------------------------------------------------------------------------
# Output helpers
# ---------------------------------------------------------------------------

def print_path1(results: list[dict]) -> None:
    print("\n" + "=" * 95)
    print("PATH 1 — Alternative projection methodologies")
    print("=" * 95)
    print(f"{'Variant':<60} {'n':>4} {'e':>4} {'maxS3/S1':>9} {'maxG2/S1':>9} {'S3✓':>4} {'G2✓':>4} {'gate':>6}")
    print("─" * 95)
    for r in results:
        flag = " ◄ PASS" if r["gate"] == "PASS" else ""
        s3ok = "✓" if r["s3_ok"] else "✗"
        g2ok = "✓" if r["g2_ok"] else "✗"
        print(f"  {r['name']:<58} {r['n']:>4} {r['e']:>4} "
              f"{r['max_s3_s1']:>9.4f} {r['max_g2_s1']:>9.4f} {s3ok:>4} {g2ok:>4} {r['gate']:>6}{flag}")
    passes = sum(1 for r in results if r["gate"] == "PASS")
    print(f"\n  {passes}/{len(results)} pass  |  Best S3/S1: {min(r['max_s3_s1'] for r in results):.4f}")


def print_path2(result: dict) -> None:
    print("\n" + "=" * 95)
    print("PATH 2 — Threshold calibration")
    print("=" * 95)
    print(f"  S1 max S3/S1 ratio (baseline): {result['s1_max_s3_s1']}")
    print(f"  Current gate threshold:         {result['current_threshold']}")
    print(f"  S3/S1 distribution over {result['n_samples']} samples:")
    print(f"    mean = {result['s3_s1_mean']:.4f}  std = {result['s3_s1_std']:.4f}  "
          f"min = {result['s3_s1_min']:.4f}  max = {result['s3_s1_max']:.4f}")
    print(f"  % of S3 samples below S1 baseline ({result['s1_max_s3_s1']}): "
          f"{result['pct_s3_below_s1']:.1f}%")
    print()
    print("  Threshold required for S1 to pass (i.e., T such that current S3/S1 ≈ 0.864 < T):")
    print("  (These are percentiles of the S3/S1 distribution — T above these means S1 passes,")
    print("   but X% of random graphs also have S3/S1 < T, so they'd pass too):")
    for pct, val in result["threshold_to_pass_at"].items():
        note = " ← current threshold" if abs(val - result["current_threshold"]) < 0.01 else ""
        print(f"    {pct}: {val:.4f}{note}")
    print()
    # How high does threshold need to be for S1 to clearly pass?
    s1_val = result["s1_max_s3_s1"]
    print(f"  S1 passes if threshold > {s1_val:.4f}.")
    print(f"  Current threshold ({result['current_threshold']:.4f}) is "
          f"{'below' if result['current_threshold'] < s1_val else 'above'} S1's ratio.")
    print(f"  For S1 to pass: threshold must be raised to ~{s1_val + 0.02:.4f} or higher.")
    print(f"  But at that level, {result['pct_s3_below_s1']:.1f}% of random graphs also pass.")


def print_path3(result: dict) -> None:
    print("\n" + "=" * 95)
    print("PATH 3 — Alternative spectral discriminants")
    print(f"  (S1 vs {result['n_s3_samples']} random S3 graphs at matched size)")
    print("=" * 95)
    print(f"  {'Statistic':<22} {'S1 value':>10} {'S3 mean':>10} {'S3 std':>8} "
          f"{'z-score':>8} {'pct rank':>9} {'distinct':>9}")
    print("  " + "─" * 80)
    for key, v in result["analysis"].items():
        dist = "YES ◄" if v["distinguishable"] else "no"
        print(f"  {key:<22} {v['s1']:>10.4f} {v['s3_mean']:>10.4f} {v['s3_std']:>8.4f} "
              f"{v['z_score']:>8.3f} {v['pct_rank']:>8.1f}% {dist:>9}")
    print()
    distinct = [k for k, v in result["analysis"].items() if v["distinguishable"]]
    print(f"  Statistics where S1 is >2σ from random: {distinct if distinct else 'none'}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    print(f"SIM-SPECTRAL-04 Three-Path Auto-Research")
    print(f"Gate: S3/S1 < {S3_S1_THRESHOLD:.4f},  G2/S1 < {G2_S1_THRESHOLD:.4f}")

    # PATH 1
    print("\nRunning PATH 1 (projection methodology variants)…")
    p1_experiments = path1_experiments()
    p1_results = []
    for name, proj in p1_experiments:
        n = len(proj["vertices"])
        e = len(proj["edges"])
        try:
            gr = run_gate(proj)
            p1_results.append({"name": name, "n": n, "e": e, **gr})
            flag = " ◄ PASS" if gr["gate"] == "PASS" else ""
            print(f"  {name[:58]:<58} S3/S1={gr['max_s3_s1']:.4f} G2/S1={gr['max_g2_s1']:.4f}{flag}")
        except Exception as exc:
            p1_results.append({"name": name, "n": n, "e": e, "gate": "ERR",
                               "s3_ok": False, "g2_ok": False,
                               "max_s3_s1": 99.0, "max_g2_s1": 99.0})
            print(f"  {name[:58]:<58} ERROR: {exc}")

    # PATH 2
    print("\nRunning PATH 2 (threshold calibration, 60 S3 samples × 3 seeds)…")
    p2_result = path2_threshold_calibration()

    # PATH 3
    print("\nRunning PATH 3 (spectral discriminants, 100 S3 samples)…")
    p3_result = path3_discriminants(n_s3_samples=100)

    # Print all results
    print_path1(p1_results)
    print_path2(p2_result)
    print_path3(p3_result)

    # Save
    out = {
        "path1": p1_results,
        "path2": p2_result,
        "path3": {k: v for k, v in p3_result.items() if k != "s1_stats"},
        "path3_s1_stats": p3_result["s1_stats"],
    }
    out_path = Path("out/sim_spectral_04_three_path_research.json")
    out_path.write_text(json.dumps(out, sort_keys=True, indent=2, allow_nan=False),
                        encoding="utf-8")
    print(f"\nFull results → {out_path}")


if __name__ == "__main__":
    main()
