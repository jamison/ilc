from __future__ import annotations

from copy import deepcopy
from decimal import Decimal

import pytest

from ilc_core.epoch.fee_burn_split_runtime import build_fee_burn_split_quote
from ilc_core.epoch.genesis_tranche_reconciliation_runtime import (
    CDL029_OVERHEAD_NOT_FULL_TRANCHE_TOKEN,
    CDL048_TRANCHE_TREATMENT_ABSENT_TOKEN,
    FIXED_GENESIS_TRANCHE_FRACTION,
    FIXED_GENESIS_TRANCHE_ILC,
    GENESIS_BURN_POOL_NOT_FIXED_TRANCHE_TOKEN,
    GENESIS_TRANCHE_REALIZATION_CONTROLLER_DEFERRED_TOKEN,
    GENESIS_TRANCHE_RECONCILIATION_QUOTE_ONLY_TOKEN,
    build_genesis_tranche_reconciliation_from_rehearsal_record,
    build_genesis_tranche_reconciliation_quote,
    verify_genesis_tranche_reconciliation_record,
)
from ilc_core.epoch.epoch_emission_runtime import C_MAX_ILC
from tests.test_phase_1568_fix2l_rehearsal_economics_record import (
    _accepted_submissions,
    _panel_payload,
    _record,
)
from tools.testbed.rehearsal_economics import (
    RehearsalEconomicsError,
    build_rehearsal_economics_record,
    settlement_root_inputs_hash,
    verify_rehearsal_economics_record,
)


def _fee_record() -> dict[str, object]:
    panel_payload = _panel_payload()
    return build_rehearsal_economics_record(
        namespace_id="phase1568-fix2q-test",
        accepted_submissions=_accepted_submissions(),
        ecu_claims=panel_payload["ecu_claim_batch"]["claims"],
        rehearsal_epoch=574,
        cumulative_issued_before_epoch_ilc="0",
        total_epoch_fees_ilc="100",
    )


def test_fix2q_constants_match_phase_599_600_fixed_genesis_tranche() -> None:
    assert C_MAX_ILC == Decimal("25920000")
    assert FIXED_GENESIS_TRANCHE_FRACTION == Decimal("0.05")
    assert FIXED_GENESIS_TRANCHE_ILC == Decimal("1296000")


def test_fix2q_rehearsal_record_separates_burn_overhead_and_fixed_tranche() -> None:
    record = _fee_record()
    reconciliation = record["genesis_tranche_reconciliation"]

    assert reconciliation["fixed_genesis_tranche_ilc"] == "1296000"
    assert reconciliation["cdl028_genesis_burn_pool_ilc"] == "10"
    assert reconciliation["cdl029_genesis_overhead_pool_ilc"] == "4.5"
    assert reconciliation["cdl028_genesis_burn_pool_is_fixed_tranche"] is False
    assert reconciliation["cdl029_genesis_overhead_is_full_tranche"] is False
    assert reconciliation["cdl048_applies_fixed_tranche"] is False
    assert reconciliation["cdl048_genesis_tranche_treatment"] == "absent"
    assert reconciliation["fixed_tranche_realized_by_current_value_path_ilc"] == "0"
    assert reconciliation["fixed_tranche_unrealized_in_current_value_path_ilc"] == "1296000"
    assert reconciliation["quote_read_model_only"] is True
    assert reconciliation["wallet_write_authorized"] is False
    assert reconciliation["treasury_write_authorized"] is False
    assert reconciliation["production_minting_authorized"] is False
    assert reconciliation["ilc_settlement_authorized"] is False

    tokens = set(reconciliation["tokens"])
    assert GENESIS_BURN_POOL_NOT_FIXED_TRANCHE_TOKEN in tokens
    assert CDL029_OVERHEAD_NOT_FULL_TRANCHE_TOKEN in tokens
    assert CDL048_TRANCHE_TREATMENT_ABSENT_TOKEN in tokens
    assert GENESIS_TRANCHE_REALIZATION_CONTROLLER_DEFERRED_TOKEN in tokens
    assert GENESIS_TRANCHE_RECONCILIATION_QUOTE_ONLY_TOKEN in tokens


def test_fix2q_verifier_recomputes_reconciliation_and_settlement_input_hash() -> None:
    record = _fee_record()
    verification = verify_rehearsal_economics_record(record)

    assert verification["settlement_root_verified"] is True
    assert verification["genesis_tranche_reconciliation_verified"] is True
    assert record["settlement_root_inputs_sha256"] == settlement_root_inputs_hash(record)
    assert build_genesis_tranche_reconciliation_from_rehearsal_record(record) == record[
        "genesis_tranche_reconciliation"
    ]


def test_fix2q_verifier_rejects_reconciliation_wallet_write_claim() -> None:
    record = deepcopy(_record())
    record["genesis_tranche_reconciliation"]["wallet_write_authorized"] = True

    with pytest.raises(RehearsalEconomicsError) as excinfo:
        verify_rehearsal_economics_record(record)

    assert excinfo.value.token == "genesis_tranche_reconciliation_invalid"
    assert "wallet_write_authorized" in str(excinfo.value)


def test_fix2q_verifier_rejects_mismatched_reconciliation_nonclaim() -> None:
    record = deepcopy(_record())
    record["genesis_tranche_reconciliation"]["cdl029_genesis_overhead_is_full_tranche"] = True

    with pytest.raises(RehearsalEconomicsError) as excinfo:
        verify_rehearsal_economics_record(record)

    assert excinfo.value.token == "genesis_tranche_reconciliation_invalid"
    assert "cdl029_genesis_overhead_is_full_tranche" in str(excinfo.value)


def test_fix2q_runtime_rejects_float_shaped_fee_burn_input() -> None:
    record = _record()
    fee_burn_quote = build_fee_burn_split_quote(574, "100").to_canonical_record()
    fee_burn_quote["genesis_burn_pool_ilc"] = 10.0

    with pytest.raises(ValueError, match="genesis_tranche_reconciliation_float_rejected"):
        build_genesis_tranche_reconciliation_quote(
            fee_burn_quote=fee_burn_quote,
            allocation_quote=record["allocation_quote"],
            cdl048_conversion_quote=record["cdl048_conversion_quote"],
        )


def test_fix2q_runtime_rejects_wrong_fee_burn_ratio_or_overhead_label() -> None:
    record = _record()
    fee_burn_quote = deepcopy(record["epoch_emission_result"]["fee_burn_quote"])
    fee_burn_quote["fee_burn_ratio"] = "0.05"

    with pytest.raises(ValueError, match="fee_burn_ratio_mismatch_phase_1568_fix2q"):
        build_genesis_tranche_reconciliation_quote(
            fee_burn_quote=fee_burn_quote,
            allocation_quote=record["allocation_quote"],
            cdl048_conversion_quote=record["cdl048_conversion_quote"],
        )

    allocation_quote = deepcopy(record["allocation_quote"])
    allocation_quote["genesis_overhead_pool_label"] = "genesis_tranche"
    with pytest.raises(
        ValueError,
        match="cdl029_allocation_genesis_overhead_pool_label_mismatch_phase_1568_fix2q",
    ):
        build_genesis_tranche_reconciliation_quote(
            fee_burn_quote=record["epoch_emission_result"]["fee_burn_quote"],
            allocation_quote=allocation_quote,
            cdl048_conversion_quote=record["cdl048_conversion_quote"],
        )


def test_fix2q_runtime_rejects_activated_cdl048_quote() -> None:
    record = _record()
    quote = deepcopy(record["cdl048_conversion_quote"])
    quote["wallet_write_authorized"] = True

    with pytest.raises(ValueError, match="cdl048_conversion_wallet_write_authorized"):
        build_genesis_tranche_reconciliation_quote(
            fee_burn_quote=record["epoch_emission_result"]["fee_burn_quote"],
            allocation_quote=record["allocation_quote"],
            cdl048_conversion_quote=quote,
        )


def test_fix2q_verifier_remains_backward_compatible_with_pre_fix2q_records() -> None:
    record = deepcopy(_record())
    record.pop("genesis_tranche_reconciliation")
    record.pop("genesis_tranche_reconciliation_verified")
    record["settlement_root_inputs_sha256"] = settlement_root_inputs_hash(record)

    verification = verify_rehearsal_economics_record(record)

    assert verification["settlement_root_verified"] is True
    assert verification["genesis_tranche_reconciliation_verified"] is False


def test_fix2q_direct_reconciliation_verifier_accepts_canonical_record() -> None:
    record = _record()
    verification = verify_genesis_tranche_reconciliation_record(
        record["genesis_tranche_reconciliation"]
    )

    assert verification["verified"] is True
    assert verification["quote_read_model_only"] is True
    assert verification["wallet_write_authorized"] is False
    assert verification["treasury_write_authorized"] is False
