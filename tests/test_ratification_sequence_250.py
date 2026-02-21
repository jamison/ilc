from __future__ import annotations

from pathlib import Path


SEQUENCE_PATH = Path("docs/specs/ilc_cdl_ratification_and_d2e_activation_sequence_250_259_v0.1.md")

REQUIRED_SECTIONS = [
    "## 1. Purpose and sequence scope",
    "## 2. Dependency baseline and entry gate",
    "## 3. Locked phase table (250-259)",
    "## 4. Per-phase sensitivity classification",
    "## 5. Mandatory entry/exit gates per phase lane",
    "## 6. CDL ratification ceremony protocol",
    "## 7. Non-goals and out-of-scope boundaries",
    "## 8. Forward pointer and carry-forward debt list",
]


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_phase_250_sequence_lock_exists_with_required_sections() -> None:
    assert SEQUENCE_PATH.exists()
    text = _read(SEQUENCE_PATH)
    for section in REQUIRED_SECTIONS:
        assert section in text


def test_phase_250_section_6_contains_irrevocability_and_required_protocol_elements() -> None:
    text = _read(SEQUENCE_PATH)
    assert "## 6. CDL ratification ceremony protocol" in text
    assert "Irrevocability clause" in text
    assert "Evidence requirements" in text
    assert "CDL file mutation protocol" in text
    assert "Batch ratification rule" in text


def test_phase_250_sequence_mentions_all_10_phases() -> None:
    text = _read(SEQUENCE_PATH)
    for phase in range(250, 260):
        assert f"| {phase} |" in text


def test_phase_250_sensitivity_table_marks_251_252_253_as_sensitive() -> None:
    text = _read(SEQUENCE_PATH)
    assert "| 251 | sensitive |" in text
    assert "| 252 | sensitive |" in text
    assert "| 253 | sensitive |" in text


def test_phase_250_has_no_ratification_execution_language() -> None:
    text = _read(SEQUENCE_PATH).lower()
    forbidden = [
        "is hereby ratified",
        "ratified in this phase",
        "this phase ratifies",
        "status changed to ratified",
    ]
    for token in forbidden:
        assert token not in text


def test_phase_250_explicit_no_runtime_mutation_statement_present() -> None:
    text = _read(SEQUENCE_PATH)
    assert "No runtime behavior changes in `ilc_core/`" in text
