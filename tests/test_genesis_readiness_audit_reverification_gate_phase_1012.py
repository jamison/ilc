from __future__ import annotations

from pathlib import Path
import subprocess


REVERIFY_GATE_SCRIPT = Path("tools/check_genesis_readiness_audit_reverification_1012.sh")


def _run_gate(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["bash", str(REVERIFY_GATE_SCRIPT), *args],
        capture_output=True,
        text=True,
        check=False,
    )


def test_phase_1012_reverify_gate_dry_run_contract() -> None:
    result = _run_gate(["--dry-run"])
    assert result.returncode == 0
    assert "Dry run: genesis readiness audit reverification gate (post-1011) commands" in result.stdout
    assert "tests/test_getting_started_docs_phase_1010.py" in result.stdout
    assert "tests/test_broad_exception_boundary_policy_phase_1011.py" in result.stdout


def test_phase_1012_reverify_gate_unknown_argument_contract() -> None:
    result = _run_gate(["--bad-arg"])
    assert result.returncode == 2
    assert "Unknown argument: --bad-arg" in result.stderr


def test_phase_1012_reverify_gate_help_contract() -> None:
    result = _run_gate(["--help"])
    assert result.returncode == 0
    assert "Usage: check_genesis_readiness_audit_reverification_1012.sh" in result.stdout
    assert "--dry-run" in result.stdout


def test_phase_1012_reverify_gate_runs_successfully() -> None:
    result = _run_gate([])
    assert result.returncode == 0
    assert "=== Genesis Readiness Audit Reverification Gate (post-1011) ===" in result.stdout
    assert "Genesis readiness audit reverification gate: PASS" in result.stdout
