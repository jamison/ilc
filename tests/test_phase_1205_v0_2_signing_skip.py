from pathlib import Path


WALKTHROUGH = Path("docs/phases/phase_1205_v0_2_signing_ceremony_walkthrough.md")
STATUS = Path("docs/phases/STATUS.md")
PLANNING_INDEX = Path("docs/PLANNING_INDEX.md")


def test_phase_1205_skip_token_in_walkthrough() -> None:
    content = WALKTHROUGH.read_text(encoding="utf-8")
    assert "**Status:** complete" in content
    assert "v0_2_signing_ceremony_deferred_pending_signing_authorization" in content


def test_phase_1205_skip_recorded_in_status() -> None:
    content = STATUS.read_text(encoding="utf-8")
    assert "## Phase 1205" in content
    assert "v0_2_signing_ceremony_deferred_pending_signing_authorization" in content
    assert "no release key was generated or registered" in content


def test_planning_index_advances_to_phase_1206() -> None:
    content = PLANNING_INDEX.read_text(encoding="utf-8")
    assert "Window 1200-1208 is IN PROGRESS through Phase 1205" in content
    assert "Phase 1206 truth-primitive permanence governance" in content


def test_no_phase_1205_release_envelope_exists() -> None:
    release_like = list(Path("out").glob("*1205*release*")) + list(
        Path("docs/specs").glob("*1205*signing*")
    )
    assert release_like == []
