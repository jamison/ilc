from dataclasses import dataclass
from typing import Dict, Iterable, Mapping, Any

from ilc_core.analysis.problem_space_kpis import ProblemSpace, infer_problem_space

BarrierLevel = str  # or Literal["low", "medium", "high"]

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

def infer_barrier_level(row: Mapping[str, Any]) -> BarrierLevel:
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
    task_rows: Iterable[Mapping[str, Any]]
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
) -> Dict[str, Dict[str, Any]]:
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
    summary: Dict[str, Dict[str, Any]] = {}
    for agent_id, per_space in kpis.items():
        by_space: Dict[str, Any] = {}
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
        avg_success = sum(success_rates) / len(success_rates) if success_rates else 0.0
        summary[agent_id] = {
            "by_space": by_space,
            "global": {
                "total_tasks": total_tasks,
                "avg_success_rate": avg_success,
            },
        }
    return summary
