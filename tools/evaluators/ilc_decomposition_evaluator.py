#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
"""ILC Decomposition Evaluator v0.1 — idea-descent runner evaluator recipe.

PUBLIC_RC_EXCLUDE: ilc_decomposition_evaluator_support_only
PUBLIC_RC_EXCLUDE_REASON: Local sidecar-layer evaluator for ILC claim decomposition
and epistemic quality assessment.  No graph writes, no ECU allocation, no CDL/ADR
mutation, not public-serving.

Evaluator contract (matches idea_descent_runner.py):
  EVALUATOR_ID: str
  EVALUATOR_TYPE: str
  REPLAY_COMMAND_TEMPLATE: str

  def run_evaluation(candidate_path: str, objective_text: str) -> dict:
      # Returns: {passed, failure_count, summary, refutation_reports}

Usage (via runner):
  .venv/bin/python tools/idea_descent_runner.py \\
    --objective docs/specs/ilc_idea_descent_decomposition_objective_v0.1.md \\
    --candidate <path_to_claim_document> \\
    --evaluator tools/evaluators/ilc_decomposition_evaluator.py \\
    --trace-out out/idea_descent/decomposition_trace.json

Usage (standalone / recipe testing):
  .venv/bin/python tools/evaluators/ilc_decomposition_evaluator.py \\
    --candidate <path_to_claim_document>

Evaluation pipeline (per claim):
  1. claim_extractor  — segments text into candidate assertion units
  2. scope_binder     — annotates each claim with domain, regime, assumptions
  3. evidence_classifier — labels evidence type and evidence-bridge risks
  4. falsifiability_checker — tests operational falsifiability

Severity mapping:
  CRITICAL    — claim is structurally unfalsifiable AND asserted (blocks ILC submission)
  SIGNIFICANT — claim is ILC-refutable but has scope or evidence-bridge warnings
  MINOR       — advisory note (missing scope marker, weak evidence type, etc.)
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from ilc_core.sidecars.idea_descent_rehearsal import (
    EVALUATOR_STATIC_AUDIT,
    SEVERITY_CRITICAL,
    SEVERITY_MINOR,
    SEVERITY_SIGNIFICANT,
)
from tools.evaluators.blocks.claim_extractor import extract_claims
from tools.evaluators.blocks.scope_binder import bind_scope
from tools.evaluators.blocks.evidence_classifier import classify_evidence
from tools.evaluators.blocks.falsifiability_checker import check_falsifiability

EVALUATOR_ID = "ilc_decomposition_evaluator_v0.1"
EVALUATOR_TYPE = EVALUATOR_STATIC_AUDIT
REPLAY_COMMAND_TEMPLATE = (
    ".venv/bin/python tools/idea_descent_runner.py "
    "--objective docs/specs/ilc_idea_descent_decomposition_objective_v0.1.md "
    "--candidate {candidate} "
    "--evaluator tools/evaluators/ilc_decomposition_evaluator.py "
    "--trace-out out/idea_descent/decomposition_trace.json"
)

# ---------------------------------------------------------------------------
# Severity thresholds
# ---------------------------------------------------------------------------

# Number of claims that must be ILC-refutable for the candidate to pass
_MIN_REFUTABLE_FRACTION = 0.5

# Evidence types that are considered "weak" for a claim that makes causal assertions
_WEAK_EVIDENCE_FOR_CAUSAL = {"asserted", "descriptive", "definitional"}


def _make_report(
    *,
    invariant: str,
    candidate_path: str,
    correction: str,
    severity: str,
    claim_id: str | None = None,
) -> dict[str, Any]:
    artifact = (
        f"{candidate_path}::{claim_id}" if claim_id else candidate_path
    )
    return {
        "failed_invariant": invariant,
        "source_artifact": artifact,
        "correction_direction": correction,
        "severity": severity,
        "replay_command": REPLAY_COMMAND_TEMPLATE.format(candidate=candidate_path),
        "affected_obl_or_cdl": None,
    }


def _evaluate_claims(
    records: list[dict[str, Any]],
    candidate_path: str,
    reports: list[dict[str, Any]],
) -> None:
    """Walk the fully-annotated claim records and emit refutation reports."""
    n_total = len(records)
    n_refutable = 0

    for rec in records:
        claim_id = rec["claim_id"]
        ilc_refutable = rec["ilc_refutable"]
        reason = rec.get("ilc_refutable_reason", "")
        form = rec.get("form", "unknown")
        evidence_type = rec.get("evidence_type", "asserted")
        scope_warnings = rec.get("scope_warnings", [])
        evidence_warnings = rec.get("evidence_warnings", [])
        falsification_warnings = rec.get("falsification_warnings", [])
        scope_explicit = rec.get("scope_explicit", False)

        if ilc_refutable:
            n_refutable += 1

        # CRITICAL: structurally unfalsifiable asserted claim
        if not ilc_refutable and "blocked" in reason:
            reports.append(
                _make_report(
                    invariant=f"claim_not_ilc_refutable:{reason}",
                    candidate_path=candidate_path,
                    correction=(
                        "Add an explicit falsification condition, a refutation "
                        "edge target, or a truth-primitive:refute.claim reference.  "
                        "If the claim is definitional, restrict its usage to that form."
                    ),
                    severity=SEVERITY_CRITICAL,
                    claim_id=claim_id,
                )
            )

        # SIGNIFICANT: causal claim with weak evidence
        if form == "causal" and evidence_type in _WEAK_EVIDENCE_FOR_CAUSAL:
            reports.append(
                _make_report(
                    invariant=f"causal_claim_with_weak_evidence:{evidence_type}",
                    candidate_path=candidate_path,
                    correction=(
                        "A causal claim requires at least computational or "
                        "theoretical backing.  Add a mechanism description, a "
                        "derivation reference, or a calibration anchor."
                    ),
                    severity=SEVERITY_SIGNIFICANT,
                    claim_id=claim_id,
                )
            )

        # SIGNIFICANT: scope-risk warnings
        for w in scope_warnings:
            if "scope_risk" in w:
                reports.append(
                    _make_report(
                        invariant=f"scope_risk_detected:{w}",
                        candidate_path=candidate_path,
                        correction=(
                            "Restrict claim scope or add a bridge argument showing "
                            "the original scope's assumptions still hold in the new context."
                        ),
                        severity=SEVERITY_SIGNIFICANT,
                        claim_id=claim_id,
                    )
                )

        # SIGNIFICANT: evidence-bridge risks
        for w in evidence_warnings:
            if "evidence_risk" in w:
                reports.append(
                    _make_report(
                        invariant=f"evidence_bridge_risk:{w}",
                        candidate_path=candidate_path,
                        correction=(
                            "Add explicit bridge language connecting the evidence type "
                            "to the claim's domain and regime."
                        ),
                        severity=SEVERITY_SIGNIFICANT,
                        claim_id=claim_id,
                    )
                )

        # MINOR: scope not explicit for quantitative/causal claims
        if not scope_explicit and form in ("quantitative", "causal", "existence"):
            reports.append(
                _make_report(
                    invariant=f"scope_not_explicit:{form}_claim",
                    candidate_path=candidate_path,
                    correction=(
                        "Add an explicit scoping marker (e.g., 'In the baseline model...' "
                        "or 'Under the assumption that...') to bound the claim."
                    ),
                    severity=SEVERITY_MINOR,
                    claim_id=claim_id,
                )
            )

        # MINOR: falsifiability advisory warnings
        for w in falsification_warnings:
            if "advisory" in w or "hedge" in w:
                reports.append(
                    _make_report(
                        invariant=f"falsifiability_advisory:{w}",
                        candidate_path=candidate_path,
                        correction="Tighten the claim to remove hedge language.",
                        severity=SEVERITY_MINOR,
                        claim_id=claim_id,
                    )
                )

    # Global: not enough refutable claims
    if n_total > 0:
        fraction = n_refutable / n_total
        if fraction < _MIN_REFUTABLE_FRACTION:
            reports.append(
                _make_report(
                    invariant=(
                        f"insufficient_refutable_claims:"
                        f"{n_refutable}/{n_total}_refutable"
                    ),
                    candidate_path=candidate_path,
                    correction=(
                        f"At least {int(_MIN_REFUTABLE_FRACTION * 100)}% of extracted "
                        f"claims must have an operational falsification condition.  "
                        f"Currently {n_refutable}/{n_total} ({fraction:.0%}) are refutable.  "
                        f"Revise claims to add testable conditions or reclassify "
                        f"definitional statements."
                    ),
                    severity=SEVERITY_CRITICAL,
                )
            )


def decompose_and_evaluate(
    text: str,
    candidate_path: str,
) -> dict[str, Any]:
    """Run the full four-block pipeline on *text*.

    Returns a dict with keys: records, reports, n_claims, n_refutable.
    This function is called by run_evaluation() and is also importable
    for use in tests and other evaluator recipes.
    """
    claims = extract_claims(text, source_id=candidate_path)
    scoped = [bind_scope(c) for c in claims]
    evidenced = [classify_evidence(s) for s in scoped]
    full = [check_falsifiability(e) for e in evidenced]

    reports: list[dict[str, Any]] = []
    _evaluate_claims(full, candidate_path, reports)

    n_refutable = sum(1 for r in full if r.get("ilc_refutable"))
    return {
        "records": full,
        "reports": reports,
        "n_claims": len(full),
        "n_refutable": n_refutable,
    }


def run_evaluation(candidate_path: str, objective_text: str) -> dict[str, Any]:
    """Evaluator contract entry point — called by idea_descent_runner.py."""
    try:
        text = Path(candidate_path).read_text(encoding="utf-8")
    except Exception as exc:
        report = {
            "failed_invariant": "candidate_read_failed",
            "source_artifact": candidate_path,
            "correction_direction": f"Ensure candidate file exists and is readable: {exc}",
            "severity": SEVERITY_CRITICAL,
            "replay_command": REPLAY_COMMAND_TEMPLATE.format(candidate=candidate_path),
            "affected_obl_or_cdl": None,
        }
        return {
            "passed": False,
            "failure_count": 1,
            "summary": "INVALID: candidate file did not load",
            "refutation_reports": [report],
        }

    result = decompose_and_evaluate(text, candidate_path)
    reports = result["reports"]
    n_claims = result["n_claims"]
    n_refutable = result["n_refutable"]
    passed = len(reports) == 0

    summary = (
        f"VALID: {n_claims} claims extracted, "
        f"{n_refutable}/{n_claims} refutable, 0 invariant failures"
        if passed
        else f"INVALID: {n_claims} claims extracted, "
             f"{n_refutable}/{n_claims} refutable, "
             f"{len(reports)} invariant failure(s)"
    )
    return {
        "passed": passed,
        "failure_count": len(reports),
        "summary": summary,
        "refutation_reports": reports,
    }


__all__ = [
    "EVALUATOR_ID",
    "EVALUATOR_TYPE",
    "REPLAY_COMMAND_TEMPLATE",
    "decompose_and_evaluate",
    "run_evaluation",
]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run ILC decomposition evaluator standalone."
    )
    parser.add_argument("--candidate", type=Path, required=True)
    args = parser.parse_args()
    result = run_evaluation(str(args.candidate), "")
    print(result["summary"])
    for r in result["refutation_reports"]:
        print(f"  [{r['severity'].upper()}] {r['failed_invariant']}")
        print(f"     → {r['correction_direction'][:120]}")
    sys.exit(0 if result["passed"] else 1)
