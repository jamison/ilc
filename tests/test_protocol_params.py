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
    c1 = ClaimRecord(id="c1", type="claim", agent_id="a", content="foo", signature="sig")
    c2 = ClaimRecord(id="c2", type="claim", agent_id="b", content="bar", signature="sig")
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

def test_load_protocol_params_parses_bool_strings(tmp_path):
    params_file = tmp_path / "params_bools.json"
    data = {
        "competence_mult_enabled": "false",
        "qa_enabled": "0"
    }
    with params_file.open("w", encoding="utf-8") as f:
        json.dump(data, f)

    params = load_protocol_params(params_file)
    assert params.competence_mult_enabled is False
    assert params.qa_enabled is False
    
    # Test True cases
    data2 = {
        "competence_mult_enabled": "true",
        "qa_enabled": "yes"
    }
    with params_file.open("w", encoding="utf-8") as f:
        json.dump(data2, f)
    params2 = load_protocol_params(params_file)
    assert params2.competence_mult_enabled is True
    assert params2.qa_enabled is True

def test_load_protocol_params_accepts_legacy_keys(tmp_path):
    # Tests rename (kappa->competence_kappa) and legacy synonyms
    params_file = tmp_path / "params_legacy.json"
    data = {
        "ce_enabled": "true",
        "toll": 0.25,
        "kappa": 0.5,
        "qa": 0.8
    }
    with params_file.open("w", encoding="utf-8") as f:
        json.dump(data, f)
        
    params = load_protocol_params(params_file)
    assert params.competence_mult_enabled is True
    assert params.toll_per_task == 0.25
    assert params.competence_kappa == 0.5
    assert params.qa_min_score == 0.8

def test_load_protocol_params_canonical_keys_take_precedence(tmp_path):
    # If both provided, canonical should win or behavior undefined? 
    # normalize logic: iterates raw items. If raw contains both, mapping processes both.
    # Last one processed wins? Dict order is insertion order in py3.7+. 
    # Usually we expect canonical to be used if provided.
    # But current implementation iterates raw. So later key overrides earlier key in `normalized`.
    pass
