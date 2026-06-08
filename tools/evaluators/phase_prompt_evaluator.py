# SPDX-License-Identifier: AGPL-3.0-only
"""Phase prompt evaluator for the idea-descent runner.

Evaluates a candidate phase prompt file against the ILC phase prompt schema
enforced by tools/validate_phase_prompt.py.

Each validation error becomes one RefutationReport. The overall evaluation
passes only when validate_phase_prompt.py reports VALID.

Evaluator module contract attributes:
  EVALUATOR_ID            — unique evaluator name
  EVALUATOR_TYPE          — "validate_phase_prompt" (sidecar EVALUATOR_TYPES)
  REPLAY_COMMAND_TEMPLATE — command to re-run with {candidate} placeholder
  run_evaluation(candidate_path, objective_text) -> dict
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from ilc_core.sidecars.idea_descent_rehearsal import (
    EVALUATOR_VALIDATE_PHASE_PROMPT,
    SEVERITY_CRITICAL,
    SEVERITY_MINOR,
    SEVERITY_SIGNIFICANT,
)

EVALUATOR_ID = "phase_prompt_schema_evaluator"
EVALUATOR_TYPE = EVALUATOR_VALIDATE_PHASE_PROMPT
REPLAY_COMMAND_TEMPLATE = (
    ".venv/bin/python tools/validate_phase_prompt.py {candidate}"
)

# Map known error-token prefixes to severity and correction direction templates
_ERROR_SEVERITY: dict[str, str] = {
    "invalid_filename_pattern": SEVERITY_CRITICAL,
    "missing_h1_title": SEVERITY_CRITICAL,
    "invalid_h1_pattern": SEVERITY_CRITICAL,
    "h1_phase_mismatch": SEVERITY_CRITICAL,
    "h1_group_mismatch": SEVERITY_CRITICAL,
    "missing_section:mission": SEVERITY_CRITICAL,
    "missing_section:scope": SEVERITY_CRITICAL,
    "missing_section:deliverables": SEVERITY_SIGNIFICANT,
    "missing_section:walkthrough requirements": SEVERITY_SIGNIFICANT,
    "missing_section:status update requirements": SEVERITY_SIGNIFICANT,
    "missing_section:inputs": SEVERITY_SIGNIFICANT,
    "missing_section:commands": SEVERITY_SIGNIFICANT,
    "missing_section:commit": SEVERITY_SIGNIFICANT,
    "missing_rule:no_ellipses_in_walkthrough": SEVERITY_MINOR,
    "missing_reference:STATUS.md": SEVERITY_MINOR,
    "missing_unknown_unknown_discovery_section:### §0a": SEVERITY_CRITICAL,
    "missing_unknown_unknown_discovery_section:### §0b": SEVERITY_CRITICAL,
    "missing_unknown_unknown_discovery_section:### §0c": SEVERITY_SIGNIFICANT,
    "missing_unknown_unknown_discovery_section:### §0d": SEVERITY_SIGNIFICANT,
}

_ERROR_CORRECTION: dict[str, str] = {
    "invalid_filename_pattern": (
        "Rename file to match: antigravity_prompt__phase_NNNx_gN_slug.md"
    ),
    "missing_h1_title": "Add H1 title: # Phase NNN-GN — <title>",
    "invalid_h1_pattern": "Fix H1 to match: # Phase NNN-GN — <title>",
    "h1_phase_mismatch": "Align H1 phase number with filename phase number",
    "h1_group_mismatch": "Align H1 group number with filename group number",
    "missing_section:mission": "Add ## Mission section",
    "missing_section:scope": "Add ## Scope section",
    "missing_section:deliverables": "Add ## Deliverables section",
    "missing_section:walkthrough requirements": "Add ## Walkthrough Requirements section",
    "missing_section:status update requirements": "Add ## Status Update Requirements section",
    "missing_section:inputs": "Add ## Required Inputs (or ## Inputs to Read First) section",
    "missing_section:commands": "Add ## Commands to Run (or ## Test Commands) section",
    "missing_section:commit": "Add ## Commit Message section",
    "missing_rule:no_ellipses_in_walkthrough": (
        "Add the literal text: 'No ellipses in walkthrough.'"
    ),
    "missing_reference:STATUS.md": "Reference docs/phases/STATUS.md in the prompt body",
    "missing_unknown_unknown_discovery_section:### §0a": (
        "Add '### §0a — Known-token audit' section with input/output token list and term-binding table"
    ),
    "missing_unknown_unknown_discovery_section:### §0b": (
        "Add '### §0b — Concept-discovery search' section with search strategy and pre-execution claim table"
    ),
    "missing_unknown_unknown_discovery_section:### §0c": (
        "Add '### §0c — Contradiction and non-claim search' section"
    ),
    "missing_unknown_unknown_discovery_section:### §0d": (
        "Add '### §0d — Source expansion and newly discovered tokens' section including the MemPalace direct-read clause"
    ),
}


def _error_to_refutation_report(
    error: str, candidate_path: str, replay_command: str
) -> dict:
    """Convert a single validate_phase_prompt error string to a RefutationReport dict."""
    # Determine severity — match by prefix
    severity = SEVERITY_MINOR
    correction = f"Fix: {error}"
    for prefix, sev in _ERROR_SEVERITY.items():
        if error.startswith(prefix):
            severity = sev
            correction = _ERROR_CORRECTION.get(prefix, f"Fix: {error}")
            break

    return {
        "failed_invariant": error,
        "source_artifact": candidate_path,
        "correction_direction": correction,
        "severity": severity,
        "replay_command": replay_command,
        "affected_obl_or_cdl": None,
    }


def run_evaluation(candidate_path: str, objective_text: str) -> dict:
    """Run validate_phase_prompt.py against the candidate and return structured results.

    Returns:
        dict with keys: passed, failure_count, summary, refutation_reports
    """
    replay_command = REPLAY_COMMAND_TEMPLATE.format(candidate=candidate_path)

    # Find the project root (two levels up from this file: tools/evaluators/ -> project root)
    root = Path(__file__).resolve().parent.parent.parent
    python = root / ".venv" / "bin" / "python"
    if not python.exists():
        python = Path(sys.executable)

    validator = root / "tools" / "validate_phase_prompt.py"
    if not validator.exists():
        return {
            "passed": False,
            "failure_count": 1,
            "summary": "validate_phase_prompt.py not found",
            "refutation_reports": [
                {
                    "failed_invariant": "validator_tool_missing",
                    "source_artifact": str(validator),
                    "correction_direction": "Ensure tools/validate_phase_prompt.py exists",
                    "severity": SEVERITY_CRITICAL,
                    "replay_command": replay_command,
                    "affected_obl_or_cdl": None,
                }
            ],
        }

    proc = subprocess.run(
        [str(python), str(validator), candidate_path],
        capture_output=True,
        text=True,
        timeout=30,
    )

    stdout = proc.stdout.strip()
    errors: list[str] = []

    if proc.returncode == 0:
        # VALID: <path>
        return {
            "passed": True,
            "failure_count": 0,
            "summary": f"VALID: {candidate_path}",
            "refutation_reports": [],
        }

    # Parse error lines: each starts with "- "
    for line in stdout.splitlines():
        if line.startswith("- "):
            errors.append(line[2:].strip())

    if not errors and proc.returncode != 0:
        # Unexpected output format
        errors.append(f"validator_unexpected_output: {stdout[:200]}")

    reports = [
        _error_to_refutation_report(e, candidate_path, replay_command)
        for e in errors
    ]

    return {
        "passed": False,
        "failure_count": len(errors),
        "summary": f"INVALID: {len(errors)} error(s)",
        "refutation_reports": reports,
    }
