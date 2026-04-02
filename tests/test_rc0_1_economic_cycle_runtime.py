from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from ilc_core.rc.economic_cycle_runtime import materialize_economic_cycle


def _write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _submission(
    *,
    agent_id: str,
    cluster_id: str,
    node_name: str,
    slot: int,
    variant: str,
    output_hash: str,
) -> dict[str, object]:
    return {
        "marker": "agent_loop_submission_ok",
        "runtime_version": "agent_loop_v1_runtime_575.v0.1",
        "submission": {
            "task_id": "task:test:economic-cycle",
            "epoch": 12,
            "channel": "cid:test",
            "profile": {
                "agent_id": agent_id,
                "cluster_id": cluster_id,
                "node_name": node_name,
                "seed_hex": f"{slot:02d}" * 16,
                "slot": slot,
                "variant": variant,
            },
            "output_hash": output_hash,
            "output_payload": {
                "task_id": "task:test:economic-cycle",
                "task_class": "graph.compression",
                "solution": "stable-output" if variant != "divergent" else "divergent-output",
                "claim_form": "falsifiable_positive",
                "verification_method": "replayable-simulation",
                "difficulty_factor": 1.0,
            },
            "ep_task": {
                "agent_id": agent_id,
                "task_id": f"task:test:economic-cycle::{agent_id[:12]}",
                "task_class": "graph.compression",
                "task_state": "completed",
                "difficulty_factor": 1.0,
                "ecu.estimate": 2.0,
                "verification_method": "replayable-simulation",
                "output_hash": output_hash,
                "timestamp_created": 1_700_000_100,
                "input_data": {
                    "cluster_id": cluster_id,
                    "node_name": node_name,
                    "variant": variant,
                    "source_task_id": "task:test:economic-cycle",
                },
                "region_scope": ["global"],
                "staking_beneficiary": None,
                "bounty_id": None,
            },
            "gossip_type": "agent_submission",
            "send_statuses": [],
        },
    }


def _scenario_fixture(root: Path) -> Path:
    scenario_root = root / "scenario"
    _write_json(
        scenario_root / "scenario_manifest.json",
        {
            "task_id": "task:test:economic-cycle",
            "epoch": 12,
            "generated_at": "2026-04-02T12:00:00Z",
            "direct_author_agent_id": "agent-alpha",
        },
    )
    _write_json(scenario_root / "submissions" / "submission_1.json", _submission(agent_id="agent-alpha", cluster_id="cluster-a", node_name="ilc-node-1", slot=1, variant="canonical", output_hash="hash-majority"))
    _write_json(scenario_root / "submissions" / "submission_2.json", _submission(agent_id="agent-beta", cluster_id="cluster-b", node_name="ilc-node-2", slot=2, variant="canonical", output_hash="hash-majority"))
    _write_json(scenario_root / "submissions" / "submission_3.json", _submission(agent_id="agent-gamma", cluster_id="cluster-c", node_name="ilc-node-3", slot=3, variant="divergent", output_hash="hash-divergent"))

    outsider_submission = _submission(
        agent_id="agent-outsider",
        cluster_id="cluster-d",
        node_name="ilc-node-1",
        slot=8,
        variant="outsider",
        output_hash="hash-majority",
    )["submission"]

    _write_json(
        scenario_root / "panel" / "panel_result.json",
        {
            "marker": "agent_loop_panel_ok",
            "runtime_version": "agent_loop_v1_runtime_575.v0.1",
            "panel_result": {
                "task_id": "task:test:economic-cycle",
                "epoch": 12,
                "yes_votes": 3,
                "no_votes": 1,
                "quorum_threshold": 3,
                "quorum_reached": True,
                "distinct_clusters": 4,
                "distinct_cluster_floor": 3,
                "diversity_floor_met": True,
                "max_cluster_share": 0.25,
                "agreement_score": 0.75,
                "reproducibility_threshold": 0.7,
                "majority_output_hash": "hash-majority",
                "direct_author_agent_id": "agent-alpha",
                "verdict_token": "panel_quorum_passed",
                "passed": True,
                "confidence_score": 0.75,
                "votes": [
                    {
                        "reviewer_agent_id": "agent-alpha",
                        "cluster_id": "cluster-a",
                        "node_name": "ilc-node-1",
                        "variant": "canonical",
                        "output_hash": "hash-majority",
                        "matches_majority": True,
                        "passed_gate": True,
                        "passed": True,
                    },
                    {
                        "reviewer_agent_id": "agent-beta",
                        "cluster_id": "cluster-b",
                        "node_name": "ilc-node-2",
                        "variant": "canonical",
                        "output_hash": "hash-majority",
                        "matches_majority": True,
                        "passed_gate": True,
                        "passed": True,
                    },
                    {
                        "reviewer_agent_id": "agent-gamma",
                        "cluster_id": "cluster-c",
                        "node_name": "ilc-node-3",
                        "variant": "divergent",
                        "output_hash": "hash-divergent",
                        "matches_majority": False,
                        "passed_gate": True,
                        "passed": False,
                    },
                    {
                        "reviewer_agent_id": "agent-outsider",
                        "cluster_id": "cluster-d",
                        "node_name": "ilc-node-1",
                        "variant": "outsider",
                        "output_hash": "hash-majority",
                        "matches_majority": True,
                        "passed_gate": True,
                        "passed": True,
                    },
                ],
            },
            "outsider_submission": outsider_submission,
        },
    )
    _write_json(
        scenario_root / "panel" / "ecu_claims.json",
        {
            "marker": "agent_loop_claims_ok",
            "runtime_version": "agent_loop_v1_runtime_575.v0.1",
            "claims": [
                {
                    "claim_id": "claim::direct",
                    "task_id": "task:test:economic-cycle",
                    "epoch": 12,
                    "agent_id": "agent-alpha",
                    "claim_kind": "direct",
                    "amount": 3.0,
                    "basis": {"base_reward": 3.0, "confidence_score": 0.75},
                },
                {
                    "claim_id": "claim::passive",
                    "task_id": "task:test:economic-cycle",
                    "epoch": 12,
                    "agent_id": "agent-beta",
                    "claim_kind": "passive",
                    "amount": 1.0,
                    "basis": {"base_reward": 3.0, "quality_score": 0.75},
                },
            ],
            "ledger": {
                "ecu_spent": 2.0,
                "clearing_price": 2.0,
                "rewards_paid": 4.0,
                "tasks": 1,
            },
            "outcome_summary": {
                "count": 1,
                "total_reward": 4.0,
                "total_stake": 2.0,
            },
        },
    )
    return scenario_root


def test_materialize_economic_cycle_persists_graph_ledger_and_wallet_state(tmp_path: Path) -> None:
    scenario_root = _scenario_fixture(tmp_path)
    output_root = tmp_path / "economic"

    manifest = materialize_economic_cycle(scenario_root=scenario_root, output_root=output_root)

    assert manifest["summary"]["reward_total"] == 4.0
    assert manifest["summary"]["distribution_check_ok"] is True

    nodes = json.loads((output_root / "graph" / "nodes.json").read_text(encoding="utf-8"))
    links = json.loads((output_root / "graph" / "links.json").read_text(encoding="utf-8"))
    wallets = json.loads((output_root / "economy" / "wallets.json").read_text(encoding="utf-8"))
    ledger = json.loads((output_root / "economy" / "ledger_state.json").read_text(encoding="utf-8"))

    assert len(nodes) == 3
    assert len(links) == 1
    assert links[0]["link_type"] == "supports"

    assert ledger["balances"]["agent-alpha"] == 3.0
    assert ledger["balances"]["agent-beta"] == 1.0

    wallet_rows = wallets["wallets"]
    assert set(wallet_rows) == {"agent-alpha", "agent-beta", "agent-gamma", "agent-outsider"}
    assert wallet_rows["agent-alpha"]["reward_status"] == "rewarded"
    assert wallet_rows["agent-gamma"]["balance_ilc"] == 0.0
    assert wallet_rows["agent-outsider"]["variant"] == "outsider"


def test_economic_cycle_tools_emit_machine_readable_outputs(tmp_path: Path) -> None:
    scenario_root = _scenario_fixture(tmp_path)
    output_root = tmp_path / "economic"

    run_result = subprocess.run(
        [
            sys.executable,
            "tools/run_rc0_1_economic_cycle.py",
            "--scenario-root",
            str(scenario_root),
            "--output-root",
            str(output_root),
        ],
        cwd=str(Path(__file__).resolve().parents[1]),
        capture_output=True,
        text=True,
        check=False,
    )
    assert run_result.returncode == 0, run_result.stderr
    run_payload = json.loads(run_result.stdout.strip())
    assert run_payload["marker"] == "rc0_1_economic_cycle_ok"

    manifest_path = output_root / "manifest.json"
    summary_result = subprocess.run(
        [
            sys.executable,
            "tools/query_rc0_1_economic_state.py",
            "--manifest",
            str(manifest_path),
            "summary",
        ],
        cwd=str(Path(__file__).resolve().parents[1]),
        capture_output=True,
        text=True,
        check=False,
    )
    assert summary_result.returncode == 0, summary_result.stderr
    summary_payload = json.loads(summary_result.stdout.strip())
    assert summary_payload["data"]["wallet_count"] == 4

    wallet_result = subprocess.run(
        [
            sys.executable,
            "tools/query_rc0_1_economic_state.py",
            "--manifest",
            str(manifest_path),
            "wallets",
            "--agent-id",
            "agent-gamma",
        ],
        cwd=str(Path(__file__).resolve().parents[1]),
        capture_output=True,
        text=True,
        check=False,
    )
    assert wallet_result.returncode == 0, wallet_result.stderr
    wallet_payload = json.loads(wallet_result.stdout.strip())
    assert wallet_payload["data"]["wallet"]["balance_ilc"] == 0.0
    assert wallet_payload["data"]["wallet"]["reward_status"] == "not_rewarded"
