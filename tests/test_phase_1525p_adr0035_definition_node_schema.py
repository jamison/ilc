"""Phase 1525p ADR-0035 definition-node schema checks.

PUBLIC_RC_EXCLUDE: phase_1525p_private_definition_node_schema_selftest
PUBLIC_RC_EXCLUDE_REASON: Internal private-window assertion. Not a public RC artifact.
"""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _read(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


def test_definition_node_schema_records_required_contract() -> None:
    text = _read(
        "docs/specs/ilc_adr0035_definition_node_verifier_and_decomposition_schema_1525p_v0.1.md"
    )

    required = [
        "adr0035_definition_node_verifier_schema_committed_phase_1525p",
        "type_system_cdl_opening_ready_for_human_review_phase_1525p",
        "`definition_id`",
        "`node_type`",
        "`content_type`",
        "`decomposition_recipe`",
        "`authority_ref`",
        "definition_node_non_attributable_required",
        "public_path_still_blocked_phase_1525p",
    ]

    for token in required:
        assert token in text


def test_definition_node_schema_records_stable_error_tokens() -> None:
    text = _read(
        "docs/specs/ilc_adr0035_definition_node_verifier_and_decomposition_schema_1525p_v0.1.md"
    )

    for token in [
        "type_definition_required_field_missing",
        "type_definition_content_type_not_authorized",
        "type_definition_missing_authority_ref",
        "type_definition_not_cdl_ratified",
        "type_definition_decomposition_recipe_missing",
        "type_definition_duplicate_recipe_scope_missing",
        "type_definition_supersession_cycle",
    ]:
        assert token in text


def test_phase_1525p_frontier_updates_are_present() -> None:
    status = _read("docs/phases/STATUS.md")
    planning = _read("docs/PLANNING_INDEX.md")
    agents = _read("AGENTS.md")
    register = _read("docs/specs/ilc_open_obligation_register_v0.1.md")
    lock = _read("docs/specs/ilc_phase_1523p_1530p_sequence_lock_v0.1.md")

    assert "Phase 1525p - ADR-0035 Definition-Node Verifier Schema" in status
    assert "adr0035_definition_node_verifier_schema_committed_phase_1525p" in planning
    assert "phase_1525p: complete_definition_node_verifier_schema" in agents
    assert "obligation_register_sweep_complete_phase_1525p" in register
    assert "| 1525p | Definition-node verifier and decomposition schema spec | NON-SENSITIVE | COMPLETE" in lock


def test_phase_1525p_does_not_mutate_adr_or_cdl_authority() -> None:
    adr = _read("docs/adr/ADR_0035_Homoiconic_Type_Definition_System.md")
    cdl = _read("docs/specs/ilc_constitutional_decision_log_v0.1.md")

    assert (
        "**Status:** Accepted — direction accepted; implementation deferred to CDL phase" in adr
        or "CDL-097 ratified Phase 1528p; implementation authority in place" in adr
    )
    assert "adr_0035_implementation_deferred_pending_cdl" in adr
    # HISTORICAL_SNAPSHOT: CDL-096 was not present when Phase 1525p ran; it is
    # now present in current canon and must not fail this historical selftest.
    assert "CDL-096" in cdl
    assert "type_definition_node_type_mismatch" not in cdl
