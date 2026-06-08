#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
"""Protocol-governed iterative epistemic refinement — descent runner.

Drives one step of a descent loop:
  1. Load the objective (what we want to achieve)
  2. Import the evaluator module and run it against the candidate
  3. Build a DescentStep using the sidecar data model
  4. Append the step to the persistent trace (created on first run)
  5. Print a revision brief listing every failed invariant with correction direction
  6. Exit 0 if accepted, 1 if rejected, 2 on runner error

Usage:
  .venv/bin/python tools/idea_descent_runner.py \\
    --objective docs/specs/ilc_idea_descent_phase_prompt_objective_v0.1.md \\
    --candidate tests/fixtures/antigravity_prompt__phase_1546p_g10_block5_init_descent_v1.md \\
    --evaluator tools/evaluators/phase_prompt_evaluator.py \\
    --trace-out out/idea_descent/phase_prompt_loop_trace.json

Evaluator module contract:
  Each evaluator module must expose:
    EVALUATOR_ID: str           — unique evaluator name
    EVALUATOR_TYPE: str         — one of EVALUATOR_TYPES from the sidecar
    REPLAY_COMMAND_TEMPLATE: str — template with {candidate} placeholder

    def run_evaluation(
        candidate_path: str,
        objective_text: str,
    ) -> dict:
        # Returns:
        # {
        #     "passed": bool,
        #     "failure_count": int,
        #     "summary": str,
        #     "refutation_reports": list[dict],  # RefutationReport dicts
        # }

Exit codes:
  0 — candidate accepted
  1 — candidate rejected
  2 — runner error
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path
from types import ModuleType
from typing import Any

# Ensure project root is on path when invoked directly from tools/
_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from ilc_core.sidecars.idea_descent_rehearsal import (
    VERDICT_ACCEPTED,
    VERDICT_INCONCLUSIVE,
    VERDICT_REJECTED,
    build_descent_step,
    build_descent_trace,
    build_evaluation_result,
    build_refutation_report,
    canonical_descent_trace_json,
)


def _load_module_from_path(path: Path) -> ModuleType:
    """Import a Python module from an arbitrary filesystem path."""
    spec = importlib.util.spec_from_file_location(path.stem, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load module from {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _load_existing_steps(trace_path: Path) -> tuple[str, str, list[dict[str, Any]]]:
    """Load trace_id, objective, and existing steps from a saved trace file.

    Returns (trace_id, objective, steps_list).
    If the file does not exist, returns defaults derived from the path.
    """
    if not trace_path.exists():
        return trace_path.stem, "", []
    raw = json.loads(trace_path.read_text(encoding="utf-8"))
    return (
        raw.get("trace_id", trace_path.stem),
        raw.get("objective", ""),
        list(raw.get("steps", [])),
    )


def _auto_revision_plan(refutation_reports: list[dict[str, Any]]) -> str | None:
    if not refutation_reports:
        return None
    lines = ["Fix the following:"]
    for r in refutation_reports:
        severity = r.get("severity", "minor")
        direction = r.get("correction_direction", "")
        invariant = r.get("failed_invariant", "")
        artifact = r.get("source_artifact", "")
        lines.append(f"  [{severity.upper()}] {invariant}")
        if artifact:
            lines.append(f"    Source: {artifact}")
        if direction:
            lines.append(f"    Fix: {direction}")
    return "\n".join(lines)


def _print_revision_brief(
    step_index: int,
    candidate_path: str,
    verdict: str,
    refutation_reports: list[dict[str, Any]],
    trace_path: Path,
) -> None:
    sep = "─" * 72
    print(sep)
    print(f"Idea Descent Step {step_index}  |  verdict: {verdict.upper()}")
    print(f"Candidate : {candidate_path}")
    print(f"Trace     : {trace_path}")
    print(sep)
    if verdict == VERDICT_ACCEPTED:
        print("✓ All evaluators passed. Candidate accepted.")
    else:
        print(f"✗ {len(refutation_reports)} invariant(s) failed:\n")
        for i, r in enumerate(refutation_reports, 1):
            severity = r.get("severity", "minor").upper()
            print(f"  {i}. [{severity}] {r.get('failed_invariant', '')}")
            artifact = r.get("source_artifact", "")
            if artifact:
                print(f"     Source: {artifact}")
            print(f"     Fix: {r.get('correction_direction', '')}")
            obl = r.get("affected_obl_or_cdl")
            if obl:
                print(f"     Affects: {obl}")
            replay = r.get("replay_command", "")
            if replay:
                print(f"     Replay: {replay}")
            print()
        print("→ Revise the candidate and re-run with the updated file.")
    print(sep)


def run_step(
    *,
    objective_path: Path,
    candidate_path: Path,
    evaluator_path: Path,
    trace_path: Path,
    step_label: str | None = None,
) -> int:
    """Execute one descent step. Returns exit code (0=accepted, 1=rejected, 2=error)."""

    # --- Load objective ---
    if not objective_path.exists():
        print(f"ERROR: objective file not found: {objective_path}", file=sys.stderr)
        return 2
    objective_text = objective_path.read_text(encoding="utf-8").strip()

    # --- Validate inputs ---
    if not candidate_path.exists():
        print(f"ERROR: candidate file not found: {candidate_path}", file=sys.stderr)
        return 2
    if not evaluator_path.exists():
        print(f"ERROR: evaluator module not found: {evaluator_path}", file=sys.stderr)
        return 2

    # --- Load evaluator ---
    try:
        evaluator = _load_module_from_path(evaluator_path)
    except Exception as exc:
        print(f"ERROR: failed to load evaluator {evaluator_path}: {exc}", file=sys.stderr)
        return 2

    for attr in ("EVALUATOR_ID", "EVALUATOR_TYPE", "REPLAY_COMMAND_TEMPLATE", "run_evaluation"):
        if not hasattr(evaluator, attr):
            print(
                f"ERROR: evaluator module missing required attribute: {attr}",
                file=sys.stderr,
            )
            return 2

    # --- Run evaluation ---
    replay_command = evaluator.REPLAY_COMMAND_TEMPLATE.format(
        candidate=str(candidate_path)
    )
    try:
        result = evaluator.run_evaluation(str(candidate_path), objective_text)
    except Exception as exc:
        print(
            f"ERROR: evaluator.run_evaluation raised unexpectedly: {exc}",
            file=sys.stderr,
        )
        return 2

    passed: bool = result.get("passed", False)
    failure_count: int = result.get("failure_count", 0)
    summary: str = result.get("summary", "")
    raw_reports: list[dict] = result.get("refutation_reports", [])

    # --- Build sidecar objects ---
    eval_result = build_evaluation_result(
        evaluator_type=evaluator.EVALUATOR_TYPE,
        replay_command=replay_command,
        passed=passed,
        failure_count=failure_count,
        summary=summary,
    )
    refutation_reports = [build_refutation_report(**r) for r in raw_reports]

    verdict = VERDICT_ACCEPTED if passed else VERDICT_REJECTED
    revision_plan = _auto_revision_plan(raw_reports) if not passed else None

    # --- Load existing trace state ---
    existing_trace_id, existing_objective, existing_steps = _load_existing_steps(trace_path)
    trace_id = existing_trace_id
    effective_objective = existing_objective or objective_text
    step_index = len(existing_steps)

    candidate_description = step_label or candidate_path.name

    # --- Build new step ---
    new_step = build_descent_step(
        step_index=step_index,
        objective=effective_objective,
        candidate_description=candidate_description,
        candidate_artifact_path=str(candidate_path),
        evaluators_run=[evaluator.EVALUATOR_TYPE],
        evaluation_results=[eval_result],
        refutation_reports=refutation_reports,
        revision_plan=revision_plan,
        verdict=verdict,
    )

    # --- Rebuild trace with all steps ---
    all_steps = existing_steps + [new_step]
    trace = build_descent_trace(
        trace_id=trace_id,
        objective=effective_objective,
        steps=all_steps,
    )

    # --- Save trace ---
    trace_path.parent.mkdir(parents=True, exist_ok=True)
    trace_path.write_text(
        canonical_descent_trace_json(trace) + "\n",
        encoding="utf-8",
    )

    # --- Print revision brief ---
    _print_revision_brief(
        step_index=step_index,
        candidate_path=str(candidate_path),
        verdict=verdict,
        refutation_reports=raw_reports,
        trace_path=trace_path,
    )

    return 0 if verdict == VERDICT_ACCEPTED else 1


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run one step of the protocol-governed epistemic refinement loop."
    )
    parser.add_argument(
        "--objective",
        type=Path,
        required=True,
        help="Path to the objective file (markdown or text)",
    )
    parser.add_argument(
        "--candidate",
        type=Path,
        required=True,
        help="Path to the candidate artifact being evaluated",
    )
    parser.add_argument(
        "--evaluator",
        type=Path,
        required=True,
        help="Path to the evaluator Python module",
    )
    parser.add_argument(
        "--trace-out",
        type=Path,
        required=True,
        dest="trace_out",
        help="Path to the persistent trace JSON file (created or appended)",
    )
    parser.add_argument(
        "--step-label",
        type=str,
        default=None,
        dest="step_label",
        help="Human-readable label for this step (default: candidate filename)",
    )
    args = parser.parse_args()

    return run_step(
        objective_path=args.objective,
        candidate_path=args.candidate,
        evaluator_path=args.evaluator,
        trace_path=args.trace_out,
        step_label=args.step_label,
    )


if __name__ == "__main__":
    sys.exit(main())
