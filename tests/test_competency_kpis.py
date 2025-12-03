import pytest
from ilc_core.analysis.competency_kpis import (
    infer_barrier_level,
    compute_agent_competency_kpis,
    summarize_competency_for_profile,
)
from ilc_core.analysis.agent_profiles import (
    AgentProfile,
    attach_competency_to_profiles,
)

def test_infer_barrier_level():
    assert infer_barrier_level({"barrier_level": "high"}) == "high"
    assert infer_barrier_level({"reward": 0.5}) == "low"
    assert infer_barrier_level({"reward": 2.0}) == "medium"
    assert infer_barrier_level({"reward": 10.0}) == "high"
    assert infer_barrier_level({}) == "low" # Default

def test_compute_agent_competency_kpis_basic():
    rows = [
        {"agent_id": "a", "task_type": "contradiction", "reward": 0.5, "success": True},
        {"agent_id": "a", "task_type": "contradiction", "reward": 0.5, "success": False},
        {"agent_id": "b", "task_type": "planning", "reward": 10.0, "success": True},
    ]

    kpis = compute_agent_competency_kpis(rows)
    
    # Agent A
    # LOCAL_CONSISTENCY (inferred from 'contradiction')
    # 2 tasks, 1 success. Barrier low.
    a_stats = kpis["a"]["LOCAL_CONSISTENCY"]
    assert a_stats.tasks_completed == 2
    assert a_stats.successes == 1
    assert a_stats.barrier_low == 2
    assert a_stats.success_rate == 0.5

    # Agent B
    # PLANNING (inferred from 'planning')
    # 1 task, 1 success. Barrier high.
    b_stats = kpis["b"]["PLANNING"]
    assert b_stats.tasks_completed == 1
    assert b_stats.successes == 1
    assert b_stats.barrier_high == 1
    assert b_stats.success_rate == 1.0

def test_summarize_competency_for_profile():
    rows = [
        {"agent_id": "a", "task_type": "contradiction", "reward": 0.5, "success": True},
    ]
    kpis = compute_agent_competency_kpis(rows)
    summary = summarize_competency_for_profile(kpis)

    assert "a" in summary
    a_sum = summary["a"]
    assert a_sum["global"]["total_tasks"] == 1
    assert a_sum["global"]["avg_success_rate"] == 1.0
    assert "LOCAL_CONSISTENCY" in a_sum["by_space"]
    assert a_sum["by_space"]["LOCAL_CONSISTENCY"]["tasks"] == 1

def test_attach_competency_to_profiles():
    profiles = {"a": AgentProfile(agent_id="a")}
    summary = {
        "a": {"global": {"total_tasks": 10}},
        "b": {"global": {"total_tasks": 5}},
    }
    
    updated = attach_competency_to_profiles(profiles, summary)
    
    assert "a" in updated
    assert updated["a"].competency == summary["a"]
    
    assert "b" in updated
    assert updated["b"].competency == summary["b"]
