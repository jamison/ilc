from pathlib import Path


WALKTHROUGH = Path("docs/phases/phase_1193_v0_2_signing_ceremony_walkthrough.md")
STATUS = Path("docs/phases/STATUS.md")
PLANNING_INDEX = Path("docs/PLANNING_INDEX.md")


def test_phase_1193_skip_token_in_walkthrough() -> None:
    content = WALKTHROUGH.read_text(encoding="utf-8")
    assert "**Status:** complete" in content
    assert "v0_2_signing_ceremony_deferred_pending_signing_authorization" in content


def test_phase_1193_skip_recorded_in_status() -> None:
    content = STATUS.read_text(encoding="utf-8")
    assert "## Phase 1193" in content
    assert "v0_2_signing_ceremony_deferred_pending_signing_authorization" in content
    assert "no release key was generated or registered" in content


def test_planning_index_advances_to_phase_1194_gate() -> None:
    content = PLANNING_INDEX.read_text(encoding="utf-8")
    assert "Window 1191-1199 is IN PROGRESS through Phase 1193" in content
    assert "Phase 1194 CDL-086 public-launch packaging blocker opening" in content


def test_no_phase_1193_release_envelope_exists() -> None:
    release_like = list(Path("out").glob("*1193*release*")) + list(
        Path("docs/specs").glob("*1193*signing*")
    )
    assert release_like == []
