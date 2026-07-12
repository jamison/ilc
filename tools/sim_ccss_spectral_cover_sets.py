#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
"""
SIM 2+3: CCSS Spectral Equivalence-Class Cover Sets v0.1
Phase: research / forward-planning (Window 1576+ lane)
Seed: 1574

What Sim 1 showed
-----------------
Random per-epoch k_batch padding FAILS at N >= 500 because:
  intersection_t(structural_t ∪ random_padding_t) → structural_t only
Random padding is inconsistent across epochs → cancels out → adversary
sees the real sender as the only node who consistently appears.

Core insight for Sim 2
-----------------------
Replace random padding with DETERMINISTIC padding derived from the
sender's local spectral fingerprint (quantized normalized-Laplacian
eigenvalues of the local neighbourhood).

Key property: the cover set is IDENTICAL every epoch (same fingerprint
→ same equivalence class). Now:

  candidates = ∩_t (structural_t ∪ stable_cover)
             = stable_cover ∪ ∩_t structural_t     [identity; A constant]

stable_cover appears in every epoch → it can never be intersected away.
Adversary is confined to the cover set size.

If |stable_cover| >= k_batch = 128 → P(success) < 1/128 < 0.01. ✓

Sim 2: 1-hop neighbourhood fingerprint (node + direct neighbours)
Sim 3: 2-hop neighbourhood fingerprint (double Laplacian, L²-layer)

Prediction
----------
High λ₂ (well-connected) → many nodes share similar local spectra →
large equivalence classes → network-wide P(success) → 0.
Low λ₂ (sparse/tree-like) → unique local spectra → small classes →
high P(success) for unique-fingerprint nodes.

Model
-----
- Adversary: relay-level observer, 1-hop attribution.
- Stable cover set: spectral equivalence class of sender, padded to
  k_batch with nearest spectral neighbours if class < k_batch.
- Adversary intersects plausible sets across T epochs.
- Success = |candidates| <= 1 (sender uniquely identified).
"""
from __future__ import annotations

import json
import math
import random
import time
from collections import defaultdict
from pathlib import Path
from typing import Any

import networkx as nx
import numpy as np

# ---------------------------------------------------------------------------
# Constants (match CCSS-SPECTRAL-01 spec)
# ---------------------------------------------------------------------------

SEED: int = 1574
K_BATCH: int = 128
K_COMPONENTS: int = 8      # max eigenvalues retained (spec: up to 32; 8 for local subgraph)
QUANT_SCALE: int = 1000
TARGET_P_SUCCESS: float = 0.01
OUTPUT_PATH: Path = Path("out/sim_ccss_spectral_cover_sets_results.json")

# ---------------------------------------------------------------------------
# Fingerprint computation
# ---------------------------------------------------------------------------


def local_fingerprint(
    G: nx.Graph,
    node: int,
    hop: int,
    k: int,
    scale: int,
) -> tuple[tuple[int, ...], np.ndarray]:
    """
    Compute local spectral fingerprint for `node` using `hop`-hop neighbourhood.
    Returns (quantized_tuple, continuous_vector).

    2-hop subgraphs are capped at 64 nodes (nearest by graph distance) to
    keep eigendecomposition tractable across large dense graphs.
    """
    if hop == 1:
        nbrs = set(G.neighbors(node)) | {node}
    else:
        # BFS up to 2 hops; cap at 64 nodes to keep eigsh fast
        nbrs = {node}
        for n in G.neighbors(node):
            nbrs.add(n)
            for nn in G.neighbors(n):
                nbrs.add(nn)
                if len(nbrs) >= 64:
                    break
            if len(nbrs) >= 64:
                break

    sub = G.subgraph(nbrs)
    n = sub.number_of_nodes()
    if n < 2:
        cont = np.zeros(k)
        return tuple([0] * k), cont

    L = nx.normalized_laplacian_matrix(sub).toarray().astype(np.float64)
    vals = np.sort(np.linalg.eigvalsh(L))

    # Pad or trim to k components
    if len(vals) >= k:
        cont = vals[:k].copy()
    else:
        cont = np.concatenate([vals, np.zeros(k - len(vals))])

    quantized = tuple(int(math.floor(scale * float(v))) for v in cont)
    return quantized, cont


def precompute_fingerprints(
    G: nx.Graph,
    hop: int,
    k: int = K_COMPONENTS,
    scale: int = QUANT_SCALE,
) -> tuple[dict[int, tuple[int, ...]], dict[int, np.ndarray]]:
    """Return dicts: node -> quantized_fingerprint, node -> continuous_vector."""
    quant: dict[int, tuple[int, ...]] = {}
    cont: dict[int, np.ndarray] = {}
    for node in G.nodes():
        q, c = local_fingerprint(G, node, hop, k, scale)
        quant[node] = q
        cont[node] = c
    return quant, cont


def build_equivalence_classes(
    quant: dict[int, tuple[int, ...]],
) -> dict[tuple[int, ...], list[int]]:
    """Group nodes by quantized fingerprint."""
    classes: dict[tuple[int, ...], list[int]] = defaultdict(list)
    for node, fp in quant.items():
        classes[fp].append(node)
    return dict(classes)


def build_cover_set(
    sender: int,
    quant: dict[int, tuple[int, ...]],
    cont: dict[int, np.ndarray],
    eq_classes: dict[tuple[int, ...], list[int]],
    all_nodes: list[int],
    k_batch: int,
) -> frozenset[int]:
    """
    Build stable cover set for sender:
    1. Start with spectral equivalence class (exact quantized match).
    2. If < k_batch, expand by nearest spectral neighbours (L2 distance).
    3. Always includes sender.
    """
    fp = quant[sender]
    base = set(eq_classes.get(fp, [sender]))
    base.add(sender)

    if len(base) >= k_batch:
        return frozenset(base)

    # Expand with nearest spectral neighbours
    sender_vec = cont[sender]
    pool = [(n, float(np.linalg.norm(cont[n] - sender_vec)))
            for n in all_nodes if n not in base]
    pool.sort(key=lambda x: x[1])
    needed = k_batch - len(base)
    for n, _ in pool[:needed]:
        base.add(n)

    return frozenset(base)


# ---------------------------------------------------------------------------
# Simulation core
# ---------------------------------------------------------------------------


def random_walk(
    adj_list: dict[int, list[int]],
    source: int,
    length: int,
    rng: random.Random,
) -> list[int]:
    path = [source]
    cur = source
    for _ in range(length):
        nbrs = adj_list[cur]
        if not nbrs:
            break
        cur = rng.choice(nbrs)
        path.append(cur)
    return path


def run_trial(
    adj: dict[int, set[int]],
    adj_list: dict[int, list[int]],
    all_nodes: list[int],
    quant: dict[int, tuple[int, ...]],
    cont: dict[int, np.ndarray],
    eq_classes: dict[tuple[int, ...], list[int]],
    T: int,
    L_walk: int,
    k_batch: int,
    rng: random.Random,
) -> tuple[bool, int]:
    """
    Returns (adversary_success, cover_set_size).
    """
    sender = rng.choice(all_nodes)

    # Build stable cover set ONCE — same every epoch
    stable_cover = build_cover_set(
        sender, quant, cont, eq_classes, all_nodes, k_batch
    )

    # Candidates start as full node set
    candidates = set(all_nodes)

    for _ in range(T):
        # Random walk (route rotation per epoch)
        path = random_walk(adj_list, sender, L_walk, rng)
        relays = path[1:]

        # Structural plausible set: neighbours of observed relays
        structural: set[int] = set()
        for relay in relays:
            structural.update(adj[relay])
        structural.add(sender)

        # Epoch plausible set: structural ∪ stable_cover
        # (adversary sees both real and cover bundles, can't distinguish)
        plausible = structural | stable_cover

        candidates &= plausible

        if len(candidates) <= 1:
            break

    success = len(candidates) <= 1
    return success, len(stable_cover)


def run_config(
    N: int,
    p: float,
    T: int,
    L_walk: int,
    hop: int,
    n_trials: int,
    seed: int,
) -> dict[str, Any]:
    rng = random.Random(seed)

    # Build graph
    G = nx.erdos_renyi_graph(N, p, seed=seed)
    while not nx.is_connected(G):
        comps = sorted(nx.connected_components(G), key=len, reverse=True)
        a = rng.choice(list(comps[0]))
        b = rng.choice(list(comps[1]))
        G.add_edge(a, b)

    all_nodes = list(G.nodes())
    adj = {n: set(G.neighbors(n)) for n in all_nodes}
    adj_list = {n: list(G.neighbors(n)) for n in all_nodes}
    avg_deg = sum(len(v) for v in adj.values()) / N

    # Compute λ₂
    if N <= 500:
        L_mat = nx.normalized_laplacian_matrix(G).toarray().astype(np.float64)
        vals = np.linalg.eigvalsh(L_mat)
        lambda2 = float(sorted(vals)[1])
    else:
        try:
            lambda2 = float(nx.algebraic_connectivity(G, method="lanczos", seed=SEED))
        except Exception:
            L_mat = nx.normalized_laplacian_matrix(G).toarray().astype(np.float64)
            vals = np.linalg.eigvalsh(L_mat)
            lambda2 = float(sorted(vals)[1])

    # Precompute spectral fingerprints
    quant, cont_vecs = precompute_fingerprints(G, hop=hop)
    eq_classes = build_equivalence_classes(quant)

    # Equivalence class size stats
    class_sizes = [len(v) for v in eq_classes.values()]
    avg_class = sum(class_sizes) / len(class_sizes)
    frac_covered = sum(
        1 for node in all_nodes
        if len(eq_classes.get(quant[node], [])) >= K_BATCH
    ) / N
    median_class = float(np.median(class_sizes))
    max_class = max(class_sizes)
    n_unique = sum(1 for s in class_sizes if s == 1)

    # Run trials
    successes = 0
    cover_sizes: list[int] = []
    for i in range(n_trials):
        ok, csz = run_trial(
            adj, adj_list, all_nodes,
            quant, cont_vecs, eq_classes,
            T, L_walk, K_BATCH, rng,
        )
        if ok:
            successes += 1
        cover_sizes.append(csz)

    p_success = successes / n_trials
    avg_cover = sum(cover_sizes) / n_trials

    return {
        "N": N,
        "p": round(p, 5),
        "hop": hop,
        "T": T,
        "L_walk": L_walk,
        "lambda2": round(lambda2, 4),
        "avg_deg": round(avg_deg, 2),
        "avg_eq_class_size": round(avg_class, 2),
        "median_eq_class_size": round(median_class, 1),
        "max_eq_class_size": max_class,
        "n_unique_fingerprints": n_unique,
        "n_eq_classes": len(eq_classes),
        "frac_nodes_covered_by_class_gte_kbatch": round(frac_covered, 4),
        "avg_cover_set_size": round(avg_cover, 1),
        "p_success": round(p_success, 4),
        "n_trials": n_trials,
        "successes": successes,
        "target_met": bool(p_success <= TARGET_P_SUCCESS),
    }


# ---------------------------------------------------------------------------
# Sweep
# ---------------------------------------------------------------------------

# Sweep: same N/p grid as Sim 1 where interesting things happened,
# plus extended p values to find the transition point.
CONFIGS: list[tuple[int, float, int, int, int]] = []

# N=500: Sim 1 found failure everywhere. Find the transition.
for p in [0.008, 0.015, 0.025, 0.04, 0.06, 0.10, 0.15, 0.25]:
    for T in [10, 20, 50]:
        for L in [3, 5]:
            for hop in [1, 2]:
                CONFIGS.append((500, p, T, L, hop))

# N=1000: sparse p only (dense is slow for 2-hop even with cap)
for p in [0.004, 0.008, 0.015, 0.025, 0.04]:
    for T in [10, 20, 50]:
        for L in [3, 5]:
            for hop in [1, 2]:
                CONFIGS.append((1000, p, T, L, hop))

# N=2000: 1-hop only at scale
for p in [0.003, 0.006, 0.010, 0.020]:
    for T in [10, 20]:
        for L in [3, 5]:
            CONFIGS.append((2000, p, T, L, 1))

TRIALS_BY_N: dict[int, int] = {500: 300, 1000: 200, 2000: 100}


def main() -> None:
    t0 = time.time()
    total = len(CONFIGS)
    results: list[dict[str, Any]] = []

    print("CCSS Spectral Cover Set SIM v0.1 (Sim 2 + Sim 3)")
    print(f"Seed={SEED}  k_batch={K_BATCH}  target P(success)≤{TARGET_P_SUCCESS}")
    print(f"Configurations: {total}\n")

    for i, (N, p, T, L, hop) in enumerate(CONFIGS):
        n_trials = TRIALS_BY_N[N]
        r = run_config(N, p, T, L, hop, n_trials, SEED + i * 13)
        results.append(r)
        mark = "✓" if r["target_met"] else "✗"
        print(
            f"[{i+1:3d}/{total}] N={N:4d} p={p:.4f} hop={hop} T={T:3d} L={L}"
            f"  λ₂={r['lambda2']:.4f}"
            f"  cls_med={r['median_eq_class_size']:6.1f}"
            f"  cls_max={r['max_eq_class_size']:5d}"
            f"  cov%={r['frac_nodes_covered_by_class_gte_kbatch']:.2f}"
            f"  P(succ)={r['p_success']:.3f}  {mark}"
        )

    elapsed = round(time.time() - t0, 1)

    # -----------------------------------------------------------------------
    # Summary: transition point analysis
    # -----------------------------------------------------------------------
    print(f"\n{'='*80}")
    print("  TRANSITION ANALYSIS: first λ₂ where target is met per (N, T, L, hop)")
    print(f"{'='*80}")

    for N in [500, 1000, 2000]:
        for hop in [1, 2]:
            for L in [3, 5]:
                for T in [10, 20, 50]:
                    sub = sorted(
                        [r for r in results
                         if r["N"] == N and r["T"] == T
                         and r["L_walk"] == L and r["hop"] == hop],
                        key=lambda r: r["lambda2"],
                    )
                    if not sub:
                        continue
                    passing = [r for r in sub if r["target_met"]]
                    if passing:
                        first = passing[0]
                        print(
                            f"  N={N:4d} hop={hop} L={L} T={T:3d}:"
                            f"  λ₂≥{first['lambda2']:.4f}"
                            f"  deg≥{first['avg_deg']:.1f}"
                            f"  class_med={first['median_eq_class_size']:.1f}"
                            f"  covered={first['frac_nodes_covered_by_class_gte_kbatch']:.2f}"
                            f"  P(succ)={first['p_success']:.4f}"
                        )
                    else:
                        print(f"  N={N:4d} hop={hop} L={L} T={T:3d}:  n/a (no passing config in sweep)")

    # -----------------------------------------------------------------------
    # Key class-size table across N and p (1-hop, T=20, L=3)
    # -----------------------------------------------------------------------
    print(f"\n{'='*80}")
    print("  EQUIVALENCE CLASS SIZES  (hop=1, T=20, L=3)")
    print(f"{'='*80}")
    print(f"  {'N':>5}  {'p':>7}  {'λ₂':>7}  {'deg':>5}  {'med_cls':>8}  "
          f"{'max_cls':>8}  {'n_uniq':>7}  {'cov%':>6}  {'P(suc)':>7}  pass")
    print("  " + "-"*75)
    for r in results:
        if r["hop"] == 1 and r["T"] == 20 and r["L_walk"] == 3:
            mark = "✓" if r["target_met"] else "✗"
            print(
                f"  {r['N']:>5}  {r['p']:>7.4f}  {r['lambda2']:>7.4f}  "
                f"{r['avg_deg']:>5.1f}  {r['median_eq_class_size']:>8.1f}  "
                f"{r['max_eq_class_size']:>8d}  {r['n_unique_fingerprints']:>7d}  "
                f"{r['frac_nodes_covered_by_class_gte_kbatch']:>6.2f}  "
                f"{r['p_success']:>7.4f}  {mark}"
            )

    # -----------------------------------------------------------------------
    # 1-hop vs 2-hop comparison
    # -----------------------------------------------------------------------
    print(f"\n{'='*80}")
    print("  1-HOP vs 2-HOP FINGERPRINT COMPARISON (T=20, L=3)")
    print(f"  Shows how many more equivalence classes the 2-hop double-Laplacian gives")
    print(f"{'='*80}")
    print(f"  {'N':>5}  {'p':>7}  {'λ₂':>7}  {'1h med_cls':>11}  "
          f"{'2h med_cls':>11}  {'1h cov%':>8}  {'2h cov%':>8}  "
          f"{'1h P(s)':>8}  {'2h P(s)':>8}")
    print("  " + "-"*85)
    for N in [500, 1000]:
        ps = sorted({r["p"] for r in results if r["N"] == N and r["hop"] == 1 and r["T"] == 20 and r["L_walk"] == 3})
        for p in ps:
            r1 = next((r for r in results if r["N"] == N and r["p"] == p and r["hop"] == 1 and r["T"] == 20 and r["L_walk"] == 3), None)
            r2 = next((r for r in results if r["N"] == N and r["p"] == p and r["hop"] == 2 and r["T"] == 20 and r["L_walk"] == 3), None)
            if r1 and r2:
                print(
                    f"  {N:>5}  {p:>7.4f}  {r1['lambda2']:>7.4f}"
                    f"  {r1['median_eq_class_size']:>11.1f}"
                    f"  {r2['median_eq_class_size']:>11.1f}"
                    f"  {r1['frac_nodes_covered_by_class_gte_kbatch']:>8.2f}"
                    f"  {r2['frac_nodes_covered_by_class_gte_kbatch']:>8.2f}"
                    f"  {r1['p_success']:>8.4f}"
                    f"  {r2['p_success']:>8.4f}"
                )

    output: dict[str, Any] = {
        "sim_id": "sim_ccss_spectral_cover_sets_v0.1",
        "seed": SEED,
        "k_batch": K_BATCH,
        "k_components": K_COMPONENTS,
        "quant_scale": QUANT_SCALE,
        "target_p_success": TARGET_P_SUCCESS,
        "model_notes": (
            "Stable spectral-equivalence-class cover sets. "
            "candidates = stable_cover ∪ ∩_t structural_t. "
            "Adversary confined to cover set size. "
            "Relay-level adversary only."
        ),
        "elapsed_seconds": elapsed,
        "results": results,
    }
    OUTPUT_PATH.parent.mkdir(exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(output, indent=2))
    print(f"\nElapsed: {elapsed}s")
    print(f"Results written to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
