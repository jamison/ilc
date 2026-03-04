"""Contract tests for Phase 348 sequence lock artifact."""

from __future__ import annotations

from pathlib import Path
import subprocess


ARTIFACT_PATH = Path("docs/specs/ilc_phase_348_357_sequence_lock_v0.1.md")
DECISION_LOG_PATH = "docs/specs/ilc_constitutional_decision_log_v0.1.md"
PHASE_348_COMMIT_SUBJECT = "docs(g8): phase 348 sequence lock 348-357 node schema ratification window"


def _read() -> str:
    return ARTIFACT_PATH.read_text(encoding="utf-8")


def test_artifact_exists() -> None:
    assert ARTIFACT_PATH.exists()


def test_required_sections_present() -> None:
    text = _read()
    for heading in (
        "## 1. Purpose and window character",
        "## 2. Entry state from phase-347 closure",
        "## 3. Current constitutional baseline and ratification intent",
        "## 4. Locked phase table (348-357)",
        "## 5. Per-phase sensitivity classification",
        "## 6. Ratification dependency order",
        "## 7. Mandatory entry and exit gates per phase",
        "## 8. No-runtime-implementation-before-authorization",
        "## 9. Phase-specific forward constraints (349-357)",
        "## 10. Closure condition and 358+ boundary",
        "## 11. Non-goals and explicit boundaries",
        "## 12. Forward pointer",
    ):
        assert heading in text


def test_lane_table_has_strict_348_to_357_order() -> None:
    text = _read()
    section = text.split("## 4. Locked phase table (348-357)", maxsplit=1)[1]
    section = section.split("## 5. Per-phase sensitivity classification", maxsplit=1)[0]
    expected_rows = [
        "| 1 | Phase 348 |",
        "| 2 | Phase 349 |",
        "| 3 | Phase 350 |",
        "| 4 | Phase 351 |",
        "| 5 | Phase 352 |",
        "| 6 | Phase 353 |",
        "| 7 | Phase 354 |",
        "| 8 | Phase 355 |",
        "| 9 | Phase 356 |",
        "| 10 | Phase 357 |",
    ]
    last_idx = -1
    for row in expected_rows:
        idx = section.find(row)
        assert idx != -1
        assert idx > last_idx
        last_idx = idx


def test_entry_inventory_window_character_and_ratification_intent_are_explicit() -> None:
    text = _read()
    for token in (
        "`CDL-034` through `CDL-038` are open and unratified at entry.",
        "Window 338-347 closure is complete.",
        "Window 348-357 is the ratification window for `CDL-034` through `CDL-038`.",
        "no runtime implementation may begin in `ilc_core/` during Window 348-357",
        "Window 358+ is authorized only for implementation of ratified surfaces.",
    ):
        assert token in text


def test_sensitivity_map_is_explicit() -> None:
    text = _read()
    for token in (
        "| Phase 348 | Non-sensitive |",
        "| Phase 349 | Sensitive |",
        "| Phase 354 | Sensitive |",
        "| Phase 355 | Non-sensitive |",
        "| Phase 357 | Sensitive |",
    ):
        assert token in text


def test_ratification_dependency_order_is_explicit() -> None:
    text = _read()
    for token in (
        "`CDL-034` must be ratified before `CDL-035`, `CDL-036`, `CDL-037`, and `CDL-038`.",
        "`CDL-035` must be ratified before `CDL-037` and `CDL-038`",
        "`CDL-036`, `CDL-037`, and `CDL-038` ratify in that order after `CDL-034` and `CDL-035` are complete.",
    ):
        assert token in text


def test_mandatory_entry_exit_gates_exist_for_each_phase() -> None:
    text = _read()
    section = text.split("## 7. Mandatory entry and exit gates per phase", maxsplit=1)[1]
    section = section.split("## 8. No-runtime-implementation-before-authorization", maxsplit=1)[0]
    for phase in range(348, 358):
        assert f"| Phase {phase} |" in section


def test_phase_354_355_356_constraints_are_explicit() -> None:
    text = _read()
    for token in (
        "ADM-003 must explicitly add the 7+1 evaluation panel as a named agent behavioral role,",
        "the governance boundary must remain explicit: the panel governs knowledge-claim evaluation, not constitutional or genesis-layer changes,",
        "capsule `v1.0` must be self-contained, not delta-only,",
        "capsule `v1.0` must carry forward the full v0.9 context where still applicable,",
        "implementation readiness maps prerequisites and module targets only,",
        "implementation readiness does not permit `ilc_core/` work,",
    ):
        assert token in text


def test_phase_357_forward_constraints_are_explicit() -> None:
    text = _read()
    for token in (
        "category 3 must use `tests/test_window_338_347_closure_gate_347.py`,",
        "closure must verify `CDL-034` through `CDL-038` are ratified,",
        "closure must verify ADM-003 role resolution is complete,",
        "closure must verify no `ilc_core/` implementation occurred in Window 348-357,",
        "Phase 357 prompt must not be drafted until Phases 348-356 are approved.",
    ):
        assert token in text


def test_window_357_closure_condition_and_358_boundary_are_explicit() -> None:
    text = _read()
    for token in (
        "Window 358+ is authorized to begin runtime implementation of ratified CDL-034 through CDL-038 surfaces.",
        "Unratified surfaces remain implementation-barred.",
        "implementation authorization becomes active only after Phase 357 closure.",
        "no decision-log mutation in Phase 348,",
        "no `ilc_core/` runtime implementation in Phase 348.",
        "ratify any CDL row,",
        "authorize runtime work merely because a plan exists.",
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


def _resolve_phase_348_commit_ref_or_fail() -> str:
    result = subprocess.run(
        ["git", "log", "--format=%H%x09%s"],
        capture_output=True,
        check=True,
        text=True,
    )
    for line in result.stdout.splitlines():
        if "\t" not in line:
            continue
        commit_hash, subject = line.split("\t", 1)
        if subject.strip() == PHASE_348_COMMIT_SUBJECT:
            return commit_hash
    raise AssertionError("phase_348_commit_not_present_in_local_history")


def test_no_decision_log_mutation_in_phase_commit() -> None:
    commit_ref = _resolve_phase_348_commit_ref_or_fail()
    changed = _changed_paths_for_commit(commit_ref)
    assert DECISION_LOG_PATH not in changed


def test_no_runtime_mutation_in_phase_commit() -> None:
    commit_ref = _resolve_phase_348_commit_ref_or_fail()
    changed = _changed_paths_for_commit(commit_ref)
    forbidden = [path for path in changed if path.startswith("ilc_core/")]
    assert not forbidden, f"phase_348_runtime_mutations:{forbidden}"
