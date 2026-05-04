# CDL-085: Werner Phi-Bound Provenance Equivalence Limit

**Status:** OPEN
**Opened:** Phase 1172 (2026-05-04)
**Authority:** CDL-084 PROVENANCE chain attribution / ADR-0037 §3.2 provenance
             equivalence criterion / SIM-SPECTRAL-05 gate pass
**Blocks:** no runtime path directly. `EDGE_MINT_PHI_BOUND` remains unset pending
           prelock, parameter selection, and later ratification.

`cdl_085_open_phase_1172`
`cdl_085_sim_gate_lifted_phase_1172_sim_spectral_05_gate_pass`

---

## 1. Problem Statement

CDL-084 ratified bounded PROVENANCE chain attribution with
`PROVENANCE_DECAY_ALPHA=Decimal("0.45")` and `PROVENANCE_MAX_DEPTH=3`. It did not
constitutionalize a broader edge-mint or provenance-equivalence limit for deciding
when claimed-independent derivation paths are productive, canonical, and separable
from Sybil-injected paths.

The prior CDL-085 candidate was held SIM-gated because SIM-SPECTRAL-03 and
SIM-SPECTRAL-04 did not establish reliable Sybil discrimination. Phase 1171 now
provides positive SIM-SPECTRAL-05 evidence:

- Track A: `track_a_pass` against `synthetic_sybil_cluster`
- Track B: `track_b_pass` on branchial convergence
- Overall: `sim_spectral_05_gate_pass`

This opening lifts the SIM gate and opens the constitutional lane. It does not
ratify a bound value and does not modify runtime behavior.

---

## 2. Gate History

CDL-085 was deferred across multiple SIM windows:

| Phase | Evidence | Result |
|-------|----------|--------|
| 1146 | SIM-SPECTRAL-03 raw authority graph + topology audit | DEFER |
| 1162 | SIM-SPECTRAL-04 claim-composition projection | `sim_spectral_04_gate_fail` |
| 1171 | SIM-SPECTRAL-05 structural Sybil + branchial convergence tracks | `sim_spectral_05_gate_pass` |

The prior blocker:

`cdl_085_sim_gated_pending_sybil_discrimination_resolution`

is lifted for opening only by:

`cdl_085_sim_gate_lifted_phase_1172_sim_spectral_05_gate_pass`

---

## 3. Opening Scope

CDL-085 opens the following constitutional question:

> Should ILC ratify a Werner φ-bound provenance-equivalence limit governing when
> edge-mint / provenance-attribution claims are canonical productive work rather
> than Sybil-amplified or non-canonical derivation branches?

The amendment scope is constrained by ADR-0037 §3.2:

- legitimate derivation paths must converge at Genesis primitives, signed Genesis
  artifacts, accepted ADRs, or ratified CDLs;
- claimed-independent paths fail provenance equivalence if they converge first at
  a non-Genesis injection point, coordinated issuer, synthetic cluster, or
  unratified authority object;
- merge scope must be declared before any attribution, authority, versioning,
  economic-flow, or SIM-classification consequence is applied.

---

## 4. Candidate Decisions for Prelock

This opening does not resolve the following questions. They are prelock scope for
the next CDL-085 phase:

### Q1 — Bound object

Candidate bound objects:

- provenance-equivalent derivation paths only;
- all edge-mint events;
- all claim-composition events that participate in ECU/ILC attribution.

### Q2 — Bound expression

Candidate expressions:

- branchial convergence separation threshold;
- structural discriminant threshold over `lambda_max`, `spectral_gap`, and
  `degree_gini`;
- combined rule requiring both structural Sybil separation and branchial
  convergence separation.

### Q3 — φ interpretation

Candidate interpretations:

- φ as a named Werner productivity bound over edge-mint expansion;
- φ as a spectral-efficiency ratio;
- φ as a governance shorthand for the combined SIM-SPECTRAL-05 pass condition.

### Q4 — Runtime relation

Candidate runtime postures:

- no runtime constant yet; constitutional policy only;
- future `EDGE_MINT_PHI_BOUND` constant after ratification;
- runtime-binding slice required before activation.

### Q5 — Economic-flow dependency

Candidate economic scope:

- no ECU/ILC mint-surface change until economic-flow observer slice is tested;
- allow constitutional ratification first, runtime/economic activation later;
- require economic-flow SIM before ratification.

---

## 5. Evidence Basis

### 5.1 SIM-SPECTRAL-05 Track A

Track A retested against the actual Sybil topology family:

| Discriminant | z-score vs Sybil | Verdict |
|--------------|------------------|---------|
| `lambda_max` | 3.180229 | `discriminates_against_sybil` |
| `spectral_gap` | 2.775223 | `discriminates_against_sybil` |
| `degree_gini` | 2.726353 | `discriminates_against_sybil` |

### 5.2 SIM-SPECTRAL-05 Track B

Track B tested branchial convergence:

| Topology | Mean convergence rate |
|----------|-----------------------|
| S1 legitimate branchial paths | 0.85 |
| S3 branchial Sybil paths | 0.25 |
| Separation | 0.60 |

### 5.3 Provenance equivalence criterion

ADR-0037 §3.2 is the provenance equivalence criterion and policy anchor. The
operational Sybil separator is:

> a claimed set of independent paths fails provenance equivalence if the paths
> converge first at a non-Genesis injection point, coordinated issuer, synthetic
> cluster, or unratified authority object before they converge at a Genesis
> primitive or signed Genesis artifact.

---

## 6. Out of Scope

This opening does not:

- ratify CDL-085;
- set `EDGE_MINT_PHI_BOUND`;
- change `PROVENANCE_DECAY_ALPHA`;
- change `PROVENANCE_MAX_DEPTH`;
- mutate `ilc_core/`;
- change ECU/ILC economic runtime behavior;
- sign the v0.2 Genesis candidate;
- accept ADR-0037 or ADR-0036.

---

## 7. Prelock Requirements

Before ratification or runtime activation, a future phase must publish a CDL-085
prelock that resolves at minimum:

1. exact bound object;
2. exact φ-bound expression;
3. whether economic-flow observer-slice testing is required before ratification;
4. whether runtime-binding observer-slice testing is required before activation;
5. interaction with ADR-0037 if ADR-0037 remains Proposed or is accepted in Phase 1173.

---

## 8. References

- `docs/sims/sim_spectral_03/disposition_1146_v0.1.md`
- `docs/sims/sim_spectral_04/program.md` §5
- `docs/sims/sim_spectral_04/disposition_1162_v0.1.md`
- `docs/research/sim_spectral_04_structural_perturbation_research_1164_v0.1.md`
- `docs/sims/sim_spectral_05/program.md`
- `docs/sims/sim_spectral_05/disposition_1171_v0.1.md`
- `docs/adr/ADR_0037_Genesis_Canonical_Lineage_Contract.md` §3.2

---

`cdl_085_open_phase_1172`
`cdl_085_sim_gate_lifted_phase_1172_sim_spectral_05_gate_pass`
