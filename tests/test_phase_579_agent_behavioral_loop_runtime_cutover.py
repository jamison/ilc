from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

from tools.agent_loop_v1 import AGENT_LOOP_V1_RUNTIME_VERSION, _normalize_channel
from tools.testbed import check_phase_579_agent_runtime_cutover as phase_579_checker
from tools.testbed import run_phase_579_agent_runtime_cutover as phase_579_runner

DOC_PATH = Path("docs/specs/ilc_rc0_1_agent_behavioral_loop_runtime_cutover_579_v0.1.md")
PROMPT_PATH = Path("docs/antigravity_tasks/antigravity_prompt__phase_579_g8_agent_behavioral_loop_runtime_cutover.md")
DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
TEST_PATH = Path("tests/test_phase_579_agent_behavioral_loop_runtime_cutover.py")
CHECKER_PATH = Path("tools/testbed/check_phase_579_agent_runtime_cutover.py")
RUNNER_PATH = Path("tools/testbed/run_phase_579_agent_runtime_cutover.py")
WALKTHROUGH_PATH = Path("docs/phases/phase_579_g8_agent_behavioral_loop_runtime_cutover_walkthrough.md")
STATUS_PATH = Path("docs/phases/STATUS.md")
PHASE_579_SUBJECT_TOKEN = "phase 579 agent behavioral loop runtime cutover"
PHASE_579_BACKFILL_SUBJECT_TOKEN = "phase 579 walkthrough and status backfill"
EXACT_REQUIRED_MAIN_PATHS = {
    str(PROMPT_PATH),
    str(DOC_PATH),
    str(TEST_PATH),
    str(CHECKER_PATH),
    str(RUNNER_PATH),
}
EXACT_REQUIRED_BACKFILL_PATHS = {
    str(WALKTHROUGH_PATH),
    str(STATUS_PATH),
}
REQUIRED_HEADINGS = (
    "## 1. Bounded RC target",
    "## 2. Authoritative runtime surfaces",
    "## 3. Deterministic cutover proof contract",
    "## 4. Runtime boundary and non-goals",
    "## 5. Carry-forward into Phase 580 and Phase 581",
)
REQUIRED_TOKENS = (
    "agent_behavioral_loop_runtime_cutover_authoritative",
    "bounded_helper_surface_no_longer_sufficient_for_phase_579",
    "phase_579_cutover_reads_locked_576_577_578_surfaces",
    "seven_live_agent_submissions_required_for_cutover",
    "panel_and_claim_broadcasts_must_complete_before_cutover_pass",
    "phase_579_keeps_transport_and_wallet_semantics_unchanged",
    "scenario_manifest_output_root_and_identity_must_match_cutover_root",
    "panel_direct_author_must_match_direct_claim",
    "phase_579_agent_cutover_ok",
    "phase_579_manifest_invalid",
    "phase_579_claim_batch_invalid",
)


def _scenario_payload() -> dict[str, object]:
    return json.loads(Path("testbed/scenarios/seven_agent_cycle_v1.json").read_text(encoding="utf-8"))


def _submission_payload(*, slot: int, node_name: str, cluster_id: str, variant: str, channel: str) -> dict[str, object]:
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
                "agent_id": f"agent-{slot:02d}",
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


def _write_cutover_root(tmp_path: Path) -> Path:
    root = tmp_path / "cutover-root"
    submissions_dir = root / "submissions"
    panel_dir = root / "panel"
    economic_dir = root / "economic-state"
    submissions_dir.mkdir(parents=True)
    panel_dir.mkdir(parents=True)
    economic_dir.mkdir(parents=True)

    scenario = _scenario_payload()
    scenario_path = tmp_path / "scenario.json"
    scenario_path.write_text(json.dumps(scenario, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    channel = _normalize_channel(str(scenario["channel"]))
    for agent in scenario["agents"]:  # type: ignore[index]
        payload = _submission_payload(
            slot=int(agent["slot"]),  # type: ignore[index]
            node_name=str(agent["node_name"]),  # type: ignore[index]
            cluster_id=str(agent["cluster_id"]),  # type: ignore[index]
            variant=str(agent["variant"]),  # type: ignore[index]
            channel=channel,
        )
        (submissions_dir / f"submission_{agent['slot']}.json").write_text(
            json.dumps(payload, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

    claims = [
        {
            "claim_id": "claim-1",
            "agent_id": "agent-01",
            "amount": 1.0,
            "claim_kind": "direct",
            "task_id": "task:three-node-seven-agent:cycle-001",
            "epoch": 574,
        }
    ]
    panel_payload = {
        "marker": "agent_loop_panel_ok",
        "runtime_version": AGENT_LOOP_V1_RUNTIME_VERSION,
        "panel_result": {
            "task_id": "task:three-node-seven-agent:cycle-001",
            "epoch": 574,
            "passed": True,
            "verdict_token": "panel_quorum_passed",
            "direct_author_agent_id": "agent-01",
        },
        "ecu_claim_batch": {
            "claims": claims,
            "ledger": {"rewards_paid": 1.0},
        },
    }
    (panel_dir / "panel_result.json").write_text(json.dumps(panel_payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    claims_payload = {
        "marker": "agent_loop_claims_ok",
        "runtime_version": AGENT_LOOP_V1_RUNTIME_VERSION,
        "claims": claims,
        "ledger": {"rewards_paid": 1.0},
    }
    (panel_dir / "ecu_claims.json").write_text(json.dumps(claims_payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (economic_dir / "manifest.json").write_text(
        json.dumps(
            {
                "scenario_root": str(root),
                "summary": {"task_id": "task:three-node-seven-agent:cycle-001", "reward_total": 1.0},
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    manifest = {
        "output_root": str(root),
        "scenario_path": str(scenario_path),
        "scenario_runtime_version": AGENT_LOOP_V1_RUNTIME_VERSION,
        "submission_count": 7,
        "submission_files": [f"submissions/submission_{agent['slot']}.json" for agent in scenario["agents"]],  # type: ignore[index]
        "task_id": "task:three-node-seven-agent:cycle-001",
        "epoch": 574,
        "panel_broadcast_statuses": [{"status_code": 202}],
        "claims_broadcast_statuses": [{"status_code": 202}],
        "economic_manifest_path": str(economic_dir / "manifest.json"),
    }
    (root / "scenario_manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return root


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _changed_paths_for_commit(commit_ref: str) -> set[str]:
    result = subprocess.run(
        ["git", "show", "--name-only", "--pretty=", commit_ref],
        capture_output=True,
        check=True,
        text=True,
    )
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


def _resolve_commit_ref(*, subject_token: str, expected_paths: set[str]) -> str:
    result = subprocess.run(
        ["git", "log", "--format=%H%x09%s"],
        capture_output=True,
        check=True,
        text=True,
    )
    matches: list[str] = []
    for line in result.stdout.splitlines():
        if "\t" not in line:
            continue
        commit_hash, subject = line.split("\t", 1)
        if subject_token not in subject.lower():
            continue
        matches.append(commit_hash)
    for commit_ref in matches:
        if _changed_paths_for_commit(commit_ref) == expected_paths:
            return commit_ref
    raise AssertionError(f"commit_not_present_in_local_history:{subject_token}")


def test_document_exists_and_contains_required_headings() -> None:
    text = _read(DOC_PATH)
    for heading in REQUIRED_HEADINGS:
        assert heading in text


def test_document_contains_required_governance_tokens() -> None:
    text = _read(DOC_PATH)
    for token in REQUIRED_TOKENS:
        assert token in text


def test_runner_and_checker_exist_and_are_importable() -> None:
    assert phase_579_checker.__file__
    assert phase_579_runner.__file__
    assert TEST_PATH.is_file()


def test_checker_passes_on_deterministic_synthetic_cutover_root(tmp_path: Path) -> None:
    root = _write_cutover_root(tmp_path)
    manifest = phase_579_checker.check_cutover_root(scenario_root=root)
    assert manifest["marker"] == "phase_579_agent_cutover_ok"
    assert manifest["submission_count"] == 7
    assert (root / "phase_579_cutover_manifest.json").is_file()


def test_submission_runtime_version_mismatch_fails_with_expected_token(tmp_path: Path) -> None:
    root = _write_cutover_root(tmp_path)
    submission_path = root / "submissions" / "submission_1.json"
    payload = json.loads(submission_path.read_text(encoding="utf-8"))
    payload["runtime_version"] = "wrong"
    submission_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    try:
        phase_579_checker.check_cutover_root(scenario_root=root)
    except phase_579_checker.Phase579CutoverError as exc:
        assert exc.token == "phase_579_submission_runtime_version_mismatch"
    else:
        raise AssertionError("expected Phase579CutoverError")


def test_missing_economic_manifest_fails_with_expected_token(tmp_path: Path) -> None:
    root = _write_cutover_root(tmp_path)
    (root / "economic-state" / "manifest.json").unlink()

    try:
        phase_579_checker.check_cutover_root(scenario_root=root)
    except phase_579_checker.Phase579CutoverError as exc:
        assert exc.token == "phase_579_economic_manifest_missing"
    else:
        raise AssertionError("expected Phase579CutoverError")


def test_manifest_output_root_mismatch_fails_with_expected_token(tmp_path: Path) -> None:
    root = _write_cutover_root(tmp_path)
    manifest_path = root / "scenario_manifest.json"
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    payload["output_root"] = "/tmp/wrong-root"
    manifest_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    try:
        phase_579_checker.check_cutover_root(scenario_root=root)
    except phase_579_checker.Phase579CutoverError as exc:
        assert exc.token == "phase_579_manifest_invalid"
    else:
        raise AssertionError("expected Phase579CutoverError")


def test_direct_author_claim_mismatch_fails_with_expected_token(tmp_path: Path) -> None:
    root = _write_cutover_root(tmp_path)
    panel_path = root / "panel" / "panel_result.json"
    payload = json.loads(panel_path.read_text(encoding="utf-8"))
    payload["panel_result"]["direct_author_agent_id"] = "agent-99"
    panel_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    try:
        phase_579_checker.check_cutover_root(scenario_root=root)
    except phase_579_checker.Phase579CutoverError as exc:
        assert exc.token == "phase_579_claim_batch_invalid"
    else:
        raise AssertionError("expected Phase579CutoverError")


def test_checker_accepts_relative_scenario_root_when_manifest_uses_absolute_paths(tmp_path: Path) -> None:
    root = _write_cutover_root(tmp_path)
    relative_root = Path(os.path.relpath(root, Path.cwd()))
    manifest = phase_579_checker.check_cutover_root(scenario_root=relative_root)
    assert manifest["marker"] == "phase_579_agent_cutover_ok"


def test_runner_delegates_to_scenario_and_checker(monkeypatch, tmp_path: Path) -> None:
    root = tmp_path / "out"
    monkeypatch.setattr(
        phase_579_runner.scenario_runner,
        "run_scenario",
        lambda scenario_path, hosts_path, output_root: {"marker": "three_node_seven_agent_scenario_ok", "output_root": str(output_root)},
    )
    monkeypatch.setattr(
        phase_579_runner,
        "check_cutover_root",
        lambda scenario_root: {"marker": "phase_579_agent_cutover_ok", "scenario_root": str(scenario_root)},
    )
    result = phase_579_runner.main(
        [
            "--output-root",
            str(root),
            "--scenario",
            "testbed/scenarios/seven_agent_cycle_v1.json",
            "--hosts",
            "testbed/hosts.json",
        ]
    )
    assert result == 0


def test_phase_579_main_commit_touches_expected_paths_only() -> None:
    commit_ref = _resolve_commit_ref(
        subject_token=PHASE_579_SUBJECT_TOKEN,
        expected_paths=EXACT_REQUIRED_MAIN_PATHS,
    )
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS


def test_phase_579_main_commit_touches_no_adr_cdl_path_and_no_ilc_core_path() -> None:
    commit_ref = _resolve_commit_ref(
        subject_token=PHASE_579_SUBJECT_TOKEN,
        expected_paths=EXACT_REQUIRED_MAIN_PATHS,
    )
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert not any(path.startswith("docs/adr/") for path in changed_paths)
    assert not any(path.startswith("docs/specs/ilc_cdl_") for path in changed_paths)
    assert not any(path.startswith("docs/specs/ilc_cdl-") for path in changed_paths)
    assert not any("/ilc_cdl_" in path for path in changed_paths)
    assert not any(path.startswith("ilc_core/") for path in changed_paths)


def test_phase_579_backfill_commit_touches_expected_paths_only() -> None:
    commit_ref = _resolve_commit_ref(
        subject_token=PHASE_579_BACKFILL_SUBJECT_TOKEN,
        expected_paths=EXACT_REQUIRED_BACKFILL_PATHS,
    )
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_BACKFILL_PATHS


def test_phase_579_backfill_commit_touches_no_adr_cdl_path_and_no_ilc_core_path() -> None:
    commit_ref = _resolve_commit_ref(
        subject_token=PHASE_579_BACKFILL_SUBJECT_TOKEN,
        expected_paths=EXACT_REQUIRED_BACKFILL_PATHS,
    )
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert not any(path.startswith("docs/adr/") for path in changed_paths)
    assert not any(path.startswith("docs/specs/ilc_cdl_") for path in changed_paths)
    assert not any(path.startswith("docs/specs/ilc_cdl-") for path in changed_paths)
    assert not any("/ilc_cdl_" in path for path in changed_paths)
    assert not any(path.startswith("ilc_core/") for path in changed_paths)
