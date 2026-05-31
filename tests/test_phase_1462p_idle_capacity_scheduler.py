from decimal import Decimal

import pytest

from ilc_core.harness.idle_capacity_scheduler import (
    IDLE_CAPACITY_SCHEDULER_NOT_ACTIVATED,
    IdleCapacityScheduler,
    MAX_CANDIDATES,
)
from ilc_core.harness.provider_usage_adapter import ProviderBudgetSnapshot


def test_idle_capacity_scheduler_uses_private_budget_and_filters_gaming() -> None:
    budget = ProviderBudgetSnapshot(
        provider_id="fixture-provider",
        total_input_tokens=0,
        total_output_tokens=0,
        total_tokens=0,
        total_cost_proxy=Decimal("0"),
        remaining_tokens=50,
    )
    scheduler = IdleCapacityScheduler(min_complexity=2, max_tasks_per_window=2)
    candidates = [
        IdleCapacityScheduler.candidate(
            task_id="task-low",
            provider_id="fixture-provider",
            requester_agent_id="agent-1",
            target_node_id="node-1",
            complexity=1,
            estimated_tokens=5,
            estimated_cost_proxy="0.01",
        ),
        IdleCapacityScheduler.candidate(
            task_id="task-ok",
            provider_id="fixture-provider",
            requester_agent_id="agent-1",
            target_node_id="node-1",
            complexity=2,
            estimated_tokens=20,
            estimated_cost_proxy="0.02",
        ),
        IdleCapacityScheduler.candidate(
            task_id="task-self",
            provider_id="fixture-provider",
            requester_agent_id="agent-2",
            target_node_id="agent-2",
            complexity=3,
            estimated_tokens=5,
            estimated_cost_proxy="0.02",
        ),
    ]

    scheduled = scheduler.schedule(budget=budget, candidates=candidates)

    assert IDLE_CAPACITY_SCHEDULER_NOT_ACTIVATED is True
    assert [task.task_id for task in scheduled] == ["task-ok"]
    assert scheduled[0].activation_state == "private_fixture_only"


def test_idle_capacity_scheduler_returns_empty_without_remaining_budget() -> None:
    budget = ProviderBudgetSnapshot(
        provider_id="fixture-provider",
        total_input_tokens=0,
        total_output_tokens=0,
        total_tokens=0,
        total_cost_proxy=Decimal("0"),
        remaining_tokens=None,
    )
    scheduler = IdleCapacityScheduler()
    candidate = IdleCapacityScheduler.candidate(
        task_id="task-ok",
        provider_id="fixture-provider",
        requester_agent_id="agent-1",
        target_node_id="node-1",
        complexity=2,
        estimated_tokens=20,
        estimated_cost_proxy="0.02",
    )

    assert scheduler.schedule(budget=budget, candidates=[candidate]) == []


def test_idle_capacity_scheduler_enforces_candidate_cap() -> None:
    budget = ProviderBudgetSnapshot(
        provider_id="fixture-provider",
        total_input_tokens=0,
        total_output_tokens=0,
        total_tokens=0,
        total_cost_proxy=Decimal("0"),
        remaining_tokens=50,
    )
    candidate = IdleCapacityScheduler.candidate(
        task_id="task-ok",
        provider_id="fixture-provider",
        requester_agent_id="agent-1",
        target_node_id="node-1",
        complexity=2,
        estimated_tokens=20,
        estimated_cost_proxy="0.02",
    )

    with pytest.raises(ValueError) as exc:
        IdleCapacityScheduler().schedule(
            budget=budget,
            candidates=[candidate] * (MAX_CANDIDATES + 1),
        )

    assert str(exc.value) == "idle_scheduler_candidate_cap_exceeded"
