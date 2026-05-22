from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "docs/research/ilc_merkle_laplacian_dual_commitment_paper_draft_v0.2.md"
REVIEW = ROOT / "docs/research/ilc_merkle_laplacian_dual_commitment_v0.2_intake_review_2026_05_22.md"
LAMBDA = "\u03bb"
SUBSCRIPT_TWO = "\u2082"
MULTIPLY = "\u00d7"
APPROX = "\u2248"
SUPERSCRIPT_FOUR = "\u2074"
EPSILON = "\u03b5"


def test_v02_paper_is_imported_and_public_rc_excluded() -> None:
    text = PAPER.read_text(encoding="utf-8")

    assert "PUBLIC_RC_EXCLUDE" in text
    assert "Draft v0.2" in text
    assert "## v0.2 Revision Notes" in text
    assert "Phase 1280 Fix1 Current-Status Addendum" in text
    assert "Do not include in a public RC package" in text


def test_v02_paper_preserves_opus_technical_fixes() -> None:
    text = PAPER.read_text(encoding="utf-8")

    required = [
        "*k* smallest eigenvalues",
        "fixed-point quantization",
        f"int64_le( round( {LAMBDA}_i(t) {MULTIPLY} q ) )",
        "challenge-response protocol",
        "full canonical hyperedge set",
        "Layer separation",
        "M(t) commits to hyperedge declaration records",
        "S(t) commits to the indexed structural assembly",
        "smallest-*k* eigenvalue sequence",
        f"not the per-epoch activation path at |*V*| {APPROX} 10{SUPERSCRIPT_FOUR}",
        "technical-review draft v0.2",
    ]

    for token in required:
        assert token in text


def test_v02_paper_removes_stale_v01_phrases() -> None:
    text = PAPER.read_text(encoding="utf-8")

    forbidden = [
        "Nakamoto [CITATION: 2008]",
        "raw top-*k* eigenvalues",
        "recorded top-*k* eigenvalue sequence",
        "| top-*k* eigenvalues |",
        "End of historical draft v0.1",
        f"producing a correct {LAMBDA}{SUBSCRIPT_TWO} without knowledge",
        f"Empirically {EPSILON}",
        "under one second on commodity hardware",
    ]

    for token in forbidden:
        assert token not in text


def test_intake_review_records_remaining_sim_obligations() -> None:
    text = REVIEW.read_text(encoding="utf-8")

    assert "PUBLIC_RC_EXCLUDE" in text
    assert "Intake Verdict" in text
    assert "Required Follow-On SIM Reruns" in text
    for sim_token in [
        "SIM-SPECTRAL-01-RERUN",
        "SIM-SPECTRAL-COST-01",
        "SIM-POSK-01",
        "SIM-DUALCOMMIT-01",
        "SIM-DIRECTED-CLOSURE-01",
        "SIM-REUSE-STABILITY-01",
    ]:
        assert sim_token in text
