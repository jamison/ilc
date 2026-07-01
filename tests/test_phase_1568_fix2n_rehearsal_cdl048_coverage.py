from __future__ import annotations

from copy import deepcopy

import pytest

from tests.test_phase_1568_fix2l_rehearsal_economics_record import _record
from tools.testbed.rehearsal_economics import (
    RehearsalEconomicsError,
    settlement_root_inputs_hash,
    verify_rehearsal_economics_record,
)


def test_fix2n_record_materializes_one_lot_per_positive_ecu_claim() -> None:
    record = _record()
    coverage = record["cdl048_per_agent_lot_coverage"]
    positive_claim_ids = {
        claim["claim_id"]
        for claim in record["ecu_claims"]
        if claim["amount"] != "0"
    }

    assert coverage["positive_claim_count"] == len(positive_claim_ids)
    assert coverage["lot_count"] == len(positive_claim_ids)
    assert coverage["per_agent_lot_count_matches_positive_claim_count"] is True
    assert len(coverage["lots"]) == len(positive_claim_ids)
    assert {item["lot"]["funding_provenance"][0] for item in coverage["lots"]} == positive_claim_ids


def test_fix2n_records_issue_through_deadline_quote_sequence_for_every_lot() -> None:
    record = _record()
    coverage = record["cdl048_per_agent_lot_coverage"]
    expected_sequence = [574, 575, 576, 577, 578]

    assert coverage["issuance_epoch_sequence"] == expected_sequence
    assert coverage["four_issuance_epoch_intervals_covered"] == 4
    assert coverage["coverage_checkpoint_count_per_lot"] == 5
    assert coverage["deadline_epoch"] == 578

    for item in coverage["lots"]:
        assert item["lot"]["issue_epoch"] == 574
        assert item["lot"]["deadline_epoch"] == 578
        assert item["quote_count"] == 5
        assert [status["current_epoch"] for status in item["deadline_status_by_epoch"]] == expected_sequence
        assert [quote["conversion_epoch"] for quote in item["quotes_by_epoch"]] == expected_sequence
        assert item["deadline_status_by_epoch"][-1]["deadline_status"] == "deadline_epoch"


def test_fix2n_every_nested_cdl048_quote_remains_quote_only_no_write() -> None:
    record = _record()
    for item in record["cdl048_per_agent_lot_coverage"]["lots"]:
        for quote in item["quotes_by_epoch"]:
            assert quote["quote_only"] is True
            assert quote["conversion_activation_authorized"] is False
            assert quote["ledger_write_authorized"] is False
            assert quote["wallet_write_authorized"] is False
            assert quote["public_claimability_activated"] is False


def test_fix2n_verifier_rejects_nested_wallet_write_authorization() -> None:
    record = deepcopy(_record())
    record["cdl048_per_agent_lot_coverage"]["lots"][0]["quotes_by_epoch"][0][
        "wallet_write_authorized"
    ] = True

    with pytest.raises(RehearsalEconomicsError) as excinfo:
        verify_rehearsal_economics_record(record)

    assert excinfo.value.token == "cdl048_per_agent_quote_write_authorization_forbidden"


def test_fix2n_verifier_rejects_truncated_deadline_sequence() -> None:
    record = deepcopy(_record())
    record["cdl048_per_agent_lot_coverage"]["issuance_epoch_sequence"] = [574, 575, 576, 577]

    with pytest.raises(RehearsalEconomicsError) as excinfo:
        verify_rehearsal_economics_record(record)

    assert excinfo.value.token == "cdl048_issuance_epoch_sequence_invalid"


def test_fix2n_verifier_remains_backward_compatible_with_fix2l_records() -> None:
    record = deepcopy(_record())
    for key in (
        "cdl048_conversion_coverage_mode",
        "cdl048_four_issuance_epoch_quote_coverage_verified",
        "cdl048_per_agent_lot_coverage",
        "cdl048_per_agent_lot_coverage_verified",
    ):
        record.pop(key)
    record["settlement_root_inputs_sha256"] = settlement_root_inputs_hash(record)

    verification = verify_rehearsal_economics_record(record)

    assert verification["settlement_root_verified"] is True
    assert verification["cdl048_per_agent_lot_coverage_verified"] is False
