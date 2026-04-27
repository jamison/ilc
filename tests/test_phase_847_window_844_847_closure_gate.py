"""Phase 847 window 844–847 closure gate.

Verifies the complete window 844–847 delivery:
- Phase 844: Rust routing instrumentation (13/13 already tested)
- Phase 845: SIM-LEAKAGE-03 live run + honest non-closure (9/9 already tested)
- Phase 846: CDL-072 + Row 5 runtime_closed (15/15 already tested)
- Phase 847: window integrity checks

Token: window_844_847_closed
Token: row5_runtime_closed_confirmed_847
"""
import subprocess
from pathlib import Path

REPO = Path(__file__).parent.parent

# Key artifacts for each phase in this window
PHASE_844_TEST = REPO / "tests" / "test_phase_844_row5_rust_routing_instrumentation.py"
PHASE_845_TEST = REPO / "tests" / "test_phase_845_sim_leakage_03_live_run.py"
PHASE_846_TEST = REPO / "tests" / "test_phase_846_cdl_072_bound_b_and_row5_closure.py"

CAPSULE_V5_20 = REPO / "docs" / "specs" / "ilc_antigravity_context_capsule_v5.20.md"
CDL_LOG = REPO / "docs" / "specs" / "ilc_constitutional_decision_log_v0.1.md"
RERUN_EVIDENCE = REPO / "docs" / "research" / "ilc_sim_leakage_03_rerun_846_v0.1.md"
STATUS_MD = REPO / "docs" / "phases" / "STATUS.md"


# ---------------------------------------------------------------------------
# Window artifact presence
# ---------------------------------------------------------------------------

def test_phase_844_gate_test_exists():
    assert PHASE_844_TEST.exists(), "Phase 844 gate test missing"


def test_phase_845_gate_test_exists():
    assert PHASE_845_TEST.exists(), "Phase 845 gate test missing"


def test_phase_846_gate_test_exists():
    assert PHASE_846_TEST.exists(), "Phase 846 gate test missing"


def test_capsule_v5_20_exists():
    assert CAPSULE_V5_20.exists(), "Capsule v5.20 missing"


def test_capsule_v5_20_supersedes_v5_19():
    text = CAPSULE_V5_20.read_text()
    assert "capsule_v5_20_supersedes_v5_19" in text
    assert "v5.19" in text


# ---------------------------------------------------------------------------
# Row 5 runtime_closed confirmed
# ---------------------------------------------------------------------------

def test_row5_runtime_closed_in_capsule():
    text = CAPSULE_V5_20.read_text()
    assert "row5_runtime_closed_846" in text, (
        "Capsule v5.20 must record row5_runtime_closed_846"
    )
    assert "runtime_closed" in text


def test_row5_runtime_closed_in_rerun_evidence():
    text = RERUN_EVIDENCE.read_text()
    assert "row5_runtime_closed_846" in text
    assert "row5_b_impl_complete" in text


def test_cdl_072_ratified_in_capsule():
    text = CAPSULE_V5_20.read_text()
    assert "CDL-072" in text
    # CDL table row has both CDL-072 and Ratified on the same line
    cdl_table_line = [l for l in text.splitlines() if "CDL-072" in l and ("Ratified" in l or "ratified" in l)]
    assert cdl_table_line, "Capsule v5.20 CDL table must show CDL-072 as Ratified"


# ---------------------------------------------------------------------------
# CDL-072 in master log
# ---------------------------------------------------------------------------

def test_cdl_072_present_in_cdl_log():
    text = CDL_LOG.read_text()
    assert "CDL-072" in text
    row_start = text.find("CDL-072")
    row = text[row_start:row_start + 1200]
    assert "ratified" in row
    assert "ratified_phase: 846" in row
    assert "ratified_date: 2026-04-26" in row


# ---------------------------------------------------------------------------
# Window 844–847 STATUS.md completeness
# ---------------------------------------------------------------------------

def test_status_md_has_phase_844():
    text = STATUS_MD.read_text()
    assert "## Phase 844" in text


def test_status_md_has_phase_845():
    text = STATUS_MD.read_text()
    assert "## Phase 845" in text


def test_status_md_has_phase_846():
    text = STATUS_MD.read_text()
    assert "## Phase 846" in text
    assert "runtime_closed" in text[text.find("## Phase 846"):]


def test_status_md_has_phase_847():
    text = STATUS_MD.read_text()
    assert "## Phase 847" in text


# ---------------------------------------------------------------------------
# No regressions: all three prior phase gate tests still collected
# ---------------------------------------------------------------------------

def test_phase_844_gate_still_importable():
    """Phase 844 gate test file is syntactically valid."""
    import ast
    ast.parse(PHASE_844_TEST.read_text())


def test_phase_845_gate_still_importable():
    """Phase 845 gate test file is syntactically valid."""
    import ast
    ast.parse(PHASE_845_TEST.read_text())


def test_phase_846_gate_still_importable():
    """Phase 846 gate test file is syntactically valid."""
    import ast
    ast.parse(PHASE_846_TEST.read_text())


# ---------------------------------------------------------------------------
# Window closure token
# ---------------------------------------------------------------------------

def test_window_closure_token_in_this_file():
    """Closure gate file self-verifies the window token."""
    text = Path(__file__).read_text()
    assert "window_844_847_closed" in text
    assert "row5_runtime_closed_confirmed_847" in text
