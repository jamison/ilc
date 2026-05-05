from pathlib import Path


CDL_REGISTER = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
OPENING = Path("docs/specs/ilc_cdl_086_public_launch_packaging_blocker_opening_1194_v0.1.md")
ROADMAP = Path("docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.0.md")
PLANNING_INDEX = Path("docs/PLANNING_INDEX.md")
STATUS = Path("docs/phases/STATUS.md")
WALKTHROUGH = Path(
    "docs/phases/phase_1194_cdl_086_public_launch_packaging_blocker_opening_walkthrough.md"
)


def test_cdl_086_open_in_register() -> None:
    content = CDL_REGISTER.read_text(encoding="utf-8")
    row = next(line for line in content.splitlines() if line.startswith("| CDL-086 |"))
    assert "Public-launch packaging blocker" in row
    assert "| open |" in row
    assert "cdl_086_public_launch_packaging_blocker_opened_phase_1194" in row
    assert "docs/specs/ilc_cdl_086_public_launch_packaging_blocker_opening_1194_v0.1.md" in row


def test_cdl_086_opening_spec_exists_and_has_token() -> None:
    content = OPENING.read_text(encoding="utf-8")
    assert "**Status:** OPEN" in content
    assert "cdl_086_public_launch_packaging_blocker_opened_phase_1194" in content
    assert "CDL-001" in content
    assert "ADR-0036" in content
    assert "ADR-0037" in content
    assert "CDL-085" in content


def test_cdl_086_opening_preserves_non_claims() -> None:
    content = OPENING.read_text(encoding="utf-8")
    assert "This opening does not:" in content
    assert "ratify CDL-086" in content
    assert "authorize a public launch claim" in content
    assert "select license terms" in content
    assert "create legal conclusions" in content
    assert "mutate `ilc_core/`" in content


def test_cdl_001_register_row_not_reused() -> None:
    content = CDL_REGISTER.read_text(encoding="utf-8")
    cdl_001_row = next(line for line in content.splitlines() if line.startswith("| CDL-001 |"))
    assert "Canonical signer lineage definition" in cdl_001_row
    assert "ratified_phase: 251" in cdl_001_row
    assert "Public-launch packaging blocker" not in cdl_001_row


def test_roadmap_and_planning_index_record_cdl_086_open() -> None:
    roadmap = ROADMAP.read_text(encoding="utf-8")
    planning = PLANNING_INDEX.read_text(encoding="utf-8")
    assert "CDL-086 is OPEN" in roadmap
    assert "cdl_086_public_launch_packaging_blocker_opened_phase_1194" in roadmap
    assert "Window 1191-1199 is IN PROGRESS through Phase 1194" in planning
    assert "cdl_086_public_launch_packaging_blocker_opened_phase_1194" in planning


def test_status_and_walkthrough_mark_phase_1194_complete() -> None:
    status = STATUS.read_text(encoding="utf-8")
    walkthrough = WALKTHROUGH.read_text(encoding="utf-8")
    assert "## Phase 1194" in status
    assert "cdl_086_public_launch_packaging_blocker_opened_phase_1194" in status
    assert "**Status:** complete" in walkthrough
    assert "cdl_086_public_launch_packaging_blocker_opened_phase_1194" in walkthrough
