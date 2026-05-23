# SPDX-License-Identifier: AGPL-3.0-or-later
"""Phase 1387a public-economics admission firewall.

This module is the explicit construction boundary for public economic events.
Private, semi-private, shard-local, or operator-local advisory material may
exist, but it cannot construct protocol ECU, public reputation, public
settlement, public corroboration, or public claimability events.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Mapping
from typing import Any

from ilc_core.node.promotion_continuity_runtime_364 import (
    PromotionContinuityRuntimeError,
    verify_promotion_continuity_record,
)


PUBLIC_ECONOMICS_ADMISSION_FIREWALL_VERSION = (
    "public_economics_admission_firewall_phase_1387a.v0.1"
)

ACCEPTED_ADR_CDL_COVERAGE_TOKEN = "accepted_adr_cdl_coverage_phase_1387a_executed"
PUBLIC_NODE_ADMISSION_TOKEN = (
    "public_economics_requires_public_node_admission_verified_phase_1387a"
)
PRIVATE_VISIBILITY_EXCLUSION_TOKEN = (
    "private_visibility_excluded_from_public_economics_phase_1387a"
)

PUBLIC_ECONOMIC_EVENT_TYPES = frozenset(
    {
        "public_ecu",
        "public_reputation",
        "public_settlement",
        "public_corroboration",
        "public_claimability",
    }
)

PUBLIC_ELIGIBLE_STATES = frozenset(
    {
        "public_admitted",
        "public_evaluated",
        "public_promoted_zero_carry_forward",
    }
)

_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


class PublicEconomicsAdmissionError(ValueError):
    """Tokenized fail-closed admission error."""

    def __init__(self, token: str, message: str) -> None:
        super().__init__(message)
        self.token = token
        self.message = message


def _stable_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _stable_sha256(value: Any) -> str:
    return hashlib.sha256(_stable_json(value).encode("utf-8")).hexdigest()


def _require_mapping(value: Any, token: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise PublicEconomicsAdmissionError(token, token)
    return value


def _require_string(value: Any, token: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise PublicEconomicsAdmissionError(token, token)
    return value


def _require_non_negative_int(value: Any, token: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise PublicEconomicsAdmissionError(token, token)
    return value


def _reject_float_tree(value: Any, token: str) -> None:
    if isinstance(value, float):
        raise PublicEconomicsAdmissionError(token, token)
    if isinstance(value, Mapping):
        for child in value.values():
            _reject_float_tree(child, token)
    elif isinstance(value, (list, tuple)):
        for child in value:
            _reject_float_tree(child, token)


def _normalize_public_admission_evidence(value: Any) -> dict[str, Any]:
    evidence = _require_mapping(
        value,
        "public_graph_admission_evidence_missing_phase_1387a",
    )
    admission_id = _require_string(
        evidence.get("admission_id"),
        "public_graph_admission_id_missing_phase_1387a",
    )
    public_graph_root = _require_string(
        evidence.get("public_graph_root"),
        "public_graph_root_missing_phase_1387a",
    )
    admitted_epoch = _require_non_negative_int(
        evidence.get("admitted_epoch"),
        "public_graph_admitted_epoch_invalid_phase_1387a",
    )
    admission_proof_sha256 = _require_string(
        evidence.get("admission_proof_sha256"),
        "public_graph_admission_proof_missing_phase_1387a",
    )
    if not _SHA256_RE.fullmatch(admission_proof_sha256):
        raise PublicEconomicsAdmissionError(
            "public_graph_admission_proof_invalid_phase_1387a",
            "public_graph_admission_proof_invalid_phase_1387a",
        )
    return {
        "admission_id": admission_id,
        "admitted_epoch": admitted_epoch,
        "admission_proof_sha256": admission_proof_sha256,
        "public_graph_root": public_graph_root,
    }


def _private_carry_forward_is_zero(value: Any) -> bool:
    if value in (None, False):
        return True
    if not isinstance(value, Mapping):
        return False
    for child in value.values():
        if child not in (None, False, 0, "0", ""):
            return False
    return True


def _validate_no_private_priority_claim(node: Mapping[str, Any], node_id: str) -> None:
    forbidden_fields = (
        "private_priority_claim",
        "private_timestamp",
        "private_commitment_ref",
        "opaque_commitment_priority_ref",
        "quantum_hedge_private_sides",
    )
    for field in forbidden_fields:
        value = node.get(field)
        if value not in (None, False, 0, "", (), [], {}):
            raise PublicEconomicsAdmissionError(
                "private_or_opaque_commitments_do_not_create_retroactive_public_priority",
                f"private_priority_forbidden:{node_id}:{field}",
            )


def _validate_promotion_continuity_if_present(node: Mapping[str, Any], node_id: str) -> None:
    promoted = node.get("promoted_from_private", False)
    record = node.get("promotion_continuity_record")
    if promoted is True and record is None:
        raise PublicEconomicsAdmissionError(
            "public_promotion_continuity_record_required_phase_1387a",
            f"promotion_continuity_record_required:{node_id}",
        )
    if record is None:
        return
    try:
        verify_promotion_continuity_record(dict(record))
    except PromotionContinuityRuntimeError as exc:
        raise PublicEconomicsAdmissionError(
            "public_promotion_continuity_record_invalid_phase_1387a",
            exc.message,
        ) from exc
    successor = record["envelopes"]["authored_payload"]["public_successor_node"]
    if successor["node_cid"] != node_id:
        raise PublicEconomicsAdmissionError(
            "public_promotion_successor_node_mismatch_phase_1387a",
            f"promotion_successor_node_mismatch:{node_id}:{successor['node_cid']}",
        )


def validate_public_economics_admission(
    source_node: Mapping[str, Any],
    event_type: str,
) -> dict[str, Any]:
    """Validate that a source node may construct a public economic event."""

    if event_type not in PUBLIC_ECONOMIC_EVENT_TYPES:
        raise PublicEconomicsAdmissionError(
            "public_economic_event_type_invalid_phase_1387a",
            f"public_economic_event_type_invalid:{event_type}",
        )

    node = _require_mapping(source_node, "public_economic_source_node_not_object_phase_1387a")
    _reject_float_tree(node, "public_economic_source_node_float_forbidden_phase_1387a")

    node_id = _require_string(node.get("node_id"), "public_economic_source_node_id_missing_phase_1387a")
    visibility = _require_string(
        node.get("visibility"),
        "public_economic_source_visibility_missing_phase_1387a",
    )
    if visibility != "public":
        raise PublicEconomicsAdmissionError(
            PRIVATE_VISIBILITY_EXCLUSION_TOKEN,
            f"public_economic_source_visibility_invalid:{node_id}:{visibility}",
        )

    admission_evidence = _normalize_public_admission_evidence(
        node.get("public_graph_admission_evidence")
    )

    eligible_public_state = _require_string(
        node.get("eligible_public_state"),
        "public_economic_eligible_state_missing_phase_1387a",
    )
    if eligible_public_state not in PUBLIC_ELIGIBLE_STATES:
        raise PublicEconomicsAdmissionError(
            "public_economic_eligible_state_invalid_phase_1387a",
            f"public_economic_eligible_state_invalid:{node_id}:{eligible_public_state}",
        )

    if not _private_carry_forward_is_zero(node.get("private_promotion_carry_forward")):
        raise PublicEconomicsAdmissionError(
            "private_promotion_does_not_rewrite_existing_public_reward_history",
            f"private_promotion_carry_forward_forbidden:{node_id}",
        )

    _validate_no_private_priority_claim(node, node_id)
    _validate_promotion_continuity_if_present(node, node_id)

    return {
        "eligible_public_state": eligible_public_state,
        "event_type": event_type,
        "node_id": node_id,
        "public_graph_admission_evidence": admission_evidence,
        "visibility": "public",
    }


def build_public_economic_event(
    *,
    event_type: str,
    source_node: Mapping[str, Any],
    payload: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Construct a canonical public economic event after fail-closed admission."""

    normalized_source = validate_public_economics_admission(source_node, event_type)
    normalized_payload = dict(payload or {})
    _reject_float_tree(normalized_payload, "public_economic_event_payload_float_forbidden_phase_1387a")

    core = {
        "event_type": event_type,
        "firewall_version": PUBLIC_ECONOMICS_ADMISSION_FIREWALL_VERSION,
        "payload": normalized_payload,
        "source": normalized_source,
    }
    return {**core, "event_sha256": _stable_sha256(core)}


__all__ = [
    "ACCEPTED_ADR_CDL_COVERAGE_TOKEN",
    "PRIVATE_VISIBILITY_EXCLUSION_TOKEN",
    "PUBLIC_ECONOMIC_EVENT_TYPES",
    "PUBLIC_ECONOMICS_ADMISSION_FIREWALL_VERSION",
    "PUBLIC_ELIGIBLE_STATES",
    "PUBLIC_NODE_ADMISSION_TOKEN",
    "PublicEconomicsAdmissionError",
    "build_public_economic_event",
    "validate_public_economics_admission",
]
