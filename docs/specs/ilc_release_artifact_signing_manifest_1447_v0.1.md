# Phase 1447 Release Artifact Signing Manifest v0.1

**Phase:** 1447  
**Window:** 1429-1458  
**Track:** G2  
**Sensitivity:** SENSITIVE  
**Date:** 2026-05-24  
**Human authority phrase:** `GO Phase 1447: authorize release artifact signing and manifest finalization`

## Result

Phase 1447 records release-artifact signing attestation against the Phase 1446 v0.3 Genesis root envelope and finalizes the `public_rc_launch_readiness_manifest_v1` payload.

Release signing token: `release_artifacts_signed_phase_1447`  
Launch-readiness token: `public_rc_launch_readiness_manifest_v1_finalized_phase_1447`  
Publication non-claim token: `public_repository_not_published_phase_1447`

No public repository, public package, public URL, public RC publication, runtime activation, manifest activation signature, or epoch transition is authorized by this record.

## Pre-Condition Verification

| Claim | Evidence | Result |
|---|---|---|
| Phase 1446 signing ceremony complete | `ilc_core/rc/signing_ceremony_status.py` | confirmed |
| Phase 1446 root envelope signed | `ilc_core/rc/signing_ceremony_status.py` | confirmed |
| Phase 1446 preconditions verified | `ilc_core/rc/signing_ceremony_status.py` | confirmed |
| Phase 1446 public RC non-publication boundary preserved | `ilc_core/rc/signing_ceremony_status.py`; `docs/specs/ilc_v03_genesis_root_envelope_signing_record_1446_v0.1.md` | confirmed |
| Launch-readiness manifest schema exists | `docs/specs/ilc_launch_readiness_manifest_schema_1422_v0.1.md` | confirmed |
| Release artifact production gate precedent exists | `ilc_core/rc/release_artifact_production_gate.py`; `docs/specs/ilc_release_artifact_production_gate_1334_v0.1.json` | confirmed |

## Phase 1446 Reproducibility Check

Phase 1446 root envelope recomputation: `PASS`.

Expected root envelope payload hash: `sha256:48e39e365f66cd3a3fea95f115034a31354af31f494f94c648eb8eae5a2ad78b`  
Recomputed root envelope payload hash: `sha256:48e39e365f66cd3a3fea95f115034a31354af31f494f94c648eb8eae5a2ad78b`  
Sidecar root envelope payload hash: `sha256:48e39e365f66cd3a3fea95f115034a31354af31f494f94c648eb8eae5a2ad78b`

Phase 1446 artifact path/hash set exact match: `PASS`.

| Path | SHA-256 |
|---|---|
| `docs/genesis/genesis_agent1_pubkey_record_838a.txt` | `d486a93065d88e68ff8adef35c87fc1729d8f256b80132b1db313ee177e4aa53` |
| `out/genesis_compile_coverage_diagnostic_v0.3_candidate.json` | `e948ac1bdd55a50c2d1fe923e44763440e91a76f0e63070b916eef64cbdf6951` |
| `out/genesis_core_star_map_v0.3_candidate.json` | `5f2be642ea6260a08e2a03a4184ad9008a063476b6c8b460320164bb0f51a5ff` |
| `tools/genesis_compile_coverage_diagnostic_v0.3_candidate.py` | `c2aa1500fece6a7615fe04c2365a4bc9f4ebe05ca3688cfce8185b63fe0cd514` |

The recomputation used:

```text
sha256(json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False))
```

## Artifact Signing Summary

Release artifacts and release artifact classes are bound to the Phase 1446 v0.3 root envelope by this Phase 1447 attestation. The root envelope payload hash is `sha256:48e39e365f66cd3a3fea95f115034a31354af31f494f94c648eb8eae5a2ad78b`.

| Artifact type | Path or class | SHA-256 | Phase 1447 treatment |
|---|---|---|---|
| `source_release_tarball` | `out/release_artifacts/phase_1334/ilc-source-release-phase-1334.tar.gz` | `60a2f404576e5abbc45bc29ab4ae106368a764aa3d37f2ca458d35363cc45a47` | actual unsigned artifact bound by Phase 1447 attestation |
| `cli_binary` | `not produced in this repo phase` | `not_applicable` | artifact class covered; no new binary bytes generated |
| `genesis_bundle` | `out/genesis_core_star_map_v0.3_candidate.json` | `5f2be642ea6260a08e2a03a4184ad9008a063476b6c8b460320164bb0f51a5ff` | v0.3 Genesis candidate bound by Phase 1446 root envelope |
| `star_map_release_envelope` | `out/genesis_compile_coverage_diagnostic_v0.3_candidate.json` | `e948ac1bdd55a50c2d1fe923e44763440e91a76f0e63070b916eef64cbdf6951` | v0.3 diagnostic companion bound by Phase 1446 root envelope |

The Phase 1447 manifest records public references and hashes only. Operator signing secrets, wallet phrases, HSM credentials, and local secret paths are not recorded.

## Launch Readiness Manifest Finalization

Manifest content hash: `sha256:fb171d78806950de07d6ce1ae7143eca3f7f2a50fef7e06e833c89447ffe5bdf`

Canonical hash rule:

```text
sha256(json.dumps(payload_with_manifest_content_hash_null_and_manifest_signature_null, sort_keys=True, separators=(",", ":"), allow_nan=False))
```

Required field evidence:

| Field | Artifact | SHA-256 | Status | Token |
|---|---|---|---|---|
| `phase_1387_hardening_gate_verdict` | `docs/specs/ilc_pre_activation_hardening_gate_report_1387_rerun_v0.2.md` | `3f0be4d5decb1d8a06d1edb391ab8b00d02808476ee8060f47020e0a547cf825` | `PASS` | `pre_activation_hardening_gate_pass_phase_1387` |
| `phase_1389_claimability_gate_verdict` | `docs/specs/ilc_public_claimability_activation_gate_report_1389_rerun_v0.2.md` | `f85faf285cb0371ad19d3f57af715b2e3af62cddf7ca75edd81f491a89fd070c` | `PASS` | `result=public_claimability_activated` |
| `j008_jury_activation_gate_verdict` | `docs/specs/ilc_production_jury_activation_gate_pass_1427_v0.1.md` | `6ed2a9b30a509541611cac22aa2b9b4291cec6743c1ebfac76294c2a49e9b12a` | `PASS` | `production_jury_activation_gate_pass_phase_1427` |
| `soft_rc_eligible` | `docs/specs/ilc_soft_rc_gate_rerun_1426_v0.1.md` | `ab591121896a0894c23b0cb5ea1588e89d13b4809d1a240a4fdb746bc7cb4ec6` | `PASS` | `soft_rc_eligible=true_phase_1426` |

`epoch_0_to_1_transition_authorized` remains `false`. `manifest_signature` remains `null`; public activation signing is outside Phase 1447.

```json
{
  "activation_timestamp_epoch": 0,
  "epoch_0_to_1_transition_authorized": false,
  "genesis_signing_authority": {
    "agent_id_ref": "docs/genesis/genesis_agent1_pubkey_record_838a.txt",
    "key_record_sha256": "d486a93065d88e68ff8adef35c87fc1729d8f256b80132b1db313ee177e4aa53",
    "key_record_token": "genesis_agent1_pubkey_record_838a",
    "phase_1446_root_envelope_hash": "sha256:48e39e365f66cd3a3fea95f115034a31354af31f494f94c648eb8eae5a2ad78b",
    "phase_1446_signing_record": "docs/specs/ilc_v03_genesis_root_envelope_signing_record_1446_v0.1.md",
    "status": "phase_1447_reference_only_manifest_signature_null"
  },
  "j008_jury_activation_gate_verdict": {
    "artifact": "docs/specs/ilc_production_jury_activation_gate_pass_1427_v0.1.md",
    "artifact_sha256": "6ed2a9b30a509541611cac22aa2b9b4291cec6743c1ebfac76294c2a49e9b12a",
    "phase": 1427,
    "status": "PASS",
    "token": "production_jury_activation_gate_pass_phase_1427",
    "verdict": "PASS"
  },
  "manifest_content_hash": "sha256:fb171d78806950de07d6ce1ae7143eca3f7f2a50fef7e06e833c89447ffe5bdf",
  "manifest_signature": null,
  "manifest_version": "public_rc_launch_readiness_manifest_v1",
  "phase_1387_hardening_gate_verdict": {
    "artifact": "docs/specs/ilc_pre_activation_hardening_gate_report_1387_rerun_v0.2.md",
    "artifact_sha256": "3f0be4d5decb1d8a06d1edb391ab8b00d02808476ee8060f47020e0a547cf825",
    "phase": 1387,
    "status": "PASS",
    "token": "pre_activation_hardening_gate_pass_phase_1387"
  },
  "phase_1389_claimability_gate_verdict": {
    "artifact": "docs/specs/ilc_public_claimability_activation_gate_report_1389_rerun_v0.2.md",
    "artifact_sha256": "f85faf285cb0371ad19d3f57af715b2e3af62cddf7ca75edd81f491a89fd070c",
    "phase": 1389,
    "status": "PASS",
    "token": "result=public_claimability_activated"
  },
  "soft_rc_eligible": {
    "artifact": "docs/specs/ilc_soft_rc_gate_rerun_1426_v0.1.md",
    "artifact_sha256": "ab591121896a0894c23b0cb5ea1588e89d13b4809d1a240a4fdb746bc7cb4ec6",
    "phase": 1426,
    "status": "PASS",
    "token": "soft_rc_eligible=true_phase_1426",
    "value": true
  }
}
```

## Deterministic Timestamp Rule

No `signed_at` field is introduced in the finalized launch-readiness payload. If a later phase requires a timestamp-like signed field, it must be derived from existing content metadata or use the fixed fallback `1970-01-01T00:00:00Z`. Phase 1447 uses no OS wall-clock value for signed bytes or manifest-content-hash inputs.

## Tokens

- `release_artifacts_signed_phase_1447`
- `public_rc_launch_readiness_manifest_v1_finalized_phase_1447`
- `public_repository_not_published_phase_1447`

## Non-Authorization Floor

- `public_repository_not_published_phase_1447`
- `epoch_0_to_1_transition_authorized=false`
- `manifest_signature=null`
- public repository publication is Phase 1448 scope
- epoch transition is Phase 1450 scope
- no new cryptographic key material is generated in this repo
- no runtime flag is activated
- no CDL mutation occurs
- no ECU, ILC, ledger, wallet, treasury, registry, or settlement mutation occurs

## Graph Delta

`graph_delta=support_only:docs/specs/ilc_release_artifact_signing_manifest_1447_v0.1.md -> public_rc/release-signing/manifest-finalization`
