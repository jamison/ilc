"""Contract tests for Phase 386 SIM-006/007 commissioning artifacts."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
import re
import subprocess

import pytest


RUNNER_PATH = Path("simulations/run_phase_386_sim_006_007.py")
COMMISSIONING_PATH = Path("docs/specs/ilc_sim_006_007_commissioning_results_386_v0.1.md")
DECISION_LOG_PATH = "docs/specs/ilc_constitutional_decision_log_v0.1.md"
SUBJECT_TOKEN = "docs(g8): phase 386 sim-006/007 commissioning"

SIM_006_ROOT = Path("out/simulations/sim_006_panel_effectiveness")
SIM_007_ROOT = Path("out/simulations/sim_007_agent_churn_orphan_accumulation")
SIM_006_SCRIPT = Path("simulations/sim_006_panel_effectiveness_386.py")
SIM_007_SCRIPT = Path("simulations/sim_007_agent_churn_orphan_accumulation_386.py")

EXPECTED_FILES = {
    "results.csv",
    "results.tsv",
    "summary_table.md",
    "requirements_summary.md",
    "run_manifest.json",
}

SIM_006_COLUMNS = {
    "capability_profile",
    "claim_complexity_tier",
    "panel_assignment_policy",
    "outsider_evidence_quality",
    "review_window_epochs",
    "consensus_accuracy_rate",
    "false_accept_rate",
    "false_reject_rate",
    "median_resolution_rounds",
    "capability_vocabulary_mode",
}

SIM_007_COLUMNS = {
    "churn_rate_per_issuance_epoch",
    "orphan_timeout_epochs",
    "reconnect_window_epochs",
    "replication_factor",
    "recovery_policy",
    "orphan_accumulation_rate",
    "timed_out_transition_rate",
    "reconnect_stability_rate",
    "backlog_recovery_epochs",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


@pytest.fixture(scope="module")
def _outputs_ready() -> None:
    subprocess.run(["python3", str(RUNNER_PATH)], check=True)


def test_simulation_scripts_and_runner_exist() -> None:
    assert SIM_006_SCRIPT.exists(), f"phase_386_missing_script:{SIM_006_SCRIPT}"
    assert SIM_007_SCRIPT.exists(), f"phase_386_missing_script:{SIM_007_SCRIPT}"
    assert RUNNER_PATH.exists(), f"phase_386_missing_runner:{RUNNER_PATH}"


def test_runner_executes_and_populates_output_roots(_outputs_ready: None) -> None:
    del _outputs_ready
    for root in (SIM_006_ROOT, SIM_007_ROOT):
        assert root.exists(), f"phase_386_missing_output_root:{root}"
        present = {path.name for path in root.iterdir() if path.is_file()}
        assert EXPECTED_FILES.issubset(present), f"phase_386_missing_output_files:{root}:{EXPECTED_FILES - present}"


def test_results_csvs_have_required_columns_and_rows(_outputs_ready: None) -> None:
    del _outputs_ready

    sim_006_csv = SIM_006_ROOT / "results.csv"
    sim_007_csv = SIM_007_ROOT / "results.csv"

    with sim_006_csv.open("r", encoding="utf-8", newline="") as handle:
        sim_006_rows = list(csv.DictReader(handle))
    with sim_007_csv.open("r", encoding="utf-8", newline="") as handle:
        sim_007_rows = list(csv.DictReader(handle))

    assert sim_006_rows, f"phase_386_empty_csv:{sim_006_csv}"
    assert sim_007_rows, f"phase_386_empty_csv:{sim_007_csv}"
    assert SIM_006_COLUMNS.issubset(sim_006_rows[0].keys()), "phase_386_sim_006_missing_columns"
    assert SIM_007_COLUMNS.issubset(sim_007_rows[0].keys()), "phase_386_sim_007_missing_columns"


def test_deterministic_rerun_epoch_context_and_sim_id_hygiene(_outputs_ready: None) -> None:
    del _outputs_ready

    tracked = [
        SIM_006_ROOT / "results.csv",
        SIM_006_ROOT / "results.tsv",
        SIM_006_ROOT / "summary_table.md",
        SIM_006_ROOT / "requirements_summary.md",
        SIM_006_ROOT / "run_manifest.json",
        SIM_007_ROOT / "results.csv",
        SIM_007_ROOT / "results.tsv",
        SIM_007_ROOT / "summary_table.md",
        SIM_007_ROOT / "requirements_summary.md",
        SIM_007_ROOT / "run_manifest.json",
    ]
    before = {path.as_posix(): _sha256(path) for path in tracked}
    subprocess.run(["python3", str(RUNNER_PATH)], check=True)
    after = {path.as_posix(): _sha256(path) for path in tracked}
    assert before == after

    sim_006_manifest = json.loads((SIM_006_ROOT / "run_manifest.json").read_text(encoding="utf-8"))
    sim_007_manifest = json.loads((SIM_007_ROOT / "run_manifest.json").read_text(encoding="utf-8"))

    assert sim_006_manifest["phase"] == 386
    assert sim_006_manifest["sim_id"] == "SIM-006"
    assert sim_006_manifest["epoch_context"]["epoch_type"] == "validation_epoch"
    assert sim_006_manifest["epoch_context"]["epoch_duration_canonical"] == "1 minute"

    assert sim_007_manifest["phase"] == 386
    assert sim_007_manifest["sim_id"] == "SIM-007"
    assert sim_007_manifest["epoch_context"]["epoch_type"] == "issuance_epoch"
    assert sim_007_manifest["epoch_context"]["epoch_duration_canonical"] == "1 month"

    for manifest in (sim_006_manifest, sim_007_manifest):
        serialized = json.dumps(manifest, sort_keys=True)
        assert re.search(r"SIM-00[89]", serialized) is None, "phase_386_manifest_references_future_sim"


def test_commissioning_artifact_has_required_sections_and_tokens() -> None:
    assert COMMISSIONING_PATH.exists()
    text = COMMISSIONING_PATH.read_text(encoding="utf-8")

    for heading in (
        "## 1. Scope and non-ratifying boundary",
        "## 2. Capability-vector vocabulary assessment and parameterization decision",
        "## 3. Implemented simulation modules",
        "## 4. Output artifacts and reproducibility",
        "## 5. SIM-006 result summary",
        "## 6. SIM-007 result summary",
        "## 7. Carry-forward constraints for Phase 387 and Phase 390",
        "## 8. Non-goals",
    ):
        assert heading in text

    for token in (
        "Modeled outputs are non-ratifying evidence inputs.",
        "SIM-006 capability_vector vocabulary precondition was evaluated during commissioning; placeholder tiers are used only when canonical vocabulary remains undefined.",
        "SIM-006 epoch context is validation_epoch and SIM-007 epoch context is issuance_epoch.",
        "SIM-006 and SIM-007 outputs feed CDL-V7 extension planning, D2d-10/11 wire-spec planning, and CDL-035 timed_out extension planning.",
        "No decision-log mutation occurred. No ilc_core runtime files were changed.",
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


def _resolve_phase_386_commit_ref_or_fail() -> str:
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
        "simulations/run_phase_386_sim_006_007.py",
        "docs/specs/ilc_sim_006_007_commissioning_results_386_v0.1.md",
        "tests/test_phase_386_sim_006_007_commissioning.py",
        "out/simulations/sim_006_panel_effectiveness/run_manifest.json",
        "out/simulations/sim_007_agent_churn_orphan_accumulation/run_manifest.json",
    }
    for commit_ref in matching_commits:
        changed = _changed_paths_for_commit(commit_ref)
        if required_paths.issubset(changed):
            return commit_ref

    if matching_commits:
        raise AssertionError("phase_386_commit_subject_present_but_no_qualifying_sim_commit")
    raise AssertionError("phase_386_commit_not_present_in_local_history")


def test_phase_386_commit_touched_required_paths_and_not_decision_log() -> None:
    commit_ref = _resolve_phase_386_commit_ref_or_fail()
    changed = _changed_paths_for_commit(commit_ref)
    assert DECISION_LOG_PATH not in changed


def test_phase_386_commit_touched_no_ilc_core_paths() -> None:
    commit_ref = _resolve_phase_386_commit_ref_or_fail()
    changed = _changed_paths_for_commit(commit_ref)
    forbidden = [path for path in changed if path.startswith("ilc_core/")]
    assert not forbidden, f"phase_386_runtime_mutations:{forbidden}"
