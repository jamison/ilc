"""Phase 1528p ADR-0035 CDL-097 ratification checks.

PUBLIC_RC_EXCLUDE: phase_1528p_private_cdl_ratification_selftest
PUBLIC_RC_EXCLUDE_REASON: Internal private-window assertion. Not a public RC artifact.
"""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _read(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


def test_ratification_evidence_records_tokens_and_boundaries() -> None:
    text = _read(
        "docs/specs/ilc_cdl_097_type_definition_node_authority_ratification_evidence_1528p_v0.1.md"
    )

    for token in [
        "cdl_097_ratified_phase_1528p",
        "adr_0035_cdl_implementation_authority_in_place_phase_1528p",
        "obl_025_cdl_condition_satisfied_phase_1528p",
        "public_path_still_blocked_phase_1528p",
        "GO Phase 1528p",
        "OBL-025 is not fully closed in Phase 1528p",
    ]:
        assert token in text

    assert "No runtime implementation occurred" not in text
    assert "does not authorize production graph writes" in text


def test_cdl_register_ratifies_cdl097_and_keeps_runtime_blocked() -> None:
    cdl = _read("docs/specs/ilc_constitutional_decision_log_v0.1.md")

    assert "| CDL-097 |" in cdl
    assert "| ratified |" in cdl
    assert "prelock_token: cdl_097_prelock_committed_phase_1527p" in cdl
    assert "scope_token: cdl_097_scope_constants_locked_phase_1527p" in cdl
    assert "ratification_token: cdl_097_ratified_phase_1528p" in cdl
    assert (
        "evidence_document: "
        "docs/specs/ilc_cdl_097_type_definition_node_authority_ratification_evidence_1528p_v0.1.md"
    ) in cdl
    assert "type_registry_implementation_status: not_authorized" in cdl
    assert "production_activation_status: not_authorized" in cdl
    assert "runtime_guard_required: ADR_0035_TYPE_REGISTRY_NOT_ACTIVATED=True (Phase 1529p)" in cdl
    assert "| CDL-096 |" not in cdl


def test_adr0035_status_records_authority_without_activation_claim() -> None:
    adr = _read("docs/adr/ADR_0035_Homoiconic_Type_Definition_System.md")
    status_line = next(line for line in adr.splitlines() if line.startswith("**Status:**"))

    assert (
        "**Status:** Accepted — CDL-097 ratified Phase 1528p; implementation "
        "authority in place; runtime scaffold is Phase 1529p work; no production "
        "activation authorized."
    ) in status_line
    assert "adr_0035_homoiconic_type_definition_system_direction_accepted" in adr
    assert "adr_0035_implementation_deferred_pending_cdl" in adr
    assert "adr_0035_cdl_implementation_authority_in_place_phase_1528p" in adr
    assert "implemented" not in status_line.lower()
    assert "production-ready" not in status_line.lower()
    assert "live" not in status_line.lower()


def test_adr0030_lists_type_definition_as_cdl097_governed_content_type() -> None:
    adr = _read("docs/adr/ADR_0030_Node_Embedding_Substrate_and_Content_Typing.md")

    assert '`"type_definition"` — a CDL-097 governed definition-node content category' in adr
    assert "CDL-097 governs type-definition authority" in adr


def test_obl025_is_cdl_condition_satisfied_but_not_closed() -> None:
    register = _read("docs/specs/ilc_open_obligation_register_v0.1.md")

    assert "obl_025_cdl_condition_satisfied_phase_1528p" in register
    row = next(line for line in register.splitlines() if line.startswith("| OBL-025 |"))
    assert (
        (
            "| open |" in row
            and "remains open pending default-off runtime scaffold" in row
        )
        or (
            "| closed |" in row
            and "obl_025_closed_phase_1529p" in row
            and "ADR_0035_TYPE_REGISTRY_NOT_ACTIVATED = True" in row
        )
    )
    assert "obl_025_closed_phase_1528p" not in register


def test_no_phase_1528p_ilc_core_runtime_guard_exists_yet() -> None:
    for path in (ROOT / "ilc_core").rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        if path.as_posix().endswith("ilc_core/bundle/type_registry.py"):
            assert "ADR_0035_TYPE_REGISTRY_NOT_ACTIVATED = True" in text
        else:
            assert "ADR_0035_TYPE_REGISTRY_NOT_ACTIVATED" not in text


def test_phase_1528p_frontier_updates_are_present() -> None:
    status = _read("docs/phases/STATUS.md")
    planning = _read("docs/PLANNING_INDEX.md")
    agents = _read("AGENTS.md")
    lock = _read("docs/specs/ilc_phase_1523p_1530p_sequence_lock_v0.1.md")
    walkthrough = _read("docs/phases/phase_1528p_adr0035_cdl_ratification_walkthrough.md")

    for text in (status, planning, agents, lock, walkthrough):
        assert "cdl_097_ratified_phase_1528p" in text
        assert "adr_0035_cdl_implementation_authority_in_place_phase_1528p" in text
        assert "obl_025_cdl_condition_satisfied_phase_1528p" in text
        assert "public_path_still_blocked_phase_1528p" in text

    assert "| 1528p | Type-system CDL ratification | SENSITIVE | COMPLETE |" in lock
    assert "phase_1528p: complete_sensitive_cdl097_ratification" in agents
    assert (
        "Phase 1529p is the next phase and is NON-SENSITIVE" in planning
        or "Phase 1530p is next and requires exact `GO Phase 1530p`" in planning
    )
