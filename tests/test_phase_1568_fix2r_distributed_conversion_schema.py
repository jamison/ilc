from __future__ import annotations

from copy import deepcopy
from decimal import Decimal

import pytest

from ilc_core.epoch import epoch_boundary_witness_runtime
from ilc_core.ledger.distributed_conversion_schema import (
    CDL029_GENESIS_OVERHEAD_POOL_LABEL,
    CDL057_WITNESS_ABSENT_TOKEN,
    GENESIS_TRANCHE_APPLIED_BY_AUTHORIZED_VALUE_PATH,
    GENESIS_TRANCHE_EXPLICITLY_DEFERRED,
    VERIFIER_ROOT_PREFIX,
    ConversionCandidate,
    attach_cdl057_witness_ref,
    build_conversion_candidate_from_quote,
    build_conversion_resolution,
    validate_genesis_tranche_treatment_source,
    verify_conversion_resolution,
)
from tests.test_phase_1568_fix2l_rehearsal_economics_record import _record
from tools.testbed.rehearsal_economics import (
    RehearsalEconomicsError,
    settlement_root_inputs_hash,
    verify_rehearsal_economics_record,
)


def _resolution_record() -> dict[str, object]:
    quote = _record()["cdl048_conversion_quote"]
    candidate = build_conversion_candidate_from_quote(quote)
    candidate = attach_cdl057_witness_ref(candidate, epoch_boundary_witness_runtime)
    resolution = build_conversion_resolution(
        candidate,
        resolution_status="pending",
        resolution_epoch=candidate.conversion_epoch,
    )
    return resolution.to_canonical_record()


def test_fix2r_candidate_and_resolution_are_distinct_canonical_records() -> None:
    quote = _record()["cdl048_conversion_quote"]
    candidate = build_conversion_candidate_from_quote(quote)
    assert candidate.to_canonical_record()["genesis_tranche_treatment"] == (
        GENESIS_TRANCHE_EXPLICITLY_DEFERRED
    )
    assert "resolution_status" not in candidate.to_canonical_record()

    resolution = _resolution_record()
    verification = verify_conversion_resolution(resolution)

    assert verification["ok"] is True
    assert resolution["resolution_status"] == "pending"
    assert resolution["verifier_root"].startswith(VERIFIER_ROOT_PREFIX)
    assert resolution["genesis_tranche_treatment"] == GENESIS_TRANCHE_EXPLICITLY_DEFERRED
    assert resolution["cdl057_witness_ref"] == CDL057_WITNESS_ABSENT_TOKEN
    assert resolution["quote_read_model_only"] is True


def test_fix2r_genesis_tranche_treatment_is_required_and_enumerated() -> None:
    quote = _record()["cdl048_conversion_quote"]
    with pytest.raises(ValueError, match="genesis_tranche_treatment_required"):
        build_conversion_candidate_from_quote(quote, genesis_tranche_treatment="")
    with pytest.raises(ValueError, match="genesis_tranche_treatment_invalid"):
        build_conversion_candidate_from_quote(quote, genesis_tranche_treatment="absent")


def test_fix2r_candidate_rejects_float_and_non_finite_amounts() -> None:
    quote = deepcopy(_record()["cdl048_conversion_quote"])
    quote["amount_ecu_debit"] = 1.0
    with pytest.raises(ValueError, match="distributed_conversion_float_rejected"):
        build_conversion_candidate_from_quote(quote)

    with pytest.raises(ValueError, match="amount_ecu_invalid"):
        ConversionCandidate(
            lot_id="lot",
            agent_id="agent",
            amount_ecu=Decimal("NaN"),
            issue_epoch=1,
            deadline_epoch=5,
            conversion_epoch=1,
            genesis_tranche_treatment=GENESIS_TRANCHE_EXPLICITLY_DEFERRED,
            cdl057_witness_ref=CDL057_WITNESS_ABSENT_TOKEN,
            candidate_source="test",
        )


def test_fix2r_verifier_rejects_write_authorization_and_noncanonical_records() -> None:
    resolution = _resolution_record()
    tampered = deepcopy(resolution)
    tampered["wallet_write_authorized"] = True
    assert verify_conversion_resolution(tampered) == {
        "ok": False,
        "reason": "wallet_write_authorized_forbidden_phase_1568_fix2r",
    }

    missing_token = deepcopy(resolution)
    missing_token.pop("tokens")
    assert verify_conversion_resolution(missing_token) == {
        "ok": False,
        "reason": "conversion_resolution_not_canonical",
    }


def test_fix2r_cdl029_overhead_pool_cannot_satisfy_fixed_tranche() -> None:
    with pytest.raises(
        ValueError,
        match="cdl029_overhead_pool_cannot_satisfy_fixed_genesis_tranche",
    ):
        validate_genesis_tranche_treatment_source(
            genesis_tranche_treatment=GENESIS_TRANCHE_APPLIED_BY_AUTHORIZED_VALUE_PATH,
            source_label=CDL029_GENESIS_OVERHEAD_POOL_LABEL,
        )
    with pytest.raises(
        ValueError,
        match="cdl029_overhead_pool_cannot_satisfy_fixed_genesis_tranche",
    ):
        build_conversion_candidate_from_quote(
            _record()["cdl048_conversion_quote"],
            genesis_tranche_treatment=GENESIS_TRANCHE_APPLIED_BY_AUTHORIZED_VALUE_PATH,
            genesis_tranche_source=CDL029_GENESIS_OVERHEAD_POOL_LABEL,
        )


def test_fix2r_rehearsal_economics_record_includes_resolution_in_root_inputs() -> None:
    record = _record()
    resolution = record["cdl048_conversion_resolution"]
    verification = verify_rehearsal_economics_record(record)

    assert record["cdl048_conversion_resolution_verified"] is True
    assert verification["cdl048_conversion_resolution_verified"] is True
    assert resolution["cdl057_witness_ref"] == CDL057_WITNESS_ABSENT_TOKEN
    assert resolution["genesis_tranche_treatment"] == GENESIS_TRANCHE_EXPLICITLY_DEFERRED
    assert record["settlement_root_inputs_sha256"] == settlement_root_inputs_hash(record)


def test_fix2r_rehearsal_verifier_rejects_resolution_mismatch() -> None:
    record = deepcopy(_record())
    record["cdl048_conversion_resolution"]["cdl057_witness_ref"] = "tampered"
    record["settlement_root_inputs_sha256"] = settlement_root_inputs_hash(record)

    with pytest.raises(RehearsalEconomicsError) as excinfo:
        verify_rehearsal_economics_record(record)

    assert excinfo.value.token == "cdl048_conversion_resolution_invalid"


def test_fix2r_source_does_not_activate_value_write_paths() -> None:
    record = _record()
    resolution = record["cdl048_conversion_resolution"]

    assert record["cdl048_wallet_write_authorized"] is False
    assert resolution["wallet_write_authorized"] is False
    assert resolution["treasury_write_authorized"] is False
    assert resolution["production_minting_authorized"] is False
    assert resolution["ilc_settlement_authorized"] is False
    assert resolution["public_claimability_activated"] is False
