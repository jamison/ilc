# ADR-0032: Temporal Hypergraph — Epoch-Stamped Incidence and Incremental Laplacian Analysis

**Status:** Accepted  
**Date:** 2026-04-21  
**Lane:** H-004 (amendment to ADR-0029)  
**Verdict token:** `run_h004_temporal_hypergraph_adr_verdict=accepted`

---

## 1. Context

ADR-0029 accepted the hypergraph substrate and established `W(e) = stake_harmonic_mean` as the
hyperedge weight function. The Tier 1 substrate implementation (`1c027054`) added an
`epoch: int` stamp field to `HyperEdge`. H-005 (SIM-SPECTRAL-01) validated that λ₂ of the
normalized hypergraph Laplacian is a viable partition-risk signal. H-006a delivered
`ilc_core/analysis/laplacian_analytics.py` implementing that signal with calibration constants
locked to H-005 results.

None of these documents formally specifies what the epoch stamp *authorizes analytically* — how
epoch-stamped incidence enables the temporal trajectory of the Laplacian, what `perturbation_norm`
means in this context, or how the incremental proof chain is structured. H-006b
(multi-scale spectral analysis) and downstream CDL work (H-007, H-008) depend on this contract
being explicit before implementation proceeds.

This ADR closes that gap. It is an amendment to ADR-0029, not a replacement.

---

## 2. Decision

### 2.1 Epoch-stamped incidence is the authorization primitive

Each `HyperEdge(members, weight, epoch)` asserts that the set of `members` participated in a
shared interaction during `epoch`. The `epoch` stamp is not metadata — it is the authorization
that allows any analytical system to construct a time-indexed incidence matrix:

```
B(t)[v, e] = weight(e)   if v ∈ members(e) and epoch(e) == t
             0            otherwise
```

This is the primitive from which all temporal Laplacian analysis derives. No temporal analysis
is authorized to use an incidence entry at time t unless its source hyperedge carries `epoch == t`.

### 2.2 The incremental Laplacian and perturbation norm

Given epoch-indexed Laplacians L(t) and L(t-1), the **perturbation norm** is defined as the
Frobenius norm of their difference:

```
perturbation_norm(t) = ‖L(t) − L(t−1)‖_F
```

This is the only authorized measure of structural change between epochs. It is implemented as
`delta_laplacian_frobenius(L_new, L_old)` in `laplacian_analytics.py` and calibrated against
the H-005 result `EPSILON_TRIGGER = 0.3391`.

**EPSILON_TRIGGER semantics:** when `perturbation_norm(t) > EPSILON_TRIGGER`, a forced full
eigendecomposition is required regardless of the N_BATCH schedule. This prevents the Rayleigh
lazy-approximation path from being used across a structurally significant topology change.

### 2.3 The Rayleigh lazy-approximation path

When the spectral gap `λ₃ − λ₂ > RAYLEIGH_SPECTRAL_GAP_MIN = 0.05`, the Fiedler value at
epoch t may be approximated without full eigendecomposition:

```
λ₂(t) ≈ v₂(t−1)ᵀ · L(t) · v₂(t−1)
```

This approximation is authorized only under two joint conditions:
1. The epoch's `perturbation_norm` is below `EPSILON_TRIGGER` (no forced recompute triggered)
2. The prior epoch's `spectral_gap` exceeds `RAYLEIGH_SPECTRAL_GAP_MIN`

When either condition fails, `compute_fiedler()` (full eigendecomposition) is mandatory.
The calibration constant `N_BATCH = 1` (locked to H-005 R7 for T2-class topologies) means
full recomputation runs every epoch regardless, making the Rayleigh path a fallback for
future topology classes — not the current T2-panel production path.

### 2.4 The temporal spectral trajectory

The epoch-stamped incidence primitive authorizes a well-defined trajectory over time:

| Symbol | Definition |
|--------|-----------|
| λ₂(t) | Fiedler value of L(t) |
| Δλ₂(t) | λ₂(t) − λ₂(t−1) |
| ΔΔλ₂(t) | Δλ₂(t) − Δλ₂(t−1) |

The sign combination of (ΔΔλ₂, Δλ₂) encodes the qualitative topology trend:

| ΔΔλ sign | Δλ sign | Pattern | Interpretation |
|---|---|---|---|
| + | + | Accelerating growth | Topology strengthening |
| − | + | Decelerating growth | Stabilizing |
| + | − | Decelerating decline | Partition healing |
| − | − | Accelerating decline | Partition risk escalating |

This table is the normative contract for any implementation that exposes `lambda2_accel`
(ΔΔλ). It must not be exposed without the `spectral_gap` field that contextualizes it.

### 2.5 Bootstrap mode and the concentration metric

During epochs 0 through `N_BOOTSTRAP = 44`, raw λ₂ is suppressed as a partition-risk signal
because a sparse-but-healthy genesis graph naturally produces low λ₂. The authorized
substitute is the **Fiedler concentration metric**:

```
C(t) = mean(|v₂[genesis_nodes]|) / mean(|v₂[all_nodes]|)
```

C(t) measures how much of the Fiedler eigenvector mass remains concentrated on genesis
nodes. A healthy bootstrap has C(t) near 1.0. C(t) declining toward 0.5 indicates that
newly joined nodes are structurally fragmenting the genesis cohesion.

Bootstrap mode exits at `N_BOOTSTRAP` nodes, after which `THETA_FLOOR = 0.001` becomes
the production partition-risk trigger.

### 2.6 What this ADR does NOT authorize

- **No CDL mutations in H-006b.** The `SpectralEpochRecord` type introduced in H-006b is
  a standalone analytics store. `delta_lambda_vec`, `eigenvec_epoch`, and `spectral_gap`
  fields in the epoch KPI store are gated on CDL H-CON-03 and are not authorized by this ADR.
- **No gossip wiring.** SpectralBeacon gossip is H-013 scope, pending SIM-BEACON-01.
- **No EpochSettlementRecord mutation.** The settlement path is not temporal-spectral-aware
  until CDL H-CON-03 ratification.

---

## 3. Consequences

### 3.1 Positive

- H-006a (`laplacian_analytics.py`) is formally authorized retroactively — its calibration
  constants, Rayleigh gate, perturbation norm, and bootstrap concentration metric all derive
  directly from the contracts in §2.
- H-006b (`spectral_trajectory.py`, `local_spectral_analytics.py`) has a precise
  specification for `SpectralEpochRecord` fields and the ΔΔλ detection table.
- Downstream CDL phases (H-007 spectral hash, H-008 PoSK gate) have a clear incremental
  proof chain to reference: epoch stamp → L(t) → perturbation_norm → λ₂ trajectory.

### 3.2 Constraints inherited

- The epoch stamp on `HyperEdge` is now load-bearing. Any implementation that strips or
  ignores the epoch field breaks the authorization primitive in §2.1.
- The Rayleigh approximation path must check both conditions in §2.3 before use. Checking
  only one is a correctness violation, not a performance optimization.
- `perturbation_norm` must use the Frobenius norm specifically. L∞ or L1 norms are not
  authorized as substitutes.

---

## 4. Relationship to prior ADRs

| ADR | Relationship |
|-----|-------------|
| ADR-0029 | This ADR amends ADR-0029 by specifying the temporal contract for the epoch stamp field already defined there. ADR-0029 remains the substrate authority; this ADR extends it into the time dimension. |
| ADR-0030 | No conflict. Content-type node embedding is orthogonal to spectral analysis. |
| ADR-0031 | No conflict. Subgraph query contract is a different analytical surface. |

---

## 5. Gate authorization

This ADR formally authorizes:

- `h_006a_laplacian_analytics_implementation` (retroactive — H-006a was implemented ahead of this document)
- `h_006b_spectral_trajectory_implementation` (forward — H-006b Part 3 SpectralEpochRecord)
- `h_006b_local_lambda2_implementation` (forward — H-006b Part 2 induced subgraph analytics)

**It does not authorize** the CDL H-CON-03 epoch KPI temporal fields or any gossip wiring
for spectral state. Those require their own CDL deliberation.
