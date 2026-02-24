from __future__ import annotations

import subprocess
from pathlib import Path


SCRIPT_PATH = Path("tools/check_cdl_ratification_verification_gate_phase_279.sh")
PARSER_SCRIPT_PATH = Path("tools/check_cdl_ratified_state_phase_279.py")
HANDOFF_PATH = Path("docs/specs/ilc_cdl_ratification_window_270_279_handoff_v0.1.md")

EXPECTED_COMMANDS = [
    "bash tools/check_cdl_ratification_verification_gate_phase_269.sh",
    "python3 tools/check_cdl_ratified_state_phase_279.py",
    "python3 -m pytest tests/test_cdl_029_ratification_272.py -q",
    "python3 -m pytest tests/test_cdl_026_ratification_273.py -q",
    "python3 -m pytest tests/test_cdl_028_ratification_274.py -q",
    "python3 -m pytest tests/test_cdl_027_ratification_276.py -q",
    "python3 -m pytest tests/test_cdl_030_ratification_277.py -q",
]


def _run_script(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["bash", str(SCRIPT_PATH), *args],
        capture_output=True,
        text=True,
        check=False,
    )


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_gate_script_exists() -> None:
    assert SCRIPT_PATH.exists()


def test_parser_script_exists_and_exits_zero() -> None:
    assert PARSER_SCRIPT_PATH.exists()
    result = subprocess.run(
        ["python3", str(PARSER_SCRIPT_PATH)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_dry_run_exits_zero_and_lists_all_commands_in_order() -> None:
    result = _run_script("--dry-run")
    assert result.returncode == 0
    output = result.stdout + result.stderr

    start_at = 0
    for cmd in EXPECTED_COMMANDS:
        idx = output.find(cmd, start_at)
        assert idx >= 0, f"missing command in dry-run output: {cmd}"
        start_at = idx + len(cmd)


def test_help_exits_zero_and_contains_usage() -> None:
    result = _run_script("--help")
    assert result.returncode == 0
    output = (result.stdout + result.stderr).lower()
    assert "usage" in output


def test_unknown_arg_exits_two() -> None:
    result = _run_script("--unknown-arg")
    assert result.returncode == 2


def test_handoff_exists() -> None:
    assert HANDOFF_PATH.exists()


def test_handoff_states_window_ratifications_with_phase_anchors() -> None:
    text = _read(HANDOFF_PATH)
    assert "CDL-029" in text and "ratified_phase: 272" in text
    assert "CDL-026" in text and "ratified_phase: 273" in text
    assert "CDL-028" in text and "ratified_phase: 274" in text
    assert "CDL-027" in text and "ratified_phase: 276" in text
    assert "CDL-030" in text and "ratified_phase: 277" in text


def test_handoff_states_cdl_031_open_and_deferred() -> None:
    text = _read(HANDOFF_PATH)
    assert "CDL-031" in text
    assert "open" in text
    assert "deferred" in text
    assert "unratified" in text


def test_handoff_includes_boundary_statement() -> None:
    text = _read(HANDOFF_PATH)
    assert "does not mutate any decision-log row" in text
    assert "does not modify runtime behavior in `ilc_core/`" in text
