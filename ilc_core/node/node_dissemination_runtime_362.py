"""Phase-362 runtime for CDL-036 node dissemination handling."""

from __future__ import annotations

import copy
import hashlib
import json
from typing import Any


NODE_DISSEMINATION_RUNTIME_VERSION = "node_dissemination_runtime_362.v0.1"
CDL_036_DEPENDENCY = "cdl_036_ratified_351.v0.1"
VALIDATION_LIFECYCLE_DEPENDENCY = "validation_lifecycle_runtime_361.v0.1"

CANDIDATE_HEADER_FIELDS = (
    "node_id",
    "creator_agent_id",
    "epistemic_type",
    "visibility",
    "channel",
    "epoch_created",
    "payload_cid",
    "signature",
)

_ALLOWED_EPISTEMIC_TYPES = (
    "objective",
    "subjective",
    "normative",
    "creative_speculative",
)
_ALLOWED_VISIBILITY = ("public", "semi-private", "private")
_ALLOWED_CHANNELS = ("Public", "CoP", "Restricted-Shadow", "Quarantine")

CANONICAL_NODE_DISSEMINATION_VECTORS: list[dict[str, Any]] = [
    {
        "authored_payload": {
            "node_id": "bafy-node-201",
            "creator_agent_id": "bafy-agent-201",
            "epistemic_type": "objective",
            "visibility": "public",
            "channel": "Public",
            "epoch_created": 361,
            "payload": {"claim": "epsilon", "confidence": 0.75},
        }
    },
    {
        "authored_payload": {
            "node_id": "bafy-node-202",
            "creator_agent_id": "bafy-agent-202",
            "epistemic_type": "normative",
            "visibility": "semi-private",
            "channel": "CoP",
            "epoch_created": 361,
            "payload": {"claim": "zeta", "policy": "draft"},
        }
    },
]


class NodeDisseminationRuntimeError(ValueError):
    """Typed dissemination validation error with deterministic tokens."""

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
        raise NodeDisseminationRuntimeError(token, message)
    return raw_value


def _normalize_authored_payload(raw_authored_payload: Any) -> dict[str, Any]:
    if not isinstance(raw_authored_payload, dict):
        raise NodeDisseminationRuntimeError(
            "node_dissemination_authored_payload_not_object",
            "authored_payload_not_object",
        )

    node_id = _validate_non_empty_string(
        raw_authored_payload.get("node_id"),
        "node_dissemination_node_id_missing",
        "node_id_missing",
    )

    creator_agent_id = _validate_non_empty_string(
        raw_authored_payload.get("creator_agent_id"),
        "node_dissemination_creator_agent_id_missing",
        f"creator_agent_id_missing:{node_id}",
    )
    epistemic_type = _validate_non_empty_string(
        raw_authored_payload.get("epistemic_type"),
        "node_dissemination_epistemic_type_missing",
        f"epistemic_type_missing:{node_id}",
    )
    visibility = _validate_non_empty_string(
        raw_authored_payload.get("visibility"),
        "node_dissemination_visibility_missing",
        f"visibility_missing:{node_id}",
    )
    channel = _validate_non_empty_string(
        raw_authored_payload.get("channel"),
        "node_dissemination_channel_missing",
        f"channel_missing:{node_id}",
    )

    if epistemic_type not in _ALLOWED_EPISTEMIC_TYPES:
        raise NodeDisseminationRuntimeError(
            "node_dissemination_epistemic_type_invalid",
            f"epistemic_type_invalid:{node_id}:{epistemic_type}",
        )
    if visibility not in _ALLOWED_VISIBILITY:
        raise NodeDisseminationRuntimeError(
            "node_dissemination_visibility_invalid",
            f"visibility_invalid:{node_id}:{visibility}",
        )
    if channel not in _ALLOWED_CHANNELS:
        raise NodeDisseminationRuntimeError(
            "node_dissemination_channel_invalid",
            f"channel_invalid:{node_id}:{channel}",
        )

    epoch_created = raw_authored_payload.get("epoch_created")
    if not isinstance(epoch_created, int) or epoch_created < 0:
        raise NodeDisseminationRuntimeError(
            "node_dissemination_epoch_created_invalid",
            f"epoch_created_invalid:{node_id}",
        )

    payload = raw_authored_payload.get("payload")
    if not isinstance(payload, dict):
        raise NodeDisseminationRuntimeError(
            "node_dissemination_payload_not_object",
            f"payload_not_object:{node_id}",
        )

    return {
        "channel": channel,
        "creator_agent_id": creator_agent_id,
        "epoch_created": epoch_created,
        "epistemic_type": epistemic_type,
        "node_id": node_id,
        "payload": _sorted_mapping(payload),
        "visibility": visibility,
    }


def _payload_cid(payload: dict[str, Any]) -> str:
    return f"cid::{_stable_sha256(payload)}"


def _signature_for_header(header_without_signature: dict[str, Any]) -> str:
    return f"sig::{_stable_sha256(header_without_signature)}"


def _normalize_options(raw_options: Any, node_id: str) -> dict[str, Any]:
    if raw_options is None:
        return {"orderer_mode": "orderer_agnostic"}
    if not isinstance(raw_options, dict):
        raise NodeDisseminationRuntimeError(
            "node_dissemination_options_not_object",
            f"options_not_object:{node_id}",
        )

    orderer_mode = raw_options.get("orderer_mode", "orderer_agnostic")
    if orderer_mode != "orderer_agnostic":
        raise NodeDisseminationRuntimeError(
            "node_dissemination_orderer_mode_forbidden",
            f"orderer_mode_forbidden:{node_id}:{orderer_mode}",
        )

    return {"orderer_mode": orderer_mode}


def generate_node_dissemination_record(payload: dict[str, Any]) -> dict[str, Any]:
    """Generate deterministic dissemination runtime output."""

    authored_payload = _normalize_authored_payload(payload.get("authored_payload"))
    options = _normalize_options(payload.get("options"), authored_payload["node_id"])

    payload_cid = _payload_cid(authored_payload["payload"])
    header_without_signature = {
        "node_id": authored_payload["node_id"],
        "creator_agent_id": authored_payload["creator_agent_id"],
        "epistemic_type": authored_payload["epistemic_type"],
        "visibility": authored_payload["visibility"],
        "channel": authored_payload["channel"],
        "epoch_created": authored_payload["epoch_created"],
        "payload_cid": payload_cid,
    }
    signature = _signature_for_header(header_without_signature)
    header = {**header_without_signature, "signature": signature}

    fetch_contract = {
        "fetch_mode": "cid_pull",
        "idempotence_key": _stable_sha256(
            {
                "node_id": authored_payload["node_id"],
                "payload_cid": payload_cid,
            }
        ),
        "retry_safe": True,
        "content_address_verified_before_interpretation": True,
    }

    transport = {
        "header": header,
        "fetch_contract": fetch_contract,
        "dissemination_mode": "pull_dominant_soft_push_signals",
        "orderer_mode": options["orderer_mode"],
        "routing_inputs": {
            "visibility": authored_payload["visibility"],
            "channel": authored_payload["channel"],
        },
    }

    protocol_interpretation = {
        "routing_lane": f"{authored_payload['visibility']}::{authored_payload['channel']}",
        "routing_inputs": {
            "visibility": authored_payload["visibility"],
            "channel": authored_payload["channel"],
        },
    }

    core = {
        "cdl_dependency": CDL_036_DEPENDENCY,
        "envelopes": {
            "authored_payload": authored_payload,
            "protocol_interpretation": protocol_interpretation,
            "transport": transport,
        },
        "validation_lifecycle_dependency": VALIDATION_LIFECYCLE_DEPENDENCY,
        "runtime_version": NODE_DISSEMINATION_RUNTIME_VERSION,
    }

    return {**core, "record_sha256": _stable_sha256(core)}


def _validate_header_fields(header: dict[str, Any], node_id: str) -> None:
    observed = tuple(header.keys())
    if observed != CANDIDATE_HEADER_FIELDS:
        raise NodeDisseminationRuntimeError(
            "node_dissemination_header_field_set_invalid",
            f"header_field_set_invalid:{node_id}:{observed}",
        )

    for field in CANDIDATE_HEADER_FIELDS:
        value = header.get(field)
        if field == "epoch_created":
            if not isinstance(value, int) or value < 0:
                raise NodeDisseminationRuntimeError(
                    "node_dissemination_header_field_invalid",
                    f"header_field_invalid:{node_id}:{field}",
                )
            continue
        if not isinstance(value, str) or not value.strip():
            raise NodeDisseminationRuntimeError(
                "node_dissemination_header_field_invalid",
                f"header_field_invalid:{node_id}:{field}",
            )


def verify_node_dissemination_record(record: dict[str, Any]) -> dict[str, Any]:
    """Verify deterministic dissemination runtime output."""

    if not isinstance(record, dict):
        raise NodeDisseminationRuntimeError(
            "node_dissemination_record_not_object",
            "record_not_object",
        )

    if record.get("runtime_version") != NODE_DISSEMINATION_RUNTIME_VERSION:
        raise NodeDisseminationRuntimeError(
            "node_dissemination_runtime_version_invalid",
            f"runtime_version_invalid:{record.get('runtime_version')}",
        )
    if record.get("cdl_dependency") != CDL_036_DEPENDENCY:
        raise NodeDisseminationRuntimeError(
            "node_dissemination_cdl_dependency_invalid",
            f"cdl_dependency_invalid:{record.get('cdl_dependency')}",
        )
    if record.get("validation_lifecycle_dependency") != VALIDATION_LIFECYCLE_DEPENDENCY:
        raise NodeDisseminationRuntimeError(
            "node_dissemination_validation_lifecycle_dependency_invalid",
            f"validation_lifecycle_dependency_invalid:{record.get('validation_lifecycle_dependency')}",
        )

    envelopes = record.get("envelopes")
    if not isinstance(envelopes, dict):
        raise NodeDisseminationRuntimeError(
            "node_dissemination_envelopes_not_object",
            "envelopes_not_object",
        )

    authored_payload = envelopes.get("authored_payload")
    transport = envelopes.get("transport")
    protocol_interpretation = envelopes.get("protocol_interpretation")

    if not isinstance(transport, dict):
        raise NodeDisseminationRuntimeError(
            "node_dissemination_transport_envelope_not_object",
            "transport_envelope_not_object",
        )
    if not isinstance(protocol_interpretation, dict):
        raise NodeDisseminationRuntimeError(
            "node_dissemination_protocol_envelope_not_object",
            "protocol_envelope_not_object",
        )

    normalized_authored = _normalize_authored_payload(authored_payload)
    node_id = normalized_authored["node_id"]

    header = transport.get("header")
    if not isinstance(header, dict):
        raise NodeDisseminationRuntimeError(
            "node_dissemination_header_not_object",
            f"header_not_object:{node_id}",
        )

    _validate_header_fields(header, node_id)

    expected_payload_cid = _payload_cid(normalized_authored["payload"])
    if header["payload_cid"] != expected_payload_cid:
        raise NodeDisseminationRuntimeError(
            "node_dissemination_payload_cid_mismatch",
            f"payload_cid_mismatch:{node_id}:{header['payload_cid']}:{expected_payload_cid}",
        )

    header_without_signature = {
        field: header[field] for field in CANDIDATE_HEADER_FIELDS if field != "signature"
    }
    expected_signature = _signature_for_header(header_without_signature)
    if header["signature"] != expected_signature:
        raise NodeDisseminationRuntimeError(
            "node_dissemination_signature_scope_violation",
            f"signature_scope_violation:{node_id}",
        )

    fetch_contract = transport.get("fetch_contract")
    if not isinstance(fetch_contract, dict):
        raise NodeDisseminationRuntimeError(
            "node_dissemination_fetch_contract_not_object",
            f"fetch_contract_not_object:{node_id}",
        )

    if fetch_contract.get("fetch_mode") != "cid_pull":
        raise NodeDisseminationRuntimeError(
            "node_dissemination_fetch_mode_invalid",
            f"fetch_mode_invalid:{node_id}:{fetch_contract.get('fetch_mode')}",
        )

    expected_idempotence_key = _stable_sha256(
        {"node_id": node_id, "payload_cid": expected_payload_cid}
    )
    if fetch_contract.get("idempotence_key") != expected_idempotence_key:
        raise NodeDisseminationRuntimeError(
            "node_dissemination_idempotence_key_invalid",
            f"idempotence_key_invalid:{node_id}",
        )

    if fetch_contract.get("retry_safe") is not True:
        raise NodeDisseminationRuntimeError(
            "node_dissemination_retry_semantics_invalid",
            f"retry_semantics_invalid:{node_id}",
        )
    if fetch_contract.get("content_address_verified_before_interpretation") is not True:
        raise NodeDisseminationRuntimeError(
            "node_dissemination_content_address_verification_missing",
            f"content_address_verification_missing:{node_id}",
        )

    if transport.get("dissemination_mode") != "pull_dominant_soft_push_signals":
        raise NodeDisseminationRuntimeError(
            "node_dissemination_mode_invalid",
            f"dissemination_mode_invalid:{node_id}:{transport.get('dissemination_mode')}",
        )
    if transport.get("orderer_mode") != "orderer_agnostic":
        raise NodeDisseminationRuntimeError(
            "node_dissemination_orderer_mode_forbidden",
            f"orderer_mode_forbidden:{node_id}:{transport.get('orderer_mode')}",
        )

    transport_routing = transport.get("routing_inputs")
    protocol_routing = protocol_interpretation.get("routing_inputs")
    if transport_routing != {
        "visibility": normalized_authored["visibility"],
        "channel": normalized_authored["channel"],
    }:
        raise NodeDisseminationRuntimeError(
            "node_dissemination_routing_inputs_invalid",
            f"routing_inputs_invalid:{node_id}:transport",
        )
    if protocol_routing != {
        "visibility": normalized_authored["visibility"],
        "channel": normalized_authored["channel"],
    }:
        raise NodeDisseminationRuntimeError(
            "node_dissemination_routing_inputs_invalid",
            f"routing_inputs_invalid:{node_id}:protocol",
        )

    regenerated = generate_node_dissemination_record({"authored_payload": normalized_authored})

    observed_core = {
        "cdl_dependency": record.get("cdl_dependency"),
        "envelopes": record.get("envelopes"),
        "validation_lifecycle_dependency": record.get("validation_lifecycle_dependency"),
        "runtime_version": record.get("runtime_version"),
    }
    expected_core = {
        "cdl_dependency": regenerated["cdl_dependency"],
        "envelopes": regenerated["envelopes"],
        "validation_lifecycle_dependency": regenerated["validation_lifecycle_dependency"],
        "runtime_version": regenerated["runtime_version"],
    }
    if _stable_json(_sorted_mapping(observed_core)) != _stable_json(_sorted_mapping(expected_core)):
        raise NodeDisseminationRuntimeError(
            "node_dissemination_record_not_canonical",
            f"record_not_canonical:{node_id}",
        )

    observed_digest = record.get("record_sha256")
    if not isinstance(observed_digest, str):
        raise NodeDisseminationRuntimeError(
            "node_dissemination_record_digest_missing",
            f"record_digest_missing:{node_id}",
        )
    if observed_digest != regenerated["record_sha256"]:
        raise NodeDisseminationRuntimeError(
            "node_dissemination_record_digest_mismatch",
            f"record_digest_mismatch:{node_id}",
        )

    return {
        "valid": True,
        "runtime_version": NODE_DISSEMINATION_RUNTIME_VERSION,
        "cdl_dependency": CDL_036_DEPENDENCY,
        "validation_lifecycle_dependency": VALIDATION_LIFECYCLE_DEPENDENCY,
        "record_sha256": regenerated["record_sha256"],
        "checks": [
            {"check_type": "runtime_version_supported", "passed": True},
            {"check_type": "cdl_dependency_locked", "passed": True},
            {"check_type": "validation_lifecycle_dependency_locked", "passed": True},
            {"check_type": "header_signature_scope_enforced", "passed": True},
            {"check_type": "cid_pull_fetch_idempotence_enforced", "passed": True},
            {"check_type": "routing_inputs_are_transport_only", "passed": True},
            {"check_type": "record_digest_matches", "passed": True},
        ],
    }


def canonical_node_dissemination_vectors() -> list[dict[str, Any]]:
    """Return a deep copy of canonical dissemination vectors."""

    return copy.deepcopy(CANONICAL_NODE_DISSEMINATION_VECTORS)
