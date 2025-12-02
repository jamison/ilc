import csv
import pytest
from pathlib import Path

from ilc_core.analysis.agent_profiles import (
    AgentProfile,
    build_agent_profiles,
    compute_agent_influence_kpis,
    attach_influence_to_profiles,
)
from ilc_core.analysis.claim_scores import ClaimInfluenceRow

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

def test_compute_agent_influence_kpis_basic(tmp_path):
    # Prepare a small claims.csv mapping c1 -> agent:a, c2 -> agent:b
    claims_csv = tmp_path / "claims.csv"
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
            "net_stake": "1.0",
            "timestamp": "t",
            "parent_ids": "",
            "target_id": "",
        })
        writer.writerow({
            "id": "c2",
            "type": "claim",
            "agent_id": "agent:b",
            "content": "bar",
            "net_stake": "1.0",
            "timestamp": "t",
            "parent_ids": "",
            "target_id": "",
        })

    rows = [
        ClaimInfluenceRow(
            claim_id="c1",
            supports_in=1,
            refutes_in=0,
            equivalent_in=0,
            depends_on_in=0,
            net_support=1,
            influence_score=1.0,
        ),
        ClaimInfluenceRow(
            claim_id="c2",
            supports_in=0,
            refutes_in=1,
            equivalent_in=0,
            depends_on_in=0,
            net_support=-1,
            influence_score=-1.0,
        ),
    ]

    kpis = compute_agent_influence_kpis(rows, claims_csv)
    assert kpis["agent:a"]["total_influence"] == 1.0
    assert kpis["agent:a"]["num_influenced_claims"] == 1.0
    assert kpis["agent:a"]["avg_influence"] == 1.0

    assert kpis["agent:b"]["total_influence"] == -1.0
    assert kpis["agent:b"]["num_influenced_claims"] == 1.0
    assert kpis["agent:b"]["avg_influence"] == -1.0

def test_attach_influence_to_profiles_in_place(tmp_path):
    # Reuse claims.csv from previous test or build a quick one again
    claims_csv = tmp_path / "claims.csv"
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
            "net_stake": "1.0",
            "timestamp": "t",
            "parent_ids": "",
            "target_id": "",
        })

    rows = [
        ClaimInfluenceRow(
            claim_id="c1",
            supports_in=1,
            refutes_in=0,
            equivalent_in=0,
            depends_on_in=0,
            net_support=1,
            influence_score=1.0,
        )
    ]

    profiles = {
        "agent:a": AgentProfile(agent_id="agent:a"),
    }

    attach_influence_to_profiles(profiles, rows, claims_csv)

    assert "agent:a" in profiles
    p = profiles["agent:a"]
    assert "total_influence" in p.influence
    assert p.influence["total_influence"] == 1.0
