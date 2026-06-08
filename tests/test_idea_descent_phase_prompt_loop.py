"""Integration test: idea-descent loop over a phase prompt candidate.

Demonstrates measurable improvement across two steps:

  Step 0 — v1 candidate (skeleton prompt missing §0a-§0d + commit section):
    verdict=rejected, 5 specific refutation reports

  Step 1 — v2 candidate (complete prompt with all required sections):
    verdict=accepted, 0 refutation reports

Measurement:
  failure_count: 5 → 0
  score: 3/8 checks → 8/8 checks

This test does NOT write to disk and does NOT require the runner CLI.
It uses the evaluator and sidecar data model directly to keep the test
deterministic and fast.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

# Ensure project root is on path (needed when running from tests/ subdirectory)
_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from ilc_core.sidecars.idea_descent_rehearsal import (
    VERDICT_ACCEPTED,
    VERDICT_REJECTED,
    build_descent_step,
    build_descent_trace,
    build_evaluation_result,
    build_refutation_report,
    canonical_descent_trace_json,
    validate_descent_trace,
)

_FIXTURES = Path(__file__).parent / "fixtures"
_V1 = _FIXTURES / "antigravity_prompt__phase_1546p_g10_block5_init_descent_v1.md"
_V2 = _FIXTURES / "antigravity_prompt__phase_1546p_g10_block5_init_descent_v2.md"
_OBJECTIVE = (
    _ROOT
    / "docs"
    / "specs"
    / "ilc_idea_descent_phase_prompt_objective_v0.1.md"
)

# Import the evaluator directly (no subprocess needed in tests)
import importlib.util as _ilu

_ev_spec = _ilu.spec_from_file_location(
    "phase_prompt_evaluator",
    _ROOT / "tools" / "evaluators" / "phase_prompt_evaluator.py",
)
_ev_mod = _ilu.module_from_spec(_ev_spec)
_ev_spec.loader.exec_module(_ev_mod)
_evaluator = _ev_mod


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

OBJECTIVE_TEXT = "Produce a valid phase prompt for Phase 1546p-G10 Window initialization"


def _evaluate(candidate_path: Path) -> dict:
    """Run the evaluator against a candidate file."""
    return _evaluator.run_evaluation(str(candidate_path), OBJECTIVE_TEXT)


def _make_step(
    step_index: int,
    candidate_path: Path,
    eval_result_dict: dict,
) -> dict:
    """Build a DescentStep from an evaluation result dict."""
    passed = eval_result_dict["passed"]
    reports_raw = eval_result_dict["refutation_reports"]
    replay_command = _evaluator.REPLAY_COMMAND_TEMPLATE.format(
        candidate=str(candidate_path)
    )

    eval_result = build_evaluation_result(
        evaluator_type=_evaluator.EVALUATOR_TYPE,
        replay_command=replay_command,
        passed=passed,
        failure_count=eval_result_dict["failure_count"],
        summary=eval_result_dict["summary"],
    )
    refutation_reports = [build_refutation_report(**r) for r in reports_raw]

    verdict = VERDICT_ACCEPTED if passed else VERDICT_REJECTED
    revision_plan: str | None = None
    if not passed and reports_raw:
        revision_plan = "Fix: " + "; ".join(
            r["correction_direction"] for r in reports_raw
        )

    return build_descent_step(
        step_index=step_index,
        objective=OBJECTIVE_TEXT,
        candidate_description=candidate_path.name,
        candidate_artifact_path=str(candidate_path),
        evaluators_run=[_evaluator.EVALUATOR_TYPE],
        evaluation_results=[eval_result],
        refutation_reports=refutation_reports,
        revision_plan=revision_plan,
        verdict=verdict,
    )


# ---------------------------------------------------------------------------
# Tests — individual step evaluation
# ---------------------------------------------------------------------------


def test_v1_candidate_files_exist() -> None:
    assert _V1.exists(), f"v1 fixture not found: {_V1}"
    assert _V2.exists(), f"v2 fixture not found: {_V2}"
    assert _OBJECTIVE.exists(), f"objective file not found: {_OBJECTIVE}"


def test_v1_evaluation_fails() -> None:
    """v1 prompt is missing §0a-§0d and commit section — evaluator must reject."""
    result = _evaluate(_V1)
    assert result["passed"] is False
    assert result["failure_count"] > 0


def test_v1_has_five_errors() -> None:
    """v1 prompt has exactly 5 schema errors."""
    result = _evaluate(_V1)
    assert result["failure_count"] == 5, (
        f"expected 5 errors, got {result['failure_count']}: "
        + str([r["failed_invariant"] for r in result["refutation_reports"]])
    )


def test_v1_missing_commit_section_reported() -> None:
    result = _evaluate(_V1)
    invariants = {r["failed_invariant"] for r in result["refutation_reports"]}
    assert "missing_section:commit" in invariants


def test_v1_missing_s0a_reported() -> None:
    result = _evaluate(_V1)
    invariants = {r["failed_invariant"] for r in result["refutation_reports"]}
    assert any("§0a" in i for i in invariants), f"§0a not in {invariants}"


def test_v1_missing_s0b_reported() -> None:
    result = _evaluate(_V1)
    invariants = {r["failed_invariant"] for r in result["refutation_reports"]}
    assert any("§0b" in i for i in invariants)


def test_v1_refutation_reports_have_correction_directions() -> None:
    result = _evaluate(_V1)
    for r in result["refutation_reports"]:
        assert r["correction_direction"], f"missing correction_direction: {r}"


def test_v2_evaluation_passes() -> None:
    """v2 prompt has all required sections — evaluator must accept."""
    result = _evaluate(_V2)
    assert result["passed"] is True
    assert result["failure_count"] == 0
    assert result["refutation_reports"] == []


# ---------------------------------------------------------------------------
# Tests — descent steps and measurable improvement
# ---------------------------------------------------------------------------


def test_step_0_verdict_rejected() -> None:
    """Step 0 (v1) must be rejected."""
    result = _evaluate(_V1)
    step = _make_step(0, _V1, result)
    assert step["verdict"] == VERDICT_REJECTED


def test_step_1_verdict_accepted() -> None:
    """Step 1 (v2) must be accepted."""
    result = _evaluate(_V2)
    step = _make_step(1, _V2, result)
    assert step["verdict"] == VERDICT_ACCEPTED


def test_failure_count_decreases() -> None:
    """The key measurable signal: failure_count drops from 5 to 0."""
    r0 = _evaluate(_V1)
    r1 = _evaluate(_V2)
    fc0 = r0["failure_count"]
    fc1 = r1["failure_count"]
    assert fc0 > fc1, f"expected improvement: {fc0} -> {fc1}"
    assert fc1 == 0, f"v2 should have 0 failures, got {fc1}"


def test_improvement_score() -> None:
    """Improvement expressed as fraction of checks passing.

    8 schema checks in validate_phase_prompt.py for phase >= 1249:
      - filename (1), h1 (1), 5 required sections (5), STATUS.md ref (1), §0a-d (4)
    v1 passes 3 of 8 structural groups; v2 passes all 8.
    """
    r0 = _evaluate(_V1)
    r1 = _evaluate(_V2)
    # v1: 5 failures out of 8 checks → score = 3/8
    # v2: 0 failures out of 8 checks → score = 8/8
    assert r0["failure_count"] == 5
    assert r1["failure_count"] == 0


# ---------------------------------------------------------------------------
# Tests — full two-step descent trace
# ---------------------------------------------------------------------------


def test_two_step_trace_builds_correctly() -> None:
    """Build a complete two-step trace and validate it."""
    r0 = _evaluate(_V1)
    r1 = _evaluate(_V2)
    step0 = _make_step(0, _V1, r0)
    step1 = _make_step(1, _V2, r1)

    trace = build_descent_trace(
        trace_id="phase_prompt_1546p_descent",
        objective=OBJECTIVE_TEXT,
        steps=[step0, step1],
    )
    assert trace["final_verdict"] == VERDICT_ACCEPTED
    assert trace["accepted_step_index"] == 1
    assert trace["total_steps"] == 2


def test_trace_integrity_survives_validate() -> None:
    """Trace hash integrity check passes after rebuild."""
    r0 = _evaluate(_V1)
    r1 = _evaluate(_V2)
    step0 = _make_step(0, _V1, r0)
    step1 = _make_step(1, _V2, r1)
    trace = build_descent_trace(
        trace_id="phase_prompt_1546p_descent",
        objective=OBJECTIVE_TEXT,
        steps=[step0, step1],
    )
    validated = validate_descent_trace(trace)
    assert validated["trace_sha256"] == trace["trace_sha256"]


def test_trace_canonical_json_parseable() -> None:
    """The canonical JSON trace must round-trip without data loss."""
    import json

    r0 = _evaluate(_V1)
    r1 = _evaluate(_V2)
    step0 = _make_step(0, _V1, r0)
    step1 = _make_step(1, _V2, r1)
    trace = build_descent_trace(
        trace_id="phase_prompt_1546p_descent",
        objective=OBJECTIVE_TEXT,
        steps=[step0, step1],
    )
    raw = canonical_descent_trace_json(trace)
    parsed = json.loads(raw)
    assert parsed["final_verdict"] == VERDICT_ACCEPTED
    assert parsed["total_steps"] == 2
    assert parsed["accepted_step_index"] == 1


def test_step_0_refutation_reports_are_actionable() -> None:
    """Every refutation report from step 0 has a non-empty correction_direction."""
    r0 = _evaluate(_V1)
    step0 = _make_step(0, _V1, r0)
    for report in step0["refutation_reports"]:
        assert report["correction_direction"], (
            f"empty correction_direction for: {report['failed_invariant']}"
        )
        assert report["severity"] in ("critical", "significant", "minor")
