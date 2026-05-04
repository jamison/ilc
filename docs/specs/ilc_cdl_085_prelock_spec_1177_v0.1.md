# CDL-085 Prelock Spec 1177 v0.1

**CDL:** CDL-085
**Prelock phase:** 1177
**Date:** 2026-05-04
**Status:** prelock — not ratified
**Authority:** SIM-SPECTRAL-05 gate pass (`sim_spectral_05_gate_pass`);
ADR-0037 §3.2 provenance equivalence criterion; CDL-084 provenance chain attribution
frontier

`cdl_085_prelock_committed_phase_1177`

---

## 1. Prelock Purpose

This prelock resolves Q1-Q5 from
`docs/specs/ilc_cdl_085_werner_phi_bound_opening_1172_v0.1.md` §4 and establishes the
candidate `EDGE_MINT_PHI_BOUND` value for future CDL-085 ratification deliberation.

This phase does not:

- mutate CDL-085 text or status;
- add or activate a runtime `EDGE_MINT_PHI_BOUND` value in `ilc_core/`;
- change `PROVENANCE_DECAY_ALPHA`;
- change `PROVENANCE_MAX_DEPTH`;
- activate economic-flow gating;
- authorize v0.2 signing.

The existing runtime placeholder remains unset. Any future active runtime value must be
introduced by a later authorized phase after ratification and activation gates.

---

## 2. Q1 Resolution — Bound Object

**Selected:** provenance-equivalent derivation paths only.

The bound applies to derivation paths evaluated under ADR-0037 §3.2. A path is in scope
only when its claimed independence and canonical convergence are being evaluated as a
provenance-equivalence question.

**Deferred:** all edge-mint events and all claim-composition events that participate in
ECU/ILC attribution. Those broader surfaces require economic-flow observer-slice evidence
before they can be safely pulled into CDL-085 or a future CDL amendment.

**Rationale:** CDL-085 was opened to decide whether edge-mint / provenance-attribution
claims are canonical productive work rather than Sybil-amplified branches. Scoping Q1 to
provenance-equivalent paths keeps the prelock aligned with the opening question and with
ADR-0037's provenance equivalence criterion.

---

## 3. Q2 Resolution — Bound Expression

**Selected:** combined rule.

Candidate expression:

```text
valid_phi_bound(path_set) :=
    branchial_convergence_separation(path_set) >= Decimal("0.60")
    AND structural_sybil_discriminants_confirm(path_set)
```

Candidate threshold:

```python
EDGE_MINT_PHI_BOUND = Decimal("0.60")
```

The `Decimal("0.60")` value is derived from SIM-SPECTRAL-05 Track B:

- S1 legitimate branchial convergence mean: `0.85`
- S3 Sybil branchial convergence mean: `0.25`
- separation: `0.60`

Track A remains auxiliary confirmation:

- `lambda_max`: 3.180229σ vs `synthetic_sybil_cluster`
- `spectral_gap`: 2.775223σ vs `synthetic_sybil_cluster`
- `degree_gini`: 2.726353σ vs `synthetic_sybil_cluster`

**Rationale:** Track B is the only numerically calibrated convergence baseline for this
prelock. Track A confirms that the relevant S1 surface is structurally separated from
the committed Sybil topology family, but Track B supplies the direct branchial
convergence bound.

---

## 4. Q3 Resolution — φ Interpretation

**Selected:** Werner productivity bound over provenance-equivalent edge-mint expansion.

In this prelock, φ is not treated as a generic spectral-efficiency ratio and not merely as
a shorthand for "SIM-SPECTRAL-05 passed." It names a productivity bound over the
expansion of provenance-equivalent edge-mint claims: paths below the branchial convergence
separation threshold are not yet canonical productive work for CDL-085 purposes.

**Rationale:** The Werner φ-bound name is meaningful only if it constrains productivity
over edge-mint expansion. The `0.60` candidate separates legitimate convergence (`0.85`)
from Sybil convergence (`0.25`) by using the measured branchial separation baseline.

---

## 5. Q4 Resolution — Runtime Relation

**Selected:** constitutional policy with a future `EDGE_MINT_PHI_BOUND` runtime constant
declared at ratification; runtime activation deferred until runtime-binding observer-slice
evidence passes.

Activation gate:

```text
sim_spectral_05_runtime_binding_slice_pass
```

Phase 1177 does not modify `ilc_core/`. The current runtime placeholder remains unset.
The future ratification phase may declare the constant, but activation should remain
gated until the runtime-binding observer slice proves that the bound can gate simulated
Sybil-amplified edge-mint events without breaking legitimate paths.

**Rationale:** This separates constitutional lock-in from runtime exposure. The prelock
can define what the bound means while refusing to put an active value on the settlement
path prematurely.

---

## 6. Q5 Resolution — Economic-Flow Dependency

**Selected:** constitutional ratification may proceed on governance grounds; economic-flow
activation is deferred until economic-flow observer-slice evidence passes.

Activation gate:

```text
sim_spectral_05_economic_flow_slice_pass
```

The economic-flow observer slice must test whether φ-bound gating on
provenance-equivalent paths produces expected ECU/ILC outcomes without suppressing
legitimate attribution paths.

**Rationale:** Economic-flow risk is real, but it should block economic-flow activation,
not the constitutional prelock. Ratification may define the governance rule; activation
requires the economic-flow slice.

---

## 7. Candidate Constant

Candidate value for future CDL-085 ratification:

```python
EDGE_MINT_PHI_BOUND = Decimal("0.60")
```

This value is not added to `ilc_core/` in Phase 1177. If a future ratification phase
introduces the constant, it should use an exact numeric contract (`Decimal` or a ratified
fixed-point integer), not a runtime-critical `float`.

---

## 8. Evidence References

- `docs/sims/sim_spectral_05/disposition_1171_v0.1.md` — Track A + Track B disposition
  and `sim_spectral_05_gate_pass`
- `out/sim_spectral_05_track_b_run_summary.json` — Track B convergence artifact
- `out/sim_spectral_05_track_a_calibration_summary.json` — Track A discriminant artifact
- `docs/adr/ADR_0037_Genesis_Canonical_Lineage_Contract.md` §3.2 — provenance
  equivalence criterion
- `docs/specs/ilc_cdl_085_werner_phi_bound_opening_1172_v0.1.md` §4 — Q1-Q5 opening
  questions

---

## 9. Ratification and Activation Routing

CDL-085 ratification is deferred to a later window. The future ratification phase must
consume this prelock and decide whether to ratify the candidate bound.

Runtime activation remains blocked until:

- `sim_spectral_05_runtime_binding_slice_pass`

Economic-flow activation remains blocked until:

- `sim_spectral_05_economic_flow_slice_pass`

The gossip observer slice remains separately deferred and does not block this prelock.

---

## 10. Prelock Token

`cdl_085_prelock_committed_phase_1177`
