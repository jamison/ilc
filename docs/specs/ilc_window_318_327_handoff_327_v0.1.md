# ILC Window 318-327 Handoff 327 v0.1

Status: Phase-327 closure handoff artifact  
Date: 2026-02-28  
Owner lane: G8 Constitution Cluster A

## 1. Window summary (318-327 completion state)

Window 318-327 completed sequence lock, three constitutional ratification lanes, wire-transport contract/runtime lanes, vulnerability-governance entry-opening lanes, coherence/capsule stabilization, and closure verification.

Closed phases in this window:
- Phase 318: sequence lock,
- Phase 319/320/321: constitutional ratification lanes,
- Phase 322: wire transport contract/evidence prelock,
- Phase 323: wire transport runtime/provider lane,
- Phase 324/325: CDL-V entry-opening and evidence-prelock lanes,
- Phase 326: coherence/capsule and snapshot-isolation stabilization,
- Phase 327: closure gate and 328+ handoff.

## 2. Deliverable matrix for phases 319-326

| Phase | Deliverable class | Primary artifacts |
| --- | --- | --- |
| 319 | CDL-020 ratification | `docs/specs/ilc_cdl_020_d2_schema_baseline_ratification_evidence_319_v0.1.md`, `tests/test_cdl_020_ratification_319.py` |
| 320 | CDL-022 ratification | `docs/specs/ilc_cdl_022_genesis_state_bundle_ratification_evidence_320_v0.1.md`, `tests/test_cdl_022_ratification_320.py` |
| 321 | CDL-023 ratification | `docs/specs/ilc_cdl_023_epoch_snapshot_ratification_evidence_321_v0.1.md`, `tests/test_cdl_023_ratification_321.py` |
| 322 | CDL-024 contract/evidence | `docs/specs/ilc_wire_transport_contract_and_cdl_024_evidence_prelock_322_v0.1.md`, `tests/test_wire_transport_contract_and_cdl_024_evidence_prelock_322.py` |
| 323 | CDL-024 runtime | `docs/specs/ilc_wire_transport_runtime_handoff_323_v0.1.md`, `tests/test_wire_transport_runtime_323.py` |
| 324 | CDL-V batch A opening | `docs/specs/ilc_cdl_v1_temporal_decay_evidence_prelock_324_v0.1.md`, `docs/specs/ilc_cdl_v2_sybil_resistance_evidence_prelock_324_v0.1.md`, `docs/specs/ilc_cdl_v3_quorum_diversity_evidence_prelock_324_v0.1.md`, `tests/test_cdl_v_batch_a_open_and_evidence_prelock_324.py` |
| 325 | CDL-V batch B opening | `docs/specs/ilc_cdl_v4_reopening_protocol_evidence_prelock_325_v0.1.md`, `docs/specs/ilc_cdl_v5_schema_epoch_translation_evidence_prelock_325_v0.1.md`, `docs/specs/ilc_cdl_v6_genesis_intervention_protocol_evidence_prelock_325_v0.1.md`, `docs/specs/ilc_cdl_v7_agent_decomposition_criteria_evidence_prelock_325_v0.1.md`, `tests/test_cdl_v_batch_b_open_and_evidence_prelock_325.py` |
| 326 | Coherence/capsule stabilization | `docs/specs/ilc_integration_coherence_report_326_v0.1.md`, `docs/specs/ilc_cdl_v_ratification_sequencing_326_v0.1.md`, `docs/specs/ilc_antigravity_context_capsule_v0.7.md`, `tests/test_integration_coherence_326.py` |

## 3. Closure-gate category evidence

Phase-327 closure gate executes and records six categories in order:

1. `prompt_contract_validation`
   - `python3 tools/validate_phase_prompt.py docs/antigravity_tasks/antigravity_prompt__phase_327_g8_constitution_cluster_a_window_318_327_closure_verification_gate_and_328_plus_handoff.md`
2. `lane_contract_tests`
   - `python3 -m pytest tests/test_phase_318_sequence_lock.py tests/test_cdl_020_ratification_319.py tests/test_cdl_022_ratification_320.py tests/test_cdl_023_ratification_321.py tests/test_wire_transport_contract_and_cdl_024_evidence_prelock_322.py tests/test_cdl_v_batch_a_open_and_evidence_prelock_324.py tests/test_cdl_v_batch_b_open_and_evidence_prelock_325.py tests/test_integration_coherence_326.py -q`
3. `cross_phase_regression`
   - `python3 -m pytest tests/test_phase_commit_manifest_296.py tests/test_mutation_canary_phase_297.py tests/test_d2_schema_baseline_runtime_310.py tests/test_genesis_state_bundle_runtime_312.py tests/test_epoch_snapshot_runtime_314.py tests/test_infrastructure_economic_risk_monitoring_update_315.py tests/test_infrastructure_composed_preflight_316.py tests/test_wire_transport_runtime_323.py tests/test_window_308_317_closure_gate_317.py -q`
4. `mutation_canary`
   - `python3 tools/run_mutation_canary_phase_297.py`
5. `closure_gate_cli_contract`
   - `python3 -m pytest tests/test_window_318_327_closure_gate_327.py -q`
6. `walkthrough_hygiene`
   - `python3 -m pytest tests/test_no_ellipses_in_walkthroughs.py -q`

## 4. Phase-316 KPI snapshot carry-forward summary

`phase_316_snapshot`: `out/monitoring/infrastructure_risk_snapshot_phase_316.json`

Locked carry-forward snapshot facts:
- `phase == "316"`,
- `preflight_scope: true`,
- lane denominator counts: `schema=26`, `genesis=25`, `epoch=25`,
- release verdict: `pass`.

## 5. Coherence and governance carry-forward summary

Authority rule:
- future CDL-V ratification prompts must treat Section 3 of the corresponding evidence-prelock artifact as authoritative when it is more specific than the compressed `required_artifacts` column in the CDL row.

Sequencing rules:
- `CDL-V2 -> CDL-V3 -> CDL-V4`,
- `CDL-V5 -> CDL-V7`,
- `CDL-V4 <-> CDL-V6`,
- `CDL-V1 has no V-series ordering constraint`.

Constitutional state carry-forward:
- `CDL-020`, `CDL-022`, and `CDL-023` are ratified,
- `CDL-024` remains open,
- `CDL-V1` through `CDL-V7` remain open.

## 6. Carry-forward risks and controls

Residual risks:
- direct execution of `tests/test_infrastructure_composed_preflight_316.py` still writes the canonical Phase-316 snapshot and requires immediate `git restore out/monitoring/infrastructure_risk_snapshot_phase_316.json` until separately remediated,
- if `tests/test_integration_coherence_326.py` is later modified, sanitize inherited `ILC_PHASE_317_ALLOW_SNAPSHOT_WRITE` and `ILC_PHASE_316_SNAPSHOT_PATH` in the default no-write assertion path,
- mutation-canary continuity remains required for closure/readiness lanes.

Controls:
- retain `git restore out/monitoring/infrastructure_risk_snapshot_phase_316.json` after direct Phase-316 regression execution outside the remediated Phase-317 gate path,
- retain snapshot override isolation using `ILC_PHASE_316_SNAPSHOT_PATH` for nested gate/preflight execution,
- retain `ILC_PHASE_317_ALLOW_SNAPSHOT_WRITE` as explicit opt-in behavior only,
- retain phase-297 mutation canary in closure/readiness gates.

## 7. Hard prerequisites for phase 328+ opening

Required before Phase 328 execution starts:
- Phase-327 closure gate script passes full run,
- no decision-log mutation introduced in Phase 327,
- no new `ilc_core/` runtime feature implementation in Phase 327,
- all 319-326 contract/runtime/coherence regression suites remain green,
- mutation-canary runner remains green,
- the authority-rule and V-series sequencing carry-forward constraints remain visible to subsequent prompt authors.

## 8. Non-goals and boundary statement

This closure lane does not:
- ratify or mutate constitutional decision-log rows,
- introduce new `ilc_core/` runtime feature implementation,
- modify the direct Phase-316 regression suite or Phase-316 preflight tools,
- reopen Phase-326 coherence artifacts for additional remediation.

Boundary statement:
- no decision-log mutation in Phase 327,
- no new `ilc_core/` runtime feature implementation in Phase 327.

## 9. Canonical anchors and next-sequence pointer

Canonical anchors:
- `docs/specs/ilc_phase_318_327_sequence_lock_v0.1.md`
- `docs/specs/ilc_cdl_020_d2_schema_baseline_ratification_evidence_319_v0.1.md`
- `docs/specs/ilc_cdl_022_genesis_state_bundle_ratification_evidence_320_v0.1.md`
- `docs/specs/ilc_cdl_023_epoch_snapshot_ratification_evidence_321_v0.1.md`
- `docs/specs/ilc_wire_transport_contract_and_cdl_024_evidence_prelock_322_v0.1.md`
- `docs/specs/ilc_wire_transport_runtime_handoff_323_v0.1.md`
- `docs/specs/ilc_cdl_v1_temporal_decay_evidence_prelock_324_v0.1.md`
- `docs/specs/ilc_cdl_v2_sybil_resistance_evidence_prelock_324_v0.1.md`
- `docs/specs/ilc_cdl_v3_quorum_diversity_evidence_prelock_324_v0.1.md`
- `docs/specs/ilc_cdl_v4_reopening_protocol_evidence_prelock_325_v0.1.md`
- `docs/specs/ilc_cdl_v5_schema_epoch_translation_evidence_prelock_325_v0.1.md`
- `docs/specs/ilc_cdl_v6_genesis_intervention_protocol_evidence_prelock_325_v0.1.md`
- `docs/specs/ilc_cdl_v7_agent_decomposition_criteria_evidence_prelock_325_v0.1.md`
- `docs/specs/ilc_integration_coherence_report_326_v0.1.md`
- `docs/specs/ilc_cdl_v_ratification_sequencing_326_v0.1.md`
- `docs/specs/ilc_antigravity_context_capsule_v0.7.md`

Next-sequence pointer:
- Phase 328 opens the next window and must treat this handoff as the closure baseline for 328+ sequencing, including the authority-rule and V-series dependency constraints.
