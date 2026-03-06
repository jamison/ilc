"""Contract tests for Phase 373 CDL-039 adversarial review and evidence freeze artifact."""

from __future__ import annotations

from pathlib import Path
import re
import subprocess

from ilc_core.testing.ratification_mutation_scope_guardrail import parse_decision_register_rows


ARTIFACT_PATH = Path("docs/specs/ilc_cdl_039_adversarial_review_and_evidence_freeze_373_v0.1.md")
DECISION_LOG_PATH = "docs/specs/ilc_constitutional_decision_log_v0.1.md"
SUBJECT_TOKEN = "docs(g8): phase 373 cdl-039 adversarial review evidence freeze"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_artifact_exists_with_required_headings() -> None:
    assert ARTIFACT_PATH.exists()
    text = _read(ARTIFACT_PATH)
    for heading in (
        "## 1. Scope and non-ratifying boundary",
        "## 2. Evidence inputs and prelock continuity",
        "## 3. Adversarial method and threat matrix",
        "## 4. Partition-state flapping adversarial findings (R_partition_cross_ref, H_release)",
        "## 5. Cluster membership reconstruction adversarial findings",
        "## 6. Private-visibility expiry and promotion-boundary adversarial findings",
        "## 7. Channel identifier leakage adversarial findings",
        "## 8. Timeout and recovery policy adversarial calibration findings",
        "## 9. Calibration outcomes and frozen evidence set",
        "## 10. Carry-forward package for Phase 374",
        "## 11. Non-goals and unresolved residual risk",
    ):
        assert heading in text


def test_artifact_has_required_tokens() -> None:
    text = _read(ARTIFACT_PATH)
    for token in (
        "Modeled outputs are non-ratifying evidence inputs.",
        "This artifact extends the Phase-359 and Phase-372 prelock artifacts additively as CDL-039 prelock evidence.",
        "Adversarial review required passive-observer cluster-membership reconstruction attempts.",
        "Adversarial review required partition-state flapping stress for R_partition_cross_ref and H_release.",
        "Adversarial review required expiry-path abuse tests around promotion_receipt timing.",
        "Adversarial review required channel-identifier semantic inference probes.",
        "Adversarial review required timeout false-positive and false-negative tradeoff analysis under validation-epoch assumptions.",
        "CDL-038 scope boundary for post-expiry recovery receives explicit disposition in this phase.",
        "Phase 373 freezes evidence and calibration outcomes but does not ratify CDL-039.",
        "Phase 374 consumes this evidence-freeze package for prelock finalization.",
        "No decision-log mutation occurred. No ilc_core runtime files were changed.",
    ):
        assert token in text


def test_calibration_outcome_disposition_present_for_all_five_parameter_groups() -> None:
    text = _read(ARTIFACT_PATH)
    rows = [
        "`R_partition_cross_ref`",
        "`H_release`",
        "`retention_epochs`",
        "`timeout_policy` / `stake_recovery_policy`",
        "`cdl_038_recovery_scope`",
    ]
    for row in rows:
        assert row in text

    allowed = {"calibrated_candidate", "bounded_range", "deferred_with_reason", "covered_by_existing_cdl_038_semantics", "requires_explicit_cdl_039_clause"}
    dispositions = set(re.findall(r"`([a-z_]+)`", text))
    assert "bounded_range" in dispositions or "deferred_with_reason" in dispositions
    assert "requires_explicit_cdl_039_clause" in text
    assert any(tag in text for tag in allowed)


def test_artifact_includes_phase374_carry_forward_statement() -> None:
    text = _read(ARTIFACT_PATH)
    assert "Phase 374 carry-forward package includes:" in text
    assert "explicit requirement to close `cdl_038_recovery_scope` in prelock text" in text


def test_artifact_includes_non_ratifying_boundary_statement() -> None:
    text = _read(ARTIFACT_PATH)
    assert "Phase 373 freezes evidence and calibration outcomes but does not ratify CDL-039." in text


def _changed_paths_for_commit(commit_ref: str) -> set[str]:
    result = subprocess.run(
        ["git", "show", "--name-only", "--pretty=", commit_ref],
        capture_output=True,
        check=True,
        text=True,
    )
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


def _decision_log_text_at_ref(ref: str) -> str:
    result = subprocess.run(
        ["git", "show", f"{ref}:{DECISION_LOG_PATH}"],
        capture_output=True,
        check=False,
        text=True,
    )
    if result.returncode != 0:
        raise AssertionError(f"unable_to_read_decision_log_at_ref:{ref}: {result.stderr.strip()}")
    return result.stdout


def _resolve_phase_373_commit_ref_or_fail() -> str:
    result = subprocess.run(
        ["git", "log", "--format=%H%x09%s"],
        capture_output=True,
        check=True,
        text=True,
    )
    matching_commits: list[str] = []
    for line in result.stdout.splitlines():
        if "\t" not in line:
            continue
        commit_hash, subject = line.split("\t", 1)
        if subject.strip().lower() == SUBJECT_TOKEN.lower():
            matching_commits.append(commit_hash)

    required_paths = {
        "docs/specs/ilc_cdl_039_adversarial_review_and_evidence_freeze_373_v0.1.md",
        "tests/test_cdl_039_adversarial_review_and_evidence_freeze_373.py",
    }
    for commit_ref in matching_commits:
        changed = _changed_paths_for_commit(commit_ref)
        if required_paths.issubset(changed):
            return commit_ref

    if matching_commits:
        raise AssertionError("phase_373_commit_subject_present_but_no_qualifying_evidence_freeze_commit")
    raise AssertionError("phase_373_commit_not_present_in_local_history")


def test_phase_373_cdl039_row_is_historical_open_reference() -> None:
    # The Phase-373 `CDL-039` row is a historical prelock reference.
    rows = parse_decision_register_rows(_decision_log_text_at_ref(_resolve_phase_373_commit_ref_or_fail()))
    row = rows["CDL-039"]
    assert row["status"] == "open"
    assert "ratified_phase" not in row
    assert "ratified_date" not in row
    assert "evidence_document" not in row


def test_phase_373_commit_touched_required_paths_and_not_decision_log() -> None:
    commit_ref = _resolve_phase_373_commit_ref_or_fail()
    changed = _changed_paths_for_commit(commit_ref)
    assert DECISION_LOG_PATH not in changed


def test_phase_373_commit_touched_no_ilc_core_paths() -> None:
    commit_ref = _resolve_phase_373_commit_ref_or_fail()
    changed = _changed_paths_for_commit(commit_ref)
    forbidden = [path for path in changed if path.startswith("ilc_core/")]
    assert not forbidden, f"phase_373_runtime_mutations:{forbidden}"
