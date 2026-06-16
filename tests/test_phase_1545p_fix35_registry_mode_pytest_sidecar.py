import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "out/test_registry_sidecar_plan_1545p_fix35.json"
REPORT = ROOT / "docs/specs/ilc_test_registry_sidecar_scaffold_report_1545p_fix35_v0.1.md"
PROMPT = ROOT / "docs/antigravity_tasks/antigravity_prompt__phase_1545p_fix35_g10_registry_mode_pytest_sidecar.md"
TOOL = ROOT / "tools/ilc_test_registry_sidecar.py"
WALKTHROUGH = ROOT / "docs/phases/phase_1545p_fix35_registry_mode_pytest_sidecar_walkthrough.md"
STATUS = ROOT / "docs/phases/STATUS.md"
PLANNING_INDEX = ROOT / "docs/PLANNING_INDEX.md"


TOKENS = {
    "pytest_sidecar_registry_mode_scaffold_committed_phase_1545p_fix35",
    "graph_resolved_pytest_commands_recorded_phase_1545p_fix35",
    "pytest_sidecar_gate_enforcement_recorded_phase_1545p_fix35",
    "pytest_sidecar_default_dry_run_phase_1545p_fix35",
    "pytest_sidecar_execution_deferred_to_evidence_phase_1545p_fix35",
    "public_path_remains_blocked_phase_1545p_fix35",
}


def _json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_fix35_plan_resolves_default_profile_pytest_commands():
    payload = _json(PLAN)

    assert payload["phase"] == "1545p-Fix35"
    assert payload["status"] == "pass"
    assert payload["sidecar_mode"] == "registry_mode_pytest_dry_run"
    assert payload["default_dry_run"] is True
    assert payload["execution_policy"] == "execution_deferred_to_fix36_evidence_envelope"
    assert payload["selection"]["profile"] == "default_local_pytest"
    assert payload["selected_count"] == 8
    assert TOKENS.issubset(set(payload["output_tokens"]))
    for command in payload["commands"]:
        assert command["command"][0:3] == ["python", "-m", "pytest"]
        assert command["command"][-1] == "-q"
        assert command["pytest_nodeid"].startswith("tests/")
        assert "::" in command["pytest_nodeid"]
        assert command["dry_run"] is True
        assert command["environment_gates"] == []


def test_fix35_report_and_status_preserve_nonclaims():
    combined = _text(REPORT) + _text(WALKTHROUGH) + _text(STATUS) + _text(PLANNING_INDEX)

    for token in TOKENS:
        assert token in combined
    for phrase in [
        "No tests were executed.",
        "No evidence envelope was generated.",
        "No canonical Atlas mutation occurred.",
        "No Genesis signing occurred.",
        "No public RC activation occurred.",
        "`--execute` fails closed in Fix35",
    ]:
        assert phrase in combined


def test_fix35_tool_fails_closed_for_execution_request(tmp_path):
    out = tmp_path / "execute.json"
    result = subprocess.run(
        [
            sys.executable,
            str(TOOL),
            "run",
            "--execute",
            "--json-out",
            str(out),
            "--report",
            str(tmp_path / "report.md"),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 2
    payload = _json(out)
    assert payload["status"] == "fail_closed"
    assert payload["error"] == "execution_deferred_to_fix36_evidence_envelope"


def test_fix35_tool_fails_closed_for_gated_profile_without_ack(tmp_path):
    out = tmp_path / "gated.json"
    result = subprocess.run(
        [
            sys.executable,
            str(TOOL),
            "run",
            "--profile",
            "historical_phase_snapshot",
            "--json-out",
            str(out),
            "--report",
            str(tmp_path / "report.md"),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 2
    payload = _json(out)
    assert payload["status"] == "fail_closed"
    assert payload["error"] == "gated_profile_requires_explicit_allow:historical_phase_snapshot"


def test_fix35_tool_supports_digest_sample_fallback(tmp_path):
    out = tmp_path / "fallback.json"
    report = tmp_path / "fallback.md"
    missing_full = tmp_path / "missing_function_artifact.json"
    result = subprocess.run(
        [
            sys.executable,
            str(TOOL),
            "run",
            "--function-artifact",
            str(missing_full),
            "--json-out",
            str(out),
            "--report",
            str(report),
            "--limit",
            "3",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    payload = _json(out)
    assert payload["input"]["function_input_scope"] == "digest_sample_fallback"
    assert payload["selected_count"] == 3
    assert report.exists()


def test_fix35_tool_and_prompt_encode_safety_boundaries():
    combined = _text(TOOL) + _text(PROMPT)

    assert "sort_keys=True" in combined
    assert "allow_nan=False" in combined
    assert "execution_deferred_to_fix36_evidence_envelope" in combined
    assert "dry_run_required_in_phase_1545p_fix35" in combined
    assert "unknown_executor_profile" in combined
    assert "environment_gate_requires_explicit_allow" in combined


def test_fix35_docs_have_no_placeholder_ellipses():
    combined = _text(REPORT) + _text(WALKTHROUGH)

    assert "..." not in combined
    assert "…" not in combined
