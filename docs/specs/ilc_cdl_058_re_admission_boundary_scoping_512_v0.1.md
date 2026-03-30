# ILC CDL-058 re_admission_boundary Scoping 512 v0.1

Status: scoping
Date: 2026-03-30
Owner lane: G8 Constitution Cluster A

## 1. Scope description

cdl_058_governs_re_admission_boundary

CDL-058 governs the validator re-admission boundary after:
- liveness threshold failure (`liveness_miss_threshold` breach),
- equivocation recovery after slash,
- voluntary exit followed by attempted re-entry.

## 2. Candidate design options

Candidate options for a future CDL-058 lane:
- cool-down period in epochs before validator re-entry,
- stake re-deposit requirement before re-admission,
- reputation floor anchored to CDL-V1/V2 before re-admission,
- sponsor attestation for re-entry into validator status.

## 3. Dependency interactions

Interaction notes:
- a reputation floor interacts with CDL-V2 sybil resistance and CDL-V1 reputation decay,
- sponsor attestation interacts with CDL-V2 sybil resistance,
- any re-entry rule that materially changes validator distribution may interact with the CDL-V3
  diversity floor.

## 4. Simulation disposition

sim_011_required

SIM-010 is not sufficient to settle the re-admission boundary because it did not model post-slash
re-entry behavior, sponsor pathways, or reputation-floor effects across validator churn.

## 5. Window 515+ opening prerequisites

Window 515+ opening prerequisites:
- choose one or more candidate options for constitutional narrowing,
- define the relationship to CDL-046 timed recovery semantics,
- define the relationship to CDL-V1/V2 reputation and sybil controls,
- define validator-diversity safeguards if re-entry affects active-set concentration.

No decision-log mutation occurs in Phase 512.
cdl_058_opening_deferred_to_window_515_plus
CDL-058 opening is deferred to Window 515+.
Phase 513 is the next authorized phase.
