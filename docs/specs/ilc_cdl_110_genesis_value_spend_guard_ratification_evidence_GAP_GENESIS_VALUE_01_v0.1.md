# CDL-110 Ratification Evidence - Genesis Value-Path Spend Guard Authority

**Phase:** GAP-GENESIS-VALUE-01
**Date:** 2026-08-03
**Status:** ratified

## Ratification Basis

The human issued the exact sensitive GO phrase:

```text
GO Phase GAP-GENESIS-VALUE-01 GENESIS-VALUE-GUARD-CDL-RATIFY
```

`docs/phases/STATUS.md` records that GO before CDL text was drafted.

GAP-GENESIS-VALUE-00 established the problem statement: Genesis has settlement
and minting accounting authority, but no Genesis-specific policy certificate
exists for direct ECU or ILC transfer submission. The audit also confirmed that
Plate 3 recovery material is recovery custody only and must not be repurposed as
online spend authorization.

## Dependency Chain

| Dependency | Status used by ratification |
|---|---|
| CDL-002 | Ratified root/delegated/session credential distinction. |
| CDL-063 | Ratified bounded ECU earmark/debit semantics; generalized ECU transfer rejected. |
| CDL-066 | Ratified narrow sender-authorization lane for ECU fast-path transfer. |
| CDL-069 | Ratified PQ root plus epoch endorsement model; long-range reconciliation target. |
| CDL-109 | Ratified Werner economic bridge; CDL-110 is the next numbered CDL and does not amend CDL-109. |
| GAP-GENESIS-VALUE-00 | Read-only audit complete; output token `genesis_value_guard_audit_complete_GAP_GENESIS_VALUE_00` present. |

## Ratified Scope

CDL-110 ratifies `GenesisValueActionPolicyCertificate` as the Genesis-scoped
policy artifact required before Genesis-sourced ECU or ILC value movement can
be accepted by public-RC transfer paths.

The ratified public-RC profile is:

| Parameter | Value |
|---|---|
| `network_id` | `ilc-rc01` |
| policy window | inclusive epoch range, maximum 4 epochs |
| guardian signature profile | 2-of-3 dedicated Ed25519 COSE_Sign1 guardian signatures |
| recipient policy | `graph_context_required` |
| action classes | `CONTRIBUTION`, `PAYMENT` |
| ECU per-transfer cap | `1_000_000_000` micro-ECU |
| ECU per-epoch cap | `5_000_000_000` micro-ECU |
| ILC per-transfer cap | `1_000_000_000` micro-ILC |
| ILC per-epoch cap | `5_000_000_000` micro-ILC |
| nonce domain | `ilc:genesis-value-action:v1` |

## Custody Boundary

The ratification permanently records that Plate 3 recovery shares are
recovery-only. They are not transfer keys, spend co-signers, guardian keys,
wallet keys, or runtime session keys. If Genesis value movement uses threshold
approval, the threshold comes from the separate Genesis value guardian key set.

## Activation Boundary

This ratification is schema and authority only. GAP-GENESIS-VALUE-02 must add
runtime enforcement after the ILC transfer verifier surface exists. RC-05 and
LIVE-RC-08 remain blocked until the runtime token
`genesis_value_guard_runtime_committed_GAP_GENESIS_VALUE_02` is present.

## Non-Claims

This phase does not change `ECU_FAST_PATH_TRANSFER_ENABLED`,
`ILC_TRANSFER_ENABLED`, `GENESIS_WALLET_WRITE_AUTHORIZED`, Rust consensus
structs, wallet spend authority, external withdrawal support, production
minting, production settlement, public RC, mainnet, or public mirror state.

## Ratification Tokens

```text
genesis_value_action_policy_cdl_ratified_GAP_GENESIS_VALUE_01
cdl_110_genesis_value_spend_guard_ratified
```
