# ILC D2e-07 Bundle Subsystem Handoff 304 v0.1

Status: Phase-304 implementation handoff artifact  
Date: 2026-02-25  
Owner lane: G8 Constitution Cluster A

## 1. Implementation scope summary

Phase 304 implements the initial D2e-07 bundle runtime tranche in `ilc_core/cli/main.py`:
- bundle subcommands: `inspect`, `verify`, `validate-local`,
- bundle-lane nested JSON envelope aligned to Phase-303 (`ok/data/meta`),
- bundle error object aligned to Phase-303 (`error.code`, `error.message`),
- deterministic `checks` ordering with minimum check schema (`check_type`, `passed`),
- local-first provider behavior with fail-closed provider-error handling.

## 2. Prototype bundle storage boundary

Phase-304 prototype storage decision:
- `inspect` and `verify` read bundle manifests from local bundle state path `ILC_BUNDLE_STATE_PATH`,
- default bundle state path is `.ilc_d2e07_bundle_state.json`,
- missing bundle state file resolves to deterministic empty local state (`bundles: []`) and emits `bundle_not_found` for unknown CIDs.

This storage boundary is implementation-level for this window and remains eligible for canonicalization in later schema/evidence lanes.

## 3. Provider-boundary outcomes

Provider boundary implemented in this tranche:
- local provider baseline is mandatory and supported with no third-party dependencies,
- provider value `blocked` fails closed with `bundle_provider_blocked`,
- no mandatory external facilitator dependency was introduced in protocol core,
- no `ilc_core/ledger/` runtime coupling was added in this tranche.

## 4. Validate-local path authority rule

`validate-local` path handling in this tranche:
- dedicated subcommand `--graph-state` path is authoritative for validation input,
- top-level CLI `--graph-state` is ignored for `validate-local` graph-state reads,
- validation checks bundle graph references against the supplied path and emits deterministic missing-reference details on failure.

## 5. Cross-lane envelope compatibility

Compatibility outcomes after bundle integration:
- query lane remains on Phase-299 envelope (`meta.schema_version: 299.v0.1`),
- verify lane remains on Phase-301 envelope (`meta.schema_version: 301.v0.1`),
- identity lane remains on legacy flat envelope (`schema_version: 254.v0.1`),
- bundle lane uses Phase-303 envelope (`meta.schema_version: 303.v0.1`) with `data.subject`, `data.result`, and `data.checks`.

## 6. Test evidence summary

Executed in this tranche:
- `tests/test_d2e_07_bundle_subsystem_304.py`,
- `tests/test_d2e_07_bundle_subsystem_contract_303.py`,
- `tests/test_d2e_06_verify_subsystem_contract_301.py`,
- `tests/test_d2e_05_query_subsystem_contract_299.py`,
- `tests/test_d2e_06_verify_subsystem_302.py`,
- `tests/test_d2e_05_query_subsystem_300.py`,
- `tests/test_d2e_04_identity_subsystem_294.py`,
- `tests/test_reputation.py`,
- `tests/test_sybil_defense.py`.

All targeted suites passed in Phase-304 execution.

## 7. Non-goals and carry-forward pointer

Non-goals in this tranche:
- no decision-log mutation,
- no D2e-08 implementation,
- no new anti-abuse/reputation constants or formula changes,
- no mandatory payment/facilitator integration path.

Carry-forward pointer:
- Phase 305 should publish the economic monitoring rollout baseline for D2e surfaces,
- Phase 306 should execute composed query/verify/bundle integration preflight against this runtime baseline.
