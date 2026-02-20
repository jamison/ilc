from __future__ import annotations

import subprocess
import sys
from pathlib import Path


SCRIPT_PATH = Path("tools/run_phase_236_preflight.py")


def _run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT_PATH), *args],
        capture_output=True,
        text=True,
        check=False,
    )


def test_phase_236_preflight_script_exists() -> None:
    assert SCRIPT_PATH.exists()


def test_phase_236_preflight_dry_run_contract() -> None:
    result = _run("--dry-run")
    assert result.returncode == 0
    out = result.stdout + result.stderr

    assert "test_sdk_boundary_contract_234.py" in out
    assert "test_bootstrap_operations_runbook_235.py" in out
    assert "test_issuance_governance_plan_233.py" in out
    assert "test_no_ellipses_in_walkthroughs.py" in out
    assert "test_reproducible_build_phase_230.py" in out


def test_phase_236_preflight_help_contract() -> None:
    result = _run("--help")
    assert result.returncode == 0
    out = result.stdout + result.stderr
    assert "usage" in out.lower()


def test_phase_236_preflight_unknown_arg_contract() -> None:
    result = _run("--bogus")
    assert result.returncode == 2
