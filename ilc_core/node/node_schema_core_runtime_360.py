"""Phase-360 runtime for CDL-034 node schema core envelope handling."""

from __future__ import annotations

import copy
import hashlib
import json
from typing import Any


NODE_SCHEMA_CORE_RUNTIME_VERSION = "node_schema_core_runtime_360.v0.1"
CDL_034_DEPENDENCY = "cdl_034_ratified_349.v0.1"
SCHEMA_BASELINE_DEPENDENCY = "d2_schema_baseline_310.v0.1"
CDL_073_DEPENDENCY = "cdl_073_homoiconic_bootstrap_schema_ratified.v0.1"

ALLOWED_PRIMITIVE_TYPES = (
    "citation",
    "execution_descriptor",
    "governance_proposal",
    "knowledge_claim",
    "observation",
)

# System-scope primitive types (consensus/genesis layer only; not agent-issuable).
# CDL-073 authorizes genesis_authority_assertion; epoch_record is commit.epoch output.
# These bypass ALLOWED_PRIMITIVE_TYPES validation for system-issued nodes only.
SYSTEM_PRIMITIVE_TYPES = frozenset({
    "genesis_authority_assertion",
    "epoch_record",
})
ALLOWED_EPISTEMIC_TYPES = (
    "creative_speculative",
    "normative",
    "objective",
    "subjective",
)
ALLOWED_VISIBILITY = ("private", "public", "semi-private")
ALLOWED_CHANNELS = ("CoP", "Public", "Quarantine", "Restricted-Shadow")

RESERVED_FIELDS = (
    "channel",
    "confidence",
    "creator_agent_id",
    "epoch_created",
    "epistemic_type",
    "gate_routing",
    "meta",
    "node_id",
    "parent_edges",
    "payload",
    "primitive_type",
    "signature",
    "uncertainty_note",
    "user_tags",
    "visibility",
)

_GATE_ROUTING_BY_EPISTEMIC_TYPE = {
    "objective": "popperian_eligible",
    "normative": "governance_lane",
    "subjective": "resonance_lane",
    "creative_speculative": "resonance_lane",
}

CANONICAL_NODE_SCHEMA_CORE_VECTORS: list[dict[str, Any]] = [
    {
        "authored_payload": {
            "node_id": "bafy-node-001",
            "payload": {"claim": "alpha"},
            "primitive_type": "knowledge_claim",
            "creator_agent_id": "bafy-agent-001",
            "epoch_created": 359,
            "parent_edges": ["bafy-edge-100"],
            "signature": "sig-001",
            "epistemic_type": "objective",
            "confidence": 0.8,
            "uncertainty_note": "bounded observational scope",
            "visibility": "public",
            "channel": "Public",
            "meta": {"org.example.domain": "physics"},
            "user_tags": ["org.example.physics"],
        }
    },
    {
        "authored_payload": {
            "node_id": "bafy-node-002",
            "payload": {"claim": "beta"},
            "primitive_type": "citation",
            "creator_agent_id": "bafy-agent-002",
            "epoch_created": 359,
            "parent_edges": [],
            "signature": "sig-002",
            "epistemic_type": "normative",
            "visibility": "semi-private",
            "channel": "CoP",
            "meta": {"org.example.domain": "governance"},
            "user_tags": ["org.example.policy"],
        }
    },
]


class NodeSchemaCoreValidationError(ValueError):
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


def _validate_string(value: Any, token: str, message: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise NodeSchemaCoreValidationError(token, message)
    return value


def _normalize_parent_edges(raw_edges: Any, node_id: str) -> list[str]:
    if not isinstance(raw_edges, list):
        raise NodeSchemaCoreValidationError(
            "node_schema_parent_edges_not_list",
            f"parent_edges_not_list:{node_id}",
        )
    normalized: list[str] = []
    for raw_edge in raw_edges:
        normalized.append(
            _validate_string(
                raw_edge,
                "node_schema_parent_edge_invalid",
                f"parent_edge_invalid:{node_id}",
            )
        )
    return sorted(set(normalized))


def _normalize_user_tags(raw_tags: Any, node_id: str) -> list[str]:
    if raw_tags is None:
        return []
    if not isinstance(raw_tags, list):
        raise NodeSchemaCoreValidationError(
            "node_schema_user_tags_not_list",
            f"user_tags_not_list:{node_id}",
        )
    normalized: list[str] = []
    for raw_tag in raw_tags:
        tag = _validate_string(
            raw_tag,
            "node_schema_user_tag_invalid",
            f"user_tag_invalid:{node_id}",
        )
        if tag in RESERVED_FIELDS:
            raise NodeSchemaCoreValidationError(
                "node_schema_reserved_field_shadow",
                f"user_tag_reserved_field_shadow:{node_id}:{tag}",
            )
        normalized.append(tag)
    return sorted(set(normalized))


def _normalize_meta(raw_meta: Any, node_id: str) -> dict[str, Any]:
    if raw_meta is None:
        return {}
    if not isinstance(raw_meta, dict):
        raise NodeSchemaCoreValidationError(
            "node_schema_meta_not_object",
            f"meta_not_object:{node_id}",
        )
    normalized = _sorted_mapping(raw_meta)
    for key in normalized:
        if str(key) in RESERVED_FIELDS:
            raise NodeSchemaCoreValidationError(
                "node_schema_reserved_field_shadow",
                f"meta_reserved_field_shadow:{node_id}:{key}",
            )
    return normalized


def _normalize_authored_payload(raw_authored_payload: Any) -> dict[str, Any]:
    if not isinstance(raw_authored_payload, dict):
        raise NodeSchemaCoreValidationError("node_schema_authored_payload_not_object", "authored_payload_not_object")

    if "gate_routing" in raw_authored_payload:
        raise NodeSchemaCoreValidationError(
            "node_schema_gate_routing_submitter_forbidden",
            "gate_routing_submitter_forbidden",
        )

    node_id = _validate_string(
        raw_authored_payload.get("node_id"),
        "node_schema_node_id_missing",
        "node_id_missing",
    )
    primitive_type = _validate_string(
        raw_authored_payload.get("primitive_type"),
        "node_schema_primitive_type_missing",
        f"primitive_type_missing:{node_id}",
    )
    if primitive_type == "refutation":
        raise NodeSchemaCoreValidationError(
            "node_schema_refutation_not_default_primitive",
            f"refutation_not_default_primitive:{node_id}",
        )
    if primitive_type not in ALLOWED_PRIMITIVE_TYPES:
        raise NodeSchemaCoreValidationError(
            "node_schema_primitive_type_invalid",
            f"primitive_type_invalid:{node_id}:{primitive_type}",
        )

    epistemic_type = _validate_string(
        raw_authored_payload.get("epistemic_type"),
        "node_schema_epistemic_type_missing",
        f"epistemic_type_missing:{node_id}",
    )
    if epistemic_type not in ALLOWED_EPISTEMIC_TYPES:
        raise NodeSchemaCoreValidationError(
            "node_schema_epistemic_type_invalid",
            f"epistemic_type_invalid:{node_id}:{epistemic_type}",
        )

    visibility = _validate_string(
        raw_authored_payload.get("visibility"),
        "node_schema_visibility_missing",
        f"visibility_missing:{node_id}",
    )
    if visibility not in ALLOWED_VISIBILITY:
        raise NodeSchemaCoreValidationError(
            "node_schema_visibility_invalid",
            f"visibility_invalid:{node_id}:{visibility}",
        )

    channel = _validate_string(
        raw_authored_payload.get("channel"),
        "node_schema_channel_missing",
        f"channel_missing:{node_id}",
    )
    if channel not in ALLOWED_CHANNELS:
        raise NodeSchemaCoreValidationError(
            "node_schema_channel_invalid",
            f"channel_invalid:{node_id}:{channel}",
        )

    epoch_created = raw_authored_payload.get("epoch_created")
    if not isinstance(epoch_created, int) or epoch_created < 0:
        raise NodeSchemaCoreValidationError(
            "node_schema_epoch_created_invalid",
            f"epoch_created_invalid:{node_id}",
        )

    payload = raw_authored_payload.get("payload")
    if not isinstance(payload, dict):
        raise NodeSchemaCoreValidationError(
            "node_schema_payload_not_object",
            f"payload_not_object:{node_id}",
        )

    creator_agent_id = _validate_string(
        raw_authored_payload.get("creator_agent_id"),
        "node_schema_creator_agent_id_missing",
        f"creator_agent_id_missing:{node_id}",
    )
    signature = _validate_string(
        raw_authored_payload.get("signature"),
        "node_schema_signature_missing",
        f"signature_missing:{node_id}",
    )

    confidence = raw_authored_payload.get("confidence")
    if confidence is not None:
        if not isinstance(confidence, (int, float)):
            raise NodeSchemaCoreValidationError(
                "node_schema_confidence_invalid",
                f"confidence_invalid:{node_id}",
            )
        confidence = float(confidence)
        if confidence < 0.0 or confidence > 1.0:
            raise NodeSchemaCoreValidationError(
                "node_schema_confidence_out_of_range",
                f"confidence_out_of_range:{node_id}",
            )

    uncertainty_note = raw_authored_payload.get("uncertainty_note")
    if uncertainty_note is not None and not isinstance(uncertainty_note, str):
        raise NodeSchemaCoreValidationError(
            "node_schema_uncertainty_note_invalid",
            f"uncertainty_note_invalid:{node_id}",
        )

    return {
        "channel": channel,
        "confidence": confidence,
        "creator_agent_id": creator_agent_id,
        "epoch_created": epoch_created,
        "epistemic_type": epistemic_type,
        "meta": _normalize_meta(raw_authored_payload.get("meta"), node_id),
        "node_id": node_id,
        "parent_edges": _normalize_parent_edges(raw_authored_payload.get("parent_edges"), node_id),
        "payload": _sorted_mapping(payload),
        "primitive_type": primitive_type,
        "signature": signature,
        "uncertainty_note": uncertainty_note,
        "user_tags": _normalize_user_tags(raw_authored_payload.get("user_tags"), node_id),
        "visibility": visibility,
    }


def generate_node_schema_core_record(payload: dict[str, Any]) -> dict[str, Any]:
    """Generate deterministic node schema core runtime output."""

    authored_payload = _normalize_authored_payload(payload.get("authored_payload"))
    gate_routing = _GATE_ROUTING_BY_EPISTEMIC_TYPE[authored_payload["epistemic_type"]]

    transport_header = {
        "channel": authored_payload["channel"],
        "creator_agent_id": authored_payload["creator_agent_id"],
        "epoch_created": authored_payload["epoch_created"],
        "node_id": authored_payload["node_id"],
        "payload_sha256": _stable_sha256(authored_payload["payload"]),
        "signature_sha256": hashlib.sha256(authored_payload["signature"].encode("utf-8")).hexdigest(),
        "visibility": authored_payload["visibility"],
    }

    core = {
        "cdl_dependency": CDL_034_DEPENDENCY,
        "envelopes": {
            "authored_payload": authored_payload,
            "protocol_interpretation": {"gate_routing": gate_routing},
            "transport": {"header": transport_header},
        },
        "runtime_version": NODE_SCHEMA_CORE_RUNTIME_VERSION,
        "schema_dependency": SCHEMA_BASELINE_DEPENDENCY,
    }
    return {**core, "record_sha256": _stable_sha256(core)}


def verify_node_schema_core_record(record: dict[str, Any]) -> dict[str, Any]:
    """Verify deterministic node schema core runtime output."""

    if not isinstance(record, dict):
        raise NodeSchemaCoreValidationError("node_schema_record_not_object", "record_not_object")

    if record.get("runtime_version") != NODE_SCHEMA_CORE_RUNTIME_VERSION:
        raise NodeSchemaCoreValidationError(
            "node_schema_runtime_version_invalid",
            f"runtime_version_invalid:{record.get('runtime_version')}",
        )
    if record.get("cdl_dependency") != CDL_034_DEPENDENCY:
        raise NodeSchemaCoreValidationError(
            "node_schema_cdl_dependency_invalid",
            f"cdl_dependency_invalid:{record.get('cdl_dependency')}",
        )
    if record.get("schema_dependency") != SCHEMA_BASELINE_DEPENDENCY:
        raise NodeSchemaCoreValidationError(
            "node_schema_schema_dependency_invalid",
            f"schema_dependency_invalid:{record.get('schema_dependency')}",
        )

    envelopes = record.get("envelopes")
    if not isinstance(envelopes, dict):
        raise NodeSchemaCoreValidationError("node_schema_envelopes_not_object", "envelopes_not_object")

    authored_payload = envelopes.get("authored_payload")
    protocol_interpretation = envelopes.get("protocol_interpretation")
    if not isinstance(protocol_interpretation, dict):
        raise NodeSchemaCoreValidationError(
            "node_schema_protocol_envelope_not_object",
            "protocol_envelope_not_object",
        )

    regenerated = generate_node_schema_core_record({"authored_payload": authored_payload})
    expected_gate_routing = regenerated["envelopes"]["protocol_interpretation"]["gate_routing"]
    observed_gate_routing = protocol_interpretation.get("gate_routing")
    if observed_gate_routing != expected_gate_routing:
        raise NodeSchemaCoreValidationError(
            "node_schema_gate_routing_mismatch",
            f"gate_routing_mismatch:{observed_gate_routing}:{expected_gate_routing}",
        )

    observed_core = {
        "cdl_dependency": record.get("cdl_dependency"),
        "envelopes": record.get("envelopes"),
        "runtime_version": record.get("runtime_version"),
        "schema_dependency": record.get("schema_dependency"),
    }
    expected_core = {
        "cdl_dependency": regenerated["cdl_dependency"],
        "envelopes": regenerated["envelopes"],
        "runtime_version": regenerated["runtime_version"],
        "schema_dependency": regenerated["schema_dependency"],
    }
    if _stable_json(_sorted_mapping(observed_core)) != _stable_json(_sorted_mapping(expected_core)):
        raise NodeSchemaCoreValidationError("node_schema_record_not_canonical", "record_not_canonical")

    observed_digest = record.get("record_sha256")
    if not isinstance(observed_digest, str):
        raise NodeSchemaCoreValidationError("node_schema_record_digest_missing", "record_sha256_missing")
    if observed_digest != regenerated["record_sha256"]:
        raise NodeSchemaCoreValidationError("node_schema_record_digest_mismatch", "record_sha256_mismatch")

    return {
        "valid": True,
        "runtime_version": NODE_SCHEMA_CORE_RUNTIME_VERSION,
        "cdl_dependency": CDL_034_DEPENDENCY,
        "schema_dependency": SCHEMA_BASELINE_DEPENDENCY,
        "record_sha256": regenerated["record_sha256"],
        "checks": [
            {"check_type": "runtime_version_supported", "passed": True},
            {"check_type": "cdl_dependency_locked", "passed": True},
            {"check_type": "schema_dependency_locked", "passed": True},
            {"check_type": "gate_routing_protocol_derived", "passed": True},
            {"check_type": "record_digest_matches", "passed": True},
        ],
    }


def canonical_node_schema_core_vectors() -> list[dict[str, Any]]:
    """Return a deep copy of canonical runtime vectors."""

    return copy.deepcopy(CANONICAL_NODE_SCHEMA_CORE_VECTORS)
