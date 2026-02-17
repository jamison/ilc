# ILC Broad Exception Boundary Policy v0.1

## Status
Locked in Phase 1011.

## Purpose

Define where broad exception catches (`except Exception`) are acceptable and where they are not.

This policy is targeted to the Genesis-readiness concern about debuggability and silent failure masking. It does not require immediate full-codebase elimination in one phase, but it does require deterministic narrowing in utility modules and explicit boundary rationale where broad catches remain.

## Rule Set

1. Utility and codec modules must use specific exception families.
2. Broad catches are allowed only at boundary wrappers where:
   - external IO/runtime behavior is intentionally collapsed to a stable error token, and
   - a deterministic debug log is emitted, or a structured CLI error is produced.
3. Silent swallow (`except Exception: pass`) is disallowed.
4. New broad catches in utility modules are prohibited.

## Narrowed module set in Phase 1011

The following modules were narrowed from broad catches to specific exceptions:

- `ilc_core/encoding/cidv1.py`
- `ilc_core/protocol/ndjson_bundle.py`
- `ilc_core/crypto/cbor_canonical.py`
- `ilc_core/eve/capsule.py`
- `ilc_core/ledger/canon_export_bundle_verify_sig.py`
- `ilc_core/ledger/canon_bundle_audit_artifact.py`
- `ilc_core/protocol/ilc_cluster_a_replay_proof_schemas.py`
- `ilc_core/protocol/ilc_cluster_a_replay_proof_batch.py`

## Remaining broad-catch boundary classes

Remaining broad catches are currently accepted in:

- CLI main wrappers that convert exceptions into stable machine-readable error payloads.
- Protocol gate/check wrappers that intentionally convert runtime exceptions into deterministic failure-check rows.
- API entrypoint wrappers that collapse unexpected internal failures into safe user-facing HTTP errors.

These are considered boundary-layer behaviors and are subject to incremental narrowing in future phases.

## Guardrail

`tests/test_broad_exception_boundary_policy_phase_1011.py` enforces that the narrowed module set no longer contains broad catches.
