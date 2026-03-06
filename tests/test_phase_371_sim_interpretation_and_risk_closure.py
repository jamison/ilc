"""Contract tests for Phase 371 SIM interpretation and CDL-039 risk closure artifact."""

from __future__ import annotations

from pathlib import Path
import subprocess


ARTIFACT_PATH = Path(
    "docs/specs/ilc_sim_003_004_005_interpretation_and_cdl_039_risk_closure_371_v0.1.md"
)
DECISION_LOG_PATH = "docs/specs/ilc_constitutional_decision_log_v0.1.md"
SUBJECT_TOKEN = "docs(g8): phase 371 sim interpretation and cdl-039 risk closure"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_artifact_exists_with_required_headings() -> None:
    assert ARTIFACT_PATH.exists()
    text = _read(ARTIFACT_PATH)
    for heading in (
        "## 1. Scope and non-ratifying boundary",
        "## 2. Input inventory and manifest provenance",
        "## 3. SIM taxonomy table (canonical numbering and scope)",
        "## 4. Epoch-type interpretation table (SIM-003, SIM-004, SIM-005)",
        "## 5. Wall-clock conversions and operational semantics",
        "## 6. Constant lock/readiness flags for Phase 372 and Phase 373",
        "## 7. CDL-039 two-timescale design closure",
        "## 8. Carry-forward constraints for Phase 372",
        "## 9. Carry-forward constraints for Phase 373",
        "## 10. Non-goals and open questions",
    ):
        assert heading in text


def test_required_tokens_are_present() -> None:
    text = _read(ARTIFACT_PATH)
    for token in (
        "Modeled outputs are non-ratifying evidence inputs.",
        "SIM taxonomy resolved for current window: SIM-003 graph growth pressure, SIM-004 partition resilience, SIM-005 agent death and orphaning.",
        "SIM-004 epoch context: issuance_epoch (1 month).",
        "SIM-005 epoch context: validation_epoch (1 minute).",
        "SIM-003 epoch interpretation is declared explicitly for retention and snapshot semantics.",
        "short-timescale CDL-039 context: validation epoch liveness and Levin stress-cascade reconnection handling.",
        "long-timescale CDL-039 context: issuance epoch partition divergence and highest_ecu_wins reconciliation.",
        "Phase 372 consumes invariant shape and interpretation-locked constants only.",
        "Phase 373 calibrates unresolved parameter constants under adversarial review.",
        "No decision-log mutation occurred. No ilc_core runtime files were changed.",
    ):
        assert token in text


def test_sim_taxonomy_table_resolves_scope_and_drift() -> None:
    text = _read(ARTIFACT_PATH)
    assert "| SIM-003 | Graph growth and storage-pressure pruning policy |" in text
    assert "| SIM-004 | Network partition divergence and reconciliation behavior |" in text
    assert "| SIM-005 | Agent death/orphaning timeout and recovery-policy behavior |" in text
    assert "Historical docs also used SIM-005 for epoch timing attack-surface" in text


def test_epoch_type_table_and_wall_clock_semantics_are_explicit() -> None:
    text = _read(ARTIFACT_PATH)
    assert "| SIM-003 | issuance_epoch | 1 month |" in text
    assert "| SIM-004 | issuance_epoch | 1 month |" in text
    assert "| SIM-005 | validation_epoch | 1 minute |" in text
    for token in (
        "retention_epochs=1` means 1 month retention; `snapshot_interval=50` means 50 months",
        "minimum_divergence_partition_duration_epochs=34` means 34 months",
        "recommended_timeout_epochs=2` means 2-minute liveness timeout",
    ):
        assert token in text


def test_constants_readiness_section_partitions_372_and_373_inputs() -> None:
    text = _read(ARTIFACT_PATH)
    assert "### Interpretation-locked for Phase 372 drafting" in text
    assert "### Calibration-required for Phase 373 adversarial review" in text
    for token in (
        "`highest_ecu_wins` as reconciliation baseline candidate",
        "`R_partition_cross_ref` cross-cluster reference cap",
        "`H_release` hysteresis release threshold",
        "Final timeout policy binding from SIM-005",
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


def _resolve_phase_371_commit_ref_or_fail() -> str:
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
        "docs/specs/ilc_sim_003_004_005_interpretation_and_cdl_039_risk_closure_371_v0.1.md",
        "tests/test_phase_371_sim_interpretation_and_risk_closure.py",
    }
    for commit_ref in matching_commits:
        changed = _changed_paths_for_commit(commit_ref)
        if required_paths.issubset(changed):
            return commit_ref

    if matching_commits:
        raise AssertionError(
            "phase_371_commit_subject_present_but_no_qualifying_interpretation_commit"
        )
    raise AssertionError("phase_371_commit_not_present_in_local_history")


def test_phase_371_commit_touched_required_paths_and_not_decision_log() -> None:
    commit_ref = _resolve_phase_371_commit_ref_or_fail()
    changed = _changed_paths_for_commit(commit_ref)
    assert DECISION_LOG_PATH not in changed


def test_phase_371_commit_touched_no_ilc_core_paths() -> None:
    commit_ref = _resolve_phase_371_commit_ref_or_fail()
    changed = _changed_paths_for_commit(commit_ref)
    forbidden = [path for path in changed if path.startswith("ilc_core/")]
    assert not forbidden, f"phase_371_runtime_mutations:{forbidden}"
