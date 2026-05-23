"""Regression tests for Phase 1437 OpenClaw harness-assisted P2P activation."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from ilc_core.network.d2d import openclaw_p2p_relay
from ilc_core.network.d2d.openclaw_p2p_relay import (
    CDL_078_RELAY_DEPENDENCY,
    CDL_078_RELAY_WIRED_OPENCLAW_HARNESS_TOKEN,
    ECU_DISTRIBUTION_ACTIVATED,
    ECU_DISTRIBUTION_NOT_ACTIVATED_TOKEN,
    EPOCH_TRANSITION_NOT_TRIGGERED_TOKEN,
    EPOCH_TRANSITION_TRIGGERED,
    NATIVE_RUST_P2P_DEFERRED_WINDOW_1459_PLUS_TOKEN,
    NATIVE_RUST_P2P_NOT_ACTIVATED,
    NATIVE_RUST_P2P_NOT_ACTIVATED_TOKEN,
    OPENCLAW_GATEWAY_NOT_PUBLICLY_ACTIVATED,
    OPENCLAW_GATEWAY_NOT_PUBLICLY_ACTIVATED_TOKEN,
    OPENCLAW_HARNESS_ASSISTED_P2P_ACTIVE_TOKEN,
    OPENCLAW_HARNESS_P2P_ACTIVATED_TOKEN,
    OPENCLAW_P2P_ACTIVATED_TOKEN,
    OPENCLAW_P2P_RELAY_VERSION,
    PUBLIC_RC_ACTIVATED,
    PUBLIC_RC_NOT_ACTIVATED_TOKEN,
    REHEARSAL_OPENCLAW_PATH_VALIDATED_GATE_TOKEN,
    TRANSPORT_HARNESS_INTERFACE_WIRED_TOKEN,
    fetch_payload_via_harness,
    openclaw_p2p_relay_manifest,
    openclaw_p2p_relay_tokens,
    relay_payload_via_harness,
)
from ilc_core.protocol.harness_interfaces import TransportHarness
from ilc_core.sidecars import public_path_activation


class MockTransportHarness:
    def __init__(self) -> None:
        self.published: list[dict[str, Any]] = []
        self.payloads = {"openclaw://payload/1": b"payload"}

    def publish_payload(
        self,
        *,
        channel: str,
        payload: bytes,
        epoch: int,
        metadata: dict[str, str] | None = None,
    ) -> str:
        self.published.append(
            {
                "channel": channel,
                "epoch": epoch,
                "metadata": dict(metadata or {}),
                "payload": payload,
            }
        )
        return "openclaw://payload/1"

    def fetch_payload(
        self,
        *,
        address: str,
        max_bytes: int,
        epoch: int,
    ) -> bytes:
        payload = self.payloads[address]
        return payload[:max_bytes]


class OversizedFetchHarness(MockTransportHarness):
    def fetch_payload(
        self,
        *,
        address: str,
        max_bytes: int,
        epoch: int,
    ) -> bytes:
        return b"x" * (max_bytes + 1)


def test_openclaw_p2p_relay_version_token() -> None:
    assert OPENCLAW_P2P_RELAY_VERSION == "openclaw_p2p_relay_phase_1437.v0.1"
    assert "1437" in OPENCLAW_P2P_RELAY_VERSION


def test_openclaw_p2p_activated_token() -> None:
    assert OPENCLAW_P2P_ACTIVATED_TOKEN == "openclaw_p2p_activated_phase_1437"


def test_openclaw_harness_p2p_activated_token() -> None:
    assert (
        OPENCLAW_HARNESS_P2P_ACTIVATED_TOKEN
        == "openclaw_harness_p2p_activated_phase_1437"
    )


def test_openclaw_harness_assisted_legacy_token() -> None:
    assert (
        OPENCLAW_HARNESS_ASSISTED_P2P_ACTIVE_TOKEN
        == "openclaw_harness_assisted_p2p_active_phase_1437"
    )


def test_native_rust_p2p_not_activated_token() -> None:
    assert NATIVE_RUST_P2P_NOT_ACTIVATED_TOKEN == "native_rust_p2p_not_activated_phase_1437"


def test_native_rust_p2p_deferred_token() -> None:
    assert (
        NATIVE_RUST_P2P_DEFERRED_WINDOW_1459_PLUS_TOKEN
        == "native_rust_p2p_deferred_window_1459_plus_phase_1437"
    )


def test_openclaw_gateway_not_publicly_activated_token() -> None:
    assert (
        OPENCLAW_GATEWAY_NOT_PUBLICLY_ACTIVATED_TOKEN
        == "openclaw_gateway_not_publicly_activated_phase_1437"
    )


def test_native_rust_p2p_not_activated_flag() -> None:
    assert NATIVE_RUST_P2P_NOT_ACTIVATED is True


def test_openclaw_gateway_not_publicly_activated_flag() -> None:
    assert OPENCLAW_GATEWAY_NOT_PUBLICLY_ACTIVATED is True


def test_no_value_or_epoch_surfaces_activated_by_relay() -> None:
    assert ECU_DISTRIBUTION_ACTIVATED is False
    assert EPOCH_TRANSITION_TRIGGERED is False
    assert PUBLIC_RC_ACTIVATED is False


def test_cdl_078_dependency_chain() -> None:
    assert CDL_078_RELAY_DEPENDENCY == "cdl_078_relay_incentive_constitutional_lock.v0.1"


def test_relay_tokens_tuple_contains_phase_contract() -> None:
    tokens = set(openclaw_p2p_relay_tokens())
    expected = {
        OPENCLAW_P2P_RELAY_VERSION,
        CDL_078_RELAY_DEPENDENCY,
        OPENCLAW_P2P_ACTIVATED_TOKEN,
        OPENCLAW_HARNESS_P2P_ACTIVATED_TOKEN,
        OPENCLAW_HARNESS_ASSISTED_P2P_ACTIVE_TOKEN,
        NATIVE_RUST_P2P_NOT_ACTIVATED_TOKEN,
        NATIVE_RUST_P2P_DEFERRED_WINDOW_1459_PLUS_TOKEN,
        OPENCLAW_GATEWAY_NOT_PUBLICLY_ACTIVATED_TOKEN,
        CDL_078_RELAY_WIRED_OPENCLAW_HARNESS_TOKEN,
        TRANSPORT_HARNESS_INTERFACE_WIRED_TOKEN,
        REHEARSAL_OPENCLAW_PATH_VALIDATED_GATE_TOKEN,
        ECU_DISTRIBUTION_NOT_ACTIVATED_TOKEN,
        EPOCH_TRANSITION_NOT_TRIGGERED_TOKEN,
        PUBLIC_RC_NOT_ACTIVATED_TOKEN,
    }
    assert expected <= tokens


def test_transport_harness_protocol_satisfied() -> None:
    assert isinstance(MockTransportHarness(), TransportHarness)


def test_relay_payload_validates_payload_size() -> None:
    with pytest.raises(ValueError, match="openclaw_p2p_relay_payload_too_large"):
        relay_payload_via_harness(
            harness=MockTransportHarness(),
            channel="claims",
            payload=b"x" * 65_537,
            epoch=1,
            peer_id="peer-1",
        )


def test_relay_payload_validates_channel() -> None:
    with pytest.raises(ValueError, match="openclaw_p2p_relay_invalid_channel"):
        relay_payload_via_harness(
            harness=MockTransportHarness(),
            channel="",
            payload=b"ok",
            epoch=1,
            peer_id="peer-1",
        )
    with pytest.raises(ValueError, match="openclaw_p2p_relay_invalid_channel"):
        relay_payload_via_harness(
            harness=MockTransportHarness(),
            channel="c" * 257,
            payload=b"ok",
            epoch=1,
            peer_id="peer-1",
        )


def test_relay_payload_validates_peer_id() -> None:
    with pytest.raises(ValueError, match="openclaw_p2p_relay_invalid_peer_id"):
        relay_payload_via_harness(
            harness=MockTransportHarness(),
            channel="claims",
            payload=b"ok",
            epoch=1,
            peer_id="",
        )
    with pytest.raises(ValueError, match="openclaw_p2p_relay_invalid_peer_id"):
        relay_payload_via_harness(
            harness=MockTransportHarness(),
            channel="claims",
            payload=b"ok",
            epoch=1,
            peer_id="p" * 1025,
        )


def test_relay_payload_validates_epoch() -> None:
    with pytest.raises(ValueError, match="openclaw_p2p_relay_invalid_epoch"):
        relay_payload_via_harness(
            harness=MockTransportHarness(),
            channel="claims",
            payload=b"ok",
            epoch=-1,
            peer_id="peer-1",
        )


def test_fetch_payload_validates_address() -> None:
    with pytest.raises(ValueError, match="openclaw_p2p_relay_invalid_address"):
        fetch_payload_via_harness(
            harness=MockTransportHarness(),
            address="",
            epoch=1,
        )
    with pytest.raises(ValueError, match="openclaw_p2p_relay_invalid_address"):
        fetch_payload_via_harness(
            harness=MockTransportHarness(),
            address="a" * 1025,
            epoch=1,
        )


def test_fetch_payload_rejects_oversized_harness_return() -> None:
    with pytest.raises(ValueError, match="openclaw_p2p_relay_payload_too_large"):
        fetch_payload_via_harness(
            harness=OversizedFetchHarness(),
            address="openclaw://payload/1",
            epoch=1,
        )


def test_relay_payload_records_serve_event(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[tuple[str, int, dict[str, Any]]] = []

    def fake_record_serve_event(node_id: str, epoch: int, state: dict[str, Any]) -> None:
        calls.append((node_id, epoch, state))

    monkeypatch.setattr(openclaw_p2p_relay, "record_serve_event", fake_record_serve_event)
    state: dict[str, Any] = {}
    harness = MockTransportHarness()

    address = relay_payload_via_harness(
        harness=harness,
        channel="claims",
        payload=b"ok",
        epoch=7,
        peer_id="peer-1",
        metadata={"artifact": "claim"},
        reputation_state=state,
    )

    assert address == "openclaw://payload/1"
    assert calls == [("peer-1", 7, state)]
    assert harness.published[0]["metadata"]["relay_dependency"] == CDL_078_RELAY_DEPENDENCY
    assert harness.published[0]["metadata"]["artifact"] == "claim"


def test_fetch_payload_returns_bounded_bytes() -> None:
    assert (
        fetch_payload_via_harness(
            harness=MockTransportHarness(),
            address="openclaw://payload/1",
            epoch=7,
        )
        == b"payload"
    )


def test_relay_manifest_records_non_claims() -> None:
    manifest = openclaw_p2p_relay_manifest()

    assert manifest["openclaw_harness_p2p_activated"] is True
    assert manifest["native_rust_p2p_activated"] is False
    assert manifest["openclaw_gateway_publicly_activated"] is False
    assert manifest["ecu_distribution_activated"] is False
    assert manifest["epoch_transition_triggered"] is False
    assert manifest["public_rc_activated"] is False


def test_public_path_activation_openclaw_p2p_now_true() -> None:
    assert public_path_activation.OPENCLAW_P2P_ACTIVATED is True


def test_public_path_activation_native_rust_still_false() -> None:
    assert public_path_activation.PUBLIC_P2P_ACTIVATED is False


def test_public_path_manifest_openclaw_p2p_activated() -> None:
    assert public_path_activation.public_path_activation_manifest()[
        "openclaw_p2p_activated"
    ] is True


def test_public_path_manifest_public_p2p_still_false() -> None:
    assert public_path_activation.public_path_activation_manifest()["public_p2p_activated"] is False


def test_openclaw_harness_p2p_token_in_required_tokens() -> None:
    tokens = set(public_path_activation.public_path_activation_required_tokens())
    assert OPENCLAW_HARNESS_P2P_ACTIVATED_TOKEN in tokens
    assert OPENCLAW_P2P_ACTIVATED_TOKEN in tokens
    assert NATIVE_RUST_P2P_NOT_ACTIVATED_TOKEN in tokens
    assert PUBLIC_RC_NOT_ACTIVATED_TOKEN in tokens


def test_sequence_lock_has_phase_1437_addendum() -> None:
    text = Path("docs/specs/ilc_phase_1429_1458_sequence_lock_v0.1.md").read_text()
    assert "openclaw_harness_p2p_activated_phase_1437" in text
    assert "phase_1437_p2p_sequence_lock_addendum_recorded" in text
