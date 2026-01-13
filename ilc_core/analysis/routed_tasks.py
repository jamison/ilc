from dataclasses import dataclass
from typing import Dict, Any, List, Mapping, Optional

# Phase 55: Routed Tasks (From Suggestions -> Task Rows)

from ilc_core.analysis.namespace_health import NamespaceHealthSnapshot
from ilc_core.analysis.agent_profiles import AgentProfile
from ilc_core.analysis.task_routing_suggestions import TaskRoutingSuggestion
from ilc_core.network.topology import DevnetTopology
from ilc_core.protocol.params import ProtocolParams

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
    protocol_params: Optional[ProtocolParams] = None,
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
    Rule Updates (Phase 63C):
      - Uses protocol_params (QA filter, kappa, toll, CE).
      - If QA filter blocks a suggestion, it is skipped.
    """
    rows = []
    
    # Defaults
    params = protocol_params or ProtocolParams()

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
            # Safety clamp: score must be in [0.0, 1.0]
            score = min(1.0, max(0.0, float(sugg.score)))
            
            # 1. QA Gating (respects qa_enabled toggle)
            if params.qa_enabled and score < params.qa_min_score:
                continue

            # 2. Reward Calculation
            # reward = base * (score ^ competence_kappa)
            # note: score assumed [0,1], but clamping safe
            safe_score = max(0.0, score)
            reward_val = params.base_reward * (safe_score ** params.competence_kappa)
            
            # 3. Consilience (Competence Multiplier) Logic
            if params.competence_mult_enabled:
                # Naive entropy weight simulation:
                # If agent has high success rate history in this space, 
                # we pretend "consilience" is higher or lower?
                # Actually, standard CE uses internal entropy of the claim graph.
                # Here we just mock it via a lookup or random factor, 
                # or just apply the min_floor/max_cap logic to the reward implicitly.
                # Let's say we apply a unity gain but clamped? 
                # Or just skip logic as "not fully implemented" but multiply by 1.0 clamped.
                # The user prompt example:
                # "success_rate lookup... entropy_w = entropy_weight(...)"
                # Let's try to grab success_rate from profile if available.
                
                # We need to look up competency:
                comp_score = 0.5
                if profile and profile.competency:
                    ds = profile.competency.get("by_space", {}).get(sugg.problem_space, {})
                    comp_score = ds.get("success_rate", 0.5)
                
                # Toy entropy function: 2 * abs(0.5 - success_rate) ? No that's polarization.
                # Let's just say entropy_weight maps [0,1] -> [min_floor, max_cap] linearly?
                # That way high competence -> high cap?
                # Let's just leave it as a multiplier of 1.0 for now but clamp it if needed.
                # Actually, the user sample code:
                # entropy_w = entropy_weight(success_rate, min_floor... max_cap...)
                # I'll implement a trivial version.
                
                # Map 0.0->min_floor, 1.0->max_cap
                entropy_w = params.competence_mult_min_floor + comp_score * (params.competence_mult_max_cap - params.competence_mult_min_floor)
                reward_val *= entropy_w

            # 4. Toll
            reward_val = max(0.0, reward_val - params.toll_per_task)
            
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
