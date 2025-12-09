import pytest
import csv
import json
import tempfile
from pathlib import Path
from ilc_core.network.node_load_export import (
    export_node_load_to_csv,
    export_node_load_to_json
)

def test_export_node_load_roundtrip():
    load = {
        "n1": {"num_tasks": 10.0, "total_reward": 100.0, "avg_reward": 10.0},
        "n2": {"num_tasks": 5.0,  "total_reward": 20.0,  "avg_reward": 4.0},
    }
    
    with tempfile.TemporaryDirectory() as tmp_dir:
        p = Path(tmp_dir)
        
        # CSV
        csv_path = p / "load.csv"
        export_node_load_to_csv(load, csv_path)
        
        assert csv_path.exists()
        with open(csv_path, "r") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            
        # Sorted by node_id: n1, n2
        assert len(rows) == 2
        assert rows[0]["node_id"] == "n1"
        assert float(rows[0]["num_tasks"]) == 10.0
        assert rows[1]["node_id"] == "n2"
        assert float(rows[1]["avg_reward"]) == 4.0
        
        # JSON
        json_path = p / "load.json"
        export_node_load_to_json(load, json_path)
        
        assert json_path.exists()
        with open(json_path, "r") as f:
            data = json.load(f)
            
        # list of dicts, sorted by node_id
        assert len(data) == 2
        assert data[0]["node_id"] == "n1"
        assert data[0]["num_tasks"] == 10.0
