# ILC Antigravity Context Capsule v2.7

Supersedes: docs/specs/ilc_antigravity_context_capsule_v2.6.md
Date: 2026-03-31
Owner lane: G8 Constitution Cluster A

This capsule is self-contained.

## 1. Current window state

Capsule v2.7 supersedes v2.6.
Window 535-544 remains active at Phase 543.
Phase 544 is the next authorized phase.

## 2. CDL status summary

CDL-052 is ratified.
CDL-059 is ratified (Phase 531).
CDL-060 is ratified (Phase 541).
CDL-053 remains reserved and unopened.

## 3. Window 535-544 summary

Window 535-544 advanced reuse centrality runtime in Phase 537, calibrated single-hop gossip
propagation in Phase 538, ratified CDL-060 in Phase 541, and calibrated the passive ECU
attribution formula in Phase 542.

## 4. Carry-forward items

CDL-060 gossip runtime is a Window 545+ carry-forward via the D2d gossip surface.
Passive ECU attribution runtime is a Window 545+ carry-forward.
Multi-hop centrality remains a Window 545+ carry-forward.
Window 545+ must decide epoch-boundary commit semantics before the CDL-060 gossip runtime is
implemented.
Signal-floor policy consistency beyond the aligned `0.05` floor remains a Window 545+
carry-forward.

## 5. Separate lanes

CDL-053 remains reserved and separate.
ADR-0022 private/gated boundary remains separate from the CDL-060 and passive-ECU lanes.

## 6. Next window state

Window 535-544 remains open only for the Phase 544 closure gate.
Phase 545+ requires a new sequence lock or amendment after the closure gate completes.
