# ILC Phase 713-716 Sequence Lock v0.1

**Phase:** 713  
**Window:** 713-716  
**Date:** 2026-04-17  
**Author:** Codex

`window_713_716_sequence_lock_active`

## 1. Baseline

Window `707-712` is closed. Capsule v4.6 is the live frontier at sequence-lock
time. `CDL-066` and `CDL-067` are already ratified, `CDL-017` remains open and
unratified, and topology-shuffling authorization remains later-scope only.

Track B state is moving independently and must be verified from
`docs/phases/STATUS.md` tail at execution time rather than copied from memory.
`track_b_status_must_be_verified_from_status_tail`

## 2. Inherited gates and constraints

This window inherits the settled gossip law from `CDL-060` and `CDL-061` and
does not reopen either lane. `cdl_060_and_cdl_061_settled_not_reopened_in_window_713_716`

The inherited hard constraints are:

- no CDL ratification in this window,
- no reopening of `CDL-060` or `CDL-061`,
- no `CDL-039` ratification in this window,
- no topology-shuffling authorization in this window,
- no mutation of `ilc_core/` or `ilc_consensus/` in this docs-only packet,
- no benchmark-results claim as a substitute for benchmark commissioning.

This means the constitutional decision log must remain untouched in all four
phases of `713-716`.

## 3. Window meaning

Window `713-716` is the adaptive-gossip and resilience-operationalization lane.
Its core job is to classify inherited live gossip behavior without overclaiming
new constitutional closure.

The central governance task is:

- complete law-vs-freedom classification of every live gossip parameter in the
  active Python D2d runtime,
- explicit partition-repair benchmark commissioning,
- explicit missing-signal doctrine selection.

`law_vs_freedom_classification_required_for_all_live_gossip_parameters`

This window explicitly has no pre-window conversation gate, no CDL ratification,
and no final production-topology authorization. `no_cdl_ratification_in_window_713_716`

## 4. Phase table and sequencing

| Order | Phase | Topic | Character |
|---|---:|---|---|
| 1 | 713 | sequence lock | gate / planning |
| 2 | 714 | adaptive-gossip contract and law-vs-freedom classification | governance / spec |
| 3 | 715 | partition-repair benchmark pack and missing-signal doctrine | resilience / spec |
| 4 | 716 | closure | gate / handoff |

Phase `714` must classify every live gossip parameter in the active path,
including `PEER_DISCOVERY_MODE`, `MAX_PEERS`, `MAX_FANOUT`, peer-selection
behavior, `request_timeout_seconds`, and `ILC-Epoch` validation / range
behavior.

Phase `715` commissions evidence and defines behavior. It does not need
benchmark results to close honestly in-window.
`partition_repair_and_missing_signal_commissioning_not_results`

Phase `716` may summarize only what Phases `714-715` actually establish.

## 5. Live parameter inventory obligation

Phase `714` must classify at minimum:

- `PEER_DISCOVERY_MODE`,
- `MAX_PEERS`,
- `MAX_FANOUT`,
- the deterministic peer-selection rule in `select_fanout_peers()`,
- any live retry / backoff / timeout surfaces,
- `ILC-Epoch` header validation and any stronger live range rule if one exists.

If a surface is not actually live in the active path, it must be explicitly
marked `deferred` rather than invented.

The classification categories are:

- `constitutional_law`
- `operator_configurable`
- `deferred`

## 6. Non-goals

This window does not include:

- any decision-log mutation,
- any CDL ratification,
- any reopening of `CDL-060` or `CDL-061`,
- any ratification of `CDL-039`,
- any final production VRF selection,
- any dynamic peer-discovery authorization,
- any benchmark-results claim in place of benchmark commissioning.

There is no ratification of `CDL-017`, no opening of `CDL-062`, and no final Option B production selection in this window.

## 7. Source inputs

The authoritative source set for the window is:

- `docs/PLANNING_INDEX.md`
- `docs/specs/ilc_window_713_716_guidance_v0.1.md`
- `docs/specs/ilc_window_713_716_candidate_phase_grouping_v0.1.md`
- `docs/specs/ilc_foundational_carry_forward_closure_program_701_plus_v0.1.md`
- `docs/specs/ilc_window_707_712_closure_gate_712_v0.1.md`
- `docs/specs/ilc_cdl_060_gossip_centrality_extension_ratification_evidence_541_v0.1.md`
- `docs/specs/ilc_cdl_061_gossip_http_envelope_ratification_evidence_561_v0.1.md`
- `docs/specs/ilc_cdl_v1_temporal_decay_runtime_handoff_388_v0.1.md`
- `docs/specs/ilc_cdl_039_topology_shuffling_authorization_scope_note_711_v0.1.md`
- `docs/phases/STATUS.md`
- `ilc_core/network/d2d/gossip_peer_registry.py`
- `ilc_core/network/d2d/centrality_delta_gossip_runtime.py`
- `ilc_core/network/d2d/gossip_transport.py`
- `ilc_core/network/d2d/http_gossip_transport_runtime.py`

This sequence lock remains active until Phase `716` closes the window.
