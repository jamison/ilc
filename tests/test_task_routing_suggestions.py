import pytest
from ilc_core.analysis.agent_profiles import AgentProfile
from ilc_core.analysis.namespace_health import NamespaceHealthSnapshot
from ilc_core.analysis.task_routing_suggestions import (
    classify_namespace_stress,
    suggest_tasks_for_agents,
    TaskRoutingSuggestion
)

def test_classify_namespace_stress():
    # Low (< 0.3)
    snap_low = NamespaceHealthSnapshot(
        epoch_index=1, namespace_id="n1", total_stress=0.1,
        validation_depth_error=0, contradiction_overflow=0, crosslink_deficit=0,
        support_ratio=0.5, controversy_ratio=0.5, mean_abs_influence=0.5, cohesion_score=0.5
    )
    assert classify_namespace_stress(snap_low) == "low"
    
    # Medium (0.3 <= x < 1.0)
    snap_med = NamespaceHealthSnapshot(
        epoch_index=1, namespace_id="n1", total_stress=0.5,
        validation_depth_error=0, contradiction_overflow=0, crosslink_deficit=0,
        support_ratio=0.5, controversy_ratio=0.5, mean_abs_influence=0.5, cohesion_score=0.5
    )
    assert classify_namespace_stress(snap_med) == "medium"
    
    # High (>= 1.0)
    snap_high = NamespaceHealthSnapshot(
        epoch_index=1, namespace_id="n1", total_stress=1.5,
        validation_depth_error=0, contradiction_overflow=0, crosslink_deficit=0,
        support_ratio=0.5, controversy_ratio=0.5, mean_abs_influence=0.5, cohesion_score=0.5
    )
    assert classify_namespace_stress(snap_high) == "high"

def test_high_contradiction_ranking():
    """
    In high stress + high contradiction, agents with high LOCAL_CONSISTENCY + prefers_high should be top.
    """
    snap_high = NamespaceHealthSnapshot(
        epoch_index=1, namespace_id="n1", total_stress=2.0,
        validation_depth_error=0, contradiction_overflow=1.5, # > 0.5 * 2.0
        crosslink_deficit=0,
        support_ratio=0.5, controversy_ratio=0.5, mean_abs_influence=0.5, cohesion_score=0.5
    )
    
    p1 = AgentProfile(agent_id="a1") # Warrior
    p1.competency = {"by_space": {"LOCAL_CONSISTENCY": {"tasks": 100, "success_rate": 1.0}}}
    p1.stress_response = {"preference": "prefers_high"}
    
    p2 = AgentProfile(agent_id="a2") # Weak / prefers low
    p2.competency = {"by_space": {"LOCAL_CONSISTENCY": {"tasks": 10, "success_rate": 0.5}}}
    p2.stress_response = {"preference": "prefers_low"}
    
    profiles = {"a1": p1, "a2": p2}
    suggestions = suggest_tasks_for_agents(profiles, snap_high)
    
    # Check a1
    s1 = suggestions["a1"]
    assert len(s1) > 0
    top = s1[0]
    assert top.problem_space == "LOCAL_CONSISTENCY"
    assert top.suggested_task_type == "contradiction_sweep"
    assert "regime:high_contradiction" in top.rationale
    # prefers_high should boost score
    # aptitude ~ 1.0 * log(101) ~ 4.6. Boost 1.5 (focus) * 1.2 (pref) -> big score.
    
    # Check a2
    s2 = suggestions["a2"]
    if s2:
        top_weak = s2[0]
        # prefers_low in high regime => penalty (x0.8)
        assert top_weak.score < top.score

def test_low_regime_planning():
    """
    Low stress -> Suggest planning/exploration.
    """
    snap_low = NamespaceHealthSnapshot(
        epoch_index=1, namespace_id="n1", total_stress=0.1,
        validation_depth_error=0, contradiction_overflow=0, crosslink_deficit=0,
        support_ratio=0.5, controversy_ratio=0.5, mean_abs_influence=0.5, cohesion_score=0.9
    )
    
    p = AgentProfile(agent_id="planner")
    p.competency = {"by_space": {"PLANNING": {"tasks": 50, "success_rate": 0.9}}}
    p.stress_response = {"preference": "prefers_low"}
    
    suggestions = suggest_tasks_for_agents({"planner": p}, snap_low)
    s = suggestions["planner"][0]
    
    assert s.suggested_task_type == "planning_task"
    assert "regime:low" in s.rationale
    assert s.problem_space == "PLANNING"
    # prefers_low in low regime => boost (x1.1)

def test_light_cone_tie_breaker():
    """
    Two identical agents, one with higher light cone -> higher score.
    """
    snap_med = NamespaceHealthSnapshot(
        epoch_index=1, namespace_id="n1", total_stress=0.5,
        validation_depth_error=0, contradiction_overflow=0, crosslink_deficit=0,
        support_ratio=0.5, controversy_ratio=0.5, mean_abs_influence=0.5, cohesion_score=0.8
    )
    
    p1 = AgentProfile(agent_id="a1")
    p1.competency = {"by_space": {"LOCAL_CONSISTENCY": {"tasks": 10, "success_rate": 0.8}}}
    p1.light_cone = {"light_cone_score": 10.0}
    
    p2 = AgentProfile(agent_id="a2")
    p2.competency = {"by_space": {"LOCAL_CONSISTENCY": {"tasks": 10, "success_rate": 0.8}}}
    p2.light_cone = {"light_cone_score": 100.0}
    
    suggestions = suggest_tasks_for_agents({"a1": p1, "a2": p2}, snap_med)
    
    s1 = suggestions["a1"][0]
    s2 = suggestions["a2"][0]
    
    assert s2.score > s1.score
