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
        "## 6. Mandatory entry and exit gates per phase",
        "## 7. No-ratification-before-lock gate",
        "## 8. Closure-gate skeleton requirements for phase 307",
        "## 9. Non-goals and explicit boundaries",
        "## 10. Forward pointer",
    ):
        assert heading in text


def test_phase_table_covers_298_to_307() -> None:
    text = _read()
    for phase in range(298, 308):
        assert f"Phase {phase}" in text


def test_lane_table_has_strict_298_to_307_order() -> None:
    text = _read()
    section = text.split("## 3. Locked phase table (298-307)", maxsplit=1)[1]
    section = section.split("## 4. Per-phase sensitivity classification", maxsplit=1)[0]
    expected_rows = [
        "| 1 | Phase 298 |",
        "| 2 | Phase 299 |",
        "| 3 | Phase 300 |",
        "| 4 | Phase 301 |",
        "| 5 | Phase 302 |",
        "| 6 | Phase 303 |",
        "| 7 | Phase 304 |",
        "| 8 | Phase 305 |",
        "| 9 | Phase 306 |",
        "| 10 | Phase 307 |",
    ]
    last_idx = -1
    for row in expected_rows:
        idx = section.find(row)
        assert idx != -1
        assert idx > last_idx
        last_idx = idx


def test_two_track_map_is_explicit() -> None:
    text = _read()
    assert "Runtime/provider track phases: `300`, `302`, `304`, `306`." in text
    assert "Schema/evidence track phases: `299`, `301`, `303`, `305`, `307`." in text


def test_no_ratification_before_lock_guard_present() -> None:
    text = _read()
    assert "No ratification lane may execute in this 298-307 window" in text
    assert "no direct CDL mutation lane is authorized by Phase 298" in text


def test_mandatory_entry_exit_gates_exist_for_each_phase() -> None:
    text = _read()
    section = text.split("## 6. Mandatory entry and exit gates per phase", maxsplit=1)[1]
    section = section.split("## 7. No-ratification-before-lock gate", maxsplit=1)[0]
    for phase in range(298, 308):
        assert f"| Phase {phase} |" in section
    assert "Mandatory entry gate" in section
    assert "Mandatory exit gate" in section


def test_dependency_edges_are_explicit() -> None:
    text = _read()
    for edge in (
        "`299` is required before `300` begins.",
        "`301` is required before `302` begins.",
        "`303` is required before `304` begins.",
        "`305` is required before `306` begins.",
        "`306` completion evidence is required before closure in `307`.",
    ):
        assert edge in text


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
