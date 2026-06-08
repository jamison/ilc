"""Phase 1541p OBL-022 ejected-stake distribution production-path tests."""

from __future__ import annotations

import hashlib
import json
from dataclasses import replace
from decimal import Decimal

import pytest

from ilc_core.epoch.ejected_stake_distribution_production_path import (
    CANONICAL_EJECTED_STAKE_DISTRIBUTION_EVENT_SCHEMA_VERSION,
    CDL_083_DEPENDENCY,
    EJECTED_STAKE_DISTRIBUTION_PRODUCTION_NOT_ACTIVATED,
    EJECTED_STAKE_DISTRIBUTION_PRODUCTION_NOT_ACTIVATED_TOKEN,
    EJECTED_STAKE_DISTRIBUTION_PRODUCTION_PATH_VERSION,
    SETTLEMENT_ROOT_SCHEMA_VERSION,
    EjectedStakeDistributionProductionResult,
    EjectedStakeSettlementRoot,
    build_canonical_ejected_stake_event_payloads,
    build_ejected_stake_distribution_result,
    compute_ejected_stake_settlement_root,
    emit_canonical_ejected_stake_distribution_events,
    require_ejected_stake_distribution_production_activation,
)


def _inputs(
    *,
    ejected_stake_ilc: Decimal = Decimal("9.000000001"),
    approve_votes: int = 2,
    participating_voters: int = 2,
) -> dict[str, object]:
    return {
        "distribution_epoch": 7,
        "ejected_stake_ilc": ejected_stake_ilc,
        "remaining_member_stakes": {
            "agent_alpha": Decimal("10"),
            "agent_beta": Decimal("20"),
            "agent_gamma": Decimal("30"),
        },
        "approve_votes": approve_votes,
        "participating_voters": participating_voters,
    }


def _result() -> EjectedStakeDistributionProductionResult:
    return build_ejected_stake_distribution_result(_inputs())


def test_phase_1541p_guard_and_activation_boundary() -> None:
    assert EJECTED_STAKE_DISTRIBUTION_PRODUCTION_NOT_ACTIVATED is True
    assert EJECTED_STAKE_DISTRIBUTION_PRODUCTION_NOT_ACTIVATED_TOKEN == (
        "production_ejected_stake_distribution_not_activated_phase_1541p"
    )

    with pytest.raises(
        NotImplementedError,
        match="production_ejected_stake_distribution_not_activated_phase_1541p",
    ):
        require_ejected_stake_distribution_production_activation()


def test_phase_1541p_builds_guarded_result_with_cdl083_dependency() -> None:
    result = _result()

    assert result.runtime_version == EJECTED_STAKE_DISTRIBUTION_PRODUCTION_PATH_VERSION
    assert result.cdl_083_dependency == CDL_083_DEPENDENCY
    assert result.hcon02_quorum_validated is True
    assert result.production_ejected_stake_distribution_activated is False
    assert result.distribution_quote.cdl_083_dependency == CDL_083_DEPENDENCY
    assert result.distribution_quote.decision_token == (
        "ejected_stake_distribution_not_activated_phase_1350"
    )


def test_phase_1541p_hcon02_quorum_is_enforced_by_underlying_quote() -> None:
    with pytest.raises(ValueError, match="h_con_02_quorum_guard_minimum_voters_not_met"):
        build_ejected_stake_distribution_result(
            _inputs(approve_votes=1, participating_voters=1)
        )


def test_phase_1541p_same_result_replays_same_root() -> None:
    first = compute_ejected_stake_settlement_root(_result())
    second = compute_ejected_stake_settlement_root(_result())

    assert isinstance(first, EjectedStakeSettlementRoot)
    assert first.root_hex == second.root_hex
    assert first.canonical_record_json == second.canonical_record_json


def test_phase_1541p_digest_matches_canonical_record_json() -> None:
    root = compute_ejected_stake_settlement_root(_result())

    digest = hashlib.sha256(root.canonical_record_json.encode("utf-8")).hexdigest()
    assert digest == root.root_hex
    assert len(root.root_hex) == 64


def test_phase_1541p_root_changes_when_ejected_stake_changes() -> None:
    first = compute_ejected_stake_settlement_root(_result())
    changed = build_ejected_stake_distribution_result(
        _inputs(ejected_stake_ilc=Decimal("6"))
    )
    second = compute_ejected_stake_settlement_root(changed)

    assert first.root_hex != second.root_hex


def test_phase_1541p_root_payload_excludes_settlement_root_hex() -> None:
    root = compute_ejected_stake_settlement_root(_result())
    payload = json.loads(root.canonical_record_json)

    assert payload["schema_version"] == SETTLEMENT_ROOT_SCHEMA_VERSION
    assert "settlement_root_hex" not in payload
    assert "settlement_root_hex" not in root.canonical_record_json


def test_phase_1541p_emits_canonical_events_with_decimal_amounts() -> None:
    result = _result()
    root = compute_ejected_stake_settlement_root(result)
    events = emit_canonical_ejected_stake_distribution_events(result, root)

    assert [event.recipient_agent_id for event in events] == [
        "agent_alpha",
        "agent_beta",
        "agent_gamma",
    ]
    assert {event.settlement_root_hex for event in events} == {root.root_hex}
    assert all(event.hcon02_quorum_validated is True for event in events)
    assert all(
        event.production_ejected_stake_distribution_activated is False
        for event in events
    )
    assert all(
        event.schema_version == CANONICAL_EJECTED_STAKE_DISTRIBUTION_EVENT_SCHEMA_VERSION
        for event in events
    )
    assert sum((Decimal(event.amount_ilc_str) for event in events), Decimal("0")) == (
        result.distribution_quote.ejected_stake_ilc
    )


def test_phase_1541p_root_commits_to_event_payload_batch() -> None:
    result = _result()
    root = compute_ejected_stake_settlement_root(result)
    events = emit_canonical_ejected_stake_distribution_events(result, root)
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
    assert event_payloads_without_root == build_canonical_ejected_stake_event_payloads(
        result
    )


def test_phase_1541p_rejects_stale_settlement_root_for_result() -> None:
    result = _result()
    stale_result = build_ejected_stake_distribution_result(
        _inputs(ejected_stake_ilc=Decimal("6"))
    )
    stale_root = compute_ejected_stake_settlement_root(stale_result)

    with pytest.raises(ValueError, match="settlement_root_event_payload_mismatch"):
        emit_canonical_ejected_stake_distribution_events(result, stale_root)


def test_phase_1541p_rejects_float_before_root() -> None:
    result = _result()
    bad_quote = replace(result.distribution_quote, ejected_stake_ilc=1.0)
    bad_result = replace(result, distribution_quote=bad_quote)

    with pytest.raises(ValueError, match="float_in_ejected_stake_distribution_record"):
        compute_ejected_stake_settlement_root(bad_result)
