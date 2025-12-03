from ilc_core.analysis.problem_space_kpis import (
    infer_problem_space,
    compute_problem_space_kpis,
)

def test_infer_problem_space_explicit_column():
    row = {"problem_space": "GLOBAL_EXPLANATION"}
    assert infer_problem_space(row) == "GLOBAL_EXPLANATION"

def test_infer_problem_space_heuristics():
    row = {"task_type": "contradiction_sweep", "domain": "graph"}
    assert infer_problem_space(row) == "LOCAL_CONSISTENCY"

    row2 = {"task_type": "global_summary", "domain": "global"}
    assert infer_problem_space(row2) == "GLOBAL_EXPLANATION"

    row3 = {"task_type": "policy_synthesis", "domain": "governance"}
    assert infer_problem_space(row3) == "POLICY_SYNTHESIS"

    row4 = {"task_type": "retrieve", "domain": "search"}
    assert infer_problem_space(row4) == "DATA_RETRIEVAL"


def test_compute_problem_space_kpis_basic():
    rows = [
        {"task_type": "contradiction_sweep", "domain": "graph", "agent_id": "agent:a"},
        {"task_type": "global_summary", "domain": "global", "agent_id": "agent:a"},
        {"task_type": "policy_synthesis", "domain": "gov", "agent_id": "agent:b"},
    ]

    kpis = compute_problem_space_kpis(rows)
    assert "agent:a" in kpis
    assert "agent:b" in kpis

    a_stats = kpis["agent:a"]
    assert a_stats["total_tasks"] == 2.0
    assert a_stats["LOCAL_CONSISTENCY"] == 1.0
    assert a_stats["GLOBAL_EXPLANATION"] == 1.0

    b_stats = kpis["agent:b"]
    assert b_stats["total_tasks"] == 1.0
    assert b_stats["POLICY_SYNTHESIS"] == 1.0
