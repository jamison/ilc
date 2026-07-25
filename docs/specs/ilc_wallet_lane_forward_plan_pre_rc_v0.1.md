# ILC Wallet Lane Forward Plan — Pre-RC and Post-RC

**Version:** 0.1  
**Date:** 2026-07-25  
**Status:** RATIFIED PLANNING — record of joint Sonnet/Codex/human decisions  
**Authority:** This doc supersedes informal chat-history wallet planning. All GAP-WALLET phases must be consistent with the decisions recorded here.

---

## §0. Canonical Decisions

These are **accepted, human-approved decisions** as of 2026-07-25. They are not open questions.

### §0.1 Architecture: ILC-Native First, External Wallets as Delegated Adapters

ILC should be wallet-agnostic by making external wallets delegated signing providers, **not** by making any external wallet curve the native consensus identity layer.

```
ILC-native agent_id:  primary account anchor; key-derived; graph-native
External wallet:      delegated signing adapter over agent_id; optional
Consensus layer:      verifies ILC-native signatures and state transitions
secp256k1/EIP-712:    adapter/sidecar layer only for public RC;
                      direct Rust consensus support deferred to later
                      ratified SignatureSchemeRegistry CDL
```

**Consequence:** an external wallet signature does not *create* an ILC account. It binds to a pre-existing agent_id. Agent-native enrollment is the canonical path. Human-wallet enrollment is an adapter path.

### §0.2 Operator-Level Delegation: Accepted (Service Account Model, On-Graph)

**Accepted by human 2026-07-25.** ILC supports operator-level delegation for fleets of agents. An operator may register authority over many agent instances through graph-native delegation records committed into ILC graph state. This is the **service account model**: operators manage many agent identities without requiring individual human-wallet ceremonies per agent.

**Required design properties — all mandatory:**

| Property | Requirement |
|----------|-------------|
| On-graph record | `OperatorDelegationRecord` graph node/edge: `operator_agent_id → controlled_agent_id` |
| Scope limits | Delegation must specify allowed action classes; no blanket root authority by default |
| Revocation | Graph-native revoke/supersede path required |
| Epoch binding | Activation epoch + optional expiry epoch |
| Nonce separation | Each controlled agent keeps its own per-agent_id nonce; no shared operator nonce |
| Auditability | Every operator-authorized action must reference delegation record hash/root |
| No balance pooling | Operator authority does not collapse agent balances unless separate treasury mechanism is ratified |
| Least privilege | Default deny; operator acts only within explicit capabilities |
| Key rotation | Operator and agent key rotations traceable through signer-lineage or successor records |
| Privacy | Public surfaces expose minimum delegation refs; opaque IDs preferred over raw external wallet keys |

**Not in scope for public RC:** live bulk operator fleet transfer authority. The model is locked now so architecture does not assume "one human wallet = one agent," but activation of live fleet transfers is post-RC unless separately upgraded by explicit GO.

### §0.3 Public RC Wallet Default: Visibility/Proof-Claimability Only

**Planning rule — binding on all phases between now and public RC:**

> Public RC wallet default is visibility/proof-claimability only.  
> Transfer-enabled public RC requires a **separate exact GO phrase at GAP-WALLET-09**.  
> Absent that GO, wallet transfer/spend/withdrawal remains blocked.

This constrains interpretation of 1575s, 1575t, and all wallet phases. Do not read any 1575 phase authorization as implying transfer/spend/withdrawal enablement.

### §0.4 Option C2 (supersedes original Option C wording in 1575q)

Genesis ILC and agent ILC balances are credited as wallet-agnostic canonical settled balances in the ILC lifecycle ledger, bound to agent_id, via `commit_settled_epoch()`. Visible through `PublicWalletRuntime` as `balance_ilc`. `claimability_state = "deferred"` unless GAP-WALLET-03 explicitly clears it.

```
GENESIS_SETTLEMENT_WRITE_AUTHORIZED = True   [set in 1575s]
GENESIS_MINTING_AUTHORIZED          = True   [set in 1575s]
GENESIS_WALLET_WRITE_AUTHORIZED     = False  [retained; means no wallet-provider
                                              spend/transfer/withdrawal authority,
                                              NOT "Genesis balance is invisible"]
```

**Do not use `GENESIS_WALLET_WRITE_AUTHORIZED=True` as the general "wallets work" switch.** General wallet support comes through signer binding, public wallet surfaces, claimability verification, and later value-action runtime.

### §0.5 Replay Prevention Architecture

| Layer | Mechanism |
|-------|-----------|
| Wallet-facing ILC transfers | Per-agent_id nonce; starts at 0 for new accounts; authoritative nonce read from ILC account state |
| Internal Rust/consensus | Object-version certificate replay (existing `balance_store.rs` model; do not replace) |
| Claimability/double-claim | Nullifier set (existing claimability runtime; not for ordinary transfers) |

**Third-party wallets must not infer nonce from local history.** The canonical nonce surface must be a future `next_action_nonce` field in `public_wallet_runtime.py` (added in GAP-WALLET-04 / transfer lane).

**Nonce is per-agent_id, not per-signer-binding.** Multiple delegated signers for the same agent share one nonce space. If future high-throughput agents need parallel lanes, add subaccount/channel nonces by CDL.

### §0.6 Canonical Payload / Signing Envelope Model

One canonical ILC intent object. Two signing presentations that are adapter projections over the same canonical payload.

```
Canonical ILC intent object:
  - sender_agent_id
  - recipient_agent_id (or agent address)
  - amount + asset_type (ILC)
  - nonce (per-agent_id)
  - network_id
  - epoch_binding (epoch number or settlement-root ref)
  - intent_schema_version
  - expiry (optional)
  - delegation_record_hash (if operator-signed)

Signing presentations:
  EIP-712:    for MetaMask/WalletConnect/Ethereum-style human wallets
  COSE Sign1: for CBOR-native, hardware wallets, autonomous agents,
              PQ-compatible flows

Equivalence requirement:
  Both EIP-712 and COSE Sign1 presentations must decode to the same
  canonical intent digest. Verifier rule must be explicitly specified
  in GAP-WALLET-02a.
```

**Domain separator must include at minimum:**
- ILC domain string
- Network ID
- Epoch or epoch-root binding
- Intent schema version
- Chain/profile identifier

This prevents testnet/mainnet and stale-epoch signature replay.

---

## §1. Phase Lane Structure

### Pre-RC Hard Stops (default)

| Phase | Name | Sensitivity | Output |
|-------|------|-------------|--------|
| GAP-WALLET-00 | Agent Identity Enrollment Spec | NON-SENSITIVE | Ratifiable enrollment model |
| GAP-WALLET-01 | Wallet Canon Reconciliation | NON-SENSITIVE | Single RC wallet target profile |
| GAP-WALLET-02a | Canonical Payload / Envelope Preflight | NON-SENSITIVE | Canonical intent object + equivalence proof spec |
| GAP-WALLET-02b | Signer Binding Authority | SENSITIVE | Ratified signer-binding, enrollment, operator delegation spec |
| GAP-WALLET-02c | Operator Delegation Runtime Preflight | NON-SENSITIVE preflight / SENSITIVE if ratifying | Operator delegation model detail; feeds GAP-WALLET-02b if combined or separate CDL |
| GAP-WALLET-03 | Proof-Claimability Gate Rerun | SENSITIVE | Proof-claimability verification enabled or blocked |
| GAP-WALLET-07 (query only) | Wallet CLI/Sidecar — Query Surface | NON-SENSITIVE | `ilc wallet status/history/export` live; `transfer --dry-run` only |
| GAP-WALLET-09 | Public RC Wallet Gate | SENSITIVE | Final human GO/NO-GO on visibility-only vs transfer-enabled RC |

### Post-RC / Upgrade Track (default — activated only by separate GO)

| Phase | Name | Sensitivity |
|-------|------|-------------|
| GAP-WALLET-04 | ILC Value-Action Transaction Schema | SENSITIVE |
| GAP-WALLET-05 | ILC Transfer Ledger Runtime | SENSITIVE |
| GAP-WALLET-06 | Wallet Provider Adapter MVP | NON-SENSITIVE (dry-run) / SENSITIVE (live submit) |
| GAP-WALLET-07 (live submit) | Wallet CLI — Live Transfer Submit | SENSITIVE |
| GAP-WALLET-08 | Wallet Transfer Integration Soak | SENSITIVE |

**Activation rule:** GAP-WALLET-04 through GAP-WALLET-08 become pre-RC hard stops **only if** the human explicitly upgrades RC scope with the phrase: `TRANSFER-ENABLED RC AUTHORIZED`. Absent that phrase, these phases run post-RC.

---

## §2. Phase Specifications

### GAP-WALLET-00 — Agent Identity Enrollment Spec `NON-SENSITIVE`

**Purpose.** Define how a new human user or autonomous agent becomes an addressable ILC account before any wallet signer is bound. The current lane assumes agent_id already exists; public RC needs a canonical answer for account creation.

**Required scope:**
- Inventory existing key-derived agent_id machinery (`ilc_cdl_adr_implementation_map_v0.1.md:115`, `validator_bootstrap_runtime.py:61`)
- Distinguish validator enrollment (genesis-specific) from general agent enrollment (not yet canonically defined)
- Define enrollment path for: autonomous agents (programmatic, no human wallet); human users with external wallet adapters; operator-managed agent fleets (service account model)
- Specify enrollment record fields: agent_id derivation, public key/signer lineage, invitation provenance ref (if applicable), graph anchor, initial nonce = 0
- Address operator delegation architecture (§0.2) as a design target; do not activate
- Output: ratifiable enrollment model (spec doc); does **not** activate enrollment or mutate any runtime

**Non-claim:** this phase does not authorize signer binding, transfer, spend, withdrawal, or claimability.

---

### GAP-WALLET-01 — Wallet Canon Reconciliation `NON-SENSITIVE`

**Purpose.** Reconcile all prior wallet/claimability canon into one coherent RC wallet target profile.

**Sources to reconcile:** phases 576, 581, 617, 1252, 1314, 1389b, 1438, 1439, 1575q, 1575s, 1575t; `ilc_wallet_agnostic_signing_strategy_codex_handoff_v0.1.md`; `ilc_rc0_1_settlement_wallet_boundary_lock_576_v0.1.md`; `ilc_wallet_withdrawal_transfer_spend_semantics_preflight_1314_v0.1.md`.

**Required output:** one canonical RC wallet profile document stating:
- What is visible at RC (settled balances, receipts, audit history)
- What is verifiable at RC (proof-claimability if GAP-WALLET-03 passes)
- What remains blocked at RC (transfer, spend, withdrawal, external-address claimability)
- Explicit Option C2 statement superseding original Option C language in 1575q

---

### GAP-WALLET-02a — Canonical Payload / Envelope Preflight `NON-SENSITIVE`

**Purpose.** Define the canonical ILC intent object and the equivalence proof between EIP-712 and COSE Sign1 presentations. No authority is ratified here.

**Required output:**
- Canonical intent object schema (all fields per §0.6)
- Domain separator specification (all required fields per §0.6)
- EIP-712 typed-data projection: type definitions, domain struct, primary type
- COSE Sign1 projection: header map, payload encoding, context label
- Equivalence verifier rule: how both decode to the same canonical intent digest
- Guidance on who generates the canonical payload (ILC node, agent, adapter sidecar)

**Non-claim:** this phase does not ratify who is authorized to sign.

---

### GAP-WALLET-02b — Signer Binding Authority `SENSITIVE`

**GO phrase required:** `GO GAP-WALLET-02b SIGNER-BINDING-AUTHORITY`

**Purpose.** Ratify how an external wallet or key becomes a delegated signer for an ILC agent_id. Incorporate operator delegation model.

**Required scope:**
- External wallet signatures **bind to an already-existing agent_id**; they do not create ILC accounts (§0.1)
- Agent-native enrollment is primary; human-wallet enrollment is an adapter path
- Opaque kid privacy constraint (per `ilc_wallet_agnostic_signing_strategy_codex_handoff_v0.1.md:36`)
- Signer rotation, revocation, recovery procedures
- Replay boundary between signer-binding actions and value-action nonces
- Privacy rules for public delegation exposure
- Operator delegation: `OperatorDelegationRecord` model per §0.2; design required, activation deferred to post-RC unless separately authorized
- secp256k1 remains adapter/sidecar layer; direct Rust consensus support deferred to SignatureSchemeRegistry CDL

**Non-claim:** this phase does not authorize transfer, spend, withdrawal, or live operator fleet activation.

---

### GAP-WALLET-02c — Operator Delegation Runtime Preflight `NON-SENSITIVE preflight`

**Purpose.** Detail the on-graph operator delegation model before it is ratified. May feed GAP-WALLET-02b or proceed as a separate CDL if scope warrants separation.

**Required scope:** all nine design requirements from §0.2 formalized as implementable spec.

---

### GAP-WALLET-03 — Proof-Claimability Gate Rerun `SENSITIVE`

**GO phrase required:** `GO GAP-WALLET-03 PROOF-CLAIMABILITY-GATE-RERUN`

**Purpose.** Rerun or supersede the older public claimability gate (`ilc_claimability_public_mode_runtime_1389b_v0.1.md:175`) after CDL-048 / 1575 economic path.

**Claimability definition in scope:**
- **Proof claimability:** an agent can cryptographically prove that a settled balance is theirs and export a verifiable receipt. Compatible with visibility-only RC.

**Out of scope:**
- External-address claimability (claim/withdraw/transfer to external address) — this is materially closer to transfer/withdrawal; remains blocked unless separately authorized.

**Non-claim:** this phase does not authorize wallet transfer, spend, withdrawal, or external-address claimability.

---

### GAP-WALLET-07 (Query Surface Only) — Wallet CLI/Sidecar `NON-SENSITIVE`

**Purpose.** Expose read-only and dry-run wallet CLI surface.

**In scope:** `ilc wallet status`, `ilc wallet history`, `ilc wallet export`, `ilc wallet transfer --dry-run` (generates signed intent for review; does not submit), `ilc wallet verify-signature`.

**Not in scope:** `--submit` flag, live transfer, spend, withdrawal. These are gated by GAP-WALLET-04/05/08 + separate GO.

---

### GAP-WALLET-09 — Public RC Wallet Gate `SENSITIVE`

**GO phrase required:** `GO GAP-WALLET-09 PUBLIC-RC-WALLET-GATE`

**Purpose.** Final human decision on RC wallet scope.

**Default outcome if no transfer upgrade:** public RC ships with visibility, proof-claimability verification (if GAP-WALLET-03 passes), and query CLI. No live transfer/spend/withdrawal.

**Transfer-enabled upgrade:** requires separate phrase `TRANSFER-ENABLED RC AUTHORIZED` in addition to the gate GO. This phrase confirms that GAP-WALLET-04 through GAP-WALLET-08 have been completed and audited.

---

### GAP-WALLET-04 — ILC Value-Action Transaction Schema `SENSITIVE` [Post-RC default]

**Purpose.** Define transfer/spend payload schema and replay prevention.

**Must resolve before runtime:**
- Replay prevention: per-agent_id nonce (§0.5) — specify initialization (nonce = 0), canonical read surface, and behavior on nonce gap/skip
- All required payload fields (§0.6)
- Expiry policy
- Delegation record ref for operator-signed actions

---

### GAP-WALLET-05 — ILC Transfer Ledger Runtime `SENSITIVE` [Post-RC default]

**Purpose.** Implement atomic debit/credit for settled ILC balances.

**Must include:** exact Decimal/integer quantization, no float, sufficient-balance checks, per-agent_id nonce/replay enforcement, deterministic receipt, settlement-root sensitivity, idempotency rules, and ≥10 tests. Must not reuse ECU transfer code without explicit audit that ECU/ILC semantics are compatible.

---

### GAP-WALLET-06 — Wallet Provider Adapter MVP `NON-SENSITIVE (dry-run) / SENSITIVE (live)` [Post-RC default]

**Purpose.** Implement adapter-layer verification for external signatures.

**secp256k1 stays in sidecar/Python adapter for public RC.** Direct Rust consensus verification of secp256k1 is deferred to a later SignatureSchemeRegistry CDL.

---

### GAP-WALLET-08 — Wallet Transfer Integration Soak `SENSITIVE` [Post-RC default]

**Purpose.** Private multi-agent ILC transfer soak after real settlement.

**Must verify:** balances, settlement roots, replay rejection, signer binding, failed double spend, failed stale nonce, deterministic receipts, no ledger drift.

---

## §3. Relationship to 1575 Economic Lane

This wallet lane does **not** block 1575r, 1575s, or 1575t. Those phases proceed on the CDL-048/economic track. The wallet lane runs in parallel and must not be conflated with economic settlement authorization.

| 1575 phase | Wallet implications |
|-----------|---------------------|
| 1575r | CDL-048 production conversion rehearsal; no wallet writes; private evidence only |
| 1575s | Sets `GENESIS_SETTLEMENT_WRITE_AUTHORIZED=True`, `GENESIS_MINTING_AUTHORIZED=True`; retains `GENESIS_WALLET_WRITE_AUTHORIZED=False` (Option C2) |
| 1575t | End-to-end economic soak; settlement accounting only; no wallet transfer/spend/withdrawal |

---

## §4. PLANNING_INDEX Entry

The following rule must be added to `PLANNING_INDEX.md` §0 before any further 1575 or GAP-WALLET phases execute:

> **Wallet scope constraint:** Public RC wallet default = visibility/proof-claimability only. Transfer-enabled public RC requires separate exact GO phrase `TRANSFER-ENABLED RC AUTHORIZED` at GAP-WALLET-09. Absent that GO, wallet transfer/spend/withdrawal remains blocked through public RC.

---

## §5. Sources

| Canonical source | Decision it grounds |
|-----------------|---------------------|
| `ilc_wallet_agnostic_signing_strategy_codex_handoff_v0.1.md:12` | Wallet-agnostic signing is ratified canon |
| `ilc_wallet_agnostic_signing_strategy_codex_handoff_v0.1.md:18` | COSE/secp256k1 as signing-provider compatibility only |
| `ilc_wallet_agnostic_signing_strategy_codex_handoff_v0.1.md:36` | Opaque kid privacy constraint |
| `ilc_wallet_agnostic_signing_strategy_codex_handoff_v0.1.md:56` | External wallet lifecycle is agent/operator responsibility |
| `ilc_rc0_1_settlement_wallet_boundary_lock_576_v0.1.md:38,79` | Wallet surfaces are read-only; no spend/transfer/withdrawal |
| `ilc_wallet_withdrawal_transfer_spend_semantics_preflight_1314_v0.1.md:31` | Transfer/spend/withdrawal blocked by Phase 1314 |
| `ilc_cdl_adr_implementation_map_v0.1.md:115` | agent_id is key-derived |
| `ilc_consensus/src/types.rs:141`, `balance_store.rs:94` | Existing Rust replay uses object/version, not wallet nonces |
| `ilc_claimability_public_mode_runtime_1389b_v0.1.md:175` | Old claimability gate exists but has not been rerun post-1575 |
| `ilc_core/genesis/validator_bootstrap_runtime.py:61` | Existing enrollment is validator-specific; general enrollment undefined |

---

*This document records human-approved decisions from the Sonnet/Codex joint wallet planning session of 2026-07-25. It does not activate any of the phases described. Full derivations, phase prompts, and implementation specs are the output of the GAP-WALLET phases above.*
