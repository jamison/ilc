from __future__ import annotations

import argparse

from ilc_core.cli import main as cli_main
from ilc_core.network.connectivity_mode import (
    CONNECTIVITY_MODE_VALIDATOR_ROLE_MAPPING,
    ConnectivityMode,
    ProbeResult,
    connectivity_mode_from_probe_result,
)
from ilc_core.network.d2d import gossip_peer_registry, peer_discovery_manager


AGENT_ID_HEX = "a" * 96


def test_identity_init_validator_participation_is_on_by_default() -> None:
    state: dict[str, object] = {}
    args = argparse.Namespace(
        no_validator=False,
        validator_endpoint="",
        validator_id=1,
        validator_key="",
        validator_network_id="public-rc",
    )

    cli_main._apply_validator_candidate_enrollment_state(args, state, AGENT_ID_HEX)

    assert state["validator_participation_enabled"] is True
    assert (
        state["validator_role_record_status"]
        == "candidate_pending_validator_key_material"
    )


def test_identity_init_no_validator_is_the_only_default_opt_out() -> None:
    state: dict[str, object] = {}
    args = argparse.Namespace(
        no_validator=True,
        validator_endpoint="validator.example:50151",
        validator_id=1,
        validator_key="a" * 96,
        validator_network_id="public-rc",
    )

    cli_main._apply_validator_candidate_enrollment_state(args, state, AGENT_ID_HEX)

    assert state["validator_participation_enabled"] is False
    assert state["validator_role_record_status"] == "opted_out"


def test_validator_observer_relay_mode_is_not_degraded_to_outbound_only() -> None:
    mode = connectivity_mode_from_probe_result(
        ProbeResult(
            has_public_ip=False,
            observed_ip=None,
            observed_port=None,
            relay_available=True,
            validator_participation_enabled=True,
            has_outbound_connectivity=True,
        )
    )

    assert mode is ConnectivityMode.VALIDATOR_OBSERVER_RELAY
    assert mode is not ConnectivityMode.OUTBOUND_ONLY


def test_admitted_validator_relay_mode_is_distinct_from_observer_relay() -> None:
    mode = connectivity_mode_from_probe_result(
        ProbeResult(
            has_public_ip=False,
            observed_ip=None,
            observed_port=None,
            relay_available=True,
            validator_participation_enabled=True,
            has_outbound_connectivity=True,
            validator_admitted=True,
        )
    )

    assert mode is ConnectivityMode.VALIDATOR_RELAY


def test_validator_direct_modes_require_verified_public_evidence() -> None:
    observer_mode = connectivity_mode_from_probe_result(
        ProbeResult(
            has_public_ip=True,
            observed_ip="203.0.113.7",
            observed_port=50151,
            relay_available=False,
            validator_participation_enabled=True,
            has_outbound_connectivity=True,
        )
    )
    admitted_mode = connectivity_mode_from_probe_result(
        ProbeResult(
            has_public_ip=True,
            observed_ip="203.0.113.7",
            observed_port=50151,
            relay_available=False,
            validator_participation_enabled=True,
            has_outbound_connectivity=True,
            validator_admitted=True,
        )
    )

    assert observer_mode is ConnectivityMode.VALIDATOR_OBSERVER_DIRECT
    assert admitted_mode is ConnectivityMode.VALIDATOR_DIRECT


def test_nat_traversed_direct_remains_candidate_not_validator_direct() -> None:
    mode = connectivity_mode_from_probe_result(
        ProbeResult(
            has_public_ip=False,
            observed_ip="192.0.2.44",
            observed_port=50151,
            relay_available=False,
            validator_participation_enabled=True,
            has_outbound_connectivity=True,
            direct_mapping_candidate=True,
        )
    )

    assert mode is ConnectivityMode.NAT_TRAVERSED_DIRECT
    assert mode is not ConnectivityMode.VALIDATOR_DIRECT
    assert (
        CONNECTIVITY_MODE_VALIDATOR_ROLE_MAPPING[mode]
        == "candidate_direct_endpoint_external_verification_pending"
    )


def test_dynamic_peer_discovery_is_testnet_active_in_both_surfaces() -> None:
    assert peer_discovery_manager.DYNAMIC_PEER_DISCOVERY_NOT_ACTIVATED is False
    assert gossip_peer_registry.DYNAMIC_PEER_DISCOVERY_NOT_ACTIVATED is False
