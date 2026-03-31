# ILC Phase 555-564 Sequence Lock v0.1

Status: locked
Date: 2026-03-31
Phase: 555
Owner lane: G8 Constitution Cluster A

## 1. Window summary

Window 555-564 binds the ratified CDL-060 single-hop gossip lane to a real D2d transport
surface. The window references accepted ADR-0011 and ADR-0025, commits the CDL-061 opening
lane for Phase 557, closes the Phase 547 signal-floor documentation obligation in Phase 556,
and defers CDL-061 ratification until implementation evidence exists.

Required lock tokens:
- `gossip_transport_http3_binding_selected`
- `cdl_061_gossip_http_envelope_to_open_phase_557`
- `adr_023_invariant_update_phase_556`
- `kind_quic_http3_production_kind_http_http2_fallback`
- `cdl_061_ratification_after_implementation`
- `static_peer_config_no_dht_v1`

## 2. Phase table

| Phase | Description | Primary output | Sensitive? |
|---|---|---|---|
| 555 | Window 555-564 sequence lock | `ilc_phase_555_564_sequence_lock_v0.1.md` | No |
| 556 | ADR-0023 signal floor invariant update | Updated `ADR_0023_Multi_Layer_Quality_Signal_Architecture.md` | No |
| 557 | CDL-061 open + prelock (gossip HTTP envelope) | CDL row + `ilc_cdl_061_gossip_http_envelope_prelock_557_v0.1.md` | YES |
| 558 | HTTP gossip transport adapter | `ilc_core/network/d2d/gossip_transport.py` | YES |
| 559 | Transport adapter hardening | `tests/test_phase_559_gossip_transport_hardening.py` + canary update | No |
| 560 | Canary probes for transport-layer invariants | Updated `tools/run_mutation_canary_phase_297.py` | No |
| 561 | CDL-061 ratification | CDL row update + dep-chain update in `gossip_transport.py` | YES |
| 562 | Static peer registry | `ilc_core/network/d2d/gossip_peer_registry.py` | YES |
| 563 | Coherence report + capsule v2.9 | `ilc_integration_coherence_report_563_v0.1.md` + capsule | No |
| 564 | Window 555-564 closure gate + handoff | Gate script + handoff doc | YES |

## 3. CDL track

This window opens and ratifies exactly one new CDL lane:
- One new CDL opening: CDL-061 (ILC gossip HTTP envelope contract), Phase 557.
- One new CDL ratification: CDL-061, Phase 561.
- No other CDL mutations in this window.

CDL-061 covers the gossip HTTP envelope contract: header field set, CDL-039 required
exclusions, CDL-060 hop-count header enforcement, HTTP status code semantics
(202/204/400/409/429/503), CBOR required encoding, and CDL-024 kind canonical
representation.

## 4. Architectural decisions locked

Accepted ADRs and transport decisions are locked for the full window:
- ADR-0025: HTTP/3 over QUIC (`kind=quic`) is the production transport binding.
- ADR-0025: HTTP/2 over TLS/TCP (`kind=http`) is the permitted fallback where UDP/QUIC is blocked.
- ADR-0011: QUIC-based encrypted streams remain the production wire requirement; ADR-0025 is
  consistent because HTTP/3 IS QUIC at the wire layer.
- CDL-039 topology privacy requirements are enforced at the HTTP header layer in Phase 559.

## 5. Carry-forward tokens from Window 545-554

The following carry-forwards are locked into this window:
1. `phase_547_adr_023_invariant_obligation` — `recommended_decay_floor >= recommended_u_floor`
   must be documented in ADR-0023; assigned to Phase 556.
2. `phase_548_1_epoch_attribution_lag_design_property` — CDL-060 gossip runtime v1 lag is
   accepted and does not require an implementation change in this window.
3. `phase_548_crash_recovery_graceful_zero` — zeroed epoch buffers are explicitly logged; no
   silent drop is permitted.
4. `cdl_061_prelock_dep_token` — Phase 558 transport adapter must use
   `CDL_061_DEPENDENCY = "cdl_061_prelock_557.v0.1"` until Phase 561 ratification.

## 6. Non-negotiable constraints

- `CDL-053` remains reserved and unopened throughout Window 555-564.
- Multi-hop remains deferred; Window 555-564 does not reopen the CDL-060 single-hop lane.
- No DHT or dynamic peer discovery in v1; `static_peer_config_no_dht_v1` remains active.
- Phase 556 closes the signal-floor obligation at ADM/ADR level; no new floor-governance CDL opens here.
- Phase 561 ratifies only after transport adapter implementation evidence exists.

## 7. Sequence integrity rule

Window 555-564 must execute in this order:
1. Phase 555 sequence lock.
2. Phase 556 ADR-0023 invariant update.
3. Phase 557 CDL-061 open + prelock.
4. Phase 558 transport adapter implementation against the prelock token.
5. Phase 559-560 hardening and canary extension.
6. Phase 561 CDL-061 ratification after implementation evidence.
7. Phase 562 peer registry on top of the ratified transport layer.
8. Phase 563-564 coherence, closure gate, and handoff.

The ordering decision is locked as `cdl_061_ratification_after_implementation`.
