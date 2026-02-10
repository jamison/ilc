# ILC Constitution Cluster A Clause Binding v0.1

**Phase**: 140
**Module**: `ilc_core.protocol.ilc_cluster_a_clause_binding`

## Overview
This specification defines the deterministic mapping between abstract constitutional requirements (IDs `CONST-*`) and executable runtime checks for Cluster A.

## Scope
Version v0.1 covers the initial acceptance integrity set:
- `CONST-001` to `CONST-004`.

## Check Definitions

### CONST-001: Deterministic Envelope Invariant
**Requirement**: All accepted records must conform to the strict, deterministic envelope schema and be ingested without error.
**Check Logic**:
- Pass: Ingest phase completed with `ok=True`.
- Fail: Ingest phase failed with `schema_violation:*` or `invalid_json`.
- Fail Code: `context_violation:non_deterministic_envelope`

### CONST-002: Identity Binding Invariant
**Requirement**: Records must be bound to a canonical policy identity (hash, epoch, window) with valid value formats.
**Check Logic**:
- Pass: Binding values are present (where required keys exist) and structurally valid (hex, int, str).
- Fail: Any `value_violation:*` in binding fields.
- Fail Code: `context_violation:identity_binding_invariant_failed`

### CONST-003: Signature & Context Integrity Invariant
**Requirement**: The bound policy context in the artifact must strictly match the expected verification context.
**Check Logic**:
- Pass: `binding_context` matches `expected_context` for all provided keys (hash/epoch/window).
- Fail: Any `context_violation:policy_*_mismatch`.
- Fail Code: `context_violation:signature_context_invariant_failed`

### CONST-004: Policy-Bound Conformance Invariant
**Requirement**: Acceptance-critical conformance checks must be performed against explicit policy expectations. Unbound checks are insufficient for governance acceptance.
**Check Logic**:
- Pass: Expectations (hash, epoch, or window) were provided to the check function.
- Fail: No expectations provided.
- Fail Code: `context_violation:policy_bound_check_invariant_failed`

## Runtime Integration
These checks are executed automatically by `conformance_check_cluster_a_artifact`.
Results are embedded in the `constitution_checks` field of the conformance result.

### Result Shape
```json
{
  "check_id": "CONST-001",
  "status": "pass|fail|not_applicable",
  "error_code": "optional_string",
  "details": null
}
```
Binary success of the conformance check (`ok=True`) strictly requires `constitution_checks.ok=True`.
