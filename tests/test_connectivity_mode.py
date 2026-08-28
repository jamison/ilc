from __future__ import annotations

import json

import pytest

from ilc_core.network.connectivity_mode import (
    CONNECTIVITY_MODE_RUNTIME_TOKEN,
    CONNECTIVITY_PROBE_RUNTIME_NOT_ACTIVATED,
    ConnectivityMode,
    ConnectivityModeValidationError,
    ConnectivityReceipt,
    ProbeResult,
    connectivity_mode_from_probe_result,
)


AGENT_ID = "a" * 96


def _mode(**kwargs: object) -> ConnectivityMode:
    defaults = {
        "has_public_ip": False,
        "observed_ip": None,
        "observed_port": None,
        "relay_available": False,
        "validator_participation_enabled": False,
        "has_outbound_connectivity": False,
        "direct_mapping_candidate": False,
        "validator_admitted": False,
    }
    defaults.update(kwargs)
    return connectivity_mode_from_probe_result(ProbeResult(**defaults))


def test_enum_has_exactly_nine_taxonomy_values() -> None:
    assert [mode.value for mode in ConnectivityMode] == [
        "local_only",
        "outbound_only",
        "nat_traversed_direct",
        "relay_reachable",
        "direct_public",
        "validator_observer_relay",
        "validator_observer_direct",
        "validator_direct",
        "validator_relay",
    ]


def test_local_only_transition() -> None:
    assert _mode() is ConnectivityMode.LOCAL_ONLY


def test_outbound_only_transition() -> None:
    assert _mode(has_outbound_connectivity=True) is ConnectivityMode.OUTBOUND_ONLY


def test_nat_traversed_direct_candidate_transition() -> None:
    assert (
        _mode(
            has_outbound_connectivity=True,
            direct_mapping_candidate=True,
            observed_ip="203.0.113.10",
            observed_port=50151,
        )
        is ConnectivityMode.NAT_TRAVERSED_DIRECT
    )


def test_relay_reachable_transition() -> None:
    assert (
        _mode(has_outbound_connectivity=True, relay_available=True)
        is ConnectivityMode.RELAY_REACHABLE
    )


def test_direct_public_transition() -> None:
    assert (
        _mode(
            has_outbound_connectivity=True,
            has_public_ip=True,
            observed_ip="203.0.113.10",
            observed_port=50151,
        )
        is ConnectivityMode.DIRECT_PUBLIC
    )


def test_validator_observer_relay_transition() -> None:
    assert (
        _mode(
            has_outbound_connectivity=True,
            relay_available=True,
            validator_participation_enabled=True,
        )
        is ConnectivityMode.VALIDATOR_OBSERVER_RELAY
    )


def test_validator_observer_direct_transition() -> None:
    assert (
        _mode(
            has_outbound_connectivity=True,
            has_public_ip=True,
            observed_ip="203.0.113.10",
            observed_port=50151,
            validator_participation_enabled=True,
        )
        is ConnectivityMode.VALIDATOR_OBSERVER_DIRECT
    )


def test_validator_direct_transition() -> None:
    assert (
        _mode(
            has_outbound_connectivity=True,
            has_public_ip=True,
            observed_ip="203.0.113.10",
            observed_port=50151,
            validator_participation_enabled=True,
            validator_admitted=True,
        )
        is ConnectivityMode.VALIDATOR_DIRECT
    )


def test_validator_relay_transition() -> None:
    assert (
        _mode(
            has_outbound_connectivity=True,
            relay_available=True,
            validator_participation_enabled=True,
            validator_admitted=True,
        )
        is ConnectivityMode.VALIDATOR_RELAY
    )


def test_direct_verified_beats_relay_for_non_validator() -> None:
    assert (
        _mode(
            has_outbound_connectivity=True,
            has_public_ip=True,
            observed_ip="203.0.113.10",
            observed_port=50151,
            relay_available=True,
        )
        is ConnectivityMode.DIRECT_PUBLIC
    )


def test_probe_result_rejects_ambiguous_direct_state() -> None:
    with pytest.raises(
        ConnectivityModeValidationError,
        match="verified_direct_and_candidate_direct_are_exclusive",
    ):
        ProbeResult(
            has_public_ip=True,
            direct_mapping_candidate=True,
            observed_ip="203.0.113.10",
            observed_port=50151,
            relay_available=False,
            validator_participation_enabled=False,
        )


def test_probe_result_rejects_validator_admitted_without_participation() -> None:
    with pytest.raises(
        ConnectivityModeValidationError,
        match="validator_admitted_requires_participation_enabled",
    ):
        ProbeResult(
            has_public_ip=False,
            observed_ip=None,
            observed_port=None,
            relay_available=True,
            validator_participation_enabled=False,
            validator_admitted=True,
        )


def test_probe_result_rejects_non_bool_flags() -> None:
    with pytest.raises(
        ConnectivityModeValidationError, match="has_public_ip_must_be_bool"
    ):
        ProbeResult(
            has_public_ip=1,  # type: ignore[arg-type]
            observed_ip=None,
            observed_port=None,
            relay_available=False,
            validator_participation_enabled=False,
        )


def test_receipt_accepts_string_mode_and_serializes_canonically() -> None:
    receipt = ConnectivityReceipt(
        mode="relay_reachable",
        observed_endpoint=None,
        relay_endpoint="relay.example:50151",
        probe_observer_agent_id=AGENT_ID,
        probe_epoch=0,
    )
    assert receipt.mode is ConnectivityMode.RELAY_REACHABLE
    decoded = json.loads(receipt.to_canonical_json())
    assert decoded == {
        "mode": "relay_reachable",
        "observed_endpoint": None,
        "probe_epoch": 0,
        "probe_observer_agent_id": AGENT_ID,
        "relay_endpoint": "relay.example:50151",
        "schema_version": "gap_connectivity_mode_runtime_00.v0.1",
    }
    assert receipt.to_canonical_json().startswith(b'{"mode":')


def test_receipt_rejects_direct_mode_without_endpoint() -> None:
    with pytest.raises(
        ConnectivityModeValidationError, match="direct_mode_requires_observed_endpoint"
    ):
        ConnectivityReceipt(
            mode=ConnectivityMode.DIRECT_PUBLIC,
            observed_endpoint=None,
            relay_endpoint=None,
            probe_observer_agent_id=None,
            probe_epoch=0,
        )


def test_receipt_rejects_relay_mode_without_endpoint() -> None:
    with pytest.raises(
        ConnectivityModeValidationError, match="relay_mode_requires_endpoint"
    ):
        ConnectivityReceipt(
            mode=ConnectivityMode.RELAY_REACHABLE,
            observed_endpoint=None,
            relay_endpoint=None,
            probe_observer_agent_id=None,
            probe_epoch=0,
        )


def test_receipt_rejects_bad_agent_id_and_bad_epoch() -> None:
    with pytest.raises(
        ConnectivityModeValidationError,
        match="probe_observer_agent_id_must_be_agent_id_hex",
    ):
        ConnectivityReceipt(
            mode=ConnectivityMode.LOCAL_ONLY,
            observed_endpoint=None,
            relay_endpoint=None,
            probe_observer_agent_id="not-agent-id",
            probe_epoch=0,
        )

    with pytest.raises(ConnectivityModeValidationError, match="probe_epoch_must_be_uint64"):
        ConnectivityReceipt(
            mode=ConnectivityMode.LOCAL_ONLY,
            observed_endpoint=None,
            relay_endpoint=None,
            probe_observer_agent_id=None,
            probe_epoch=-1,
        )


def test_guard_and_output_token_are_present() -> None:
    assert CONNECTIVITY_PROBE_RUNTIME_NOT_ACTIVATED is False
    assert (
        CONNECTIVITY_MODE_RUNTIME_TOKEN
        == "connectivity_mode_runtime_committed_GAP_CONNECTIVITY_MODE_RUNTIME_00"
    )
