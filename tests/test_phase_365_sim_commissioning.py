"""Contract tests for Phase 365 SIM-001/002/003 commissioning artifacts."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
import subprocess

import pytest


RUNNER_PATH = Path("simulations/run_phase_365_simulations.py")
COMMISSIONING_PATH = Path("docs/specs/ilc_sim_001_002_003_commissioning_results_365_v0.1.md")
DECISION_LOG_PATH = "docs/specs/ilc_constitutional_decision_log_v0.1.md"
SUBJECT_TOKEN = "docs(g8): phase 365 sim-001/002/003 commissioning"

SIM_OUTPUT_ROOTS = [
    Path("out/simulations/sim_001_bootstrap_threshold"),
    Path("out/simulations/sim_002_micro_agent_economics"),
    Path("out/simulations/sim_003_graph_growth"),
]

EXPECTED_SCRIPTS = [
    Path("simulations/phase_365_sim_utils.py"),
    Path("simulations/sim_001_bootstrap_threshold_365.py"),
    Path("simulations/sim_002_micro_agent_cost_floor_365.py"),
    Path("simulations/sim_003_graph_growth_storage_pressure_365.py"),
    RUNNER_PATH,
]

EXPECTED_COLUMNS = {
    "out/simulations/sim_001_bootstrap_threshold/results.csv": {
        "n_agents",
        "claims_per_epoch",
        "sybil_fraction",
        "signal_quality",
        "sybil_true_positive",
        "sybil_false_positive",
    },
    "out/simulations/sim_002_micro_agent_economics/results.csv": {
        "write_fee_multiplier",
        "access_fee_ilc",
        "initial_reputation",
        "initial_stake_ilc",
        "claims_per_epoch",
        "epochs_to_first_reward",
        "participation_cliff",
    },
    "out/simulations/sim_003_graph_growth/results.csv": {
        "claims_per_epoch",
        "refutation_rate",
        "ecu_score_floor",
        "retention_epochs",
        "snapshot_interval",
        "max_graph_bytes",
        "coverage_ratio",
    },
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


@pytest.fixture(scope="module")
def _sim_outputs_ready() -> None:
    subprocess.run(["python3", str(RUNNER_PATH)], check=True)


def test_phase_365_scripts_exist() -> None:
    for path in EXPECTED_SCRIPTS:
        assert path.exists(), f"phase_365_missing_script:{path}"


def test_simulation_runner_produces_required_output_roots(
    _sim_outputs_ready: None,
) -> None:
    del _sim_outputs_ready
    required_files = {"results.csv", "results.tsv", "summary_table.md", "run_manifest.json"}
    for root in SIM_OUTPUT_ROOTS:
        assert root.exists(), f"phase_365_missing_output_root:{root}"
        present = {path.name for path in root.iterdir() if path.is_file()}
        assert required_files.issubset(present), f"phase_365_missing_output_files:{root}:{required_files - present}"


def test_output_csv_shapes_and_manifest_contract(
    _sim_outputs_ready: None,
) -> None:
    del _sim_outputs_ready
    for csv_path_str, required_columns in EXPECTED_COLUMNS.items():
        csv_path = Path(csv_path_str)
        with csv_path.open("r", encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))
        assert rows, f"phase_365_empty_csv:{csv_path}"
        assert required_columns.issubset(rows[0].keys()), f"phase_365_missing_columns:{csv_path}"

        manifest_path = csv_path.parent / "run_manifest.json"
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
        assert payload["phase"] == 365
        assert payload["sim_id"].startswith("SIM-")
        assert isinstance(payload["seed"], int)
        assert payload["artifacts"], f"phase_365_manifest_artifacts_empty:{manifest_path}"


def test_deterministic_rerun_preserves_output_hashes(
    _sim_outputs_ready: None,
) -> None:
    del _sim_outputs_ready
    tracked_files = []
    for root in SIM_OUTPUT_ROOTS:
        tracked_files.extend(
            [
                root / "results.csv",
                root / "results.tsv",
                root / "summary_table.md",
                root / "run_manifest.json",
            ]
        )

    before = {path.as_posix(): _sha256(path) for path in tracked_files}
    subprocess.run(["python3", str(RUNNER_PATH)], check=True)
    after = {path.as_posix(): _sha256(path) for path in tracked_files}
    assert before == after


def test_commissioning_artifact_has_required_sections_and_boundary_tokens() -> None:
    assert COMMISSIONING_PATH.exists()
    text = COMMISSIONING_PATH.read_text(encoding="utf-8")
    for heading in (
        "## 1. Scope and non-ratifying boundary",
        "## 2. Implemented simulation modules",
        "## 3. Output artifacts and reproducibility",
        "## 4. SIM-001 result summary (bootstrap threshold)",
        "## 5. SIM-002 result summary (micro-agent cost floor)",
        "## 6. SIM-003 result summary (graph growth and storage pressure)",
        "## 7. Carry-forward constraints for phase 366",
        "## 8. Non-goals",
    ):
        assert heading in text
    assert "No decision-log mutation occurred. No `ilc_core/` runtime files were changed." in text


def _changed_paths_for_commit(commit_ref: str) -> set[str]:
    result = subprocess.run(
        ["git", "show", "--name-only", "--pretty=", commit_ref],
        capture_output=True,
        check=True,
        text=True,
    )
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


def _resolve_phase_365_commit_ref_or_fail() -> str:
    result = subprocess.run(
        ["git", "log", "--format=%H%x09%s"],
        capture_output=True,
        check=True,
        text=True,
    )
    saw_subject_match = False
    for line in result.stdout.splitlines():
        if "\t" not in line:
            continue
        commit_hash, subject = line.split("\t", 1)
        if subject.strip().lower() != SUBJECT_TOKEN.lower():
            continue
        saw_subject_match = True
        changed = _changed_paths_for_commit(commit_hash)
        if {
            "simulations/run_phase_365_simulations.py",
            "docs/specs/ilc_sim_001_002_003_commissioning_results_365_v0.1.md",
            "tests/test_phase_365_sim_commissioning.py",
            "out/simulations/sim_001_bootstrap_threshold/run_manifest.json",
            "out/simulations/sim_002_micro_agent_economics/run_manifest.json",
            "out/simulations/sim_003_graph_growth/run_manifest.json",
        }.issubset(changed):
            return commit_hash
    if saw_subject_match:
        raise AssertionError(
            "phase_365_commit_subject_present_but_no_qualifying_sim_commit"
        )
    raise AssertionError("phase_365_commit_not_present_in_local_history")


def test_phase_365_commit_touched_required_paths_and_not_decision_log() -> None:
    commit_ref = _resolve_phase_365_commit_ref_or_fail()
    changed = _changed_paths_for_commit(commit_ref)
    assert DECISION_LOG_PATH not in changed


def test_phase_365_commit_touched_no_ilc_core_paths() -> None:
    commit_ref = _resolve_phase_365_commit_ref_or_fail()
    changed = _changed_paths_for_commit(commit_ref)
    forbidden = [path for path in changed if path.startswith("ilc_core/")]
    assert not forbidden, f"phase_365_runtime_mutations:{forbidden}"
