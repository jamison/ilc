from pathlib import Path


DELIBERATION = Path("docs/specs/ilc_cdl_086_deliberation_1203_v0.1.md")
STATUS = Path("docs/phases/STATUS.md")
WALKTHROUGH = Path("docs/phases/phase_1203_cdl_086_deliberation_walkthrough.md")
PLANNING_INDEX = Path("docs/PLANNING_INDEX.md")


def test_deliberation_doc_exists() -> None:
    assert DELIBERATION.exists()


def test_deliberation_token() -> None:
    content = DELIBERATION.read_text(encoding="utf-8")
    assert "cdl_086_deliberation_committed_phase_1203" in content


def test_all_five_questions_addressed() -> None:
    content = DELIBERATION.read_text(encoding="utf-8")
    for q in ("Q1", "Q2", "Q3", "Q4", "Q5"):
        assert f"| {q} |" in content


def test_deliberation_records_no_human_blockers_for_prelock_eligibility() -> None:
    content = DELIBERATION.read_text(encoding="utf-8")
    assert "All five questions are resolved without a human blocker" in content
    assert "GO Phase 1204" in content
    assert "does not itself authorize Phase 1204" in content


def test_q3_does_not_block_internal_rc2_but_blocks_public_launch() -> None:
    content = DELIBERATION.read_text(encoding="utf-8")
    assert "does not block internal RC2 engineering work" in content
    assert "public launch claims" in content
    assert "public repository publication" in content
    assert "external operator bootstrap" in content


def test_q5_counsel_is_ratification_condition() -> None:
    content = DELIBERATION.read_text(encoding="utf-8")
    assert "Counsel closure is a ratification and public-launch condition" in content
    assert "not an opening or deliberation prerequisite" in content


def test_phase_1203_frontier_docs_updated() -> None:
    status = STATUS.read_text(encoding="utf-8")
    walkthrough = WALKTHROUGH.read_text(encoding="utf-8")
    planning = PLANNING_INDEX.read_text(encoding="utf-8")
    assert "## Phase 1203" in status
    assert "cdl_086_deliberation_committed_phase_1203" in status
    assert "**Status:** complete" in walkthrough
    assert "Window 1200-1208 is IN PROGRESS through Phase 1203" in planning
