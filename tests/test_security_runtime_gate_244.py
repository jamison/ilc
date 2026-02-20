from __future__ import annotations

from pathlib import Path
import subprocess
import sys


GATE_SCRIPT = Path("tools/run_phase_244_security_runtime_gate.py")


def _run_gate(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(GATE_SCRIPT), *args],
        capture_output=True,
        text=True,
        check=False,
        timeout=1200,
    )


def test_phase_244_gate_script_exists() -> None:
    assert GATE_SCRIPT.exists()


def test_phase_244_gate_dry_run_contract() -> None:
    result = _run_gate(["--dry-run"])
    assert result.returncode == 0
    assert "Phase 244 security runtime gate dry-run:" in result.stdout

    expected_tokens = [
        "tests/test_lineage_event_schema_phase_240.py",
        "tests/test_security_runtime_sequence_240.py",
        "tests/test_cdl_001_signer_lineage_runtime.py",
        "tests/test_cdl_002_key_compromise_runtime.py",
        "tests/test_cdl_007_rollback_resistance_runtime.py",
        "tests/test_security_runtime_cross_cdl_interactions_244.py",
        "tools/run_phase_236_preflight.py",
    ]
    for token in expected_tokens:
        assert token in result.stdout


def test_phase_244_gate_help_contract() -> None:
    result = _run_gate(["--help"])
    assert result.returncode == 0
    assert "usage" in result.stdout.lower()


def test_phase_244_gate_unknown_argument_contract() -> None:
    result = _run_gate(["--bad-arg"])
    assert result.returncode == 2
    assert "Unknown argument(s): --bad-arg" in result.stderr
