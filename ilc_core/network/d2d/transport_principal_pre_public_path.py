# SPDX-License-Identifier: AGPL-3.0-only
"""Phase 1267 TransportPrincipal pre-public runtime identity helpers.

This module does not activate public P2P or non-loopback sidecar/projection
serving. It gives later public-path work a deterministic, authenticated
transport-credential key source that is not JSON `requester_id`, AgentID, or
client IP fallback identity.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any, Collection, Mapping


TRANSPORT_PRINCIPAL_PRE_PUBLIC_PATH_VERSION = (
    "transport_principal_runtime_identity_pre_public_path_phase_1267.v0.1"
)
TRANSPORT_PRINCIPAL_NOT_PUBLIC_P2P_TOKEN = (
    "transport_principal_runtime_not_public_p2p_activation_phase_1267"
)
REQUESTER_ID_RATE_LIMIT_FALLBACK_FORBIDDEN_TOKEN = (
    "requester_id_rate_limit_fallback_still_forbidden_phase_1267"
)
NON_LOOPBACK_PROJECTION_STILL_BLOCKED_TOKEN = (
    "non_loopback_projection_still_blocked_phase_1267"
)

_ALLOWED_CREDENTIAL_KINDS = frozenset(
    {
        "mtls_certificate_fingerprint",
        "quic_peer_credential",
        "rustls_peer_certificate_chain_hash",
        "signed_transport_handshake",
        "transport_credential",
    }
)
_FORBIDDEN_IDENTITY_FALLBACK_KINDS = frozenset(
    {
        "agent_id",
        "agentid",
        "client_ip",
        "harness_identity",
        "ip_address",
        "json_body_requester_id",
        "requester_id",
    }
)
_FORBIDDEN_MATERIAL_PREFIXES = tuple(
    prefix.encode("utf-8")
    for prefix in (
        "agent_id:",
        "agentid:",
        "client_ip:",
        "harness_identity:",
        "ip_address:",
        "json_body_requester_id:",
        "requester_id:",
    )
)
_MAX_CREDENTIAL_MATERIAL_BYTES = 4096
_MAX_HANDSHAKE_NONCE_BYTES = 512
_HEX_DIGEST_LENGTH = 64


@dataclass(frozen=True)
class TransportPrincipalContext:
    version: str
    scope: str
    credential_kind: str
    credential_fingerprint: str
    principal_id: str
    issued_epoch: int
    expires_epoch: int
    current_epoch: int
    handshake_nonce_fingerprint: str
    rate_limit_key: str
    admission_key: str
    ban_key: str
    replay_key: str
    public_p2p_enabled: bool
    non_loopback_projection_enabled: bool
    requester_id_fallback_allowed: bool
    agent_id_rate_limit_key_allowed: bool
    client_ip_rate_limit_key_allowed: bool
    tokens: tuple[str, ...]


def _require_epoch(name: str, value: Any) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise ValueError(f"transport_principal_{name}_epoch_invalid")
    return value


def _require_flag_false(name: str, value: Any, token: str) -> bool:
    if value is not False:
        raise ValueError(token)
    return False


def _normalize_credential_kind(value: Any) -> str:
    if not isinstance(value, str):
        raise ValueError("transport_principal_credential_kind_invalid")
    normalized = value.strip().lower()
    if normalized in _FORBIDDEN_IDENTITY_FALLBACK_KINDS:
        raise ValueError("transport_principal_forbidden_identity_fallback")
    if normalized not in _ALLOWED_CREDENTIAL_KINDS:
        raise ValueError("transport_principal_credential_kind_unsupported")
    return normalized


def _as_bounded_bytes(name: str, value: Any, max_bytes: int) -> bytes:
    if isinstance(value, str):
        raw = value.encode("utf-8")
    elif isinstance(value, bytes):
        raw = value
    else:
        raise ValueError(f"transport_principal_{name}_invalid")
    if not raw:
        raise ValueError(f"transport_principal_{name}_empty")
    if len(raw) > max_bytes:
        raise ValueError(f"transport_principal_{name}_too_large")
    return raw


def _reject_disguised_fallback_material(raw: bytes) -> None:
    normalized_prefix = raw[:128].strip().lower()
    if normalized_prefix.startswith(_FORBIDDEN_MATERIAL_PREFIXES):
        raise ValueError("transport_principal_forbidden_identity_fallback")


def _digest(*parts: bytes) -> str:
    digest = hashlib.sha256()
    for part in parts:
        digest.update(len(part).to_bytes(8, byteorder="big", signed=False))
        digest.update(part)
    return digest.hexdigest()


def _derive_key(prefix: str, purpose: str, credential_fingerprint: str) -> str:
    return f"{prefix}:{_digest(purpose.encode('utf-8'), credential_fingerprint.encode('utf-8'))}"


def _context_to_dict(context: TransportPrincipalContext) -> dict[str, Any]:
    return {
        "admission_key": context.admission_key,
        "agent_id_rate_limit_key_allowed": context.agent_id_rate_limit_key_allowed,
        "ban_key": context.ban_key,
        "client_ip_rate_limit_key_allowed": context.client_ip_rate_limit_key_allowed,
        "credential_fingerprint": context.credential_fingerprint,
        "credential_kind": context.credential_kind,
        "current_epoch": context.current_epoch,
        "expires_epoch": context.expires_epoch,
        "handshake_nonce_fingerprint": context.handshake_nonce_fingerprint,
        "issued_epoch": context.issued_epoch,
        "non_loopback_projection_enabled": context.non_loopback_projection_enabled,
        "principal_id": context.principal_id,
        "public_p2p_enabled": context.public_p2p_enabled,
        "rate_limit_key": context.rate_limit_key,
        "replay_key": context.replay_key,
        "requester_id_fallback_allowed": context.requester_id_fallback_allowed,
        "scope": context.scope,
        "tokens": list(context.tokens),
        "version": context.version,
    }


def _require_hex_digest(name: str, value: Any) -> str:
    if (
        not isinstance(value, str)
        or len(value) != _HEX_DIGEST_LENGTH
        or any(char not in "0123456789abcdef" for char in value)
    ):
        raise ValueError(f"transport_principal_{name}_invalid")
    return value


def _require_prefixed_digest(name: str, value: Any, prefix: str) -> str:
    expected_prefix = f"{prefix}:"
    if not isinstance(value, str) or not value.startswith(expected_prefix):
        raise ValueError(f"transport_principal_{name}_invalid")
    _require_hex_digest(name, value[len(expected_prefix):])
    return value


def _reject_float_values(value: Any) -> None:
    if isinstance(value, float):
        raise ValueError("transport_principal_float_values_forbidden")
    if isinstance(value, Mapping):
        for key, item in value.items():
            if isinstance(key, float):
                raise ValueError("transport_principal_float_values_forbidden")
            _reject_float_values(item)
        return
    if isinstance(value, (list, tuple)):
        for item in value:
            _reject_float_values(item)


def build_transport_principal_context(
    *,
    credential_kind: str,
    credential_material: bytes | str,
    handshake_nonce: bytes | str,
    issued_epoch: int,
    expires_epoch: int,
    current_epoch: int,
    public_p2p_enabled: bool = False,
    non_loopback_projection_enabled: bool = False,
    revoked_credential_fingerprints: Collection[str] = (),
    replay_cache: Collection[str] = (),
) -> dict[str, Any]:
    """Build a deterministic pre-public TransportPrincipal context.

    The credential material is assumed to come from an already authenticated
    transport handshake. This helper deliberately refuses caller-provided JSON
    identity, AgentID, harness identity, or client IP fallback material.
    """

    normalized_kind = _normalize_credential_kind(credential_kind)
    material = _as_bounded_bytes(
        "credential_material",
        credential_material,
        _MAX_CREDENTIAL_MATERIAL_BYTES,
    )
    _reject_disguised_fallback_material(material)
    nonce = _as_bounded_bytes("handshake_nonce", handshake_nonce, _MAX_HANDSHAKE_NONCE_BYTES)
    issued = _require_epoch("issued", issued_epoch)
    expires = _require_epoch("expires", expires_epoch)
    current = _require_epoch("current", current_epoch)
    if issued > current or current > expires:
        raise ValueError("transport_principal_epoch_window_invalid")
    _require_flag_false(
        "public_p2p_enabled",
        public_p2p_enabled,
        TRANSPORT_PRINCIPAL_NOT_PUBLIC_P2P_TOKEN,
    )
    _require_flag_false(
        "non_loopback_projection_enabled",
        non_loopback_projection_enabled,
        NON_LOOPBACK_PROJECTION_STILL_BLOCKED_TOKEN,
    )

    kind_bytes = normalized_kind.encode("utf-8")
    credential_fingerprint = _digest(b"credential", kind_bytes, material)
    nonce_fingerprint = _digest(b"handshake_nonce", nonce)
    context = TransportPrincipalContext(
        version=TRANSPORT_PRINCIPAL_PRE_PUBLIC_PATH_VERSION,
        scope="pre_public_path",
        credential_kind=normalized_kind,
        credential_fingerprint=credential_fingerprint,
        principal_id=f"tp:{_digest(b'principal', kind_bytes, material)}",
        issued_epoch=issued,
        expires_epoch=expires,
        current_epoch=current,
        handshake_nonce_fingerprint=nonce_fingerprint,
        rate_limit_key=_derive_key("tp_rate", "rate_limit", credential_fingerprint),
        admission_key=_derive_key("tp_admission", "admission", credential_fingerprint),
        ban_key=_derive_key("tp_ban", "ban", credential_fingerprint),
        replay_key=f"tp_replay:{_digest(b'replay', credential_fingerprint.encode('utf-8'), nonce_fingerprint.encode('utf-8'))}",
        public_p2p_enabled=False,
        non_loopback_projection_enabled=False,
        requester_id_fallback_allowed=False,
        agent_id_rate_limit_key_allowed=False,
        client_ip_rate_limit_key_allowed=False,
        tokens=(
            TRANSPORT_PRINCIPAL_PRE_PUBLIC_PATH_VERSION,
            TRANSPORT_PRINCIPAL_NOT_PUBLIC_P2P_TOKEN,
            REQUESTER_ID_RATE_LIMIT_FALLBACK_FORBIDDEN_TOKEN,
            NON_LOOPBACK_PROJECTION_STILL_BLOCKED_TOKEN,
        ),
    )
    return validate_transport_principal_context(
        _context_to_dict(context),
        current_epoch=current,
        revoked_credential_fingerprints=revoked_credential_fingerprints,
        replay_cache=replay_cache,
    )


def validate_transport_principal_context(
    context: Mapping[str, Any],
    *,
    current_epoch: int,
    revoked_credential_fingerprints: Collection[str] = (),
    replay_cache: Collection[str] = (),
) -> dict[str, Any]:
    """Validate a pre-public TransportPrincipal context without side effects."""

    if not isinstance(context, Mapping):
        raise ValueError("transport_principal_context_invalid")
    current = _require_epoch("current", current_epoch)
    if context.get("version") != TRANSPORT_PRINCIPAL_PRE_PUBLIC_PATH_VERSION:
        raise ValueError("transport_principal_context_version_invalid")
    if context.get("scope") != "pre_public_path":
        raise ValueError("transport_principal_context_scope_invalid")

    normalized_kind = _normalize_credential_kind(context.get("credential_kind"))
    credential_fingerprint = _require_hex_digest(
        "credential_fingerprint",
        context.get("credential_fingerprint"),
    )
    principal_id = _require_prefixed_digest("principal_id", context.get("principal_id"), "tp")
    nonce_fingerprint = _require_hex_digest(
        "handshake_nonce_fingerprint",
        context.get("handshake_nonce_fingerprint"),
    )
    issued = _require_epoch("issued", context.get("issued_epoch"))
    expires = _require_epoch("expires", context.get("expires_epoch"))
    embedded_current = _require_epoch("current", context.get("current_epoch"))
    if embedded_current != current:
        raise ValueError("transport_principal_current_epoch_mismatch")
    if issued > current or current > expires:
        raise ValueError("transport_principal_epoch_window_invalid")

    rate_limit_key = _require_prefixed_digest(
        "rate_limit_key",
        context.get("rate_limit_key"),
        "tp_rate",
    )
    admission_key = _require_prefixed_digest(
        "admission_key",
        context.get("admission_key"),
        "tp_admission",
    )
    ban_key = _require_prefixed_digest("ban_key", context.get("ban_key"), "tp_ban")
    replay_key = _require_prefixed_digest(
        "replay_key",
        context.get("replay_key"),
        "tp_replay",
    )
    _require_flag_false(
        "public_p2p_enabled",
        context.get("public_p2p_enabled"),
        TRANSPORT_PRINCIPAL_NOT_PUBLIC_P2P_TOKEN,
    )
    _require_flag_false(
        "non_loopback_projection_enabled",
        context.get("non_loopback_projection_enabled"),
        NON_LOOPBACK_PROJECTION_STILL_BLOCKED_TOKEN,
    )
    _require_flag_false(
        "requester_id_fallback_allowed",
        context.get("requester_id_fallback_allowed"),
        REQUESTER_ID_RATE_LIMIT_FALLBACK_FORBIDDEN_TOKEN,
    )
    _require_flag_false(
        "agent_id_rate_limit_key_allowed",
        context.get("agent_id_rate_limit_key_allowed"),
        "transport_principal_agent_id_rate_limit_key_forbidden",
    )
    _require_flag_false(
        "client_ip_rate_limit_key_allowed",
        context.get("client_ip_rate_limit_key_allowed"),
        "transport_principal_client_ip_rate_limit_key_forbidden",
    )
    if credential_fingerprint in revoked_credential_fingerprints or principal_id in revoked_credential_fingerprints:
        raise ValueError("transport_principal_revoked")
    if replay_key in replay_cache:
        raise ValueError("transport_principal_replay_detected")

    tokens = context.get("tokens")
    if not isinstance(tokens, list) or not all(isinstance(token, str) for token in tokens):
        raise ValueError("transport_principal_tokens_invalid")
    required_tokens = {
        TRANSPORT_PRINCIPAL_PRE_PUBLIC_PATH_VERSION,
        TRANSPORT_PRINCIPAL_NOT_PUBLIC_P2P_TOKEN,
        REQUESTER_ID_RATE_LIMIT_FALLBACK_FORBIDDEN_TOKEN,
        NON_LOOPBACK_PROJECTION_STILL_BLOCKED_TOKEN,
    }
    if not required_tokens.issubset(set(tokens)):
        raise ValueError("transport_principal_required_tokens_missing")

    validated = {
        "admission_key": admission_key,
        "agent_id_rate_limit_key_allowed": False,
        "ban_key": ban_key,
        "client_ip_rate_limit_key_allowed": False,
        "credential_fingerprint": credential_fingerprint,
        "credential_kind": normalized_kind,
        "current_epoch": current,
        "expires_epoch": expires,
        "handshake_nonce_fingerprint": nonce_fingerprint,
        "issued_epoch": issued,
        "non_loopback_projection_enabled": False,
        "principal_id": principal_id,
        "public_p2p_enabled": False,
        "rate_limit_key": rate_limit_key,
        "replay_key": replay_key,
        "requester_id_fallback_allowed": False,
        "scope": "pre_public_path",
        "tokens": sorted(required_tokens),
        "version": TRANSPORT_PRINCIPAL_PRE_PUBLIC_PATH_VERSION,
    }
    _reject_float_values(validated)
    return validated


def export_transport_principal_context_json(context: Mapping[str, Any]) -> str:
    """Export a TransportPrincipal context as canonical JSON."""

    if not isinstance(context, Mapping):
        raise ValueError("transport_principal_context_invalid")
    current_epoch = _require_epoch("current", context.get("current_epoch"))
    validated = validate_transport_principal_context(context, current_epoch=current_epoch)
    _reject_float_values(validated)
    return json.dumps(
        validated,
        sort_keys=True,
        allow_nan=False,
        separators=(",", ":"),
    )
