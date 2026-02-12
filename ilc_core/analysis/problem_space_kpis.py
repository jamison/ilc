from typing import Dict, List, Literal, Mapping, TypedDict, TypeAlias

# We keep this as a Literal set for now; can be expanded later.
ProblemSpace = Literal[
    "LOCAL_CONSISTENCY",
    "GLOBAL_EXPLANATION",
    "POLICY_SYNTHESIS",
    "PLANNING",
    "DATA_RETRIEVAL",
    "OTHER",
]


class ProblemSpaceKpiRow(TypedDict):
    total_tasks: float
    LOCAL_CONSISTENCY: float
    GLOBAL_EXPLANATION: float
    POLICY_SYNTHESIS: float
    PLANNING: float
    DATA_RETRIEVAL: float
    OTHER: float


ProblemSpaceKpiMap: TypeAlias = Dict[str, ProblemSpaceKpiRow]

TaskFieldValue: TypeAlias = str | int | float | bool | None
TaskRowLike: TypeAlias = Mapping[str, TaskFieldValue]


def infer_problem_space(task_row: TaskRowLike) -> str:
    """
    Infer the problem space for a task.

    If a 'problem_space' column exists, use it (with a default of 'OTHER').
    Otherwise, fall back to simple heuristics based on task_type/domain.
    For now, heuristics are intentionally minimal.
    """
    explicit = task_row.get("problem_space")
    if explicit:
        return explicit

    # Minimal placeholder heuristic: this can be expanded later.
    task_type = (task_row.get("task_type") or "").lower()
    domain = (task_row.get("domain") or "").lower()

    if "contradiction" in task_type or "consistency" in task_type:
        return "LOCAL_CONSISTENCY"
    if "policy" in task_type:
        return "POLICY_SYNTHESIS"
    if "summary" in task_type or "synthesis" in task_type or "global" in domain:
        return "GLOBAL_EXPLANATION"
    if "plan" in task_type:
        return "PLANNING"
    if "retrieval" in task_type or "search" in task_type or "retrieve" in task_type:
        return "DATA_RETRIEVAL"

    return "OTHER"


def compute_problem_space_kpis(
    task_rows: List[TaskRowLike],
) -> ProblemSpaceKpiMap:
    """
    Aggregate task counts per agent and per problem space.

    Returns:
        {
            agent_id: {
                'total_tasks': ...,
                'LOCAL_CONSISTENCY': ...,
                'GLOBAL_EXPLANATION': ...,
                'POLICY_SYNTHESIS': ...,
                'PLANNING': ...,
                'DATA_RETRIEVAL': ...,
                'OTHER': ...,
            },
            ...
        }
    """
    per_agent: ProblemSpaceKpiMap = {}

    for row in task_rows:
        agent_id = row.get("agent_id") or "unknown"
        ps = infer_problem_space(row)

        stats = per_agent.setdefault(
            agent_id,
            {
                "total_tasks": 0.0,
                "LOCAL_CONSISTENCY": 0.0,
                "GLOBAL_EXPLANATION": 0.0,
                "POLICY_SYNTHESIS": 0.0,
                "PLANNING": 0.0,
                "DATA_RETRIEVAL": 0.0,
                "OTHER": 0.0,
            },
        )

        stats["total_tasks"] += 1.0
        if ps in stats:
            stats[ps] += 1.0
        else:
            # Safety: unknown spaces bucketed into OTHER
            stats["OTHER"] += 1.0

    return per_agent
