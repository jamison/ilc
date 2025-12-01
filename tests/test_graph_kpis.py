from ilc_core.types import ClaimRecord, LinkRecord
from ilc_core.graph import EpistemicGraph
from ilc_core.analysis.graph_kpis import (
    compute_claim_link_stats,
    find_conflict_hotspots,
)

def make_small_graph() -> EpistemicGraph:
    g = EpistemicGraph()
    c1 = ClaimRecord(id="c1", type="claim", agent_id="a", content="foo")
    c2 = ClaimRecord(id="c2", type="claim", agent_id="b", content="bar")
    c3 = ClaimRecord(id="c3", type="claim", agent_id="c", content="baz")
    g.add_claim(c1)
    g.add_claim(c2)
    g.add_claim(c3)

    g.add_link(LinkRecord(id="l1", link_type="supports", source_id="c1", target_id="c2"))
    g.add_link(LinkRecord(id="l2", link_type="refutes", source_id="c3", target_id="c2"))
    return g

def test_compute_claim_link_stats_basic():
    g = make_small_graph()
    stats = compute_claim_link_stats(g)

    assert "c2" in stats
    s = stats["c2"]
    assert s.supports_in == 1
    assert s.refutes_in == 1
    assert s.net_support == 0
    assert s.equivalent_in == 0
    assert s.depends_on_in == 0

def test_find_conflict_hotspots_basic():
    g = make_small_graph()
    hotspots = find_conflict_hotspots(g)
    assert "c2" in hotspots
    assert hotspots["c2"].is_controversial

def test_no_hotspots_if_threshold_not_met():
    g = make_small_graph()
    # c2 has 1 support, 1 refute.
    # If we require 2 supports, it shouldn't be a hotspot.
    hotspots = find_conflict_hotspots(g, min_supports=2)
    assert "c2" not in hotspots
