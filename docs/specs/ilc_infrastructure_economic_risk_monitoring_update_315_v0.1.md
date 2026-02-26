# ILC Infrastructure Economic Risk Monitoring Update 315 v0.1

Status: Phase-315 monitoring update artifact  
Date: 2026-02-26  
Owner lane: G8 Constitution Cluster A

## 1. Purpose and constitutional boundary

Update the economic-risk monitoring baseline to include the infrastructure runtime surfaces delivered in Phases 310, 312, and 314 before Phase 316 composed preflight.

Boundary in this phase:
- no mutation of `docs/specs/ilc_constitutional_decision_log_v0.1.md`,
- no runtime implementation changes under `ilc_core/`,
- no ratification action for any CDL row.

## 2. Surface expansion from Phase 305 baseline

Phase-305 baseline (`docs/specs/ilc_d2e_economic_risk_monitoring_baseline_305_v0.1.md`) remains authoritative for D2e query/verify/bundle surfaces.

Phase-315 adds infrastructure monitoring coverage for:
- D2 schema runtime (`d2_schema_baseline_310.v0.1`),
- genesis bundle runtime (`genesis_state_bundle_312.v0.1`),
- epoch snapshot runtime (`epoch_snapshot_runtime_314.v0.1`).

This update is additive: existing D2e KPIs and thresholds remain in force unless superseded below.

## 3. KPI catalog update for schema/genesis/epoch surfaces

All ratios are in `[0.0, 1.0]` unless stated otherwise.

### 3.1 Schema runtime KPIs

- `kpi_schema_invalid_catalog_rate`
  - formula: `schema_invalid_catalog_events / total_schema_requests`
- `kpi_schema_dependency_mismatch_rate`
  - formula: `schema_dependency_mismatch_events / total_schema_requests`
- `kpi_schema_canonical_drift_rate`
  - formula: `schema_canonical_drift_events / total_schema_requests`

### 3.2 Genesis runtime KPIs

- `kpi_genesis_ceremony_sequence_failure_rate`
  - formula: `genesis_ceremony_sequence_failure_events / total_genesis_requests`
- `kpi_genesis_dependency_mismatch_rate`
  - formula: `genesis_dependency_mismatch_events / total_genesis_requests`
- `kpi_genesis_digest_mismatch_rate`
  - formula: `genesis_digest_mismatch_events / total_genesis_requests`

### 3.3 Epoch runtime KPIs

- `kpi_epoch_bootstrap_range_failure_rate`
  - formula: `epoch_bootstrap_range_failure_events / total_epoch_requests`
- `kpi_epoch_retention_window_failure_rate`
  - formula: `epoch_retention_window_failure_events / total_epoch_requests`
- `kpi_epoch_dependency_mismatch_rate`
  - formula: `epoch_dependency_mismatch_events / total_epoch_requests`

## 4. Severity thresholds and Phase-316 release-gate mapping

Severity levels:
- `S0`: informational
- `S1`: warning
- `S2`: elevated risk
- `S3`: release-blocking

Infrastructure thresholds:
- `kpi_schema_invalid_catalog_rate > 0.05` -> `S2`
- `kpi_schema_dependency_mismatch_rate > 0.00` -> `S2`
- `kpi_schema_canonical_drift_rate > 0.00` -> `S2`
- `kpi_genesis_ceremony_sequence_failure_rate > 0.00` -> `S2`
- `kpi_genesis_dependency_mismatch_rate > 0.00` -> `S2`
- `kpi_genesis_digest_mismatch_rate > 0.00` -> `S2`
- `kpi_epoch_bootstrap_range_failure_rate > 0.00` -> `S2`
- `kpi_epoch_retention_window_failure_rate > 0.00` -> `S2`
- `kpi_epoch_dependency_mismatch_rate > 0.00` -> `S2`
- any decision-log mutation or out-of-scope runtime mutation -> `S3`

Release-blocking gate for Phase 316:
- no open `S3` indicators,
- all open `S2` indicators require mitigation note or explicit GO override.

## 5. Measurement window and reporting artifacts

Measurement-window rule:
- for operational monitoring, denominators are per-epoch request totals per surface,
- for Phase-316 composed preflight snapshot, denominators are scenario executions per lane in that preflight run,
- Phase-316 snapshot metadata must include `preflight_scope: true` and lane denominator counts.

Reporting artifacts:
- `out/monitoring/d2e_risk_snapshot_phase_306.json` remains prior-window baseline,
- `out/monitoring/infrastructure_risk_snapshot_phase_316.json` is required in Phase 316,
- Phase 316 walkthrough must include infrastructure KPI summary and threshold status.

## 6. Owner and escalation path

Ownership mapping:
- `S0`: phase executor records KPI values in walkthrough,
- `S1`: phase executor and reviewer assess trend,
- `S2`: architecture/governance review before next sensitive phase,
- `S3`: immediate execution freeze until remediation and explicit human GO.

Escalation package must include:
- indicator name,
- observed value and denominator,
- threshold breached,
- mitigation plan and target closure phase.

## 7. Complexity gate carry-forward

Carry forward the mandatory complexity gate from Phase 305:
- necessity test,
- simpler-alternative test,
- complexity budget fields (`n_new_params`, `n_new_conditionals`, `n_new_cross_dependencies`),
- escalation required if:
  - `n_new_params > 2`, or
  - `n_new_conditionals > 2`, or
  - `n_new_cross_dependencies > 1`.

## 8. Phase-316 entry criteria lock

Phase 316 may begin only when all of the following are true:
- `tests/test_d2_schema_baseline_runtime_310.py` is green,
- `tests/test_genesis_state_bundle_runtime_312.py` is green,
- `tests/test_epoch_snapshot_runtime_314.py` is green,
- `tests/test_infrastructure_economic_risk_monitoring_update_315.py` is green,
- no open `S3` indicators from this update,
- any open `S2` indicator has mitigation or explicit GO override documented.

## 9. Non-goals and canonical anchors

This update does not:
- mutate CDL rows,
- replace constitutional ratification lanes,
- require third-party monitoring providers,
- add runtime telemetry collectors in this phase.

Canonical anchors:
- `docs/specs/ilc_d2e_economic_risk_monitoring_baseline_305_v0.1.md`
- `docs/specs/ilc_d2_schema_baseline_runtime_handoff_310_v0.1.md`
- `docs/specs/ilc_genesis_state_bundle_runtime_handoff_312_v0.1.md`
- `docs/specs/ilc_epoch_snapshot_runtime_handoff_314_v0.1.md`
- `docs/specs/ilc_phase_308_317_sequence_lock_v0.1.md`
