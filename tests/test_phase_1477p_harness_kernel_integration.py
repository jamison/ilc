from decimal import Decimal

import pytest

from ilc_core.harness.idle_capacity_scheduler import (
    IDLE_CAPACITY_SCHEDULER_NOT_ACTIVATED,
    IdleCapacityScheduler,
)
from ilc_core.harness.provider_usage_adapter import ProviderBudgetSnapshot


def _budget() -> ProviderBudgetSnapshot:
    return ProviderBudgetSnapshot(
        provider_id="fixture-provider",
        total_input_tokens=0,
        total_output_tokens=0,
        total_tokens=0,
        total_cost_proxy=Decimal("0"),
        remaining_tokens=100,
    )


def _node_score(weight: Decimal) -> dict[str, object]:
    return {
        "node_id": "node-scored",
        "reuse_component": Decimal("0.1"),
        "contradiction_component": Decimal("0.1"),
        "validation_component": Decimal("0.1"),
        "path_component": Decimal("0.1"),
        "reuse_diversity_multiplier": Decimal("1"),
        "epistemic_weight": weight,
        "freshness_gate": Decimal("1"),
        "utility_flow": weight,
    }


def _candidate(task_id: str, *, weight: Decimal | None = None):
    return IdleCapacityScheduler.candidate(
        task_id=task_id,
        provider_id="fixture-provider",
        requester_agent_id=f"agent-{task_id}",
        target_node_id=f"node-{task_id}",
        complexity=1,
        estimated_tokens=10,
        estimated_cost_proxy="0.01",
        node_score=None if weight is None else _node_score(weight),
    )


def test_ordering_with_node_score_uses_decimal_comparison() -> None:
    scheduled = IdleCapacityScheduler().schedule(
        budget=_budget(),
        candidates=[
            _candidate("task-low", weight=Decimal("0.5")),
            _candidate("task-high", weight=Decimal("0.9")),
        ],
    )

    assert [task.task_id for task in scheduled] == ["task-high", "task-low"]


def test_ordering_decimal_string_equivalent_to_decimal_object() -> None:
    parsed_from_string = Decimal("0.75")
    direct_decimal = Decimal("0.75")

    scheduled_a = IdleCapacityScheduler().schedule(
        budget=_budget(),
        candidates=[
            _candidate("task-b", weight=parsed_from_string),
            _candidate("task-a", weight=Decimal("0.5")),
        ],
    )
    scheduled_b = IdleCapacityScheduler().schedule(
        budget=_budget(),
        candidates=[
            _candidate("task-b", weight=direct_decimal),
            _candidate("task-a", weight=Decimal("0.5")),
        ],
    )

    assert [task.task_id for task in scheduled_a] == [task.task_id for task in scheduled_b]


def test_epistemic_weight_type_remains_decimal() -> None:
    candidate = _candidate("task-decimal", weight=Decimal("0.75"))

    assert isinstance(candidate.node_score["epistemic_weight"], Decimal)  # type: ignore[index]
    IdleCapacityScheduler().schedule(budget=_budget(), candidates=[candidate])
    assert isinstance(candidate.node_score["epistemic_weight"], Decimal)  # type: ignore[index]


@pytest.mark.parametrize("weight", [Decimal("NaN"), Decimal("Infinity")])
def test_non_finite_epistemic_weight_rejected(weight: Decimal) -> None:
    with pytest.raises(
        ValueError,
        match="harness_kernel_integration_non_finite_epistemic_weight",
    ):
        _candidate("task-bad-weight", weight=weight)


def test_ordering_without_node_score_unchanged() -> None:
    scheduled = IdleCapacityScheduler().schedule(
        budget=_budget(),
        candidates=[
            _candidate("task-b"),
            _candidate("task-a"),
        ],
    )

    assert [task.task_id for task in scheduled] == ["task-a", "task-b"]


def test_idle_capacity_scheduler_not_activated_flag_unchanged() -> None:
    assert IDLE_CAPACITY_SCHEDULER_NOT_ACTIVATED is True
