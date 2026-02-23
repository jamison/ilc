from __future__ import annotations

import subprocess
from pathlib import Path


SCRIPT_PATH = Path("tools/check_cdl_ratification_verification_gate_phase_269.sh")
HANDOFF_PATH = Path("docs/specs/ilc_cdl_ratification_window_260_269_handoff_v0.1.md")

EXPECTED_COMMANDS = [
    "python3 -m pytest tests/test_cdl_025_ratification_267.py -q",
    "python3 -m pytest tests/test_cdl_019_ratification_268.py -q",
    "python3 -m pytest tests/test_ratification_mutation_scope_261.py -q",
    "python3 -m pytest tests/test_cdl_032_ratification_253.py tests/test_security_cdl_ratification_251.py -q",
    "bash tools/check_d2e_03_prototype_closure_phase_265.sh",
    "bash tools/check_refutation_profitability_invariant_phase_212.sh",
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


def test_dry_run_exits_zero_and_lists_all_commands() -> None:
    result = _run_script("--dry-run")
    assert result.returncode == 0
    output = result.stdout + result.stderr
    for cmd in EXPECTED_COMMANDS:
        assert cmd in output


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


def test_handoff_states_cdl_025_and_cdl_019_are_ratified() -> None:
    text = _read(HANDOFF_PATH)
    assert "CDL-025" in text
    assert "CDL-019" in text
    assert "ratified" in text
    assert "ilc_cdl_025_terminal_issuance_model_ratification_evidence_267_v0.1.md" in text
    assert "ilc_cdl_019_multiplier_governance_surface_ratification_evidence_268_v0.1.md" in text


def test_handoff_states_cdl_031_unblocked_and_still_open() -> None:
    text = _read(HANDOFF_PATH)
    assert "CDL-031" in text
    assert "unblocked" in text
    assert "open" in text
    assert "unratified" in text


def test_handoff_includes_no_runtime_change_boundary_statement() -> None:
    text = _read(HANDOFF_PATH)
    assert "does not" in text
    assert "modify runtime behavior in `ilc_core/`" in text
