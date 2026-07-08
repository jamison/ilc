"""Phase 1524p ADR-0035 dependency reconciliation checks.

PUBLIC_RC_EXCLUDE: phase_1524p_private_dependency_reconciliation_selftest
PUBLIC_RC_EXCLUDE_REASON: Internal private-window assertion. Not a public RC artifact.
"""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _read(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


def test_dependency_reconciliation_records_required_boundaries() -> None:
    text = _read("docs/specs/ilc_adr0035_dependency_reconciliation_1524p_v0.1.md")

    required = [
        "adr0035_dependency_reconciliation_committed_phase_1524p",
        "ADR-0030 `content_type` is content-layer metadata",
        "ADR-0035 type definitions are graph-structure governance semantics",
        "A new agent cannot create an authoritative type-definition node by INIT alone.",
        "No independent \"type author identity\" namespace is created.",
        "Bundle verification proves package integrity, not constitutional authority.",
        "CDL-096 is eligible to open but reserved for the Werner flow-governor lane.",
        "public_path_still_blocked_phase_1524p",
    ]

    for token in required:
        assert token in text


def test_dependency_reconciliation_preserves_non_mutation_state() -> None:
    adr35 = _read("docs/adr/ADR_0035_Homoiconic_Type_Definition_System.md")
    cdl = _read("docs/specs/ilc_constitutional_decision_log_v0.1.md")

    assert (
        "**Status:** Accepted — direction accepted; implementation deferred to CDL phase" in adr35
        or "CDL-097 ratified Phase 1528p; implementation authority in place" in adr35
    )
    assert "adr_0035_implementation_deferred_pending_cdl" in adr35
    # HISTORICAL_SNAPSHOT: Phase 1524p reserved CDL-096 for the Werner lane.
    # Current canon has since opened and ratified CDL-096, so this test now
    # checks the historical reservation token rather than forbidding the row.
    assert "cdl_096_status: separate_werner_lane_unaffected" in cdl or "| CDL-096 |" in cdl
    if "cdl_097_ratified_phase_1528p" in cdl:
        assert "type_registry_implementation_status: not_authorized" in cdl
    else:
        assert "type-system CDL opening" not in cdl


def test_phase_1524p_frontier_updates_are_present() -> None:
    status = _read("docs/phases/STATUS.md")
    planning = _read("docs/PLANNING_INDEX.md")
    agents = _read("AGENTS.md")
    register = _read("docs/specs/ilc_open_obligation_register_v0.1.md")
    lock = _read("docs/specs/ilc_phase_1523p_1530p_sequence_lock_v0.1.md")

    assert "Phase 1524p - ADR-0035 Dependency Reconciliation" in status
    assert "adr0035_dependency_reconciliation_committed_phase_1524p" in planning
    assert "phase_1524p: complete_adr0035_dependency_reconciliation" in agents
    assert "obligation_register_sweep_complete_phase_1524p" in register
    assert "| 1524p | ADR-0035 dependency reconciliation spec | NON-SENSITIVE | COMPLETE" in lock
