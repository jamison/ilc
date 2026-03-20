from __future__ import annotations

import subprocess
from pathlib import Path


COHERENCE_REPORT_PATH = Path("docs/specs/ilc_window_441_449_coherence_report_448_v0.1.md")
CAPSULE_PATH = Path("docs/specs/ilc_antigravity_context_capsule_v1.9.md")
DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
PHASE_448_SUBJECT_TOKEN = "docs(g8): phase 448 coherence and capsule v1.9"
REQUIRED_COHERENCE_HEADINGS = (
    "## 1. Constitutional consensus block settlement (Phases 441-443)",
    "## 2. Consensus runtime tranche settlement (Phases 444-446)",
    "## 3. Adversarial regression hardening settlement (Phase 447)",
    "## 4. Cross-cutting issues and boundary observations",
    "## 5. Window 441-449 boundary state",
    "## 6. Phase 449 pointer",
)
REQUIRED_COHERENCE_TOKENS = (
    "CDL-051 was ratified in Phase 443 after constitutional opening in Phase 441 and prelock hardening in Phase 442.",
    "The consensus runtime tranche authorized by CDL-051 completed in Phases 444, 445, and 446.",
    "Phase 447 published the consensus findings memo and adversarial regression guards without introducing new runtime surfaces.",
    "CDL-050 remains unopened and unjustified at the close of Phase 448.",
    "No Treasury P_e authorization occurred in Window 441-449.",
    "Phase 449 is the next authorized closure-gate phase for Window 441-449.",
)
REQUIRED_CAPSULE_HEADINGS = (
    "## 1. Current window state",
    "## 2. CDL status summary",
    "## 3. Consensus runtime surfaces added",
    "## 4. Treasury P_e carry-forward state",
    "## 5. Release-engineering boundary",
    "## 6. Next phase pointer",
)
REQUIRED_CAPSULE_TOKENS = (
    "Supersedes: docs/specs/ilc_antigravity_context_capsule_v1.8.md",
    "This capsule is self-contained.",
    "Active window: 441-449 (closing).",
    "CDL-051 is ratified. CDL-050 remains unopened.",
    "epoch_state_runtime.py (Phase 444) and finality_evaluator.py (Phase 445) are the key runtime surfaces added in Window 441-449.",
    "Treasury P_e prerequisites remain unsatisfied and CDL-050 remains unopened at the close of Phase 448.",
    "Public packaging/bootstrap work remains on the parallel release-engineering track.",
    "Phase 449 is the next authorized phase.",
)
EXPECTED_CHANGED_PATHS = {
    "docs/specs/ilc_window_441_449_coherence_report_448_v0.1.md",
    "docs/specs/ilc_antigravity_context_capsule_v1.9.md",
    "tests/test_phase_448_coherence_and_capsule_v1_9.py",
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _changed_paths_for_commit(commit_ref: str) -> set[str]:
    result = subprocess.run(
        ["git", "show", "--name-only", "--pretty=", commit_ref],
        capture_output=True,
        check=True,
        text=True,
    )
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


def _resolve_phase_448_commit_ref() -> str:
    result = subprocess.run(
        ["git", "log", "--format=%H%x09%s"],
        capture_output=True,
        check=True,
        text=True,
    )
    saw_subject = False
    for line in result.stdout.splitlines():
        if "\t" not in line:
            continue
        commit_hash, subject = line.split("\t", 1)
        if subject.strip() != PHASE_448_SUBJECT_TOKEN:
            continue
        saw_subject = True
        if _changed_paths_for_commit(commit_hash) == EXPECTED_CHANGED_PATHS:
            return commit_hash
    if saw_subject:
        raise AssertionError("phase_448_commit_subject_present_but_no_qualifying_synthesis_commit")
    raise AssertionError("phase_448_commit_not_present_in_local_history")


def test_coherence_report_exists_and_contains_required_headings() -> None:
    text = _read(COHERENCE_REPORT_PATH)

    assert COHERENCE_REPORT_PATH.exists()
    for heading in REQUIRED_COHERENCE_HEADINGS:
        assert heading in text


def test_coherence_report_contains_required_tokens() -> None:
    text = _read(COHERENCE_REPORT_PATH)

    for token in REQUIRED_COHERENCE_TOKENS:
        assert token in text


def test_capsule_v1_9_exists_and_contains_required_headings() -> None:
    text = _read(CAPSULE_PATH)

    assert CAPSULE_PATH.exists()
    for heading in REQUIRED_CAPSULE_HEADINGS:
        assert heading in text


def test_capsule_v1_9_contains_required_tokens() -> None:
    text = _read(CAPSULE_PATH)

    for token in REQUIRED_CAPSULE_TOKENS:
        assert token in text


def test_capsule_and_coherence_report_preserve_release_engineering_boundary() -> None:
    coherence = _read(COHERENCE_REPORT_PATH)
    capsule = _read(CAPSULE_PATH)

    assert "release-engineering track" in coherence
    assert "release-engineering track" in capsule
    assert "Supersedes: docs/specs/ilc_antigravity_context_capsule_v1.8.md" in capsule


def test_phase_448_commit_touches_exactly_required_paths() -> None:
    commit_ref = _resolve_phase_448_commit_ref()
    assert _changed_paths_for_commit(commit_ref) == EXPECTED_CHANGED_PATHS


def test_phase_448_commit_respects_non_mutation_boundaries() -> None:
    commit_ref = _resolve_phase_448_commit_ref()
    changed_paths = _changed_paths_for_commit(commit_ref)

    assert str(DECISION_LOG_PATH) not in changed_paths
    assert not any(path.startswith("ilc_core/") for path in changed_paths)
    assert not any(path.startswith("tools/") for path in changed_paths)
    assert not any(
        path.startswith(prefix)
        for prefix in (
            "ILC_release_track/",
            "release_engineering/",
            "docs/release_engineering/",
            "docs/packaging/",
        )
        for path in changed_paths
    )
