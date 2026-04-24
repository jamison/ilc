"""H-013 sealed spectral beacon construction.

This module implements the bounded one-relay sealed-sender payload from
ADR-0034. It performs no network I/O and does not activate D2d gossip in
production. Callers may wrap the returned payload in the existing CDL-060/061
gossip envelope surface.
"""

from __future__ import annotations

import base64
from dataclasses import dataclass
import json
import math
import secrets
from typing import Any, List, Mapping

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import x25519
from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

from .gossip import build_transport_envelope
from .interface import validate_d2d_channel, validate_d2d_peer_id


H013_SEALED_SPECTRAL_BEACON_VERSION = "h013_sealed_spectral_beacon.v0.1"
ADR_0034_DEPENDENCY = "run_h013_d2d_sealed_sender_adr_verdict=accepted"

MAX_LAMBDA_VALUES = 32
MAX_AGENT_ID_BYTES = 128
INNER_PLAINTEXT_SIZE = 2048
OUTER_PLAINTEXT_SIZE = 4096
X25519_PUBLIC_KEY_SIZE = 32
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
    sealed_outer: bytes


@dataclass(frozen=True)
class RelayPeelResult:
    """Relay-visible result after peeling one layer."""

    next_hop_peer_id: str
    channel_id: str
    sealed_inner: bytes


@dataclass(frozen=True)
class TerminalOpenResult:
    """Terminal-visible opened spectral beacon."""

    terminal_peer_id: str
    channel_id: str
    beacon: SpectralBeacon


def generate_sealed_sender_keypair() -> SealedSenderKeypair:
    """Generate an X25519 sealed-sender keypair."""

    return SealedSenderKeypair(private_key=x25519.X25519PrivateKey.generate())


def public_key_from_bytes(public_key: bytes) -> x25519.X25519PublicKey:
    if not isinstance(public_key, bytes) or len(public_key) != X25519_PUBLIC_KEY_SIZE:
        raise SpectralBeaconValidationError(
            "h013_public_key_invalid",
            "x25519_public_key_must_be_32_bytes",
        )
    return x25519.X25519PublicKey.from_public_bytes(public_key)


def build_sealed_spectral_beacon(
    *,
    beacon: SpectralBeacon,
    relay_peer_id: str,
    relay_public_key: bytes,
    terminal_peer_id: str,
    terminal_public_key: bytes,
    channel_id: str,
) -> SealedSpectralBeaconEnvelope:
    """Build a fixed-size one-relay sealed spectral beacon envelope."""

    normalized_relay = validate_d2d_peer_id(relay_peer_id)
    normalized_terminal = validate_d2d_peer_id(terminal_peer_id)
    normalized_channel = str(validate_d2d_channel(channel_id))
    normalized_beacon = _normalize_beacon(beacon)

    inner_plaintext = _pack_fixed_json(
        {
            "terminal_peer_id": normalized_terminal,
            "beacon": normalized_beacon,
        },
        INNER_PLAINTEXT_SIZE,
        "h013_inner_payload_too_large",
    )
    sealed_inner = _seal_for_recipient(
        plaintext=inner_plaintext,
        recipient_public_key=public_key_from_bytes(terminal_public_key),
        aad=_layer_aad("inner", normalized_channel),
    )
    if len(sealed_inner) != INNER_ENVELOPE_SIZE:
        raise SpectralBeaconValidationError(
            "h013_inner_envelope_size_invariant_failed",
            "inner_envelope_size_invariant_failed",
        )

    outer_plaintext = _pack_fixed_json(
        {
            "next_hop_peer_id": normalized_terminal,
            "sealed_inner_b64": base64.b64encode(sealed_inner).decode("ascii"),
        },
        OUTER_PLAINTEXT_SIZE,
        "h013_outer_payload_too_large",
    )
    sealed_outer = _seal_for_recipient(
        plaintext=outer_plaintext,
        recipient_public_key=public_key_from_bytes(relay_public_key),
        aad=_layer_aad("outer", normalized_channel),
    )
    if len(sealed_outer) != OUTER_ENVELOPE_SIZE:
        raise SpectralBeaconValidationError(
            "h013_outer_envelope_size_invariant_failed",
            "outer_envelope_size_invariant_failed",
        )

    return SealedSpectralBeaconEnvelope(
        relay_peer_id=normalized_relay,
        channel_id=normalized_channel,
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
        aad=_layer_aad("outer", envelope.channel_id),
    )
    decoded = _unpack_fixed_json(plaintext, "h013_outer_payload_invalid")
    next_hop = validate_d2d_peer_id(decoded.get("next_hop_peer_id"))
    sealed_inner = base64.b64decode(_require_str(decoded.get("sealed_inner_b64"), "h013_inner_missing"))
    if len(sealed_inner) != INNER_ENVELOPE_SIZE:
        raise SpectralBeaconValidationError(
            "h013_inner_envelope_size_invalid",
            "inner_envelope_size_invalid",
        )
    return RelayPeelResult(
        next_hop_peer_id=next_hop,
        channel_id=envelope.channel_id,
        sealed_inner=sealed_inner,
    )


def open_terminal_layer(
    relay_result: RelayPeelResult,
    terminal_private_key: x25519.X25519PrivateKey,
) -> TerminalOpenResult:
    """Open the terminal layer and reconstruct the spectral beacon."""

    if len(relay_result.sealed_inner) != INNER_ENVELOPE_SIZE:
        raise SpectralBeaconValidationError(
            "h013_inner_envelope_size_invalid",
            "inner_envelope_size_invalid",
        )
    plaintext = _open_from_recipient(
        envelope_bytes=relay_result.sealed_inner,
        recipient_private_key=terminal_private_key,
        aad=_layer_aad("inner", relay_result.channel_id),
    )
    decoded = _unpack_fixed_json(plaintext, "h013_inner_payload_invalid")
    terminal_peer_id = validate_d2d_peer_id(decoded.get("terminal_peer_id"))
    if terminal_peer_id != relay_result.next_hop_peer_id:
        raise SpectralBeaconValidationError(
            "h013_terminal_peer_mismatch",
            "terminal_peer_mismatch",
        )
    return TerminalOpenResult(
        terminal_peer_id=terminal_peer_id,
        channel_id=relay_result.channel_id,
        beacon=_beacon_from_mapping(decoded.get("beacon")),
    )


def build_h013_gossip_envelope(
    *,
    sealed_envelope: SealedSpectralBeaconEnvelope,
    message_id: str,
    payload_cid: str,
    sender_peer_id: str,
    transport_headers: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Wrap sealed-beacon metadata in the existing D2d gossip envelope shape."""

    headers = {
        "schema_ref": H013_SEALED_SPECTRAL_BEACON_VERSION,
        "topic": "spectral.beacon.sealed",
    }
    if transport_headers:
        headers.update({str(k): str(v) for k, v in transport_headers.items()})
    return build_transport_envelope(
        message_id=message_id,
        payload_cid=payload_cid,
        channel_id=sealed_envelope.channel_id,
        sender_peer_id=sender_peer_id,
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
    shared_secret = ephemeral_private.exchange(recipient_public_key)
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
    shared_secret = recipient_private_key.exchange(ephemeral_public)
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


def _layer_aad(layer: str, channel_id: str) -> bytes:
    return f"{H013_SEALED_SPECTRAL_BEACON_VERSION}:{layer}:{channel_id}".encode("utf-8")


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
    decoded = json.loads(value[4:4 + payload_len].decode("utf-8"))
    if not isinstance(decoded, dict):
        raise SpectralBeaconValidationError(token, "fixed_payload_not_object")
    return decoded


def _normalize_beacon(beacon: SpectralBeacon) -> dict[str, Any]:
    if not isinstance(beacon.epoch, int) or beacon.epoch < 0:
        raise SpectralBeaconValidationError("h013_epoch_invalid", "epoch_invalid")
    if not isinstance(beacon.lambda_local, list) or not beacon.lambda_local:
        raise SpectralBeaconValidationError("h013_lambda_local_invalid", "lambda_local_invalid")
    if len(beacon.lambda_local) > MAX_LAMBDA_VALUES:
        raise SpectralBeaconValidationError("h013_lambda_local_too_large", "lambda_local_too_large")
    normalized_lambda: list[float] = []
    for value in beacon.lambda_local:
        if not isinstance(value, (float, int)) or not math.isfinite(float(value)):
            raise SpectralBeaconValidationError("h013_lambda_local_non_finite", "lambda_local_non_finite")
        normalized_lambda.append(float(value))
    if not isinstance(beacon.noise_sigma, (float, int)) or not math.isfinite(float(beacon.noise_sigma)):
        raise SpectralBeaconValidationError("h013_noise_sigma_invalid", "noise_sigma_invalid")
    agent_id = _require_str(beacon.agent_id, "h013_agent_id_invalid")
    if len(agent_id.encode("utf-8")) > MAX_AGENT_ID_BYTES:
        raise SpectralBeaconValidationError("h013_agent_id_too_large", "agent_id_too_large")
    return {
        "agent_id": agent_id,
        "epoch": beacon.epoch,
        "lambda_local": normalized_lambda,
        "noise_sigma": float(beacon.noise_sigma),
    }


def _beacon_from_mapping(value: Any) -> SpectralBeacon:
    if not isinstance(value, dict):
        raise SpectralBeaconValidationError("h013_beacon_payload_invalid", "beacon_payload_invalid")
    return SpectralBeacon(
        epoch=value["epoch"],
        lambda_local=[float(v) for v in value["lambda_local"]],
        noise_sigma=float(value["noise_sigma"]),
        agent_id=_require_str(value["agent_id"], "h013_agent_id_invalid"),
    )


def _require_str(value: Any, token: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise SpectralBeaconValidationError(token, token)
    return value.strip()
