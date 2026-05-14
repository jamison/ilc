from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HANDOFF = ROOT / "docs/specs/ilc_window_1330_1342_handoff_1342_v0.1.md"
PROMPT = (
    ROOT
    / "docs/antigravity_tasks/antigravity_prompt__phase_1342_g8_window_1330_1342_closure_handoff.md"
)
PLANNING_INDEX = ROOT / "docs/PLANNING_INDEX.md"
STATUS = ROOT / "docs/phases/STATUS.md"
WALKTHROUGH = ROOT / "docs/phases/phase_1342_window_1330_1342_closure_handoff_walkthrough.md"
ROADMAP = ROOT / "docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md"
FORWARD_PLAN = (
    ROOT / "docs/specs/ilc_forward_phase_windows_1303_1342_packaging_and_signing_plan_v0.2.md"
)
CDL_REGISTER = ROOT / "docs/specs/ilc_constitutional_decision_log_v0.1.md"


REQUIRED_TOKENS = (
    "window_1330_1342_closed_phase_1342",
    "window_1330_1342_closure_gate_verdict=pass_or_blocked_with_carry_forward",
    "phase_1342_window_1330_1342_closure_complete",
    "window_1343_plus_sequence_lock_required_before_next_phase_assignment",
    "final_rc_publication_and_signing_blockers_classified_phase_1342",
    "public_rc_final_status_recorded_phase_1342",
)

FINAL_PUBLIC_RC_BLOCKERS = (
    "publication_target_or_tag_not_selected",
    "counsel_publication_clearance_missing",
    "release_artifact_not_release_signed",
    "public_claimability_api_not_activated",
    "public_path_p2p_sidecar_serving_not_activated",
    "wallet_ecu_ilc_value_path_not_activated",
)

GRAPH_DELTAS = (
    "graph_delta=support_only:docs/specs/ilc_window_1330_1342_handoff_1342_v0.1.md -> planning/frontier",
    "graph_delta=support_tests_added:tests/test_phase_1342_window_1330_1342_closure_handoff.py -> validation",
    "graph_delta=support_only:docs/phases/phase_1342_window_1330_1342_closure_handoff_walkthrough.md -> planning/frontier",
    "graph_delta=support_only:docs/phases/STATUS.md -> planning/frontier",
    "graph_delta=support_only:docs/PLANNING_INDEX.md -> planning/frontier",
    "graph_delta=support_only:docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md -> planning/frontier",
    "graph_delta=support_only:docs/specs/ilc_forward_phase_windows_1303_1342_packaging_and_signing_plan_v0.2.md -> planning/frontier",
)


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_phase_1342_required_tokens_are_anchored_in_closure_sources() -> None:
    paths = (HANDOFF, PROMPT, PLANNING_INDEX, STATUS, WALKTHROUGH, ROADMAP, FORWARD_PLAN)

    for path in paths:
        text = _text(path)
        for token in REQUIRED_TOKENS:
            assert token in text, f"{token} missing from {path}"


def test_phase_1342_handoff_closes_all_window_rows_and_preserves_public_non_claim() -> None:
    text = _text(HANDOFF)

    for phase in range(1330, 1342):
        assert f"| {phase} |" in text

    for fix_row in ("1331 Fix1", "1331 Fix2", "1331 Fix3", "1332 Fix4"):
        assert fix_row in text

    assert "Window 1330-1342 is CLOSED / PASS with carry-forward through Phase 1342" in text
    assert "public_rc_final_status=not_published_blocked_with_findings" in text
    assert "No row in this window has status `published_with_authority`" in text
    assert "Public RC was not published" in text


def test_phase_1342_final_public_rc_blockers_are_recorded_everywhere() -> None:
    paths = (HANDOFF, WALKTHROUGH, STATUS, PLANNING_INDEX, ROADMAP, FORWARD_PLAN)

    for path in paths:
        text = _text(path)
        for blocker in FINAL_PUBLIC_RC_BLOCKERS:
            assert blocker in text, f"{blocker} missing from {path}"


def test_phase_1342_records_next_window_sequence_lock_requirement() -> None:
    for path in (HANDOFF, WALKTHROUGH, STATUS, PLANNING_INDEX, ROADMAP, FORWARD_PLAN):
        text = _text(path)
        assert "window_1343_plus_sequence_lock_required_before_next_phase_assignment" in text
        assert "Window 1343+ sequence lock required" in text or "Window 1343+ is not open" in text


def test_phase_1342_graph_delta_is_consistent() -> None:
    for path in (HANDOFF, WALKTHROUGH, STATUS):
        text = _text(path)
        for delta in GRAPH_DELTAS:
            assert delta in text, f"{delta} missing from {path}"


def test_phase_1342_non_authorization_boundary_remains_closed() -> None:
    boundary_terms = (
        "release signing",
        "public claimability",
        "public verifier service",
        "wallet-facing withdrawal request",
        "ECU minting",
        "ILC settlement",
        "CDL-088 opening",
        "counsel approval",
    )

    for path in (HANDOFF, WALKTHROUGH, STATUS, PLANNING_INDEX):
        text = _text(path)
        for term in boundary_terms:
            assert term in text, f"{term} missing from {path}"


def test_cdl_088_remains_unopened_in_register() -> None:
    text = _text(CDL_REGISTER)

    assert "| CDL-088 |" not in text
    assert "CDL-087" in text
