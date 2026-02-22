from __future__ import annotations

from pathlib import Path


SEQUENCE_LOCK_PATH = Path("docs/specs/ilc_phase_260_269_sequence_lock_v0.1.md")


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_sequence_lock_exists() -> None:
    assert SEQUENCE_LOCK_PATH.exists()


def test_required_section_headings_present() -> None:
    text = _read(SEQUENCE_LOCK_PATH)
    headings = [
        "## 1. Purpose and sequence scope",
        "## 2. Dependency baseline and entry gate",
        "## 3. Locked phase table (260-269)",
        "## 4. Per-phase sensitivity classification",
        "## 5. Mandatory entry/exit gates per lane",
        "## 6. Ratification mutation-scope guardrail prerequisite",
        "## 7. Non-goals and out-of-scope boundaries",
        "## 8. Forward pointer and carry-forward debt list",
    ]
    for heading in headings:
        assert heading in text


def test_locked_phase_table_mentions_260_through_269() -> None:
    text = _read(SEQUENCE_LOCK_PATH)
    for phase in range(260, 270):
        assert f"| {phase} |" in text


def test_locked_phase_table_has_required_column_order() -> None:
    text = _read(SEQUENCE_LOCK_PATH)
    assert "| Step | Phase | Lane type | Objective | Dependencies | Exit gate |" in text


def test_267_268_269_marked_sensitive() -> None:
    text = _read(SEQUENCE_LOCK_PATH)
    assert "| 267 | sensitive |" in text
    assert "| 268 | sensitive |" in text
    assert "| 269 | sensitive |" in text


def test_section_six_includes_guardrail_and_allowed_fields() -> None:
    text = _read(SEQUENCE_LOCK_PATH)
    assert "Before any Phase 260+ ratification lane" in text
    for field in ["status", "ratified_phase", "ratified_date", "evidence_document"]:
        assert field in text


def test_no_phase_260_cdl_mutation_execution_language() -> None:
    text = _read(SEQUENCE_LOCK_PATH)
    assert "No CDL status mutation in this phase." in text


def test_no_ilc_core_paths_as_phase_260_deliverables() -> None:
    text = _read(SEQUENCE_LOCK_PATH)
    line = next(
        l for l in text.splitlines() if l.startswith("- No `ilc_core/` runtime behavior changes in this phase.")
    )
    assert "ilc_core" in line
