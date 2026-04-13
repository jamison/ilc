# ILC Canonical JSON and Signature Boundary Hardening 644 v0.1

Status: hardening artifact
Date: 2026-04-14
Classification: implementation and security hardening
Phase: 644
Owner lane: G8 security boundary and remaining-float strike force

## 1. Scope and threat basis

Phase 644 hardens the touched bundle/report/signature surfaces that still used
`sort_keys=False` or otherwise left canonical JSON vulnerable to insertion-order
or whitespace drift.

## 2. Canonical JSON contract

Touched machine-verifiable or machine-consumed JSON surfaces now use:
- `sort_keys=True`
- `separators=(",", ":")`
- `allow_nan=False`

`canonical_json_sort_keys_and_compact_separators_locked`
`canonical_json_no_whitespace_hash_drift_on_touched_surfaces`

## 3. Touched file changes

Touched in this phase:
- `ilc_core/ledger/canon_bundle_replay_report.py`
- `ilc_core/ledger/canon_export_bundle_sign.py`
- `ilc_core/ledger/canon_bundle_pipeline_report.py`
- `ilc_core/cli/canon_bundle_sign.py`
- `ilc_core/cli/canon_bundle_validate.py`
- `ilc_core/cli/canon_bundle_replay.py`
- `ilc_core/cli/canon_bundle_pipeline.py`

The manifest-signing path now signs canonical manifest bytes rather than
insertion-order-dependent JSON text.

`manifest_signing_uses_canonical_json_bytes`
`machine_verifiable_bundle_reports_no_longer_use_sort_keys_false`

## 4. Non-finite JSON boundary

Touched canonical JSON emission now rejects non-finite values rather than
allowing `NaN` or infinities to survive on machine-verifiable JSON paths.

The manifest-signing path additionally rejects non-finite constants while
loading manifest JSON for rewrite/signing.

`canonical_json_non_finite_constants_rejected_on_touched_surfaces`

## 5. Second-order regression guardrails

This phase explicitly avoids the common follow-on bug where keys are sorted but
JSON whitespace remains inconsistent across language implementations.

The touched canonical JSON paths therefore lock compact separators alongside key
ordering.

`json_canonicalization_fix_does_not_introduce_separator_drift`

## 6. Verification evidence

Verification in this phase covers:
- canonical JSON emission on touched sources
- manifest-signing integrity preservation
- non-finite manifest rejection
- existing CLI parseability after canonicalization changes
