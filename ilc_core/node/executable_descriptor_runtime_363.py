# SPDX-License-Identifier: AGPL-3.0-only
"""Phase-363 runtime for CDL-037 executable descriptor handling."""

from __future__ import annotations

import copy
import hashlib
import json
from typing import Any


EXECUTABLE_DESCRIPTOR_RUNTIME_VERSION = "executable_descriptor_runtime_363.v0.1"
CDL_037_DEPENDENCY = "cdl_037_ratified_352.v0.1"
NODE_DISSEMINATION_DEPENDENCY = "node_dissemination_runtime_362.v0.1"

_DESCRIPTOR_FIELDS = (
    "declared_inputs",
    "declared_outputs",
    "declared_side_effects",
    "safety_assertions",
    "determinism_guarantees",
    "bounded_resource_guarantees",
)
_ALLOWED_SIDE_EFFECTS = ("network", "none", "storage")
_ALLOWED_RUNTIME_BINDINGS = ("sandboxed_agent_runtime",)

CANONICAL_EXECUTABLE_DESCRIPTOR_VECTORS: list[dict[str, Any]] = [
    {
        "authored_payload": {
            "node_id": "bafy-node-exec-301",
            "descriptor": {
                "declared_inputs": ["payload_cid"],
                "declared_outputs": ["verification_report"],
                "declared_side_effects": ["none"],
                "safety_assertions": ["sandbox_required", "no_self_authorization"],
                "determinism_guarantees": ["deterministic_for_same_input"],
                "bounded_resource_guarantees": ["cpu_ms<=500", "memory_mb<=64"],
            },
            "safety_contract_ref": "genesis://contracts/executable-301",
            "genesis_trusted": True,
        },
        "execution_context": {
            "runtime_binding": "sandboxed_agent_runtime",
            "requested_execution": False,
        },
    },
    {
        "authored_payload": {
            "node_id": "bafy-node-exec-302",
            "descriptor": {
                "declared_inputs": ["node_header"],
                "declared_outputs": ["routing_hint"],
                "declared_side_effects": ["network"],
                "safety_assertions": ["sandbox_required", "no_self_authorization"],
                "determinism_guarantees": ["bounded_non_determinism_declared"],
                "bounded_resource_guarantees": ["cpu_ms<=900", "memory_mb<=128"],
            },
            "safety_contract_ref": "contract://safety/non-genesis-302",
            "genesis_trusted": False,
        },
        "execution_context": {
            "runtime_binding": "sandboxed_agent_runtime",
            "requested_execution": False,
        },
    },
]


class ExecutableDescriptorRuntimeError(ValueError):
    """Typed descriptor validation error with deterministic tokenized semantics."""

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
        raise ExecutableDescriptorRuntimeError(token, message)
    return raw_value


def _normalize_descriptor(raw_descriptor: Any, node_id: str) -> dict[str, list[str]]:
    if not isinstance(raw_descriptor, dict):
        raise ExecutableDescriptorRuntimeError(
            "executable_descriptor_not_object",
            f"descriptor_not_object:{node_id}",
        )

    normalized: dict[str, list[str]] = {}
    for field in _DESCRIPTOR_FIELDS:
        raw_values = raw_descriptor.get(field)
        if not isinstance(raw_values, list) or not raw_values:
            raise ExecutableDescriptorRuntimeError(
                "executable_descriptor_field_invalid",
                f"descriptor_field_invalid:{node_id}:{field}",
            )

        values: list[str] = []
        seen: set[str] = set()
        for raw_value in raw_values:
            value = _validate_non_empty_string(
                raw_value,
                "executable_descriptor_field_value_invalid",
                f"descriptor_field_value_invalid:{node_id}:{field}",
            )
            if value in seen:
                continue
            seen.add(value)
            values.append(value)
        normalized[field] = values

    if any(value not in _ALLOWED_SIDE_EFFECTS for value in normalized["declared_side_effects"]):
        raise ExecutableDescriptorRuntimeError(
            "executable_descriptor_side_effect_not_allowed",
            f"side_effect_not_allowed:{node_id}",
        )

    if "no_self_authorization" not in normalized["safety_assertions"]:
        raise ExecutableDescriptorRuntimeError(
            "executable_descriptor_safety_assertion_missing",
            f"safety_assertion_missing:{node_id}:no_self_authorization",
        )
    if "sandbox_required" not in normalized["safety_assertions"]:
        raise ExecutableDescriptorRuntimeError(
            "executable_descriptor_safety_assertion_missing",
            f"safety_assertion_missing:{node_id}:sandbox_required",
        )

    return normalized


def _normalize_authored_payload(raw_authored_payload: Any) -> dict[str, Any]:
    if not isinstance(raw_authored_payload, dict):
        raise ExecutableDescriptorRuntimeError(
            "executable_authored_payload_not_object",
            "authored_payload_not_object",
        )

    if "execution_context" in raw_authored_payload:
        raise ExecutableDescriptorRuntimeError(
            "executable_context_inside_authored_payload_forbidden",
            "execution_context_inside_authored_payload",
        )

    node_id = _validate_non_empty_string(
        raw_authored_payload.get("node_id"),
        "executable_node_id_missing",
        "node_id_missing",
    )
    descriptor = _normalize_descriptor(raw_authored_payload.get("descriptor"), node_id)

    safety_contract_ref = _validate_non_empty_string(
        raw_authored_payload.get("safety_contract_ref"),
        "executable_safety_contract_ref_missing",
        f"safety_contract_ref_missing:{node_id}",
    )

    genesis_trusted = raw_authored_payload.get("genesis_trusted")
    if not isinstance(genesis_trusted, bool):
        raise ExecutableDescriptorRuntimeError(
            "executable_genesis_trusted_invalid",
            f"genesis_trusted_invalid:{node_id}",
        )

    if genesis_trusted:
        if not safety_contract_ref.startswith("genesis://"):
            raise ExecutableDescriptorRuntimeError(
                "executable_genesis_boundary_violation",
                f"genesis_boundary_violation:{node_id}:expected_genesis_contract",
            )
    else:
        if not safety_contract_ref.startswith("contract://"):
            raise ExecutableDescriptorRuntimeError(
                "executable_genesis_boundary_violation",
                f"genesis_boundary_violation:{node_id}:expected_non_genesis_contract",
            )

    return {
        "descriptor": descriptor,
        "genesis_trusted": genesis_trusted,
        "node_id": node_id,
        "safety_contract_ref": safety_contract_ref,
    }


def _normalize_execution_context(raw_execution_context: Any, node_id: str) -> dict[str, Any]:
    if not isinstance(raw_execution_context, dict):
        raise ExecutableDescriptorRuntimeError(
            "executable_execution_context_not_object",
            f"execution_context_not_object:{node_id}",
        )

    runtime_binding = _validate_non_empty_string(
        raw_execution_context.get("runtime_binding"),
        "executable_runtime_binding_missing",
        f"runtime_binding_missing:{node_id}",
    )
    if runtime_binding not in _ALLOWED_RUNTIME_BINDINGS:
        raise ExecutableDescriptorRuntimeError(
            "executable_runtime_binding_invalid",
            f"runtime_binding_invalid:{node_id}:{runtime_binding}",
        )

    requested_execution = raw_execution_context.get("requested_execution")
    if requested_execution is not False:
        raise ExecutableDescriptorRuntimeError(
            "executable_self_authorized_execution_forbidden",
            f"self_authorized_execution_forbidden:{node_id}",
        )

    return {
        "runtime_binding": runtime_binding,
        "requested_execution": False,
    }


def generate_executable_descriptor_record(payload: dict[str, Any]) -> dict[str, Any]:
    """Generate deterministic executable descriptor runtime output."""

    authored_payload = _normalize_authored_payload(payload.get("authored_payload"))
    execution_context = _normalize_execution_context(
        payload.get("execution_context"),
        authored_payload["node_id"],
    )

    protocol_interpretation = {
        "descriptor_class": "genesis_trusted"
        if authored_payload["genesis_trusted"]
        else "non_genesis",
        "safety_contract_verified": True,
        "challengeable_under_cdl_v7": True,
    }

    runtime_binding = {
        "runtime_binding": execution_context["runtime_binding"],
        "recommendation_only": True,
        "self_authorized_execution": False,
    }

    core = {
        "cdl_dependency": CDL_037_DEPENDENCY,
        "envelopes": {
            "authored_payload": authored_payload,
            "protocol_interpretation": protocol_interpretation,
            "runtime_binding": runtime_binding,
        },
        "node_dissemination_dependency": NODE_DISSEMINATION_DEPENDENCY,
        "runtime_version": EXECUTABLE_DESCRIPTOR_RUNTIME_VERSION,
    }

    return {**core, "record_sha256": _stable_sha256(core)}


def verify_executable_descriptor_record(record: dict[str, Any]) -> dict[str, Any]:
    """Verify deterministic executable descriptor runtime output."""

    if not isinstance(record, dict):
        raise ExecutableDescriptorRuntimeError(
            "executable_record_not_object",
            "record_not_object",
        )

    if record.get("runtime_version") != EXECUTABLE_DESCRIPTOR_RUNTIME_VERSION:
        raise ExecutableDescriptorRuntimeError(
            "executable_runtime_version_invalid",
            f"runtime_version_invalid:{record.get('runtime_version')}",
        )
    if record.get("cdl_dependency") != CDL_037_DEPENDENCY:
        raise ExecutableDescriptorRuntimeError(
            "executable_cdl_dependency_invalid",
            f"cdl_dependency_invalid:{record.get('cdl_dependency')}",
        )
    if record.get("node_dissemination_dependency") != NODE_DISSEMINATION_DEPENDENCY:
        raise ExecutableDescriptorRuntimeError(
            "executable_node_dissemination_dependency_invalid",
            f"node_dissemination_dependency_invalid:{record.get('node_dissemination_dependency')}",
        )

    envelopes = record.get("envelopes")
    if not isinstance(envelopes, dict):
        raise ExecutableDescriptorRuntimeError(
            "executable_envelopes_not_object",
            "envelopes_not_object",
        )

    authored_payload = _normalize_authored_payload(envelopes.get("authored_payload"))
    runtime_binding = envelopes.get("runtime_binding")
    protocol_interpretation = envelopes.get("protocol_interpretation")

    if not isinstance(runtime_binding, dict):
        raise ExecutableDescriptorRuntimeError(
            "executable_runtime_binding_not_object",
            f"runtime_binding_not_object:{authored_payload['node_id']}",
        )
    if not isinstance(protocol_interpretation, dict):
        raise ExecutableDescriptorRuntimeError(
            "executable_protocol_envelope_not_object",
            f"protocol_envelope_not_object:{authored_payload['node_id']}",
        )

    normalized_execution_context = _normalize_execution_context(
        {
            "runtime_binding": runtime_binding.get("runtime_binding"),
            "requested_execution": runtime_binding.get("self_authorized_execution"),
        },
        authored_payload["node_id"],
    )

    if runtime_binding.get("recommendation_only") is not True:
        raise ExecutableDescriptorRuntimeError(
            "executable_recommendation_only_violation",
            f"recommendation_only_violation:{authored_payload['node_id']}",
        )

    expected_descriptor_class = (
        "genesis_trusted" if authored_payload["genesis_trusted"] else "non_genesis"
    )
    if protocol_interpretation.get("descriptor_class") != expected_descriptor_class:
        raise ExecutableDescriptorRuntimeError(
            "executable_descriptor_class_invalid",
            f"descriptor_class_invalid:{authored_payload['node_id']}",
        )
    if protocol_interpretation.get("safety_contract_verified") is not True:
        raise ExecutableDescriptorRuntimeError(
            "executable_safety_contract_verification_invalid",
            f"safety_contract_verification_invalid:{authored_payload['node_id']}",
        )
    if protocol_interpretation.get("challengeable_under_cdl_v7") is not True:
        raise ExecutableDescriptorRuntimeError(
            "executable_cdl_v7_boundary_invalid",
            f"cdl_v7_boundary_invalid:{authored_payload['node_id']}",
        )

    regenerated = generate_executable_descriptor_record(
        {
            "authored_payload": authored_payload,
            "execution_context": normalized_execution_context,
        }
    )

    observed_core = {
        "cdl_dependency": record.get("cdl_dependency"),
        "envelopes": record.get("envelopes"),
        "node_dissemination_dependency": record.get("node_dissemination_dependency"),
        "runtime_version": record.get("runtime_version"),
    }
    expected_core = {
        "cdl_dependency": regenerated["cdl_dependency"],
        "envelopes": regenerated["envelopes"],
        "node_dissemination_dependency": regenerated["node_dissemination_dependency"],
        "runtime_version": regenerated["runtime_version"],
    }
    if _stable_json(_sorted_mapping(observed_core)) != _stable_json(_sorted_mapping(expected_core)):
        raise ExecutableDescriptorRuntimeError(
            "executable_record_not_canonical",
            f"record_not_canonical:{authored_payload['node_id']}",
        )

    observed_digest = record.get("record_sha256")
    if not isinstance(observed_digest, str):
        raise ExecutableDescriptorRuntimeError(
            "executable_record_digest_missing",
            f"record_digest_missing:{authored_payload['node_id']}",
        )
    if observed_digest != regenerated["record_sha256"]:
        raise ExecutableDescriptorRuntimeError(
            "executable_record_digest_mismatch",
            f"record_digest_mismatch:{authored_payload['node_id']}",
        )

    return {
        "valid": True,
        "runtime_version": EXECUTABLE_DESCRIPTOR_RUNTIME_VERSION,
        "cdl_dependency": CDL_037_DEPENDENCY,
        "node_dissemination_dependency": NODE_DISSEMINATION_DEPENDENCY,
        "record_sha256": regenerated["record_sha256"],
        "checks": [
            {"check_type": "runtime_version_supported", "passed": True},
            {"check_type": "cdl_dependency_locked", "passed": True},
            {"check_type": "node_dissemination_dependency_locked", "passed": True},
            {"check_type": "sandboxed_runtime_binding_enforced", "passed": True},
            {"check_type": "safety_contract_boundary_enforced", "passed": True},
            {"check_type": "genesis_trust_boundary_enforced", "passed": True},
            {"check_type": "record_digest_matches", "passed": True},
        ],
    }


def canonical_executable_descriptor_vectors() -> list[dict[str, Any]]:
    """Return a deep copy of canonical executable descriptor vectors."""

    return copy.deepcopy(CANONICAL_EXECUTABLE_DESCRIPTOR_VECTORS)
