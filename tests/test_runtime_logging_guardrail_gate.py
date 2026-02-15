from __future__ import annotations

from pathlib import Path
import subprocess


GUARDRAIL_GATE_SCRIPT = Path("tools/check_runtime_logging_guardrails.sh")


def _run_guardrail_gate(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["bash", str(GUARDRAIL_GATE_SCRIPT), *args],
        capture_output=True,
        text=True,
        check=False,
    )


def test_runtime_logging_guardrail_gate_dry_run_contract() -> None:
    result = _run_guardrail_gate(["--dry-run"])
    assert result.returncode == 0
    assert "Dry run: runtime logging guardrail gate commands" in result.stdout
    assert (
        "python3 -m pytest tests/test_runtime_logging_contracts.py "
        "tests/test_logging_entry_surface_contracts.py -q"
    ) in result.stdout


def test_runtime_logging_guardrail_gate_unknown_argument_exit_code() -> None:
    result = _run_guardrail_gate(["--bad-arg"])
    assert result.returncode == 2
    assert "Unknown argument: --bad-arg" in result.stderr


def test_runtime_logging_guardrail_gate_help_contract() -> None:
    result = _run_guardrail_gate(["--help"])
    assert result.returncode == 0
    assert "Usage: check_runtime_logging_guardrails.sh" in result.stdout
    assert "--dry-run" in result.stdout


def test_runtime_logging_guardrail_gate_runs_successfully() -> None:
    result = _run_guardrail_gate([])
    assert result.returncode == 0
    assert "=== Runtime Logging Guardrail Gate ===" in result.stdout
    assert "Runtime logging guardrail gate: PASS" in result.stdout
