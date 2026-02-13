from ilc_core.graph import EpistemicGraph, GraphEdge
from ilc_core.types import ClaimRecord


def _seed_graph() -> EpistemicGraph:
    g = EpistemicGraph()
    c1 = ClaimRecord(id="c1", type="claim", agent_id="a", content="x", signature="sig")
    c2 = ClaimRecord(id="c2", type="claim", agent_id="b", content="y", signature="sig")
    g.add_claim(c1)
    g.add_claim(c2)
    return g


def test_add_edge_and_iterators():
    g = _seed_graph()
    edge = GraphEdge(source_id="c1", target_id="c2", type="derives_from")
    g.add_edge(edge)

    out_edges = list(g.iter_edges_from("c1"))
    in_edges = list(g.iter_edges_to("c2"))
    between = list(g.iter_edges_between("c1", "c2"))

    assert len(g.edges) == 1
    assert len(out_edges) == 1
    assert len(in_edges) == 1
    assert len(between) == 1
    assert out_edges[0].target_id == "c2"


def test_add_edge_by_ids_and_edge_count():
    g = _seed_graph()
    g.add_edge_by_ids("c1", "c2", "derives_from")

    assert g.edge_count() == 1
    out_edges = list(g.iter_edges_from("c1"))
    assert len(out_edges) == 1
    assert out_edges[0].target_id == "c2"


def test_iterators_track_legacy_direct_append():
    g = _seed_graph()
    g.edges.append(GraphEdge(source_id="c1", target_id="c2", type="derives_from"))

    # Lazy index rebuild should detect legacy mutation and still provide correct results.
    out_edges = list(g.iter_edges_from("c1"))
    assert len(out_edges) == 1
    assert out_edges[0].target_id == "c2"


def test_add_edge_missing_node_raises():
    g = _seed_graph()

    try:
        g.add_edge(GraphEdge(source_id="missing", target_id="c2", type="derives_from"))
    except KeyError:
        pass
    else:
        raise AssertionError("Expected KeyError for unknown source_id")


def test_legacy_direct_append_warns_once(caplog):
    g = _seed_graph()
    with caplog.at_level("WARNING"):
        g.edges.append(GraphEdge(source_id="c1", target_id="c2", type="derives_from"))
        list(g.iter_edges_from("c1"))
        list(g.iter_edges_from("c1"))

    messages = [record.getMessage() for record in caplog.records]
    assert sum("legacy_edge_mutation_detected" in msg for msg in messages) == 1
