from __future__ import annotations

from pathlib import Path
import subprocess


CLOSURE_GATE_SCRIPT = Path("tools/check_main_track_return_closure_202_210.sh")


def _run_gate(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["bash", str(CLOSURE_GATE_SCRIPT), *args],
        capture_output=True,
        text=True,
        check=False,
    )


def test_phase_211_closure_gate_dry_run_contract() -> None:
    result = _run_gate(["--dry-run"])
    assert result.returncode == 0
    assert "Dry run: main-track return closure gate (202-210) commands" in result.stdout
    assert "tests/test_main_track_return_sequence_phase_202.py" in result.stdout
    assert "tests/test_main_track_return_preflight_gate_phase_210.py" in result.stdout


def test_phase_211_closure_gate_unknown_argument_contract() -> None:
    result = _run_gate(["--bad-arg"])
    assert result.returncode == 2
    assert "Unknown argument: --bad-arg" in result.stderr


def test_phase_211_closure_gate_help_contract() -> None:
    result = _run_gate(["--help"])
    assert result.returncode == 0
    assert "Usage: check_main_track_return_closure_202_210.sh" in result.stdout
    assert "--dry-run" in result.stdout


def test_phase_211_closure_gate_runs_successfully() -> None:
    result = _run_gate([])
    assert result.returncode == 0
    assert "=== Main-Track Return Closure Gate (202-210) ===" in result.stdout
    assert "Main-track return closure gate: PASS" in result.stdout
