import pytest
import csv
import json
from pathlib import Path
from ilc_core.analysis.namespace_health import NamespaceHealthSnapshot
from ilc_core.analysis.agent_profiles import AgentProfile
from ilc_core.analysis.epoch_report_export import (
    build_epoch_agent_rows,
    export_epoch_report_to_csv,
    export_epoch_report_to_json
)

@pytest.fixture
def snapshot():
    return NamespaceHealthSnapshot(
        epoch_index=1,
        namespace_id="ns:test",
        validation_depth_error=0.1,
        contradiction_overflow=0.2,
        crosslink_deficit=0.0,
        total_stress=0.5,
        support_ratio=0.8,
        controversy_ratio=0.0,
        mean_abs_influence=1.0,
        cohesion_score=0.9
    )

@pytest.fixture
def profiles():
    p1 = AgentProfile(agent_id="a1")
    p1.econ = {"bal": 10.0}
    
    p2 = AgentProfile(agent_id="a2")
    p2.competency = {"global": {"avg_success_rate": 0.8}}
    
    return {"a1": p1, "a2": p2}

def test_build_epoch_agent_rows(snapshot, profiles):
    rows = build_epoch_agent_rows(1, snapshot, profiles)
    assert len(rows) == 2
    
    # Check fields
    r1 = rows[0]
    assert r1["epoch_index"] == 1
    assert r1["namespace_id"] == "ns:test"
    assert "agent_id" in r1
    # Check flattening worked
    if r1["agent_id"] == "a1":
        assert r1["econ_bal"] == 10.0
    
def test_export_epoch_report_to_csv(tmp_path, snapshot, profiles):
    csv_path = tmp_path / "report.csv"
    export_epoch_report_to_csv(1, snapshot, profiles, csv_path)
    
    assert csv_path.exists()
    
    with open(csv_path, "r") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        
    assert len(rows) == 2
    header = reader.fieldnames
    assert "epoch_index" in header
    assert "total_stress" in header
    assert "agent_id" in header
    assert "econ_bal" in header # from p1
    assert "competency_avg_success_rate" in header # from p2

def test_export_epoch_report_to_json(tmp_path, snapshot, profiles):
    json_path = tmp_path / "report.json"
    export_epoch_report_to_json(1, snapshot, profiles, json_path)
    
    assert json_path.exists()
    
    with open(json_path, "r") as f:
        data = json.load(f)
        
    assert data["epoch_index"] == 1
    assert data["namespace"]["namespace_id"] == "ns:test"
    assert len(data["agents"]) == 2
    assert data["agents"][0]["agent_id"] in ["a1", "a2"]

def test_export_empty_profiles(tmp_path, snapshot):
    csv_path = tmp_path / "empty.csv"
    export_epoch_report_to_csv(1, snapshot, {}, csv_path)
    
    with open(csv_path, "r") as f:
        reader = csv.DictReader(f)
        assert "epoch_index" in reader.fieldnames
        assert len(list(reader)) == 0

    json_path = tmp_path / "empty.json"
    export_epoch_report_to_json(1, snapshot, {}, json_path)
    
    with open(json_path, "r") as f:
        data = json.load(f)
        assert data["agents"] == []
