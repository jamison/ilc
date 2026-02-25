# ILC Window 298-307 Handoff 307 v0.1

Status: Phase-307 closure handoff artifact  
Date: 2026-02-25  
Owner lane: G8 Constitution Cluster A

## 1. Window summary (298-307 completion state)

Window 298-307 completed the D2e query/verify/bundle contract/runtime tranche, monitoring baseline, and composed preflight closure checks.

Closed phases in this window:
- Phase 298: sequence lock,
- Phase 299/301/303: contract lanes,
- Phase 300/302/304: runtime lanes,
- Phase 305: monitoring baseline,
- Phase 306: composed preflight,
- Phase 307: closure gate and 308+ handoff.

## 2. Deliverable matrix for phases 299-306

| Phase | Deliverable class | Primary artifacts |
| --- | --- | --- |
| 299 | D2e-05 contract | `docs/specs/ilc_d2e_05_query_subsystem_contract_299_v0.1.md`, `tests/test_d2e_05_query_subsystem_contract_299.py` |
| 300 | D2e-05 runtime | `docs/specs/ilc_d2e_05_query_subsystem_handoff_300_v0.1.md`, `tests/test_d2e_05_query_subsystem_300.py` |
| 301 | D2e-06 contract | `docs/specs/ilc_d2e_06_verify_subsystem_contract_301_v0.1.md`, `tests/test_d2e_06_verify_subsystem_contract_301.py` |
| 302 | D2e-06 runtime | `docs/specs/ilc_d2e_06_verify_subsystem_handoff_302_v0.1.md`, `tests/test_d2e_06_verify_subsystem_302.py` |
| 303 | D2e-07 contract | `docs/specs/ilc_d2e_07_bundle_subsystem_contract_303_v0.1.md`, `tests/test_d2e_07_bundle_subsystem_contract_303.py` |
| 304 | D2e-07 runtime | `docs/specs/ilc_d2e_07_bundle_subsystem_handoff_304_v0.1.md`, `tests/test_d2e_07_bundle_subsystem_304.py` |
| 305 | Monitoring baseline | `docs/specs/ilc_d2e_economic_risk_monitoring_baseline_305_v0.1.md`, `tests/test_d2e_economic_risk_monitoring_baseline_305.py` |
| 306 | Composed preflight | `tools/check_d2e_composed_preflight_phase_306.sh`, `tools/run_d2e_composed_preflight_phase_306.py`, `tests/test_d2e_composed_preflight_306.py`, `out/monitoring/d2e_risk_snapshot_phase_306.json` |

## 3. Closure-gate category evidence

Phase-307 closure gate executes and records the six sequence-lock categories in order:

1. `prompt_contract_validation`
   - `python3 tools/validate_phase_prompt.py docs/antigravity_tasks/antigravity_prompt__phase_307_g8_constitution_cluster_a_window_298_307_closure_verification_gate_and_308_plus_handoff.md`
2. `lane_contract_tests`
   - `python3 -m pytest tests/test_d2e_05_query_subsystem_contract_299.py tests/test_d2e_06_verify_subsystem_contract_301.py tests/test_d2e_07_bundle_subsystem_contract_303.py -q`
3. `cross_phase_regression`
   - `python3 -m pytest tests/test_phase_commit_manifest_296.py tests/test_mutation_canary_phase_297.py tests/test_d2e_05_query_subsystem_300.py tests/test_d2e_06_verify_subsystem_302.py tests/test_d2e_07_bundle_subsystem_304.py tests/test_d2e_economic_risk_monitoring_baseline_305.py tests/test_d2e_composed_preflight_306.py -q`
4. `mutation_canary`
   - `python3 tools/run_mutation_canary_phase_297.py`
5. `closure_gate_cli_contract`
   - `python3 -m pytest tests/test_window_298_307_closure_gate_307.py -q`
6. `walkthrough_hygiene`
   - `python3 -m pytest tests/test_no_ellipses_in_walkthroughs.py -q`

## 4. Phase-306 KPI snapshot carry-forward summary

`phase_306_snapshot`: `out/monitoring/d2e_risk_snapshot_phase_306.json`

Locked carry-forward snapshot facts:
- `phase == "306"`,
- `preflight_scope: true`,
- lane denominator counts present (`query`, `verify`, `bundle`),
- release verdict carried forward from snapshot severity summary.

Threshold sensitivity note:
- `kpi_bundle_backend_unavailable_rate` remains close to the `S2` boundary and should stay explicitly tracked in 308+ closure/readiness reporting.

## 5. KPI provenance policy for closure interpretation

Every KPI referenced in closure interpretation must carry provenance:
- `measured`: observed directly in runner outputs,
- `derived`: computed from measured values via declared formula,
- `not_applicable_in_preflight`: intentionally out of scope for this synthetic preflight.

Rules:
- no verdict-driving KPI (`S2`/`S3`) may be `not_applicable_in_preflight`,
- placeholder/default values are forbidden for verdict-driving KPI fields,
- release verdict interpretation must cite KPI provenance class.

## 6. Carry-forward risks and controls

Carry-forward risks:
- synthetic preflight behavior does not replace operational telemetry,
- provider-blocked recovery ratio must be interpreted as actual recovery, not error-token handling,
- mutation-canary continuity must remain active across 308+ lanes.

Controls:
- retain phase-297 mutation canary in closure/readiness gates,
- retain explicit threshold-sensitivity notes in window handoffs,
- retain subprocess envelope-regression checks for query/verify/bundle/identity schema boundaries.

## 7. Hard prerequisites for phase 308+ opening

Required before phase 308 execution starts:
- Phase-307 closure gate script passes full run,
- no decision-log mutation introduced in phase-307 commit,
- no new `ilc_core/` runtime feature implementation in phase-307 commit,
- D2e contract/runtime regression suites remain green,
- mutation-canary runner remains green.

## 8. Non-goals and boundary statement

This closure lane does not:
- ratify or mutate constitutional decision-log rows,
- introduce new `ilc_core/` runtime feature implementation,
- alter locked schema versions (`299.v0.1`, `301.v0.1`, `303.v0.1`, `254.v0.1`).

Boundary statement:
- no decision-log mutation in Phase 307,
- no new `ilc_core/` runtime feature implementation in Phase 307.

## 9. Canonical anchors and next-sequence pointer

Canonical anchors:
- `docs/specs/ilc_phase_298_307_sequence_lock_v0.1.md`
- `docs/specs/ilc_d2e_05_query_subsystem_contract_299_v0.1.md`
- `docs/specs/ilc_d2e_06_verify_subsystem_contract_301_v0.1.md`
- `docs/specs/ilc_d2e_07_bundle_subsystem_contract_303_v0.1.md`
- `docs/specs/ilc_d2e_economic_risk_monitoring_baseline_305_v0.1.md`
- `docs/specs/ilc_d2e_composed_integration_preflight_handoff_306_v0.1.md`

Next-sequence pointer:
- Phase 308 opens the next window and must treat this handoff as the closure baseline.
