# ILC Window 555-564 Candidate Phase Grouping v0.1

Status: candidate phase grouping — awaiting sequence lock
Date: 2026-03-31
Owner lane: G8 Constitution Cluster A

This document supersedes the informal carry-forward notes in the Window 545-554 handoff.
The Phase 555 sequence lock will canonicalize and may amend this grouping.

---

## 1. Window purpose

Window 555-564 binds the ratified CDL-060 gossip lane to a real D2d transport surface,
locks the gossip HTTP envelope contract under CDL-061, and carries the signal-floor
invariant into ADR-0023 without reopening the economics lane.

Primary lane A: CDL-061 gossip HTTP envelope governance. Open in Phase 557, ratify in
Phase 561 after implementation evidence exists.

Primary lane B: D2d transport runtime. Publish `gossip_transport.py` in Phase 558,
harden transport invariants in Phases 559-560, and publish `gossip_peer_registry.py`
in Phase 562.

Documentation lane: carry the `recommended_decay_floor >= recommended_u_floor` invariant
into ADR-0023 in Phase 556, then close the window with coherence and closure artifacts in
Phases 563-564.

---

## 2. Carry-forward inputs from Window 545-554

| Item | Source | Window 555-564 action |
|---|---|---|
| `signal_floor_governance_adm_only` | Phase 547 | Phase 556 ADR-0023 update |
| `recommended_decay_floor >= recommended_u_floor` | Phase 547 / Phase 554 handoff | Phase 556 documentation lock |
| One-epoch attribution lag is accepted | Phase 548 | Preserved; no runtime change in this window |
| Crash-recovery graceful-zero logging | Phase 548 | Preserved; no runtime change in this window |
| CDL-060 single-hop lane remains complete | Phase 552 | Preserved; no multi-hop authorization |
| `sim_multi_hop_01_insufficient` | Phase 552 | Multi-hop remains deferred |
| `phase_554_verdict=pass` | Phase 554 | Entry gate for Phase 555 |

---

## 3. Architectural decisions locked at window entry

| Decision | Status | Window impact |
|---|---|---|
| ADR-0011 Native P2P Transport Baseline | Accepted | QUIC remains the production wire requirement |
| ADR-0025 D2d HTTP Gossip Transport Binding | Accepted | HTTP/3 over QUIC is production; HTTP/2 over TCP is fallback |
| CDL-024 kind mapping | settled via ADR-0025 | `kind=quic` for HTTP/3, `kind=http` for HTTP/2 |
| CDL-039 topology privacy | ratified | enforced at the gossip HTTP header layer |
| CDL-060 single-hop centrality delta lane | ratified | carried into header contract and transport adapter |

---

## 4. CDL status at window entry

| CDL | Status | Window 555-564 action |
|---|---|---|
| CDL-036 | ratified | no mutation |
| CDL-039 | ratified | no mutation; enforced in transport/header layer |
| CDL-052 | ratified | no mutation |
| CDL-059 | ratified | no mutation |
| CDL-060 | ratified | no mutation; consumed by transport adapter |
| CDL-061 | absent | open in Phase 557; ratify in Phase 561 |
| CDL-053 | reserved (unopened) | protected throughout |

---

## 5. Phase map

| Phase | Description | Primary output | Sensitive? |
|---|---|---|---|
| 555 | Window 555-564 sequence lock | `ilc_phase_555_564_sequence_lock_v0.1.md` | No |
| 556 | ADR-0023 signal floor invariant update | Updated `ADR_0023_Multi_Layer_Quality_Signal_Architecture.md` | No |
| 557 | CDL-061 open + prelock | CDL row + `ilc_cdl_061_gossip_http_envelope_prelock_557_v0.1.md` | Yes |
| 558 | HTTP gossip transport adapter | `ilc_core/network/d2d/gossip_transport.py` | Yes |
| 559 | Transport adapter hardening | `tests/test_phase_559_gossip_transport_hardening.py` + canary update | No |
| 560 | Canary probes for transport-layer invariants | Updated `tools/run_mutation_canary_phase_297.py` | No |
| 561 | CDL-061 ratification | CDL row update + dep update in `gossip_transport.py` | Yes |
| 562 | Static peer registry | `ilc_core/network/d2d/gossip_peer_registry.py` | Yes |
| 563 | Coherence report + capsule v2.9 | `ilc_integration_coherence_report_563_v0.1.md` + capsule | No |
| 564 | Window 555-564 closure gate + handoff | Gate script + handoff doc | Yes |

---

## 6. Protected boundaries and non-goals

Protected boundaries:
- CDL-053 remains reserved and unopened throughout the window.
- CDL-060 remains single-hop only; Window 555-564 does not reopen multi-hop.
- ADR-0025 transport selection is locked at entry; this window does not revisit libp2p.

Non-goals:
- no passive ECU formula recalibration
- no passive ECU runtime rewrite
- no DHT or dynamic peer discovery
- no genesis export/import or multi-machine packaging yet (carry-forward to Window 565-574)
- no node lifecycle/runtime packaging work beyond documenting carry-forwards

---

## 7. Execution notes

Expected ordering constraints:
- Phase 556 must land before CDL-061 opening to close the Phase 547 ADM-only invariant path.
- Phase 557 opens CDL-061 and publishes the prelock before any transport adapter code lands.
- Phase 558 implements against `CDL_061_DEPENDENCY = "cdl_061_prelock_557.v0.1"`.
- Phase 561 ratifies CDL-061 and updates `gossip_transport.py` to the ratified dep string.
- Phase 562 peer registry depends on the ratified transport layer.
- Phase 564 closure gate must verify the full dep chain and canary count of 8.
