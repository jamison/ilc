import pytest
from ilc_core.types import ClaimRecord, LinkRecord
from ilc_core.links import validate_link_type
from ilc_core.graph import EpistemicGraph

def test_validate_link_type_accepts_mvp_types():
    for t in ("supports", "refutes", "equivalent", "depends_on"):
        assert validate_link_type(t) == t

def test_validate_link_type_rejects_invalid():
    with pytest.raises(ValueError):
        validate_link_type("invalid_type")

def test_epistemic_graph_add_and_query_links():
    graph = EpistemicGraph()

    c1 = ClaimRecord(
        id="c1",
        type="claim",
        agent_id="agent:a",
        content="foo",
    )
    c2 = ClaimRecord(
        id="c2",
        type="claim",
        agent_id="agent:b",
        content="bar",
    )
    graph.add_claim(c1)
    graph.add_claim(c2)

    link = LinkRecord(
        id="l1",
        link_type="supports",
        source_id="c1",
        target_id="c2",
        agent_id="agent:a",
    )
    graph.add_link(link)

    outgoing = list(graph.iter_links_from("c1"))
    incoming = list(graph.iter_links_to("c2"))
    assert len(outgoing) == 1
    assert len(incoming) == 1
    assert outgoing[0].id == "l1"
    assert incoming[0].id == "l1"

def test_add_duplicate_link_raises():
    graph = EpistemicGraph()
    c1 = ClaimRecord(id="c1", type="claim", agent_id="a", content="x")
    c2 = ClaimRecord(id="c2", type="claim", agent_id="b", content="y")
    graph.add_claim(c1)
    graph.add_claim(c2)

    link = LinkRecord(id="l1", link_type="supports", source_id="c1", target_id="c2", agent_id="a")
    graph.add_link(link)
    
    with pytest.raises(ValueError):
        graph.add_link(link)

def test_add_link_with_missing_nodes_raises():
    graph = EpistemicGraph()
    link = LinkRecord(id="l1", link_type="supports", source_id="missing1", target_id="missing2", agent_id="a")
    
    with pytest.raises(KeyError):
        graph.add_link(link)
