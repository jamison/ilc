import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROMPT = (
    ROOT
    / "docs/antigravity_tasks/antigravity_prompt__phase_1545p_fix36_g10_canonical_test_evidence_envelopes.md"
)
TOOL = ROOT / "tools/run_test_registry_evidence_envelopes.py"
ARTIFACT = ROOT / "out/test_registry_evidence_envelopes_1545p_fix36.json"
REPORT = ROOT / "docs/specs/ilc_test_registry_evidence_envelope_report_1545p_fix36_v0.1.md"
STATUS = ROOT / "docs/phases/STATUS.md"
PLANNING_INDEX = ROOT / "docs/PLANNING_INDEX.md"


TOKENS = {
    "canonical_test_evidence_envelopes_committed_phase_1545p_fix36",
    "graph_resolved_pytest_execution_bounded_phase_1545p_fix36",
    "test_evidence_canonical_serialization_confirmed_phase_1545p_fix36",
    "test_evidence_no_authority_overclaim_phase_1545p_fix36",
    "pytest_execution_profiles_remained_default_local_phase_1545p_fix36",
    "public_path_remains_blocked_phase_1545p_fix36",
}


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_fix36_prompt_validates() -> None:
    result = subprocess.run(
        [sys.executable, "tools/validate_phase_prompt.py", str(PROMPT)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr


def test_fix36_artifact_records_canonical_evidence_runs() -> None:
    payload = load(ARTIFACT)

    assert payload["phase"] == "1545p-Fix36"
    assert payload["status"] == "pass"
    assert payload["execution_scope"] == "bounded_default_local_pytest_from_fix35_plan"
    assert payload["selected_count"] == 8
    assert payload["result_status_counts"] == {"passed": 8}
    assert TOKENS.issubset(set(payload["output_tokens"]))
    assert payload["environment_profile"]["executor_profile"] == "default_local_pytest"
    assert payload["environment_profile"]["wall_clock_protocol_semantics"] is False

    for item in payload["evidence_runs"]:
        assert item["evidence_run_id"].startswith("test_evidence_run:")
        assert item["result_status"] == "passed"
        assert item["executor_profile"] == "default_local_pytest"
        assert item["command"][0:3] == ["python", "-m", "pytest"]
        assert item["command"][-1] == "-q"
        assert item["pytest_nodeid"].startswith("tests/")
        assert "::" in item["pytest_nodeid"]
        assert item["wall_clock_protocol_semantics"] is False
        assert item["produced_edges"] == ["PRODUCES_EVIDENCE", "EVIDENCES"]
        assert "test_evidence_is_not_authority" in item["non_claim_boundaries"]
        assert "no_graph_mutation" in item["non_claim_boundaries"]
        assert len(item["source_digest_sha256"]) == 64
        assert len(item["stdout_digest_sha256"]) == 64
        assert len(item["stderr_digest_sha256"]) == 64


def test_fix36_report_status_and_planning_preserve_boundaries() -> None:
    combined = read(REPORT) + read(STATUS) + read(PLANNING_INDEX)

    for token in TOKENS:
        assert token in combined
    for phrase in [
        "Evidence is support evidence only.",
        "Evidence does not grant authority, activation, eligibility, claimability, governance effect, or economic effect.",
        "Only `default_local_pytest` commands without environment gates were executed.",
        "No graph mutation, edge promotion, signing, upload, publication, runtime activation, sidecar activation, ADR mutation, or CDL mutation occurred.",
    ]:
        assert phrase in combined


def test_fix36_runner_fails_closed_for_non_default_profile(tmp_path) -> None:
    plan = load(ROOT / "out/test_registry_sidecar_plan_1545p_fix35.json")
    plan["commands"][0]["executor_profile"] = "historical_phase_snapshot"
    bad_plan = tmp_path / "bad_plan.json"
    bad_plan.write_text(json.dumps(plan, sort_keys=True), encoding="utf-8")
    out = tmp_path / "out.json"

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
    assert payload["error"] == "non_default_profile_execution_forbidden"
    assert payload["output_tokens"] == []


def test_fix36_runner_fails_closed_for_environment_gate(tmp_path) -> None:
    plan = load(ROOT / "out/test_registry_sidecar_plan_1545p_fix35.json")
    plan["commands"][0]["environment_gates"] = ["ILC_RUN_HISTORICAL_PHASE_SNAPSHOT_TESTS=1"]
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
