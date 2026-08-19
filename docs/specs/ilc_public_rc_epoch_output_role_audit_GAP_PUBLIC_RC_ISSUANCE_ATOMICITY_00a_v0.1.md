# ILC Public RC Epoch Output Role Audit — GAP-PUBLIC-RC-ISSUANCE-ATOMICITY-00a

**Phase:** GAP-PUBLIC-RC-ISSUANCE-ATOMICITY-00a  
**Date:** 2026-08-19  
**Sensitivity:** NON-SENSITIVE  
**Verdict:** PASS as audit baseline; launch-critical runtime gaps are routed to the follow-on issuance-atomicity lane.

## 1. Invariant

This phase names the public-RC issuance conservation invariant:

```text
NO_UNSETTLED_ILC_ISSUANCE:
gross_epoch_value
  = sum(agent_settled_balance_deltas)
  + validator_reward_deltas
  + treasury_settled_delta
  + genesis_settled_delta
  + protocol_reserve_delta
  + carry_forward_out
  - carry_forward_in
```

At public RC, every nonzero computed ILC amount must either be credited to a concrete settled destination or recorded in an explicit non-spendable reserve/carry-forward account. A hash root, quote, canonical event, or audit record is not a spendable balance.

## 2. Direct Findings

### F-1 — Scheduled emission is live as a source event but has no settlement writer

`ilc_core/epoch/epoch_emission_production_path.py` has `PRODUCTION_EMISSION_NOT_ACTIVATED = False`, and emits a `scheduled_emission_pool` canonical economic event from `emission.capped_epoch_budget_ilc`. The same module states that it makes no ledger, wallet, treasury, graph, or external writes.

This is the largest launch-critical gap: current code commits a scheduled-emission event/root, but does not assign the scheduled emission into final balances or reserve/carry-forward state.

### F-2 — Performer/auditor/genesis-overhead pools are currently fee-residual allocations, not scheduled-emission allocations

In the current implementation, `compute_epoch_emission_production_path()` calls:

```python
allocation_quote = build_allocation_distribution_quote(
    epoch,
    fee_burn_quote.remaining_fee_pool_ilc,
    ...
)
```

So the current performer/auditor/genesis-overhead pools are derived from post-CDL-028 fee residuals. They are not currently derived from the CDL-027 scheduled emission amount.

Numerical readback in `.venv`:

```text
scheduled 366640.241162707
genesis_burn 10.000000000
remaining_fee 90.000000000
performer 72.000000000
auditor 13.500000000
genesis_overhead 4.500000000
production_emission_activated True
```

This means any future distribution writer must first decide and encode the correct canonical relationship between CDL-027 scheduled emission and CDL-029 allocation. It must not silently assume the performer/auditor pools already consume scheduled emission.

### F-3 — `genesis_burn_pool` is quote-only and not routed to Genesis

`ilc_core/epoch/fee_burn_split_runtime.py` computes `genesis_burn_pool_ilc = total_epoch_fees_ilc * 0.10`, sets `production_fee_burn_activated=False`, and has no ledger write path.

`ilc_core/epoch/genesis_settlement_destination.py` explicitly records that the CDL-028 `genesis_burn_pool` is not routed to Genesis Agent 1. Therefore the follow-on CDL-028 amendment/protocol-reserve phases are required before any nonzero `genesis_burn_pool` may participate in a public-RC epoch commit.

### F-4 — Genesis Agent 1 has a settlement destination, but no integrated batch writer

`GENESIS_AGENT1_AGENT_ID` is present, `GENESIS_SETTLEMENT_WRITE_AUTHORIZED=True`, and `GENESIS_MINTING_AUTHORIZED=True`; `GENESIS_WALLET_WRITE_AUTHORIZED=False`. This supports settled accounting but not wallet-provider spend authority.

The available `EcuIlcLifecycleRuntime.commit_settled_epoch()` writes one agent wallet/history row at a time. No audited batch writer currently atomically commits Genesis, performer, auditor, validator, treasury, protocol-reserve, and carry-forward outputs together.

The post-audit hardening disposition is stricter: `DISTRIBUTION-WRITER-00` must either wrap all recipient writes and batch metadata in one LMDB write transaction or introduce a settlement batch record with complete/incomplete status that makes crash replay deterministic. Sequential per-recipient calls without a batch record are not acceptable for public RC.

### F-5 — Treasury binding is not required at launch unless the guard is cleared

`TREASURY_DISTRIBUTION_NOT_ACTIVATED=True`, and the treasury production path explicitly says it does not execute transfers, validator payouts, ledger writes, wallet writes, or live settlement. Therefore this phase emits the “not required at launch” treasury token.

If a later phase clears treasury distribution or introduces nonzero treasury settlement deltas, treasury destination binding becomes mandatory before epoch commit.

### F-6 — Validator reward pool is distinct from `genesis_burn_pool`

`validator_reward_pool` is computed as 2% of `write_fee_burn_pool_ilc`, not from `genesis_burn_pool`. This confirms validator reward binding is a separate writer path and should not be solved by the CDL-028 reserve amendment.

### F-7 — CDL-048 is a conversion deadline, not a maturation floor

`CDL048_CONVERSION_DEADLINE_ISSUANCE_EPOCHS = 4`. Registration sets `deadline_epoch = issue_epoch + 4`. Conversion rejects epochs before issue and after deadline, but does not reject conversion at the issue epoch or issue epoch + 1. The ratification evidence frames CDL-048 as anti-hoarding forced circulation.

Therefore public-RC planning must not assume a four-epoch maturation delay. The code evidence supports “maximum deadline,” not “minimum wait.”

### F-8 — Genesis cap inputs are caller-trusted today

`compute_epoch_emission_production_path()` only evaluates the Genesis cap when `genesis_cumulative_accrual_ilc` is supplied. `build_allocation_distribution_quote()` only applies partial-cap allowance when `genesis_overhead_remaining_allowance_ilc` is supplied. Production distribution code must not call these paths with `None`; it must provide authoritative Genesis cumulative accrual and remaining allowance inputs.

### F-9 — Partial-cap and cap-blocked paths need explicit tests before launch

The integration gate scenarios do not exercise `genesis_overhead_remaining_allowance_ilc`. Also, `cap_blocked=True` with nonzero total allocation intentionally raises rather than silently rerouting a full Genesis tranche. The distribution writer must handle this deliberately by computing the correct post-cap allocation inputs and proving partial-cap and cap-blocked cases with regression tests.

## 3. Output Role Table

| Role | Source | Current amount behavior | Current destination | Writer state | Launch disposition |
|---|---|---:|---|---|---|
| `scheduled_emission_pool` | CDL-027 emission quote | Nonzero from epoch 1 | None | Canonical event/root only | BLOCKER for distribution writer; must be consumed by concrete outputs or explicit non-spendable account. |
| `performer_pool` | Current code: post-CDL-028 fee residual × 80% | Nonzero only if fee residual nonzero | None | Quote/root only | Requires distribution writer and eligible-agent/carry-forward semantics. |
| `auditor_pool` | Current code: post-CDL-028 fee residual × 15% | Nonzero only if fee residual nonzero | None | Quote/root only | Requires distribution writer and eligible-agent/carry-forward semantics. |
| `genesis_overhead_pool` | Current code: post-CDL-028 fee residual × 5% plus residual | Nonzero only if fee residual nonzero | Genesis Agent 1 settlement destination exists | No integrated batch writer | Wire via distribution writer with Genesis cap and wallet-spend separation intact. |
| `genesis_burn_pool` | CDL-028 10% fee split | Nonzero only if fees nonzero | Not Genesis; currently permanent-burn semantics | No ledger writer | Requires CDL-028 amendment and protocol-reserve ledger entity. |
| `validator_reward_pool` | CDL-054, 2% of write-fee-burn pool | Fee-driven | Validator destination registry not part of this phase | Distribution not activated | Separate validator writer path; not reserve. |
| `treasury_*` | CDL-047 treasury quote/runtime | Guarded quote only | No live destination required while guarded | `TREASURY_DISTRIBUTION_NOT_ACTIVATED=True` | Not required at launch unless guard clears. |
| `settlement_root` | Canonical economic event batch | Hash, not ILC | N/A | Proof only | Not a balance. |

## 4. Follow-On Requirements

The next phases must close these gaps in order:

1. Amend CDL-028 so `genesis_burn_pool` is a non-circulating protocol reserve, not a permanent deflationary burn.
2. Implement a concrete protocol-reserve ledger destination that cannot transfer, withdraw, or spend at launch.
3. Define carry-forward accounts for unallocated performer/auditor amounts.
4. Implement an atomic distribution writer that consumes scheduled emission, fee-derived pools, reserve deltas, Genesis deltas, validator deltas, treasury deltas if activated, and carry-forward in/out exactly once.
5. Enforce Genesis cap inputs in the production writer: no `None` accrual/allowance values in public-RC settlement.
6. Patch the epoch 0→1 gate to reject any nonzero unassigned amount and to verify the conservation equation after settlement writes.
7. Retain lifecycle hardening: numeric epoch-history ordering and C_MAX balance ceiling must remain covered by tests.

## 5. Tokens

- `epoch_output_role_audit_complete_GAP_PUBLIC_RC_ISSUANCE_ATOMICITY_00a`
- `cdl048_maturation_semantics_verified_GAP_PUBLIC_RC_ISSUANCE_ATOMICITY_00a`
- `treasury_binding_not_required_at_launch_GAP_PUBLIC_RC_ISSUANCE_ATOMICITY_00a`

## 6. Non-Claims

This phase does not amend CDL-028, implement reserve accounts, activate treasury, write ledger balances, run an epoch transition, push a public mirror, authorize public RC, authorize transfers, mint ILC, or mutate any runtime source.
