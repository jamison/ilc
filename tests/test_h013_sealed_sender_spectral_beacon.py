"""Tests for H-013 sealed-sender spectral beacon implementation."""

from __future__ import annotations

from pathlib import Path

import pytest

from ilc_core.network.d2d import spectral_beacon as spectral_beacon_module
from ilc_core.network.d2d.spectral_beacon import (
    ADR_0034_DEPENDENCY,
    H013_SEALED_SPECTRAL_BEACON_VERSION,
    INNER_ENVELOPE_SIZE,
    OUTER_ENVELOPE_SIZE,
    SealedSpectralBeaconEnvelope,
    SpectralBeacon,
    SpectralBeaconValidationError,
    build_h013_gossip_envelope,
    build_sealed_spectral_beacon,
    generate_sealed_sender_keypair,
    open_terminal_layer,
    peel_relay_layer,
)


SOURCE_PATH = Path("ilc_core/network/d2d/spectral_beacon.py")


def _keypairs():
    return generate_sealed_sender_keypair(), generate_sealed_sender_keypair()


def _beacon(agent_id: str = "agent-alpha") -> SpectralBeacon:
    return SpectralBeacon(
        epoch=823,
        lambda_local=[0.12, 0.34, 0.56],
        noise_sigma=0.08,
        agent_id=agent_id,
    )


def _sealed(beacon: SpectralBeacon | None = None):
    relay, terminal = _keypairs()
    sealed = build_sealed_spectral_beacon(
        beacon=beacon or _beacon(),
        relay_peer_id="peer:relay-01",
        relay_public_key=relay.public_key_bytes,
        terminal_peer_id="peer:terminal-01",
        terminal_public_key=terminal.public_key_bytes,
        channel_id="rand:abcdef0123456789abcdef0123456789",
    )
    return relay, terminal, sealed


def test_version_dependency_and_fixed_size_constants_are_locked() -> None:
    assert H013_SEALED_SPECTRAL_BEACON_VERSION == "h013_sealed_spectral_beacon.v0.1"
    assert ADR_0034_DEPENDENCY == "run_h013_d2d_sealed_sender_adr_verdict=accepted"
    assert INNER_ENVELOPE_SIZE == 2108
    assert OUTER_ENVELOPE_SIZE == 4156


def test_envelope_construction_relay_peel_and_terminal_delivery() -> None:
    relay, terminal, sealed = _sealed()

    assert sealed.relay_peer_id == "peer:relay-01"
    assert sealed.channel_id == "rand:abcdef0123456789abcdef0123456789"
    assert len(sealed.sealed_outer) == OUTER_ENVELOPE_SIZE

    relay_result = peel_relay_layer(sealed, relay.private_key)
    assert relay_result.next_hop_peer_id == "peer:terminal-01"
    assert relay_result.channel_id == sealed.channel_id
    assert len(relay_result.sealed_inner) == INNER_ENVELOPE_SIZE

    terminal_result = open_terminal_layer(relay_result, terminal.private_key)
    assert terminal_result.terminal_peer_id == "peer:terminal-01"
    assert terminal_result.beacon == _beacon()


def test_relay_peel_exposes_only_next_hop_and_inner_ciphertext() -> None:
    relay, _terminal, sealed = _sealed(_beacon(agent_id="agent-secret-source"))

    relay_result = peel_relay_layer(sealed, relay.private_key)

    assert relay_result.next_hop_peer_id == "peer:terminal-01"
    assert not hasattr(relay_result, "beacon")
    assert b"agent-secret-source" not in relay_result.sealed_inner
    assert b"agent-secret-source" not in sealed.sealed_outer


def test_fixed_size_padding_invariant_holds_for_different_payload_sizes() -> None:
    relay, terminal = _keypairs()
    small = build_sealed_spectral_beacon(
        beacon=SpectralBeacon(epoch=1, lambda_local=[0.1], noise_sigma=0.01, agent_id="a"),
        relay_peer_id="peer:relay-01",
        relay_public_key=relay.public_key_bytes,
        terminal_peer_id="peer:terminal-01",
        terminal_public_key=terminal.public_key_bytes,
        channel_id="cid:0123456789abcdef0123456789abcdef",
    )
    large = build_sealed_spectral_beacon(
        beacon=SpectralBeacon(
            epoch=1,
            lambda_local=[float(index) / 100.0 for index in range(32)],
            noise_sigma=0.01,
            agent_id="agent-with-a-longer-but-still-bounded-identifier",
        ),
        relay_peer_id="peer:relay-01",
        relay_public_key=relay.public_key_bytes,
        terminal_peer_id="peer:terminal-01",
        terminal_public_key=terminal.public_key_bytes,
        channel_id="cid:0123456789abcdef0123456789abcdef",
    )

    assert len(small.sealed_outer) == OUTER_ENVELOPE_SIZE
    assert len(large.sealed_outer) == OUTER_ENVELOPE_SIZE
    assert len(peel_relay_layer(small, relay.private_key).sealed_inner) == INNER_ENVELOPE_SIZE
    assert len(peel_relay_layer(large, relay.private_key).sealed_inner) == INNER_ENVELOPE_SIZE


def test_wrong_key_cannot_open_relay_or_terminal_layers() -> None:
    relay, terminal, sealed = _sealed()
    wrong = generate_sealed_sender_keypair()

    with pytest.raises(SpectralBeaconValidationError) as relay_exc:
        peel_relay_layer(sealed, wrong.private_key)
    assert relay_exc.value.token == "h013_decryption_failed"

    relay_result = peel_relay_layer(sealed, relay.private_key)
    with pytest.raises(SpectralBeaconValidationError) as terminal_exc:
        open_terminal_layer(relay_result, relay.private_key)
    assert terminal_exc.value.token == "h013_decryption_failed"

    opened = open_terminal_layer(relay_result, terminal.private_key)
    assert opened.beacon.agent_id == "agent-alpha"


def test_validation_rejects_non_finite_lambda_values() -> None:
    relay, terminal = _keypairs()
    with pytest.raises(SpectralBeaconValidationError) as exc:
        build_sealed_spectral_beacon(
            beacon=SpectralBeacon(
                epoch=1,
                lambda_local=[0.1, float("nan")],
                noise_sigma=0.01,
                agent_id="agent-alpha",
            ),
            relay_peer_id="peer:relay-01",
            relay_public_key=relay.public_key_bytes,
            terminal_peer_id="peer:terminal-01",
            terminal_public_key=terminal.public_key_bytes,
            channel_id="rand:abcdef0123456789abcdef0123456789",
        )
    assert exc.value.token == "h013_lambda_local_non_finite"


def test_malformed_fixed_json_uses_tokenized_validation_error() -> None:
    empty_json_payload = (0).to_bytes(4, "big") + b"\x00" * 12

    with pytest.raises(SpectralBeaconValidationError) as exc:
        spectral_beacon_module._unpack_fixed_json(empty_json_payload, "h013_inner_payload_invalid")

    assert exc.value.token == "h013_inner_payload_invalid"
    assert exc.value.message == "fixed_payload_json_invalid"


def test_malformed_decrypted_beacon_mapping_uses_tokenized_validation_error() -> None:
    with pytest.raises(SpectralBeaconValidationError) as missing_exc:
        spectral_beacon_module._beacon_from_mapping({"epoch": 1})
    assert missing_exc.value.token == "h013_beacon_payload_invalid"

    with pytest.raises(SpectralBeaconValidationError) as finite_exc:
        spectral_beacon_module._beacon_from_mapping(
            {
                "epoch": 1,
                "lambda_local": ["nan"],
                "noise_sigma": 0.01,
                "agent_id": "agent-alpha",
            }
        )
    assert finite_exc.value.token == "h013_lambda_local_non_finite"


def test_gossip_envelope_integration_preserves_cdl_060_061_boundaries() -> None:
    _relay, _terminal, sealed = _sealed()

    envelope = build_h013_gossip_envelope(
        sealed_envelope=sealed,
        message_id="msg-h013-001",
        payload_cid="bafybeigdyrzt6ncp4m2xg7r5z2xw7sbn3r7r2j7vph6a2m5wqk35m4w5ay",
        sender_peer_id="peer:sender-01",
        transport_headers={"purpose": "testnet-only"},
    )

    assert envelope["channel_id"] == sealed.channel_id
    assert envelope["sender_peer_id"] == "peer:sender-01"
    assert envelope["transport_headers"]["schema_ref"] == H013_SEALED_SPECTRAL_BEACON_VERSION
    assert envelope["transport_headers"]["topic"] == "spectral.beacon.sealed"
    assert "creator_agent_id" not in envelope["transport_headers"]


def test_source_contract_has_no_network_io_or_predictable_prng() -> None:
    source = SOURCE_PATH.read_text(encoding="utf-8")
    for forbidden in (
        "import random",
        "from random",
        "socket.",
        "open_connection(",
        "requests.",
        "time.sleep(",
    ):
        assert forbidden not in source
