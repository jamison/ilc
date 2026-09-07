# ILC Genesis Invite-Issuer Delegation Schema

**Phase:** GAP-GENESIS-INVITE-ISSUER-00
**Schema version:** `genesis_invite_issuer_delegation.v0.1`
**Date:** 2026-09-07
**Network:** `public-rc`

## Purpose

This schema defines the public delegation record by which Genesis Agent 01
delegates public-RC invite shortcode issuance to a dedicated BLS12-381 G1 key.
The delegated key is purpose-scoped to relay-hosted invite code issuance and
must not be reused as a validator hot key, relay-bootstrap capsule key, wallet
key, or general Genesis identity key.

Genesis Agent 01 is identified by the Phase 838a PQ identity record at
`docs/genesis/genesis_agent1_pubkey_record_838a.txt`. That record contains the
canonical `mldsa_pk_hex` used to verify this delegation. Phase 1431 identity
material is historical private rehearsal context only and is not public-RC
authority for this delegation.

## Field Schema

| Field | Type | Semantics |
| --- | --- | --- |
| `invite_issuer_pk_hex` | str | Dedicated BLS12-381 G1 compressed public key, 96 lowercase hex chars. |
| `role` | str | Must be `genesis_delegate_invite_issuer_v1`. |
| `network_id` | str | Must be `public-rc`. |
| `epoch_scope` | str | Must be `epoch_0_and_beyond`. |
| `issuance_limits` | object | Machine-checkable limits: `max_batch_size`, `max_total_batches`, and `limit_authority_status`. Null numeric limits mean governance-pending, not unbounded protocol law. |
| `revocation_policy` | str | Must be `genesis_revocable`. Genesis may publish a signed revocation record. |
| `shortcode_authority_scope` | str | Must be `public_rc_validator_bootstrap`. |
| `bls_sign_dst` | str | Primary bundle-authenticity DST: `ILC_RELAY_INVITE_BUNDLE_V1_BLS12381G2_XMD:SHA-256_SSWU_RO_`. |
| `relay_store_request_dst` | str | Associated relay upload/request DST: `ILC_RELAY_INVITE_STORE_V1_BLS12381G2_XMD:SHA-256_SSWU_RO_`. |
| `genesis_agent_cid` | str | Canonical Genesis Agent 01 CID from Phase 838a. |
| `delegation_sig_hex` | str | ML-DSA-65 signature by Genesis Agent 01 over the canonical signed payload. |
| `delegation_sig_scheme` | str | Must be `mldsa`. |
| `delegation_signed_date` | str | Ceremony date in ISO `YYYY-MM-DD` form. |
| `phase` | str | Must be `GAP-GENESIS-INVITE-ISSUER-00`. |
| `phase_tokens` | list[str] | Phase completion tokens. Excluded from signed payload. |

## Signed Payload Boundary

The ML-DSA signed payload is the canonical JSON object containing every field
except `delegation_sig_hex` and `phase_tokens`.

Canonical serialization:

```text
json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
```

The `delegation_sig_hex` field is excluded because it is the signature being
produced. The `phase_tokens` field is excluded because it records phase-status
metadata rather than delegated authority state.

## Required Invariants

- `invite_issuer_pk_hex` must not equal `GENESIS_CAPSULE_SIGNING_PK_HEX`.
- `invite_issuer_pk_hex` must not equal any public-RC validator AgentID.
- No private key, seed, mnemonic, or secret material may appear in the committed
  delegation record.
- `GENESIS_INVITE_ISSUER_PK_HEX` must not be added to `ilc_core/` in this
  phase; runtime wiring belongs to GAP-PUBLIC-RC-INVITE-00b.
- The delegated key authorizes shortcode invite-bundle authenticity signing
  under `ILC_RELAY_INVITE_BUNDLE_V1_BLS12381G2_XMD:SHA-256_SSWU_RO_`.
- The same key may authenticate relay store requests under
  `ILC_RELAY_INVITE_STORE_V1_BLS12381G2_XMD:SHA-256_SSWU_RO_` only for this
  shortcode issuance role.

## Revocation

Genesis may revoke this delegation by publishing a record containing:

```json
{
  "revocation_of": "<sha256-or-path-ref-of-delegation-record>",
  "revocation_sig_hex": "<Genesis Agent 01 ML-DSA signature>",
  "delegation_sig_scheme": "mldsa",
  "revocation_date": "<YYYY-MM-DD>"
}
```

Revocation does not retroactively alter already redeemed invite nullifiers. It
does prevent future acceptance of new store requests or bundle-authenticity
signatures under the revoked key once runtime wiring consumes revocation state.

## Non-Claims

- No invite enforcement is activated by this schema.
- No invite shortcodes are issued by this schema.
- No LMDB, validator, epoch, settlement, minting, public mirror, or runtime
  guard mutation is authorized by this schema.
- No Genesis Agent 01 BLS signing capability is implied.
