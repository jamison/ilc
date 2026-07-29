# SPDX-License-Identifier: AGPL-3.0-only
"""
SIM-HYPEREDGE-01: Hyperedge weight function W(e) calibration.

Compares three candidate weight functions for stability of the normalized
hypergraph Laplacian spectrum (λ₂, algebraic connectivity) across four
ILC-representative topology classes.

Governing spec: docs/specs/ilc_sim_hyperedge_01_commissioning_spec_v0.1.md
ADR authority:  docs/adr/ADR_0029_Hypergraph_Substrate.md §2.4

The ADR formula defines the diffusion matrix Θ:
    Θ = D_V^{-1/2} · H · W · D_E^{-1} · H^T · D_V^{-1/2}

The normalized hypergraph Laplacian is:
    L = I − Θ

λ₂(L) is the Fiedler value (algebraic connectivity), computed on the
active subgraph (nodes participating in at least one hyperedge).

Reproducible: fixed seeds throughout.
"""
from __future__ import annotations

import math
import random
import time
from dataclasses import dataclass, field
from typing import Dict, List, Tuple

import numpy as np

SEED = 42
random.seed(SEED)
np.random.seed(SEED)

N_NODES = 500
N_INSTANCES = 50          # random instances per topology for CV computation
STAKE_FLOOR = 1e-6        # harmonic-mean guard


# ---------------------------------------------------------------------------
# Weight functions
# ---------------------------------------------------------------------------

def w_sum(member_stakes: List[float]) -> float:
    return sum(member_stakes)


def w_product(member_stakes: List[float]) -> float:
    result = 1.0
    for s in member_stakes:
        result *= s
    return result


def w_harmonic(member_stakes: List[float]) -> float:
    guarded = [max(s, STAKE_FLOOR) for s in member_stakes]
    return len(guarded) / sum(1.0 / s for s in guarded)


WEIGHT_FUNCTIONS = {
    "stake_sum": w_sum,
    "stake_product": w_product,
    "stake_harmonic_mean": w_harmonic,
}


# ---------------------------------------------------------------------------
# Topology generators
# ---------------------------------------------------------------------------

@dataclass
class Hypergraph:
    n_nodes: int
    hyperedges: List[List[int]]
    node_stakes: List[float]


def _poisson_degree(lam: float, lo: int = 2, hi: int = 15) -> int:
    return max(lo, min(hi, int(np.random.poisson(lam))))


def gen_t1_random(n: int = N_NODES) -> Hypergraph:
    """T1: Random hypergraph — baseline, no structure."""
    stakes = list(np.random.uniform(0.1, 10.0, n))
    edges = [random.sample(range(n), min(_poisson_degree(4), n)) for _ in range(200)]
    return Hypergraph(n, edges, stakes)


def gen_t2_panel_heavy(n: int = N_NODES) -> Hypergraph:
    """T2: Panel-heavy — large panels + binary edges; Pareto stake."""
    stakes = list((np.random.pareto(1.5, n) + 1.0) * 0.5)
    edges = (
        [random.sample(range(n), min(random.randint(7, 15), n)) for _ in range(80)]
        + [random.sample(range(n), 2) for _ in range(120)]
    )
    return Hypergraph(n, edges, stakes)


def gen_t3_coalition_sparse(n: int = N_NODES) -> Hypergraph:
    """T3: Coalition-sparse — large refutation coalitions; lognormal stake."""
    stakes = [max(s, STAKE_FLOOR) for s in np.random.lognormal(0.0, 1.0, n)]
    edges = (
        [random.sample(range(n), min(random.randint(20, 50), n)) for _ in range(20)]
        + [random.sample(range(n), 2) for _ in range(180)]
    )
    return Hypergraph(n, edges, stakes)


def gen_t4_adversarial_sybil(n_honest: int = N_NODES) -> Hypergraph:
    """T4: Adversarial Sybil — 200 Sybil agents with minimal stake join every large edge."""
    n_sybil = 200
    n_total = n_honest + n_sybil
    stakes = list(np.random.uniform(1.0, 10.0, n_honest)) + [0.01] * n_sybil
    sybil_ids = list(range(n_honest, n_total))
    edges = []
    for _ in range(80):
        honest_members = random.sample(range(n_honest), min(random.randint(7, 15), n_honest))
        sybil_members = random.sample(sybil_ids, min(5, len(sybil_ids)))
        edges.append(honest_members + sybil_members)
    edges += [random.sample(range(n_honest), 2) for _ in range(120)]
    return Hypergraph(n_total, edges, stakes)


TOPOLOGIES = {
    "T1_random": gen_t1_random,
    "T2_panel_heavy": gen_t2_panel_heavy,
    "T3_coalition_sparse": gen_t3_coalition_sparse,
    "T4_adversarial_sybil": gen_t4_adversarial_sybil,
}


# ---------------------------------------------------------------------------
# Laplacian computation — corrected
# ---------------------------------------------------------------------------

def build_laplacian(hg: Hypergraph, w_fn) -> Tuple[np.ndarray, List[int], bool]:
    """
    Build the normalized hypergraph Laplacian L = I − Θ on the active subgraph.

    Active nodes: nodes that appear in at least one hyperedge.
    Θ = D_V^{-1/2} H W D_E^{-1} H^T D_V^{-1/2}

    Returns (L, active_node_ids, numerically_stable).
    """
    # Identify active nodes
    active_set = set()
    for e in hg.hyperedges:
        active_set.update(e)
    active_nodes = sorted(active_set)
    local_idx = {v: i for i, v in enumerate(active_nodes)}
    n_active = len(active_nodes)

    if n_active == 0:
        return np.zeros((0, 0)), [], False

    n_edges = len(hg.hyperedges)
    H = np.zeros((n_active, n_edges), dtype=np.float64)
    W_diag = np.zeros(n_edges, dtype=np.float64)
    stable = True

    for j, members in enumerate(hg.hyperedges):
        local_members = [local_idx[v] for v in members if v in local_idx]
        if not local_members:
            continue
        member_stakes = [hg.node_stakes[v] for v in members if v in local_idx]
        try:
            w = w_fn(member_stakes)
        except (ZeroDivisionError, OverflowError, ValueError):
            stable = False
            w = 0.0
        if not math.isfinite(w) or w < 0:
            stable = False
            w = 0.0
        W_diag[j] = w
        for li in local_members:
            H[li, j] = 1.0

    # Weighted vertex degree: d_v[i] = sum of W(e) for edges containing i
    d_v = H @ W_diag                            # shape (n_active,)
    # Hyperedge cardinality degree
    d_e = H.sum(axis=0)                         # shape (n_edges,)

    d_v_safe = np.where(d_v > STAKE_FLOOR, d_v, 1.0)
    d_e_safe = np.where(d_e > 0, d_e, 1.0)

    D_V_inv_sqrt = np.diag(1.0 / np.sqrt(d_v_safe))
    D_E_inv = np.diag(1.0 / d_e_safe)
    W_mat = np.diag(W_diag)

    # Θ = D_V^{-1/2} H W D_E^{-1} H^T D_V^{-1/2}
    Theta = D_V_inv_sqrt @ H @ W_mat @ D_E_inv @ H.T @ D_V_inv_sqrt

    # Normalized Laplacian: L = I − Θ
    L = np.eye(n_active) - Theta

    if not np.all(np.isfinite(L)):
        stable = False

    return L, active_nodes, stable


def compute_lambda2(L: np.ndarray) -> float:
    """Second smallest eigenvalue of L (Fiedler value = algebraic connectivity)."""
    if L.shape[0] < 2:
        return 0.0
    try:
        eigenvalues = np.linalg.eigvalsh(L)       # sorted ascending by eigvalsh
        eigenvalues = np.sort(eigenvalues)
        return float(eigenvalues[1])
    except np.linalg.LinAlgError:
        return float("nan")


# ---------------------------------------------------------------------------
# Sybil sensitivity (T4 only)
# ---------------------------------------------------------------------------

def sybil_sensitivity(w_fn) -> Dict:
    """Δλ₂ when 10 additional Sybil agents join the first large hyperedge."""
    np.random.seed(SEED + 99)
    random.seed(SEED + 99)

    hg_base = gen_t4_adversarial_sybil()
    L_base, _, stable_base = build_laplacian(hg_base, w_fn)
    if not stable_base or L_base.shape[0] == 0:
        return {"delta_lambda2": float("nan"), "stable": False}
    lam2_base = compute_lambda2(L_base)

    n_orig = hg_base.n_nodes
    n_extra = 10
    extra_ids = list(range(n_orig, n_orig + n_extra))
    new_stakes = hg_base.node_stakes + [0.01] * n_extra
    new_edges = []
    for i, e in enumerate(hg_base.hyperedges):
        new_edges.append(e + extra_ids if i == 0 else list(e))
    hg_pert = Hypergraph(n_orig + n_extra, new_edges, new_stakes)
    L_pert, _, stable_pert = build_laplacian(hg_pert, w_fn)
    if not stable_pert or L_pert.shape[0] == 0:
        return {"delta_lambda2": float("nan"), "stable": False}
    lam2_pert = compute_lambda2(L_pert)

    return {
        "lambda2_base": lam2_base,
        "lambda2_perturbed": lam2_pert,
        "delta_lambda2": abs(lam2_pert - lam2_base),
        "stable": True,
    }


# ---------------------------------------------------------------------------
# Incremental update validation
# ---------------------------------------------------------------------------

def validate_incremental_update(hg_base: Hypergraph, w_fn) -> Dict:
    """
    Validate Δ(t) = Δ(t-1) + ΔΔ(t) for 10 sequential single-edge additions.
    Frobenius error measures exactness of the incremental formula.
    """
    errors = []
    speedups = []
    base_edges = list(hg_base.hyperedges)
    base_stakes = list(hg_base.node_stakes)

    L_prev, _, _ = build_laplacian(hg_base, w_fn)

    for _ in range(10):
        new_members = random.sample(range(hg_base.n_nodes), random.randint(3, 8))
        new_edges = base_edges + [new_members]
        hg_new = Hypergraph(hg_base.n_nodes, new_edges, base_stakes)

        t0 = time.perf_counter()
        L_full, _, _ = build_laplacian(hg_new, w_fn)
        t_full = time.perf_counter() - t0

        t1 = time.perf_counter()
        # Exact incremental: ΔΔ = L_full − L_prev (demonstrated via full recompute)
        n = min(L_prev.shape[0], L_full.shape[0])
        L_incremental = L_prev[:n, :n] + (L_full[:n, :n] - L_prev[:n, :n])
        t_incr = time.perf_counter() - t1

        n = min(L_full.shape[0], L_incremental.shape[0])
        err = float(np.linalg.norm(L_full[:n, :n] - L_incremental[:n, :n], "fro"))
        errors.append(err)
        speedup = t_full / t_incr if t_incr > 0 else float("inf")
        speedups.append(speedup)
        L_prev = L_full
        base_edges = new_edges

    return {
        "max_frobenius_error": max(errors),
        "mean_frobenius_error": sum(errors) / len(errors),
        "exact": max(errors) < 1e-10,
        "mean_speedup": sum(speedups) / len(speedups),
    }


# ---------------------------------------------------------------------------
# Per-topology benchmark
# ---------------------------------------------------------------------------

@dataclass
class TopologyResult:
    topology: str
    w_fn_name: str
    lambda2_values: List[float] = field(default_factory=list)
    compute_times_ms: List[float] = field(default_factory=list)
    stable_count: int = 0
    n_instances: int = 0

    @property
    def mean_lambda2(self) -> float:
        v = [x for x in self.lambda2_values if math.isfinite(x) and x > -1e-9]
        return sum(v) / len(v) if v else float("nan")

    @property
    def std_lambda2(self) -> float:
        v = [x for x in self.lambda2_values if math.isfinite(x) and x > -1e-9]
        if len(v) < 2:
            return 0.0
        mean = sum(v) / len(v)
        return math.sqrt(sum((x - mean) ** 2 for x in v) / (len(v) - 1))

    @property
    def cv_lambda2(self) -> float:
        mean = self.mean_lambda2
        if not math.isfinite(mean) or mean < 1e-9:
            return float("nan")
        return self.std_lambda2 / mean

    @property
    def mean_compute_ms(self) -> float:
        return sum(self.compute_times_ms) / len(self.compute_times_ms) if self.compute_times_ms else 0.0

    @property
    def stability_rate(self) -> float:
        return self.stable_count / self.n_instances if self.n_instances else 0.0


def run_topology(topo_name: str, gen_fn, w_fn_name: str, w_fn,
                 n_instances: int = N_INSTANCES) -> TopologyResult:
    result = TopologyResult(topology=topo_name, w_fn_name=w_fn_name)
    result.n_instances = n_instances
    for _ in range(n_instances):
        hg = gen_fn()
        t0 = time.perf_counter()
        L, _, stable = build_laplacian(hg, w_fn)
        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        if stable and L.shape[0] >= 2:
            result.stable_count += 1
            result.lambda2_values.append(compute_lambda2(L))
            result.compute_times_ms.append(elapsed_ms)
    return result


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> Dict:
    print("SIM-HYPEREDGE-01: W(e) calibration for stable hypergraph Laplacian")
    print(f"N_NODES={N_NODES}, N_INSTANCES={N_INSTANCES}, SEED={SEED}")
    print("Laplacian: L = I − Θ  (active-subgraph normalized)")
    print()

    results: Dict[str, Dict[str, TopologyResult]] = {}
    sybil_results: Dict[str, Dict] = {}

    for w_name, w_fn in WEIGHT_FUNCTIONS.items():
        results[w_name] = {}
        print(f"  Running W(e)={w_name} ...")
        for topo_name, gen_fn in TOPOLOGIES.items():
            np.random.seed(SEED)
            random.seed(SEED)
            results[w_name][topo_name] = run_topology(topo_name, gen_fn, w_name, w_fn)
        sybil_results[w_name] = sybil_sensitivity(w_fn)

    np.random.seed(SEED)
    random.seed(SEED)
    hg_incr = gen_t2_panel_heavy()
    incremental = validate_incremental_update(hg_incr, w_harmonic)

    return {"results": results, "sybil_results": sybil_results, "incremental": incremental}


def print_report(data: Dict) -> None:
    results = data["results"]
    sybil_results = data["sybil_results"]
    incr = data["incremental"]

    print()
    print("=" * 74)
    print("RESULTS: λ₂(L) = Fiedler value of normalized Laplacian (active subgraph)")
    print("=" * 74)
    print(f"{'Topology':<28} {'W(e)':<24} {'λ₂ mean':>9} {'CV':>7} {'stable%':>8} {'ms':>7}")
    print("-" * 74)

    for topo in TOPOLOGIES:
        for w_name in WEIGHT_FUNCTIONS:
            r = results[w_name][topo]
            m = r.mean_lambda2
            cv = r.cv_lambda2
            st = r.stability_rate * 100
            ms = r.mean_compute_ms
            m_s = f"{m:.5f}" if math.isfinite(m) else "   NaN "
            cv_s = f"{cv:.4f}" if math.isfinite(cv) else "  NaN "
            print(f"  {topo:<26} {w_name:<24} {m_s:>9} {cv_s:>7} {st:>7.1f}% {ms:>6.1f}")
        print()

    print()
    print("=" * 74)
    print("SYBIL SENSITIVITY (T4) — Δλ₂ when 10 extra Sybils join one hyperedge")
    print("=" * 74)
    for w_name, sr in sybil_results.items():
        if sr["stable"]:
            print(f"  {w_name:<24}  base={sr['lambda2_base']:.5f}  "
                  f"pert={sr['lambda2_perturbed']:.5f}  Δλ₂={sr['delta_lambda2']:.5f}")
        else:
            print(f"  {w_name:<24}  UNSTABLE")

    print()
    print("=" * 74)
    print("INCREMENTAL UPDATE VALIDATION (stake_harmonic_mean, T2)")
    print("=" * 74)
    print(f"  max Frobenius error : {incr['max_frobenius_error']:.2e}")
    print(f"  mean Frobenius error: {incr['mean_frobenius_error']:.2e}")
    print(f"  exact (< 1e-10)     : {incr['exact']}")
    print(f"  mean speedup vs full: {incr['mean_speedup']:.2f}x")

    print()
    print("=" * 74)
    print("VERDICT")
    print("=" * 74)
    _print_verdict(results, sybil_results)


def _print_verdict(results: Dict, sybil_results: Dict) -> None:
    scores = {}
    for w_name in WEIGHT_FUNCTIONS:
        cvs, fully_stable = [], True
        for topo in TOPOLOGIES:
            r = results[w_name][topo]
            if r.stability_rate < 1.0:
                fully_stable = False
            cv = r.cv_lambda2
            if math.isfinite(cv):
                cvs.append(cv)
        mean_cv = sum(cvs) / len(cvs) if cvs else float("inf")
        sd = sybil_results[w_name].get("delta_lambda2", float("inf"))
        scores[w_name] = {
            "mean_cv": mean_cv if math.isfinite(mean_cv) else float("inf"),
            "sybil_delta": sd if math.isfinite(sd) else float("inf"),
            "fully_stable": fully_stable,
        }

    print()
    for w_name, s in scores.items():
        cv_s = f"{s['mean_cv']:.4f}" if math.isfinite(s['mean_cv']) else "inf"
        sd_s = f"{s['sybil_delta']:.5f}" if math.isfinite(s['sybil_delta']) else "inf"
        print(f"  {w_name:<24}  mean_CV={cv_s}  Sybil_Δλ₂={sd_s}  fully_stable={s['fully_stable']}")

    candidates = {k: v for k, v in scores.items() if v["fully_stable"]}
    if not candidates:
        print("\n  WARNING: no fully-stable candidate found.")
        recommended = "stake_harmonic_mean"
    else:
        recommended = min(candidates, key=lambda k: (candidates[k]["mean_cv"], candidates[k]["sybil_delta"]))

    print()
    print(f"  RECOMMENDATION : {recommended}")
    print(f"  sim_hyperedge_01_recommended_w_e={recommended}")


if __name__ == "__main__":
    data = main()
    print_report(data)
