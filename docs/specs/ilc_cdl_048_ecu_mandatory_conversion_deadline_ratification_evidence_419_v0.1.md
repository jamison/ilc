# ILC CDL-048 ECU Mandatory Conversion Deadline Ratification Evidence 419 v0.1

Status: ratification evidence artifact
Date: 2026-03-15
Owner lane: G8 Constitution Cluster A

## 1. Scope and ratification boundary

This artifact records the ratification evidence for `CDL-048` only.

Phase 419 ratifies `CDL-048` and mutates no other CDL row.

No runtime mutation occurs in `ilc_core/` during this phase.

## 2. CDL-048 open-state anchor

The authoritative historical open-state anchor for this lane is the Phase-414 opening batch:
- `docs/specs/ilc_cdl_048_ecu_mandatory_conversion_deadline_opening_stub_414_v0.1.md`
- the Phase-414 decision-log snapshot where `CDL-048` first entered the register as `status: open`

That historical opening state remains the anchor consumed by this ratification artifact and by the
required historical hardening applied to the Phase-414, Phase-416, Phase-417, and Phase-418 test suites.

## 3. Constitutional evidence for ECU mandatory conversion deadline

CDL-048 is ratified as the ECU mandatory conversion deadline framework for forced circulation and anti-hoarding policy.

ECU mandatory conversion eliminates ECU hoarding and forces ECU into economic circulation.

CDL-048 complements CDL-V1 temporal decay and CDL-035 lifecycle governance rather than replacing them.

ECU-to-ILC conversion is a lifecycle transition and does not carry forward reputation or attribution automatically.

Indefinite ECU retention is rejected because it permits hoarding pressure and defeats the constitutional circulation objective of the ECU layer in the late economy.

Discretionary operator conversion windows is rejected because operator-level timing discretion would undermine uniform economic lifecycle rules and constitutional comparability across agents.

## 4. Phase-416 prelock hardening anchor

The ratification record relies directly on `docs/specs/ilc_cdl_048_ecu_mandatory_conversion_deadline_prelock_hardening_416_v0.1.md` as the primary prelock evidence artifact.

Phase 416 locked the winning conversion-deadline candidate, both rejection rationales, the anti-hoarding and forced-circulation clause, the CDL-V1 and CDL-035 continuity clause, the no-reputation-carry-forward clause, and the SIM-008 deadline anchor that now becomes ratified in this phase.

## 5. SIM-008 deadline calibration evidence satisfaction

ecu_conversion_deadline = 4 issuance epochs

The SIM-008 deadline calibration evidence is accepted as constitutionally sufficient for ratification of the ECU mandatory conversion deadline lane.

This ratified governance constant fixes a uniform deadline for forced circulation and anti-hoarding enforcement without introducing operator-specific timing discretion.

## 6. Section-7 ratification readiness evidence checklist satisfaction

1. The Phase-414 opening row and opening stub remain the authoritative historical open-state anchor for `CDL-048`.
2. The Phase-416 prelock artifact confirms the selected conversion deadline candidate and preserves exclusion of both rejected candidates.
3. The SIM-008 deadline calibration anchor is accepted as a ratified governance constant: `ecu_conversion_deadline = 4 issuance epochs`.
4. The CDL-V1 temporal decay and CDL-035 lifecycle continuity clause is satisfied: CDL-048 complements rather than replaces the existing validation and circulation governance layers.
5. The Phase-417 governance review recorded no `CDL-048`-specific blocking defect and therefore does not block ratification.

## 7. Ratified governance tokens and constitutional effect

Phase 417 recorded no CDL-047-specific or CDL-048-specific CRITICAL findings; Phase 419 proceeds unblocked.

The ratified governance effect is:
- ecu_conversion_deadline = 4 issuance epochs
- ECU mandatory conversion eliminates ECU hoarding and forces ECU into economic circulation.
- ECU-to-ILC conversion is a lifecycle transition and does not carry forward reputation or attribution automatically.

The constitutional effect is a bounded circulation-enforcement lane that attaches a fixed late-economy deadline to ECU conversion while preserving CDL-V1 temporal decay and CDL-035 lifecycle semantics.

## 8. Non-goals and boundary

Phase 419 does not mutate `CDL-047`.

Phase 419 does not open `CDL-049`.

Phase 419 does not alter the content of the Phase-414 opening stubs, the Phase-416 prelock artifact, the Phase-417 governance review artifact, or the Phase-418 ratification evidence artifact.

Phase 419 does not modify any `ilc_core/` runtime file.

## 9. Canonical anchors

- `docs/specs/ilc_constitutional_decision_log_v0.1.md`
- `docs/specs/ilc_phase_414_423_sequence_lock_v0.1.md`
- `docs/specs/ilc_cdl_048_ecu_mandatory_conversion_deadline_opening_stub_414_v0.1.md`
- `docs/specs/ilc_cdl_048_ecu_mandatory_conversion_deadline_prelock_hardening_416_v0.1.md`
- `docs/specs/ilc_popperian_claim_form_governance_review_417_v0.1.md`
- `docs/specs/ilc_sim_008_commissioning_results_406_v0.1.md`
- `docs/adr/ADR_0017_Post_Issuance_Economic_Transition.md`
