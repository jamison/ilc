# ILC Runtime Tranche Findings Memo 437 v0.1

Status: Phase-437 findings memo artifact
Date: 2026-03-17
Owner lane: G8 Constitution Cluster A

## 1. Runtime tranche settlement summary

Phase 437 records the settled findings state after the numbered runtime tranche completed in Phases 435 and 436.

Real HTTP peer fanout landed in Phase 435 and the benchmark harness landed in Phase 436.

## 2. Measured local baseline evidence

The Phase-437 measurements were taken with tools/runtime_baseline.py using 3 iterations at fanout 2, 5, 10, and the default fanout 3 baseline.

All four default runtime baseline budgets remained within budget in the Phase-437 local-process measurements.

Default fanout-3 local-process averages were claim_ingest=2.395 ms, peer_fanout=0.718 ms, epoch_snapshot=0.176 ms, event_export=22.118 ms.

## 3. Peer fanout observations

Peer fanout average latency at fanout 2 was 0.523 ms with 3824.092 deliveries_per_second.

Peer fanout average latency at fanout 5 was 1.053 ms with 4748.338 deliveries_per_second.

Peer fanout average latency at fanout 10 was 1.66 ms with 6024.096 deliveries_per_second.

The observed local-process measurements show fanout cost increasing with target count while remaining well within the current peer-fanout budget.

## 4. Code-health and regression-hardening assessment

`tests/test_code_health.py` remained green after the Phase-435 hotspot cleanup.

No additional regression hardening was required beyond the exact path-set and source-hash guards already published in Phases 435 and 436.

## 5. Open items and non-goals

No multi-process or native-P2P measurement exists yet; that remains future work outside Phase 437.

CDL-050 remains unopened and unaffected by Phase 437.

Non-goals in Phase 437:
- no runtime file mutation,
- no Treasury `P_e` constitutional action,
- no release-engineering packaging/bootstrap merge,
- no new planning tree.

## 6. Phase 438 pointer

Phase 438 is the next authorized Treasury P_e prerequisite-satisfaction review.
