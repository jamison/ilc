from __future__ import annotations

from pathlib import Path


SURVEY_PATH = Path("docs/specs/ilc_issuance_governance_activation_survey_247_v0.1.md")

REQUIRED_SECTIONS = [
    "## 1. Scope and window anchor",
    "## 2. Per-CDL assessment (CDL-025 through CDL-031)",
    "## 3. Dependency graph narrative",
    "## 4. Non-goal boundaries",
    "## 5. Forward pointer",
]


CDL_IDS = [
    "CDL-025",
    "CDL-026",
    "CDL-027",
    "CDL-028",
    "CDL-029",
    "CDL-030",
    "CDL-031",
]


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_phase_247_survey_file_exists() -> None:
    assert SURVEY_PATH.exists()


def test_phase_247_required_sections_present() -> None:
    text = _read(SURVEY_PATH)
    for section in REQUIRED_SECTIONS:
        assert section in text


def test_phase_247_all_cdl_entries_present_in_assessment() -> None:
    text = _read(SURVEY_PATH)
    for cdl_id in CDL_IDS:
        assert cdl_id in text


def test_phase_247_references_phase_233_artifact() -> None:
    text = _read(SURVEY_PATH)
    assert "docs/specs/ilc_issuance_governance_plan_233_v0.1.md" in text


def test_phase_247_explicit_runtime_constraint_drift_statement_present() -> None:
    text = _read(SURVEY_PATH)
    assert "No constraint drift detected from Phase 241-244 runtime work" in text


def test_phase_247_has_no_ratification_language() -> None:
    text = _read(SURVEY_PATH).lower()
    forbidden = [
        "is hereby ratified",
        "ratified in this phase",
        "this phase ratifies",
        "status changed to ratified",
    ]
    for token in forbidden:
        assert token not in text
