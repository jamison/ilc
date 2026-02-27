"""Contract tests for Phase 318 sequence lock artifact."""

from __future__ import annotations

from pathlib import Path
import subprocess


ARTIFACT_PATH = Path("docs/specs/ilc_phase_318_327_sequence_lock_v0.1.md")
DECISION_LOG_PATH = "docs/specs/ilc_constitutional_decision_log_v0.1.md"
PHASE_318_COMMIT_SUBJECT = "docs(g8): phase 318 sequence lock 318-327 parallel tracks"


def _read() -> str:
    return ARTIFACT_PATH.read_text(encoding="utf-8")


def test_artifact_exists() -> None:
    assert ARTIFACT_PATH.exists()


def test_required_sections_present() -> None:
    text = _read()
    for heading in (
        "## 1. Purpose and sequence scope",
        "## 2. Entry state from phase-317 closure controls",
        "## 3. Open CDL inventory and window intent",
        "## 4. Locked phase table (318-327)",
        "## 5. Per-phase sensitivity classification",
        "## 6. Dependency map and synchronization rules",
        "## 7. Mandatory entry and exit gates per phase",
        "## 8. No-ratification-before-lock and authorization boundaries",
        "## 9. Closure-gate skeleton requirements for phase 327",
        "## 10. Non-goals and explicit boundaries",
        "## 11. Forward pointer",
    ):
        assert heading in text


def test_phase_table_covers_318_to_327() -> None:
    text = _read()
    for phase in range(318, 328):
        assert f"Phase {phase}" in text


def test_lane_table_has_strict_318_to_327_order() -> None:
    text = _read()
    section = text.split("## 4. Locked phase table (318-327)", maxsplit=1)[1]
    section = section.split("## 5. Per-phase sensitivity classification", maxsplit=1)[0]
    expected_rows = [
        "| 1 | Phase 318 |",
        "| 2 | Phase 319 |",
        "| 3 | Phase 320 |",
        "| 4 | Phase 321 |",
        "| 5 | Phase 322 |",
        "| 6 | Phase 323 |",
        "| 7 | Phase 324 |",
        "| 8 | Phase 325 |",
        "| 9 | Phase 326 |",
        "| 10 | Phase 327 |",
    ]
    last_idx = -1
    for row in expected_rows:
        idx = section.find(row)
        assert idx != -1
        assert idx > last_idx
        last_idx = idx


def test_open_cdl_inventory_and_window_treatment_are_explicit() -> None:
    text = _read()
    for token in (
        "CDL-020",
        "CDL-021",
        "CDL-022",
        "CDL-023",
        "CDL-024",
        "milestone-triggered",
        "out of active execution",
    ):
        assert token in text


def test_sensitivity_and_constitutional_mutation_lanes_are_explicit() -> None:
    text = _read()
    for token in (
        "| Phase 324 | Sensitive |",
        "| Phase 325 | Sensitive |",
        "adding/opening new CDL-V entries mutates constitutional decision-log state",
    ):
        assert token in text


def test_dependency_map_is_explicit() -> None:
    text = _read()
    for token in (
        "Track model:",
        "Ratification track phases: `319`, `320`, `321`.",
        "Transport track phases: `322`, `323`.",
        "Vulnerability governance track phases: `324`, `325`.",
        "Closure/handoff lane phase: `327`.",
    ):
        assert token in text


def test_no_ratification_before_lock_guard_and_authorized_lanes_are_explicit() -> None:
    text = _read()
    assert "no ratification lane may execute in this 318-327 window" in text
    assert "authorized ratification lanes in this window are limited to phases `319`, `320`, and `321`." in text
    assert "`CDL-021` remains milestone-triggered and is not authorized for execution in this window" in text


def test_closure_gate_skeleton_and_snapshot_isolation_standard_are_explicit() -> None:
    text = _read()
    for token in (
        "Prompt contract validation category",
        "Lane-specific contract tests category",
        "Cross-phase regression category",
        "Mutation canary category",
        "CLI contract category",
        "Walkthrough hygiene category",
        "ILC_PHASE_<PHASE>_SNAPSHOT_PATH",
        "tmp_path",
        "must not mutate canonical snapshots under `out/monitoring/`",
    ):
        assert token in text


def test_mandatory_entry_exit_gates_exist_for_each_phase() -> None:
    text = _read()
    section = text.split("## 7. Mandatory entry and exit gates per phase", maxsplit=1)[1]
    section = section.split("## 8. No-ratification-before-lock and authorization boundaries", maxsplit=1)[0]
    for phase in range(318, 328):
        assert f"| Phase {phase} |" in section


def _resolve_phase_318_commit_ref_or_fail() -> str:
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
        if subject.strip() == PHASE_318_COMMIT_SUBJECT:
            return commit_hash
    raise AssertionError("phase_318_commit_not_present_in_local_history")


def test_no_decision_log_mutation_in_phase_commit() -> None:
    commit_ref = _resolve_phase_318_commit_ref_or_fail()
    result = subprocess.run(
        ["git", "show", "--name-only", "--pretty=", commit_ref],
        capture_output=True,
        check=True,
        text=True,
    )
    changed = {line.strip() for line in result.stdout.splitlines() if line.strip()}
    assert DECISION_LOG_PATH not in changed


def test_no_runtime_mutation_in_phase_commit() -> None:
    commit_ref = _resolve_phase_318_commit_ref_or_fail()
    result = subprocess.run(
        ["git", "show", "--name-only", "--pretty=", commit_ref],
        capture_output=True,
        check=True,
        text=True,
    )
    changed = {line.strip() for line in result.stdout.splitlines() if line.strip()}
    forbidden = [path for path in changed if path.startswith("ilc_core/")]
    assert not forbidden, f"phase_318_runtime_mutations:{forbidden}"
