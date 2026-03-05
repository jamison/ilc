"""Contract tests for Phase 366 coherence and capsule v1.1 artifacts."""

from __future__ import annotations

from pathlib import Path
import subprocess


COHERENCE_PATH = Path("docs/specs/ilc_integration_coherence_report_366_v0.1.md")
CAPSULE_PATH = Path("docs/specs/ilc_antigravity_context_capsule_v1.1.md")
SUBJECT_TOKEN = "docs(g8): phase 366 coherence and capsule v1.1"
DECISION_LOG_PATH = "docs/specs/ilc_constitutional_decision_log_v0.1.md"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_coherence_artifact_has_required_headings() -> None:
    assert COHERENCE_PATH.exists()
    text = _read(COHERENCE_PATH)
    for heading in (
        "## 1. Scope",
        "## 2. Runtime implementation status (CDL-034 through CDL-038)",
        "## 3. SIM-001 interpretation",
        "## 4. SIM-002 interpretation",
        "## 5. SIM-003 interpretation",
        "## 6. Gap-analysis carry-forward",
        "## 7. Phase-367 closure preconditions",
        "## 8. Non-goals and canonical anchors",
    ):
        assert heading in text


def test_coherence_artifact_has_required_interpretation_tokens() -> None:
    text = _read(COHERENCE_PATH)
    for token in (
        "SIM-001 minimum viable N_agents modeled threshold: 10000",
        "SIM-002 recommended write_fee_multiplier bound (modeled): <= 0.5",
        "SIM-003 recommended pruning policy (modeled): ecu_score_floor=0.5, retention_epochs=1, snapshot_interval=50",
        "Modeled outputs are non-ratifying evidence inputs.",
        "No decision-log mutation occurred. No ilc_core runtime files were changed.",
    ):
        assert token in text


def test_capsule_v11_exists_is_self_contained_and_supersedes_v10() -> None:
    assert CAPSULE_PATH.exists()
    text = _read(CAPSULE_PATH)
    assert "Supersedes: docs/specs/ilc_antigravity_context_capsule_v1.0.md" in text
    assert "This capsule is self-contained." in text
    for heading in (
        "## 1. Project identity",
        "## 2. Core architectural invariants",
        "## 3. Project state (as of Phase 366 completion)",
        "## 4. Window 358-367 constitutional and runtime state",
        "## 5. Implemented node-schema runtime surfaces",
        "## 6. Simulation evidence now available",
        "## 7. Runtime authorization and implementation boundary",
        "## 8. Phase 367 closure preconditions",
        "## 9. Change log from v1.0",
        "## 10. Key canonical anchors",
    ):
        assert heading in text


def test_capsule_v11_has_required_state_tokens() -> None:
    text = _read(CAPSULE_PATH)
    for token in (
        "Phase 366 complete.",
        "Phase 367 next.",
        "CDL-034 through CDL-038 runtime implementation tranches are complete in phases 360-364.",
        "CDL-039 remains open and implementation-barred in this window.",
        "ILC co-opts existing wallet trust rather than building competing wallet infrastructure.",
    ):
        assert token in text


def test_gap_analysis_carry_forward_anchor_is_present() -> None:
    coherence_text = _read(COHERENCE_PATH)
    capsule_text = _read(CAPSULE_PATH)
    token = "docs/specs/ilc_open_requirements_and_unknown_unknowns_analysis_354_v0.1.md"
    assert token in coherence_text
    assert token in capsule_text


def _changed_paths_for_commit(commit_ref: str) -> set[str]:
    result = subprocess.run(
        ["git", "show", "--name-only", "--pretty=", commit_ref],
        capture_output=True,
        check=True,
        text=True,
    )
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


def _resolve_phase_366_commit_ref_or_fail() -> str:
    result = subprocess.run(
        ["git", "log", "--format=%H%x09%s"],
        capture_output=True,
        check=True,
        text=True,
    )
    saw_subject_match = False
    for line in result.stdout.splitlines():
        if "\t" not in line:
            continue
        commit_hash, subject = line.split("\t", 1)
        if subject.strip().lower() != SUBJECT_TOKEN.lower():
            continue
        saw_subject_match = True
        changed = _changed_paths_for_commit(commit_hash)
        if {
            "docs/specs/ilc_integration_coherence_report_366_v0.1.md",
            "docs/specs/ilc_antigravity_context_capsule_v1.1.md",
            "tests/test_phase_366_coherence_and_capsule_v1_1.py",
        }.issubset(changed):
            return commit_hash
    if saw_subject_match:
        raise AssertionError(
            "phase_366_commit_subject_present_but_no_qualifying_coherence_commit"
        )
    raise AssertionError("phase_366_commit_not_present_in_local_history")


def test_phase_366_commit_touched_required_paths_and_not_decision_log() -> None:
    commit_ref = _resolve_phase_366_commit_ref_or_fail()
    changed = _changed_paths_for_commit(commit_ref)
    assert DECISION_LOG_PATH not in changed


def test_phase_366_commit_touched_no_ilc_core_paths() -> None:
    commit_ref = _resolve_phase_366_commit_ref_or_fail()
    changed = _changed_paths_for_commit(commit_ref)
    forbidden = [path for path in changed if path.startswith("ilc_core/")]
    assert not forbidden, f"phase_366_runtime_mutations:{forbidden}"
