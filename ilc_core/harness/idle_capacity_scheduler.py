"""PUBLIC_RC_EXCLUDE: private_idle_capacity_scheduler
PUBLIC_RC_EXCLUDE_REASON: Private scheduler stub. No maintenance lottery activation or credit minting.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import TYPE_CHECKING

from ilc_core.harness.provider_usage_adapter import ProviderBudgetSnapshot

if TYPE_CHECKING:
    from ilc_core.analysis.node_value_kernel import NodeScoreVector

IDLE_CAPACITY_SCHEDULER_NOT_ACTIVATED = True
MAX_TASKS_PER_WINDOW = 16
MAX_CANDIDATES = 1024

# harness_kernel_decimal_integration_complete_phase_1477p


def _decimal_from_value(value: object, token: str) -> Decimal:
    if isinstance(value, bool):
        raise ValueError(token)
    try:
        out = Decimal(str(value))
    except (InvalidOperation, ValueError):
        raise ValueError(token) from None
    if not out.is_finite() or out < Decimal("0"):
        raise ValueError(token)
    return out


def _node_score_epistemic_weight(
    node_score: NodeScoreVector | None,
) -> Decimal:
    if node_score is None:
        return Decimal("0")
    epistemic_weight = node_score.get("epistemic_weight")
    if not isinstance(epistemic_weight, Decimal):
        raise ValueError("harness_kernel_integration_invalid_epistemic_weight")
    if not epistemic_weight.is_finite():
        raise ValueError("harness_kernel_integration_non_finite_epistemic_weight")
    return epistemic_weight


@dataclass(frozen=True)
class MaintenanceTaskCandidate:
    task_id: str
    provider_id: str
    requester_agent_id: str
    target_node_id: str
    complexity: int
    estimated_tokens: int
    estimated_cost_proxy: Decimal
    node_score: NodeScoreVector | None = None


@dataclass(frozen=True)
class ScheduledMaintenanceTask:
    task_id: str
    provider_id: str
    requester_agent_id: str
    target_node_id: str
    estimated_tokens: int
    activation_state: str = "private_fixture_only"


class IdleCapacityScheduler:
    """Routes idle local token budget to deterministic maintenance candidates."""

    def __init__(
        self,
        *,
        min_complexity: int = 1,
        max_tasks_per_window: int = MAX_TASKS_PER_WINDOW,
    ) -> None:
        if min_complexity < 1:
            raise ValueError("idle_scheduler_invalid_min_complexity")
        if max_tasks_per_window < 1 or max_tasks_per_window > MAX_TASKS_PER_WINDOW:
            raise ValueError("idle_scheduler_invalid_max_tasks")
        self._min_complexity = min_complexity
        self._max_tasks_per_window = max_tasks_per_window

    @staticmethod
    def candidate(
        *,
        task_id: str,
        provider_id: str,
        requester_agent_id: str,
        target_node_id: str,
        complexity: int,
        estimated_tokens: int,
        estimated_cost_proxy: object,
        node_score: NodeScoreVector | None = None,
    ) -> MaintenanceTaskCandidate:
        if "" in {task_id, provider_id, requester_agent_id, target_node_id}:
            raise ValueError("idle_scheduler_missing_identifier")
        if complexity < 1 or estimated_tokens < 1:
            raise ValueError("idle_scheduler_invalid_candidate_bounds")
        _node_score_epistemic_weight(node_score)
        return MaintenanceTaskCandidate(
            task_id=task_id,
            provider_id=provider_id,
            requester_agent_id=requester_agent_id,
            target_node_id=target_node_id,
            complexity=complexity,
            estimated_tokens=estimated_tokens,
            estimated_cost_proxy=_decimal_from_value(
                estimated_cost_proxy,
                "idle_scheduler_invalid_estimated_cost_proxy",
            ),
            node_score=node_score,
        )

    def schedule(
        self,
        *,
        budget: ProviderBudgetSnapshot,
        candidates: list[MaintenanceTaskCandidate],
    ) -> list[ScheduledMaintenanceTask]:
        if len(candidates) > MAX_CANDIDATES:
            raise ValueError("idle_scheduler_candidate_cap_exceeded")
        remaining = budget.remaining_tokens
        if remaining is None or remaining <= 0:
            return []

        scheduled: list[ScheduledMaintenanceTask] = []
        consumed = 0
        seen_requesters: dict[str, int] = {}
        for candidate in sorted(
            candidates,
            key=lambda row: (-_node_score_epistemic_weight(row.node_score), row.task_id),
        ):
            if len(scheduled) >= self._max_tasks_per_window:
                break
            if candidate.provider_id != budget.provider_id:
                continue
            if candidate.complexity < self._min_complexity:
                continue
            if candidate.requester_agent_id == candidate.target_node_id:
                continue
            requester_count = seen_requesters.get(candidate.requester_agent_id, 0)
            if requester_count >= 2:
                continue
            if consumed + candidate.estimated_tokens > remaining:
                continue
            scheduled.append(
                ScheduledMaintenanceTask(
                    task_id=candidate.task_id,
                    provider_id=candidate.provider_id,
                    requester_agent_id=candidate.requester_agent_id,
                    target_node_id=candidate.target_node_id,
                    estimated_tokens=candidate.estimated_tokens,
                )
            )
            consumed += candidate.estimated_tokens
            seen_requesters[candidate.requester_agent_id] = requester_count + 1
        return scheduled
