"""ADR-0008 reconciliation cleanup regression."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ADR_PATH = ROOT / "docs/adr/ADR_0008_Node_Usefulness_vs_Governance_Weight_and_Genesis_Dilution.md"


def _adr_text() -> str:
    return ADR_PATH.read_text(encoding="utf-8")


def test_adr_0008_records_reconciliation_scope_without_accepting_status() -> None:
    # ADR-0008 was accepted (Status changed from Proposed → Accepted after Phase 600
    # closure gates resolved all open issues). The "Scope of Acceptance" section must
    # still be present — acceptance was scoped to the architectural boundary claim,
    # not to every numeric parameter.
    text = _adr_text()
    assert "Status: Accepted" in text
    assert "## Scope of Acceptance" in text
    assert "not every numeric" in text
    assert "score parameter" in text


def test_adr_0008_links_later_genesis_closure_phases() -> None:
    text = _adr_text()
    for phase_doc in (
        "ilc_genesis_governance_dilution_and_brake_semantics_closure_597_v0.1.md",
        "ilc_freshness_gate_provenance_and_genesis_exemption_closure_598_v0.1.md",
        "ilc_genesis_accrual_governor_provenance_reconciliation_599_v0.1.md",
        "ilc_deterministic_genesis_economics_evidence_and_parameter_closure_600_v0.1.md",
    ):
        assert phase_doc in text


def test_adr_0008_dispositions_former_open_issues() -> None:
    text = _adr_text()
    assert "## Disposition of Former Open Issues" in text
    assert "Status: deferred." in text
    assert "Status: closed by Phase 597." in text
    assert "governance side closed by Phase 597; economic side closed by" in text
    assert "Status: closed by Phase 598." in text


def test_adr_0008_does_not_launder_genesis_privilege_or_coefficients() -> None:
    text = _adr_text()
    assert "no standing Genesis governance baseline or contribution bonus survives" in text
    assert "not a standing Genesis veto" in text
    assert "does not" in text
    assert "ratify them as final constitutional coefficients" in text
    assert "not a governance bonus" in text
