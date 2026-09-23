from __future__ import annotations

from decimal import Decimal
from collections.abc import Iterator, Mapping

import pytest

from ilc_core.epoch.epoch_emission_production_path import GENESIS_FIXED_TRANCHE_ILC
from ilc_core.epoch.epoch_emission_runtime import raw_epoch_emission_budget
from ilc_core.epoch.epoch_maturity_gate import (
    EPOCH_ZERO_NONZERO_SETTLEMENT_NOT_MATURE_TOKEN,
    MIN_MONTHLY_ISSUANCE_VALIDATION_EPOCH_SPAN,
    MonthlyIssuanceMaturityProof,
)
from ilc_core.epoch.epoch_distribution_writer import (
    DEFAULT_SOURCE_SETTLEMENT_ROOT_HEX,
    EPOCH_ID_FORMAT,
    ILC_QUANTUM,
    MAX_ELIGIBLE_AGENTS,
    MAX_PRIOR_CARRY_FORWARD_RECORDS,
    EpochDistributionInput,
    _allocate_pool_to_agents,
    _process_agent_settlement,
    _require_lifecycle_settlement_delta,
    compute_epoch_distribution,
    commit_epoch_distribution,
    commit_verified_epoch_distribution,
    format_epoch_id,
)
from ilc_core.epoch.genesis_settlement_destination import GENESIS_AGENT1_AGENT_ID
from ilc_core.epoch.pool_carry_forward_runtime import (
    AUDITOR_CARRY_FORWARD_ACCOUNT_ID,
    AUDITOR_POOL_ROLE,
    CONSUMED_STATUS,
    PERFORMER_CARRY_FORWARD_ACCOUNT_ID,
    PERFORMER_POOL_ROLE,
    create_carry_forward_record,
    mark_carry_forward_consumed,
)
from ilc_core.epoch.protocol_reserve_destination import PROTOCOL_RESERVE_ACCOUNT_ID
from ilc_core.ledger.ecu_active_layer_runtime import EcuActiveLayerRuntime
from ilc_core.ledger.ecu_ilc_lifecycle_runtime import (
    EcuIlcLifecycleRuntime,
    EcuIlcLifecycleRuntimeError,
)
from ilc_core.storage.lmdb_public_runtime import LmdbWalletStore


ROOT_HEX = "b" * 64
CIDV1_ROOT_HEX = "01711220" + "b" * 64
AGENT_A = "a" * 96
AGENT_B = "b" * 96
AGENT_C = "c" * 96
AGENT_ZERO = "d" * 96
PERFORMER_AGENT = "e" * 96
AUDITOR_AGENT = "f" * 96


class RecordingBatchLifecycle:
    ilc_atomic_epoch_batch_writer = True

    def __init__(self) -> None:
        self.calls: list[dict[str, object]] = []

    def commit_settled_epoch_batch(
        self,
        *,
        settlements: dict[str, Decimal],
        epoch_id: str,
    ) -> list[dict[str, object]]:
        self.calls.append({"settlements": settlements, "epoch_id": epoch_id})
        return [{"ok": True, "token": "recorded", "data": {}}]


class OversizedWeightMapping(Mapping[str, Decimal]):
    def __getitem__(self, key: str) -> Decimal:
        raise KeyError(key)

    def __iter__(self) -> Iterator[str]:
        return iter(())

    def __len__(self) -> int:
        return MAX_ELIGIBLE_AGENTS + 1


class OversizedPriorRecordList(list[object]):
    def __len__(self) -> int:
        return MAX_PRIOR_CARRY_FORWARD_RECORDS + 1


class UnmarkedDuckBatchLifecycle:
    def commit_settled_epoch_batch(
        self,
        *,
        settlements: dict[str, Decimal],
        epoch_id: str,
    ) -> list[dict[str, object]]:
        return [{"settlements": settlements, "epoch_id": epoch_id}]


def _inputs(**overrides: object) -> EpochDistributionInput:
    values = {
        "issuance_epoch": 0,
        "total_epoch_fees_ilc": Decimal("0"),
        "genesis_cumulative_accrual_ilc": Decimal("0"),
        "eligible_agents": {},
        "prior_carry_forward_records": [],
        "source_settlement_root_hex": ROOT_HEX,
    }
    values.update(overrides)
    if "monthly_maturity_proof" not in overrides:
        issuance_epoch = values.get("issuance_epoch")
        source_root = values.get("source_settlement_root_hex")
        if (
            isinstance(issuance_epoch, int)
            and not isinstance(issuance_epoch, bool)
            and issuance_epoch > 0
            and isinstance(source_root, str)
            and _looks_valid_root(source_root)
        ):
            values["monthly_maturity_proof"] = _maturity_proof(
                distribution_issuance_epoch=issuance_epoch,
                source_settlement_root_hex=source_root,
            )
    return EpochDistributionInput(**values)  # type: ignore[arg-type]


def _looks_valid_root(value: str) -> bool:
    return (
        len(value) == 64
        and all(char in "0123456789abcdef" for char in value)
    ) or (
        len(value) == 72
        and value.startswith("01711220")
        and all(char in "0123456789abcdef" for char in value)
    )


def _maturity_proof(
    *,
    distribution_issuance_epoch: int = 1,
    source_settlement_root_hex: str = ROOT_HEX,
) -> MonthlyIssuanceMaturityProof:
    opening_epoch = (distribution_issuance_epoch - 1) * MIN_MONTHLY_ISSUANCE_VALIDATION_EPOCH_SPAN
    closing_epoch = distribution_issuance_epoch * MIN_MONTHLY_ISSUANCE_VALIDATION_EPOCH_SPAN
    return MonthlyIssuanceMaturityProof(
        matured_issuance_epoch=distribution_issuance_epoch - 1,
        distribution_issuance_epoch=distribution_issuance_epoch,
        source_settlement_root_hex=source_settlement_root_hex,
        opening_validation_epoch=opening_epoch,
        closing_validation_epoch=closing_epoch,
        validator_quorum_certificate_ref=f"validator_quorum_sha256:{'a' * 64}",
        evidence_ref=f"monthly_close_evidence_sha256:{'b' * 64}",
    )


def _prior_record(
    *,
    role: str = PERFORMER_POOL_ROLE,
    amount: Decimal = Decimal("10"),
    source_epoch: int = 1,
    target_epoch: int = 2,
    source_settlement_root: str = ROOT_HEX,
) -> object:
    return create_carry_forward_record(
        source_epoch=source_epoch,
        target_epoch=target_epoch,
        pool_role=role,
        amount_ilc=amount,
        account_id=(
            PERFORMER_CARRY_FORWARD_ACCOUNT_ID
            if role == PERFORMER_POOL_ROLE
            else AUDITOR_CARRY_FORWARD_ACCOUNT_ID
        ),
        reason="test prior carry-forward",
        source_settlement_root=source_settlement_root,
    )


def test_zero_epoch_zero_fee_has_no_outputs() -> None:
    output = compute_epoch_distribution(_inputs())

    assert output.epoch_id == "0000000000"
    assert output.emission_quote is None
    assert output.conservation_verified is True
    assert output.conservation_record.total_debit_ilc == Decimal("0")
    assert output.agent_settled_balance_deltas == {}
    assert output.genesis_settled_delta == Decimal("0E-9")
    assert output.protocol_reserve_delta == Decimal("0E-9")
    assert output.carry_forward_out_records == ()


def test_nonzero_fee_no_agents_routes_to_carry_forward_genesis_and_reserve() -> None:
    output = compute_epoch_distribution(_inputs(total_epoch_fees_ilc=Decimal("100")))

    assert output.protocol_reserve_delta == Decimal("10.000000000")
    assert output.genesis_settled_delta == Decimal("4.500000000")
    assert output.agent_settled_balance_deltas == {}
    assert [record.account_id for record in output.carry_forward_out_records] == [
        PERFORMER_CARRY_FORWARD_ACCOUNT_ID,
        AUDITOR_CARRY_FORWARD_ACCOUNT_ID,
    ]
    assert sum(record.amount_ilc for record in output.carry_forward_out_records) == Decimal(
        "85.500000000"
    )
    assert output.conservation_record.total_debit_ilc == output.conservation_record.total_credit_ilc


def test_nonzero_fee_with_agents_settles_performer_and_auditor_pools() -> None:
    output = compute_epoch_distribution(
        _inputs(total_epoch_fees_ilc=Decimal("100"), eligible_agents={AGENT_A: Decimal("1")})
    )

    assert output.agent_settled_balance_deltas == {AGENT_A: Decimal("85.500000000")}
    assert output.carry_forward_out_records == ()
    assert output.protocol_reserve_delta == Decimal("10.000000000")
    assert output.genesis_settled_delta == Decimal("4.500000000")


def test_epoch_one_scheduled_emission_is_distributed_after_monthly_maturity() -> None:
    output = compute_epoch_distribution(
        _inputs(issuance_epoch=1, eligible_agents={AGENT_A: Decimal("1")})
    )
    expected_emission = raw_epoch_emission_budget(0)

    assert output.conservation_record.current_emission_ilc == expected_emission
    assert output.conservation_record.gross_epoch_value_ilc == expected_emission
    assert output.genesis_settled_delta > Decimal("0")
    assert output.agent_settled_balance_deltas[AGENT_A] > Decimal("0")
    assert output.protocol_reserve_delta == Decimal("0E-9")
    assert output.monthly_maturity_proof is not None
    assert output.monthly_maturity_proof.matured_issuance_epoch == 0


def test_epoch_one_nonzero_emission_with_no_eligible_agents_still_requires_maturity() -> None:
    with pytest.raises(ValueError, match="monthly_issuance_maturity_proof_required"):
        compute_epoch_distribution(
            EpochDistributionInput(
                issuance_epoch=1,
                total_epoch_fees_ilc=Decimal("0"),
                genesis_cumulative_accrual_ilc=Decimal("0"),
                eligible_agents={},
                prior_carry_forward_records=[],
                source_settlement_root_hex=ROOT_HEX,
                monthly_maturity_proof=None,
            )
        )

    output = compute_epoch_distribution(_inputs(issuance_epoch=1, eligible_agents={}))
    assert output.monthly_maturity_proof is not None
    assert output.agent_settled_balance_deltas == {}
    assert output.genesis_settled_delta > Decimal("0")
    assert output.carry_forward_out_records


def test_epoch_one_accepts_rust_cidv1_source_settlement_root() -> None:
    output = compute_epoch_distribution(
        _inputs(
            issuance_epoch=1,
            source_settlement_root_hex=CIDV1_ROOT_HEX,
            allow_default_source_settlement_root=False,
        )
    )

    assert output.carry_forward_out_records
    assert all(
        record.source_settlement_root == CIDV1_ROOT_HEX
        for record in output.carry_forward_out_records
    )


def test_auditor_agents_can_be_distinct_from_performer_agents() -> None:
    output = compute_epoch_distribution(
        _inputs(
            total_epoch_fees_ilc=Decimal("100"),
            eligible_agents={PERFORMER_AGENT: Decimal("1")},
            eligible_auditor_agents={AUDITOR_AGENT: Decimal("1")},
        )
    )

    assert output.agent_settled_balance_deltas[PERFORMER_AGENT] == Decimal("72.000000000")
    assert output.agent_settled_balance_deltas[AUDITOR_AGENT] == Decimal("13.500000000")


def test_partial_genesis_cap_routes_excess_to_performer_pool() -> None:
    output = compute_epoch_distribution(
        _inputs(
            total_epoch_fees_ilc=Decimal("100"),
            genesis_cumulative_accrual_ilc=GENESIS_FIXED_TRANCHE_ILC - Decimal("1"),
            eligible_agents={AGENT_A: Decimal("1")},
        )
    )

    assert output.genesis_overhead_remaining_allowance_ilc == Decimal("1.000000000")
    assert output.genesis_settled_delta == Decimal("1.000000000")
    assert output.agent_settled_balance_deltas[AGENT_A] == Decimal("89.000000000")


def test_saturated_genesis_cap_routes_zero_to_genesis_without_losing_allocation() -> None:
    output = compute_epoch_distribution(
        _inputs(
            total_epoch_fees_ilc=Decimal("100"),
            genesis_cumulative_accrual_ilc=GENESIS_FIXED_TRANCHE_ILC,
            eligible_agents={AGENT_A: Decimal("1")},
        )
    )

    assert output.genesis_overhead_remaining_allowance_ilc == Decimal("0E-9")
    assert output.genesis_settled_delta == Decimal("0E-9")
    assert output.agent_settled_balance_deltas[AGENT_A] == Decimal("90.000000000")


def test_prior_carry_forward_is_consumed_into_agent_distribution() -> None:
    prior = _prior_record(amount=Decimal("10"), target_epoch=2)
    output = compute_epoch_distribution(
        _inputs(
            issuance_epoch=2,
            eligible_agents={AGENT_A: Decimal("1")},
            prior_carry_forward_records=[prior],
        )
    )

    assert output.consumed_carry_forward_records[0].status == CONSUMED_STATUS
    assert output.consumed_carry_forward_records[0].consumed_at_epoch == 2
    assert output.agent_settled_balance_deltas[AGENT_A] > Decimal("10")
    assert output.conservation_record.distribution_carry_forward_in_ilc == Decimal("10")


def test_prior_carry_forward_without_agents_is_recarried_once() -> None:
    prior = _prior_record(amount=Decimal("10"), target_epoch=2)
    output = compute_epoch_distribution(
        _inputs(issuance_epoch=2, prior_carry_forward_records=[prior])
    )

    assert output.consumed_carry_forward_records[0].consumed_at_epoch == 2
    assert sum(record.amount_ilc for record in output.carry_forward_out_records) > Decimal("10")
    assert output.conservation_record.distribution_carry_forward_in_ilc == Decimal("10")


def test_consumed_prior_carry_forward_is_rejected() -> None:
    prior = mark_carry_forward_consumed(
        _prior_record(amount=Decimal("10"), target_epoch=2), consumed_at_epoch=2
    )

    with pytest.raises(ValueError, match="prior_carry_forward_record_must_be_pending"):
        compute_epoch_distribution(_inputs(issuance_epoch=3, prior_carry_forward_records=[prior]))


def test_duplicate_prior_carry_forward_is_rejected() -> None:
    prior = _prior_record(amount=Decimal("10"), target_epoch=2)

    with pytest.raises(ValueError, match="prior_carry_forward_record_duplicate"):
        compute_epoch_distribution(_inputs(issuance_epoch=2, prior_carry_forward_records=[prior, prior]))


def test_future_target_prior_carry_forward_is_rejected() -> None:
    prior = _prior_record(amount=Decimal("10"), source_epoch=2, target_epoch=3)

    with pytest.raises(ValueError, match="prior_carry_forward_target_epoch_not_reached"):
        compute_epoch_distribution(_inputs(issuance_epoch=2, prior_carry_forward_records=[prior]))


def test_prior_carry_forward_records_must_be_sequence() -> None:
    with pytest.raises(ValueError, match="prior_carry_forward_records_must_be_sequence"):
        compute_epoch_distribution(_inputs(prior_carry_forward_records=None))


def test_eligible_agent_count_is_bounded_before_iteration() -> None:
    with pytest.raises(ValueError, match="eligible_agents_exceeds_max_count"):
        compute_epoch_distribution(_inputs(eligible_agents=OversizedWeightMapping()))


def test_eligible_auditor_agent_count_is_bounded_before_iteration() -> None:
    with pytest.raises(ValueError, match="eligible_auditor_agents_exceeds_max_count"):
        compute_epoch_distribution(
            _inputs(
                eligible_agents={},
                eligible_auditor_agents=OversizedWeightMapping(),
            )
        )


def test_prior_carry_forward_count_is_bounded_before_iteration() -> None:
    with pytest.raises(ValueError, match="prior_carry_forward_records_exceeds_max_count"):
        compute_epoch_distribution(
            _inputs(prior_carry_forward_records=OversizedPriorRecordList())
        )


def test_genesis_accrual_cannot_exceed_fixed_tranche() -> None:
    with pytest.raises(ValueError, match="genesis_cumulative_accrual_exceeds_fixed_tranche"):
        compute_epoch_distribution(
            _inputs(
                genesis_cumulative_accrual_ilc=GENESIS_FIXED_TRANCHE_ILC + ILC_QUANTUM
            )
        )


def test_default_settlement_root_can_be_rejected_for_production_gate() -> None:
    with pytest.raises(ValueError, match="source_settlement_root_default_not_allowed"):
        compute_epoch_distribution(
            _inputs(
                source_settlement_root_hex=DEFAULT_SOURCE_SETTLEMENT_ROOT_HEX,
                allow_default_source_settlement_root=False,
            )
        )


def test_default_settlement_root_is_automatically_rejected_after_epoch_zero() -> None:
    with pytest.raises(ValueError, match="source_settlement_root_default_only_allowed_for_epoch_zero"):
        compute_epoch_distribution(
            _inputs(
                issuance_epoch=1,
                source_settlement_root_hex=DEFAULT_SOURCE_SETTLEMENT_ROOT_HEX,
            )
        )


@pytest.mark.parametrize(
    "bad_root",
    [
        "A" * 64,
        "g" * 64,
        "b" * 63,
        "b" * 65,
        123,
    ],
)
def test_malformed_source_settlement_root_rejected_by_commit_path(bad_root: object) -> None:
    lifecycle = RecordingBatchLifecycle()

    with pytest.raises(ValueError, match="source_settlement_root_must_be_sha256_or_cidv1_hex"):
        commit_epoch_distribution(
            _inputs(
                total_epoch_fees_ilc=Decimal("100"),
                source_settlement_root_hex=bad_root,
            ),
            lifecycle,
        )

    assert lifecycle.calls == []


def test_non_default_settlement_root_passes_when_default_root_is_forbidden() -> None:
    output = compute_epoch_distribution(
        _inputs(
            total_epoch_fees_ilc=Decimal("100"),
            source_settlement_root_hex=ROOT_HEX,
            allow_default_source_settlement_root=False,
        )
    )

    assert output.conservation_verified is True
    assert output.carry_forward_out_records
    assert {record.source_settlement_root for record in output.carry_forward_out_records} == {
        ROOT_HEX
    }


def test_non_default_cidv1_settlement_root_passes_when_default_root_is_forbidden() -> None:
    output = compute_epoch_distribution(
        _inputs(
            total_epoch_fees_ilc=Decimal("100"),
            source_settlement_root_hex=CIDV1_ROOT_HEX,
            allow_default_source_settlement_root=False,
        )
    )

    assert output.conservation_verified is True
    assert output.carry_forward_out_records
    assert {record.source_settlement_root for record in output.carry_forward_out_records} == {
        CIDV1_ROOT_HEX
    }


def test_malformed_cidv1_source_settlement_root_prefix_rejected() -> None:
    with pytest.raises(ValueError, match="source_settlement_root_must_be_sha256_or_cidv1_hex"):
        compute_epoch_distribution(
            _inputs(
                issuance_epoch=1,
                source_settlement_root_hex="01711221" + "b" * 64,
                allow_default_source_settlement_root=False,
            )
        )


@pytest.mark.parametrize(
    "reserved_account_id",
    [
        PERFORMER_CARRY_FORWARD_ACCOUNT_ID,
        AUDITOR_CARRY_FORWARD_ACCOUNT_ID,
        GENESIS_AGENT1_AGENT_ID,
        PROTOCOL_RESERVE_ACCOUNT_ID,
    ],
)
def test_reserved_protocol_accounts_cannot_be_performer_eligible_agents(
    reserved_account_id: str,
) -> None:
    with pytest.raises(ValueError, match="eligible_agent_id_is_reserved_protocol_account"):
        compute_epoch_distribution(
            _inputs(
                total_epoch_fees_ilc=Decimal("100"),
                eligible_agents={reserved_account_id: Decimal("1")},
            )
        )


def test_malformed_eligible_agent_id_is_rejected() -> None:
    with pytest.raises(ValueError, match="eligible_agent_id_must_be_96_hex"):
        compute_epoch_distribution(
            _inputs(
                total_epoch_fees_ilc=Decimal("100"),
                eligible_agents={"agent:a": Decimal("1")},
            )
        )


def test_unknown_protocol_account_id_is_rejected() -> None:
    with pytest.raises(Exception) as exc_info:
        _require_lifecycle_settlement_delta(
            "pool:cdl029:future_unregistered_account",
            Decimal("-1"),
        )

    assert getattr(exc_info.value, "token", None) == "unknown_protocol_account_id"


@pytest.mark.parametrize(
    "reserved_account_id",
    [
        PERFORMER_CARRY_FORWARD_ACCOUNT_ID,
        AUDITOR_CARRY_FORWARD_ACCOUNT_ID,
        GENESIS_AGENT1_AGENT_ID,
        PROTOCOL_RESERVE_ACCOUNT_ID,
    ],
)
def test_reserved_protocol_accounts_cannot_be_auditor_eligible_agents(
    reserved_account_id: str,
) -> None:
    with pytest.raises(ValueError, match="eligible_agent_id_is_reserved_protocol_account"):
        compute_epoch_distribution(
            _inputs(
                total_epoch_fees_ilc=Decimal("100"),
                eligible_agents={PERFORMER_AGENT: Decimal("1")},
                eligible_auditor_agents={reserved_account_id: Decimal("1")},
            )
        )


def test_dust_assignment_order_is_lexicographic_by_agent_id() -> None:
    allocations, residual = _allocate_pool_to_agents(
        Decimal("0.000000005"),
        {
            AGENT_C: Decimal("1"),
            AGENT_B: Decimal("1"),
            AGENT_A: Decimal("1"),
        },
    )

    assert residual == Decimal("0E-9")
    assert allocations == {
        AGENT_A: Decimal("0.000000002"),
        AGENT_B: Decimal("0.000000002"),
        AGENT_C: Decimal("0.000000001"),
    }


def test_commit_skips_zero_weight_agents_and_zero_delta_recipients() -> None:
    lifecycle = RecordingBatchLifecycle()

    output = commit_epoch_distribution(
        _inputs(
            issuance_epoch=1,
            total_epoch_fees_ilc=Decimal("100"),
            eligible_agents={AGENT_A: Decimal("1"), AGENT_ZERO: Decimal("0")},
        ),
        lifecycle,
    )

    settlements = lifecycle.calls[0]["settlements"]
    assert isinstance(settlements, dict)
    assert AGENT_ZERO not in settlements
    assert settlements[AGENT_A] == output.agent_settled_balance_deltas[AGENT_A]


def test_epoch_id_zero_padding_format_is_locked() -> None:
    assert EPOCH_ID_FORMAT == "{:010d}"
    assert format_epoch_id(0) == "0000000000"
    assert format_epoch_id(1) == "0000000001"
    assert format_epoch_id(9_999_999_999) == "9999999999"
    with pytest.raises(ValueError, match="issuance_epoch_exceeds_zero_padded_width"):
        format_epoch_id(10_000_000_000)


def test_commit_requires_atomic_batch_writer_for_unknown_lifecycle() -> None:
    with pytest.raises(ValueError, match="atomic_lifecycle_batch_writer_required"):
        commit_epoch_distribution(
            _inputs(issuance_epoch=1, total_epoch_fees_ilc=Decimal("1")),
            object(),  # type: ignore[arg-type]
        )


def test_commit_rejects_unmarked_duck_typed_batch_writer() -> None:
    with pytest.raises(ValueError, match="atomic_lifecycle_batch_writer_required"):
        commit_epoch_distribution(
            _inputs(issuance_epoch=1, total_epoch_fees_ilc=Decimal("1")),
            UnmarkedDuckBatchLifecycle(),  # type: ignore[arg-type]
        )


def test_conservation_failure_writes_nothing(monkeypatch: pytest.MonkeyPatch) -> None:
    lifecycle = RecordingBatchLifecycle()

    def _fail(_record: object) -> None:
        raise ValueError("forced_conservation_failure")

    monkeypatch.setattr("ilc_core.epoch.epoch_distribution_writer._verify_conservation", _fail)
    with pytest.raises(ValueError, match="forced_conservation_failure"):
        commit_epoch_distribution(_inputs(total_epoch_fees_ilc=Decimal("1")), lifecycle)

    assert lifecycle.calls == []


def test_commit_epoch_distribution_invokes_load_bearing_conservation_gate(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    lifecycle = RecordingBatchLifecycle()
    calls: list[object] = []

    def _gate(output: object) -> None:
        calls.append(output)
        raise ValueError("load_bearing_gate_forced_failure")

    monkeypatch.setattr(
        "ilc_core.epoch.epoch_conservation_gate.verify_epoch_conservation_before_commit",
        _gate,
    )

    with pytest.raises(ValueError, match="load_bearing_gate_forced_failure"):
        commit_epoch_distribution(_inputs(total_epoch_fees_ilc=Decimal("100")), lifecycle)

    assert len(calls) == 1
    assert lifecycle.calls == []


def test_commit_verified_epoch_distribution_commits_supplied_output_without_recompute(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    lifecycle = RecordingBatchLifecycle()
    output = compute_epoch_distribution(
        _inputs(issuance_epoch=1, total_epoch_fees_ilc=Decimal("100"))
    )

    def _fail_recompute(_inputs: object) -> object:
        raise AssertionError("must not recompute already verified output")

    monkeypatch.setattr(
        "ilc_core.epoch.epoch_distribution_writer.compute_epoch_distribution",
        _fail_recompute,
    )

    committed = commit_verified_epoch_distribution(output, lifecycle)

    assert committed is output
    assert lifecycle.calls


def test_real_lmdb_lifecycle_commit_is_idempotent(tmp_path) -> None:  # type: ignore[no-untyped-def]
    wallet_store = LmdbWalletStore(tmp_path / "wallets")
    lifecycle = EcuIlcLifecycleRuntime(
        wallet_store=wallet_store,
        ecu_runtime=EcuActiveLayerRuntime(),
    )
    inputs = _inputs(
        issuance_epoch=1,
        total_epoch_fees_ilc=Decimal("100"),
        eligible_agents={AGENT_A: Decimal("1")},
    )

    first = commit_epoch_distribution(inputs, lifecycle)
    second = commit_epoch_distribution(inputs, lifecycle)

    assert first.conservation_verified is True
    assert second.conservation_verified is True
    assert wallet_store.get_wallet(AGENT_A)["last_settled_epoch_id"] == "0000000001"  # type: ignore[index]
    assert wallet_store.get_wallet(PROTOCOL_RESERVE_ACCOUNT_ID)["balance_ilc"] == "10"  # type: ignore[index]
    assert Decimal(wallet_store.get_wallet(GENESIS_AGENT1_AGENT_ID)["balance_ilc"]) > Decimal("4.5")  # type: ignore[index]


def test_lmdb_epoch_sequence_rejects_corrupt_last_settled_epoch_id(tmp_path) -> None:  # type: ignore[no-untyped-def]
    wallet_store = LmdbWalletStore(tmp_path / "wallets")
    wallet_store.put_wallet(
        AGENT_B,
        {
            "agent_id": AGENT_B,
            "balance_ilc": "1",
            "last_settled_epoch_id": "corrupt",
        },
    )
    lifecycle = EcuIlcLifecycleRuntime(
        wallet_store=wallet_store,
        ecu_runtime=EcuActiveLayerRuntime(),
    )

    with pytest.raises(EcuIlcLifecycleRuntimeError) as exc_info:
        commit_epoch_distribution(
            _inputs(
                issuance_epoch=1,
                total_epoch_fees_ilc=Decimal("100"),
                eligible_agents={AGENT_A: Decimal("1")},
            ),
            lifecycle,
        )

    assert exc_info.value.token == "lifecycle_last_settled_epoch_id_invalid"


def test_lmdb_idempotent_replay_preserves_empty_wallet_row(tmp_path) -> None:  # type: ignore[no-untyped-def]
    wallet_store = LmdbWalletStore(tmp_path / "wallets")
    epoch_id = "0000000001"
    existing_receipt = {
        "epoch_id": epoch_id,
        "reward_delta_ilc": "1",
        "balance_after_ilc": "1",
        "settlement_status": "applied",
    }
    wallet_store.put_wallet_history(
        AGENT_A,
        {
            "agent_id": AGENT_A,
            "balance_history": [existing_receipt],
            "history_digest": "history-digest",
        },
    )

    with wallet_store.wallet_batch_transaction() as batch:
        result = _process_agent_settlement(
            batch=batch,
            agent_id=AGENT_A,
            settlement_delta=Decimal("1"),
            epoch_id=epoch_id,
            replay_epoch=False,
        )

    assert result == {
        "ok": True,
        "token": "lifecycle_epoch_commit_idempotent_replay",
        "data": {},
    }
    assert wallet_store.get_wallet(AGENT_A) is None


def test_real_lmdb_zero_value_epoch_commit_records_marker(tmp_path) -> None:  # type: ignore[no-untyped-def]
    wallet_store = LmdbWalletStore(tmp_path / "wallets")
    lifecycle = EcuIlcLifecycleRuntime(
        wallet_store=wallet_store,
        ecu_runtime=EcuActiveLayerRuntime(),
    )

    output = commit_epoch_distribution(_inputs(), lifecycle)

    assert output.epoch_id == "0000000000"
    assert wallet_store.get_epoch_commit_marker("0000000000") == {
        "epoch_id": "0000000000",
        "settlement_count": 0,
        "settlement_status": "verified_zero_value_epoch_committed",
    }


def test_real_lmdb_rejects_epoch_zero_nonzero_settlement_as_immature(tmp_path) -> None:  # type: ignore[no-untyped-def]
    wallet_store = LmdbWalletStore(tmp_path / "wallets")
    lifecycle = EcuIlcLifecycleRuntime(
        wallet_store=wallet_store,
        ecu_runtime=EcuActiveLayerRuntime(),
    )

    with pytest.raises(ValueError, match=EPOCH_ZERO_NONZERO_SETTLEMENT_NOT_MATURE_TOKEN):
        commit_epoch_distribution(
            _inputs(total_epoch_fees_ilc=Decimal("100"), eligible_agents={AGENT_A: Decimal("1")}),
            lifecycle,
        )

    assert wallet_store.get_wallet(AGENT_A) is None


def test_real_lmdb_allows_first_nonzero_public_rc_settlement_epoch_one(tmp_path) -> None:  # type: ignore[no-untyped-def]
    wallet_store = LmdbWalletStore(tmp_path / "wallets")
    lifecycle = EcuIlcLifecycleRuntime(
        wallet_store=wallet_store,
        ecu_runtime=EcuActiveLayerRuntime(),
    )

    output = commit_epoch_distribution(
        _inputs(
            issuance_epoch=1,
            eligible_agents={AGENT_A: Decimal("1")},
        ),
        lifecycle,
    )

    assert output.issuance_epoch == 1
    assert wallet_store.get_wallet(AGENT_A)["last_settled_epoch_id"] == "0000000001"  # type: ignore[index]


def test_real_lmdb_rejects_initial_epoch_gap(tmp_path) -> None:  # type: ignore[no-untyped-def]
    wallet_store = LmdbWalletStore(tmp_path / "wallets")
    lifecycle = EcuIlcLifecycleRuntime(
        wallet_store=wallet_store,
        ecu_runtime=EcuActiveLayerRuntime(),
    )

    with pytest.raises(EcuIlcLifecycleRuntimeError) as exc_info:
        commit_epoch_distribution(
            _inputs(
                issuance_epoch=2,
                eligible_agents={AGENT_A: Decimal("1")},
            ),
            lifecycle,
        )

    assert exc_info.value.token == "lifecycle_epoch_sequence_gap"


def test_real_lmdb_rejects_out_of_order_epoch_gap(tmp_path) -> None:  # type: ignore[no-untyped-def]
    wallet_store = LmdbWalletStore(tmp_path / "wallets")
    lifecycle = EcuIlcLifecycleRuntime(
        wallet_store=wallet_store,
        ecu_runtime=EcuActiveLayerRuntime(),
    )

    commit_epoch_distribution(
        _inputs(
            issuance_epoch=1,
            total_epoch_fees_ilc=Decimal("100"),
            eligible_agents={AGENT_A: Decimal("1")},
        ),
        lifecycle,
    )

    with pytest.raises(EcuIlcLifecycleRuntimeError) as exc_info:
        commit_epoch_distribution(
            _inputs(
                issuance_epoch=3,
                eligible_agents={AGENT_A: Decimal("1")},
            ),
            lifecycle,
        )

    assert exc_info.value.token == "lifecycle_epoch_sequence_gap"


def test_real_lmdb_rejects_same_epoch_recipient_extension(tmp_path) -> None:  # type: ignore[no-untyped-def]
    wallet_store = LmdbWalletStore(tmp_path / "wallets")
    lifecycle = EcuIlcLifecycleRuntime(
        wallet_store=wallet_store,
        ecu_runtime=EcuActiveLayerRuntime(),
    )

    commit_epoch_distribution(
        _inputs(
            issuance_epoch=1,
            total_epoch_fees_ilc=Decimal("100"),
            eligible_agents={AGENT_A: Decimal("1")},
        ),
        lifecycle,
    )

    with pytest.raises(EcuIlcLifecycleRuntimeError) as exc_info:
        commit_epoch_distribution(
            _inputs(
                issuance_epoch=1,
                total_epoch_fees_ilc=Decimal("100"),
                eligible_agents={AGENT_B: Decimal("1")},
            ),
            lifecycle,
        )

    assert exc_info.value.token == "lifecycle_epoch_replay_recipient_extension"


def test_real_lmdb_carry_forward_consumption_debits_pool_accounts(tmp_path) -> None:  # type: ignore[no-untyped-def]
    wallet_store = LmdbWalletStore(tmp_path / "wallets")
    lifecycle = EcuIlcLifecycleRuntime(
        wallet_store=wallet_store,
        ecu_runtime=EcuActiveLayerRuntime(),
    )

    first = commit_epoch_distribution(
        _inputs(issuance_epoch=1, total_epoch_fees_ilc=Decimal("100"), eligible_agents={}),
        lifecycle,
    )
    assert Decimal(wallet_store.get_wallet(PERFORMER_CARRY_FORWARD_ACCOUNT_ID)["balance_ilc"]) > Decimal("72")  # type: ignore[index]
    assert Decimal(wallet_store.get_wallet(AUDITOR_CARRY_FORWARD_ACCOUNT_ID)["balance_ilc"]) > Decimal("13.5")  # type: ignore[index]

    second = commit_epoch_distribution(
        _inputs(
            issuance_epoch=2,
            eligible_agents={AGENT_A: Decimal("1")},
            prior_carry_forward_records=first.carry_forward_out_records,
        ),
        lifecycle,
    )

    assert second.conservation_record.distribution_carry_forward_in_ilc == sum(
        record.amount_ilc for record in first.carry_forward_out_records
    )
    assert wallet_store.get_wallet(PERFORMER_CARRY_FORWARD_ACCOUNT_ID)["balance_ilc"] == "0"  # type: ignore[index]
    assert wallet_store.get_wallet(AUDITOR_CARRY_FORWARD_ACCOUNT_ID)["balance_ilc"] == "0"  # type: ignore[index]
    agent_wallet = wallet_store.get_wallet(AGENT_A)
    assert agent_wallet is not None
    assert Decimal(agent_wallet["balance_ilc"]) > Decimal("85.5")


def test_saturated_genesis_cap_with_fees_and_prior_carry_forward_conserves() -> None:
    prior = _prior_record(amount=Decimal("10"), source_epoch=0, target_epoch=1)

    output = compute_epoch_distribution(
        _inputs(
            issuance_epoch=1,
            total_epoch_fees_ilc=Decimal("100"),
            genesis_cumulative_accrual_ilc=GENESIS_FIXED_TRANCHE_ILC,
            eligible_agents={AGENT_A: Decimal("1")},
            prior_carry_forward_records=[prior],
        )
    )

    assert output.genesis_settled_delta == Decimal("0E-9")
    assert output.agent_settled_balance_deltas[AGENT_A] > Decimal("10")
    assert output.conservation_record.distribution_carry_forward_in_ilc == Decimal("10")
    assert output.conservation_record.difference_ilc == Decimal("0E-9")


def test_float_and_missing_genesis_accrual_are_rejected() -> None:
    with pytest.raises(ValueError, match="total_epoch_fees_ilc_must_be_exact_decimal"):
        compute_epoch_distribution(_inputs(total_epoch_fees_ilc=0.1))
    with pytest.raises(ValueError, match="genesis_cumulative_accrual_ilc_required"):
        compute_epoch_distribution(_inputs(genesis_cumulative_accrual_ilc=None))


@pytest.mark.parametrize("bad_weight", [Decimal("NaN"), Decimal("Infinity")])
def test_non_finite_eligible_agent_weights_are_rejected(bad_weight: Decimal) -> None:
    with pytest.raises(ValueError, match="eligible_agents_weight_must_be_finite"):
        compute_epoch_distribution(_inputs(eligible_agents={AGENT_A: bad_weight}))


@pytest.mark.parametrize("bad_weight", [Decimal("NaN"), Decimal("Infinity")])
def test_non_finite_eligible_auditor_weights_are_rejected(bad_weight: Decimal) -> None:
    with pytest.raises(ValueError, match="eligible_auditor_agents_weight_must_be_finite"):
        compute_epoch_distribution(
            _inputs(
                eligible_agents={},
                eligible_auditor_agents={AUDITOR_AGENT: bad_weight},
            )
        )


def test_conservation_record_canonical_serialization_uses_decimal_strings() -> None:
    output = compute_epoch_distribution(
        _inputs(total_epoch_fees_ilc=Decimal("100"), eligible_agents={AGENT_A: Decimal("1")})
    )

    canonical = output.conservation_record.to_canonical_record()

    assert canonical
    assert all(isinstance(value, str) for value in canonical.values())
    assert all(isinstance(value, Decimal) for value in output.conservation_record.__dict__.values())
    assert {
        key: Decimal(value)
        for key, value in canonical.items()
    } == output.conservation_record.__dict__


def test_lifecycle_regular_agent_delta_must_align_to_ilc_quantum() -> None:
    with pytest.raises(Exception) as exc_info:
        _require_lifecycle_settlement_delta(AGENT_A, Decimal("1.0000000001"))

    assert getattr(exc_info.value, "token", None) == "lifecycle_reward_delta_invalid"


def test_lifecycle_carry_forward_delta_must_align_to_ilc_quantum() -> None:
    with pytest.raises(Exception) as exc_info:
        _require_lifecycle_settlement_delta(
            PERFORMER_CARRY_FORWARD_ACCOUNT_ID,
            Decimal("-1.0000000001"),
        )

    assert getattr(exc_info.value, "token", None) == "lifecycle_settlement_delta_invalid"


def test_prior_carry_forward_dedup_allows_different_settlement_roots() -> None:
    first = _prior_record(
        amount=Decimal("10"),
        source_settlement_root="a" * 64,
    )
    second = _prior_record(
        amount=Decimal("10"),
        source_settlement_root="b" * 64,
    )

    output = compute_epoch_distribution(
        _inputs(
            issuance_epoch=2,
            eligible_agents={AGENT_A: Decimal("1")},
            prior_carry_forward_records=[first, second],
        )
    )

    assert output.conservation_record.distribution_carry_forward_in_ilc == Decimal("20")
    assert len(output.consumed_carry_forward_records) == 2


def test_validator_and_treasury_outputs_are_zero_while_guards_active() -> None:
    output = compute_epoch_distribution(_inputs(total_epoch_fees_ilc=Decimal("100")))

    assert output.validator_reward_deltas == {}
    assert output.treasury_settled_delta == Decimal("0")
    assert output.conservation_record.validator_reward_deltas_ilc == Decimal("0")
    assert output.conservation_record.treasury_settled_delta_ilc == Decimal("0")


def test_epoch_package_exports_distribution_writer_surface() -> None:
    import ilc_core.epoch as epoch

    assert epoch.EPOCH_ID_FORMAT == "{:010d}"
    assert epoch.MAX_ELIGIBLE_AGENTS == MAX_ELIGIBLE_AGENTS
    assert epoch.EpochDistributionInput is EpochDistributionInput
    assert epoch.compute_epoch_distribution is compute_epoch_distribution
    assert epoch.commit_epoch_distribution is commit_epoch_distribution
    assert epoch.commit_verified_epoch_distribution is commit_verified_epoch_distribution
