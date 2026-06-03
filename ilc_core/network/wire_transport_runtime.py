# SPDX-License-Identifier: AGPL-3.0-only
"""Phase-323 wire transport generator/verifier runtime."""

from __future__ import annotations

import copy
import hashlib
import json
from typing import Any


WIRE_TRANSPORT_RUNTIME_VERSION = "wire_transport_runtime_323.v0.1"
SCHEMA_BASELINE_DEPENDENCY = "d2_schema_baseline_310.v0.1"
GENESIS_BUNDLE_DEPENDENCY = "genesis_state_bundle_312.v0.1"
EPOCH_SNAPSHOT_DEPENDENCY = "epoch_snapshot_runtime_314.v0.1"

ALLOWED_TRANSPORT_KINDS = ("http", "libp2p", "quic")
ALLOWED_DELIVERY_MODES = ("pubsub", "request_response", "stream")
ALLOWED_QOS_MODES = ("at_least_once", "at_most_once", "exactly_once")


CANONICAL_WIRE_TRANSPORT_VECTORS: list[dict[str, Any]] = [
    {
        "envelope": {
            "message_id": "msg-claim-1",
            "schema_ref": "d2.claim.v1",
            "content_type": "application/json",
            "headers": {
                "source": "agent-alpha",
                "topic": "claim.submit",
            },
            "payload": {
                "claim_id": "claim-a",
                "epoch": 10,
            },
        },
        "transport": {
            "kind": "quic",
            "delivery_mode": "request_response",
            "qos": "at_least_once",
            "retry_policy": {
                "max_retries": 2,
                "backoff_ms": 200,
            },
        },
    },
    {
        "envelope": {
            "message_id": "msg-edge-1",
            "schema_ref": "d2.edge.v1",
            "content_type": "application/json",
            "headers": {
                "source": "agent-beta",
                "topic": "edge.propagate",
            },
            "payload": {
                "edge_id": "edge-a",
                "source": "node-1",
                "target": "node-2",
            },
        },
        "transport": {
            "kind": "libp2p",
            "delivery_mode": "pubsub",
            "qos": "at_most_once",
            "retry_policy": {
                "max_retries": 0,
                "backoff_ms": 0,
            },
        },
    },
]


class WireTransportValidationError(ValueError):
    """Typed validation exception with deterministic error token."""

    def __init__(self, token: str, message: str) -> None:
        super().__init__(message)
        self.token = token
        self.message = message


def _stable_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def _stable_sha256(value: Any) -> str:
    return hashlib.sha256(_stable_json(value).encode("utf-8")).hexdigest()


def _sorted_mapping(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _sorted_mapping(value[key]) for key in sorted(value, key=str)}
    if isinstance(value, list):
        return [_sorted_mapping(item) for item in value]
    return value


def _normalize_headers(raw_headers: Any) -> dict[str, str]:
    if not isinstance(raw_headers, dict):
        raise WireTransportValidationError(
            "wire_transport_headers_not_object",
            "headers_not_object",
        )

    normalized: dict[str, str] = {}
    for key, value in raw_headers.items():
        if not isinstance(key, str) or not key.strip():
            raise WireTransportValidationError(
                "wire_transport_header_key_invalid",
                "header_key_invalid",
            )
        if not isinstance(value, str) or not value.strip():
            raise WireTransportValidationError(
                "wire_transport_header_value_invalid",
                f"header_value_invalid:{key}",
            )
        normalized[key] = value
    return {key: normalized[key] for key in sorted(normalized)}


def _normalize_envelope(raw_envelope: Any) -> dict[str, Any]:
    if not isinstance(raw_envelope, dict):
        raise WireTransportValidationError(
            "wire_transport_envelope_not_object",
            "envelope_not_object",
        )

    message_id = raw_envelope.get("message_id")
    if not isinstance(message_id, str) or not message_id.strip():
        raise WireTransportValidationError(
            "wire_transport_message_id_missing",
            "message_id_missing",
        )

    schema_ref = raw_envelope.get("schema_ref")
    if not isinstance(schema_ref, str) or not schema_ref.strip():
        raise WireTransportValidationError(
            "wire_transport_schema_ref_missing",
            f"schema_ref_missing:{message_id}",
        )

    content_type = raw_envelope.get("content_type")
    if not isinstance(content_type, str) or not content_type.strip():
        raise WireTransportValidationError(
            "wire_transport_content_type_missing",
            f"content_type_missing:{message_id}",
        )

    payload = raw_envelope.get("payload")
    if not isinstance(payload, dict):
        raise WireTransportValidationError(
            "wire_transport_payload_not_object",
            f"payload_not_object:{message_id}",
        )

    return {
        "content_type": content_type,
        "headers": _normalize_headers(raw_envelope.get("headers")),
        "message_id": message_id,
        "payload": _sorted_mapping(payload),
        "schema_ref": schema_ref,
    }


def _normalize_retry_policy(raw_policy: Any, *, message_id: str) -> dict[str, int]:
    if not isinstance(raw_policy, dict):
        raise WireTransportValidationError(
            "wire_transport_retry_policy_not_object",
            f"retry_policy_not_object:{message_id}",
        )

    max_retries = raw_policy.get("max_retries")
    if not isinstance(max_retries, int) or max_retries < 0:
        raise WireTransportValidationError(
            "wire_transport_retry_max_invalid",
            f"retry_max_invalid:{message_id}",
        )

    backoff_ms = raw_policy.get("backoff_ms")
    if not isinstance(backoff_ms, int) or backoff_ms < 0:
        raise WireTransportValidationError(
            "wire_transport_retry_backoff_invalid",
            f"retry_backoff_invalid:{message_id}",
        )

    return {
        "backoff_ms": backoff_ms,
        "max_retries": max_retries,
    }


def _normalize_transport(raw_transport: Any, *, message_id: str) -> dict[str, Any]:
    if not isinstance(raw_transport, dict):
        raise WireTransportValidationError(
            "wire_transport_transport_not_object",
            f"transport_not_object:{message_id}",
        )

    kind = raw_transport.get("kind")
    if not isinstance(kind, str) or kind not in ALLOWED_TRANSPORT_KINDS:
        raise WireTransportValidationError(
            "wire_transport_kind_invalid",
            f"transport_kind_invalid:{message_id}:{kind}",
        )

    delivery_mode = raw_transport.get("delivery_mode")
    if not isinstance(delivery_mode, str) or delivery_mode not in ALLOWED_DELIVERY_MODES:
        raise WireTransportValidationError(
            "wire_transport_delivery_mode_invalid",
            f"delivery_mode_invalid:{message_id}:{delivery_mode}",
        )

    qos = raw_transport.get("qos")
    if not isinstance(qos, str) or qos not in ALLOWED_QOS_MODES:
        raise WireTransportValidationError(
            "wire_transport_qos_invalid",
            f"qos_invalid:{message_id}:{qos}",
        )

    return {
        "delivery_mode": delivery_mode,
        "kind": kind,
        "qos": qos,
        "retry_policy": _normalize_retry_policy(raw_transport.get("retry_policy"), message_id=message_id),
    }


def _normalize_payload(payload: Any) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise WireTransportValidationError(
            "wire_transport_payload_record_not_object",
            "payload_record_not_object",
        )

    envelope = _normalize_envelope(payload.get("envelope"))
    transport = _normalize_transport(payload.get("transport"), message_id=envelope["message_id"])
    return {
        "envelope": envelope,
        "transport": transport,
    }


def generate_wire_transport_envelope(payload: dict[str, Any]) -> dict[str, Any]:
    """Generate deterministic wire transport envelope output."""

    normalized = _normalize_payload(payload)
    core = {
        "envelope": normalized["envelope"],
        "transport": normalized["transport"],
        "runtime_version": WIRE_TRANSPORT_RUNTIME_VERSION,
        "schema_dependency": SCHEMA_BASELINE_DEPENDENCY,
        "genesis_dependency": GENESIS_BUNDLE_DEPENDENCY,
        "epoch_dependency": EPOCH_SNAPSHOT_DEPENDENCY,
    }
    return {
        **core,
        "envelope_sha256": _stable_sha256(core),
    }


def verify_wire_transport_envelope(record: dict[str, Any]) -> dict[str, Any]:
    """Verify deterministic wire transport envelope output."""

    if not isinstance(record, dict):
        raise WireTransportValidationError(
            "wire_transport_record_not_object",
            "record_not_object",
        )

    runtime_version = record.get("runtime_version")
    if runtime_version != WIRE_TRANSPORT_RUNTIME_VERSION:
        raise WireTransportValidationError(
            "wire_transport_runtime_version_invalid",
            f"runtime_version_invalid:{runtime_version}",
        )

    schema_dependency = record.get("schema_dependency")
    if schema_dependency != SCHEMA_BASELINE_DEPENDENCY:
        raise WireTransportValidationError(
            "wire_transport_schema_dependency_invalid",
            f"schema_dependency_invalid:{schema_dependency}",
        )

    genesis_dependency = record.get("genesis_dependency")
    if genesis_dependency != GENESIS_BUNDLE_DEPENDENCY:
        raise WireTransportValidationError(
            "wire_transport_genesis_dependency_invalid",
            f"genesis_dependency_invalid:{genesis_dependency}",
        )

    epoch_dependency = record.get("epoch_dependency")
    if epoch_dependency != EPOCH_SNAPSHOT_DEPENDENCY:
        raise WireTransportValidationError(
            "wire_transport_epoch_dependency_invalid",
            f"epoch_dependency_invalid:{epoch_dependency}",
        )

    payload = {
        "envelope": record.get("envelope"),
        "transport": record.get("transport"),
    }
    regenerated = generate_wire_transport_envelope(payload)

    digest = record.get("envelope_sha256")
    if not isinstance(digest, str):
        raise WireTransportValidationError(
            "wire_transport_digest_missing",
            "envelope_sha256_missing",
        )
    if digest != regenerated["envelope_sha256"]:
        raise WireTransportValidationError(
            "wire_transport_digest_mismatch",
            "envelope_sha256_mismatch",
        )

    observed_core = {
        "envelope": record.get("envelope"),
        "transport": record.get("transport"),
        "runtime_version": runtime_version,
        "schema_dependency": schema_dependency,
        "genesis_dependency": genesis_dependency,
        "epoch_dependency": epoch_dependency,
    }
    expected_core = {
        "envelope": regenerated["envelope"],
        "transport": regenerated["transport"],
        "runtime_version": regenerated["runtime_version"],
        "schema_dependency": regenerated["schema_dependency"],
        "genesis_dependency": regenerated["genesis_dependency"],
        "epoch_dependency": regenerated["epoch_dependency"],
    }
    if _stable_json(_sorted_mapping(observed_core)) != _stable_json(_sorted_mapping(expected_core)):
        raise WireTransportValidationError(
            "wire_transport_not_canonical",
            "wire_transport_not_canonical"
        )

    return {
        "valid": True,
        "runtime_version": WIRE_TRANSPORT_RUNTIME_VERSION,
        "schema_dependency": SCHEMA_BASELINE_DEPENDENCY,
        "genesis_dependency": GENESIS_BUNDLE_DEPENDENCY,
        "epoch_dependency": EPOCH_SNAPSHOT_DEPENDENCY,
        "envelope_sha256": regenerated["envelope_sha256"],
        "checks": [
            {"check_type": "runtime_version_supported", "passed": True},
            {"check_type": "schema_dependency_locked", "passed": True},
            {"check_type": "genesis_dependency_locked", "passed": True},
            {"check_type": "epoch_dependency_locked", "passed": True},
            {"check_type": "transport_envelope_digest_matches", "passed": True},
        ],
    }


def canonical_wire_transport_vectors() -> list[dict[str, Any]]:
    """Return a copy of baseline canonical vectors for deterministic tests."""

    return copy.deepcopy(CANONICAL_WIRE_TRANSPORT_VECTORS)
