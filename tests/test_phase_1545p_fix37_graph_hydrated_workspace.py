import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROMPT = (
    ROOT
    / "docs/antigravity_tasks/antigravity_prompt__phase_1545p_fix37_g10_graph_hydrated_workspace.md"
)
ARTIFACT = ROOT / "out/test_registry_hydrated_workspace_1545p_fix37.json"
REPORT = ROOT / "docs/specs/ilc_test_registry_hydrated_workspace_report_1545p_fix37_v0.1.md"
STATUS = ROOT / "docs/phases/STATUS.md"
PLANNING_INDEX = ROOT / "docs/PLANNING_INDEX.md"
TOOL = ROOT / "tools/run_test_registry_hydrated_workspace.py"


TOKENS = {
    "pytest_sidecar_graph_hydrated_workspace_committed_phase_1545p_fix37",
    "hydrated_workspace_digest_verification_recorded_phase_1545p_fix37",
    "graph_hydrated_pytest_execution_bounded_phase_1545p_fix37",
    "pytest_sidecar_hydration_limits_recorded_phase_1545p_fix37",
    "graph_hydrated_evidence_no_authority_overclaim_phase_1545p_fix37",
    "public_path_remains_blocked_phase_1545p_fix37",
}


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_fix37_prompt_validates() -> None:
    result = subprocess.run(
        [sys.executable, "tools/validate_phase_prompt.py", str(PROMPT)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr


def test_fix37_artifact_records_verified_hydrated_workspace() -> None:
    payload = load(ARTIFACT)

    assert payload["phase"] == "1545p-Fix37"
    assert payload["status"] == "pass"
    assert payload["execution_scope"] == "bounded_graph_hydrated_workspace_from_fix35_plan"
    assert payload["selected_count"] == 6
    assert payload["excluded_count"] == 2
    assert payload["hydrated_file_count"] == 7
    assert payload["workspace_persistence"] == "deleted_after_run"
    assert payload["workspace_path"] is None
    assert payload["result_status_counts"] == {"passed": 6}
    assert TOKENS.issubset(set(payload["output_tokens"]))
    assert len(payload["source_tree_manifest_digest"]) == 64
    assert payload["environment_profile"]["executor_profile"] == "graph_hydrated_workspace_local"
    assert payload["environment_profile"]["wall_clock_protocol_semantics"] is False

    hydrated_paths = {entry["repo_path"] for entry in payload["hydrated_files"]}
    for required_path in {
        "pyproject.toml",
        "conftest.py",
        "tests/conftest.py",
        "tests/test_adm_003_7_plus_1_panel_role_354.py",
        "tests/test_adm_003_reference_agent_architecture_292.py",
        "tests/test_adm_003_role_resolution_339.py",
        "docs/specs/ilc_adm_003_reference_agent_architecture_v0.1.md",
    }:
        assert required_path in hydrated_paths

    for entry in payload["hydrated_files"]:
        assert entry["verified"] is True
        assert ".git" not in entry["repo_path"]
        assert len(entry["sha256"]) == 64


def test_fix37_excludes_git_history_dependent_commands() -> None:
    payload = load(ARTIFACT)

    excluded = {item["pytest_nodeid"]: item["reason"] for item in payload["excluded_commands"]}
    assert excluded == {
        "tests/test_adm_003_7_plus_1_panel_role_354.py::test_no_decision_log_mutation_in_phase_354_commit": "requires_git_history_not_hydrated",
        "tests/test_adm_003_7_plus_1_panel_role_354.py::test_no_ilc_core_runtime_mutation_in_phase_354_commit": "requires_git_history_not_hydrated",
    }


def test_fix37_evidence_runs_preserve_fix36_envelope_boundary() -> None:
    payload = load(ARTIFACT)

    for item in payload["evidence_runs"]:
        assert item["evidence_run_id"].startswith("test_evidence_run:")
        assert item["result_status"] == "passed"
        assert item["executor_profile"] == "graph_hydrated_workspace_local"
        assert item["hydration_mode"] == "bounded_plan_derived_source_tree_slice"
        assert item["command"][0:3] == ["python", "-m", "pytest"]
        assert item["command"][-1] == "-q"
        assert item["pytest_nodeid"].startswith("tests/")
        assert "::" in item["pytest_nodeid"]
        assert item["wall_clock_protocol_semantics"] is False
        assert item["produced_edges"] == ["PRODUCES_EVIDENCE", "EVIDENCES"]
        assert item["source_tree_manifest_digest"] == payload["source_tree_manifest_digest"]
        assert "test_evidence_is_not_authority" in item["non_claim_boundaries"]
        assert "no_graph_mutation" in item["non_claim_boundaries"]
        assert len(item["source_digest_sha256"]) == 64
        assert len(item["stdout_digest_sha256"]) == 64
        assert len(item["stderr_digest_sha256"]) == 64


def test_fix37_report_status_and_planning_preserve_boundaries() -> None:
    combined = read(REPORT) + read(STATUS) + read(PLANNING_INDEX)

    for token in TOKENS:
        assert token in combined
    for phrase in [
        "Evidence is support evidence only.",
        "Evidence does not grant authority, activation, eligibility, claimability, governance effect, or economic effect.",
        "Git history was not hydrated; git-history-dependent tests were excluded.",
        "No graph mutation, edge promotion, signing, upload, publication, runtime activation, sidecar activation, ADR mutation, or CDL mutation occurred.",
    ]:
        assert phrase in combined


def test_fix37_runner_fails_closed_for_environment_gate(tmp_path) -> None:
    plan = load(ROOT / "out/test_registry_sidecar_plan_1545p_fix35.json")
    plan["commands"][0]["environment_gates"] = ["ILC_RUN_PRIVATE_TESTS=1"]
    bad_plan = tmp_path / "bad_plan_env.json"
    bad_plan.write_text(json.dumps(plan, sort_keys=True), encoding="utf-8")
    out = tmp_path / "out_env.json"

    result = subprocess.run(
        [
            sys.executable,
            str(TOOL),
            "--plan",
            str(bad_plan),
            "--json-out",
            str(out),
            "--report",
            str(tmp_path / "report.md"),
            "--limit",
            "1",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 2
    payload = load(out)
    assert payload["status"] == "fail_closed"
    assert payload["error"] == "environment_gated_execution_forbidden"
    assert payload["output_tokens"] == []
