from __future__ import annotations

from pathlib import Path
import subprocess


CLOSURE_GATE_SCRIPT = Path("tools/check_genesis_readiness_remediation_closure_996_1008.sh")


def _run_gate(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["bash", str(CLOSURE_GATE_SCRIPT), *args],
        capture_output=True,
        text=True,
        check=False,
    )


def test_phase_1009_closure_gate_dry_run_contract() -> None:
    result = _run_gate(["--dry-run"])
    assert result.returncode == 0
    assert "Dry run: genesis readiness remediation closure gate (996-1008) commands" in result.stdout
    assert "tests/test_license_presence_phase_997.py" in result.stdout
    assert "tests/test_operator_config_docs_phase_1008.py" in result.stdout


def test_phase_1009_closure_gate_unknown_argument_contract() -> None:
    result = _run_gate(["--bad-arg"])
    assert result.returncode == 2
    assert "Unknown argument: --bad-arg" in result.stderr


def test_phase_1009_closure_gate_help_contract() -> None:
    result = _run_gate(["--help"])
    assert result.returncode == 0
    assert "Usage: check_genesis_readiness_remediation_closure_996_1008.sh" in result.stdout
    assert "--dry-run" in result.stdout


def test_phase_1009_closure_gate_runs_successfully() -> None:
    result = _run_gate([])
    assert result.returncode == 0
    assert "=== Genesis Readiness Remediation Closure Gate (996-1008) ===" in result.stdout
    assert "Genesis readiness remediation closure gate: PASS" in result.stdout
