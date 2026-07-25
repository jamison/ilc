# ILC Signer Binding Authority Spec 1578d v0.1

**Phase:** 1578d / GAP-WALLET-02b  
**Date:** 2026-07-25  
**Status:** committed authority spec / CDL deferred / no runtime activation  
**Sensitivity:** SENSITIVE

## 1. Purpose

This spec defines how an external signing key may become a delegated signer for an already-enrolled ILC `agent_id`. It binds wallet-agnostic signing to the ILC-native account model without making any external wallet address the account anchor.

This phase does not activate a runtime signer-binding verifier, create a binding for any real agent, clear any wallet action guard, authorize transfer, authorize spend, authorize withdrawal, authorize wallet-provider signing, write wallet state, mint ECU or ILC, settle economics, publish a public mirror, or activate public RC.

## 2. Binding Authority Model

| Concept | Rule |
|---------|------|
| Account anchor | `agent_id` is the canonical ILC account anchor. External wallet keys do not create accounts. |
| Enrollment boundary | Agent enrollment precedes signer binding. A binding is invalid unless it references an already-enrolled `agent_id`. |
| External signer role | External keys are delegated signing adapters over a canonical ILC intent object. |
| Consensus boundary | secp256k1/EIP-712 remains adapter/sidecar evidence for public RC. Direct Rust consensus verification is deferred to a later ratified SignatureSchemeRegistry CDL. |
| Wallet action boundary | Binding authority does not imply transfer, spend, withdrawal, or wallet ledger-write authority. |
| Root authority | Root identity keys remain governed by CDL-001/CDL-002/CDL-042/CDL-069 identity and lineage canon. Delegated signers may be revoked or superseded by root or precommitted policy. |

The model is consistent with the wallet lane decision that ILC is native-first and wallet-agnostic (`docs/specs/ilc_wallet_lane_forward_plan_pre_rc_v0.1.md:14-28`) and with the wallet-agnostic signing handoff that key storage is an operator concern (`docs/specs/ilc_wallet_agnostic_signing_strategy_codex_handoff_v0.1.md:12-20`, `:62-70`, `:99-107`).

## 3. SignerBindingRecord Schema

`SignerBindingRecord` is the candidate on-graph authority object for future runtime work:

| Field | Required | Semantics |
|-------|----------|-----------|
| `record_version` | yes | Literal `ilc.signer_binding_record.v0.1` until superseded |
| `agent_id` | yes | Already-enrolled ILC account anchor |
| `agent_enrollment_ref` | yes | Content/address reference to the enrollment record or admitted identity evidence |
| `external_key_type` | yes | One of `evm_secp256k1_address`, `ed25519_public_key`, `bls_public_key`, `cose_key_ref`, `hardware_wallet_ref`, or future ratified extension |
| `external_public_key_ref` | yes | Opaque public key reference or address commitment; raw private key material is forbidden |
| `external_key_fingerprint` | conditional | Domain-separated fingerprint for dedupe/audit when privacy policy permits; must not be raw public key bytes |
| `binding_scope` | yes | Explicit allowed action classes; default deny |
| `binding_epoch` | yes | Epoch at which the binding becomes visible to ILC state |
| `expiry_epoch` | optional | Last epoch in which the binding is valid |
| `revocation_policy` | yes | Root-authorized, precommitted-policy, or governance-quorum revocation route |
| `key_rotation_policy` | yes | Rotation/supersession rule that preserves `agent_id` continuity |
| `nonce_separation` | yes | Canonical wallet-action nonce is per `agent_id`; adapter-local anti-replay metadata is non-authoritative and cannot replace account nonce |
| `intent_envelope_profile` | yes | Reference to `ilc.intent.v1` canonical payload and adapter projection rules |
| `operator_delegation_ref` | conditional | Required if an operator signs for a controlled agent |
| `privacy_profile` | yes | Public projection policy for key refs, fingerprints, and delegation metadata |
| `revoked_by_ref` | optional | Superseding revocation record reference |
| `supersedes_binding_ref` | optional | Prior binding superseded by this record |
| `non_activation_flags` | yes | Machine-readable booleans proving no transfer/spend/withdrawal/wallet write was activated by the binding record |

## 4. Supported External Key Types

| Key type | Adapter projection | Binding rule | Notes |
|----------|--------------------|--------------|-------|
| EVM address / secp256k1 | EIP-712 projection over canonical ILC intent | Binding records address/fingerprint and requires verifier reconstruction of canonical digest | Adapter/sidecar evidence only for public RC |
| Ed25519 public key | Bare-key or COSE Sign1 projection | Binding records opaque public key ref and verifier profile | Suitable for simple local keys and some hardware-backed flows |
| BLS public key | Bare-key verifier profile | Binding records BLS public key ref and scope | BLS use must not be confused with consensus validator signing unless separately authorized |
| COSE key | COSE Sign1 projection | Binding records COSE key ref, algorithm id, and protected header policy | `kid` should be protocol-internal opaque identifier, not raw or hashed public key material |
| Hardware wallet / HSM ref | Provider-mediated EIP-712, COSE, or bare-key projection | Binding records opaque provider reference and verified public key commitment | Provider lifecycle events must be propagated into ILC registry by agent/operator |

## 5. Scope Limits

`binding_scope` must be an explicit allowlist. The default scope is empty.

| Scope | Pre-RC default | Additional authority required |
|-------|----------------|-------------------------------|
| `wallet_query_authorization` | Eligible for future query-only wallet phase | 1578g query surface |
| `claimability_proof_request` | Eligible after proof-claimability gate rerun | 1578f |
| `signer_binding_request` | Eligible as self/rotation evidence only | 1578d successor runtime or later CDL |
| `operator_controlled_agent_action` | Preflight only | 1578e and later authority |
| `value_transfer_request` | Blocked | `TRANSFER-ENABLED RC AUTHORIZED` plus 1579a/1579b or successor |
| `spend_request` | Blocked | Separate value-action authority |
| `withdrawal_request` | Blocked | Separate withdrawal authority |

An implementation must reject any signer-binding record that implies `wallet_transfer_enabled`, `wallet_spend_enabled`, `wallet_withdrawal_enabled`, `wallet_signing_authorized`, or `wallet_ledger_write_authorized` unless a later phase explicitly clears the relevant guard.

## 6. Revocation and Rotation

| Operation | Required authority | Effect |
|-----------|--------------------|--------|
| Revoke delegated signer | Root identity key, precommitted recovery policy, or authorized governance/quorum path | Binding is marked revoked after effective epoch; agent account remains intact |
| Rotate delegated signer | Same as revoke plus new binding record | New binding supersedes old binding; `agent_id` does not change |
| Supersede compromised signer | Root or precommitted compromise policy | Compromised delegated signer no longer authorizes future intents |
| Root identity succession | Existing CDL-002 recovery/succession canon only | Out of scope for this phase |

External wallet rotations are not automatically visible to ILC. The agent or operator must publish the corresponding ILC revocation/rotation evidence. This follows the existing wallet-agnostic signing strategy (`docs/specs/ilc_wallet_agnostic_signing_strategy_codex_handoff_v0.1.md:53-57`).

## 7. Operator Delegation

Operator-level delegation is accepted as an on-graph service-account model, but live bulk fleet transfer authority remains out of scope. A future `OperatorDelegationRecord` must reference:

| Field | Requirement |
|-------|-------------|
| `operator_agent_id` | Enrolled operator identity |
| `controlled_agent_id` | Enrolled controlled-agent identity |
| `delegation_scope` | Explicit allowed action classes; default deny |
| `activation_epoch` | First epoch in which delegation may be used |
| `expiry_epoch` | Optional terminal epoch |
| `revocation_ref` | Revocation/supersession path |
| `delegation_record_hash` | Hash referenced by any operator-signed intent |

Every operator-authorized action must reference the delegation record hash/root. Operator authority does not pool balances, merge nonces, or bypass per-agent admission and replay rules.

## 8. CDL Decision

No new CDL is opened in Phase 1578d.

Disposition: signer-binding CDL is explicitly deferred to a later SignatureSchemeRegistry / SignerBinding activation CDL, because:

1. The current pre-RC wallet default is visibility/proof-claimability only (`docs/specs/ilc_wallet_lane_forward_plan_pre_rc_v0.1.md:50-58`).
2. Direct Rust consensus support for secp256k1/EIP-712 is already deferred to a later ratified SignatureSchemeRegistry CDL (`docs/specs/ilc_wallet_lane_forward_plan_pre_rc_v0.1.md:14-28`).
3. No fresh CDL number is assigned in the current forward plan for signer binding, while CDL-102, CDL-103, CDL-104, and a tentative validator-identity CDL are already routed.
4. This phase can safely specify the authority object and non-activation boundary without making the binding runtime live.

Output token: `signer_binding_cdl_opened_or_deferred_phase_1578d` with disposition `deferred_to_signature_scheme_registry_or_signer_binding_activation_cdl`.

## 9. Runtime Boundary

`ilc_core/sidecars/wallet_action_semantics_preflight.py:54-71` lists false authorization flags, including wallet withdrawal, transfer, spend, signing, ledger write, public claimability, endpoint, bridge, mint, and settlement flags. `ilc_core/protocol/public_wallet_runtime.py:36-42`, `:44-60`, `:62-82`, and `:111-142` provide read-only display/query surfaces and hardcode `claimability_state="deferred"`.

Repository search found no active `def ...signer_binding...` or `def ...bind_signer...` runtime path in `ilc_core/`.

## 10. Non-Activation Statement

This phase does not activate runtime signer binding, does not bind any real external signer to any `agent_id`, does not authorize wallet-provider signing, does not create or mutate account state, does not clear transfer/spend/withdrawal/wallet-write guards, does not open or amend a CDL, does not publish a public mirror, does not mint ECU or ILC, does not settle economics, and does not activate public RC.

## 11. Output Tokens

- `signer_binding_authority_spec_committed_phase_1578d`
- `signer_binding_record_schema_specified_phase_1578d`
- `signer_binding_cdl_opened_or_deferred_phase_1578d`
