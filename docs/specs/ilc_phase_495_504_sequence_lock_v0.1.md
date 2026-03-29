# ILC Phase 495-504 Sequence Lock v0.1

Status: completed constitutional sequence lock
Date: 2026-03-29
Owner lane: G8 Constitution Cluster A

## 1. Window identity

Window 495-504 is open as of Phase 495.

This window is the canonical sequence lock for validator trust-tier and staking carry-forward
work. It is the only active constitutional authority for Phases 495 through 504.

## 2. Scope freeze

Window 495-504 freezes around:
- CDL-055 carry-forward ratification as the first priority of the window,
- governance-boundary analysis for Validator Trust-Tier Elevation,
- provisional assignment of CDL-056 to Validator Trust-Tier Elevation,
- epoch-boundary enforcement architectural scoping,
- optional ADM-001 v0.3 publication only if CDL-056 ratifies,
- coherence, capsule, and closure-gate handoff work.

CDL-055 is the first ratification target of Window 495-504.
CDL-056 is provisionally assigned to Validator Trust-Tier Elevation.
CDL-053 remains reserved and unopened.
Phase 497 governance boundary analysis gates CDL-056 opening.

No decision-log mutation occurs in Phase 495.

## 3. Non-goals

This window does not authorize:
- opening or ratifying CDL-053,
- redesigning the 7+1 quorum ladder or L-tier requirements,
- validator co-location or validator network join/recovery work,
- epoch-boundary CDL amendment ratification,
- `ilc_core/` runtime mutation in Phase 495.

## 4. Phase sequence and gate dependencies

| Phase | Topic | Gate dependency | Progression rule |
| --- | --- | --- | --- |
| 495 | Window sequence lock and CDL-055 disposition | none | opens the lane and freezes numbering and scope |
| 496 | CDL-055 ratification evidence | Phase 495 complete | ratifies the carry-forward staking and liveness lane |
| 497 | Validator trust-tier governance boundary analysis | Phase 496 complete | determines whether CDL-056 may open or must remain deferred |
| 498 | Epoch-boundary enforcement architectural scoping | Phase 496 complete | records carry-forward analysis without opening a CDL |
| 499 | CDL-056 opening stub | Phases 496-497 complete | opens CDL-056 only if the governance boundary analysis authorizes it |
| 500 | CDL-056 prelock hardening | Phase 499 complete | hardens the open CDL-056 lane without ratifying it |
| 501 | CDL-056 ratification evidence | Phase 500 complete | ratifies CDL-056 if the prelock and governance boundary support it |
| 502 | ADM-001 v0.3 validator trust-tier amendment | Phase 501 complete | publishes the companion amendment only after CDL-056 ratifies |
| 503 | Coherence report and capsule v2.3 | Phases 496 and 498 complete; 499-502 if executed | records either the successful or blocked trust-tier path |
| 504 | Closure gate and handoff | executed Phases 495-503 complete | closes the window under the successful or blocked scenario |

Phase 496 must complete before Phase 499.
Phase 497 must complete before Phase 499.
If executed, Phase 502 must complete before Phase 503.
Phase 504 always executes as the closure gate.

## 5. Entry conditions from Window 485-494

Inherited entry conditions from Window 485-494:
- CDL-054 is ratified.
- CDL-055 is status: open and prelock-hardened.
- Window 485-494 is closed.
- `docs/specs/ilc_window_485_494_handoff_494_v0.1.md` exists.
- Phase 495 is the next numbered phase after Window 485-494.
