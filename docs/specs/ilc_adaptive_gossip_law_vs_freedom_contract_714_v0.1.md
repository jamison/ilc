# ILC Adaptive Gossip Law-vs-Freedom Contract 714 v0.1

**Phase:** 714  
**Window:** 713-716  
**Date:** 2026-04-17  
**Author:** Codex

`adaptive_gossip_law_vs_freedom_contract_714`

## 1. Baseline

Phase `713` opened Window `713-716` as the adaptive-gossip and
resilience-operationalization lane. `CDL-060` and `CDL-061` are already
settled, `CDL-039` remains a governing privacy boundary, and this phase does
not ratify or reopen any constitutional lane.

The active governance target is the Python D2d gossip stack:

- `ilc_core/network/d2d/gossip_peer_registry.py`
- `ilc_core/network/d2d/centrality_delta_gossip_runtime.py`
- `ilc_core/network/d2d/gossip_transport.py`
- `ilc_core/network/d2d/http_gossip_transport_runtime.py`

This artifact classifies every live gossip parameter in that active path as
`constitutional_law`, `operator_configurable`, or `deferred`.
`every_live_gossip_parameter_classified`

## 2. Inherited settled law

`CDL-060` and `CDL-061` are inherited anchors, not reopened here.
`cdl_060_and_cdl_061_settled_not_reopened`

The settled constitutional lane inherited into this phase is:

- single-hop `centrality_delta` gossip only,
- opaque `ILC-Channel` values under the `CDL-039` privacy boundary,
- bounded fanout as a constitutional principle,
- HTTP envelope validation with required header set,
- `ILC-Hop-Count: 1` as the only permitted hop count,
- `ILC-Epoch` header presence with integer, non-negative validation.

This phase therefore distinguishes carefully between:

- inherited law-level constraints, and
- live implementation choices that are present in code but not clearly ratified
  as fixed constitutional numbers or heuristics.

`CDL-039` ratification does not occur in this window.

## 3. Live gossip parameter inventory

The live parameter inventory in the active Python D2d path is:

| Surface | Runtime location | Current live value / behavior |
|---|---|---|
| `PEER_DISCOVERY_MODE` | `gossip_peer_registry.py` | `"static_v1"` |
| `MAX_PEERS` | `gossip_peer_registry.py` | `16` |
| `MAX_FANOUT` | `centrality_delta_gossip_runtime.py` | `3` |
| `select_fanout_peers()` | `gossip_peer_registry.py` | deterministic sorted-prefix peer choice |
| `request_timeout_seconds` | `http_gossip_transport_runtime.py` | `2.0` seconds |
| `MAX_INBOUND_PAYLOAD_BYTES` | `http_gossip_transport_runtime.py` | `1_048_576` bytes |
| `MAX_INBOUND_READ_CHUNK_BYTES` | `http_gossip_transport_runtime.py` | `64 * 1024` bytes |
| `ILC-Epoch` header validation | `gossip_transport.py` | required, integer, non-negative |
| stronger epoch staleness / range rule | active Python D2d path | not implemented as a live rule |
| retry / backoff knob | active Python D2d path | not implemented as a live knob |

If a retry/backoff surface is not actually live in the current code path, it is
marked `deferred` rather than invented.
`retry_and_epoch_range_surfaces_classified_or_explicitly_deferred`

## 4. Classification matrix

| Surface | Classification | Reason |
|---|---|---|
| `PEER_DISCOVERY_MODE = "static_v1"` | `constitutional_law` | The live runtime asserts `static_v1` and binds dynamic discovery to later explicit authorization under the `CDL-039` privacy boundary. |
| `MAX_PEERS = 16` | `operator_configurable` | The active ceiling is load-bearing in code, but the exact number is not clearly constitutionalized by `CDL-060` or `CDL-061`. |
| `MAX_FANOUT = 3` | `operator_configurable` | The inherited law is bounded fanout, not clearly the literal value `3`; the exact numeric cap is a calibrated live setting unless later fixed by stronger law. |
| bounded-fanout principle | `constitutional_law` | `CDL-060` ratifies single-hop gossip under bounded fanout. |
| peer-selection behavior in `select_fanout_peers()` | `operator_configurable` | Deterministic sorted-prefix selection is the current v1 heuristic, but the exact ordering rule is not itself ratified law so long as privacy and bounded-fanout constraints remain intact. |
| `request_timeout_seconds = 2.0` | `operator_configurable` | The timeout is live and operator-visible, but no ratified row fixes the literal number. |
| `MAX_INBOUND_PAYLOAD_BYTES = 1_048_576` | `operator_configurable` | The live payload cap is implementation hardening, not presently constitutionalized law. |
| `MAX_INBOUND_READ_CHUNK_BYTES = 64 * 1024` | `operator_configurable` | Read chunk size is a local runtime tuning value rather than a constitutional invariant. |
| `ILC-Epoch` header validation / non-negative rule | `constitutional_law` | Required header presence and integer, non-negative validation are part of the inherited envelope contract. |
| stronger epoch staleness / range rule | `deferred` | No stronger live staleness window or committed-epoch range rule exists in the active Python path beyond header validation. |
| explicit retry / backoff knob | `deferred` | No first-class retry/backoff parameter is exposed in the active Python path; this must not be fabricated by doctrine. |

## 5. Constitutional-law set

The current `constitutional_law` set for the active Python D2d gossip path is:

- `PEER_DISCOVERY_MODE = "static_v1"` as the active no-dynamic-discovery
  baseline,
- bounded fanout as a governing principle,
- single-hop envelope semantics,
- opaque channel privacy and forbidden-header exclusions,
- `ILC-Epoch` header presence with integer, non-negative validation.

This means constitutional law governs the lane shape and privacy / hop / epoch
invariants, but not every current numeric constant.

## 6. Operator-configurable set

The current `operator_configurable` set is:

- `MAX_PEERS = 16`,
- `MAX_FANOUT = 3`,
- deterministic sorted-prefix peer selection in `select_fanout_peers()`,
- `request_timeout_seconds = 2.0`,
- `MAX_INBOUND_PAYLOAD_BYTES = 1_048_576`,
- `MAX_INBOUND_READ_CHUNK_BYTES = 64 * 1024`.

These surfaces are live and governance-relevant, but the exact numbers or
heuristics are not clearly fixed by the already-ratified constitutional rows.

## 7. Deferred set

The current `deferred` set is:

- stronger epoch staleness / range policy beyond current `ILC-Epoch` header
  validation,
- explicit retry/backoff tuning surfaces,
- dynamic peer discovery beyond `static_v1`,
- topology shuffling or any `CDL-039` authorization expansion,
- any production-QUIC-only selection question for this Python D2d lane.

This phase uses `deferred` only where the surface is not actually live or is
explicitly routed to later authorization rather than silent operator choice.

## 8. Non-goals and carry-forward

This phase does not:

- mutate the constitutional decision log,
- ratify any CDL,
- reopen `CDL-060` or `CDL-061`,
- ratify `CDL-039`,
- claim benchmark results,
- mutate `ilc_core/` or `ilc_consensus/`.

Carry-forward from this classification:

- Phase `715` may commission partition-repair evidence and choose missing-signal
  behavior using this contract as the governing baseline.
- Any later attempt to move operator-configurable numbers into constitutional
  law needs a separate evidence-bearing lane.
- Dynamic discovery, topology shuffling, and stronger epoch-range semantics
  remain later questions rather than silently adopted authority.
