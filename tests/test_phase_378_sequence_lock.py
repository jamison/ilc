"""Contract tests for Phase 378 sequence-lock artifact."""

from __future__ import annotations

from pathlib import Path
import subprocess


ARTIFACT_PATH = Path("docs/specs/ilc_phase_378_391_sequence_lock_v0.1.md")
DECISION_LOG_PATH = "docs/specs/ilc_constitutional_decision_log_v0.1.md"
SUBJECT_TOKEN = "docs(g8): phase 378 window 378-391 sequence lock runtime transition block"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_artifact_exists_and_contains_required_headings() -> None:
    assert ARTIFACT_PATH.exists()
    text = _read(ARTIFACT_PATH)
    for heading in (
        "## 1. Purpose and runtime transition character",
        "## 2. Entry state from window 368-377 closure",
        "## 3. Constitutional inventory and unresolved lanes",
        "## 4. Locked phase table (378-391)",
        "## 5. Phase sensitivity and execution policy",
        "## 6. D2d runtime track (380-382) and enforcement boundaries",
        "## 7. Constitutional prelock track (383-385)",
        "## 8. Simulation and authorization track (386-387)",
        "## 9. V-series runtime enforcement track (388-389)",
        "## 10. Coherence and closure track (390-391)",
        "## 11. Explicit deferrals and non-goals",
        "## 12. Forward pointer to window 392+",
    ):
        assert heading in text


def test_required_runtime_transition_and_authority_tokens_are_present() -> None:
    text = _read(ARTIFACT_PATH)
    for token in (
        "Window 378-391 is the Runtime Transition Block.",
        "Phase 378 is a scope declaration, not the implementation authorization source of truth for V-series runtime work.",
        "Phase 387 is the single source of truth for V-series implementation authorization.",
        "If Phase 378 and Phase 387 conflict on exact target paths or dependency token values, Phase 387 governs.",
        "CDL-039 ratification is authorized in Phase 379 based on the Phase 374 prelock finalization package.",
        "The Phase 379 ratification artifact must contain a dedicated section headed with a ## heading containing the word calibration (case-insensitive). Calibration constants resolution text must appear within that section and not in prose outside it. This structural requirement enables section-scoped parsing by the Phase 391 closure gate.",
        "Phase 378 is non-sensitive and non-ratifying.",
        "No decision-log mutation occurred. No ilc_core runtime files were changed.",
    ):
        assert token in text


def test_d2d_boundary_tokens_are_present() -> None:
    text = _read(ARTIFACT_PATH)
    for token in (
        "D2d wire protocol implementation lives in ilc_core/network/d2d/.",
        "D2d implementation phases may use asyncio. Abstract interfaces (Phase 380) must contain no asyncio.",
        "Peering loop (Phase 381) and gossip state machine (Phase 382) may use asyncio.run() with deterministic mock event loops.",
        "Real socket binds, real DNS lookups, and wall-clock timeouts are prohibited in test code.",
    ):
        assert token in text


def test_locked_phase_table_contains_all_fourteen_phases_with_sensitivity() -> None:
    text = _read(ARTIFACT_PATH)
    for token in (
        "Phase 378",
        "Phase 379",
        "Phase 380",
        "Phase 381",
        "Phase 382",
        "Phase 383",
        "Phase 384",
        "Phase 385",
        "Phase 386",
        "Phase 387",
        "Phase 388",
        "Phase 389",
        "Phase 390",
        "Phase 391",
        "non-sensitive",
        "sensitive",
    ):
        assert token in text


def test_deferral_sim_and_cross_cutting_tokens_are_present() -> None:
    text = _read(ARTIFACT_PATH)
    for token in (
        "CDL-V1 and CDL-V2 are authorized for Window 378+ implementation, with exact runtime targets and dependency token values declared in Phase 387.",
        "CDL-V3 and CDL-V7 remain requires_additional_governance_input pending SIM-006 results and Window 392+ governance resolution.",
        "CDL-V4, CDL-V5, CDL-V6 remain governance-procedural and implementation-barred.",
        "CDL-042 (agent identity namespace) is deferred to Window 392+ pending CDL-039/040 scope resolution.",
        "SIM-006 capability_vector vocabulary precondition is declared in this sequence lock and must be verified in Phase 386.",
        "SIM-006 models panel effectiveness under capability heterogeneity.",
        "SIM-007 models agent churn and orphan accumulation for CDL-035 timed_out extension and D2d wire-spec planning.",
        "Phase 379 must harden all four CDL-039 prelock tests before commit and use a seven-path commit resolver that includes tests 359, 372, 373, and 374 hardening targets.",
        "Runtime phases 380, 381, 382, 388, and 389 must use custom runtime mutation-scope asserters and must not use assert_head_commit_touched_no_runtime_files.",
        "CDL-mutation phases 379, 383, 384, and 385 require ILC_CDL_MUTATION_AUTHORIZED=1, ILC_CDL_MUTATION_PHASE=<NNN>, and a clean git diff HEAD -- ilc_core/ preflight.",
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


def _resolve_phase_378_commit_ref_or_fail() -> str:
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
        "docs/specs/ilc_phase_378_391_sequence_lock_v0.1.md",
        "tests/test_phase_378_sequence_lock.py",
    }
    for commit_ref in matching_commits:
        changed = _changed_paths_for_commit(commit_ref)
        if required_paths.issubset(changed):
            return commit_ref

    if matching_commits:
        raise AssertionError("phase_378_commit_subject_present_but_no_qualifying_sequence_lock_commit")
    raise AssertionError("phase_378_commit_not_present_in_local_history")


def test_phase_378_commit_touched_required_paths_and_not_decision_log() -> None:
    commit_ref = _resolve_phase_378_commit_ref_or_fail()
    changed = _changed_paths_for_commit(commit_ref)
    assert DECISION_LOG_PATH not in changed


def test_phase_378_commit_touched_no_ilc_core_paths() -> None:
    commit_ref = _resolve_phase_378_commit_ref_or_fail()
    changed = _changed_paths_for_commit(commit_ref)
    forbidden = [path for path in changed if path.startswith("ilc_core/")]
    assert not forbidden, f"phase_378_runtime_mutations:{forbidden}"
