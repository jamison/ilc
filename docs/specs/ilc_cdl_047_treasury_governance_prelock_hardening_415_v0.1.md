# ILC CDL-047 Treasury Governance Prelock Hardening 415 v0.1

Status: prelock hardening artifact
Date: 2026-03-15
Owner lane: G8 Constitution Cluster A

## 1. Scope and non-ratifying boundary

This artifact publishes the full non-ratifying prelock evidence record for `CDL-047`.

status: open

CDL-047 prelock hardening confirms the proposed candidate: governed treasury framework with bounty-cap, burn-floor, velocity-alert, and counter-cyclical authorization.

No CDL row mutation occurs in Phase 415.

Phase 418 is the targeted CDL-047 ratification lane; this hardening artifact constitutes the primary prelock evidence.

## 2. CDL-047 open-state evidence anchor

The live constitutional register remains in the Phase-414 opening state: `CDL-047` is present and remains `open`.

The authoritative open-state anchor for this lane is `docs/specs/ilc_cdl_047_treasury_governance_opening_stub_414_v0.1.md`.

The Phase-414 opening lane already locked the core constitutional framing that CDL-047 layers on CDL-028 without amending the 10% genesis fee-burn default.

## 3. Candidate discrimination and winning candidate confirmation

The proposed candidate is confirmed as the winning prelock candidate: governed treasury framework with bounty-cap, burn-floor, velocity-alert, and counter-cyclical authorization.

Fixed treasury constants without adaptive governance is rejected because the genesis fee-burn default does not provide a constitutional mechanism for late-economy adjustment as the issuance-to-fee transition progresses.

Defer treasury governance indefinitely pending later study is rejected because SIM-008 provides a sufficient calibrated evidence base for constitutional opening, and indefinite deferral leaves a governance gap during the issuance-to-fee transition period.

CDL-047 layers on CDL-028 without amending the 10% genesis fee-burn default.

CDL-047 authorizes an adaptive governance mechanism that allows the burn ratio to be reduced below 10% by governance action as the economy matures, subject to a constitutional burn floor of 0.05.

## 4. Section-7 ratification readiness evidence checklist satisfaction

1. The governed treasury framework with bounty-cap, burn-floor, velocity-alert, and counter-cyclical authorization is confirmed as the proposed candidate and both rejected candidates remain excluded.
2. SIM-008 bounty-cap calibration anchor is locked: bounty_cap = 0.15 × B_e, as the per-epoch bounty issuance cap prelock input.
3. SIM-008 burn-floor and velocity-alert calibration anchors are locked: burn_floor = 0.05 and velocity_alert_floor = 0.91, as the late-economy policy floor prelock inputs.
4. CDL-028 layering clause is satisfied: CDL-047 layers on CDL-028 without amending the 10% genesis fee-burn default; CDL-047 authorizes the adaptive governance mechanism only.
5. Counter-cyclical authorization scope is constitutionally bounded to late-economy stabilization; fixed-parameter and indefinitely-deferred candidates remain excluded.

## 5. SIM-008 bounty-cap calibration anchor

bounty_cap = 0.15 × B_e

SIM-008 recommends this bounty-cap anchor because it maximized average policy score across the commissioned scenario grid while keeping treasury drawdown bounded under low-fee conditions.

Under ADR-0016, bounty issuance functions as a bounded counter-cyclical productive-stimulus mechanism. The cap is therefore an upper bound on per-epoch treasury bounty issuance, not a floor or a target.

This anchor remains constitutionally provisional until CDL-047 ratification in Phase 418.

## 6. SIM-008 burn-floor calibration anchor

burn_floor = 0.05

SIM-008 recommends this burn-floor anchor because it preserves a non-zero permanent sink while outperforming zero-burn and high-burn alternatives on combined stability and resilience metrics.

This floor is the lower bound of the adaptive governance range. The CDL-028 genesis default remains 10%, and Phase 415 does not amend or replace that genesis value.

This anchor remains constitutionally provisional until CDL-047 ratification in Phase 418.

## 7. SIM-008 velocity-alert calibration anchor

velocity_alert_floor = 0.91

SIM-008 recommends this velocity-alert anchor as the conservative lower-tail planning threshold from the selected policy lane.

Velocity below this floor is a monitoring signal rather than an automatic governance trigger. Trigger mechanics, intervention thresholds, and operational treasury responses remain deferred.

This anchor remains constitutionally provisional until CDL-047 ratification in Phase 418.

These SIM-008 calibration anchors are prelock inputs and do not become constitutional constants until CDL-047 ratification in Phase 418.

## 8. Upstream dependency chain

The prelock dependency chain for CDL-047 is:

- `docs/adr/ADR_0016_Productive_ECU_Expansion_Bounty_Mechanism.md`
- `docs/adr/ADR_0017_Post_Issuance_Economic_Transition.md`
- `CDL-028`
- `CDL-030`
- `docs/specs/ilc_sim_008_commissioning_results_406_v0.1.md`

ADR-0016 provides the architectural rationale for bounty-cap governance as bounded productive stimulus.

ADR-0017 provides the late-economy adaptive-burn, treasury-stabilization, and velocity-monitoring rationale for this lane.

CDL-028 provides the genesis fee-burn default that CDL-047 layers on without amendment.

CDL-030 establishes ECU price-clamp bounds that treasury governance must remain compatible with.

SIM-008 provides all three calibration anchors used in this prelock.

## 9. Non-goals

Phase 415 does not ratify CDL-047.

Phase 415 does not mutate the constitutional decision log.

Phase 415 does not define treasury trigger mechanics, treasury drawdown limits, or sunset-fuse parameters.

Phase 415 does not harden CDL-048 or open CDL-049.

Phase 415 does not modify any `ilc_core/` runtime file.
