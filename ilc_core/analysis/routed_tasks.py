from dataclasses import dataclass
from typing import Dict, Any, List, Mapping, Optional

# Phase 55: Routed Tasks (From Suggestions -> Task Rows)

from ilc_core.analysis.namespace_health import NamespaceHealthSnapshot
from ilc_core.analysis.agent_profiles import AgentProfile
from ilc_core.analysis.task_routing_suggestions import TaskRoutingSuggestion
from ilc_core.network.topology import DevnetTopology

@dataclass
class RoutedTaskRow:
    agent_id: str
    node_id: str
    namespace_id: str
    problem_space: str
    task_type: str
    barrier_level: str
    regime: str            # e.g. "low", "medium", "high"
    reward: float
    success: bool

    def as_dict(self) -> Dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "node_id": self.node_id,
            "namespace_id": self.namespace_id,
            "task_type": self.task_type,
            "problem_space": self.problem_space,
            "barrier_level": self.barrier_level,
            "regime": self.regime,
            "reward": self.reward,
            "success": self.success,
        }

def materialize_routed_tasks_for_epoch(
    epoch_index: int,
    namespace_snapshot: NamespaceHealthSnapshot,
    profiles: Dict[str, AgentProfile],
    suggestions: Dict[str, List[TaskRoutingSuggestion]],
    topology: DevnetTopology,
    *,
    base_reward: float = 1.0,
) -> List[RoutedTaskRow]:
    """
    Turn per-agent TaskRoutingSuggestion lists into concrete RoutedTaskRow objects.

    Rules (MVP):
      - node_id comes from profile.node_id if present, otherwise "unassigned".
      - namespace_id comes from namespace_snapshot.namespace_id.
      - regime is derived by a simple helper from snapshot.total_stress:
          total_stress < 0.3 -> "low"
          0.3 <= < 1.0       -> "medium"
          >= 1.0             -> "high"
      - reward:
          Start with base_reward (e.g. 1.0) and scale lightly by suggestion.score,
          e.g. reward = base_reward * (1.0 + 0.1 * suggestion.score)
          (clamp to non-negative).
      - success:
          For MVP, assume success=True if suggestion.score >= 0.5, else False
          (toy heuristic just to exercise downstream KPIs).
    """
    rows = []
    
    # Simple regime helper
    stress = namespace_snapshot.total_stress
    if stress < 0.3:
        regime = "low"
    elif stress < 1.0:
        regime = "medium"
    else:
        regime = "high"
        
    for agent_id, agent_suggestions in suggestions.items():
        profile = profiles.get(agent_id)
        node_id = "unassigned"
        if profile and profile.node_id:
            node_id = profile.node_id
            
        for sugg in agent_suggestions:
            # Heuristic reward/success logic
            # scale reward by score
            score = sugg.score
            reward_val = base_reward * (1.0 + 0.1 * score)
            reward_val = max(0.0, reward_val)
            
            # Simple success threshold
            is_success = score >= 0.5
            
            row = RoutedTaskRow(
                agent_id=agent_id,
                node_id=node_id,
                namespace_id=namespace_snapshot.namespace_id,
                problem_space=sugg.problem_space,
                task_type=sugg.suggested_task_type,
                barrier_level=sugg.barrier_level,
                regime=regime,
                reward=reward_val,
                success=is_success,
            )
            rows.append(row)
            
    return rows

def routed_tasks_to_task_rows_dicts(
    routed: List[RoutedTaskRow],
) -> List[Dict[str, Any]]:
    """
    Convert RoutedTaskRow list into a list of dicts consumable by:
      - compute_node_load_metrics (expects agent_id + reward)
      - competency / problem-space KPIs (agent_id, task_type, reward, success, etc.)

    Keys should include at least:
      - agent_id
      - node_id
      - namespace_id
      - task_type
      - problem_space
      - barrier_level
      - reward
      - success
    """
    return [r.as_dict() for r in routed]
