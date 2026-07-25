# ILC Canonical Intent Payload Envelope Spec 1578c v0.1

**Phase:** 1578c / GAP-WALLET-02a  
**Date:** 2026-07-25  
**Status:** committed preflight spec / no runtime activation  
**Sensitivity:** NON-SENSITIVE

## 1. Purpose

This spec defines the pre-RC canonical ILC intent payload envelope. The envelope is the single ILC-native signing preimage for future wallet-facing actions. EIP-712, COSE Sign1, and bare-key signatures are adapter projections over that canonical object; none of them is the protocol-canonical representation.

This phase writes no runtime code and activates no signer, transfer, spend, withdrawal, claimability, minting, settlement, or wallet write path.

## 2. Design Rationale

ILC remains wallet-agnostic by making the ILC-native object authoritative and treating external wallet formats as projections. This avoids three failure modes:

| Failure mode | Design response |
|--------------|-----------------|
| Wallet address becomes the account anchor | `agent_id` remains the account anchor; external signing keys are later signer bindings |
| EIP-712 and COSE signatures authorize different payloads | Each adapter must decode to the same canonical intent digest |
| Testnet, stale epoch, or profile replay | The domain separator includes ILC domain, network, epoch binding, schema version, and chain/profile identifier |

The design follows wallet lane decision 6 in `docs/specs/ilc_wallet_lane_forward_plan_pre_rc_v0.1.md:86-120`, and the 1578b no-conflict finding in `docs/specs/ilc_wallet_canon_reconciliation_1578b_v0.1.md:47-52`.

## 3. Canonical Serialization

For this pre-RC envelope, the canonical preimage is UTF-8 JSON bytes produced with:

| Parameter | Required value |
|-----------|----------------|
| Key order | Lexicographic key order |
| Separators | `(",", ":")` |
| Unicode | No escaping requirement beyond valid UTF-8 JSON; hashed bytes are exactly the emitted UTF-8 bytes |
| Floating point | Forbidden; JSON encoder must reject NaN/Infinity with `allow_nan=False` |
| Numeric amounts | Decimal strings only; no JSON float or binary float |
| Digest | `sha256:<64 lowercase hex>` over the canonical JSON bytes |

This is a pre-RC wallet-intent rule only. It does not change existing DAG-CBOR/CIDv1 commitment rules for protocol bundles, graph nodes, or epoch state roots.

## 4. Canonical Intent Object Schema

| Field | Required | Type | Semantics |
|-------|----------|------|-----------|
| `intent_schema_version` | yes | string literal | `ilc.intent.v1` |
| `domain` | yes | string literal | `ILC_CANONICAL_INTENT` |
| `network_id` | yes | string | ILC network identifier, for example `ilc-pre-rc-private` or future public network identifier |
| `chain_profile_id` | yes | string | ILC chain/profile identifier; distinct from external wallet chain id |
| `epoch_binding` | yes | object | Epoch number plus root reference or pending epoch marker that binds the signature to a time/state domain |
| `agent_id` | yes | string | ILC-native account anchor for the actor whose intent is being signed |
| `nonce` | yes | integer | Per-`agent_id` wallet-action nonce; starts at `0` for newly enrolled accounts |
| `intent_type` | yes | string enum | `claimability_proof_request`, `signer_binding_request`, `wallet_query_authorization`, or future `value_transfer_request` after separate authority |
| `intent_body` | yes | object | Type-specific payload. For pre-RC, must not contain transfer, spend, withdrawal, or external destination authority unless a later phase authorizes that type |
| `expiry_epoch` | optional | integer | Last epoch for which this intent may be accepted |
| `delegation_record_hash` | optional | `sha256:<hex>` | Required only for operator-signed actions once operator delegation is authorized |
| `signer_binding_ref` | optional | string | Reference to later signer-binding record; not valid until Phase 1578d or successor authorizes it |
| `created_by` | optional | string | Local display metadata; not an authority field |

`intent_body` is intentionally opaque at this layer but must be canonical JSON and must obey the no-float rule. Later phases must define per-`intent_type` field schemas before any value-action or submission runtime can accept those intents.

## 5. Domain Separator

The domain separator is the ordered tuple:

| Component | Source field | Purpose |
|-----------|--------------|---------|
| ILC domain string | `domain` | Separates ILC intents from non-ILC messages |
| Network identifier | `network_id` | Blocks cross-network replay |
| Epoch binding | `epoch_binding` | Blocks stale-epoch and wrong-state replay |
| Intent schema version | `intent_schema_version` | Blocks schema-confusion replay |
| Chain/profile identifier | `chain_profile_id` | Separates public RC, private testbed, sidecar profile, and future chain profiles |

Adapters may include additional wallet-native domain fields, but they must not omit or reinterpret these five ILC fields.

## 6. Adapter Projections

| Adapter | Projection rule | Required equivalence check | Adapter-specific fields allowed |
|---------|-----------------|----------------------------|--------------------------------|
| EIP-712 | Map the canonical object into typed data with the five ILC domain fields in the EIP-712 domain or primary message; string fields stay strings; Decimal amounts stay strings | Recover typed data, reconstruct canonical intent JSON, compute digest, and compare to claimed canonical digest | EVM `chainId`, verifying-contract placeholder, wallet address, UI label; none may alter canonical fields |
| COSE Sign1 | Protected headers record algorithm, key id policy, content type `application/ilc-intent+json`, and profile id; payload bytes are the canonical JSON bytes | Verify COSE payload bytes hash directly to the canonical digest | COSE algorithm id, protected `kid` when privacy policy permits, certificate chain refs |
| Bare-key | Sign the canonical digest or canonical JSON bytes with an ILC-native key according to the selected verifier | Verify signature against the enrolled ILC identity or authorized delegated signer and compare canonical digest | Algorithm id, public key ref, verifier profile |

The adapter verifier rule is strict: a signature is valid only if the adapter-specific presentation decodes to the exact canonical object and canonical digest. If decoding is lossy, ambiguous, or changes field types, the signature must be rejected.

## 7. Replay Prevention Integration

| Replay domain | Mechanism | Source |
|---------------|-----------|--------|
| Wallet-facing actions | Per-`agent_id` monotonic nonce; newly enrolled accounts start at `0` | `docs/specs/ilc_wallet_lane_forward_plan_pre_rc_v0.1.md:74-84`; `docs/specs/ilc_agent_identity_enrollment_spec_1578a_v0.1.md:53-59` |
| Rust / consensus object updates | Object-version certificate replay model; do not replace with wallet nonce | `docs/specs/ilc_wallet_lane_forward_plan_pre_rc_v0.1.md:76-80` |
| Claimability and duplicate claims | Nullifier registry and duplicate-claim checks | `ilc_core/sidecars/claim_nullifier_registry_v1.py:14-23`; `ilc_core/sidecars/claim_nullifier_registry_v1.py:87-121`; `ilc_core/sidecars/claim_nullifier_registry_v1.py:199-244` |

Wallet nonces do not replace claimability nullifiers. Claimability nullifiers do not authorize general value transfers. Object-version certificates remain the consensus-side replay mechanism.

## 8. Current Runtime Boundary

`ilc_core/protocol/public_wallet_runtime.py` has read-only wallet status, history, export, summary, and snapshot surfaces, but no canonical signing envelope or submission path. `ilc_core/sidecars/wallet_action_semantics_preflight.py:54-71` keeps signer binding, wallet transfer, wallet spend, wallet withdrawal, wallet provider signing, ledger write, and public claimability authorization flags false.

This spec is therefore a preflight contract for later phases, not an active runtime feature.

## 9. Non-Activation Statement

This phase does not activate any signing adapter, bind any external signer key to an `agent_id`, enable transfer/spend/withdrawal, enable wallet-provider signing, write wallet state, open or amend any CDL, clear any guard, mint ECU or ILC, settle economics, publish a public mirror, or activate public RC.

## 10. Output Tokens

- `canonical_payload_envelope_spec_committed_phase_1578c`
- `eip712_cose_adapter_projection_design_recorded_phase_1578c`
- `domain_separator_fields_specified_phase_1578c`
