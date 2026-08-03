# ILC ECU Fast-Path Transfer Canon Reconciliation
Version: v0.1
Phase: GAP-ECU-TRANSFER-RC-00
Date: 2026-08-03
Status: committed reconciliation (non-activating)
Governs: CDL-063/CDL-066 ECU transfer boundary, Rust ECUTransfer layout,
         Python pre-submit enforcement strategy, pre-RC scope limits

## 1. CDL-063 - What Was Decided and What Was Rejected

CDL-063 is ratified for ECU directed-commission earmark and bounded debit
semantics. The selected option is `bounded-earmark-with-debit-on-delivery`.
The rejected option set includes `generalized-ecu-transfer`; the constitutional
log records this at CDL-063 with ratified phase 627 and evidence document
`docs/specs/ilc_cdl_063_ecu_directed_commission_ratification_evidence_627_v0.1.md`.

Therefore generalized ECU money transfer is not authorized now, not by this
phase, and not automatically at public RC. CDL-063 authorizes bounded directed
commission/debit coordination, not a wallet-like ECU payment rail.

## 2. CDL-066 - The Fast-Path Authorization

CDL-066 is ratified for an agent sender-authorization envelope for ECU
fast-path transfers. The selected option is a narrow sender-authorization lane
for fast-path transfers, not a generalized transfer redesign. The constitutional
log records ratification at Phase 708 with evidence document
`docs/specs/ilc_cdl_066_agent_sender_authorization_ratification_evidence_708_v0.1.md`.

CDL-066 authorizes a bounded, sender-authorized ECU fast-path surface carried
through Rust `ECUTransfer` and guarded by sender signature. It does not
authorize settled ILC transfer, wallet spend, wallet withdrawal, or generalized
ECU money transfer.

## 3. Rust ECUTransfer Struct - Exact Layout

The current Rust layout in `ilc_consensus/src/types.rs` is:

```rust
pub struct ECUTransfer {
    pub object_ref: ObjectRef,
    pub to: AgentID,
    pub amount_micro_ecu: u64,
    pub transfer_class: TransferClass,
    pub sender_sig: AgentSig,
}
```

`TransferClass` has two variants:

```rust
Contribution
Payment { express: Option<ExpressConsent> }
```

There is no `work_context_ref` field and no `commission_id` field in the Rust
struct. Adding either field would change the Rust consensus wire object and
would require a CDL-066 amendment or successor authority. GAP-ECU-TRANSFER-RC
does not take that route pre-RC.

## 4. SafetyNoDualCert Mechanism

`balance_store.rs` enforces double-spend prevention by locking on
`cert.transfer.object_ref`. `ObjectRef` contains the sender agent and a
monotonic version. A transfer using a given object reference can succeed only
once because the balance store checks the sender object version before applying
the transfer and advances the version after success.

This is the Rust fast-path safety boundary. It is not a Python-layer
work-context guard. Python may reject a malformed intent before submission, but
Rust replay safety is anchored to `object_ref`.

## 5. Python-Layer Enforcement Strategy - Option A

This lane adopts Option A: work-context and graph-anchor requirements are
enforced by a Python pre-submit verifier before any Rust bridge call. Option B
would add graph-context fields to `ECUTransfer`; that would mutate the Rust
struct and require a CDL-066 amendment, so it is not appropriate for this
pre-RC lane.

The Python verifier in later phases must:

- For `Contribution`, require a non-None `graph_context_anchor`.
- For `Payment`, require no graph anchor; express consent remains optional and
  maps to Rust `ExpressConsent`.
- Reject live submission while `ECU_FAST_PATH_TRANSFER_ENABLED` is false.
- Check amount conversion and u64 overflow before passing `amount_micro_ecu` to
  Rust.
- Preserve the Rust `ECUTransfer` field set exactly.

## 6. Ed25519 / COSE Sign1 Constraint

The current ILC Python signing surface uses COSE Sign1 with Ed25519. The
verifier enforces `COSE_ALG_EDDSA = -8`; `cose_sign1_verify()` rejects any
decoded algorithm that is not EdDSA before validating signature length and
cryptographic signature bytes. Initial ECU fast-path sender signatures therefore
must remain Ed25519/COSE Sign1 unless a later SENSITIVE signing-provider phase
authorizes another provider.

## 7. Blocking Token Status

`wallet_transfer_spend_withdrawal_blocked_through_public_rc_phase_1578h` is a
historical default-scope wallet block. It blocks wallet transfer/spend/withdrawal
unless superseded by the dedicated value-action live-RC lane. It does not govern
ECU fast-path transfer directly.

ECU fast-path transfer is gated by the future `ECU_FAST_PATH_TRANSFER_ENABLED`
activation guard. ILC settled transfer is governed by the separate
GAP-VALUE-ACTION-LIVE-RC lane. The historical 1578h token remains in STATUS.md
as a record and must not be deleted by this lane.

## 8. Lane Boundary

In scope for GAP-ECU-TRANSFER-RC-00 through RC-05:

- ECU fast-path transfer under CDL-066 only.
- Python intent schema, context verifier, and adapter.
- Pre-RC adversarial soak.
- Activation gate under a later SENSITIVE human authorization.

Out of scope:

- ILC settled transfer, which belongs to the separate value-action live-RC lane.
- Generalized ECU money transfer, rejected by CDL-063.
- Wallet spend/withdrawal.
- CDL-066 amendment or Rust `ECUTransfer` field mutation.
- Public mirror push, mainnet activation, or public RC activation.

## 9. Non-Claims

- This phase does not open or ratify any CDL.
- This phase does not create or activate runtime code.
- This phase does not change the Rust `ECUTransfer` struct.
- This phase does not close any transfer-enabled gate.
- This phase does not authorize any ECU movement.
- This phase does not change the historical Phase 1578h wallet block token.
- This phase does not push to any public mirror.

## 10. Output Token

`ecu_transfer_canon_reconciliation_committed_phase_gap_ecu_transfer_rc_00`
