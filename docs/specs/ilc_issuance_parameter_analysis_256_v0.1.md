# ILC Issuance Parameter Analysis 256 v0.1

Status: Non-ratified analytical artifact
Date: 2026-02-21
Window: Phase 256
Primary anchors:
- `docs/specs/ilc_issuance_governance_plan_233_v0.1.md`
- `docs/specs/ilc_issuance_governance_activation_survey_247_v0.1.md`
- `docs/specs/ilc_constitutional_decision_log_v0.1.md`

## 1. Scope and methodology

This analysis evaluates issuance-governance queue readiness (`CDL-025` through `CDL-031`) and provides a closure-readiness assessment for `CDL-019`. Method:
- compare Phase-233 dependency map to Phase-247 activation survey,
- identify available evidence vs missing evidence per CDL,
- classify each CDL as `READY`, `NEAR-READY`, or `BLOCKED`.

## 2. Per-CDL ratification readiness assessment (CDL-025 through CDL-031)

| CDL | Topic | Current proposal baseline | Evidence available | Evidence gaps | Readiness verdict | Blocking prerequisites |
| --- | --- | --- | --- | --- | --- | --- |
| `CDL-025` | Terminal issuance model reconciliation | Model B fee-funded tail recommended in Phase 233 | Phase-233 model framing and Phase-247 dependency consistency | additional modeling on long-horizon fee sustainability | `NEAR-READY` | comparative simulation package for Model A/B/C |
| `CDL-026` | `C_max` lock | finite cap lock depends on CDL-025 closure | ordering dependency documented; downstream effects mapped | final cap candidate and sensitivity analysis missing | `BLOCKED` | CDL-025 decision candidate + cap analysis |
| `CDL-027` | Decay formulation and schedule | `H` vs `lambda` unresolved | dependency path documented in Phase-233 | schedule-specific scenario results missing | `BLOCKED` | CDL-026 cap baseline + schedule simulations |
| `CDL-028` | Fee-burn split ratio | unresolved split candidates | dependency to CDL-025 identified | market-behavior and incentive stress tests missing | `BLOCKED` | CDL-025 candidate + payout sensitivity studies |
| `CDL-029` | Allocation split validation | 80/15/5 proposed in planning | validation target defined with `theta_hard = 1/20` dependency | formal validation report and adversarial checks missing | `NEAR-READY` | allocation validation report |
| `CDL-030` | ECU clamp bounds | bounds derive from issuance schedule | dependency and derivation path documented | clamp-bound simulation and parameter envelope missing | `BLOCKED` | CDL-027 schedule closure + pricing simulations |
| `CDL-031` | Dynamic ranking multiplier policy | deferred behind CDL-019 | explicit defer posture documented | policy mechanism and invariant migration evidence missing | `BLOCKED` | CDL-019 closure and ranking-policy evidence |

## 3. Recommended ratification ordering

Recommended ordering from current evidence:
1. `CDL-025` (terminal issuance model) first.
2. `CDL-029` in parallel prep lane (validation evidence completion).
3. `CDL-026` after CDL-025 candidate stabilizes.
4. `CDL-027` after CDL-026.
5. `CDL-028` after CDL-025 evidence package completes.
6. `CDL-030` after CDL-027.
7. `CDL-031` only after CDL-019 closure criteria are satisfied.

Model-B assessment:
- Phase-233 Model B remains the strongest candidate but still requires additional fee-sustainability evidence before governance closure lanes.

## 4. Simulation and modeling requirements

Additional modeling recommended to close outstanding evidence gaps:
- long-horizon issuance sustainability across terminal model variants,
- cap sensitivity and emission-curve scenario sweeps,
- fee-burn split incentive impact under adversarial usage,
- allocation split resilience checks against concentration and gaming,
- clamp-bound stability tests under volatile reward demand.

Progress note (post-256, non-ratifying):
- epoch-duration wall-clock mapping and policy candidate table (`A/B/C`) now captured in
  `docs/specs/ilc_epoch_duration_candidate_matrix_and_policy_options_274_fix2_v0.1.md`,
- this narrows the schedule-selection ambiguity for `CDL-027` but does not ratify schedule constants.

## 5. Cross-reference and drift check

Cross-reference to activation survey:
- `docs/specs/ilc_issuance_governance_activation_survey_247_v0.1.md`

Constraint drift assessment:
- no additional issuance constraints were introduced by Phase 241-244 runtime work; Phase-247 drift statement remains valid.

## 6. CDL-019 closure assessment

Assessment target: multiplier-governance surface (`CDL-019`).

Evidence status:
- available: Phase-233 framing of flat constant, invariant floor, and dynamic policy defer path.
- missing: explicit migration plan artifacts and performance-rank policy proof package.

Recommendation:
- `NEEDS MORE WORK`.

Rationale:
- the current evidence is structurally strong but does not yet include full migration and governance-operational evidence needed for closure.

## 7. Non-goal boundaries

This analysis does not:
- execute any CDL status mutation,
- lock issuance parameter values,
- trigger any ratification action,
- modify `ilc_core/` runtime behavior.
