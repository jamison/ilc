"""Phase 932-933: ≥20 tests for spectral_beacon.py (H-013 crypto surface).

Karpathy Auto Research methodology applied:
  Fixed evaluator: ≥20 passing tests covering all H-013 hard-pass conditions.
  Hypotheses decomposed across:
    - Full seal/peel/open roundtrip invariants
    - Fixed-size envelope size invariants
    - Replay detection (epoch-keyed, LRU-bounded)
    - Noise sigma floor enforcement (MIN_NOISE_SIGMA=0.005)
    - AAD binding (channel_id / emission_id tamper → decryption failure)
    - Wrong recipient key → decryption failure
    - Lambda validation (empty, too many, NaN, inf, out-of-range)
    - Ed25519 signature tamper detection
    - Transport header sanitization (forbidden keys, key collision)
    - derive_h013_agent_id (deterministic, prefix, key-bound)
    - spectral_hash (deterministic, sort-invariant, hex format)
    - spectral_distance (identity, symmetry)
    - add_noise (CSPRNG — result differs from input)
    - PeerFingerprintCache integration with beacon fingerprint data
    - Dead-peer detection (silence threshold)
    - H013 gossip envelope wrapping (topic, emission_id)
    - BEACON_EMISSION_MODE constants

Gate: h013_gossip_beacon_activation_sequence_lock_930.v0.1
CDL:  cdl_080_star_map_n_gram_route_index.v0.1
"""
from __future__ import annotations

import math

import pytest

from ilc_core.network.d2d.spectral_beacon import (
    BEACON_EMISSION_MODE_MAINNET,
    BEACON_EMISSION_MODE_TESTNET,
    CHACHA20POLY1305_NONCE_SIZE,
    CHACHA20POLY1305_TAG_SIZE,
    INNER_ENVELOPE_SIZE,
    INNER_PLAINTEXT_SIZE,
    MIN_NOISE_SIGMA,
    OUTER_ENVELOPE_SIZE,
    OUTER_PLAINTEXT_SIZE,
    RelayPeelResult,
    SealedSpectralBeaconEnvelope,
    SpectralBeacon,
    SpectralBeaconReplayCache,
    SpectralBeaconValidationError,
    X25519_PUBLIC_KEY_SIZE,
    build_h013_gossip_envelope,
    build_sealed_spectral_beacon,
    derive_h013_agent_id,
    generate_beacon_signing_keypair,
    generate_sealed_sender_keypair,
    open_terminal_layer,
    peel_relay_layer,
    sign_spectral_beacon,
)
from ilc_core.analysis.spectral_utils import add_noise, spectral_distance, spectral_hash
from ilc_core.network.d2d.peer_fingerprint_cache import PeerFingerprintCache

# ---------------------------------------------------------------------------
# Test constants — valid shapes for all helper functions
# ---------------------------------------------------------------------------

_RELAY_PEER_ID = "peer:relay001"
_TERMINAL_PEER_ID = "peer:terminal001"
_CHANNEL_ID = "cid:0000000000000000"
_TEST_LAMBDA = [0.3, 0.8, 1.2]
_TEST_SIGMA = 0.05
_TEST_EPOCH = 42


# ---------------------------------------------------------------------------
# Fixtures / helpers
# ---------------------------------------------------------------------------

def _make_beacon(
    *,
    epoch: int = _TEST_EPOCH,
    lambda_local: list[float] | None = None,
    noise_sigma: float = _TEST_SIGMA,
):
    kp = generate_beacon_signing_keypair()
    beacon = sign_spectral_beacon(
        epoch=epoch,
        lambda_local=lambda_local if lambda_local is not None else list(_TEST_LAMBDA),
        noise_sigma=noise_sigma,
        signing_keypair=kp,
    )
    return kp, beacon


def _make_relay_terminal_kps():
    return generate_sealed_sender_keypair(), generate_sealed_sender_keypair()


def _build_envelope(beacon, relay_kp, terminal_kp, *, channel_id=_CHANNEL_ID, emission_id=None):
    return build_sealed_spectral_beacon(
        beacon=beacon,
        relay_peer_id=_RELAY_PEER_ID,
        relay_public_key=relay_kp.public_key_bytes,
        terminal_peer_id=_TERMINAL_PEER_ID,
        terminal_public_key=terminal_kp.public_key_bytes,
        channel_id=channel_id,
        emission_id=emission_id,
    )


def _full_roundtrip(beacon, relay_kp, terminal_kp, *, emission_id=None, replay_cache=None):
    if replay_cache is None:
        replay_cache = SpectralBeaconReplayCache()
    envelope = _build_envelope(beacon, relay_kp, terminal_kp, emission_id=emission_id)
    relay_result = peel_relay_layer(envelope, relay_kp.private_key)
    return open_terminal_layer(relay_result, terminal_kp.private_key, replay_cache=replay_cache)


# ---------------------------------------------------------------------------
# Test 01 — BEACON_EMISSION_MODE constants
# ---------------------------------------------------------------------------

def test_01_beacon_emission_mode_constants():
    assert BEACON_EMISSION_MODE_TESTNET == "testnet"
    assert BEACON_EMISSION_MODE_MAINNET == "mainnet"
    assert BEACON_EMISSION_MODE_TESTNET != BEACON_EMISSION_MODE_MAINNET


# ---------------------------------------------------------------------------
# Test 02 — Envelope size constants match their structural derivation
# ---------------------------------------------------------------------------

def test_02_envelope_size_constants_structurally_correct():
    expected_inner = (
        X25519_PUBLIC_KEY_SIZE
        + CHACHA20POLY1305_NONCE_SIZE
        + INNER_PLAINTEXT_SIZE
        + CHACHA20POLY1305_TAG_SIZE
    )
    expected_outer = (
        X25519_PUBLIC_KEY_SIZE
        + CHACHA20POLY1305_NONCE_SIZE
        + OUTER_PLAINTEXT_SIZE
        + CHACHA20POLY1305_TAG_SIZE
    )
    assert INNER_ENVELOPE_SIZE == expected_inner == 2108
    assert OUTER_ENVELOPE_SIZE == expected_outer == 4156


# ---------------------------------------------------------------------------
# Tests 03–05 — Full roundtrip + fixed-size byte invariants
# ---------------------------------------------------------------------------

def test_03_full_roundtrip_recovers_beacon_fields():
    _, beacon = _make_beacon()
    relay_kp, terminal_kp = _make_relay_terminal_kps()
    result = _full_roundtrip(beacon, relay_kp, terminal_kp)
    assert result.beacon.epoch == beacon.epoch
    assert result.beacon.lambda_local == beacon.lambda_local
    assert result.beacon.noise_sigma == beacon.noise_sigma
    assert result.beacon.agent_id == beacon.agent_id


def test_04_roundtrip_terminal_peer_id_matches():
    _, beacon = _make_beacon()
    relay_kp, terminal_kp = _make_relay_terminal_kps()
    result = _full_roundtrip(beacon, relay_kp, terminal_kp)
    assert result.terminal_peer_id == _TERMINAL_PEER_ID


def test_05_envelope_bytes_are_fixed_size():
    _, beacon = _make_beacon()
    relay_kp, terminal_kp = _make_relay_terminal_kps()
    envelope = _build_envelope(beacon, relay_kp, terminal_kp)
    assert len(envelope.sealed_outer) == OUTER_ENVELOPE_SIZE
    relay_result = peel_relay_layer(envelope, relay_kp.private_key)
    assert len(relay_result.sealed_inner) == INNER_ENVELOPE_SIZE


# ---------------------------------------------------------------------------
# Tests 06–08 — Replay detection (epoch-keyed)
# ---------------------------------------------------------------------------

def test_06_replay_same_emission_id_same_epoch_rejected():
    _, beacon = _make_beacon()
    relay_kp, terminal_kp = _make_relay_terminal_kps()
    emission_id = "test:E001"
    replay_cache = SpectralBeaconReplayCache()

    # First delivery succeeds.
    _full_roundtrip(beacon, relay_kp, terminal_kp, emission_id=emission_id, replay_cache=replay_cache)

    # Second delivery with same (emission_id, epoch) must be rejected.
    envelope2 = _build_envelope(beacon, relay_kp, terminal_kp, emission_id=emission_id)
    relay_result2 = peel_relay_layer(envelope2, relay_kp.private_key)
    with pytest.raises(SpectralBeaconValidationError) as exc_info:
        open_terminal_layer(relay_result2, terminal_kp.private_key, replay_cache=replay_cache)
    assert exc_info.value.token == "h013_replay_detected"


def test_07_replay_same_id_different_epoch_allowed():
    """(emission_id, epoch1) and (emission_id, epoch2) are distinct cache keys."""
    relay_kp, terminal_kp = _make_relay_terminal_kps()
    signing_kp = generate_beacon_signing_keypair()
    emission_id = "test:E002"
    replay_cache = SpectralBeaconReplayCache()

    beacon_a = sign_spectral_beacon(epoch=10, lambda_local=_TEST_LAMBDA, noise_sigma=_TEST_SIGMA, signing_keypair=signing_kp)
    beacon_b = sign_spectral_beacon(epoch=11, lambda_local=_TEST_LAMBDA, noise_sigma=_TEST_SIGMA, signing_keypair=signing_kp)

    _full_roundtrip(beacon_a, relay_kp, terminal_kp, emission_id=emission_id, replay_cache=replay_cache)
    result_b = _full_roundtrip(beacon_b, relay_kp, terminal_kp, emission_id=emission_id, replay_cache=replay_cache)
    assert result_b.beacon.epoch == 11


def test_08_replay_different_id_same_epoch_allowed():
    """Distinct emission IDs at the same epoch are not each other's replays."""
    relay_kp, terminal_kp = _make_relay_terminal_kps()
    _, beacon = _make_beacon()
    replay_cache = SpectralBeaconReplayCache()

    _full_roundtrip(beacon, relay_kp, terminal_kp, emission_id="test:E003a", replay_cache=replay_cache)
    result_b = _full_roundtrip(beacon, relay_kp, terminal_kp, emission_id="test:E003b", replay_cache=replay_cache)
    assert result_b.beacon.epoch == _TEST_EPOCH


# ---------------------------------------------------------------------------
# Tests 09–10 — Noise sigma floor (MIN_NOISE_SIGMA = 0.005)
# ---------------------------------------------------------------------------

def test_09_sigma_at_floor_is_accepted():
    kp = generate_beacon_signing_keypair()
    beacon = sign_spectral_beacon(epoch=1, lambda_local=_TEST_LAMBDA, noise_sigma=MIN_NOISE_SIGMA, signing_keypair=kp)
    assert beacon.noise_sigma == MIN_NOISE_SIGMA


def test_10_sigma_below_floor_is_rejected():
    kp = generate_beacon_signing_keypair()
    with pytest.raises(SpectralBeaconValidationError) as exc_info:
        sign_spectral_beacon(
            epoch=1,
            lambda_local=_TEST_LAMBDA,
            noise_sigma=MIN_NOISE_SIGMA - 0.001,
            signing_keypair=kp,
        )
    assert exc_info.value.token == "h013_noise_sigma_below_floor"


# ---------------------------------------------------------------------------
# Tests 11–12 — Wrong decryption key → failure
# ---------------------------------------------------------------------------

def test_11_wrong_relay_private_key_fails_peel():
    _, beacon = _make_beacon()
    relay_kp, terminal_kp = _make_relay_terminal_kps()
    wrong_relay_kp = generate_sealed_sender_keypair()
    envelope = _build_envelope(beacon, relay_kp, terminal_kp)
    with pytest.raises(SpectralBeaconValidationError) as exc_info:
        peel_relay_layer(envelope, wrong_relay_kp.private_key)
    assert exc_info.value.token == "h013_decryption_failed"


def test_12_wrong_terminal_private_key_fails_open():
    _, beacon = _make_beacon()
    relay_kp, terminal_kp = _make_relay_terminal_kps()
    wrong_terminal_kp = generate_sealed_sender_keypair()
    envelope = _build_envelope(beacon, relay_kp, terminal_kp)
    relay_result = peel_relay_layer(envelope, relay_kp.private_key)
    with pytest.raises(SpectralBeaconValidationError) as exc_info:
        open_terminal_layer(relay_result, wrong_terminal_kp.private_key, replay_cache=SpectralBeaconReplayCache())
    assert exc_info.value.token == "h013_decryption_failed"


# ---------------------------------------------------------------------------
# Tests 13–14 — AAD binding (tampered metadata → decryption failure)
# ---------------------------------------------------------------------------

def test_13_tampered_channel_id_invalidates_outer_aad():
    """Changing channel_id post-sealing corrupts the outer layer AAD."""
    _, beacon = _make_beacon()
    relay_kp, terminal_kp = _make_relay_terminal_kps()
    envelope = _build_envelope(beacon, relay_kp, terminal_kp, channel_id=_CHANNEL_ID)
    # Substitute a different but valid channel_id — AAD won't match.
    tampered = SealedSpectralBeaconEnvelope(
        relay_peer_id=envelope.relay_peer_id,
        channel_id="rand:0000000000000000",
        emission_id=envelope.emission_id,
        sealed_outer=envelope.sealed_outer,
    )
    with pytest.raises(SpectralBeaconValidationError) as exc_info:
        peel_relay_layer(tampered, relay_kp.private_key)
    assert exc_info.value.token == "h013_decryption_failed"


def test_14_tampered_emission_id_invalidates_inner_aad():
    """Changing emission_id in the relay result corrupts the inner layer AAD."""
    _, beacon = _make_beacon()
    relay_kp, terminal_kp = _make_relay_terminal_kps()
    envelope = _build_envelope(beacon, relay_kp, terminal_kp, emission_id="test:E004")
    relay_result = peel_relay_layer(envelope, relay_kp.private_key)
    tampered_relay = RelayPeelResult(
        next_hop_peer_id=relay_result.next_hop_peer_id,
        channel_id=relay_result.channel_id,
        emission_id="test:E999",  # wrong — AAD mismatch
        sealed_inner=relay_result.sealed_inner,
    )
    with pytest.raises(SpectralBeaconValidationError) as exc_info:
        open_terminal_layer(tampered_relay, terminal_kp.private_key, replay_cache=SpectralBeaconReplayCache())
    assert exc_info.value.token == "h013_decryption_failed"


# ---------------------------------------------------------------------------
# Tests 15–17c — Lambda validation
# ---------------------------------------------------------------------------

def test_15_lambda_empty_list_rejected():
    kp = generate_beacon_signing_keypair()
    with pytest.raises(SpectralBeaconValidationError) as exc_info:
        sign_spectral_beacon(epoch=1, lambda_local=[], noise_sigma=_TEST_SIGMA, signing_keypair=kp)
    assert exc_info.value.token == "h013_lambda_local_invalid"


def test_16_lambda_exceeds_max_values_rejected():
    kp = generate_beacon_signing_keypair()
    with pytest.raises(SpectralBeaconValidationError) as exc_info:
        sign_spectral_beacon(epoch=1, lambda_local=[0.5] * 33, noise_sigma=_TEST_SIGMA, signing_keypair=kp)
    assert exc_info.value.token == "h013_lambda_local_too_large"


def test_17a_lambda_nan_rejected():
    kp = generate_beacon_signing_keypair()
    with pytest.raises(SpectralBeaconValidationError) as exc_info:
        sign_spectral_beacon(epoch=1, lambda_local=[0.5, float("nan")], noise_sigma=_TEST_SIGMA, signing_keypair=kp)
    assert exc_info.value.token == "h013_lambda_local_non_finite"


def test_17b_lambda_inf_rejected():
    kp = generate_beacon_signing_keypair()
    with pytest.raises(SpectralBeaconValidationError) as exc_info:
        sign_spectral_beacon(epoch=1, lambda_local=[0.5, float("inf")], noise_sigma=_TEST_SIGMA, signing_keypair=kp)
    assert exc_info.value.token == "h013_lambda_local_non_finite"


def test_17c_lambda_above_max_laplacian_eigenvalue_rejected():
    """Normalized Laplacian eigenvalues lie in [0, 2]; values above 2.0 are invalid."""
    kp = generate_beacon_signing_keypair()
    with pytest.raises(SpectralBeaconValidationError) as exc_info:
        sign_spectral_beacon(epoch=1, lambda_local=[2.001], noise_sigma=_TEST_SIGMA, signing_keypair=kp)
    assert exc_info.value.token == "h013_lambda_local_out_of_range"


# ---------------------------------------------------------------------------
# Test 18 — Ed25519 signature tamper detection
# ---------------------------------------------------------------------------

def test_18_tampered_lambda_rejects_old_signature():
    """Constructing a SpectralBeacon with modified lambda but the original
    Ed25519 signature must be caught by _normalize_beacon inside build_sealed_spectral_beacon."""
    kp = generate_beacon_signing_keypair()
    beacon = sign_spectral_beacon(epoch=1, lambda_local=[0.5, 1.0], noise_sigma=_TEST_SIGMA, signing_keypair=kp)
    tampered = SpectralBeacon(
        epoch=beacon.epoch,
        lambda_local=[0.6, 1.1],        # modified — signature no longer valid
        noise_sigma=beacon.noise_sigma,
        agent_id=beacon.agent_id,
        agent_public_key=beacon.agent_public_key,
        agent_signature=beacon.agent_signature,
    )
    relay_kp, terminal_kp = _make_relay_terminal_kps()
    with pytest.raises(SpectralBeaconValidationError) as exc_info:
        build_sealed_spectral_beacon(
            beacon=tampered,
            relay_peer_id=_RELAY_PEER_ID,
            relay_public_key=relay_kp.public_key_bytes,
            terminal_peer_id=_TERMINAL_PEER_ID,
            terminal_public_key=terminal_kp.public_key_bytes,
            channel_id=_CHANNEL_ID,
        )
    assert exc_info.value.token == "h013_agent_signature_invalid"


# ---------------------------------------------------------------------------
# Tests 19–21 — Transport header sanitization
# ---------------------------------------------------------------------------

def test_19_forbidden_header_agent_id_rejected():
    _, beacon = _make_beacon()
    relay_kp, terminal_kp = _make_relay_terminal_kps()
    envelope = _build_envelope(beacon, relay_kp, terminal_kp)
    with pytest.raises(SpectralBeaconValidationError) as exc_info:
        build_h013_gossip_envelope(
            sealed_envelope=envelope,
            payload_cid="bafyreiabc",
            transport_headers={"agent_id": "forbidden-value"},
        )
    assert exc_info.value.token == "h013_transport_header_forbidden"


def test_20_forbidden_header_lambda_local_rejected():
    _, beacon = _make_beacon()
    relay_kp, terminal_kp = _make_relay_terminal_kps()
    envelope = _build_envelope(beacon, relay_kp, terminal_kp)
    with pytest.raises(SpectralBeaconValidationError) as exc_info:
        build_h013_gossip_envelope(
            sealed_envelope=envelope,
            payload_cid="bafyreiabc",
            transport_headers={"lambda_local": "0.5,1.0"},
        )
    assert exc_info.value.token == "h013_transport_header_forbidden"


def test_21_header_key_collision_rejected():
    """'x-custom-key' and 'X-Custom-Key' lower-case to the same key → collision."""
    _, beacon = _make_beacon()
    relay_kp, terminal_kp = _make_relay_terminal_kps()
    envelope = _build_envelope(beacon, relay_kp, terminal_kp)
    with pytest.raises(SpectralBeaconValidationError) as exc_info:
        build_h013_gossip_envelope(
            sealed_envelope=envelope,
            payload_cid="bafyreiabc",
            transport_headers={"x-custom-key": "val1", "X-Custom-Key": "val2"},
        )
    assert exc_info.value.token == "h013_transport_header_key_collision"


# ---------------------------------------------------------------------------
# Tests 22–23b — derive_h013_agent_id
# ---------------------------------------------------------------------------

def test_22_derive_agent_id_is_deterministic():
    kp = generate_beacon_signing_keypair()
    pub = kp.public_key_bytes
    assert derive_h013_agent_id(pub) == derive_h013_agent_id(pub)


def test_23_derive_agent_id_has_agent_prefix():
    kp = generate_beacon_signing_keypair()
    assert derive_h013_agent_id(kp.public_key_bytes).startswith("agent:")


def test_23b_different_keys_produce_different_agent_ids():
    kp1 = generate_beacon_signing_keypair()
    kp2 = generate_beacon_signing_keypair()
    assert derive_h013_agent_id(kp1.public_key_bytes) != derive_h013_agent_id(kp2.public_key_bytes)


# ---------------------------------------------------------------------------
# Tests 24–26 — spectral_hash
# ---------------------------------------------------------------------------

def test_24_spectral_hash_is_deterministic():
    vals = [1.5, 0.3, 0.9]
    assert spectral_hash(vals) == spectral_hash(vals)


def test_25_spectral_hash_is_sort_invariant():
    """spectral_hash sorts internally; order of input must not matter."""
    vals = [1.5, 0.3, 0.9]
    shuffled = [0.9, 1.5, 0.3]
    assert spectral_hash(vals) == spectral_hash(shuffled)


def test_26_spectral_hash_is_64_char_lowercase_hex():
    h = spectral_hash([0.1, 0.5, 1.0])
    assert len(h) == 64
    assert all(c in "0123456789abcdef" for c in h)


# ---------------------------------------------------------------------------
# Tests 27–28 — spectral_distance
# ---------------------------------------------------------------------------

def test_27_spectral_distance_to_self_is_zero():
    vals = [0.5, 1.0, 1.5]
    assert spectral_distance(vals, vals) == pytest.approx(0.0)


def test_28_spectral_distance_is_symmetric():
    a = [0.3, 0.8, 1.2]
    b = [0.5, 1.0, 0.9]
    assert spectral_distance(a, b) == pytest.approx(spectral_distance(b, a))


# ---------------------------------------------------------------------------
# Test 29 — add_noise (CSPRNG — result must differ from input)
# ---------------------------------------------------------------------------

def test_29_add_noise_changes_values_and_preserves_length():
    """add_noise uses os.urandom/Box-Muller; result must not equal the input
    (the probability of all three values being identical after Gaussian noise
    with sigma=0.1 is astronomically small — treat any equality as a test failure)."""
    vals = [0.5, 1.0, 1.5]
    noised = add_noise(vals, sigma=0.1)
    assert len(noised) == len(vals)
    assert noised != vals, "add_noise must perturb eigenvalues"
    assert all(math.isfinite(v) for v in noised)


# ---------------------------------------------------------------------------
# Tests 30–31 — PeerFingerprintCache ↔ beacon integration
# ---------------------------------------------------------------------------

def test_30_peer_fingerprint_cache_roundtrip_with_beacon():
    """Cache the result of a beacon open, then verify as_fingerprint_dict()."""
    kp = generate_beacon_signing_keypair()
    beacon = sign_spectral_beacon(epoch=_TEST_EPOCH, lambda_local=_TEST_LAMBDA, noise_sigma=_TEST_SIGMA, signing_keypair=kp)
    cache = PeerFingerprintCache()
    cache.update(
        peer_endpoint=_TERMINAL_PEER_ID,
        lambda_local=beacon.lambda_local,
        noise_sigma=beacon.noise_sigma,
        epoch=beacon.epoch,
        agent_id=beacon.agent_id,
    )
    fp_dict = cache.as_fingerprint_dict()
    assert _TERMINAL_PEER_ID in fp_dict
    assert fp_dict[_TERMINAL_PEER_ID] == beacon.lambda_local


def test_31_dead_peer_detection_respects_silence_threshold():
    """A peer silent for > DEFAULT_DEAD_PEER_SILENCE_EPOCHS (10) is declared dead.
    A peer last seen exactly at the threshold boundary is still alive."""
    cache = PeerFingerprintCache()
    cache.update(
        peer_endpoint="peer:oldnode001",
        lambda_local=[0.5, 1.0],
        noise_sigma=_TEST_SIGMA,
        epoch=100,
    )
    # 111 - 100 = 11 > 10 → dead
    assert cache.is_dead_peer("peer:oldnode001", current_epoch=111)
    # 110 - 100 = 10, not > 10 → alive
    assert not cache.is_dead_peer("peer:oldnode001", current_epoch=110)


# ---------------------------------------------------------------------------
# Test 32 — H-013 gossip envelope wrapping
# ---------------------------------------------------------------------------

def test_32_gossip_envelope_carries_topic_and_emission_id():
    """build_h013_gossip_envelope must embed topic and emission_id in transport headers."""
    _, beacon = _make_beacon()
    relay_kp, terminal_kp = _make_relay_terminal_kps()
    emission_id = "test:E005"
    envelope = _build_envelope(beacon, relay_kp, terminal_kp, emission_id=emission_id)
    gossip = build_h013_gossip_envelope(
        sealed_envelope=envelope,
        payload_cid="bafyreiabc",
    )
    headers = gossip["transport_headers"]
    assert headers["topic"] == "spectral.beacon.sealed"
    assert headers["h013_emission_id"] == emission_id
