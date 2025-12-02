import csv
from pathlib import Path

from ilc_core.types import ClaimRecord, LinkRecord
from ilc_core.graph import EpistemicGraph
from ilc_core.protocol.params import ProtocolParams
from ilc_core.analysis.claim_scores import (
    ClaimInfluenceRow,
    build_claim_influence_table,
    write_claim_influence_csv,
)

def make_small_graph() -> EpistemicGraph:
    g = EpistemicGraph()
    c1 = ClaimRecord(id="c1", type="claim", agent_id="a", content="foo")
    c2 = ClaimRecord(id="c2", type="claim", agent_id="b", content="bar")
    g.add_claim(c1)
    g.add_claim(c2)

    g.add_link(LinkRecord(id="l1", link_type="supports", source_id="c1", target_id="c2"))
    g.add_link(LinkRecord(id="l2", link_type="refutes", source_id="c1", target_id="c2"))

    return g

def test_build_claim_influence_table_basic():
    g = make_small_graph()
    params = ProtocolParams()
    rows = build_claim_influence_table(g, params)

    # Only c2 is a target in this small graph
    assert len(rows) == 1
    row = rows[0]
    assert row.claim_id == "c2"
    assert row.supports_in == 1
    assert row.refutes_in == 1
    assert row.net_support == 0
    # With default weights 1 and 1, influence is 1 - 1 = 0
    assert row.influence_score == 0.0

def test_write_claim_influence_csv(tmp_path):
    rows = [
        ClaimInfluenceRow(
            claim_id="c1",
            supports_in=2,
            refutes_in=0,
            equivalent_in=0,
            depends_on_in=0,
            net_support=2,
            influence_score=2.0,
        )
    ]
    csv_path = tmp_path / "claim_influence.csv"
    write_claim_influence_csv(rows, csv_path)

    assert csv_path.exists()
    with csv_path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        rows_read = list(reader)

    assert len(rows_read) == 1
    r = rows_read[0]
    assert r["claim_id"] == "c1"
    assert r["influence_score"] == "2.0"
