"""Contract tests for Phase 338 sequence lock artifact."""

from __future__ import annotations

from pathlib import Path
import subprocess


ARTIFACT_PATH = Path("docs/specs/ilc_phase_338_347_sequence_lock_v0.1.md")
DECISION_LOG_PATH = "docs/specs/ilc_constitutional_decision_log_v0.1.md"
PHASE_338_COMMIT_SUBJECT = "docs(g8): phase 338 sequence lock 338-347 node schema contract window"


def _read() -> str:
    return ARTIFACT_PATH.read_text(encoding="utf-8")


def test_artifact_exists() -> None:
    assert ARTIFACT_PATH.exists()


def test_required_sections_present() -> None:
    text = _read()
    for heading in (
        "## 1. Purpose and window character",
        "## 2. Entry state from phase-337 closure",
        "## 3. Current constitutional baseline and window intent",
        "## 4. Locked phase table (338-347)",
        "## 5. Per-phase sensitivity classification",
        "## 6. Opening-lane map and dependency order",
        "## 7. Mandatory entry and exit gates per phase",
        "## 8. No-ratification-before-lock and no-implementation-before-ratification",
        "## 9. Phase-specific forward constraints (340-345)",
        "## 10. Closure condition and 348+ boundary",
        "## 11. Non-goals and explicit boundaries",
        "## 12. Forward pointer",
    ):
        assert heading in text


def test_lane_table_has_strict_338_to_347_order() -> None:
    text = _read()
    section = text.split("## 4. Locked phase table (338-347)", maxsplit=1)[1]
    section = section.split("## 5. Per-phase sensitivity classification", maxsplit=1)[0]
    expected_rows = [
        "| 1 | Phase 338 |",
        "| 2 | Phase 339 |",
        "| 3 | Phase 340 |",
        "| 4 | Phase 341 |",
        "| 5 | Phase 342 |",
        "| 6 | Phase 343 |",
        "| 7 | Phase 344 |",
        "| 8 | Phase 345 |",
        "| 9 | Phase 346 |",
        "| 10 | Phase 347 |",
    ]
    last_idx = -1
    for row in expected_rows:
        idx = section.find(row)
        assert idx != -1
        assert idx > last_idx
        last_idx = idx


def test_current_inventory_window_treatment_and_guards_are_explicit() -> None:
    text = _read()
    for token in (
        "`CDL-021` remains open and deferred.",
        "`CDL-024` and `CDL-V1` through `CDL-V7` are ratified.",
        "`CDL-034` through `CDL-038` are not yet opened in Phase 338.",
        "Window 338-347 is a pre-ratification, pre-implementation contract window.",
        "Window 348+ begins with ratification work rather than runtime implementation.",
        "no ratification or opening lane may execute in Window 338-347 unless this sequence lock is published first",
        "no node-schema runtime implementation may begin in `ilc_core/` during Window 338-347",
        "no node-schema surface becomes implementation-authorized merely because its CDL row was opened or its prelock was published",
        "Phase 345 may constrain future reputation design but may not create a de facto reputation CDL.",
    ):
        assert token in text


def test_sensitivity_map_and_opening_lane_map_are_explicit() -> None:
    text = _read()
    for token in (
        "| Phase 338 | Non-sensitive |",
        "| Phase 340 | Sensitive |",
        "| Phase 345 | Non-sensitive |",
        "| Phase 347 | Sensitive |",
        "`340 -> CDL-034`",
        "`341 -> CDL-035`",
        "`342 -> CDL-036`",
        "`343 -> CDL-037`",
        "`344 -> CDL-038`",
    ):
        assert token in text


def test_dependency_map_is_explicit() -> None:
    text = _read()
    for token in (
        "Phase 339 must complete before any schema-evolution monitoring or custom-field elevation work is authorized.",
        "Phase 340 establishes the node-schema core boundary that later phases must reference.",
        "Phase 344 depends on the Window-338 sequence lock and must cross-reference the Phase-340 reserved-field/custom-extension model.",
        "Phase 346 requires completion evidence from Phases 339 through 345.",
        "Phase 347 requires Phase 346 completion evidence plus green closure prerequisites.",
    ):
        assert token in text


def test_mandatory_entry_exit_gates_exist_for_each_phase() -> None:
    text = _read()
    section = text.split("## 7. Mandatory entry and exit gates per phase", maxsplit=1)[1]
    section = section.split("## 8. No-ratification-before-lock and no-implementation-before-ratification", maxsplit=1)[0]
    for phase in range(338, 348):
        assert f"| Phase {phase} |" in section

def test_phase_340_forward_constraints_are_explicit() -> None:
    text = _read()
    for token in (
        "The three-envelope model is the anchor invariant for `CDL-034`.",
        "`confidence` and `uncertainty_note` must receive an explicit disposition.",
        "`gate_routing` is protocol-derived and not submitter-controlled authored payload.",
        "custom-extension namespace rules and reserved-field collision rules must be explicit.",
        "a single-primary-epistemic-lane rule must be stated explicitly.",
    ):
        assert token in text


def test_phase_344_and_phase_345_constraints_are_explicit() -> None:
    text = _read()
    for token in (
        "promotion occurs by successor public node plus `promotion_receipt`, never by mutating the original node.",
        "promotion continuity must cross-reference the `CDL-034` reserved-field and custom-extension model.",
        "no automatic public corroboration or reuse credit carry-forward is allowed.",
        "do not lock quorum thresholds for reputation",
        "do not treat L-tier quorum levels as reputation tiers",
        "do not embed `CDL-V3` diversity criteria as implicit reputation defaults",
        "do not create a de facto reputation CDL without opening one explicitly.",
    ):
        assert token in text


def test_window_347_closure_condition_and_348_boundary_are_explicit() -> None:
    text = _read()
    for token in (
        "`CDL-034` through `CDL-038` remain open and unratified",
        "Window 348+ begins with ratification work rather than runtime implementation.",
        "Runtime implementation remains barred until the relevant CDL is ratified.",
        "The first authorized Window-348+ work is controlled ratification of `CDL-034` through `CDL-038`.",
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


def _resolve_phase_338_commit_ref_or_fail() -> str:
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
        if subject.strip() == PHASE_338_COMMIT_SUBJECT:
            return commit_hash
    raise AssertionError("phase_338_commit_not_present_in_local_history")


def test_no_decision_log_mutation_in_phase_commit() -> None:
    commit_ref = _resolve_phase_338_commit_ref_or_fail()
    changed = _changed_paths_for_commit(commit_ref)
    assert DECISION_LOG_PATH not in changed


def test_no_runtime_mutation_in_phase_commit() -> None:
    commit_ref = _resolve_phase_338_commit_ref_or_fail()
    changed = _changed_paths_for_commit(commit_ref)
    forbidden = [path for path in changed if path.startswith("ilc_core/")]
    assert not forbidden, f"phase_338_runtime_mutations:{forbidden}"
