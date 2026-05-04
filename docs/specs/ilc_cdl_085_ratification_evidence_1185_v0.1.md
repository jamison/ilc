# CDL-085 Ratification Evidence 1185 v0.1

**CDL:** CDL-085
**Ratification phase:** 1185
**Date:** 2026-05-04
**Status:** RATIFIED

`cdl_085_ratified_phase_1185`

---

## 1. Ratification Summary

CDL-085 ratifies the Werner phi-bound provenance equivalence limit for
provenance-equivalent derivation paths under ADR-0037 §3.2.

Ratified value:

```python
EDGE_MINT_PHI_BOUND = Decimal("0.60")
```

Dependency token:

```python
CDL_085_DEPENDENCY = "cdl_085_werner_phi_bound_ratified_1185.v0.1"
```

---

## 2. Prelock Reference

CDL-085 prelock was committed in Phase 1177:

- Prelock doc: `docs/specs/ilc_cdl_085_prelock_spec_1177_v0.1.md`
- Prelock commit: `509b6c6f`
- Prelock token: `cdl_085_prelock_committed_phase_1177`
- Candidate value: `EDGE_MINT_PHI_BOUND = Decimal("0.60")`

Phase 1184 added historical-hardening tests that read the opening and prelock states from
their original commits before ratification.

---

## 3. Q1-Q5 Resolution Summary

Q1 — Bound object:

- Selected: provenance-equivalent derivation paths only.
- Broader edge-mint and claim-composition surfaces remain outside this direct ratification
  unless evaluated through the provenance-equivalence path rule.

Q2 — Bound expression:

```text
valid_phi_bound(path_set) :=
    branchial_convergence_separation(path_set) >= Decimal("0.60")
    AND structural_sybil_discriminants_confirm(path_set)
```

Q3 — Phi interpretation:

- Werner productivity bound over provenance-equivalent edge-mint expansion.
- Paths below the branchial convergence separation threshold are not canonical productive
  work for CDL-085 purposes.

Q4 — Runtime relation:

- Constitutional policy plus active runtime constant after ratification.
- Runtime activation requires `sim_spectral_05_runtime_binding_slice_pass`.

Q5 — Economic-flow dependency:

- Economic-flow activation requires `sim_spectral_05_economic_flow_slice_pass`.
- The economic-flow slice must confirm Sybil suppression without suppressing legitimate
  attribution paths.

---

## 4. Activation Gate Clearances

The required observer-slice activation gates are satisfied:

- Runtime-binding: `sim_spectral_05_runtime_binding_slice_pass`
- Economic-flow: `sim_spectral_05_economic_flow_slice_pass`

Supporting references:

- `docs/sims/sim_spectral_05/runtime_binding_slice_disposition_1179_v0.1.md`
- `docs/sims/sim_spectral_05/economic_flow_slice_disposition_1180_v0.1.md`
- `docs/sims/sim_spectral_05/disposition_1171_v0.1.md`

---

## 5. Runtime Mutation Scope

Phase 1185 uses the required two-commit pattern:

1. CDL mutation commit:
   - `docs/specs/ilc_constitutional_decision_log_v0.1.md`
   - `docs/specs/ilc_cdl_085_ratification_evidence_1185_v0.1.md`
   - CDL-only tests in `tests/test_phase_1185_cdl_085_ratification.py`

2. Runtime activation commit:
   - `ilc_core/types.py`
   - `ilc_core/economics/epoch_attribution_settle_runtime.py`
   - Runtime import/value tests in `tests/test_phase_1185_cdl_085_ratification.py`

The runtime mutation must activate an exact numeric value:

```python
EDGE_MINT_PHI_BOUND: Decimal = Decimal("0.60")
```

Using `float` for this attribution bound is forbidden by repo coding standards.

---

## 6. RC2 Milestone

CDL-085 ratification satisfies RC2 gate 1:

```text
RC2 gate 1: CDL-085 ratified — SATISFIED
```

This does not sign v0.2, generate a release key, open CDL-001, or mutate signed Genesis
v0.1.

---

## 7. Ratification Tokens

```text
cdl_085_ratified_phase_1185
CDL_085_DEPENDENCY = "cdl_085_werner_phi_bound_ratified_1185.v0.1"
EDGE_MINT_PHI_BOUND = Decimal("0.60")
```
