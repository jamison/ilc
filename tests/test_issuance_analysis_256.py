from __future__ import annotations

from pathlib import Path


ANALYSIS_PATH = Path("docs/specs/ilc_issuance_parameter_analysis_256_v0.1.md")


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_phase_256_analysis_document_exists() -> None:
    assert ANALYSIS_PATH.exists()


def test_phase_256_per_cdl_assessment_covers_025_through_031() -> None:
    text = _read(ANALYSIS_PATH)
    for cdl in range(25, 32):
        assert f"CDL-0{cdl}" in text


def test_phase_256_contains_ordering_and_modeling_sections() -> None:
    text = _read(ANALYSIS_PATH)
    assert "## 3. Recommended ratification ordering" in text
    assert "## 4. Simulation and modeling requirements" in text


def test_phase_256_contains_cdl_019_closure_assessment() -> None:
    text = _read(ANALYSIS_PATH)
    assert "## 6. CDL-019 closure assessment" in text
    assert "Recommendation:" in text


def test_phase_256_references_phase_247_and_phase_233_artifacts() -> None:
    text = _read(ANALYSIS_PATH)
    assert "docs/specs/ilc_issuance_governance_activation_survey_247_v0.1.md" in text
    assert "docs/specs/ilc_issuance_governance_plan_233_v0.1.md" in text


def test_phase_256_no_ratification_execution_or_status_mutation_language() -> None:
    text = _read(ANALYSIS_PATH).lower()
    forbidden = [
        "is hereby ratified",
        "ratified in this phase",
        "this phase ratifies",
        "status changed to ratified",
        "set status to ratified",
    ]
    for token in forbidden:
        assert token not in text
