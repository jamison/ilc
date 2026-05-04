from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ADR = ROOT / "docs/adr/ADR_0036_Operational_Release_Key_Genesis_Binding.md"


def test_adr_0036_exists_and_remains_proposed() -> None:
    text = ADR.read_text(encoding="utf-8")
    assert "# ADR-0036: Operational Release Key Genesis Binding" in text
    assert "**Status:** Proposed" in text
    assert "adr_0036_release_key_draft_committed_phase_1159" in text


def test_adr_0036_keeps_lineage_contract_separate() -> None:
    text = ADR.read_text(encoding="utf-8")
    assert "genesis_canonical_lineage_contract_adr_required_separate_from_adr_0036" in text
    assert "`network_id` derivation" in text
    assert "Node 0 Merkle-inclusion proof requirements" in text


def test_adr_0036_defines_release_key_chain() -> None:
    text = ADR.read_text(encoding="utf-8")
    assert "Genesis root envelope" in text
    assert "release key registration artifact" in text
    assert "release envelope" in text
