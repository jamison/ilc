from __future__ import annotations

import base64
import json
import subprocess
from pathlib import Path

from tools import agent_loop_v1
from tools.testbed import run_three_node_seven_agent_scenario as scenario_runner


def _task() -> dict[str, object]:
    return {
        "task_id": "task:test:agent-loop-v1",
        "task_class": "graph.compression",
        "region_scope": ["global"],
        "difficulty_factor": 1.25,
        "verification_method": "replayable-simulation",
        "ecu_estimate": 2.0,
        "timestamp_created": 1700000100,
        "epoch": 574,
        "channel": "ilc.agent-loop.v1",
        "claim_form": "falsifiable_positive",
        "has_falsifiable_test": True,
        "is_inadmissible_counterexample": False,
        "reproducibility_threshold": 0.85,
        "canonical_output": "diagnostics-ledger-compression-v1",
        "divergent_output_prefix": "diagnostics-ledger-divergent-v1",
    }


def _submission(slot: int, seed_hex: str, cluster_id: str, variant: str = "canonical") -> dict[str, object]:
    payload = agent_loop_v1.run_agent_once(
        slot=slot,
        seed_hex=seed_hex,
        cluster_id=cluster_id,
        node_name=f"ilc-node-{((slot - 1) % 3) + 1}",
        node_config_path="unused-when-broadcast-disabled.json",
        variant=variant,
        task=_task(),
        broadcast=False,
    )
    return payload["submission"]


def test_run_agent_once_builds_stable_submission_without_broadcast() -> None:
    payload = agent_loop_v1.run_agent_once(
        slot=1,
        seed_hex="01" * 16,
        cluster_id="cluster-a",
        node_name="ilc-node-1",
        node_config_path="unused-when-broadcast-disabled.json",
        variant="canonical",
        task=_task(),
        broadcast=False,
    )

    submission = payload["submission"]
    assert payload["marker"] == "agent_loop_submission_ok"
    assert submission["profile"]["agent_id"].startswith("agent-")
    assert submission["send_statuses"] == []
    assert submission["ep_task"]["output_hash"] == submission["output_hash"]


def test_panel_pass_and_ecu_claim_flow_are_deterministic() -> None:
    submissions = [
        _submission(1, "01" * 16, "cluster-a"),
        _submission(2, "02" * 16, "cluster-b"),
        _submission(3, "03" * 16, "cluster-c"),
        _submission(4, "04" * 16, "cluster-a"),
        _submission(5, "05" * 16, "cluster-b"),
        _submission(6, "06" * 16, "cluster-c"),
        _submission(7, "07" * 16, "cluster-d", variant="divergent"),
    ]
    outsider = agent_loop_v1._build_outsider_submission(_task(), "08" * 16, "cluster-e", "ilc-node-1")

    panel_payload = agent_loop_v1.evaluate_panel(task=_task(), submissions=submissions, outsider_submission=outsider)
    panel = panel_payload["panel_result"]
    claim_payload = agent_loop_v1.build_ecu_claim_batch(_task(), panel_payload)

    assert panel_payload["marker"] == "agent_loop_panel_ok"
    assert panel["passed"] is True
    assert panel["verdict_token"] == "panel_quorum_passed"
    assert panel["yes_votes"] == 7
    assert panel["distinct_clusters"] == 5
    assert panel["agreement_score"] == 0.875

    claims = claim_payload["claims"]
    assert claim_payload["marker"] == "agent_loop_claims_ok"
    assert len(claims) == 6
    direct = next(claim for claim in claims if claim["claim_kind"] == "direct")
    passive = next(claim for claim in claims if claim["claim_kind"] == "passive")
    assert direct["amount"] > passive["amount"]
    assert claim_payload["ledger"]["rewards_paid"] == claim_payload["outcome_summary"]["total_reward"]


def test_panel_fails_when_diversity_floor_is_not_met() -> None:
    submissions = [
        _submission(1, "01" * 16, "cluster-a"),
        _submission(2, "02" * 16, "cluster-a"),
        _submission(3, "03" * 16, "cluster-a"),
        _submission(4, "04" * 16, "cluster-a"),
        _submission(5, "05" * 16, "cluster-b"),
        _submission(6, "06" * 16, "cluster-b"),
        _submission(7, "07" * 16, "cluster-b"),
    ]
    outsider = agent_loop_v1._build_outsider_submission(_task(), "08" * 16, "cluster-b", "ilc-node-1")

    panel_payload = agent_loop_v1.evaluate_panel(task=_task(), submissions=submissions, outsider_submission=outsider)

    assert panel_payload["marker"] == "agent_loop_panel_failed"
    assert panel_payload["panel_result"]["passed"] is False
    assert panel_payload["panel_result"]["verdict_token"] == "panel_diversity_floor_failed"


def test_cli_run_agent_writes_submission_file(tmp_path: Path) -> None:
    task_json_b64 = base64.b64encode(json.dumps(_task()).encode("utf-8")).decode("ascii")
    result = subprocess.run(
        [
            "python3",
            "tools/agent_loop_v1.py",
            "run-agent",
            "--slot",
            "1",
            "--seed-hex",
            "01" * 16,
            "--cluster-id",
            "cluster-a",
            "--node-name",
            "ilc-node-1",
            "--node-config",
            "unused-when-broadcast-disabled.json",
            "--variant",
            "canonical",
            "--emit-dir",
            str(tmp_path),
            "--no-broadcast",
            "--task-json-base64",
            task_json_b64,
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout.strip())
    assert payload["marker"] == "agent_loop_submission_ok"
    assert (tmp_path / "submission_1.json").exists()


def test_cli_replay_panel_verifies_saved_artifacts(tmp_path: Path) -> None:
    task = _task()
    submissions_dir = tmp_path / "submissions"
    submissions_dir.mkdir()
    submissions = [
        _submission(1, "01" * 16, "cluster-a"),
        _submission(2, "02" * 16, "cluster-b"),
        _submission(3, "03" * 16, "cluster-c"),
        _submission(4, "04" * 16, "cluster-a"),
        _submission(5, "05" * 16, "cluster-b"),
        _submission(6, "06" * 16, "cluster-c"),
        _submission(7, "07" * 16, "cluster-d", variant="divergent"),
    ]
    for index, submission in enumerate(submissions, start=1):
        (submissions_dir / f"submission_{index}.json").write_text(
            json.dumps({"submission": submission}, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

    outsider = agent_loop_v1._build_outsider_submission(task, "08" * 16, "cluster-e", "ilc-node-1")
    panel_payload = agent_loop_v1.evaluate_panel(task=task, submissions=submissions, outsider_submission=outsider)
    claim_payload = agent_loop_v1.build_ecu_claim_batch(task, panel_payload)
    panel_path = tmp_path / "panel_result.json"
    claims_path = tmp_path / "ecu_claims.json"
    panel_path.write_text(json.dumps(panel_payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    claims_path.write_text(json.dumps(claim_payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    task_json_b64 = base64.b64encode(json.dumps(task).encode("utf-8")).decode("ascii")
    result = subprocess.run(
        [
            "python3",
            "tools/agent_loop_v1.py",
            "replay-panel",
            "--submission-dir",
            str(submissions_dir),
            "--panel-result-file",
            str(panel_path),
            "--ecu-claims-file",
            str(claims_path),
            "--outsider-seed-hex",
            "08" * 16,
            "--outsider-cluster-id",
            "cluster-e",
            "--outsider-node-name",
            "ilc-node-1",
            "--emit-dir",
            str(tmp_path),
            "--task-json-base64",
            task_json_b64,
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout.strip())
    assert payload["marker"] == "agent_loop_replay_ok"
    assert payload["panel_result_matches"] is True
    assert payload["ecu_claims_match"] is True
    assert (tmp_path / "panel_replay.json").exists()


def test_default_scenario_spec_has_seven_agents_and_outsider() -> None:
    payload = scenario_runner._load_scenario(scenario_runner.DEFAULT_SCENARIO_SPEC)
    assert len(payload["agents"]) == 7
    assert payload["outsider"]["cluster_id"] == "cluster-e"
