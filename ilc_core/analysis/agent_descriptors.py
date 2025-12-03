from dataclasses import dataclass, field, asdict
from typing import Dict, List
from os import PathLike
from pathlib import Path
import csv

from ilc_core.analysis.problem_space_kpis import (
    ProblemSpace,
    compute_problem_space_kpis,
)

@dataclass
class AgentDescriptor:
    """
    Lightweight descriptor of an agent's behavior across problem spaces.
    """
    agent_id: str
    problem_space_counts: Dict[str, float] = field(default_factory=dict)
    total_tasks: float = 0.0
    dominant_problem_space: str = "OTHER"

    def as_dict(self) -> Dict[str, float]:
        data = {
            "agent_id": self.agent_id,
            "total_tasks": self.total_tasks,
            "dominant_problem_space": self.dominant_problem_space,
        }
        # Flatten counts with a prefix for clarity.
        for space, count in self.problem_space_counts.items():
            data[f"space_{space}"] = count
        return data


def build_agent_descriptors_from_task_rows(
    task_rows: List[Dict[str, str]],
) -> Dict[str, AgentDescriptor]:
    """
    Build AgentDescriptors from in-memory task rows.
    """
    space_kpis = compute_problem_space_kpis(task_rows)
    descriptors: Dict[str, AgentDescriptor] = {}

    for agent_id, stats in space_kpis.items():
        total_tasks = stats.get("total_tasks", 0.0)

        # Extract per-space counts (excluding total_tasks).
        problem_space_counts = {
            k: v for k, v in stats.items() if k != "total_tasks"
        }

        # Identify dominant problem space (ties broken arbitrarily by max).
        if problem_space_counts:
            dominant_space = max(problem_space_counts.items(), key=lambda kv: kv[1])[0]
        else:
            dominant_space = "OTHER"

        descriptors[agent_id] = AgentDescriptor(
            agent_id=agent_id,
            problem_space_counts=problem_space_counts,
            total_tasks=total_tasks,
            dominant_problem_space=dominant_space,
        )

    return descriptors


def load_tasks_csv(path: PathLike) -> List[Dict[str, str]]:
    """
    Convenience loader for tasks.csv to feed into descriptor builders.
    """
    p = Path(path)
    rows: List[Dict[str, str]] = []
    if not p.exists():
        return rows

    with p.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(dict(row))
    return rows


def build_agent_descriptors_from_tasks_csv(
    tasks_csv_path: PathLike,
) -> Dict[str, AgentDescriptor]:
    """
    High-level helper: load tasks.csv and build AgentDescriptors.
    """
    rows = load_tasks_csv(tasks_csv_path)
    return build_agent_descriptors_from_task_rows(rows)
