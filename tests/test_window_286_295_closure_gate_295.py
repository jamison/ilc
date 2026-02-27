"""Contract checks for Phase 295 closure gate and handoff."""

from __future__ import annotations

import subprocess
from pathlib import Path

SCRIPT_PATH = Path("tools/check_window_286_295_closure_gate_phase_295.sh")
HANDOFF_PATH = Path("docs/specs/ilc_window_286_295_handoff_295_v0.1.md")


def test_gate_script_exists() -> None:
    assert SCRIPT_PATH.exists()


def test_dry_run_includes_exact_commands_in_order() -> None:
    result = subprocess.run(
        ["bash", str(SCRIPT_PATH), "--dry-run"],
        check=True,
        capture_output=True,
        text=True,
    )
    lines = [line.strip() for line in result.stdout.splitlines() if line.strip().startswith("[")]
    assert lines == [
        "[1/5] bash tools/check_cdl_031_ratification_verification_gate_phase_289.sh",
        "[2/5] python3 -m pytest tests/test_cdl_033_ratification_291.py -q",
        "[3/5] python3 -m pytest tests/test_adm_003_reference_agent_architecture_292.py -q",
        "[4/5] python3 -m pytest tests/test_d2e_04_identity_subsystem_contract_293.py -q",
        "[5/5] python3 -m pytest tests/test_d2e_04_identity_subsystem_294.py -q",
    ]


def test_help_and_unknown_arg_contract() -> None:
    help_res = subprocess.run(["bash", str(SCRIPT_PATH), "--help"], capture_output=True, text=True)
    assert help_res.returncode == 0
    assert "usage:" in help_res.stdout

    bad_res = subprocess.run(["bash", str(SCRIPT_PATH), "--bad"], capture_output=True, text=True)
    assert bad_res.returncode == 2


def test_handoff_exists_with_required_sections() -> None:
    assert HANDOFF_PATH.exists()
    text = HANDOFF_PATH.read_text(encoding="utf-8")
    for heading in (
        "## 1. Window summary (286-295)",
        "## 2. Verified ratification state (`CDL-031`, `CDL-033`)",
        "## 3. Hard prerequisites for phase 296+",
        "## 4. D2e and architecture carry-forward state",
        "## 5. Non-goals and boundary statement",
        "## 6. Canonical anchors and next-sequence pointer",
    ):
        assert heading in text


def test_handoff_records_ratified_state_and_boundaries() -> None:
    text = HANDOFF_PATH.read_text(encoding="utf-8").lower()
    assert "cdl-031" in text and "ratified" in text
    assert "cdl-033" in text and "ratified" in text
    assert "no new decision-log mutation" in text
    assert "no new runtime implementation changes" in text
