#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
"""
SIM: CCSS Spectral Fiedler Intersection Resistance v0.2
Phase: research / forward-planning (Window 1576+ lane)
Seed: 1574

Research question
-----------------
What minimum Fiedler value λ₂ is required to defeat intersection attacks
against CCSS-SPECTRAL-01 relay routing, as a function of network size N,
adversary observation epochs T, and relay walk length L?

Model
-----
Sender routes each message through an independent random walk of L hops
(route rotation per epoch, as required by ccss_pre_rc_cover_batch_profile_v1).

Adversary capability (relay-level, NOT global passive observer):
  - Observes which relay nodes forwarded at least one bundle in epoch t.
  - Infers plausible senders as all nodes adjacent to any observed relay
    (1-hop attribution: sender must be a neighbor of the first relay it
    contacts — standard for unauthenticated gossip).
  - Batch anonymity floor: plausible set always padded to >= k_batch = 128
    (from ccss_pre_rc_cover_batch_profile_v1_candidate).
  - After T epochs, intersects all T plausible sender sets.
  - Succeeds when |intersection| == 1 (sender uniquely identified).

Key physics
-----------
  High λ₂ (well-connected) → large per-epoch plausible sets →
    intersection stays large → adversary fails.
  Low λ₂ (sparse graph) → small plausible sets →
    intersection converges quickly → adversary succeeds.

The simulation sweeps (N, edge_probability → λ₂, T, L) and records
P(adversary success), then extracts the minimum λ₂ threshold for each
(N, T, L) tuple at which the target P ≤ 0.01 is first met.

Non-claims
----------
This simulation does not prove formal anonymity, DP, or unlinkability.
It does not activate CCSS-SPECTRAL-01 runtime or any guard.
It is evidence toward the "Fiedler-bounded intersection resistance"
framework described in the Window 1576+ forward plan.
"""
from __future__ import annotations

import json
import random
import time
from pathlib import Path
from typing import Any

import networkx as nx
import numpy as np
from scipy.sparse.linalg import eigsh

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SEED: int = 1574
K_BATCH: int = 128          # from ccss_pre_rc_cover_batch_profile_v1_candidate
TARGET_P_SUCCESS: float = 0.01
OUTPUT_PATH: Path = Path("out/sim_ccss_fiedler_v0.2_normalized_results.json")

# ---------------------------------------------------------------------------
# Graph utilities
# ---------------------------------------------------------------------------


def make_connected_er_graph(N: int, p: float, seed: int) -> nx.Graph:
    """Erdős-Rényi graph guaranteed connected by adding minimum bridge edges."""
    G = nx.erdos_renyi_graph(N, p, seed=seed)
    rng = random.Random(seed ^ 0xDEAD_BEEF)
    while not nx.is_connected(G):
        comps = sorted(nx.connected_components(G), key=len, reverse=True)
        a = rng.choice(list(comps[0]))
        b = rng.choice(list(comps[1]))
        G.add_edge(a, b)
    return G


def compute_fiedler(G: nx.Graph) -> float:
    """
    Second-smallest eigenvalue of the normalized Laplacian (Fiedler value λ₂).
    The normalized Laplacian has spectrum in [0, 2]; use the same operator
    for every graph size so small-N and large-N rows are comparable.
    """
    N = len(G)
    L = nx.normalized_laplacian_matrix(G).astype(np.float64)
    if N <= 500:
        vals = np.linalg.eigvalsh(L.toarray())
        lam2 = float(sorted(vals)[1])
    else:
        vals = eigsh(L, k=2, which="SM", return_eigenvectors=False, tol=1e-6)
        lam2 = float(sorted(vals)[1])
    assert 0.0 <= lam2 <= 2.0 + 1e-9, f"impossible normalized lambda2={lam2}"
    return lam2


# ---------------------------------------------------------------------------
# Simulation core
# ---------------------------------------------------------------------------


def random_walk(adj_list: dict[int, list[int]], source: int, length: int,
                rng: random.Random) -> list[int]:
    """Random walk of `length` hops; returns full path including source."""
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
    T: int,
    L_walk: int,
    k_batch: int,
    rng: random.Random,
) -> bool:
    """
    Single intersection-attack trial.
    Returns True if adversary successfully identifies sender after T epochs.
    """
    sender = rng.choice(all_nodes)
    candidates: set[int] = set(all_nodes)

    for _ in range(T):
        # Independent random walk per epoch (route rotation)
        path = random_walk(adj_list, sender, L_walk, rng)
        relays = path[1:]  # sender position is unknown to adversary

        # Plausible senders = all nodes adjacent to any observed relay
        plausible: set[int] = set()
        for relay in relays:
            plausible.update(adj[relay])

        # Batch anonymity floor: pad to k_batch if necessary
        if len(plausible) < k_batch:
            needed = k_batch - len(plausible)
            pool = [n for n in all_nodes if n not in plausible]
            plausible.update(rng.sample(pool, min(needed, len(pool))))

        # Sender is always in the plausible set (by definition)
        plausible.add(sender)

        # Intersect with running candidate set
        candidates &= plausible

        # Early termination: adversary already won
        if len(candidates) <= 1:
            return True

    return len(candidates) <= 1


def run_config(
    N: int,
    p: float,
    T: int,
    L_walk: int,
    n_trials: int,
    seed: int,
) -> dict[str, Any]:
    rng = random.Random(seed)
    G = make_connected_er_graph(N, p, seed)
    all_nodes = list(G.nodes())
    adj = {n: set(G.neighbors(n)) for n in all_nodes}
    adj_list = {n: list(G.neighbors(n)) for n in all_nodes}
    lambda2 = compute_fiedler(G)
    avg_deg = sum(len(v) for v in adj.values()) / N

    successes = sum(
        run_trial(adj, adj_list, all_nodes, T, L_walk, K_BATCH, rng)
        for _ in range(n_trials)
    )
    p_success = successes / n_trials
    return {
        "N": N,
        "p": round(p, 5),
        "T": T,
        "L_walk": L_walk,
        "lambda2": round(lambda2, 5),
        "avg_deg": round(avg_deg, 2),
        "p_success": round(p_success, 4),
        "n_trials": n_trials,
        "successes": successes,
        "target_met": bool(p_success <= TARGET_P_SUCCESS),
    }


# ---------------------------------------------------------------------------
# Sweep configuration
# ---------------------------------------------------------------------------

# Edge probabilities chosen to produce a wide range of λ₂ values.
# For G(N, p): expected average degree d = (N-1)*p ≈ N*p.
# λ₂ is roughly proportional to d/N for sparse graphs and approaches 1
# for dense graphs. We want coverage from λ₂ ≈ 0.01 to λ₂ ≈ 0.5+.
PROBS_BY_N: dict[int, list[float]] = {
    100:  [0.03, 0.05, 0.08, 0.13, 0.20, 0.40],   # d ≈  3–40
    500:  [0.008, 0.015, 0.03, 0.06, 0.12, 0.25],  # d ≈  4–125
    1000: [0.004, 0.008, 0.015, 0.03, 0.06, 0.12], # d ≈  4–120
    5000: [0.001, 0.002, 0.004, 0.008, 0.015, 0.03], # d ≈  5–150
}
T_VALUES: list[int] = [10, 20, 50]
L_VALUES: list[int] = [3, 5]

# Fewer trials for large N to keep total runtime reasonable
TRIALS_BY_N: dict[int, int] = {100: 400, 500: 300, 1000: 200, 5000: 100}


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    t0 = time.time()

    sweep: list[tuple[int, float, int, int]] = [
        (N, p, T, L)
        for N, probs in PROBS_BY_N.items()
        for p in probs
        for T in T_VALUES
        for L in L_VALUES
    ]
    total = len(sweep)
    results: list[dict[str, Any]] = []

    print("CCSS Fiedler Intersection Resistance SIM v0.2 normalized")
    print(f"Seed={SEED}  k_batch={K_BATCH}  target P(success)≤{TARGET_P_SUCCESS}")
    print(f"Configurations: {total}\n")

    for i, (N, p, T, L) in enumerate(sweep):
        n_trials = TRIALS_BY_N[N]
        r = run_config(N, p, T, L, n_trials, SEED + i * 7)
        results.append(r)
        mark = "✓" if r["target_met"] else "✗"
        print(
            f"[{i+1:3d}/{total}] N={N:5d} p={p:.4f} T={T:3d} L={L}"
            f"  λ₂={r['lambda2']:.4f}  deg={r['avg_deg']:6.1f}"
            f"  P(succ)={r['p_success']:.3f}  {mark}"
        )

    # -----------------------------------------------------------------------
    # Summary: minimum λ₂ for target per (N, T, L)
    # -----------------------------------------------------------------------
    summary: dict[str, Any] = {}
    for N in PROBS_BY_N:
        for T in T_VALUES:
            for L in L_VALUES:
                sub = sorted(
                    [r for r in results
                     if r["N"] == N and r["T"] == T and r["L_walk"] == L],
                    key=lambda r: r["lambda2"],
                )
                min_lam = next(
                    (r["lambda2"] for r in sub if r["target_met"]), None
                )
                summary[f"N={N}_T={T}_L={L}"] = {
                    "min_lambda2": min_lam,
                    "curve": [
                        {"lambda2": r["lambda2"], "avg_deg": r["avg_deg"],
                         "p_success": r["p_success"]}
                        for r in sub
                    ],
                }

    elapsed = round(time.time() - t0, 1)
    output: dict[str, Any] = {
        "sim_id": "sim_ccss_fiedler_v0.2_normalized",
        "supersedes": "out/sim_ccss_fiedler_intersection_resistance_results.json",
        "seed": SEED,
        "k_batch": K_BATCH,
        "target_p_success": TARGET_P_SUCCESS,
        "model_notes": (
            "1-hop relay attribution; route rotation per epoch; "
            "batch floor k_batch=128; relay-level adversary only "
            "(not global passive observer)."
        ),
        "elapsed_seconds": elapsed,
        "results": results,
        "summary": summary,
    }
    OUTPUT_PATH.parent.mkdir(exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(output, indent=2, sort_keys=True, allow_nan=False))

    # -----------------------------------------------------------------------
    # Print summary table
    # -----------------------------------------------------------------------
    print(f"\n{'='*65}")
    print(f"  Minimum λ₂ for P(adversary success) ≤ {TARGET_P_SUCCESS}")
    print(f"  Model: relay-level adversary, 1-hop attribution, k_batch={K_BATCH}")
    print(f"{'='*65}")

    # Print as table: rows = (N, L), cols = T
    print(f"{'N':>6}  {'L':>4}  {'T=10':>10}  {'T=20':>10}  {'T=50':>10}")
    print("-" * 55)
    for N in PROBS_BY_N:
        for L in L_VALUES:
            row = [f"{N:>6}  {L:>4}"]
            for T in T_VALUES:
                val = summary[f"N={N}_T={T}_L={L}"]["min_lambda2"]
                row.append(f"{val:.4f}    " if val is not None else "  n/a      ")
            print("  ".join(row))
        print()

    print(f"\nElapsed: {elapsed}s")
    print(f"Results written to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
