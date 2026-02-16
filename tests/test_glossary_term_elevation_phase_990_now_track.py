from pathlib import Path


CANON_PATH = Path("docs/architecture/ilc_canonical_glossary_and_concepts_v0.2.md")
REFERENCE_PATH = Path("docs/reference/ilc_comprehensive_reference_glossary_v0.1.md")
SPEC_PATH = Path("docs/specs/ilc_protocol_runtime_term_contracts_v0.1.md")


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_phase_990_spec_exists_and_scoped_terms_present() -> None:
    text = _read(SPEC_PATH)
    assert "ILC Protocol and Runtime Term Contracts v0.1" in text
    for term in (
        "Node ID",
        "Canonical Encoding",
        "Deterministic CBOR",
        "Consensus Engine",
        "Node Indexing",
    ):
        assert term in text


def test_phase_990_canonical_glossary_has_contract_section() -> None:
    text = _read(CANON_PATH)
    assert "2.6 Protocol and Runtime Contracts (Phase 990)" in text
    for term in (
        "Node ID",
        "Canonical Encoding",
        "Deterministic CBOR",
        "Consensus Engine",
        "Node Indexing",
    ):
        assert f"**{term}**" in text


def test_phase_990_reference_statuses_promoted_to_active_contract() -> None:
    text = _read(REFERENCE_PATH)
    assert (
        "| **Node ID** | Deterministic identifier used to reference a Graph Node "
        "across serialization, validation, and replay boundaries. | "
        "**Canonical-adjacent (active contract)** |"
    ) in text
    assert (
        "| **Canonical Encoding** | Deterministic serialization constraints that "
        "ensure identical content hashes and replay outcomes across implementations. | "
        "**Canonical-adjacent (active contract)** |"
    ) in text
    assert (
        "| **Deterministic CBOR** | CBOR encoding profile constrained for stable "
        "byte output and cross-runtime hash parity. | "
        "**Canonical-adjacent (active contract)** |"
    ) in text
    assert (
        "| **Consensus Engine** | Runtime component that applies validation and "
        "settlement rules to produce accepted state transitions. | "
        "**Canonical-adjacent (active contract)** |"
    ) in text
    assert (
        "| **Node Indexing** | Index structures that accelerate retrieval/traversal "
        "compared with full-scan edge walks. | "
        "**Canonical-adjacent (active contract)** |"
    ) in text
