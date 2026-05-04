"""Phase 1154 — Pre-public-RC obligations synthesis."""

from __future__ import annotations

import pathlib


ROOT = pathlib.Path(__file__).resolve().parents[1]


def _read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_obligations_synthesis_exists_with_token() -> None:
    text = _read("docs/specs/ilc_pre_public_rc_obligations_synthesis_1154_v0.1.md")
    assert "pre_public_rc_obligations_synthesis_committed_phase_1154" in text


def test_required_phase_1146_obligations_are_registered() -> None:
    text = _read("docs/specs/ilc_pre_public_rc_obligations_synthesis_1154_v0.1.md")
    for token in (
        "genesis_canonical_lineage_contract_required_before_public_rc",
        "truth_primitive_permanence_requires_community_ratification_before_genesis_sunset",
        "public_rc_envelope_hash_transition_policy_required",
        "contributor_agreement_required_before_public_repo",
    ):
        assert token in text


def test_adr_acceptance_and_tier2_signing_gaps_are_registered() -> None:
    text = _read("docs/specs/ilc_pre_public_rc_obligations_synthesis_1154_v0.1.md")
    assert "adr_0008_tier2_blocked_status_proposed_not_accepted" in text
    assert "adr_0020_acceptance_review_priority_before_tier3_embedding_linkage" in text
    assert "Atlas Tier-2 signing ceremony" in text


def test_counsel_track_is_registered_without_legal_conclusions() -> None:
    text = _read("docs/specs/ilc_pre_public_rc_obligations_synthesis_1154_v0.1.md")
    assert "counsel track" in text
    assert "makes no legal recommendation" in text
    assert "select license terms" in text


def test_canon_bundle_failures_are_carried_forward() -> None:
    text = _read("docs/specs/ilc_pre_public_rc_obligations_synthesis_1154_v0.1.md")
    assert "test_canon_bundle_audit_artifact.py" in text
    assert "test_canon_bundle_pipeline_report.py" in text


def test_non_claims_prevent_scope_creep() -> None:
    text = _read("docs/specs/ilc_pre_public_rc_obligations_synthesis_1154_v0.1.md")
    assert "open or ratify any CDL" in text
    assert "accept any proposed ADR" in text
    assert "authorize Phase 1156 signing" in text
