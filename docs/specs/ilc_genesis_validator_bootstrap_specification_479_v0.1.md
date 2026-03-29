# ILC Genesis Validator Bootstrap Specification 479 v0.1

Status: specification only
Date: 2026-03-29
Owner lane: G8 Constitution Cluster A

No ilc_core/ implementation occurs in Phase 479.
No decision-log mutation occurs in Phase 479.

## 1. Signing key format

Ed25519 is the required signing algorithm for genesis validator identity.

Signing key contract:
- public key format: Ed25519 public key, 32 bytes,
- public key encoding: base64url string,
- validator_id derivation input: decoded public-key bytes,
- validator_id is derived from the public key using the CDL-042 key-derivation method.

## 2. Enrollment record structure

Required fields:
- `validator_id` (str, key-derived),
- `public_key_b64url` (str),
- `cluster_id` (str),
- `vote_weight` (positive int),
- `epoch_zero` (int, must be 0),
- `enrolled_by` (str, genesis authority identifier).

Optional fields:
- `display_name` (str),
- `notes` (str).

## 3. Epoch-zero state record format

Required fields:
- `epoch` (int, must be 0),
- `genesis_block_cid` (str),
- `quorum_record_seed` (str),
- `validator_set_hash` (str).

The epoch-zero record is the deterministic bootstrap state consumed by the runtime phases.

## 4. Key-loading ceremony protocol

The key-loading ceremony protocol defines the human-operator procedure for genesis validator enrollment.

1. Generate an Ed25519 key pair offline.
2. Extract the public key and encode it as base64url.
3. Derive `validator_id` using the CDL-042 key-derivation method.
4. Construct the enrollment record.
5. Deliver the enrollment record for bundle assembly.
6. Verify the returned epoch-zero state record before accepting activation.

Human-facing ceremony tooling is planned for tools/, while deterministic verification runtime lives under ilc_core/genesis/.

Private key management, hardware security module integration, and threshold signatures are out of scope for Phase 479.

## 5. Admission-control pre-population bundle format

The pre-population bundle contains:
- the list of enrollment records,
- the epoch-zero state record,
- a bundle integrity hash.

No admission-control runtime enforcement occurs in Phase 479. That work is deferred to
Phase 481.

## 6. Key material preparation checklist

- [ ] Generate and retain the Ed25519 private key offline.
- [ ] Export the Ed25519 public key in base64url form.
- [ ] Record the derived `validator_id`.
- [ ] Record the assigned `cluster_id`.
- [ ] Record the assigned `vote_weight`.
- [ ] Prepare the enrollment record with `epoch_zero = 0`.
- [ ] Prepare a local verification copy of the returned epoch-zero state record.

## 7. Out-of-scope items and Phase 480 pointer

Validator network join and recovery flow is out of scope for this bootstrap specification.

Private key management, hardware security module integration, and threshold signatures are out of scope for Phase 479.

Phase 480 is the next authorized phase.
