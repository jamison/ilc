from __future__ import annotations

import subprocess
from pathlib import Path


SCRIPT_PATH = Path("tools/check_security_runtime_window_closure_240_248_phase_249.sh")
HANDOFF_PATH = Path("docs/specs/ilc_security_runtime_window_240_248_handoff_v0.1.md")


def _run_script(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["bash", str(SCRIPT_PATH), *args],
        capture_output=True,
        text=True,
        check=False,
    )


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_phase_249_closure_script_exists() -> None:
    assert SCRIPT_PATH.exists()


def test_phase_249_dry_run_exits_zero_and_mentions_phase_244_gate_and_phase_248_tests() -> None:
    result = _run_script("--dry-run")
    assert result.returncode == 0
    output = result.stdout + result.stderr
    assert "run_phase_244_security_runtime_gate.py" in output
    assert "test_integration_coherence_248.py" in output


def test_phase_249_help_exits_zero_and_contains_usage() -> None:
    result = _run_script("--help")
    assert result.returncode == 0
    output = (result.stdout + result.stderr).lower()
    assert "usage" in output


def test_phase_249_unknown_arg_exits_two() -> None:
    result = _run_script("--unknown-arg")
    assert result.returncode == 2


def test_phase_249_handoff_file_exists() -> None:
    assert HANDOFF_PATH.exists()


def test_phase_249_handoff_section_2_mentions_cdl_001_002_007() -> None:
    text = _read(HANDOFF_PATH)
    assert "CDL-001" in text
    assert "CDL-002" in text
    assert "CDL-007" in text


def test_phase_249_handoff_section_3_mentions_cdl_025_and_cdl_032() -> None:
    text = _read(HANDOFF_PATH)
    assert "CDL-025" in text
    assert "CDL-032" in text


def test_phase_249_handoff_section_4_mentions_d2e_03_and_d2_01() -> None:
    text = _read(HANDOFF_PATH)
    assert "D2e-03" in text
    assert "D2-01" in text
