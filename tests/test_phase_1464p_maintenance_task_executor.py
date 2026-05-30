from decimal import Decimal

from ilc_core.harness.idle_capacity_scheduler import ScheduledMaintenanceTask
from ilc_core.harness.maintenance_task_executor import (
    MAINTENANCE_TASK_EXECUTOR_NOT_ACTIVATED,
    MaintenanceTaskExecutor,
    verify_query_response_artifact,
)


def test_maintenance_task_executor_builds_deterministic_private_artifact() -> None:
    task = ScheduledMaintenanceTask(
        task_id="task-1",
        provider_id="fixture-provider",
        requester_agent_id="agent-1",
        target_node_id="node-1",
        estimated_tokens=20,
    )
    executor = MaintenanceTaskExecutor(processing_capacity_tier="local_fixture_tier_1")

    artifact = executor.execute(
        task=task,
        query_payload={"question": "check node", "cost": str(Decimal("0.01"))},
        response_payload={"answer": "ok", "verdict": "private_fixture"},
    )

    assert MAINTENANCE_TASK_EXECUTOR_NOT_ACTIVATED is True
    assert artifact.public_rc_exclude is True
    assert artifact.processing_capacity_tier == "local_fixture_tier_1"
    assert artifact.query_node["truth_primitive"] == "assert.truth"
    assert artifact.response_node["truth_primitive"] == "validate.claim"
    assert verify_query_response_artifact(artifact) is True
