# ILC SIM-SPECTRAL-01 Commissioning Spec v0.1

**Date:** 2026-04-21  
**Status:** commissioned — gate cleared by H-001 (`sim_hyperedge_01_recommended_w_e=stake_harmonic_mean`)  
**Output needed:** validated λ₂ signal viability for ILC partition-risk detection, PoSK admission,
and reputation scoring; Rayleigh recomputation schedule calibration  
**Blocks:** H-006a (Laplacian analytics impl), H-006b (multi-scale spectral), H-007 (CDL spectral
hash), H-008 (CDL PoSK gate), H-009 (SIM-BEACON-01), H-CON-03 (CDL epoch KPI temporal fields),
Merkle-Laplacian paper §8.4–§8.5

`sim_spectral_01_commissioned`
`h001_gate_cleared`

---

## 1. Purpose

SIM-HYPEREDGE-01 (H-001) established that `stake_harmonic_mean` is the most stable W(e)
formula for the normalized hypergraph Laplacian (mean CV 2.5683, 100% stable, Frobenius
incremental error 3.84e-17). SIM-SPECTRAL-01 takes that formula as a fixed input and
answers the next set of questions:

1. **Signal viability**: Is λ₂(L) a detectable, informative, and non-spoofable partition-risk
   signal at ILC graph scales?
2. **Compute feasibility**: Can the full eigendecomposition run within the epoch time budget on
   commodity hardware, and what is the optimal lazy-recomputation schedule?
3. **PoSK admission calibration**: What detection threshold θ correctly admits legitimate
   validators while excluding structurally-isolated actors?
4. **Bootstrap behavior**: How does λ₂ behave in the genesis/bootstrap regime, and what
   supplementary signals protect against false exclusion of newly joined nodes?
5. **Reputation input**: Does the Fiedler vector per-node centrality score carry non-redundant
   signal relative to stake-weighted degree?

The Laplacian formula is fixed by H-001:

```
Θ = D_V^{-1/2} · H · W · D_E^{-1} · H^T · D_V^{-1/2}    (diffusion matrix)
L = I − Θ                                                   (normalized Laplacian)
W(e) = stake_harmonic_mean with floor 1e-6
```

λ₂(L) is the Fiedler value (second-smallest eigenvalue of L), computed on the active subgraph
(nodes in at least one hyperedge). All simulations use `random.seed(42)` and
`numpy.random.seed(42)`.

---

## 2. Mandatory requirements (R1–R8)

These eight requirements were identified in the spectral discussion of 2026-04-21 and are
authoritative scope additions to this SIM. All eight must be addressed in the results document.

**Source:** `docs/research/ilc_fiedler_genesis_homoiconicity_discussion_2026_04_21.md`  
**Planning doc:** `docs/research/ilc_hypergraph_implementation_lane_h_series_v0.1.md` §H-005

| # | Requirement | Description |
|---|---|---|
| R1 | **Bootstrap health signal** | During epochs 0–N_bootstrap, use Fiedler vector *concentration* on Genesis nodes as primary health metric instead of raw λ₂ (which is naturally near-zero on a sparse graph). Validate that concentration is measurable and distinct from the mature-graph regime. |
| R2 | **Genesis epoch floor** | Define a protocol for distinguishing "sparse-but-healthy" λ₂ (bootstrap) from "near-partition" λ₂ (failure). Suppress partition-risk alerts during bootstrap. Determine N_bootstrap. |
| R3 | **Founding hyperedge weight anchor** | Validate that a genesis-design in which all founding validators are members of every genesis hyperedge produces a non-zero λ₂ floor at epoch 1. This is a design test — parameterize genesis.json accordingly. |
| R4 | **New-node exclusion guard** | Calibrate detection threshold θ such that a legitimately formed cluster of newly joined, low-stake nodes is not falsely excluded by the PoSK gate. Test on a bootstrap topology with N_new ∈ {10, 50, 200} new nodes joining simultaneously. |
| R5 | **Fiedler vector per-node centrality as reputation input** | Compute v₂[i] per node and compare rank-order with stake-weighted degree. Measure rank correlation (Spearman ρ) across topology classes. Determine whether Fiedler centrality is non-redundant vs. degree centrality (ρ < 0.9 = non-redundant; ρ ≥ 0.9 = redundant). |
| R6 | **Rayleigh quotient lazy recomputation validation** | Measure the approximation error of `λ₂(t) ≈ v₂(t−1)ᵀ · L(t) · v₂(t−1)` across 50 sequential epoch updates per topology class. Verify error stays below ε for normal epoch drift. Report max and mean error. |
| R7 | **N_batch and ε calibration** | Determine optimal batch recompute interval N_batch (epochs) and perturbation trigger threshold ε (‖ΔL‖_F) such that: (a) Rayleigh approximation error remains < δ_max throughout the batch, and (b) full recomputation is triggered when error would exceed δ_max. Test across all four topology classes. |
| R8 | **spectral_gap reporting** | Validate that `spectral_gap = λ₃ − λ₂` is reliably positive and meaningful under normal ILC graph dynamics. Report mean and std(spectral_gap) per topology class. A small spectral_gap means Rayleigh approximation is unreliable — flag if spectral_gap < 1e-4. |

---

## 3. Simulation methodology

### 3.1 Topology classes

Reuse the four topology classes from SIM-HYPEREDGE-01 plus two new bootstrap classes:

| ID | Description | N_nodes | Stake |
|---|---|---|---|
| T1_random | Random hypergraph, Poisson degree, 200 edges | 500 | Uniform(0.1, 10) |
| T2_panel_heavy | 80 large panels (|e|=7–15) + 120 binary | 500 | Pareto(α=1.5) |
| T3_coalition_sparse | 20 large coalitions (|e|=20–50) + 180 binary | 500 | Lognormal |
| T4_adversarial_sybil | 80 mixed + 120 binary; 200 Sybil at stake=0.01 | 700 | Honest Uniform(1,10) |
| T5_bootstrap_sparse | Genesis topology: 4 founding validators, all-to-all hyperedge + 10 binary edges | 4–20 | All equal, high (10.0) |
| T6_new_node_influx | T2 base + N_new new low-stake nodes joining simultaneously | 500 + N_new | New nodes stake=0.1 |

T5 is used for R1, R2, R3. T6 (with N_new ∈ {10, 50, 200}) is used for R4.

### 3.2 Metrics per topology per experiment

| Metric | Description | Target |
|---|---|---|
| λ₂ mean | Fiedler value averaged over 50 instances | Stable, non-zero on T1–T4 |
| λ₂ CV | std(λ₂) / mean(λ₂) | < 0.20 preferred (from H-001 baseline) |
| Detection threshold θ | λ₂ value below which partition-risk alert fires | Must not exclude T6 new-node clusters |
| False-positive rate | Fraction of healthy instances with λ₂ < θ | < 5% target |
| Full decomp time (ms) | Wall-clock for full L eigendecomposition (not just λ₂) | < 5000ms for N=500 |
| Rayleigh approx error | |λ₂_approx − λ₂_full| per epoch update | < δ_max = 1e-4 |
| spectral_gap | λ₃ − λ₂ per instance | > 1e-4 for Rayleigh to be reliable |
| Fiedler centrality ρ | Spearman rank correlation(v₂[i], stake_weighted_degree) | Report; flag if ρ ≥ 0.9 |
| Fiedler concentration | std(v₂[i] for i in genesis_nodes) / std(v₂ global) at T5 | High at bootstrap, low at maturity |
| Sybil spoofability | Δλ₂ when coalition of validators suppresses honest hyperedges | Hard to fake high λ₂ without real connectivity |

### 3.3 Signal viability test

For T1–T4, measure:
- Whether λ₂ is detectable above numerical noise (mean λ₂ > 10 × machine epsilon)
- Whether λ₂ differs meaningfully between the four topology classes (cross-topology ANOVA)
- Whether λ₂ is sensitive to the "partition scenario": remove one randomly chosen bridge hyperedge;
  measure Δλ₂. A useful signal should drop significantly (Δλ₂ / λ₂ > 0.10).

### 3.4 Spoofability analysis

For T4 (adversarial Sybil), measure whether a coordinated validator coalition can:
1. **Inflate λ₂** by adding fake hyperedge memberships (low-stake Sybil agents joining many edges)
2. **Suppress λ₂** by withholding honest hyperedge participation

For each scenario, report Δλ₂ as a fraction of baseline λ₂. The `stake_harmonic_mean` weight
function structurally resists inflation (bounded by minimum member stake), but this must be
quantified.

### 3.5 Bootstrap validation (R1–R3)

Using T5 (4 founding validators, all-to-all genesis hyperedge):

1. Compute λ₂(t) as nodes are added sequentially from 4 to 500 (simulating network growth)
2. Plot λ₂ trajectory: does it start near-zero and grow monotonically?
3. Measure Fiedler vector concentration on genesis nodes: `C(t) = mean(|v₂[i]| for i ∈ genesis) / mean(|v₂|)`
4. Confirm C(t) is high early (genesis nodes are structural hinge) and declines as network grows
5. Define N_bootstrap as the epoch at which C(t) < 2.0 × C(∞) — i.e., when Genesis node
   centrality has normalized to within 2× of the mature-graph baseline

### 3.6 New-node exclusion guard (R4)

For T6 with N_new ∈ {10, 50, 200}:
1. Compute λ₂ on the base graph (T2, 500 nodes)
2. Add N_new new nodes, each joining a single new binary hyperedge with one established node
3. Compute λ₂ on the extended graph
4. Compute λ₂ on the induced subgraph of just the N_new new nodes + their one connecting edge
5. Report: does the global λ₂ change? Does the new-node cluster have positive local λ₂?
6. Calibrate θ such that legitimate new-node clusters (local λ₂ > 0 but small) are not excluded

### 3.7 Rayleigh recomputation validation (R6–R8)

Using T2_panel_heavy (most realistic ILC topology):

1. Compute full eigendecomposition at epoch 0: store v₂(0), λ₂(0), spectral_gap(0)
2. For epochs 1–50: add one random hyperedge per epoch (simulating normal operation)
3. At each epoch t, compute:
   - `λ₂_full(t)` via full eigvalsh
   - `λ₂_approx(t) = v₂(t−1)ᵀ · L(t) · v₂(t−1)` (Rayleigh quotient)
   - Error: `|λ₂_approx(t) − λ₂_full(t)|`
   - `spectral_gap(t) = λ₃(t) − λ₂(t)`
4. Identify the epoch N_batch_empirical at which error first exceeds δ_max = 1e-4
5. Report: recommended N_batch = N_batch_empirical × 0.8 (safety margin)
6. Report: recommended ε = ‖ΔL‖_F at the epoch where error first exceeds δ_max

Repeat for T1, T3, T4. Report the minimum N_batch across all topology classes as the
conservative recommendation.

### 3.8 Fiedler centrality reputation input (R5)

For each topology class:
1. Compute v₂[i] for all active nodes
2. Compute stake_weighted_degree: `d_w[i] = Σ_{e: i ∈ e} W(e)` (already computed as d_v in H-001)
3. Compute Spearman rank correlation ρ(v₂, d_w) across all active nodes
4. Report ρ per topology class
5. If ρ < 0.9 in any topology: Fiedler centrality is non-redundant — recommend inclusion in
   reputation layer
6. If ρ ≥ 0.9 in all topologies: Fiedler centrality is redundant with degree — note but do not
   exclude (structural centrality may still be useful under adversarial conditions)

---

## 4. Implementation notes

All simulation code goes in `tools/sim/sim_spectral_01_signal_quality.py`. Must be
self-contained and reproducible with fixed seeds. The `stake_harmonic_mean` weight function
must be imported from or match exactly the implementation in
`tools/sim/sim_hyperedge_01_w_e_calibration.py`:

```python
STAKE_FLOOR = 1e-6

def w_harmonic(member_stakes: list[float]) -> float:
    guarded = [max(s, STAKE_FLOOR) for s in member_stakes]
    return len(guarded) / sum(1.0 / s for s in guarded)
```

For the Rayleigh quotient approximation:

```python
def rayleigh_approx_lambda2(v_prev: np.ndarray, L_new: np.ndarray) -> float:
    """Approximate λ₂(t) using cached eigenvector from epoch t-1."""
    return float(v_prev @ L_new @ v_prev)
```

For the spectral gap:

```python
def spectral_gap(L: np.ndarray) -> float:
    """λ₃ − λ₂: reliability indicator for Rayleigh approximation."""
    vals = np.linalg.eigvalsh(L)
    return float(vals[2] - vals[1]) if len(vals) >= 3 else 0.0
```

The Fiedler vector is the eigenvector corresponding to λ₂:

```python
def fiedler_vector(L: np.ndarray) -> np.ndarray:
    """Eigenvector corresponding to λ₂ (second-smallest eigenvalue)."""
    vals, vecs = np.linalg.eigh(L)
    return vecs[:, 1]   # column 1 = second-smallest eigenvalue's eigenvector
```

---

## 5. Required outputs

### 5.1 Research document

`docs/research/ilc_sim_spectral_01_results_v0.1.md`

Must contain:
- λ₂ signal viability verdict per topology class (T1–T4)
- Detection threshold θ with false-positive rate
- Bootstrap λ₂ trajectory plot description and N_bootstrap value (R1–R3)
- New-node exclusion guard: θ calibrated for T6 new-node clusters (R4)
- Fiedler centrality rank correlation ρ per topology class (R5)
- Rayleigh approximation error table: max and mean error per topology (R6)
- Recommended N_batch and ε values (R7)
- spectral_gap statistics per topology; flag any topology where gap < 1e-4 (R8)
- Explicit spoofability verdict: can high λ₂ be faked by a coalition?
- Carry-forward: N_batch, ε, δ_max, θ, N_bootstrap are the inputs to H-006a and H-CON-03

Token required: `sim_spectral_01_lambda2_signal_viable=true|false`

### 5.2 Simulation script

`tools/sim/sim_spectral_01_signal_quality.py`

Must be self-contained and reproducible. Must produce all metrics in §3.

### 5.3 Test

`tests/test_sim_spectral_01_commissioning.py`

Verifies:
- The results document exists
- The viability token is present
- All six topology classes are mentioned
- All eight requirements (R1–R8) are addressed
- Rayleigh calibration outputs (N_batch, ε) are present as quoted values
- At least one raw numeric result from the simulation is present (anti-fabrication)
- The bootstrap N_bootstrap value is present

Uses `ILC_SIM_SPECTRAL_01_SELFTEST=1` selftest guard.

---

## 6. What this SIM does NOT decide

- Which embedding model to use per content_type (SIM-EMBED-01, H-002)
- The noise budget ε for the spectral beacon (SIM-BEACON-01, H-009)
- Whether `spectral_hash` enters the epoch commitment record (CDL H-007)
- The constitutional PoSK admission rule (CDL H-008)
- Multi-scale local λ₂ per knowledge cluster (H-006b)
- Temporal spectral trajectory implementation (H-006b Part 3)

---

## 7. Downstream gates this SIM clears

A positive result (`sim_spectral_01_lambda2_signal_viable=true`) clears:

1. **H-006a** — Laplacian analytics implementation; use N_batch and ε from R7
2. **H-006b** — Multi-scale spectral analysis; requires global signal validated first
3. **H-007** — CDL: spectral hash in epoch commitment record
4. **H-008** — CDL: λ₂ range as PoSK validator admission gate (also needs H-011)
5. **H-009** — SIM-BEACON-01: spectral beacon privacy calibration
6. **H-011** — Patent assessment (needs signal viability confirmed before IP filing)
7. **H-CON-03** — CDL: epoch KPI temporal fields; needs N_batch and ε from R7
8. **Merkle-Laplacian paper §8.4** — sensitivity data; §8.5 local λ₂ (with H-006b)

A negative result (`sim_spectral_01_lambda2_signal_viable=false`) requires a review session
before any downstream work proceeds. It does not cancel the H-lane — it may redirect to
alternative connectivity metrics (e.g., graph diameter, clustering coefficient).

---

## 8. Source authority

- `docs/research/ilc_hypergraph_implementation_lane_h_series_v0.1.md` §H-005 (requirements R1–R8)
- `docs/research/ilc_fiedler_genesis_homoiconicity_discussion_2026_04_21.md` (R1–R5, R6–R8 derivation)
- `docs/research/ilc_sim_hyperedge_01_results_v0.1.md` (W(e) formula, baseline CV data, incremental update speedup)
- `docs/adr/ADR_0029_Hypergraph_Substrate.md` §2.4 (Laplacian formula)
- `docs/research/ilc_merkle_laplacian_dual_commitment_paper_draft_v0.1.md` §4 and §8
