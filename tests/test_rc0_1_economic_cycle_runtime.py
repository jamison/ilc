from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from ilc_core.rc.economic_cycle_runtime import EconomicCycleRuntimeError, materialize_economic_cycle
from tools import check_rc0_1_economic_state
from tools import prove_rc0_1_economic_state
from tools import query_rc0_1_economic_state


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
                "difficulty_factor": "1.0",
            },
            "ep_task": {
                "agent_id": agent_id,
                "task_id": f"task:test:economic-cycle::{agent_id[:12]}",
                "task_class": "graph.compression",
                "task_state": "completed",
                "difficulty_factor": "1.0",
                "ecu.estimate": "2.0",
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
                "max_cluster_share": "0.25",
                "agreement_score": "0.75",
                "reproducibility_threshold": "0.7",
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
                    "amount": "3.0",
                    "basis": {"base_reward": "3.0", "confidence_score": "0.75"},
                },
                {
                    "claim_id": "claim::passive",
                    "task_id": "task:test:economic-cycle",
                    "epoch": 12,
                    "agent_id": "agent-beta",
                    "claim_kind": "passive",
                    "amount": "1.0",
                    "basis": {"base_reward": "3.0", "quality_score": "0.75"},
                },
            ],
            "ledger": {
                "ecu_spent": "2.0",
                "clearing_price": "2.0",
                "rewards_paid": "4.0",
                "tasks": 1,
            },
            "outcome_summary": {
                "count": 1,
                "total_reward": "4.0",
                "total_stake": "2.0",
            },
        },
    )
    return scenario_root


def test_materialize_economic_cycle_persists_graph_ledger_and_wallet_state(tmp_path: Path) -> None:
    scenario_root = _scenario_fixture(tmp_path)
    output_root = tmp_path / "economic"

    manifest = materialize_economic_cycle(scenario_root=scenario_root, output_root=output_root)

    assert manifest["summary"]["reward_total"] == "4"
    assert manifest["summary"]["distribution_check_ok"] is True
    assert manifest["runtime_store"]["store_kind"] == "lmdb_public_runtime_v0.1"
    assert Path(manifest["runtime_store"]["graph_store_root"]).is_dir()
    assert Path(manifest["runtime_store"]["ledger_store_root"]).is_dir()
    assert Path(manifest["runtime_store"]["wallet_store_root"]).is_dir()

    nodes = json.loads((output_root / "graph" / "nodes.json").read_text(encoding="utf-8"))
    links = json.loads((output_root / "graph" / "links.json").read_text(encoding="utf-8"))
    wallets = json.loads((output_root / "economy" / "wallets.json").read_text(encoding="utf-8"))
    ledger = json.loads((output_root / "economy" / "ledger_state.json").read_text(encoding="utf-8"))

    assert len(nodes) == 3
    assert len(links) == 1
    assert links[0]["link_type"] == "supports"

    assert ledger["balances"]["agent-alpha"] == "3"
    assert ledger["balances"]["agent-beta"] == "1"

    wallet_rows = wallets["wallets"]
    assert set(wallet_rows) == {"agent-alpha", "agent-beta", "agent-gamma", "agent-outsider"}
    assert wallet_rows["agent-alpha"]["reward_status"] == "rewarded"
    assert wallet_rows["agent-alpha"]["last_settled_epoch_id"] == "rc0_1::task:test:economic-cycle::epoch::12"
    assert wallet_rows["agent-alpha"]["lifetime_claim_count"] == 1
    assert wallet_rows["agent-alpha"]["settled_epoch_count"] == 1
    assert wallet_rows["agent-gamma"]["balance_ilc"] == "0"
    assert wallet_rows["agent-outsider"]["variant"] == "outsider"
    assert manifest["settlement_manifest"]["settlement_status"] == "applied"
    assert manifest["runtime_identity"]["claims_sha256"] == manifest["settlement_manifest"]["claim_batch_sha256"]


def test_materialize_economic_cycle_ignores_submission_artifact_decoys(tmp_path: Path) -> None:
    scenario_root = _scenario_fixture(tmp_path)
    _write_json(
        scenario_root / "submissions" / "submission_artifact_1.json",
        {
            "artifact_kind": "agent_submission",
            "submission": "not-a-wrapper-submission",
        },
    )

    manifest = materialize_economic_cycle(scenario_root=scenario_root, output_root=tmp_path / "economic")

    assert manifest["summary"]["node_count"] == 3
    assert manifest["summary"]["wallet_count"] == 4


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
    assert wallet_payload["data"]["wallet"]["balance_ilc"] == "0"
    assert wallet_payload["data"]["wallet"]["reward_status"] == "not_rewarded"

    history_result = subprocess.run(
        [
            sys.executable,
            "tools/query_rc0_1_economic_state.py",
            "--manifest",
            str(manifest_path),
            "wallet-history",
            "--agent-id",
            "agent-alpha",
        ],
        cwd=str(Path(__file__).resolve().parents[1]),
        capture_output=True,
        text=True,
        check=False,
    )
    assert history_result.returncode == 0, history_result.stderr
    history_payload = json.loads(history_result.stdout.strip())
    assert len(history_payload["data"]["claim_history"]) == 1
    assert history_payload["data"]["epoch_history"][0]["epoch_id"] == "rc0_1::task:test:economic-cycle::epoch::12"
    assert history_payload["data"]["balance_history"][0]["reward_delta_ilc"] == "3"
    assert history_payload["data"]["latest_epoch_id"] == "rc0_1::task:test:economic-cycle::epoch::12"

    wallet_status_result = subprocess.run(
        [
            sys.executable,
            "tools/query_rc0_1_economic_state.py",
            "--manifest",
            str(manifest_path),
            "wallet-status",
            "--agent-id",
            "agent-alpha",
        ],
        cwd=str(Path(__file__).resolve().parents[1]),
        capture_output=True,
        text=True,
        check=False,
    )
    assert wallet_status_result.returncode == 0, wallet_status_result.stderr
    wallet_status_payload = json.loads(wallet_status_result.stdout.strip())
    assert wallet_status_payload["data"]["claim_count"] == 1
    assert wallet_status_payload["data"]["settled_epoch_count"] == 1
    assert wallet_status_payload["data"]["latest_balance_receipt"]["reward_delta_ilc"] == "3"

    store_summary_result = subprocess.run(
        [
            sys.executable,
            "tools/query_rc0_1_economic_state.py",
            "--manifest",
            str(manifest_path),
            "store-summary",
        ],
        cwd=str(Path(__file__).resolve().parents[1]),
        capture_output=True,
        text=True,
        check=False,
    )
    assert store_summary_result.returncode == 0, store_summary_result.stderr
    store_summary_payload = json.loads(store_summary_result.stdout.strip())
    assert store_summary_payload["data"]["runtime_store"]["store_kind"] == "lmdb_public_runtime_v0.1"


def test_check_economic_state_accepts_persisted_runtime_store(tmp_path: Path) -> None:
    scenario_root = _scenario_fixture(tmp_path)
    output_root = tmp_path / "economic"
    materialize_economic_cycle(scenario_root=scenario_root, output_root=output_root)

    verdict, failures, summary = check_rc0_1_economic_state.check_economic_state(output_root / "manifest.json")

    assert verdict == "pass"
    assert failures == []
    assert summary["wallet_balance_total"] == "4"
    assert summary["runtime_store"]["store_kind"] == "lmdb_public_runtime_v0.1"


def test_check_economic_state_rejects_reward_total_mismatch(tmp_path: Path) -> None:
    scenario_root = _scenario_fixture(tmp_path)
    output_root = tmp_path / "economic"
    materialize_economic_cycle(scenario_root=scenario_root, output_root=output_root)
    manifest_path = output_root / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["summary"]["reward_total"] = "9.0"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    verdict, failures, _summary = check_rc0_1_economic_state.check_economic_state(manifest_path)

    assert verdict == "fail"
    assert "economic_reward_total_mismatch:wallets" in failures
    assert "economic_reward_total_mismatch:ledger" in failures


def test_prove_economic_state_replays_durable_runtime_state(tmp_path: Path) -> None:
    scenario_root = _scenario_fixture(tmp_path)
    output_root = tmp_path / "economic"
    materialize_economic_cycle(scenario_root=scenario_root, output_root=output_root)

    proof_manifest = prove_rc0_1_economic_state.prove_economic_state(
        manifest_path=output_root / "manifest.json",
        output_root=tmp_path / "proof",
    )

    assert all(proof_manifest["comparison"].values())
    assert proof_manifest["runtime_store"]["store_kind"] == "lmdb_public_runtime_v0.1"
    assert proof_manifest["proof_manifest_path"].endswith("proof/manifest.json")
    assert proof_manifest["query_payloads"]["quorum_record"]["data"]["quorum_record"]["task_id"] == "task:test:economic-cycle"


def test_materialize_economic_cycle_marks_idempotent_replay_on_same_output_root(tmp_path: Path) -> None:
    scenario_root = _scenario_fixture(tmp_path)
    output_root = tmp_path / "economic"

    first_manifest = materialize_economic_cycle(scenario_root=scenario_root, output_root=output_root)
    second_manifest = materialize_economic_cycle(scenario_root=scenario_root, output_root=output_root)

    assert first_manifest["settlement_manifest"]["settlement_status"] == "applied"
    assert second_manifest["settlement_manifest"]["settlement_status"] == "idempotent_replay"
    wallet_row, history = query_rc0_1_economic_state.load_wallet_history(output_root / "manifest.json", "agent-alpha")
    assert wallet_row["settled_epoch_count"] == 1
    assert len(history["claim_history"]) == 1
    assert len(history["balance_history"]) == 1


def test_materialize_economic_cycle_rejects_conflicting_reuse_of_output_root(tmp_path: Path) -> None:
    scenario_root = _scenario_fixture(tmp_path)
    output_root = tmp_path / "economic"
    materialize_economic_cycle(scenario_root=scenario_root, output_root=output_root)

    claims_path = scenario_root / "panel" / "ecu_claims.json"
    claims_payload = json.loads(claims_path.read_text(encoding="utf-8"))
    claims_payload["claims"][0]["amount"] = "2.5"
    claims_payload["ledger"]["rewards_paid"] = "3.5"
    claims_payload["outcome_summary"]["total_reward"] = "3.5"
    claims_path.write_text(json.dumps(claims_payload, indent=2) + "\n", encoding="utf-8")

    with pytest.raises(EconomicCycleRuntimeError, match="economic_runtime_root_conflict"):
        materialize_economic_cycle(scenario_root=scenario_root, output_root=output_root)


def test_query_helpers_return_quorum_and_wallet_export(tmp_path: Path) -> None:
    scenario_root = _scenario_fixture(tmp_path)
    output_root = tmp_path / "economic"
    materialize_economic_cycle(scenario_root=scenario_root, output_root=output_root)
    manifest_path = output_root / "manifest.json"

    quorum_payload = query_rc0_1_economic_state.query_quorum_record(manifest_path)
    wallet_export_payload = query_rc0_1_economic_state.query_wallet_export(manifest_path)
    graph_summary_payload = query_rc0_1_economic_state.query_graph_summary(manifest_path)
    graph_links_payload = query_rc0_1_economic_state.query_graph_links(manifest_path, agent_id="agent-beta")
    ledger_summary_payload = query_rc0_1_economic_state.query_ledger_summary(manifest_path)

    assert quorum_payload["data"]["quorum_record"]["task_id"] == "task:test:economic-cycle"
    assert wallet_export_payload["data"]["balances"]["agent-alpha"] == "3"
    assert graph_summary_payload["data"]["node_count"] == 3
    assert graph_links_payload["data"]["link_count"] == 1
    assert ledger_summary_payload["data"]["reward_total"] == "4"


def test_economic_negative_path_drills_emit_expected_tokens(tmp_path: Path) -> None:
    scenario_root = _scenario_fixture(tmp_path)
    output_root = tmp_path / "economic"
    materialize_economic_cycle(scenario_root=scenario_root, output_root=output_root)

    result = subprocess.run(
        [
            sys.executable,
            "tools/testbed/run_economic_negative_path_drills.py",
            "--manifest",
            str(output_root / "manifest.json"),
        ],
        cwd=str(Path(__file__).resolve().parents[1]),
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert "economic_negative_path_missing_store_ok" in result.stdout
    assert "economic_negative_path_reward_mismatch_ok" in result.stdout
    assert "economic_negative_path_wallet_count_ok" in result.stdout
    assert "economic_negative_path_runtime_identity_ok" in result.stdout
    assert "economic_negative_path_wallet_history_ok" in result.stdout
    assert "economic_negative_path_quorum_record_ok" in result.stdout
    assert "economic_negative_path_drill_ok" in result.stdout


def test_economic_replay_drills_emit_expected_tokens(tmp_path: Path) -> None:
    scenario_root = _scenario_fixture(tmp_path)
    result = subprocess.run(
        [
            sys.executable,
            "tools/testbed/run_economic_replay_drills.py",
            "--scenario-root",
            str(scenario_root),
            "--output-root",
            str(tmp_path / "economic-replay"),
        ],
        cwd=str(Path(__file__).resolve().parents[1]),
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert "economic_replay_idempotent_ok" in result.stdout
    assert "economic_replay_conflict_ok" in result.stdout
    assert "economic_replay_drill_ok" in result.stdout


def test_run_economic_proof_emits_combined_manifest(tmp_path: Path) -> None:
    scenario_root = _scenario_fixture(tmp_path)
    output_root = tmp_path / "economic"
    materialize_economic_cycle(scenario_root=scenario_root, output_root=output_root)

    result = subprocess.run(
        [
            sys.executable,
            "tools/run_rc0_1_economic_proof.py",
            "--manifest",
            str(output_root / "manifest.json"),
            "--output-root",
            str(tmp_path / "proof-runner"),
        ],
        cwd=str(Path(__file__).resolve().parents[1]),
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout.strip())
    manifest = payload["manifest"]
    assert manifest["negative_path_verdict"] == "pass"
    assert manifest["replay_verdict"] == "pass"
    assert manifest["replay_settlement_status"] == "idempotent_replay"
    assert manifest["query_payloads"]["ledger_summary"]["data"]["reward_total"] == "4"
    assert manifest["query_payloads"]["graph_summary"]["data"]["node_count"] == 3
