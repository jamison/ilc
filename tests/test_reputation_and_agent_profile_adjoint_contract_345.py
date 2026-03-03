from __future__ import annotations

from pathlib import Path


ARTIFACT_PATH = Path("docs/specs/ilc_reputation_and_agent_profile_adjoint_contract_345_v0.1.md")


def _read() -> str:
    return ARTIFACT_PATH.read_text(encoding="utf-8")


def test_artifact_exists_and_has_required_headings() -> None:
    assert ARTIFACT_PATH.exists()
    text = _read()
    for heading in (
        "## 1. Purpose and scope",
        "## 2. How reputation is derived",
        "## 3. Global integrity vs domain-scoped competency",
        "## 4. Agent Profile and derived trust data",
        "## 5. Forbidden patterns and boundary constraints",
        "## 6. CDL decision: does reputation require its own lane in Window 348+?",
        "## 7. Carry-forward constraints",
    ):
        assert heading in text


def test_derivation_and_non_inline_reputation_tokens_are_present() -> None:
    text = _read()
    for token in (
        "Reputation is derived from lifecycle outputs, not from a direct score field.",
        "Reputation is downstream of lifecycle semantics, not a constitutional primitive.",
        "derive it from graph history",
        "Mutable inline node-level reputation fields remain explicitly forbidden.",
        "Authored payload mutation is barred by CDL-034; reputation cannot be embedded there.",
        "docs/specs/ilc_cdl_034_node_schema_core_envelope_and_reserved_fields_evidence_prelock_340_v0.1.md",
        "docs/specs/ilc_cdl_035_validation_lifecycle_and_gate_verdict_attachment_evidence_prelock_341_v0.1.md",
        "docs/specs/ilc_cdl_038_private_to_public_promotion_and_promotion_receipt_evidence_prelock_344_v0.1.md",
        "docs/specs/ilc_node_schema_concretization_proposals_v0.1.md",
        "docs/specs/ilc_phase_338_347_sequence_lock_v0.1.md",
    ):
        assert token in text


def test_global_integrity_domain_competency_and_agent_profile_tokens_are_present() -> None:
    text = _read()
    for token in (
        "global integrity",
        "domain-scoped competency",
        "Agent Profile",
        "Quorum Record-adjacent attestation objects",
        "reputation gates panel eligibility and may weight reviewer selection",
        "Reputation should influence who gets trusted to evaluate, not what is true.",
    ):
        assert token in text


def test_forbidden_pattern_and_boundary_tokens_are_present() -> None:
    text = _read()
    for token in (
        "The L-tier ladder should not become a disguised reputation ladder.",
        "do not lock quorum thresholds for reputation",
        "do not treat L-tier quorum levels as reputation tiers",
        "do not embed CDL-V3 diversity criteria as implicit reputation defaults",
        "do not create a de facto reputation CDL without opening one explicitly",
    ):
        assert token in text


def test_binary_verdict_and_carry_forward_tokens_are_correct() -> None:
    text = _read()
    expected = "Reputation adjunct contract is sufficient; no dedicated CDL lane is required in Window 348+."
    rejected = "Reputation warrants a dedicated CDL lane; Window 348+ should open CDL-039."
    assert expected in text
    assert rejected not in text
    assert text.count(expected) == 1
    assert "Phase 346 coherence report must incorporate this adjoint contract verdict." in text
    assert "No decision-log mutation occurs in Phase 345." in text
    assert "No runtime implementation occurs in Phase 345." in text
