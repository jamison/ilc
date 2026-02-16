from typing import Mapping

import pytest

from ilc_core.analysis.node_value_input_canon import (
    collect_node_value_input_events,
    validate_node_value_input_event,
)
from ilc_core.exceptions import NodeValueInputValidationError


def test_validate_task_outcome_event_accepts_required_contract() -> None:
    event: Mapping[str, object] = {
        "kind": "task_outcome",
        "payload": {
            "task_id": "task-1",
            "agent_id": "agent-a",
            "epoch": 7,
            "reward_paid": 2.5,
            "stake_spent": 1.0,
            "success": True,
            "domain": "logic",
        },
    }

    normalized = validate_node_value_input_event(event)
    assert normalized["kind"] == "task_outcome"
    payload = normalized["payload"]
    assert payload["task_id"] == "task-1"
    assert payload["epoch"] == 7
    assert payload["success"] is True


def test_validate_event_rejects_missing_required_field() -> None:
    event: Mapping[str, object] = {
        "kind": "task_outcome",
        "payload": {
            "agent_id": "agent-a",
            "epoch": 7,
            "reward_paid": 2.5,
            "stake_spent": 1.0,
            "success": True,
            "domain": "logic",
        },
    }

    with pytest.raises(NodeValueInputValidationError) as exc_info:
        validate_node_value_input_event(event)

    assert str(exc_info.value) == "node_value_input_missing_task_id"


def test_collect_reports_telemetry_for_unknown_and_invalid_shapes() -> None:
    events: list[Mapping[str, object]] = [
        {
            "kind": "task_outcome",
            "payload": {
                "task_id": "task-1",
                "agent_id": "agent-a",
                "epoch": 7,
                "reward_paid": 2.5,
                "stake_spent": 1.0,
                "success": True,
                "domain": "logic",
            },
        },
        {
            "kind": "unrecognized_kind",
            "payload": {"x": 1},
        },
        {
            "kind": "claim",
            "payload": {
                "id": "claim-1",
                "agent_id": "agent-a",
                "timestamp": "2026-02-16T00:00:00Z",
                "net_stake": 1.25,
                "parent_ids": "bad-shape",
                "target_id": "node-1",
            },
        },
    ]

    accepted, telemetry = collect_node_value_input_events(events)
    assert len(accepted) == 1
    assert telemetry == {
        "total_seen": 3,
        "accepted": 1,
        "rejected_invalid_shape": 1,
        "rejected_unknown_kind": 1,
    }
