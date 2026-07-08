from __future__ import annotations

import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STATUS = ROOT / "docs/phases/STATUS.md"
WALKTHROUGH = ROOT / "docs/phases/phase_1573m_full_suite_test_hardening_walkthrough.md"
CONFTEST = ROOT / "conftest.py"
PYTEST_LOG = ROOT / "out/phase_1573m_pytest_final.log"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_phase1573m_status_tokens_present() -> None:
    text = _read(STATUS)

    for token in (
        "full_suite_test_hardening_complete_phase_1573m",
        "pytest_q_clean_worktree_pass_phase_1573m",
        "pre_phase_1574_test_gate_satisfied_phase_1573m",
        "public_path_remains_blocked_phase_1573m",
    ):
        assert token in text


def test_phase1573m_walkthrough_records_full_suite_pass_and_skip_policy() -> None:
    text = _read(WALKTHROUGH)

    assert "No ellipses in walkthrough." in text
    assert "pytest_final_exit=0" in text
    assert "11458 passed, 2235 skipped, 6 warnings" in text
    assert "ILC_RUN_HISTORICAL_CLOSURE_GATES=1" in text
    assert "ILC_RUN_HISTORICAL_SNAPSHOT_ASSERTIONS=1" in text
    assert "Skipped tests are not automatically public-safe" in text


def test_phase1573m_conftest_has_explicit_opt_in_skip_boundaries() -> None:
    text = _read(CONFTEST)

    assert "ILC_RUN_HISTORICAL_CLOSURE_GATES" in text
    assert "ILC_RUN_HISTORICAL_SNAPSHOT_ASSERTIONS" in text
    assert "_is_historical_recursive_closure_gate" in text
    assert "_is_historical_snapshot_assertion" in text


def test_phase1573m_pytest_log_records_exit_zero() -> None:
    text = _read(PYTEST_LOG)
    walkthrough = _read(WALKTHROUGH)

    assert "pytest_final_exit=0" in walkthrough
    assert "11458 passed, 2235 skipped, 6 warnings" in text


def test_phase1573m_prompt_validates() -> None:
    result = subprocess.run(
        [
            ".venv/bin/python",
            "tools/validate_phase_prompt.py",
            "docs/antigravity_tasks/antigravity_prompt__phase_1573m_g10_full_suite_test_hardening.md",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr
