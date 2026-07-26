# ILC Operator Delegation Runtime Preflight 1578e v0.1

**Phase:** 1578e / GAP-WALLET-02c  
**Date:** 2026-07-26  
**Status:** committed preflight / no runtime activation  
**Sensitivity:** NON-SENSITIVE

## 1. Purpose

This preflight records the runtime-readiness boundary for operator-level delegation in the wallet lane. Operator delegation is accepted as an on-graph service-account design target, but no live `OperatorDelegationRecord` runtime exists and no operator delegation activation is authorized by this phase.

This phase does not open a CDL, ratify a new authority, activate a runtime verifier, write wallet or ledger state, authorize transfer, authorize spend, authorize withdrawal, clear guards, mint ECU or ILC, settle economics, publish a public mirror, or activate public RC.

## 2. Source-Read Summary

| Source | Direct-read finding |
|--------|---------------------|
| `docs/specs/ilc_wallet_lane_forward_plan_pre_rc_v0.1.md:14-27` | ILC-native `agent_id` is the account anchor; external wallets are delegated signing adapters, not native consensus identities. |
| `docs/specs/ilc_wallet_lane_forward_plan_pre_rc_v0.1.md:29-48` | Operator-level delegation is accepted as an on-graph service-account model with mandatory design properties and live bulk fleet transfer authority out of public-RC scope. |
| `docs/specs/ilc_wallet_lane_forward_plan_pre_rc_v0.1.md:50-58` | Public RC wallet default is visibility/proof-claimability only; transfer-enabled RC requires a separate exact GO phrase. |
| `docs/specs/ilc_wallet_lane_forward_plan_pre_rc_v0.1.md:74-84` | Wallet-facing replay prevention is per-`agent_id`; no shared operator nonce is authorized. |
| `docs/specs/ilc_wallet_lane_forward_plan_pre_rc_v0.1.md:201-217` | Signer binding is SENSITIVE; operator delegation is designed there but activation remains deferred unless separately authorized. |
| `docs/specs/ilc_wallet_lane_forward_plan_pre_rc_v0.1.md:221-225` | GAP-WALLET-02c formalizes the operator-delegation design as preflight scope. |
| `docs/specs/ilc_agent_identity_enrollment_spec_1578a_v0.1.md:28-32` | Operator-managed fleets enroll each controlled agent as its own `agent_id`; the future delegation edge is `operator_agent_id -> controlled_agent_id`. |
| `docs/specs/ilc_agent_identity_enrollment_spec_1578a_v0.1.md:53-59` | New `agent_id` action nonce starts at `0`; nonce is not keyed by external wallet, adapter, operator, or signer-binding record. |
| `docs/specs/ilc_agent_identity_enrollment_spec_1578a_v0.1.md:61-76` | The enrollment spec records an eight-row compressed operator-delegation design target and states live operator delegation is not activated. |
| `docs/specs/ilc_signer_binding_authority_spec_1578d_v0.1.md:14-25` | External signers are delegated adapters; secp256k1/EIP-712 remains sidecar evidence for public RC; binding authority does not imply value-action authority. |
| `docs/specs/ilc_signer_binding_authority_spec_1578d_v0.1.md:27-50` | `SignerBindingRecord` has a conditional `operator_delegation_ref` and per-`agent_id` nonce separation. |
| `docs/specs/ilc_signer_binding_authority_spec_1578d_v0.1.md:89-103` | Future `OperatorDelegationRecord` fields are named; operator authority does not pool balances, merge nonces, or bypass admission/replay rules. |
| `docs/specs/ilc_signer_binding_authority_spec_1578d_v0.1.md:105-122` | No signer-binding CDL was opened in 1578d; activation is deferred to a later SignatureSchemeRegistry or SignerBinding activation CDL. |
| `ilc_core/protocol/public_wallet_runtime.py:36-42` | `wallet_status()` is read-only and returns status data. |
| `ilc_core/protocol/public_wallet_runtime.py:44-60` | `wallet_history()` is read-only and hardcodes `claimability_state = "deferred"`. |
| `ilc_core/protocol/public_wallet_runtime.py:62-82` | `wallet_export()` is read-only and hardcodes `claimability_state = "deferred"`. |
| `ilc_core/protocol/public_wallet_runtime.py:111-142` | `_wallet_snapshot()` constructs display status from lifecycle state; no operator-delegation field or enforcement path exists. |
| `ilc_core/sidecars/wallet_action_semantics_preflight.py:54-71` | Wallet action authorization flags are all false-by-default surfaces, including transfer, spend, signing, ledger write, public claimability, endpoint, bridge, mint, and settlement flags. |
| `ilc_core/sidecars/wallet_action_semantics_preflight.py:181-209` | `_require_all_false()` enforcement rejects attempts to flip wallet action flags in the preflight packet. |
| `docs/adr/ADR_0026_Protocol_vs_Harness_Product_Boundary.md:39-45` | Protocol truth, settlement semantics, graph legitimacy, and wallet authority stay in protocol/runtime; operator conveniences sit above protocol through machine-legible surfaces. |
| `docs/adr/ADR_0026_Protocol_vs_Harness_Product_Boundary.md:93-109` | Wallet UX remains narrow unless separately authorized; spend, transfer, withdrawal, and generalized signing authority require explicit authorization. |
| `docs/specs/ilc_constitutional_decision_log_v0.1.md:77` | CDL-042 ratifies globally flat key-derived `agent_id`; this supports per-controlled-agent identity rather than operator-scoped account collapse. |
| `docs/specs/ilc_constitutional_decision_log_v0.1.md:101` | CDL-069 ratifies ML-DSA-65 as the post-quantum identity root and epoch endorsement protocol. |
| `docs/specs/ilc_constitutional_decision_log_v0.1.md:131` | CDL-101 records D2D actor binding and says delegation is out of scope v1, so operator delegation needs a separate authority lane for live network use. |

## 3. Design Target Restatement

The authoritative source is the wallet lane forward plan. It records ten mandatory design properties for `OperatorDelegationRecord`; the Phase 1578a enrollment spec compresses these into eight rows and omits explicit rows for auditability and least privilege. This preflight preserves the ten-property source to avoid losing security-critical constraints.

| Property | Required preflight interpretation |
|----------|-----------------------------------|
| On-graph record | Create a graph-native `OperatorDelegationRecord` node/edge binding `operator_agent_id -> controlled_agent_id`; source: `docs/specs/ilc_wallet_lane_forward_plan_pre_rc_v0.1.md:37`. |
| Scope limits | Delegation records must carry explicit allowed action classes; no blanket root authority by default; source: `docs/specs/ilc_wallet_lane_forward_plan_pre_rc_v0.1.md:38`. |
| Revocation | Runtime design requires graph-native revoke or supersede records; source: `docs/specs/ilc_wallet_lane_forward_plan_pre_rc_v0.1.md:39`. |
| Epoch binding | Activation epoch and optional expiry epoch are required; source: `docs/specs/ilc_wallet_lane_forward_plan_pre_rc_v0.1.md:40`. |
| Nonce separation | Each controlled agent keeps its own per-`agent_id` nonce; there is no shared operator nonce; source: `docs/specs/ilc_wallet_lane_forward_plan_pre_rc_v0.1.md:41` and `:78-84`. |
| Auditability | Every operator-authorized action must reference the delegation record hash/root; source: `docs/specs/ilc_wallet_lane_forward_plan_pre_rc_v0.1.md:42`. |
| No balance pooling | Operator authority must not collapse agent balances unless a separate treasury mechanism is ratified; source: `docs/specs/ilc_wallet_lane_forward_plan_pre_rc_v0.1.md:43`. |
| Least privilege | Default deny; operator acts only within explicit capabilities; source: `docs/specs/ilc_wallet_lane_forward_plan_pre_rc_v0.1.md:44`. |
| Key rotation | Operator and controlled-agent key rotations must be traceable through signer lineage or successor records; source: `docs/specs/ilc_wallet_lane_forward_plan_pre_rc_v0.1.md:45`. |
| Privacy | Public surfaces should expose minimum delegation references and prefer opaque IDs over raw external wallet keys; source: `docs/specs/ilc_wallet_lane_forward_plan_pre_rc_v0.1.md:46`. |

## 4. Current Runtime State

Repository search found no active `OperatorDelegationRecord` runtime in `ilc_core/`.

| Runtime surface | Current state | Implication |
|-----------------|---------------|-------------|
| `ilc_core/protocol/public_wallet_runtime.py` | Read-only display/export/status layer; hardcoded `claimability_state = "deferred"`; no delegation fields | Suitable future read surface, but no delegation state or action authority exists. |
| `ilc_core/sidecars/wallet_action_semantics_preflight.py` | False authorization flag inventory and fail-closed enforcement for wallet actions | Future operator-delegation preflight/activation should reuse this guard posture: explicit false defaults, reject accidental activation. |
| `ilc_core/sidecars/openclaw_local_capture.py` | Local capture envelope carries `operator_agent_id` and `local_agent_id` metadata | Related operator metadata exists, but it is local capture provenance only, not wallet delegation authority. |
| `ilc_core/sidecars/openclaw_idle_mining.py` | Local idle-task envelope carries `operator_agent_id` and `local_agent_id` metadata | Related operator metadata exists, but it is local orchestration evidence only, not graph-native `OperatorDelegationRecord`. |
| Rust `ECUTransfer` path | CDL-066 sender authorization exists for narrow ECU fast-path transfer sender auth | It does not authorize wallet-facing ILC value actions or operator delegation. |

## 5. Preconditions Before Activation

| Precondition | Required before live operator delegation | Rationale |
|--------------|------------------------------------------|-----------|
| Agent enrollment model complete | Phase 1578a complete; future activation must consume an implemented `AgentEnrollmentRecord` runtime or equivalent | Delegation cannot bind to non-existent or unenrolled identities. |
| Signer binding authority complete | Phase 1578d complete; future activation needs the deferred SignatureSchemeRegistry or SignerBinding activation CDL | Operators may act through external or delegated signers only after signer authority is ratified. |
| Canonical intent payload complete | Phase 1578c complete; future value-action activation must preserve canonical digest equivalence across adapter projections | Operator-signed actions need an unambiguous payload preimage. |
| Per-controlled-agent nonce surface | Future transfer/value-action runtime must expose canonical per-`agent_id` `next_action_nonce` | Prevents replay and prevents shared operator nonce collapse. |
| Graph schema route | A graph-native node/edge representation for `OperatorDelegationRecord`, revocation, and supersession must be specified | Required by the on-graph auditability design property. |
| Scope vocabulary | Allowed action classes must be enumerated and default-deny | Prevents blanket root authority and accidental transfer/spend/withdrawal grants. |
| Revocation and rotation runtime | Runtime must verify effective epoch, expiry epoch, revoked-by references, and supersession chains | Required for safety after compromise or key rotation. |
| Privacy profile | Public projection must use opaque delegation refs and avoid raw wallet key leakage | Keeps wallet-agnostic support from leaking external wallet identity. |
| Wallet action guard authority | Any transfer/spend/withdrawal authority requires later explicit GO and guard clearance | Public RC default is visibility/proof-claimability only. |
| CDL authority | A future SENSITIVE CDL must ratify operator-delegation activation or fold it into the later SignatureSchemeRegistry / SignerBinding activation CDL | CDL-101 explicitly leaves delegation out of scope v1, and 1578d deferred signer-binding activation. |

## 6. Blocker Inventory

No active runtime blocker conflicts with the operator-delegation design because there is no active operator-delegation runtime to contradict it.

The following are activation blockers, not design conflicts:

| Blocker | Type | Disposition |
|---------|------|-------------|
| No `OperatorDelegationRecord` runtime | Missing implementation | Future runtime phase after CDL authority. |
| No graph-native delegation schema in runtime | Missing implementation | Future schema/runtime phase. |
| No per-agent wallet action nonce read surface | Missing implementation | Future GAP-WALLET-04 / transfer lane. |
| Wallet transfer/spend/withdrawal flags false | Intentional guard | Must remain blocked through visibility-only public RC. |
| Signer-binding CDL authority deferred | Constitutional authority gap | Separate SENSITIVE SignatureSchemeRegistry / SignerBinding activation CDL. |
| CDL-101 delegation out of scope v1 | Constitutional scope gap | Do not reuse D2D signed gossip actor binding as operator delegation authority. |

## 7. CDL Gap Assessment

Operator delegation needs a future SENSITIVE authority decision before activation. The cleanest route is a combined `SignatureSchemeRegistry / SignerBinding / OperatorDelegation` activation CDL if the future implementation binds external signers and operator scopes together. If the implementation keeps operator delegation independent of external wallet signers, use a separate `OperatorDelegationRecord` CDL.

Minimum CDL questions before activation:

1. Is `OperatorDelegationRecord` a wallet-lane object only, or a general graph-authority object usable by non-wallet agent actions?
2. Which scope vocabulary is canonical for public RC and post-RC?
3. What edge names encode grant, revoke, supersede, and action-reference links?
4. Which signer types may authorize the operator side: ILC-native ML-DSA root, delegated external signer, HSM/provider ref, or a subset?
5. What public projection is allowed for delegation refs without leaking external wallet keys?
6. Is live operator-controlled transfer authority allowed only after `TRANSFER-ENABLED RC AUTHORIZED`, or can non-value operator actions activate earlier?

No CDL is opened in this phase.

## 8. Activation-Deferred Statement

Operator delegation activation is deferred. Phase 1578e records readiness and blockers only.

| Non-claim | Status |
|-----------|--------|
| Operator delegation runtime activated | false |
| `OperatorDelegationRecord` written to runtime state | false |
| Real operator granted authority over any controlled agent | false |
| Signer binding runtime activated | false |
| Wallet transfer enabled | false |
| Wallet spend enabled | false |
| Wallet withdrawal enabled | false |
| Wallet signing authorized | false |
| Wallet ledger write authorized | false |
| CDL opened or amended | false |
| Guard cleared | false |
| ECU or ILC minted | false |
| Economic settlement executed | false |
| Public mirror pushed | false |

## 9. Output Tokens

- `operator_delegation_preflight_committed_phase_1578e`
- `operator_delegation_preconditions_specified_phase_1578e`
- `operator_delegation_activation_blocker_inventory_complete_phase_1578e`
- `operator_delegation_activation_deferred_phase_1578e`
- `operator_delegation_cdl_gap_recorded_phase_1578e`
