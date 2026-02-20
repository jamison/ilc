from __future__ import annotations

from pathlib import Path


SPEC_PATH = Path("docs/specs/ilc_d2e_pipeline_scaffolding_spec_v0.1.md")


REQUIRED_SECTIONS = [
    "## 1. Purpose and scope",
    "## 2. Layer mapping",
    "## 3. Pipeline stage definitions",
    "## 4. Pre-conditions and ordering constraints",
    "## 5. Explicit deferred boundaries",
    "## 6. Carry-forward and non-goal statement",
]


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_phase_246_spec_exists() -> None:
    assert SPEC_PATH.exists()


def test_phase_246_spec_has_required_sections_1_to_6() -> None:
    text = _read(SPEC_PATH)
    for section in REQUIRED_SECTIONS:
        assert section in text


def test_phase_246_spec_has_adm_001_v0_2_anchor() -> None:
    text = _read(SPEC_PATH)
    assert "docs/specs/ilc_adm_001_protocol_native_bundle_distribution_v0.2.md" in text


def test_phase_246_spec_has_explicit_deferred_d3_d4_d5_boundaries() -> None:
    text = _read(SPEC_PATH)
    assert "D3" in text
    assert "D4" in text
    assert "D5" in text


def test_phase_246_spec_has_no_ratification_language() -> None:
    text = _read(SPEC_PATH).lower()
    forbidden = [
        "is hereby ratified",
        "ratified in this phase",
        "this phase ratifies",
        "status changed to ratified",
    ]
    for token in forbidden:
        assert token not in text
