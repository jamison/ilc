# ILC Distribution Architecture Roadmap v0.4

Status: non-normative planning artifact — subject to decision-log ratification
Date: 2026-03-05
Supersedes: ilc_distribution_architecture_roadmap_v0.3.md
Phase: 358

## 1. Strategic framing update

Roadmap v0.4 pivots from ratification-only progress tracking to execution sequencing for Windows 358-387.

D2d wire protocol is elevated from technical plumbing to a communication resilience layer.
Gossip-based discovery is the protocol immune system.
The objective is to make geographic and jurisdictional interference a routing resilience problem instead of a protocol continuity failure.
Implementation remains scheduled for Window 378+.
Design constraints include partition-tolerant epoch consensus and gossip topology privacy constraints.

## 2. Current track status snapshot

| Track | Status | Notes |
| --- | --- | --- |
| D1 Genesis reproducibility | completed | Closed in prior windows |
| D2 Protocol bundle/type system | completed | Ratified and operationalized |
| D2b Genesis state bundle | completed | Runtime and tests complete |
| D2c Epoch snapshots | completed | Runtime and closure-gate coverage complete |
| D2d Wire protocol | partial/incomplete | Baseline exists, resilience architecture deferred |
| D2e Agent SDK/CLI | partial/incomplete | Constitutional lane exists, implementation deferred |
| D3 OpenClaw integration | partial/incomplete | Planning in place, implementation pending |

## 3. Window 358-367 execution plan

Primary tracks in this window:
- Node schema implementation
- SIM commissioning
- CDL-039 opening

Phase sequence:
1. Phase 358: sequence lock and roadmap publish
2. Phase 359: additive CDL opening for CDL-039
3. Phase 360-364: bounded runtime implementation for CDL-034 through CDL-038
4. Phase 365: simulation commissioning
5. Phase 366: coherence and capsule v1.1
6. Phase 367: closure and handoff

CDL focus in this window:
- CDL-034
- CDL-035
- CDL-036
- CDL-037
- CDL-038
- CDL-039

## 4. Window 368-377 preview

Deferred from Window 358 and carried forward:
- V-series enforcement
- D2d deepening with privacy-aware topology constraints

The Window 368 lock must explicitly evaluate Levin gossip + coordinate mechanism proposals as candidate inputs, but no lock occurs in Phase 358.

## 5. Window 378+ preview

Future constitutional expansion and runtime lanes:
- CDL-040 through CDL-044
- D2d implementation lane
- D2e implementation lane

Wallet and signing strategy remains stable:
- wallet-agnostic identity surface
- signing provider interface continuity

## 6. Governance and remediation continuity

The 1000-series remediation track remains part of program governance carry-forward and must stay visible in roadmap status, with completed remediation phases preserved as closed historical actions.

## 7. Dependency and risk highlights

- Phase 359 is the only decision-log mutation phase in the near-term lock-start sequence.
- Runtime implementation in 360-364 remains bounded to ratified node-schema surfaces.
- CDL-039 prelock finalization remains deferred until post-SIM evidence in Phase 374.
- V-series runtime activation remains explicitly out of scope for Window 358-367.

## 8. Roadmap carry-forward directive

This roadmap supersedes v0.3 planning assumptions for active execution management in Windows 358-387 while preserving constitutional boundaries established by Phase 357 closure.
