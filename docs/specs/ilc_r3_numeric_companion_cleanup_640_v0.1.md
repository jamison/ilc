# ILC R3 Numeric Companion Cleanup 640 v0.1

Status: implemented
Date: 2026-04-13
Window: 637-641
Phase: 640
Owner lane: G8 residual exact-numeric cleanup

## 1. Ratified dependency and cleanup target

Phase 640 consumes ratified `CDL-064` and cleans up the remaining `R3`
canon-export companion validators and scalar contracts so they align with the
exact-numeric rule already active in the core runtime surfaces.

The target is limited to the bounded companion layer only. No decision-log
mutation occurs in Phase 640. No ADR mutation occurs in Phase 640.

`r3_numeric_companion_cleanup_640_locked`
`cdl_064_dependency_consumed_in_phase_640`

## 2. Companion files migrated

The companion files migrated in Phase 640 are:
- `ilc_core/ledger/canon_export_validate.py`
- `ilc_core/ledger/canon_export_bundle_validate.py`
- `ilc_core/ledger/canon_export_bundle.py`
- `ilc_core/ledger/canon_export_format.py`
- `ilc_core/ledger/canon_bundle_audit_artifact.py`

Directly coupled tests updated for coherence:
- `tests/test_canon_export_validate.py`
- `tests/test_canon_export_bundle_validate.py`
- `tests/test_canon_export_bundle.py`
- `tests/test_canon_export_format.py`

## 3. Canon-export companion contract changes

Phase 640 aligned the companion scalar contracts to the exact-numeric rule:
- the touched companion `JsonScalar` type aliases no longer declare `float` as
  the scalar contract for machine-legible exact numeric surfaces
- `ilc_core/ledger/canon_export_format.py` now normalizes finite float/decimal
  numeric scalars into CDL-064 canonical decimal strings before returning the
  export payload
- `ilc_core/ledger/canon_export_bundle.py` now normalizes bundle payload
  numeric scalars before deterministic JSON serialization so bundle content does
  not reintroduce float-backed exact numeric surfaces
- `ilc_core/ledger/canon_bundle_audit_artifact.py` now writes audit JSON with
  `allow_nan=False` and canonical key ordering

The machine-readable companion assumption after Phase 640 is:
- exact numeric surfaces in the touched export/bundle companion layer are
  string-or-int at the JSON boundary rather than float-backed
- finite legacy float ingress is normalized to canonical decimal strings where
  this phase still preserves compatibility

`canon_export_companion_float_scalar_contract_removed`

## 4. Validation and scalar contract cleanup

Phase 640 cleaned the companion validators so they stop treating float as the
canonical numeric input:
- `ilc_core/ledger/canon_export_validate.py` now validates snapshot balances
  through exact-decimal parsing and rejects negative or non-finite numeric
  values
- `ilc_core/ledger/canon_export_bundle_validate.py` now loads manifest/export/
  validate JSON with explicit non-finite rejection so `NaN`, `Infinity`, and `-Infinity` cannot pass through companion validation
- bundle validation only escalates to full canon-export schema validation when
  the export payload explicitly declares `canon_export_format`, preserving the
  older bounded bundle contract while still enforcing exact-numeric safety

Residual bounded compatibility left after this phase:
- finite legacy float ingress may still be accepted by touched companion
  builders, but it is normalized immediately to canonical decimal strings
- final residual hardening and no-float closure remain in Phase 641

`canon_export_companion_validators_aligned_to_exact_numeric`
`canon_export_companion_non_finite_rejection_aligned`

## 5. Verification and residual defers

Verification used for Phase 640:
- prompt validation
- Phase 639 cleanup gate
- direct canon-export validator, bundle-validator, bundle-writer, and format
  tests
- decision-log no-diff guard

Residual carry-forward after this phase:
- final residual numeric hardening and closure move to Phase 641

`r3_numeric_companion_cleanup_verification_defined`
`window_637_641_moves_to_residual_numeric_hardening_gate`
