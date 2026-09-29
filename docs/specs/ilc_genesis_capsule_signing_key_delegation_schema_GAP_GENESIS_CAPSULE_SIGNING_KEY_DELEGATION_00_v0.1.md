# ILC Genesis Capsule Signing Key Delegation Schema

**Phase:** GAP-GENESIS-CAPSULE-SIGNING-KEY-DELEGATION-00
**Schema version:** `genesis_capsule_signing_key_delegation.v0.1`
**Date:** 2026-09-29
**Network scope:** `all_relay_bootstrap_networks`

## Purpose

This schema defines the public delegation record by which Genesis Agent 01
authorizes the dedicated BLS12-381 G1 key used for relay-bootstrap capsule
signing.

The delegated key is purpose-scoped to relay-bootstrap capsule signing only. It
must not be reused as a validator hot key, public submit ingress key, invite
issuer key, wallet key, release key, or general Genesis identity key.

Genesis Agent 01 is identified by the Phase 838a PQ identity record at
`docs/genesis/genesis_agent1_pubkey_record_838a.txt`. That record contains the
canonical `mldsa_pk_hex` used to verify this delegation.

## Field Schema

| Field | Type | Semantics |
| --- | --- | --- |
| `capsule_signing_pk_hex` | str | Dedicated BLS12-381 G1 compressed public key, 96 lowercase hex chars. Must equal `GENESIS_CAPSULE_SIGNING_PK_HEX`. |
| `role` | str | Must be `genesis_delegate_capsule_signing_v1`. |
| `purpose` | str | Must be `relay_bootstrap_capsule_signing`. |
| `network_scope` | str | Must be `all_relay_bootstrap_networks`. |
| `revocation_policy` | str | Must be `genesis_revocable`. Genesis may publish a signed revocation record. |
| `genesis_agent_cid` | str | Canonical Genesis Agent 01 CID from Phase 838a. |
| `delegation_sig_hex` | str | ML-DSA-65 signature by Genesis Agent 01 over the canonical signed payload. |
| `delegation_sig_scheme` | str | Must be `mldsa`. |
| `delegation_signed_date` | str | Ceremony date in ISO `YYYY-MM-DD` form. |
| `phase` | str | Must be `GAP-GENESIS-CAPSULE-SIGNING-KEY-DELEGATION-00`. |
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

- `capsule_signing_pk_hex` must equal `GENESIS_CAPSULE_SIGNING_PK_HEX`.
- `capsule_signing_pk_hex` must not equal `GENESIS_AGENT1_AGENT_ID`.
- `capsule_signing_pk_hex` must not equal
  `GENESIS_PUBLIC_SUBMIT_INGRESS_BLS_PK_HEX`.
- `capsule_signing_pk_hex` must not equal the Genesis invite issuer key.
- `capsule_signing_pk_hex` must not equal any public-RC validator AgentID.
- No private key, seed, mnemonic, or secret material may appear in the committed
  delegation record.
- The delegated key authorizes only the relay-bootstrap capsule signing role
  named in this schema. It does not become a general Genesis AgentID, wallet key,
  submit ingress key, release key, or validator key.

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

Revocation prevents future acceptance of new relay-bootstrap capsules under the
revoked key once runtime wiring consumes revocation state. It does not rewrite
already committed phase records.

## Non-Claims

- No guard is cleared by this schema.
- No relay-bootstrap capsule is generated or changed by this schema.
- No Atlas LMDB write is authorized by this schema.
- No validator, epoch, settlement, minting, package, public mirror, or mainnet
  mutation is authorized by this schema.
- No Genesis Agent 01 BLS signing capability is implied.
