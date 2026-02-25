# ILC D2e-05 Query Subsystem Handoff 300 v0.1

Status: Phase-300 implementation handoff artifact  
Date: 2026-02-25  
Owner lane: G8 Constitution Cluster A

## 1. Implementation scope summary

Phase 300 implements the initial D2e-05 query runtime tranche in `ilc_core/cli/main.py`:
- query subcommands: `node`, `epoch`, `claim`,
- query-local nested JSON envelope aligned to Phase-299 (`ok/data/meta`),
- query error object aligned to Phase-299 (`error.code`, `error.message`),
- deterministic ordering for multi-match claim results.

## 2. Envelope boundary decision (Option A)

Locked boundary in this tranche:
- query subcommands use nested Phase-299 envelope,
- non-query commands (including `identity`) remain on legacy flat envelope.

This keeps D2e-05 implementation in-scope without forcing cross-command envelope migration in Phase 300.

## 3. Data and anti-abuse boundary notes

Phase-300 query behavior is schema-conservative:
- no new reputation/reuse/sybil policy logic,
- no new reputation/reuse/sybil canonical field mappings,
- node payloads are returned as stored-state records without remapping.

Carry-forward:
- any canonical reputation/sybil query-schema expansion is deferred to Phase 302+ contract/runtime lanes.

## 4. Contract compliance snapshot

Compliance points:
- `meta.schema_version` for query responses is fixed to `299.v0.1`,
- argument/usage failures for query return exit code `2` with `query_invalid_input`,
- operational query failures return exit code `1` with contract tokens (`query_not_found`, `query_backend_unavailable`, `query_internal_error`),
- success paths return exit code `0`.

## 5. Test evidence summary

Executed in this tranche:
- `tests/test_d2e_05_query_subsystem_300.py`,
- `tests/test_d2e_05_query_subsystem_contract_299.py`,
- `tests/test_d2e_04_identity_subsystem_294.py`,
- `tests/test_reputation.py`,
- `tests/test_sybil_defense.py`.

All targeted suites passed in Phase-300 execution.

## 6. Non-goals and carry-forward pointer

Non-goals:
- no decision-log mutation,
- no D2e-06 or D2e-07 implementation,
- no cross-command envelope migration.

Carry-forward pointer:
- Phase 301 should lock verify-subsystem contract boundaries against the now-shipped query runtime envelope split.
