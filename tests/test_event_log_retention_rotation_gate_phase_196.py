from __future__ import annotations

from pathlib import Path
import subprocess


GATE_SCRIPT = Path("tools/check_event_log_retention_rotation.sh")


def _run_gate(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["bash", str(GATE_SCRIPT), *args],
        capture_output=True,
        text=True,
        check=False,
    )


def test_phase_196_gate_dry_run_contract() -> None:
    result = _run_gate(["--dry-run"])
    assert result.returncode == 0
    assert "Dry run: event-log retention/rotation gate commands" in result.stdout
    assert "python3 -m pytest tests/test_event_log_retention_rotation_phase_196.py -q" in result.stdout


def test_phase_196_gate_unknown_argument_contract() -> None:
    result = _run_gate(["--bad-arg"])
    assert result.returncode == 2
    assert "Unknown argument: --bad-arg" in result.stderr


def test_phase_196_gate_help_contract() -> None:
    result = _run_gate(["--help"])
    assert result.returncode == 0
    assert "Usage: check_event_log_retention_rotation.sh" in result.stdout
    assert "--dry-run" in result.stdout


def test_phase_196_gate_runs_successfully() -> None:
    result = _run_gate([])
    assert result.returncode == 0
    assert "=== Event Log Retention and Rotation Gate ===" in result.stdout
    assert "Event log retention and rotation gate: PASS" in result.stdout
