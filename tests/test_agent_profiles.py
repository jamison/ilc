import csv
import pytest
from pathlib import Path

from ilc_core.analysis.agent_profiles import AgentProfile, build_agent_profiles

def test_agent_profile_as_dict_namespaces_keys():
    p = AgentProfile(
        agent_id="agent:a",
        econ={"tasks": 2.0, "reward": 1.5},
        claims={"num_claims": 3.0, "total_net_stake": 10.0},
    )
    d = p.as_dict()
    assert d["agent_id"] == "agent:a"
    assert d["econ_tasks"] == 2.0
    assert d["econ_reward"] == 1.5
    assert d["claim_num_claims"] == 3.0
    assert d["claim_total_net_stake"] == 10.0

def test_build_agent_profiles_merges_econ_and_claims(tmp_path):
    tasks_csv = tmp_path / "tasks.csv"
    epochs_csv = tmp_path / "epochs.csv"
    claims_csv = tmp_path / "claims.csv"

    # Minimal tasks CSV
    with tasks_csv.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "task_id", "task_type", "domain", "agent_id",
            "epoch", "stake_spent", "reward_paid", "ecu_spent",
        ])
        writer.writeheader()
        writer.writerow({
            "task_id": "t1",
            "task_type": "demo",
            "domain": "MEDIUM",
            "agent_id": "agent:a",
            "epoch": "1",
            "stake_spent": "1.0",
            "reward_paid": "0.5",
            "ecu_spent": "1.0",
        })

    # Minimal epochs CSV
    with epochs_csv.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "epoch",
            "total_tasks",
            "total_ecu_spent",
            "total_reward_paid",
            "clearing_price_ilc_per_ecu",
        ])
        writer.writeheader()
        writer.writerow({
            "epoch": "1",
            "total_tasks": "1",
            "total_ecu_spent": "1.0",
            "total_reward_paid": "0.5",
            "clearing_price_ilc_per_ecu": "0.5",
        })

    # Minimal claims CSV
    with claims_csv.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "id", "type", "agent_id", "content",
            "net_stake", "timestamp", "parent_ids", "target_id",
        ])
        writer.writeheader()
        writer.writerow({
            "id": "c1",
            "type": "claim",
            "agent_id": "agent:a",
            "content": "foo",
            "net_stake": "5.0",
            "timestamp": "t",
            "parent_ids": "",
            "target_id": "",
        })

    profiles = build_agent_profiles(tasks_csv, epochs_csv, claims_csv)

    assert "agent:a" in profiles
    profile = profiles["agent:a"]
    d = profile.as_dict()
    # Econ portion should include something; exact keys depend on compute_basic_kpis
    # We just verify that econ_ and claim_ keys exist.
    econ_keys = [k for k in d.keys() if k.startswith("econ_")]
    claim_keys = [k for k in d.keys() if k.startswith("claim_")]
    assert econ_keys, "expected some econ_* keys"
    assert claim_keys, "expected some claim_* keys"
