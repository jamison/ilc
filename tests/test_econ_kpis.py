import csv
import pytest
from ilc_core.analysis.econ_kpis import (
    load_tasks_csv,
    load_epochs_csv,
    compute_basic_kpis,
)
from ilc_core.protocol.event_export import (
    TASK_OUTCOME_HEADERS,
    EPOCH_SUMMARY_HEADERS,
)

def test_compute_basic_kpis_synthetic(tmp_path):
    """Test KPI computation with synthetic CSV data."""
    tasks_csv = tmp_path / "tasks.csv"
    epochs_csv = tmp_path / "epochs.csv"

    # Create tasks.csv
    with tasks_csv.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=TASK_OUTCOME_HEADERS)
        writer.writeheader()
        writer.writerows([
            {
                "task_id": "t1",
                "task_type": "claim.submit",
                "domain": "EASY",
                "agent_id": "agent:a",
                "epoch": "1",
                "stake_spent": "0.1",
                "reward_paid": "0.2",
                "success": "True",
            },
            {
                "task_id": "t2",
                "task_type": "claim.submit",
                "domain": "MEDIUM",
                "agent_id": "agent:b",
                "epoch": "1",
                "stake_spent": "0.2",
                "reward_paid": "0.6",
                "success": "True",
            },
            {
                "task_id": "t3",
                "task_type": "refute.attempt",
                "domain": "MEDIUM",
                "agent_id": "agent:c",
                "epoch": "2",
                "stake_spent": "0.3",
                "reward_paid": "0.3",
                "success": "False",
            },
        ])

    # Create epochs.csv
    with epochs_csv.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=EPOCH_SUMMARY_HEADERS)
        writer.writeheader()
        writer.writerows([
            {
                "epoch": "1",
                "total_tasks": "2",
                "total_ecu_spent": "0.3",
                "total_reward_paid": "0.8",
                "clearing_price_ilc_per_ecu": "2.6667",
            },
            {
                "epoch": "2",
                "total_tasks": "1",
                "total_ecu_spent": "0.3",
                "total_reward_paid": "0.3",
                "clearing_price_ilc_per_ecu": "1.0",
            },
        ])

    task_rows = load_tasks_csv(tasks_csv)
    epoch_rows = load_epochs_csv(epochs_csv)
    kpis = compute_basic_kpis(task_rows, epoch_rows)

    # Assertions
    assert kpis["total_tasks"] == 3
    assert kpis["total_reward_ilc"] == pytest.approx(1.1)
    assert kpis["total_ecu_spent"] == pytest.approx(0.6)
    assert kpis["realized_price_ilc_per_ecu"] == pytest.approx(1.1 / 0.6)
    
    assert kpis["tasks_by_domain"] == {"EASY": 1, "MEDIUM": 2}
    assert kpis["avg_reward_by_domain"]["EASY"] == pytest.approx(0.2)
    assert kpis["avg_reward_by_domain"]["MEDIUM"] == pytest.approx((0.6 + 0.3) / 2)

    assert kpis["epochs_count"] == 2
    assert kpis["max_epoch"] == 2
    assert kpis["total_tasks_from_epochs"] == 3
    assert kpis["avg_tasks_per_epoch"] == 1.5

def test_compute_basic_kpis_empty():
    """Test KPI computation with empty inputs."""
    kpis = compute_basic_kpis([], [])
    
    assert kpis["total_tasks"] == 0
    assert kpis["total_reward_ilc"] == 0.0
    assert kpis["total_ecu_spent"] == 0.0
    assert kpis["avg_reward_per_task"] == 0.0
    assert kpis["realized_price_ilc_per_ecu"] == 0.0
    
    assert kpis["epochs_count"] == 0
    assert kpis["max_epoch"] is None
    assert kpis["avg_clearing_price_ilc_per_ecu"] == 0.0

def test_compute_basic_kpis_robustness(tmp_path):
    """Test robustness to missing or malformed numeric fields."""
    tasks_csv = tmp_path / "bad_tasks.csv"
    
    with tasks_csv.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=TASK_OUTCOME_HEADERS)
        writer.writeheader()
        writer.writerows([
            {
                "task_id": "t1",
                "stake_spent": "not-a-number",  # Should default to 0.0
                "reward_paid": "",              # Should default to 0.0
                "domain": "HARD",
            }
        ])
        
    task_rows = load_tasks_csv(tasks_csv)
    kpis = compute_basic_kpis(task_rows, [])
    
    assert kpis["total_tasks"] == 1
    assert kpis["total_reward_ilc"] == 0.0
    assert kpis["total_ecu_spent"] == 0.0
    assert kpis["tasks_by_domain"] == {"HARD": 1}
