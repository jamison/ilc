from __future__ import annotations

from pathlib import Path
import subprocess


CLOSURE_GATE_SCRIPT = Path("tools/check_domain_exception_migration_closure.sh")


def _run_closure_gate(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["bash", str(CLOSURE_GATE_SCRIPT), *args],
        capture_output=True,
        text=True,
        check=False,
    )


def test_domain_exception_closure_gate_dry_run_contract() -> None:
    result = _run_closure_gate(["--dry-run"])
    assert result.returncode == 0
    assert "Dry run: domain exception migration closure gate commands" in result.stdout
    assert (
        "python3 -m pytest tests/test_domain_exception_migration_guardrail.py "
        "tests/test_domain_exception_migration_guardrail_gate.py "
        "tests/test_track1_closure_guardrail_gate_ops.py "
        "tests/test_ci_workflow_regression_gate.py -q"
    ) in result.stdout


def test_domain_exception_closure_gate_unknown_argument_exit_code() -> None:
    result = _run_closure_gate(["--bad-arg"])
    assert result.returncode == 2
    assert "Unknown argument: --bad-arg" in result.stderr


def test_domain_exception_closure_gate_help_contract() -> None:
    result = _run_closure_gate(["--help"])
    assert result.returncode == 0
    assert "Usage: check_domain_exception_migration_closure.sh" in result.stdout
    assert "--dry-run" in result.stdout


def test_domain_exception_closure_gate_runs_successfully() -> None:
    result = _run_closure_gate([])
    assert result.returncode == 0
    assert "=== Domain Exception Migration Closure Gate ===" in result.stdout
    assert "Domain exception migration closure gate: PASS" in result.stdout
