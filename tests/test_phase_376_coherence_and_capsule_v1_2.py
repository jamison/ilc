"""Contract tests for Phase 376 coherence and capsule v1.2 artifact set."""

from __future__ import annotations

from pathlib import Path
import subprocess


COHERENCE_PATH = Path("docs/specs/ilc_integration_coherence_report_376_v0.1.md")
CAPSULE_PATH = Path("docs/specs/ilc_antigravity_context_capsule_v1.2.md")
DECISION_LOG_PATH = "docs/specs/ilc_constitutional_decision_log_v0.1.md"
SUBJECT_TOKEN = "docs(g8): phase 376 coherence and capsule v1.2"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_coherence_artifact_exists_with_required_headings() -> None:
    assert COHERENCE_PATH.exists()
    text = _read(COHERENCE_PATH)
    for heading in (
        "## 1. Scope and non-ratifying boundary",
        "## 2. Governance-first track completion (Phases 368-374)",
        "## 3. CDL-039 prelock finalization summary",
        "## 4. V-series activation-precondition summary (Phase 375)",
        "## 5. Epoch disambiguation closure (two-epoch architecture)",
        "## 6. SIM taxonomy and interpretation closure",
        "## 7. Phase 377 closure preconditions",
        "## 8. Non-goals and canonical anchors",
    ):
        assert heading in text


def test_coherence_contains_required_tokens() -> None:
    text = _read(COHERENCE_PATH)
    for token in (
        "Modeled outputs are non-ratifying evidence inputs.",
        "CDL-039 prelock is finalized in Phase 374; CDL-039 remains open and unratified.",
        "Five-invariant prelock set is frozen for ratification-lane carry-forward.",
        "Two-timescale closure: validation-epoch liveness and issuance-epoch partition reconciliation.",
        "CDL-038 recovery clause text is now explicit in prelock finalization evidence.",
        "V-series activation-precondition matrix is locked in Phase 375 for Window 378+ planning.",
        "Two-epoch architecture is now explicit: issuance_epoch=1 month, validation_epoch=1 minute.",
        "SIM taxonomy closure for this lane: SIM-003 graph growth, SIM-004 partition resilience, SIM-005 agent death/orphaning.",
        "No decision-log mutation occurred. No ilc_core runtime files were changed.",
    ):
        assert token in text


def test_capsule_v1_2_exists_self_contained_and_supersedes_v1_1() -> None:
    assert CAPSULE_PATH.exists()
    text = _read(CAPSULE_PATH)
    assert "Supersedes: docs/specs/ilc_antigravity_context_capsule_v1.1.md" in text
    assert "This capsule is self-contained." in text
    for heading in (
        "## 1. Project identity",
        "## 2. Core architectural invariants",
        "## 3. Project state (as of Phase 376 completion)",
        "## 4. Window 368-377 governance-first completion state",
        "## 5. CDL-039 prelock finalization state",
        "## 6. V-series planning boundary for Window 378+",
        "## 7. Two-epoch architecture and SIM interpretation closure",
        "## 8. Runtime authorization boundary",
        "## 9. Phase 377 closure preconditions",
        "## 10. Change log from v1.1",
        "## 11. Key canonical anchors",
    ):
        assert heading in text


def test_capsule_contains_required_state_and_boundary_tokens() -> None:
    text = _read(CAPSULE_PATH)
    for token in (
        "Phase 376 complete.",
        "Phase 377 next.",
        "CDL-039 is prelock-finalized only; it is not ratified in Window 368-377.",
        "Phase-374 finalized prelock includes five invariants, two-timescale closure, and explicit post-expiry recovery clause text.",
        "Phase-375 locked V-series activation-precondition planning for Window 378+ with no runtime implementation.",
        "Two-epoch architecture lock: issuance_epoch=1 month; validation_epoch=1 minute.",
        "SIM interpretation closure: SIM-003/SIM-004/SIM-005 mapped to explicit epoch contexts and carry-forward constants.",
        "CDL-034 through CDL-038 runtime implementation tranches remain complete from phases 360-364.",
    ):
        assert token in text


def test_coherence_and_capsule_include_v_series_and_two_epoch_closure() -> None:
    coherence = _read(COHERENCE_PATH)
    capsule = _read(CAPSULE_PATH)
    assert "`CDL-V1`: `ready_for_window_378_authorization`" in coherence
    assert "`CDL-V2`: `ready_for_window_378_authorization`" in coherence
    assert "`CDL-V3`: `requires_additional_governance_input`" in coherence
    assert "`CDL-V7`: `requires_additional_governance_input`" in coherence
    assert "issuance_epoch=1 month" in coherence
    assert "validation_epoch=1 minute" in coherence
    assert "issuance_epoch=1 month; validation_epoch=1 minute." in capsule


def _changed_paths_for_commit(commit_ref: str) -> set[str]:
    result = subprocess.run(
        ["git", "show", "--name-only", "--pretty=", commit_ref],
        capture_output=True,
        check=True,
        text=True,
    )
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


def _resolve_phase_376_commit_ref_or_fail() -> str:
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
        "docs/specs/ilc_integration_coherence_report_376_v0.1.md",
        "docs/specs/ilc_antigravity_context_capsule_v1.2.md",
        "tests/test_phase_376_coherence_and_capsule_v1_2.py",
    }
    for commit_ref in matching_commits:
        changed = _changed_paths_for_commit(commit_ref)
        if required_paths.issubset(changed):
            return commit_ref

    if matching_commits:
        raise AssertionError("phase_376_commit_subject_present_but_no_qualifying_coherence_commit")
    raise AssertionError("phase_376_commit_not_present_in_local_history")


def test_phase_376_commit_touched_required_paths_and_not_decision_log() -> None:
    commit_ref = _resolve_phase_376_commit_ref_or_fail()
    changed = _changed_paths_for_commit(commit_ref)
    assert DECISION_LOG_PATH not in changed


def test_phase_376_commit_touched_no_ilc_core_paths() -> None:
    commit_ref = _resolve_phase_376_commit_ref_or_fail()
    changed = _changed_paths_for_commit(commit_ref)
    forbidden = [path for path in changed if path.startswith("ilc_core/")]
    assert not forbidden, f"phase_376_runtime_mutations:{forbidden}"
