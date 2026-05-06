from pathlib import Path


WALKTHROUGH = Path("docs/phases/phase_1230_v0_2_signing_ceremony_walkthrough.md")
STATUS = Path("docs/phases/STATUS.md")
SIGNING_EVIDENCE = Path("docs/specs/ilc_genesis_v0_2_signing_evidence_1230_v0.1.md")


def test_phase_1230_skip_recorded_in_walkthrough() -> None:
    text = WALKTHROUGH.read_text(encoding="utf-8")
    assert "**Status:** complete" in text
    assert "v0_2_signing_ceremony_deferred_pending_signing_authorization" in text
    assert "No signing ceremony executed" in text


def test_phase_1230_skip_recorded_in_status() -> None:
    text = STATUS.read_text(encoding="utf-8")
    assert "## Phase 1230" in text
    assert "v0_2_signing_ceremony_deferred_pending_signing_authorization" in text
    assert "v0.2 remains an unsigned 41-node / 73-edge candidate" in text


def test_no_phase_1230_signing_evidence_created() -> None:
    assert not SIGNING_EVIDENCE.exists()
