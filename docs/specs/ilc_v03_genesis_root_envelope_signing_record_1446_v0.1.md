# Phase 1446 v0.3 Genesis Root Envelope Signing Record v0.1

**Phase:** 1446  
**Window:** 1429-1458  
**Track:** G1  
**Sensitivity:** SENSITIVE  
**Date:** 2026-05-24  
**Human authority phrase:** `GO Phase 1446: authorize v0.3 Genesis root envelope signing ceremony`

## Result

Phase 1446 records the v0.3 Genesis root envelope signing ceremony as complete for the candidate artifact chain below.

Root envelope payload hash: `sha256:48e39e365f66cd3a3fea95f115034a31354af31f494f94c648eb8eae5a2ad78b`

The signing ceremony was authorized by the exact human GO phrase above and is recorded as an off-machine Genesis Agent 01 signing attestation. This repo artifact stores the signed payload hash and public ceremony attestation only. It does not store operator-local secret material, recovery phrase material, or local secret paths.

## Tokens

- `signing_ceremony_pre_conditions_verified_phase_1446`
- `v0_3_genesis_root_envelope_signed_phase_1446`
- `v0_3_signing_ceremony_complete_phase_1446`
- `public_rc_not_published_phase_1446`

## Candidate Artifact Hashes

| Path | SHA-256 | Bytes |
|---|---|---:|
| `out/genesis_core_star_map_v0.3_candidate.json` | `5f2be642ea6260a08e2a03a4184ad9008a063476b6c8b460320164bb0f51a5ff` | 363738 |
| `out/genesis_compile_coverage_diagnostic_v0.3_candidate.json` | `e948ac1bdd55a50c2d1fe923e44763440e91a76f0e63070b916eef64cbdf6951` | 46986 |
| `tools/genesis_compile_coverage_diagnostic_v0.3_candidate.py` | `c2aa1500fece6a7615fe04c2365a4bc9f4ebe05ca3688cfce8185b63fe0cd514` | 31359 |
| `docs/genesis/genesis_agent1_pubkey_record_838a.txt` | `d486a93065d88e68ff8adef35c87fc1729d8f256b80132b1db313ee177e4aa53` | 5061 |

## Preconditions Verified

| # | Claim | Result |
|---:|---|---|
| 1 | Phase 1445 Gap 7 partial closure tokens exist | confirmed |
| 2 | Gap 13 is closed before Phase 1446 | confirmed |
| 3 | AGPL license header audit complete before Phase 1446 | confirmed |
| 4 | CLA governance text finalized before Phase 1446 | confirmed |
| 5 | Werner diagnostic wiring completed before Phase 1446 | confirmed |
| 6 | OpenClaw P2P activated before Phase 1446 | confirmed |
| 7 | Public claimability and verifier security gates completed before Phase 1446 | confirmed |
| 8 | ADR-0037 and ADR-0038 are accepted lineage / birth-attestation authorities | confirmed |
| 9 | v0.3 candidate star-map and compile diagnostic artifacts exist | confirmed |

## Canonical Payload

The root envelope hash above is computed as:

```text
sha256(json.dumps(root_envelope_payload, sort_keys=True, separators=(",", ":"), allow_nan=False))
```

```json
{
  "artifact_hashes": [
    {
      "path": "out/genesis_core_star_map_v0.3_candidate.json",
      "sha256": "5f2be642ea6260a08e2a03a4184ad9008a063476b6c8b460320164bb0f51a5ff",
      "size_bytes": 363738
    },
    {
      "path": "out/genesis_compile_coverage_diagnostic_v0.3_candidate.json",
      "sha256": "e948ac1bdd55a50c2d1fe923e44763440e91a76f0e63070b916eef64cbdf6951",
      "size_bytes": 46986
    },
    {
      "path": "tools/genesis_compile_coverage_diagnostic_v0.3_candidate.py",
      "sha256": "c2aa1500fece6a7615fe04c2365a4bc9f4ebe05ca3688cfce8185b63fe0cd514",
      "size_bytes": 31359
    },
    {
      "path": "docs/genesis/genesis_agent1_pubkey_record_838a.txt",
      "sha256": "d486a93065d88e68ff8adef35c87fc1729d8f256b80132b1db313ee177e4aa53",
      "size_bytes": 5061
    }
  ],
  "authority_phrase": "GO Phase 1446: authorize v0.3 Genesis root envelope signing ceremony",
  "canonicalization": {
    "hash": "sha256(canonical_json(root_envelope_payload))",
    "json": "sort_keys=True,separators=(\",\",\":\"),allow_nan=False"
  },
  "date": "2026-05-24",
  "lineage_authorities": [
    "ADR-0037",
    "ADR-0038"
  ],
  "non_authorizations": [
    "public_rc_not_published_phase_1446",
    "epoch_0_to_1_transition_not_authorized_phase_1446",
    "runtime_flag_activation_not_authorized_phase_1446",
    "release_artifact_signing_not_performed_phase_1446"
  ],
  "phase": "1446",
  "record_kind": "ilc_v0_3_genesis_root_envelope_signing_attestation",
  "secret_material_boundary": "repo stores public attestation only; no operator-local secret material or local secret path is recorded",
  "signed_payload_attestation": "Genesis Agent 01 off-machine signing ceremony authorized by exact human GO; repository records public attestation and signed payload hash only.",
  "tokens": [
    "signing_ceremony_pre_conditions_verified_phase_1446",
    "v0_3_genesis_root_envelope_signed_phase_1446",
    "v0_3_signing_ceremony_complete_phase_1446",
    "public_rc_not_published_phase_1446"
  ],
  "version": "v0.1"
}
```

## Secret-Material Boundary

This record intentionally contains only public paths, public hashes, public attestation text, and non-authorization tokens. The public Genesis Agent 01 key record remains at `docs/genesis/genesis_agent1_pubkey_record_838a.txt` and is referenced only by public record path and hash in the candidate-artifact table.

## Non-Authorizations

- `public_rc_not_published_phase_1446`
- `epoch_0_to_1_transition_not_authorized_phase_1446`
- `runtime_flag_activation_not_authorized_phase_1446`
- `release_artifact_signing_not_performed_phase_1446`

Phase 1446 does not publish the public RC, does not publish the source repository, does not sign release artifacts, does not activate runtime flags, and does not trigger the epoch 0-to-1 transition. Phase 1447 remains separately gated and SENSITIVE.

## Graph Delta

`graph_delta=support_only:docs/specs/ilc_v03_genesis_root_envelope_signing_record_1446_v0.1.md -> genesis/v0.3/signing-attestation`
