# SPDX-License-Identifier: AGPL-3.0-or-later
"""H-013 sealed spectral beacon construction.

This module implements the bounded one-relay sealed-sender payload from
ADR-0034. It performs no network I/O and does not activate D2d gossip in
production. Callers may wrap the returned payload in the existing CDL-060/061
gossip envelope surface.
"""

from __future__ import annotations

import base64
import binascii
from dataclasses import dataclass, field
import hashlib
import json
import math
import re
import secrets
from typing import Any, List, Mapping

from cryptography.exceptions import InvalidSignature, InvalidTag
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ed25519, x25519
from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

from .gossip import build_transport_envelope
from .interface import validate_d2d_channel, validate_d2d_peer_id


H013_SEALED_SPECTRAL_BEACON_VERSION = "h013_sealed_spectral_beacon.v0.1"
ADR_0034_DEPENDENCY = "run_h013_d2d_sealed_sender_adr_verdict=accepted"

MAX_LAMBDA_VALUES = 32
MAX_AGENT_ID_BYTES = 128
MAX_EMISSION_ID_BYTES = 128
MIN_NOISE_SIGMA = 0.005
# H-013 Q1 Option C: beacon emission gated by mode flag.
# TESTNET: emit with placeholder epsilon (sigma=0.05); no mainnet risk.
# MAINNET: gate lifted only after SIM-BEACON-01 calibration completes.
BEACON_EMISSION_MODE_TESTNET = "testnet"
BEACON_EMISSION_MODE_MAINNET = "mainnet"
MAX_NORMALIZED_LAPLACIAN_EIGENVALUE = 2.0
MAX_REPLAY_CACHE_ENTRIES = 4096
INNER_PLAINTEXT_SIZE = 2048
OUTER_PLAINTEXT_SIZE = 4096
X25519_PUBLIC_KEY_SIZE = 32
ED25519_PUBLIC_KEY_SIZE = 32
ED25519_SIGNATURE_SIZE = 64
CHACHA20POLY1305_NONCE_SIZE = 12
CHACHA20POLY1305_TAG_SIZE = 16
INNER_ENVELOPE_SIZE = X25519_PUBLIC_KEY_SIZE + CHACHA20POLY1305_NONCE_SIZE + INNER_PLAINTEXT_SIZE + CHACHA20POLY1305_TAG_SIZE
OUTER_ENVELOPE_SIZE = X25519_PUBLIC_KEY_SIZE + CHACHA20POLY1305_NONCE_SIZE + OUTER_PLAINTEXT_SIZE + CHACHA20POLY1305_TAG_SIZE


class SpectralBeaconValidationError(ValueError):
    """Validation exception with deterministic token semantics."""

    def __init__(self, token: str, message: str) -> None:
        super().__init__(message)
        self.token = token
        self.message = message


@dataclass(frozen=True)
class SpectralBeacon:
    """Privacy-noised local spectral fingerprint.

    `agent_id` is present only in the terminal payload. Relay nodes never see it
    after peeling the outer sealed-sender layer.
    """

    epoch: int
    lambda_local: List[float]
    noise_sigma: float
    agent_id: str
    agent_public_key: bytes
    agent_signature: bytes


@dataclass(frozen=True)
class BeaconSigningKeypair:
    """Ed25519 keypair used to authenticate the terminal-visible beacon."""

    private_key: ed25519.Ed25519PrivateKey

    @property
    def public_key_bytes(self) -> bytes:
        return self.private_key.public_key().public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw,
        )

    @property
    def agent_id(self) -> str:
        return derive_h013_agent_id(self.public_key_bytes)


@dataclass(frozen=True)
class SealedSenderKeypair:
    """X25519 keypair for the H-013 sealed-sender testnet surface."""

    private_key: x25519.X25519PrivateKey

    @property
    def public_key_bytes(self) -> bytes:
        return self.private_key.public_key().public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw,
        )


@dataclass(frozen=True)
class SealedSpectralBeaconEnvelope:
    """Outer sealed envelope addressed to a bounded relay."""

    relay_peer_id: str
    channel_id: str
    emission_id: str
    sealed_outer: bytes


@dataclass(frozen=True)
class RelayPeelResult:
    """Relay-visible result after peeling one layer."""

    next_hop_peer_id: str
    channel_id: str
    emission_id: str
    sealed_inner: bytes


@dataclass(frozen=True)
class TerminalOpenResult:
    """Terminal-visible opened spectral beacon."""

    terminal_peer_id: str
    channel_id: str
    emission_id: str
    beacon: SpectralBeacon


@dataclass
class SpectralBeaconReplayCache:
    """Terminal-side replay guard for H-013 emission IDs.

    Keys are (normalized_emission_id, epoch) tuples. This makes beacons from
    prior epochs trivially invalid without needing cross-epoch coordination:
    a replayed beacon is rejected not only because its emission_id was seen,
    but because its (emission_id, epoch) pair is bound to a specific epoch and
    cannot be re-used in a different epoch even if the LRU evicts the entry.

    Eviction policy: LRU by insertion order (dict iteration is insertion-ordered
    in Python 3.7+). Oldest (emission_id, epoch) pair is dropped when the cache
    is full. An attacker replaying an evicted beacon from a prior epoch will be
    caught by epoch staleness validation at the application layer, not the cache.
    """

    seen_keys: dict[tuple[str, int], None] = field(default_factory=dict)
    max_entries: int = MAX_REPLAY_CACHE_ENTRIES

    def check_and_store(self, emission_id: str, epoch: int) -> None:
        """Check for replay and store the (emission_id, epoch) key.

        Raises SpectralBeaconValidationError if:
        - max_entries is not positive (misconfigured cache)
        - (emission_id, epoch) pair was already seen (replay detected)
        """
        normalized = _normalize_emission_id(emission_id)
        if not isinstance(epoch, int) or isinstance(epoch, bool) or epoch < 0:
            raise SpectralBeaconValidationError(
                "h013_replay_cache_epoch_invalid",
                "replay_cache_epoch_must_be_non_negative_int",
            )
        cache_key = (normalized, epoch)
        if self.max_entries <= 0:
            raise SpectralBeaconValidationError(
                "h013_replay_cache_size_invalid",
                "replay_cache_size_invalid",
            )
        if cache_key in self.seen_keys:
            raise SpectralBeaconValidationError(
                "h013_replay_detected",
                "emission_id_epoch_pair_replayed",
            )
        if len(self.seen_keys) >= self.max_entries:
            self.seen_keys.pop(next(iter(self.seen_keys)))
        self.seen_keys[cache_key] = None


def generate_sealed_sender_keypair() -> SealedSenderKeypair:
    """Generate an X25519 sealed-sender keypair."""

    return SealedSenderKeypair(private_key=x25519.X25519PrivateKey.generate())


def generate_beacon_signing_keypair() -> BeaconSigningKeypair:
    """Generate an Ed25519 beacon-signing keypair."""

    return BeaconSigningKeypair(private_key=ed25519.Ed25519PrivateKey.generate())


def derive_h013_agent_id(agent_public_key: bytes) -> str:
    """Derive the H-013 terminal-visible agent ID from an Ed25519 public key."""

    normalized = _normalize_agent_public_key(agent_public_key)
    return "agent:" + hashlib.sha256(normalized).hexdigest()[:32]


def sign_spectral_beacon(
    *,
    epoch: int,
    lambda_local: List[float],
    noise_sigma: float,
    signing_keypair: BeaconSigningKeypair,
) -> SpectralBeacon:
    """Construct an authenticated spectral beacon from calibrated inputs."""

    normalized_epoch = _normalize_epoch(epoch)
    normalized_lambda = _normalize_lambda_local(lambda_local)
    normalized_noise = _normalize_noise_sigma(noise_sigma)
    public_key = signing_keypair.public_key_bytes
    agent_id = derive_h013_agent_id(public_key)
    payload = _beacon_signing_payload(
        agent_id=agent_id,
        agent_public_key=public_key,
        epoch=normalized_epoch,
        lambda_local=normalized_lambda,
        noise_sigma=normalized_noise,
    )
    signature = signing_keypair.private_key.sign(payload)
    return SpectralBeacon(
        epoch=normalized_epoch,
        lambda_local=normalized_lambda,
        noise_sigma=normalized_noise,
        agent_id=agent_id,
        agent_public_key=public_key,
        agent_signature=signature,
    )


def public_key_from_bytes(public_key: bytes) -> x25519.X25519PublicKey:
    if not isinstance(public_key, bytes) or len(public_key) != X25519_PUBLIC_KEY_SIZE:
        raise SpectralBeaconValidationError(
            "h013_public_key_invalid",
            "x25519_public_key_must_be_32_bytes",
        )
    try:
        return x25519.X25519PublicKey.from_public_bytes(public_key)
    except ValueError as exc:
        raise SpectralBeaconValidationError(
            "h013_public_key_invalid",
            "x25519_public_key_invalid",
        ) from exc


def build_sealed_spectral_beacon(
    *,
    beacon: SpectralBeacon,
    relay_peer_id: str,
    relay_public_key: bytes,
    terminal_peer_id: str,
    terminal_public_key: bytes,
    channel_id: str,
    emission_id: str | None = None,
) -> SealedSpectralBeaconEnvelope:
    """Build a fixed-size one-relay sealed spectral beacon envelope."""

    normalized_relay = validate_d2d_peer_id(relay_peer_id)
    normalized_terminal = validate_d2d_peer_id(terminal_peer_id)
    normalized_channel = str(validate_d2d_channel(channel_id))
    normalized_emission_id = _normalize_emission_id(emission_id or secrets.token_urlsafe(24))
    normalized_beacon = _normalize_beacon(beacon)

    inner_plaintext = _pack_fixed_json(
        {
            "emission_id": normalized_emission_id,
            "terminal_peer_id": normalized_terminal,
            "beacon": normalized_beacon,
        },
        INNER_PLAINTEXT_SIZE,
        "h013_inner_payload_too_large",
    )
    sealed_inner = _seal_for_recipient(
        plaintext=inner_plaintext,
        recipient_public_key=public_key_from_bytes(terminal_public_key),
        aad=_layer_aad("inner", normalized_channel, normalized_emission_id),
    )
    if len(sealed_inner) != INNER_ENVELOPE_SIZE:
        raise SpectralBeaconValidationError(
            "h013_inner_envelope_size_invariant_failed",
            "inner_envelope_size_invariant_failed",
        )

    outer_plaintext = _pack_fixed_json(
        {
            "emission_id": normalized_emission_id,
            "next_hop_peer_id": normalized_terminal,
            "sealed_inner_b64": base64.b64encode(sealed_inner).decode("ascii"),
        },
        OUTER_PLAINTEXT_SIZE,
        "h013_outer_payload_too_large",
    )
    sealed_outer = _seal_for_recipient(
        plaintext=outer_plaintext,
        recipient_public_key=public_key_from_bytes(relay_public_key),
        aad=_layer_aad("outer", normalized_channel, normalized_emission_id),
    )
    if len(sealed_outer) != OUTER_ENVELOPE_SIZE:
        raise SpectralBeaconValidationError(
            "h013_outer_envelope_size_invariant_failed",
            "outer_envelope_size_invariant_failed",
        )

    return SealedSpectralBeaconEnvelope(
        relay_peer_id=normalized_relay,
        channel_id=normalized_channel,
        emission_id=normalized_emission_id,
        sealed_outer=sealed_outer,
    )


def peel_relay_layer(
    envelope: SealedSpectralBeaconEnvelope,
    relay_private_key: x25519.X25519PrivateKey,
) -> RelayPeelResult:
    """Peel the outer layer. The relay learns only next hop plus inner bytes."""

    if len(envelope.sealed_outer) != OUTER_ENVELOPE_SIZE:
        raise SpectralBeaconValidationError(
            "h013_outer_envelope_size_invalid",
            "outer_envelope_size_invalid",
        )
    plaintext = _open_from_recipient(
        envelope_bytes=envelope.sealed_outer,
        recipient_private_key=relay_private_key,
        aad=_layer_aad("outer", envelope.channel_id, envelope.emission_id),
    )
    decoded = _unpack_fixed_json(plaintext, "h013_outer_payload_invalid")
    decoded_emission_id = _normalize_emission_id(decoded.get("emission_id"))
    if decoded_emission_id != envelope.emission_id:
        raise SpectralBeaconValidationError(
            "h013_outer_emission_id_mismatch",
            "outer_emission_id_mismatch",
        )
    next_hop = validate_d2d_peer_id(decoded.get("next_hop_peer_id"))
    try:
        sealed_inner = base64.b64decode(
            _require_str(decoded.get("sealed_inner_b64"), "h013_inner_missing"),
            validate=True,
        )
    except (binascii.Error, ValueError) as exc:
        raise SpectralBeaconValidationError(
            "h013_inner_base64_invalid",
            "inner_base64_invalid",
        ) from exc
    if len(sealed_inner) != INNER_ENVELOPE_SIZE:
        raise SpectralBeaconValidationError(
            "h013_inner_envelope_size_invalid",
            "inner_envelope_size_invalid",
        )
    return RelayPeelResult(
        next_hop_peer_id=next_hop,
        channel_id=envelope.channel_id,
        emission_id=envelope.emission_id,
        sealed_inner=sealed_inner,
    )


def open_terminal_layer(
    relay_result: RelayPeelResult,
    terminal_private_key: x25519.X25519PrivateKey,
    *,
    replay_cache: SpectralBeaconReplayCache,
) -> TerminalOpenResult:
    """Open the terminal layer and reconstruct the spectral beacon."""

    if not isinstance(replay_cache, SpectralBeaconReplayCache):
        raise SpectralBeaconValidationError(
            "h013_replay_cache_invalid",
            "replay_cache_invalid",
        )
    if len(relay_result.sealed_inner) != INNER_ENVELOPE_SIZE:
        raise SpectralBeaconValidationError(
            "h013_inner_envelope_size_invalid",
            "inner_envelope_size_invalid",
        )
    plaintext = _open_from_recipient(
        envelope_bytes=relay_result.sealed_inner,
        recipient_private_key=terminal_private_key,
        aad=_layer_aad("inner", relay_result.channel_id, relay_result.emission_id),
    )
    decoded = _unpack_fixed_json(plaintext, "h013_inner_payload_invalid")
    decoded_emission_id = _normalize_emission_id(decoded.get("emission_id"))
    if decoded_emission_id != relay_result.emission_id:
        raise SpectralBeaconValidationError(
            "h013_inner_emission_id_mismatch",
            "inner_emission_id_mismatch",
        )
    terminal_peer_id = validate_d2d_peer_id(decoded.get("terminal_peer_id"))
    if terminal_peer_id != relay_result.next_hop_peer_id:
        raise SpectralBeaconValidationError(
            "h013_terminal_peer_mismatch",
            "terminal_peer_mismatch",
        )
    beacon = _beacon_from_mapping(decoded.get("beacon"))
    # Key replay cache by (emission_id, beacon.epoch): a beacon from a prior
    # epoch cannot replay in the current epoch even if the LRU entry was evicted.
    replay_cache.check_and_store(relay_result.emission_id, beacon.epoch)
    return TerminalOpenResult(
        terminal_peer_id=terminal_peer_id,
        channel_id=relay_result.channel_id,
        emission_id=relay_result.emission_id,
        beacon=beacon,
    )


def build_h013_gossip_envelope(
    *,
    sealed_envelope: SealedSpectralBeaconEnvelope,
    payload_cid: str,
    transport_headers: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Wrap sealed-beacon metadata in the existing D2d gossip envelope shape."""

    normalized_headers = _sanitize_h013_transport_headers(transport_headers or {})
    headers = {
        "schema_ref": H013_SEALED_SPECTRAL_BEACON_VERSION,
        "topic": "spectral.beacon.sealed",
        "h013_emission_id": sealed_envelope.emission_id,
    }
    headers.update(normalized_headers)
    return build_transport_envelope(
        message_id=sealed_envelope.emission_id,
        payload_cid=payload_cid,
        channel_id=sealed_envelope.channel_id,
        sender_peer_id=sealed_envelope.relay_peer_id,
        transport_headers=headers,
    )


def _seal_for_recipient(
    *,
    plaintext: bytes,
    recipient_public_key: x25519.X25519PublicKey,
    aad: bytes,
) -> bytes:
    ephemeral_private = x25519.X25519PrivateKey.generate()
    ephemeral_public = ephemeral_private.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )
    try:
        shared_secret = ephemeral_private.exchange(recipient_public_key)
    except ValueError as exc:
        raise SpectralBeaconValidationError(
            "h013_key_exchange_failed",
            "x25519_key_exchange_failed",
        ) from exc
    key = _derive_layer_key(shared_secret, aad)
    nonce = secrets.token_bytes(CHACHA20POLY1305_NONCE_SIZE)
    ciphertext = ChaCha20Poly1305(key).encrypt(nonce, plaintext, aad)
    return ephemeral_public + nonce + ciphertext


def _open_from_recipient(
    *,
    envelope_bytes: bytes,
    recipient_private_key: x25519.X25519PrivateKey,
    aad: bytes,
) -> bytes:
    if len(envelope_bytes) < X25519_PUBLIC_KEY_SIZE + CHACHA20POLY1305_NONCE_SIZE + CHACHA20POLY1305_TAG_SIZE:
        raise SpectralBeaconValidationError(
            "h013_envelope_too_short",
            "sealed_envelope_too_short",
        )
    try:
        ephemeral_public = x25519.X25519PublicKey.from_public_bytes(envelope_bytes[:X25519_PUBLIC_KEY_SIZE])
    except ValueError as exc:
        raise SpectralBeaconValidationError(
            "h013_ephemeral_public_key_invalid",
            "ephemeral_public_key_invalid",
        ) from exc
    nonce_start = X25519_PUBLIC_KEY_SIZE
    nonce_end = nonce_start + CHACHA20POLY1305_NONCE_SIZE
    nonce = envelope_bytes[nonce_start:nonce_end]
    ciphertext = envelope_bytes[nonce_end:]
    try:
        shared_secret = recipient_private_key.exchange(ephemeral_public)
    except ValueError as exc:
        raise SpectralBeaconValidationError(
            "h013_key_exchange_failed",
            "x25519_key_exchange_failed",
        ) from exc
    key = _derive_layer_key(shared_secret, aad)
    try:
        return ChaCha20Poly1305(key).decrypt(nonce, ciphertext, aad)
    except InvalidTag as exc:
        raise SpectralBeaconValidationError(
            "h013_decryption_failed",
            "sealed_envelope_decryption_failed",
        ) from exc


def _derive_layer_key(shared_secret: bytes, aad: bytes) -> bytes:
    return HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=None,
        info=b"ILC-H013-SEALED-SPECTRAL-BEACON:" + aad,
    ).derive(shared_secret)


def _layer_aad(layer: str, channel_id: str, emission_id: str) -> bytes:
    return f"{H013_SEALED_SPECTRAL_BEACON_VERSION}:{layer}:{channel_id}:{emission_id}".encode("utf-8")


def _pack_fixed_json(value: Mapping[str, Any], size: int, token: str) -> bytes:
    payload = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    if len(payload) > size - 4:
        raise SpectralBeaconValidationError(token, f"payload_too_large:{len(payload)}>{size - 4}")
    return len(payload).to_bytes(4, "big") + payload + b"\x00" * (size - 4 - len(payload))


def _unpack_fixed_json(value: bytes, token: str) -> dict[str, Any]:
    if len(value) < 4:
        raise SpectralBeaconValidationError(token, "fixed_payload_too_short")
    payload_len = int.from_bytes(value[:4], "big")
    if payload_len > len(value) - 4:
        raise SpectralBeaconValidationError(token, "fixed_payload_length_invalid")
    padding = value[4 + payload_len:]
    if any(padding):
        raise SpectralBeaconValidationError(token, "fixed_payload_padding_invalid")
    try:
        decoded = json.loads(value[4:4 + payload_len].decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise SpectralBeaconValidationError(token, "fixed_payload_json_invalid") from exc
    if not isinstance(decoded, dict):
        raise SpectralBeaconValidationError(token, "fixed_payload_not_object")
    return decoded


def _normalize_beacon(beacon: SpectralBeacon) -> dict[str, Any]:
    if not isinstance(beacon, SpectralBeacon):
        raise SpectralBeaconValidationError("h013_beacon_invalid", "beacon_invalid")
    normalized_epoch = _normalize_epoch(beacon.epoch)
    normalized_lambda = _normalize_lambda_local(beacon.lambda_local)
    normalized_noise = _normalize_noise_sigma(beacon.noise_sigma)
    public_key = _normalize_agent_public_key(beacon.agent_public_key)
    signature = _normalize_agent_signature(beacon.agent_signature)
    agent_id = _require_str(beacon.agent_id, "h013_agent_id_invalid")
    if len(agent_id.encode("utf-8")) > MAX_AGENT_ID_BYTES:
        raise SpectralBeaconValidationError("h013_agent_id_too_large", "agent_id_too_large")
    expected_agent_id = derive_h013_agent_id(public_key)
    if agent_id != expected_agent_id:
        raise SpectralBeaconValidationError(
            "h013_agent_id_key_mismatch",
            "agent_id_key_mismatch",
        )
    payload = _beacon_signing_payload(
        agent_id=agent_id,
        agent_public_key=public_key,
        epoch=normalized_epoch,
        lambda_local=normalized_lambda,
        noise_sigma=normalized_noise,
    )
    try:
        ed25519.Ed25519PublicKey.from_public_bytes(public_key).verify(signature, payload)
    except InvalidSignature as exc:
        raise SpectralBeaconValidationError(
            "h013_agent_signature_invalid",
            "agent_signature_invalid",
        ) from exc
    return {
        "agent_id": agent_id,
        "agent_public_key_b64": base64.b64encode(public_key).decode("ascii"),
        "agent_signature_b64": base64.b64encode(signature).decode("ascii"),
        "epoch": normalized_epoch,
        "lambda_local": normalized_lambda,
        "noise_sigma": normalized_noise,
    }


def _beacon_from_mapping(value: Any) -> SpectralBeacon:
    if not isinstance(value, dict):
        raise SpectralBeaconValidationError("h013_beacon_payload_invalid", "beacon_payload_invalid")
    try:
        candidate = SpectralBeacon(
            epoch=value["epoch"],
            lambda_local=value["lambda_local"],
            noise_sigma=value["noise_sigma"],
            agent_id=value["agent_id"],
            agent_public_key=_b64decode_str(value.get("agent_public_key_b64"), "h013_agent_public_key_invalid"),
            agent_signature=_b64decode_str(value.get("agent_signature_b64"), "h013_agent_signature_invalid"),
        )
    except KeyError as exc:
        raise SpectralBeaconValidationError(
            "h013_beacon_payload_invalid",
            f"beacon_payload_missing:{exc.args[0]}",
        ) from exc
    normalized = _normalize_beacon(candidate)
    return SpectralBeacon(
        epoch=normalized["epoch"],
        lambda_local=normalized["lambda_local"],
        noise_sigma=normalized["noise_sigma"],
        agent_id=normalized["agent_id"],
        agent_public_key=_b64decode_str(normalized["agent_public_key_b64"], "h013_agent_public_key_invalid"),
        agent_signature=_b64decode_str(normalized["agent_signature_b64"], "h013_agent_signature_invalid"),
    )


def _require_str(value: Any, token: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise SpectralBeaconValidationError(token, token)
    return value.strip()


def _normalize_epoch(value: Any) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise SpectralBeaconValidationError("h013_epoch_invalid", "epoch_invalid")
    return value


def _normalize_lambda_local(value: Any) -> list[float]:
    if not isinstance(value, list) or not value:
        raise SpectralBeaconValidationError("h013_lambda_local_invalid", "lambda_local_invalid")
    if len(value) > MAX_LAMBDA_VALUES:
        raise SpectralBeaconValidationError("h013_lambda_local_too_large", "lambda_local_too_large")
    normalized: list[float] = []
    for raw in value:
        if (
            not isinstance(raw, (float, int))
            or isinstance(raw, bool)
            or not math.isfinite(float(raw))
        ):
            raise SpectralBeaconValidationError("h013_lambda_local_non_finite", "lambda_local_non_finite")
        candidate = float(raw)
        if candidate < 0.0 or candidate > MAX_NORMALIZED_LAPLACIAN_EIGENVALUE:
            raise SpectralBeaconValidationError("h013_lambda_local_out_of_range", "lambda_local_out_of_range")
        normalized.append(candidate)
    return normalized


def _normalize_noise_sigma(value: Any) -> float:
    if (
        not isinstance(value, (float, int))
        or isinstance(value, bool)
        or not math.isfinite(float(value))
    ):
        raise SpectralBeaconValidationError("h013_noise_sigma_invalid", "noise_sigma_invalid")
    normalized = float(value)
    if normalized < MIN_NOISE_SIGMA:
        raise SpectralBeaconValidationError("h013_noise_sigma_below_floor", "noise_sigma_below_floor")
    return normalized


def _normalize_emission_id(value: Any) -> str:
    emission_id = _require_str(value, "h013_emission_id_invalid")
    if len(emission_id.encode("utf-8")) > MAX_EMISSION_ID_BYTES:
        raise SpectralBeaconValidationError("h013_emission_id_too_large", "emission_id_too_large")
    if not re.fullmatch(r"[A-Za-z0-9._:-]+", emission_id):
        raise SpectralBeaconValidationError("h013_emission_id_invalid", "emission_id_shape_invalid")
    return emission_id


def _normalize_agent_public_key(value: Any) -> bytes:
    if not isinstance(value, bytes) or len(value) != ED25519_PUBLIC_KEY_SIZE:
        raise SpectralBeaconValidationError(
            "h013_agent_public_key_invalid",
            "ed25519_public_key_must_be_32_bytes",
        )
    try:
        ed25519.Ed25519PublicKey.from_public_bytes(value)
    except ValueError as exc:
        raise SpectralBeaconValidationError(
            "h013_agent_public_key_invalid",
            "ed25519_public_key_invalid",
        ) from exc
    return value


def _normalize_agent_signature(value: Any) -> bytes:
    if not isinstance(value, bytes) or len(value) != ED25519_SIGNATURE_SIZE:
        raise SpectralBeaconValidationError(
            "h013_agent_signature_invalid",
            "ed25519_signature_must_be_64_bytes",
        )
    return value


def _beacon_signing_payload(
    *,
    agent_id: str,
    agent_public_key: bytes,
    epoch: int,
    lambda_local: list[float],
    noise_sigma: float,
) -> bytes:
    return json.dumps(
        {
            "agent_id": agent_id,
            "agent_public_key_b64": base64.b64encode(agent_public_key).decode("ascii"),
            "epoch": epoch,
            "lambda_local": lambda_local,
            "noise_sigma": noise_sigma,
            "version": H013_SEALED_SPECTRAL_BEACON_VERSION,
        },
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def _b64decode_str(value: Any, token: str) -> bytes:
    try:
        return base64.b64decode(_require_str(value, token), validate=True)
    except (binascii.Error, ValueError) as exc:
        raise SpectralBeaconValidationError(token, "base64_invalid") from exc


def _canonical_header_alias(value: str) -> str:
    return re.sub(r"[-.]", "_", value.lower())


def _sanitize_h013_transport_headers(headers: Mapping[str, Any]) -> dict[str, str]:
    if not isinstance(headers, Mapping):
        raise SpectralBeaconValidationError(
            "h013_transport_headers_not_mapping",
            "transport_headers_not_mapping",
        )
    forbidden_aliases = {
        "agent_id",
        "creator_agent_id",
        "h013_emission_id",
        "source_agent_id",
        "sender_peer_id",
        "schema_ref",
        "origin_peer_id",
        "lambda_local",
        "noise_sigma",
        "raw_spectral_coordinates",
        "route_history",
        "cluster_membership",
        "cluster_members",
        "topic",
    }
    normalized: dict[str, str] = {}
    for raw_key, raw_value in headers.items():
        key = _require_str(raw_key, "h013_transport_header_key_invalid")
        alias = _canonical_header_alias(key)
        if alias in forbidden_aliases:
            raise SpectralBeaconValidationError(
                "h013_transport_header_forbidden",
                f"transport_header_forbidden:{alias}",
            )
        key_lower = key.lower()
        if key_lower in normalized:
            raise SpectralBeaconValidationError(
                "h013_transport_header_key_collision",
                f"transport_header_key_collision:{key_lower}",
            )
        normalized[key_lower] = _require_str(raw_value, "h013_transport_header_value_invalid")
    return {key: normalized[key] for key in sorted(normalized)}
