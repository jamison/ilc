from pathlib import Path


REGISTER = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
EVIDENCE = Path("docs/specs/ilc_cdl_086_ratification_evidence_1220_v0.1.md")
DISPOSITION = Path("docs/specs/ilc_cdl_086_counsel_disposition_1220_v0.1.md")
WALKTHROUGH = Path("docs/phases/phase_1220_cdl_086_ratification_walkthrough.md")
STATUS = Path("docs/phases/STATUS.md")
PLANNING = Path("docs/PLANNING_INDEX.md")


def test_cdl_086_register_ratified_phase_1220() -> None:
    register = REGISTER.read_text(encoding="utf-8")
    lines = [line for line in register.splitlines() if "| CDL-086 |" in line]
    assert len(lines) == 1
    row = lines[0]
    assert "| ratified |" in row
    assert "ratified_phase: 1220" in row
    assert "cdl_086_ratified_phase_1220" in row
    assert "public launch" in row.lower()


def test_ratification_evidence_records_token_and_phase_1213_artifacts() -> None:
    text = EVIDENCE.read_text(encoding="utf-8")
    assert "cdl_086_ratified_phase_1220" in text
    assert "release_artifact_manifest_schema_committed_phase_1213" in text
    assert "distribution_channel_integrity_checklist_committed_phase_1213" in text


def test_ratification_evidence_disposes_all_nine_prelock_conditions() -> None:
    text = EVIDENCE.read_text(encoding="utf-8")
    for number in range(1, 10):
        assert f"| {number} |" in text
    assert "All 9 prelock conditions" not in text
    assert "Prelock Condition Disposition" in text


def test_counsel_disposition_all_five_items_recorded_as_provisional() -> None:
    disposition = DISPOSITION.read_text(encoding="utf-8")
    evidence = EVIDENCE.read_text(encoding="utf-8")
    assert "GENESIS-AUTHORIZED PROVISIONAL DISPOSITIONS" in disposition
    assert "NOT COUNSEL-APPROVED LEGAL CONCLUSIONS" in disposition
    for item in ("C1", "C2", "C3", "C4", "C5"):
        assert item in disposition
        assert item in evidence
    assert "MIT for all zones at public" in disposition
    assert "release\" is explicitly rejected" in disposition
    assert "explicitly rejected" in disposition


def test_ratification_does_not_authorize_public_launch_or_runtime_change() -> None:
    text = EVIDENCE.read_text(encoding="utf-8")
    assert "does not authorize" in text
    assert "public repository publication" in text
    assert "public release artifact distribution" in text
    assert "runtime mutation" in text
    assert "v0.2 signing" in text


def test_phase_1220_walkthrough_status_and_planning_updated() -> None:
    walkthrough = WALKTHROUGH.read_text(encoding="utf-8")
    status = STATUS.read_text(encoding="utf-8")
    planning = PLANNING.read_text(encoding="utf-8")
    assert "**Status:** complete" in walkthrough
    assert "cdl_086_ratified_phase_1220" in walkthrough
    assert "## Phase 1220" in status
    assert "cdl_086_ratified_phase_1220" in status
    assert "Phase 1220 complete" in planning
