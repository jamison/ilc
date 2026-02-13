from pathlib import Path
import subprocess


GUARDRAIL_GATE_SCRIPT = Path("tools/check_track1_closure_guardrails.sh")
CI_GATE_SCRIPT = Path("tools/check_cluster_a_replay_proof_ci_gate.sh")
RELEASE_GATE_SCRIPT = Path("tools/check_cluster_a_replay_proof_release_gate.sh")


def _run_guardrail_gate(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["bash", str(GUARDRAIL_GATE_SCRIPT), *args],
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

    assert 'check_track1_closure_guardrails.sh' in ci_text
    assert "=== CI Gate Step 0: Track 1 Closure Guardrails ===" in ci_text

    assert 'check_track1_closure_guardrails.sh' in release_text
    assert "=== Release Gate Step 0: Track 1 Closure Guardrails ===" in release_text
