import pytest
import csv
import json
from pathlib import Path
from ilc_core.analysis.agent_profiles import AgentProfile
from ilc_core.analysis.agent_dossier_export import (
    flatten_profile_for_csv,
    export_agent_dossiers_to_csv,
    export_agent_dossiers_to_json
)

def test_flatten_profile_for_csv_full():
    p = AgentProfile(agent_id="test_agent")
    p.econ = {"balance": 100.0}
    p.competency = {"global": {"total_tasks": 10, "avg_success_rate": 0.5}}
    p.stress_response = {"preference": "neutral"}
    p.light_cone = {"light_cone_score": 5.0, "reach_score": 1.0}
    
    row = flatten_profile_for_csv(p)
    
    assert row["agent_id"] == "test_agent"
    assert row["econ_balance"] == 100.0
    assert row["competency_total_tasks"] == 10
    assert row["competency_avg_success_rate"] == 0.5
    assert "competency_json" in row
    assert row["stress_preference"] == "neutral"
    assert "stress_response_json" in row
    assert row["light_cone_score"] == 5.0
    assert row["light_cone_reach"] == 1.0
    assert "light_cone_json" in row

def test_flatten_profile_for_csv_minimal():
    p = AgentProfile(agent_id="min_agent")
    row = flatten_profile_for_csv(p)
    
    assert row["agent_id"] == "min_agent"
    assert "competency_total_tasks" not in row
    assert "stress_preference" not in row
    assert "light_cone_score" not in row

def test_export_agent_dossiers_to_csv(tmp_path):
    p1 = AgentProfile(agent_id="a1", econ={"bal": 10})
    p2 = AgentProfile(agent_id="a2", econ={"bal": 20})
    profiles = {"a1": p1, "a2": p2}
    
    csv_path = tmp_path / "dossiers.csv"
    export_agent_dossiers_to_csv(profiles, csv_path)
    
    assert csv_path.exists()
    
    with open(csv_path, "r") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        
    assert len(rows) == 2
    # Check content
    r1 = next(r for r in rows if r["agent_id"] == "a1")
    assert float(r1["econ_bal"]) == 10.0

def test_export_agent_dossiers_to_json(tmp_path):
    p1 = AgentProfile(agent_id="a1", econ={"bal": 10})
    profiles = {"a1": p1}
    
    json_path = tmp_path / "dossiers.json"
    export_agent_dossiers_to_json(profiles, json_path)
    
    assert json_path.exists()
    
    with open(json_path, "r") as f:
        data = json.load(f)
        
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["agent_id"] == "a1"
    assert data[0]["econ_bal"] == 10.0
