from __future__ import annotations

from pathlib import Path
import subprocess


GATE_SCRIPT = Path("tools/check_refutation_profitability_invariant_phase_212.sh")


def _run_gate(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["bash", str(GATE_SCRIPT), *args],
        capture_output=True,
        text=True,
        check=False,
    )


def test_phase_212_invariant_gate_dry_run_contract() -> None:
    result = _run_gate(["--dry-run"])
    assert result.returncode == 0
    assert "Dry run: refutation-profitability invariant gate commands" in result.stdout
    assert "tests/test_refutation_profitability_invariant_phase_212.py" in result.stdout
    assert "tests/test_devnet_multi_epoch.py" in result.stdout


def test_phase_212_invariant_gate_unknown_argument_contract() -> None:
    result = _run_gate(["--bad-arg"])
    assert result.returncode == 2
    assert "Unknown argument: --bad-arg" in result.stderr


def test_phase_212_invariant_gate_help_contract() -> None:
    result = _run_gate(["--help"])
    assert result.returncode == 0
    assert "Usage: check_refutation_profitability_invariant_phase_212.sh" in result.stdout
    assert "--dry-run" in result.stdout


def test_phase_212_invariant_gate_runs_successfully() -> None:
    result = _run_gate([])
    assert result.returncode == 0
    assert "=== Refutation-Profitability Invariant Gate (Phase 212) ===" in result.stdout
    assert "Refutation-profitability invariant gate: PASS" in result.stdout

