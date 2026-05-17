# ILC CDL-090 Identity Bootstrap Prelock Spec 1372 v0.1

**CDL number:** CDL-090
**Title:** Identity Bootstrap
**Status after this phase:** OPEN / PRELOCKED
**Phase:** 1372
**Date:** 2026-05-17
**Prelock token:** `cdl_090_prelock_committed_phase_1372`
**Non-ratification token:** `cdl_090_not_ratified_phase_1372`
**Scope-lock token:** `cdl_090_scope_constants_locked_phase_1372`
**Basis:** `cdl_090_identity_bootstrap_opened_phase_1371`

---

## 1. Prelock Statement

Phase 1372 prelocks CDL-090 by resolving the Phase 1371 identity-bootstrap
opening questions and locking the scope constants for Phase 1373 ratification.
CDL-090 remains open and not ratified. This phase does not mutate the CDL
register, does not implement runtime code, does not create an identity artifact,
does not generate or store secret material, does not activate public identity,
and does not authorize public claimability or wallet/value-path behavior.

```text
cdl_090_prelock_committed_phase_1372
cdl_090_not_ratified_phase_1372
cdl_090_scope_constants_locked_phase_1372
```

---

## 2. Authority Inputs

| Authority | Binding for CDL-090 |
| --- | --- |
| ADR-0038 Agent Birth Attestation | Requires Genesis-rooted identity-origin proof, non-custodial default, secure output target, no-stdout secret emission, and private-graph entropy exclusion. |
| ADR-0037 Genesis Canonical Lineage Contract | Supplies the signed Genesis lineage anchor and deterministic proof path back to signed Genesis v0.1. |
| CDL-042 Agent Identity Namespace | Supplies the globally flat `agent_id` namespace and rejects operator-scoped, epoch-scoped, registry-issued, or runtime-discretionary identity namespaces. |
| CDL-069 PQ Identity Root and Epoch Endorsement | Supplies the Genesis-forward identity-seed derivation path: `agent_id = sha384("ilc-agent-id-v1:" || identity_seed)`. |
| Phase 587 Public Identity Boundary | Confirms local identity existence is not public activation or public write-path authority. |

---

## 3. Terminology Lock

| Term | Meaning |
| --- | --- |
| `identity_seed` | Secret seed material for deriving the public `agent_id` under CDL-069. It is never public artifact content and is never written to stdout, logs, docs, walkthroughs, STATUS, chat transcripts, terminal scrollback, or environment dumps. |
| `agent_id` | Public protocol identity material derived under CDL-042/CDL-069. A local `agent_id` may exist without public activation. |
| `secure_output_target_ref` | Non-secret descriptor proving where secret material was written. It references a secure target without revealing seed, mnemonic, private-key, recovery-seed, recovery-share, vault secret, or access credential material. |
| `identity_bootstrap_attestation` | Non-secret canonical birth-attestation payload and signature envelope binding `agent_id`, identity-seed commitment reference, Genesis lineage anchor, ceremony mode, custody statement, and secure-output target reference. |
| `environment_class` | Explicit artifact label: `production_public_candidate`, `devnet_non_authoritative`, `test_fixture_non_authoritative`, or `local_private_non_authoritative`. |
| `prelock` | A deliberation record that resolves open questions and locks scope constants for ratification. It is not ratification. |

---

## 4. Phase 1371 Questions Resolved

| Q | Resolution | Scope constant locked |
| --- | --- | --- |
| Q1 secure-store format / secure-output target | A conforming bootstrap must write secret material only to an approved secure output target and must emit only a non-secret `secure_output_target_ref`. Approved production target classes are `os_keychain`, `hardware_secure_element`, `hardware_wallet`, `encrypted_local_vault`, `operator_secret_manager`, and `offline_cold_storage_record`. `test_fixture_ephemeral_store` is allowed only for non-production environment classes. | `secure_output_target_contract_v1` |
| Q2 recovery and rotation policy | The `identity_seed` is the non-rotating origin for `agent_id`; rotating it creates a new identity, not recovery of the old one. Root signing keys, operational signing keys, recovery commitments, and endorsed epoch keys may rotate only by signed recovery or rotation receipts linked to the original birth attestation and the same `agent_id`. Recovery material follows the same secure-output and no-stdout rules as the identity seed. | `identity_seed_non_rotating_agent_id_origin_v1` and `recovery_rotation_receipt_chain_v1` |
| Q3 agent-mode output contract | Agent-mode ceremony is valid only when it preserves non-custodial control, writes secrets to an approved secure output target, emits no secret material to stdout/logs/docs/chat/env dumps, and produces a non-secret receipt suitable for audit. Agent-mode is not permission for server custody. Devnet/test agent-mode outputs must carry non-authoritative labels. | `agent_mode_no_secret_stdout_output_contract_v1` |
| Q4 canonical attestation serialization and signature envelope | The attestation payload must be canonical JSON with deterministic key ordering, compact separators, and non-finite numeric rejection. The signature envelope signs the canonical payload under domain `ilc-identity-bootstrap-attestation-v1` using the identity root or a CDL-090-authorized birth signing mechanism bound to the same identity seed path. | `identity_bootstrap_attestation_envelope_v1` |
| Q5 mandatory, optional, and forbidden fields | Section 6 locks mandatory, optional, and forbidden fields. Secret material is forbidden in all public or non-secret artifacts. | `identity_bootstrap_public_artifact_field_contract_v1` |
| Q6 production/devnet/test/local-private distinction | Every artifact must declare `environment_class`. Only `production_public_candidate` may be evaluated by a later public-identity activation gate. Devnet, test fixture, and local/private artifacts are non-authoritative and cannot be mistaken for public identity authority. | `identity_bootstrap_environment_class_v1` |

No Phase 1371 question remains unresolved for Phase 1373, except the separate
ratification decision itself.

---

## 5. Locked Scope Constants

| Constant | Locked value |
| --- | --- |
| `agent_id_derivation_contract` | CDL-069 derivation remains active for Genesis-forward agents: `agent_id = sha384("ilc-agent-id-v1:" || identity_seed)`. CDL-090 does not reopen CDL-042 namespace law or CDL-069 derivation authority. |
| `secure_output_target_contract_v1` | A secure output target is required before any conforming identity bootstrap claim. The public/non-secret reference must identify target class, custody model, environment class, and receipt/proof reference without exposing secrets. |
| `approved_production_secure_target_classes` | `os_keychain`, `hardware_secure_element`, `hardware_wallet`, `encrypted_local_vault`, `operator_secret_manager`, `offline_cold_storage_record`. |
| `non_production_only_secure_target_classes` | `test_fixture_ephemeral_store`, valid only when `environment_class` is `devnet_non_authoritative` or `test_fixture_non_authoritative`. |
| `no_stdout_secret_emission_rule` | Seed, mnemonic, private-key, recovery-seed, recovery-share, Shamir-share, vault secret, secret-manager credential, and equivalent secret material must not be written to stdout, stderr, logs, docs, walkthroughs, STATUS entries, chat transcripts, terminal scrollback, environment dumps, or public artifacts. |
| `private_graph_entropy_exclusion_rule` | Private graph content, semi-private shard content, private research branches, private claim text, private provenance, local MemPalace retrieval text, chat history, local wallet history, and other private knowledge artifacts must not be identity-seed entropy or recovery material. |
| `non_custodial_default_rule` | Controller custody is the default. Server custody, provider seed escrow, verifier-service custody, wallet-provider custody, hosted harness custody, or public package distributor custody is prohibited as the default path. Any future custodial or managed-recovery option requires later explicit ADR or CDL authority and must be opt-in and disclosed. |
| `identity_seed_non_rotating_agent_id_origin_v1` | The original `identity_seed` is the identity-origin secret for the `agent_id`. It is not rotated in place. Loss recovery or key rotation preserves identity only through signed receipts linked to the original birth attestation and same `agent_id`. |
| `recovery_rotation_receipt_chain_v1` | Rotation or recovery receipts must bind `agent_id`, prior public key or commitment reference, successor public key or commitment reference, original birth-attestation reference, authorization proof reference, environment class, and signature reference. They must not contain recovery secrets. |
| `agent_mode_no_secret_stdout_output_contract_v1` | Agent-mode output consists only of non-secret attestation and receipt material. It must declare the secure output target reference, custody statement, environment class, and no-secret-output statement. |
| `identity_bootstrap_attestation_envelope_v1` | The attestation payload uses canonical JSON. Any implementation later producing machine artifacts must serialize with deterministic key ordering and reject non-finite numeric values before signing or hashing. |
| `identity_bootstrap_environment_class_v1` | Valid values are `production_public_candidate`, `devnet_non_authoritative`, `test_fixture_non_authoritative`, and `local_private_non_authoritative`. Non-production classes cannot grant public authority. |

---

## 6. Public Artifact Field Contract

### Mandatory fields

| Field | Requirement |
| --- | --- |
| `attestation_version` | Stable format label, initially `identity_bootstrap_attestation_v1`. |
| `agent_id` | Public agent identifier derived under CDL-042/CDL-069. |
| `agent_id_derivation_ref` | Reference to CDL-042 and CDL-069 derivation authority. |
| `identity_seed_commitment_ref` | Non-secret commitment reference. It must not reveal the seed. |
| `genesis_lineage_anchor` | Signed Genesis/Atlas lineage anchor tracing to ADR-0037. |
| `lineage_proof_ref` | Reference to the proof bundle or verifiable lineage proof. |
| `ceremony_mode` | Either `interactive` or `agent_mode`. |
| `secure_output_target_ref` | Non-secret reference to the approved secure output target. |
| `environment_class` | One of the four locked environment classes. |
| `entropy_source_statement` | Non-secret statement that approved randomness was used and private graph content was excluded. |
| `custody_statement` | Non-secret statement that the bootstrap follows the non-custodial default. |
| `no_secret_output_statement` | Statement that no secret material was emitted to forbidden output paths. |
| `artifact_authority_scope` | Statement that the artifact is not public activation, not public write authority, and not public claimability. |
| `attestation_signature_ref` | Reference to the signature over the canonical attestation payload. |

### Optional fields

| Field | Constraint |
| --- | --- |
| `hardware_attestation_ref` | Non-secret reference only; no device unlock secret or seed material. |
| `recovery_commitment_ref` | Non-secret recovery commitment only; no recovery seed or share. |
| `operator_disclosure_ref` | Optional non-secret custody/operation disclosure. |
| `test_fixture_ref` | Allowed only for `devnet_non_authoritative` or `test_fixture_non_authoritative`. |
| `local_private_scope_ref` | Allowed only for `local_private_non_authoritative`; it does not create public authority. |

### Forbidden fields and payload fragments

The following are forbidden in any public or non-secret identity bootstrap
artifact:

1. Plaintext identity seed.
2. Mnemonic.
3. Private key.
4. Recovery seed.
5. Recovery share or Shamir share.
6. Vault unlock secret.
7. Secret-manager credential.
8. Private graph content.
9. Semi-private shard content.
10. Chat transcript.
11. MemPalace retrieval text.
12. Wallet history.
13. Environment variable dump.
14. Terminal scrollback.
15. Any stdout or log fragment containing secret material.

---

## 7. Canonical Attestation Envelope

The Phase 1373 ratification evidence may refine exact schema wording, but it
must preserve this envelope shape:

```json
{
  "payload": {
    "agent_id": "<public-agent-id>",
    "agent_id_derivation_ref": "CDL-042/CDL-069",
    "artifact_authority_scope": "not_public_activation",
    "attestation_version": "identity_bootstrap_attestation_v1",
    "ceremony_mode": "interactive|agent_mode",
    "custody_statement": "<non-secret-non-custodial-statement>",
    "entropy_source_statement": "<non-secret-entropy-statement>",
    "environment_class": "production_public_candidate|devnet_non_authoritative|test_fixture_non_authoritative|local_private_non_authoritative",
    "genesis_lineage_anchor": "<signed-genesis-lineage-anchor-ref>",
    "identity_seed_commitment_ref": "<non-secret-commitment-ref>",
    "lineage_proof_ref": "<lineage-proof-ref>",
    "no_secret_output_statement": "<non-secret-output-statement>",
    "secure_output_target_ref": "<non-secret-secure-target-ref>"
  },
  "signature": {
    "domain": "ilc-identity-bootstrap-attestation-v1",
    "signature_algorithm_ref": "<cdl-069-or-cdl-090-authorized-signature-ref>",
    "signature_key_ref": "<public-key-or-key-commitment-ref>",
    "signature_ref": "<signature-ref-over-canonical-payload>"
  }
}
```

The signature covers the canonical `payload` object. Canonical JSON means
deterministic key ordering, compact separators, and no non-finite numeric
values. Secret material is never part of the signed public payload.

---

## 8. Environment-Class Consequences

| Environment class | Consequence |
| --- | --- |
| `production_public_candidate` | May be evaluated by a later public-identity activation or admission gate. It is not public activation by itself. |
| `devnet_non_authoritative` | Suitable for devnet testing only. It must not be used as public identity authority. |
| `test_fixture_non_authoritative` | Suitable for tests only. It must not be used as public identity authority. |
| `local_private_non_authoritative` | Suitable for local/private use only. It does not grant public write-path authority, public claimability, settlement authority, or public reputation authority. |

---

## 9. Rejected Candidates

The following candidates remain rejected:

1. Default custodial identity bootstrap.
2. Provider-controlled seed escrow as an undisclosed default.
3. Private graph content or private research output as identity-seed entropy.
4. Private graph content or private research output as recovery material.
5. Stdout, stderr, logs, docs, walkthroughs, STATUS entries, chat transcripts,
   terminal scrollback, or environment dumps as valid secret output paths.
6. Operator-scoped, epoch-scoped, registry-issued, or runtime-discretionary
   identity namespaces replacing CDL-042/CDL-069.
7. Treating a local `agent_id` or local identity artifact as public activation.
8. Treating devnet, test fixture, or local/private bootstrap artifacts as public
   identity authority.

---

## 10. Non-Goals And Non-Claims

This prelock does not:

1. Ratify CDL-090.
2. Mutate the CDL register.
3. Open CDL-088.
4. Create an identity artifact.
5. Generate an identity seed.
6. Generate a mnemonic, private key, recovery seed, recovery share, or Shamir share.
7. Write a secret store.
8. Activate public identity.
9. Activate public claimability.
10. Activate public API behavior, wallet behavior, ECU behavior, ILC settlement,
    validator behavior, rewards, treasury behavior, production minting, production
    mining, or public RC publication.
11. Modify `ilc_core/`.

Phase 1373 ratification remains required before CDL-090 can be marked ratified:

```text
cdl_090_not_ratified_phase_1372
```

