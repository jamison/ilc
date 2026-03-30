# ILC Phase 515-524 Sequence Lock v0.1

Status: completed constitutional sequence lock
Date: 2026-03-30
Owner lane: G8 Constitution Cluster A

## 1. Window identity

Window 515-524 is open as of Phase 515.

This window is the canonical sequence lock for the CDL-057 epoch-boundary witness runtime,
SIM-011 re_admission calibration, CDL-058 constitutional lifecycle work, and ADR-0023 scoping.
It is the only active constitutional authority for Phases 515 through 524.

## 2. Carry-forward freeze

Window 515-524 freezes around:
- CDL-057 epoch-boundary witness runtime implementation,
- SIM-011 calibration for validator re-admission cooldowns,
- CDL-058 opening, prelock, ratification, and runtime implementation,
- ADR-0023 quality signal CDL scoping,
- coherence, capsule, and closure-gate handoff work.

CDL-057 runtime implementation is authorized for Window 515-524.
SIM-011 is required before CDL-058 can be opened.
CDL-053 remains reserved and unopened throughout Window 515-524.
Phase 524 is the closure gate.

## 3. Non-goals

This window does not authorize:
- opening or ratifying CDL-053,
- implementing blocking authority for epoch-boundary witnesses,
- opening CDL-059 in Window 515-524,
- altering the 7+1 quorum ladder or CDL-V3 diversity floor,
- modifying any Genesis bootstrap or admission-control lane.

## 4. Phase sequence and primary deliverables

| Phase | Topic | Primary deliverable |
| --- | --- | --- |
| 515 | Window sequence lock and carry-forward intake | `docs/specs/ilc_phase_515_524_sequence_lock_v0.1.md` |
| 516 | CDL-057 epoch-boundary witness runtime | `ilc_core/epoch/epoch_boundary_witness_runtime.py` |
| 517 | SIM-011 re_admission boundary calibration | `docs/specs/ilc_sim_011_re_admission_boundary_calibration_517_v0.1.md` |
| 518 | CDL-058 re_admission boundary opening | `docs/specs/ilc_cdl_058_re_admission_boundary_opening_stub_518_v0.1.md` |
| 519 | CDL-058 prelock hardening | `docs/specs/ilc_cdl_058_re_admission_boundary_prelock_hardening_519_v0.1.md` |
| 520 | CDL-058 ratification | `docs/specs/ilc_cdl_058_re_admission_boundary_ratification_evidence_520_v0.1.md` |
| 521 | CDL-058 re_admission boundary runtime | `ilc_core/validator/re_admission_runtime.py` |
| 522 | ADR-0023 CDL scoping analysis | `docs/specs/ilc_adr_0023_cdl_scoping_analysis_522_v0.1.md` |
| 523 | Coherence report and capsule v2.5 | `docs/specs/ilc_antigravity_context_capsule_v2.5.md` |
| 524 | Window closure gate and handoff | `docs/specs/ilc_window_515_524_handoff_524_v0.1.md` |

## 5. Entry conditions from Window 505-514

Inherited entry conditions from Window 505-514:
- Window 505-514 is closed on the success path.
- CDL-055 is ratified.
- CDL-056 is ratified.
- CDL-057 is ratified.
- CDL-058 is absent before Phase 518.
- `docs/specs/ilc_window_505_514_handoff_514_v0.1.md` exists.
