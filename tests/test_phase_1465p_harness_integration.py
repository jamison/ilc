from ilc_core.harness.co_attestation_receipt import (
    build_co_attestation_receipt,
    verify_co_attestation_receipt,
)
from ilc_core.harness.idle_capacity_scheduler import IdleCapacityScheduler
from ilc_core.harness.maintenance_task_executor import (
    MaintenanceTaskExecutor,
    verify_query_response_artifact,
)
from ilc_core.harness.provider_usage_adapter import ProviderUsageAdapter


def test_private_harness_full_stack_query_response_artifact() -> None:
    usage = ProviderUsageAdapter()
    usage.record_usage(
        provider_id="fixture-provider",
        input_tokens=10,
        output_tokens=5,
        cost_proxy="0.01",
        quota_headers={"x-ratelimit-remaining-tokens": "100"},
    )

    scheduler = IdleCapacityScheduler(min_complexity=2)
    candidate = IdleCapacityScheduler.candidate(
        task_id="task-1",
        provider_id="fixture-provider",
        requester_agent_id="agent-1",
        target_node_id="node-1",
        complexity=2,
        estimated_tokens=20,
        estimated_cost_proxy="0.02",
    )
    scheduled = scheduler.schedule(
        budget=usage.snapshot("fixture-provider"),
        candidates=[candidate],
    )

    executor = MaintenanceTaskExecutor(processing_capacity_tier="local_fixture_tier_1")
    artifact = executor.execute(
        task=scheduled[0],
        query_payload={"query": "verify private node"},
        response_payload={"result": "accepted_private_fixture"},
    )
    receipt = build_co_attestation_receipt(
        receipt_id="receipt-1",
        artifact_sha256=artifact.sha256,
        attestation_signatures=[
            {"agent_id": "agent-1", "signature": "sig-1"},
            {"agent_id": "agent-2", "signature": "sig-2"},
        ],
    )

    assert scheduled[0].activation_state == "private_fixture_only"
    assert verify_query_response_artifact(artifact) is True
    assert verify_co_attestation_receipt(receipt) is True
    assert artifact.public_rc_exclude is True
    assert receipt.public_rc_exclude is True
