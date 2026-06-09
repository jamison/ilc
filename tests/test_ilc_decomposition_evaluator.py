"""Tests for the ILC Decomposition Evaluator v0.1 — base blocks and evaluator recipe.

LOCAL_ONLY: True
NO_GRAPH_WRITES: True
NO_ECU_ALLOCATED: True
"""

from __future__ import annotations

from pathlib import Path

import pytest

from tools.evaluators.blocks.claim_extractor import extract_claims
from tools.evaluators.blocks.scope_binder import bind_scope
from tools.evaluators.blocks.evidence_classifier import classify_evidence
from tools.evaluators.blocks.falsifiability_checker import check_falsifiability
from tools.evaluators.ilc_decomposition_evaluator import (
    EVALUATOR_ID,
    EVALUATOR_TYPE,
    decompose_and_evaluate,
    run_evaluation,
)
from ilc_core.sidecars.idea_descent_rehearsal import (
    EVALUATOR_STATIC_AUDIT,
    SEVERITY_CRITICAL,
    SEVERITY_SIGNIFICANT,
    SEVERITY_MINOR,
)

_FIXTURES = Path(__file__).parent / "fixtures"
_RAW_CANDIDATE = str(_FIXTURES / "romer_solow_raw_claims_v1.md")
_REFINED_CANDIDATE = str(_FIXTURES / "romer_solow_refined_claims_v2.md")


# ---------------------------------------------------------------------------
# Evaluator contract constants
# ---------------------------------------------------------------------------


def test_evaluator_id() -> None:
    assert EVALUATOR_ID == "ilc_decomposition_evaluator_v0.1"


def test_evaluator_type_is_static_audit() -> None:
    assert EVALUATOR_TYPE == EVALUATOR_STATIC_AUDIT


def test_replay_command_template_has_candidate_placeholder() -> None:
    from tools.evaluators.ilc_decomposition_evaluator import REPLAY_COMMAND_TEMPLATE
    assert "{candidate}" in REPLAY_COMMAND_TEMPLATE


# ---------------------------------------------------------------------------
# Block 1: claim_extractor
# ---------------------------------------------------------------------------


def test_extract_claims_basic() -> None:
    text = (
        "Capital accumulates over time.  "
        "Output is produced by combining capital and labor.  "
        "Technology is exogenous."
    )
    claims = extract_claims(text, source_id="test_doc")
    assert len(claims) >= 1


def test_extract_claims_returns_claim_ids() -> None:
    text = "Higher savings rates cause higher steady-state capital per worker."
    claims = extract_claims(text, source_id="test::doc")
    assert all("claim_id" in c for c in claims)
    assert all(c["source_id"] == "test::doc" for c in claims)


def test_extract_claims_skips_headers() -> None:
    text = "# Introduction\nCapital accumulates over time."
    claims = extract_claims(text, source_id="doc")
    # The header line should not appear as a claim
    for c in claims:
        assert not c["text"].startswith("#")


def test_extract_claims_form_causal() -> None:
    text = "Higher savings rates cause higher steady-state capital per worker."
    claims = extract_claims(text, source_id="doc")
    assert any(c["form"] == "causal" for c in claims)


def test_extract_claims_form_quantitative() -> None:
    text = "Growth equals 3 percent per year on average."
    claims = extract_claims(text, source_id="doc")
    assert any(c["form"] == "quantitative" for c in claims)


def test_extract_claims_form_definitional() -> None:
    text = "We define the capital-labor ratio k as K divided by L."
    claims = extract_claims(text, source_id="doc")
    assert any(c["form"] == "definitional" for c in claims)


def test_extract_claims_line_numbers_are_positive() -> None:
    text = "Line one.\nCapital accumulates over time.\nLine three."
    claims = extract_claims(text, source_id="doc")
    assert all(c["line_start"] >= 1 for c in claims)
    assert all(c["line_end"] >= c["line_start"] for c in claims)


# ---------------------------------------------------------------------------
# Block 2: scope_binder
# ---------------------------------------------------------------------------


def test_bind_scope_returns_extended_record() -> None:
    text = "In the Solow model, the economy converges to a steady state."
    claims = extract_claims(text, source_id="doc")
    assert claims
    scoped = bind_scope(claims[0])
    assert "domain" in scoped
    assert "regime" in scoped
    assert "universality" in scoped
    assert "scope_explicit" in scoped
    assert "scope_warnings" in scoped


def test_bind_scope_domain_economics() -> None:
    text = "In the Solow model, the savings rate determines capital accumulation."
    claims = extract_claims(text, source_id="doc")
    for c in claims:
        scoped = bind_scope(c)
        if "Solow" in scoped["text"] or "savings" in scoped["text"]:
            assert scoped["domain"] == "economics"
            break


def test_bind_scope_regime_steady_state() -> None:
    text = "In the long-run steady state, capital per worker is constant."
    claims = extract_claims(text, source_id="doc")
    assert claims
    scoped = bind_scope(claims[0])
    assert scoped["regime"] == "steady_state"


def test_bind_scope_warns_human_to_ai_transfer() -> None:
    text = (
        "Diminishing returns to human capital also apply to AI capital, "
        "because AI workers behave like human workers."
    )
    claims = extract_claims(text, source_id="doc")
    assert claims
    scoped = bind_scope(claims[0])
    warnings = scoped["scope_warnings"]
    assert any("AI" in w or "human" in w.lower() for w in warnings)


def test_bind_scope_does_not_mutate_input() -> None:
    text = "Capital accumulates over time."
    claims = extract_claims(text, source_id="doc")
    original = dict(claims[0])
    bind_scope(claims[0])
    assert claims[0] == original


# ---------------------------------------------------------------------------
# Block 3: evidence_classifier
# ---------------------------------------------------------------------------


def test_classify_evidence_theoretical() -> None:
    text = "We prove that the economy converges to the steady state by Lyapunov argument."
    claims = extract_claims(text, source_id="doc")
    assert claims
    scoped = bind_scope(claims[0])
    evidenced = classify_evidence(scoped)
    assert evidenced["evidence_type"] == "theoretical"


def test_classify_evidence_empirical() -> None:
    text = (
        "Cross-country data show that countries with higher savings rates "
        "have higher capital-output ratios (regression coefficient = 0.42)."
    )
    claims = extract_claims(text, source_id="doc")
    assert claims
    scoped = bind_scope(claims[0])
    evidenced = classify_evidence(scoped)
    assert evidenced["evidence_type"] == "empirical"


def test_classify_evidence_computational() -> None:
    text = "The simulation shows convergence to steady state within 50 periods."
    claims = extract_claims(text, source_id="doc")
    assert claims
    scoped = bind_scope(claims[0])
    evidenced = classify_evidence(scoped)
    assert evidenced["evidence_type"] == "computational"


def test_classify_evidence_asserted() -> None:
    text = "Capital accumulates over time."
    claims = extract_claims(text, source_id="doc")
    assert claims
    scoped = bind_scope(claims[0])
    evidenced = classify_evidence(scoped)
    assert evidenced["evidence_type"] == "asserted"


def test_classify_evidence_cites_source() -> None:
    text = "As shown by Solow (1956), steady-state growth is determined by technology."
    claims = extract_claims(text, source_id="doc")
    assert claims
    scoped = bind_scope(claims[0])
    evidenced = classify_evidence(scoped)
    assert evidenced["cites_source"] is True


def test_classify_evidence_warns_human_labor_applied_to_ai() -> None:
    text = (
        "Empirically, diminishing returns to human capital also apply to "
        "AI capital because AI workers follow the same production function."
    )
    claims = extract_claims(text, source_id="doc")
    assert claims
    scoped = bind_scope(claims[0])
    evidenced = classify_evidence(scoped)
    assert any("AI_capital" in w for w in evidenced["evidence_warnings"])


def test_classify_evidence_does_not_mutate_input() -> None:
    text = "We prove that output increases with capital."
    claims = extract_claims(text, source_id="doc")
    scoped = bind_scope(claims[0])
    original = dict(scoped)
    classify_evidence(scoped)
    assert scoped == original


# ---------------------------------------------------------------------------
# Block 4: falsifiability_checker
# ---------------------------------------------------------------------------


def test_check_falsifiability_has_condition_when_explicit() -> None:
    text = (
        "This convergence fails when the Inada conditions are violated, "
        "such as in AK models."
    )
    claims = extract_claims(text, source_id="doc")
    assert claims
    scoped = bind_scope(claims[0])
    evidenced = classify_evidence(scoped)
    full = check_falsifiability(evidenced)
    assert full["has_falsification_condition"] is True
    assert full["ilc_refutable"] is True


def test_check_falsifiability_no_condition_asserted() -> None:
    text = "Capital accumulates over time."
    claims = extract_claims(text, source_id="doc")
    assert claims
    scoped = bind_scope(claims[0])
    evidenced = classify_evidence(scoped)
    full = check_falsifiability(evidenced)
    # Asserted claim without explicit falsification condition
    assert full["has_falsification_condition"] is False


def test_check_falsifiability_normative_no_hook_blocked() -> None:
    text = "The economy ought to save more, broadly speaking."
    claims = extract_claims(text, source_id="doc")
    assert claims
    scoped = bind_scope(claims[0])
    evidenced = classify_evidence(scoped)
    full = check_falsifiability(evidenced)
    # Normative claim with no verification hook and universal hedge
    # should be blocked or have warnings
    has_normative_warning = any(
        "normative" in w or "hedge" in w
        for w in full.get("falsification_warnings", [])
    )
    assert has_normative_warning or not full["ilc_refutable"]


def test_check_falsifiability_definitional_blocked() -> None:
    text = "By definition, k is defined as the capital-labor ratio K/L."
    claims = extract_claims(text, source_id="doc")
    assert claims
    scoped = bind_scope(claims[0])
    evidenced = classify_evidence(scoped)
    full = check_falsifiability(evidenced)
    assert any("definitional" in w for w in full.get("falsification_warnings", []))


def test_check_falsifiability_does_not_mutate_input() -> None:
    text = "We prove convergence unless the Inada conditions are violated."
    claims = extract_claims(text, source_id="doc")
    scoped = bind_scope(claims[0])
    evidenced = classify_evidence(scoped)
    original = dict(evidenced)
    check_falsifiability(evidenced)
    assert evidenced == original


# ---------------------------------------------------------------------------
# Full pipeline: decompose_and_evaluate
# ---------------------------------------------------------------------------


def test_pipeline_returns_required_keys() -> None:
    text = "Capital accumulates over time."
    result = decompose_and_evaluate(text, "test_doc")
    assert "records" in result
    assert "reports" in result
    assert "n_claims" in result
    assert "n_refutable" in result


def test_pipeline_all_records_have_ilc_refutable() -> None:
    text = (
        "We prove that output increases with capital input.  "
        "This fails when the production function is not concave."
    )
    result = decompose_and_evaluate(text, "test_doc")
    for rec in result["records"]:
        assert "ilc_refutable" in rec
        assert "ilc_refutable_reason" in rec


def test_pipeline_reports_have_required_refutation_report_keys() -> None:
    text = "Capital accumulates.  Savings rate causes growth."
    result = decompose_and_evaluate(text, "test_doc")
    required_keys = {
        "failed_invariant",
        "source_artifact",
        "correction_direction",
        "severity",
        "replay_command",
        "affected_obl_or_cdl",
    }
    for report in result["reports"]:
        assert required_keys.issubset(report.keys()), (
            f"Report missing keys: {required_keys - report.keys()}"
        )


# ---------------------------------------------------------------------------
# Evaluator contract: run_evaluation — measurable improvement loop
# ---------------------------------------------------------------------------


def test_raw_candidate_rejected() -> None:
    """Raw Romer claims doc (v1) must be rejected — too many unfalsifiable assertions."""
    result = run_evaluation(_RAW_CANDIDATE, "")
    assert result["passed"] is False
    assert result["failure_count"] > 0


def test_refined_candidate_has_fewer_failures_than_raw() -> None:
    """Refined candidate (v2) must have strictly fewer failures than the raw version.

    This is the key descent measurement: failure_count must decrease.
    The refined doc adds scope markers, falsification conditions, and evidence anchors.
    """
    raw_result = run_evaluation(_RAW_CANDIDATE, "")
    refined_result = run_evaluation(_REFINED_CANDIDATE, "")
    assert refined_result["failure_count"] < raw_result["failure_count"], (
        f"Expected refined to have fewer failures than raw.  "
        f"Raw: {raw_result['failure_count']}, "
        f"Refined: {refined_result['failure_count']}"
    )


def test_raw_candidate_summary_contains_invalid() -> None:
    result = run_evaluation(_RAW_CANDIDATE, "")
    assert "INVALID" in result["summary"]


def test_refined_candidate_summary_format() -> None:
    result = run_evaluation(_REFINED_CANDIDATE, "")
    assert "claims extracted" in result["summary"]


def test_run_evaluation_missing_file_returns_error() -> None:
    result = run_evaluation("/nonexistent/path/doc.md", "")
    assert result["passed"] is False
    assert result["failure_count"] == 1
    assert "candidate_read_failed" in result["refutation_reports"][0]["failed_invariant"]


def test_run_evaluation_returns_all_required_keys() -> None:
    result = run_evaluation(_RAW_CANDIDATE, "")
    assert "passed" in result
    assert "failure_count" in result
    assert "summary" in result
    assert "refutation_reports" in result
    assert isinstance(result["refutation_reports"], list)


def test_scope_risk_in_raw_candidate_reports() -> None:
    """Raw candidate has AI-capital claims that violate the diminishing-returns scope.

    At least one SIGNIFICANT report should reference a scope_risk.
    """
    result = run_evaluation(_RAW_CANDIDATE, "")
    significant_reports = [
        r for r in result["refutation_reports"]
        if r["severity"] == SEVERITY_SIGNIFICANT
    ]
    scope_risk_reports = [
        r for r in significant_reports
        if "scope_risk" in r["failed_invariant"]
    ]
    assert len(scope_risk_reports) > 0, (
        "Expected at least one scope_risk report from AI-capital overclaim in raw candidate"
    )


def test_two_step_descent_reduces_failure_count() -> None:
    """Integration: two-step loop must show measurable improvement.

    Step 0: raw candidate → failure_count > 0
    Step 1: refined candidate → failure_count < step 0

    This mirrors the test pattern in test_idea_descent_phase_prompt_loop.py.
    """
    r0 = run_evaluation(_RAW_CANDIDATE, "")
    r1 = run_evaluation(_REFINED_CANDIDATE, "")
    assert r0["failure_count"] > 0, "Step 0 should have failures"
    assert r1["failure_count"] < r0["failure_count"], (
        f"Step 1 should improve: {r0['failure_count']} → {r1['failure_count']}"
    )
