# ILC Phase 505-514 Sequence Lock v0.1

Status: completed constitutional sequence lock
Date: 2026-03-30
Owner lane: G8 Constitution Cluster A

## 1. Window identity

Window 505-514 is open as of Phase 505.

This window is the canonical sequence lock for validator runtime carry-forward,
epoch-boundary witness law, and re_admission_boundary scoping. It is the only active
constitutional authority for Phases 505 through 514.

## 2. Carry-forward freeze

Window 505-514 freezes around:
- CDL-055 validator staking and liveness runtime implementation,
- CDL-056 validator trust-tier runtime implementation,
- CDL-057 epoch-boundary witness lane opened under the Phase 508 vehicle rationale,
- CDL-058 scoping only, with opening deferred,
- coherence, capsule, and closure-gate handoff work.

re_admission_boundary is out of scope for the CDL-055 runtime in Window 505-514.
CDL-058 opening is deferred to Window 515+.
CDL-053 remains reserved and unopened throughout Window 505-514.
Phase 514 is the closure gate.

## 3. Non-goals

This window does not authorize:
- opening or ratifying CDL-053,
- folding re_admission_boundary into the CDL-055 runtime,
- modifying the 7+1 quorum ladder or CDL-V3 diversity floor,
- validator co-location or recovery-lane work,
- any `ilc_core/` mutation in Phase 505.

## 4. Phase sequence and primary deliverables

| Phase | Topic | Primary deliverable |
| --- | --- | --- |
| 505 | Window sequence lock and carry-forward intake | `docs/specs/ilc_phase_505_514_sequence_lock_v0.1.md` |
| 506 | CDL-055 validator staking and liveness runtime | `ilc_core/validator/staking_liveness_runtime.py` |
| 507 | CDL-056 validator trust-tier runtime | `ilc_core/validator/trust_tier_runtime.py` |
| 508 | Epoch-boundary CDL vehicle selection | `docs/specs/ilc_epoch_boundary_cdl_vehicle_selection_508_v0.1.md` |
| 509 | Epoch-boundary CDL opening | `docs/specs/ilc_epoch_boundary_witness_opening_stub_509_v0.1.md` |
| 510 | Epoch-boundary CDL prelock hardening | `docs/specs/ilc_epoch_boundary_witness_prelock_hardening_510_v0.1.md` |
| 511 | Epoch-boundary CDL ratification | `docs/specs/ilc_epoch_boundary_witness_ratification_evidence_511_v0.1.md` |
| 512 | re_admission_boundary CDL scoping | `docs/specs/ilc_cdl_058_re_admission_boundary_scoping_512_v0.1.md` |
| 513 | Coherence report and capsule v2.4 | `docs/specs/ilc_antigravity_context_capsule_v2.4.md` |
| 514 | Window closure gate and handoff | `docs/specs/ilc_window_505_514_handoff_514_v0.1.md` |

## 5. Entry conditions from Window 495-504

Inherited entry conditions from Window 495-504:
- Window 495-504 is closed.
- CDL-055 is ratified.
- CDL-056 is ratified.
- CDL-057 is absent before Phase 509.
- CDL-058 is absent before Phase 512 and remains unopened in this window.
- `docs/specs/ilc_window_495_504_handoff_504_v0.1.md` exists.
