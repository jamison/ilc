"""Phase 1543p Block 4B round-trip integration tests."""

from __future__ import annotations

import json
from dataclasses import replace
from decimal import Decimal

import pytest

from ilc_core.economics.productive_ecu_expansion_bounty_runtime import (
    PRODUCTIVE_ECU_EXPANSION_NOT_ACTIVATED,
    build_bounty_delivery_stub,
    build_bounty_issuance_quote,
    compute_bounty_accounting_settlement_root,
    emit_canonical_bounty_accounting_events,
)
from ilc_core.epoch.ejected_stake_distribution_production_path import (
    EJECTED_STAKE_DISTRIBUTION_PRODUCTION_NOT_ACTIVATED,
    build_ejected_stake_distribution_result,
    compute_ejected_stake_settlement_root,
    emit_canonical_ejected_stake_distribution_events,
)
from ilc_core.epoch.treasury_validator_reward_production_path import (
    TREASURY_DISTRIBUTION_NOT_ACTIVATED,
    build_treasury_validator_reward_result,
    compute_treasury_distribution_settlement_root,
    emit_canonical_treasury_distribution_events,
)
from ilc_core.identity.agent_id_runtime import derive_agent_id_v2
from ilc_core.validator.validator_admission_ejection_production_path import (
    VALIDATOR_ADMISSION_NOT_ACTIVATED,
    build_validator_set_transition_result,
    compute_validator_transition_settlement_root,
    emit_canonical_validator_set_transition_events,
)


def _canonical_json(payload: dict[str, object]) -> str:
    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
        ensure_ascii=True,
    )


def _agent_id(seed_byte: int = 17) -> str:
    return derive_agent_id_v2(bytes([seed_byte]) * 32)


def _validator_admit_inputs(validator_id: int = 5) -> dict[str, object]:
    return {
        "current_epoch": 10,
        "active_from_epoch": 11,
        "current_validator_ids": [1, 2, 3, 4],
        "validator_id": validator_id,
        "agent_id": _agent_id(validator_id),
        "stake_ecu": Decimal("400"),
    }


def _validator_eject_inputs(validator_id: int = 2) -> dict[str, object]:
    return {
        "current_epoch": 10,
        "active_from_epoch": 11,
        "current_validator_ids": [1, 2, 3, 4],
        "validator_id": validator_id,
        "exit_reason": "voluntary_exit",
    }


def _validator_result():
    return build_validator_set_transition_result(
        _validator_admit_inputs(),
        _validator_eject_inputs(),
    )


def _treasury_inputs() -> dict[str, object]:
    return {
        "issuance_epoch": 3,
        "epoch_budget_ilc": Decimal("356202.705201831"),
        "requested_bounty_ilc": Decimal("1000"),
        "planned_burn_ilc": Decimal("20000"),
        "treasury_planned_burn_ilc": Decimal("20000"),
        "observed_velocity": Decimal("0.95"),
        "write_fee_burn_pool_ilc": Decimal("50000"),
        "cumulative_issued_before_epoch_ilc": Decimal("1000"),
    }


def _treasury_result():
    return build_treasury_validator_reward_result(_treasury_inputs())


def _ejected_stake_inputs() -> dict[str, object]:
    return {
        "distribution_epoch": 7,
        "ejected_stake_ilc": Decimal("9.000000001"),
        "remaining_member_stakes": {
            "agent_alpha": Decimal("10"),
            "agent_beta": Decimal("20"),
            "agent_gamma": Decimal("30"),
        },
        "approve_votes": 2,
        "participating_voters": 2,
    }


def _ejected_stake_result():
    return build_ejected_stake_distribution_result(_ejected_stake_inputs())


def _bounty_quote_and_stub():
    return build_bounty_issuance_quote(Decimal("1000"), Decimal("200")), (
        build_bounty_delivery_stub("bounty-alpha")
    )


def _tampered_root(root):
    payload = json.loads(root.canonical_record_json)
    payload["event_payloads"] = []
    return replace(root, canonical_record_json=_canonical_json(payload))


def test_obl021_validator_transition_result_serializes() -> None:
    result = _validator_result()

    serialized = _canonical_json(result.to_canonical_record())
    assert json.loads(serialized)["production_validator_admission_activated"] is False


def test_obl021_replay_root_equals_original_root() -> None:
    result = _validator_result()
    root = compute_validator_transition_settlement_root(result)
    replayed = compute_validator_transition_settlement_root(result)

    assert root.root_hex == replayed.root_hex
    assert root.canonical_record_json == replayed.canonical_record_json


def test_obl021_emit_accepts_correct_root_and_serializes_events() -> None:
    result = _validator_result()
    root = compute_validator_transition_settlement_root(result)
    events = emit_canonical_validator_set_transition_events(result, root)
    event_dicts = [json.loads(event.to_canonical_json()) for event in events]

    assert len(event_dicts) == 2
    assert {event["settlement_root_hex"] for event in event_dicts} == {root.root_hex}


def test_obl021_guard_token_propagates() -> None:
    result = _validator_result()
    root = compute_validator_transition_settlement_root(result)
    events = emit_canonical_validator_set_transition_events(result, root)

    assert VALIDATOR_ADMISSION_NOT_ACTIVATED is True
    assert result.production_validator_admission_activated is False
    assert all(event.production_validator_admission_activated is False for event in events)


def test_obl021_stale_root_rejected() -> None:
    result = _validator_result()
    root = compute_validator_transition_settlement_root(result)

    with pytest.raises(ValueError, match="settlement_root_event_payload_mismatch"):
        emit_canonical_validator_set_transition_events(result, _tampered_root(root))


def test_obl022_treasury_distribution_result_serializes() -> None:
    result = _treasury_result()

    serialized = _canonical_json(result.to_canonical_record())
    assert json.loads(serialized)["production_treasury_distribution_activated"] is False


def test_obl022_treasury_replay_root_equals_original_root() -> None:
    result = _treasury_result()
    root = compute_treasury_distribution_settlement_root(result)
    replayed = compute_treasury_distribution_settlement_root(result)

    assert root.root_hex == replayed.root_hex
    assert root.canonical_record_json == replayed.canonical_record_json


def test_obl022_treasury_guard_propagates_to_events() -> None:
    result = _treasury_result()
    root = compute_treasury_distribution_settlement_root(result)
    events = emit_canonical_treasury_distribution_events(result, root)

    assert TREASURY_DISTRIBUTION_NOT_ACTIVATED is True
    assert result.production_treasury_distribution_activated is False
    assert all(event.production_treasury_distribution_activated is False for event in events)
    assert {event.settlement_root_hex for event in events} == {root.root_hex}


def test_obl022_ejected_stake_result_serializes() -> None:
    result = _ejected_stake_result()

    serialized = _canonical_json(result.to_canonical_record())
    assert (
        json.loads(serialized)["production_ejected_stake_distribution_activated"]
        is False
    )


def test_obl022_ejected_stake_replay_root_equals_original_root() -> None:
    result = _ejected_stake_result()
    root = compute_ejected_stake_settlement_root(result)
    replayed = compute_ejected_stake_settlement_root(result)

    assert root.root_hex == replayed.root_hex
    assert root.canonical_record_json == replayed.canonical_record_json


def test_obl022_ejected_stake_guard_propagates_to_events() -> None:
    result = _ejected_stake_result()
    root = compute_ejected_stake_settlement_root(result)
    events = emit_canonical_ejected_stake_distribution_events(result, root)

    assert EJECTED_STAKE_DISTRIBUTION_PRODUCTION_NOT_ACTIVATED is True
    assert result.production_ejected_stake_distribution_activated is False
    assert all(
        event.production_ejected_stake_distribution_activated is False
        for event in events
    )
    assert {event.settlement_root_hex for event in events} == {root.root_hex}


def test_obl027_bounty_accounting_result_serializes() -> None:
    quote, stub = _bounty_quote_and_stub()

    quote_serialized = _canonical_json(quote.to_canonical_record())
    stub_serialized = _canonical_json(stub.to_canonical_record())

    assert json.loads(quote_serialized)["production_bounty_activated"] is False
    assert json.loads(stub_serialized)["production_bounty_activated"] is False


def test_obl027_bounty_replay_root_equals_original_root() -> None:
    quote, stub = _bounty_quote_and_stub()
    root = compute_bounty_accounting_settlement_root(quote, stub)
    replayed = compute_bounty_accounting_settlement_root(quote, stub)

    assert root.root_hex == replayed.root_hex
    assert root.canonical_record_json == replayed.canonical_record_json


def test_obl027_bounty_guard_propagates_to_events() -> None:
    quote, stub = _bounty_quote_and_stub()
    root = compute_bounty_accounting_settlement_root(quote, stub)
    events = emit_canonical_bounty_accounting_events(quote, stub, root)

    assert PRODUCTIVE_ECU_EXPANSION_NOT_ACTIVATED is True
    assert quote.production_bounty_activated is False
    assert stub.production_bounty_activated is False
    assert all(event.production_activated is False for event in events)
    assert {event.settlement_root_hex for event in events} == {root.root_hex}
