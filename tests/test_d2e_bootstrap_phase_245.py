from __future__ import annotations

from pathlib import Path


ADM_V2_PATH = Path("docs/specs/ilc_adm_002_cli_first_agent_sdk_v0.2.md")
ASSESSMENT_PATH = Path("docs/specs/ilc_d2e_activation_assessment_245_v0.1.md")


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_phase_245_adm_v2_exists_and_supersedes_v1() -> None:
    assert ADM_V2_PATH.exists()
    text = _read(ADM_V2_PATH)
    assert "Supersedes: `docs/specs/ilc_adm_002_cli_first_agent_sdk_v0.1.md`" in text


def test_phase_245_adm_v2_references_phase_234_sdk_boundary_contract() -> None:
    text = _read(ADM_V2_PATH)
    assert "docs/specs/ilc_sdk_boundary_contract_234_v0.1.md" in text


def test_phase_245_activation_assessment_exists() -> None:
    assert ASSESSMENT_PATH.exists()


def test_phase_245_assessment_identifies_d2_schema_blocking_for_d2e_03_plus() -> None:
    text = _read(ASSESSMENT_PATH)
    assert "D2 schema prerequisites are blocking for D2e-03 and later" in text
    assert "Node, Edge, and Epoch Record schemas" in text


def test_phase_245_assessment_references_roadmap_v0_3() -> None:
    text = _read(ASSESSMENT_PATH)
    assert "docs/specs/ilc_distribution_architecture_roadmap_v0.3.md" in text


def test_phase_245_no_ratification_language() -> None:
    text = (_read(ADM_V2_PATH) + "\n" + _read(ASSESSMENT_PATH)).lower()
    forbidden = [
        "is hereby ratified",
        "ratified in this phase",
        "this phase ratifies",
        "status changed to ratified",
    ]
    for token in forbidden:
        assert token not in text
