"""Phase 1420 copyright counsel disposition tests."""

from __future__ import annotations

from pathlib import Path

from ilc_core.epistemic.jury_activation_gate import (
    GateConditionStatus,
    evaluate_jury_activation_gate,
)

REPO = Path(__file__).resolve().parents[1]
ARTIFACT = REPO / "docs/specs/ilc_copyright_counsel_disposition_1420_v0.1.md"
GATE_SOURCE = REPO / "ilc_core/epistemic/jury_activation_gate.py"


def _artifact_text() -> str:
    assert ARTIFACT.exists()
    return ARTIFACT.read_text(encoding="utf-8")


def test_phase_1420_artifact_contains_required_tokens() -> None:
    text = _artifact_text()

    for token in (
        "copyright_counsel_disposition_complete_phase_1420",
        "self_counsel_verbatim_storage_boundary_phase_1420",
        "self_counsel_d2d_distribution_boundary_phase_1420",
        "copyright_counsel_not_external_legal_opinion_phase_1420",
        "license_not_public_before_repo_authorized_public_phase_1420",
    ):
        assert token in text


def test_artifact_states_self_counsel_not_external_opinion() -> None:
    text = _artifact_text()

    assert "Genesis-authority self-counsel decision" in text
    assert "not an external legal opinion" in text
    assert "not attorney sign-off" in text
    assert "not commercial legal advice" in text


def test_artifact_addresses_all_adr_0041_sub_questions() -> None:
    text = _artifact_text()

    assert "### 1. Verbatim Full-Text Storage" in text
    assert "### 2. D2D Distribution And Serve-Credit" in text
    assert "### 3. Fair-Use, Fair-Dealing, Research, And TDM Exceptions" in text


def test_verbatim_storage_boundary_is_conservative() -> None:
    text = _artifact_text()

    assert "must not store verbatim full-text bytes" in text
    assert "Absent one of those documented conditions" in text
    assert "deferred to a separately counsel-cleared path" in text
    for condition in (
        "project owns the relevant rights",
        "public domain",
        "explicit license",
        "open-access",
        "later external legal review",
    ):
        assert condition in text


def test_d2d_distribution_boundary_does_not_authorize_verbatim_distribution() -> None:
    text = _artifact_text()

    assert "does not authorize verbatim D2D distribution" in text
    assert "Verbatim third-party copyrighted bytes must not be distributed" in text
    assert "separately cleared by license evidence" in text


def test_fair_use_and_tdm_are_not_blanket_authorizations() -> None:
    text = _artifact_text()

    assert "no blanket fair-use" in text
    assert "no blanket fair-use, fair-dealing, research-exemption, or" in text
    assert "must not rely on a generic fair-use, research, or" in text
    assert "rights reservations or opt-outs" in text


def test_license_publication_boundary_preserved() -> None:
    text = _artifact_text()

    assert "The license must not go public before the repository is authorized public" in text
    assert "does not publish the repository" in text
    assert "public license" in text


def test_gate_source_not_patched_by_phase_1420() -> None:
    source = GATE_SOURCE.read_text(encoding="utf-8")
    report = evaluate_jury_activation_gate()
    condition = next(
        c for c in report.conditions if c.condition_id == "COPYRIGHT_COUNSEL_DISPOSITION"
    )

    assert condition.status is GateConditionStatus.NOT_MET
    assert "counsel track: no disposition recorded" in source


def test_official_reference_links_are_recorded() -> None:
    text = _artifact_text()

    assert "https://www.copyright.gov/fair-use/" in text
    assert (
        "https://digital-strategy.ec.europa.eu/en/faqs/"
        "stakeholder-consultation-ai-and-copyright-compliance"
    ) in text
