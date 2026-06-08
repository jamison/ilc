"""Phase 1542p OBL-027 productive ECU expansion bounty scaffold tests."""

from __future__ import annotations

import hashlib
import json
from dataclasses import replace
from decimal import Decimal

import pytest

from ilc_core.economics.productive_ecu_expansion_bounty_runtime import (
    ADR_0016_STATUS_PROPOSED,
    BOUNTY_CAP_FRACTION_OF_EPOCH_BUDGET,
    BOUNTY_PANEL_ASSIGNMENT_NOT_IMPLEMENTED,
    CANONICAL_BOUNTY_ACCOUNTING_EVENT_SCHEMA_VERSION,
    PRODUCTIVE_ECU_EXPANSION_BOUNTY_RUNTIME_VERSION,
    PRODUCTIVE_ECU_EXPANSION_NOT_ACTIVATED,
    PRODUCTIVE_ECU_EXPANSION_NOT_ACTIVATED_TOKEN,
    SETTLEMENT_ROOT_SCHEMA_VERSION,
    BountyAccountingSettlementRoot,
    build_bounty_delivery_stub,
    build_bounty_issuance_quote,
    build_canonical_bounty_accounting_event_payloads,
    compute_bounty_accounting_settlement_root,
    emit_canonical_bounty_accounting_events,
    require_productive_ecu_expansion_activation,
)


def _quote(
    epoch_budget_ecu: Decimal = Decimal("1000"),
    requested_bounty_ecu: Decimal = Decimal("200"),
):
    return build_bounty_issuance_quote(epoch_budget_ecu, requested_bounty_ecu)


def _stub(bounty_id: str = "bounty-alpha"):
    return build_bounty_delivery_stub(bounty_id)


def test_phase_1542p_guard_and_adr_status_boundary() -> None:
    assert PRODUCTIVE_ECU_EXPANSION_NOT_ACTIVATED is True
    assert PRODUCTIVE_ECU_EXPANSION_NOT_ACTIVATED_TOKEN == (
        "productive_ecu_expansion_not_activated_phase_1542p"
    )
    assert ADR_0016_STATUS_PROPOSED == (
        "adr_0016_status_proposed_bounty_activation_requires_governance_event"
    )

    with pytest.raises(
        NotImplementedError,
        match="productive_ecu_expansion_not_activated_phase_1542p",
    ):
        require_productive_ecu_expansion_activation()


def test_phase_1542p_cdl047_cap_enforced_without_debt() -> None:
    quote = _quote()

    assert quote.runtime_version == PRODUCTIVE_ECU_EXPANSION_BOUNTY_RUNTIME_VERSION
    assert quote.cap_fraction_of_epoch_budget == BOUNTY_CAP_FRACTION_OF_EPOCH_BUDGET
    assert quote.requested_ecu == Decimal("200.000000000")
    assert quote.cap_ecu == Decimal("150.000000000")
    assert quote.approved_ecu == Decimal("150.000000000")
    assert quote.cap_fraction_applied is True
    assert quote.production_bounty_activated is False


def test_phase_1542p_uncapped_request_is_approved_at_requested_amount() -> None:
    quote = _quote(requested_bounty_ecu=Decimal("50"))

    assert quote.cap_ecu == Decimal("150.000000000")
    assert quote.approved_ecu == Decimal("50.000000000")
    assert quote.cap_fraction_applied is False


def test_phase_1542p_zero_budget_creates_zero_approved_ecu_not_debt() -> None:
    quote = _quote(epoch_budget_ecu=Decimal("0"), requested_bounty_ecu=Decimal("10"))

    assert quote.cap_ecu == Decimal("0E-9")
    assert quote.approved_ecu == Decimal("0E-9")
    assert quote.cap_fraction_applied is True


def test_phase_1542p_rejects_non_finite_and_float_inputs() -> None:
    with pytest.raises(ValueError, match="epoch_budget_ecu_must_be_exact_decimal"):
        build_bounty_issuance_quote(1.0, Decimal("1"))

    with pytest.raises(ValueError, match="invalid_amount_non_finite"):
        build_bounty_issuance_quote(Decimal("NaN"), Decimal("1"))


def test_phase_1542p_delivery_stub_records_panel_requirements_without_activation() -> None:
    stub = _stub()

    assert stub.bounty_id == "bounty-alpha"
    assert stub.panel_assignment_result == BOUNTY_PANEL_ASSIGNMENT_NOT_IMPLEMENTED
    assert stub.cdl_v3_diversity_requirement_recorded is True
    assert stub.cdl_v7_popperian_gate_requirement_recorded is True
    assert stub.peer_funded_bounty_excluded is True
    assert stub.adr_0016_status == ADR_0016_STATUS_PROPOSED
    assert stub.production_bounty_activated is False


def test_phase_1542p_settlement_root_replays_deterministically() -> None:
    first = compute_bounty_accounting_settlement_root(_quote(), _stub())
    second = compute_bounty_accounting_settlement_root(_quote(), _stub())

    assert isinstance(first, BountyAccountingSettlementRoot)
    assert first.root_hex == second.root_hex
    assert first.canonical_record_json == second.canonical_record_json


def test_phase_1542p_digest_matches_canonical_record_json() -> None:
    root = compute_bounty_accounting_settlement_root(_quote(), _stub())

    digest = hashlib.sha256(root.canonical_record_json.encode("utf-8")).hexdigest()
    assert digest == root.root_hex
    assert len(root.root_hex) == 64


def test_phase_1542p_root_payload_excludes_settlement_root_hex() -> None:
    root = compute_bounty_accounting_settlement_root(_quote(), _stub())
    payload = json.loads(root.canonical_record_json)

    assert payload["schema_version"] == SETTLEMENT_ROOT_SCHEMA_VERSION
    assert "settlement_root_hex" not in payload
    assert "settlement_root_hex" not in root.canonical_record_json


def test_phase_1542p_emits_canonical_events_with_proposed_status() -> None:
    quote = _quote()
    stub = _stub()
    root = compute_bounty_accounting_settlement_root(quote, stub)
    events = emit_canonical_bounty_accounting_events(quote, stub, root)

    assert [event.event_type for event in events] == [
        "productive_ecu_expansion_bounty_issuance_quote",
        "productive_ecu_expansion_bounty_delivery_stub",
    ]
    assert {event.settlement_root_hex for event in events} == {root.root_hex}
    assert all(event.adr_0016_status == ADR_0016_STATUS_PROPOSED for event in events)
    assert all(event.production_activated is False for event in events)
    assert all(event.peer_funded_bounty_excluded is True for event in events)
    assert all(
        event.schema_version == CANONICAL_BOUNTY_ACCOUNTING_EVENT_SCHEMA_VERSION
        for event in events
    )


def test_phase_1542p_root_commits_to_event_payload_batch() -> None:
    quote = _quote()
    stub = _stub()
    root = compute_bounty_accounting_settlement_root(quote, stub)
    events = emit_canonical_bounty_accounting_events(quote, stub, root)
    root_payload = json.loads(root.canonical_record_json)
    event_payloads_without_root = [
        {
            key: value
            for key, value in event.to_canonical_record().items()
            if key != "settlement_root_hex"
        }
        for event in events
    ]

    assert root_payload["event_payloads"] == event_payloads_without_root
    assert event_payloads_without_root == build_canonical_bounty_accounting_event_payloads(
        quote,
        stub,
    )


def test_phase_1542p_rejects_stale_settlement_root() -> None:
    quote = _quote()
    stub = _stub()
    stale_root = compute_bounty_accounting_settlement_root(_quote(requested_bounty_ecu=50), stub)

    with pytest.raises(ValueError, match="settlement_root_event_payload_mismatch"):
        emit_canonical_bounty_accounting_events(quote, stub, stale_root)


def test_phase_1542p_rejects_float_before_root() -> None:
    quote = _quote()
    bad_quote = replace(quote, approved_ecu=1.0)

    with pytest.raises(ValueError, match="float_in_bounty_accounting_record_rejected"):
        compute_bounty_accounting_settlement_root(bad_quote, _stub())
