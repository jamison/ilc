# ILC Runtime Tranche Benchmark Handoff 436 v0.1

Status: Phase-436 runtime-tranche completion artifact
Date: 2026-03-17
Owner lane: G8 Constitution Cluster A

## 1. Phase 436 runtime scope summary

Phase 436 imported only the remaining Phase-434-authorized runtime-tranche file: tools/runtime_baseline.py.

Release-track source anchor: ../ILC_release_track/docs/handoffs/main_track_handoff_window_434_runtime_tranche_v0.1.md

Release-track source handoff sha256: 4e16ccb979d555329158753499b9dbbf38180460dd5db969a987999fc08a3113

Release-track source tool sha256: dcffef7fb20e10d1ca4f649c752b9bb92875738133b0863881f7a52157ec29db

## 2. Imported runtime surface

Imported runtime surface in this tranche:
- `tools/runtime_baseline.py`

Runtime baseline harness import was byte-aligned to the frozen release-track source.

Window 434+ must cherry-pick the release-track runtime tranche before any public repo packaging commits are merged.

Runtime tranche imports landed on main with identifiable runtime commit messages and not as a bulk packaging merge.

## 3. Runtime baseline harness contract

`tools/runtime_baseline.py` now provides the numbered runtime tranche benchmark harness for:
- claim ingest latency,
- peer fanout latency,
- epoch snapshot roundtrip,
- event export latency.

The harness writes a machine-readable JSON report, prints the report JSON to stdout, and supports the locked CLI flags `--iterations`, `--fanout-peers`, `--report-path`, and `--enforce-budgets`.

## 4. Preserved runtime and constitutional invariants

Phase 436 did not mutate ilc_core/network/peer.py, ilc_core/cli/main.py, or ilc_core/node/node_dissemination_runtime_362.py.

CDL-050 remains unopened and unaffected by Phase 436.

No decision-log mutation occurred in Phase 436.

Public packaging/bootstrap work remained outside the numbered window.

## 5. Test evidence and tranche completion state

Phase-436 verification evidence must include:
- `tests/test_phase_436_runtime_tranche_benchmark_harness_and_tranche_completion.py`
- `tests/test_phase_435_runtime_tranche_peer_fanout_integration.py`
- `tests/test_phase_434_window_434_440_sequence_lock_and_runtime_tranche_intake.py`
- `tests/test_window_424_433_closure_gate_433.py`
- `tests/test_network.py tests/test_network_gossip.py tests/test_node_dissemination_runtime_362.py tests/test_code_health.py`

The numbered runtime tranche authorized by Phase 434 is complete after Phase 436.

## 6. Non-goals and Phase 437 pointer

Non-goals in Phase 436:
- no `CDL-050` opening,
- no Treasury `P_e` constitutional work,
- no public packaging/bootstrap merge,
- no mutation of the Phase-435 runtime files.

Phase 437 is the next authorized non-sensitive findings and regression-hardening phase.
