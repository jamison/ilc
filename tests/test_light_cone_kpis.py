import pytest
from ilc_core.graph import EpistemicGraph
from ilc_core.types import ClaimRecord, LinkRecord
from ilc_core.analysis.light_cone_kpis import compute_agent_light_cone_kpis
from ilc_core.analysis.agent_profiles import AgentProfile, attach_light_cone_to_profiles

def test_compute_agent_light_cone_kpis_reach():
    g = EpistemicGraph()
    # Agent A -> B, Agent A -> C
    g.add_claim(ClaimRecord(id="c1", type="claim", agent_id="a", content="foo", signature="sig"))
    g.add_claim(ClaimRecord(id="c2", type="claim", agent_id="b", content="bar", signature="sig"))
    g.add_claim(ClaimRecord(id="c3", type="claim", agent_id="c", content="baz", signature="sig"))
    
    g.add_link(LinkRecord(id="l1", link_type="supports", source_id="c1", target_id="c2"))
    g.add_link(LinkRecord(id="l2", link_type="supports", source_id="c1", target_id="c3"))
    
    # Agent D: isolated
    g.add_claim(ClaimRecord(id="c4", type="claim", agent_id="d", content="qux", signature="sig"))
    
    kpis = compute_agent_light_cone_kpis(g, [])
    
    assert kpis["a"].reach_score == 2.0
    assert kpis["d"].reach_score == 0.0

def test_compute_agent_light_cone_kpis_horizon_domain():
    g = EpistemicGraph()
    tasks = [
        {"agent_id": "a", "problem_space": "LOCAL_CONSISTENCY", "horizon": 1.0},
        {"agent_id": "a", "problem_space": "GLOBAL_EXPLANATION", "horizon": 3.0},
        {"agent_id": "b", "problem_space": "LOCAL_CONSISTENCY", "verification_window": 5.0},
    ]
    
    kpis = compute_agent_light_cone_kpis(g, tasks)
    
    # Agent A: avg horizon (1+3)/2 = 2.0. Domain span = 2.
    assert kpis["a"].horizon_score == 2.0
    assert kpis["a"].domain_span == 2
    
    # Agent B: horizon 5.0. Domain span = 1.
    assert kpis["b"].horizon_score == 5.0
    assert kpis["b"].domain_span == 1

def test_light_cone_composite_score():
    g = EpistemicGraph()
    # Agent A: Reach 1 (c1->c2)
    g.add_claim(ClaimRecord(id="c1", type="claim", agent_id="a", content="foo", signature="sig"))
    g.add_claim(ClaimRecord(id="c2", type="claim", agent_id="b", content="bar", signature="sig"))
    g.add_link(LinkRecord(id="l1", link_type="supports", source_id="c1", target_id="c2"))
    
    # Agent A: Horizon 1, Domain 1
    tasks = [{"agent_id": "a", "problem_space": "LOCAL_CONSISTENCY", "horizon": 1.0}]
    
    kpis = compute_agent_light_cone_kpis(g, tasks)
    
    # Score = (1+1) * (1+1) * (1+1) = 8.0
    assert kpis["a"].light_cone_score == pytest.approx(8.0)

def test_attach_light_cone_to_profiles():
    g = EpistemicGraph()
    tasks = [{"agent_id": "a", "problem_space": "LOCAL_CONSISTENCY", "horizon": 1.0}]
    kpis = compute_agent_light_cone_kpis(g, tasks)
    
    profiles = {"a": AgentProfile(agent_id="a")}
    updated = attach_light_cone_to_profiles(profiles, kpis)
    
    assert "a" in updated
    assert updated["a"].light_cone["horizon_score"] == 1.0
