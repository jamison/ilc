"""Phase 1526p ADR-0035 type-system CDL opening checks.

PUBLIC_RC_EXCLUDE: phase_1526p_private_cdl_opening_selftest
PUBLIC_RC_EXCLUDE_REASON: Internal private-window assertion. Not a public RC artifact.
"""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _read(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


def test_cdl097_opening_artifact_records_required_tokens_and_questions() -> None:
    text = _read(
        "docs/specs/ilc_cdl_097_type_definition_node_authority_opening_1526p_v0.1.md"
    )

    for token in [
        "cdl_097_type_definition_node_authority_opened_phase_1526p",
        "cdl_097_deliberation_questions_recorded_phase_1526p",
        "type_system_cdl_number_assigned_phase_1526p",
        "cdl_096_not_consumed_phase_1526p",
        "public_path_still_blocked_phase_1526p",
        "cdl_097_not_ratified_phase_1526p",
        "Q1 - CDL number",
        "Q7 - Initial definition-node scope",
    ]:
        assert token in text


def test_cdl_register_has_cdl097_and_no_cdl096_row() -> None:
    cdl = _read("docs/specs/ilc_constitutional_decision_log_v0.1.md")

    assert "| CDL-096 |" not in cdl
    assert "| CDL-097 |" in cdl
    assert "Type-definition node authority" in cdl
    assert "cdl_097_type_definition_node_authority_opened_phase_1526p" in cdl
    assert "cdl_097_deliberation_questions_recorded_phase_1526p" in cdl
    assert "cdl_096_status: separate_werner_lane_unaffected" in cdl
    if "ratification_token: cdl_097_ratified_phase_1528p" in cdl:
        assert "type_registry_implementation_status: not_authorized" in cdl
    else:
        assert "| open |" in cdl


def test_phase_1526p_preserves_adr0035_and_runtime_non_mutation() -> None:
    adr35 = _read("docs/adr/ADR_0035_Homoiconic_Type_Definition_System.md")
    cdl = _read("docs/specs/ilc_constitutional_decision_log_v0.1.md")

    assert (
        "**Status:** Accepted — direction accepted; implementation deferred to CDL phase" in adr35
        or "CDL-097 ratified Phase 1528p; implementation authority in place" in adr35
    )
    assert "adr_0035_implementation_deferred_pending_cdl" in adr35
    assert "ADR_0035_TYPE_REGISTRY_NOT_ACTIVATED = False" not in cdl
    assert "type_registry_status: not_authorized" in cdl or "type_registry_implementation_status: not_authorized" in cdl


def test_phase_1526p_frontier_updates_are_present() -> None:
    status = _read("docs/phases/STATUS.md")
    planning = _read("docs/PLANNING_INDEX.md")
    agents = _read("AGENTS.md")
    register = _read("docs/specs/ilc_open_obligation_register_v0.1.md")
    lock = _read("docs/specs/ilc_phase_1523p_1530p_sequence_lock_v0.1.md")

    assert "Phase 1526p - ADR-0035 Type-System CDL Opening" in status
    assert "cdl_097_type_definition_node_authority_opened_phase_1526p" in planning
    assert "phase_1526p: complete_sensitive_cdl097_type_system_cdl_opening" in agents
    assert "Phase 1526p Sweep" in register
    assert "OBL-025 remains open" in register
    assert "| 1526p | Type-system CDL opening | SENSITIVE | COMPLETE |" in lock
