# ILC D2e-06 Verify Subsystem Handoff 302 v0.1

Status: Phase-302 implementation handoff artifact  
Date: 2026-02-25  
Owner lane: G8 Constitution Cluster A

## 1. Implementation scope summary

Phase 302 implements the initial D2e-06 verify runtime tranche in `ilc_core/cli/main.py`:
- verify subcommands: `claim`, `node`, `lineage`,
- verify-local nested JSON envelope aligned to Phase-301 (`ok/data/meta`),
- verify error object aligned to Phase-301 (`error.code`, `error.message`),
- deterministic `checks` ordering with minimum check schema.

## 2. Verify lineage boundary in this tranche

Locked boundary in this tranche:
- `verify lineage` validates against local identity-state only,
- no import or mutation of signer-lineage runtime modules under `ilc_core/security/`.

This keeps Phase-302 verify runtime in-scope and avoids cross-lane coupling to CDL-001 runtime internals.

## 3. Minimum checks schema lock

All verify success payloads in this tranche emit `checks` entries with minimum fields:
- `check_type`: string token,
- `passed`: boolean.

Optional additional fields are permitted when deterministic.

## 4. Query and identity compatibility notes

Compatibility outcomes:
- query command remains on Phase-299 nested envelope (`schema_version: 299.v0.1`),
- identity command remains on legacy flat envelope (`schema_version: 254.v0.1`),
- query read path is side-effect-free in this tranche (query no longer mutates graph state file metadata).

## 5. Contract compliance snapshot

Compliance points:
- `meta.schema_version` for verify responses is fixed to `301.v0.1`,
- usage failures for verify return exit code `2` with `verify_invalid_input`,
- operational verify failures return exit code `1` with contract tokens (`verify_not_found`, `verify_backend_unavailable`, `verify_internal_error`),
- success paths return exit code `0`.

## 6. Test evidence summary

Executed in this tranche:
- `tests/test_d2e_06_verify_subsystem_302.py`,
- `tests/test_d2e_06_verify_subsystem_contract_301.py`,
- `tests/test_d2e_05_query_subsystem_300.py`,
- `tests/test_d2e_05_query_subsystem_contract_299.py`,
- `tests/test_d2e_04_identity_subsystem_294.py`,
- `tests/test_reputation.py`,
- `tests/test_sybil_defense.py`.

All targeted suites passed in Phase-302 execution.

## 7. Non-goals and carry-forward pointer

Non-goals:
- no decision-log mutation,
- no D2e-07 implementation,
- no anti-abuse/reputation policy constant changes.

Carry-forward pointer:
- Phase 303 should lock bundle contract boundaries against the now-shipped query and verify runtime envelope split.
