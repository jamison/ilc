# SPDX-License-Identifier: AGPL-3.0-or-later
"""Phase-364 runtime for CDL-038 promotion continuity handling."""

from __future__ import annotations

import copy
import hashlib
import json
from typing import Any


PROMOTION_CONTINUITY_RUNTIME_VERSION = "promotion_continuity_runtime_364.v0.1"
CDL_038_DEPENDENCY = "cdl_038_ratified_353.v0.1"
EXECUTABLE_DESCRIPTOR_DEPENDENCY = "executable_descriptor_runtime_363.v0.1"

_PROMOTION_RECEIPT_FIELDS = (
    "original_node_cid",
    "public_successor_node_cid",
    "disclosed_lineage_reference",
    "promotion_epoch",
)

CANONICAL_PROMOTION_CONTINUITY_VECTORS: list[dict[str, Any]] = [
    {
        "original_private_node": {
            "node_cid": "bafy-private-401",
            "visibility": "private",
            "validation_state": "corroborated",
            "corroboration_reuse_credit": 12,
            "reputation_score": 44,
        },
        "public_successor_node": {
            "node_cid": "bafy-public-401",
            "visibility": "public",
            "validation_state": "proposed",
            "corroboration_reuse_credit": 0,
            "reputation_score": 0,
        },
        "promotion_receipt": {
            "original_node_cid": "bafy-private-401",
            "public_successor_node_cid": "bafy-public-401",
            "disclosed_lineage_reference": "lineage://private-401-to-public-401",
            "promotion_epoch": 364,
        },
    },
    {
        "original_private_node": {
            "node_cid": "bafy-private-402",
            "visibility": "private",
            "validation_state": "refuted",
            "corroboration_reuse_credit": 0,
            "reputation_score": 7,
        },
        "public_successor_node": {
            "node_cid": "bafy-public-402",
            "visibility": "public",
            "validation_state": "proposed",
            "corroboration_reuse_credit": 0,
            "reputation_score": 0,
        },
        "promotion_receipt": {
            "original_node_cid": "bafy-private-402",
            "public_successor_node_cid": "bafy-public-402",
            "disclosed_lineage_reference": "lineage://private-402-to-public-402",
            "promotion_epoch": 364,
        },
    },
]


class PromotionContinuityRuntimeError(ValueError):
    """Typed promotion validation error with deterministic tokenized semantics."""

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
        raise PromotionContinuityRuntimeError(token, message)
    return raw_value


def _normalize_original_private_node(raw_node: Any) -> dict[str, Any]:
    if not isinstance(raw_node, dict):
        raise PromotionContinuityRuntimeError(
            "promotion_original_node_not_object",
            "original_node_not_object",
        )

    node_cid = _validate_non_empty_string(
        raw_node.get("node_cid"),
        "promotion_original_node_cid_missing",
        "original_node_cid_missing",
    )
    visibility = _validate_non_empty_string(
        raw_node.get("visibility"),
        "promotion_original_visibility_missing",
        f"original_visibility_missing:{node_cid}",
    )
    if visibility != "private":
        raise PromotionContinuityRuntimeError(
            "promotion_original_visibility_invalid",
            f"original_visibility_invalid:{node_cid}:{visibility}",
        )

    validation_state = _validate_non_empty_string(
        raw_node.get("validation_state"),
        "promotion_original_validation_state_missing",
        f"original_validation_state_missing:{node_cid}",
    )

    corroboration_reuse_credit = raw_node.get("corroboration_reuse_credit")
    reputation_score = raw_node.get("reputation_score")
    if not isinstance(corroboration_reuse_credit, int) or corroboration_reuse_credit < 0:
        raise PromotionContinuityRuntimeError(
            "promotion_original_corroboration_credit_invalid",
            f"original_corroboration_credit_invalid:{node_cid}",
        )
    if not isinstance(reputation_score, int) or reputation_score < 0:
        raise PromotionContinuityRuntimeError(
            "promotion_original_reputation_invalid",
            f"original_reputation_invalid:{node_cid}",
        )

    return {
        "node_cid": node_cid,
        "visibility": visibility,
        "validation_state": validation_state,
        "corroboration_reuse_credit": corroboration_reuse_credit,
        "reputation_score": reputation_score,
    }


def _normalize_public_successor_node(raw_node: Any) -> dict[str, Any]:
    if not isinstance(raw_node, dict):
        raise PromotionContinuityRuntimeError(
            "promotion_successor_node_not_object",
            "successor_node_not_object",
        )

    node_cid = _validate_non_empty_string(
        raw_node.get("node_cid"),
        "promotion_successor_node_cid_missing",
        "successor_node_cid_missing",
    )
    visibility = _validate_non_empty_string(
        raw_node.get("visibility"),
        "promotion_successor_visibility_missing",
        f"successor_visibility_missing:{node_cid}",
    )
    if visibility != "public":
        raise PromotionContinuityRuntimeError(
            "promotion_successor_visibility_invalid",
            f"successor_visibility_invalid:{node_cid}:{visibility}",
        )

    validation_state = _validate_non_empty_string(
        raw_node.get("validation_state"),
        "promotion_successor_validation_state_missing",
        f"successor_validation_state_missing:{node_cid}",
    )
    if validation_state != "proposed":
        raise PromotionContinuityRuntimeError(
            "promotion_validation_state_carry_forward_forbidden",
            f"validation_state_carry_forward_forbidden:{node_cid}:{validation_state}",
        )

    corroboration_reuse_credit = raw_node.get("corroboration_reuse_credit")
    reputation_score = raw_node.get("reputation_score")
    if corroboration_reuse_credit != 0:
        raise PromotionContinuityRuntimeError(
            "promotion_corroboration_carry_forward_forbidden",
            f"corroboration_carry_forward_forbidden:{node_cid}:{corroboration_reuse_credit}",
        )
    if reputation_score != 0:
        raise PromotionContinuityRuntimeError(
            "promotion_reputation_carry_forward_forbidden",
            f"reputation_carry_forward_forbidden:{node_cid}:{reputation_score}",
        )

    return {
        "node_cid": node_cid,
        "visibility": visibility,
        "validation_state": validation_state,
        "corroboration_reuse_credit": 0,
        "reputation_score": 0,
    }


def _normalize_promotion_receipt(raw_receipt: Any) -> dict[str, Any]:
    if not isinstance(raw_receipt, dict):
        raise PromotionContinuityRuntimeError(
            "promotion_receipt_not_object",
            "promotion_receipt_not_object"
        )

    observed_fields = set(raw_receipt.keys())
    expected_fields = set(_PROMOTION_RECEIPT_FIELDS)
    if observed_fields != expected_fields:
        raise PromotionContinuityRuntimeError(
            "promotion_receipt_field_set_invalid",
            f"promotion_receipt_field_set_invalid:{tuple(sorted(observed_fields))}",
        )

    original_node_cid = _validate_non_empty_string(
        raw_receipt.get("original_node_cid"),
        "promotion_receipt_original_node_cid_missing",
        "promotion_receipt_original_node_cid_missing"
    )
    public_successor_node_cid = _validate_non_empty_string(
        raw_receipt.get("public_successor_node_cid"),
        "promotion_receipt_successor_node_cid_missing",
        "promotion_receipt_successor_node_cid_missing"
    )
    disclosed_lineage_reference = _validate_non_empty_string(
        raw_receipt.get("disclosed_lineage_reference"),
        "promotion_receipt_lineage_reference_missing",
        "promotion_receipt_lineage_reference_missing"
    )

    promotion_epoch = raw_receipt.get("promotion_epoch")
    if not isinstance(promotion_epoch, int) or promotion_epoch < 0:
        raise PromotionContinuityRuntimeError(
            "promotion_receipt_epoch_invalid",
            f"promotion_receipt_epoch_invalid:{promotion_epoch}",
        )

    return {
        "original_node_cid": original_node_cid,
        "public_successor_node_cid": public_successor_node_cid,
        "disclosed_lineage_reference": disclosed_lineage_reference,
        "promotion_epoch": promotion_epoch,
    }


def generate_promotion_continuity_record(payload: dict[str, Any]) -> dict[str, Any]:
    """Generate deterministic promotion continuity runtime output."""

    original_private_node = _normalize_original_private_node(payload.get("original_private_node"))
    public_successor_node = _normalize_public_successor_node(payload.get("public_successor_node"))
    promotion_receipt = _normalize_promotion_receipt(payload.get("promotion_receipt"))

    if original_private_node["node_cid"] == public_successor_node["node_cid"]:
        raise PromotionContinuityRuntimeError(
            "promotion_in_place_visibility_mutation_forbidden",
            f"in_place_visibility_mutation_forbidden:{original_private_node['node_cid']}",
        )

    if promotion_receipt["original_node_cid"] != original_private_node["node_cid"]:
        raise PromotionContinuityRuntimeError(
            "promotion_receipt_original_node_mismatch",
            f"promotion_receipt_original_node_mismatch:{promotion_receipt['original_node_cid']}:{original_private_node['node_cid']}",
        )
    if promotion_receipt["public_successor_node_cid"] != public_successor_node["node_cid"]:
        raise PromotionContinuityRuntimeError(
            "promotion_receipt_successor_node_mismatch",
            f"promotion_receipt_successor_node_mismatch:{promotion_receipt['public_successor_node_cid']}:{public_successor_node['node_cid']}",
        )

    protocol_interpretation = {
        "promotion_model": "successor_node_plus_promotion_receipt",
        "one_way_visibility_transition": True,
        "carry_forward_blocked": {
            "validation_state": True,
            "corroboration_reuse_credit": True,
            "reputation": True,
        },
    }

    transport = {
        "transition_direction": "private_to_public",
        "disclosed_lineage_reference": promotion_receipt["disclosed_lineage_reference"],
        "promotion_epoch": promotion_receipt["promotion_epoch"],
    }

    core = {
        "cdl_dependency": CDL_038_DEPENDENCY,
        "envelopes": {
            "authored_payload": {
                "original_private_node": original_private_node,
                "public_successor_node": public_successor_node,
                "promotion_receipt": promotion_receipt,
            },
            "protocol_interpretation": protocol_interpretation,
            "transport": transport,
        },
        "executable_descriptor_dependency": EXECUTABLE_DESCRIPTOR_DEPENDENCY,
        "runtime_version": PROMOTION_CONTINUITY_RUNTIME_VERSION,
    }

    return {**core, "record_sha256": _stable_sha256(core)}


def verify_promotion_continuity_record(record: dict[str, Any]) -> dict[str, Any]:
    """Verify deterministic promotion continuity runtime output."""

    if not isinstance(record, dict):
        raise PromotionContinuityRuntimeError(
            "promotion_record_not_object",
            "record_not_object",
        )

    if record.get("runtime_version") != PROMOTION_CONTINUITY_RUNTIME_VERSION:
        raise PromotionContinuityRuntimeError(
            "promotion_runtime_version_invalid",
            f"runtime_version_invalid:{record.get('runtime_version')}",
        )
    if record.get("cdl_dependency") != CDL_038_DEPENDENCY:
        raise PromotionContinuityRuntimeError(
            "promotion_cdl_dependency_invalid",
            f"cdl_dependency_invalid:{record.get('cdl_dependency')}",
        )
    if record.get("executable_descriptor_dependency") != EXECUTABLE_DESCRIPTOR_DEPENDENCY:
        raise PromotionContinuityRuntimeError(
            "promotion_executable_descriptor_dependency_invalid",
            f"executable_descriptor_dependency_invalid:{record.get('executable_descriptor_dependency')}",
        )

    envelopes = record.get("envelopes")
    if not isinstance(envelopes, dict):
        raise PromotionContinuityRuntimeError(
            "promotion_envelopes_not_object",
            "envelopes_not_object",
        )

    authored_payload = envelopes.get("authored_payload")
    protocol_interpretation = envelopes.get("protocol_interpretation")
    transport = envelopes.get("transport")

    if not isinstance(authored_payload, dict):
        raise PromotionContinuityRuntimeError(
            "promotion_authored_payload_not_object",
            "promotion_authored_payload_not_object"
        )
    if not isinstance(protocol_interpretation, dict):
        raise PromotionContinuityRuntimeError(
            "promotion_protocol_envelope_not_object",
            "promotion_protocol_envelope_not_object"
        )
    if not isinstance(transport, dict):
        raise PromotionContinuityRuntimeError(
            "promotion_transport_envelope_not_object",
            "promotion_transport_envelope_not_object"
        )

    original_private_node = _normalize_original_private_node(authored_payload.get("original_private_node"))
    public_successor_node = _normalize_public_successor_node(authored_payload.get("public_successor_node"))
    promotion_receipt = _normalize_promotion_receipt(authored_payload.get("promotion_receipt"))

    regenerated = generate_promotion_continuity_record(
        {
            "original_private_node": original_private_node,
            "public_successor_node": public_successor_node,
            "promotion_receipt": promotion_receipt,
        }
    )

    if protocol_interpretation != regenerated["envelopes"]["protocol_interpretation"]:
        raise PromotionContinuityRuntimeError(
            "promotion_protocol_interpretation_mismatch",
            "promotion_protocol_interpretation_mismatch"
        )
    if transport != regenerated["envelopes"]["transport"]:
        raise PromotionContinuityRuntimeError(
            "promotion_transport_envelope_mismatch",
            "promotion_transport_envelope_mismatch"
        )

    observed_core = {
        "cdl_dependency": record.get("cdl_dependency"),
        "envelopes": record.get("envelopes"),
        "executable_descriptor_dependency": record.get("executable_descriptor_dependency"),
        "runtime_version": record.get("runtime_version"),
    }
    expected_core = {
        "cdl_dependency": regenerated["cdl_dependency"],
        "envelopes": regenerated["envelopes"],
        "executable_descriptor_dependency": regenerated["executable_descriptor_dependency"],
        "runtime_version": regenerated["runtime_version"],
    }
    if _stable_json(_sorted_mapping(observed_core)) != _stable_json(_sorted_mapping(expected_core)):
        raise PromotionContinuityRuntimeError(
            "promotion_record_not_canonical",
            "promotion_record_not_canonical"
        )

    observed_digest = record.get("record_sha256")
    if not isinstance(observed_digest, str):
        raise PromotionContinuityRuntimeError(
            "promotion_record_digest_missing",
            "promotion_record_digest_missing"
        )
    if observed_digest != regenerated["record_sha256"]:
        raise PromotionContinuityRuntimeError(
            "promotion_record_digest_mismatch",
            "promotion_record_digest_mismatch"
        )

    return {
        "valid": True,
        "runtime_version": PROMOTION_CONTINUITY_RUNTIME_VERSION,
        "cdl_dependency": CDL_038_DEPENDENCY,
        "executable_descriptor_dependency": EXECUTABLE_DESCRIPTOR_DEPENDENCY,
        "record_sha256": regenerated["record_sha256"],
        "checks": [
            {"check_type": "runtime_version_supported", "passed": True},
            {"check_type": "cdl_dependency_locked", "passed": True},
            {"check_type": "executable_descriptor_dependency_locked", "passed": True},
            {"check_type": "successor_node_promotion_enforced", "passed": True},
            {"check_type": "in_place_visibility_mutation_forbidden", "passed": True},
            {"check_type": "carry_forward_blocked", "passed": True},
            {"check_type": "record_digest_matches", "passed": True},
        ],
    }


def canonical_promotion_continuity_vectors() -> list[dict[str, Any]]:
    """Return a deep copy of canonical promotion continuity vectors."""

    return copy.deepcopy(CANONICAL_PROMOTION_CONTINUITY_VECTORS)
