import pytest
import tempfile
import csv
from pathlib import Path
from dataclasses import asdict

from ilc_core.network.topology import build_star_topology
from ilc_core.sim.devnet_multi_epoch import DevnetMultiEpochResult, DevnetEpochResult
from ilc_core.sim.devnet_experiments import (
    DevnetExperimentSummary,
    summarize_multi_epoch_run,
    export_experiment_summaries_to_csv
)

def test_summarize_multi_epoch_run_basic():
    # Construct a fake multi-epoch result
    # We don't need real topology/snapshots, just the aggregate_node_load and list of results
    
    # 2 epochs (just list length matters for avg)
    epoch_results = [
        DevnetEpochResult(1, "ns", [], {}),
        DevnetEpochResult(2, "ns", [], {})
    ]
    
    # Fake aggregate load
    # Node 1: 10 tasks, 100 reward
    # Node 2: 5 tasks, 20 reward
    agg_load = {
        "n1": {"num_tasks": 10.0, "total_reward": 100.0, "avg_reward": 10.0},
        "n2": {"num_tasks": 5.0,  "total_reward": 20.0,  "avg_reward": 4.0}
    }
    
    multi = DevnetMultiEpochResult(
        namespace_id="ns_test",
        topology=None, # type: ignore
        epoch_results=epoch_results, 
        aggregate_node_load=agg_load
    )
    
    summary = summarize_multi_epoch_run("exp_1", multi)
    
    assert summary.label == "exp_1"
    assert summary.namespace_id == "ns_test"
    assert summary.num_epochs == 2
    
    # Totals
    assert summary.total_tasks == 15.0  # 10 + 5
    assert summary.total_reward == 120.0 # 100 + 20
    
    # Averages
    # Tasks per epoch = 15 / 2 = 7.5
    assert summary.avg_tasks_per_epoch == 7.5
    # Reward per task = 120 / 15 = 8.0
    assert summary.avg_reward_per_task == 8.0
    
    # Max node tasks
    assert summary.max_node_tasks == 10.0

def test_summarize_empty_multi_epoch():
    multi = DevnetMultiEpochResult(
        namespace_id="",
        topology=None, # type: ignore
        epoch_results=[],
        aggregate_node_load={}
    )
    
    summary = summarize_multi_epoch_run("empty", multi)
    
    assert summary.num_epochs == 0
    assert summary.total_tasks == 0.0
    assert summary.avg_tasks_per_epoch == 0.0
    assert summary.avg_reward_per_task == 0.0
    assert summary.max_node_tasks == 0.0

def test_export_experiment_summaries_to_csv_roundtrip():
    s1 = DevnetExperimentSummary(
        label="test1", namespace_id="ns1", num_epochs=1, 
        total_tasks=10.0, total_reward=100.0, 
        avg_tasks_per_epoch=10.0, avg_reward_per_task=10.0, max_node_tasks=10.0
    )
    s2 = DevnetExperimentSummary(
        label="test2", namespace_id="ns1", num_epochs=2, 
        total_tasks=20.0, total_reward=100.0, 
        avg_tasks_per_epoch=10.0, avg_reward_per_task=5.0, max_node_tasks=10.0
    )
    
    with tempfile.TemporaryDirectory() as tmp_dir:
        p = Path(tmp_dir) / "test.csv"
        export_experiment_summaries_to_csv([s1, s2], p)
        
        # Read back
        with open(p, "r") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            
        assert len(rows) == 2
        assert rows[0]["label"] == "test1"
        assert float(rows[0]["total_tasks"]) == 10.0
        assert rows[1]["label"] == "test2"
        assert float(rows[1]["avg_reward_per_task"]) == 5.0
