# ILC CDL-044 retention_epochs Amendment Open Prelock v0.1

Status: Phase-392 constitutional opening prelock
Date: 2026-03-09
Owner lane: G8 Constitution Cluster A

## 1. Purpose and scope

This artifact opens the constitutional amendment lane for retention_epochs deployment semantics after CDL-039 ratification.

The opening is additive and non-ratifying.

## 2. CDL-044 opening state

status: open

CDL-044 opens as the retention_epochs constitutional amendment lane required by CDL-039 ratification carry-forward obligations.

## 3. Constitutional obligation anchors

Anchors:
- Phase-379 CDL-039 ratification evidence naming the forward retention_epochs obligation.
- Phase-391 handoff carry-forward requirement that Window 392+ must open the amendment as first constitutional action.

## 4. Calibration anchor and bounded-range rationale

SIM-003 retention_epochs=1 is the floor anchor for calibration; this opening does not ratify a fixed operational value.

The bounded-range prelock is required because operational deployment conditions, network density regime, and post-ratification evidence assembly may justify a value above the floor while preserving constitutional constraints.

## 5. Evidence-assembly plan (393-398)

Evidence in this lane is assembled while ratification work proceeds for CDL-040, CDL-041, CDL-043 and while V-series resolution phases execute.

Inputs include:
- SIM-003 pre-network calibration,
- phase-by-phase constitutional consistency checks against CDL-039,
- coherence carry-forward obligations from Phases 390-391.

## 6. Sequencing and dependency constraints

Phase-399 is the targeted ratification lane for CDL-044 pending evidence assembly through Phases 393-398.

No runtime implementation occurs in Phase 392.

CDL-042 remains deferred in this phase and does not block CDL-044 opening.

## 7. Out-of-scope and deferred tracks

Treasury governance CDL cluster and mandatory ECU conversion deadline CDL remain out-of-scope in this phase and SIM-008 gated.

No economic governance CDL opening occurs in Phase 392.

## 8. Canonical anchors

- `docs/specs/ilc_cdl_039_p2p_transport_and_topology_privacy_ratification_evidence_379_v0.1.md`
- `docs/specs/ilc_window_378_391_handoff_391_v0.1.md`
- `docs/specs/ilc_sim_001_002_003_commissioning_results_365_v0.1.md`
- `docs/specs/ilc_sim_003_004_005_interpretation_and_cdl_039_risk_closure_371_v0.1.md`
