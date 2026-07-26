# ILC Agent Identity Enrollment Spec 1578a v0.1

**Phase:** 1578a / GAP-WALLET-00  
**Date:** 2026-07-25  
**Status:** committed spec / no runtime activation  
**Sensitivity:** NON-SENSITIVE

## 1. Purpose

This spec defines how a human user, autonomous agent, or operator-managed agent becomes an addressable ILC account before any wallet signer is bound. Enrollment creates or recognizes the ILC-native `agent_id` account anchor. It does not create a spendable external wallet, activate signer binding, or authorize transfer, spend, withdrawal, public claimability, minting, settlement, or wallet writes.

## 2. Existing Machinery Inventory

| Surface | Current source | Current scope | Enrollment implication |
|---------|----------------|---------------|------------------------|
| Validator enrollment | `ilc_core/genesis/validator_bootstrap_runtime.py:61-85` | Genesis validator bootstrap record: `validator_id`, Ed25519 public key, cluster, vote weight, epoch zero, enrolled-by field | Validator-specific; not the general user/agent enrollment path |
| Validator enrollment verification | `ilc_core/genesis/validator_bootstrap_runtime.py:88-122` | Verifies required fields and key-derived `validator_id` | Confirms existing path is tightly validator-scoped |
| Agent identity namespace | `docs/architecture/ilc_cdl_adr_implementation_map_v0.1.md:114-118` | CDL-042 key-derived globally flat `agent_id`; CDL-069 PQ identity / epoch endorsement | Canonical account anchor is `agent_id`, not wallet address |
| Canonical glossary | `docs/architecture/ilc_canonical_glossary_and_concepts_v0.2.md:157-168` | Distinguishes Genesis Agent, sidecar, and protocol actors | Enrollment must distinguish identity from host, sidecar, and wallet adapter |
| Invitation provenance | `ilc_core/genesis/invitation_provenance_record.py:98-125` and `:204-226` | Invite redemption record binds batch, nullifier, proof, redeemer public key CID, derived redeemer `agent_id`, epoch, inviter CID | Human public-RC enrollment must reference invite provenance once the invite lane is live |
| Identity seed derivation | `ilc_core/genesis/invitation_provenance_record.py:235-237` | `derive_agent_id_from_identity_seed()` returns SHA-384 over `ilc-agent-id-v1:` domain and identity seed | Existing non-validator derivation primitive exists, but no general enrollment record schema exists |
| Wallet lane decisions | `docs/specs/ilc_wallet_lane_forward_plan_pre_rc_v0.1.md:14-48` | ILC-native first; external wallets are delegated adapters; operator delegation accepted as on-graph service-account model | Enrollment must precede signer binding and must support operator fleets |

Direct search found no general `def enroll...` function in `ilc_core/genesis/`, `ilc_core/identity/`, or `ilc_core/protocol/` beyond validator bootstrap and related admission-control use. General enrollment is therefore a spec gap, not an already-active runtime path.

## 3. Enrollment Path Matrix

| Agent class | Enrollment path | Required fields | Graph anchor | Deferred surfaces |
|-------------|-----------------|-----------------|--------------|-------------------|
| Autonomous agent | Generate or possess an ILC-native identity seed/root key, derive `agent_id`, create an `AgentEnrollmentRecord`, and anchor it as a graph-supported identity record | `agent_id`, `identity_key_ref`, `identity_derivation_rule`, `enrollment_epoch`, `graph_anchor_ref`, `initial_nonce`, `enrollment_class` | `agent_enrollment_record:<sha256>` node with `SOURCE_TREE_MEMBER` / future identity edge to the agent graph | External signer binding, wallet provider, transfer, spend, withdrawal |
| Human user with external wallet adapter | First enroll ILC-native `agent_id`; attach invitation provenance if invite enforcement is active; defer external wallet signer binding to Phase 1578d | Autonomous fields plus `invitation_provenance_ref`, optional `external_wallet_hint` as non-authoritative metadata | Same `AgentEnrollmentRecord`; wallet key is not the account anchor | Signer binding, EIP-712/COSE authority, transfer, spend, withdrawal |
| Operator-managed agent fleet | Enroll each controlled agent as its own `agent_id`; record operator relationship as design-target `OperatorDelegationRecord` only after authority phase | Controlled-agent enrollment fields plus future `operator_delegation_ref` when authorized | Separate enrollment nodes per controlled agent; future delegation edge `operator_agent_id -> controlled_agent_id` | Live fleet transfer authority, balance pooling, blanket root authority |

## 4. Enrollment Record Schema

`AgentEnrollmentRecord` is the candidate canonical schema for future runtime work:

| Field | Required | Semantics |
|-------|----------|-----------|
| `record_version` | yes | Literal `agent_identity_enrollment_record_1578a.v0.1` until superseded |
| `agent_id` | yes | ILC-native account anchor; 96-character SHA-384 hex where current CDL-069/CDL-042 machinery applies |
| `identity_derivation_rule` | yes | Domain-separated derivation rule, e.g. `sha384(ilc-agent-id-v1 || identity_seed)` for current invite-derived identities |
| `identity_key_ref` | yes | Opaque reference to the enrolled identity public key or commitment; raw private key material is forbidden |
| `enrollment_class` | yes | One of `autonomous_agent`, `human_user_external_wallet_adapter`, `operator_managed_agent` |
| `invitation_provenance_ref` | conditional | Required for public-RC human enrollment once mandatory invite enforcement is live |
| `graph_anchor_ref` | yes | Content-addressed graph node/ref that anchors the enrollment record |
| `initial_nonce` | yes | Integer `0` for a newly enrolled `agent_id` |
| `enrollment_epoch` | yes | Protocol epoch at which enrollment becomes visible to ILC state |
| `signer_lineage_ref` | optional | Opaque lineage reference for later signer-binding phase; not an authorization by itself |
| `operator_delegation_ref` | optional | Future delegation record reference; not active in this phase |
| `non_activation_flags` | yes | Machine-readable booleans proving no transfer/spend/withdrawal/signer binding was activated |

## 5. Nonce Initialization Rule

For a newly enrolled `agent_id`, wallet-facing action nonce starts at `0`.

The nonce is a property of the ILC-native account state keyed by `agent_id`. It is not a property of an external wallet address, adapter, operator, or signer-binding record. Multiple future delegated signers for the same `agent_id` share the same account nonce unless a later CDL authorizes subaccount or channel nonces.

Third-party wallets must read nonce state from ILC account state once the query surface exists. They must not infer nonce validity from local history.

## 6. Operator Delegation Design Target

Operator-level delegation is accepted as a design target from the wallet lane forward plan. The authoritative source for all ten required properties is `docs/specs/ilc_wallet_lane_forward_plan_pre_rc_v0.1.md §0.2`. The required future object is an on-graph `OperatorDelegationRecord` with all ten mandatory properties:

| Property | Required behavior | Source |
|----------|-------------------|--------|
| On-graph record | `OperatorDelegationRecord` graph node/edge: `operator_agent_id → controlled_agent_id` | forward plan §0.2 |
| Scope limits | Delegation must specify allowed action classes; no blanket root authority by default | forward plan §0.2 |
| Revocation | Graph-native revoke/supersede path required | forward plan §0.2 |
| Epoch binding | Activation epoch + optional expiry epoch | forward plan §0.2 |
| Nonce separation | Each controlled agent keeps its own per-`agent_id` nonce; no shared operator nonce | forward plan §0.2 |
| Auditability | Every operator-authorized action must reference the delegation record hash/root | forward plan §0.2 |
| No balance pooling | Operator authority does not collapse agent balances unless a separate treasury mechanism is ratified | forward plan §0.2 |
| Least privilege | Default deny; operator acts only within explicit capabilities | forward plan §0.2 |
| Key rotation | Operator and agent key rotations traceable through signer-lineage or successor records | forward plan §0.2 |
| Privacy | Public surfaces expose minimum delegation refs; opaque IDs preferred over raw external wallet keys | forward plan §0.2 |

**Source correction note (2026-07-26):** An earlier draft of this section listed eight properties, collapsing "On-graph record" and "Auditability" into a single row and omitting "Least privilege". The wallet lane forward plan §0.2 is the definitive authority and specifies ten mandatory properties. This section has been corrected to match. Any downstream spec or phase prompt that references this section must use the ten-property table above, not the earlier eight-property version.

This phase records the design target only. It does not activate live operator delegation.

## 7. Non-Claims

| Non-claim | Status |
|-----------|--------|
| Runtime general enrollment activated | false |
| Signer binding activated | false |
| Wallet transfer enabled | false |
| Wallet spend enabled | false |
| Wallet withdrawal enabled | false |
| Wallet provider signing authorized | false |
| Wallet ledger write authorized | false |
| Public claimability activated by this phase | false |
| CDL opened or mutated | false |
| Public mirror pushed | false |

## 8. Output Tokens

- `agent_identity_enrollment_spec_committed_phase_1578a`
- `general_agent_enrollment_distinguished_from_validator_phase_1578a`
- `operator_delegation_design_target_recorded_phase_1578a`
