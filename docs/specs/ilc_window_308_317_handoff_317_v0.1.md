# ILC Window 308-317 Handoff 317 v0.1

Status: Phase-317 closure handoff artifact  
Date: 2026-02-27  
Owner lane: G8 Constitution Cluster A

## 1. Window summary (308-317 completion state)

Window 308-317 completed sequence lock, schema/evidence lanes, runtime lanes, monitoring update, and composed infrastructure preflight closure checks.

Closed phases in this window:
- Phase 308: sequence lock,
- Phase 309/311/313/315: contract and evidence lanes,
- Phase 310/312/314: runtime lanes,
- Phase 316: composed infrastructure preflight,
- Phase 317: closure gate and 318+ handoff.

## 2. Deliverable matrix for phases 309-316

| Phase | Deliverable class | Primary artifacts |
| --- | --- | --- |
| 309 | D2 schema contract | `docs/specs/ilc_d2_schema_baseline_contract_and_cdl_020_evidence_prelock_309_v0.1.md`, `tests/test_d2_schema_baseline_contract_and_cdl_020_evidence_prelock_309.py` |
| 310 | D2 schema runtime | `docs/specs/ilc_d2_schema_baseline_runtime_handoff_310_v0.1.md`, `tests/test_d2_schema_baseline_runtime_310.py` |
| 311 | Genesis contract | `docs/specs/ilc_genesis_state_bundle_contract_and_cdl_022_evidence_prelock_311_v0.1.md`, `tests/test_genesis_state_bundle_contract_and_cdl_022_evidence_prelock_311.py` |
| 312 | Genesis runtime | `docs/specs/ilc_genesis_state_bundle_runtime_handoff_312_v0.1.md`, `tests/test_genesis_state_bundle_runtime_312.py` |
| 313 | Epoch contract | `docs/specs/ilc_epoch_snapshot_contract_and_cdl_023_evidence_prelock_313_v0.1.md`, `tests/test_epoch_snapshot_contract_and_cdl_023_evidence_prelock_313.py` |
| 314 | Epoch runtime | `docs/specs/ilc_epoch_snapshot_runtime_handoff_314_v0.1.md`, `tests/test_epoch_snapshot_runtime_314.py` |
| 315 | Monitoring update | `docs/specs/ilc_infrastructure_economic_risk_monitoring_update_315_v0.1.md`, `tests/test_infrastructure_economic_risk_monitoring_update_315.py` |
| 316 | Composed preflight | `tools/check_infrastructure_composed_preflight_phase_316.sh`, `tools/run_infrastructure_composed_preflight_phase_316.py`, `tests/test_infrastructure_composed_preflight_316.py`, `out/monitoring/infrastructure_risk_snapshot_phase_316.json` |

## 3. Closure-gate category evidence

Phase-317 closure gate executes and records six categories in order:

1. `prompt_contract_validation`
   - `python3 tools/validate_phase_prompt.py docs/antigravity_tasks/antigravity_prompt__phase_317_g8_constitution_cluster_a_window_308_317_closure_verification_gate_and_318_plus_handoff.md`
2. `lane_contract_tests`
   - `python3 -m pytest tests/test_phase_308_sequence_lock.py tests/test_d2_schema_baseline_contract_and_cdl_020_evidence_prelock_309.py tests/test_genesis_state_bundle_contract_and_cdl_022_evidence_prelock_311.py tests/test_epoch_snapshot_contract_and_cdl_023_evidence_prelock_313.py tests/test_infrastructure_economic_risk_monitoring_update_315.py -q`
3. `cross_phase_regression`
   - `python3 -m pytest tests/test_phase_commit_manifest_296.py tests/test_mutation_canary_phase_297.py tests/test_d2_schema_baseline_runtime_310.py tests/test_genesis_state_bundle_runtime_312.py tests/test_epoch_snapshot_runtime_314.py tests/test_infrastructure_composed_preflight_316.py -q`
4. `mutation_canary`
   - `python3 tools/run_mutation_canary_phase_297.py`
5. `closure_gate_cli_contract`
   - `python3 -m pytest tests/test_window_308_317_closure_gate_317.py -q`
6. `walkthrough_hygiene`
   - `python3 -m pytest tests/test_no_ellipses_in_walkthroughs.py -q`

## 4. Phase-316 KPI snapshot carry-forward summary

`phase_316_snapshot`: `out/monitoring/infrastructure_risk_snapshot_phase_316.json`

Locked carry-forward snapshot facts:
- `phase == "316"`,
- `preflight_scope: true`,
- lane denominator counts: `schema=26`, `genesis=25`, `epoch=25`,
- release verdict: `pass`.

Threshold sensitivity note:
- `kpi_schema_invalid_catalog_rate = 0.03846154`, `S2` threshold is `> 0.05`, leaving approximately 23.1% headroom before crossing into `S2`; keep this explicitly tracked in 318+ readiness reporting.

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
- snapshot override isolation must remain enforced in future gate tests,
- mutation-canary continuity must remain active across 318+ lanes.

Controls:
- retain phase-297 mutation canary in closure/readiness gates,
- retain explicit threshold-sensitivity notes in window handoffs,
- retain snapshot-override test isolation using `ILC_PHASE_<PHASE>_SNAPSHOT_PATH` + `tmp_path` copies.

## 7. Hard prerequisites for phase 318+ opening

Required before Phase 318 execution starts:
- Phase-317 closure gate script passes full run,
- no decision-log mutation introduced in phase-317 commit,
- no new `ilc_core/` runtime feature implementation in phase-317 commit,
- all 309-316 contract/runtime regression suites remain green,
- mutation-canary runner remains green.

## 8. Non-goals and boundary statement

This closure lane does not:
- ratify or mutate constitutional decision-log rows,
- introduce new `ilc_core/` runtime feature implementation,
- alter locked version/dependency tokens (`d2_schema_baseline_310.v0.1`, `genesis_state_bundle_312.v0.1`, `epoch_snapshot_runtime_314.v0.1`).

Boundary statement:
- no decision-log mutation in Phase 317,
- no new `ilc_core/` runtime feature implementation in Phase 317.

## 9. Canonical anchors and next-sequence pointer

Canonical anchors:
- `docs/specs/ilc_phase_308_317_sequence_lock_v0.1.md`
- `docs/specs/ilc_d2_schema_baseline_contract_and_cdl_020_evidence_prelock_309_v0.1.md`
- `docs/specs/ilc_d2_schema_baseline_runtime_handoff_310_v0.1.md`
- `docs/specs/ilc_genesis_state_bundle_contract_and_cdl_022_evidence_prelock_311_v0.1.md`
- `docs/specs/ilc_genesis_state_bundle_runtime_handoff_312_v0.1.md`
- `docs/specs/ilc_epoch_snapshot_contract_and_cdl_023_evidence_prelock_313_v0.1.md`
- `docs/specs/ilc_epoch_snapshot_runtime_handoff_314_v0.1.md`
- `docs/specs/ilc_infrastructure_economic_risk_monitoring_update_315_v0.1.md`
- `docs/specs/ilc_infrastructure_composed_preflight_handoff_316_v0.1.md`

Next-sequence pointer:
- Phase 318 opens the next window and must treat this handoff as the closure baseline.
