# ILC Phase 1576 Bootstrap Census Intake v0.1

**Phase:** `1576-bootstrap-census-intake`  
**Validator-safe label:** `1576-Fix2`  
**Date:** 2026-07-19  
**Sensitivity:** NON-SENSITIVE unless live network submission is authorized

## 1. Purpose

Phase 1576 bootstrap receipt work created a local, agent-side proof surface for install status, local identity status, signed baseline-slice verification, and explicit no-mint/no-settlement non-claims. This phase adds the Genesis-side local intake path for those receipts.

The intake path is a staging and validation layer only. It does not credit ECU, mint ILC, assign verifier status, write LMDB, publish graph state, touch wallets, or advance epoch state.

## 2. Runtime Surface

Runtime module:

`ilc_core/rc/bootstrap_census_intake.py`

CLI surface:

```bash
ilc bootstrap-census intake \
  --receipt out/public_agent_bootstrap_receipts_1576/local_receipt_post_commit_07b667fef.json \
  --json-out out/bootstrap_census_intake_1576/local_intake_current.json
```

The command accepts repeated `--receipt` paths and repeated `--receipt-dir` directories. Directory intake is bounded to `*.json` files, deduplicated by resolved local path before validation, and then deduplicated by receipt ID.

## 3. Validation Rules

Each accepted input receipt must satisfy:

- Schema version equals `public_agent_bootstrap_receipt_1576.v0.1`.
- Receipt kind equals `public_agent_bootstrap_receipt`.
- Phase equals `1576-public-agent-bootstrap-receipts`.
- Required bootstrap receipt tokens are present.
- Receipt ID equals `public_agent_bootstrap_receipt:<receipt_body_sha256>`.
- `receipt_body_sha256` matches the canonical JSON hash of the receipt body fields.
- Required no-claim booleans are all `true`.
- Distribution telemetry boundary flags are all `false`.
- No float appears anywhere in the receipt or intake payload.

Invalid receipts fail closed by default. Operators may pass `--allow-invalid` to stage invalid receipt metadata for offline review without accepting it as graph evidence.

## 4. Deduplication And Classification

The intake bundle stores one accepted entry per receipt ID. Duplicate receipts are recorded separately with their duplicate source path and original accepted source path.

Accepted receipts are classified into one of four status-only classes:

- `identity_status_and_baseline_verified`
- `identity_status_only`
- `install_baseline_verified_no_identity`
- `install_status_only`

These classes are not verifier roles and do not imply agent participation in consensus. They are local census categories for later graph-native admission review.

## 5. Non-Claims

The intake bundle commits these non-claims:

- `no_ecu_credit`
- `no_epoch_transition`
- `no_lmdb_write`
- `no_live_settlement`
- `no_production_minting`
- `no_public_graph_write`
- `no_verifier_role_claim`
- `no_wallet_write`

This phase intentionally keeps the bridge from public adoption telemetry to graph evidence narrow. GitHub visits, GitHub clones, and ClawHub installs remain distribution telemetry, not graph-native evidence.

## 6. Local Evidence Run

The local intake rehearsal consumed the post-commit bootstrap receipt from the prior phase:

`out/public_agent_bootstrap_receipts_1576/local_receipt_post_commit_07b667fef.json`

Output:

`out/bootstrap_census_intake_1576/local_intake_current.json`

Observed result:

- Intake ID: `bootstrap_census_intake:3bbe3366acfc808432e5e4ba3806ea660e2d085554b90dbf7eb1c0609689c82e`
- Accepted receipts: `1`
- Duplicate receipts: `0`
- Invalid receipts: `0`
- Classification: `identity_status_and_baseline_verified`
- LMDB write: `false`

The output path is an ignored local artifact. It is intentionally not a committed authority artifact.

## 7. Tokens

- `bootstrap_census_intake_local_queue_committed_phase_1576`
- `bootstrap_census_receipt_dedup_validation_committed_phase_1576`
- `bootstrap_census_identity_status_only_classification_committed_phase_1576`
- `bootstrap_census_no_lmdb_no_public_graph_write_phase_1576`

## 8. Next Work

The next bootstrap lane should decide how staged local census bundles become graph-native evidence nodes. That later phase must define the privacy review, authority boundary, LMDB write API, and public/private slice membership rules before any intake data is promoted into graph state.
