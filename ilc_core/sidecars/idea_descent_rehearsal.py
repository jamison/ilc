# SPDX-License-Identifier: AGPL-3.0-only
"""Protocol-governed iterative epistemic refinement sidecar (idea-descent rehearsal).

This module provides the local-only data model and trace-recording surface for
a structured iterative refinement loop over ILC specs, phase prompts, or runtime
artifacts.

Internal name: protocol_governed_epistemic_refinement_sidecar
External community context: "Idea Descent" (Papailiopoulos / OpenAI Codex, June 2026)
ILC internal name: protocol-governed iterative epistemic refinement

The refinement loop is:
  1. Seed an objective (what to improve and why)
  2. Propose a candidate (a change, a draft artifact, a patch direction)
  3. Run evaluators (tests, taboo checker, prompt validator, gap search, simulation)
  4. Convert failures into a structured refutation report
  5. Produce a revision plan or accept the candidate
  6. Record the full step as a replayable evidence artifact
  7. Repeat from step 2 until accepted or iteration limit reached

This module does NOT execute tests, generate candidates, write to the graph,
mint ECU, issue ILC, open or mutate CDLs or ADRs, serve a public endpoint,
apply patches without explicit human/phase authority, or make automatic commits.

PUBLIC_RC_EXCLUDE: idea_descent_rehearsal_sidecar_local_only
PUBLIC_RC_EXCLUDE_REASON: Local rehearsal harness only; does not authorize graph
writes, ECU minting, public activation, CDL/ADR mutation, or automatic commits.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping, Sequence
from typing import Any


IDEA_DESCENT_REHEARSAL_SIDECAR_VERSION = (
    "protocol_governed_epistemic_refinement_sidecar_support.v0.1"
)
IDEA_DESCENT_SIDECAR_NOT_PUBLIC_SERVING = True
IDEA_DESCENT_SIDECAR_NO_GRAPH_WRITES = True
IDEA_DESCENT_SIDECAR_NO_ECU_ALLOCATED = True
IDEA_DESCENT_SIDECAR_NO_CDL_ADR_MUTATION = True

IDEA_DESCENT_SIDECAR_LOCAL_ONLY_TOKEN = (
    "idea_descent_rehearsal_sidecar_local_only_support_v0_1"
)
IDEA_DESCENT_SIDECAR_NO_ACTIVATION_TOKEN = (
    "idea_descent_rehearsal_sidecar_no_activation_support_v0_1"
)

# Evaluator surface identifiers — matches the test_inventory.md evaluator families
EVALUATOR_PYTEST_SUITE = "pytest_suite"
EVALUATOR_TABOO_CHECKER = "taboo_checker"
EVALUATOR_VALIDATE_PHASE_PROMPT = "validate_phase_prompt"
EVALUATOR_GAP_SEARCH = "gap_search"
EVALUATOR_STATIC_AUDIT = "static_audit"
EVALUATOR_SIMULATION = "simulation"

EVALUATOR_TYPES: frozenset[str] = frozenset(
    {
        EVALUATOR_PYTEST_SUITE,
        EVALUATOR_TABOO_CHECKER,
        EVALUATOR_VALIDATE_PHASE_PROMPT,
        EVALUATOR_GAP_SEARCH,
        EVALUATOR_STATIC_AUDIT,
        EVALUATOR_SIMULATION,
    }
)

# Severity levels for refutation reports
SEVERITY_CRITICAL = "critical"     # blocks closure
SEVERITY_SIGNIFICANT = "significant"  # should be fixed before closure
SEVERITY_MINOR = "minor"           # carry-forward acceptable

SEVERITY_LEVELS: frozenset[str] = frozenset(
    {SEVERITY_CRITICAL, SEVERITY_SIGNIFICANT, SEVERITY_MINOR}
)

# Verdict values
VERDICT_ACCEPTED = "accepted"
VERDICT_REJECTED = "rejected"
VERDICT_INCONCLUSIVE = "inconclusive"

VERDICT_VALUES: frozenset[str] = frozenset(
    {VERDICT_ACCEPTED, VERDICT_REJECTED, VERDICT_INCONCLUSIVE}
)

_MAX_TEXT_LENGTH = 4096
_MAX_PATH_LENGTH = 512
_MAX_EVALUATION_RESULTS = 32
_MAX_REFUTATION_REPORTS = 64
_MAX_STEPS = 100
_MAX_TOKENS = 64

_EVALUATION_RESULT_KEYS = frozenset(
    {"evaluator_type", "replay_command", "passed", "failure_count", "summary"}
)
_REFUTATION_REPORT_KEYS = frozenset(
    {
        "failed_invariant",
        "source_artifact",
        "correction_direction",
        "severity",
        "replay_command",
        "affected_obl_or_cdl",
    }
)
_DESCENT_STEP_KEYS = frozenset(
    {
        "step_index",
        "objective",
        "candidate_description",
        "candidate_artifact_path",
        "evaluators_run",
        "evaluation_results",
        "refutation_reports",
        "revision_plan",
        "verdict",
        "step_sha256",
        "sidecar_version",
        "local_only",
        "graph_writes_performed",
        "ecu_allocated",
        "cdl_mutated",
    }
)
_DESCENT_TRACE_KEYS = frozenset(
    {
        "trace_id",
        "objective",
        "steps",
        "final_verdict",
        "accepted_step_index",
        "total_steps",
        "sidecar_version",
        "trace_sha256",
        "local_only",
        "tokens",
    }
)


class IdeaDescentRehearsalError(ValueError):
    """Fail-closed idea-descent rehearsal error with a stable token."""

    def __init__(self, token: str, message: str) -> None:
        super().__init__(f"{token}: {message}")
        self.token = token


# ---------------------------------------------------------------------------
# EvaluationResult
# ---------------------------------------------------------------------------


def build_evaluation_result(
    *,
    evaluator_type: str,
    replay_command: str,
    passed: bool,
    failure_count: int,
    summary: str,
) -> dict[str, Any]:
    """Build a single evaluator result record."""
    if evaluator_type not in EVALUATOR_TYPES:
        raise IdeaDescentRehearsalError(
            "idea_descent_evaluator_type_invalid",
            f"evaluator_type must be one of {sorted(EVALUATOR_TYPES)}",
        )
    if not isinstance(passed, bool):
        raise IdeaDescentRehearsalError(
            "idea_descent_evaluation_result_passed_not_bool",
            "passed must be a bool",
        )
    if not isinstance(failure_count, int) or isinstance(failure_count, bool) or failure_count < 0:
        raise IdeaDescentRehearsalError(
            "idea_descent_evaluation_result_failure_count_invalid",
            "failure_count must be a non-negative int",
        )
    return {
        "evaluator_type": _require_text("evaluator_type", evaluator_type),
        "replay_command": _require_text("replay_command", replay_command, max_len=_MAX_PATH_LENGTH * 4),
        "passed": passed,
        "failure_count": failure_count,
        "summary": _require_text("summary", summary),
    }


def validate_evaluation_result(result: Any) -> dict[str, Any]:
    _require_mapping("evaluation_result", result)
    if set(result) != _EVALUATION_RESULT_KEYS:
        raise IdeaDescentRehearsalError(
            "idea_descent_evaluation_result_keys_invalid",
            "evaluation_result keys do not match contract",
        )
    return build_evaluation_result(
        evaluator_type=result["evaluator_type"],
        replay_command=result["replay_command"],
        passed=result["passed"],
        failure_count=result["failure_count"],
        summary=result["summary"],
    )


# ---------------------------------------------------------------------------
# RefutationReport
# ---------------------------------------------------------------------------


def build_refutation_report(
    *,
    failed_invariant: str,
    source_artifact: str,
    correction_direction: str,
    severity: str,
    replay_command: str,
    affected_obl_or_cdl: str | None = None,
) -> dict[str, Any]:
    """Build a single refutation report record."""
    if severity not in SEVERITY_LEVELS:
        raise IdeaDescentRehearsalError(
            "idea_descent_refutation_severity_invalid",
            f"severity must be one of {sorted(SEVERITY_LEVELS)}",
        )
    return {
        "failed_invariant": _require_text("failed_invariant", failed_invariant),
        "source_artifact": _require_text("source_artifact", source_artifact, max_len=_MAX_PATH_LENGTH),
        "correction_direction": _require_text("correction_direction", correction_direction),
        "severity": severity,
        "replay_command": _require_text("replay_command", replay_command, max_len=_MAX_PATH_LENGTH * 4),
        "affected_obl_or_cdl": (
            _require_text("affected_obl_or_cdl", affected_obl_or_cdl, max_len=_MAX_PATH_LENGTH)
            if affected_obl_or_cdl is not None
            else None
        ),
    }


def validate_refutation_report(report: Any) -> dict[str, Any]:
    _require_mapping("refutation_report", report)
    if set(report) != _REFUTATION_REPORT_KEYS:
        raise IdeaDescentRehearsalError(
            "idea_descent_refutation_report_keys_invalid",
            "refutation_report keys do not match contract",
        )
    return build_refutation_report(
        failed_invariant=report["failed_invariant"],
        source_artifact=report["source_artifact"],
        correction_direction=report["correction_direction"],
        severity=report["severity"],
        replay_command=report["replay_command"],
        affected_obl_or_cdl=report["affected_obl_or_cdl"],
    )


# ---------------------------------------------------------------------------
# DescentStep
# ---------------------------------------------------------------------------


def build_descent_step(
    *,
    step_index: int,
    objective: str,
    candidate_description: str,
    candidate_artifact_path: str | None,
    evaluators_run: Sequence[str],
    evaluation_results: Sequence[Mapping[str, Any]],
    refutation_reports: Sequence[Mapping[str, Any]],
    revision_plan: str | None,
    verdict: str,
) -> dict[str, Any]:
    """Build a single descent step record."""
    if not isinstance(step_index, int) or isinstance(step_index, bool) or step_index < 0:
        raise IdeaDescentRehearsalError(
            "idea_descent_step_index_invalid",
            "step_index must be a non-negative int",
        )
    if verdict not in VERDICT_VALUES:
        raise IdeaDescentRehearsalError(
            "idea_descent_verdict_invalid",
            f"verdict must be one of {sorted(VERDICT_VALUES)}",
        )
    # Validate evaluators_run list
    if not isinstance(evaluators_run, (list, tuple)) or len(evaluators_run) > _MAX_EVALUATION_RESULTS:
        raise IdeaDescentRehearsalError(
            "idea_descent_evaluators_run_invalid",
            "evaluators_run must be a sequence of at most {_MAX_EVALUATION_RESULTS} items",
        )
    for ev in evaluators_run:
        if ev not in EVALUATOR_TYPES:
            raise IdeaDescentRehearsalError(
                "idea_descent_evaluators_run_type_invalid",
                f"evaluators_run entry must be one of {sorted(EVALUATOR_TYPES)}",
            )
    # Validate evaluation_results
    if not isinstance(evaluation_results, (list, tuple)) or len(evaluation_results) > _MAX_EVALUATION_RESULTS:
        raise IdeaDescentRehearsalError(
            "idea_descent_evaluation_results_too_many",
            "evaluation_results must be a bounded sequence",
        )
    validated_results = [validate_evaluation_result(r) for r in evaluation_results]
    # Validate refutation_reports
    if not isinstance(refutation_reports, (list, tuple)) or len(refutation_reports) > _MAX_REFUTATION_REPORTS:
        raise IdeaDescentRehearsalError(
            "idea_descent_refutation_reports_too_many",
            "refutation_reports must be a bounded sequence",
        )
    validated_reports = [validate_refutation_report(r) for r in refutation_reports]
    # Accepted steps must have no revision plan; rejected steps must have one
    if verdict == VERDICT_ACCEPTED and revision_plan is not None:
        raise IdeaDescentRehearsalError(
            "idea_descent_accepted_step_has_revision_plan",
            "an accepted step must not have a revision_plan",
        )
    if verdict == VERDICT_REJECTED and revision_plan is None:
        raise IdeaDescentRehearsalError(
            "idea_descent_rejected_step_missing_revision_plan",
            "a rejected step must have a revision_plan",
        )

    step: dict[str, Any] = {
        "step_index": step_index,
        "objective": _require_text("objective", objective),
        "candidate_description": _require_text("candidate_description", candidate_description),
        "candidate_artifact_path": (
            _require_text("candidate_artifact_path", candidate_artifact_path, max_len=_MAX_PATH_LENGTH)
            if candidate_artifact_path is not None
            else None
        ),
        "evaluators_run": sorted(set(evaluators_run)),
        "evaluation_results": validated_results,
        "refutation_reports": validated_reports,
        "revision_plan": (
            _require_text("revision_plan", revision_plan)
            if revision_plan is not None
            else None
        ),
        "verdict": verdict,
        "sidecar_version": IDEA_DESCENT_REHEARSAL_SIDECAR_VERSION,
        "local_only": True,
        "graph_writes_performed": False,
        "ecu_allocated": False,
        "cdl_mutated": False,
    }
    step["step_sha256"] = _step_sha256(step)
    return step


# ---------------------------------------------------------------------------
# DescentTrace
# ---------------------------------------------------------------------------


def build_descent_trace(
    *,
    trace_id: str,
    objective: str,
    steps: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """Build a complete descent trace from a sequence of validated steps."""
    if not isinstance(steps, (list, tuple)) or len(steps) > _MAX_STEPS:
        raise IdeaDescentRehearsalError(
            "idea_descent_trace_too_many_steps",
            f"a descent trace may have at most {_MAX_STEPS} steps",
        )
    validated_steps = [_validate_descent_step(s) for s in steps]

    # Determine final verdict and accepted_step_index
    accepted_index: int | None = None
    for s in validated_steps:
        if s["verdict"] == VERDICT_ACCEPTED:
            accepted_index = s["step_index"]
            break
    final_verdict = VERDICT_ACCEPTED if accepted_index is not None else (
        VERDICT_REJECTED if validated_steps else VERDICT_INCONCLUSIVE
    )

    trace: dict[str, Any] = {
        "trace_id": _require_text("trace_id", trace_id, max_len=_MAX_PATH_LENGTH),
        "objective": _require_text("objective", objective),
        "steps": validated_steps,
        "final_verdict": final_verdict,
        "accepted_step_index": accepted_index,
        "total_steps": len(validated_steps),
        "sidecar_version": IDEA_DESCENT_REHEARSAL_SIDECAR_VERSION,
        "local_only": True,
        "tokens": [
            IDEA_DESCENT_SIDECAR_LOCAL_ONLY_TOKEN,
            IDEA_DESCENT_SIDECAR_NO_ACTIVATION_TOKEN,
        ],
    }
    trace["trace_sha256"] = _trace_sha256(trace)
    return trace


def validate_descent_trace(trace: Any) -> dict[str, Any]:
    """Validate a descent trace dict against the module contract."""
    _require_mapping("descent_trace", trace)
    if set(trace) != _DESCENT_TRACE_KEYS:
        raise IdeaDescentRehearsalError(
            "idea_descent_trace_keys_invalid",
            "descent_trace keys do not match contract",
        )
    if trace.get("sidecar_version") != IDEA_DESCENT_REHEARSAL_SIDECAR_VERSION:
        raise IdeaDescentRehearsalError(
            "idea_descent_trace_version_invalid",
            "descent_trace sidecar_version is invalid",
        )
    if trace.get("local_only") is not True:
        raise IdeaDescentRehearsalError(
            "idea_descent_trace_must_be_local_only",
            "descent_trace must have local_only=True",
        )
    if trace.get("tokens") != [
        IDEA_DESCENT_SIDECAR_LOCAL_ONLY_TOKEN,
        IDEA_DESCENT_SIDECAR_NO_ACTIVATION_TOKEN,
    ]:
        raise IdeaDescentRehearsalError(
            "idea_descent_trace_tokens_invalid",
            "descent_trace required tokens are invalid",
        )
    # Re-derive the trace hash to verify integrity
    candidate_sha256 = trace.get("trace_sha256")
    rebuilt = build_descent_trace(
        trace_id=trace["trace_id"],
        objective=trace["objective"],
        steps=trace["steps"],
    )
    if candidate_sha256 != rebuilt["trace_sha256"]:
        raise IdeaDescentRehearsalError(
            "idea_descent_trace_hash_mismatch",
            "descent_trace hash does not match recomputed hash",
        )
    return rebuilt


def canonical_descent_trace_json(trace: Mapping[str, Any]) -> str:
    """Canonical JSON serialization of a descent trace (sort_keys=True, no NaN)."""
    return json.dumps(trace, allow_nan=False, separators=(",", ":"), sort_keys=True)


# ---------------------------------------------------------------------------
# Sidecar manifest
# ---------------------------------------------------------------------------


def idea_descent_rehearsal_sidecar_manifest() -> dict[str, Any]:
    """Deterministic local/package metadata for the idea-descent rehearsal sidecar."""
    return {
        "sidecar_version": IDEA_DESCENT_REHEARSAL_SIDECAR_VERSION,
        "local_only": True,
        "public_serving_enabled": False,
        "graph_writes_enabled": False,
        "ecu_allocation_enabled": False,
        "cdl_adr_mutation_enabled": False,
        "automatic_commits_enabled": False,
        "evaluator_types": sorted(EVALUATOR_TYPES),
        "verdict_values": sorted(VERDICT_VALUES),
        "severity_levels": sorted(SEVERITY_LEVELS),
        "tokens": [
            IDEA_DESCENT_SIDECAR_LOCAL_ONLY_TOKEN,
            IDEA_DESCENT_SIDECAR_NO_ACTIVATION_TOKEN,
        ],
    }


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _validate_descent_step(step: Any) -> dict[str, Any]:
    """Validate a descent step dict (used internally by build_descent_trace)."""
    _require_mapping("descent_step", step)
    if set(step) != _DESCENT_STEP_KEYS:
        raise IdeaDescentRehearsalError(
            "idea_descent_step_keys_invalid",
            "descent_step keys do not match contract",
        )
    if step.get("sidecar_version") != IDEA_DESCENT_REHEARSAL_SIDECAR_VERSION:
        raise IdeaDescentRehearsalError(
            "idea_descent_step_version_invalid",
            "descent_step sidecar_version is invalid",
        )
    if step.get("local_only") is not True:
        raise IdeaDescentRehearsalError(
            "idea_descent_step_must_be_local_only",
            "descent_step must have local_only=True",
        )
    for flag_name in ("graph_writes_performed", "ecu_allocated", "cdl_mutated"):
        if step.get(flag_name) is not False:
            raise IdeaDescentRehearsalError(
                f"idea_descent_step_{flag_name}_must_be_false",
                f"descent_step must have {flag_name}=False",
            )
    # Re-derive step hash to verify integrity
    without_hash = {k: v for k, v in step.items() if k != "step_sha256"}
    if step.get("step_sha256") != _step_sha256_from_dict(without_hash):
        raise IdeaDescentRehearsalError(
            "idea_descent_step_hash_mismatch",
            "descent_step hash does not match recomputed hash",
        )
    return dict(step)


def _step_sha256(step: dict[str, Any]) -> str:
    without_hash = {k: v for k, v in step.items() if k != "step_sha256"}
    return _step_sha256_from_dict(without_hash)


def _step_sha256_from_dict(d: dict[str, Any]) -> str:
    return hashlib.sha256(
        json.dumps(d, allow_nan=False, separators=(",", ":"), sort_keys=True).encode("utf-8")
    ).hexdigest()


def _trace_sha256(trace: dict[str, Any]) -> str:
    without_hash = {k: v for k, v in trace.items() if k != "trace_sha256"}
    return hashlib.sha256(
        json.dumps(without_hash, allow_nan=False, separators=(",", ":"), sort_keys=True).encode("utf-8")
    ).hexdigest()


def _require_text(name: str, value: object, *, max_len: int = _MAX_TEXT_LENGTH) -> str:
    if not isinstance(value, str) or not value.strip():
        raise IdeaDescentRehearsalError(
            f"idea_descent_{name}_invalid_text",
            f"{name} must be a non-empty string",
        )
    if len(value) > max_len:
        raise IdeaDescentRehearsalError(
            f"idea_descent_{name}_too_long",
            f"{name} must be at most {max_len} characters",
        )
    return value


def _require_mapping(name: str, value: object) -> None:
    if not isinstance(value, Mapping):
        raise IdeaDescentRehearsalError(
            f"idea_descent_{name}_not_a_mapping",
            f"{name} must be a mapping",
        )


__all__ = [
    # Guard constants
    "IDEA_DESCENT_SIDECAR_NOT_PUBLIC_SERVING",
    "IDEA_DESCENT_SIDECAR_NO_GRAPH_WRITES",
    "IDEA_DESCENT_SIDECAR_NO_ECU_ALLOCATED",
    "IDEA_DESCENT_SIDECAR_NO_CDL_ADR_MUTATION",
    # Version and tokens
    "IDEA_DESCENT_REHEARSAL_SIDECAR_VERSION",
    "IDEA_DESCENT_SIDECAR_LOCAL_ONLY_TOKEN",
    "IDEA_DESCENT_SIDECAR_NO_ACTIVATION_TOKEN",
    # Evaluator surface
    "EVALUATOR_PYTEST_SUITE",
    "EVALUATOR_TABOO_CHECKER",
    "EVALUATOR_VALIDATE_PHASE_PROMPT",
    "EVALUATOR_GAP_SEARCH",
    "EVALUATOR_STATIC_AUDIT",
    "EVALUATOR_SIMULATION",
    "EVALUATOR_TYPES",
    # Verdict and severity
    "VERDICT_ACCEPTED",
    "VERDICT_REJECTED",
    "VERDICT_INCONCLUSIVE",
    "VERDICT_VALUES",
    "SEVERITY_CRITICAL",
    "SEVERITY_SIGNIFICANT",
    "SEVERITY_MINOR",
    "SEVERITY_LEVELS",
    # Error class
    "IdeaDescentRehearsalError",
    # Build functions
    "build_evaluation_result",
    "build_refutation_report",
    "build_descent_step",
    "build_descent_trace",
    # Validate functions
    "validate_evaluation_result",
    "validate_refutation_report",
    "validate_descent_trace",
    # Serialization
    "canonical_descent_trace_json",
    # Manifest
    "idea_descent_rehearsal_sidecar_manifest",
]
