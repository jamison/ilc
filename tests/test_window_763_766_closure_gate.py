from __future__ import annotations

import os
import subprocess
from pathlib import Path


COHERENCE_PATH = Path("docs/specs/ilc_coherence_report_766_v0.1.md")
CAPSULE_PATH = Path("docs/specs/ilc_antigravity_context_capsule_v5.5.md")
GATE_PATH = Path("docs/specs/ilc_window_763_766_closure_gate_766_v0.1.md")
SEQUENCE_LOCK_PATH = Path("docs/specs/ilc_phase_763_766_sequence_lock_v0.1.md")
STATUS_PATH = Path("docs/phases/STATUS.md")
PLANNING_INDEX_PATH = Path("docs/PLANNING_INDEX.md")
TEST_PATH = Path("tests/test_window_763_766_closure_gate.py")
DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
PHASE_765_ARTIFACT_PATH = Path(
    "docs/specs/ilc_cdl_017_validator_governance_framework_ratification_evidence_765_v0.1.md"
)
LEGACY_TEST_PATHS = (
    Path("tests/test_phase_751_stale_planning_doc_archival_and_planning_index_advance.py"),
    Path("tests/test_phase_752_window_749_752_closure_gate.py"),
    Path("tests/test_phase_753_window_753_756_sequence_lock.py"),
    Path("tests/test_phase_756_window_753_756_closure_gate.py"),
    Path("tests/test_cw6_convergence_window_closure_gate.py"),
    Path("tests/test_phase_763_window_763_766_sequence_lock.py"),
    Path("tests/test_phase_764_cdl_017_interaction_synthesis_and_activation_boundary_record.py"),
    Path("tests/test_phase_765_cdl_017_ratification_evidence.py"),
)
REQUIRED_HEADINGS_COHERENCE = (
    "## 1. Window verdict",
    "## 2. Phase-by-phase coherence",
    "## 3. Constitutional and runtime posture at close",
    "## 4. Track B verification and cross-lane posture",
    "## 5. Carry-forward after ratification and closure",
)
REQUIRED_HEADINGS_CAPSULE = (
    "## 1. Current frontier state",
    "## 2. Frozen inherited boundary state",
    "## 3. Window 763-766 closure state",
    "## 4. Remaining post-ratification blockers and carry-forward",
    "## 5. Window 763-766 Closure Summary",
    "## 6. Next authorized continuation",
)
REQUIRED_HEADINGS_GATE = (
    "## 1. Completion checklist",
    "## 2. Constitutional and runtime posture at closure",
    "## 3. Track B verification",
    "## 4. Planning-surface advance",
    "## 5. Carry-forward",
    "## 6. Selftest chain",
    "## 7. Closure verdict",
)
REQUIRED_TOKENS = (
    "window_763_766_closure_gate_pass",
    "window_763_766_sequence_lock_consumed_and_closed",
    "cdl_017_ratified_in_phase_765",
    "phase_766_no_decision_log_mutation",
    "phase_766_no_main_lane_runtime_mutation",
)
PHASE_SUBJECT = (
    "phase 766",
    "coherence report",
    "window 763-766 closure gate",
)
EXACT_REQUIRED_PATHS = {
    str(COHERENCE_PATH),
    str(CAPSULE_PATH),
    str(GATE_PATH),
    str(TEST_PATH),
    str(STATUS_PATH),
    str(PLANNING_INDEX_PATH),
    *(str(path) for path in LEGACY_TEST_PATHS),
}
SELFTEST_ENV = "ILC_PHASE_766_GATE_SELFTEST"
SELFTEST_CHAIN = (
    "ILC_CW6_GATE_SELFTEST=1",
    "ILC_PHASE_766_GATE_SELFTEST=1",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _normalized(text: str) -> str:
    return " ".join(text.split())


def _selftest() -> bool:
    return os.environ.get(SELFTEST_ENV) == "1"


def _changed_paths_for_commit(commit_ref: str) -> set[str]:
    result = subprocess.run(
        ["git", "show", "--name-only", "--pretty=", commit_ref],
        capture_output=True,
        check=True,
        text=True,
    )
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


def _resolve_commit_ref(subject_tokens: tuple[str, ...], expected_paths: set[str]) -> str:
    result = subprocess.run(
        ["git", "log", "--format=%H%x09%s"],
        capture_output=True,
        check=True,
        text=True,
    )
    matches: list[str] = []
    for line in result.stdout.splitlines():
        if "\t" not in line:
            continue
        commit_hash, subject = line.split("\t", 1)
        lowered = subject.lower()
        if all(token in lowered for token in subject_tokens):
            matches.append(commit_hash)
    for commit_ref in matches:
        if _changed_paths_for_commit(commit_ref) == expected_paths:
            return commit_ref
    raise AssertionError("phase_766_commit_not_present_in_local_history")


def _try_resolve_commit_ref(subject_tokens: tuple[str, ...], expected_paths: set[str]) -> str | None:
    try:
        return _resolve_commit_ref(subject_tokens, expected_paths)
    except AssertionError:
        return None


def _current_phase_paths_in_worktree(expected_paths: set[str]) -> set[str]:
    result = subprocess.run(
        ["git", "status", "--short", "--", *sorted(expected_paths)],
        capture_output=True,
        check=True,
        text=True,
    )
    paths: set[str] = set()
    for line in result.stdout.splitlines():
        if not line.strip():
            continue
        paths.add(line[3:].strip())
    return paths


def test_output_files_exist_with_required_headings_in_order() -> None:
    if _selftest():
        return
    coherence = _read(COHERENCE_PATH)
    capsule = _read(CAPSULE_PATH)
    gate = _read(GATE_PATH)
    assert [coherence.index(h) for h in REQUIRED_HEADINGS_COHERENCE] == sorted(
        coherence.index(h) for h in REQUIRED_HEADINGS_COHERENCE
    )
    assert [capsule.index(h) for h in REQUIRED_HEADINGS_CAPSULE] == sorted(
        capsule.index(h) for h in REQUIRED_HEADINGS_CAPSULE
    )
    assert [gate.index(h) for h in REQUIRED_HEADINGS_GATE] == sorted(
        gate.index(h) for h in REQUIRED_HEADINGS_GATE
    )


def test_closure_gate_tokens_and_sequence_lock_token_are_present() -> None:
    if _selftest():
        return
    gate = _read(GATE_PATH)
    sequence_lock = _read(SEQUENCE_LOCK_PATH)
    for token in REQUIRED_TOKENS:
        assert token in gate
    assert "window_763_766_sequence_lock_active" in sequence_lock


def test_coherence_and_gate_record_what_changed_and_what_did_not() -> None:
    if _selftest():
        return
    combined = _normalized(_read(COHERENCE_PATH) + "\n" + _read(GATE_PATH))
    assert "the single `CDL-017` row moved from `open` to `ratified`" in combined
    assert "validator governance is constitutionally settled" in combined
    assert "Genesis-only validator authority remains operative" in combined
    assert "M-007 `admit_validator` / `eject_validator` hooks remain `unimplemented!`" in combined
    assert "`SEC-004` remains post-ratification implementation work" in combined
    assert "`CDL-055`, `CDL-056`, and `CDL-068` remain unchanged" in combined
    assert "no `ilc_core/` or `ilc_consensus/` mutation occurred in Phase `766`" in combined


def test_capsule_v55_supersedes_v54_and_records_h006a() -> None:
    if _selftest():
        return
    text = _normalized(_read(CAPSULE_PATH))
    assert "Supersedes: docs/specs/ilc_antigravity_context_capsule_v5.4.md" in text
    assert "`CDL-017` is ratified in Phase `765`" in text
    assert "ilc_core/analysis/laplacian_analytics.py" in text
    assert "tests/test_laplacian_analytics.py" in text
    assert "commit `6b954ff5`" in text
    assert "`H-006a` is now implemented" in text
    assert "`H-006b` and `SIM-EMBED-01` remain pending" in text


def test_selftest_chain_is_declared_in_gate_and_test_file() -> None:
    text = _read(TEST_PATH) + "\n" + _read(GATE_PATH)
    for token in SELFTEST_CHAIN:
        assert token in text
    assert SELFTEST_ENV in text


def test_status_and_planning_index_advance_to_closed_window_763_766_frontier() -> None:
    if _selftest():
        return
    status = _normalized(_read(STATUS_PATH))
    planning = _normalized(_read(PLANNING_INDEX_PATH))
    assert "## Phase 766" in status
    assert "window 763-766 closure gate" in status
    assert str(COHERENCE_PATH) in status
    assert str(CAPSULE_PATH) in status
    assert str(GATE_PATH) in status
    assert "Window `763-766` CLOSED via Phase `766` closure gate" in planning
    assert "Context Capsule v5.5" in planning
    assert "docs/specs/ilc_window_763_766_closure_gate_766_v0.1.md" in planning
    assert "`CDL-017` is ratified" in planning


def test_decision_log_and_runtime_code_surfaces_are_untouched_in_phase_766() -> None:
    if _selftest():
        return
    commit_ref = _try_resolve_commit_ref(PHASE_SUBJECT, EXACT_REQUIRED_PATHS)
    if commit_ref:
        changed_paths = _changed_paths_for_commit(commit_ref)
        assert str(DECISION_LOG_PATH) not in changed_paths
        assert not any(path == "ilc_core" or path.startswith("ilc_core/") for path in changed_paths)
        assert not any(
            path == "ilc_consensus" or path.startswith("ilc_consensus/")
            for path in changed_paths
        )
        return

    result_decision = subprocess.run(
        ["git", "diff", "--exit-code", "--", str(DECISION_LOG_PATH)],
        capture_output=True,
        text=True,
    )
    assert result_decision.returncode == 0


def test_phase_766_single_commit_touches_expected_paths_only() -> None:
    if _selftest():
        return
    commit_ref = _try_resolve_commit_ref(PHASE_SUBJECT, EXACT_REQUIRED_PATHS)
    if commit_ref:
        assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_PATHS
        return

    assert _current_phase_paths_in_worktree(EXACT_REQUIRED_PATHS) == EXACT_REQUIRED_PATHS
