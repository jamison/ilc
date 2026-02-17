from __future__ import annotations

import pytest

from ilc_core.exceptions import GraphIntegrityError
from ilc_core.graph import EpistemicGraph, GraphEdge
from ilc_core.types import ClaimRecord, LinkRecord


def _seed_graph() -> EpistemicGraph:
    g = EpistemicGraph()
    c1 = ClaimRecord(id="c1", type="claim", agent_id="a", content="x", signature="sig")
    c2 = ClaimRecord(id="c2", type="claim", agent_id="b", content="y", signature="sig")
    g.add_claim(c1)
    g.add_claim(c2)
    return g


def test_edge_path_accepts_lineage_type_only() -> None:
    g = _seed_graph()
    g.add_edge(GraphEdge(source_id="c1", target_id="c2", type="derives_from"))
    assert g.edge_count() == 1

    with pytest.raises(GraphIntegrityError):
        g.add_edge(GraphEdge(source_id="c1", target_id="c2", type="supports"))


def test_link_path_keeps_semantic_relation_types() -> None:
    g = _seed_graph()
    link = LinkRecord(
        id="l1",
        link_type="supports",
        source_id="c1",
        target_id="c2",
        agent_id="agent:test",
    )
    g.add_link(link)
    out = list(g.iter_links_between("c1", "c2"))
    assert len(out) == 1
    assert out[0].link_type == "supports"
