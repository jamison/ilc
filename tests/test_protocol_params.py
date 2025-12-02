import json
from pathlib import Path
import pytest

from ilc_core.protocol.params import ProtocolParams, load_protocol_params
from ilc_core.types import ClaimRecord, LinkRecord
from ilc_core.graph import EpistemicGraph
from ilc_core.analysis.graph_kpis import get_local_influence_scores

def test_protocol_params_defaults():
    params = ProtocolParams()
    assert params.local_influence_algorithm_id == "algo.local_influence.v0_toy"
    assert params.weight_supports == 1.0
    assert params.weight_refutes == 1.0

def test_load_protocol_params_from_json(tmp_path):
    params_file = tmp_path / "params.json"
    data = {
        "local_influence_algorithm_id": "algo.local_influence.v0_toy",
        "weight_supports": 2.0,
        "weight_refutes": 0.5,
    }
    with params_file.open("w", encoding="utf-8") as f:
        json.dump(data, f)

    params = load_protocol_params(params_file)
    assert params.local_influence_algorithm_id == "algo.local_influence.v0_toy"
    assert params.weight_supports == 2.0
    assert params.weight_refutes == 0.5

def test_get_local_influence_scores_dispatch():
    # Build a trivial graph with one support and one refute on same target
    g = EpistemicGraph()
    c1 = ClaimRecord(id="c1", type="claim", agent_id="a", content="foo")
    c2 = ClaimRecord(id="c2", type="claim", agent_id="b", content="bar")
    g.add_claim(c1)
    g.add_claim(c2)

    g.add_link(LinkRecord(id="l1", link_type="supports", source_id="c1", target_id="c2"))
    g.add_link(LinkRecord(id="l2", link_type="refutes", source_id="c1", target_id="c2"))

    params = ProtocolParams(
        local_influence_algorithm_id="algo.local_influence.v0_toy",
        weight_supports=1.0,
        weight_refutes=1.0,
    )
    scores = get_local_influence_scores(g, params)
    # 1 support - 1 refute -> 0
    assert scores["c2"] == 0.0

def test_get_local_influence_scores_unsupported_algo():
    g = EpistemicGraph()
    params = ProtocolParams(local_influence_algorithm_id="unknown_algo")
    
    with pytest.raises(ValueError, match="Unsupported local_influence_algorithm_id"):
        get_local_influence_scores(g, params)
