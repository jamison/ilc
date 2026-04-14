# ILC Signing Export Reproducibility Fix 656 v0.1

Status: implemented
Date: 2026-04-14
Phase: 656
Window: 655-658

## 1. Bug class and touched surfaces

`canon_export_manifest_signing_reproducibility_fixed_in_656`
`registry_signature_sidecar_reproducibility_fixed_in_656`

Phase 656 fixes the immediate wall-clock reproducibility defects in:
- `ilc_core/ledger/canon_export_bundle_sign.py`
- `ilc_core/ledger/canon_bundle_key_registry.py`

The bug class was simple and dangerous: `signed_at` fields inside touched
signed metadata were derived from implicit local wall clock, so repeated signing
of the same logical payload could produce different signed metadata solely due
to local execution time.

## 2. Manifest signing contract

`signed_metadata_timestamp_must_be_explicit_or_deterministic`

The canon-export manifest signing contract is now:
- `sign_manifest(...)` accepts explicit `signed_at`
- explicit `signed_at` must be strict ISO-8601 with timezone
- when explicit `signed_at` is absent, the signer reuses manifest `signed_at`
  if already present and valid
- otherwise the signer falls back deterministically to manifest `created_at`
- if neither field is available, the signer uses `1970-01-01T00:00:00Z`

This removes implicit local wall clock from touched manifest signing while
preserving the strict ISO `signed_at` field required by manifest validation and
signature verification.

## 3. Registry signature sidecar contract

The detached registry signature sidecar contract is now:
- `sign_registry_file(...)` accepts explicit `signed_at`
- explicit `signed_at` must be strict ISO-8601 with timezone
- when explicit `signed_at` is absent, the signer falls back deterministically
  to registry `updated_at`
- if deterministic registry state cannot provide a valid timestamp, the signer
  uses `1970-01-01T00:00:00Z`
- the detached sidecar is written as sorted-key, compact-separator,
  `allow_nan=False` JSON

This removes implicit local wall clock from touched registry signing while
keeping detached verification compatibility intact.

## 4. Verification compatibility and preserved boundaries

`verification_compatibility_preserved_after_656`

Phase 656 preserves:
- strict ISO timestamp verification on touched manifest and registry sidecar
  surfaces
- existing verification compatibility for registry signature sidecars,
  including compatibility-mode acceptance of legacy sidecars without
  `key_fingerprint`
- bounded scope with no decision-log mutation, no ADR mutation, and no helper
  cleanup beyond the manifest and detached registry-signature surfaces

Phase 656 does not yet close the helper-level timestamp surfaces assigned to
Phase 657.
