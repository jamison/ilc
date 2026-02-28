"""Contract tests for Phase 328 sequence lock artifact."""

from __future__ import annotations

from pathlib import Path
import subprocess


ARTIFACT_PATH = Path("docs/specs/ilc_phase_328_337_sequence_lock_v0.1.md")
DECISION_LOG_PATH = "docs/specs/ilc_constitutional_decision_log_v0.1.md"
PHASE_328_COMMIT_SUBJECT = "docs(g8): phase 328 sequence lock 328-337 parallel tracks"


def _read() -> str:
    return ARTIFACT_PATH.read_text(encoding="utf-8")


def test_artifact_exists() -> None:
    assert ARTIFACT_PATH.exists()


def test_required_sections_present() -> None:
    text = _read()
    for heading in (
        "## 1. Purpose and sequence scope",
        "## 2. Entry state from phase-327 closure controls",
        "## 3. Open constitutional inventory and window intent",
        "## 4. Locked phase table (328-337)",
        "## 5. Per-phase sensitivity classification",
        "## 6. Dependency map and synchronization rules",
        "## 7. Mandatory entry and exit gates per phase",
        "## 8. No-ratification-before-lock and authorization boundaries",
        "## 9. V-series sequencing and special lane constraints",
        "## 10. Closure-gate skeleton requirements for phase 337",
        "## 11. Non-goals and explicit boundaries",
        "## 12. Forward pointer",
    ):
        assert heading in text


def test_phase_table_covers_328_to_337() -> None:
    text = _read()
    for phase in range(328, 338):
        assert f"Phase {phase}" in text


def test_lane_table_has_strict_328_to_337_order() -> None:
    text = _read()
    section = text.split("## 4. Locked phase table (328-337)", maxsplit=1)[1]
    section = section.split("## 5. Per-phase sensitivity classification", maxsplit=1)[0]
    expected_rows = [
        "| 1 | Phase 328 |",
        "| 2 | Phase 329 |",
        "| 3 | Phase 330 |",
        "| 4 | Phase 331 |",
        "| 5 | Phase 332 |",
        "| 6 | Phase 333 |",
        "| 7 | Phase 334 |",
        "| 8 | Phase 335 |",
        "| 9 | Phase 336 |",
        "| 10 | Phase 337 |",
    ]
    last_idx = -1
    for row in expected_rows:
        idx = section.find(row)
        assert idx != -1
        assert idx > last_idx
        last_idx = idx


def test_open_inventory_and_window_treatment_are_explicit() -> None:
    text = _read()
    for token in (
        "CDL-021",
        "CDL-024",
        "CDL-V1",
        "CDL-V2",
        "CDL-V3",
        "CDL-V4",
        "CDL-V5",
        "CDL-V6",
        "CDL-V7",
        "milestone-triggered",
        "out-of-window",
        "no ratification lane may execute in the 328-337 window unless this sequence lock is published first",
        "authorized ratification lanes in this window are limited to phases `329`, `330`, `331`, `332`, `333`, `334`, and `335`.",
        "`CDL-021` remains `open`, milestone-triggered, and out-of-window for active execution in this sequence",
    ):
        assert token in text


def test_sensitivity_map_and_dual_row_lane_are_explicit() -> None:
    text = _read()
    for token in (
        "| Phase 336 | Non-sensitive |",
        "| Phase 337 | Sensitive |",
        "Phase 334 is a dual-row constitutional mutation lane",
        "phase `334` is sensitive as a dual-row constitutional mutation lane",
    ):
        assert token in text


def test_dependency_map_is_explicit() -> None:
    text = _read()
    for token in (
        "Ratification track phases: `329`, `330`, `331`, `332`, `333`, `334`, `335`.",
        "Coherence/capsule lane phase: `336`.",
        "Closure/handoff lane phase: `337`.",
        "`334` requires `332` and remains coupled to `CDL-V6` because `CDL-V4 <-> CDL-V6`.",
        "`337` requires `336` completion evidence plus green closure prerequisites.",
    ):
        assert token in text


def test_mandatory_entry_exit_gates_exist_for_each_phase() -> None:
    text = _read()
    section = text.split("## 7. Mandatory entry and exit gates per phase", maxsplit=1)[1]
    section = section.split("## 8. No-ratification-before-lock and authorization boundaries", maxsplit=1)[0]
    for phase in range(328, 338):
        assert f"| Phase {phase} |" in section


def test_v_series_constraints_and_phase_specific_notes_are_explicit() -> None:
    text = _read()
    for token in (
        "CDL-V2 -> CDL-V3 -> CDL-V4",
        "CDL-V5 -> CDL-V7",
        "CDL-V4 <-> CDL-V6",
        "CDL-V1 has no V-series ordering constraint",
        "tests/test_wire_transport_contract_and_cdl_024_evidence_prelock_322.py",
        "historical `status: open` pattern",
        "ratifying `CDL-V3` will break the raw-row anchor used by `tests/test_cdl_v_batch_a_open_and_evidence_prelock_324.py`",
        "Exactly `CDL-V4` and `CDL-V6` may change",
        "all other rows remain unchanged",
        "both rows transition `open -> ratified` in the same commit",
    ):
        assert token in text


def test_closure_gate_skeleton_and_snapshot_residual_rule_are_explicit() -> None:
    text = _read()
    for token in (
        "Prompt contract validation category",
        "Lane-specific contract tests category",
        "Cross-phase regression category",
        "Mutation canary category",
        "CLI contract category",
        "Walkthrough hygiene category",
        "ILC_PHASE_<PHASE>_SNAPSHOT_PATH",
        "ILC_PHASE_316_SNAPSHOT_PATH",
        "tests/test_infrastructure_composed_preflight_316.py",
        "git restore out/monitoring/infrastructure_risk_snapshot_phase_316.json",
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


def _resolve_phase_328_commit_ref_or_fail() -> str:
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
        if subject.strip() == PHASE_328_COMMIT_SUBJECT:
            return commit_hash
    raise AssertionError("phase_328_commit_not_present_in_local_history")


def test_no_decision_log_mutation_in_phase_commit() -> None:
    commit_ref = _resolve_phase_328_commit_ref_or_fail()
    changed = _changed_paths_for_commit(commit_ref)
    assert DECISION_LOG_PATH not in changed


def test_no_runtime_mutation_in_phase_commit() -> None:
    commit_ref = _resolve_phase_328_commit_ref_or_fail()
    changed = _changed_paths_for_commit(commit_ref)
    forbidden = [path for path in changed if path.startswith("ilc_core/")]
    assert not forbidden, f"phase_328_runtime_mutations:{forbidden}"
