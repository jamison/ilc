from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OPENING = ROOT / "docs/specs/ilc_cdl_096_opening_1551p_v0.1.md"
CDL_REGISTER = ROOT / "docs/specs/ilc_constitutional_decision_log_v0.1.md"
SEQUENCE_LOCK = ROOT / "docs/specs/ilc_phase_1546p_1555p_sequence_lock_v0.1.md"
PLANNING_INDEX = ROOT / "docs/PLANNING_INDEX.md"
STATUS = ROOT / "docs/phases/STATUS.md"
AGENTS = ROOT / "AGENTS.md"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_phase_1551_opening_artifact_records_option_a_only() -> None:
    text = read(OPENING)
    assert "cdl_096_opened_phase_1551p" in text
    assert "cdl_096_scope_option_selected_phase_1551p" in text
    assert "cdl_096_scope_selection_option_a_phase_1551p" in text
    assert "cdl_096_scope_selection_option_b_phase_1551p" not in text
    assert "cdl_096_scope_selection_option_c_phase_1551p" not in text
    assert "combined Werner flow-governor authority plus CDL-095 global-tier jury finality" in text


def test_cdl_register_has_cdl096_with_option_a_and_no_runtime_activation() -> None:
    register = read(CDL_REGISTER)
    assert "| CDL-096 |" in register
    cdl096_row = next(line for line in register.splitlines() if line.startswith("| CDL-096 |"))
    assert "| ratified |" in cdl096_row
    assert "opened_phase: 1551p" in cdl096_row
    assert "opening_token: cdl_096_opened_phase_1551p" in cdl096_row
    assert "scope_selection_token: cdl_096_scope_selection_option_a_phase_1551p" in cdl096_row
    assert "prelock_status: cdl_096_prelock_committed_phase_1552p" in cdl096_row
    assert "ratification_status: ratified_phase_1553p" in cdl096_row
    assert "ratification_token: cdl_096_ratified_phase_1553p" in cdl096_row
    assert "werner_flow_governor_runtime_status: not_authorized" in cdl096_row
    assert "global_tier_activation_status: not_authorized" in cdl096_row
    assert "cdl_095_amendment_status: not_required_for_option_a" in cdl096_row
    assert "cdl_098_status: unconsumed" in cdl096_row


def test_cdl095_pointer_remains_visible_and_no_amendment_claimed() -> None:
    register = read(CDL_REGISTER)
    cdl095_row = next(line for line in register.splitlines() if line.startswith("| CDL-095 |"))
    assert "global_tier_activation_status: deferred_to_cdl_096" in cdl095_row
    assert "cdl_095_amendment_status: not_required_for_option_a" in register
    assert "CDL-095 must be amended" not in read(OPENING)


def test_sequence_lock_frontier_advances_through_ratification() -> None:
    lock = read(SEQUENCE_LOCK)
    assert "| 1551p | CDL-096 opening after human scope selection | SENSITIVE | COMPLETE - Option A |" in lock
    assert "cdl_096_scope_selection_option_a_phase_1551p" in lock
    assert "| 1552p | CDL-096 deliberation and prelock | NON-SENSITIVE | COMPLETE |" in lock
    assert "| 1553p | CDL-096 ratification | SENSITIVE | COMPLETE |" in lock
    assert "| 1554p | Block 5 coherence report and capsule update | NON-SENSITIVE | COMPLETE |" in lock
    assert "Window 1546p-1555p is closed" in lock
    assert "go_window_1556p_block6_required_next" in lock
    assert "Phase 1551p is the next phase" not in lock


def test_frontier_docs_record_ratified_runtime_not_activated_boundary() -> None:
    combined = "\n".join(read(path) for path in (PLANNING_INDEX, STATUS, AGENTS))
    assert "cdl_096_opened_phase_1551p" in combined
    assert "cdl_096_scope_selection_option_a_phase_1551p" in combined
    assert "no_cdl_096_runtime_activation_phase_1551p" in combined
    assert "cdl_096_ratified_phase_1553p" in combined
    assert "cdl_096_runtime_activation_not_authorized_phase_1553p" in combined
    assert "no_cdl_096_open,no_formal_uspto_receipts" not in combined
