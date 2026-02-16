from pathlib import Path


CANON_PATH = Path("docs/architecture/ilc_canonical_glossary_and_concepts_v0.2.md")
REFERENCE_PATH = Path("docs/reference/ilc_comprehensive_reference_glossary_v0.1.md")
SPEC_PATH = Path("docs/specs/ilc_governance_economics_near_term_contracts_v0.1.md")


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_phase_994_spec_exists_and_scoped_terms_present() -> None:
    text = _read(SPEC_PATH)
    assert "ILC Governance and Economics Near-Term Contracts v0.1" in text
    for term in (
        "Quorum",
        "Slashing",
        "Token Sink",
        "Validator",
        "Reward Surface",
        "Epoch Reward Ledger",
        "Governance Config Surface",
        "Namespace Hierarchy",
    ):
        assert term in text


def test_phase_994_canonical_glossary_has_contract_section() -> None:
    text = _read(CANON_PATH)
    assert "2.9 Governance and Economics Near-Term Contracts (Phase 994)" in text
    for term in (
        "Quorum",
        "Slashing",
        "Token Sink",
        "Validator",
        "Reward Surface",
        "Epoch Reward Ledger",
        "Governance Config Surface",
        "Namespace Hierarchy",
    ):
        assert f"**{term}**" in text


def test_phase_994_reference_statuses_promoted_to_active_contract() -> None:
    text = _read(REFERENCE_PATH)
    for row in (
        "| **Quorum** | A minimum validator subset required for a decision to be considered valid. | **Canonical-adjacent (active contract)** |",
        "| **Slashing** | Economic penalty for provably bad behavior by staked actors. | **Canonical-adjacent (active contract)** |",
        "| **Token Sink** | Any mechanism that removes circulating tokens (e.g., burns, fees, lockups). | **Canonical-adjacent (active contract)** |",
        "| **Validator** | Actor/role that verifies claims, tasks, or settlement artifacts under protocol rules. | **Canonical-adjacent (active contract)** |",
        "| **Reward Surface** | Function family mapping verified work quality and policy constraints into payout outcomes. | **Canonical-adjacent (active contract)** |",
        "| **Epoch Reward Ledger** | Per-epoch accounting surface recording validated reward events and settlement inputs. | **Canonical-adjacent (active contract)** |",
        "| **Governance Config Surface** | The explicit set of configurable governance parameters exposed for policy control and versioned evolution. | **Canonical-adjacent (active contract)** |",
        "| **Namespace Hierarchy** | Structured namespace layering used for governance boundaries, compatibility, and modular extension. | **Canonical-adjacent (active contract)** |",
    ):
        assert row in text
