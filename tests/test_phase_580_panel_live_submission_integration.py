from __future__ import annotations

import json
from pathlib import Path

from tools.agent_loop_v1 import AGENT_LOOP_V1_RUNTIME_VERSION, _normalize_channel
from tools.testbed import check_phase_580_panel_live_submission_integration as phase_580_checker
from tools.testbed import run_phase_580_panel_live_submission_integration as phase_580_runner

DOC_PATH = Path("docs/specs/ilc_rc0_1_7_plus_1_panel_live_submission_integration_580_v0.1.md")
PROMPT_PATH = Path("docs/antigravity_tasks/antigravity_prompt__phase_580_g8_7_plus_1_panel_live_submission_integration.md")
TEST_PATH = Path("tests/test_phase_580_panel_live_submission_integration.py")
REQUIRED_HEADINGS = (
    "## 1. Bounded RC target",
    "## 2. Authoritative runtime surfaces",
    "## 3. Deterministic integration contract",
    "## 4. Outsider boundary and live broadcast rule",
    "## 5. Carry-forward into Phase 581",
)
REQUIRED_TOKENS = (
    "phase_580_panel_submission_path_authoritative",
    "phase_580_replay_agreement_required",
    "phase_580_outsider_review_only_boundary",
    "phase_580_panel_claim_alignment_required",
    "phase_580_broadcasts_must_reflect_live_artifacts",
    "phase_580_keeps_576_577_578_semantics_unchanged",
)


def _scenario_payload() -> dict[str, object]:
    return json.loads(Path("testbed/scenarios/seven_agent_cycle_v1.json").read_text(encoding="utf-8"))


def _submission_payload(*, slot: int, node_name: str, cluster_id: str, variant: str, channel: str) -> dict[str, object]:
    agent_id = f"agent-{slot:02d}"
    return {
        "marker": "agent_loop_submission_ok",
        "runtime_version": AGENT_LOOP_V1_RUNTIME_VERSION,
        "submission": {
            "task_id": "task:three-node-seven-agent:cycle-001",
            "epoch": 574,
            "channel": channel,
            "profile": {
                "slot": slot,
                "seed_hex": f"{slot:02x}" * 16,
                "cluster_id": cluster_id,
                "node_name": node_name,
                "variant": variant,
                "agent_id": agent_id,
            },
            "output_hash": f"hash-{slot}",
            "output_payload": {"task_id": "task:three-node-seven-agent:cycle-001"},
            "ep_task": {"output_hash": f"hash-{slot}"},
            "gossip_type": "agent_submission",
            "send_statuses": [
                {"endpoint": "https://peer-a", "payload_bytes": 10, "payload_sha256": f"sha-{slot}-a", "status_code": 202},
                {"endpoint": "https://peer-b", "payload_bytes": 10, "payload_sha256": f"sha-{slot}-b", "status_code": 202},
            ],
        },
    }


def _write_integration_root(tmp_path: Path) -> tuple[Path, Path]:
    root = tmp_path / "phase-580-root"
    submissions_dir = root / "submissions"
    panel_dir = root / "panel"
    replay_dir = root / "replay"
    economic_dir = root / "economic-state"
    submissions_dir.mkdir(parents=True)
    panel_dir.mkdir(parents=True)
    replay_dir.mkdir(parents=True)
    economic_dir.mkdir(parents=True)

    scenario = _scenario_payload()
    scenario_path = tmp_path / "scenario.json"
    scenario_path.write_text(json.dumps(scenario, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    channel = _normalize_channel(str(scenario["channel"]))

    submission_agent_ids: list[str] = []
    votes: list[dict[str, object]] = []
    for agent in scenario["agents"]:  # type: ignore[index]
        slot = int(agent["slot"])
        payload = _submission_payload(
            slot=slot,
            node_name=str(agent["node_name"]),
            cluster_id=str(agent["cluster_id"]),
            variant=str(agent["variant"]),
            channel=channel,
        )
        submission_agent_ids.append(payload["submission"]["profile"]["agent_id"])  # type: ignore[index]
        (submissions_dir / f"submission_{slot}.json").write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        votes.append(
            {
                "reviewer_agent_id": payload["submission"]["profile"]["agent_id"],  # type: ignore[index]
                "cluster_id": payload["submission"]["profile"]["cluster_id"],  # type: ignore[index]
                "node_name": payload["submission"]["profile"]["node_name"],  # type: ignore[index]
                "variant": payload["submission"]["profile"]["variant"],  # type: ignore[index]
                "output_hash": payload["submission"]["output_hash"],  # type: ignore[index]
                "matches_majority": True,
                "passed_gate": True,
                "passed": True,
            }
        )

    outsider_agent_id = "agent-outsider"
    outsider_submission = {
        "task_id": "task:three-node-seven-agent:cycle-001",
        "epoch": 574,
        "channel": channel,
        "gossip_type": "agent_submission",
        "output_hash": "hash-outsider",
        "output_payload": {"task_id": "task:three-node-seven-agent:cycle-001"},
        "profile": {
            "agent_id": outsider_agent_id,
            "cluster_id": "cluster-outsider",
            "node_name": "ilc-node-1",
            "seed_hex": "08" * 16,
            "slot": 8,
            "variant": "outsider",
        },
        "send_statuses": [],
    }
    votes.append(
        {
            "reviewer_agent_id": outsider_agent_id,
            "cluster_id": "cluster-outsider",
            "node_name": "ilc-node-1",
            "variant": "outsider",
            "output_hash": "hash-outsider",
            "matches_majority": True,
            "passed_gate": True,
            "passed": True,
        }
    )

    claims = [
        {
            "claim_id": "claim-direct",
            "task_id": "task:three-node-seven-agent:cycle-001",
            "epoch": 574,
            "agent_id": submission_agent_ids[0],
            "claim_kind": "direct",
            "amount": 3.0,
        },
        {
            "claim_id": "claim-passive",
            "task_id": "task:three-node-seven-agent:cycle-001",
            "epoch": 574,
            "agent_id": submission_agent_ids[1],
            "claim_kind": "passive",
            "amount": 1.0,
        },
    ]
    panel_payload = {
        "marker": "agent_loop_panel_ok",
        "runtime_version": AGENT_LOOP_V1_RUNTIME_VERSION,
        "panel_result": {
            "task_id": "task:three-node-seven-agent:cycle-001",
            "epoch": 574,
            "passed": True,
            "verdict_token": "panel_quorum_passed",
            "yes_votes": 8,
            "no_votes": 0,
            "direct_author_agent_id": submission_agent_ids[0],
            "votes": votes,
        },
        "ecu_claim_batch": {
            "claims": claims,
            "ledger": {"rewards_paid": 4.0},
        },
        "outsider_submission": outsider_submission,
    }
    (panel_dir / "panel_result.json").write_text(json.dumps(panel_payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    claims_payload = {
        "marker": "agent_loop_claims_ok",
        "runtime_version": AGENT_LOOP_V1_RUNTIME_VERSION,
        "claims": claims,
        "ledger": {"rewards_paid": 4.0},
    }
    (panel_dir / "ecu_claims.json").write_text(json.dumps(claims_payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (panel_dir / "outsider_submission.json").write_text(json.dumps(outsider_submission, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    panel_broadcast = {
        "marker": "agent_loop_broadcast_ok",
        "runtime_version": AGENT_LOOP_V1_RUNTIME_VERSION,
        "artifact_file": str(panel_dir / "panel_result.json"),
        "gossip_type": "panel_verdict",
        "send_statuses": [{"status_code": 202}],
    }
    claims_broadcast = {
        "marker": "agent_loop_broadcast_ok",
        "runtime_version": AGENT_LOOP_V1_RUNTIME_VERSION,
        "artifact_file": str(panel_dir / "ecu_claims.json"),
        "gossip_type": "ecu_claim_batch",
        "send_statuses": [{"status_code": 202}],
    }
    (panel_dir / "broadcast_panel_verdict.json").write_text(json.dumps(panel_broadcast, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (panel_dir / "broadcast_ecu_claim_batch.json").write_text(json.dumps(claims_broadcast, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (economic_dir / "manifest.json").write_text(json.dumps({"scenario_root": str(root), "summary": {"task_id": "task:three-node-seven-agent:cycle-001", "reward_total": 4.0}}, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    scenario_manifest = {
        "scenario_path": str(scenario_path),
        "output_root": str(root),
        "scenario_runtime_version": AGENT_LOOP_V1_RUNTIME_VERSION,
        "submission_count": 7,
        "submission_files": [f"submissions/submission_{slot}.json" for slot in range(1, 8)],
        "task_id": "task:three-node-seven-agent:cycle-001",
        "epoch": 574,
        "panel_broadcast_statuses": [{"status_code": 202}],
        "claims_broadcast_statuses": [{"status_code": 202}],
        "economic_manifest_path": str(economic_dir / "manifest.json"),
    }
    (root / "scenario_manifest.json").write_text(json.dumps(scenario_manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    phase_579_manifest = {
        "marker": "phase_579_agent_cutover_ok",
        "runtime_version": AGENT_LOOP_V1_RUNTIME_VERSION,
        "scenario_root": str(root),
        "task_id": "task:three-node-seven-agent:cycle-001",
        "epoch": 574,
        "submission_count": 7,
        "panel_verdict_token": "panel_quorum_passed",
        "claim_count": 2,
        "reward_total": 4.0,
        "economic_manifest_path": str(economic_dir / "manifest.json"),
    }
    (root / "phase_579_cutover_manifest.json").write_text(json.dumps(phase_579_manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    replay_manifest = {
        "version": "three_node_seven_agent_replay_v0.1",
        "generated_at": "2026-04-03T00:00:00Z",
        "scenario_root": str(root),
        "scenario_spec_path": str(scenario_path),
        "panel_replay_file": str(replay_dir / "panel_replay.json"),
        "replay_payload": {
            "marker": "agent_loop_replay_ok",
            "runtime_version": AGENT_LOOP_V1_RUNTIME_VERSION,
            "panel_result_matches": True,
            "ecu_claims_match": True,
            "panel_verdict_token": "panel_quorum_passed",
            "ecu_claim_count": 2,
            "reward_total": 4.0,
        },
    }
    (replay_dir / "replay_manifest.json").write_text(json.dumps(replay_manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (replay_dir / "panel_replay.json").write_text(json.dumps(replay_manifest["replay_payload"], indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return root, replay_dir


def test_document_exists_and_contains_required_headings() -> None:
    text = DOC_PATH.read_text(encoding="utf-8")
    for heading in REQUIRED_HEADINGS:
        assert heading in text


def test_document_contains_required_governance_tokens() -> None:
    text = DOC_PATH.read_text(encoding="utf-8")
    for token in REQUIRED_TOKENS:
        assert token in text


def test_runner_and_checker_exist_and_are_importable() -> None:
    assert phase_580_checker.__file__
    assert phase_580_runner.__file__
    assert PROMPT_PATH.is_file()
    assert TEST_PATH.is_file()


def test_checker_passes_on_deterministic_synthetic_integration_root(tmp_path: Path) -> None:
    root, replay_dir = _write_integration_root(tmp_path)
    manifest = phase_580_checker.check_panel_live_submission_integration(scenario_root=root, replay_root=replay_dir)
    assert manifest["marker"] == "phase_580_panel_live_submission_ok"
    assert manifest["canonical_vote_count"] == 7
    assert manifest["outsider_vote_count"] == 1


def test_panel_replay_mismatch_fails_with_expected_token(tmp_path: Path) -> None:
    root, replay_dir = _write_integration_root(tmp_path)
    manifest_path = replay_dir / "replay_manifest.json"
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    payload["replay_payload"]["panel_result_matches"] = False
    manifest_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    try:
        phase_580_checker.check_panel_live_submission_integration(scenario_root=root, replay_root=replay_dir)
    except phase_580_checker.Phase580IntegrationError as exc:
        assert exc.token == "phase_580_panel_replay_invalid"
    else:
        raise AssertionError("expected Phase580IntegrationError")


def test_outsider_boundary_drift_fails_with_expected_token(tmp_path: Path) -> None:
    root, replay_dir = _write_integration_root(tmp_path)
    outsider_claim = {"claim_id": "outsider-claim", "task_id": "task:three-node-seven-agent:cycle-001", "epoch": 574, "agent_id": "agent-outsider", "claim_kind": "passive", "amount": 1.0}
    claims_path = root / "panel" / "ecu_claims.json"
    claims_payload = json.loads(claims_path.read_text(encoding="utf-8"))
    claims_payload["claims"].append(outsider_claim)
    claims_path.write_text(json.dumps(claims_payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    panel_path = root / "panel" / "panel_result.json"
    panel_payload = json.loads(panel_path.read_text(encoding="utf-8"))
    panel_payload["ecu_claim_batch"]["claims"].append(outsider_claim)
    panel_path.write_text(json.dumps(panel_payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    try:
        phase_580_checker.check_panel_live_submission_integration(scenario_root=root, replay_root=replay_dir)
    except phase_580_checker.Phase580IntegrationError as exc:
        assert exc.token == "phase_580_outsider_boundary_invalid"
    else:
        raise AssertionError("expected Phase580IntegrationError")


def test_non_202_broadcast_status_fails_with_expected_token(tmp_path: Path) -> None:
    root, replay_dir = _write_integration_root(tmp_path)
    path = root / "panel" / "broadcast_panel_verdict.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["send_statuses"][0]["status_code"] = 500
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    try:
        phase_580_checker.check_panel_live_submission_integration(scenario_root=root, replay_root=replay_dir)
    except phase_580_checker.Phase580IntegrationError as exc:
        assert exc.token == "phase_580_submission_broadcast_invalid"
    else:
        raise AssertionError("expected Phase580IntegrationError")


def test_runner_delegates_to_scenario_replay_and_checker(monkeypatch, tmp_path: Path) -> None:
    root = tmp_path / "out"
    monkeypatch.setattr(
        phase_580_runner.scenario_runner,
        "run_scenario",
        lambda scenario_path, hosts_path, output_root: {"marker": "three_node_seven_agent_scenario_ok", "output_root": str(output_root)},
    )
    monkeypatch.setattr(
        phase_580_runner,
        "check_cutover_root",
        lambda scenario_root: {"marker": "phase_579_agent_cutover_ok", "scenario_root": str(scenario_root)},
    )
    monkeypatch.setattr(
        phase_580_runner.replay_runner,
        "replay_scenario",
        lambda scenario_root, scenario_spec_path, output_root: {"marker": "three_node_seven_agent_replay_ok", "scenario_root": str(scenario_root), "output_root": str(output_root)},
    )
    monkeypatch.setattr(
        phase_580_runner,
        "check_panel_live_submission_integration",
        lambda scenario_root, replay_root: {"marker": "phase_580_panel_live_submission_ok", "scenario_root": str(scenario_root), "replay_root": str(replay_root)},
    )
    result = phase_580_runner.main([
        "--output-root", str(root),
        "--scenario", "testbed/scenarios/seven_agent_cycle_v1.json",
        "--hosts", "testbed/hosts.json",
    ])
    assert result == 0
