"""Phase 1539p OBL-021 validator admission/ejection production-path tests."""

from __future__ import annotations

import hashlib
import json
from dataclasses import replace
from decimal import Decimal

import pytest

from ilc_core.identity.agent_id_runtime import derive_agent_id_v2
from ilc_core.validator.validator_admission_ejection_production_path import (
    CANONICAL_VALIDATOR_SET_TRANSITION_EVENT_SCHEMA_VERSION,
    CDL_017_DEPENDENCY,
    SETTLEMENT_ROOT_SCHEMA_VERSION,
    VALIDATOR_ADMISSION_EJECTION_PRODUCTION_PATH_VERSION,
    VALIDATOR_ADMISSION_NOT_ACTIVATED,
    VALIDATOR_ADMISSION_NOT_ACTIVATED_TOKEN,
    ValidatorSetTransitionResult,
    ValidatorTransitionSettlementRoot,
    build_canonical_validator_set_transition_event_payloads,
    build_validator_set_transition_result,
    compute_validator_transition_settlement_root,
    emit_canonical_validator_set_transition_events,
    require_validator_admission_production_activation,
)


def _agent_id(seed_byte: int = 17) -> str:
    return derive_agent_id_v2(bytes([seed_byte]) * 32)


def _admit_inputs(validator_id: int = 5) -> dict[str, object]:
    return {
        "current_epoch": 10,
        "active_from_epoch": 11,
        "current_validator_ids": [1, 2, 3, 4],
        "validator_id": validator_id,
        "agent_id": _agent_id(validator_id),
        "stake_ecu": Decimal("400"),
    }


def _eject_inputs(validator_id: int = 2) -> dict[str, object]:
    return {
        "current_epoch": 10,
        "active_from_epoch": 11,
        "current_validator_ids": [1, 2, 3, 4],
        "validator_id": validator_id,
        "exit_reason": "voluntary_exit",
    }


def _result() -> ValidatorSetTransitionResult:
    return build_validator_set_transition_result(_admit_inputs(), _eject_inputs())


def test_phase_1539p_guard_and_activation_boundary() -> None:
    assert VALIDATOR_ADMISSION_NOT_ACTIVATED is True
    assert VALIDATOR_ADMISSION_NOT_ACTIVATED_TOKEN == (
        "production_validator_admission_not_activated_phase_1539p"
    )

    with pytest.raises(
        NotImplementedError,
        match="production_validator_admission_not_activated_phase_1539p",
    ):
        require_validator_admission_production_activation()


def test_phase_1539p_builds_guarded_transition_result() -> None:
    result = _result()

    assert result.runtime_version == VALIDATOR_ADMISSION_EJECTION_PRODUCTION_PATH_VERSION
    assert result.cdl_017_dependency == CDL_017_DEPENDENCY
    assert result.production_validator_admission_activated is False
    assert result.guard_token == VALIDATOR_ADMISSION_NOT_ACTIVATED_TOKEN
    assert result.admission_decision.validator_id == 5
    assert result.ejection_decision.validator_id == 2
    assert result.transition_context == "validator_set_transition:admit_5_epoch_11:eject_2_epoch_11"


def test_phase_1539p_same_result_replays_same_root() -> None:
    first = compute_validator_transition_settlement_root(_result())
    second = compute_validator_transition_settlement_root(_result())

    assert isinstance(first, ValidatorTransitionSettlementRoot)
    assert first.root_hex == second.root_hex
    assert first.canonical_record_json == second.canonical_record_json
    assert first.root_algorithm == "sha256_over_canonical_json"


def test_phase_1539p_digest_matches_canonical_record_json() -> None:
    root = compute_validator_transition_settlement_root(_result())

    digest = hashlib.sha256(root.canonical_record_json.encode("utf-8")).hexdigest()
    assert digest == root.root_hex
    assert len(root.root_hex) == 64


def test_phase_1539p_root_changes_when_transition_changes() -> None:
    first = compute_validator_transition_settlement_root(_result())
    changed = build_validator_set_transition_result(_admit_inputs(validator_id=6), _eject_inputs())
    second = compute_validator_transition_settlement_root(changed)

    assert first.root_hex != second.root_hex


def test_phase_1539p_root_payload_excludes_settlement_root_hex() -> None:
    root = compute_validator_transition_settlement_root(_result())
    payload = json.loads(root.canonical_record_json)

    assert payload["schema_version"] == SETTLEMENT_ROOT_SCHEMA_VERSION
    assert "settlement_root_hex" not in payload
    assert "settlement_root_hex" not in root.canonical_record_json


def test_phase_1539p_validator_id_sets_are_canonicalized_before_root() -> None:
    result = build_validator_set_transition_result(
        _admit_inputs() | {"current_validator_ids": [4, 2, 1, 3]},
        _eject_inputs() | {"current_validator_ids": [4, 2, 1, 3]},
    )
    root = compute_validator_transition_settlement_root(result)
    payload = json.loads(root.canonical_record_json)

    assert result.admission_decision.current_validator_ids == (1, 2, 3, 4)
    assert result.admission_decision.next_validator_ids == (1, 2, 3, 4, 5)
    assert result.ejection_decision.current_validator_ids == (1, 2, 3, 4)
    assert result.ejection_decision.next_validator_ids == (1, 3, 4)
    assert payload["event_payloads"][0]["current_validator_ids"] == [1, 2, 3, 4]
    assert payload["event_payloads"][0]["next_validator_ids"] == [1, 2, 3, 4, 5]
    assert payload["event_payloads"][1]["current_validator_ids"] == [1, 2, 3, 4]
    assert payload["event_payloads"][1]["next_validator_ids"] == [1, 3, 4]


def test_phase_1539p_emits_canonical_events_with_root_injected() -> None:
    result = _result()
    root = compute_validator_transition_settlement_root(result)
    events = emit_canonical_validator_set_transition_events(result, root)

    assert [event.event_type for event in events] == [
        "validator_admission",
        "validator_ejection",
    ]
    assert {event.settlement_root_hex for event in events} == {root.root_hex}
    assert all(event.production_validator_admission_activated is False for event in events)
    assert all(
        event.schema_version == CANONICAL_VALIDATOR_SET_TRANSITION_EVENT_SCHEMA_VERSION
        for event in events
    )


def test_phase_1539p_root_commits_to_event_payload_batch() -> None:
    result = _result()
    root = compute_validator_transition_settlement_root(result)
    events = emit_canonical_validator_set_transition_events(result, root)
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
    assert event_payloads_without_root == build_canonical_validator_set_transition_event_payloads(
        result
    )


def test_phase_1539p_rejects_stale_settlement_root_for_result() -> None:
    result = _result()
    stale_result = build_validator_set_transition_result(
        _admit_inputs(validator_id=6),
        _eject_inputs(),
    )
    stale_root = compute_validator_transition_settlement_root(stale_result)

    with pytest.raises(ValueError, match="settlement_root_event_payload_mismatch"):
        emit_canonical_validator_set_transition_events(result, stale_root)


def test_phase_1539p_rejects_float_before_root() -> None:
    result = _result()
    bad_admission = replace(result.admission_decision, stake_ecu=1.0)
    bad_result = replace(result, admission_decision=bad_admission)

    with pytest.raises(ValueError, match="float_in_validator_transition_record_rejected"):
        compute_validator_transition_settlement_root(bad_result)
