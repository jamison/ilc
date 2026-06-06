"""Phase 1530p Window 1523p-1530p closure-gate checks.

PUBLIC_RC_EXCLUDE: phase_1530p_private_window_closure_selftest
PUBLIC_RC_EXCLUDE_REASON: Internal private-window closure assertions. Not a public RC artifact.
"""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _read(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


def test_phase_1530p_handoff_records_required_closure_tokens() -> None:
    handoff = _read("docs/specs/ilc_window_1523p_1530p_handoff_1530p_v0.1.md")

    for token in [
        "window_1523p_closed_phase_1530p",
        "window_1523p_closure_gate_committed_phase_1530p",
        "window_1523p_closure_gate_verdict=pass",
        "public_path_remains_blocked_phase_1530p",
        "go_window_1531p_required_next",
    ]:
        assert token in handoff

    assert "**Status:** CLOSED PASS" in handoff
    assert "**Authorization received:** `GO Phase 1530p`" in handoff
    assert "Window 1531p is not opened by this handoff" in handoff


def test_phase_1530p_handoff_satisfies_closure_schema_sections() -> None:
    handoff = _read("docs/specs/ilc_window_1523p_1530p_handoff_1530p_v0.1.md")

    for section in [
        "## 1. Window Identity And Closure Basis",
        "## 2. Inputs And Closure Inheritance",
        "## 3. Closure Verdict Summary",
        "## 4. Carry-Forward Items And Residual Blockers",
        "## 5. Next-Window Entry Criteria And Routing",
        "## 6. MemPalace Refresh Disposition",
    ]:
        assert section in handoff

    assert "**Disposition:** required" in handoff
    assert "**Active working set impacted:** yes" in handoff
    assert "bash tools/mempalace/build_active_working_set.sh" in handoff


def test_phase_1530p_gate_summary_records_block3_closed_and_public_path_blocked() -> None:
    handoff = _read("docs/specs/ilc_window_1523p_1530p_handoff_1530p_v0.1.md")

    for row in [
        "| Phase 1523p sequence lock committed | PASS |",
        "| Phase 1524p dependency reconciliation committed | PASS |",
        "| Phase 1525p verifier schema committed | PASS |",
        "| Phase 1526p CDL-097 opened | PASS |",
        "| Phase 1527p prelock committed | PASS |",
        "| Phase 1528p CDL-097 ratified | PASS |",
        "| Phase 1529p type registry scaffold committed | PASS |",
        "| OBL-025 closed | PASS |",
        "| CDL-096 not consumed | PASS |",
        "| Public path still blocked | PASS |",
        "| `ADR_0035_TYPE_REGISTRY_NOT_ACTIVATED = True` | PASS |",
        "| ADR-0041/CDL-042/CDL-069 reconciliation accounted for | PASS |",
    ]:
        assert row in handoff

    assert "Block 4 Economic Finality" in handoff


def test_phase_1530p_obl025_closed_and_remaining_obls_routed() -> None:
    register = _read("docs/specs/ilc_open_obligation_register_v0.1.md")
    handoff = _read("docs/specs/ilc_window_1523p_1530p_handoff_1530p_v0.1.md")

    row = next(line for line in register.splitlines() if line.startswith("| OBL-025 |"))
    assert "| closed |" in row
    assert "obl_025_closed_phase_1529p" in row
    assert "ADR_0035_TYPE_REGISTRY_NOT_ACTIVATED = True" in row

    for obligation in ["OBL-020", "OBL-021", "OBL-022", "OBL-027"]:
        assert f"| {obligation} | Open | Block 4 Economic Finality" in handoff

    for obligation in ["OBL-023", "OBL-024", "OBL-028", "OBL-029"]:
        assert f"| {obligation} | Open | Block 5 governance/economic edge specs" in handoff


def test_phase_1530p_cdl097_ratified_and_cdl096_absent() -> None:
    cdl = _read("docs/specs/ilc_constitutional_decision_log_v0.1.md")
    handoff = _read("docs/specs/ilc_window_1523p_1530p_handoff_1530p_v0.1.md")

    assert "| CDL-097 |" in cdl
    assert "ratification_token: cdl_097_ratified_phase_1528p" in cdl
    assert "runtime_guard_required: ADR_0035_TYPE_REGISTRY_NOT_ACTIVATED=True (Phase 1529p)" in cdl
    assert "cdl_096_status: separate_werner_lane_unaffected" in cdl
    assert "| CDL-096 |" not in cdl

    assert "| CDL-096 | Eligible, unopened |" in handoff
    assert "CDL-096" in handoff
    assert "remains eligible for the Werner flow-governor lane and remains unopened" in handoff


def test_phase_1530p_type_registry_remains_default_off_and_non_authority_bearing() -> None:
    source = _read("ilc_core/bundle/type_registry.py")
    handoff = _read("docs/specs/ilc_window_1523p_1530p_handoff_1530p_v0.1.md")

    assert "ADR_0035_TYPE_REGISTRY_NOT_ACTIVATED = True" in source
    assert "ADR_0035_TYPE_REGISTRY_NOT_ACTIVATED = False" not in source
    assert "def load_from_graph" in source
    assert "activated=False" in source

    assert "`Node(type=\"type_definition\")` parseable but not authority-bearing" in handoff
    assert "Agent INIT cannot create authority-bearing type-definition nodes" in handoff


def test_phase_1530p_frontier_surfaces_are_closed_and_single_current() -> None:
    lock = _read("docs/specs/ilc_phase_1523p_1530p_sequence_lock_v0.1.md")
    planning = _read("docs/PLANNING_INDEX.md")
    status = _read("docs/phases/STATUS.md")
    agents = _read("AGENTS.md")

    for text in (lock, planning, status, agents):
        assert "window_1523p_closed_phase_1530p" in text
        assert "window_1523p_closure_gate_verdict=pass" in text
        assert "public_path_remains_blocked_phase_1530p" in text
        assert "go_window_1531p_required_next" in text

    assert "**Status:** CLOSED PASS - Window 1523p-1530p closed by Phase 1530p" in lock
    assert "| 1530p | Window closure gate | SENSITIVE | COMPLETE |" in lock
    assert planning.count("⬅ CURRENT") == 1
    assert "Phase 1530p Window 1523p-1530p closure" in planning
    assert "window_1523p_1530p: CLOSED_PASS" in agents


def test_phase_1530p_non_authorization_floor_is_preserved() -> None:
    handoff = _read("docs/specs/ilc_window_1523p_1530p_handoff_1530p_v0.1.md")
    status = _read("docs/phases/STATUS.md")

    for blocked in [
        "public source export",
        "public RC",
        "epoch transition",
        "ECU minting",
        "ILC settlement",
        "CDL-096 opening",
        "ADR-0035 type registry production activation",
        "`ADR_0035_TYPE_REGISTRY_NOT_ACTIVATED` clearance",
        "public-path activation",
    ]:
        assert blocked in handoff
        assert blocked in status


def test_phase_1530p_graph_delta_records_closure_artifacts() -> None:
    walkthrough = _read(
        "docs/phases/phase_1530p_window_1523p_1530p_closure_gate_walkthrough.md"
    )

    for delta in [
        "graph_delta=load_bearing_artifact_added:docs/specs/ilc_window_1523p_1530p_handoff_1530p_v0.1.md -> planning/window-1523p-closure",
        "graph_delta=load_bearing_artifact_changed:docs/specs/ilc_phase_1523p_1530p_sequence_lock_v0.1.md -> planning/window-1523p-sequence-lock",
        "graph_delta=deferred:go_window_1531p_required_next",
    ]:
        assert delta in walkthrough
