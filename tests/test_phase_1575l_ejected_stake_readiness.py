# SPDX-License-Identifier: AGPL-3.0-only

from __future__ import annotations

import hashlib
import json
from decimal import Decimal

import pytest

from ilc_core.epoch.ejected_stake_distribution_production_path import (
    EJECTED_STAKE_DISTRIBUTION_PRODUCTION_NOT_ACTIVATED,
    EJECTED_STAKE_DISTRIBUTION_PRODUCTION_NOT_ACTIVATED_TOKEN,
    build_ejected_stake_distribution_result,
    require_ejected_stake_distribution_production_activation,
)
from tools.phase_1575l_ejected_stake_readiness import (
    build_phase_1575l_evidence,
    stable_json,
)


def test_phase_1575l_guard_remains_default_off_and_raises_not_implemented() -> None:
    assert EJECTED_STAKE_DISTRIBUTION_PRODUCTION_NOT_ACTIVATED is True
    with pytest.raises(
        NotImplementedError,
        match=EJECTED_STAKE_DISTRIBUTION_PRODUCTION_NOT_ACTIVATED_TOKEN,
    ):
        require_ejected_stake_distribution_production_activation()


def test_phase_1575l_rehearsal_uses_real_production_wrapper() -> None:
    result = build_ejected_stake_distribution_result(
        {
            "distribution_epoch": 1575,
            "ejected_stake_ilc": Decimal("123.456789123"),
            "remaining_member_stakes": {
                "agent:phase1575l_validator_a": Decimal("100.000000000"),
                "agent:phase1575l_validator_b": Decimal("200.000000000"),
                "agent:phase1575l_validator_c": Decimal("300.000000000"),
            },
            "approve_votes": 3,
            "participating_voters": 3,
        }
    )

    assert result.production_ejected_stake_distribution_activated is False
    assert result.distribution_quote.payouts == (
        ("agent:phase1575l_validator_a", Decimal("20.576131520")),
        ("agent:phase1575l_validator_b", Decimal("41.152263041")),
        ("agent:phase1575l_validator_c", Decimal("61.728394562")),
    )
    assert sum((amount for _, amount in result.distribution_quote.payouts), Decimal("0")) == (
        result.distribution_quote.ejected_stake_ilc
    )
    assert all(isinstance(amount, Decimal) for _, amount in result.distribution_quote.payouts)


def test_phase_1575l_evidence_certificate_records_non_claims_and_conservation() -> None:
    evidence = build_phase_1575l_evidence()
    event = evidence["event_record"]
    certificate = evidence["certificate"]

    assert event["decimal_conservation_verified"] is True
    assert event["fail_closed_behavior_verified"] is True
    assert event["treasury_amount"] is None
    assert event["treasury_routes_to_genesis_agent1"] is False
    assert "genesis_agent:01" not in stable_json(event)
    assert certificate["guard_value"] is True
    assert certificate["guard_cleared"] is False
    assert certificate["rehearsal_passed"] is True
    assert certificate["no_wallet_writes"] is True
    assert certificate["no_live_stake_redistribution"] is True
    assert certificate["no_ecu_minted"] is True
    assert certificate["no_ilc_settled"] is True
    assert certificate["treasury_routing_non_genesis"] is True
    assert certificate["double_lock_exception_type"] == "NotImplementedError"


def test_phase_1575l_fail_closed_quorum_reduces_to_exception() -> None:
    with pytest.raises(
        ValueError,
        match="h_con_02_quorum_guard_minimum_voters_not_met_phase_1350",
    ):
        build_ejected_stake_distribution_result(
            {
                "distribution_epoch": 1575,
                "ejected_stake_ilc": Decimal("123.456789123"),
                "remaining_member_stakes": {
                    "agent:phase1575l_validator_a": Decimal("100.000000000"),
                    "agent:phase1575l_validator_b": Decimal("200.000000000"),
                    "agent:phase1575l_validator_c": Decimal("300.000000000"),
                },
                "approve_votes": 1,
                "participating_voters": 1,
            }
        )


def test_phase_1575l_stable_json_rejects_float_and_non_finite_decimal() -> None:
    with pytest.raises(ValueError, match="float_in_phase_1575l_evidence_rejected"):
        stable_json({"amount": 0.1})
    with pytest.raises(ValueError, match="invalid_decimal_in_phase_1575l_evidence"):
        stable_json({"amount": Decimal("NaN")})


def test_phase_1575l_evidence_is_canonical_and_deterministic() -> None:
    first = build_phase_1575l_evidence()
    second = build_phase_1575l_evidence()

    assert stable_json(first) == stable_json(second)
    event_without_hash = {
        k: v for k, v in first["event_record"].items() if k != "event_record_sha256"
    }
    assert hashlib.sha256(stable_json(event_without_hash).encode("utf-8")).hexdigest() == (
        first["event_record"]["event_record_sha256"]
    )
    cert_without_hash = {
        k: v for k, v in first["certificate"].items() if k != "certificate_sha256"
    }
    assert hashlib.sha256(stable_json(cert_without_hash).encode("utf-8")).hexdigest() == (
        first["certificate"]["certificate_sha256"]
    )


def test_phase_1575l_written_json_shape(tmp_path, monkeypatch) -> None:
    from tools import phase_1575l_ejected_stake_readiness as tool

    monkeypatch.setattr(tool, "OUTPUT_DIR", tmp_path)
    monkeypatch.setattr(tool, "EVENT_PATH", tmp_path / "event.json")
    monkeypatch.setattr(tool, "CERTIFICATE_PATH", tmp_path / "certificate.json")

    receipt = tool.write_phase_1575l_evidence()
    event = json.loads((tmp_path / "event.json").read_text())
    certificate = json.loads((tmp_path / "certificate.json").read_text())

    assert receipt["status"] == "PASS"
    assert event["phase"] == "1575l"
    assert certificate["phase"] == "1575l"
    assert receipt["event_sha256"] == hashlib.sha256((tmp_path / "event.json").read_bytes()).hexdigest()
    assert receipt["certificate_sha256"] == hashlib.sha256(
        (tmp_path / "certificate.json").read_bytes()
    ).hexdigest()
