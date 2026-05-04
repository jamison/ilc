from pathlib import Path


CDL_REGISTER = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
RATIFICATION_EVIDENCE = Path(
    "docs/specs/ilc_cdl_085_ratification_evidence_1185_v0.1.md"
)


def test_cdl_085_ratified_in_register() -> None:
    content = CDL_REGISTER.read_text(encoding="utf-8")
    assert "cdl_085_ratified_phase_1185" in content
    assert "ratified_phase: 1185" in content


def test_ratification_evidence_exists() -> None:
    assert RATIFICATION_EVIDENCE.exists()


def test_ratification_evidence_token() -> None:
    content = RATIFICATION_EVIDENCE.read_text(encoding="utf-8")
    assert "cdl_085_ratified_phase_1185" in content
    assert 'EDGE_MINT_PHI_BOUND = Decimal("0.60")' in content
