# ILC CDL-058 re_admission_boundary Ratification Evidence 520 v0.1

Status: ratification evidence
Date: 2026-03-30
Owner lane: G8 Constitution Cluster A

## 1. Ratified lane identity

CDL-058 is ratified in Phase 520.
The ratified lane governs validator re_admission after `liveness_miss`, `equivocation`, or
`voluntary_exit` through cooldown periods measured in issuance epochs.

## 2. Evidence anchors

Required anchors:
- `docs/specs/ilc_cdl_058_re_admission_boundary_scoping_512_v0.1.md`
- `docs/specs/ilc_sim_011_re_admission_boundary_calibration_517_v0.1.md`
- `docs/specs/ilc_cdl_058_re_admission_boundary_opening_stub_518_v0.1.md`
- `docs/specs/ilc_cdl_058_re_admission_boundary_prelock_hardening_519_v0.1.md`

## 3. Rejected alternatives

Rejected alternatives preserved through ratification:
- sponsor or attestation-based re-entry gates,
- reputation-floor gating before re-admission,
- stake re-deposit as a constitutional re-entry prerequisite,
- timed_out amalgamation with `CDL-046`.

## 4. Constitutional boundary after ratification

The ratified boundary remains the narrow option `cooldown_period_per_exit_reason`.
Cooldown constants remain anchored to SIM-011 and measured in issuance epochs.
`CDL-046 timed_out` remains orthogonal to validator re-admission.
No ilc_core/ mutation occurs in Phase 520.

## 5. Governance tokens

cdl_058_governs_re_admission_boundary
cdl_046_timed_out_orthogonal
cdl_053_reserved
sim_011_calibrated_cooldown_constants

## 6. Section-5 ratification readiness evidence checklist satisfaction

Section 5 is satisfied because:
- the lane identity is explicitly tied to validator re_admission and not to node lifecycle repair,
- `CDL-046 timed_out` orthogonality is preserved from scoping through prelock,
- `CDL-053` remains reserved and unopened,
- the SIM-011 calibrated cooldown constants (`2 / 12 / 1` issuance epochs) remain the only
  evidence-backed constants admitted into the lane in this window.
