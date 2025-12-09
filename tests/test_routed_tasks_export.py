import pytest
import csv
import json
import tempfile
from pathlib import Path
from ilc_core.analysis.routed_tasks_export import (
    export_routed_tasks_to_csv,
    export_routed_tasks_to_json
)

def test_export_routed_tasks_roundtrip():
    tasks = [
        {"agent_id": "a1", "node_id": "n1", "reward": 5.0, "namespace": "ns1"},
        {"agent_id": "a2", "node_id": "n2", "reward": 10.0, "namespace": "ns1"},
    ]
    
    with tempfile.TemporaryDirectory() as tmp_dir:
        p = Path(tmp_dir)
        
        # Test CSV
        csv_path = p / "test.csv"
        export_routed_tasks_to_csv(tasks, csv_path)
        
        assert csv_path.exists()
        with open(csv_path, "r") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            
        assert len(rows) == 2
        assert rows[0]["agent_id"] == "a1"
        # CSV values are strings
        assert float(rows[1]["reward"]) == 10.0
        
        # Test JSON
        json_path = p / "test.json"
        export_routed_tasks_to_json(tasks, json_path)
        
        assert json_path.exists()
        with open(json_path, "r") as f:
            data = json.load(f)
            
        assert len(data) == 2
        assert data[0]["agent_id"] == "a1"
        assert data[1]["reward"] == 10.0 # JSON preserves numbers mostly

def test_export_routed_tasks_empty():
    with tempfile.TemporaryDirectory() as tmp_dir:
        p = Path(tmp_dir)
        
        # CSV
        csv_path = p / "empty.csv"
        export_routed_tasks_to_csv([], csv_path)
        assert csv_path.exists()
        # Should be empty file or maybe empty?
        assert csv_path.stat().st_size == 0
        
        # JSON
        json_path = p / "empty.json"
        export_routed_tasks_to_json([], json_path)
        assert json_path.exists()
        with open(json_path, "r") as f:
            data = json.load(f)
            assert data == []
