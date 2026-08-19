from __future__ import annotations

import pytest

from ilc_core.epoch.genesis_settlement_destination import GENESIS_AGENT1_AGENT_ID
from ilc_core.epoch.protocol_reserve_destination import (
    CDL_028_AMENDMENT_DEPENDENCY,
    PROTOCOL_RESERVE_ACCOUNT_ID,
    PROTOCOL_RESERVE_DESTINATION_MODULE_CREATED_TOKEN,
    PROTOCOL_RESERVE_DISTINCT_FROM_GENESIS_AGENT_TOKEN,
    PROTOCOL_RESERVE_DISTINCT_FROM_TREASURY_TOKEN,
    PROTOCOL_RESERVE_GOVERNANCE_DEPLOYMENT_BLOCKED_TOKEN,
    PROTOCOL_RESERVE_GOVERNANCE_DEPLOYMENT_ENABLED,
    PROTOCOL_RESERVE_TRANSFER_BLOCKED_TOKEN,
    PROTOCOL_RESERVE_TRANSFER_ENABLED,
    PROTOCOL_RESERVE_WITHDRAWAL_BLOCKED_TOKEN,
    PROTOCOL_RESERVE_WITHDRAWAL_ENABLED,
    get_protocol_reserve_destination_record,
    require_protocol_reserve_governance_deployment_blocked,
    require_protocol_reserve_transfer_blocked,
    require_protocol_reserve_withdrawal_blocked,
    verify_protocol_reserve_destination_record,
)


def test_protocol_reserve_account_id_exact() -> None:
    assert PROTOCOL_RESERVE_ACCOUNT_ID == "reserve:cdl028:genesis_burn_pool"


def test_protocol_reserve_flags_default_false() -> None:
    assert PROTOCOL_RESERVE_TRANSFER_ENABLED is False
    assert PROTOCOL_RESERVE_WITHDRAWAL_ENABLED is False
    assert PROTOCOL_RESERVE_GOVERNANCE_DEPLOYMENT_ENABLED is False


def test_protocol_reserve_transfer_guard_raises() -> None:
    with pytest.raises(ValueError, match=PROTOCOL_RESERVE_TRANSFER_BLOCKED_TOKEN):
        require_protocol_reserve_transfer_blocked()


def test_protocol_reserve_withdrawal_guard_raises() -> None:
    with pytest.raises(ValueError, match=PROTOCOL_RESERVE_WITHDRAWAL_BLOCKED_TOKEN):
        require_protocol_reserve_withdrawal_blocked()


def test_protocol_reserve_governance_deployment_guard_raises() -> None:
    with pytest.raises(ValueError, match=PROTOCOL_RESERVE_GOVERNANCE_DEPLOYMENT_BLOCKED_TOKEN):
        require_protocol_reserve_governance_deployment_blocked()


def test_destination_record_contains_required_false_flags() -> None:
    record = get_protocol_reserve_destination_record()

    assert record["account_id"] == PROTOCOL_RESERVE_ACCOUNT_ID
    assert record["transfer_enabled"] is False
    assert record["withdrawal_enabled"] is False
    assert record["governance_deployment_enabled"] is False
    assert record["cdl_028_amendment_dependency"] == CDL_028_AMENDMENT_DEPENDENCY
    assert record["module_created_token"] == PROTOCOL_RESERVE_DESTINATION_MODULE_CREATED_TOKEN


def test_verify_valid_destination_record_passes() -> None:
    verify_protocol_reserve_destination_record(get_protocol_reserve_destination_record())


@pytest.mark.parametrize(
    "field",
    [
        "transfer_enabled",
        "withdrawal_enabled",
        "governance_deployment_enabled",
    ],
)
def test_verify_rejects_any_enabled_authority(field: str) -> None:
    record = get_protocol_reserve_destination_record()
    record[field] = True

    with pytest.raises(ValueError, match=f"protocol_reserve_{field}_must_be_false"):
        verify_protocol_reserve_destination_record(record)


def test_verify_rejects_extra_unsigned_fields() -> None:
    record = get_protocol_reserve_destination_record()
    record["unexpected_authority"] = False

    with pytest.raises(ValueError, match="protocol_reserve_destination_record_keys_mismatch"):
        verify_protocol_reserve_destination_record(record)


def test_reserve_account_is_not_genesis_agent() -> None:
    assert PROTOCOL_RESERVE_ACCOUNT_ID != GENESIS_AGENT1_AGENT_ID


def test_reserve_account_is_not_treasury() -> None:
    assert "treasury" not in PROTOCOL_RESERVE_ACCOUNT_ID


def test_record_confirms_non_overlap_tokens() -> None:
    record = get_protocol_reserve_destination_record()

    assert record["distinct_from_genesis_agent"] is True
    assert record["distinct_from_treasury"] is True
    assert PROTOCOL_RESERVE_DISTINCT_FROM_GENESIS_AGENT_TOKEN
    assert PROTOCOL_RESERVE_DISTINCT_FROM_TREASURY_TOKEN


def test_verify_rejects_missing_non_overlap_confirmation() -> None:
    record = get_protocol_reserve_destination_record()
    record["distinct_from_genesis_agent"] = False

    with pytest.raises(ValueError, match=PROTOCOL_RESERVE_DISTINCT_FROM_GENESIS_AGENT_TOKEN):
        verify_protocol_reserve_destination_record(record)
