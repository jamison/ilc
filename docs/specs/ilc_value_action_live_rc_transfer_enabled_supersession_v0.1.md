# ILC Transfer-Enabled Public RC Scope Supersession

**Phase:** GAP-VALUE-ACTION-LIVE-RC-00
**Date:** 2026-08-03
**Status:** supersession record committed
**Sensitivity:** SENSITIVE governance scope record

## Purpose

This document records the human decision to expand public-RC launch scope beyond
the Phase 1578h safe default. Phase 1578h remains historically correct: it
cleared public-RC wallet visibility plus proof-claimability only, and kept
transfer, spend, withdrawal, wallet signing, wallet ledger writes, and
external-address claimability blocked because the separate transfer-enabled GO
phrase had not been issued at that time.

The human has now issued the separate transfer-enabled GO phrase. This record
supersedes the launch-gate force of the 1578h default block without deleting or
reverting the 1578h record.

## Authorizing GO Phrase

```text
TRANSFER-ENABLED RC AUTHORIZED — AGENT-ID ILC TRANSFER + BOUNDED GRAPH-CONTEXTUAL ECU FAST-PATH TRANSFER; NO GENERALIZED ECU MONEY TRANSFER; NO EXTERNAL WITHDRAWAL
```

The phrase is recorded in `docs/phases/STATUS.md` as the positive
authorization for GAP-VALUE-ACTION-LIVE-RC-00.

## Supersession Mechanics

The historical token
`wallet_transfer_spend_withdrawal_blocked_through_public_rc_phase_1578h`
remains in `docs/phases/STATUS.md`. It is not removed, edited, or treated as an
error.

This phase emits the additive supersession token:

```text
transfer_enabled_rc_scope_supersedes_1578h_default_block_GAP_VALUE_ACTION_LIVE_RC_00
```

Downstream gates must interpret these two records together:

- Phase 1578h: correct safe-default wallet gate at the time it ran.
- GAP-VALUE-ACTION-LIVE-RC-00: later human authorization to do the additional
  pre-RC work required for bounded live value movement.

## Newly In Scope For Public RC

The following value movement surfaces are now in public-RC launch scope, subject
to their own implementation, soak, guard, and activation gates:

- AgentID-to-AgentID settled ILC transfer in the Python LMDB settlement layer.
- Local Ed25519/COSE signing only for the public-RC ILC transfer lane.
- Bounded graph/work-contextual ECU fast-path transfers under CDL-066.
- Genesis-sourced value movement only after CDL-110 runtime enforcement is
  implemented by GAP-GENESIS-VALUE-02.

## Still Out Of Scope

The GO phrase and this supersession record do not authorize:

- External wallet adapter transfers.
- Withdrawals to external accounts.
- Marketplace spend.
- secp256k1/EIP-712 live signing runtime.
- Operator fleet transfer authority.
- Generalized ECU money transfer; CDL-063 rejection remains in force.
- `EpochSettlementRecord` mutation to support ILC transfer.
- Any transfer mechanism not explicitly listed as in scope above.
- Public mirror publication.
- Mainnet activation.

## Relationship To Other Lanes

The ILC settled-transfer lane is GAP-VALUE-ACTION-LIVE-RC-01 through
GAP-VALUE-ACTION-LIVE-RC-08. RC-00 only records supersession authority and does
not implement or activate runtime.

The ECU fast-path lane is GAP-ECU-TRANSFER-RC-01 through
GAP-ECU-TRANSFER-RC-05. It remains bounded by CDL-066 and CDL-063: sender
authorization is in scope, generalized ECU money transfer is not.

The Genesis guard lane remains a hard prerequisite for activation:
GAP-GENESIS-VALUE-02 must emit
`genesis_value_guard_runtime_committed_GAP_GENESIS_VALUE_02` before either the
ECU RC-05 or ILC LIVE-RC-08 activation gate may pass.

## Non-Claims

This phase does not activate any transfer capability, does not change any
runtime flag or module, does not revert Phase 1578h, does not remove the 1578h
block token, does not authorize generalized ECU transfer, does not authorize
external withdrawal, does not authorize secp256k1/EIP-712 live runtime, does
not authorize operator fleet transfer, and does not create any `ilc_core/`
runtime file.
