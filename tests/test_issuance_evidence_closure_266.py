from __future__ import annotations

from pathlib import Path


EVIDENCE_PATH = Path("docs/specs/ilc_issuance_evidence_closure_a_266_v0.1.md")
RECON_PATH = Path("docs/specs/ilc_genesis_accrual_reconciliation_8pct_vs_theta_hard_266_v0.1.md")


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_artifacts_exist() -> None:
    assert EVIDENCE_PATH.exists()
    assert RECON_PATH.exists()


def test_issuance_closure_artifact_has_required_sections() -> None:
    text = _read(EVIDENCE_PATH)
    headings = [
        "## 1. Purpose and scope",
        "## 2. CDL-025 evidence closure summary",
        "## 3. CDL-029 evidence closure summary",
        "## 4. Evidence matrix (available evidence vs remaining evidence)",
        "## 5. Ratification readiness recommendation for Phase 267+",
        "## 6. Non-goals",
        "## 7. Canonical anchors",
    ]
    for heading in headings:
        assert heading in text


def test_reconciliation_artifact_has_required_sections() -> None:
    text = _read(RECON_PATH)
    headings = [
        "## 1. Problem statement",
        "## 2. Metric-surface distinction",
        "## 3. Compatibility framing and assumptions",
        "## 4. Open questions and next ratification-lane requirements",
        "## 5. Canonical anchors",
    ]
    for heading in headings:
        assert heading in text


def test_issuance_artifact_references_cdl_025_and_cdl_029() -> None:
    text = _read(EVIDENCE_PATH)
    assert "CDL-025" in text
    assert "CDL-029" in text


def test_reconciliation_mentions_required_constants() -> None:
    text = _read(RECON_PATH)
    assert "8%" in text
    assert "theta_hard = 1/20" in text
    assert "theta_soft = exp(-3)" in text


def test_artifacts_include_non_ratification_language() -> None:
    evidence = _read(EVIDENCE_PATH)
    recon = _read(RECON_PATH)
    assert "does not ratify" in evidence
    assert "remain unratified" in evidence
    assert "does not itself pick or ratify policy values" in recon


def test_artifacts_do_not_claim_cdl_status_mutation_execution() -> None:
    evidence = _read(EVIDENCE_PATH).lower()
    recon = _read(RECON_PATH).lower()
    forbidden = [
        "status mutated",
        "ratified_phase set",
        "ratified_date set",
        "evidence_document set",
    ]
    for token in forbidden:
        assert token not in evidence
        assert token not in recon
