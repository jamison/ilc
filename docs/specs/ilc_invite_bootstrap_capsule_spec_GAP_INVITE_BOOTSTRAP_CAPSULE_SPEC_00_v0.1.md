# ILC Invite Bootstrap Capsule Spec GAP-INVITE-BOOTSTRAP-CAPSULE-SPEC-00 v0.1

## 1. Metadata

| Field | Value |
|-------|-------|
| Phase | GAP-INVITE-BOOTSTRAP-CAPSULE-SPEC-00 |
| Date | 2026-08-30 |
| Status | committed-spec-candidate |
| Sensitivity | NON-SENSITIVE |
| Runtime activation | none |
| CDL mutation | none |
| Output token | `invite_bootstrap_capsule_spec_complete_GAP_INVITE_BOOTSTRAP_CAPSULE_SPEC_00` |

This phase defines the pre-RC invite bootstrap capsule extension. It does not
modify runtime code, mutate an invite bundle implementation, open or amend a
CDL, activate public P2P, or grant validator authority.

## 2. Source Authorities

| Authority | Constraint used here |
|-----------|----------------------|
| CDL-103 | Signed `PeerAdvertisement` records, `MAX_TTL_EPOCHS = 4`, `DEFAULT_INTRODUCTION_SET_SIZE = 8`, digest-only `installed_slices_digest`, no validator or economic authority from advertisements. |
| GAP-CONNECTIVITY-RECONCILE-00 | Connectivity modes are receipts, not authority; relay reachability does not create validator admission. |
| GAP-AGENT-ONBOARDING-00d | Invite redemption is bound to AgentID proof-of-possession and invite nullifier persistence. |
| CDL-105 | Validator operational surface registration is a separate endpoint/certificate assertion authority and is not created by this capsule. |
| CDL-107 | Reputation gates eligibility, not ECU payout magnitude; invite connectivity metadata must not become an ECU multiplier. |
| ADR-0020 | Long-term target is knowledge-node-first and homoiconic distribution, while keeping the genesis layer minimal and non-circular. |

## 3. Existing Invite Bundle Baseline

The current CLI invite bundle builder emits the following fields:

| Field | Meaning |
|-------|---------|
| `atlas_slice_manifest_witness` | Portable manifest witness verified before materialization. |
| `intended_epoch` | Epoch intended for install bootstrap. |
| `intended_profile` | Install profile string. |
| `invite_batch_record` | Public invite batch record. |
| `invite_id` | Batch-derived invite identifier. |
| `nonce_membership_proof` | Merkle membership proof for the selected nonce. |
| `private_invite_nonce` | One private invite nonce for this bundle. |
| `starmap_manifest_payload` | Starmap payload materialized by the installer. |

The extension in this spec appends fields to that bundle. It does not replace
the current invite nullifier, proof-of-possession, starmap, or manifest witness
checks.

## 4. New Capsule Fields

### 4.1 `known_peer_hints`

`known_peer_hints` is an optional list of at most 8 signed CDL-103
`PeerAdvertisement` records selected from the inviter's verified known-peer
table.

Validation requirements:

| Rule | Required behavior |
|------|-------------------|
| Type and cap | Value must be a list; length greater than 8 is a hard stop with a stable error token. |
| Schema | Each element must parse as `PeerAdvertisement.from_dict(...)`. |
| Signature | A hint is usable only after ML-DSA-65 signature verification succeeds against a resolved key binding. |
| TTL | A hint is usable only if `ttl_epochs <= 4`, `peer_timestamp_epoch <= current_epoch + 1`, and the advertisement is not expired at `current_epoch`. |
| Private address literals | Public validation keeps private address literals forbidden except for explicit testnet fixtures. |
| Deduplication | Implementation should deduplicate by `(agent_id, transport_endpoint)` and retain deterministic order. |
| Invalid hint disposition | Malformed list shape or count overflow is a hard stop; individual expired, unverifiable, or stale hints are dropped and reported in install evidence without blocking install. |

`known_peer_hints` are transport hints only. They do not create peer-table root
authority, validator admission, serving credit, economic credit, wallet
authority, or public sidecar activation. They also do not supersede static
Genesis-signed bootstrap seeds.

### 4.2 `genesis_state_root`

`genesis_state_root` is a required string in the extended capsule. It carries the
immutable Genesis domain anchor that the invitee must compare against the
hardcoded constitutional root in the installed package.

Pre-RC binding:

```text
genesis_state_root == ilc_core.identity.first_run_provisioning.GENESIS_ROOT_ENVELOPE_HASH
```

Mismatch is a hard stop before peer hints are trusted, install materialization is
claimed, or bilateral receipt evidence is emitted. This field is not a mutable
runtime state hash, epoch state root, package hash, LMDB root, or mirror head.

### 4.3 `inviter_connectivity_mode`

`inviter_connectivity_mode` is an optional string carrying the inviter's
`ConnectivityMode` at invite-generation time.

It is informational only. It may help the invitee choose whether to try direct
peer hints, relay, or bootstrap fetch first. It must not affect validator
eligibility, reputation, ECU generation, invite validity, or install success.

## 5. Bilateral Install Receipt

The pre-RC bilateral receipt is a receipt pair, not a synchronous authority
handshake required to finish local install.

### 5.1 Invitee Install Receipt

After install completes, the invitee produces an `invitee_install_receipt`
signed by the newly provisioned AgentID key over canonical JSON excluding the
signature field.

Required fields:

| Field | Meaning |
|-------|---------|
| `schema_version` | `invitee_install_receipt.v0.1` |
| `signature_domain` | Domain string for invitee install receipt signatures. |
| `agent_id` | New invitee AgentID. |
| `invite_id` | Invite identifier consumed by this install. |
| `invite_nullifier` | Redeemed invite nullifier or hash reference. |
| `software_version` | Installed `ilc-core` package version. |
| `installed_release_artifact_id` | Release artifact identifier, if available. |
| `installed_release_canonical_hash` | Verified artifact hash or manifest hash. |
| `genesis_state_root` | Genesis root accepted by the installer. |
| `connectivity_mode` | Connectivity mode recorded at install time. |
| `connectivity_receipt_sha384` | SHA-384 of the local connectivity receipt when present. |
| `onboarding_receipt_sha384` | SHA-384 of the local onboarding receipt. |
| `install_epoch` | Epoch interpreted by the install bundle. |
| `created_at_unix` | Local receipt timestamp for operator diagnostics only. |
| `signature` | AgentID signature over the canonical receipt body. |

The receipt must not return private key material, raw identity seed, raw
validator IKM, raw invite nonce, or unredacted local filesystem paths to the
inviter.

### 5.2 Inviter Receipt Acknowledgment

An `inviter_receipt_ack` may later be returned by the inviter. It signs the
invitee receipt hash, accepted invite ID, inviter AgentID, and acknowledgment
epoch. The acknowledgment is optional for the local install to complete and is
not pre-RC validator admission evidence by itself.

## 6. Privacy Bounds

The invite bootstrap capsule must stay privacy-bounded:

| Boundary | Rule |
|----------|------|
| No content ID disclosure | Peer hints must not carry content IDs, file paths, CIDs, or per-content availability. CDL-103 `installed_slices_digest` remains digest only. |
| No raw peer list fallback | `known_peer_hints` must contain signed `PeerAdvertisement` records, not unsigned raw IP lists. |
| Bounded hint count | Maximum 8 hints limits graph-topology and social-neighborhood leakage. |
| Coarse connectivity only | `inviter_connectivity_mode` is a coarse enum string, not NAT details, router model, firewall state, or private LAN address. |
| No secret echo | Install receipts must not echo raw invite nonce or private key material. |

## 7. Installer Verification Order

The implementation phase should verify in this order:

1. Load invite bundle with the existing byte cap and no-float JSON parser.
2. Verify existing invite bootstrap/nullifier/proof-of-possession path.
3. Verify `genesis_state_root` equals the installed package root. Hard stop on mismatch.
4. Verify starmap payload and atlas slice witness as today.
5. Provision or reuse local identity according to existing install rules.
6. Generate onboarding and connectivity receipts.
7. Validate `known_peer_hints`; drop and report expired or unverifiable hints.
8. Seed the local discovery table with verified hints if that runtime path exists.
9. Emit invitee install receipt.

This order prevents a malicious or stale inviter from steering the install into
a counterfeit protocol root while still allowing stale peer hints to degrade
gracefully.

## 8. Non-Claims

- This phase does not modify any `ilc_core/` runtime.
- This phase does not implement `known_peer_hints`, `genesis_state_root`, or
  `inviter_connectivity_mode`.
- This phase does not amend CDL-103, CDL-105, CDL-107, or any invite CDL.
- This phase does not grant validator admission, endpoint assertion authority,
  BFT quorum weight, economic credit, reputation credit, or serving rewards.
- This phase does not activate public P2P, public sidecar serving, relay
  deployment, DHT, or central-repository removal.
- This phase does not require PyPI, GitHub, or a relay to be trusted as protocol
  authority.

## 9. Output Token

`invite_bootstrap_capsule_spec_complete_GAP_INVITE_BOOTSTRAP_CAPSULE_SPEC_00`
