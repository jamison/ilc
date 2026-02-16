from pathlib import Path


CANON_PATH = Path("docs/architecture/ilc_canonical_glossary_and_concepts_v0.2.md")
REFERENCE_PATH = Path("docs/reference/ilc_comprehensive_reference_glossary_v0.1.md")
SPEC_PATH = Path("docs/specs/ilc_near_prep_non_governance_term_contracts_v0.1.md")


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_phase_992_spec_exists_and_scoped_terms_present() -> None:
    text = _read(SPEC_PATH)
    assert "ILC Near-Prep Non-Governance Term Contracts v0.1" in text
    for term in ("Canonical JSON", "Convergent Consensus", "Node Load Metrics"):
        assert term in text


def test_phase_992_canonical_glossary_has_pre_alignment_section() -> None:
    text = _read(CANON_PATH)
    assert "2.8 Near-Term Non-Governance Pre-Alignment Contracts (Phase 992)" in text
    for term in ("Canonical JSON", "Convergent Consensus", "Node Load Metrics"):
        assert f"**{term}**" in text


def test_phase_992_reference_statuses_mark_pre_alignment() -> None:
    text = _read(REFERENCE_PATH)
    assert (
        "| **Convergent Consensus** | Consensus framing where independent validators "
        "converge on equivalent outcomes. | "
        "**Discussed (near-prealigned contract)** |"
    ) in text
    assert (
        "| **Canonical JSON** | JSON normalization discipline used where CBOR is "
        "unavailable, preserving deterministic field/value interpretation. | "
        "**Canonical-adjacent (near-prealigned contract)** |"
    ) in text
    assert (
        "| **Node Load Metrics** | Runtime load measurements (for example compute, "
        "queue, throughput) used in balancing and policy tuning. | "
        "**Canonical-adjacent (near-prealigned contract)** |"
    ) in text
