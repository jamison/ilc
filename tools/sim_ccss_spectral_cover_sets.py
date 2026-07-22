#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
"""
SIM 2+3: CCSS Spectral Equivalence-Class Cover Sets v0.2
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
from scipy.sparse.linalg import eigsh

# ---------------------------------------------------------------------------
# Constants (match CCSS-SPECTRAL-01 spec)
# ---------------------------------------------------------------------------

SEED: int = 1574
K_BATCH: int = 128
K_COMPONENTS: int = 8      # max eigenvalues retained (spec: up to 32; 8 for local subgraph)
QUANT_SCALE: int = 1000
TARGET_P_SUCCESS: float = 0.01
OUTPUT_PATH: Path = Path("out/sim_ccss_spectral_cover_v0.2_adversary_taxonomy_results.json")
ADVERSARY_RELAY_LABELABLE: str = "relay_level_intersection_relay_labelable_cover"
ADVERSARY_SENDER_GENERATED: str = "relay_level_intersection_sender_generated_cover"
_GRAPH_CONTEXT_CACHE: dict[tuple[int, float, int], dict[str, Any]] = {}

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

    sub = G.subgraph(nbrs).copy()
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


def compute_normalized_fiedler(G: nx.Graph) -> float:
    """Return λ₂ for the normalized Laplacian; the valid range is [0, 2]."""
    n = len(G)
    laplacian = nx.normalized_laplacian_matrix(G).astype(np.float64)
    if n <= 500:
        vals = np.linalg.eigvalsh(laplacian.toarray())
        lam2 = float(sorted(vals)[1])
    else:
        vals = eigsh(laplacian, k=2, which="SM", return_eigenvectors=False, tol=1e-6)
        lam2 = float(sorted(vals)[1])
    assert 0.0 <= lam2 <= 2.0 + 1e-9, f"impossible normalized lambda2={lam2}"
    return lam2


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
    cover_sets: dict[int, frozenset[int]],
    T: int,
    L_walk: int,
    rng: random.Random,
) -> tuple[bool, int, int]:
    """
    Returns (adversary_success, cover_set_size, final_candidate_set_size).
    """
    sender = rng.choice(all_nodes)

    # Build stable cover set ONCE — same every epoch
    stable_cover = cover_sets[sender]

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
    return success, len(stable_cover), len(candidates)


def run_trial_relay_labelable_cover(
    adj: dict[int, set[int]],
    adj_list: dict[int, list[int]],
    all_nodes: list[int],
    T: int,
    L_walk: int,
    rng: random.Random,
) -> tuple[bool, int]:
    """
    Malicious-relay model: relay can label and discard cover bundles.
    Stable cover therefore provides no protection; only structural plausible
    senders remain in each epoch before intersection.
    """
    sender = rng.choice(all_nodes)
    candidates = set(all_nodes)
    for _ in range(T):
        path = random_walk(adj_list, sender, L_walk, rng)
        structural: set[int] = set()
        for relay in path[1:]:
            structural.update(adj[relay])
        structural.add(sender)
        candidates &= structural
        if len(candidates) <= 1:
            break
    return len(candidates) <= 1, len(candidates)


def run_cohort_linkability_trial(
    adj: dict[int, set[int]],
    adj_list: dict[int, list[int]],
    cover_sets: dict[int, frozenset[int]],
    all_nodes: list[int],
    T: int,
    L_walk: int,
    k_batch: int,
    rng: random.Random,
) -> bool:
    """
    Sender-generated-cover cohort test: can the adversary reduce repeated
    participation to a cohort smaller than one quarter of the anonymity floor?
    """
    cohort_threshold = k_batch // 4
    sender = rng.choice(all_nodes)
    stable = cover_sets[sender]
    candidates = set(all_nodes)
    for _ in range(T):
        path = random_walk(adj_list, sender, L_walk, rng)
        structural: set[int] = set()
        for relay in path[1:]:
            structural.update(adj[relay])
        structural.add(sender)
        candidates &= structural | stable
        if len(candidates) <= cohort_threshold:
            break
    return len(candidates) <= cohort_threshold


def _candidate_metrics(
    candidate_sizes: list[int],
    n_trials: int,
) -> dict[str, Any]:
    return {
        "guessing_advantage": round(
            sum(1.0 / max(s, 1) for s in candidate_sizes) / n_trials, 5
        ),
        "median_candidate_size": float(np.median(candidate_sizes)),
        "p_candidates_below_k": round(
            sum(1 for s in candidate_sizes if s < K_BATCH) / n_trials, 4
        ),
    }


def _get_graph_context(
    N: int,
    p: float,
    hop: int,
    seed: int,
) -> dict[str, Any]:
    """Build or return the deterministic graph/fingerprint context."""
    key = (N, p, hop)
    cached = _GRAPH_CONTEXT_CACHE.get(key)
    if cached is not None:
        return cached

    rng = random.Random(seed)
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
    lambda2 = compute_normalized_fiedler(G)

    quant, cont_vecs = precompute_fingerprints(G, hop=hop)
    eq_classes = build_equivalence_classes(quant)
    cover_sets = {
        node: build_cover_set(node, quant, cont_vecs, eq_classes, all_nodes, K_BATCH)
        for node in all_nodes
    }

    class_sizes = [len(v) for v in eq_classes.values()]
    context: dict[str, Any] = {
        "all_nodes": all_nodes,
        "adj": adj,
        "adj_list": adj_list,
        "quant": quant,
        "cont_vecs": cont_vecs,
        "eq_classes": eq_classes,
        "cover_sets": cover_sets,
        "lambda2": lambda2,
        "avg_deg": avg_deg,
        "avg_eq_class_size": sum(class_sizes) / len(class_sizes),
        "median_eq_class_size": float(np.median(class_sizes)),
        "max_eq_class_size": max(class_sizes),
        "n_unique_fingerprints": sum(1 for s in class_sizes if s == 1),
        "n_eq_classes": len(eq_classes),
        "frac_nodes_covered_by_class_gte_kbatch": (
            sum(
                1 for node in all_nodes
                if len(eq_classes.get(quant[node], [])) >= K_BATCH
            ) / N
        ),
        "graph_seed": seed,
    }
    _GRAPH_CONTEXT_CACHE[key] = context
    return context


def _graph_seed_for_context(N: int, p: float, hop: int) -> int:
    """Stable per-context seed; never use Python hash randomization."""
    return SEED + N * 101 + int(round(p * 1_000_000)) * 17 + hop * 1009


def run_config(
    N: int,
    p: float,
    T: int,
    L_walk: int,
    hop: int,
    n_trials: int,
    seed: int,
) -> list[dict[str, Any]]:
    rng = random.Random(seed)
    context = _get_graph_context(N, p, hop, _graph_seed_for_context(N, p, hop))
    all_nodes = context["all_nodes"]
    adj = context["adj"]
    adj_list = context["adj_list"]
    cover_sets = context["cover_sets"]

    # Run relay-labelable-cover trials (Model A)
    labelable_successes = 0
    labelable_candidate_sizes: list[int] = []
    for _ in range(n_trials):
        ok, candidate_size = run_trial_relay_labelable_cover(
            adj, adj_list, all_nodes, T, L_walk, rng
        )
        if ok:
            labelable_successes += 1
        labelable_candidate_sizes.append(candidate_size)

    # Run sender-generated-cover trials (Model B)
    sender_generated_successes = 0
    cover_sizes: list[int] = []
    sender_generated_candidate_sizes: list[int] = []
    cohort_linkable_count = 0
    for _ in range(n_trials):
        ok, csz, candidate_size = run_trial(
            adj, adj_list, all_nodes,
            cover_sets,
            T, L_walk, rng,
        )
        if ok:
            sender_generated_successes += 1
        cover_sizes.append(csz)
        sender_generated_candidate_sizes.append(candidate_size)
        if run_cohort_linkability_trial(
            adj, adj_list, cover_sets,
            all_nodes, T, L_walk, K_BATCH, rng,
        ):
            cohort_linkable_count += 1

    labelable_p_success = labelable_successes / n_trials
    sender_generated_p_success = sender_generated_successes / n_trials
    avg_cover = sum(cover_sizes) / n_trials

    shared = {
        "N": N,
        "p": round(p, 5),
        "hop": hop,
        "T": T,
        "L_walk": L_walk,
        "lambda2": round(context["lambda2"], 4),
        "avg_deg": round(context["avg_deg"], 2),
        "avg_eq_class_size": round(context["avg_eq_class_size"], 2),
        "median_eq_class_size": round(context["median_eq_class_size"], 1),
        "max_eq_class_size": context["max_eq_class_size"],
        "n_unique_fingerprints": context["n_unique_fingerprints"],
        "n_eq_classes": context["n_eq_classes"],
        "frac_nodes_covered_by_class_gte_kbatch": round(
            context["frac_nodes_covered_by_class_gte_kbatch"], 4
        ),
        "graph_seed": context["graph_seed"],
        "n_trials": n_trials,
    }
    labelable = {
        **shared,
        "adversary_class": ADVERSARY_RELAY_LABELABLE,
        "avg_cover_set_size": 0.0,
        "p_success": round(labelable_p_success, 4),
        "successes": labelable_successes,
        "target_met": bool(labelable_p_success <= TARGET_P_SUCCESS),
        "p_cohort_linkable": round(
            sum(1 for s in labelable_candidate_sizes if s <= K_BATCH // 4) / n_trials,
            4,
        ),
        **_candidate_metrics(labelable_candidate_sizes, n_trials),
    }
    sender_generated = {
        **shared,
        "adversary_class": ADVERSARY_SENDER_GENERATED,
        "avg_cover_set_size": round(avg_cover, 1),
        "p_success": round(sender_generated_p_success, 4),
        "successes": sender_generated_successes,
        "target_met": bool(sender_generated_p_success <= TARGET_P_SUCCESS),
        "p_cohort_linkable": round(cohort_linkable_count / n_trials, 4),
        **_candidate_metrics(sender_generated_candidate_sizes, n_trials),
    }
    return [labelable, sender_generated]


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

    print("CCSS Spectral Cover Set SIM v0.2 adversary taxonomy")
    print(f"Seed={SEED}  k_batch={K_BATCH}  target P(success)≤{TARGET_P_SUCCESS}")
    print(f"Configurations: {total}\n")

    for i, (N, p, T, L, hop) in enumerate(CONFIGS):
        n_trials = TRIALS_BY_N[N]
        config_results = run_config(N, p, T, L, hop, n_trials, SEED + i * 13)
        results.extend(config_results)
        labelable = next(
            r for r in config_results if r["adversary_class"] == ADVERSARY_RELAY_LABELABLE
        )
        sender_generated = next(
            r for r in config_results if r["adversary_class"] == ADVERSARY_SENDER_GENERATED
        )
        mark = "✓" if sender_generated["target_met"] else "✗"
        print(
            f"[{i+1:3d}/{total}] N={N:4d} p={p:.4f} hop={hop} T={T:3d} L={L}"
            f"  λ₂={sender_generated['lambda2']:.4f}"
            f"  cls_med={sender_generated['median_eq_class_size']:6.1f}"
            f"  cls_max={sender_generated['max_eq_class_size']:5d}"
            f"  cov%={sender_generated['frac_nodes_covered_by_class_gte_kbatch']:.2f}"
            f"  P(labelable)={labelable['p_success']:.3f}"
            f"  P(sender-gen)={sender_generated['p_success']:.3f}  {mark}",
            flush=True,
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
                         and r["L_walk"] == L and r["hop"] == hop
                         and r["adversary_class"] == ADVERSARY_SENDER_GENERATED],
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
          f"{'max_cls':>8}  {'n_uniq':>7}  {'cov%':>6}  {'P(A)':>7}  "
          f"{'P(B)':>7}  {'guess_B':>8}  pass")
    print("  " + "-"*92)
    for r in results:
        if (
            r["hop"] == 1
            and r["T"] == 20
            and r["L_walk"] == 3
            and r["adversary_class"] == ADVERSARY_SENDER_GENERATED
        ):
            labelable = next(
                x for x in results
                if x["N"] == r["N"]
                and x["p"] == r["p"]
                and x["hop"] == r["hop"]
                and x["T"] == r["T"]
                and x["L_walk"] == r["L_walk"]
                and x["adversary_class"] == ADVERSARY_RELAY_LABELABLE
            )
            mark = "✓" if r["target_met"] else "✗"
            print(
                f"  {r['N']:>5}  {r['p']:>7.4f}  {r['lambda2']:>7.4f}  "
                f"{r['avg_deg']:>5.1f}  {r['median_eq_class_size']:>8.1f}  "
                f"{r['max_eq_class_size']:>8d}  {r['n_unique_fingerprints']:>7d}  "
                f"{r['frac_nodes_covered_by_class_gte_kbatch']:>6.2f}  "
                f"{labelable['p_success']:>7.4f}  {r['p_success']:>7.4f}  "
                f"{r['guessing_advantage']:>8.5f}  {mark}"
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
        ps = sorted({
            r["p"] for r in results
            if r["N"] == N
            and r["hop"] == 1
            and r["T"] == 20
            and r["L_walk"] == 3
            and r["adversary_class"] == ADVERSARY_SENDER_GENERATED
        })
        for p in ps:
            r1 = next((r for r in results if r["N"] == N and r["p"] == p and r["hop"] == 1 and r["T"] == 20 and r["L_walk"] == 3 and r["adversary_class"] == ADVERSARY_SENDER_GENERATED), None)
            r2 = next((r for r in results if r["N"] == N and r["p"] == p and r["hop"] == 2 and r["T"] == 20 and r["L_walk"] == 3 and r["adversary_class"] == ADVERSARY_SENDER_GENERATED), None)
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
        "sim_id": "sim_ccss_spectral_cover_v0.2_adversary_taxonomy",
        "supersedes": "out/sim_ccss_spectral_cover_sets_results.json",
        "seed": SEED,
        "k_batch": K_BATCH,
        "k_components": K_COMPONENTS,
        "quant_scale": QUANT_SCALE,
        "target_p_success": TARGET_P_SUCCESS,
        "model_notes": (
            "Stable spectral-equivalence-class cover sets. "
            "candidates = stable_cover ∪ ∩_t structural_t. "
            "Adversary confined to cover set size. "
            "Model A relay-labelable cover strips cover from the plausible set. "
            "Model B sender-generated cover assumes relay cannot label cover."
        ),
        "adversary_taxonomy": [
            "external_batch_observer",
            "relay_level_intersection",
            "honest_relay",
            "malicious_relay",
            "source_edge_gpo",
            "multi_epoch_gpo",
        ],
        "elapsed_seconds": elapsed,
        "results": results,
    }
    OUTPUT_PATH.parent.mkdir(exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(output, indent=2, sort_keys=True, allow_nan=False))
    print(f"\nElapsed: {elapsed}s")
    print(f"Results written to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
