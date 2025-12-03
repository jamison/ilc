import pytest
from ilc_core.analysis.stress_response_kpis import (
    bucket_stress_level,
    compute_agent_stress_response,
    attach_stress_response_to_profiles,
    AgentStressResponseRow,
)
from ilc_core.analysis.agent_profiles import AgentProfile

def test_bucket_stress_level():
    assert bucket_stress_level(0.0) == "low"
    assert bucket_stress_level(0.49) == "low"
    assert bucket_stress_level(0.5) == "medium"
    assert bucket_stress_level(1.0) == "medium"
    assert bucket_stress_level(1.49) == "medium"
    assert bucket_stress_level(1.5) == "high"
    assert bucket_stress_level(2.0) == "high"

def test_compute_agent_stress_response_basic():
    samples = [
        {"agent_id": "a", "stress": 0.2, "success": True},  # low, success
        {"agent_id": "a", "stress": 0.2, "success": False}, # low, fail
        {"agent_id": "a", "stress": 2.0, "success": False}, # high, fail
        {"agent_id": "b", "stress": 2.0, "success": True},  # high, success
    ]
    
    kpis = compute_agent_stress_response(samples)
    
    # Agent A
    # Low: 2 tasks, 1 success -> 0.5 rate
    # High: 1 task, 0 success -> 0.0 rate
    a_row = kpis["a"]
    assert a_row.low_tasks == 2
    assert a_row.low_successes == 1
    assert a_row.low_success_rate == 0.5
    assert a_row.high_tasks == 1
    assert a_row.high_successes == 0
    assert a_row.high_success_rate == 0.0
    
    # Agent B
    # High: 1 task, 1 success -> 1.0 rate
    b_row = kpis["b"]
    assert b_row.high_tasks == 1
    assert b_row.high_successes == 1
    assert b_row.high_success_rate == 1.0

def test_preference_classification():
    # Prefers low
    row = AgentStressResponseRow(
        agent_id="test",
        low_tasks=10, low_successes=9, # 0.9
        high_tasks=10, high_successes=5, # 0.5
    )
    assert row.preference == "prefers_low"

    # Prefers high
    row = AgentStressResponseRow(
        agent_id="test",
        low_tasks=10, low_successes=5, # 0.5
        high_tasks=10, high_successes=9, # 0.9
    )
    assert row.preference == "prefers_high"

    # Neutral
    row = AgentStressResponseRow(
        agent_id="test",
        low_tasks=10, low_successes=5, # 0.5
        high_tasks=10, high_successes=5, # 0.5
    )
    assert row.preference == "neutral"

def test_attach_stress_response_to_profiles():
    profiles = {"a": AgentProfile(agent_id="a")}
    response = {
        "a": AgentStressResponseRow(agent_id="a", low_tasks=10),
        "b": AgentStressResponseRow(agent_id="b", high_tasks=5),
    }
    
    updated = attach_stress_response_to_profiles(profiles, response)
    
    assert "a" in updated
    assert updated["a"].stress_response["low_tasks"] == 10
    
    assert "b" in updated
    assert updated["b"].stress_response["high_tasks"] == 5
