import pytest
from ilc_core.genesis.work_task import (
    EpistemicWorkTask,
    ep_task_to_json,
    ep_task_from_json,
)
from ilc_core.work.task_queue import TaskDescriptor

def test_epistemic_work_task_construction_and_alias():
    """Verify basic construction and alias handling (ecu.estimate)."""
    task = EpistemicWorkTask(
        task_id="task:123",
        task_class="star.map.embedding",
        agent_id="agent:test",
        region_scope=["region:A"],
        verification_method="hash-match",
        task_state="proposed",
        timestamp_created=1000,
        ecu_estimate=5.5,
    )

    assert task.task_id == "task:123"
    assert task.ecu_estimate == 5.5

    # Check alias export
    data = task.model_dump(by_alias=True)
    assert "ecu.estimate" in data
    assert data["ecu.estimate"] == 5.5
    assert "ecu_estimate" not in data

def test_epistemic_work_task_json_roundtrip():
    """Verify JSON round-trip with alias keys."""
    data = {
        "task_id": "task:roundtrip",
        "task_class": "contradiction.sweep",
        "agent_id": "agent:rt",
        "region_scope": ["region:B"],
        "verification_method": "signature",
        "task_state": "claimed",
        "timestamp_created": 2000,
        "ecu.estimate": 10.0,  # Input using alias
        "difficulty_factor": 1.2
    }

    # Parse
    task = ep_task_from_json(data)
    assert task.task_id == "task:roundtrip"
    assert task.ecu_estimate == 10.0
    assert task.difficulty_factor == 1.2

    # Serialize back
    data_out = ep_task_to_json(task)
    assert data_out["ecu.estimate"] == 10.0
    assert data_out["task_id"] == "task:roundtrip"

def test_task_queue_bridge_helper():
    """Verify TaskDescriptor.from_epistemic_work_task helper."""
    task = EpistemicWorkTask(
        task_id="task:bridge",
        task_class="custom",
        agent_id="agent:bridge",
        region_scope=[],
        verification_method="peer-audit",
        task_state="proposed",
        timestamp_created=3000,
    )

    td = TaskDescriptor.from_epistemic_work_task(task)

    assert td.task_id == "task:bridge"
    assert td.agent_id == "agent:bridge"
    assert td.task_type == "genesis.epistemic.work.task"
    assert "epistemic_work_task" in td.payload
    
    payload_task = td.payload["epistemic_work_task"]
    assert payload_task["task_id"] == "task:bridge"
    assert payload_task["task_class"] == "custom"

def test_task_queue_bridge_helper_override():
    """Verify agent_id override in bridge helper."""
    task = EpistemicWorkTask(
        task_id="task:override",
        task_class="custom",
        agent_id="agent:original",
        region_scope=[],
        verification_method="peer-audit",
        task_state="proposed",
        timestamp_created=4000,
    )

    td = TaskDescriptor.from_epistemic_work_task(task, agent_id_override="agent:new")
    assert td.agent_id == "agent:new"
