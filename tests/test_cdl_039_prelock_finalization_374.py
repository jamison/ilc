"""Contract tests for Phase 374 CDL-039 prelock finalization artifact."""

from __future__ import annotations

from pathlib import Path
import re
import subprocess


ARTIFACT_PATH = Path("docs/specs/ilc_cdl_039_prelock_finalization_374_v0.1.md")
DECISION_LOG_PATH = "docs/specs/ilc_constitutional_decision_log_v0.1.md"
SUBJECT_TOKEN = "docs(g8): phase 374 cdl-039 prelock finalization"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_artifact_exists_and_has_required_headings() -> None:
    assert ARTIFACT_PATH.exists()
    text = _read(ARTIFACT_PATH)
    for heading in (
        "## 1. Scope and non-ratifying boundary",
        "## 2. Prelock evidence continuity and consolidation",
        "## 3. Finalized invariant set for CDL-039 prelock",
        "## 4. Two-timescale protocol closure",
        "## 5. Final calibration dispositions for prelock",
        "## 6. CDL-038 scope boundary disposition",
        "## 7. Phase 374 frozen prelock package",
        "## 8. Carry-forward constraints for ratification lane",
        "## 9. Non-goals and residual risk",
    ):
        assert heading in text


def test_artifact_contains_required_finalization_tokens() -> None:
    text = _read(ARTIFACT_PATH)
    for token in (
        "Modeled outputs are non-ratifying evidence inputs.",
        "This artifact finalizes CDL-039 prelock evidence in Window 368-377 without ratifying CDL-039.",
        "This artifact extends the Phase-359, Phase-372, and Phase-373 prelock artifacts additively as a consolidated prelock package.",
        "Transport Envelope routing headers MUST NOT carry creator_agent_id; authorship attribution is resolved from Authored Payload and protocol interpretation.",
        "Transport channel routing field MUST be an opaque identifier (CID or uniformly random bytes); human-readable channel labels are UI-layer concerns only.",
        "short-timescale CDL-039 context: validation epoch liveness and Levin stress-cascade reconnection handling.",
        "long-timescale CDL-039 context: issuance epoch partition divergence and highest_ecu_wins reconciliation.",
        "cdl_038_recovery_scope disposition: requires_explicit_cdl_039_clause.",
        "Phase 374 freezes prelock text and calibration dispositions but does not ratify CDL-039.",
        "No decision-log mutation occurred. No ilc_core runtime files were changed.",
    ):
        assert token in text


def test_artifact_contains_disposition_entries_for_all_parameter_groups() -> None:
    text = _read(ARTIFACT_PATH)
    groups = (
        "`R_partition_cross_ref`",
        "`H_release`",
        "`retention_epochs`",
        "`timeout_policy` / `stake_recovery_policy`",
        "`cdl_038_recovery_scope`",
    )
    for group in groups:
        assert group in text

    standard_values = {"`calibrated_candidate`", "`bounded_range`", "`deferred_with_reason`"}
    assert any(value in text for value in standard_values)

    assert "`requires_explicit_cdl_039_clause`" in text
    assert any(
        marker in text
        for marker in (
            "`covered_by_existing_cdl_038_semantics`",
            "`requires_explicit_cdl_039_clause`",
            "`deferred_with_reason`",
        )
    )
    # Section 6 must carry substantive clause text, not only the disposition label.
    assert "## 6. CDL-038 scope boundary disposition" in text
    assert "Proposed CDL-039 prelock clause text for post-expiry recovery semantics:" in text
    assert "must re-enter via a successor-node re-assertion path" in text
    assert "no automatic carry-forward of expired-node promotion eligibility is permitted" in text


def test_artifact_contains_non_ratifying_finalization_statement() -> None:
    text = _read(ARTIFACT_PATH)
    assert "This artifact finalizes CDL-039 prelock evidence in Window 368-377 without ratifying CDL-039." in text
    assert "Phase 374 freezes prelock text and calibration dispositions but does not ratify CDL-039." in text


def test_artifact_contains_explicit_carry_forward_constraints_for_ratification_lane() -> None:
    text = _read(ARTIFACT_PATH)
    assert "## 8. Carry-forward constraints for ratification lane" in text
    assert "ratification lane must preserve non-authorship transport header boundary" in text
    assert "ratification lane must preserve opaque channel identifier requirement" in text


def _changed_paths_for_commit(commit_ref: str) -> set[str]:
    result = subprocess.run(
        ["git", "show", "--name-only", "--pretty=", commit_ref],
        capture_output=True,
        check=True,
        text=True,
    )
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


def _resolve_phase_374_commit_ref_or_fail() -> str:
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
        "docs/specs/ilc_cdl_039_prelock_finalization_374_v0.1.md",
        "tests/test_cdl_039_prelock_finalization_374.py",
    }
    for commit_ref in matching_commits:
        changed = _changed_paths_for_commit(commit_ref)
        if required_paths.issubset(changed):
            return commit_ref

    if matching_commits:
        raise AssertionError("phase_374_commit_subject_present_but_no_qualifying_finalization_commit")
    raise AssertionError("phase_374_commit_not_present_in_local_history")


def test_phase_374_commit_touched_required_paths_and_not_decision_log() -> None:
    commit_ref = _resolve_phase_374_commit_ref_or_fail()
    changed = _changed_paths_for_commit(commit_ref)
    assert DECISION_LOG_PATH not in changed


def test_phase_374_commit_touched_no_ilc_core_paths() -> None:
    commit_ref = _resolve_phase_374_commit_ref_or_fail()
    changed = _changed_paths_for_commit(commit_ref)
    forbidden = [path for path in changed if path.startswith("ilc_core/")]
    assert not forbidden, f"phase_374_runtime_mutations:{forbidden}"
