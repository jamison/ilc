# ILC Antigravity Context Capsule v2.8

Supersedes: docs/specs/ilc_antigravity_context_capsule_v2.7.md
Date: 2026-03-31
Owner lane: G8 Constitution Cluster A

This capsule is self-contained.

## 1. Current window state

Capsule v2.8 supersedes v2.7.
Window 545-554 remains active at Phase 553.
Phase 554 is the next authorized phase.

## 2. CDL status summary

CDL-052 is ratified.
CDL-059 is ratified.
CDL-060 is ratified.
CDL-053 remains reserved and unopened.

## 3. Window 545-554 summary

Window 545-554 selected `epoch_boundary_atomic` accumulation in Phase 546, implemented the
CDL-060 gossip runtime in Phase 548, implemented the passive ECU attribution runtime in Phase 550,
and concluded in Phase 552 that SIM-MULTI-HOP-01 is insufficient for a new multi-hop CDL opening.

## 4. Carry-forward items

SIM-MULTI-HOP-01 is insufficient and multi-hop remains deferred pending future evidence.
Signal-floor policy remains `signal_floor_governance_adm_only` and Window 555+ must record the
invariant `recommended_decay_floor >= recommended_u_floor` in ADR guidance.
CDL-053 remains reserved and unopened.

## 5. Separate lanes

CDL-053 remains reserved and separate.
The multi-hop planning track remains separate from the ratified CDL-060 single-hop lane.
Passive ECU runtime follow-through remains separate from any future multi-hop governance lane.

## 6. Next window state

Window 545-554 remains open only for the Phase 554 closure gate.
Phase 555+ requires a new sequence lock or amendment.
