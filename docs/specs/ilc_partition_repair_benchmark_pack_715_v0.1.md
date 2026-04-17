# ILC Partition Repair Benchmark Pack 715 v0.1

**Phase:** 715  
**Window:** 713-716  
**Date:** 2026-04-17  
**Author:** Codex

`partition_repair_commissioning_only_no_results_claimed`

## 1. Baseline

Phase `714` classified the live Python D2d gossip surfaces and preserved
`PEER_DISCOVERY_MODE = "static_v1"` as the current constitutional baseline.

The repair question in this phase is therefore bounded by the present live lane:

- static peer registry only,
- single-hop bounded-fanout gossip,
- no dynamic discovery authorization,
- no topology-shuffling authorization,
- no benchmark-results claim in-window.

## 2. Commissioning posture

This artifact commissions partition-repair evidence. It does not publish benchmark results.

The purpose of the pack is to define:

- scenario family,
- pass criteria,
- evidence format,
- repair definition,
- explicit deferred boundaries.

The current static-peer baseline is preserved throughout this pack.
`static_v1_peer_registry_preserved`

## 3. Scenario matrix

| Scenario ID | Scenario | Static baseline condition | Expected repair action | Result posture |
|---|---|---|---|---|
| `PR-715-01` | transient single-peer timeout | peer remains in the same static registry | bounded reconnect and re-sync to the same peer set | commissioning only |
| `PR-715-02` | multi-peer partition then heal | registry remains static; no discovery or shuffling | bounded reconnect to the same static peers, deterministic re-sync, auditable reconciliation | commissioning only |
| `PR-715-03` | prolonged silence from one static subset | no topology expansion permitted | grace period, alert, then degraded behavior while preserving the same peer set | commissioning only |

These scenarios intentionally exclude:

- dynamic discovery-based recovery,
- topology shuffling as a repair primitive,
- new peer admission,
- benchmark-result claims in this window.

## 4. Pass criteria and evidence format

For later execution, the evidence pack must record at minimum:

- scenario identifier,
- affected peer subset,
- start epoch and end epoch,
- detection signal,
- repair action taken,
- repair-complete epoch if reached,
- whether the node stayed inside the static peer baseline,
- whether topology shuffling or discovery was invoked,
- whether the reconciliation trail is deterministic and auditable.

The minimum pass criteria for a later run are:

1. repair remains within the current static peer registry,
2. no discovery or topology shuffling is required,
3. reconciliation behavior is deterministic and auditable,
4. the gossip lane resumes bounded operation or degraded bounded operation
   without global halt,
5. any unresolved failure is reported explicitly rather than silently treated as
   successful repair.

`repair_evidence_format_defined`

## 5. Repair definition

Repair under the current static-peer baseline means:

- bounded reconnect and re-sync over the same static peer set,
- deterministic re-entry into the existing peer registry,
- no new peer discovery,
- no topology shuffling,
- no quiet expansion of the topology-authorization boundary.

Repair does not mean:

- discovering new peers,
- reseeding from hidden topology state,
- authorizing shuffle cadence,
- claiming measured resilience results before the benchmark is executed.

## 6. Explicit deferred boundaries

This benchmark pack defers:

- dynamic peer discovery authorization,
- topology shuffling authorization,
- benchmark execution results,
- any `CDL-039` ratification move,
- any runtime mutation in `ilc_core/` or `ilc_consensus/`.

`topology_shuffling_not_authorized_here`

Later evidence execution may evaluate whether those deferred capabilities are
needed, but they are not authorized by this artifact.
