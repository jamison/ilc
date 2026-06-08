"""Tests for H-013 sealed-sender spectral beacon implementation."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import pytest

from ilc_core.network.d2d import spectral_beacon as spectral_beacon_module
from ilc_core.network.d2d.spectral_beacon import (
    ADR_0034_DEPENDENCY,
    H013_SEALED_SPECTRAL_BEACON_VERSION,
    INNER_ENVELOPE_SIZE,
    MIN_NOISE_SIGMA,
    OUTER_ENVELOPE_SIZE,
    SpectralBeacon,
    SpectralBeaconReplayCache,
    SpectralBeaconValidationError,
    build_h013_gossip_envelope,
    build_sealed_spectral_beacon,
    derive_h013_agent_id,
    generate_beacon_signing_keypair,
    generate_sealed_sender_keypair,
    open_terminal_layer,
    peel_relay_layer,
    sign_spectral_beacon,
)


SOURCE_PATH = Path("ilc_core/network/d2d/spectral_beacon.py")


def _keypairs():
    return generate_sealed_sender_keypair(), generate_sealed_sender_keypair()


def _beacon(
    *,
    signing_keypair=None,
    epoch: int = 823,
    lambda_local: list[float] | None = None,
    noise_sigma: float = 0.08,
) -> SpectralBeacon:
    return sign_spectral_beacon(
        epoch=epoch,
        lambda_local=lambda_local or [0.12, 0.34, 0.56],
        noise_sigma=noise_sigma,
        signing_keypair=signing_keypair or generate_beacon_signing_keypair(),
    )


def _sealed(beacon: SpectralBeacon | None = None):
    relay, terminal = _keypairs()
    sealed_beacon = beacon or _beacon()
    sealed = build_sealed_spectral_beacon(
        beacon=sealed_beacon,
        relay_peer_id="peer:relay-01",
        relay_public_key=relay.public_key_bytes,
        terminal_peer_id="peer:terminal-01",
        terminal_public_key=terminal.public_key_bytes,
        channel_id="rand:abcdef0123456789abcdef0123456789",
        emission_id="emission:h013-test-001",
    )
    return relay, terminal, sealed_beacon, sealed


def test_version_dependency_and_fixed_size_constants_are_locked() -> None:
    assert H013_SEALED_SPECTRAL_BEACON_VERSION == "h013_sealed_spectral_beacon.v0.1"
    assert ADR_0034_DEPENDENCY == "run_h013_d2d_sealed_sender_adr_verdict=accepted"
    assert INNER_ENVELOPE_SIZE == 2108
    assert OUTER_ENVELOPE_SIZE == 4156


def test_envelope_construction_relay_peel_and_terminal_delivery() -> None:
    relay, terminal, beacon, sealed = _sealed()

    assert sealed.relay_peer_id == "peer:relay-01"
    assert sealed.channel_id == "rand:abcdef0123456789abcdef0123456789"
    assert sealed.emission_id == "emission:h013-test-001"
    assert len(sealed.sealed_outer) == OUTER_ENVELOPE_SIZE

    relay_result = peel_relay_layer(sealed, relay.private_key)
    assert relay_result.next_hop_peer_id == "peer:terminal-01"
    assert relay_result.channel_id == sealed.channel_id
    assert relay_result.emission_id == sealed.emission_id
    assert len(relay_result.sealed_inner) == INNER_ENVELOPE_SIZE

    terminal_result = open_terminal_layer(
        relay_result,
        terminal.private_key,
        replay_cache=SpectralBeaconReplayCache(),
    )
    assert terminal_result.terminal_peer_id == "peer:terminal-01"
    assert terminal_result.emission_id == sealed.emission_id
    assert terminal_result.beacon == beacon


def test_relay_peel_exposes_only_next_hop_and_inner_ciphertext() -> None:
    beacon = _beacon()
    relay, _terminal, _beacon_value, sealed = _sealed(beacon)

    relay_result = peel_relay_layer(sealed, relay.private_key)

    assert relay_result.next_hop_peer_id == "peer:terminal-01"
    assert not hasattr(relay_result, "beacon")
    assert beacon.agent_id.encode("utf-8") not in relay_result.sealed_inner
    assert beacon.agent_id.encode("utf-8") not in sealed.sealed_outer


def test_fixed_size_padding_invariant_holds_for_different_payload_sizes() -> None:
    relay, terminal = _keypairs()
    small = build_sealed_spectral_beacon(
        beacon=_beacon(epoch=1, lambda_local=[0.1], noise_sigma=MIN_NOISE_SIGMA),
        relay_peer_id="peer:relay-01",
        relay_public_key=relay.public_key_bytes,
        terminal_peer_id="peer:terminal-01",
        terminal_public_key=terminal.public_key_bytes,
        channel_id="cid:0123456789abcdef0123456789abcdef",
        emission_id="emission:h013-small",
    )
    large = build_sealed_spectral_beacon(
        beacon=_beacon(
            epoch=1,
            lambda_local=[float(index) / 100.0 for index in range(32)],
            noise_sigma=MIN_NOISE_SIGMA,
        ),
        relay_peer_id="peer:relay-01",
        relay_public_key=relay.public_key_bytes,
        terminal_peer_id="peer:terminal-01",
        terminal_public_key=terminal.public_key_bytes,
        channel_id="cid:0123456789abcdef0123456789abcdef",
        emission_id="emission:h013-large",
    )

    assert len(small.sealed_outer) == OUTER_ENVELOPE_SIZE
    assert len(large.sealed_outer) == OUTER_ENVELOPE_SIZE
    assert len(peel_relay_layer(small, relay.private_key).sealed_inner) == INNER_ENVELOPE_SIZE
    assert len(peel_relay_layer(large, relay.private_key).sealed_inner) == INNER_ENVELOPE_SIZE


def test_wrong_key_cannot_open_relay_or_terminal_layers() -> None:
    relay, terminal, beacon, sealed = _sealed()
    wrong = generate_sealed_sender_keypair()

    with pytest.raises(SpectralBeaconValidationError) as relay_exc:
        peel_relay_layer(sealed, wrong.private_key)
    assert relay_exc.value.token == "h013_decryption_failed"

    relay_result = peel_relay_layer(sealed, relay.private_key)
    with pytest.raises(SpectralBeaconValidationError) as terminal_exc:
        open_terminal_layer(
            relay_result,
            relay.private_key,
            replay_cache=SpectralBeaconReplayCache(),
        )
    assert terminal_exc.value.token == "h013_decryption_failed"

    opened = open_terminal_layer(
        relay_result,
        terminal.private_key,
        replay_cache=SpectralBeaconReplayCache(),
    )
    assert opened.beacon.agent_id == beacon.agent_id


def test_validation_rejects_non_finite_lambda_values() -> None:
    with pytest.raises(SpectralBeaconValidationError) as exc:
        _beacon(lambda_local=[0.1, float("nan")], noise_sigma=MIN_NOISE_SIGMA)
    assert exc.value.token == "h013_lambda_local_non_finite"


def test_validation_rejects_out_of_range_spectral_values() -> None:
    with pytest.raises(SpectralBeaconValidationError) as exc:
        _beacon(lambda_local=[2.01], noise_sigma=MIN_NOISE_SIGMA)
    assert exc.value.token == "h013_lambda_local_out_of_range"


def test_validation_rejects_sim_beacon_noise_floor_bypass() -> None:
    with pytest.raises(SpectralBeaconValidationError) as exc:
        _beacon(lambda_local=[0.1], noise_sigma=0.0)
    assert exc.value.token == "h013_noise_sigma_below_floor"


def test_validation_rejects_bool_epoch_and_bool_spectral_numbers() -> None:
    with pytest.raises(SpectralBeaconValidationError) as epoch_exc:
        _beacon(epoch=True, lambda_local=[0.1], noise_sigma=MIN_NOISE_SIGMA)  # type: ignore[arg-type]
    assert epoch_exc.value.token == "h013_epoch_invalid"

    with pytest.raises(SpectralBeaconValidationError) as lambda_exc:
        _beacon(lambda_local=[True], noise_sigma=MIN_NOISE_SIGMA)  # type: ignore[list-item]
    assert lambda_exc.value.token == "h013_lambda_local_non_finite"


def test_terminal_replay_cache_rejects_duplicate_emission_id() -> None:
    relay, terminal, _beacon_value, sealed = _sealed()
    relay_result = peel_relay_layer(sealed, relay.private_key)
    cache = SpectralBeaconReplayCache()

    open_terminal_layer(relay_result, terminal.private_key, replay_cache=cache)

    with pytest.raises(SpectralBeaconValidationError) as exc:
        open_terminal_layer(relay_result, terminal.private_key, replay_cache=cache)
    assert exc.value.token == "h013_replay_detected"


def test_terminal_open_requires_explicit_replay_cache() -> None:
    relay, terminal, _beacon_value, sealed = _sealed()
    relay_result = peel_relay_layer(sealed, relay.private_key)

    with pytest.raises(SpectralBeaconValidationError) as exc:
        open_terminal_layer(relay_result, terminal.private_key, replay_cache=None)  # type: ignore[arg-type]
    assert exc.value.token == "h013_replay_cache_invalid"


def test_terminal_replay_cache_is_bounded() -> None:
    cache = SpectralBeaconReplayCache(max_entries=2)

    cache.check_and_store("emission:one", epoch=1)
    cache.check_and_store("emission:two", epoch=1)
    cache.check_and_store("emission:three", epoch=1)

    assert list(cache.seen_keys) == [
        ("emission:two", 1),
        ("emission:three", 1),
    ]


def test_malformed_terminal_payload_does_not_poison_replay_cache() -> None:
    relay, terminal = _keypairs()
    cache = SpectralBeaconReplayCache()
    channel_id = "rand:abcdef0123456789abcdef0123456789"
    emission_id = "emission:h013-invalid-first"
    invalid_plaintext = spectral_beacon_module._pack_fixed_json(
        {
            "emission_id": emission_id,
            "terminal_peer_id": "peer:terminal-01",
            "beacon": {"epoch": 1},
        },
        spectral_beacon_module.INNER_PLAINTEXT_SIZE,
        "h013_inner_payload_too_large",
    )
    invalid_relay_result = spectral_beacon_module.RelayPeelResult(
        next_hop_peer_id="peer:terminal-01",
        channel_id=channel_id,
        emission_id=emission_id,
        sealed_inner=spectral_beacon_module._seal_for_recipient(
            plaintext=invalid_plaintext,
            recipient_public_key=spectral_beacon_module.public_key_from_bytes(
                terminal.public_key_bytes,
            ),
            aad=spectral_beacon_module._layer_aad("inner", channel_id, emission_id),
        ),
    )

    with pytest.raises(SpectralBeaconValidationError) as exc:
        open_terminal_layer(invalid_relay_result, terminal.private_key, replay_cache=cache)
    assert exc.value.token == "h013_beacon_payload_invalid"
    assert cache.seen_keys == {}

    valid = build_sealed_spectral_beacon(
        beacon=_beacon(epoch=1, lambda_local=[0.1], noise_sigma=MIN_NOISE_SIGMA),
        relay_peer_id="peer:relay-01",
        relay_public_key=relay.public_key_bytes,
        terminal_peer_id="peer:terminal-01",
        terminal_public_key=terminal.public_key_bytes,
        channel_id=channel_id,
        emission_id=emission_id,
    )
    opened = open_terminal_layer(
        peel_relay_layer(valid, relay.private_key),
        terminal.private_key,
        replay_cache=cache,
    )
    assert opened.emission_id == emission_id


def test_beacon_agent_id_is_derived_from_authenticated_public_key() -> None:
    beacon = _beacon()
    assert beacon.agent_id == derive_h013_agent_id(beacon.agent_public_key)

    relay, terminal = _keypairs()
    forged = replace(beacon, agent_id="agent:forged")
    with pytest.raises(SpectralBeaconValidationError) as exc:
        build_sealed_spectral_beacon(
            beacon=forged,
            relay_peer_id="peer:relay-01",
            relay_public_key=relay.public_key_bytes,
            terminal_peer_id="peer:terminal-01",
            terminal_public_key=terminal.public_key_bytes,
            channel_id="rand:abcdef0123456789abcdef0123456789",
            emission_id="emission:h013-forged",
        )
    assert exc.value.token == "h013_agent_id_key_mismatch"


def test_beacon_signature_must_verify_terminal_visible_claims() -> None:
    beacon = _beacon()
    relay, terminal = _keypairs()
    tampered = replace(beacon, agent_signature=b"\x00" * 64)

    with pytest.raises(SpectralBeaconValidationError) as exc:
        build_sealed_spectral_beacon(
            beacon=tampered,
            relay_peer_id="peer:relay-01",
            relay_public_key=relay.public_key_bytes,
            terminal_peer_id="peer:terminal-01",
            terminal_public_key=terminal.public_key_bytes,
            channel_id="rand:abcdef0123456789abcdef0123456789",
            emission_id="emission:h013-tampered-signature",
        )
    assert exc.value.token == "h013_agent_signature_invalid"


def test_low_order_x25519_public_key_uses_tokenized_validation_error() -> None:
    terminal = generate_sealed_sender_keypair()

    with pytest.raises(SpectralBeaconValidationError) as exc:
        build_sealed_spectral_beacon(
            beacon=_beacon(),
            relay_peer_id="peer:relay-01",
            relay_public_key=b"\x00" * 32,
            terminal_peer_id="peer:terminal-01",
            terminal_public_key=terminal.public_key_bytes,
            channel_id="rand:abcdef0123456789abcdef0123456789",
            emission_id="emission:h013-low-order",
        )
    assert exc.value.token == "h013_key_exchange_failed"


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

    valid_mapping = spectral_beacon_module._normalize_beacon(_beacon())
    valid_mapping["lambda_local"] = ["nan"]
    with pytest.raises(SpectralBeaconValidationError) as finite_exc:
        spectral_beacon_module._beacon_from_mapping(valid_mapping)
    assert finite_exc.value.token == "h013_lambda_local_non_finite"


def test_gossip_envelope_integration_preserves_cdl_060_061_boundaries() -> None:
    _relay, _terminal, _beacon_value, sealed = _sealed()

    envelope = build_h013_gossip_envelope(
        sealed_envelope=sealed,
        payload_cid="bafybeigdyrzt6ncp4m2xg7r5z2xw7sbn3r7r2j7vph6a2m5wqk35m4w5ay",
        transport_headers={"purpose": "testnet-only"},
    )

    assert envelope["message_id"] == sealed.emission_id
    assert envelope["channel_id"] == sealed.channel_id
    assert envelope["sender_peer_id"] == sealed.relay_peer_id
    assert envelope["transport_headers"]["schema_ref"] == H013_SEALED_SPECTRAL_BEACON_VERSION
    assert envelope["transport_headers"]["topic"] == "spectral.beacon.sealed"
    assert envelope["transport_headers"]["h013_emission_id"] == sealed.emission_id
    assert "creator_agent_id" not in envelope["transport_headers"]
    assert "agent_id" not in envelope["transport_headers"]


def test_gossip_envelope_rejects_header_fields_that_reidentify_origin_or_spectral_payload() -> None:
    _relay, _terminal, _beacon_value, sealed = _sealed()

    for forbidden_header in (
        "agent_id",
        "schema_ref",
        "topic",
        "h013-emission-id",
        "source-agent-id",
        "sender_peer_id",
        "origin.peer.id",
        "lambda_local",
        "noise_sigma",
        "raw_spectral_coordinates",
        "cluster_membership",
    ):
        with pytest.raises(SpectralBeaconValidationError) as exc:
            build_h013_gossip_envelope(
                sealed_envelope=sealed,
                payload_cid="bafybeigdyrzt6ncp4m2xg7r5z2xw7sbn3r7r2j7vph6a2m5wqk35m4w5ay",
                transport_headers={forbidden_header: "leak"},
            )
        assert exc.value.token == "h013_transport_header_forbidden"


def test_gossip_envelope_rejects_case_folded_transport_header_collisions() -> None:
    _relay, _terminal, _beacon_value, sealed = _sealed()

    with pytest.raises(SpectralBeaconValidationError) as exc:
        build_h013_gossip_envelope(
            sealed_envelope=sealed,
            payload_cid="bafybeigdyrzt6ncp4m2xg7r5z2xw7sbn3r7r2j7vph6a2m5wqk35m4w5ay",
            transport_headers={"Purpose": "one", "purpose": "two"},
        )
    assert exc.value.token == "h013_transport_header_key_collision"


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
