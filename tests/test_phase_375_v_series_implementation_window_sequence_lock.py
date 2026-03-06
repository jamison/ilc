"""Contract tests for Phase 375 V-series implementation window sequence lock artifact."""

from __future__ import annotations

from pathlib import Path
import re
import subprocess


ARTIFACT_PATH = Path("docs/specs/ilc_v_series_implementation_window_sequence_lock_375_v0.1.md")
DECISION_LOG_PATH = "docs/specs/ilc_constitutional_decision_log_v0.1.md"
SUBJECT_TOKEN = "docs(g8): phase 375 v-series implementation window sequence lock"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_artifact_exists_and_contains_required_headings() -> None:
    assert ARTIFACT_PATH.exists()
    text = _read(ARTIFACT_PATH)
    for heading in (
        "## 1. Scope and planning-only boundary",
        "## 2. Inputs and constitutional carry-forward",
        "## 3. V-series classification and enforcement boundary",
        "## 4. Window 378+ implementation-window sequencing principles",
        "## 5. Activation-precondition matrix",
        "## 6. Explicit non-goals in Window 368-377",
        "## 7. Dependencies for Phase 376 and Phase 377",
        "## 8. Residual risks and open planning questions",
    ):
        assert heading in text


def test_artifact_contains_required_planning_boundary_tokens() -> None:
    text = _read(ARTIFACT_PATH)
    for token in (
        "Phase 375 is planning-only and non-ratifying.",
        "No runtime implementation is authorized in Phase 375.",
        "V-series implementation window scope: CDL-V1, CDL-V2, CDL-V3, CDL-V7 computational enforcement surfaces.",
        "CDL-V4, CDL-V5, CDL-V6 remain governance-procedural and implementation-barred unless reclassified by constitutional action.",
        "CDL-039 remains open after Phase 374 prelock finalization.",
        "Window 378+ is the earliest authorization boundary for D2d/network runtime enforcement.",
        "Phase 376 consumes this sequence lock for coherence and capsule v1.2 synthesis.",
        "Phase 377 consumes this sequence lock for closure-gate and 378+ handoff validation.",
        "No decision-log mutation occurred. No ilc_core runtime files were changed.",
    ):
        assert token in text


def test_matrix_contains_all_four_v_series_rows() -> None:
    text = _read(ARTIFACT_PATH)
    for row_id in ("CDL-V1", "CDL-V2", "CDL-V3", "CDL-V7"):
        pattern = (
            rf"\|\s*`{row_id}`\s*\|\s*[^|]+\|\s*`"
            r"(ready_for_window_378_authorization|requires_additional_governance_input)`\s*\|"
        )
        assert re.search(pattern, text), f"missing_or_malformed_matrix_row:{row_id}"


def test_matrix_uses_only_allowed_planning_status_values() -> None:
    text = _read(ARTIFACT_PATH)
    statuses = set(re.findall(r"`(ready_for_window_378_authorization|requires_additional_governance_input)`", text))
    assert statuses
    assert statuses.issubset({"ready_for_window_378_authorization", "requires_additional_governance_input"})


def test_artifact_contains_phase376_and_phase377_dependency_statements() -> None:
    text = _read(ARTIFACT_PATH)
    assert "Phase 376 consumes this sequence lock for coherence and capsule v1.2 synthesis." in text
    assert "Phase 377 consumes this sequence lock for closure-gate and 378+ handoff validation." in text


def _changed_paths_for_commit(commit_ref: str) -> set[str]:
    result = subprocess.run(
        ["git", "show", "--name-only", "--pretty=", commit_ref],
        capture_output=True,
        check=True,
        text=True,
    )
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


def _resolve_phase_375_commit_ref_or_fail() -> str:
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
        "docs/specs/ilc_v_series_implementation_window_sequence_lock_375_v0.1.md",
        "tests/test_phase_375_v_series_implementation_window_sequence_lock.py",
    }
    for commit_ref in matching_commits:
        changed = _changed_paths_for_commit(commit_ref)
        if required_paths.issubset(changed):
            return commit_ref

    if matching_commits:
        raise AssertionError("phase_375_commit_subject_present_but_no_qualifying_sequence_lock_commit")
    raise AssertionError("phase_375_commit_not_present_in_local_history")


def test_phase_375_commit_touched_required_paths_and_not_decision_log() -> None:
    commit_ref = _resolve_phase_375_commit_ref_or_fail()
    changed = _changed_paths_for_commit(commit_ref)
    assert DECISION_LOG_PATH not in changed


def test_phase_375_commit_touched_no_ilc_core_paths() -> None:
    commit_ref = _resolve_phase_375_commit_ref_or_fail()
    changed = _changed_paths_for_commit(commit_ref)
    forbidden = [path for path in changed if path.startswith("ilc_core/")]
    assert not forbidden, f"phase_375_runtime_mutations:{forbidden}"
