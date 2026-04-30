"""Phase 1101 — Window 945–950, 1100–1101 Closure Gate.

Asserts all seven prior phases completed correctly:
  Phase 945: sequence lock
  Phase 946: H-012 settle() runtime (CDL-081 §§4.1–4.6 partial)
  Phase 947: H-012 ratification evidence tests (31 tests)
  Phase 948: CDL-082 opening
  Phase 949: CDL-082 prelock
  Phase 950: CDL-082 ratification (H013_CHANGE_THRESHOLD = 0.15)
  Phase 1100: coherence report + capsule v5.33

Sensitivity: SENSITIVE — human GO token required for closure verdict.
Selftest guard: ILC_PHASE_1101_GATE_SELFTEST=1 skips full gate (prevents recursion).
"""

import os
import subprocess
from pathlib import Path

import pytest

SELFTEST_MODE = os.environ.get("ILC_PHASE_1101_GATE_SELFTEST") == "1"

# ---------------------------------------------------------------------------
# Category 5 — Selftest Probe (always runs)
# ---------------------------------------------------------------------------


def test_cat5_selftest_env_recognized():
    """Internal probe: selftest guard mechanism is present and functional."""
    assert isinstance(SELFTEST_MODE, bool)


# ---------------------------------------------------------------------------
# Category 1 — Phase 945 Artifacts
# ---------------------------------------------------------------------------


def test_cat1_sequence_lock_exists():
    assert Path("docs/specs/ilc_phase_945_952_sequence_lock_v0.1.md").exists()


@pytest.mark.skipif(SELFTEST_MODE, reason="selftest mode")
def test_cat1_sequence_lock_token():
    content = Path("docs/specs/ilc_phase_945_952_sequence_lock_v0.1.md").read_text()
    assert "window_945_952_sequence_lock_committed_phase_945" in content


@pytest.mark.skipif(SELFTEST_MODE, reason="selftest mode")
def test_cat1_numbering_correction_token():
    """Phantom edit guard: phase numbering correction token must be present."""
    content = Path("docs/specs/ilc_phase_945_952_sequence_lock_v0.1.md").read_text()
    assert "window_945_1101_phase_numbering_corrected_phase_1100" in content


@pytest.mark.skipif(SELFTEST_MODE, reason="selftest mode")
def test_cat1_capsule_v532_exists():
    assert Path("docs/specs/ilc_antigravity_context_capsule_v5.32.md").exists()


@pytest.mark.skipif(SELFTEST_MODE, reason="selftest mode")
def test_cat1_capsule_v532_supersedes_v531():
    content = Path("docs/specs/ilc_antigravity_context_capsule_v5.32.md").read_text()
    assert "capsule_v5_32_supersedes_v5_31" in content


# ---------------------------------------------------------------------------
# Category 2 — Phase 946–947 H-012 Runtime
# ---------------------------------------------------------------------------


@pytest.mark.skipif(SELFTEST_MODE, reason="selftest mode")
def test_cat2_settle_runtime_version():
    from ilc_core.economics.epoch_attribution_settle_runtime import (
        EPOCH_ATTRIBUTION_SETTLE_RUNTIME_VERSION,
    )
    assert EPOCH_ATTRIBUTION_SETTLE_RUNTIME_VERSION == "epoch_attribution_settle_runtime_1129_fix1.v0.5"


@pytest.mark.skipif(SELFTEST_MODE, reason="selftest mode")
def test_cat2_cdl_081_dependency_token():
    from ilc_core.economics.epoch_attribution_settle_runtime import CDL_081_DEPENDENCY
    assert CDL_081_DEPENDENCY == "cdl_081_hyperedge_ecu_attribution_ratified_943.v0.1"


@pytest.mark.skipif(SELFTEST_MODE, reason="selftest mode")
def test_cat2_cdl_hcon_02_dependency_stub_active():
    """CDL_HCON_02_DEPENDENCY must remain as a forward-obligation marker token."""
    from ilc_core.economics.epoch_attribution_settle_runtime import CDL_HCON_02_DEPENDENCY
    assert CDL_HCON_02_DEPENDENCY == "h_con_02_cdl_required_before_ejected_stake_treasury_executes"


@pytest.mark.skipif(SELFTEST_MODE, reason="selftest mode")
def test_cat2_epoch_attribution_batch_version_updated():
    from ilc_core.types import EPOCH_ATTRIBUTION_BATCH_VERSION
    assert EPOCH_ATTRIBUTION_BATCH_VERSION == "epoch_attribution_batch.v0.2"
    assert "stub" not in EPOCH_ATTRIBUTION_BATCH_VERSION


@pytest.mark.skipif(SELFTEST_MODE, reason="selftest mode")
def test_cat2_reuse_attribution_rate_locked():
    from decimal import Decimal
    from ilc_core.types import REUSE_ATTRIBUTION_RATE
    assert REUSE_ATTRIBUTION_RATE == Decimal("0.20")
    assert isinstance(REUSE_ATTRIBUTION_RATE, Decimal)


@pytest.mark.skipif(SELFTEST_MODE, reason="selftest mode")
def test_cat2_cdl_hcon_01_dependency_removed():
    """Phantom edit guard: CDL_HCON_01_DEPENDENCY must be absent from types.py."""
    result = subprocess.run(
        ["grep", "-n", "CDL_HCON_01_DEPENDENCY", "ilc_core/types.py"],
        capture_output=True, text=True,
    )
    assert result.stdout.strip() == "", (
        f"CDL_HCON_01_DEPENDENCY still present in types.py:\n{result.stdout}"
    )


@pytest.mark.skipif(SELFTEST_MODE, reason="selftest mode")
def test_cat2_passive_ecu_rate_is_decimal():
    from decimal import Decimal
    from ilc_core.economics.passive_ecu_attribution_runtime import PASSIVE_ATTRIBUTION_RATE
    assert isinstance(PASSIVE_ATTRIBUTION_RATE, Decimal)
    assert PASSIVE_ATTRIBUTION_RATE == Decimal("0.20")


@pytest.mark.skipif(SELFTEST_MODE, reason="selftest mode")
def test_cat2_h012_evidence_tests_exist():
    assert Path("tests/test_phase_0947_h012_epoch_attribution_settle.py").exists()


@pytest.mark.skipif(SELFTEST_MODE, reason="selftest mode")
def test_cat2_h012_evidence_tests_pass():
    """Run the 31 H-012 evidence tests and assert all pass."""
    result = subprocess.run(
        ["python3", "-m", "pytest",
         "tests/test_phase_0947_h012_epoch_attribution_settle.py",
         "-v", "--tb=short", "-q"],
        capture_output=True, text=True,
    )
    assert result.returncode == 0, (
        f"H-012 evidence tests failed:\n{result.stdout}\n{result.stderr}"
    )
    combined = result.stdout + result.stderr
    assert "31 passed" in combined, (
        f"Expected 31 passed, got:\n{combined}"
    )


# ---------------------------------------------------------------------------
# Category 3 — Phase 948–950 CDL-082
# ---------------------------------------------------------------------------


@pytest.mark.skipif(SELFTEST_MODE, reason="selftest mode")
def test_cat3_cdl_082_spec_exists():
    assert Path(
        "docs/specs/ilc_cdl_082_h013_emission_threshold_amendment_opening_948_v0.1.md"
    ).exists()


@pytest.mark.skipif(SELFTEST_MODE, reason="selftest mode")
def test_cat3_cdl_082_ratified_in_spec():
    content = Path(
        "docs/specs/ilc_cdl_082_h013_emission_threshold_amendment_opening_948_v0.1.md"
    ).read_text()
    assert "**Status:** RATIFIED" in content
    assert "cdl_082_ratified_phase_950" in content


@pytest.mark.skipif(SELFTEST_MODE, reason="selftest mode")
def test_cat3_cdl_082_ratified_in_log():
    content = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md").read_text()
    assert "CDL-082" in content
    for line in content.splitlines():
        if "CDL-082" in line:
            assert "ratified" in line.lower(), f"CDL-082 not ratified in log: {line}"
            break


@pytest.mark.skipif(SELFTEST_MODE, reason="selftest mode")
def test_cat3_h013_change_threshold_updated():
    content = Path("ilc_core/node/node_startup_runtime.py").read_text()
    assert "H013_CHANGE_THRESHOLD: float = 0.15" in content, (
        "H013_CHANGE_THRESHOLD not updated to 0.15 in node_startup_runtime.py"
    )


@pytest.mark.skipif(SELFTEST_MODE, reason="selftest mode")
def test_cat3_cdl_082_was_open_at_phase_948_commit():
    """Historical prelock: CDL-082 was OPEN at the Phase 948 introducing commit."""
    log_result = subprocess.run(
        ["git", "log", "--oneline", "--diff-filter=A", "--",
         "docs/specs/ilc_cdl_082_h013_emission_threshold_amendment_opening_948_v0.1.md"],
        capture_output=True, text=True,
    )
    lines = log_result.stdout.strip().splitlines()
    assert lines, (
        "Cannot find introducing commit for CDL-082 spec — was Phase 948 committed?"
    )
    opening_commit = lines[0].split()[0]
    show_result = subprocess.run(
        ["git", "show",
         f"{opening_commit}:docs/specs/"
         "ilc_cdl_082_h013_emission_threshold_amendment_opening_948_v0.1.md"],
        capture_output=True, text=True,
    )
    assert show_result.returncode == 0
    assert "**Status:** OPEN" in show_result.stdout, (
        f"CDL-082 was not OPEN at Phase 948 commit {opening_commit}."
    )


# ---------------------------------------------------------------------------
# Category 4 — Phase 1100 Coherence
# ---------------------------------------------------------------------------


@pytest.mark.skipif(SELFTEST_MODE, reason="selftest mode")
def test_cat4_coherence_report_1100_exists():
    assert Path("docs/specs/ilc_integration_coherence_report_1100_v0.1.md").exists()


@pytest.mark.skipif(SELFTEST_MODE, reason="selftest mode")
def test_cat4_coherence_report_verdict_pass():
    content = Path("docs/specs/ilc_integration_coherence_report_1100_v0.1.md").read_text()
    assert "coherence_report_1100_verdict=pass" in content


@pytest.mark.skipif(SELFTEST_MODE, reason="selftest mode")
def test_cat4_capsule_v533_exists():
    assert Path("docs/specs/ilc_antigravity_context_capsule_v5.33.md").exists()


@pytest.mark.skipif(SELFTEST_MODE, reason="selftest mode")
def test_cat4_capsule_v533_supersedes_v532():
    content = Path("docs/specs/ilc_antigravity_context_capsule_v5.33.md").read_text()
    assert "capsule_v5_33_supersedes_v5_32" in content


@pytest.mark.skipif(SELFTEST_MODE, reason="selftest mode")
def test_cat4_capsule_v533_window_notation_correct():
    """Capsule must record the corrected window notation."""
    content = Path("docs/specs/ilc_antigravity_context_capsule_v5.33.md").read_text()
    assert "window_945_1101_complete" in content
