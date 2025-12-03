from ilc_core.analysis.agent_descriptors import (
    AgentDescriptor,
    build_agent_descriptors_from_task_rows,
)

def test_build_agent_descriptors_from_task_rows_basic():
    rows = [
        {
            "task_type": "contradiction_sweep",
            "domain": "graph",
            "agent_id": "agent:a",
        },
        {
            "task_type": "contradiction_sweep",
            "domain": "graph",
            "agent_id": "agent:a",
        },
        {
            "task_type": "global_summary",
            "domain": "global",
            "agent_id": "agent:b",
        },
    ]

    descriptors = build_agent_descriptors_from_task_rows(rows)
    assert "agent:a" in descriptors
    assert "agent:b" in descriptors

    a_desc = descriptors["agent:a"]
    assert a_desc.total_tasks == 2.0
    assert a_desc.problem_space_counts["LOCAL_CONSISTENCY"] == 2.0
    assert a_desc.dominant_problem_space == "LOCAL_CONSISTENCY"

    b_desc = descriptors["agent:b"]
    assert b_desc.total_tasks == 1.0
    assert b_desc.dominant_problem_space == "GLOBAL_EXPLANATION"
