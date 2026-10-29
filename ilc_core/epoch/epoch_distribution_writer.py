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

import json
import re
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation, ROUND_DOWN
from pathlib import Path
from typing import Any, Mapping, Protocol, runtime_checkable

from ilc_core.epoch.allocation_distributor_runtime import (
    EpochAllocationDistributionQuote,
    build_allocation_distribution_quote,
)
from ilc_core.epoch.epoch_emission_runtime import (
    C_MAX_ILC,
    ILC_QUANTUM,
    EpochEmissionQuote,
    build_epoch_emission_quote,
)
from ilc_core.epoch.epoch_maturity_gate import (
    CIDV1_DAG_CBOR_SHA2_256_ROOT_PREFIX_HEX,
    EPOCH_ZERO_NONZERO_SETTLEMENT_NOT_MATURE_TOKEN,
    MONTHLY_ISSUANCE_MATURITY_PROOF_REQUIRED_TOKEN,
    MonthlyIssuanceMaturityProof,
    require_monthly_issuance_maturity_proof,
)
from ilc_core.epoch.economic_activation_state import (
    TREASURY_DISTRIBUTION_NOT_ACTIVATED,
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
from ilc_core.epoch.protocol_account_boundary import (
    CARRY_FORWARD_PROTOCOL_ACCOUNT_IDS,
    RESERVED_PROTOCOL_ACCOUNT_IDS,
    RESERVED_PROTOCOL_ACCOUNT_PREFIXES,
    require_known_protocol_account_id,
)
from ilc_core.epoch.protocol_reserve_destination import PROTOCOL_RESERVE_ACCOUNT_ID
from ilc_core.epoch.validator_reward_pool_routing_runtime import (
    VALIDATOR_REWARD_DISTRIBUTION_NOT_ACTIVATED_TOKEN,
)
from ilc_core.ledger.exact_numeric import (
    ZERO,
    decimal_to_canonical_string,
    parse_non_negative_decimal,
    to_decimal,
)
from ilc_core.ledger.ecu_ilc_lifecycle_runtime import (
    EcuIlcLifecycleRuntime,
    EcuIlcLifecycleRuntimeError,
    LIFECYCLE_BALANCE_EXCEEDS_C_MAX_TOKEN,
    _epoch_history_sort_key,
    _stable_digest,
)
from ilc_core.storage.lmdb_public_runtime import (
    LmdbWalletStore,
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
FALLBACK_SET_EMPTY_OBSERVE_00_HARD_STOP_TOKEN = (
    "fallback_set_empty_observe_00_hard_stop"
)

MAX_AGENT_ID_BYTES = 256
MAX_ELIGIBLE_AGENTS = 65_536
MAX_PRIOR_CARRY_FORWARD_RECORDS = 65_536
DEFAULT_SOURCE_SETTLEMENT_ROOT_HEX = "0" * 64
_AGENT_ID_RE = re.compile(r"^[0-9a-f]{96}$")
_RESERVED_REWARD_RECIPIENT_IDS = RESERVED_PROTOCOL_ACCOUNT_IDS | frozenset({GENESIS_AGENT1_AGENT_ID})
_CARRY_FORWARD_ACCOUNT_IDS = CARRY_FORWARD_PROTOCOL_ACCOUNT_IDS
_PROTOCOL_ACCOUNT_PREFIXES = RESERVED_PROTOCOL_ACCOUNT_PREFIXES
_EMPTY_WEIGHT_FALLBACK_ELIGIBLE_SET_ARTIFACT = (
    "docs/specs/ilc_ecu_empty_weight_fallback_eligible_set_v0.1.json"
)
_EMPTY_WEIGHT_FALLBACK_AGENTS = (
    "8b4370fe4ffa16bbb9fc8430d638d9d19a12d8efad02964c85a867f65d942f98230a0b78baaa59b340ba88c6c480ac19",
    "8c3b517ece61ca111a1e44939b40c2fb85e96d0295b935ce50b2f95204cd938d23c244178a7367b21fc1622f5a95e62f",
    "97fc59d642f4df19bc017ede43e0e15202d933c89913201da5945b672d624fbf963262e795d23309362e5b419fd5ba09",
    "b306d66948b4dca95aade079b42931dd553432131d7138cc2b6e8ba804807fc881689bfc7fc0d9568e198bdbbea8d1e9",
    GENESIS_AGENT1_AGENT_ID,
)
_EMPTY_WEIGHT_FALLBACK_WEIGHT = Decimal("0.2")
_FALLBACK_ARTIFACT_VALIDATION_CACHE: tuple[str, int, int] | None = None


@runtime_checkable
class AtomicEpochBatchWriter(Protocol):
    ilc_atomic_epoch_batch_writer: bool

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
    # None means reuse performer weights for the auditor pool. An explicit empty
    # mapping means no auditor recipients and carries the auditor pool forward.
    eligible_auditor_agents: Mapping[str, Decimal | int | str] | None = None
    source_settlement_root_hex: str = DEFAULT_SOURCE_SETTLEMENT_ROOT_HEX
    allow_default_source_settlement_root: bool = True
    monthly_maturity_proof: MonthlyIssuanceMaturityProof | Mapping[str, Any] | None = None


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
    source_settlement_root_hex: str
    monthly_maturity_proof: MonthlyIssuanceMaturityProof | None

    def __post_init__(self) -> None:
        if not isinstance(self.conservation_record, EpochDistributionConservationRecord):
            return
        if self.conservation_verified:
            if (
                self.conservation_record.difference_ilc != ZERO
                or self.conservation_record.total_debit_ilc
                != self.conservation_record.total_credit_ilc
            ):
                raise ValueError("epoch_distribution_output_conservation_mismatch")
        if self.monthly_maturity_proof is not None:
            require_monthly_issuance_maturity_proof(
                self.monthly_maturity_proof,
                distribution_issuance_epoch=self.issuance_epoch,
                source_settlement_root_hex=self.source_settlement_root_hex,
            )
            return
        if self.issuance_epoch > 0 and self.conservation_record.current_emission_ilc > ZERO:
            raise ValueError(MONTHLY_ISSUANCE_MATURITY_PROOF_REQUIRED_TOKEN)


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
        # Emission quote indices are zero-based; distribution issuance epoch N
        # consumes the emission budget for matured issuance interval N - 1.
        emission_quote = build_epoch_emission_quote(
            issuance_epoch - 1,
            cumulative_issued_before_epoch,
        )
        current_emission = emission_quote.capped_epoch_budget_ilc
    monthly_maturity_proof = _validate_monthly_maturity_for_compute(
        proof=inputs.monthly_maturity_proof,
        issuance_epoch=issuance_epoch,
        source_settlement_root=source_settlement_root,
        current_emission=current_emission,
    )

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
        fallback_on_empty=issuance_epoch > 0,
        close_epoch_boundary=issuance_epoch,
    )
    auditor_weights = (
        resolved["eligible_auditor_agents"]
        if resolved["eligible_auditor_agents"] is not None
        else resolved["eligible_agents"]
    )
    auditor_allocations, unallocated_auditor = _allocate_pool_to_agents(
        available_auditor_pool,
        auditor_weights,
        fallback_on_empty=issuance_epoch > 0,
        close_epoch_boundary=issuance_epoch,
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
        source_settlement_root_hex=source_settlement_root,
        monthly_maturity_proof=monthly_maturity_proof,
    )


def commit_epoch_distribution(
    inputs: EpochDistributionInput,
    lifecycle_runtime: EcuIlcLifecycleRuntime | AtomicEpochBatchWriter,
) -> EpochDistributionOutput:
    output = compute_epoch_distribution(inputs)
    return commit_verified_epoch_distribution(output, lifecycle_runtime)


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


def format_epoch_id(issuance_epoch: int) -> str:
    epoch = _require_epoch(issuance_epoch, "issuance_epoch")
    if epoch > 9_999_999_999:
        raise ValueError("issuance_epoch_exceeds_zero_padded_width")
    return EPOCH_ID_FORMAT.format(epoch)


def load_fallback_eligible_set(close_epoch_boundary: int) -> dict[str, Decimal]:
    """Return the ratified empty-weight fallback set for OBSERVE-00.

    Runtime uses embedded constants so installed wheels do not depend on the
    repository ``docs/`` tree. Source checkouts additionally validate the
    committed JSON artifact against those constants to catch policy drift.
    """
    epoch = _require_epoch(close_epoch_boundary, "close_epoch_boundary")
    if epoch != 1:
        raise ValueError("fallback_policy_epoch_not_ratified")
    fallback = {
        agent_id: _EMPTY_WEIGHT_FALLBACK_WEIGHT
        for agent_id in _EMPTY_WEIGHT_FALLBACK_AGENTS
    }
    _require_fallback_weight_mapping(fallback)
    _validate_fallback_artifact_if_present(fallback)
    return dict(sorted(fallback.items()))


def _require_inputs(inputs: EpochDistributionInput) -> dict[str, Any]:
    if not isinstance(inputs, EpochDistributionInput):
        raise ValueError("epoch_distribution_input_required")
    if inputs.genesis_cumulative_accrual_ilc is None:
        raise ValueError("genesis_cumulative_accrual_ilc_required")
    if _treasury_distribution_not_activated() is not True:
        raise ValueError("treasury_distribution_guard_cleared_without_writer_update")
    issuance_epoch = _require_epoch(inputs.issuance_epoch, "issuance_epoch")
    allow_default_source_settlement_root = _require_bool(
        inputs.allow_default_source_settlement_root,
        "allow_default_source_settlement_root",
    )
    return {
        "issuance_epoch": issuance_epoch,
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
        "source_settlement_root_hex": _require_settlement_root(
            inputs.source_settlement_root_hex,
            issuance_epoch=issuance_epoch,
            allow_default_source_settlement_root=allow_default_source_settlement_root,
        ),
    }


def _validate_monthly_maturity_for_compute(
    *,
    proof: MonthlyIssuanceMaturityProof | Mapping[str, Any] | None,
    issuance_epoch: int,
    source_settlement_root: str,
    current_emission: Decimal,
) -> MonthlyIssuanceMaturityProof | None:
    if current_emission > ZERO:
        return require_monthly_issuance_maturity_proof(
            proof,
            distribution_issuance_epoch=issuance_epoch,
            source_settlement_root_hex=source_settlement_root,
        )
    if proof is not None:
        return require_monthly_issuance_maturity_proof(
            proof,
            distribution_issuance_epoch=issuance_epoch,
            source_settlement_root_hex=source_settlement_root,
        )
    return None


def _require_maturity_before_settlement_commit(
    output: EpochDistributionOutput,
    settlements: Mapping[str, Decimal],
) -> None:
    if not settlements:
        return
    if output.issuance_epoch == 0:
        raise ValueError(EPOCH_ZERO_NONZERO_SETTLEMENT_NOT_MATURE_TOKEN)
    require_monthly_issuance_maturity_proof(
        output.monthly_maturity_proof,
        distribution_issuance_epoch=output.issuance_epoch,
        source_settlement_root_hex=output.source_settlement_root_hex,
    )


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
    if len(value) > MAX_ELIGIBLE_AGENTS:
        raise ValueError(f"{field_name}_exceeds_max_count")
    normalized: dict[str, Decimal] = {}
    for agent_id, raw_weight in value.items():
        normalized_agent_id = _require_agent_id(agent_id)
        if normalized_agent_id in _RESERVED_REWARD_RECIPIENT_IDS:
            raise ValueError("eligible_agent_id_is_reserved_protocol_account")
        normalized[normalized_agent_id] = _require_non_negative_weight(
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
    if value.startswith(_PROTOCOL_ACCOUNT_PREFIXES):
        return require_known_protocol_account_id(value)
    if _AGENT_ID_RE.fullmatch(value) is None:
        raise ValueError("eligible_agent_id_must_be_96_hex")
    if len(value.encode("utf-8")) > MAX_AGENT_ID_BYTES:
        raise ValueError("eligible_agent_id_exceeds_max_bytes")
    return value


def _require_bool(value: object, field_name: str) -> bool:
    if not isinstance(value, bool):
        raise ValueError(f"{field_name}_must_be_bool")
    return value


def _require_settlement_root(
    value: object,
    *,
    issuance_epoch: int,
    allow_default_source_settlement_root: bool,
) -> str:
    if not isinstance(value, str) or any(char not in "0123456789abcdef" for char in value):
        raise ValueError("source_settlement_root_must_be_sha256_or_cidv1_hex")
    if len(value) == 64:
        pass
    elif len(value) == 72 and value.startswith(CIDV1_DAG_CBOR_SHA2_256_ROOT_PREFIX_HEX):
        pass
    else:
        raise ValueError("source_settlement_root_must_be_sha256_or_cidv1_hex")
    if not allow_default_source_settlement_root and value == DEFAULT_SOURCE_SETTLEMENT_ROOT_HEX:
        raise ValueError("source_settlement_root_default_not_allowed")
    if issuance_epoch > 0 and value == DEFAULT_SOURCE_SETTLEMENT_ROOT_HEX:
        raise ValueError("source_settlement_root_default_only_allowed_for_epoch_zero")
    return value


def _require_prior_record_container(value: object) -> tuple[PoolCarryForwardRecord, ...]:
    if not isinstance(value, (list, tuple)):
        raise ValueError("prior_carry_forward_records_must_be_sequence")
    if len(value) > MAX_PRIOR_CARRY_FORWARD_RECORDS:
        raise ValueError("prior_carry_forward_records_exceeds_max_count")
    return tuple(value)


def _genesis_remaining_allowance(genesis_cumulative_accrual_ilc: Decimal) -> Decimal:
    genesis_fixed_tranche_ilc = _genesis_fixed_tranche_ilc()
    if genesis_cumulative_accrual_ilc > genesis_fixed_tranche_ilc:
        raise ValueError("genesis_cumulative_accrual_exceeds_fixed_tranche")
    return genesis_fixed_tranche_ilc - genesis_cumulative_accrual_ilc


def _genesis_fixed_tranche_ilc() -> Decimal:
    from ilc_core.epoch.epoch_emission_production_path import GENESIS_FIXED_TRANCHE_ILC

    return GENESIS_FIXED_TRANCHE_ILC


def _treasury_distribution_not_activated() -> bool:
    return TREASURY_DISTRIBUTION_NOT_ACTIVATED


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
    *,
    fallback_on_empty: bool = False,
    close_epoch_boundary: int = 1,
) -> tuple[dict[str, Decimal], Decimal]:
    if pool == ZERO:
        return {}, ZERO
    active_weights = weights
    if not active_weights:
        if not fallback_on_empty:
            return {}, pool
        active_weights = load_fallback_eligible_set(close_epoch_boundary)
    positive_weights = {
        agent_id: weight
        for agent_id, weight in active_weights.items()
        if weight > ZERO
    }
    # This branch handles the case where `weights` was non-empty but contained only
    # non-positive entries (e.g. all-zero attribution weights).  If `weights` was
    # originally empty, `active_weights` was already replaced with the fallback set
    # above, so `positive_weights` will be non-empty and this branch is not reached.
    if not positive_weights:
        if not fallback_on_empty:
            return {}, pool
        positive_weights = {
            agent_id: weight
            for agent_id, weight in load_fallback_eligible_set(close_epoch_boundary).items()
            if weight > ZERO
        }
        if not positive_weights:
            raise ValueError(FALLBACK_SET_EMPTY_OBSERVE_00_HARD_STOP_TOKEN)

    total_weight = sum(positive_weights.values(), ZERO)
    total_quanta = int(pool / ILC_QUANTUM)
    allocations_quanta: dict[str, int] = {}
    allocated_quanta = 0
    remainders: dict[str, Decimal] = {}
    for agent_id, weight in sorted(positive_weights.items()):
        exact_share = Decimal(total_quanta) * weight / total_weight
        share_quanta = int(exact_share.to_integral_value(rounding=ROUND_DOWN))
        allocations_quanta[agent_id] = share_quanta
        allocated_quanta += share_quanta
        remainders[agent_id] = exact_share - Decimal(share_quanta)

    remaining_quanta = total_quanta - allocated_quanta
    # Largest-remainder assignment; AgentID order is only the deterministic tie-break.
    for agent_id, _remainder in sorted(
        remainders.items(),
        key=lambda item: (-item[1], item[0]),
    ):
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


def _require_fallback_weight_mapping(weights: Mapping[str, Decimal]) -> None:
    if not weights:
        raise ValueError(FALLBACK_SET_EMPTY_OBSERVE_00_HARD_STOP_TOKEN)
    if len(weights) > MAX_ELIGIBLE_AGENTS:
        raise ValueError("fallback_eligible_set_exceeds_max_count")
    normalized: dict[str, Decimal] = {}
    for agent_id, weight in weights.items():
        normalized[_require_fallback_agent_id(agent_id)] = _require_non_negative_weight(
            weight,
            "fallback_eligible_weight",
        )
    if any(weight <= ZERO for weight in normalized.values()):
        raise ValueError("fallback_eligible_weight_must_be_positive")
    if sum(normalized.values(), ZERO) != Decimal("1"):
        raise ValueError("fallback_eligible_weight_sum_invalid_observe_00")


def _require_fallback_agent_id(value: object) -> str:
    # Fallback eligibility is a pre-open policy set and may include Genesis.
    # Normal attribution weights still reject reserved reward recipients upstream.
    if not isinstance(value, str) or _AGENT_ID_RE.fullmatch(value) is None:
        raise ValueError("fallback_eligible_agent_id_invalid_observe_00")
    if len(value.encode("utf-8")) > MAX_AGENT_ID_BYTES:
        raise ValueError("fallback_eligible_agent_id_exceeds_max_bytes")
    return value


def _validate_fallback_artifact_if_present(expected: Mapping[str, Decimal]) -> None:
    global _FALLBACK_ARTIFACT_VALIDATION_CACHE
    artifact_path = Path(__file__).resolve().parents[2] / _EMPTY_WEIGHT_FALLBACK_ELIGIBLE_SET_ARTIFACT
    if not artifact_path.exists():
        return
    stat = artifact_path.stat()
    cache_key = (str(artifact_path.resolve()), stat.st_mtime_ns, stat.st_size)
    if _FALLBACK_ARTIFACT_VALIDATION_CACHE == cache_key:
        return
    try:
        with artifact_path.open("r", encoding="utf-8") as handle:
            artifact = json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError("fallback_eligible_set_artifact_invalid") from exc
    expected_fields = {
        "discovery_rule": "no_grpc_list_agents_no_runtime_operator_expansion",
        "eligibility_rule": "committed_pre_open_config_only",
        "issuance_epoch": 1,
        "issuance_epoch_open_anchor_ms": 1791007007082,
        "network_id": "public-rc",
        "phase": "GAP-ECU-MONTHLY-CLOSE-EMPTY-POOL-FALLBACK-POLICY-00",
        "schema_version": "ilc.ecu_empty_weight_fallback_eligible_set.v0.1",
        "tie_breaker": "largest_remainder_then_agent_id_lexicographic_ascending",
        "total_weight": "1",
        "weighting_rule": "equal_weight_per_agent",
    }
    for field_name, expected_value in expected_fields.items():
        if artifact.get(field_name) != expected_value:
            raise ValueError("fallback_eligible_set_artifact_invalid")
    agents = artifact.get("agents")
    weights = artifact.get("weights")
    if not isinstance(agents, list) or not isinstance(weights, dict):
        raise ValueError("fallback_eligible_set_artifact_invalid")
    artifact_weights: dict[str, Decimal] = {}
    for agent_id in agents:
        if agent_id not in weights:
            raise ValueError("fallback_eligible_set_artifact_invalid")
        artifact_weights[_require_fallback_agent_id(agent_id)] = _require_non_negative_weight(
            weights[agent_id],
            "fallback_eligible_weight",
        )
    _require_fallback_weight_mapping(artifact_weights)
    if dict(sorted(artifact_weights.items())) != dict(sorted(expected.items())):
        raise ValueError("fallback_eligible_set_artifact_mismatch")
    _FALLBACK_ARTIFACT_VALIDATION_CACHE = cache_key


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
    if isinstance(lifecycle_runtime, EcuIlcLifecycleRuntime):
        return _commit_lmdb_lifecycle_batch(
            lifecycle_runtime=lifecycle_runtime,
            settlements=settlements,
            epoch_id=epoch_id,
        )
    if (
        isinstance(lifecycle_runtime, AtomicEpochBatchWriter)
        and getattr(lifecycle_runtime, "ilc_atomic_epoch_batch_writer", None) is True
    ):
        result = lifecycle_runtime.commit_settled_epoch_batch(
            settlements=dict(settlements),
            epoch_id=epoch_id,
        )
        if not isinstance(result, list):
            raise ValueError("atomic_lifecycle_batch_writer_result_required")
        return result
    raise ValueError("atomic_lifecycle_batch_writer_required")


def _require_lmdb_wallet_store(lifecycle_runtime: EcuIlcLifecycleRuntime) -> LmdbWalletStore:
    wallet_store = lifecycle_runtime.wallet_store
    if not isinstance(wallet_store, LmdbWalletStore):
        raise ValueError("atomic_lmdb_wallet_store_required")
    return wallet_store


def _validate_epoch_sequence(batch: Any, epoch_number: int) -> bool:
    current_epoch_number = _current_lmdb_epoch_number(batch)
    if current_epoch_number is None:
        if epoch_number not in {0, 1}:
            raise EcuIlcLifecycleRuntimeError(
                "lifecycle_epoch_sequence_gap",
                "first lifecycle settlement epoch must be 0000000000 or 0000000001",
            )
        return False
    if epoch_number not in {current_epoch_number, current_epoch_number + 1}:
        raise EcuIlcLifecycleRuntimeError(
            "lifecycle_epoch_sequence_gap",
            "lifecycle settlement epoch must be current epoch or next sequential epoch",
        )
    return epoch_number == current_epoch_number


def _build_zero_settlement_marker(epoch_id: str) -> dict[str, Any]:
    return {
        "epoch_id": epoch_id,
        "settlement_count": 0,
        "settlement_status": "verified_zero_value_epoch_committed",
    }


def _build_epoch_commit_marker(
    epoch_id: str,
    settlements: Mapping[str, Decimal],
) -> dict[str, Any]:
    settlement_rows = [
        {
            "agent_id": agent_id,
            "settlement_delta_ilc": decimal_to_canonical_string(delta),
        }
        for agent_id, delta in sorted(settlements.items())
    ]
    return {
        "epoch_id": epoch_id,
        "settlement_count": len(settlement_rows),
        "settlement_digest": _stable_digest(
            {
                "epoch_id": epoch_id,
                "settlements": settlement_rows,
            }
        ),
        "settlements": settlement_rows,
        "settlement_status": "verified_epoch_committed",
    }


def _process_agent_settlement(
    *,
    batch: Any,
    agent_id: str,
    settlement_delta: Decimal,
    epoch_id: str,
    replay_epoch: bool,
) -> dict[str, Any]:
    batch_row = batch.get_wallet_pair(agent_id)
    wallet_row = batch_row.wallet
    wallet_history = batch_row.history
    if not isinstance(wallet_row, dict) or not isinstance(wallet_history, dict):
        raise EcuIlcLifecycleRuntimeError(
            "lifecycle_wallet_row_invalid",
            "wallet and history rows must be JSON objects",
        )
    balance_history = wallet_history.get("balance_history")
    if not isinstance(balance_history, list):
        balance_history = []

    history_by_epoch = _balance_history_by_epoch(balance_history)
    existing_entry = history_by_epoch.get(epoch_id)
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
        current_wallet_row = (
            wallet_row
            if wallet_row is not None
            else {
                "agent_id": agent_id,
                "balance_ilc": "0",
                "last_settled_epoch_id": epoch_id,
                "reward_status": "not_rewarded",
                "history_digest": wallet_history.get("history_digest"),
                "latest_balance_receipt": existing_entry,
                "claimability_state": "deferred",
            }
        )
        return {
            "ok": True,
            "token": "lifecycle_epoch_commit_idempotent_replay",
            "data": current_wallet_row,
        }

    if replay_epoch:
        raise EcuIlcLifecycleRuntimeError(
            "lifecycle_epoch_replay_recipient_extension",
            "same-epoch replay cannot add new settlement recipients",
        )

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
    history_by_epoch[epoch_id] = latest_balance_receipt
    merged_balance_history = sorted(history_by_epoch.values(), key=_epoch_history_sort_key)
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
    batch.put_wallet_pair(
        agent_id,
        wallet_payload=next_wallet_row,
        history_payload=next_wallet_history,
    )
    return {
        "ok": True,
        "token": "lifecycle_epoch_commit_applied",
        "data": next_wallet_row,
    }


def _balance_history_by_epoch(balance_history: list[Any]) -> dict[str, dict[str, Any]]:
    return {
        item["epoch_id"]: item
        for item in balance_history
        if isinstance(item, dict) and "epoch_id" in item
    }


def _require_matching_replay_marker(
    batch: Any,
    *,
    epoch_id: str,
    expected_marker: Mapping[str, Any],
) -> None:
    existing_marker = batch.get_epoch_commit_marker(epoch_id)
    if existing_marker is None:
        raise EcuIlcLifecycleRuntimeError(
            "lifecycle_epoch_replay_manifest_missing",
            "same-epoch replay requires an existing epoch commit marker",
        )
    if existing_marker == expected_marker:
        return

    existing_rows = existing_marker.get("settlements")
    expected_rows = expected_marker.get("settlements")
    if isinstance(existing_rows, list) and isinstance(expected_rows, list):
        existing_agent_ids = {
            row.get("agent_id") for row in existing_rows if isinstance(row, dict)
        }
        expected_agent_ids = {
            row.get("agent_id") for row in expected_rows if isinstance(row, dict)
        }
        if not expected_agent_ids <= existing_agent_ids:
            raise EcuIlcLifecycleRuntimeError(
                "lifecycle_epoch_replay_recipient_extension",
                "same-epoch replay cannot add new settlement recipients",
            )
    raise EcuIlcLifecycleRuntimeError(
        "lifecycle_epoch_replay_set_mismatch",
        "same-epoch replay must match the committed recipient set and deltas",
    )


def _commit_lmdb_lifecycle_batch(
    *,
    lifecycle_runtime: EcuIlcLifecycleRuntime,
    settlements: Mapping[str, Decimal],
    epoch_id: str,
) -> list[dict[str, Any]]:
    wallet_store = _require_lmdb_wallet_store(lifecycle_runtime)
    epoch_number = _require_epoch_id_format(epoch_id)
    normalized_settlements: dict[str, Decimal] = {}
    for agent_id, amount in sorted(settlements.items()):
        _require_agent_id(agent_id)
        settlement_delta = _require_lifecycle_settlement_delta(agent_id, amount)
        if settlement_delta != ZERO:
            normalized_settlements[agent_id] = settlement_delta
    expected_marker = (
        _build_epoch_commit_marker(epoch_id, normalized_settlements)
        if normalized_settlements
        else _build_zero_settlement_marker(epoch_id)
    )
    results: list[dict[str, Any]] = []
    with wallet_store.wallet_batch_transaction() as batch:
        replay_epoch = _validate_epoch_sequence(batch, epoch_number)
        if replay_epoch:
            _require_matching_replay_marker(
                batch,
                epoch_id=epoch_id,
                expected_marker=expected_marker,
            )
        for agent_id, settlement_delta in sorted(normalized_settlements.items()):
            results.append(
                _process_agent_settlement(
                    batch=batch,
                    agent_id=agent_id,
                    settlement_delta=settlement_delta,
                    epoch_id=epoch_id,
                    replay_epoch=replay_epoch,
                )
            )
        if not replay_epoch:
            batch.put_epoch_commit_marker(epoch_id, expected_marker)
    return results


def _require_epoch_id_format(epoch_id: str) -> int:
    if not isinstance(epoch_id, str) or len(epoch_id) != 10 or not epoch_id.isdecimal():
        raise EcuIlcLifecycleRuntimeError(
            "lifecycle_epoch_id_invalid",
            "epoch_id must be a 10-digit zero-padded decimal string",
        )
    return int(epoch_id)


def _current_lmdb_epoch_number(batch: Any) -> int | None:
    current: int | None = None
    for _, wallet_row in batch.iter_wallet_rows():
        last_epoch = wallet_row.get("last_settled_epoch_id")
        if not isinstance(last_epoch, str) or len(last_epoch) != 10 or not last_epoch.isdecimal():
            raise EcuIlcLifecycleRuntimeError(
                "lifecycle_last_settled_epoch_id_invalid",
                "wallet row last_settled_epoch_id must be a 10-digit epoch id",
            )
        epoch_number = int(last_epoch)
        current = epoch_number if current is None else max(current, epoch_number)
    return current


def _require_lifecycle_settlement_delta(agent_id: str, amount: Decimal) -> Decimal:
    if agent_id.startswith(_PROTOCOL_ACCOUNT_PREFIXES) and agent_id not in RESERVED_PROTOCOL_ACCOUNT_IDS:
        raise EcuIlcLifecycleRuntimeError(
            "unknown_protocol_account_id",
            "protocol account id must be explicitly registered before settlement",
        )
    if agent_id in _CARRY_FORWARD_ACCOUNT_IDS:
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
        if settlement_delta % ILC_QUANTUM != ZERO:
            raise EcuIlcLifecycleRuntimeError(
                "lifecycle_settlement_delta_invalid",
                "settlement delta must align to ILC quantum",
            )
        return settlement_delta
    settlement_delta = parse_non_negative_decimal(
        amount,
        token="lifecycle_reward_delta_invalid",
    )
    if settlement_delta % ILC_QUANTUM != ZERO:
        raise EcuIlcLifecycleRuntimeError(
            "lifecycle_reward_delta_invalid",
            "reward delta must align to ILC quantum",
        )
    return settlement_delta


def _decimal_string(value: Decimal) -> str:
    return decimal_to_canonical_string(value)


__all__ = [
    "ATOMIC_SETTLEMENT_WRITER_CREATED_TOKEN",
    "CARRY_FORWARD_CONSUMED_EXACTLY_ONCE_WIRED_TOKEN",
    "CIDV1_DAG_CBOR_SHA2_256_ROOT_PREFIX_HEX",
    "CONSERVATION_EQUATION_ENFORCED_TOKEN",
    "DEFAULT_SOURCE_SETTLEMENT_ROOT_HEX",
    "EPOCH_DISTRIBUTION_WRITER_VERSION",
    "EPOCH_ID_FORMAT",
    "EPOCH_ID_ZERO_PADDED_FORMAT_LOCKED_TOKEN",
    "EpochDistributionConservationRecord",
    "EpochDistributionInput",
    "EpochDistributionOutput",
    "FALLBACK_SET_EMPTY_OBSERVE_00_HARD_STOP_TOKEN",
    "GENESIS_CAP_ALWAYS_SUPPLIED_TOKEN",
    "MAX_ELIGIBLE_AGENTS",
    "MAX_PRIOR_CARRY_FORWARD_RECORDS",
    "PROTOCOL_RESERVE_WIRED_TOKEN",
    "compute_epoch_distribution",
    "commit_epoch_distribution",
    "commit_verified_epoch_distribution",
    "format_epoch_id",
    "load_fallback_eligible_set",
]
