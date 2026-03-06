"""Contract tests for Phase 369 SIM-004 commissioning artifacts."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
import subprocess

import pytest


RUNNER_PATH = Path("simulations/run_phase_369_sim_004.py")
COMMISSIONING_PATH = Path(
    "docs/specs/ilc_sim_004_partition_resilience_commissioning_results_369_v0.1.md"
)
DECISION_LOG_PATH = "docs/specs/ilc_constitutional_decision_log_v0.1.md"
SUBJECT_TOKEN = "docs(g8): phase 369 sim-004 partition resilience commissioning"

OUTPUT_ROOT = Path("out/simulations/sim_004_partition_resilience")
SIM_SCRIPT = Path("simulations/sim_004_partition_divergence_369.py")
EXPECTED_FILES = {
    "results.csv",
    "results.tsv",
    "summary_table.md",
    "requirements_summary.md",
    "run_manifest.json",
}
EXPECTED_COLUMNS = {
    "partition_duration_epochs",
    "claims_per_epoch_per_partition",
    "cross_partition_reference_rate",
    "refutation_rate",
    "reconciliation_rule",
    "conflict_rate",
    "reconciliation_cost_epochs",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


@pytest.fixture(scope="module")
def _outputs_ready() -> None:
    subprocess.run(["python3", str(RUNNER_PATH)], check=True)


def test_simulation_script_and_runner_exist() -> None:
    assert SIM_SCRIPT.exists(), f"phase_369_missing_script:{SIM_SCRIPT}"
    assert RUNNER_PATH.exists(), f"phase_369_missing_runner:{RUNNER_PATH}"


def test_runner_executes_and_populates_output_root(_outputs_ready: None) -> None:
    del _outputs_ready
    assert OUTPUT_ROOT.exists(), f"phase_369_missing_output_root:{OUTPUT_ROOT}"
    present = {path.name for path in OUTPUT_ROOT.iterdir() if path.is_file()}
    assert EXPECTED_FILES.issubset(
        present
    ), f"phase_369_missing_output_files:{EXPECTED_FILES - present}"


def test_results_csv_has_required_columns_and_rows(_outputs_ready: None) -> None:
    del _outputs_ready
    csv_path = OUTPUT_ROOT / "results.csv"
    with csv_path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert rows, f"phase_369_empty_csv:{csv_path}"
    assert EXPECTED_COLUMNS.issubset(rows[0].keys()), "phase_369_missing_csv_columns"


def test_deterministic_rerun_preserves_output_hashes(_outputs_ready: None) -> None:
    del _outputs_ready
    tracked = [
        OUTPUT_ROOT / "results.csv",
        OUTPUT_ROOT / "results.tsv",
        OUTPUT_ROOT / "summary_table.md",
        OUTPUT_ROOT / "requirements_summary.md",
        OUTPUT_ROOT / "run_manifest.json",
    ]
    before = {path.as_posix(): _sha256(path) for path in tracked}
    subprocess.run(["python3", str(RUNNER_PATH)], check=True)
    after = {path.as_posix(): _sha256(path) for path in tracked}
    assert before == after

    manifest = json.loads((OUTPUT_ROOT / "run_manifest.json").read_text(encoding="utf-8"))
    assert manifest["phase"] == 369
    assert manifest["sim_id"] == "SIM-004"
    assert isinstance(manifest["seed"], int)
    assert manifest["epoch_context"]["epoch_type"] == "issuance_epoch"
    assert manifest["epoch_context"]["epoch_duration_canonical"] == "1 month"
    assert manifest["artifacts"], "phase_369_manifest_artifacts_empty"


def test_commissioning_artifact_has_required_sections_and_tokens() -> None:
    assert COMMISSIONING_PATH.exists()
    text = COMMISSIONING_PATH.read_text(encoding="utf-8")
    for heading in (
        "## 1. Scope and non-ratifying boundary",
        "## 2. Implemented simulation modules",
        "## 3. Output artifacts and reproducibility",
        "## 4. SIM-004 result summary",
        "## 5. Explicit CDL-039 design requirements derived from modeled outputs",
        "## 6. Carry-forward constraints for Phase 372",
        "## 7. Non-goals",
    ):
        assert heading in text

    for token in (
        "Modeled outputs are non-ratifying evidence inputs.",
        "partition-tolerant epoch consensus required",
        "reconnection policy must bound conflict-reconciliation load under partition duration T",
        "cross-partition reference reconciliation must be deterministic and auditable",
        "Levin stress-cascade reconnection mechanism remains a candidate design input for Phase 372 CDL-039 topology/privacy hardening.",
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


def _resolve_phase_369_commit_ref_or_fail() -> str:
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
        "simulations/run_phase_369_sim_004.py",
        "docs/specs/ilc_sim_004_partition_resilience_commissioning_results_369_v0.1.md",
        "tests/test_phase_369_sim_004_commissioning.py",
        "out/simulations/sim_004_partition_resilience/run_manifest.json",
    }
    for commit_ref in matching_commits:
        changed = _changed_paths_for_commit(commit_ref)
        if required_paths.issubset(changed):
            return commit_ref

    if matching_commits:
        raise AssertionError("phase_369_commit_subject_present_but_no_qualifying_sim_commit")
    raise AssertionError("phase_369_commit_not_present_in_local_history")


def test_phase_369_commit_touched_required_paths_and_not_decision_log() -> None:
    commit_ref = _resolve_phase_369_commit_ref_or_fail()
    changed = _changed_paths_for_commit(commit_ref)
    assert DECISION_LOG_PATH not in changed


def test_phase_369_commit_touched_no_ilc_core_paths() -> None:
    commit_ref = _resolve_phase_369_commit_ref_or_fail()
    changed = _changed_paths_for_commit(commit_ref)
    forbidden = [path for path in changed if path.startswith("ilc_core/")]
    assert not forbidden, f"phase_369_runtime_mutations:{forbidden}"
