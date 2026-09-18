# ILC First Issuance Disposition Policy — GAP-FIRST-ISSUANCE-DISPOSITION-POLICY-00

**Version:** v0.1
**Date:** 2026-09-18
**Phase:** GAP-FIRST-ISSUANCE-DISPOSITION-POLICY-00
**Sensitivity:** NON-SENSITIVE
**Status:** Confirmed implemented by direct code trace; documentation-only phase

## 1. Zero-User First Monthly Close Behavior

At the first monthly issuance close with zero public user submissions and zero write fees, the distribution writer still has a deterministic disposition for the scheduled monthly emission. The implemented basis is:

```python
    allocatable_current_value = current_emission + fee_burn_quote.remaining_fee_pool_ilc
```

Because write fees are zero, `fee_burn_quote.remaining_fee_pool_ilc` is zero and `allocatable_current_value == current_emission`.

The distribution writer passes that value into the CDL-029 allocation splitter:

```python
    allocation_quote = build_allocation_distribution_quote(
        issuance_epoch,
        allocatable_current_value,
        genesis_overhead_cap_blocked=False,
        genesis_overhead_remaining_allowance_ilc=remaining_allowance,
    )
```

The allocation runtime defines the launch split:

```python
PERFORMER_ALLOCATION_FRACTION = Decimal("0.80")
AUDITOR_ALLOCATION_FRACTION = Decimal("0.15")
GENESIS_OVERHEAD_ALLOCATION_FRACTION = Decimal("0.05")
```

With zero eligible agents, `_allocate_pool_to_agents()` returns no agent deltas and leaves the whole pool unallocated:

```python
def _allocate_pool_to_agents(
    pool: Decimal,
    weights: Mapping[str, Decimal],
) -> tuple[dict[str, Decimal], Decimal]:
    if pool == ZERO:
        return {}, ZERO
    if not weights:
        return {}, pool
    positive_weights = {agent_id: weight for agent_id, weight in weights.items() if weight > ZERO}
    if not positive_weights:
        return {}, pool
```

The unallocated performer and auditor portions become explicit carry-forward records:

```python
def _build_carry_forward_out_records(
    *,
    issuance_epoch: int,
    source_settlement_root: str,
    unallocated_performer: Decimal,
    unallocated_auditor: Decimal,
) -> tuple[PoolCarryForwardRecord, ...]:
    records: list[PoolCarryForwardRecord] = []
    if unallocated_performer > ZERO:
        records.append(
            create_carry_forward_record(
                source_epoch=issuance_epoch,
                target_epoch=issuance_epoch + 1,
                pool_role=PERFORMER_POOL_ROLE,
                amount_ilc=unallocated_performer,
                account_id=PERFORMER_CARRY_FORWARD_ACCOUNT_ID,
                reason="unallocated performer distribution",
                source_settlement_root=source_settlement_root,
            )
        )
    if unallocated_auditor > ZERO:
        records.append(
            create_carry_forward_record(
                source_epoch=issuance_epoch,
                target_epoch=issuance_epoch + 1,
                pool_role=AUDITOR_POOL_ROLE,
                amount_ilc=unallocated_auditor,
                account_id=AUDITOR_CARRY_FORWARD_ACCOUNT_ID,
                reason="unallocated auditor distribution",
                source_settlement_root=source_settlement_root,
            )
        )
    return tuple(records)
```

Local computation using a synthetic structural maturity proof, zero fees, and zero eligible agents produced:

```text
zero_user_compute_pass
current_emission 371609.891246338
remaining_fee_pool 0E-9
genesis_overhead 18580.494562318
protocol_reserve_delta 0E-9
validator_reward_deltas {}
agent_deltas_len 0
carry_forward_count 2
carry_forward performer 297287.912997070 pool:cdl029:performer_unallocated_carry_forward pending_consumption
carry_forward auditor 55741.483686950 pool:cdl029:auditor_unallocated_carry_forward pending_consumption
difference 0E-9
```

This was a local documentation proof only. It did not run `GAP-FIRST-MONTHLY-ISSUANCE-CLOSE-OBSERVE-00`, did not produce or consume a live monthly close proof, and did not write settlement state.

## 2. Non-Evaporation Invariant

The non-evaporation invariant is already implemented. The conservation gate verifies the full double-entry equation before settlement commit:

```python
def verify_epoch_conservation_before_commit(output: EpochDistributionOutput) -> None:
    """Raise unless an epoch distribution output is exactly conserved."""
    if not isinstance(output, EpochDistributionOutput):
        raise ValueError("conservation_gate_requires_epoch_distribution_output")
    if output.conservation_verified is not True:
        raise ValueError(NO_UNSETTLED_ILC_ISSUANCE_GATE_TOKEN)
    record = output.conservation_record
    values = {
        field_name: _require_finite_decimal(getattr(record, field_name, None))
        for field_name in _RECORD_DECIMAL_FIELDS
    }

    expected_total_debit = (
        values["current_emission_ilc"]
        + values["remaining_fee_pool_ilc"]
        + values["genesis_burn_pool_ilc"]
    )
    expected_total_credit = (
        values["agent_settled_balance_deltas_ilc"]
        + values["genesis_settled_delta_ilc"]
        + values["protocol_reserve_delta_ilc"]
        + values["validator_reward_deltas_ilc"]
        + values["treasury_settled_delta_ilc"]
        + values["distribution_carry_forward_out_ilc"]
        - values["distribution_carry_forward_in_ilc"]
        + values["explicit_rounding_sinks_ilc"]
    )
    if values["gross_epoch_value_ilc"] != expected_total_debit:
        raise ValueError(NO_UNSETTLED_ILC_ISSUANCE_GATE_TOKEN)
    if values["total_debit_ilc"] != expected_total_debit:
        raise ValueError(NO_UNSETTLED_ILC_ISSUANCE_GATE_TOKEN)
    if values["total_credit_ilc"] != expected_total_credit:
        raise ValueError(NO_UNSETTLED_ILC_ISSUANCE_GATE_TOKEN)
    if values["difference_ilc"] != values["total_debit_ilc"] - values["total_credit_ilc"]:
        raise ValueError(NO_UNSETTLED_ILC_ISSUANCE_GATE_TOKEN)
    if values["difference_ilc"] != _ZERO:
        raise ValueError(NO_UNSETTLED_ILC_ISSUANCE_GATE_TOKEN)
```

The commit helper calls this gate before any lifecycle write:

```python
def commit_verified_epoch_distribution(
    output: EpochDistributionOutput,
    lifecycle_runtime: EcuIlcLifecycleRuntime | AtomicEpochBatchWriter,
) -> EpochDistributionOutput:
    from ilc_core.epoch.epoch_conservation_gate import verify_epoch_conservation_before_commit

    verify_epoch_conservation_before_commit(output)

    settlements = _settlement_deltas_for_commit(output)
    _require_maturity_before_settlement_commit(output, settlements)
    _commit_settled_epoch_batch(
        lifecycle_runtime=lifecycle_runtime,
        settlements=settlements,
        epoch_id=output.epoch_id,
    )
    return output
```

Uninfluenceable ILC property confirmed: every emitted ILC quantum has a deterministic, non-discretionary disposition path. At zero-user first close, no operator chooses recipients or reroutes funds. The code routes scheduled emission into Genesis overhead plus explicit performer/auditor carry-forward records, then fails closed unless the conservation equation balances exactly.

## 3. Validator Reward at Launch (CDL-054)

CDL-054 validator reward is not sourced from the CDL-028 `genesis_burn_pool`. The prior output-role audit records:

```text
`validator_reward_pool` is computed as 2% of `write_fee_burn_pool_ilc`, not from `genesis_burn_pool`. This confirms validator reward binding is a separate writer path and should not be solved by the CDL-028 reserve amendment.
```

The validator reward routing runtime confirms the source and activation guard:

```python
VALIDATOR_REWARD_FRACTION_OF_WRITE_FEE_BURN = Decimal("0.02")
VALIDATOR_REWARD_POOL_LABEL = "validator_reward_pool"
WRITE_FEE_BURN_POOL_LABEL = "write_fee_burn_pool"
```

```python
    validator_reward_pool = _quantize_ilc(write_fee_burn_pool * fraction)
```

```python
        production_validator_reward_distribution_activated=False,
        decision_token=VALIDATOR_REWARD_DISTRIBUTION_NOT_ACTIVATED_TOKEN,
```

At launch, public write fees are zero, so the validator reward pool is zero. The current distribution writer also explicitly emits no validator reward deltas:

```python
        validator_reward_deltas={},
```

The distribution writer currently routes the CDL-028 `genesis_burn_pool` to the protocol reserve:

```python
        protocol_reserve_delta=fee_burn_quote.genesis_burn_pool_ilc,
```

This is a planned carry-forward, not a current implementation gap. No non-evaporation violation exists at launch. When CDL-054 activates and nonzero write fees exist, the distribution writer will need a separately audited update that adds `validator_reward_deltas` from the write-fee-burn pool while preserving the protocol-reserve / fee-burn semantics.

## 4. Carry-Forward Accounts

Carry-forward accounts are explicit protocol accounts, not implicit evaporation:

```python
PERFORMER_CARRY_FORWARD_ACCOUNT_ID = "pool:cdl029:performer_unallocated_carry_forward"
AUDITOR_CARRY_FORWARD_ACCOUNT_ID = "pool:cdl029:auditor_unallocated_carry_forward"

CARRY_FORWARD_TRANSFER_ENABLED = False
CARRY_FORWARD_WITHDRAWAL_ENABLED = False
CARRY_FORWARD_CLAIM_ENABLED = False
CARRY_FORWARD_SPEND_ENABLED = False
```

The record structure is:

```python
@dataclass(frozen=True)
class PoolCarryForwardRecord:
    source_epoch: int
    target_epoch: int
    pool_role: str
    amount_ilc: Decimal
    account_id: str
    reason: str
    source_settlement_root: str
    status: str
    consumed_at_epoch: int | None

    def __post_init__(self) -> None:
        _validate_record(self)

    def to_canonical_record(self) -> dict[str, Any]:
        return {
            "account_id": self.account_id,
            "amount_ilc": decimal_to_canonical_string(self.amount_ilc),
            "cdl_029_allocation_dependency": CDL_029_ALLOCATION_DEPENDENCY,
            "consumed_at_epoch": self.consumed_at_epoch,
            "pool_role": self.pool_role,
            "reason": self.reason,
            "runtime_version": POOL_CARRY_FORWARD_RUNTIME_VERSION,
            "source_epoch": self.source_epoch,
            "source_settlement_root": self.source_settlement_root,
            "status": self.status,
            "target_epoch": self.target_epoch,
        }
```

Carry-forward records require positive Decimal amounts, source and target epochs, role-bound account IDs, a source settlement root, and `pending_consumption` or `consumed` status. Zero-user close therefore records performer/auditor value into persistent nonspendable carry-forward accounts rather than losing it.

Genesis overhead is credited immediately when settlement is mature and authorized. Performer and auditor portions wait in carry-forward until eligible agents appear and the later distribution path consumes those records exactly once.

## 5. Implementation Evidence Summary

| Invariant | Enforced by | File:line |
|---|---|---|
| Non-evaporation | `verify_epoch_conservation_before_commit()` | `ilc_core/epoch/epoch_conservation_gate.py:51` |
| Conservation before write | `commit_verified_epoch_distribution()` calls the conservation gate before settlement batch commit | `ilc_core/epoch/epoch_distribution_writer.py:347` |
| Allocation basis | `allocatable_current_value = current_emission + fee_burn_quote.remaining_fee_pool_ilc` | `ilc_core/epoch/epoch_distribution_writer.py:250` |
| Zero-agent carry-forward | `_allocate_pool_to_agents()` returns the unallocated pool when weights are empty | `ilc_core/epoch/epoch_distribution_writer.py:611` |
| Carry-forward records | `_build_carry_forward_out_records()` | `ilc_core/epoch/epoch_distribution_writer.py:662` |
| Genesis overhead | 5% of allocatable value through `GENESIS_OVERHEAD_ALLOCATION_FRACTION = Decimal("0.05")` | `ilc_core/epoch/allocation_distributor_runtime.py:79` |
| Validator reward at launch | CDL-054 default-off and fee-driven; zero when write fees are zero | `ilc_core/epoch/validator_reward_pool_routing_runtime.py:55`, `ilc_core/epoch/validator_reward_pool_routing_runtime.py:267` |

## 6. Non-Claims

This document does not execute `GAP-FIRST-MONTHLY-ISSUANCE-CLOSE-OBSERVE-00`, does not create or consume a live `MonthlyIssuanceMaturityProof`, does not write LMDB, does not advance an epoch, does not change any runtime module, does not activate CDL-054, does not clear validator reward distribution, does not mint ECU, does not settle ILC, does not retarget packages, and does not push the public mirror.
