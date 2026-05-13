"""Phase 1313 default-off public fetch/P2P readiness candidate.

This module records readiness evidence only. It does not create a server,
listener, socket, public P2P path, public fetch serving path, peer-discovery
path, wallet action, ECU mint, ILC settlement, release artifact, or signing
surface.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from typing import Any

from ilc_core.sidecars.transport_principal_admission import (
    transport_principal_admission_sidecar_manifest,
)


PUBLIC_FETCH_P2P_READINESS_VERSION = (
    "public_fetch_p2p_activation_candidate_default_off_phase_1313.v0.1"
)
RUST_PUBLIC_P2P_SUBSTRATE_GATE_STATUS_RECORDED_TOKEN = (
    "rust_public_p2p_substrate_gate_status_recorded_phase_1313"
)
PUBLIC_P2P_DEFAULT_OFF_TOKEN = "public_p2p_default_off_phase_1313"
PUBLIC_FETCH_SERVING_DEFAULT_OFF_TOKEN = "public_fetch_serving_default_off_phase_1313"
TRANSPORT_PUBLIC_PATH_ACTIVATION_NOT_AUTHORIZED_TOKEN = (
    "transport_public_path_activation_not_authorized_phase_1313"
)
PHASE_1314_NEXT_TOKEN = "phase_1314_wallet_withdrawal_transfer_spend_preflight_next"
PUBLIC_RC_REMAINS_BLOCKED_AFTER_PHASE_1313_TOKEN = (
    "public_rc_remains_blocked_after_phase_1313"
)
RUST_PUBLIC_P2P_SUBSTRATE_GATE_STILL_REQUIRED_PHASE_1313_TOKEN = (
    "rust_public_p2p_substrate_gate_still_required_phase_1313"
)

READINESS_STATE = "public_fetch_p2p_readiness_default_off_phase_1313"
READINESS_REF_PREFIX = "public_fetch_p2p_readiness_candidate_sha256"

_MAX_PAYLOAD_DEPTH = 32
_MAX_PAYLOAD_NODES = 100_000
_MAX_TEXT_LENGTH = 4096
_MAX_CANONICAL_JSON_BYTES = 10_000_000
_MAX_EPOCH = 1_000_000_000_000
_HEX_DIGEST_LENGTH = 64
_HEX = frozenset("0123456789abcdef")
_ALLOWED_RUST_GATE_STATUSES = (
    "gate_required_not_satisfied",
    "gate_ambiguous_human_review_required",
    "adr_integration_gate_satisfied_but_activation_out_of_scope",
)
_FALSE_AUTHORIZATION_FLAGS = (
    "public_p2p_enabled",
    "public_fetch_serving_enabled",
    "transport_public_path_activation_authorized",
    "public_listener_enabled",
    "peer_discovery_enabled",
    "non_loopback_bind_enabled",
    "wildcard_bind_enabled",
    "public_host_bind_enabled",
    "python_http_transport_public_substrate_enabled",
    "public_sidecar_projection_serving_enabled",
    "release_artifact_authorized",
    "cdl088_opened",
)
_READINESS_PACKET_KEYS = frozenset(
    {
        "authorization_flags",
        "candidate_sha256",
        "current_epoch",
        "local_only",
        "python_http_transport_classification",
        "readiness_verdict",
        "required_before_public_activation",
        "rust_public_p2p_substrate_gate",
        "source_evidence",
        "state",
        "tokens",
        "transport_principal_dependency",
        "version",
    }
)
_REQUIRED_BEFORE_PUBLIC_ACTIVATION = (
    "explicit_rust_public_p2p_substrate_adr_integration_gate",
    "transport_principal_public_path_activation_authority",
    "public_fetch_serving_authority",
    "listener_bind_peer_discovery_authority",
    "hostile_network_rate_ban_replay_privacy_policy_activation",
    "release_publication_authority_if_artifact_claimed",
    "separate_human_authorization_after_phase_1313",
)
_SOURCE_EVIDENCE = {
    "cdl087_status": "ratified_public_fetch_serving_still_not_enabled",
    "ilc_consensus_network_rs": "rust_quic_tls_validator_gossip_exists_not_public_d2d_gate",
    "phase_1313_scope": "readiness_only_default_off",
    "python_http_fetch_runtime": "bounded_devnet_test_fetch_runtime_not_public_substrate",
    "python_http_gossip_runtime": "bounded_devnet_test_gossip_runtime_not_public_substrate",
}


class PublicFetchP2PReadinessError(ValueError):
    """Fail-closed Phase 1313 readiness error with a stable token."""

    def __init__(self, token: str, message: str) -> None:
        super().__init__(message)
        self.token = token


def public_fetch_p2p_readiness_required_tokens() -> list[str]:
    return [
        PUBLIC_FETCH_P2P_READINESS_VERSION,
        RUST_PUBLIC_P2P_SUBSTRATE_GATE_STATUS_RECORDED_TOKEN,
        PUBLIC_P2P_DEFAULT_OFF_TOKEN,
        PUBLIC_FETCH_SERVING_DEFAULT_OFF_TOKEN,
        TRANSPORT_PUBLIC_PATH_ACTIVATION_NOT_AUTHORIZED_TOKEN,
        PHASE_1314_NEXT_TOKEN,
        PUBLIC_RC_REMAINS_BLOCKED_AFTER_PHASE_1313_TOKEN,
    ]


def public_fetch_p2p_readiness_candidate_manifest() -> dict[str, Any]:
    """Return deterministic local/package metadata for the readiness candidate."""

    manifest = {
        "activation_candidate_authorized": False,
        "contract_version": PUBLIC_FETCH_P2P_READINESS_VERSION,
        "local_only": True,
        "public_fetch_serving_enabled": False,
        "public_listener_enabled": False,
        "public_p2p_enabled": False,
        "readiness_only": True,
        "rust_public_p2p_substrate_gate_required": True,
        "rust_public_p2p_substrate_gate_token": (
            RUST_PUBLIC_P2P_SUBSTRATE_GATE_STILL_REQUIRED_PHASE_1313_TOKEN
        ),
        "tokens": public_fetch_p2p_readiness_required_tokens(),
        "transport_public_path_activation_authorized": False,
    }
    _reject_unsafe_json_tree(manifest)
    return manifest


def build_public_fetch_p2p_readiness_candidate(
    *,
    current_epoch: int,
    rust_public_p2p_substrate_gate_status: str = "gate_required_not_satisfied",
    rust_network_rs_present: bool = True,
    rust_quic_tls_code_present: bool = True,
    explicit_rust_public_p2p_adr_integration_gate_present: bool = False,
    public_p2p_enabled: bool = False,
    public_fetch_serving_enabled: bool = False,
    transport_public_path_activation_authorized: bool = False,
    public_listener_enabled: bool = False,
    peer_discovery_enabled: bool = False,
    non_loopback_bind_enabled: bool = False,
    wildcard_bind_enabled: bool = False,
    public_host_bind_enabled: bool = False,
    python_http_transport_public_substrate_enabled: bool = False,
    public_sidecar_projection_serving_enabled: bool = False,
    release_artifact_authorized: bool = False,
    cdl088_opened: bool = False,
) -> dict[str, Any]:
    """Build a deterministic default-off public fetch/P2P readiness packet."""

    current = _require_epoch("current", current_epoch)
    rust_status = _require_choice(
        rust_public_p2p_substrate_gate_status,
        allowed=_ALLOWED_RUST_GATE_STATUSES,
        token="public_fetch_p2p_rust_gate_status_invalid_phase_1313",
    )
    _require_bool("rust_network_rs_present", rust_network_rs_present)
    _require_bool("rust_quic_tls_code_present", rust_quic_tls_code_present)
    _require_bool(
        "explicit_rust_public_p2p_adr_integration_gate_present",
        explicit_rust_public_p2p_adr_integration_gate_present,
    )
    if rust_status == "gate_required_not_satisfied":
        if explicit_rust_public_p2p_adr_integration_gate_present:
            raise PublicFetchP2PReadinessError(
                "public_fetch_p2p_rust_gate_status_contradiction_phase_1313",
                "unsatisfied Rust gate status cannot claim an explicit integration gate",
            )
    elif rust_status == "gate_ambiguous_human_review_required":
        if explicit_rust_public_p2p_adr_integration_gate_present:
            raise PublicFetchP2PReadinessError(
                "public_fetch_p2p_rust_gate_status_contradiction_phase_1313",
                "ambiguous Rust gate status cannot claim an explicit integration gate",
            )
    elif rust_status == "adr_integration_gate_satisfied_but_activation_out_of_scope":
        if explicit_rust_public_p2p_adr_integration_gate_present is not True:
            raise PublicFetchP2PReadinessError(
                "public_fetch_p2p_rust_gate_evidence_required_phase_1313",
                "satisfied Rust gate status requires an explicit integration gate marker",
            )

    _require_all_false(
        {
            "public_p2p_enabled": public_p2p_enabled,
            "public_fetch_serving_enabled": public_fetch_serving_enabled,
            "transport_public_path_activation_authorized": (
                transport_public_path_activation_authorized
            ),
            "public_listener_enabled": public_listener_enabled,
            "peer_discovery_enabled": peer_discovery_enabled,
            "non_loopback_bind_enabled": non_loopback_bind_enabled,
            "wildcard_bind_enabled": wildcard_bind_enabled,
            "public_host_bind_enabled": public_host_bind_enabled,
            "python_http_transport_public_substrate_enabled": (
                python_http_transport_public_substrate_enabled
            ),
            "public_sidecar_projection_serving_enabled": (
                public_sidecar_projection_serving_enabled
            ),
            "release_artifact_authorized": release_artifact_authorized,
            "cdl088_opened": cdl088_opened,
        },
        token_by_name={
            "public_p2p_enabled": PUBLIC_P2P_DEFAULT_OFF_TOKEN,
            "public_fetch_serving_enabled": PUBLIC_FETCH_SERVING_DEFAULT_OFF_TOKEN,
            "transport_public_path_activation_authorized": (
                TRANSPORT_PUBLIC_PATH_ACTIVATION_NOT_AUTHORIZED_TOKEN
            ),
        },
        default_token="public_fetch_p2p_public_authority_forbidden_phase_1313",
    )

    transport_manifest = transport_principal_admission_sidecar_manifest()
    packet: dict[str, Any] = {
        "authorization_flags": {name: False for name in _FALSE_AUTHORIZATION_FLAGS},
        "current_epoch": current,
        "local_only": True,
        "python_http_transport_classification": {
            "http_fetch_transport_runtime": "devnet_test_not_public_p2p_substrate",
            "http_gossip_transport_runtime": "devnet_test_not_public_p2p_substrate",
            "public_substrate_enabled": False,
        },
        "readiness_verdict": (
            "blocked_default_off_rust_public_p2p_substrate_gate_required"
            if rust_status != "adr_integration_gate_satisfied_but_activation_out_of_scope"
            else "readiness_only_activation_out_of_scope_even_with_substrate_gate"
        ),
        "required_before_public_activation": list(_REQUIRED_BEFORE_PUBLIC_ACTIVATION),
        "rust_public_p2p_substrate_gate": {
            "activation_candidate_authorized": False,
            "explicit_adr_integration_gate_present": (
                explicit_rust_public_p2p_adr_integration_gate_present
            ),
            "rust_network_rs_path": "ilc_consensus/src/network.rs",
            "rust_network_rs_present": rust_network_rs_present,
            "rust_quic_tls_code_present": rust_quic_tls_code_present,
            "status": rust_status,
            "substrate_decision_adr_required": (
                rust_status != "adr_integration_gate_satisfied_but_activation_out_of_scope"
            ),
            "token": RUST_PUBLIC_P2P_SUBSTRATE_GATE_STATUS_RECORDED_TOKEN,
        },
        "source_evidence": dict(_SOURCE_EVIDENCE),
        "state": READINESS_STATE,
        "tokens": public_fetch_p2p_readiness_required_tokens(),
        "transport_principal_dependency": {
            "admission_sidecar_contract_version": transport_manifest["contract_version"],
            "hostile_network_public_path_blocked": transport_manifest[
                "hostile_network_public_path_blocked"
            ],
            "local_only": transport_manifest["local_only"],
            "public_fetch_serving_enabled": transport_manifest[
                "public_fetch_serving_enabled"
            ],
            "public_path_activation_authorized": transport_manifest[
                "public_path_activation_authorized"
            ],
            "public_p2p_enabled": transport_manifest["public_p2p_enabled"],
        },
        "version": PUBLIC_FETCH_P2P_READINESS_VERSION,
    }
    packet["candidate_sha256"] = _packet_sha256(packet)
    return validate_public_fetch_p2p_readiness_candidate(packet)


def validate_public_fetch_p2p_readiness_candidate(
    packet: Mapping[str, Any],
) -> dict[str, Any]:
    """Validate a Phase 1313 readiness packet without widening authority."""

    if not isinstance(packet, Mapping):
        raise PublicFetchP2PReadinessError(
            "public_fetch_p2p_readiness_candidate_invalid_phase_1313",
            "readiness packet must be a mapping",
        )
    _reject_unsafe_json_tree(packet)
    if set(packet) != _READINESS_PACKET_KEYS:
        raise PublicFetchP2PReadinessError(
            "public_fetch_p2p_readiness_candidate_keys_invalid_phase_1313",
            "readiness packet keys do not match the Phase 1313 contract",
        )
    if packet.get("version") != PUBLIC_FETCH_P2P_READINESS_VERSION:
        raise PublicFetchP2PReadinessError(
            "public_fetch_p2p_readiness_version_invalid_phase_1313",
            "readiness packet version is invalid",
        )
    if packet.get("state") != READINESS_STATE:
        raise PublicFetchP2PReadinessError(
            "public_fetch_p2p_readiness_state_invalid_phase_1313",
            "readiness packet state is invalid",
        )
    current = _require_epoch("current", packet.get("current_epoch"))
    if packet.get("local_only") is not True:
        raise PublicFetchP2PReadinessError(
            "public_fetch_p2p_readiness_local_only_required_phase_1313",
            "Phase 1313 readiness packet must remain local only",
        )
    if packet.get("tokens") != public_fetch_p2p_readiness_required_tokens():
        raise PublicFetchP2PReadinessError(
            "public_fetch_p2p_readiness_tokens_invalid_phase_1313",
            "Phase 1313 readiness packet tokens are invalid",
        )

    flags = _require_mapping(
        packet.get("authorization_flags"),
        token="public_fetch_p2p_readiness_authorization_flags_invalid_phase_1313",
    )
    if set(flags) != set(_FALSE_AUTHORIZATION_FLAGS):
        raise PublicFetchP2PReadinessError(
            "public_fetch_p2p_readiness_authorization_flags_invalid_phase_1313",
            "Phase 1313 authorization flags are invalid",
        )
    _require_all_false(
        flags,
        token_by_name={
            "public_p2p_enabled": PUBLIC_P2P_DEFAULT_OFF_TOKEN,
            "public_fetch_serving_enabled": PUBLIC_FETCH_SERVING_DEFAULT_OFF_TOKEN,
            "transport_public_path_activation_authorized": (
                TRANSPORT_PUBLIC_PATH_ACTIVATION_NOT_AUTHORIZED_TOKEN
            ),
        },
        default_token="public_fetch_p2p_public_authority_forbidden_phase_1313",
    )

    rust_gate = _require_mapping(
        packet.get("rust_public_p2p_substrate_gate"),
        token="public_fetch_p2p_rust_gate_invalid_phase_1313",
    )
    status = _require_choice(
        rust_gate.get("status"),
        allowed=_ALLOWED_RUST_GATE_STATUSES,
        token="public_fetch_p2p_rust_gate_status_invalid_phase_1313",
    )
    if rust_gate.get("token") != RUST_PUBLIC_P2P_SUBSTRATE_GATE_STATUS_RECORDED_TOKEN:
        raise PublicFetchP2PReadinessError(
            "public_fetch_p2p_rust_gate_token_invalid_phase_1313",
            "Rust public-P2P substrate gate token is invalid",
        )
    for key in (
        "activation_candidate_authorized",
        "explicit_adr_integration_gate_present",
    ):
        if not isinstance(rust_gate.get(key), bool):
            raise PublicFetchP2PReadinessError(
                "public_fetch_p2p_rust_gate_bool_invalid_phase_1313",
                "Rust gate boolean field is invalid",
            )
    if rust_gate.get("activation_candidate_authorized") is not False:
        raise PublicFetchP2PReadinessError(
            "public_fetch_p2p_activation_candidate_forbidden_phase_1313",
            "Phase 1313 cannot authorize a public activation candidate",
        )
    if status == "gate_required_not_satisfied":
        if rust_gate.get("explicit_adr_integration_gate_present") is not False:
            raise PublicFetchP2PReadinessError(
                "public_fetch_p2p_rust_gate_status_contradiction_phase_1313",
                "unsatisfied Rust gate cannot claim an explicit integration gate",
            )
        if rust_gate.get("substrate_decision_adr_required") is not True:
            raise PublicFetchP2PReadinessError(
                "public_fetch_p2p_rust_gate_required_phase_1313",
                "unsatisfied Rust gate must keep ADR/integration requirement true",
            )
    if status == "gate_ambiguous_human_review_required":
        if rust_gate.get("explicit_adr_integration_gate_present") is not False:
            raise PublicFetchP2PReadinessError(
                "public_fetch_p2p_rust_gate_status_contradiction_phase_1313",
                "ambiguous Rust gate cannot claim an explicit integration gate",
            )
        if rust_gate.get("substrate_decision_adr_required") is not True:
            raise PublicFetchP2PReadinessError(
                "public_fetch_p2p_rust_gate_required_phase_1313",
                "ambiguous Rust gate must keep ADR/integration requirement true",
            )
    if status == "adr_integration_gate_satisfied_but_activation_out_of_scope":
        if rust_gate.get("explicit_adr_integration_gate_present") is not True:
            raise PublicFetchP2PReadinessError(
                "public_fetch_p2p_rust_gate_evidence_required_phase_1313",
                "satisfied Rust gate status requires explicit gate marker",
            )
        if rust_gate.get("substrate_decision_adr_required") is not False:
            raise PublicFetchP2PReadinessError(
                "public_fetch_p2p_rust_gate_required_phase_1313",
                "satisfied Rust gate status must record the substrate requirement as closed",
            )
    if rust_gate.get("rust_network_rs_path") != "ilc_consensus/src/network.rs":
        raise PublicFetchP2PReadinessError(
            "public_fetch_p2p_rust_gate_path_invalid_phase_1313",
            "Rust network source path is invalid",
        )
    for key in ("rust_network_rs_present", "rust_quic_tls_code_present"):
        if rust_gate.get(key) is not True:
            raise PublicFetchP2PReadinessError(
                "public_fetch_p2p_rust_evidence_missing_phase_1313",
                "Rust QUIC/TLS source evidence is missing",
            )

    python_http = _require_mapping(
        packet.get("python_http_transport_classification"),
        token="public_fetch_p2p_python_http_classification_invalid_phase_1313",
    )
    if python_http.get("public_substrate_enabled") is not False:
        raise PublicFetchP2PReadinessError(
            "public_fetch_p2p_python_http_public_substrate_forbidden_phase_1313",
            "Python HTTP transport cannot be classified as a public substrate",
        )
    for key in ("http_fetch_transport_runtime", "http_gossip_transport_runtime"):
        if python_http.get(key) != "devnet_test_not_public_p2p_substrate":
            raise PublicFetchP2PReadinessError(
                "public_fetch_p2p_python_http_classification_invalid_phase_1313",
                "Python HTTP transport classification is invalid",
            )

    transport = _require_mapping(
        packet.get("transport_principal_dependency"),
        token="public_fetch_p2p_transport_dependency_invalid_phase_1313",
    )
    if transport.get("local_only") is not True:
        raise PublicFetchP2PReadinessError(
            "public_fetch_p2p_transport_dependency_local_only_required_phase_1313",
            "TransportPrincipal dependency must remain local only",
        )
    if transport.get("hostile_network_public_path_blocked") is not True:
        raise PublicFetchP2PReadinessError(
            "public_fetch_p2p_transport_dependency_blocked_required_phase_1313",
            "TransportPrincipal public path must remain blocked",
        )
    for key in (
        "public_fetch_serving_enabled",
        "public_path_activation_authorized",
        "public_p2p_enabled",
    ):
        if transport.get(key) is not False:
            raise PublicFetchP2PReadinessError(
                "public_fetch_p2p_transport_dependency_public_authority_forbidden_phase_1313",
                "TransportPrincipal dependency cannot enable public authority",
            )

    requirements = packet.get("required_before_public_activation")
    if requirements != list(_REQUIRED_BEFORE_PUBLIC_ACTIVATION):
        raise PublicFetchP2PReadinessError(
            "public_fetch_p2p_requirements_invalid_phase_1313",
            "Phase 1313 public-activation requirements are invalid",
        )
    source_evidence = _require_mapping(
        packet.get("source_evidence"),
        token="public_fetch_p2p_source_evidence_invalid_phase_1313",
    )
    if dict(source_evidence) != _SOURCE_EVIDENCE:
        raise PublicFetchP2PReadinessError(
            "public_fetch_p2p_source_evidence_invalid_phase_1313",
            "Phase 1313 source evidence is invalid",
        )
    expected_verdict = (
        "readiness_only_activation_out_of_scope_even_with_substrate_gate"
        if status == "adr_integration_gate_satisfied_but_activation_out_of_scope"
        else "blocked_default_off_rust_public_p2p_substrate_gate_required"
    )
    if packet.get("readiness_verdict") != expected_verdict:
        raise PublicFetchP2PReadinessError(
            "public_fetch_p2p_readiness_verdict_invalid_phase_1313",
            "Phase 1313 readiness verdict is invalid",
        )
    candidate_sha256 = _require_hex_digest(packet.get("candidate_sha256"))
    if candidate_sha256 != _packet_sha256(packet):
        raise PublicFetchP2PReadinessError(
            "public_fetch_p2p_readiness_candidate_hash_mismatch_phase_1313",
            "Phase 1313 readiness packet hash mismatch",
        )

    validated = dict(packet)
    validated["current_epoch"] = current
    canonical_public_fetch_p2p_readiness_candidate_json(validated)
    return validated


def public_fetch_p2p_readiness_candidate_ref(packet: Mapping[str, Any]) -> str:
    validated = validate_public_fetch_p2p_readiness_candidate(packet)
    return f"{READINESS_REF_PREFIX}:{validated['candidate_sha256']}"


def canonical_public_fetch_p2p_readiness_candidate_json(packet: Mapping[str, Any]) -> str:
    _reject_unsafe_json_tree(packet)
    canonical = json.dumps(packet, allow_nan=False, separators=(",", ":"), sort_keys=True)
    if len(canonical.encode("utf-8")) > _MAX_CANONICAL_JSON_BYTES:
        raise PublicFetchP2PReadinessError(
            "public_fetch_p2p_payload_size_exceeded_phase_1313",
            "Phase 1313 readiness canonical JSON exceeds the byte bound",
        )
    return canonical


def export_public_fetch_p2p_readiness_candidate_json(
    packet: Mapping[str, Any] | None = None,
) -> str:
    active = (
        build_public_fetch_p2p_readiness_candidate(current_epoch=1)
        if packet is None
        else validate_public_fetch_p2p_readiness_candidate(packet)
    )
    return canonical_public_fetch_p2p_readiness_candidate_json(active)


def _packet_sha256(packet: Mapping[str, Any]) -> str:
    payload = dict(packet)
    payload.pop("candidate_sha256", None)
    return hashlib.sha256(
        canonical_public_fetch_p2p_readiness_candidate_json(payload).encode("utf-8")
    ).hexdigest()


def _reject_unsafe_json_tree(
    value: Any,
    *,
    _depth: int = 0,
    _seen: set[int] | None = None,
    _counter: list[int] | None = None,
) -> None:
    if _depth > _MAX_PAYLOAD_DEPTH:
        raise PublicFetchP2PReadinessError(
            "public_fetch_p2p_payload_too_deep_phase_1313",
            "Phase 1313 readiness payload is too deep",
        )
    if _seen is None:
        _seen = set()
    if _counter is None:
        _counter = [0]
    _counter[0] += 1
    if _counter[0] > _MAX_PAYLOAD_NODES:
        raise PublicFetchP2PReadinessError(
            "public_fetch_p2p_payload_too_large_phase_1313",
            "Phase 1313 readiness payload is too large",
        )
    if isinstance(value, float):
        raise PublicFetchP2PReadinessError(
            "public_fetch_p2p_float_values_forbidden_phase_1313",
            "Phase 1313 readiness payload cannot contain floats",
        )
    if isinstance(value, bool):
        return
    if isinstance(value, int):
        if value < 0 or value > _MAX_EPOCH:
            raise PublicFetchP2PReadinessError(
                "public_fetch_p2p_int_values_invalid_phase_1313",
                "Phase 1313 readiness integer values must be non-negative and bounded",
            )
        return
    if isinstance(value, str):
        _require_text(value)
        return
    if value is None:
        return
    if isinstance(value, Mapping):
        object_id = id(value)
        if object_id in _seen:
            raise PublicFetchP2PReadinessError(
                "public_fetch_p2p_payload_cycle_forbidden_phase_1313",
                "Phase 1313 readiness payload cannot contain cycles",
            )
        _seen.add(object_id)
        try:
            for key, item in value.items():
                _require_text(key)
                _counter[0] += 1
                if _counter[0] > _MAX_PAYLOAD_NODES:
                    raise PublicFetchP2PReadinessError(
                        "public_fetch_p2p_payload_too_large_phase_1313",
                        "Phase 1313 readiness payload is too large",
                    )
                _reject_unsafe_json_tree(
                    item,
                    _depth=_depth + 1,
                    _seen=_seen,
                    _counter=_counter,
                )
        finally:
            _seen.remove(object_id)
        return
    if isinstance(value, list):
        object_id = id(value)
        if object_id in _seen:
            raise PublicFetchP2PReadinessError(
                "public_fetch_p2p_payload_cycle_forbidden_phase_1313",
                "Phase 1313 readiness payload cannot contain cycles",
            )
        _seen.add(object_id)
        try:
            for item in value:
                _reject_unsafe_json_tree(
                    item,
                    _depth=_depth + 1,
                    _seen=_seen,
                    _counter=_counter,
                )
        finally:
            _seen.remove(object_id)
        return
    raise PublicFetchP2PReadinessError(
        "public_fetch_p2p_payload_type_invalid_phase_1313",
        "Phase 1313 readiness payload contains a non-JSON type",
    )


def _require_epoch(name: str, value: object) -> int:
    if (
        not isinstance(value, int)
        or isinstance(value, bool)
        or value < 1
        or value > _MAX_EPOCH
    ):
        raise PublicFetchP2PReadinessError(
            f"public_fetch_p2p_{name}_epoch_invalid_phase_1313",
            "Phase 1313 readiness epoch must be a positive bounded integer",
        )
    return value


def _require_text(value: object) -> str:
    if not isinstance(value, str) or not value.strip() or value != value.strip():
        raise PublicFetchP2PReadinessError(
            "public_fetch_p2p_text_invalid_phase_1313",
            "Phase 1313 readiness text is invalid",
        )
    if any(ord(char) < 0x20 for char in value):
        raise PublicFetchP2PReadinessError(
            "public_fetch_p2p_text_invalid_phase_1313",
            "Phase 1313 readiness text must not contain control characters",
        )
    if len(value) > _MAX_TEXT_LENGTH:
        raise PublicFetchP2PReadinessError(
            "public_fetch_p2p_text_too_large_phase_1313",
            "Phase 1313 readiness text exceeds the size bound",
        )
    return value


def _require_hex_digest(value: object) -> str:
    if (
        not isinstance(value, str)
        or len(value) != _HEX_DIGEST_LENGTH
        or any(char not in _HEX for char in value)
    ):
        raise PublicFetchP2PReadinessError(
            "public_fetch_p2p_hex_digest_invalid_phase_1313",
            "Phase 1313 readiness digest is invalid",
        )
    return value


def _require_bool(name: str, value: object) -> bool:
    if not isinstance(value, bool):
        raise PublicFetchP2PReadinessError(
            f"public_fetch_p2p_{name}_bool_invalid_phase_1313",
            "Phase 1313 readiness boolean field is invalid",
        )
    return value


def _require_mapping(value: object, *, token: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise PublicFetchP2PReadinessError(
            token,
            "Phase 1313 readiness mapping is invalid",
        )
    return value


def _require_choice(value: object, *, allowed: tuple[str, ...], token: str) -> str:
    text = _require_text(value)
    if text not in allowed:
        raise PublicFetchP2PReadinessError(
            token,
            "Phase 1313 readiness choice is invalid",
        )
    return text


def _require_all_false(
    flags: Mapping[str, object],
    *,
    token_by_name: Mapping[str, str] | None = None,
    default_token: str,
) -> None:
    token_map = {} if token_by_name is None else dict(token_by_name)
    for name, value in flags.items():
        if value is not False:
            token = token_map.get(name, default_token)
            raise PublicFetchP2PReadinessError(
                token,
                f"Phase 1313 requires {name} to remain false",
            )


__all__ = [
    "PHASE_1314_NEXT_TOKEN",
    "PUBLIC_FETCH_P2P_READINESS_VERSION",
    "PUBLIC_FETCH_SERVING_DEFAULT_OFF_TOKEN",
    "PUBLIC_P2P_DEFAULT_OFF_TOKEN",
    "PUBLIC_RC_REMAINS_BLOCKED_AFTER_PHASE_1313_TOKEN",
    "PublicFetchP2PReadinessError",
    "READINESS_REF_PREFIX",
    "READINESS_STATE",
    "RUST_PUBLIC_P2P_SUBSTRATE_GATE_STATUS_RECORDED_TOKEN",
    "RUST_PUBLIC_P2P_SUBSTRATE_GATE_STILL_REQUIRED_PHASE_1313_TOKEN",
    "TRANSPORT_PUBLIC_PATH_ACTIVATION_NOT_AUTHORIZED_TOKEN",
    "build_public_fetch_p2p_readiness_candidate",
    "canonical_public_fetch_p2p_readiness_candidate_json",
    "export_public_fetch_p2p_readiness_candidate_json",
    "public_fetch_p2p_readiness_candidate_manifest",
    "public_fetch_p2p_readiness_candidate_ref",
    "public_fetch_p2p_readiness_required_tokens",
    "validate_public_fetch_p2p_readiness_candidate",
]
