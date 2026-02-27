"""Contract checks for Phase 289 CDL-031 verification gate and handoff."""

from __future__ import annotations

import subprocess
from pathlib import Path

SCRIPT_PATH = Path("tools/check_cdl_031_ratification_verification_gate_phase_289.sh")
HANDOFF_PATH = Path("docs/specs/ilc_cdl_031_ratification_handoff_289_v0.1.md")


def test_gate_script_exists() -> None:
    assert SCRIPT_PATH.exists()


def test_dry_run_lists_exact_commands_in_order() -> None:
    result = subprocess.run(
        ["bash", str(SCRIPT_PATH), "--dry-run"],
        check=True,
        capture_output=True,
        text=True,
    )
    lines = [line.strip() for line in result.stdout.splitlines() if line.strip().startswith("[")]
    assert lines == [
        "[1/4] bash tools/check_cdl_ratification_verification_gate_phase_279.sh",
        "[2/4] python3 -m pytest tests/test_cdl_031_ratification_288.py -q",
        "[3/4] python3 -m pytest tests/test_ratification_mutation_scope_261.py -q",
        "[4/4] python3 -m pytest tests/test_crypto_migration_initial_tranche_283.py -q",
    ]


def test_help_exits_zero_with_usage() -> None:
    result = subprocess.run(
        ["bash", str(SCRIPT_PATH), "--help"],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "usage:" in result.stdout


def test_unknown_arg_exits_two() -> None:
    result = subprocess.run(
        ["bash", str(SCRIPT_PATH), "--bogus"],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 2


def test_handoff_exists_and_states_phase_288_ratified() -> None:
    assert HANDOFF_PATH.exists()
    text = HANDOFF_PATH.read_text(encoding="utf-8")
    assert "CDL-031" in text
    assert "ratified" in text
    assert "`288`" in text


def test_handoff_includes_boundary_statement() -> None:
    text = HANDOFF_PATH.read_text(encoding="utf-8").lower()
    assert "does not" in text
    assert "mutate decision-log rows" in text
    assert "modify runtime files" in text
