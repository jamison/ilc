"""Phase 1533p OBL-020 settlement-root replay invariant tests."""

from __future__ import annotations

import hashlib
import json
from dataclasses import replace
from decimal import Decimal

import pytest

from ilc_core.epoch.epoch_emission_production_path import (
    PRODUCTION_EMISSION_NOT_ACTIVATED,
    EpochSettlementRoot,
    compute_epoch_emission_production_path,
    compute_settlement_root,
)


def _result(epoch: int = 7, fees: Decimal = Decimal("123.456789123")):
    return compute_epoch_emission_production_path(
        epoch,
        Decimal("1000.000000001"),
        fees,
    )


def test_phase_1533p_same_result_replays_same_root() -> None:
    first = compute_settlement_root(_result())
    second = compute_settlement_root(_result())

    assert isinstance(first, EpochSettlementRoot)
    assert first.root_hex == second.root_hex
    assert first.canonical_record_json == second.canonical_record_json


def test_phase_1533p_different_epoch_changes_root() -> None:
    first = compute_settlement_root(_result(epoch=7))
    second = compute_settlement_root(_result(epoch=8))

    assert first.root_hex != second.root_hex


def test_phase_1533p_decimal_field_change_changes_root() -> None:
    first = compute_settlement_root(_result(fees=Decimal("123.456789123")))
    second = compute_settlement_root(_result(fees=Decimal("123.456789124")))

    assert first.root_hex != second.root_hex


def test_phase_1533p_digest_matches_canonical_record_json() -> None:
    root = compute_settlement_root(_result())

    digest = hashlib.sha256(root.canonical_record_json.encode("utf-8")).hexdigest()
    assert digest == root.root_hex


def test_phase_1533p_rejects_non_finite_decimal_before_root() -> None:
    result = _result()
    bad_fee_quote = replace(result.fee_burn_quote, total_epoch_fees_ilc=Decimal("NaN"))
    bad_result = replace(result, fee_burn_quote=bad_fee_quote)

    with pytest.raises(ValueError, match="invalid_amount_non_finite"):
        compute_settlement_root(bad_result)


def test_phase_1533p_rejects_float_before_root() -> None:
    result = _result()
    bad_fee_quote = replace(result.fee_burn_quote, total_epoch_fees_ilc=1.0)
    bad_result = replace(result, fee_burn_quote=bad_fee_quote)

    with pytest.raises(ValueError, match="float_in_canonical_record_rejected"):
        compute_settlement_root(bad_result)


def test_phase_1533p_root_metadata_and_guard_floor() -> None:
    root = compute_settlement_root(_result())

    assert PRODUCTION_EMISSION_NOT_ACTIVATED is True
    assert root.issuance_epoch == 7
    assert root.root_algorithm == "sha256_over_canonical_json"
    assert len(root.root_hex) == 64


def test_phase_1533p_anti_circularity_excludes_settlement_root_hex() -> None:
    root = compute_settlement_root(_result())
    payload = json.loads(root.canonical_record_json)

    assert "settlement_root_hex" not in payload
    assert "settlement_root_hex" not in root.canonical_record_json


def test_phase_1575c_fix3d_settlement_root_excludes_governor_report() -> None:
    result = compute_epoch_emission_production_path(
        7,
        Decimal("1000.000000001"),
        Decimal("123.456789123"),
        genesis_cumulative_accrual_ilc=Decimal("10"),
    )
    assert result.governor_report is not None

    root = compute_settlement_root(result)
    payload = json.loads(root.canonical_record_json)

    assert "governor_report" not in payload
    assert "governor_report" not in root.canonical_record_json


def test_phase_1537p_fix1_root_commits_to_canonical_event_payloads() -> None:
    result = _result()
    root = compute_settlement_root(result)
    payload = json.loads(root.canonical_record_json)

    assert payload["schema_version"] == "epoch_emission_event_batch_root_1537p_fix1.v0.2"
    assert [event["role"] for event in payload["economic_event_payloads"]] == [
        "scheduled_emission_pool",
        "performer_pool",
        "auditor_pool",
        "genesis_overhead_pool",
        "genesis_burn_pool",
    ]
    assert payload["rounding_residual_metadata"]["residual_route"] in {
        "genesis",
        "performer_pool",
        "upheld_refutation_recipients",
    }
