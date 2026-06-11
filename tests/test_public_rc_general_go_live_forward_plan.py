from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "docs/specs/ilc_public_rc_general_go_live_forward_plan_1555p_v0.1.md"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_plan_records_required_tokens() -> None:
    text = _read(PLAN)
    for token in (
        "public_rc_general_go_live_forward_plan_committed_2026_06_11",
        "all_no_deferral_blocks_1_to_5_complete_or_closure_ready_phase_1555p",
        "adr_cdl_go_live_activation_matrix_recorded_2026_06_11",
        "block6_private_rehearsal_is_required_before_public_rc",
        "public_rc_guard_clearance_decision_matrix_required_before_publication",
        "public_rc_publication_gate_remains_blocked_pending_block6_and_final_gate",
    ):
        assert token in text


def test_plan_keeps_implementation_rehearsal_public_live_distinct() -> None:
    text = _read(PLAN)
    assert "`implemented_default_off`" in text
    assert "`private_rehearsal_active`" in text
    assert "`public_rc_live`" in text
    assert "Public RC must not infer `public_rc_live` from `implemented_default_off`." in text


def test_plan_routes_remaining_work_to_ordered_public_rc_steps() -> None:
    text = _read(PLAN)
    expected_steps = (
        "Step 1 - Close Window 1546p-1555p",
        "Step 2 - Run Fix17 Before Fix6-Fix16",
        "Step 3 - Run Fix6 And Fix7",
        "Step 4 - Run Fix8-Fix16 As Successor-Manifest Support Work",
        "Step 5 - Open Block 6",
        "Step 6 - Final Public RC Gate",
    )
    for step in expected_steps:
        assert step in text


def test_plan_names_guarded_surfaces_and_non_authorizations() -> None:
    text = _read(PLAN)
    for surface in (
        "ADR-0009",
        "ADR-0035 / CDL-097",
        "CDL-096",
        "OBL-020",
        "OBL-021",
        "OBL-022",
        "OBL-027 / ADR-0016",
        "OBL-029",
        "ADR-0010",
        "ADR-0013",
        "ADR-0014",
        "ADR-0024",
    ):
        assert surface in text
    for non_authorization in (
        "public repository publication",
        "guard clearance",
        "ECU minting",
        "ILC settlement",
        "ADR status mutation",
        "CDL opening, prelock, ratification, or amendment",
    ):
        assert non_authorization in text
