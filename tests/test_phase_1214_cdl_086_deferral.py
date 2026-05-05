from pathlib import Path


WALKTHROUGH = Path("docs/phases/phase_1214_cdl_086_ratification_walkthrough.md")
STATUS = Path("docs/phases/STATUS.md")
RATIFICATION_EVIDENCE = Path("docs/specs/ilc_cdl_086_ratification_evidence_1214_v0.1.md")


def test_phase_1214_deferral_token_in_walkthrough():
    text = WALKTHROUGH.read_text(encoding="utf-8")
    assert "**Status:** complete" in text
    assert "cdl_086_ratification_deferred_pending_counsel_disposition" in text


def test_phase_1214_deferral_recorded_in_status():
    text = STATUS.read_text(encoding="utf-8")
    assert "## Phase 1214" in text
    assert "cdl_086_ratification_deferred_pending_counsel_disposition" in text
    assert "No CDL register mutation" in text


def test_no_phase_1214_ratification_evidence_created():
    assert not RATIFICATION_EVIDENCE.exists()
