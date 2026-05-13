"""Phase 1309 local TransportPrincipal admission sidecar substrate.

This module materializes a deterministic local admission decision from an
already-authenticated TransportPrincipal context. It does not create a server,
listener, public P2P path, public fetch path, public credential issuer,
persistent public registry, wallet action, ECU mint, or ILC settlement surface.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Collection, Mapping
from typing import Any

from ilc_core.network.d2d.transport_principal_pre_public_path import (
    TRANSPORT_PRINCIPAL_PRE_PUBLIC_PATH_VERSION,
    validate_transport_principal_context,
)


TRANSPORT_PRINCIPAL_ADMISSION_SIDECAR_VERSION = (
    "transport_principal_admission_sidecar_lifecycle_hardening_phase_1309.v0.1"
)
TRANSPORT_PRINCIPAL_LIFECYCLE_POLICY_LOCAL_SUBSTRATE_TOKEN = (
    "transport_principal_lifecycle_policy_local_substrate_phase_1309"
)
TRANSPORT_PRINCIPAL_PUBLIC_PATH_NOT_ACTIVATED_TOKEN = (
    "transport_principal_public_path_not_activated_phase_1309"
)
PUBLIC_P2P_NOT_ACTIVATED_TOKEN = "public_p2p_not_activated_phase_1309"
PHASE_1310_NEXT_TOKEN = "phase_1310_revocation_replay_admission_ban_tests_next"
PUBLIC_RC_REMAINS_BLOCKED_AFTER_PHASE_1309_TOKEN = (
    "public_rc_remains_blocked_after_phase_1309"
)
REVOCATION_REPLAY_ADMISSION_BAN_TESTS_PHASE_1310_VERSION = (
    "revocation_replay_admission_ban_tests_phase_1310.v0.1"
)
TRANSPORT_PRINCIPAL_REVOCATION_REPLAY_TESTS_HARDENED_PHASE_1310_TOKEN = (
    "transport_principal_revocation_replay_tests_hardened_phase_1310"
)
ADMISSION_BAN_RATE_PRIVACY_TESTS_HARDENED_PHASE_1310_TOKEN = (
    "admission_ban_rate_privacy_tests_hardened_phase_1310"
)
HOSTILE_NETWORK_PUBLIC_PATH_STILL_BLOCKED_PHASE_1310_TOKEN = (
    "hostile_network_public_path_still_blocked_phase_1310"
)
PHASE_1311_NEXT_TOKEN = "phase_1311_local_graph_memory_projection_sidecar_next"
PUBLIC_RC_REMAINS_BLOCKED_AFTER_PHASE_1310_TOKEN = (
    "public_rc_remains_blocked_after_phase_1310"
)

ADMISSION_DECISION_STATE = "transport_principal_admission_lifecycle_local_only"
ADMITTED_LOCAL_ONLY_DECISION = "admitted_local_only_no_public_path_phase_1309"
TRANSPORT_PRINCIPAL_ADMISSION_DECISION_REF_PREFIX = (
    "transport_principal_admission_decision_sha256"
)

_MAX_PAYLOAD_DEPTH = 32
_MAX_PAYLOAD_NODES = 100_000
_MAX_TEXT_LENGTH = 4096
_MAX_CANONICAL_JSON_BYTES = 10_000_000
_MAX_COLLECTION_SIZE = 10_000
_MAX_PROTOCOL_INT = 1_000_000_000_000
_MAX_RATE_LIMIT_COUNT = 1_000_000_000
_DEFAULT_LOCAL_RATE_LIMIT_CEILING = 1_000
_HEX_DIGEST_LENGTH = 64
_HEX = frozenset("0123456789abcdef")

_DEFAULT_ACCEPTED_CREDENTIAL_KINDS = (
    "mtls_certificate_fingerprint",
    "quic_peer_credential",
    "rustls_peer_certificate_chain_hash",
    "signed_transport_handshake",
    "transport_credential",
)
_ALLOWED_PRIVACY_MODES = (
    "ephemeral_principal_no_agentid_default",
    "rotating_pseudonymous_transport_principal",
)
_FALSE_AUTHORIZATION_FLAGS = (
    "public_path_activation_authorized",
    "public_p2p_enabled",
    "public_fetch_serving_enabled",
    "public_sidecar_serving_enabled",
    "non_loopback_projection_enabled",
    "public_listener_enabled",
    "peer_discovery_enabled",
    "public_credential_issuer_authorized",
    "public_revocation_registry_activated",
    "public_replay_cache_activated",
    "public_rate_limit_state_activated",
    "release_artifact_authorized",
)
_FALSE_FALLBACK_FLAGS = (
    "requester_id_fallback_allowed",
    "json_body_requester_id_fallback_allowed",
    "client_ip_rate_limit_key_allowed",
    "agent_id_rate_limit_key_allowed",
    "harness_identity_rate_limit_key_allowed",
    "openclaw_identity_rate_limit_key_allowed",
    "tailscale_identity_rate_limit_key_allowed",
)
_FORBIDDEN_CONTEXT_KEYS = frozenset(
    {
        "AgentID",
        "agent_id",
        "agentid",
        "client_ip",
        "economic_position",
        "graph_position",
        "harness_identity",
        "ip_address",
        "json_body_requester_id",
        "openclaw_identity",
        "private_graph_position",
        "requester_id",
        "stake",
        "stake_balance",
        "tailscale_identity",
        "wallet",
        "wallet_address",
        "wallet_balance",
    }
)
_EXPECTED_TRANSPORT_PRINCIPAL_CONTEXT_KEYS = frozenset(
    {
        "admission_key",
        "agent_id_rate_limit_key_allowed",
        "ban_key",
        "client_ip_rate_limit_key_allowed",
        "credential_fingerprint",
        "credential_kind",
        "current_epoch",
        "expires_epoch",
        "handshake_nonce_fingerprint",
        "issued_epoch",
        "non_loopback_projection_enabled",
        "principal_id",
        "public_p2p_enabled",
        "rate_limit_key",
        "replay_key",
        "requester_id_fallback_allowed",
        "scope",
        "tokens",
        "version",
    }
)
_PUBLIC_MODE_BLOCKERS = (
    "public_path_activation_authority_missing_phase_1309",
    "public_credential_issuer_authority_missing_phase_1309",
    "public_revocation_registry_not_activated_phase_1309",
    "public_replay_cache_not_activated_phase_1309",
    "public_rate_limit_state_not_activated_phase_1309",
    "rust_public_p2p_substrate_gate_still_required_phase_1309",
    "phase_1310_revocation_replay_admission_ban_tests_required",
)
_ADMISSION_DECISION_KEYS = frozenset(
    {
        "admission_decision_sha256",
        "admission_key",
        "authorization_flags",
        "ban_key",
        "context_scope",
        "context_sha256",
        "context_tokens",
        "context_version",
        "credential_fingerprint",
        "credential_kind",
        "current_epoch",
        "decision",
        "expires_epoch",
        "fallback_policy",
        "issued_epoch",
        "lifecycle_policy",
        "principal_id",
        "privacy_mode",
        "public_mode_blockers",
        "rate_limit_key",
        "replay_key",
        "state",
        "state_checks",
        "tokens",
        "version",
    }
)


class TransportPrincipalAdmissionSidecarError(ValueError):
    """Fail-closed local admission error with a stable token."""

    def __init__(self, token: str, message: str) -> None:
        super().__init__(message)
        self.token = token


def transport_principal_admission_required_tokens() -> list[str]:
    return [
        TRANSPORT_PRINCIPAL_ADMISSION_SIDECAR_VERSION,
        TRANSPORT_PRINCIPAL_LIFECYCLE_POLICY_LOCAL_SUBSTRATE_TOKEN,
        TRANSPORT_PRINCIPAL_PUBLIC_PATH_NOT_ACTIVATED_TOKEN,
        PUBLIC_P2P_NOT_ACTIVATED_TOKEN,
        PHASE_1310_NEXT_TOKEN,
        PUBLIC_RC_REMAINS_BLOCKED_AFTER_PHASE_1309_TOKEN,
    ]


def transport_principal_hostile_network_required_tokens() -> list[str]:
    return [
        REVOCATION_REPLAY_ADMISSION_BAN_TESTS_PHASE_1310_VERSION,
        TRANSPORT_PRINCIPAL_REVOCATION_REPLAY_TESTS_HARDENED_PHASE_1310_TOKEN,
        ADMISSION_BAN_RATE_PRIVACY_TESTS_HARDENED_PHASE_1310_TOKEN,
        HOSTILE_NETWORK_PUBLIC_PATH_STILL_BLOCKED_PHASE_1310_TOKEN,
        PHASE_1311_NEXT_TOKEN,
        PUBLIC_RC_REMAINS_BLOCKED_AFTER_PHASE_1310_TOKEN,
    ]


def transport_principal_admission_sidecar_manifest() -> dict[str, Any]:
    """Return deterministic local-only sidecar metadata."""

    manifest = {
        "admission_ban_rate_privacy_tests_hardened": True,
        "allowed_binding_modes": [
            "in_process_import",
            "local_cli_subprocess",
            "private_loopback_or_private_overlay_when_authorized_by_harness",
        ],
        "contract_version": TRANSPORT_PRINCIPAL_ADMISSION_SIDECAR_VERSION,
        "hostile_network_public_path_blocked": True,
        "hostile_network_test_tokens": transport_principal_hostile_network_required_tokens(),
        "local_only": True,
        "public_credential_issuer_authorized": False,
        "public_fetch_serving_enabled": False,
        "public_path_activation_authorized": False,
        "public_p2p_enabled": False,
        "public_rate_limit_state_activated": False,
        "public_replay_cache_activated": False,
        "public_revocation_registry_activated": False,
        "revocation_replay_tests_hardened": True,
        "public_sidecar_serving_enabled": False,
        "source_context_version": TRANSPORT_PRINCIPAL_PRE_PUBLIC_PATH_VERSION,
        "tokens": transport_principal_admission_required_tokens(),
    }
    _reject_unsafe_json_tree(manifest)
    return manifest


def build_transport_principal_admission_decision(
    *,
    transport_principal_context: Mapping[str, Any],
    current_epoch: int,
    privacy_mode: str = "ephemeral_principal_no_agentid_default",
    accepted_credential_kinds: Collection[str] = _DEFAULT_ACCEPTED_CREDENTIAL_KINDS,
    revoked_credential_fingerprints: Collection[str] = (),
    replay_cache: Collection[str] = (),
    banned_transport_keys: Collection[str] = (),
    rate_limit_counters: Mapping[str, int] | None = None,
    local_rate_limit_ceiling: int = _DEFAULT_LOCAL_RATE_LIMIT_CEILING,
    public_path_activation_authorized: bool = False,
    public_p2p_enabled: bool = False,
    public_fetch_serving_enabled: bool = False,
    public_sidecar_serving_enabled: bool = False,
    non_loopback_projection_enabled: bool = False,
    public_listener_enabled: bool = False,
    peer_discovery_enabled: bool = False,
    public_credential_issuer_authorized: bool = False,
    public_revocation_registry_activated: bool = False,
    public_replay_cache_activated: bool = False,
    public_rate_limit_state_activated: bool = False,
    release_artifact_authorized: bool = False,
    requester_id_fallback_allowed: bool = False,
    json_body_requester_id_fallback_allowed: bool = False,
    client_ip_rate_limit_key_allowed: bool = False,
    agent_id_rate_limit_key_allowed: bool = False,
    harness_identity_rate_limit_key_allowed: bool = False,
    openclaw_identity_rate_limit_key_allowed: bool = False,
    tailscale_identity_rate_limit_key_allowed: bool = False,
) -> dict[str, Any]:
    """Build a deterministic local-only admission decision.

    Caller-supplied revocation, replay, ban, and accepted-kind collections are
    normalized and bounded before the Phase 1267 context validator is called.
    """

    _reject_unsafe_json_tree(transport_principal_context)
    _reject_forbidden_context_keys(transport_principal_context)
    _require_transport_principal_context_keys(transport_principal_context)
    current = _require_epoch("current", current_epoch)
    ceiling = _require_local_rate_limit_ceiling(local_rate_limit_ceiling)
    mode = _require_choice(
        "privacy_mode",
        privacy_mode,
        allowed=_ALLOWED_PRIVACY_MODES,
        token="transport_principal_admission_privacy_mode_invalid_phase_1309",
    )
    accepted_kinds = _normalize_text_collection(
        accepted_credential_kinds,
        token="transport_principal_admission_credential_kind_policy_invalid_phase_1309",
    )
    revoked = _normalize_text_collection(
        revoked_credential_fingerprints,
        token="transport_principal_admission_revocation_state_invalid_phase_1309",
    )
    replay = _normalize_text_collection(
        replay_cache,
        token="transport_principal_admission_replay_state_invalid_phase_1309",
    )
    banned = _normalize_text_collection(
        banned_transport_keys,
        token="transport_principal_admission_ban_state_invalid_phase_1309",
    )
    rate_counters = _normalize_rate_limit_counters(rate_limit_counters)
    _require_all_false(
        {
            "public_path_activation_authorized": public_path_activation_authorized,
            "public_p2p_enabled": public_p2p_enabled,
            "public_fetch_serving_enabled": public_fetch_serving_enabled,
            "public_sidecar_serving_enabled": public_sidecar_serving_enabled,
            "non_loopback_projection_enabled": non_loopback_projection_enabled,
            "public_listener_enabled": public_listener_enabled,
            "peer_discovery_enabled": peer_discovery_enabled,
            "public_credential_issuer_authorized": public_credential_issuer_authorized,
            "public_revocation_registry_activated": public_revocation_registry_activated,
            "public_replay_cache_activated": public_replay_cache_activated,
            "public_rate_limit_state_activated": public_rate_limit_state_activated,
            "release_artifact_authorized": release_artifact_authorized,
        },
        token_by_name={
            "public_path_activation_authorized": TRANSPORT_PRINCIPAL_PUBLIC_PATH_NOT_ACTIVATED_TOKEN,
            "public_p2p_enabled": PUBLIC_P2P_NOT_ACTIVATED_TOKEN,
        },
        default_token="transport_principal_admission_public_authority_forbidden_phase_1309",
    )
    _require_all_false(
        {
            "requester_id_fallback_allowed": requester_id_fallback_allowed,
            "json_body_requester_id_fallback_allowed": json_body_requester_id_fallback_allowed,
            "client_ip_rate_limit_key_allowed": client_ip_rate_limit_key_allowed,
            "agent_id_rate_limit_key_allowed": agent_id_rate_limit_key_allowed,
            "harness_identity_rate_limit_key_allowed": harness_identity_rate_limit_key_allowed,
            "openclaw_identity_rate_limit_key_allowed": openclaw_identity_rate_limit_key_allowed,
            "tailscale_identity_rate_limit_key_allowed": tailscale_identity_rate_limit_key_allowed,
        },
        default_token="transport_principal_admission_fallback_identity_forbidden_phase_1309",
    )

    validated_context = validate_transport_principal_context(
        transport_principal_context,
        current_epoch=current,
        revoked_credential_fingerprints=revoked,
        replay_cache=replay,
    )
    credential_kind = _require_text(validated_context["credential_kind"])
    if credential_kind not in accepted_kinds:
        raise TransportPrincipalAdmissionSidecarError(
            "transport_principal_admission_credential_kind_rejected_phase_1309",
            "credential kind is not admitted by the local Phase 1309 policy",
        )

    ban_subjects = {
        validated_context["ban_key"],
        validated_context["credential_fingerprint"],
        validated_context["principal_id"],
    }
    if ban_subjects & set(banned):
        raise TransportPrincipalAdmissionSidecarError(
            "transport_principal_admission_banned_phase_1309",
            "transport principal is banned by local Phase 1309 state",
        )
    local_rate_count = rate_counters.get(validated_context["rate_limit_key"], 0)
    if local_rate_count >= ceiling:
        raise TransportPrincipalAdmissionSidecarError(
            "transport_principal_admission_rate_limit_exceeded_phase_1310",
            "transport principal exceeds the caller-supplied local rate-limit state",
        )

    authorization_flags = {name: False for name in _FALSE_AUTHORIZATION_FLAGS}
    fallback_policy = {
        **{name: False for name in _FALSE_FALLBACK_FLAGS},
        "rate_limit_identity_source": "authenticated_transport_principal",
    }
    lifecycle_policy = {
        "accepted_credential_kinds": list(accepted_kinds),
        "credential_issuer_public_authority": False,
        "credential_kind_admitted": True,
        "epoch_window_checked": True,
        "lifecycle_policy_scope": "local_call_scope_only",
        "rotation_required_before_public_path": True,
    }
    state_checks = {
        "admission_key_checked": True,
        "ban_checked": True,
        "ban_registry_source": "caller_supplied_local_collection",
        "public_persistent_state_activated": False,
        "rate_limit_ceiling": ceiling,
        "rate_limit_checked": True,
        "rate_limit_counter": local_rate_count,
        "rate_limit_key_bound_to_transport_principal": True,
        "rate_limit_state_source": "caller_supplied_local_collection",
        "replay_cache_source": "caller_supplied_local_collection",
        "replay_checked": True,
        "revocation_checked": True,
        "revocation_registry_source": "caller_supplied_local_collection",
    }
    body = {
        "admission_key": validated_context["admission_key"],
        "authorization_flags": authorization_flags,
        "ban_key": validated_context["ban_key"],
        "context_scope": validated_context["scope"],
        "context_sha256": _sha256_payload(validated_context),
        "context_tokens": list(validated_context["tokens"]),
        "context_version": validated_context["version"],
        "credential_fingerprint": validated_context["credential_fingerprint"],
        "credential_kind": credential_kind,
        "current_epoch": current,
        "decision": ADMITTED_LOCAL_ONLY_DECISION,
        "expires_epoch": validated_context["expires_epoch"],
        "fallback_policy": fallback_policy,
        "issued_epoch": validated_context["issued_epoch"],
        "lifecycle_policy": lifecycle_policy,
        "principal_id": validated_context["principal_id"],
        "privacy_mode": mode,
        "public_mode_blockers": sorted(_PUBLIC_MODE_BLOCKERS),
        "rate_limit_key": validated_context["rate_limit_key"],
        "replay_key": validated_context["replay_key"],
        "state": ADMISSION_DECISION_STATE,
        "state_checks": state_checks,
        "tokens": sorted(transport_principal_admission_required_tokens()),
        "version": TRANSPORT_PRINCIPAL_ADMISSION_SIDECAR_VERSION,
    }
    decision = {"admission_decision_sha256": _sha256_payload(body), **body}
    return validate_transport_principal_admission_decision(decision, current_epoch=current)


def validate_transport_principal_admission_decision(
    decision: Mapping[str, Any],
    *,
    current_epoch: int,
) -> dict[str, Any]:
    """Validate a Phase 1309 local admission decision packet."""

    if not isinstance(decision, Mapping):
        raise TransportPrincipalAdmissionSidecarError(
            "transport_principal_admission_decision_invalid_phase_1309",
            "admission decision must be a mapping",
        )
    _reject_unsafe_json_tree(decision)
    current = _require_epoch("current", current_epoch)
    payload = dict(decision)
    if set(payload) != _ADMISSION_DECISION_KEYS:
        raise TransportPrincipalAdmissionSidecarError(
            "transport_principal_admission_unexpected_keys_forbidden_phase_1310",
            "admission decision keys do not match the Phase 1310 contract",
        )
    if payload.get("version") != TRANSPORT_PRINCIPAL_ADMISSION_SIDECAR_VERSION:
        raise TransportPrincipalAdmissionSidecarError(
            "transport_principal_admission_version_invalid_phase_1309",
            "admission decision version is invalid",
        )
    if payload.get("state") != ADMISSION_DECISION_STATE:
        raise TransportPrincipalAdmissionSidecarError(
            "transport_principal_admission_state_invalid_phase_1309",
            "admission decision state is invalid",
        )
    if payload.get("decision") != ADMITTED_LOCAL_ONLY_DECISION:
        raise TransportPrincipalAdmissionSidecarError(
            "transport_principal_admission_decision_token_invalid_phase_1309",
            "admission decision token is invalid",
        )
    if _require_epoch("current", payload.get("current_epoch")) != current:
        raise TransportPrincipalAdmissionSidecarError(
            "transport_principal_admission_current_epoch_mismatch_phase_1309",
            "admission decision current epoch does not match caller epoch",
        )
    issued = _require_epoch("issued", payload.get("issued_epoch"))
    expires = _require_epoch("expires", payload.get("expires_epoch"))
    if issued > current or current > expires:
        raise TransportPrincipalAdmissionSidecarError(
            "transport_principal_admission_epoch_window_invalid_phase_1309",
            "admission decision epoch window is invalid",
        )

    normalized = {
        "admission_decision_sha256": _require_hex_digest(
            "admission_decision_sha256",
            payload.get("admission_decision_sha256"),
        ),
        "admission_key": _require_prefixed_digest(
            "admission_key",
            payload.get("admission_key"),
            "tp_admission",
        ),
        "authorization_flags": _normalize_false_flag_mapping(
            payload.get("authorization_flags"),
            required_keys=_FALSE_AUTHORIZATION_FLAGS,
            token="transport_principal_admission_authorization_flags_invalid_phase_1309",
        ),
        "ban_key": _require_prefixed_digest("ban_key", payload.get("ban_key"), "tp_ban"),
        "context_scope": _require_choice(
            "context_scope",
            payload.get("context_scope"),
            allowed=("pre_public_path",),
            token="transport_principal_admission_context_scope_invalid_phase_1309",
        ),
        "context_sha256": _require_hex_digest("context_sha256", payload.get("context_sha256")),
        "context_tokens": _normalize_text_list(
            payload.get("context_tokens"),
            token="transport_principal_admission_context_tokens_invalid_phase_1309",
        ),
        "context_version": _require_choice(
            "context_version",
            payload.get("context_version"),
            allowed=(TRANSPORT_PRINCIPAL_PRE_PUBLIC_PATH_VERSION,),
            token="transport_principal_admission_context_version_invalid_phase_1309",
        ),
        "credential_fingerprint": _require_hex_digest(
            "credential_fingerprint",
            payload.get("credential_fingerprint"),
        ),
        "credential_kind": _require_choice(
            "credential_kind",
            payload.get("credential_kind"),
            allowed=_DEFAULT_ACCEPTED_CREDENTIAL_KINDS,
            token="transport_principal_admission_credential_kind_invalid_phase_1309",
        ),
        "current_epoch": current,
        "decision": ADMITTED_LOCAL_ONLY_DECISION,
        "expires_epoch": expires,
        "fallback_policy": _normalize_fallback_policy(payload.get("fallback_policy")),
        "issued_epoch": issued,
        "lifecycle_policy": _normalize_lifecycle_policy(payload.get("lifecycle_policy")),
        "principal_id": _require_prefixed_digest("principal_id", payload.get("principal_id"), "tp"),
        "privacy_mode": _require_choice(
            "privacy_mode",
            payload.get("privacy_mode"),
            allowed=_ALLOWED_PRIVACY_MODES,
            token="transport_principal_admission_privacy_mode_invalid_phase_1309",
        ),
        "public_mode_blockers": _normalize_exact_text_list(
            payload.get("public_mode_blockers"),
            expected=_PUBLIC_MODE_BLOCKERS,
            token="transport_principal_admission_public_mode_blockers_invalid_phase_1309",
        ),
        "rate_limit_key": _require_prefixed_digest(
            "rate_limit_key",
            payload.get("rate_limit_key"),
            "tp_rate",
        ),
        "replay_key": _require_prefixed_digest(
            "replay_key",
            payload.get("replay_key"),
            "tp_replay",
        ),
        "state": ADMISSION_DECISION_STATE,
        "state_checks": _normalize_state_checks(payload.get("state_checks")),
        "tokens": _normalize_exact_text_list(
            payload.get("tokens"),
            expected=transport_principal_admission_required_tokens(),
            token="transport_principal_admission_tokens_invalid_phase_1309",
        ),
        "version": TRANSPORT_PRINCIPAL_ADMISSION_SIDECAR_VERSION,
    }
    expected_hash_body = dict(normalized)
    actual_hash = expected_hash_body.pop("admission_decision_sha256")
    if actual_hash != _sha256_payload(expected_hash_body):
        raise TransportPrincipalAdmissionSidecarError(
            "transport_principal_admission_decision_hash_mismatch_phase_1309",
            "admission decision hash does not match canonical decision body",
        )
    return normalized


def transport_principal_admission_decision_ref(decision: Mapping[str, Any]) -> str:
    if not isinstance(decision, Mapping):
        raise TransportPrincipalAdmissionSidecarError(
            "transport_principal_admission_decision_invalid_phase_1309",
            "admission decision must be a mapping",
        )
    validated = validate_transport_principal_admission_decision(
        decision,
        current_epoch=_require_epoch("current", decision.get("current_epoch")),
    )
    return f"{TRANSPORT_PRINCIPAL_ADMISSION_DECISION_REF_PREFIX}:{validated['admission_decision_sha256']}"


def canonical_transport_principal_admission_json(payload: Mapping[str, Any]) -> str:
    _reject_unsafe_json_tree(payload)
    canonical = json.dumps(payload, allow_nan=False, separators=(",", ":"), sort_keys=True)
    if len(canonical.encode("utf-8")) > _MAX_CANONICAL_JSON_BYTES:
        raise TransportPrincipalAdmissionSidecarError(
            "transport_principal_admission_payload_size_exceeded_phase_1309",
            "canonical JSON payload exceeds byte bound",
        )
    return canonical


def export_transport_principal_admission_decision_json(decision: Mapping[str, Any]) -> str:
    if not isinstance(decision, Mapping):
        raise TransportPrincipalAdmissionSidecarError(
            "transport_principal_admission_decision_invalid_phase_1309",
            "admission decision must be a mapping",
        )
    validated = validate_transport_principal_admission_decision(
        decision,
        current_epoch=_require_epoch("current", decision.get("current_epoch")),
    )
    return canonical_transport_principal_admission_json(validated)


def _normalize_lifecycle_policy(value: object) -> dict[str, Any]:
    policy = _require_mapping(
        value,
        token="transport_principal_admission_lifecycle_policy_invalid_phase_1309",
    )
    accepted = _normalize_text_list(
        policy.get("accepted_credential_kinds"),
        token="transport_principal_admission_lifecycle_policy_invalid_phase_1309",
    )
    if not set(accepted) <= set(_DEFAULT_ACCEPTED_CREDENTIAL_KINDS):
        raise TransportPrincipalAdmissionSidecarError(
            "transport_principal_admission_lifecycle_policy_invalid_phase_1309",
            "accepted credential kinds must be a subset of the Phase 1309 defaults",
        )
    if policy.get("credential_issuer_public_authority") is not False:
        raise TransportPrincipalAdmissionSidecarError(
            "transport_principal_admission_lifecycle_policy_invalid_phase_1309",
            "credential issuer public authority must be false",
        )
    for key in ("credential_kind_admitted", "epoch_window_checked", "rotation_required_before_public_path"):
        if policy.get(key) is not True:
            raise TransportPrincipalAdmissionSidecarError(
                "transport_principal_admission_lifecycle_policy_invalid_phase_1309",
                "lifecycle policy booleans must remain true",
            )
    if policy.get("lifecycle_policy_scope") != "local_call_scope_only":
        raise TransportPrincipalAdmissionSidecarError(
            "transport_principal_admission_lifecycle_policy_invalid_phase_1309",
            "lifecycle policy scope is invalid",
        )
    return {
        "accepted_credential_kinds": accepted,
        "credential_issuer_public_authority": False,
        "credential_kind_admitted": True,
        "epoch_window_checked": True,
        "lifecycle_policy_scope": "local_call_scope_only",
        "rotation_required_before_public_path": True,
    }


def _normalize_state_checks(value: object) -> dict[str, Any]:
    state = _require_mapping(
        value,
        token="transport_principal_admission_state_checks_invalid_phase_1309",
    )
    true_keys = (
        "admission_key_checked",
        "ban_checked",
        "rate_limit_checked",
        "rate_limit_key_bound_to_transport_principal",
        "replay_checked",
        "revocation_checked",
    )
    for key in true_keys:
        if state.get(key) is not True:
            raise TransportPrincipalAdmissionSidecarError(
                "transport_principal_admission_state_checks_invalid_phase_1309",
                "state check booleans must remain true",
            )
    if state.get("public_persistent_state_activated") is not False:
        raise TransportPrincipalAdmissionSidecarError(
            "transport_principal_admission_state_checks_invalid_phase_1309",
            "public persistent state must remain false",
        )
    required_sources = {
        "ban_registry_source": "caller_supplied_local_collection",
        "rate_limit_state_source": "caller_supplied_local_collection",
        "replay_cache_source": "caller_supplied_local_collection",
        "revocation_registry_source": "caller_supplied_local_collection",
    }
    for key, expected in required_sources.items():
        if state.get(key) != expected:
            raise TransportPrincipalAdmissionSidecarError(
                "transport_principal_admission_state_checks_invalid_phase_1309",
                "state source is invalid",
            )
    ceiling = _require_local_rate_limit_ceiling(state.get("rate_limit_ceiling"))
    counter = _require_rate_limit_count(
        "rate_limit_counter",
        state.get("rate_limit_counter"),
    )
    if counter >= ceiling:
        raise TransportPrincipalAdmissionSidecarError(
            "transport_principal_admission_state_checks_invalid_phase_1310",
            "admitted decisions must remain below the local rate-limit ceiling",
        )
    return {
        "admission_key_checked": True,
        "ban_checked": True,
        "ban_registry_source": "caller_supplied_local_collection",
        "public_persistent_state_activated": False,
        "rate_limit_ceiling": ceiling,
        "rate_limit_checked": True,
        "rate_limit_counter": counter,
        "rate_limit_key_bound_to_transport_principal": True,
        "rate_limit_state_source": "caller_supplied_local_collection",
        "replay_cache_source": "caller_supplied_local_collection",
        "replay_checked": True,
        "revocation_checked": True,
        "revocation_registry_source": "caller_supplied_local_collection",
    }


def _normalize_fallback_policy(value: object) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise TransportPrincipalAdmissionSidecarError(
            "transport_principal_admission_fallback_policy_invalid_phase_1309",
            "fallback policy must be a mapping",
        )
    allowed_keys = set(_FALSE_FALLBACK_FLAGS) | {"rate_limit_identity_source"}
    if set(value) != allowed_keys:
        raise TransportPrincipalAdmissionSidecarError(
            "transport_principal_admission_fallback_policy_invalid_phase_1309",
            "fallback policy keys are invalid",
        )
    policy: dict[str, bool] = {}
    for key in _FALSE_FALLBACK_FLAGS:
        if value.get(key) is not False:
            raise TransportPrincipalAdmissionSidecarError(
                "transport_principal_admission_fallback_policy_invalid_phase_1309",
                f"{key} must be false",
            )
        policy[key] = False
    if value.get("rate_limit_identity_source") != "authenticated_transport_principal":
        raise TransportPrincipalAdmissionSidecarError(
            "transport_principal_admission_fallback_policy_invalid_phase_1309",
            "fallback policy identity source is invalid",
        )
    return {**policy, "rate_limit_identity_source": "authenticated_transport_principal"}


def _normalize_false_flag_mapping(
    value: object,
    *,
    required_keys: tuple[str, ...],
    token: str,
) -> dict[str, bool]:
    flags = _require_mapping(value, token=token)
    if set(flags) != set(required_keys):
        raise TransportPrincipalAdmissionSidecarError(token, "false-flag mapping keys are invalid")
    normalized: dict[str, bool] = {}
    for key in required_keys:
        if flags.get(key) is not False:
            raise TransportPrincipalAdmissionSidecarError(token, f"{key} must be false")
        normalized[key] = False
    return normalized


def _normalize_exact_text_list(
    value: object,
    *,
    expected: Collection[str],
    token: str,
) -> list[str]:
    normalized = _normalize_text_list(value, token=token)
    expected_list = sorted(_require_text(item) for item in expected)
    if normalized != expected_list:
        raise TransportPrincipalAdmissionSidecarError(token, "text list does not match contract")
    return normalized


def _normalize_text_list(value: object, *, token: str) -> list[str]:
    if not isinstance(value, list):
        raise TransportPrincipalAdmissionSidecarError(token, "value must be a list")
    if len(value) > _MAX_COLLECTION_SIZE:
        raise TransportPrincipalAdmissionSidecarError(token, "list is too large")
    normalized = [_require_text(item) for item in value]
    if normalized != sorted(normalized) or len(set(normalized)) != len(normalized):
        raise TransportPrincipalAdmissionSidecarError(token, "list must be sorted and unique")
    return normalized


def _normalize_text_collection(value: object, *, token: str) -> tuple[str, ...]:
    if isinstance(value, (str, bytes, Mapping)) or not isinstance(value, Collection):
        raise TransportPrincipalAdmissionSidecarError(token, "value must be a bounded collection")
    if len(value) > _MAX_COLLECTION_SIZE:
        raise TransportPrincipalAdmissionSidecarError(token, "collection is too large")
    normalized = tuple(sorted({_require_text(item) for item in value}))
    return normalized


def _normalize_rate_limit_counters(value: object) -> dict[str, int]:
    if value is None:
        return {}
    if not isinstance(value, Mapping):
        raise TransportPrincipalAdmissionSidecarError(
            "transport_principal_admission_rate_limit_state_invalid_phase_1310",
            "rate-limit state must be a bounded mapping",
        )
    if len(value) > _MAX_COLLECTION_SIZE:
        raise TransportPrincipalAdmissionSidecarError(
            "transport_principal_admission_rate_limit_state_invalid_phase_1310",
            "rate-limit state is too large",
        )
    normalized: dict[str, int] = {}
    for key, count in value.items():
        normalized[_require_prefixed_digest("rate_limit_key", key, "tp_rate")] = (
            _require_rate_limit_count("rate_limit_count", count)
        )
    return dict(sorted(normalized.items()))


def _require_all_false(
    values: Mapping[str, object],
    *,
    default_token: str,
    token_by_name: Mapping[str, str] | None = None,
) -> None:
    custom = token_by_name or {}
    for name, value in values.items():
        if value is not False:
            token = custom.get(name, default_token)
            raise TransportPrincipalAdmissionSidecarError(token, f"{name} must be false")


def _require_mapping(value: object, *, token: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise TransportPrincipalAdmissionSidecarError(token, "value must be a mapping")
    return value


def _require_transport_principal_context_keys(value: Mapping[str, Any]) -> None:
    if set(value) != _EXPECTED_TRANSPORT_PRINCIPAL_CONTEXT_KEYS:
        raise TransportPrincipalAdmissionSidecarError(
            "transport_principal_admission_context_keys_invalid_phase_1310",
            "TransportPrincipal context keys do not match the pre-public contract",
        )


def _require_choice(name: str, value: object, *, allowed: Collection[str], token: str) -> str:
    text = _require_text(value)
    if text not in set(allowed):
        raise TransportPrincipalAdmissionSidecarError(token, f"{name} is not allowed")
    return text


def _require_epoch(name: str, value: object) -> int:
    if (
        not isinstance(value, int)
        or isinstance(value, bool)
        or value < 1
        or value > _MAX_PROTOCOL_INT
    ):
        raise TransportPrincipalAdmissionSidecarError(
            f"transport_principal_admission_{name}_epoch_invalid_phase_1309",
            f"{name} epoch must be a positive bounded integer",
        )
    return value


def _require_local_rate_limit_ceiling(value: object) -> int:
    ceiling = _require_rate_limit_count("rate_limit_ceiling", value)
    if ceiling > _MAX_RATE_LIMIT_COUNT:
        raise TransportPrincipalAdmissionSidecarError(
            "transport_principal_admission_rate_limit_ceiling_invalid_phase_1310",
            "local rate-limit ceiling is too large",
        )
    return ceiling


def _require_rate_limit_count(name: str, value: object) -> int:
    if (
        not isinstance(value, int)
        or isinstance(value, bool)
        or value < 0
        or value > _MAX_RATE_LIMIT_COUNT
    ):
        raise TransportPrincipalAdmissionSidecarError(
            "transport_principal_admission_rate_limit_state_invalid_phase_1310",
            f"{name} must be a non-negative bounded integer",
        )
    return value


def _require_text(value: object) -> str:
    if not isinstance(value, str) or not value or value != value.strip():
        raise TransportPrincipalAdmissionSidecarError(
            "transport_principal_admission_text_invalid_phase_1309",
            "text value is invalid",
        )
    if len(value) > _MAX_TEXT_LENGTH:
        raise TransportPrincipalAdmissionSidecarError(
            "transport_principal_admission_text_too_large_phase_1309",
            "text value is too large",
        )
    if any(ord(char) < 0x20 for char in value):
        raise TransportPrincipalAdmissionSidecarError(
            "transport_principal_admission_text_invalid_phase_1309",
            "text value contains a control character",
        )
    return value


def _require_hex_digest(name: str, value: object) -> str:
    if (
        not isinstance(value, str)
        or len(value) != _HEX_DIGEST_LENGTH
        or any(char not in _HEX for char in value)
    ):
        raise TransportPrincipalAdmissionSidecarError(
            f"transport_principal_admission_{name}_invalid_phase_1309",
            f"{name} must be a lowercase sha256 hex digest",
        )
    return value


def _require_prefixed_digest(name: str, value: object, prefix: str) -> str:
    expected_prefix = f"{prefix}:"
    if not isinstance(value, str) or not value.startswith(expected_prefix):
        raise TransportPrincipalAdmissionSidecarError(
            f"transport_principal_admission_{name}_invalid_phase_1309",
            f"{name} must use {expected_prefix}",
        )
    _require_hex_digest(name, value[len(expected_prefix) :])
    return value


def _sha256_payload(value: Mapping[str, Any]) -> str:
    return hashlib.sha256(canonical_transport_principal_admission_json(value).encode("utf-8")).hexdigest()


def _reject_forbidden_context_keys(value: object) -> None:
    if isinstance(value, Mapping):
        for key, item in value.items():
            if key in _FORBIDDEN_CONTEXT_KEYS:
                raise TransportPrincipalAdmissionSidecarError(
                    "transport_principal_admission_forbidden_identity_context_key_phase_1310",
                    "TransportPrincipal context includes a forbidden fallback or privacy key",
                )
            _reject_forbidden_context_keys(item)
        return
    if isinstance(value, list):
        for item in value:
            _reject_forbidden_context_keys(item)


def _reject_unsafe_json_tree(
    value: object,
    *,
    _depth: int = 0,
    _seen: set[int] | None = None,
    _counter: list[int] | None = None,
) -> None:
    if _depth > _MAX_PAYLOAD_DEPTH:
        raise TransportPrincipalAdmissionSidecarError(
            "transport_principal_admission_payload_too_deep_phase_1309",
            "payload nesting is too deep",
        )
    if _seen is None:
        _seen = set()
    if _counter is None:
        _counter = [0]
    _counter[0] += 1
    if _counter[0] > _MAX_PAYLOAD_NODES:
        raise TransportPrincipalAdmissionSidecarError(
            "transport_principal_admission_payload_too_large_phase_1309",
            "payload has too many nodes",
        )
    if isinstance(value, float):
        raise TransportPrincipalAdmissionSidecarError(
            "transport_principal_admission_float_values_forbidden_phase_1309",
            "float values are not allowed in admission payloads",
        )
    if isinstance(value, bool):
        return
    if isinstance(value, int):
        if value < 0 or value > _MAX_PROTOCOL_INT:
            raise TransportPrincipalAdmissionSidecarError(
                "transport_principal_admission_payload_int_invalid_phase_1309",
                "integer values must be non-negative and bounded",
            )
        return
    if isinstance(value, Mapping):
        object_id = id(value)
        if object_id in _seen:
            raise TransportPrincipalAdmissionSidecarError(
                "transport_principal_admission_payload_cycle_forbidden_phase_1309",
                "mapping cycle is not allowed",
            )
        _seen.add(object_id)
        try:
            for key, item in value.items():
                if not isinstance(key, str):
                    raise TransportPrincipalAdmissionSidecarError(
                        "transport_principal_admission_payload_key_invalid_phase_1309",
                        "mapping keys must be strings",
                    )
                _require_text(key)
                _counter[0] += 1
                if _counter[0] > _MAX_PAYLOAD_NODES:
                    raise TransportPrincipalAdmissionSidecarError(
                        "transport_principal_admission_payload_too_large_phase_1309",
                        "payload has too many nodes",
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
    if isinstance(value, tuple):
        raise TransportPrincipalAdmissionSidecarError(
            "transport_principal_admission_tuple_values_forbidden_phase_1309",
            "tuple values are not canonical JSON",
        )
    if isinstance(value, list):
        object_id = id(value)
        if object_id in _seen:
            raise TransportPrincipalAdmissionSidecarError(
                "transport_principal_admission_payload_cycle_forbidden_phase_1309",
                "list cycle is not allowed",
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
    if isinstance(value, str):
        _require_text(value)
        return
    if value is None:
        return
    raise TransportPrincipalAdmissionSidecarError(
        "transport_principal_admission_payload_type_invalid_phase_1310",
        "payload contains a non-JSON value type",
    )


__all__ = [
    "ADMISSION_DECISION_STATE",
    "ADMITTED_LOCAL_ONLY_DECISION",
    "PHASE_1310_NEXT_TOKEN",
    "PHASE_1311_NEXT_TOKEN",
    "PUBLIC_P2P_NOT_ACTIVATED_TOKEN",
    "PUBLIC_RC_REMAINS_BLOCKED_AFTER_PHASE_1310_TOKEN",
    "PUBLIC_RC_REMAINS_BLOCKED_AFTER_PHASE_1309_TOKEN",
    "ADMISSION_BAN_RATE_PRIVACY_TESTS_HARDENED_PHASE_1310_TOKEN",
    "HOSTILE_NETWORK_PUBLIC_PATH_STILL_BLOCKED_PHASE_1310_TOKEN",
    "REVOCATION_REPLAY_ADMISSION_BAN_TESTS_PHASE_1310_VERSION",
    "TRANSPORT_PRINCIPAL_ADMISSION_DECISION_REF_PREFIX",
    "TRANSPORT_PRINCIPAL_ADMISSION_SIDECAR_VERSION",
    "TRANSPORT_PRINCIPAL_LIFECYCLE_POLICY_LOCAL_SUBSTRATE_TOKEN",
    "TRANSPORT_PRINCIPAL_PUBLIC_PATH_NOT_ACTIVATED_TOKEN",
    "TRANSPORT_PRINCIPAL_REVOCATION_REPLAY_TESTS_HARDENED_PHASE_1310_TOKEN",
    "TransportPrincipalAdmissionSidecarError",
    "build_transport_principal_admission_decision",
    "canonical_transport_principal_admission_json",
    "export_transport_principal_admission_decision_json",
    "transport_principal_admission_decision_ref",
    "transport_principal_admission_required_tokens",
    "transport_principal_admission_sidecar_manifest",
    "transport_principal_hostile_network_required_tokens",
    "validate_transport_principal_admission_decision",
]
