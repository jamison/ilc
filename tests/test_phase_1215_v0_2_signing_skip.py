from pathlib import Path


WALKTHROUGH = Path("docs/phases/phase_1215_v0_2_signing_ceremony_walkthrough.md")
STATUS = Path("docs/phases/STATUS.md")
SIGNING_EVIDENCE = Path("docs/specs/ilc_genesis_v0_2_signing_evidence_1215_v0.1.md")


def test_phase_1215_skip_token_in_walkthrough():
    text = WALKTHROUGH.read_text(encoding="utf-8")
    assert "**Status:** complete" in text
    assert "v0_2_signing_ceremony_deferred_pending_signing_authorization" in text


def test_phase_1215_skip_recorded_in_status():
    text = STATUS.read_text(encoding="utf-8")
    assert "## Phase 1215" in text
    assert "v0_2_signing_ceremony_deferred_pending_signing_authorization" in text
    assert "No signing ceremony executed" in text


def test_no_phase_1215_signing_evidence_created():
    assert not SIGNING_EVIDENCE.exists()
