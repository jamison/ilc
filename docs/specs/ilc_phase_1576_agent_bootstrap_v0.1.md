# ILC Phase 1576 Agent Bootstrap v0.1

**Phase:** `1576-agent-bootstrap`  
**Validator-safe label:** `1576-Fix3`  
**Date:** 2026-07-19  
**Sensitivity:** NON-SENSITIVE

## 1. Purpose

This phase defines the first local agent-bootstrap readiness plan after public distribution. It consumes the local bootstrap census intake bundle and verifies the signed Genesis v0.5 release artifacts that a public or local agent must anchor to before later graph-native participation.

This is not the full distributed bootstrap rehearsal. The full rehearsal still depends on `1576-slice-schema`, `1576-slice-verifier`, `1576-slice-materializer`, `1576-sidecar-profile`, and `1576-private-slice`.

## 2. Runtime Surface

Runtime module:

`ilc_core/rc/agent_bootstrap.py`

CLI surface:

```bash
ilc agent-bootstrap plan \
  --census-intake out/bootstrap_census_intake_1576/local_intake_current.json \
  --release-manifest release_artifacts/genesis_v05/manifest.json \
  --json-out out/agent_bootstrap_1576/local_agent_bootstrap_plan.json
```

The command writes one local JSON plan. It does not write LMDB, public graph state, wallets, settlement state, minting state, treasury state, or epoch state.

## 3. Dependency Verification

The plan validates:

- Census intake schema version equals `bootstrap_census_intake_1576.v0.1`.
- Census intake phase equals `1576-bootstrap-census-intake`.
- Census intake ID equals `bootstrap_census_intake:<intake_body_sha256>`.
- Census intake canonical body hash matches `intake_body_sha256`.
- Required census intake tokens are present.
- Required census intake non-claims are present and `true`.
- Release artifact manifest schema equals `ilc_release_artifact_manifest.v0.1`.
- Release artifact manifest phase equals `1575c-Fix3`.
- Every file listed in the release artifact manifest exists and matches its file-byte SHA-256.
- Core Slice 0 detached verification sidecar reports `signature_verified`.
- Public-RC Baseline Slice 1 detached verification sidecar reports `signature_verified`.
- Signature payload file SHA-256 matches the sidecar `signature_payload_sha256`.
- Signature hex text SHA-256, after trimming surrounding whitespace, matches the sidecar `signature_sha256`.

The final point is intentional: the release artifact manifest commits to the file bytes, including final newline, while the signature verification sidecars record the hash of the canonical hex text submitted to the verifier.

## 4. Candidate Rows

Each accepted census intake entry becomes one candidate bootstrap row:

- `bootstrap_candidate_id`
- `receipt_id`
- `install_surface`
- `bootstrap_classification`
- `agent_identity_configured`
- `d2e_lineage_id`
- `ccss_agent_id`
- `baseline_all_signatures_verified`
- `verifier_status = not_granted`
- `graph_write_status = not_written`

The row is status-only bootstrap evidence. It is not a validator admission decision and not a claim of live verifier participation.

## 5. Materialization Boundary

The local bootstrap plan records:

`atlas_slice_manifest_materialization = pending_1576_slice_schema_verifier_materializer`

Required downstream phases:

- `1576-slice-schema`
- `1576-slice-verifier`
- `1576-slice-materializer`
- `1576-sidecar-profile`
- `1576-private-slice`

This keeps the current bridge honest. Agents can verify the signed v0.5 release artifacts and stage local candidate state now. Full graph-native distributed bootstrap still requires the slice production lanes.

## 6. Non-Claims

The plan commits these non-claims:

- `no_ccss_delivery_activation`
- `no_ecu_credit`
- `no_epoch_transition`
- `no_full_distributed_bootstrap_rehearsal`
- `no_lmdb_write`
- `no_live_settlement`
- `no_production_minting`
- `no_public_graph_write`
- `no_public_p2p_activation`
- `no_verifier_role_grant`
- `no_wallet_write`

## 7. Local Evidence Run

The local plan consumed:

`out/bootstrap_census_intake_1576/local_intake_current.json`

and:

`release_artifacts/genesis_v05/manifest.json`

Output:

`out/agent_bootstrap_1576/local_agent_bootstrap_plan.json`

Observed result:

- Plan ID: `agent_bootstrap_plan:9f5fa174eefabf350c73367707b3ac7dfc70aae95a72a17fbba6794c3f3aadcf`
- Candidate agents: `1`
- Release artifact manifest verified: `true`
- Detached signature sidecars verified: `true`
- Candidate verifier status: `not_granted`
- Candidate graph write status: `not_written`
- Materialization status: `pending_1576_slice_schema_verifier_materializer`

The output path is an ignored local artifact. It is intentionally not a committed authority artifact.

## 8. Tokens

- `agent_bootstrap_plan_committed_phase_1576`
- `agent_bootstrap_census_intake_dependency_verified_phase_1576`
- `agent_bootstrap_signed_baseline_manifest_verified_phase_1576`
- `agent_bootstrap_no_verifier_no_epoch_transition_phase_1576`

## 9. Next Work

The next main-lane phases should implement the signed slice production path:

1. `1576-slice-schema`
2. `1576-slice-verifier`
3. `1576-slice-materializer`
4. `1576-sidecar-profile`
5. `1576-private-slice`

Only after those are complete should ILC claim a full multi-machine, multi-agent bootstrap rehearsal from signed slices.
