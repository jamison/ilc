# SPDX-License-Identifier: AGPL-3.0-only
"""Phase 1436 public-path activation gates.

This module does not create listeners. It validates that a caller already has
explicit Phase 1436 authority, Gap 14 package-profile closure, CDL-094
TransportPrincipal authority, and an authenticated TransportPrincipal context
before a runtime may bind non-loopback sidecar/projection or public fetch paths.
"""

from __future__ import annotations

import hashlib
import ipaddress
import json
from collections.abc import Mapping
from typing import Any

from ilc_core.distribution.package_profiles import GAP_14_CLOSED_TOKEN
from ilc_core.network.d2d.openclaw_p2p_relay import (
    ECU_DISTRIBUTION_NOT_ACTIVATED_TOKEN as PHASE_1437_ECU_DISTRIBUTION_NOT_ACTIVATED_TOKEN,
    EPOCH_TRANSITION_NOT_TRIGGERED_TOKEN as PHASE_1437_EPOCH_TRANSITION_NOT_TRIGGERED_TOKEN,
    NATIVE_RUST_P2P_DEFERRED_WINDOW_1459_PLUS_TOKEN,
    NATIVE_RUST_P2P_NOT_ACTIVATED_TOKEN,
    OPENCLAW_GATEWAY_NOT_PUBLICLY_ACTIVATED_TOKEN,
    OPENCLAW_HARNESS_ASSISTED_P2P_ACTIVE_TOKEN,
    OPENCLAW_HARNESS_P2P_ACTIVATED_TOKEN,
    OPENCLAW_P2P_ACTIVATED_TOKEN,
    PUBLIC_RC_NOT_ACTIVATED_TOKEN,
    REHEARSAL_OPENCLAW_PATH_VALIDATED_GATE_TOKEN,
)
from ilc_core.network.d2d.transport_principal_pre_public_path import (
    validate_transport_principal_context,
)


PUBLIC_PATH_ACTIVATION_VERSION = "public_path_activation_phase_1436.v0.1"
NON_LOOPBACK_SIDECAR_PROJECTION_ACTIVATED_TOKEN = (
    "non_loopback_sidecar_projection_activated_phase_1436"
)
PUBLIC_FETCH_SERVING_ACTIVATED_TOKEN = "public_fetch_serving_activated_phase_1436"
TRANSPORT_PRINCIPAL_CDL_RATIFIED_GATE_WIRED_TOKEN = (
    "transport_principal_cdl_ratified_gate_wired_phase_1436"
)
GAP_14_COMPLETE_GATE_WIRED_TOKEN = "gap_14_complete_gate_wired_phase_1436"
OPENCLAW_P2P_NOT_ACTIVATED_TOKEN = "openclaw_p2p_not_activated_phase_1436"
NATIVE_RUST_P2P_ACTIVATED_TOKEN = "native_rust_p2p_activated_GAP_P2P_ACTIVATE_00"
ECU_DISTRIBUTION_NOT_ACTIVATED_TOKEN = "ecu_distribution_not_activated_phase_1436"
EPOCH_TRANSITION_NOT_TRIGGERED_TOKEN = "epoch_transition_not_triggered_phase_1436"
TRANSPORT_PRINCIPAL_CDL_RATIFIED_PHASE_1435_TOKEN = (
    "transport_principal_cdl_ratified_phase_1435"
)

TRANSPORT_PRINCIPAL_CDL_RATIFIED = True
PUBLIC_FETCH_SERVING_ACTIVATED = True
NON_LOOPBACK_SIDECAR_PROJECTION_ACTIVATED = True
OPENCLAW_P2P_ACTIVATED = True
ECU_DISTRIBUTION_ACTIVATED = False
EPOCH_TRANSITION_TRIGGERED = False
PUBLIC_P2P_ACTIVATED = True
PUBLIC_CONFIDENTIAL_COORDINATION_ACTIVATED = False

PUBLIC_PATH_DEFAULT_TIMEOUT_SECONDS = 5
PUBLIC_PATH_MAX_INBOUND_BYTES = 65_536
PUBLIC_PATH_MAX_RATE_COUNTERS = 10_000
PUBLIC_PATH_DEFAULT_RATE_LIMIT_CEILING = 1_000
PUBLIC_PATH_MAX_DECISION_BYTES = 1_000_000

PUBLIC_PATH_SURFACE_PUBLIC_FETCH = "public_fetch"
PUBLIC_PATH_SURFACE_SIDECAR_PROJECTION = "sidecar_projection"
PUBLIC_PATH_SURFACES = frozenset(
    {
        PUBLIC_PATH_SURFACE_PUBLIC_FETCH,
        PUBLIC_PATH_SURFACE_SIDECAR_PROJECTION,
    }
)

_HEX_DIGEST_LENGTH = 64
_HEX = frozenset("0123456789abcdef")
_MAX_PAYLOAD_DEPTH = 32
_MAX_PAYLOAD_NODES = 100_000
_REQUIRED_TOKENS = (
    PUBLIC_PATH_ACTIVATION_VERSION,
    NON_LOOPBACK_SIDECAR_PROJECTION_ACTIVATED_TOKEN,
    PUBLIC_FETCH_SERVING_ACTIVATED_TOKEN,
    TRANSPORT_PRINCIPAL_CDL_RATIFIED_GATE_WIRED_TOKEN,
    GAP_14_COMPLETE_GATE_WIRED_TOKEN,
    OPENCLAW_P2P_ACTIVATED_TOKEN,
    OPENCLAW_HARNESS_P2P_ACTIVATED_TOKEN,
    OPENCLAW_HARNESS_ASSISTED_P2P_ACTIVE_TOKEN,
    NATIVE_RUST_P2P_ACTIVATED_TOKEN,
    OPENCLAW_GATEWAY_NOT_PUBLICLY_ACTIVATED_TOKEN,
    REHEARSAL_OPENCLAW_PATH_VALIDATED_GATE_TOKEN,
    PUBLIC_RC_NOT_ACTIVATED_TOKEN,
    ECU_DISTRIBUTION_NOT_ACTIVATED_TOKEN,
    EPOCH_TRANSITION_NOT_TRIGGERED_TOKEN,
    PHASE_1437_ECU_DISTRIBUTION_NOT_ACTIVATED_TOKEN,
    PHASE_1437_EPOCH_TRANSITION_NOT_TRIGGERED_TOKEN,
    TRANSPORT_PRINCIPAL_CDL_RATIFIED_PHASE_1435_TOKEN,
    GAP_14_CLOSED_TOKEN,
)
_DECISION_KEYS = frozenset(
    {
        "activation_decision_sha256",
        "allowed",
        "bind_host",
        "current_epoch",
        "decision_scope",
        "ecu_distribution_activated",
        "epoch_transition_triggered",
        "gap_14_closed",
        "non_loopback_bind",
        "non_loopback_sidecar_projection_enabled",
        "openclaw_p2p_activated",
        "principal_id",
        "public_confidential_coordination_activated",
        "public_fetch_serving_enabled",
        "public_p2p_activated",
        "rate_limit_ceiling",
        "rate_limit_counter",
        "rate_limit_identity_source",
        "rate_limit_key",
        "rate_limit_window_basis",
        "request_timeout_seconds",
        "requester_id_fallback_allowed",
        "surface",
        "tokens",
        "transport_principal_cdl_ratified",
        "transport_principal_context_tokens",
        "transport_principal_context_version",
        "version",
    }
)


class PublicPathActivationError(ValueError):
    """Fail-closed public-path activation error with a stable token."""

    def __init__(self, token: str, message: str) -> None:
        super().__init__(f"{token}: {message}")
        self.token = token


def public_path_activation_required_tokens() -> tuple[str, ...]:
    """Return current public-path activation and non-activation tokens."""

    return _REQUIRED_TOKENS


def public_path_activation_manifest() -> dict[str, Any]:
    """Return side-effect-free Phase 1436 activation metadata."""

    return {
        "ecu_distribution_activated": ECU_DISTRIBUTION_ACTIVATED,
        "epoch_transition_triggered": EPOCH_TRANSITION_TRIGGERED,
        "gap_14_closed_token": GAP_14_CLOSED_TOKEN,
        "non_loopback_sidecar_projection_activated": (
            NON_LOOPBACK_SIDECAR_PROJECTION_ACTIVATED
        ),
        "openclaw_p2p_activated": OPENCLAW_P2P_ACTIVATED,
        "public_confidential_coordination_activated": (
            PUBLIC_CONFIDENTIAL_COORDINATION_ACTIVATED
        ),
        "public_fetch_serving_activated": PUBLIC_FETCH_SERVING_ACTIVATED,
        "public_p2p_activated": PUBLIC_P2P_ACTIVATED,
        "request_timeout_seconds": PUBLIC_PATH_DEFAULT_TIMEOUT_SECONDS,
        "tokens": public_path_activation_required_tokens(),
        "transport_principal_cdl_ratified": TRANSPORT_PRINCIPAL_CDL_RATIFIED,
        "version": PUBLIC_PATH_ACTIVATION_VERSION,
    }


def is_loopback_bind_host(bind_host: str) -> bool:
    """Return True only for explicit loopback hostnames or addresses."""

    host = _require_bind_host(bind_host)
    normalized = host.strip().lower()
    if normalized == "localhost":
        return True
    if normalized.startswith("[") and normalized.endswith("]"):
        normalized = normalized[1:-1]
    try:
        return ipaddress.ip_address(normalized).is_loopback
    except ValueError:
        return False


def authorize_public_fetch_serving(
    *,
    bind_host: str,
    transport_principal_context: Mapping[str, Any],
    current_epoch: int,
    rate_limit_counters: Mapping[str, int] | None = None,
    rate_limit_ceiling: int = PUBLIC_PATH_DEFAULT_RATE_LIMIT_CEILING,
) -> dict[str, Any]:
    """Authorize Phase 1436 public fetch serving for a non-loopback bind."""

    return build_public_path_activation_decision(
        surface=PUBLIC_PATH_SURFACE_PUBLIC_FETCH,
        bind_host=bind_host,
        transport_principal_context=transport_principal_context,
        current_epoch=current_epoch,
        rate_limit_counters=rate_limit_counters,
        rate_limit_ceiling=rate_limit_ceiling,
    )


def authorize_non_loopback_sidecar_projection(
    *,
    bind_host: str,
    transport_principal_context: Mapping[str, Any],
    current_epoch: int,
    rate_limit_counters: Mapping[str, int] | None = None,
    rate_limit_ceiling: int = PUBLIC_PATH_DEFAULT_RATE_LIMIT_CEILING,
) -> dict[str, Any]:
    """Authorize Phase 1436 non-loopback sidecar/projection serving."""

    return build_public_path_activation_decision(
        surface=PUBLIC_PATH_SURFACE_SIDECAR_PROJECTION,
        bind_host=bind_host,
        transport_principal_context=transport_principal_context,
        current_epoch=current_epoch,
        rate_limit_counters=rate_limit_counters,
        rate_limit_ceiling=rate_limit_ceiling,
    )


def build_public_path_activation_decision(
    *,
    surface: str,
    bind_host: str,
    transport_principal_context: Mapping[str, Any],
    current_epoch: int,
    rate_limit_counters: Mapping[str, int] | None = None,
    rate_limit_ceiling: int = PUBLIC_PATH_DEFAULT_RATE_LIMIT_CEILING,
) -> dict[str, Any]:
    """Build and validate a Phase 1436 public-path activation decision."""

    active_surface = _require_surface(surface)
    host = _require_bind_host(bind_host)
    current = _require_epoch("current", current_epoch)
    if is_loopback_bind_host(host):
        raise PublicPathActivationError(
            "public_path_non_loopback_bind_required_phase_1436",
            "Phase 1436 activation decisions are for non-loopback public paths",
        )
    if not TRANSPORT_PRINCIPAL_CDL_RATIFIED:
        raise PublicPathActivationError(
            "transport_principal_cdl_not_ratified_phase_1436",
            "CDL-094 TransportPrincipal gate is not ratified",
        )
    if GAP_14_CLOSED_TOKEN != "gap_14_closed_phase_1436b":
        raise PublicPathActivationError(
            "gap_14_not_closed_phase_1436",
            "Gap 14 package-profile gate is not closed",
        )
    validated_context = validate_transport_principal_context(
        transport_principal_context,
        current_epoch=current,
    )
    ceiling = _require_positive_int("rate_limit_ceiling", rate_limit_ceiling)
    counters = _normalize_rate_limit_counters(rate_limit_counters)
    rate_limit_key = _require_text("rate_limit_key", validated_context["rate_limit_key"])
    counter = counters.get(rate_limit_key, 0)
    if counter >= ceiling:
        raise PublicPathActivationError(
            "public_path_rate_limit_exceeded_phase_1436",
            "TransportPrincipal rate-limit counter exceeds the Phase 1436 ceiling",
        )

    body = {
        "allowed": True,
        "bind_host": host,
        "current_epoch": current,
        "decision_scope": "phase_1436_public_path_activation",
        "ecu_distribution_activated": False,
        "epoch_transition_triggered": False,
        "gap_14_closed": True,
        "non_loopback_bind": True,
        "non_loopback_sidecar_projection_enabled": (
            active_surface == PUBLIC_PATH_SURFACE_SIDECAR_PROJECTION
        ),
        "openclaw_p2p_activated": OPENCLAW_P2P_ACTIVATED,
        "principal_id": validated_context["principal_id"],
        "public_confidential_coordination_activated": False,
        "public_fetch_serving_enabled": active_surface == PUBLIC_PATH_SURFACE_PUBLIC_FETCH,
        "public_p2p_activated": PUBLIC_P2P_ACTIVATED,
        "rate_limit_ceiling": ceiling,
        "rate_limit_counter": counter,
        "rate_limit_identity_source": "authenticated_transport_principal",
        "rate_limit_key": rate_limit_key,
        "rate_limit_window_basis": "epoch_sequence",
        "request_timeout_seconds": PUBLIC_PATH_DEFAULT_TIMEOUT_SECONDS,
        "requester_id_fallback_allowed": False,
        "surface": active_surface,
        "tokens": sorted(_REQUIRED_TOKENS),
        "transport_principal_cdl_ratified": True,
        "transport_principal_context_tokens": list(validated_context["tokens"]),
        "transport_principal_context_version": validated_context["version"],
        "version": PUBLIC_PATH_ACTIVATION_VERSION,
    }
    decision = {"activation_decision_sha256": _sha256_payload(body), **body}
    return validate_public_path_activation_decision(
        decision,
        current_epoch=current,
        surface=active_surface,
    )


def validate_public_path_activation_decision(
    decision: Mapping[str, Any],
    *,
    current_epoch: int,
    surface: str | None = None,
) -> dict[str, Any]:
    """Validate a Phase 1436 public-path activation decision."""

    if not isinstance(decision, Mapping):
        raise PublicPathActivationError(
            "public_path_activation_decision_invalid_phase_1436",
            "activation decision must be a mapping",
        )
    _reject_float_values(decision)
    current = _require_epoch("current", current_epoch)
    payload = dict(decision)
    if set(payload) != _DECISION_KEYS:
        raise PublicPathActivationError(
            "public_path_activation_decision_keys_invalid_phase_1436",
            "activation decision keys do not match the Phase 1436 contract",
        )
    active_surface = _require_surface(payload.get("surface"))
    if surface is not None and active_surface != _require_surface(surface):
        raise PublicPathActivationError(
            "public_path_activation_surface_mismatch_phase_1436",
            "activation decision surface does not match caller expectation",
        )
    if payload.get("version") != PUBLIC_PATH_ACTIVATION_VERSION:
        raise PublicPathActivationError(
            "public_path_activation_version_invalid_phase_1436",
            "activation decision version is invalid",
        )
    if _require_epoch("current", payload.get("current_epoch")) != current:
        raise PublicPathActivationError(
            "public_path_activation_current_epoch_mismatch_phase_1436",
            "activation decision current epoch does not match caller epoch",
        )
    host = _require_bind_host(payload.get("bind_host"))
    if is_loopback_bind_host(host):
        raise PublicPathActivationError(
            "public_path_non_loopback_bind_required_phase_1436",
            "activation decision bind host must be non-loopback",
        )
    _require_true(payload.get("allowed"), "public_path_activation_allowed_invalid_phase_1436")
    _require_true(
        payload.get("gap_14_closed"),
        "public_path_activation_gap_14_closed_invalid_phase_1436",
    )
    _require_true(
        payload.get("non_loopback_bind"),
        "public_path_activation_non_loopback_bind_invalid_phase_1436",
    )
    _require_true(
        payload.get("transport_principal_cdl_ratified"),
        "public_path_activation_cdl_094_gate_invalid_phase_1436",
    )
    _require_true(
        payload.get("openclaw_p2p_activated"),
        OPENCLAW_HARNESS_P2P_ACTIVATED_TOKEN,
    )
    _require_true(payload.get("public_p2p_activated"), NATIVE_RUST_P2P_ACTIVATED_TOKEN)
    _require_false(
        payload.get("public_confidential_coordination_activated"),
        "public_confidential_coordination_not_activated_phase_1436",
    )
    _require_false(payload.get("ecu_distribution_activated"), ECU_DISTRIBUTION_NOT_ACTIVATED_TOKEN)
    _require_false(payload.get("epoch_transition_triggered"), EPOCH_TRANSITION_NOT_TRIGGERED_TOKEN)
    _require_false(
        payload.get("requester_id_fallback_allowed"),
        "public_path_requester_id_fallback_forbidden_phase_1436",
    )
    fetch_enabled = _require_bool(
        payload.get("public_fetch_serving_enabled"),
        "public_path_activation_fetch_flag_invalid_phase_1436",
    )
    sidecar_enabled = _require_bool(
        payload.get("non_loopback_sidecar_projection_enabled"),
        "public_path_activation_sidecar_flag_invalid_phase_1436",
    )
    if active_surface == PUBLIC_PATH_SURFACE_PUBLIC_FETCH:
        _require_true(fetch_enabled, PUBLIC_FETCH_SERVING_ACTIVATED_TOKEN)
        _require_false(
            sidecar_enabled,
            "sidecar_projection_not_enabled_for_public_fetch_phase_1436",
        )
    else:
        _require_true(sidecar_enabled, NON_LOOPBACK_SIDECAR_PROJECTION_ACTIVATED_TOKEN)
        _require_false(
            fetch_enabled,
            "public_fetch_not_enabled_for_sidecar_projection_phase_1436",
        )
    tokens = _normalize_exact_tokens(payload.get("tokens"), expected=_REQUIRED_TOKENS)
    context_tokens = _normalize_text_list(payload.get("transport_principal_context_tokens"))
    rate_limit_key = _require_text("rate_limit_key", payload.get("rate_limit_key"))
    rate_limit_ceiling = _require_positive_int(
        "rate_limit_ceiling",
        payload.get("rate_limit_ceiling"),
    )
    rate_limit_counter = _require_non_negative_int(
        "rate_limit_counter",
        payload.get("rate_limit_counter"),
    )
    if rate_limit_counter >= rate_limit_ceiling:
        raise PublicPathActivationError(
            "public_path_activation_rate_limit_counter_invalid_phase_1436",
            "validated decisions must remain below the rate-limit ceiling",
        )
    if payload.get("rate_limit_identity_source") != "authenticated_transport_principal":
        raise PublicPathActivationError(
            "public_path_activation_rate_limit_identity_source_invalid_phase_1436",
            "rate-limit identity must be the authenticated TransportPrincipal",
        )
    if payload.get("rate_limit_window_basis") != "epoch_sequence":
        raise PublicPathActivationError(
            "public_path_activation_rate_limit_window_invalid_phase_1436",
            "rate-limit window basis must be epoch sequence",
        )
    timeout = _require_positive_int(
        "request_timeout_seconds",
        payload.get("request_timeout_seconds"),
    )
    principal_id = _require_text("principal_id", payload.get("principal_id"))
    context_version = _require_text(
        "transport_principal_context_version",
        payload.get("transport_principal_context_version"),
    )

    normalized = {
        "activation_decision_sha256": _require_hex_digest(
            "activation_decision_sha256",
            payload.get("activation_decision_sha256"),
        ),
        "allowed": True,
        "bind_host": host,
        "current_epoch": current,
        "decision_scope": "phase_1436_public_path_activation",
        "ecu_distribution_activated": False,
        "epoch_transition_triggered": False,
        "gap_14_closed": True,
        "non_loopback_bind": True,
        "non_loopback_sidecar_projection_enabled": sidecar_enabled,
        "openclaw_p2p_activated": OPENCLAW_P2P_ACTIVATED,
        "principal_id": principal_id,
        "public_confidential_coordination_activated": False,
        "public_fetch_serving_enabled": fetch_enabled,
        "public_p2p_activated": True,
        "rate_limit_ceiling": rate_limit_ceiling,
        "rate_limit_counter": rate_limit_counter,
        "rate_limit_identity_source": "authenticated_transport_principal",
        "rate_limit_key": rate_limit_key,
        "rate_limit_window_basis": "epoch_sequence",
        "request_timeout_seconds": timeout,
        "requester_id_fallback_allowed": False,
        "surface": active_surface,
        "tokens": tokens,
        "transport_principal_cdl_ratified": True,
        "transport_principal_context_tokens": context_tokens,
        "transport_principal_context_version": context_version,
        "version": PUBLIC_PATH_ACTIVATION_VERSION,
    }
    expected_hash_body = dict(normalized)
    actual_hash = expected_hash_body.pop("activation_decision_sha256")
    if actual_hash != _sha256_payload(expected_hash_body):
        raise PublicPathActivationError(
            "public_path_activation_decision_hash_mismatch_phase_1436",
            "activation decision hash does not match canonical body",
        )
    return normalized


def export_public_path_activation_decision_json(decision: Mapping[str, Any]) -> str:
    """Export a Phase 1436 activation decision as canonical JSON."""

    if not isinstance(decision, Mapping):
        raise PublicPathActivationError(
            "public_path_activation_decision_invalid_phase_1436",
            "activation decision must be a mapping",
        )
    current = _require_epoch("current", decision.get("current_epoch"))
    validated = validate_public_path_activation_decision(decision, current_epoch=current)
    return _canonical_json(validated)


def _canonical_json(value: Mapping[str, Any]) -> str:
    _reject_float_values(value)
    payload = json.dumps(value, allow_nan=False, separators=(",", ":"), sort_keys=True)
    if len(payload.encode("utf-8")) > PUBLIC_PATH_MAX_DECISION_BYTES:
        raise PublicPathActivationError(
            "public_path_activation_decision_size_exceeded_phase_1436",
            "activation decision exceeds byte bound",
        )
    return payload


def _sha256_payload(value: Mapping[str, Any]) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _require_surface(value: Any) -> str:
    if not isinstance(value, str):
        raise PublicPathActivationError(
            "public_path_activation_surface_invalid_phase_1436",
            "surface must be text",
        )
    normalized = value.strip().lower()
    if normalized not in PUBLIC_PATH_SURFACES:
        raise PublicPathActivationError(
            "public_path_activation_surface_invalid_phase_1436",
            "surface is not in the Phase 1436 public-path surface set",
        )
    return normalized


def _require_bind_host(value: Any) -> str:
    if not isinstance(value, str) or not value.strip():
        raise PublicPathActivationError(
            "public_path_bind_host_invalid_phase_1436",
            "bind host must be non-empty text",
        )
    return value.strip()


def _require_epoch(name: str, value: Any) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise PublicPathActivationError(
            f"public_path_activation_{name}_epoch_invalid_phase_1436",
            "epoch values must be non-negative integers",
        )
    return value


def _require_text(name: str, value: Any) -> str:
    if not isinstance(value, str) or not value.strip():
        raise PublicPathActivationError(
            f"public_path_activation_{name}_invalid_phase_1436",
            "text field must be non-empty",
        )
    return value


def _require_bool(value: Any, token: str) -> bool:
    if not isinstance(value, bool):
        raise PublicPathActivationError(token, "boolean field is invalid")
    return value


def _require_true(value: Any, token: str) -> bool:
    if value is not True:
        raise PublicPathActivationError(token, "required true field is not true")
    return True


def _require_false(value: Any, token: str) -> bool:
    if value is not False:
        raise PublicPathActivationError(token, "required false field is not false")
    return False


def _require_positive_int(name: str, value: Any) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
        raise PublicPathActivationError(
            f"public_path_activation_{name}_invalid_phase_1436",
            "value must be a positive integer",
        )
    return value


def _require_non_negative_int(name: str, value: Any) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise PublicPathActivationError(
            f"public_path_activation_{name}_invalid_phase_1436",
            "value must be a non-negative integer",
        )
    return value


def _require_hex_digest(name: str, value: Any) -> str:
    if (
        not isinstance(value, str)
        or len(value) != _HEX_DIGEST_LENGTH
        or any(char not in _HEX for char in value)
    ):
        raise PublicPathActivationError(
            f"public_path_activation_{name}_invalid_phase_1436",
            "hex digest is invalid",
        )
    return value


def _normalize_rate_limit_counters(value: Mapping[str, int] | None) -> dict[str, int]:
    if value is None:
        return {}
    if not isinstance(value, Mapping):
        raise PublicPathActivationError(
            "public_path_activation_rate_counters_invalid_phase_1436",
            "rate-limit counters must be a mapping",
        )
    if len(value) > PUBLIC_PATH_MAX_RATE_COUNTERS:
        raise PublicPathActivationError(
            "public_path_activation_rate_counters_too_large_phase_1436",
            "rate-limit counter mapping exceeds bound",
        )
    counters: dict[str, int] = {}
    for key, count in value.items():
        counters[_require_text("rate_limit_counter_key", key)] = _require_non_negative_int(
            "rate_limit_counter",
            count,
        )
    return counters


def _normalize_exact_tokens(value: Any, *, expected: tuple[str, ...]) -> list[str]:
    tokens = _normalize_text_list(value)
    if tuple(tokens) != tuple(sorted(expected)):
        raise PublicPathActivationError(
            "public_path_activation_tokens_invalid_phase_1436",
            "activation decision tokens do not match Phase 1436 requirements",
        )
    return tokens


def _normalize_text_list(value: Any) -> list[str]:
    if not isinstance(value, (list, tuple)) or not all(
        isinstance(item, str) and item for item in value
    ):
        raise PublicPathActivationError(
            "public_path_activation_text_list_invalid_phase_1436",
            "text list is invalid",
        )
    return list(value)


def _reject_float_values(
    value: Any,
    *,
    _depth: int = 0,
    _seen: set[int] | None = None,
    _counter: list[int] | None = None,
) -> None:
    if _depth > _MAX_PAYLOAD_DEPTH:
        raise PublicPathActivationError(
            "public_path_activation_payload_too_deep_phase_1436",
            "payload nesting exceeds bound",
        )
    if _seen is None:
        _seen = set()
    if _counter is None:
        _counter = [0]
    _counter[0] += 1
    if _counter[0] > _MAX_PAYLOAD_NODES:
        raise PublicPathActivationError(
            "public_path_activation_payload_too_large_phase_1436",
            "payload node count exceeds bound",
        )
    if isinstance(value, float):
        raise PublicPathActivationError(
            "public_path_activation_float_values_forbidden_phase_1436",
            "float values are forbidden in activation decisions",
        )
    if isinstance(value, Mapping):
        object_id = id(value)
        if object_id in _seen:
            raise PublicPathActivationError(
                "public_path_activation_payload_cycle_forbidden_phase_1436",
                "payload cycles are forbidden",
            )
        _seen.add(object_id)
        try:
            for key, item in value.items():
                if not isinstance(key, str):
                    raise PublicPathActivationError(
                        "public_path_activation_payload_key_invalid_phase_1436",
                        "payload keys must be text",
                    )
                _reject_float_values(
                    item,
                    _depth=_depth + 1,
                    _seen=_seen,
                    _counter=_counter,
                )
        finally:
            _seen.remove(object_id)
        return
    if isinstance(value, (list, tuple)):
        object_id = id(value)
        if object_id in _seen:
            raise PublicPathActivationError(
                "public_path_activation_payload_cycle_forbidden_phase_1436",
                "payload cycles are forbidden",
            )
        _seen.add(object_id)
        try:
            for item in value:
                _reject_float_values(
                    item,
                    _depth=_depth + 1,
                    _seen=_seen,
                    _counter=_counter,
                )
        finally:
            _seen.remove(object_id)
