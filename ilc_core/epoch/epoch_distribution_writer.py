# SPDX-License-Identifier: AGPL-3.0-only
"""Atomic public-RC epoch distribution writer.

C-1 atomicity strategy: ``LmdbWalletStore.put_wallet`` and
``put_wallet_history`` are separate write transactions, so this module does not
call them one-by-one for the production lifecycle runtime. When committing
through ``EcuIlcLifecycleRuntime`` backed by ``LmdbWalletStore``, all wallet and
history rows for one epoch are written in one LMDB write transaction. Alternate
test/runtime objects must expose ``commit_settled_epoch_batch``; otherwise this
module fails closed with ``atomic_lifecycle_batch_writer_required``.

    Carry-forward consumption is atomic ledger movement. Consumed carry-forward
    records create negative settlement deltas against their nonspendable
    carry-forward accounts in the same LMDB transaction that credits newly eligible
    recipients. Negative deltas are rejected for every other account class.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation, ROUND_DOWN
from typing import Any, Mapping, Protocol

from ilc_core.epoch.allocation_distributor_runtime import (
    EpochAllocationDistributionQuote,
    build_allocation_distribution_quote,
)
from ilc_core.epoch.epoch_emission_production_path import GENESIS_FIXED_TRANCHE_ILC
from ilc_core.epoch.epoch_emission_runtime import (
    C_MAX_ILC,
    ILC_QUANTUM,
    EpochEmissionQuote,
    build_epoch_emission_quote,
)
from ilc_core.epoch.fee_burn_split_runtime import (
    EpochFeeBurnSplitQuote,
    build_fee_burn_split_quote,
)
from ilc_core.epoch.genesis_settlement_destination import GENESIS_AGENT1_AGENT_ID
from ilc_core.epoch.pool_carry_forward_runtime import (
    AUDITOR_CARRY_FORWARD_ACCOUNT_ID,
    AUDITOR_POOL_ROLE,
    PERFORMER_CARRY_FORWARD_ACCOUNT_ID,
    PERFORMER_POOL_ROLE,
    PoolCarryForwardRecord,
    create_carry_forward_record,
    mark_carry_forward_consumed,
)
from ilc_core.epoch.protocol_reserve_destination import PROTOCOL_RESERVE_ACCOUNT_ID
from ilc_core.epoch.treasury_validator_reward_production_path import (
    TREASURY_DISTRIBUTION_NOT_ACTIVATED,
)
from ilc_core.epoch.validator_reward_pool_routing_runtime import (
    VALIDATOR_REWARD_DISTRIBUTION_NOT_ACTIVATED_TOKEN,
)
from ilc_core.ledger.ecu_ilc_lifecycle_runtime import (
    EcuIlcLifecycleRuntime,
    EcuIlcLifecycleRuntimeError,
    LIFECYCLE_BALANCE_EXCEEDS_C_MAX_TOKEN,
    _epoch_history_sort_key,
    _stable_digest,
)
from ilc_core.ledger.exact_numeric import (
    ZERO,
    decimal_to_canonical_string,
    parse_non_negative_decimal,
    to_decimal,
)
from ilc_core.storage.lmdb_public_runtime import (
    LmdbWalletStore,
    _decode_json,
    _encode_json,
    _encode_key,
)


EPOCH_DISTRIBUTION_WRITER_VERSION = (
    "epoch_distribution_writer_GAP_PUBLIC_RC_DISTRIBUTION_WRITER_00.v0.1"
)
EPOCH_ID_FORMAT = "{:010d}"
ATOMIC_SETTLEMENT_WRITER_CREATED_TOKEN = (
    "atomic_settlement_writer_created_GAP_PUBLIC_RC_DISTRIBUTION_WRITER_00"
)
CONSERVATION_EQUATION_ENFORCED_TOKEN = (
    "conservation_equation_enforced_GAP_PUBLIC_RC_DISTRIBUTION_WRITER_00"
)
GENESIS_CAP_ALWAYS_SUPPLIED_TOKEN = (
    "genesis_cap_always_supplied_GAP_PUBLIC_RC_DISTRIBUTION_WRITER_00"
)
PROTOCOL_RESERVE_WIRED_TOKEN = (
    "protocol_reserve_wired_GAP_PUBLIC_RC_DISTRIBUTION_WRITER_00"
)
CARRY_FORWARD_CONSUMED_EXACTLY_ONCE_WIRED_TOKEN = (
    "carry_forward_consumed_exactly_once_wired_GAP_PUBLIC_RC_DISTRIBUTION_WRITER_00"
)
EPOCH_ID_ZERO_PADDED_FORMAT_LOCKED_TOKEN = (
    "epoch_id_zero_padded_format_locked_GAP_PUBLIC_RC_DISTRIBUTION_WRITER_00"
)

MAX_AGENT_ID_BYTES = 256
DEFAULT_SOURCE_SETTLEMENT_ROOT_HEX = "0" * 64


class AtomicEpochBatchWriter(Protocol):
    def commit_settled_epoch_batch(
        self,
        *,
        settlements: Mapping[str, Decimal],
        epoch_id: str,
    ) -> list[dict[str, Any]]:
        ...


@dataclass(frozen=True)
class EpochDistributionInput:
    issuance_epoch: int
    total_epoch_fees_ilc: Decimal | int | str
    genesis_cumulative_accrual_ilc: Decimal | int | str
    eligible_agents: Mapping[str, Decimal | int | str]
    prior_carry_forward_records: tuple[PoolCarryForwardRecord, ...] | list[PoolCarryForwardRecord]
    cumulative_issued_before_epoch_ilc: Decimal | int | str = ZERO
    eligible_auditor_agents: Mapping[str, Decimal | int | str] | None = None
    source_settlement_root_hex: str = DEFAULT_SOURCE_SETTLEMENT_ROOT_HEX


@dataclass(frozen=True)
class EpochDistributionConservationRecord:
    gross_epoch_value_ilc: Decimal
    current_emission_ilc: Decimal
    remaining_fee_pool_ilc: Decimal
    genesis_burn_pool_ilc: Decimal
    agent_settled_balance_deltas_ilc: Decimal
    genesis_settled_delta_ilc: Decimal
    protocol_reserve_delta_ilc: Decimal
    validator_reward_deltas_ilc: Decimal
    treasury_settled_delta_ilc: Decimal
    distribution_carry_forward_out_ilc: Decimal
    distribution_carry_forward_in_ilc: Decimal
    explicit_rounding_sinks_ilc: Decimal
    total_debit_ilc: Decimal
    total_credit_ilc: Decimal
    difference_ilc: Decimal

    def to_canonical_record(self) -> dict[str, str]:
        return {
            "agent_settled_balance_deltas_ilc": _decimal_string(
                self.agent_settled_balance_deltas_ilc
            ),
            "current_emission_ilc": _decimal_string(self.current_emission_ilc),
            "difference_ilc": _decimal_string(self.difference_ilc),
            "distribution_carry_forward_in_ilc": _decimal_string(
                self.distribution_carry_forward_in_ilc
            ),
            "distribution_carry_forward_out_ilc": _decimal_string(
                self.distribution_carry_forward_out_ilc
            ),
            "explicit_rounding_sinks_ilc": _decimal_string(self.explicit_rounding_sinks_ilc),
            "genesis_burn_pool_ilc": _decimal_string(self.genesis_burn_pool_ilc),
            "genesis_settled_delta_ilc": _decimal_string(self.genesis_settled_delta_ilc),
            "gross_epoch_value_ilc": _decimal_string(self.gross_epoch_value_ilc),
            "protocol_reserve_delta_ilc": _decimal_string(self.protocol_reserve_delta_ilc),
            "remaining_fee_pool_ilc": _decimal_string(self.remaining_fee_pool_ilc),
            "total_credit_ilc": _decimal_string(self.total_credit_ilc),
            "total_debit_ilc": _decimal_string(self.total_debit_ilc),
            "treasury_settled_delta_ilc": _decimal_string(self.treasury_settled_delta_ilc),
            "validator_reward_deltas_ilc": _decimal_string(self.validator_reward_deltas_ilc),
        }


@dataclass(frozen=True)
class EpochDistributionOutput:
    runtime_version: str
    issuance_epoch: int
    epoch_id: str
    emission_quote: EpochEmissionQuote | None
    fee_burn_quote: EpochFeeBurnSplitQuote
    allocation_quote: EpochAllocationDistributionQuote
    genesis_overhead_remaining_allowance_ilc: Decimal
    agent_settled_balance_deltas: dict[str, Decimal]
    genesis_settled_delta: Decimal
    protocol_reserve_delta: Decimal
    validator_reward_deltas: dict[str, Decimal]
    treasury_settled_delta: Decimal
    carry_forward_out_records: tuple[PoolCarryForwardRecord, ...]
    consumed_carry_forward_records: tuple[PoolCarryForwardRecord, ...]
    conservation_record: EpochDistributionConservationRecord
    conservation_verified: bool
    decision_tokens: tuple[str, ...]


def compute_epoch_distribution(inputs: EpochDistributionInput) -> EpochDistributionOutput:
    resolved = _require_inputs(inputs)
    issuance_epoch = resolved["issuance_epoch"]
    epoch_id = format_epoch_id(issuance_epoch)
    total_fees = resolved["total_epoch_fees_ilc"]
    genesis_accrual = resolved["genesis_cumulative_accrual_ilc"]
    cumulative_issued_before_epoch = resolved["cumulative_issued_before_epoch_ilc"]
    source_settlement_root = resolved["source_settlement_root_hex"]

    fee_burn_quote = build_fee_burn_split_quote(issuance_epoch, total_fees)
    emission_quote: EpochEmissionQuote | None = None
    current_emission = ZERO
    if issuance_epoch > 0:
        emission_quote = build_epoch_emission_quote(
            issuance_epoch - 1,
            cumulative_issued_before_epoch,
        )
        current_emission = emission_quote.capped_epoch_budget_ilc

    remaining_allowance = _genesis_remaining_allowance(genesis_accrual)
    allocatable_current_value = current_emission + fee_burn_quote.remaining_fee_pool_ilc
    allocation_quote = build_allocation_distribution_quote(
        issuance_epoch,
        allocatable_current_value,
        genesis_overhead_cap_blocked=False,
        genesis_overhead_remaining_allowance_ilc=remaining_allowance,
    )

    prior_records = _require_prior_carry_forward_records(
        resolved["prior_carry_forward_records"],
        issuance_epoch,
    )
    prior_by_role = _sum_prior_carry_forward_by_role(prior_records)
    available_performer_pool = (
        allocation_quote.performer_reward_pool_ilc + prior_by_role[PERFORMER_POOL_ROLE]
    )
    available_auditor_pool = (
        allocation_quote.auditor_reward_pool_ilc + prior_by_role[AUDITOR_POOL_ROLE]
    )

    performer_allocations, unallocated_performer = _allocate_pool_to_agents(
        available_performer_pool,
        resolved["eligible_agents"],
    )
    auditor_weights = (
        resolved["eligible_auditor_agents"]
        if resolved["eligible_auditor_agents"] is not None
        else resolved["eligible_agents"]
    )
    auditor_allocations, unallocated_auditor = _allocate_pool_to_agents(
        available_auditor_pool,
        auditor_weights,
    )
    agent_deltas = _merge_agent_allocations(performer_allocations, auditor_allocations)

    carry_forward_out_records = _build_carry_forward_out_records(
        issuance_epoch=issuance_epoch,
        source_settlement_root=source_settlement_root,
        unallocated_performer=unallocated_performer,
        unallocated_auditor=unallocated_auditor,
    )
    consumed_records = tuple(
        mark_carry_forward_consumed(record, consumed_at_epoch=issuance_epoch)
        for record in prior_records
    )

    conservation = _build_conservation_record(
        current_emission=current_emission,
        remaining_fee_pool=fee_burn_quote.remaining_fee_pool_ilc,
        genesis_burn_pool=fee_burn_quote.genesis_burn_pool_ilc,
        agent_deltas=agent_deltas,
        genesis_delta=allocation_quote.genesis_overhead_pool_ilc,
        reserve_delta=fee_burn_quote.genesis_burn_pool_ilc,
        carry_forward_out=sum((record.amount_ilc for record in carry_forward_out_records), ZERO),
        carry_forward_in=sum((record.amount_ilc for record in prior_records), ZERO),
    )
    _verify_conservation(conservation)

    return EpochDistributionOutput(
        runtime_version=EPOCH_DISTRIBUTION_WRITER_VERSION,
        issuance_epoch=issuance_epoch,
        epoch_id=epoch_id,
        emission_quote=emission_quote,
        fee_burn_quote=fee_burn_quote,
        allocation_quote=allocation_quote,
        genesis_overhead_remaining_allowance_ilc=remaining_allowance,
        agent_settled_balance_deltas=agent_deltas,
        genesis_settled_delta=allocation_quote.genesis_overhead_pool_ilc,
        protocol_reserve_delta=fee_burn_quote.genesis_burn_pool_ilc,
        validator_reward_deltas={},
        treasury_settled_delta=ZERO,
        carry_forward_out_records=carry_forward_out_records,
        consumed_carry_forward_records=consumed_records,
        conservation_record=conservation,
        conservation_verified=True,
        decision_tokens=(
            ATOMIC_SETTLEMENT_WRITER_CREATED_TOKEN,
            CONSERVATION_EQUATION_ENFORCED_TOKEN,
            GENESIS_CAP_ALWAYS_SUPPLIED_TOKEN,
            PROTOCOL_RESERVE_WIRED_TOKEN,
            CARRY_FORWARD_CONSUMED_EXACTLY_ONCE_WIRED_TOKEN,
            EPOCH_ID_ZERO_PADDED_FORMAT_LOCKED_TOKEN,
            VALIDATOR_REWARD_DISTRIBUTION_NOT_ACTIVATED_TOKEN,
        ),
    )


def commit_epoch_distribution(
    inputs: EpochDistributionInput,
    lifecycle_runtime: EcuIlcLifecycleRuntime | AtomicEpochBatchWriter,
) -> EpochDistributionOutput:
    output = compute_epoch_distribution(inputs)
    if not output.conservation_verified:
        raise ValueError("epoch_distribution_conservation_not_verified")

    settlements = _settlement_deltas_for_commit(output)
    if settlements:
        _commit_settled_epoch_batch(
            lifecycle_runtime=lifecycle_runtime,
            settlements=settlements,
            epoch_id=output.epoch_id,
        )
    return output


def format_epoch_id(issuance_epoch: int) -> str:
    epoch = _require_epoch(issuance_epoch, "issuance_epoch")
    if epoch > 9_999_999_999:
        raise ValueError("issuance_epoch_exceeds_zero_padded_width")
    return EPOCH_ID_FORMAT.format(epoch)


def _require_inputs(inputs: EpochDistributionInput) -> dict[str, Any]:
    if not isinstance(inputs, EpochDistributionInput):
        raise ValueError("epoch_distribution_input_required")
    if inputs.genesis_cumulative_accrual_ilc is None:
        raise ValueError("genesis_cumulative_accrual_ilc_required")
    if TREASURY_DISTRIBUTION_NOT_ACTIVATED is not True:
        raise ValueError("treasury_distribution_guard_cleared_without_writer_update")
    return {
        "issuance_epoch": _require_epoch(inputs.issuance_epoch, "issuance_epoch"),
        "total_epoch_fees_ilc": _require_non_negative_ilc(
            inputs.total_epoch_fees_ilc,
            "total_epoch_fees_ilc",
        ),
        "genesis_cumulative_accrual_ilc": _require_non_negative_ilc(
            inputs.genesis_cumulative_accrual_ilc,
            "genesis_cumulative_accrual_ilc",
        ),
        "cumulative_issued_before_epoch_ilc": _require_non_negative_ilc(
            inputs.cumulative_issued_before_epoch_ilc,
            "cumulative_issued_before_epoch_ilc",
        ),
        "eligible_agents": _require_weight_mapping(inputs.eligible_agents, "eligible_agents"),
        "eligible_auditor_agents": (
            None
            if inputs.eligible_auditor_agents is None
            else _require_weight_mapping(inputs.eligible_auditor_agents, "eligible_auditor_agents")
        ),
        "prior_carry_forward_records": _require_prior_record_container(
            inputs.prior_carry_forward_records
        ),
        "source_settlement_root_hex": _require_settlement_root(inputs.source_settlement_root_hex),
    }


def _require_epoch(value: object, field_name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"{field_name}_must_be_non_negative_int")
    return value


def _require_non_negative_ilc(value: object, field_name: str) -> Decimal:
    if isinstance(value, bool) or isinstance(value, float):
        raise ValueError(f"{field_name}_must_be_exact_decimal")
    try:
        amount = value if isinstance(value, Decimal) else Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise ValueError(f"{field_name}_must_be_exact_decimal") from exc
    if not amount.is_finite():
        raise ValueError(f"{field_name}_must_be_finite")
    if amount < ZERO:
        raise ValueError(f"{field_name}_must_be_non_negative")
    if amount % ILC_QUANTUM != ZERO:
        raise ValueError(f"{field_name}_must_align_to_ilc_quantum")
    return amount


def _require_weight_mapping(
    value: Mapping[str, Decimal | int | str],
    field_name: str,
) -> dict[str, Decimal]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{field_name}_must_be_mapping")
    normalized: dict[str, Decimal] = {}
    for agent_id, raw_weight in value.items():
        normalized[_require_agent_id(agent_id)] = _require_non_negative_weight(
            raw_weight,
            f"{field_name}_weight",
        )
    return dict(sorted(normalized.items()))


def _require_non_negative_weight(value: object, field_name: str) -> Decimal:
    if isinstance(value, bool) or isinstance(value, float):
        raise ValueError(f"{field_name}_must_be_exact_decimal")
    try:
        weight = value if isinstance(value, Decimal) else Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise ValueError(f"{field_name}_must_be_exact_decimal") from exc
    if not weight.is_finite():
        raise ValueError(f"{field_name}_must_be_finite")
    if weight < ZERO:
        raise ValueError(f"{field_name}_must_be_non_negative")
    return weight


def _require_agent_id(value: object) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("eligible_agent_id_required")
    if len(value.encode("utf-8")) > MAX_AGENT_ID_BYTES:
        raise ValueError("eligible_agent_id_exceeds_max_bytes")
    return value


def _require_settlement_root(value: object) -> str:
    if not isinstance(value, str) or len(value) != 64:
        raise ValueError("source_settlement_root_must_be_sha256_hex")
    if any(char not in "0123456789abcdef" for char in value):
        raise ValueError("source_settlement_root_must_be_sha256_hex")
    return value


def _require_prior_record_container(value: object) -> tuple[PoolCarryForwardRecord, ...]:
    if not isinstance(value, (list, tuple)):
        raise ValueError("prior_carry_forward_records_must_be_sequence")
    return tuple(value)


def _genesis_remaining_allowance(genesis_cumulative_accrual_ilc: Decimal) -> Decimal:
    if genesis_cumulative_accrual_ilc > C_MAX_ILC:
        raise ValueError("genesis_cumulative_accrual_exceeds_c_max")
    remaining = GENESIS_FIXED_TRANCHE_ILC - genesis_cumulative_accrual_ilc
    return remaining if remaining > ZERO else ZERO


def _require_prior_carry_forward_records(
    records: tuple[PoolCarryForwardRecord, ...],
    issuance_epoch: int,
) -> tuple[PoolCarryForwardRecord, ...]:
    normalized: list[PoolCarryForwardRecord] = []
    seen: set[tuple[int, str, str, Decimal]] = set()
    for record in records:
        if not isinstance(record, PoolCarryForwardRecord):
            raise ValueError("prior_carry_forward_record_required")
        if record.status != "pending_consumption":
            raise ValueError("prior_carry_forward_record_must_be_pending")
        if record.target_epoch > issuance_epoch:
            raise ValueError("prior_carry_forward_target_epoch_not_reached")
        key = (
            record.source_epoch,
            record.pool_role,
            record.source_settlement_root,
            record.amount_ilc,
        )
        if key in seen:
            raise ValueError("prior_carry_forward_record_duplicate")
        seen.add(key)
        normalized.append(record)
    return tuple(normalized)


def _sum_prior_carry_forward_by_role(
    records: tuple[PoolCarryForwardRecord, ...],
) -> dict[str, Decimal]:
    totals = {PERFORMER_POOL_ROLE: ZERO, AUDITOR_POOL_ROLE: ZERO}
    for record in records:
        totals[record.pool_role] += record.amount_ilc
    return totals


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

    total_weight = sum(positive_weights.values(), ZERO)
    total_quanta = int(pool / ILC_QUANTUM)
    allocations_quanta: dict[str, int] = {}
    allocated_quanta = 0
    for agent_id, weight in sorted(positive_weights.items()):
        share_quanta = int((Decimal(total_quanta) * weight / total_weight).to_integral_value(rounding=ROUND_DOWN))
        allocations_quanta[agent_id] = share_quanta
        allocated_quanta += share_quanta

    remaining_quanta = total_quanta - allocated_quanta
    for agent_id in sorted(allocations_quanta):
        if remaining_quanta <= 0:
            break
        allocations_quanta[agent_id] += 1
        remaining_quanta -= 1

    allocations = {
        agent_id: ILC_QUANTUM * quanta
        for agent_id, quanta in allocations_quanta.items()
        if quanta > 0
    }
    allocated = sum(allocations.values(), ZERO)
    return allocations, pool - allocated


def _merge_agent_allocations(
    first: Mapping[str, Decimal],
    second: Mapping[str, Decimal],
) -> dict[str, Decimal]:
    merged: dict[str, Decimal] = {}
    for source in (first, second):
        for agent_id, amount in source.items():
            if amount == ZERO:
                continue
            merged[agent_id] = merged.get(agent_id, ZERO) + amount
    return dict(sorted(merged.items()))


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


def _build_conservation_record(
    *,
    current_emission: Decimal,
    remaining_fee_pool: Decimal,
    genesis_burn_pool: Decimal,
    agent_deltas: Mapping[str, Decimal],
    genesis_delta: Decimal,
    reserve_delta: Decimal,
    carry_forward_out: Decimal,
    carry_forward_in: Decimal,
) -> EpochDistributionConservationRecord:
    agent_total = sum(agent_deltas.values(), ZERO)
    validator_total = ZERO
    treasury_total = ZERO
    rounding_sinks = ZERO
    gross = current_emission + remaining_fee_pool + genesis_burn_pool
    credit = (
        agent_total
        + genesis_delta
        + reserve_delta
        + validator_total
        + treasury_total
        + carry_forward_out
        - carry_forward_in
        + rounding_sinks
    )
    return EpochDistributionConservationRecord(
        gross_epoch_value_ilc=gross,
        current_emission_ilc=current_emission,
        remaining_fee_pool_ilc=remaining_fee_pool,
        genesis_burn_pool_ilc=genesis_burn_pool,
        agent_settled_balance_deltas_ilc=agent_total,
        genesis_settled_delta_ilc=genesis_delta,
        protocol_reserve_delta_ilc=reserve_delta,
        validator_reward_deltas_ilc=validator_total,
        treasury_settled_delta_ilc=treasury_total,
        distribution_carry_forward_out_ilc=carry_forward_out,
        distribution_carry_forward_in_ilc=carry_forward_in,
        explicit_rounding_sinks_ilc=rounding_sinks,
        total_debit_ilc=gross,
        total_credit_ilc=credit,
        difference_ilc=gross - credit,
    )


def _verify_conservation(record: EpochDistributionConservationRecord) -> None:
    if record.difference_ilc != ZERO:
        raise ValueError("epoch_distribution_conservation_mismatch")


def _settlement_deltas_for_commit(output: EpochDistributionOutput) -> dict[str, Decimal]:
    settlements = dict(output.agent_settled_balance_deltas)
    if output.genesis_settled_delta > ZERO:
        settlements[GENESIS_AGENT1_AGENT_ID] = (
            settlements.get(GENESIS_AGENT1_AGENT_ID, ZERO) + output.genesis_settled_delta
        )
    if output.protocol_reserve_delta > ZERO:
        settlements[PROTOCOL_RESERVE_ACCOUNT_ID] = (
            settlements.get(PROTOCOL_RESERVE_ACCOUNT_ID, ZERO) + output.protocol_reserve_delta
        )
    for record in output.carry_forward_out_records:
        settlements[record.account_id] = settlements.get(record.account_id, ZERO) + record.amount_ilc
    for record in output.consumed_carry_forward_records:
        settlements[record.account_id] = settlements.get(record.account_id, ZERO) - record.amount_ilc
    return {
        agent_id: amount
        for agent_id, amount in sorted(settlements.items())
        if amount != ZERO
    }


def _commit_settled_epoch_batch(
    *,
    lifecycle_runtime: EcuIlcLifecycleRuntime | AtomicEpochBatchWriter,
    settlements: Mapping[str, Decimal],
    epoch_id: str,
) -> list[dict[str, Any]]:
    batch_method = getattr(lifecycle_runtime, "commit_settled_epoch_batch", None)
    if callable(batch_method):
        return batch_method(settlements=dict(settlements), epoch_id=epoch_id)
    if isinstance(lifecycle_runtime, EcuIlcLifecycleRuntime):
        return _commit_lmdb_lifecycle_batch(
            lifecycle_runtime=lifecycle_runtime,
            settlements=settlements,
            epoch_id=epoch_id,
        )
    raise ValueError("atomic_lifecycle_batch_writer_required")


def _commit_lmdb_lifecycle_batch(
    *,
    lifecycle_runtime: EcuIlcLifecycleRuntime,
    settlements: Mapping[str, Decimal],
    epoch_id: str,
) -> list[dict[str, Any]]:
    wallet_store = lifecycle_runtime.wallet_store
    if not isinstance(wallet_store, LmdbWalletStore):
        raise ValueError("atomic_lmdb_wallet_store_required")
    results: list[dict[str, Any]] = []
    wallets_db = wallet_store._dbs[b"wallets"]
    history_db = wallet_store._dbs[b"wallet_history"]
    with wallet_store.env.begin(write=True) as txn:
        for agent_id, amount in sorted(settlements.items()):
            _require_agent_id(agent_id)
            settlement_delta = _require_lifecycle_settlement_delta(agent_id, amount)
            if settlement_delta == ZERO:
                continue
            wallet_row = _decode_json(txn.get(_encode_key(agent_id), db=wallets_db)) or {}
            wallet_history = _decode_json(txn.get(_encode_key(agent_id), db=history_db)) or {}
            if not isinstance(wallet_row, dict) or not isinstance(wallet_history, dict):
                raise EcuIlcLifecycleRuntimeError(
                    "lifecycle_wallet_row_invalid",
                    "wallet and history rows must be JSON objects",
                )
            balance_history = wallet_history.get("balance_history")
            if not isinstance(balance_history, list):
                balance_history = []
            existing_entry = next(
                (
                    item
                    for item in balance_history
                    if isinstance(item, dict) and item.get("epoch_id") == epoch_id
                ),
                None,
            )
            if existing_entry is not None:
                existing_delta = decimal_to_canonical_string(
                    to_decimal(
                        existing_entry.get("reward_delta_ilc", "0"),
                        token="lifecycle_reward_delta_invalid",
                    )
                )
                requested_delta = decimal_to_canonical_string(settlement_delta)
                if existing_delta != requested_delta:
                    raise EcuIlcLifecycleRuntimeError(
                        "lifecycle_epoch_replay_conflict",
                        "epoch_id replay conflicts with existing reward delta",
                    )
                current_wallet_row = wallet_row or {
                    "agent_id": agent_id,
                    "balance_ilc": "0",
                    "last_settled_epoch_id": epoch_id,
                    "reward_status": "not_rewarded",
                    "history_digest": wallet_history.get("history_digest"),
                    "latest_balance_receipt": existing_entry,
                    "claimability_state": "deferred",
                }
                results.append(
                    {
                        "ok": True,
                        "token": "lifecycle_epoch_commit_idempotent_replay",
                        "data": current_wallet_row,
                    }
                )
                continue

            prior_balance = to_decimal(
                wallet_row.get("balance_ilc", "0"),
                token="lifecycle_wallet_balance_invalid",
            )
            balance_after = prior_balance + settlement_delta
            if balance_after < ZERO:
                raise EcuIlcLifecycleRuntimeError(
                    "lifecycle_wallet_balance_underflow",
                    "wallet balance cannot become negative",
                )
            if balance_after > C_MAX_ILC:
                raise EcuIlcLifecycleRuntimeError(
                    LIFECYCLE_BALANCE_EXCEEDS_C_MAX_TOKEN,
                    "wallet balance cannot exceed the constitutional C_MAX_ILC ceiling",
                )
            latest_balance_receipt = {
                "epoch_id": epoch_id,
                "reward_delta_ilc": decimal_to_canonical_string(settlement_delta),
                "balance_after_ilc": decimal_to_canonical_string(balance_after),
                "settlement_status": "applied",
            }
            merged_balance_history = [
                item
                for item in balance_history
                if isinstance(item, dict) and item.get("epoch_id") != epoch_id
            ]
            merged_balance_history.append(latest_balance_receipt)
            merged_balance_history.sort(key=_epoch_history_sort_key)
            history_digest = _stable_digest({"balance_history": merged_balance_history})
            next_wallet_row = {
                "agent_id": agent_id,
                "balance_ilc": decimal_to_canonical_string(balance_after),
                "last_settled_epoch_id": epoch_id,
                "reward_status": "rewarded" if balance_after > ZERO else "not_rewarded",
                "history_digest": history_digest,
                "latest_balance_receipt": latest_balance_receipt,
                "claimability_state": "deferred",
            }
            next_wallet_history = {
                "agent_id": agent_id,
                "balance_history": merged_balance_history,
                "history_digest": history_digest,
            }
            txn.put(_encode_key(agent_id), _encode_json(next_wallet_row), db=wallets_db)
            txn.put(_encode_key(agent_id), _encode_json(next_wallet_history), db=history_db)
            results.append(
                {
                    "ok": True,
                    "token": "lifecycle_epoch_commit_applied",
                    "data": next_wallet_row,
                }
            )
    return results


def _require_lifecycle_settlement_delta(agent_id: str, amount: Decimal) -> Decimal:
    if agent_id in {PERFORMER_CARRY_FORWARD_ACCOUNT_ID, AUDITOR_CARRY_FORWARD_ACCOUNT_ID}:
        try:
            settlement_delta = to_decimal(
                amount,
                token="lifecycle_settlement_delta_invalid",
            )
        except ValueError as exc:
            raise EcuIlcLifecycleRuntimeError("lifecycle_settlement_delta_invalid", str(exc)) from exc
        if not settlement_delta.is_finite():
            raise EcuIlcLifecycleRuntimeError(
                "lifecycle_settlement_delta_invalid",
                "settlement delta must be finite",
            )
        return settlement_delta
    return parse_non_negative_decimal(
        amount,
        token="lifecycle_reward_delta_invalid",
    )


def _decimal_string(value: Decimal) -> str:
    return decimal_to_canonical_string(value)


__all__ = [
    "ATOMIC_SETTLEMENT_WRITER_CREATED_TOKEN",
    "CARRY_FORWARD_CONSUMED_EXACTLY_ONCE_WIRED_TOKEN",
    "CONSERVATION_EQUATION_ENFORCED_TOKEN",
    "EPOCH_DISTRIBUTION_WRITER_VERSION",
    "EPOCH_ID_FORMAT",
    "EPOCH_ID_ZERO_PADDED_FORMAT_LOCKED_TOKEN",
    "EpochDistributionConservationRecord",
    "EpochDistributionInput",
    "EpochDistributionOutput",
    "GENESIS_CAP_ALWAYS_SUPPLIED_TOKEN",
    "PROTOCOL_RESERVE_WIRED_TOKEN",
    "compute_epoch_distribution",
    "commit_epoch_distribution",
    "format_epoch_id",
]
