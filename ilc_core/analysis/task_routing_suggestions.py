from dataclasses import dataclass
from typing import Dict, List, Any, Optional
import math

from ilc_core.analysis.namespace_health import NamespaceHealthSnapshot
from ilc_core.analysis.agent_profiles import AgentProfile
from ilc_core.analysis.problem_space_kpis import ProblemSpace

@dataclass
class TaskRoutingSuggestion:
    agent_id: str
    problem_space: str # ProblemSpace is technically a string (Literal) in current codebase
    suggested_task_type: str # e.g. "contradiction_sweep", "global_summary", "planning_task"
    barrier_level: str # "low" | "medium" | "high"
    score: float
    rationale: str # short tag like "stress:contradiction", "cohesion:low", etc.

def classify_namespace_stress(snap: NamespaceHealthSnapshot) -> str:
    """
    Return one of: "low", "medium", "high" based on snap.total_stress.
    Suggested thresholds (tweakable):
      total_stress < 0.3  -> "low"
      0.3 <= < 1.0        -> "medium"
      >= 1.0              -> "high"
    """
    if snap.total_stress < 0.3:
        return "low"
    elif snap.total_stress < 1.0:
        return "medium"
    else:
        return "high"

def suggest_tasks_for_agents(
    profiles: Dict[str, AgentProfile],
    namespace_health: NamespaceHealthSnapshot,
    *,
    max_suggestions_per_agent: int = 3,
) -> Dict[str, List[TaskRoutingSuggestion]]:
    """
    Generate prioritized task suggestions for each agent based on namespace health
    and agent profile signals (competency, stress preference, light cone).
    """
    results: Dict[str, List[TaskRoutingSuggestion]] = {}
    
    regime = classify_namespace_stress(namespace_health)
    
    # Determine regime-specific focus
    regime_focus_spaces = []
    regime_task_type = "generic_task"
    
    # Heuristic Logic
    if regime == "high" and namespace_health.contradiction_overflow >= 0.5 * max(1e-9, namespace_health.total_stress):
        # High Contradiction Stress
        regime_focus_spaces = ["LOCAL_CONSISTENCY"]
        regime_task_type = "contradiction_sweep"
        regime_tag = "regime:high_contradiction"
    elif namespace_health.cohesion_score < 0.4:
        # Low Cohesion (but not necessarily high stress per se, or just disorganized)
        regime_focus_spaces = ["GLOBAL_EXPLANATION", "POLICY_SYNTHESIS"]
        regime_task_type = "global_summary" # or policy_synthesis, picking one for simplicity
        regime_tag = "regime:low_cohesion"
    elif regime == "low":
        # Low Stress -> Exploration/Planning
        regime_focus_spaces = ["PLANNING", "EXPLORATION"]
        regime_task_type = "planning_task"
        regime_tag = "regime:low"
    else:
        # Medium / Default
        regime_focus_spaces = ["LOCAL_CONSISTENCY", "GLOBAL_EXPLANATION"]
        regime_task_type = "maintenance_task"
        regime_tag = f"regime:{regime}"

    for agent_id, profile in profiles.items():
        suggestions: List[TaskRoutingSuggestion] = []
        
        # 1. Extract competency
        comp = profile.competency or {}
        by_space = comp.get("by_space", {})
        
        # 2. Extract stress preference
        stress_pref = (profile.stress_response or {}).get("preference", "neutral")
        
        # 3. Extract light cone
        lc = profile.light_cone or {}
        lc_score = float(lc.get("light_cone_score", 0.0))
        
        # Candidate spaces: strict intersection with regime focus? 
        # Or should we allow agent to suggest ANY space they are good at, but boost regime ones?
        # The prompt says: "Focus spaces: ...". Let's stick to suggesting tasks primarily in focus spaces 
        # IF the agent has competency there. If comp empty, maybe fallback?
        # For this MVP, let's iterate over spaces the agent IS competent in, and score them.
        # But we also want to suggest the "regime task type".
        
        # Strategy: Iterate over regime_focus_spaces. If agent has data, use it. If not, maybe skip or use defaults.
        # Also iterate over agent's known spaces?
        # Let's iterate over the union, but only score if we have data or if it's a focus space.
        
        # Actually, let's keep it simple: iterate over regime_focus_spaces.
        # If agent has no competency entry, success_rate=0.0 -> score low.
        
        # Also check if agent has other strong spaces? The prompt implies strict regime guidance.
        # "In a low-stress snapshot: An agent with PLANNING competency is suggested 'planning_task'."
        
        # Let's iterate over ALL spaces in by_space, plus the regime_focus_spaces (deduplicated).
        candidate_spaces = set(by_space.keys()) | set(regime_focus_spaces)
        
        for space_name in candidate_spaces:
            # Get competency stats
            space_stats = by_space.get(space_name, {})
            tasks_count = space_stats.get("tasks", 0)
            success_rate = space_stats.get("success_rate", 0.0)
            
            # Aptitude
            # aptitude = success_rate * (1.0 + math.log1p(tasks))
            # If no history, assume small epsilon aptitude if it's a focus space?
            # Or just 0.0?
            if tasks_count == 0:
                 # If it is a regime focus space, give a tiny boost so they at least consider it?
                 # Prompt says "aptitude = success_rate * ...". If success_rate 0, aptitude 0.
                 # Let's stick to formula.
                 aptitude = 0.0
            else:
                aptitude = success_rate * (1.0 + math.log1p(tasks_count))
                
            # Determine task type and fit
            # If space is in regime_focus_spaces, use regime_task_type.
            # Else? Maybe "standard_task"?
            if space_name in regime_focus_spaces:
                task_type = regime_task_type
                is_focus = True
            else:
                # If not a focus space, use a generic name or skip?
                # The prompt examples suggest we drive the network.
                # Let's include it but maybe it gets lower score unless aptitude is huge.
                task_type = "routine_task"
                is_focus = False
            
            # Base Score
            base_score = aptitude
            
            # Stress Preference Multipliers
            if regime == "high":
                if stress_pref == "prefers_high":
                    base_score *= 1.2
                elif stress_pref == "prefers_low":
                    base_score *= 0.8
            elif regime == "low":
                if stress_pref == "prefers_low":
                    base_score *= 1.1
                    
            # Regime fit boost (if we are suggesting what the namespace needs)
            if is_focus:
                base_score *= 1.5
            
            # Light-cone tie-breaker
            final_score = base_score * (1.0 + 0.1 * lc_score)
            
            # Skip zero scores?
            if final_score <= 0.001:
                continue
                
            # Barrier Level
            if aptitude < 0.5:
                barrier = "low"
            elif aptitude < 1.5:
                barrier = "medium"
            else:
                # High aptitude
                barrier = "high"
                
            # Rationale
            rationale = f"{regime_tag},space:{space_name},pref:{stress_pref}"
            
            suggestions.append(TaskRoutingSuggestion(
                agent_id=agent_id,
                problem_space=space_name,
                suggested_task_type=task_type,
                barrier_level=barrier,
                score=final_score,
                rationale=rationale
            ))
            
        # Sort and truncate
        suggestions.sort(key=lambda s: s.score, reverse=True)
        results[agent_id] = suggestions[:max_suggestions_per_agent]
        
    return results
