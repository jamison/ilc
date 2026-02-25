# ILC D2e Economic Risk Monitoring Baseline 305 v0.1

Status: Phase-305 baseline artifact  
Date: 2026-02-25  
Owner lane: G8 Constitution Cluster A

## 1. Purpose and constitutional boundary

Define a concrete, testable economic-risk monitoring baseline for the D2e query/verify/bundle surfaces before Phase 306 composed integration preflight.

This artifact is operational-policy guidance and does not ratify CDL values.

Boundary in this phase:
- no mutation of `docs/specs/ilc_constitutional_decision_log_v0.1.md`,
- no runtime implementation changes under `ilc_core/`,
- no new anti-abuse or economic policy constants are ratified.

## 2. Monitoring planes mapped to D2e surfaces

The six monitoring planes are mandatory and mapped to D2e surfaces:

1. Protocol invariants
   - command envelope conformance (`query`, `verify`, `bundle`),
   - fail-closed error behavior,
   - deterministic output ordering.

2. Economic invariants
   - invalid-input overhead rate,
   - not-found and backend-unavailable pressure,
   - check-failure drift under repeated workload.

3. Governance hygiene
   - phase-scoped mutation boundaries,
   - evidence-chain completeness,
   - non-target file protection.

4. Operational resilience
   - local-state path availability,
   - provider boundary behavior under blocked/absent paths,
   - runbook handoff readiness.

5. Adoption utility
   - successful command completion ratio,
   - median command latency,
   - validation closure quality for local graph references.

6. Narrative integrity
   - utility-first framing in artifacts,
   - no macro-hedge framing drift,
   - no vendor-lock language in baseline operation.

## 3. KPI catalog and formula definitions

Each KPI is measured per command lane and reported as a ratio in `[0.0, 1.0]` unless marked otherwise.

### 3.1 Query KPIs

- `kpi_query_invalid_input_rate`
  - formula: `query_invalid_input_events / total_query_requests`
  - unit: ratio
- `kpi_query_not_found_rate`
  - formula: `query_not_found_events / total_query_requests`
  - unit: ratio
- `kpi_query_backend_unavailable_rate`
  - formula: `query_backend_unavailable_events / total_query_requests`
  - unit: ratio
- `kpi_query_p95_latency_ms`
  - formula: `p95(query_response_latency_ms)`
  - unit: milliseconds

### 3.2 Verify KPIs

- `kpi_verify_invalid_input_rate`
  - formula: `verify_invalid_input_events / total_verify_requests`
  - unit: ratio
- `kpi_verify_not_found_rate`
  - formula: `verify_not_found_events / total_verify_requests`
  - unit: ratio
- `kpi_verify_backend_unavailable_rate`
  - formula: `verify_backend_unavailable_events / total_verify_requests`
  - unit: ratio
- `kpi_verify_check_failure_ratio`
  - formula: `failed_verify_checks / total_verify_checks`
  - unit: ratio

### 3.3 Bundle KPIs

- `kpi_bundle_invalid_input_rate`
  - formula: `bundle_invalid_input_events / total_bundle_requests`
  - unit: ratio
- `kpi_bundle_not_found_rate`
  - formula: `bundle_not_found_events / total_bundle_requests`
  - unit: ratio
- `kpi_bundle_manifest_invalid_rate`
  - formula: `bundle_manifest_invalid_events / total_bundle_requests`
  - unit: ratio
- `kpi_bundle_provider_blocked_rate`
  - formula: `bundle_provider_blocked_events / total_bundle_requests`
  - unit: ratio
- `kpi_bundle_backend_unavailable_rate`
  - formula: `bundle_backend_unavailable_events / total_bundle_requests`
  - unit: ratio
- `kpi_bundle_validate_local_ref_missing_rate`
  - formula: `validate_local_ref_missing_events / total_validate_local_requests`
  - unit: ratio

### 3.4 Cross-lane utility KPIs

- `kpi_d2e_success_ratio`
  - formula: `successful_requests / total_d2e_requests`
  - unit: ratio
- `kpi_d2e_median_latency_ms`
  - formula: `median(command_latency_ms)`
  - unit: milliseconds

## 4. Severity thresholds and release gates

Severity levels:
- `S0`: informational
- `S1`: warning
- `S2`: elevated risk
- `S3`: release-blocking

Default thresholds:
- `kpi_query_backend_unavailable_rate > 0.01` -> `S2`
- `kpi_verify_backend_unavailable_rate > 0.01` -> `S2`
- `kpi_bundle_backend_unavailable_rate > 0.01` -> `S2`
- `kpi_verify_check_failure_ratio > 0.05` -> `S2`
- `kpi_bundle_manifest_invalid_rate > 0.05` -> `S2`
- any phase-scoped mutation boundary violation -> `S3`
- any fail-closed contract violation -> `S3`

Release-blocking gate for Phase 306:
- no `S3` indicators may be open,
- all `S2` indicators require documented mitigation or explicit GO override.

## 5. Cadence and reporting artifacts

Required cadence:
- per-epoch snapshot,
- per-phase summary,
- per-window consolidated rollup.

Artifact paths:
- `out/monitoring/d2e_risk_snapshot_phase_<phase>.json`
- `docs/specs/ilc_d2e_risk_monitoring_rollup_298_307_v0.1.md`
- `docs/phases/phase_30x_..._walkthrough.md` KPI summary section

## 6. Owner and escalation path

Ownership mapping:
- `S0`: phase executor records KPI in phase walkthrough.
- `S1`: phase executor + reviewer (Sonnet/Codex lane reviewer) assess trend.
- `S2`: escalate to architecture/governance review before next sensitive GO.
- `S3`: immediate execution freeze for affected lane until remediation and explicit human GO.

Escalation handoff requires:
- indicator name,
- observed value,
- threshold breached,
- mitigation plan,
- target phase for closure.

## 7. Complexity gate (mandatory)

Every new D2e economic/governance proposal must include:

1. Necessity test
   - what concrete failure mode is being addressed,
   - baseline metric proving the issue exists.

2. Simpler-alternative test
   - at least one simpler alternative,
   - explicit rejection reason.

3. Complexity budget fields
   - `n_new_params`,
   - `n_new_conditionals`,
   - `n_new_cross_dependencies`.

4. Complexity escalation rule
   - explicit review required if:
     - `n_new_params > 2`, or
     - `n_new_conditionals > 2`, or
     - `n_new_cross_dependencies > 1`.

## 8. Phase-306 entry criteria lock

Phase 306 may begin only when all of the following are true:
- `tests/test_d2e_05_query_subsystem_300.py` is green,
- `tests/test_d2e_06_verify_subsystem_302.py` is green,
- `tests/test_d2e_07_bundle_subsystem_304.py` is green,
- no open `S3` indicators from this baseline,
- any open `S2` indicator has mitigation or explicit GO override documented.

## 9. Non-goals

This baseline does not:
- mutate CDL rows,
- replace constitutional ratification lanes,
- require any third-party monitoring provider,
- implement runtime telemetry collectors in this phase.
