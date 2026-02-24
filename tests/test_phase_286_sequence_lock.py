"""Contract tests for Phase 286 sequence lock artifact."""

from pathlib import Path

ARTIFACT_PATH = Path("docs/specs/ilc_phase_286_295_sequence_lock_v0.1.md")


def _read() -> str:
    return ARTIFACT_PATH.read_text(encoding="utf-8")


def test_artifact_exists() -> None:
    assert ARTIFACT_PATH.exists()


def test_required_sections_present() -> None:
    text = _read()
    for heading in (
        "## 1. Purpose and sequence scope",
        "## 2. Entry state from Phase 285 crypto completion",
        "## 3. Locked phase table (286-295) plus prerequisite lane note",
        "## 4. Per-phase sensitivity classification",
        "## 5. CDL dependency map and ratification ordering",
        "## 6. Mandatory entry/exit gates per lane",
        "## 7. Non-goals and out-of-scope boundaries",
        "## 8. Forward pointer to Phase 296+",
    ):
        assert heading in text


def test_phase_table_covers_286_to_295() -> None:
    text = _read()
    for phase in range(286, 296):
        assert f"Phase {phase}" in text


def test_prerequisite_lane_280_pre1_before_287() -> None:
    text = _read()
    idx_pre = text.find("Phase 280-pre1")
    idx_287 = text.find("Phase 287")
    assert idx_pre != -1
    assert idx_287 != -1
    assert idx_pre < idx_287


def test_sensitive_classification_includes_required_lanes() -> None:
    text = _read()
    for lane in ("Phase 288", "Phase 289", "Phase 291", "Phase 294", "Phase 295"):
        assert f"| {lane} | Sensitive |" in text


def test_phase_287_is_non_sensitive() -> None:
    text = _read()
    assert "| Phase 287 | Non-sensitive |" in text


def test_no_ratification_in_phase_286() -> None:
    text = _read()
    assert "No CDL ratification occurs in Phase 286." in text
