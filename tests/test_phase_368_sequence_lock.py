"""Contract tests for Phase 368 sequence-lock artifact."""

from __future__ import annotations

from pathlib import Path
import subprocess


SEQUENCE_LOCK_PATH = Path("docs/specs/ilc_phase_368_377_sequence_lock_v0.1.md")
DECISION_LOG_PATH = "docs/specs/ilc_constitutional_decision_log_v0.1.md"
SUBJECT_TOKEN = "phase 368 window 368-377 sequence lock governance-first boundary"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_sequence_lock_exists_and_has_required_headings() -> None:
    assert SEQUENCE_LOCK_PATH.exists()
    text = _read(SEQUENCE_LOCK_PATH)
    for heading in (
        "## 1. Purpose and window character",
        "## 2. Entry state from phase-367 closure",
        "## 3. Constitutional inventory and open lanes",
        "## 4. Locked phase table (368-377)",
        "## 5. Phase sensitivity classification",
        "## 6. Governance-first track (368-374)",
        "## 7. Implementation track boundary (375-377)",
        "## 8. CDL-039 prelock finalization boundary",
        "## 9. V-series runtime activation boundary",
        "## 10. D2d deferral and Levin-evaluation boundary",
        "## 11. Non-goals and explicit exclusions",
        "## 12. Forward pointer",
    ):
        assert heading in text


def test_governance_and_implementation_boundary_tokens_are_explicit() -> None:
    text = _read(SEQUENCE_LOCK_PATH)
    for token in (
        "Governance-first track: phases 368-374.",
        "Implementation-boundary track: phases 375-377, bounded by V-series runtime enforcement authorization only.",
        "CDL-039 remains open in Window 368-377; prelock finalization target is Phase 374.",
        "No CDL-039 ratification action is authorized in Window 368-377.",
        "CDL-V1 through CDL-V7 runtime activation decision is bounded to computational enforcement surfaces only.",
        "CDL-V4, CDL-V5, CDL-V6 remain governance-procedural and are implementation-barred unless explicitly reclassified.",
    ):
        assert token in text


def test_d2d_deferral_levin_and_sim_scope_tokens_are_explicit() -> None:
    text = _read(SEQUENCE_LOCK_PATH)
    for token in (
        "D2d runtime implementation remains deferred to Window 378+.",
        "No P2P peering loop, routing loop, or gossip runtime implementation is authorized in Window 368-377.",
        "Window 368 sequence-lock drafting must evaluate Levin gossip + coordinate mechanism proposals as D2d wire-protocol inputs.",
        "SIM-004 models network partition resilience and CDL-039 connectivity failure modes.",
        "SIM-005 models agent death and graph orphaning behavior under protocol conditions.",
        "Window 378 begins with D2d runtime implementation authorization review.",
    ):
        assert token in text


def test_locked_phase_table_rows_for_all_ten_phases_are_present() -> None:
    text = _read(SEQUENCE_LOCK_PATH)
    for token in (
        "Phase 368",
        "Phase 369",
        "Phase 370",
        "Phase 371",
        "Phase 372",
        "Phase 373",
        "Phase 374",
        "Phase 375",
        "Phase 376",
        "Phase 377",
    ):
        assert token in text


def test_cdl039_prelock_only_boundary_is_explicit() -> None:
    text = _read(SEQUENCE_LOCK_PATH)
    for token in (
        "prelock hardening and adversarial review occur in phases 372-373",
        "prelock finalization target is phase 374",
        "ratification is explicitly deferred beyond Window 368-377",
    ):
        assert token in text


def _changed_paths_for_commit(commit_ref: str) -> set[str]:
    result = subprocess.run(
        ["git", "show", "--name-only", "--pretty=", commit_ref],
        capture_output=True,
        check=True,
        text=True,
    )
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


def _resolve_phase_368_commit_ref_or_fail() -> str:
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
        if SUBJECT_TOKEN in subject.lower():
            matching_commits.append(commit_hash)

    required_paths = {
        "docs/specs/ilc_phase_368_377_sequence_lock_v0.1.md",
        "tests/test_phase_368_sequence_lock.py",
    }
    for commit_ref in matching_commits:
        changed = _changed_paths_for_commit(commit_ref)
        if required_paths.issubset(changed):
            return commit_ref

    if matching_commits:
        raise AssertionError("phase_368_commit_subject_present_but_no_qualifying_sequence_lock_commit")
    raise AssertionError("phase_368_commit_not_present_in_local_history")


def test_phase_commit_touched_required_paths_and_not_decision_log() -> None:
    commit_ref = _resolve_phase_368_commit_ref_or_fail()
    changed = _changed_paths_for_commit(commit_ref)
    assert "docs/specs/ilc_phase_368_377_sequence_lock_v0.1.md" in changed
    assert "tests/test_phase_368_sequence_lock.py" in changed
    assert DECISION_LOG_PATH not in changed


def test_phase_commit_touched_no_ilc_core_paths() -> None:
    commit_ref = _resolve_phase_368_commit_ref_or_fail()
    changed = _changed_paths_for_commit(commit_ref)
    forbidden = [path for path in changed if path.startswith("ilc_core/")]
    assert not forbidden, f"phase_368_runtime_mutations:{forbidden}"
