"""Tests for the protocol-governed iterative epistemic refinement sidecar.

Phase: support-only addendum — idea-descent rehearsal sidecar
LOCAL_ONLY: True
NO_GRAPH_WRITES: True
NO_ECU_ALLOCATED: True
"""

from __future__ import annotations

import json
import pytest

from ilc_core.sidecars.idea_descent_rehearsal import (
    EVALUATOR_GAP_SEARCH,
    EVALUATOR_PYTEST_SUITE,
    EVALUATOR_TABOO_CHECKER,
    EVALUATOR_TYPES,
    IDEA_DESCENT_REHEARSAL_SIDECAR_VERSION,
    IDEA_DESCENT_SIDECAR_LOCAL_ONLY_TOKEN,
    IDEA_DESCENT_SIDECAR_NO_ACTIVATION_TOKEN,
    IDEA_DESCENT_SIDECAR_NO_CDL_ADR_MUTATION,
    IDEA_DESCENT_SIDECAR_NO_ECU_ALLOCATED,
    IDEA_DESCENT_SIDECAR_NO_GRAPH_WRITES,
    IDEA_DESCENT_SIDECAR_NOT_PUBLIC_SERVING,
    SEVERITY_CRITICAL,
    SEVERITY_MINOR,
    SEVERITY_SIGNIFICANT,
    VERDICT_ACCEPTED,
    VERDICT_INCONCLUSIVE,
    VERDICT_REJECTED,
    IdeaDescentRehearsalError,
    build_descent_step,
    build_descent_trace,
    build_evaluation_result,
    build_refutation_report,
    canonical_descent_trace_json,
    idea_descent_rehearsal_sidecar_manifest,
    validate_descent_trace,
    validate_evaluation_result,
    validate_refutation_report,
)


# ---------------------------------------------------------------------------
# Guard constants
# ---------------------------------------------------------------------------


def test_guard_not_public_serving() -> None:
    assert IDEA_DESCENT_SIDECAR_NOT_PUBLIC_SERVING is True


def test_guard_no_graph_writes() -> None:
    assert IDEA_DESCENT_SIDECAR_NO_GRAPH_WRITES is True


def test_guard_no_ecu_allocated() -> None:
    assert IDEA_DESCENT_SIDECAR_NO_ECU_ALLOCATED is True


def test_guard_no_cdl_adr_mutation() -> None:
    assert IDEA_DESCENT_SIDECAR_NO_CDL_ADR_MUTATION is True


# ---------------------------------------------------------------------------
# Manifest
# ---------------------------------------------------------------------------


def test_manifest_local_only() -> None:
    m = idea_descent_rehearsal_sidecar_manifest()
    assert m["local_only"] is True
    assert m["public_serving_enabled"] is False
    assert m["graph_writes_enabled"] is False
    assert m["ecu_allocation_enabled"] is False
    assert m["cdl_adr_mutation_enabled"] is False
    assert m["automatic_commits_enabled"] is False


def test_manifest_evaluator_types() -> None:
    m = idea_descent_rehearsal_sidecar_manifest()
    assert set(m["evaluator_types"]) == EVALUATOR_TYPES


def test_manifest_tokens() -> None:
    m = idea_descent_rehearsal_sidecar_manifest()
    assert IDEA_DESCENT_SIDECAR_LOCAL_ONLY_TOKEN in m["tokens"]
    assert IDEA_DESCENT_SIDECAR_NO_ACTIVATION_TOKEN in m["tokens"]


# ---------------------------------------------------------------------------
# EvaluationResult
# ---------------------------------------------------------------------------


def _sample_eval_result(passed: bool = True, failure_count: int = 0) -> dict:
    return build_evaluation_result(
        evaluator_type=EVALUATOR_PYTEST_SUITE,
        replay_command=".venv/bin/python -m pytest tests/ -q",
        passed=passed,
        failure_count=failure_count,
        summary="90 passed" if passed else "2 failed",
    )


def test_build_evaluation_result_pass() -> None:
    r = _sample_eval_result(passed=True)
    assert r["evaluator_type"] == EVALUATOR_PYTEST_SUITE
    assert r["passed"] is True
    assert r["failure_count"] == 0


def test_build_evaluation_result_fail() -> None:
    r = _sample_eval_result(passed=False, failure_count=2)
    assert r["passed"] is False
    assert r["failure_count"] == 2


def test_evaluation_result_invalid_type() -> None:
    with pytest.raises(IdeaDescentRehearsalError):
        build_evaluation_result(
            evaluator_type="not_a_real_evaluator",
            replay_command="cmd",
            passed=True,
            failure_count=0,
            summary="ok",
        )


def test_evaluation_result_negative_failure_count() -> None:
    with pytest.raises(IdeaDescentRehearsalError):
        build_evaluation_result(
            evaluator_type=EVALUATOR_PYTEST_SUITE,
            replay_command="cmd",
            passed=False,
            failure_count=-1,
            summary="bad",
        )


def test_validate_evaluation_result_roundtrip() -> None:
    r = _sample_eval_result()
    assert validate_evaluation_result(r) == r


# ---------------------------------------------------------------------------
# RefutationReport
# ---------------------------------------------------------------------------


def _sample_refutation() -> dict:
    return build_refutation_report(
        failed_invariant="PRODUCTION_EMISSION_NOT_ACTIVATED must be True",
        source_artifact="ilc_core/epoch/epoch_emission_production_path.py:12",
        correction_direction="Restore the guard to True before closure",
        severity=SEVERITY_CRITICAL,
        replay_command=".venv/bin/python tools/check_sensitive_runtime_coding_taboos.py",
        affected_obl_or_cdl="OBL-020",
    )


def test_build_refutation_report() -> None:
    r = _sample_refutation()
    assert r["severity"] == SEVERITY_CRITICAL
    assert r["affected_obl_or_cdl"] == "OBL-020"


def test_refutation_report_none_obl() -> None:
    r = build_refutation_report(
        failed_invariant="sort_keys missing",
        source_artifact="ilc_core/foo.py:10",
        correction_direction="Add sort_keys=True",
        severity=SEVERITY_MINOR,
        replay_command="tools/check_sensitive_runtime_coding_taboos.py",
        affected_obl_or_cdl=None,
    )
    assert r["affected_obl_or_cdl"] is None


def test_refutation_report_invalid_severity() -> None:
    with pytest.raises(IdeaDescentRehearsalError):
        build_refutation_report(
            failed_invariant="x",
            source_artifact="file.py:1",
            correction_direction="fix it",
            severity="not_a_real_severity",
            replay_command="cmd",
        )


def test_validate_refutation_report_roundtrip() -> None:
    r = _sample_refutation()
    assert validate_refutation_report(r) == r


# ---------------------------------------------------------------------------
# DescentStep
# ---------------------------------------------------------------------------


def _sample_step(
    verdict: str = VERDICT_ACCEPTED,
    step_index: int = 0,
    revision_plan: str | None = None,
) -> dict:
    return build_descent_step(
        step_index=step_index,
        objective="Close OBL-020 at default-off with all guards True",
        candidate_description="Phase 1535p emission path module with PRODUCTION_EMISSION_NOT_ACTIVATED=True",
        candidate_artifact_path="ilc_core/epoch/epoch_emission_production_path.py",
        evaluators_run=[EVALUATOR_PYTEST_SUITE, EVALUATOR_TABOO_CHECKER],
        evaluation_results=[_sample_eval_result(passed=(verdict == VERDICT_ACCEPTED))],
        refutation_reports=[] if verdict == VERDICT_ACCEPTED else [_sample_refutation()],
        revision_plan=revision_plan,
        verdict=verdict,
    )


def test_build_descent_step_accepted() -> None:
    s = _sample_step(VERDICT_ACCEPTED)
    assert s["verdict"] == VERDICT_ACCEPTED
    assert s["local_only"] is True
    assert s["graph_writes_performed"] is False
    assert s["ecu_allocated"] is False
    assert s["cdl_mutated"] is False
    assert len(s["step_sha256"]) == 64


def test_build_descent_step_rejected() -> None:
    s = _sample_step(VERDICT_REJECTED, revision_plan="Restore the guard constant")
    assert s["verdict"] == VERDICT_REJECTED
    assert s["revision_plan"] == "Restore the guard constant"
    assert len(s["refutation_reports"]) == 1


def test_descent_step_accepted_no_revision_plan() -> None:
    """Accepted step must not have a revision_plan."""
    with pytest.raises(IdeaDescentRehearsalError, match="accepted_step_has_revision_plan"):
        build_descent_step(
            step_index=0,
            objective="obj",
            candidate_description="cand",
            candidate_artifact_path=None,
            evaluators_run=[EVALUATOR_PYTEST_SUITE],
            evaluation_results=[_sample_eval_result()],
            refutation_reports=[],
            revision_plan="This should not be here",
            verdict=VERDICT_ACCEPTED,
        )


def test_descent_step_rejected_requires_revision_plan() -> None:
    """Rejected step must have a revision_plan."""
    with pytest.raises(IdeaDescentRehearsalError, match="rejected_step_missing_revision_plan"):
        build_descent_step(
            step_index=0,
            objective="obj",
            candidate_description="cand",
            candidate_artifact_path=None,
            evaluators_run=[EVALUATOR_PYTEST_SUITE],
            evaluation_results=[_sample_eval_result(passed=False, failure_count=1)],
            refutation_reports=[_sample_refutation()],
            revision_plan=None,
            verdict=VERDICT_REJECTED,
        )


def test_descent_step_hash_determinism() -> None:
    s1 = _sample_step()
    s2 = _sample_step()
    assert s1["step_sha256"] == s2["step_sha256"]


# ---------------------------------------------------------------------------
# DescentTrace
# ---------------------------------------------------------------------------


def _sample_trace() -> dict:
    steps = [
        _sample_step(VERDICT_REJECTED, step_index=0, revision_plan="Fix the guard"),
        _sample_step(VERDICT_ACCEPTED, step_index=1),
    ]
    return build_descent_trace(
        trace_id="rehearsal_obl020_block4a",
        objective="Verify OBL-020 default-off closure",
        steps=steps,
    )


def test_build_descent_trace_accepted() -> None:
    t = _sample_trace()
    assert t["final_verdict"] == VERDICT_ACCEPTED
    assert t["accepted_step_index"] == 1
    assert t["total_steps"] == 2
    assert t["local_only"] is True
    assert len(t["trace_sha256"]) == 64


def test_descent_trace_empty_inconclusive() -> None:
    t = build_descent_trace(
        trace_id="empty_rehearsal",
        objective="nothing attempted",
        steps=[],
    )
    assert t["final_verdict"] == VERDICT_INCONCLUSIVE
    assert t["accepted_step_index"] is None
    assert t["total_steps"] == 0


def test_descent_trace_all_rejected() -> None:
    steps = [_sample_step(VERDICT_REJECTED, step_index=i, revision_plan=f"fix {i}") for i in range(3)]
    t = build_descent_trace(trace_id="all_rejected", objective="obj", steps=steps)
    assert t["final_verdict"] == VERDICT_REJECTED
    assert t["accepted_step_index"] is None


def test_descent_trace_tokens() -> None:
    t = _sample_trace()
    assert IDEA_DESCENT_SIDECAR_LOCAL_ONLY_TOKEN in t["tokens"]
    assert IDEA_DESCENT_SIDECAR_NO_ACTIVATION_TOKEN in t["tokens"]


def test_validate_descent_trace_roundtrip() -> None:
    t = _sample_trace()
    validated = validate_descent_trace(t)
    assert validated["trace_sha256"] == t["trace_sha256"]


def test_validate_descent_trace_rejects_tampered_hash() -> None:
    t = _sample_trace()
    t_bad = dict(t)
    t_bad["trace_sha256"] = "a" * 64
    with pytest.raises(IdeaDescentRehearsalError, match="hash_mismatch"):
        validate_descent_trace(t_bad)


def test_canonical_json_determinism() -> None:
    t1 = _sample_trace()
    t2 = _sample_trace()
    assert canonical_descent_trace_json(t1) == canonical_descent_trace_json(t2)


def test_canonical_json_is_valid_json() -> None:
    t = _sample_trace()
    parsed = json.loads(canonical_descent_trace_json(t))
    assert parsed["final_verdict"] == VERDICT_ACCEPTED


def test_canonical_json_sort_keys() -> None:
    """Keys in the serialized JSON must be sorted."""
    t = _sample_trace()
    raw = canonical_descent_trace_json(t)
    # Verify every object's keys appear in sorted order
    parsed = json.loads(raw)
    re_serialized = json.dumps(parsed, allow_nan=False, separators=(",", ":"), sort_keys=True)
    assert raw == re_serialized


def test_descent_trace_too_many_steps() -> None:
    steps = [_sample_step(VERDICT_REJECTED, step_index=i, revision_plan=f"fix {i}") for i in range(101)]
    with pytest.raises(IdeaDescentRehearsalError, match="too_many_steps"):
        build_descent_trace(trace_id="oversize", objective="obj", steps=steps)
