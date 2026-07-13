# SPDX-License-Identifier: AGPL-3.0-only
"""Deterministic local OpenClaw capture helper.

This module is local/private harness glue. It does not call OpenClaw, provider
APIs, wallet code, public graph submission, minting, settlement, or activation
surfaces.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from decimal import Decimal
from typing import Any

OPENCLAW_LOCAL_CAPTURE_VERSION = "openclaw_local_capture_1575b_fix2a.v0.1"
ESTIMATE_SCHEMA_VERSION = "estimate_schema_v0.1_private_heuristic"

MAX_STRING_CHARS = 8192
MAX_MAPPING_KEYS = 64
MAX_SEQUENCE_ITEMS = 64
MAX_EDGE_HINTS = 16
MAX_DEPTH = 8

ALLOWED_CANDIDATE_NODE_TYPES = frozenset(
    {
        "claim_candidate",
        "evidence_candidate",
        "refutation_candidate",
        "summary_candidate",
        "test_result_candidate",
        "maintenance_result_candidate",
    }
)

ALLOWED_PAYLOAD_KINDS = frozenset(
    {
        "prompt",
        "reply",
        "tool_result",
        "api_result",
        "test_result",
        "maintenance_result",
    }
)

ALLOWED_PRIVACY_CLASSES = frozenset({"local_private", "public_candidate"})
ALLOWED_CONSENT_STATES = frozenset(
    {
        "local_only",
        "needs_review",
        "approved_for_public_submission",
        "rejected",
    }
)

SCORE_FIELDS = (
    "novelty_score",
    "reuse_potential",
    "evidence_strength",
    "falsifiability",
    "duplicate_risk",
    "privacy_risk",
)


@dataclass(frozen=True)
class CaptureEnvelope:
    capture_id: str
    source_harness: str
    operator_agent_id: str
    local_agent_id: str
    provider_id: str
    session_id_hash: str
    raw_payload_sha256: str
    payload_kind: str
    privacy_class: str
    created_epoch: int
    candidate_node_type: str
    candidate_edges: tuple[Mapping[str, str], ...]
    consent_state: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "candidate_edges": [dict(edge) for edge in self.candidate_edges],
            "candidate_node_type": self.candidate_node_type,
            "capture_id": self.capture_id,
            "consent_state": self.consent_state,
            "created_epoch": self.created_epoch,
            "local_agent_id": self.local_agent_id,
            "operator_agent_id": self.operator_agent_id,
            "payload_kind": self.payload_kind,
            "privacy_class": self.privacy_class,
            "provider_id": self.provider_id,
            "raw_payload_sha256": self.raw_payload_sha256,
            "session_id_hash": self.session_id_hash,
            "source_harness": self.source_harness,
        }


def canonical_json_bytes(payload: Mapping[str, Any]) -> bytes:
    _validate_json_input(payload)
    return json.dumps(
        payload,
        allow_nan=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")


def raw_payload_sha256(raw_payload: Mapping[str, Any]) -> str:
    return hashlib.sha256(canonical_json_bytes(raw_payload)).hexdigest()


def session_hash(session_id: str) -> str:
    _require_non_empty_string(session_id, "openclaw_session_id_invalid")
    return hashlib.sha256(session_id.encode("utf-8")).hexdigest()


def classify_payload(payload_kind: str, raw_payload: Mapping[str, Any]) -> str:
    _require_member(payload_kind, ALLOWED_PAYLOAD_KINDS, "openclaw_payload_kind_invalid")
    explicit = raw_payload.get("candidate_node_type")
    if explicit is not None:
        if type(explicit) is not str:
            raise ValueError("openclaw_candidate_node_type_invalid")
        _require_member(
            explicit,
            ALLOWED_CANDIDATE_NODE_TYPES,
            "openclaw_candidate_node_type_invalid",
        )
        return explicit
    if payload_kind in {"tool_result", "api_result"}:
        return "evidence_candidate"
    if payload_kind == "test_result":
        return "test_result_candidate"
    if payload_kind == "maintenance_result":
        return "maintenance_result_candidate"
    text = str(raw_payload.get("text", "")).lower()
    if any(marker in text for marker in ("refute", "contradict", "false")):
        return "refutation_candidate"
    if len(text) > 240:
        return "summary_candidate"
    return "claim_candidate"


def build_capture_envelope(
    *,
    raw_payload: Mapping[str, Any],
    payload_kind: str,
    operator_agent_id: str,
    local_agent_id: str,
    provider_id: str,
    session_id: str,
    source_harness: str = "openclaw",
    privacy_class: str = "local_private",
    created_epoch: int = 0,
    consent_state: str = "local_only",
    candidate_edges: Sequence[Mapping[str, str]] = (),
) -> CaptureEnvelope:
    _require_non_empty_string(source_harness, "openclaw_source_harness_invalid")
    _require_non_empty_string(operator_agent_id, "openclaw_operator_agent_id_invalid")
    _require_non_empty_string(local_agent_id, "openclaw_local_agent_id_invalid")
    _require_non_empty_string(provider_id, "openclaw_provider_id_invalid")
    if type(created_epoch) is not int or created_epoch < 0:
        raise ValueError("openclaw_created_epoch_invalid")
    _require_member(payload_kind, ALLOWED_PAYLOAD_KINDS, "openclaw_payload_kind_invalid")
    _require_member(privacy_class, ALLOWED_PRIVACY_CLASSES, "openclaw_privacy_class_invalid")
    _require_member(consent_state, ALLOWED_CONSENT_STATES, "openclaw_consent_state_invalid")
    _validate_json_input(raw_payload)
    edges = _coerce_edges(candidate_edges)
    payload_hash = raw_payload_sha256(raw_payload)
    candidate_node_type = classify_payload(payload_kind, raw_payload)
    capture_preimage = {
        "local_agent_id": local_agent_id,
        "operator_agent_id": operator_agent_id,
        "payload_kind": payload_kind,
        "raw_payload_sha256": payload_hash,
        "session_id_hash": session_hash(session_id),
        "source_harness": source_harness,
        "version": OPENCLAW_LOCAL_CAPTURE_VERSION,
    }
    capture_id = "openclaw_capture:" + hashlib.sha256(
        canonical_json_bytes(capture_preimage).decode("utf-8").encode("utf-8")
    ).hexdigest()
    return CaptureEnvelope(
        capture_id=capture_id,
        source_harness=source_harness,
        operator_agent_id=operator_agent_id,
        local_agent_id=local_agent_id,
        provider_id=provider_id,
        session_id_hash=capture_preimage["session_id_hash"],
        raw_payload_sha256=payload_hash,
        payload_kind=payload_kind,
        privacy_class=privacy_class,
        created_epoch=created_epoch,
        candidate_node_type=candidate_node_type,
        candidate_edges=edges,
        consent_state=consent_state,
    )


def estimate_private_ecu(
    envelope: CaptureEnvelope | Mapping[str, Any],
    *,
    local_duplicate_count: int = 0,
) -> dict[str, str]:
    data = envelope.to_dict() if isinstance(envelope, CaptureEnvelope) else dict(envelope)
    if type(local_duplicate_count) is not int or local_duplicate_count < 0:
        raise ValueError("openclaw_duplicate_count_invalid")
    node_type = str(data.get("candidate_node_type", ""))
    kind = str(data.get("payload_kind", ""))
    duplicate_risk = Decimal("1.00") if local_duplicate_count else Decimal("0.00")
    privacy_risk = Decimal("0.80") if data.get("privacy_class") != "local_private" else Decimal("0.20")
    evidence_strength = Decimal("0.80") if node_type in {"evidence_candidate", "test_result_candidate"} else Decimal("0.50")
    falsifiability = Decimal("0.75") if node_type in {"claim_candidate", "refutation_candidate", "test_result_candidate"} else Decimal("0.40")
    reuse_potential = Decimal("0.85") if kind in {"tool_result", "api_result", "maintenance_result"} else Decimal("0.55")
    novelty_score = max(Decimal("0.00"), Decimal("0.70") - (duplicate_risk * Decimal("0.70")))
    scores = {
        "duplicate_risk": duplicate_risk,
        "evidence_strength": evidence_strength,
        "falsifiability": falsifiability,
        "novelty_score": novelty_score,
        "privacy_risk": privacy_risk,
        "reuse_potential": reuse_potential,
    }
    return {key: _decimal_score(value) for key, value in scores.items()}


def build_estimate_record(
    envelope: CaptureEnvelope | Mapping[str, Any],
    *,
    local_duplicate_count: int = 0,
) -> dict[str, Any]:
    scores = estimate_private_ecu(envelope, local_duplicate_count=local_duplicate_count)
    return {
        "estimate_label": "non_binding_private_projection",
        "estimate_schema": ESTIMATE_SCHEMA_VERSION,
        "local_novelty_only": True,
        "not_claimability": True,
        "not_settlement": True,
        "not_wallet_balance": True,
        "score_fields": scores,
    }


def evaluate_consent_gate(
    envelope: CaptureEnvelope | Mapping[str, Any],
    *,
    action: str,
) -> dict[str, Any]:
    data = envelope.to_dict() if isinstance(envelope, CaptureEnvelope) else dict(envelope)
    _require_non_empty_string(action, "openclaw_consent_action_invalid")
    consent_state = data.get("consent_state")
    if consent_state not in ALLOWED_CONSENT_STATES:
        raise ValueError("openclaw_consent_state_invalid")
    if action != "submit":
        return {
            "action": action,
            "allowed": True,
            "authority": "local_private_only",
            "public_submission_performed": False,
        }
    allowed = consent_state == "approved_for_public_submission"
    return {
        "action": "submit",
        "allowed": allowed,
        "authority": "submission_intent_only" if allowed else "blocked_by_consent_gate",
        "defect_token": None if allowed else "openclaw_consent_gate_denied",
        "permanence_warning": (
            "public_graph_nodes_are_permanent_corrections_use_revision_refutation_pruning_reputation"
        ),
        "public_submission_performed": False,
    }


def build_status_record(envelopes: Sequence[CaptureEnvelope]) -> dict[str, Any]:
    return {
        "flagged_items": [
            env.capture_id
            for env in envelopes
            if env.consent_state in {"needs_review", "approved_for_public_submission"}
        ],
        "local_queue_count": len(envelopes),
        "next_human_action": "review_flagged_items_with_ilc_status",
        "policy_state": "bounded_autonomy_local_capture",
        "public_submission_performed": False,
    }


def _validate_json_input(value: Any, *, depth: int = 0) -> None:
    if depth > MAX_DEPTH:
        raise ValueError("openclaw_payload_depth_exceeded")
    if isinstance(value, bool):
        raise ValueError("openclaw_bool_as_int_rejected")
    if isinstance(value, float):
        raise ValueError("openclaw_float_not_allowed")
    if isinstance(value, str):
        if len(value) > MAX_STRING_CHARS:
            raise ValueError("openclaw_string_too_long")
        return
    if value is None or isinstance(value, int):
        return
    if isinstance(value, Mapping):
        if len(value) > MAX_MAPPING_KEYS:
            raise ValueError("openclaw_mapping_too_large")
        for key, nested in value.items():
            if type(key) is not str or not key or len(key) > MAX_STRING_CHARS:
                raise ValueError("openclaw_mapping_key_invalid")
            _validate_json_input(nested, depth=depth + 1)
        return
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        if len(value) > MAX_SEQUENCE_ITEMS:
            raise ValueError("openclaw_sequence_too_large")
        for nested in value:
            _validate_json_input(nested, depth=depth + 1)
        return
    raise ValueError("openclaw_payload_type_invalid")


def _require_non_empty_string(value: object, token: str) -> None:
    if type(value) is not str or not value or len(value) > MAX_STRING_CHARS:
        raise ValueError(token)


def _require_member(value: object, allowed: frozenset[str], token: str) -> None:
    if type(value) is not str or value not in allowed:
        raise ValueError(token)


def _coerce_edges(edges: Sequence[Mapping[str, str]]) -> tuple[Mapping[str, str], ...]:
    if not isinstance(edges, Sequence) or isinstance(edges, (str, bytes, bytearray)):
        raise ValueError("openclaw_candidate_edges_invalid")
    if len(edges) > MAX_EDGE_HINTS:
        raise ValueError("openclaw_candidate_edges_too_many")
    out: list[Mapping[str, str]] = []
    for edge in edges:
        if not isinstance(edge, Mapping):
            raise ValueError("openclaw_candidate_edge_invalid")
        source = edge.get("source", "local_capture")
        edge_type = edge.get("edge_type", "")
        target = edge.get("target", "")
        if type(source) is not str or type(edge_type) is not str or type(target) is not str:
            raise ValueError("openclaw_candidate_edge_invalid")
        if not edge_type or not target:
            raise ValueError("openclaw_candidate_edge_invalid")
        out.append({"edge_type": edge_type, "source": source, "target": target})
    return tuple(out)


def _decimal_score(value: Decimal) -> str:
    if not value.is_finite() or value < Decimal("0") or value > Decimal("1"):
        raise ValueError("openclaw_estimate_score_invalid")
    return str(value.quantize(Decimal("0.01")))


__all__ = [
    "ALLOWED_CANDIDATE_NODE_TYPES",
    "ALLOWED_CONSENT_STATES",
    "ALLOWED_PAYLOAD_KINDS",
    "ALLOWED_PRIVACY_CLASSES",
    "CaptureEnvelope",
    "ESTIMATE_SCHEMA_VERSION",
    "OPENCLAW_LOCAL_CAPTURE_VERSION",
    "SCORE_FIELDS",
    "build_capture_envelope",
    "build_estimate_record",
    "build_status_record",
    "canonical_json_bytes",
    "classify_payload",
    "estimate_private_ecu",
    "evaluate_consent_gate",
    "raw_payload_sha256",
    "session_hash",
]
