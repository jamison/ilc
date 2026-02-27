"""Contract tests for Phase 287 CDL-031 evidence closure artifact."""

from pathlib import Path

ARTIFACT_PATH = Path("docs/specs/ilc_cdl_031_ranking_policy_evidence_closure_287_v0.1.md")


def _read() -> str:
    return ARTIFACT_PATH.read_text(encoding="utf-8")


def test_artifact_exists() -> None:
    assert ARTIFACT_PATH.exists()


def test_required_sections_present() -> None:
    text = _read()
    for heading in (
        "## 1. Purpose and non-ratifying boundary",
        "## 2. Evidence chain summary",
        "## 3. Policy option matrix for ranking multiplier admission",
        "## 4. Epistemic-type payout boundary alignment",
        "## 5. Sybil and anti-gaming guardrail alignment",
        "## 6. Ratification readiness statement",
        "## 7. Deferred decisions and non-goals",
        "## 8. Canonical anchors",
    ):
        assert heading in text


def test_cdl_031_open_non_ratifying_language_present() -> None:
    text = _read().lower()
    assert "cdl-031" in text
    assert "still open" in text
    assert "non-ratifying" in text


def test_candidate_recommendation_for_phase_288_present() -> None:
    text = _read().lower()
    assert "candidate recommendation for phase-288 ratification" in text
    assert "option b" in text


def test_sybil_alignment_references_reuse_diversity_controls() -> None:
    text = _read().lower()
    assert "reuse-diversity" in text
    assert "sponsor-root independence" in text
    assert "missing provenance" in text


def test_boundary_statements_present() -> None:
    text = _read().lower()
    assert "no mutation of `docs/specs/ilc_constitutional_decision_log_v0.1.md`" in text
    assert "no runtime changes in `ilc_core/`" in text
