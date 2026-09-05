# SPDX-License-Identifier: AGPL-3.0-only
from dataclasses import dataclass
from typing import Dict, Iterable, TypedDict, TypeAlias

from ilc_core.analysis.problem_space_kpis import ProblemSpace, TaskRowLike, infer_problem_space

BarrierLevel = str  # locked values: "low", "medium", "high"
_VALID_BARRIER_LEVELS = frozenset({"low", "medium", "high"})


class CompetencySpaceSummary(TypedDict):
    tasks: int
    success_rate: float
    barrier_low: int
    barrier_medium: int
    barrier_high: int


class CompetencyGlobalSummary(TypedDict):
    total_tasks: int
    avg_success_rate: float


AgentCompetencySummary = TypedDict(
    "AgentCompetencySummary",
    {
        "by_space": Dict[str, CompetencySpaceSummary],
        "global": CompetencyGlobalSummary,
    },
)


AgentCompetencySummaryMap: TypeAlias = Dict[str, AgentCompetencySummary]

@dataclass
class AgentCompetencyRow:
    agent_id: str
    problem_space: ProblemSpace
    tasks_completed: int
    successes: int
    barrier_low: int
    barrier_medium: int
    barrier_high: int

    @property
    def success_rate(self) -> float:
        return self.successes / self.tasks_completed if self.tasks_completed > 0 else 0.0

def infer_barrier_level(row: TaskRowLike) -> BarrierLevel:
    """
    Heuristic barrier inference:
      - If 'barrier_level' is explicitly present, use it.
      - Otherwise, infer from 'reward' as a toy proxy:
          reward < 1.0 -> "low"
          1.0 <= reward < 5.0 -> "medium"
          reward >= 5.0 -> "high"
    If 'reward' is missing or not parseable, default to 'low'.
    """
    explicit = row.get("barrier_level")
    if isinstance(explicit, str) and explicit:
        if explicit not in _VALID_BARRIER_LEVELS:
            raise ValueError("competency_barrier_level_invalid")
        return explicit

    reward_raw = row.get("reward", 0.0)
    try:
        reward = float(reward_raw)
    except (TypeError, ValueError):
        reward = 0.0

    if reward < 1.0:
        return "low"
    elif reward < 5.0:
        return "medium"
    else:
        return "high"

def compute_agent_competency_kpis(
    task_rows: Iterable[TaskRowLike]
) -> Dict[str, Dict[ProblemSpace, AgentCompetencyRow]]:
    """
    Aggregate competency metrics per (agent, problem_space).

    Success is interpreted from:
      - 'success' field if present (truthy)
      - otherwise: reward > 0.0 as a fallback heuristic.
    """
    result: Dict[str, Dict[ProblemSpace, AgentCompetencyRow]] = {}

    for row in task_rows:
        agent_id = str(row.get("agent_id", "unknown"))
        space = infer_problem_space(row)
        barrier = infer_barrier_level(row)

        # Initialize row if needed
        per_agent = result.setdefault(agent_id, {})
        comp = per_agent.get(space)
        if comp is None:
            comp = AgentCompetencyRow(
                agent_id=agent_id,
                problem_space=space,
                tasks_completed=0,
                successes=0,
                barrier_low=0,
                barrier_medium=0,
                barrier_high=0,
            )
            per_agent[space] = comp

        comp.tasks_completed += 1

        # success heuristic
        success_flag = row.get("success")
        if success_flag is None:
            # fall back to reward > 0
            reward_raw = row.get("reward", 0.0)
            try:
                reward = float(reward_raw)
            except (TypeError, ValueError):
                reward = 0.0
            success_flag = reward > 0.0

        if bool(success_flag):
            comp.successes += 1

        if barrier == "low":
            comp.barrier_low += 1
        elif barrier == "medium":
            comp.barrier_medium += 1
        elif barrier == "high":
            comp.barrier_high += 1

    return result

def summarize_competency_for_profile(
    kpis: Dict[str, Dict[ProblemSpace, AgentCompetencyRow]]
) -> AgentCompetencySummaryMap:
    """
    Convert nested competency rows into a per-agent summary dictionary
    suitable for embedding in AgentProfile.competency.

    Example structure per agent:
      {
        "by_space": {
          "LOCAL_CONSISTENCY": {"tasks": 10, "success_rate": 0.8},
          ...
        },
        "global": {
          "total_tasks": 42,
          "avg_success_rate": 0.7,
        },
      }
    """
    summary: AgentCompetencySummaryMap = {}
    for agent_id, per_space in kpis.items():
        by_space: Dict[str, CompetencySpaceSummary] = {}
        total_tasks = 0
        success_rates = []
        for space, row in per_space.items():
            total_tasks += row.tasks_completed
            by_space[str(space)] = {
                "tasks": row.tasks_completed,
                "success_rate": row.success_rate,
                "barrier_low": row.barrier_low,
                "barrier_medium": row.barrier_medium,
                "barrier_high": row.barrier_high,
            }
            success_rates.append(row.success_rate)
        total_successes = sum(row.successes for row in per_space.values())
        avg_success = total_successes / total_tasks if total_tasks else 0.0
        summary[agent_id] = {
            "by_space": by_space,
            "global": {
                "total_tasks": total_tasks,
                "avg_success_rate": avg_success,
            },
        }
    return summary
