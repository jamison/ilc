from pathlib import Path


PRELOCK = Path("docs/specs/ilc_cdl_086_prelock_spec_1204_v0.1.md")
CDL_REGISTER = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
STATUS = Path("docs/phases/STATUS.md")
PLANNING_INDEX = Path("docs/PLANNING_INDEX.md")


def test_prelock_doc_exists() -> None:
    assert PRELOCK.exists()


def test_prelock_token_present() -> None:
    content = PRELOCK.read_text(encoding="utf-8")
    assert "cdl_086_prelock_committed_phase_1204" in content


def test_prelock_references_deliberation_and_dependencies() -> None:
    content = PRELOCK.read_text(encoding="utf-8")
    assert "cdl_086_deliberation_committed_phase_1203" in content
    assert "CDL-001" in content
    assert "ADR-0036" in content
    assert "ADR-0037" in content
    assert "CDL-085" in content


def test_prelock_is_not_ratification_or_public_launch_authorization() -> None:
    content = PRELOCK.read_text(encoding="utf-8")
    assert "does not ratify CDL-086" in content
    assert "authorize a public launch claim" in content
    assert "mutate signed Genesis v0.1" in content


def test_cdl_register_still_open_not_ratified() -> None:
    register = CDL_REGISTER.read_text(encoding="utf-8")
    cdl_086_lines = [line for line in register.splitlines() if "| CDL-086 |" in line]
    assert len(cdl_086_lines) == 1
    assert "open" in cdl_086_lines[0].lower()
    assert "ratified_phase: 1204" not in cdl_086_lines[0]


def test_status_and_planning_record_phase_1204() -> None:
    status = STATUS.read_text(encoding="utf-8")
    planning = PLANNING_INDEX.read_text(encoding="utf-8")
    assert "## Phase 1204" in status
    assert "cdl_086_prelock_committed_phase_1204" in status
    assert (
        "Window 1200-1208 is IN PROGRESS through Phase 1204" in planning
        or "Window 1200-1208 is CLOSED" in planning
    )
