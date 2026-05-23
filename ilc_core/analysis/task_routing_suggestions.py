# SPDX-License-Identifier: AGPL-3.0-or-later
from dataclasses import dataclass
from typing import Dict, List, Optional, TypeAlias
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


SuggestionMap: TypeAlias = Dict[str, List[TaskRoutingSuggestion]]

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

def _determine_regime_focus(
    regime: str,
    namespace_health: NamespaceHealthSnapshot
) -> tuple[List[str], str, str]:
    """Determine focus spaces and task type based on regime and health metrics."""
    # Heuristic Logic
    if regime == "high" and namespace_health.contradiction_overflow >= 0.5 * max(1e-9, namespace_health.total_stress):
        # High Contradiction Stress
        return ["LOCAL_CONSISTENCY"], "contradiction_sweep", "regime:high_contradiction"
    elif namespace_health.cohesion_score < 0.4:
        # Low Cohesion (but not necessarily high stress per se, or just disorganized)
        return ["GLOBAL_EXPLANATION", "POLICY_SYNTHESIS"], "global_summary", "regime:low_cohesion"
    elif regime == "low":
        # Low Stress -> Exploration/Planning
        return ["PLANNING", "EXPLORATION"], "planning_task", "regime:low"
    else:
        # Medium / Default
        return ["LOCAL_CONSISTENCY", "GLOBAL_EXPLANATION"], "maintenance_task", f"regime:{regime}"

def _score_suggestion_for_space(
    agent_id: str,
    space_name: str,
    profile: AgentProfile,
    regime: str,
    regime_tag: str,
    regime_focus_spaces: List[str],
    regime_task_type: str,
) -> Optional[TaskRoutingSuggestion]:
    """Calculate score and create suggestion for a specific space."""
    
    # 1. Extract competency
    comp = profile.competency or {}
    by_space = comp.get("by_space", {})
    space_stats = by_space.get(space_name, {})
    tasks_count = space_stats.get("tasks", 0)
    success_rate = space_stats.get("success_rate", 0.0)
    
    # Aptitude
    if tasks_count == 0:
         aptitude = 0.0
    else:
        aptitude = success_rate * (1.0 + math.log1p(tasks_count))
        
    # Determine task type and fit
    if space_name in regime_focus_spaces:
        task_type = regime_task_type
        is_focus = True
    else:
        task_type = "routine_task"
        is_focus = False
    
    # Base Score
    base_score = aptitude
    
    # Stress Preference Multipliers
    stress_pref = (profile.stress_response or {}).get("preference", "neutral")
    if regime == "high":
        if stress_pref == "prefers_high":
            base_score *= 1.2
        elif stress_pref == "prefers_low":
            base_score *= 0.8
    elif regime == "low":
        if stress_pref == "prefers_low":
            base_score *= 1.1
            
    # Regime fit boost
    if is_focus:
        base_score *= 1.5
    
    # Light-cone tie-breaker
    lc = profile.light_cone or {}
    lc_score = float(lc.get("light_cone_score", 0.0))
    final_score = base_score * (1.0 + 0.1 * lc_score)
    
    # Skip zero scores
    if final_score <= 0.001:
        return None
        
    # Barrier Level
    if aptitude < 0.5:
        barrier = "low"
    elif aptitude < 1.5:
        barrier = "medium"
    else:
        barrier = "high"
        
    # Rationale
    rationale = f"{regime_tag},space:{space_name},pref:{stress_pref}"
    
    return TaskRoutingSuggestion(
        agent_id=agent_id,
        problem_space=space_name,
        suggested_task_type=task_type,
        barrier_level=barrier,
        score=final_score,
        rationale=rationale
    )

def _generate_agent_suggestions(
    agent_id: str,
    profile: AgentProfile,
    regime: str,
    regime_focus_spaces: List[str],
    regime_task_type: str,
    regime_tag: str,
    max_suggestions: int,
) -> List[TaskRoutingSuggestion]:
    """Generate suggestions for a single agent."""
    suggestions: List[TaskRoutingSuggestion] = []
    
    comp = profile.competency or {}
    by_space = comp.get("by_space", {})
    
    # Candidate spaces: Union of agent competency spaces and regime focus spaces
    candidate_spaces = set(by_space.keys()) | set(regime_focus_spaces)
    
    for space_name in candidate_spaces:
        suggestion = _score_suggestion_for_space(
            agent_id, space_name, profile, regime, 
            regime_tag, regime_focus_spaces, regime_task_type
        )
        if suggestion:
            suggestions.append(suggestion)
            
    # Sort and truncate
    suggestions.sort(key=lambda s: s.score, reverse=True)
    return suggestions[:max_suggestions]

def suggest_tasks_for_agents(
    profiles: Dict[str, AgentProfile],
    namespace_health: NamespaceHealthSnapshot,
    *,
    max_suggestions_per_agent: int = 3,
) -> SuggestionMap:
    """
    Generate prioritized task suggestions for each agent based on namespace health
    and agent profile signals (competency, stress preference, light cone).
    """
    results: SuggestionMap = {}
    
    regime = classify_namespace_stress(namespace_health)
    
    # Determine regime-specific focus
    regime_focus_spaces, regime_task_type, regime_tag = _determine_regime_focus(
        regime, namespace_health
    )

    for agent_id, profile in profiles.items():
        results[agent_id] = _generate_agent_suggestions(
            agent_id, profile, regime, 
            regime_focus_spaces, regime_task_type, regime_tag,
            max_suggestions_per_agent
        )
        
    return results
