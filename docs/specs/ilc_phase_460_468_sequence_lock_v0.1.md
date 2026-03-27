# ILC Phase 460-468 Sequence Lock v0.1

Status: completed constitutional sequence lock
Date: 2026-03-27
Owner lane: G8 Constitution Cluster A

## 1. Window identity

Window 460-468 is open as of Phase 460.

This window is the canonical sequence lock for the CDL-052 lane.
It is the only active constitutional authority for Phases 460 through 468.
Phase 459 Post1 through Phase 459 Post5 do not amend the constitutional scope or authority of Window 460-468.

## 2. Scope freeze

CDL-052 governs the three-mode epistemic evaluation architecture.

In scope for the CDL-052 lane:
- Mode 1 default reuse-valuation boundary,
- Mode 2 Popperian elevation via `refutation_criterion`,
- Mode 3 anomaly-triggered auditor review,
- schema and staking prerequisites required to open CDL-052,
- constitutional ratification of the epistemic evaluation architecture.

Out of scope for this window's CDL-052 lane:
- CDL-050 implementation,
- CDL-051 consensus runtime,
- temporal decay parameter calibration,
- runtime implementation in `ilc_core/`,
- Genesis validator implementation,
- OpenClaw implementation.

CDL-052 does not govern CDL-050 implementation, CDL-051 consensus runtime, or temporal decay parameter calibration.
Phase 460 does not open CDL-052.
CDL-052 remains absent at Phase 460 completion.

## 3. Non-goals

This window does not authorize:
- runtime implementation of CDL-052 surfaces,
- runtime implementation of CDL-051 consensus machinery,
- staking constant calibration,
- broader macro or Treasury scope carry-over,
- any decision-log mutation before the Gate 1 / Gate 2 / Gate 3 prerequisites are cleared.

## 4. Phase sequence and gate dependencies

CDL-052 may not open unless Gate 1, Gate 2, and Gate 3 are all cleared.

| Phase | Topic | Gate dependency | Progression rule |
| --- | --- | --- | --- |
| 460 | Window sequence lock and CDL-052 scope freeze | none | establishes the lane and freezes scope |
| 461 | ADR-0021 Epistemic Finality Claims | none | must produce Gate 1 disposition |
| 462 | `refutation_criterion` formal schema specification | Gate 1 cleared | must produce Gate 2 clearance |
| 463 | Minimal staking contract specification | Gate 1 cleared, Gate 2 cleared | must produce Gate 3 clearance |
| 464 | CDL-052 opening | Gate 1 cleared, Gate 2 cleared, Gate 3 cleared | must not proceed if any of Gates 1-3 is unresolved |
| 465 | CDL-052 prelock hardening and adversarial review | CDL-052 open and Gates 1-3 cleared | must not proceed if any of Gates 1-3 is unresolved |
| 466 | CDL-052 ratification and epistemic model closure | CDL-052 prelock and Gates 1-3 cleared | must not proceed if any of Gates 1-3 is unresolved |
| 467 | TLA+ CDL-051 shell specification | CDL-052 ratified | research/specification only |
| 468 | Genesis validator and OpenClaw scoping and Window 460-468 closure gate | CDL-052 ratified | closes the window and publishes handoff |

## 5. Entry conditions from Window 450-459

Inherited entry conditions from Window 450-459:
- CDL-050 is ratified.
- CDL-051 is ratified.
- `docs/specs/ilc_antigravity_context_capsule_v2.0.md` exists.
- `docs/specs/ilc_simplified_epistemic_model_synthesis_v0.1.md` exists and is committed.
- `docs/specs/ilc_refutation_novelty_requirement_v0.1.md` exists and is committed.
- Window 450-459 is closed and remains untouched by this sequence lock.
- Phase 459 Post1 through Phase 459 Post5 remain post-window supplements only and do not alter the authority of this window.
