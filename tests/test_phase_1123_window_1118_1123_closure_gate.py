from __future__ import annotations

import os
import pathlib
import re
import subprocess
import sys
from decimal import Decimal

from ilc_core.types import PROVENANCE_DECAY_ALPHA


SELFTEST_MODE = os.environ.get("ILC_PHASE_1123_GATE_SELFTEST") == "1"

ROOT = pathlib.Path(__file__).resolve().parents[1]


def _read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_cat0_selftest_env_recognized() -> None:
    assert isinstance(SELFTEST_MODE, bool)


def test_cat1_sequence_lock_exists() -> None:
    assert (ROOT / "docs/specs/ilc_phase_1118_1123_sequence_lock_v0.1.md").exists()


def test_cat1_sequence_lock_contains_window_token() -> None:
    src = _read("docs/specs/ilc_phase_1118_1123_sequence_lock_v0.1.md")
    assert "window_1118_1123_sequence_lock_committed_phase_1118" in src


def test_cat1_sequence_lock_contains_float_kill_unblock_token() -> None:
    src = _read("docs/specs/ilc_phase_1118_1123_sequence_lock_v0.1.md")
    assert "float_kill_01_commits_1_2_unblock_sim_provenance_01_commissioning" in src


def test_cat1_sequence_lock_contains_provenance_alpha_provisional_token() -> None:
    src = _read("docs/specs/ilc_phase_1118_1123_sequence_lock_v0.1.md")
    assert "sim_provenance_01_alpha_remains_provisional_until_execution" in src


def test_cat2_phase_1119_walkthrough_exists_with_window_anchor() -> None:
    src = _read("docs/phases/phase_1119_float_kill_01_ilc_core_float_prng_hardening_walkthrough.md")
    assert "Window: 1118-1123" in src


def test_cat2_prng_grep_has_no_forbidden_active_runtime_imports() -> None:
    result = subprocess.run(
        [
            "grep",
            "-r",
            "import random",
            "ilc_core/",
            "--include=*.py",
            "--exclude-dir=sim",
            "--exclude-dir=analysis",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    lines = [
        line
        for line in result.stdout.splitlines()
        if "devnet" not in line and "benchmark" not in line
    ]
    assert lines == [], f"Forbidden random imports found: {lines}"


def test_cat2_sensitive_runtime_taboos_test_passes() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "tests/test_sensitive_runtime_coding_taboos.py",
            "-q",
            "--tb=short",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "1 passed" in result.stdout + result.stderr


def test_cat2_provenance_decay_alpha_is_decimal_0_5() -> None:
    assert isinstance(PROVENANCE_DECAY_ALPHA, Decimal)
    assert not isinstance(PROVENANCE_DECAY_ALPHA, float)
    assert PROVENANCE_DECAY_ALPHA == Decimal("0.5")


def test_cat2_float_kill_02_not_triggered() -> None:
    src = _read("docs/phases/phase_1119_float_kill_01_ilc_core_float_prng_hardening_walkthrough.md")
    assert "FLOAT-KILL-02 was not triggered" in src


def test_cat3_sim_program_exists_with_q8_token() -> None:
    src = _read("docs/sims/sim_provenance_01/program.md")
    assert "q8_epoch_mint_source_sim_provenance_01_required" in src


def test_cat3_sim_harness_exists_with_alpha_parameter() -> None:
    src = _read("tools/sim_provenance_01.py")
    assert "ALPHA = Decimal(\"0.5\")" in src
    assert "ALPHA_SWEEP" in src


def test_cat3_run_01_results_exist_with_token() -> None:
    src = _read("docs/sims/sim_provenance_01/results_phase_1120_run_01.md")
    assert "sim_provenance_01_run_01_complete_phase_1120" in src


def test_cat3_phase_1120_evidence_suite_passes() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "tests/test_phase_1120_sim_provenance_01_commissioning.py",
            "-q",
            "--tb=short",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "22 passed" in result.stdout + result.stderr


def test_cat4_run_02_results_exist_with_token() -> None:
    src = _read("docs/sims/sim_provenance_01/results_phase_1121_run_02.md")
    assert "sim_provenance_01_run_02_complete_phase_1121" in src


def test_cat4_alpha_disposition_exists_with_q2_token() -> None:
    src = _read("docs/sims/sim_provenance_01/alpha_disposition_phase_1121.md")
    assert "q2_geometric_decay_alpha_decimal_0_5_provisional" in src


def test_cat4_alpha_disposition_contains_q8_token() -> None:
    src = _read("docs/sims/sim_provenance_01/alpha_disposition_phase_1121.md")
    assert "q8_epoch_mint_source_sim_provenance_01_required" in src


def test_cat4_alpha_disposition_recommends_0_45_and_keeps_runtime_provisional() -> None:
    src = _read("docs/sims/sim_provenance_01/alpha_disposition_phase_1121.md")
    assert "Recommended alpha: `0.45`" in src
    assert "PROVENANCE_DECAY_ALPHA remains Decimal(\"0.50\") in ilc_core/types.py" in src


def test_cat4_alpha_recommendation_is_in_0_40_to_0_50_range() -> None:
    src = _read("docs/sims/sim_provenance_01/alpha_disposition_phase_1121.md")
    match = re.search(r"Recommended alpha: `(?P<alpha>0\.[0-9]+)`", src)
    assert match is not None
    alpha = Decimal(match.group("alpha"))
    assert Decimal("0.40") <= alpha <= Decimal("0.50")
    assert PROVENANCE_DECAY_ALPHA == Decimal("0.5")


def test_cat5_coherence_report_exists_with_pass_verdict() -> None:
    src = _read("docs/specs/ilc_integration_coherence_report_1122_v0.1.md")
    assert "coherence_report_1122_verdict=pass" in src


def test_cat5_capsule_v5_36_exists_with_supersession_token() -> None:
    src = _read("docs/specs/ilc_antigravity_context_capsule_v5.36.md")
    assert "capsule_v5_36_supersedes_v5_35" in src


def test_cat5_capsule_records_float_kill_complete() -> None:
    src = _read("docs/specs/ilc_antigravity_context_capsule_v5.36.md")
    assert "float_kill_01_complete_phase_1119" in src


def test_cat5_capsule_records_sim_provenance_complete() -> None:
    src = _read("docs/specs/ilc_antigravity_context_capsule_v5.36.md")
    assert "sim_provenance_01_complete_phase_1120_1121" in src


def test_cat5_capsule_records_q8_satisfied() -> None:
    src = _read("docs/specs/ilc_antigravity_context_capsule_v5.36.md")
    assert "q8_satisfied_sim_provenance_01_complete" in src


def test_cat5_capsule_records_q2_active_alpha_amendment_pending() -> None:
    src = _read("docs/specs/ilc_antigravity_context_capsule_v5.36.md")
    assert "q2_active_cdl_amendment_pending_alpha_0_45" in src
