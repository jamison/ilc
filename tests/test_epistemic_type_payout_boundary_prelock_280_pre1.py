"""Contract checks for Phase 280-pre1 epistemic-type prelock artifact."""

from pathlib import Path

PRELOCK_PATH = Path(
    "docs/specs/ilc_epistemic_type_and_subjective_objective_payout_boundary_prelock_280_pre1_v0.1.md"
)


def _read() -> str:
    return PRELOCK_PATH.read_text(encoding="utf-8")


def test_prelock_file_exists() -> None:
    assert PRELOCK_PATH.exists()


def test_required_section_headings_present() -> None:
    text = _read()
    for heading in (
        "## 1. Purpose and non-ratifying boundary",
        "## 2. Epistemic type schema candidate",
        "## 3. Validation-path matrix by type",
        "## 4. Payout-boundary matrix by type",
        "## 5. Sybil and anti-gaming controls (anchor map)",
        "## 6. Ratification-entry criteria and deferred decisions",
        "## 7. Canonical source anchors",
    ):
        assert heading in text


def test_required_enum_candidates_present() -> None:
    text = _read()
    for token in ("`objective`", "`subjective`", "`normative`", "`creative_speculative`"):
        assert token in text


def test_required_matrix_statements_present() -> None:
    text = _read()
    required = (
        "objective` lane uses full contradiction/refute path and full reuse valuation",
        "subjective` lane uses curation/reuse-resonance path and is not auto-promoted to objective-core without decomposition/reclassification criteria",
        "normative` lane uses governance-bound challenge path",
        "creative_speculative` lane remains exploratory by default",
    )
    for line in required:
        assert line in text


def test_anti_sybil_anchor_statements_present() -> None:
    text = _read()
    for line in (
        "reuse-diversity policy remains binding for scoring-boundary integrity",
        "sponsor-root independence is required for quorum independence claims",
        "missing provenance fails closed in scoring path",
        "citation-loop/collusion risk remains explicitly bounded by diversity/cluster controls",
    ):
        assert line in text


def test_non_ratifying_boundary_is_explicit() -> None:
    text = _read()
    assert "no mutation of `docs/specs/ilc_constitutional_decision_log_v0.1.md`" in text
    assert "no mutation of any CDL status field" in text
    assert "no runtime implementation changes in `ilc_core/`" in text
