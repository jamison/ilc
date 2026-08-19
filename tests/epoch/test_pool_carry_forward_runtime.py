from __future__ import annotations

from decimal import Decimal

import pytest

from ilc_core.epoch.genesis_settlement_destination import GENESIS_AGENT1_AGENT_ID
from ilc_core.epoch.pool_carry_forward_runtime import (
    AUDITOR_CARRY_FORWARD_ACCOUNT_ID,
    AUDITOR_POOL_ROLE,
    CARRY_FORWARD_CLAIM_ENABLED,
    CARRY_FORWARD_CONSUME_EXACTLY_ONCE_TOKEN,
    CARRY_FORWARD_NONSPENDABLE_TOKEN,
    CARRY_FORWARD_SPEND_ENABLED,
    CARRY_FORWARD_TRANSFER_ENABLED,
    CARRY_FORWARD_WITHDRAWAL_ENABLED,
    CONSUMED_STATUS,
    PENDING_CONSUMPTION_STATUS,
    PERFORMER_CARRY_FORWARD_ACCOUNT_ID,
    PERFORMER_POOL_ROLE,
    POOL_CARRY_FORWARD_RUNTIME_VERSION,
    PoolCarryForwardRecord,
    create_carry_forward_record,
    get_carry_forward_pool_record,
    mark_carry_forward_consumed,
    require_carry_forward_not_spendable,
    verify_carry_forward_pool_record,
)


ROOT_HEX = "a" * 64


def _valid_record(**overrides: object) -> PoolCarryForwardRecord:
    values = {
        "source_epoch": 1,
        "target_epoch": 2,
        "pool_role": PERFORMER_POOL_ROLE,
        "amount_ilc": Decimal("10"),
        "account_id": PERFORMER_CARRY_FORWARD_ACCOUNT_ID,
        "reason": "no eligible performer recipients",
        "source_settlement_root": ROOT_HEX,
    }
    values.update(overrides)
    return create_carry_forward_record(**values)  # type: ignore[arg-type]


def test_valid_round_trip_canonical_record() -> None:
    record = _valid_record()

    canonical = record.to_canonical_record()

    assert canonical == {
        "account_id": PERFORMER_CARRY_FORWARD_ACCOUNT_ID,
        "amount_ilc": "10",
        "cdl_029_allocation_dependency": "cdl_029_allocation_distributor_runtime_phase_1347.v0.1",
        "consumed_at_epoch": None,
        "pool_role": PERFORMER_POOL_ROLE,
        "reason": "no eligible performer recipients",
        "runtime_version": POOL_CARRY_FORWARD_RUNTIME_VERSION,
        "source_epoch": 1,
        "source_settlement_root": ROOT_HEX,
        "status": PENDING_CONSUMPTION_STATUS,
        "target_epoch": 2,
    }


def test_valid_consumption_sets_status_and_consumed_epoch() -> None:
    record = _valid_record()

    consumed = mark_carry_forward_consumed(record, consumed_at_epoch=2)

    assert consumed.status == CONSUMED_STATUS
    assert consumed.consumed_at_epoch == 2
    assert consumed.to_canonical_record()["amount_ilc"] == "10"


@pytest.mark.parametrize(
    ("amount", "token"),
    [
        (Decimal("0"), "carry_forward_amount_must_be_nonzero_positive"),
        (Decimal("-1"), "carry_forward_amount_must_be_nonzero_positive"),
        (Decimal("NaN"), "carry_forward_amount_must_be_finite"),
        (Decimal("Infinity"), "carry_forward_amount_must_be_finite"),
        (10, "carry_forward_amount_must_be_decimal"),
        ("10", "carry_forward_amount_must_be_decimal"),
    ],
)
def test_invalid_amount_rejected(amount: object, token: str) -> None:
    with pytest.raises(ValueError, match=token):
        _valid_record(amount_ilc=amount)


def test_amount_magnitude_rejected() -> None:
    with pytest.raises(ValueError, match="carry_forward_amount_exceeds_max_magnitude"):
        _valid_record(amount_ilc=Decimal("1e19"))


def test_invalid_pool_role_rejected() -> None:
    with pytest.raises(ValueError, match="invalid_carry_forward_pool_role"):
        _valid_record(pool_role="genesis", account_id=PERFORMER_CARRY_FORWARD_ACCOUNT_ID)


def test_account_id_must_match_pool_role() -> None:
    with pytest.raises(ValueError, match="carry_forward_account_id_role_mismatch"):
        _valid_record(pool_role=AUDITOR_POOL_ROLE, account_id=PERFORMER_CARRY_FORWARD_ACCOUNT_ID)


@pytest.mark.parametrize(
    ("source_epoch", "target_epoch", "token"),
    [
        (1, 1, "carry_forward_target_epoch_must_follow_source_epoch"),
        (2, 1, "carry_forward_target_epoch_must_follow_source_epoch"),
        (-1, 2, "source_epoch_must_be_non_negative_int"),
        (1, -2, "target_epoch_must_be_non_negative_int"),
        (True, 2, "source_epoch_must_be_non_negative_int"),
    ],
)
def test_invalid_source_or_target_epoch_rejected(
    source_epoch: object,
    target_epoch: object,
    token: str,
) -> None:
    with pytest.raises(ValueError, match=token):
        _valid_record(source_epoch=source_epoch, target_epoch=target_epoch)


@pytest.mark.parametrize("consumed_at_epoch", [0, 1, True, -1])
def test_invalid_consumed_epoch_rejected(consumed_at_epoch: object) -> None:
    record = _valid_record()

    with pytest.raises(ValueError):
        mark_carry_forward_consumed(record, consumed_at_epoch=consumed_at_epoch)  # type: ignore[arg-type]


def test_double_consumption_raises_token() -> None:
    record = _valid_record()
    consumed = mark_carry_forward_consumed(record, consumed_at_epoch=2)

    with pytest.raises(ValueError, match=CARRY_FORWARD_CONSUME_EXACTLY_ONCE_TOKEN):
        mark_carry_forward_consumed(consumed, consumed_at_epoch=3)


def test_nonspendable_guard_always_raises() -> None:
    with pytest.raises(ValueError, match=CARRY_FORWARD_NONSPENDABLE_TOKEN):
        require_carry_forward_not_spendable()


def test_account_ids_are_distinct_from_genesis_treasury_and_reserve() -> None:
    for account_id in (PERFORMER_CARRY_FORWARD_ACCOUNT_ID, AUDITOR_CARRY_FORWARD_ACCOUNT_ID):
        assert account_id != GENESIS_AGENT1_AGENT_ID
        assert "treasury" not in account_id
        assert "reserve" not in account_id
        assert account_id.startswith("pool:cdl029:")


def test_get_pool_records_and_verify_exact_shape() -> None:
    performer = get_carry_forward_pool_record(PERFORMER_POOL_ROLE)
    auditor = get_carry_forward_pool_record(AUDITOR_POOL_ROLE)

    assert performer["account_id"] == PERFORMER_CARRY_FORWARD_ACCOUNT_ID
    assert auditor["account_id"] == AUDITOR_CARRY_FORWARD_ACCOUNT_ID
    for record in (performer, auditor):
        assert record["transfer_enabled"] is CARRY_FORWARD_TRANSFER_ENABLED is False
        assert record["withdrawal_enabled"] is CARRY_FORWARD_WITHDRAWAL_ENABLED is False
        assert record["claim_enabled"] is CARRY_FORWARD_CLAIM_ENABLED is False
        assert record["spend_enabled"] is CARRY_FORWARD_SPEND_ENABLED is False
        verify_carry_forward_pool_record(record)


def test_verify_pool_record_rejects_extra_field() -> None:
    record = get_carry_forward_pool_record(PERFORMER_POOL_ROLE)
    record["extra"] = "nope"

    with pytest.raises(ValueError, match="carry_forward_pool_record_keys_mismatch"):
        verify_carry_forward_pool_record(record)


@pytest.mark.parametrize("bad_root", ["abc123", "A" * 64, "g" * 64, "a" * 63, "a" * 65])
def test_source_settlement_root_must_be_sha256_hex(bad_root: str) -> None:
    with pytest.raises(ValueError, match="carry_forward_source_settlement_root_must_be_sha256_hex"):
        _valid_record(source_settlement_root=bad_root)


def test_reason_required_and_bounded() -> None:
    with pytest.raises(ValueError, match="carry_forward_reason_required"):
        _valid_record(reason="")
    with pytest.raises(ValueError, match="carry_forward_reason_exceeds_max_bytes"):
        _valid_record(reason="x" * 257)
