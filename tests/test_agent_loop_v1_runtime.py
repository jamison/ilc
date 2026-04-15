from __future__ import annotations

import base64
import json
import subprocess
from pathlib import Path

import pytest

from ilc_core.crypto.cbor_canonical import cbor_loads
from tools import agent_loop_v1
from tools import query_rc0_1_economic_state
from tools.testbed import run_rc0_1_benchmarks as benchmark_runner
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


def test_panel_direct_author_uses_hashed_tiebreak_not_lexicographic_order() -> None:
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

    majority_agents = sorted(
        vote["reviewer_agent_id"]
        for vote in panel["votes"]
        if vote["matches_majority"] and vote["variant"] != "outsider"
    )
    expected_direct_author = min(
        majority_agents,
        key=lambda agent_id: (
            agent_loop_v1._direct_author_tiebreak_digest(_task(), panel["majority_output_hash"], agent_id),
            agent_id,
        ),
    )

    assert panel["direct_author_agent_id"] == expected_direct_author
    assert panel["direct_author_agent_id"] != majority_agents[0]


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


def test_broadcast_submission_emits_cbor_payload_and_latency_metrics(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        agent_loop_v1,
        "_transport_bundle",
        lambda _config_path: (
            agent_loop_v1.TransportRuntimeConfig(
                transport_kind="http",
                bind_host="127.0.0.1",
                bind_port=0,
                tls_cert_path="unused-cert.pem",
                tls_key_path="unused-key.pem",
            ),
            ["https://peer-a.example", "https://peer-b.example"],
        ),
    )

    calls: list[tuple[str, str, str, int, str, bytes, str]] = []

    class _FakeRuntime:
        def __init__(self, _config: object) -> None:
            pass

        def send_gossip(
            self,
            peer_endpoint: str,
            gossip_type: str,
            channel: str,
            epoch: int,
            signature: str,
            payload: bytes | str = b"",
            *,
            content_type: str = "application/cbor",
        ) -> int:
            normalized = payload if isinstance(payload, bytes) else payload.encode("utf-8")
            calls.append((peer_endpoint, gossip_type, channel, epoch, signature, normalized, content_type))
            return 202

    monkeypatch.setattr(agent_loop_v1, "HttpGossipTransportRuntime", _FakeRuntime)

    payload = agent_loop_v1.run_agent_once(
        slot=1,
        seed_hex="01" * 16,
        cluster_id="cluster-a",
        node_name="ilc-node-1",
        node_config_path="unused.json",
        variant="canonical",
        task=_task(),
        broadcast=True,
    )

    statuses = payload["submission"]["send_statuses"]
    assert len(statuses) == 2
    assert all(status["status_code"] == 202 for status in statuses)
    assert all(status["payload_bytes"] > 0 for status in statuses)
    assert all(isinstance(status["payload_sha256"], str) and status["payload_sha256"] for status in statuses)
    assert all(status["duration_ms"] >= 0.0 for status in statuses)

    assert len(calls) == 2
    assert all(call[6] == "application/cbor" for call in calls)
    decoded = cbor_loads(calls[0][5])
    assert decoded["artifact_kind"] == "agent_submission"
    assert decoded["task_id"] == _task()["task_id"]


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


def test_local_python_prefers_repo_venv(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    repo_root = tmp_path / "repo"
    venv_python = repo_root / ".venv" / "bin" / "python"
    venv_python.parent.mkdir(parents=True)
    venv_python.write_text("#!/bin/sh\n", encoding="utf-8")
    monkeypatch.setattr(scenario_runner, "REPO_ROOT", repo_root)

    assert scenario_runner._local_python() == str(venv_python)


def test_run_scenario_emits_live_economic_state(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    hosts_path = tmp_path / "hosts.json"
    hosts_path.write_text(
        json.dumps(
            {
                "version": "testbed_hosts_v0.1",
                "control_machine": {
                    "name": "ilc-node-1",
                    "tailscale_name": "imac",
                    "tailscale_ip": "100.96.35.87",
                    "repo_path": "/tmp/repo",
                    "role": "control_and_node",
                },
                "remote_hosts": [
                    {
                        "name": "ilc-node-2",
                        "ssh_host": "ilc-node-2",
                        "ssh_user": "ilcops",
                        "repo_path": "/opt/ilc/current",
                        "venv_path": "/opt/ilc/venv",
                        "config_path": "/etc/ilc",
                    },
                    {
                        "name": "ilc-node-3",
                        "ssh_host": "ilc-node-3",
                        "ssh_user": "ilcops",
                        "repo_path": "/opt/ilc/current",
                        "venv_path": "/opt/ilc/venv",
                        "config_path": "/etc/ilc",
                    },
                ],
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    scenario = scenario_runner._load_scenario(scenario_runner.DEFAULT_SCENARIO_SPEC)
    task_payload = {key: value for key, value in scenario.items() if key not in {"agents", "outsider", "scenario_id"}}
    payloads_by_slot = {
        agent["slot"]: {
            **agent_loop_v1.run_agent_once(
                slot=int(agent["slot"]),
                seed_hex=str(agent["seed_hex"]),
                cluster_id=str(agent["cluster_id"]),
                node_name=str(agent["node_name"]),
                node_config_path="unused-when-broadcast-disabled.json",
                variant=str(agent["variant"]),
                task=task_payload,
                broadcast=False,
            ),
        }
        for agent in scenario["agents"]
    }
    panel_submissions = [payloads_by_slot[agent["slot"]]["submission"] for agent in scenario["agents"]]
    outsider_submission = agent_loop_v1._build_outsider_submission(
        task_payload,
        str(scenario["outsider"]["seed_hex"]),
        str(scenario["outsider"]["cluster_id"]),
        str(scenario["outsider"]["node_name"]),
    )
    panel_eval = agent_loop_v1.evaluate_panel(
        task=task_payload,
        submissions=panel_submissions,
        outsider_submission=outsider_submission,
    )
    claim_payload = agent_loop_v1.build_ecu_claim_batch(task_payload, panel_eval)
    combined_panel_payload = {
        "marker": panel_eval["marker"],
        "runtime_version": agent_loop_v1.AGENT_LOOP_V1_RUNTIME_VERSION,
        "panel_result": panel_eval["panel_result"],
        "ecu_claim_batch": {
            key: value for key, value in claim_payload.items() if key not in {"marker", "runtime_version"}
        },
        "outsider_submission": outsider_submission,
    }

    monkeypatch.setattr(scenario_runner, "_git_head", lambda: "deadbeef")
    monkeypatch.setattr(scenario_runner, "_ensure_home_started", lambda: (False, "home_node_running"))
    monkeypatch.setattr(scenario_runner, "_stop_home_if_needed", lambda _started_here: None)
    monkeypatch.setattr(
        scenario_runner,
        "_run",
        lambda command, cwd=None, env=None: subprocess.CompletedProcess(command, 0, stdout="ok\n", stderr=""),
    )
    monkeypatch.setattr(
        scenario_runner,
        "_run_local_agent",
        lambda agent, task, emit_dir: payloads_by_slot[int(agent["slot"])],
    )

    def _fake_run_remote_agent(agent: dict[str, object], task: dict[str, object], emit_dir: Path, host_payload: dict[str, object]) -> dict[str, object]:
        payload = payloads_by_slot[int(agent["slot"])]
        (emit_dir / f"submission_{agent['slot']}.json").write_text(
            json.dumps(payload, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        return payload

    monkeypatch.setattr(scenario_runner, "_run_remote_agent", _fake_run_remote_agent)

    def _fake_evaluate_panel(task_payload: dict[str, object], submission_dir: Path, outsider: dict[str, object], emit_dir: Path) -> dict[str, object]:
        (emit_dir / "panel_result.json").write_text(
            json.dumps(combined_panel_payload, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        (emit_dir / "ecu_claims.json").write_text(
            json.dumps(claim_payload, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        (emit_dir / "outsider_submission.json").write_text(
            json.dumps(outsider_submission, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        return combined_panel_payload

    monkeypatch.setattr(scenario_runner, "_evaluate_panel", _fake_evaluate_panel)
    monkeypatch.setattr(
        scenario_runner,
        "_broadcast_from_home",
        lambda task_payload, artifact_file, gossip_type, emit_dir: {
            "send_statuses": [
                {"peer": "ilc-node-2", "send_status": 202},
                {"peer": "ilc-node-3", "send_status": 202},
            ]
        },
    )
    monkeypatch.setattr(
        scenario_runner,
        "_collect_diagnostics",
        lambda output_root: (output_root / "diagnostics").mkdir(parents=True, exist_ok=True),
    )

    output_root = tmp_path / "scenario-output"
    manifest = scenario_runner.run_scenario(
        scenario_path=scenario_runner.DEFAULT_SCENARIO_SPEC,
        hosts_path=hosts_path,
        output_root=output_root,
    )

    economic_manifest_path = output_root / "economic-state" / "manifest.json"
    assert economic_manifest_path.is_file()
    assert manifest["economic_manifest_path"] == str(economic_manifest_path)
    assert manifest["economic_distribution_check_ok"] is True
    assert manifest["economic_wallet_count"] == 8
    assert manifest["economic_reward_total"] == str(claim_payload["ledger"]["rewards_paid"])
    assert manifest["benchmark_metrics"]["panel_evaluation_ms"] >= 0.0
    assert manifest["benchmark_metrics"]["submission_to_panel_verdict_ms"] >= 0.0
    assert manifest["benchmark_metrics"]["submission_to_network_visibility_ms"] >= 0.0
    assert manifest["benchmark_metrics"]["claim_submission_delivery_metrics"]["endpoint_delivery_count"] == 0
    assert manifest["benchmark_metrics"]["claim_submission_delivery_metrics"]["duplicate_endpoint_delivery_ratio"] == 0.0

    summary_payload = query_rc0_1_economic_state.query_summary(economic_manifest_path)
    assert summary_payload["data"]["distribution_check_ok"] is True
    assert summary_payload["data"]["wallet_count"] == 8


def test_benchmark_distribution_uses_percentile_contract() -> None:
    distribution = benchmark_runner._distribution([10.0, 20.0, 30.0, 40.0])

    assert distribution["count"] == 4
    assert distribution["min_ms"] == 10.0
    assert distribution["max_ms"] == 40.0
    assert distribution["p50_ms"] == 20.0
    assert distribution["p95_ms"] == 40.0
    assert distribution["p99_ms"] == 40.0
