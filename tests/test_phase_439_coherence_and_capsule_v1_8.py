"""Phase 439 coherence and capsule v1.8 tests."""

from __future__ import annotations

import subprocess
from pathlib import Path

COHERENCE_PATH = Path("docs/specs/ilc_integration_coherence_report_439_v0.1.md")
CAPSULE_PATH = Path("docs/specs/ilc_antigravity_context_capsule_v1.8.md")
DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
PHASE_439_COMMIT_SUBJECT = "docs(g8): phase 439 coherence and capsule v1.8"


def _changed_paths_for_commit(commit_ref: str) -> set[str]:
    result = subprocess.run(
        ["git", "show", "--name-only", "--pretty=", commit_ref],
        capture_output=True,
        check=True,
        text=True,
    )
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


def _resolve_phase_439_commit_ref() -> str:
    result = subprocess.run(
        ["git", "log", "--format=%H%x09%s"],
        capture_output=True,
        check=True,
        text=True,
    )
    required_paths = {
        str(COHERENCE_PATH),
        str(CAPSULE_PATH),
        "tests/test_phase_439_coherence_and_capsule_v1_8.py",
    }
    matching_commits: list[str] = []
    for line in result.stdout.splitlines():
        if "\t" not in line:
            continue
        commit_hash, subject = line.split("\t", 1)
        if subject.strip() == PHASE_439_COMMIT_SUBJECT:
            matching_commits.append(commit_hash)

    for commit_ref in matching_commits:
        changed_paths = _changed_paths_for_commit(commit_ref)
        if changed_paths == required_paths:
            return commit_ref

    if matching_commits:
        raise AssertionError("phase_439_commit_subject_present_but_no_qualifying_synthesis_commit")
    raise AssertionError("phase_439_commit_not_present_in_local_history")


def _assert_phase_439_scope(commit_ref: str) -> None:
    changed_paths = _changed_paths_for_commit(commit_ref)
    required_paths = {
        str(COHERENCE_PATH),
        str(CAPSULE_PATH),
        "tests/test_phase_439_coherence_and_capsule_v1_8.py",
    }
    assert changed_paths == required_paths, f"phase_439_scope_mismatch:{sorted(changed_paths)}"
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert not any(path.startswith("ilc_core/") for path in changed_paths)
    assert "tools/runtime_baseline.py" not in changed_paths


def test_coherence_report_has_required_headings() -> None:
    text = COHERENCE_PATH.read_text(encoding="utf-8")
    for heading in (
        "## 1. Runtime tranche settlement",
        "## 2. Treasury P_e review outcome",
        "## 3. Window 434-440 boundary state",
        "## 4. Phase 440 pointer",
    ):
        assert heading in text


def test_coherence_report_contains_required_tokens() -> None:
    text = COHERENCE_PATH.read_text(encoding="utf-8")
    for token in (
        "The numbered runtime tranche authorized by Phase 434 completed in Phases 435 and 436.",
        "Phase 437 published the settled runtime-tranche findings memo without further runtime mutation.",
        "Phase 438 confirmed that all three Phase-431 prerequisites remain unsatisfied.",
        "CDL-050 remains unopened and unjustified at the close of Phase 439.",
        "Public packaging/bootstrap work remains outside the numbered window.",
        "Phase 440 is the next authorized closure-gate phase for Window 434-440.",
    ):
        assert token in text


def test_capsule_has_required_headings() -> None:
    text = CAPSULE_PATH.read_text(encoding="utf-8")
    for heading in (
        "## 1. Current window state",
        "## 2. Runtime tranche settlement",
        "## 3. Treasury P_e carry-forward state",
        "## 4. Release-engineering boundary",
        "## 5. Next phase pointer",
    ):
        assert heading in text


def test_capsule_contains_required_tokens() -> None:
    text = CAPSULE_PATH.read_text(encoding="utf-8")
    for token in (
        "Supersedes: docs/specs/ilc_antigravity_context_capsule_v1.7.md",
        "This capsule is self-contained.",
        "Window 440 is the closure-gate lane for Window 434-440.",
        "CDL-049 remains ratified and unaffected by Window 434-440 runtime-tranche work.",
        "The numbered runtime tranche is complete after Phases 435 and 436.",
        "Treasury P_e prerequisites remain unsatisfied after Phase 438, so CDL-050 remains unopened.",
        "Public packaging/bootstrap work remains on the parallel release-engineering track.",
        "Phase 440 is the next authorized phase.",
    ):
        assert token in text


def test_capsule_and_coherence_preserve_release_boundary() -> None:
    coherence_text = COHERENCE_PATH.read_text(encoding="utf-8")
    capsule_text = CAPSULE_PATH.read_text(encoding="utf-8")
    assert "Public packaging/bootstrap work remains outside the numbered window." in coherence_text
    assert "Public packaging/bootstrap work remains on the parallel release-engineering track." in capsule_text


def test_phase_439_commit_did_not_mutate_decision_log() -> None:
    commit_ref = _resolve_phase_439_commit_ref()
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert str(DECISION_LOG_PATH) not in changed_paths


def test_phase_439_scope_is_exact() -> None:
    commit_ref = _resolve_phase_439_commit_ref()
    _assert_phase_439_scope(commit_ref)
