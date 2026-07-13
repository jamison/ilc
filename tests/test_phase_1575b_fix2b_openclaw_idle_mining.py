from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pytest

from ilc_core.sidecars.openclaw_idle_mining import (
    ALLOWED_TASK_TYPES,
    GRAPH_MAINTENANCE_TASK_TYPES,
    MAX_HISTORY_RECORDS,
    REVIEW_LANE_TASK_TYPES,
    build_task_envelope,
    evaluate_task_offer,
    execute_fixture_task,
    parse_provider_usage,
)
from ilc_core.sidecars.openclaw_local_capture import build_estimate_record


def _payload(label: str = "x") -> dict[str, object]:
    return {"fixture": label, "phase": "1575b-Fix2b"}


def _api_usage(tokens: int = 2000) -> dict[str, object]:
    return parse_provider_usage(
        provider_id="anthropic",
        headers={"anthropic-ratelimit-tokens-remaining": str(tokens)},
    )


def _offer(**overrides: object) -> dict[str, object]:
    base: dict[str, object] = {
        "task_type": "candidate_review",
        "input_payload": _payload(),
        "operator_agent_id": "operator:one",
        "local_agent_id": "agent:one",
        "autonomy_level": "maintenance_idle",
        "resource_policy_profile": "api_metered",
        "contribution_mode": "paid_api_budget_recovery",
        "provider_usage": _api_usage(),
        "min_remaining_tokens": 500,
        "session_consent": True,
        "hour_utc": 23,
        "user_active": False,
        "system_load_percent": 10,
        "max_system_load_percent": 40,
        "idle_window_id": "window:one",
    }
    base.update(overrides)
    return evaluate_task_offer(**base)


def test_api_metered_paid_api_budget_recovery_offers_review_lane_task_with_consent() -> None:
    offer = _offer(task_type="candidate_review")
    assert offer["allowed"] is True
    assert offer["resource_used"] == "api_metered"
    assert offer["contribution_mode"] == "paid_api_budget_recovery"


def test_api_metered_paid_api_budget_recovery_refuses_below_budget_threshold() -> None:
    offer = _offer(provider_usage=_api_usage(100), min_remaining_tokens=500)
    assert offer["allowed"] is False
    assert offer["block_reason"] == "budget_below_threshold"


def test_api_metered_paid_api_budget_recovery_refuses_without_session_consent() -> None:
    offer = _offer(session_consent=False)
    assert offer["allowed"] is False
    assert offer["block_reason"] == "session_consent_required"


def test_local_compute_offers_graph_maintenance_task_inside_idle_window() -> None:
    offer = _offer(
        task_type="star.map.embedding",
        resource_policy_profile="local_compute",
        contribution_mode="local_idle_compute_contribution",
        provider_usage=None,
        session_consent=False,
        hour_utc=23,
    )
    assert offer["allowed"] is True
    assert offer["resource_used"] == "local_compute"


def test_local_compute_refuses_outside_idle_window() -> None:
    offer = _offer(
        resource_policy_profile="local_compute",
        contribution_mode="local_idle_compute_contribution",
        provider_usage=None,
        session_consent=False,
        hour_utc=12,
    )
    assert offer["allowed"] is False
    assert offer["block_reason"] == "local_idle_conditions_not_met"


def test_hybrid_profile_uses_local_compute_first_and_blocks_api_escalation_without_flag() -> None:
    local = _offer(
        resource_policy_profile="hybrid",
        contribution_mode="local_idle_compute_contribution",
        provider_usage=parse_provider_usage(provider_id="gemini", local_remaining_tokens=2000),
        session_consent=True,
        hour_utc=23,
        allow_api_escalation=False,
    )
    assert local["allowed"] is True
    assert local["resource_used"] == "local_compute"
    blocked = _offer(
        resource_policy_profile="hybrid",
        contribution_mode="local_idle_compute_contribution",
        provider_usage=parse_provider_usage(provider_id="gemini", local_remaining_tokens=2000),
        session_consent=True,
        hour_utc=12,
        allow_api_escalation=False,
    )
    assert blocked["allowed"] is False
    assert blocked["block_reason"] == "api_escalation_not_allowed"


def test_provider_quota_is_not_included_in_ecu_estimate_math() -> None:
    first = _offer(provider_usage=_api_usage(2000))
    second = _offer(provider_usage=_api_usage(9000))
    assert first["allowed"] is True
    assert second["allowed"] is True
    first_result = execute_fixture_task(first["task_envelope"])
    second_result = execute_fixture_task(second["task_envelope"])
    assert build_estimate_record(first_result["capture"]) == build_estimate_record(second_result["capture"])


@pytest.mark.parametrize("autonomy", ["manual_only", "disabled", "bounded_autonomy"])
def test_idle_scheduler_refuses_non_maintenance_idle_autonomy_levels(autonomy: str) -> None:
    offer = _offer(autonomy_level=autonomy)
    assert offer["allowed"] is False
    assert offer["block_reason"] == "autonomy_not_maintenance_idle"


def test_per_agent_cap_is_enforced_per_idle_window() -> None:
    history = [
        {
            "idle_window_id": "window:one",
            "local_agent_id": "agent:one",
            "task_id": f"task:{idx}",
            "task_type": f"type:{idx}",
        }
        for idx in range(4)
    ]
    offer = _offer(task_type="candidate_review", task_history=history)
    assert offer["allowed"] is False
    assert offer["block_reason"] == "per_agent_idle_window_cap_exceeded"


def test_per_task_type_diversity_is_enforced_per_idle_window() -> None:
    history = [
        {
            "idle_window_id": "window:one",
            "local_agent_id": "agent:one",
            "task_id": "task:prior",
            "task_type": "candidate_review",
        }
    ]
    offer = _offer(task_type="candidate_review", input_payload=_payload("different"), task_history=history)
    assert offer["allowed"] is False
    assert offer["block_reason"] == "per_task_type_idle_window_cap_exceeded"


def test_duplicate_task_ids_are_suppressed() -> None:
    first = _offer(task_type="candidate_review", input_payload=_payload("same"))
    history = [
        {
            "idle_window_id": "window:one",
            "local_agent_id": "agent:one",
            "task_id": first["task_envelope"]["task_id"],
            "task_type": "other_type",
        }
    ]
    second = _offer(task_type="candidate_review", input_payload=_payload("same"), task_history=history)
    assert second["allowed"] is False
    assert second["block_reason"] == "duplicate_task_suppressed"


@pytest.mark.parametrize("task_type", sorted(ALLOWED_TASK_TYPES))
def test_every_allowlisted_task_type_produces_deterministic_envelope_with_subtype(task_type: str) -> None:
    first = build_task_envelope(
        task_type=task_type,
        input_payload=_payload(task_type),
        operator_agent_id="operator:one",
        local_agent_id="agent:one",
        resource_policy_profile="local_compute",
        contribution_mode="local_idle_compute_contribution",
    )
    second = build_task_envelope(
        task_type=task_type,
        input_payload=_payload(task_type),
        operator_agent_id="operator:one",
        local_agent_id="agent:one",
        resource_policy_profile="local_compute",
        contribution_mode="local_idle_compute_contribution",
    )
    assert first == second
    assert first["subtype"]
    assert task_type in (*GRAPH_MAINTENANCE_TASK_TYPES, *REVIEW_LANE_TASK_TYPES)


def test_task_type_outside_allowlist_is_rejected() -> None:
    with pytest.raises(ValueError):
        build_task_envelope(
            task_type="unknown",
            input_payload=_payload(),
            operator_agent_id="operator:one",
            local_agent_id="agent:one",
            resource_policy_profile="local_compute",
            contribution_mode="local_idle_compute_contribution",
        )


def test_result_routes_through_local_capture_with_local_only_consent_state() -> None:
    offer = _offer()
    result = execute_fixture_task(offer["task_envelope"])
    assert result["capture"]["payload_kind"] == "maintenance_result"
    assert result["capture"]["consent_state"] == "local_only"
    assert result["consent_gate_submit_decision"]["allowed"] is False
    assert result["consent_gate_submit_decision"]["public_submission_performed"] is False


def test_credit_boundary_flags_are_non_authorizing() -> None:
    result = execute_fixture_task(_offer()["task_envelope"])
    assert result["werner_credit_pending_track_c_cdl"] is True
    assert result["credit_minted"] is False
    assert result["wallet_write"] is False
    assert result["public_submission"] is False


def test_content_hash_equals_raw_task_result_payload_hash() -> None:
    result = execute_fixture_task(_offer()["task_envelope"])
    raw = json.dumps(result["raw_result_payload"], sort_keys=True, separators=(",", ":"), allow_nan=False)
    assert result["content_hash"] == hashlib.sha256(raw.encode("utf-8")).hexdigest()


def test_content_hash_differs_from_context_packed_prompt_hash() -> None:
    result = execute_fixture_task(_offer()["task_envelope"])
    assert result["content_hash"] != result["packed_context_hash"]


def test_envelope_fields_are_not_included_in_result_content_hash() -> None:
    first = execute_fixture_task(_offer(local_agent_id="agent:one")["task_envelope"])
    second = execute_fixture_task(_offer(local_agent_id="agent:two")["task_envelope"])
    assert first["content_hash"] == second["content_hash"]
    assert first["task_envelope"]["task_id"] != second["task_envelope"]["task_id"]


@pytest.mark.parametrize(
    "bad_kwargs",
    [
        {"min_remaining_tokens": 1.5},
        {"min_remaining_tokens": -1},
        {"system_load_percent": float("nan")},
        {"system_load_percent": True},
        {"input_payload": {"bad": float("inf")}},
    ],
)
def test_float_nan_infinity_bool_and_negative_inputs_are_rejected(bad_kwargs: dict[str, object]) -> None:
    with pytest.raises(ValueError):
        _offer(**bad_kwargs)


def test_overlarge_mapping_payload_is_rejected() -> None:
    with pytest.raises(ValueError, match="openclaw_idle_mapping_too_wide"):
        build_task_envelope(
            task_type="candidate_review",
            input_payload={str(index): "v" for index in range(65)},
            operator_agent_id="operator:one",
            local_agent_id="agent:one",
            resource_policy_profile="local_compute",
            contribution_mode="local_idle_compute_contribution",
        )


def test_overlarge_sequence_payload_is_rejected() -> None:
    with pytest.raises(ValueError, match="openclaw_idle_sequence_too_long"):
        build_task_envelope(
            task_type="candidate_review",
            input_payload={"items": list(range(65))},
            operator_agent_id="operator:one",
            local_agent_id="agent:one",
            resource_policy_profile="local_compute",
            contribution_mode="local_idle_compute_contribution",
        )


def test_task_history_over_max_records_raises() -> None:
    history = [
        {
            "idle_window_id": "window:one",
            "local_agent_id": "agent:one",
            "task_id": f"task:{index}",
            "task_type": "candidate_review",
        }
        for index in range(MAX_HISTORY_RECORDS + 1)
    ]
    with pytest.raises(ValueError, match="openclaw_task_history_too_large"):
        _offer(task_history=history)


def test_provider_headers_are_scheduling_hints_and_unknown_providers_use_local_counter() -> None:
    anthropic = parse_provider_usage(
        provider_id="anthropic",
        headers={"anthropic-ratelimit-tokens-remaining": "1500"},
    )
    openai = parse_provider_usage(
        provider_id="openai",
        headers={"x-ratelimit-remaining-tokens": "1600"},
    )
    gemini = parse_provider_usage(provider_id="gemini", local_remaining_tokens=1700)
    assert anthropic["provider_header_authority"] is True
    assert openai["provider_header_authority"] is True
    assert gemini["provider_header_authority"] is False
    assert gemini["provider_quota_authority"] == "local_counter_fallback"


def test_rehearsal_tool_writes_deterministic_evidence() -> None:
    subprocess.run([sys.executable, "tools/openclaw_idle_mining_rehearsal.py"], check=True)
    path = Path("out/block6_openclaw_idle_mining_fix2b/evidence_records.json")
    first = path.read_bytes()
    first_hash = hashlib.sha256(first).hexdigest()
    subprocess.run([sys.executable, "tools/openclaw_idle_mining_rehearsal.py"], check=True)
    second = path.read_bytes()
    assert hashlib.sha256(second).hexdigest() == first_hash
    data = json.loads(second)
    assert data["no_distributed_task_reservation"] is True
    assert data["no_ecu_minting"] is True
    assert data["mode_counts"]["paid_api_budget_recovery"] >= 2
    assert data["profile_counts"]["hybrid"] >= 1
