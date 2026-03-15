# ILC CDL-047 Treasury Governance Ratification Evidence 418 v0.1

Status: ratification evidence artifact
Date: 2026-03-15
Owner lane: G8 Constitution Cluster A

## 1. Scope and ratification boundary

This artifact records the ratification evidence for `CDL-047` only.

Phase 418 ratifies `CDL-047` and mutates no other CDL row.

No runtime mutation occurs in `ilc_core/` during this phase.

## 2. CDL-047 open-state anchor

The authoritative historical open-state anchor for this lane is the Phase-414 opening batch:
- `docs/specs/ilc_cdl_047_treasury_governance_opening_stub_414_v0.1.md`
- the Phase-414 decision-log snapshot where `CDL-047` first entered the register as `status: open`

That historical opening state remains the anchor consumed by this ratification artifact and by the
required historical hardening applied to the Phase-414, Phase-415, and Phase-417 test suites.

## 3. Constitutional evidence for treasury governance framework

CDL-047 is ratified as the treasury governance framework for bounty issuance cap, late-economy burn floor, velocity alert, and counter-cyclical authorization.

CDL-047 layers on CDL-028 without amending the 10% genesis fee-burn default.

Counter-cyclical treasury authorization is constitutionally bounded to late-economy stabilization and does not amend the 10% genesis fee-burn default of CDL-028.

Fixed treasury constants without adaptive governance is rejected because the genesis fee-burn default does not provide a constitutional mechanism for late-economy adjustment as the issuance-to-fee transition progresses.

Defer treasury governance indefinitely pending later study is rejected because SIM-008 provides a sufficient calibrated evidence base for constitutional opening, and indefinite deferral leaves a governance gap during the issuance-to-fee transition period.

## 4. Phase-415 prelock hardening anchor

The ratification record relies directly on `docs/specs/ilc_cdl_047_treasury_governance_prelock_hardening_415_v0.1.md` as the primary prelock evidence artifact.

Phase 415 locked the winning candidate, both rejection rationales, the CDL-028 layering clause, the
bounded counter-cyclical authorization scope, and the three SIM-008 calibration anchors that now
become ratified governance constants in this phase.

## 5. SIM-008 calibration evidence satisfaction

The SIM-008 calibration evidence is accepted as constitutionally sufficient for ratification of the treasury-governance framework.

The ratified governance constants are:
- per-epoch bounty issuance cap of 0.15 × B_e
- late-economy fee-burn floor of 0.05
- ILC velocity monitoring alert floor of 0.91

These calibrated values remain bounded governance constants inside the CDL-047 constitutional lane and do not alter the genesis default of CDL-028.

## 6. Section-7 ratification readiness evidence checklist satisfaction

1. The Phase-414 opening row and opening stub remain the authoritative historical open-state anchor for `CDL-047`.
2. The Phase-415 prelock artifact confirms the selected treasury-governance candidate and preserves exclusion of both rejected candidates.
3. The SIM-008 calibration anchors are accepted as ratified governance constants: `bounty_cap = 0.15 × B_e`, `burn_floor = 0.05`, and `velocity_alert_floor = 0.91`.
4. The CDL-028 layering clause and counter-cyclical authorization boundary are satisfied without amending the 10% genesis fee-burn default.
5. The Phase-417 governance review recorded no `CDL-047`-specific blocking defect and therefore does not block ratification.

## 7. Ratified governance tokens and constitutional effect

Phase 417 recorded no CDL-047-specific or CDL-048-specific CRITICAL findings; Phase 418 proceeds unblocked.

The ratified treasury-governance effect is:
- per-epoch bounty issuance cap of 0.15 × B_e
- late-economy fee-burn floor of 0.05
- ILC velocity monitoring alert floor of 0.91

The constitutional effect is a bounded adaptive-governance lane for late-economy treasury stabilization, subject to the counter-cyclical authorization boundary and the preserved CDL-028 genesis fee-burn default.

## 8. Non-goals and boundary

Phase 418 does not ratify `CDL-048`.

Phase 418 does not open `CDL-049`.

Phase 418 does not alter the content of the Phase-414 opening stubs, the Phase-415 prelock artifact, the Phase-416 prelock artifact, or the Phase-417 governance review artifact.

Phase 418 does not modify any `ilc_core/` runtime file.

## 9. Canonical anchors

- `docs/specs/ilc_constitutional_decision_log_v0.1.md`
- `docs/specs/ilc_phase_414_423_sequence_lock_v0.1.md`
- `docs/specs/ilc_cdl_047_treasury_governance_opening_stub_414_v0.1.md`
- `docs/specs/ilc_cdl_047_treasury_governance_prelock_hardening_415_v0.1.md`
- `docs/specs/ilc_popperian_claim_form_governance_review_417_v0.1.md`
- `docs/specs/ilc_sim_008_commissioning_results_406_v0.1.md`
- `docs/adr/ADR_0016_Productive_ECU_Expansion_Bounty_Mechanism.md`
- `docs/adr/ADR_0017_Post_Issuance_Economic_Transition.md`
