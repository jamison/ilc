# SPDX-License-Identifier: AGPL-3.0-only
"""Deterministic local OpenClaw idle-capacity scheduler rehearsal.

This module is local/private harness glue. Provider quota, local load, and idle
signals are scheduling hints only. They are not protocol truth, credit proof,
wallet state, settlement state, or public graph publication authority.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping, Sequence
from decimal import Decimal
from typing import Any

from ilc_core.sidecars.openclaw_local_capture import (
    CaptureEnvelope,
    build_capture_envelope,
    canonical_json_bytes,
    evaluate_consent_gate,
    raw_payload_sha256,
)

OPENCLAW_IDLE_CAPACITY_VERSION = "openclaw_idle_capacity_1575b_fix2b.v0.1"

CONTRIBUTION_MODES = frozenset(
    {
        "paid_api_budget_recovery",
        "local_idle_compute_contribution",
    }
)
RESOURCE_POLICY_PROFILES = frozenset({"api_metered", "local_compute", "hybrid"})
AUTONOMY_LEVELS = frozenset(
    {"disabled", "manual_only", "approve_low_risk", "bounded_autonomy", "maintenance_idle"}
)
GRAPH_MAINTENANCE_TASK_TYPES = (
    "star.map.embedding",
    "contradiction.sweep",
    "graph.compression",
    "stability.simulation",
)
REVIEW_LANE_TASK_TYPES = (
    "candidate_review",
    "exact_dedup_check",
    "evidence_strength_scoring",
    "falsifiability_classification",
    "node_quality_review",
    "queue_cleanup",
    "stale_node_triage",
    "test_proposal_generation",
)
ALLOWED_TASK_TYPES = frozenset((*GRAPH_MAINTENANCE_TASK_TYPES, *REVIEW_LANE_TASK_TYPES))
TASK_SUBTYPES = {
    "star.map.embedding": "embedding_record",
    "contradiction.sweep": "refutation_candidate_batch",
    "graph.compression": "compression_record",
    "stability.simulation": "simulation_result",
    **{task: "review_lane_result" for task in REVIEW_LANE_TASK_TYPES},
}

MAX_STRING_CHARS = 8192
MAX_HISTORY_RECORDS = 256
MAX_TASKS_PER_IDLE_WINDOW = 4
MAX_TASKS_PER_TYPE_PER_WINDOW = 1


def parse_provider_usage(
    *,
    provider_id: str,
    headers: Mapping[str, str] | None = None,
    local_remaining_tokens: int | None = None,
) -> dict[str, Any]:
    _require_non_empty_string(provider_id, "openclaw_provider_id_invalid")
    headers = dict(headers or {})
    provider_key = provider_id.lower()
    if provider_key == "anthropic":
        remaining = _header_int(headers, "anthropic-ratelimit-tokens-remaining")
        authority = "provider_header"
    elif provider_key == "openai":
        remaining = _header_int(headers, "x-ratelimit-remaining-tokens")
        authority = "provider_header"
    else:
        if local_remaining_tokens is None:
            raise ValueError("openclaw_local_counter_required")
        remaining = _require_non_negative_int(local_remaining_tokens, "openclaw_remaining_tokens_invalid")
        authority = "local_counter_fallback"
    return {
        "provider_id": provider_id,
        "provider_header_authority": authority == "provider_header",
        "provider_quota_authority": authority,
        "remaining_tokens": remaining,
        "scheduling_hint_only": True,
    }


def is_idle_window_active(
    *,
    hour_utc: int,
    idle_start_hour_utc: int = 22,
    idle_end_hour_utc: int = 6,
) -> bool:
    hour = _require_hour(hour_utc, "openclaw_hour_utc_invalid")
    start = _require_hour(idle_start_hour_utc, "openclaw_idle_start_invalid")
    end = _require_hour(idle_end_hour_utc, "openclaw_idle_end_invalid")
    if start == end:
        return True
    if start < end:
        return start <= hour < end
    return hour >= start or hour < end


def build_task_envelope(
    *,
    task_type: str,
    input_payload: Mapping[str, Any],
    operator_agent_id: str,
    local_agent_id: str,
    resource_policy_profile: str,
    contribution_mode: str,
) -> dict[str, Any]:
    _require_member(task_type, ALLOWED_TASK_TYPES, "openclaw_task_type_invalid")
    _require_member(resource_policy_profile, RESOURCE_POLICY_PROFILES, "openclaw_resource_profile_invalid")
    _require_member(contribution_mode, CONTRIBUTION_MODES, "openclaw_contribution_mode_invalid")
    _require_non_empty_string(operator_agent_id, "openclaw_operator_agent_id_invalid")
    _require_non_empty_string(local_agent_id, "openclaw_local_agent_id_invalid")
    _validate_payload(input_payload)
    input_content_hash = _sha256_mapping(input_payload)
    task_preimage = {
        "input_content_hash": input_content_hash,
        "local_agent_id": local_agent_id,
        "profile": resource_policy_profile,
        "task_type": task_type,
    }
    task_id = "openclaw_idle_task:" + hashlib.sha256(canonical_json_bytes(task_preimage)).hexdigest()
    return {
        "contribution_mode": contribution_mode,
        "input_content_hash": input_content_hash,
        "local_agent_id": local_agent_id,
        "operator_agent_id": operator_agent_id,
        "resource_policy_profile": resource_policy_profile,
        "subtype": TASK_SUBTYPES[task_type],
        "task_id": task_id,
        "task_type": task_type,
        "version": OPENCLAW_IDLE_CAPACITY_VERSION,
    }


def evaluate_task_offer(
    *,
    task_type: str,
    input_payload: Mapping[str, Any],
    operator_agent_id: str,
    local_agent_id: str,
    autonomy_level: str,
    resource_policy_profile: str,
    contribution_mode: str,
    provider_usage: Mapping[str, Any] | None = None,
    min_remaining_tokens: int = 0,
    session_consent: bool = False,
    hour_utc: int = 23,
    user_active: bool = False,
    system_load_percent: int = 0,
    max_system_load_percent: int = 40,
    local_compute_available: bool = True,
    allow_api_escalation: bool = False,
    task_history: Sequence[Mapping[str, Any]] = (),
    idle_window_id: str = "default_idle_window",
) -> dict[str, Any]:
    _require_member(autonomy_level, AUTONOMY_LEVELS, "openclaw_autonomy_level_invalid")
    _require_member(resource_policy_profile, RESOURCE_POLICY_PROFILES, "openclaw_resource_profile_invalid")
    _require_member(contribution_mode, CONTRIBUTION_MODES, "openclaw_contribution_mode_invalid")
    _require_member(task_type, ALLOWED_TASK_TYPES, "openclaw_task_type_invalid")
    min_tokens = _require_non_negative_int(min_remaining_tokens, "openclaw_min_tokens_invalid")
    load = _require_percent(system_load_percent, "openclaw_system_load_invalid")
    max_load = _require_percent(max_system_load_percent, "openclaw_max_system_load_invalid")
    _require_bool(session_consent, "openclaw_session_consent_invalid")
    _require_bool(user_active, "openclaw_user_active_invalid")
    _require_bool(local_compute_available, "openclaw_local_compute_available_invalid")
    _require_bool(allow_api_escalation, "openclaw_allow_api_escalation_invalid")
    _require_non_empty_string(idle_window_id, "openclaw_idle_window_id_invalid")
    envelope = build_task_envelope(
        task_type=task_type,
        input_payload=input_payload,
        operator_agent_id=operator_agent_id,
        local_agent_id=local_agent_id,
        resource_policy_profile=resource_policy_profile,
        contribution_mode=contribution_mode,
    )
    if autonomy_level != "maintenance_idle":
        return _blocked("autonomy_not_maintenance_idle", envelope)
    local_ok = (
        local_compute_available
        and not user_active
        and load <= max_load
        and is_idle_window_active(hour_utc=hour_utc)
    )
    api_ok = False
    if resource_policy_profile in {"api_metered", "hybrid"}:
        if not session_consent:
            return _blocked("session_consent_required", envelope)
        if provider_usage is None:
            return _blocked("provider_usage_required", envelope)
        remaining = _require_non_negative_int(
            provider_usage.get("remaining_tokens"),
            "openclaw_remaining_tokens_invalid",
        )
        api_ok = remaining >= min_tokens
        if resource_policy_profile == "api_metered" and not api_ok:
            return _blocked("budget_below_threshold", envelope)
    if resource_policy_profile == "local_compute":
        if not local_ok:
            return _blocked("local_idle_conditions_not_met", envelope)
        resource_used = "local_compute"
    elif resource_policy_profile == "api_metered":
        resource_used = "api_metered"
    else:
        if local_ok:
            resource_used = "local_compute"
        elif not allow_api_escalation:
            return _blocked("api_escalation_not_allowed", envelope)
        elif not api_ok:
            return _blocked("budget_below_threshold", envelope)
        else:
            resource_used = "api_metered"
    limit_reason = _anti_gaming_block_reason(
        history=task_history,
        local_agent_id=local_agent_id,
        task_id=envelope["task_id"],
        task_type=task_type,
        idle_window_id=idle_window_id,
    )
    if limit_reason:
        return _blocked(limit_reason, envelope)
    return {
        "allowed": True,
        "block_reason": None,
        "contribution_mode": contribution_mode,
        "idle_window_id": idle_window_id,
        "resource_policy_profile": resource_policy_profile,
        "resource_used": resource_used,
        "task_envelope": envelope,
    }


def execute_fixture_task(
    task_envelope: Mapping[str, Any],
    *,
    provider_id: str = "synthetic_provider",
) -> dict[str, Any]:
    envelope = dict(task_envelope)
    _require_member(envelope.get("task_type"), ALLOWED_TASK_TYPES, "openclaw_task_type_invalid")
    _require_member(
        envelope.get("resource_policy_profile"),
        RESOURCE_POLICY_PROFILES,
        "openclaw_resource_profile_invalid",
    )
    _require_member(envelope.get("contribution_mode"), CONTRIBUTION_MODES, "openclaw_contribution_mode_invalid")
    raw_result = {
        "input_content_hash": str(envelope["input_content_hash"]),
        "quality_marker": "synthetic_rehearsal_local_only",
        "result": "fixture_pass",
        "subtype": str(envelope["subtype"]),
        "task_type": str(envelope["task_type"]),
    }
    content_hash = raw_payload_sha256(raw_result)
    packed_context = {
        "operator_agent_id": str(envelope["operator_agent_id"]),
        "profile": str(envelope["resource_policy_profile"]),
        "raw_result": raw_result,
        "task_id": str(envelope["task_id"]),
    }
    packed_context_hash = _sha256_mapping(packed_context)
    capture = build_capture_envelope(
        raw_payload=raw_result,
        payload_kind="maintenance_result",
        operator_agent_id=str(envelope["operator_agent_id"]),
        local_agent_id=str(envelope["local_agent_id"]),
        provider_id=provider_id,
        session_id=str(envelope["task_id"]),
        consent_state="local_only",
        candidate_edges=(
            {"edge_type": "EVIDENCES", "target": str(envelope["task_id"])},
        ),
    )
    return {
        "capture": capture.to_dict(),
        "consent_gate_submit_decision": evaluate_consent_gate(capture, action="submit"),
        "content_hash": content_hash,
        "content_hash_excludes_envelope": True,
        "credit_minted": False,
        "packed_context_hash": packed_context_hash,
        "public_submission": False,
        "raw_result_payload": raw_result,
        "task_envelope": envelope,
        "wallet_write": False,
        "werner_credit_pending_track_c_cdl": True,
    }


def _blocked(reason: str, envelope: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "allowed": False,
        "block_reason": reason,
        "credit_minted": False,
        "public_submission": False,
        "task_envelope": dict(envelope),
        "wallet_write": False,
    }


def _anti_gaming_block_reason(
    *,
    history: Sequence[Mapping[str, Any]],
    local_agent_id: str,
    task_id: str,
    task_type: str,
    idle_window_id: str,
) -> str | None:
    if len(history) > MAX_HISTORY_RECORDS:
        raise ValueError("openclaw_task_history_too_large")
    same_agent = [
        record
        for record in history
        if record.get("local_agent_id") == local_agent_id
        and record.get("idle_window_id") == idle_window_id
    ]
    if any(record.get("task_id") == task_id for record in same_agent):
        return "duplicate_task_suppressed"
    if len(same_agent) >= MAX_TASKS_PER_IDLE_WINDOW:
        return "per_agent_idle_window_cap_exceeded"
    same_type = [record for record in same_agent if record.get("task_type") == task_type]
    if len(same_type) >= MAX_TASKS_PER_TYPE_PER_WINDOW:
        return "per_task_type_idle_window_cap_exceeded"
    return None


def _sha256_mapping(payload: Mapping[str, Any]) -> str:
    _validate_payload(payload)
    return hashlib.sha256(canonical_json_bytes(payload)).hexdigest()


def _validate_payload(value: Any, *, depth: int = 0) -> None:
    if depth > 8:
        raise ValueError("openclaw_idle_payload_depth_exceeded")
    if isinstance(value, bool):
        raise ValueError("openclaw_idle_bool_as_int_rejected")
    if isinstance(value, float):
        raise ValueError("openclaw_idle_float_not_allowed")
    if isinstance(value, str):
        if len(value) > MAX_STRING_CHARS:
            raise ValueError("openclaw_idle_string_too_long")
        return
    if value is None or isinstance(value, int):
        return
    if isinstance(value, Mapping):
        for key, nested in value.items():
            _require_non_empty_string(key, "openclaw_idle_mapping_key_invalid")
            _validate_payload(nested, depth=depth + 1)
        return
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for nested in value:
            _validate_payload(nested, depth=depth + 1)
        return
    raise ValueError("openclaw_idle_payload_type_invalid")


def _header_int(headers: Mapping[str, str], key: str) -> int:
    value = headers.get(key)
    if type(value) is not str or not value.isdigit():
        raise ValueError("openclaw_provider_header_invalid")
    return int(value)


def _require_non_negative_int(value: object, token: str) -> int:
    if type(value) is not int or value < 0:
        raise ValueError(token)
    return value


def _require_percent(value: object, token: str) -> int:
    percent = _require_non_negative_int(value, token)
    if percent > 100:
        raise ValueError(token)
    return percent


def _require_hour(value: object, token: str) -> int:
    hour = _require_non_negative_int(value, token)
    if hour > 23:
        raise ValueError(token)
    return hour


def _require_bool(value: object, token: str) -> None:
    if type(value) is not bool:
        raise ValueError(token)


def _require_non_empty_string(value: object, token: str) -> None:
    if type(value) is not str or not value or len(value) > MAX_STRING_CHARS:
        raise ValueError(token)


def _require_member(value: object, allowed: frozenset[str], token: str) -> None:
    if type(value) is not str or value not in allowed:
        raise ValueError(token)


__all__ = [
    "ALLOWED_TASK_TYPES",
    "AUTONOMY_LEVELS",
    "CONTRIBUTION_MODES",
    "GRAPH_MAINTENANCE_TASK_TYPES",
    "OPENCLAW_IDLE_CAPACITY_VERSION",
    "RESOURCE_POLICY_PROFILES",
    "REVIEW_LANE_TASK_TYPES",
    "TASK_SUBTYPES",
    "build_task_envelope",
    "evaluate_task_offer",
    "execute_fixture_task",
    "is_idle_window_active",
    "parse_provider_usage",
]
