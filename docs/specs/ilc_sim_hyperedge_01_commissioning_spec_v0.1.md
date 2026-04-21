# ILC SIM-HYPEREDGE-01 Commissioning Spec v0.1

**Date:** 2026-04-21  
**Status:** commissioned — gate cleared (ADR-0029 accepted; substrate live at commit `1c027054`)  
**Output needed:** recommended W(e) formula for stable hypergraph Laplacian spectrum  
**Blocks:** SIM-SPECTRAL-01, Merkle-Laplacian paper §8.4, spectral KPI storage in epoch record

`sim_hyperedge_01_commissioned`
`adr_0029_substrate_gate_cleared`
`w_e_formula_selection_required_before_sim_spectral_01`

---

## 1. Purpose

The hypergraph Laplacian is:

```
Δ = D_V^{-1/2} · H · W · D_E^{-1} · H^T · D_V^{-1/2}
```

where W is a diagonal matrix of hyperedge weights W(e). The spectral properties
of Δ — in particular the Fiedler value λ₂ (algebraic connectivity) — are the
foundation of:

- partition-risk detection (low λ₂ → vulnerable to graph split)
- Proof of Structural Knowledge (PoSK) admission primitive
- spectral routing metric (distance between λ-fingerprints)
- Merkle-Laplacian dual commitment (epoch structural fingerprint)

The choice of W(e) determines whether the Laplacian spectrum is stable under
normal ILC graph dynamics or noisy, spoofable, or compute-intensive. This SIM
selects W(e) before any downstream spectral work begins.

---

## 2. Three candidate weight functions

All three candidates produce W(e) > 0 for any non-empty hyperedge. All are
deterministic given the stake vector. The question is which produces the most
stable and informative λ₂ signal on realistic ILC graph topologies.

### 2.1 W_sum — stake-sum

```
W_sum(e) = Σ_{v ∈ e} stake(v)
```

Properties:
- additive; scales with hyperedge cardinality
- large high-degree hyperedges dominate the spectrum
- a single high-stake agent added to a hyperedge causes a large weight jump
- susceptible to Sybil amplification if stake is cheap

### 2.2 W_product — stake-product

```
W_product(e) = Π_{v ∈ e} stake(v)
```

Properties:
- multiplicative; extremely sensitive to low-stake members (a single zero-stake
  agent collapses the weight to zero)
- very large for high-cardinality high-stake hyperedges; numerical overflow
  risk at mainnet scale without log-space computation
- not recommended for general use; included for completeness

### 2.3 W_harmonic — stake-harmonic-mean

```
W_harmonic(e) = |e| / Σ_{v ∈ e} (1 / stake(v))
```

Properties:
- bounded by the minimum stake in the hyperedge (resistant to Sybil inflation)
- insensitive to cardinality explosion — adding many low-stake agents does not
  inflate the weight
- undefined if any member has stake(v) = 0; requires stake-floor guard
- expected to produce the most stable λ₂ signal under adversarial conditions

---

## 3. Simulation methodology

### 3.1 Synthetic graph topologies

Run each W(e) candidate against four topology classes that represent the
expected ILC graph regime:

| Topology | Description | Rationale |
|---|---|---|
| T1: Random hypergraph | N=500 nodes, E=200 hyperedges, degree ~ Poisson(4), stake ~ Uniform(0.1, 10) | Baseline; no structure |
| T2: Panel-heavy | N=500, E=80 large panels (|e|=7–15), E=120 binary edges; stake ~ Pareto(α=1.5) | Mimics ILC claim-evaluation structure |
| T3: Coalition-sparse | N=500, E=20 large refutation coalitions (|e|=20–50), rest binary; stake ~ Lognormal | Stress test for high-cardinality weight function stability |
| T4: Adversarial Sybil | N=500 honest + N=200 Sybil (stake=0.01 each), Sybil agents join every large hyperedge | Tests W_harmonic vs W_sum resistance to Sybil inflation |

### 3.2 Metrics to collect per topology per W(e)

| Metric | Description | Target |
|---|---|---|
| λ₂ (Fiedler value) | Algebraic connectivity of normalized Laplacian | Stable, non-zero, informative |
| λ₂ coefficient of variation | std(λ₂) / mean(λ₂) across 50 random instances of each topology | < 0.20 preferred |
| λ₂ sensitivity to stake perturbation | Δλ₂ / Δstake for a ±10% stake change on one member | Low is better |
| λ₂ sensitivity to Sybil injection | Δλ₂ when 10 Sybil agents join a hyperedge (T4 only) | W_harmonic should show lower sensitivity |
| Numerical stability | Condition number of intermediate matrix products | Flag overflow / underflow |
| Compute time | Wall-clock time for full Δ computation on each topology | Must be feasible on commodity hardware (< 5s for N=500) |

### 3.3 Incremental update validation

For the recommended W(e), additionally validate the incremental Laplacian update:

```
Δ(t) = Δ(t-1) + ΔΔ(t)
```

where ΔΔ(t) affects only rows/columns of nodes involved in new/removed
hyperedges in epoch t. Measure:
- approximation error: `||Δ_incremental - Δ_full||_F` — should be zero (exact, not approximate)
- speedup factor vs. full recomputation across 10 sequential epoch updates

---

## 4. Implementation notes

All simulation code goes in `ilc_core/sim/` or `tools/sim/`. The simulation
must be reproducible: fix `random.seed(42)` and `numpy.random.seed(42)` at
the top of each script.

The stake-floor guard for W_harmonic (stake(v) = 0 case) should be:

```python
def w_harmonic(member_stakes: list[float]) -> float:
    floor = 1e-6  # validator minimum stake floor
    guarded = [max(s, floor) for s in member_stakes]
    return len(guarded) / sum(1.0 / s for s in guarded)
```

This floor matches the spirit of the CDL-055 validator stake floor without
requiring the exact CDL value — the SIM is not testing the floor value, only
whether W_harmonic is structurally stable.

---

## 5. Required outputs

### 5.1 Research document

`docs/research/ilc_sim_hyperedge_01_results_v0.1.md`

Must contain:
- methodology summary (topology classes, metric definitions, candidate formulas)
- per-topology per-W(e) results table (at minimum λ₂ CV and Sybil sensitivity)
- incremental update validation for the recommended candidate
- explicit recommended W(e) formula with rationale
- any disqualifying findings (e.g., W_product numerical overflow)
- carry-forward: the recommended W(e) is the input to SIM-SPECTRAL-01

Token required: `sim_hyperedge_01_recommended_w_e=<formula_name>`
(one of: `stake_sum`, `stake_harmonic_mean`, `stake_product`, or
`stake_harmonic_mean_with_floor` if the guard is considered part of the formula)

### 5.2 Simulation script(s)

`tools/sim/sim_hyperedge_01_w_e_calibration.py` (or equivalent path in `ilc_core/sim/`)

Must be self-contained and reproducible. Must produce the results table.

### 5.3 Test

`tests/test_sim_hyperedge_01_commissioning.py`

Verifies:
- the results document exists
- the recommended W(e) token is present
- the four topology classes are mentioned
- the incremental update validation result is present
- no fabricated numeric results (verifies at least one quoted raw number from the simulation)

Uses `ILC_SIM_HYPEREDGE_01_SELFTEST=1` selftest guard.

---

## 6. What this SIM does NOT decide

- The exact λ₂ detection threshold for PoSK (that is SIM-SPECTRAL-01)
- The noise budget ε for the spectral beacon (that is SIM-BEACON-01)
- Whether spectral_hash enters the epoch commitment record (that requires a CDL)
- The embedding model per content_type (that is SIM-EMBED-01)

---

## 7. Downstream gates this SIM clears

A positive SIM-HYPEREDGE-01 result (stable W(e) recommendation) clears the
prerequisite for:

1. **SIM-SPECTRAL-01** — λ₂ signal quality validation; uses the recommended W(e)
2. **Laplacian analytics implementation** — `compute_laplacian_delta()` in
   `ilc_core/analysis/spectral_utils.py`; do not implement before this SIM
3. **`perturbation_norm` in epoch KPI store** — depends on the incremental update
   validation result
4. **Merkle-Laplacian paper §8.4** — sensitivity analysis requires the
   per-topology λ₂ CV data

---

## 8. Source authority

- `docs/adr/ADR_0029_Hypergraph_Substrate.md` §2.4 (Laplacian computation)
- `docs/research/ilc_morphogenetic_hypergraph_planning_classification_v0.1.md` §1.3
- `docs/research/ilc_merkle_laplacian_dual_commitment_paper_draft_v0.1.md` §4 and §8.4
