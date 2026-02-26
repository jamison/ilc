"""Contract tests for Phase 308 sequence lock artifact."""

from __future__ import annotations

from pathlib import Path
import subprocess


ARTIFACT_PATH = Path("docs/specs/ilc_phase_308_317_sequence_lock_v0.1.md")
DECISION_LOG_PATH = "docs/specs/ilc_constitutional_decision_log_v0.1.md"
PHASE_308_COMMIT_SUBJECT = "docs(g8): phase 308 sequence lock 308-317 parallel tracks"


def _read() -> str:
    return ARTIFACT_PATH.read_text(encoding="utf-8")


def test_artifact_exists() -> None:
    assert ARTIFACT_PATH.exists()


def test_required_sections_present() -> None:
    text = _read()
    for heading in (
        "## 1. Purpose and sequence scope",
        "## 2. Entry state from phase-307 closure controls",
        "## 3. Open CDL inventory and window intent",
        "## 4. Locked phase table (308-317)",
        "## 5. Per-phase sensitivity classification",
        "## 6. Parallel-track dependency and synchronization map",
        "## 7. Mandatory entry and exit gates per phase",
        "## 8. No-ratification-before-lock gate",
        "## 9. Closure-gate skeleton requirements for phase 317",
        "## 10. Non-goals and explicit boundaries",
        "## 11. Forward pointer",
    ):
        assert heading in text


def test_phase_table_covers_308_to_317() -> None:
    text = _read()
    for phase in range(308, 318):
        assert f"Phase {phase}" in text


def test_lane_table_has_strict_308_to_317_order() -> None:
    text = _read()
    section = text.split("## 4. Locked phase table (308-317)", maxsplit=1)[1]
    section = section.split("## 5. Per-phase sensitivity classification", maxsplit=1)[0]
    expected_rows = [
        "| 1 | Phase 308 |",
        "| 2 | Phase 309 |",
        "| 3 | Phase 310 |",
        "| 4 | Phase 311 |",
        "| 5 | Phase 312 |",
        "| 6 | Phase 313 |",
        "| 7 | Phase 314 |",
        "| 8 | Phase 315 |",
        "| 9 | Phase 316 |",
        "| 10 | Phase 317 |",
    ]
    last_idx = -1
    for row in expected_rows:
        idx = section.find(row)
        assert idx != -1
        assert idx > last_idx
        last_idx = idx


def test_two_track_map_is_explicit() -> None:
    text = _read()
    assert "Runtime/provider track phases: `310`, `312`, `314`, `316`." in text
    assert "Schema/evidence track phases: `309`, `311`, `313`, `315`, `317`." in text


def test_no_ratification_before_lock_guard_present() -> None:
    text = _read()
    assert "no ratification lane may execute in this 308-317 window" in text
    assert "no direct CDL mutation lane is authorized by Phase 308" in text


def test_open_cdl_inventory_context_is_explicit() -> None:
    text = _read()
    for token in (
        "CDL-020",
        "CDL-021",
        "CDL-022",
        "CDL-023",
        "CDL-024",
        "milestone-triggered",
        "defer",
    ):
        assert token in text


def test_closure_gate_skeleton_declares_required_categories() -> None:
    text = _read()
    for category in (
        "Prompt contract validation category",
        "Lane-specific contract tests category",
        "Cross-phase regression category",
        "Mutation canary category",
        "CLI contract category",
        "Walkthrough hygiene category",
    ):
        assert category in text


def test_snapshot_isolation_standard_is_explicit() -> None:
    text = _read()
    for token in (
        "ILC_PHASE_<PHASE>_SNAPSHOT_PATH",
        "tmp_path",
        "must not mutate canonical snapshots under `out/monitoring/`",
    ):
        assert token in text


def test_mandatory_entry_exit_gates_exist_for_each_phase() -> None:
    text = _read()
    section = text.split("## 7. Mandatory entry and exit gates per phase", maxsplit=1)[1]
    section = section.split("## 8. No-ratification-before-lock gate", maxsplit=1)[0]
    for phase in range(308, 318):
        assert f"| Phase {phase} |" in section


def _resolve_phase_308_commit_ref() -> str:
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
        if subject.strip() == PHASE_308_COMMIT_SUBJECT:
            return commit_hash
    raise AssertionError("phase_308_commit_not_present_in_local_history")


def test_no_decision_log_mutation_in_phase_commit() -> None:
    commit_ref = _resolve_phase_308_commit_ref()
    result = subprocess.run(
        ["git", "show", "--name-only", "--pretty=", commit_ref],
        capture_output=True,
        check=True,
        text=True,
    )
    changed = {line.strip() for line in result.stdout.splitlines() if line.strip()}
    assert DECISION_LOG_PATH not in changed


def test_no_runtime_mutation_in_phase_commit() -> None:
    commit_ref = _resolve_phase_308_commit_ref()
    result = subprocess.run(
        ["git", "show", "--name-only", "--pretty=", commit_ref],
        capture_output=True,
        check=True,
        text=True,
    )
    changed = {line.strip() for line in result.stdout.splitlines() if line.strip()}
    forbidden = [path for path in changed if path.startswith("ilc_core/")]
    assert not forbidden, f"phase_308_runtime_mutations:{forbidden}"
