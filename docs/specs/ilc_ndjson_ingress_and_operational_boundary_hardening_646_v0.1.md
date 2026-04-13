# ILC NDJSON Ingress and Operational Boundary Hardening 646 v0.1

Status: hardening artifact
Date: 2026-04-14
Classification: implementation and security hardening
Phase: 646
Owner lane: G8 security boundary and remaining-float strike force

## 1. Scope and threat basis

Phase 646 hardens two touched operational boundaries:
- NDJSON bundle ingestion scale limits
- the `ep_task_cli` HTTP boundary

## 2. Bundle-scale hard limits

Touched NDJSON bundle reading is now bounded by:
- line size
- record count
- aggregate bundle bytes

The touched fix remains in-memory and iterator-based. It does not introduce any
temporary-disk spool path.

`ndjson_bundle_total_scale_bounded_without_temp_disk_spooling`
`ndjson_bundle_record_count_and_total_bytes_limited`

## 3. Non-finite and parser boundary rules

The touched NDJSON path continues to reject non-finite JSON constants and does
not reopen `NaN` / `Infinity` acceptance while adding aggregate bounds.

`ndjson_bundle_non_finite_json_constants_rejected`

## 4. CLI timeout and exception boundary

`ep_task_cli` now uses explicit bifurcated connect/read timeouts in the default
HTTP wrapper and narrows the touched broad catch boundaries to operator-facing
error classes rather than a single blanket catch.

`ep_task_cli_http_timeout_contract_is_explicit_and_bifurcated`
`ep_task_cli_broad_exception_catch_reduced_on_touched_boundary`

## 5. Wall-clock classification

The touched 646 surfaces do not introduce wall clock as protocol-state truth.
Any remaining wall-clock usage on these paths remains metadata only.

`wall_clock_remains_metadata_only_in_touched_646_surfaces`

## 6. Verification evidence

Verification in this phase covers:
- bundle record-count bounding
- bundle aggregate-byte bounding
- continued non-finite rejection
- bifurcated CLI timeout behavior
- continued structured CLI error payload behavior
