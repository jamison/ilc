from __future__ import annotations

from pathlib import Path

import pytest

from ilc_core.epoch.allocation_distributor_runtime import GENESIS_OVERHEAD_POOL_LABEL
from ilc_core.epoch.fee_burn_split_runtime import GENESIS_BURN_POOL_LABEL
from ilc_core.epoch.genesis_settlement_destination import (
    CDL048_TREATMENT_APPLIED_TOKEN,
    CDL_048_GENESIS_TRANCHE_TREATMENT,
    GENESIS_AGENT1_AGENT_ID,
    GENESIS_BURN_POOL_NOT_ROUTED_TO_GENESIS_AGENT_TOKEN,
    GENESIS_DESTINATION_BINDING_TOKEN,
    get_genesis_settlement_destination_record,
    verify_genesis_settlement_destination_record,
)
from ilc_core.epoch.genesis_tranche_reconciliation_runtime import (
    build_genesis_tranche_reconciliation_quote,
    verify_genesis_tranche_reconciliation_record,
)


def _fee_burn_quote() -> dict[str, object]:
    return {
        "production_fee_burn_activated": False,
        "genesis_burn_pool_label": GENESIS_BURN_POOL_LABEL,
        "fee_burn_ratio": "0.10",
        "genesis_burn_pool_ilc": "1",
    }


def _allocation_quote() -> dict[str, object]:
    return {
        "production_allocation_distribution_activated": False,
        "genesis_overhead_pool_label": GENESIS_OVERHEAD_POOL_LABEL,
        "genesis_overhead_fraction": "0.05",
        "genesis_overhead_pool_ilc": "10",
    }


def _cdl048_quote() -> dict[str, object]:
    return {
        "conversion_activation_authorized": False,
        "ledger_write_authorized": False,
        "wallet_write_authorized": False,
        "genesis_tranche_treatment": CDL_048_GENESIS_TRANCHE_TREATMENT,
        "amount_ilc_credit": "0",
    }


def test_fix3e_destination_token_pinned() -> None:
    assert GENESIS_DESTINATION_BINDING_TOKEN == (
        "genesis_settlement_destination_bound_phase_1575c_fix3e.v0.1"
    )


def test_fix3e_cdl048_treatment_applied_token_pinned() -> None:
    assert CDL048_TREATMENT_APPLIED_TOKEN == (
        "cdl_048_genesis_tranche_treatment_applied_phase_1575c_fix3e.v0.1"
    )


def test_fix3e_agent_id_matches_pubkey_record() -> None:
    record = Path("docs/genesis/genesis_agent1_pubkey_record_838a.txt").read_text(
        encoding="utf-8"
    )

    assert f"agent_id:                 {GENESIS_AGENT1_AGENT_ID}" in record


def test_fix3e_destination_record_phase_1575s_guard_state() -> None:
    record = get_genesis_settlement_destination_record()

    assert record["genesis_wallet_write_authorized"] is False
    assert record["genesis_settlement_write_authorized"] is True
    assert record["genesis_minting_authorized"] is True


def test_fix3e_destination_record_burn_pool_not_routed() -> None:
    record = get_genesis_settlement_destination_record()

    assert record["genesis_burn_pool_routed_to_genesis_agent"] is False
    assert GENESIS_BURN_POOL_NOT_ROUTED_TO_GENESIS_AGENT_TOKEN == (
        "genesis_burn_pool_not_routed_to_genesis_agent_phase_1575c_fix3e"
    )


def test_fix3e_verify_destination_record_passes() -> None:
    verify_genesis_settlement_destination_record(
        get_genesis_settlement_destination_record()
    )


def test_fix3e_verify_destination_record_rejects_wallet_write_true() -> None:
    record = get_genesis_settlement_destination_record()
    record["genesis_wallet_write_authorized"] = True

    with pytest.raises(ValueError, match="genesis_wallet_write_authorized_must_be_false"):
        verify_genesis_settlement_destination_record(record)


def test_fix3e_verify_destination_record_rejects_missing_wallet_guard() -> None:
    record = get_genesis_settlement_destination_record()
    record.pop("genesis_wallet_write_authorized")

    with pytest.raises(ValueError, match="genesis_wallet_write_authorized_must_be_false"):
        verify_genesis_settlement_destination_record(record)


@pytest.mark.parametrize(
    "field",
    [
        "genesis_settlement_write_authorized",
        "genesis_minting_authorized",
    ],
)
def test_fix3e_verify_destination_record_rejects_missing_accounting_guard(
    field: str,
) -> None:
    record = get_genesis_settlement_destination_record()
    record.pop(field)

    with pytest.raises(ValueError, match=f"{field}_must_be_true_phase_1575s"):
        verify_genesis_settlement_destination_record(record)


@pytest.mark.parametrize(
    "field",
    [
        "genesis_settlement_write_authorized",
        "genesis_minting_authorized",
    ],
)
def test_fix3e_verify_destination_record_rejects_each_accounting_guard_false(
    field: str,
) -> None:
    record = get_genesis_settlement_destination_record()
    record[field] = False

    with pytest.raises(ValueError, match=f"{field}_must_be_true_phase_1575s"):
        verify_genesis_settlement_destination_record(record)


def test_fix3e_verify_destination_record_rejects_wrong_agent_id() -> None:
    record = get_genesis_settlement_destination_record()
    record["agent_id"] = "agent:wrong"

    with pytest.raises(ValueError, match="genesis_settlement_agent_id_mismatch"):
        verify_genesis_settlement_destination_record(record)


def test_fix3e_reconciliation_accepts_destination_bound_treatment() -> None:
    quote = build_genesis_tranche_reconciliation_quote(
        fee_burn_quote=_fee_burn_quote(),
        allocation_quote=_allocation_quote(),
        cdl048_conversion_quote=_cdl048_quote(),
    )
    record = quote.to_canonical_record()

    assert record["cdl048_genesis_tranche_treatment"] == (
        CDL_048_GENESIS_TRANCHE_TREATMENT
    )
    assert record["cdl048_applies_fixed_tranche"] is True
    assert record["fixed_tranche_realized_by_current_value_path_ilc"] == "1296000"
    assert record["fixed_tranche_unrealized_in_current_value_path_ilc"] == "0"
    assert record["wallet_write_authorized"] is False
    assert record["treasury_write_authorized"] is False
    assert record["production_minting_authorized"] is False
    assert record["ilc_settlement_authorized"] is False
    assert CDL048_TREATMENT_APPLIED_TOKEN in record["tokens"]
    assert GENESIS_DESTINATION_BINDING_TOKEN in record["tokens"]


def test_fix3e_reconciliation_verifier_accepts_destination_bound_treatment() -> None:
    quote = build_genesis_tranche_reconciliation_quote(
        fee_burn_quote=_fee_burn_quote(),
        allocation_quote=_allocation_quote(),
        cdl048_conversion_quote=_cdl048_quote(),
    )

    verification = verify_genesis_tranche_reconciliation_record(
        quote.to_canonical_record()
    )

    assert verification["verified"] is True
    assert verification["cdl048_applies_fixed_tranche"] is True


def test_fix3e_reconciliation_rejects_legacy_applied_treatment() -> None:
    cdl048_quote = _cdl048_quote()
    cdl048_quote["genesis_tranche_treatment"] = "applied"

    with pytest.raises(
        ValueError,
        match="cdl048_legacy_applied_treatment_rejected_phase_1575c_fix3e",
    ):
        build_genesis_tranche_reconciliation_quote(
            fee_burn_quote=_fee_burn_quote(),
            allocation_quote=_allocation_quote(),
            cdl048_conversion_quote=cdl048_quote,
        )


def test_fix3e_reconciliation_verifier_rejects_fixed_tranche_without_fix3e_treatment() -> None:
    quote = build_genesis_tranche_reconciliation_quote(
        fee_burn_quote=_fee_burn_quote(),
        allocation_quote=_allocation_quote(),
        cdl048_conversion_quote=_cdl048_quote(),
    )
    record = quote.to_canonical_record()
    record["cdl048_genesis_tranche_treatment"] = "applied"

    with pytest.raises(
        ValueError,
        match="cdl048_fixed_tranche_requires_fix3e_treatment",
    ):
        verify_genesis_tranche_reconciliation_record(record)
