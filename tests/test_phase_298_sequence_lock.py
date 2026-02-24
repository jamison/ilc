"""Contract tests for Phase 298 sequence lock artifact."""

from pathlib import Path

ARTIFACT_PATH = Path("docs/specs/ilc_phase_298_307_sequence_lock_v0.1.md")


def _read() -> str:
    return ARTIFACT_PATH.read_text(encoding="utf-8")


def test_artifact_exists() -> None:
    assert ARTIFACT_PATH.exists()


def test_required_sections_present() -> None:
    text = _read()
    for heading in (
        "## 1. Purpose and sequence scope",
        "## 2. Entry state from phase-296 and phase-297 controls",
        "## 3. Locked phase table (298-307)",
        "## 4. Per-phase sensitivity classification",
        "## 5. Parallel-track dependency and synchronization map",
        "## 6. No-ratification-before-lock gate",
        "## 7. Closure-gate skeleton requirements for phase 307",
        "## 8. Non-goals and explicit boundaries",
        "## 9. Forward pointer",
    ):
        assert heading in text


def test_phase_table_covers_298_to_307() -> None:
    text = _read()
    for phase in range(298, 308):
        assert f"Phase {phase}" in text


def test_two_track_map_is_explicit() -> None:
    text = _read()
    assert "Runtime/provider track phases: `300`, `302`, `304`, `306`." in text
    assert "Schema/evidence track phases: `299`, `301`, `303`, `305`, `307`." in text


def test_no_ratification_before_lock_guard_present() -> None:
    text = _read()
    assert "No ratification lane may execute in this 298-307 window" in text
    assert "no direct CDL mutation lane is authorized by Phase 298" in text


def test_closure_gate_skeleton_declares_required_categories() -> None:
    text = _read()
    for category in (
        "Prompt contract validation category",
        "Lane-specific contract tests category",
        "Cross-phase regression category",
        "Mutation canary category",
        "CLI contract category",
        "Walkthrough hygiene category",
    ):
        assert category in text


def test_sensitive_classification_includes_runtime_and_closure_phases() -> None:
    text = _read()
    for lane in ("Phase 300", "Phase 302", "Phase 304", "Phase 306", "Phase 307"):
        assert f"| {lane} | Sensitive |" in text


def test_non_sensitive_classification_includes_lock_and_schema_phases() -> None:
    text = _read()
    for lane in ("Phase 298", "Phase 299", "Phase 301", "Phase 303", "Phase 305"):
        assert f"| {lane} | Non-sensitive |" in text
