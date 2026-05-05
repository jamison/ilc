from pathlib import Path


DOC = Path("docs/specs/ilc_truth_primitive_permanence_governance_1206_v0.1.md")
ROADMAP = Path("docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.0.md")
STATUS = Path("docs/phases/STATUS.md")
PLANNING_INDEX = Path("docs/PLANNING_INDEX.md")


def test_governance_doc_exists() -> None:
    assert DOC.exists()


def test_routing_token_present() -> None:
    content = DOC.read_text(encoding="utf-8")
    assert "truth_primitive_permanence_governance_routed_phase_1206" in content


def test_routing_is_concrete_not_indefinite() -> None:
    content = DOC.read_text(encoding="utf-8")
    assert "truth_primitive_permanence_ratification_packet_required_window_1209" in content
    assert "ROUTED — ratification packet required" in content
    assert "does not open a CDL" in content


def test_roadmap_records_routed_gate() -> None:
    content = ROADMAP.read_text(encoding="utf-8")
    assert "Truth-primitive permanence community ratification" in content
    assert "**ROUTED** — ratification packet required" in content


def test_status_and_planning_record_phase_1206() -> None:
    status = STATUS.read_text(encoding="utf-8")
    planning = PLANNING_INDEX.read_text(encoding="utf-8")
    assert "## Phase 1206" in status
    assert "truth_primitive_permanence_governance_routed_phase_1206" in status
    assert (
        "Window 1200-1208 is IN PROGRESS through Phase 1206" in planning
        or "Window 1200-1208 is CLOSED" in planning
    )
