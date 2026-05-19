"""Phase 1387d — ADR-0035 Homoiconic Type Definition System formal spec.

Tests verify:
- ADR-0035 formal doc exists at docs/adr/ADR_0035_*.md
- Governance tokens are present
- All three Phase-1387b deferral questions are resolved (§3.1 / §3.2 / §3.3)
- Forward obligations section is present
- Interaction matrix references key ADRs (0004, 0029, 0030)
- Working spec cross-reference is present
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).parent.parent
ADR_DIR = ROOT / "docs" / "adr"
ADR_0035 = ADR_DIR / "ADR_0035_Homoiconic_Type_Definition_System.md"


def _text() -> str:
    return ADR_0035.read_text()


def test_adr_0035_file_exists() -> None:
    assert ADR_0035.exists(), "ADR_0035_Homoiconic_Type_Definition_System.md not found"


def test_adr_0035_direction_accepted_token() -> None:
    assert "adr_0035_homoiconic_type_definition_system_direction_accepted" in _text()


def test_adr_0035_deferred_pending_cdl_token() -> None:
    assert "adr_0035_implementation_deferred_pending_cdl" in _text()


def test_adr_0035_type_regress_resolved() -> None:
    """§3.1 — type regress question answered: type_definition is hardcoded meta-type."""
    text = _text()
    assert "type_definition" in text, "type_definition primitive not mentioned"
    assert "regress" in text.lower(), "regress question not addressed"


def test_adr_0035_adr_0030_relationship_resolved() -> None:
    """§3.2 — relationship to ADR-0030 content_type tokens resolved."""
    text = _text()
    assert "ADR-0030" in text, "ADR-0030 not referenced"
    assert "content_type" in text, "content_type not discussed"


def test_adr_0035_popperian_claim_form_resolved() -> None:
    """§3.3 — Popperian claim-form for type-level nodes resolved."""
    text = _text()
    assert "Popperian" in text or "popperian" in text.lower(), (
        "Popperian evaluation not discussed"
    )
    # Must distinguish type-level from instance-level claims
    assert "instance" in text.lower(), "instance-level claim distinction not present"


def test_adr_0035_compositional_primitive_basis() -> None:
    """§4.3 — decomposition_recipe / compositional primitive basis constraint present."""
    text = _text()
    assert "decomposition_recipe" in text, "decomposition_recipe constraint not present"
    assert "irreducible" in text, "irreducible flag not mentioned"


def test_adr_0035_forward_obligations_section() -> None:
    text = _text()
    assert "Forward Obligations" in text or "forward obligation" in text.lower()


def test_adr_0035_references_adr_0004() -> None:
    assert "ADR-0004" in _text(), "ADR-0004 (truth primitives) not referenced"


def test_adr_0035_references_adr_0029() -> None:
    assert "ADR-0029" in _text(), "ADR-0029 (hypergraph substrate) not referenced"


def test_adr_0035_references_adr_0030() -> None:
    assert "ADR-0030" in _text(), "ADR-0030 (content typing) not referenced"


def test_adr_0035_working_spec_cross_reference() -> None:
    """ADR-0035 must reference its working spec document."""
    assert "ilc_adr_0035_homoiconic_type_definition_system_v0.1.md" in _text(), (
        "Working spec cross-reference not found in ADR"
    )


def test_adr_0035_retroactivity_rule_present() -> None:
    """Snapshot semantics for amendment retroactivity must be stated."""
    text = _text()
    assert "retroact" in text.lower() or "snapshot" in text.lower(), (
        "Retroactivity / snapshot semantics not addressed"
    )


def test_adr_0035_non_attributable_definition_nodes() -> None:
    """Definition nodes must be declared non-attributable (infrastructure, not content)."""
    assert "non-attributable" in _text() or "Non-attributable" in _text()


def test_phase_1387d_token() -> None:
    """Phase 1387d token must appear in this ADR."""
    assert "1387d" in _text(), "Phase 1387d token not found in ADR-0035"
