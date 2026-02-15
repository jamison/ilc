from pathlib import Path
import subprocess


GUARDRAIL_GATE_SCRIPT = Path("tools/check_track1_closure_guardrails.sh")
SCHEMA_PARITY_GATE_SCRIPT = Path("tools/check_replay_proof_schema_parity.sh")
CI_GATE_SCRIPT = Path("tools/check_cluster_a_replay_proof_ci_gate.sh")
RELEASE_GATE_SCRIPT = Path("tools/check_cluster_a_replay_proof_release_gate.sh")


def _run_guardrail_gate(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["bash", str(GUARDRAIL_GATE_SCRIPT), *args],
        capture_output=True,
        text=True,
        check=False,
    )


def _run_schema_parity_gate(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["bash", str(SCHEMA_PARITY_GATE_SCRIPT), *args],
        capture_output=True,
        text=True,
        check=False,
    )


def _run_release_gate(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["bash", str(RELEASE_GATE_SCRIPT), *args],
        capture_output=True,
        text=True,
        check=False,
    )


def _run_ci_gate(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["bash", str(CI_GATE_SCRIPT), *args],
        capture_output=True,
        text=True,
        check=False,
    )


def test_guardrail_gate_dry_run_lists_deterministic_commands() -> None:
    result = _run_guardrail_gate(["--dry-run"])
    assert result.returncode == 0
    assert "Dry run: Track 1 closure guardrail gate commands" in result.stdout
    assert "python3 -m pytest tests/test_edge_removal_phase1_guardrails.py tests/test_graph_edges.py -q" in result.stdout
    assert "ilc_core tests | sort" in result.stdout
    assert "\\bEdge\\b|\\bEdge\\(" in result.stdout


def test_guardrail_gate_unknown_argument_fails_with_code_2() -> None:
    result = _run_guardrail_gate(["--bad-arg"])
    assert result.returncode == 2
    assert "Unknown argument: --bad-arg" in result.stderr


def test_ops_gate_scripts_include_track1_guardrail_prestep() -> None:
    ci_text = CI_GATE_SCRIPT.read_text(encoding="utf-8")
    release_text = RELEASE_GATE_SCRIPT.read_text(encoding="utf-8")

    assert 'check_replay_proof_schema_parity.sh' in ci_text
    assert "=== CI Gate Step -1: Replay-Proof Schema Parity ===" in ci_text
    assert 'check_track1_closure_guardrails.sh' in ci_text
    assert "=== CI Gate Step 0: Track 1 Closure Guardrails ===" in ci_text

    assert 'check_replay_proof_schema_parity.sh' in release_text
    assert "=== Release Gate Step -1: Replay-Proof Schema Parity ===" in release_text
    assert 'check_track1_closure_guardrails.sh' in release_text
    assert "=== Release Gate Step 0: Track 1 Closure Guardrails ===" in release_text


def test_schema_parity_gate_dry_run_lists_deterministic_commands() -> None:
    result = _run_schema_parity_gate(["--dry-run"])
    assert result.returncode == 0
    assert "Dry run: replay-proof schema parity preflight commands" in result.stdout
    assert "python3 -m pytest tests/test_replay_proof_schema_parity.py -q" in result.stdout


def test_schema_parity_gate_unknown_argument_fails_with_code_2() -> None:
    result = _run_schema_parity_gate(["--bad-arg"])
    assert result.returncode == 2
    assert "Unknown argument: --bad-arg" in result.stderr


def test_ci_gate_dry_run_lists_deterministic_command_plan() -> None:
    result = _run_ci_gate(["--dry-run"])
    assert result.returncode == 0
    assert "Dry run: replay-proof ci-gate command plan" in result.stdout
    assert "check_replay_proof_schema_parity.sh" in result.stdout
    assert "check_track1_closure_guardrails.sh" in result.stdout
    assert "ilc_core.cli.canon_cluster_a_replay_proof ci-gate" in result.stdout
    assert "Dry run complete: no commands executed" in result.stdout


def test_ci_gate_unknown_argument_fails_with_code_2() -> None:
    result = _run_ci_gate(["--bad-arg"])
    assert result.returncode == 2
    assert "Unknown argument: --bad-arg" in result.stderr


def test_ci_gate_missing_baseline_argument_fails_with_code_2() -> None:
    result = _run_ci_gate(["--baseline"])
    assert result.returncode == 2
    assert "Missing value for --baseline" in result.stderr


def test_ci_gate_dry_run_no_enforce_reflected() -> None:
    result = _run_ci_gate(["--dry-run", "--no-enforce"])
    assert result.returncode == 0
    assert "Enforce:  false" in result.stdout


def test_ci_gate_help_contract() -> None:
    result = _run_ci_gate(["--help"])
    assert result.returncode == 0
    assert "Usage: check_cluster_a_replay_proof_ci_gate.sh" in result.stdout
    assert "--baseline <path>" in result.stdout
    assert "--no-enforce" in result.stdout
    assert "--dry-run" in result.stdout


def test_ci_gate_short_help_contract() -> None:
    result = _run_ci_gate(["-h"])
    assert result.returncode == 0
    assert "Usage: check_cluster_a_replay_proof_ci_gate.sh" in result.stdout


def test_release_gate_dry_run_lists_deterministic_commands() -> None:
    result = _run_release_gate(["--dry-run"])
    assert result.returncode == 0
    assert "Dry run: replay-proof release gate command plan" in result.stdout
    assert "check_replay_proof_schema_parity.sh" in result.stdout
    assert "check_track1_closure_guardrails.sh" in result.stdout
    assert "ilc_core.cli.canon_cluster_a_replay_proof ci-gate" in result.stdout
    assert "ilc_core.cli.canon_cluster_a_replay_proof verify-and-compare" in result.stdout
    assert "Dry run complete: no commands executed" in result.stdout


def test_release_gate_unknown_argument_fails_with_code_2() -> None:
    result = _run_release_gate(["--bad-arg"])
    assert result.returncode == 2
    assert "Unknown argument: --bad-arg" in result.stderr


def test_release_gate_dry_run_no_enforce_reflected() -> None:
    result = _run_release_gate(["--dry-run", "--no-enforce"])
    assert result.returncode == 0
    assert "Enforce:  false" in result.stdout


def test_release_gate_help_contract() -> None:
    result = _run_release_gate(["--help"])
    assert result.returncode == 0
    assert "Usage: check_cluster_a_replay_proof_release_gate.sh" in result.stdout
    assert "--no-enforce" in result.stdout
    assert "--dry-run" in result.stdout
