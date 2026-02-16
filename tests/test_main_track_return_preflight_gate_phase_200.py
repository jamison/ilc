from __future__ import annotations

from pathlib import Path
import subprocess


GATE_SCRIPT = Path("tools/check_main_track_return_preflight_193_199.sh")


def _run_gate(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["bash", str(GATE_SCRIPT), *args],
        capture_output=True,
        text=True,
        check=False,
    )


def test_phase_200_gate_dry_run_contract() -> None:
    result = _run_gate(["--dry-run"])
    assert result.returncode == 0
    assert "Dry run: main-track return preflight (phases 193-199) commands" in result.stdout
    assert "tests/test_commit_epoch_emission_phase_193.py" in result.stdout
    assert "tests/test_server_instance_isolation_phase_199.py" in result.stdout


def test_phase_200_gate_unknown_argument_contract() -> None:
    result = _run_gate(["--bad-arg"])
    assert result.returncode == 2
    assert "Unknown argument: --bad-arg" in result.stderr


def test_phase_200_gate_help_contract() -> None:
    result = _run_gate(["--help"])
    assert result.returncode == 0
    assert "Usage: check_main_track_return_preflight_193_199.sh" in result.stdout
    assert "--dry-run" in result.stdout


def test_phase_200_gate_runs_successfully() -> None:
    result = _run_gate([])
    assert result.returncode == 0
    assert "=== Main-Track Return Preflight Gate (193-199) ===" in result.stdout
    assert "Main-track return preflight gate: PASS" in result.stdout
