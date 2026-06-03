# SPDX-License-Identifier: AGPL-3.0-only
"""Phase-361 runtime for CDL-035 validation lifecycle handling."""

from __future__ import annotations

import copy
import hashlib
import json
from typing import Any


VALIDATION_LIFECYCLE_RUNTIME_VERSION = "validation_lifecycle_runtime_361.v0.1"
CDL_035_DEPENDENCY = "cdl_035_ratified_350.v0.1"
NODE_SCHEMA_CORE_DEPENDENCY = "node_schema_core_runtime_360.v0.1"

ALLOWED_LIFECYCLE_STATES = (
    "proposed",
    "under_review",
    "corroborated",
    "quarantined",
    "refuted",
    "finalized",
)

ALLOWED_TRANSITIONS = {
    "proposed": ("under_review", "quarantined"),
    "under_review": ("corroborated", "refuted", "quarantined"),
    "corroborated": ("finalized", "refuted", "quarantined"),
    "quarantined": ("under_review", "refuted"),
    "refuted": ("under_review",),
    "finalized": (),
}

_GATE_VERDICT_REQUIRED_TARGETS = {
    "corroborated",
    "quarantined",
    "refuted",
}

CANONICAL_VALIDATION_LIFECYCLE_VECTORS: list[dict[str, Any]] = [
    {
        "authored_payload": {
            "node_id": "bafy-node-100",
            "payload": {"claim": "gamma"},
            "primitive_type": "knowledge_claim",
            "creator_agent_id": "bafy-agent-100",
            "epoch_created": 360,
            "epistemic_type": "objective",
            "visibility": "public",
            "channel": "Public",
        },
        "transition": {
            "from_state": "proposed",
            "to_state": "under_review",
            "gate_verdict_ref": None,
        },
    },
    {
        "authored_payload": {
            "node_id": "bafy-node-101",
            "payload": {"claim": "delta"},
            "primitive_type": "knowledge_claim",
            "creator_agent_id": "bafy-agent-101",
            "epoch_created": 360,
            "epistemic_type": "objective",
            "visibility": "public",
            "channel": "Public",
        },
        "transition": {
            "from_state": "under_review",
            "to_state": "quarantined",
            "gate_verdict_ref": "gate://verdict/quarantine-101",
        },
    },
]


class ValidationLifecycleRuntimeError(ValueError):
    """Typed validation error with deterministic tokenized semantics."""

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


def _validate_non_empty_string(raw_value: Any, token: str, message: str) -> str:
    if not isinstance(raw_value, str) or not raw_value.strip():
        raise ValidationLifecycleRuntimeError(token, message)
    return raw_value


def _normalize_authored_payload(raw_authored_payload: Any) -> dict[str, Any]:
    if not isinstance(raw_authored_payload, dict):
        raise ValidationLifecycleRuntimeError(
            "validation_lifecycle_authored_payload_not_object",
            "authored_payload_not_object",
        )

    node_id = _validate_non_empty_string(
        raw_authored_payload.get("node_id"),
        "validation_lifecycle_node_id_missing",
        "node_id_missing",
    )
    payload = raw_authored_payload.get("payload")
    if not isinstance(payload, dict):
        raise ValidationLifecycleRuntimeError(
            "validation_lifecycle_payload_not_object",
            f"payload_not_object:{node_id}",
        )

    normalized = {
        "channel": raw_authored_payload.get("channel"),
        "creator_agent_id": raw_authored_payload.get("creator_agent_id"),
        "epoch_created": raw_authored_payload.get("epoch_created"),
        "epistemic_type": raw_authored_payload.get("epistemic_type"),
        "node_id": node_id,
        "payload": _sorted_mapping(payload),
        "primitive_type": raw_authored_payload.get("primitive_type"),
        "visibility": raw_authored_payload.get("visibility"),
    }

    for key in (
        "channel",
        "creator_agent_id",
        "epistemic_type",
        "primitive_type",
        "visibility",
    ):
        normalized[key] = _validate_non_empty_string(
            normalized.get(key),
            "validation_lifecycle_authored_field_missing",
            f"authored_field_missing:{node_id}:{key}",
        )

    epoch_created = normalized.get("epoch_created")
    if not isinstance(epoch_created, int) or epoch_created < 0:
        raise ValidationLifecycleRuntimeError(
            "validation_lifecycle_epoch_created_invalid",
            f"epoch_created_invalid:{node_id}",
        )

    return normalized


def _normalize_transition(raw_transition: Any, node_id: str) -> dict[str, Any]:
    if not isinstance(raw_transition, dict):
        raise ValidationLifecycleRuntimeError(
            "validation_lifecycle_transition_not_object",
            f"transition_not_object:{node_id}",
        )

    from_state = _validate_non_empty_string(
        raw_transition.get("from_state"),
        "validation_lifecycle_from_state_missing",
        f"from_state_missing:{node_id}",
    )
    to_state = _validate_non_empty_string(
        raw_transition.get("to_state"),
        "validation_lifecycle_to_state_missing",
        f"to_state_missing:{node_id}",
    )

    if from_state not in ALLOWED_LIFECYCLE_STATES:
        raise ValidationLifecycleRuntimeError(
            "validation_lifecycle_from_state_invalid",
            f"from_state_invalid:{node_id}:{from_state}",
        )
    if to_state not in ALLOWED_LIFECYCLE_STATES:
        raise ValidationLifecycleRuntimeError(
            "validation_lifecycle_to_state_invalid",
            f"to_state_invalid:{node_id}:{to_state}",
        )

    if to_state not in ALLOWED_TRANSITIONS[from_state]:
        raise ValidationLifecycleRuntimeError(
            "validation_lifecycle_transition_forbidden",
            f"transition_forbidden:{node_id}:{from_state}->{to_state}",
        )

    gate_verdict_ref = raw_transition.get("gate_verdict_ref")
    if gate_verdict_ref is not None:
        gate_verdict_ref = _validate_non_empty_string(
            gate_verdict_ref,
            "validation_lifecycle_gate_verdict_ref_invalid",
            f"gate_verdict_ref_invalid:{node_id}",
        )

    if to_state in _GATE_VERDICT_REQUIRED_TARGETS and gate_verdict_ref is None:
        raise ValidationLifecycleRuntimeError(
            "validation_lifecycle_gate_verdict_ref_required",
            f"gate_verdict_ref_required:{node_id}:{to_state}",
        )

    return {
        "from_state": from_state,
        "to_state": to_state,
        "gate_verdict_ref": gate_verdict_ref,
    }


def generate_validation_lifecycle_record(payload: dict[str, Any]) -> dict[str, Any]:
    """Generate deterministic validation lifecycle output."""

    authored_payload = _normalize_authored_payload(payload.get("authored_payload"))
    transition = _normalize_transition(payload.get("transition"), authored_payload["node_id"])

    transition_edge = f"{transition['from_state']}->{transition['to_state']}"
    protocol_interpretation = {
        "gate_verdict_ref": transition["gate_verdict_ref"],
        "lifecycle_state": transition["to_state"],
        "previous_lifecycle_state": transition["from_state"],
        "transition_edge": transition_edge,
    }

    transport = {
        "header": {
            "lifecycle_state": transition["to_state"],
            "node_id": authored_payload["node_id"],
            "payload_sha256": _stable_sha256(authored_payload["payload"]),
            "transition_edge": transition_edge,
        }
    }

    core = {
        "cdl_dependency": CDL_035_DEPENDENCY,
        "envelopes": {
            "authored_payload": authored_payload,
            "protocol_interpretation": protocol_interpretation,
            "transport": transport,
        },
        "node_schema_dependency": NODE_SCHEMA_CORE_DEPENDENCY,
        "runtime_version": VALIDATION_LIFECYCLE_RUNTIME_VERSION,
    }
    return {**core, "record_sha256": _stable_sha256(core)}


def verify_validation_lifecycle_record(record: dict[str, Any]) -> dict[str, Any]:
    """Verify deterministic validation lifecycle output."""

    if not isinstance(record, dict):
        raise ValidationLifecycleRuntimeError(
            "validation_lifecycle_record_not_object",
            "record_not_object",
        )

    if record.get("runtime_version") != VALIDATION_LIFECYCLE_RUNTIME_VERSION:
        raise ValidationLifecycleRuntimeError(
            "validation_lifecycle_runtime_version_invalid",
            f"runtime_version_invalid:{record.get('runtime_version')}",
        )
    if record.get("cdl_dependency") != CDL_035_DEPENDENCY:
        raise ValidationLifecycleRuntimeError(
            "validation_lifecycle_cdl_dependency_invalid",
            f"cdl_dependency_invalid:{record.get('cdl_dependency')}",
        )
    if record.get("node_schema_dependency") != NODE_SCHEMA_CORE_DEPENDENCY:
        raise ValidationLifecycleRuntimeError(
            "validation_lifecycle_node_schema_dependency_invalid",
            f"node_schema_dependency_invalid:{record.get('node_schema_dependency')}",
        )

    envelopes = record.get("envelopes")
    if not isinstance(envelopes, dict):
        raise ValidationLifecycleRuntimeError(
            "validation_lifecycle_envelopes_not_object",
            "envelopes_not_object",
        )

    protocol_interpretation = envelopes.get("protocol_interpretation")
    if not isinstance(protocol_interpretation, dict):
        raise ValidationLifecycleRuntimeError(
            "validation_lifecycle_protocol_envelope_not_object",
            "protocol_envelope_not_object",
        )

    regenerated = generate_validation_lifecycle_record(
        {
            "authored_payload": envelopes.get("authored_payload"),
            "transition": {
                "from_state": protocol_interpretation.get("previous_lifecycle_state"),
                "to_state": protocol_interpretation.get("lifecycle_state"),
                "gate_verdict_ref": protocol_interpretation.get("gate_verdict_ref"),
            },
        }
    )

    observed_core = {
        "cdl_dependency": record.get("cdl_dependency"),
        "envelopes": record.get("envelopes"),
        "node_schema_dependency": record.get("node_schema_dependency"),
        "runtime_version": record.get("runtime_version"),
    }
    expected_core = {
        "cdl_dependency": regenerated["cdl_dependency"],
        "envelopes": regenerated["envelopes"],
        "node_schema_dependency": regenerated["node_schema_dependency"],
        "runtime_version": regenerated["runtime_version"],
    }
    if _stable_json(_sorted_mapping(observed_core)) != _stable_json(_sorted_mapping(expected_core)):
        raise ValidationLifecycleRuntimeError(
            "validation_lifecycle_record_not_canonical",
            "record_not_canonical",
        )

    observed_digest = record.get("record_sha256")
    if not isinstance(observed_digest, str):
        raise ValidationLifecycleRuntimeError(
            "validation_lifecycle_record_digest_missing",
            "record_digest_missing",
        )
    if observed_digest != regenerated["record_sha256"]:
        raise ValidationLifecycleRuntimeError(
            "validation_lifecycle_record_digest_mismatch",
            "record_digest_mismatch",
        )

    return {
        "valid": True,
        "runtime_version": VALIDATION_LIFECYCLE_RUNTIME_VERSION,
        "cdl_dependency": CDL_035_DEPENDENCY,
        "node_schema_dependency": NODE_SCHEMA_CORE_DEPENDENCY,
        "record_sha256": regenerated["record_sha256"],
        "checks": [
            {"check_type": "runtime_version_supported", "passed": True},
            {"check_type": "cdl_dependency_locked", "passed": True},
            {"check_type": "node_schema_dependency_locked", "passed": True},
            {"check_type": "gate_verdict_attached_by_reference", "passed": True},
            {"check_type": "quarantine_transition_semantics_enforced", "passed": True},
            {"check_type": "record_digest_matches", "passed": True},
        ],
    }


def canonical_validation_lifecycle_vectors() -> list[dict[str, Any]]:
    """Return a deep copy of canonical validation lifecycle vectors."""

    return copy.deepcopy(CANONICAL_VALIDATION_LIFECYCLE_VECTORS)
