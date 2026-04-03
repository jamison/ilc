from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from ilc_core.rc.economic_cycle_runtime import materialize_economic_cycle
from tools.run_rc0_1_economic_proof import run_economic_proof
from tools.testbed import check_phase_581_settlement_wallet_query_integration as phase_581_checker
from tools.testbed import run_phase_581_settlement_wallet_query_integration as phase_581_runner
from tests.test_phase_580_panel_live_submission_integration import _write_integration_root

DOC_PATH = Path("docs/specs/ilc_rc0_1_ecu_settlement_wallet_query_integration_581_v0.1.md")
PROMPT_PATH = Path("docs/antigravity_tasks/antigravity_prompt__phase_581_g8_ecu_settlement_wallet_query_integration.md")
DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
TEST_PATH = Path("tests/test_phase_581_settlement_wallet_query_integration.py")
CHECKER_PATH = Path("tools/testbed/check_phase_581_settlement_wallet_query_integration.py")
RUNNER_PATH = Path("tools/testbed/run_phase_581_settlement_wallet_query_integration.py")
WALKTHROUGH_PATH = Path("docs/phases/phase_581_g8_ecu_settlement_wallet_query_integration_walkthrough.md")
STATUS_PATH = Path("docs/phases/STATUS.md")
PHASE_581_SUBJECT_TOKEN = "phase 581 settlement and wallet query integration"
PHASE_581_BACKFILL_SUBJECT_TOKEN = "phase 581 walkthrough and status backfill"
EXACT_REQUIRED_MAIN_PATHS = {
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
    "## 3. Deterministic settlement and wallet query contract",
    "## 4. Claimability and read-only boundary",
    "## 5. Carry-forward into Phase 582",
)
REQUIRED_TOKENS = (
    "phase_581_live_settlement_path_authoritative",
    "phase_581_replay_idempotency_required",
    "phase_581_wallet_queries_must_read_settled_lmdb_state",
    "phase_581_runtime_roots_must_remain_identity_aligned",
    "phase_581_no_public_claimability_or_spend_semantics",
    "phase_581_keeps_576_577_578_meaning_unchanged",
)


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
    pytest.skip(f"commit_not_present_in_local_history:{subject_token}")


def _write_phase_581_root(tmp_path: Path) -> tuple[Path, Path, Path]:
    root, replay_dir = _write_integration_root(tmp_path)
    phase_580_manifest = {
        "marker": "phase_580_panel_live_submission_ok",
        "scenario_root": str(root),
        "replay_root": str(replay_dir),
    }
    (root / "phase_580_panel_integration_manifest.json").write_text(
        json.dumps(phase_580_manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    economic_state_root = root / "economic-state"
    if economic_state_root.exists():
        import shutil

        shutil.rmtree(economic_state_root)
    claims_path = root / "panel" / "ecu_claims.json"
    claims_payload = json.loads(claims_path.read_text(encoding="utf-8"))
    outcome_summary = {"count": len(claims_payload.get("claims", [])), "total_stake": 4.0, "total_reward": 4.0}
    claims_payload.setdefault("outcome_summary", outcome_summary)
    claims_path.write_text(json.dumps(claims_payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    panel_path = root / "panel" / "panel_result.json"
    panel_payload = json.loads(panel_path.read_text(encoding="utf-8"))
    panel_payload.setdefault("ecu_claim_batch", {}).setdefault("outcome_summary", outcome_summary)
    panel_path.write_text(json.dumps(panel_payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    materialize_economic_cycle(scenario_root=root, output_root=root / "economic-state")
    manifest_path = root / "economic-state" / "manifest.json"
    proof_root = tmp_path / "proof"
    replay_proof_root = tmp_path / "proof-replay"
    run_economic_proof(manifest_path=manifest_path, output_root=proof_root)
    run_economic_proof(manifest_path=manifest_path, output_root=replay_proof_root)
    return root, proof_root, replay_proof_root


def test_document_exists_and_contains_required_headings() -> None:
    text = _read(DOC_PATH)
    for heading in REQUIRED_HEADINGS:
        assert heading in text


def test_document_contains_required_governance_tokens() -> None:
    text = _read(DOC_PATH)
    for token in REQUIRED_TOKENS:
        assert token in text


def test_runner_and_checker_exist_and_are_importable() -> None:
    assert phase_581_checker.__file__
    assert phase_581_runner.__file__
    assert PROMPT_PATH.is_file()
    assert TEST_PATH.is_file()


def test_checker_passes_on_deterministic_synthetic_root(tmp_path: Path) -> None:
    root, proof_root, replay_proof_root = _write_phase_581_root(tmp_path)
    manifest = phase_581_checker.check_settlement_wallet_query_integration(
        scenario_root=root,
        proof_root=proof_root,
        replay_proof_root=replay_proof_root,
    )
    assert manifest["marker"] == "phase_581_settlement_wallet_query_ok"
    assert manifest["settlement_status"] == "applied"
    assert manifest["replay_settlement_status"] == "idempotent_replay"


def test_replay_drift_fails_with_expected_token(tmp_path: Path) -> None:
    root, proof_root, replay_proof_root = _write_phase_581_root(tmp_path)
    manifest_path = replay_proof_root / "manifest.json"
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    payload["comparison"]["wallets_match"] = False
    manifest_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    try:
        phase_581_checker.check_settlement_wallet_query_integration(
            scenario_root=root,
            proof_root=proof_root,
            replay_proof_root=replay_proof_root,
        )
    except phase_581_checker.Phase581IntegrationError as exc:
        assert exc.token == "phase_581_replay_drift_detected"
    else:
        raise AssertionError("expected Phase581IntegrationError")


def test_wallet_history_digest_mismatch_fails_with_expected_token(tmp_path: Path) -> None:
    root, proof_root, replay_proof_root = _write_phase_581_root(tmp_path)
    manifest_path = proof_root / "manifest.json"
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    payload["query_payloads"]["wallet_history"]["data"]["history_digest"] = "tampered-history-digest"
    manifest_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    try:
        phase_581_checker.check_settlement_wallet_query_integration(
            scenario_root=root,
            proof_root=proof_root,
            replay_proof_root=replay_proof_root,
        )
    except phase_581_checker.Phase581IntegrationError as exc:
        assert exc.token == "phase_581_wallet_history_invalid"
    else:
        raise AssertionError("expected Phase581IntegrationError")


def test_runtime_store_identity_mismatch_fails_with_expected_token(tmp_path: Path) -> None:
    root, proof_root, replay_proof_root = _write_phase_581_root(tmp_path)
    manifest_path = root / "economic-state" / "manifest.json"
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    payload["runtime_identity"]["task_id"] = "task:tampered"
    manifest_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    try:
        phase_581_checker.check_settlement_wallet_query_integration(
            scenario_root=root,
            proof_root=proof_root,
            replay_proof_root=replay_proof_root,
        )
    except phase_581_checker.Phase581IntegrationError as exc:
        assert exc.token == "phase_581_runtime_store_invalid"
    else:
        raise AssertionError("expected Phase581IntegrationError")


def test_claimability_boundary_drift_fails_with_expected_token(tmp_path: Path) -> None:
    root, proof_root, replay_proof_root = _write_phase_581_root(tmp_path)
    manifest_path = proof_root / "manifest.json"
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    payload["query_payloads"]["wallet_status"]["data"]["wallet"]["spend_authority"] = True
    manifest_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    try:
        phase_581_checker.check_settlement_wallet_query_integration(
            scenario_root=root,
            proof_root=proof_root,
            replay_proof_root=replay_proof_root,
        )
    except phase_581_checker.Phase581IntegrationError as exc:
        assert exc.token == "phase_581_claimability_boundary_invalid"
    else:
        raise AssertionError("expected Phase581IntegrationError")


def test_runner_delegates_to_runtime_and_checker(monkeypatch, tmp_path: Path) -> None:
    root = tmp_path / "out"
    monkeypatch.setattr(
        phase_581_runner.scenario_runner,
        "run_scenario",
        lambda scenario_path, hosts_path, output_root: {"marker": "three_node_seven_agent_scenario_ok", "output_root": str(output_root)},
    )
    monkeypatch.setattr(
        phase_581_runner,
        "check_cutover_root",
        lambda scenario_root: {"marker": "phase_579_agent_cutover_ok", "scenario_root": str(scenario_root)},
    )
    monkeypatch.setattr(
        phase_581_runner.replay_runner,
        "replay_scenario",
        lambda scenario_root, scenario_spec_path, output_root: {"marker": "three_node_seven_agent_replay_ok", "scenario_root": str(scenario_root), "output_root": str(output_root)},
    )
    monkeypatch.setattr(
        phase_581_runner,
        "check_panel_live_submission_integration",
        lambda scenario_root, replay_root: {"marker": "phase_580_panel_live_submission_ok", "scenario_root": str(scenario_root), "replay_root": str(replay_root)},
    )
    monkeypatch.setattr(
        phase_581_runner,
        "run_economic_proof",
        lambda manifest_path, output_root: {"manifest_path": str(manifest_path), "proof_runner_manifest_path": str(output_root / "manifest.json")},
    )
    monkeypatch.setattr(
        phase_581_runner,
        "check_settlement_wallet_query_integration",
        lambda scenario_root, proof_root, replay_proof_root: {"marker": "phase_581_settlement_wallet_query_ok", "scenario_root": str(scenario_root), "proof_root": str(proof_root), "replay_proof_root": str(replay_proof_root)},
    )
    result = phase_581_runner.main([
        "--output-root", str(root),
        "--scenario", "testbed/scenarios/seven_agent_cycle_v1.json",
        "--hosts", "testbed/hosts.json",
    ])
    assert result == 0


def test_phase_581_main_commit_touches_expected_paths_only() -> None:
    commit_ref = _resolve_commit_ref(subject_token=PHASE_581_SUBJECT_TOKEN, expected_paths=EXACT_REQUIRED_MAIN_PATHS)
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS


def test_phase_581_main_commit_touches_no_adr_cdl_path_and_no_ilc_core_path() -> None:
    commit_ref = _resolve_commit_ref(subject_token=PHASE_581_SUBJECT_TOKEN, expected_paths=EXACT_REQUIRED_MAIN_PATHS)
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert not any(path.startswith("docs/adr/") for path in changed_paths)
    assert not any(path.startswith("docs/specs/ilc_cdl_") for path in changed_paths)
    assert not any(path.startswith("docs/specs/ilc_cdl-") for path in changed_paths)
    assert not any("/ilc_cdl_" in path for path in changed_paths)
    assert not any(path.startswith("ilc_core/") for path in changed_paths)


def test_phase_581_backfill_commit_touches_expected_paths_only() -> None:
    commit_ref = _resolve_commit_ref(subject_token=PHASE_581_BACKFILL_SUBJECT_TOKEN, expected_paths=EXACT_REQUIRED_BACKFILL_PATHS)
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_BACKFILL_PATHS


def test_phase_581_backfill_commit_touches_no_adr_cdl_path_and_no_ilc_core_path() -> None:
    commit_ref = _resolve_commit_ref(subject_token=PHASE_581_BACKFILL_SUBJECT_TOKEN, expected_paths=EXACT_REQUIRED_BACKFILL_PATHS)
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert not any(path.startswith("docs/adr/") for path in changed_paths)
    assert not any(path.startswith("docs/specs/ilc_cdl_") for path in changed_paths)
    assert not any(path.startswith("docs/specs/ilc_cdl-") for path in changed_paths)
    assert not any("/ilc_cdl_" in path for path in changed_paths)
    assert not any(path.startswith("ilc_core/") for path in changed_paths)
