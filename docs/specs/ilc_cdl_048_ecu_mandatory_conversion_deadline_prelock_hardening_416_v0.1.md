# ILC CDL-048 ECU Mandatory Conversion Deadline Prelock Hardening 416 v0.1

Status: prelock hardening artifact
Date: 2026-03-15
Owner lane: G8 Constitution Cluster A

## 1. Scope and non-ratifying boundary

This artifact publishes the full non-ratifying prelock evidence record for `CDL-048`.

status: open

CDL-048 prelock hardening confirms the proposed candidate: governed conversion deadline with anti-hoarding forced circulation.

No CDL row mutation occurs in Phase 416.

Phase 419 is the targeted CDL-048 ratification lane; this hardening artifact constitutes the primary prelock evidence.

## 2. CDL-048 open-state evidence anchor

The live constitutional register remains in the Phase-414 opening state: `CDL-048` is present and remains `open`.

The authoritative open-state anchor for this lane is `docs/specs/ilc_cdl_048_ecu_mandatory_conversion_deadline_opening_stub_414_v0.1.md`.

The opening lane already locked the anti-hoarding and forced-circulation scope while leaving ratification and runtime implementation deferred.

## 3. Candidate discrimination and winning candidate confirmation

The proposed candidate is confirmed as the winning prelock candidate: governed conversion deadline with anti-hoarding forced circulation.

Indefinite ECU retention is rejected because it permits hoarding pressure and defeats the constitutional circulation objective of the ECU layer in the late economy.

Discretionary operator conversion windows is rejected because operator-level timing discretion would undermine uniform economic lifecycle rules and constitutional comparability across agents.

The winning candidate preserves a single constitutional deadline and a uniform circulation discipline across the network.

## 4. Section-7 ratification readiness evidence checklist satisfaction

1. The governed conversion deadline with anti-hoarding forced circulation is confirmed as the proposed candidate and both rejected candidates remain excluded.
2. SIM-008 deadline calibration anchor is locked: ecu_conversion_deadline = 4 issuance epochs, as the conversion-deadline prelock input.
3. Anti-hoarding intent is locked: ECU mandatory conversion eliminates ECU hoarding and forces ECU into economic circulation.
4. CDL-V1 temporal decay and CDL-035 lifecycle continuity is satisfied: CDL-048 complements the existing validation and circulation governance layers rather than replacing them.
5. No-reputation-carry-forward is locked: ECU-to-ILC conversion is a lifecycle transition and not an achievement or attribution event.

## 5. SIM-008 conversion-deadline calibration anchor

ecu_conversion_deadline = 4 issuance epochs

SIM-008 recommends this conversion-deadline anchor as the strongest late-economy planning candidate in the commissioned scenario grid.

The recommendation is a prelock calibration anchor and remains provisional until constitutional ratification in Phase 419.

This SIM-008 deadline anchor is a prelock input and does not become a constitutional constant until CDL-048 ratification in Phase 419.

## 6. Anti-hoarding and forced-circulation rationale

ECU mandatory conversion eliminates ECU hoarding and forces ECU into economic circulation.

The deadline prevents indefinite warehouse-style retention of ECU and preserves the intended role of ECU as a circulating medium rather than a speculative stockpile.

This circulation rule remains constitutionally provisional until Phase 419 ratification.

## 7. Relationship to CDL-V1 temporal decay and CDL-035 lifecycle

CDL-048 complements CDL-V1 temporal decay and CDL-035 lifecycle governance rather than replacing them.

CDL-V1 continues to govern validation-weight decay and circulation-health monitoring, while CDL-035 continues to govern lifecycle semantics. CDL-048 adds a separate late-economy economic lifecycle deadline for ECU conversion.

This continuity statement remains constitutionally provisional until Phase 419 ratification.

## 8. No-reputation-carry-forward clause and dependency chain

ECU-to-ILC conversion is a lifecycle transition and does not carry forward reputation or attribution automatically.

The prelock dependency chain for CDL-048 is:

- `docs/adr/ADR_0017_Post_Issuance_Economic_Transition.md`
- `CDL-V1`
- `CDL-035`
- `docs/specs/ilc_sim_008_commissioning_results_406_v0.1.md`

ADR-0017 provides the late-economy circulation and conversion rationale. CDL-V1 provides temporal-decay continuity. CDL-035 provides lifecycle boundary continuity. SIM-008 provides the deadline anchor.

## 9. Non-goals

Phase 416 does not ratify CDL-048.

Phase 416 does not mutate the constitutional decision log.

Phase 416 does not define conversion execution mechanics, CLI surfaces, or operator workflows.

Phase 416 does not patch CDL-047 or open CDL-049.

Phase 416 does not modify any `ilc_core/` runtime file.
