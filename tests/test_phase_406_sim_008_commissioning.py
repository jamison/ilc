"""Contract tests for Phase 406 SIM-008 commissioning artifacts."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
import re
import subprocess

import pytest


RUNNER_PATH = Path("simulations/run_phase_406_sim_008.py")
COMMISSIONING_PATH = Path("docs/specs/ilc_sim_008_commissioning_results_406_v0.1.md")
DECISION_LOG_PATH = "docs/specs/ilc_constitutional_decision_log_v0.1.md"
SUBJECT_TOKEN = "docs(g8): phase 406 sim-008 commissioning"

SIM_008_ROOT = Path("out/simulations/sim_008_post_issuance_transition")
SIM_008_SCRIPT = Path("simulations/sim_008_post_issuance_transition_406.py")

EXPECTED_FILES = {
    "results.csv",
    "results.tsv",
    "summary_table.md",
    "requirements_summary.md",
    "run_manifest.json",
}

SIM_008_COLUMNS = {
    "lost_coin_rate_annual",
    "fee_revenue_index",
    "activity_index",
    "late_epoch_burn_ratio",
    "bounty_cap_fraction_of_budget",
    "ecu_conversion_deadline_epochs",
    "velocity_index",
    "pe_stability_index",
    "treasury_drawdown_ratio",
    "hoarding_pressure_index",
    "budget_resilience_index",
    "policy_score",
}

RECOMMENDATION_KEYS = {
    "recommended_bounty_cap_fraction_of_budget",
    "recommended_ecu_conversion_deadline_epochs",
    "recommended_late_epoch_burn_ratio_floor",
    "recommended_velocity_alert_floor",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


@pytest.fixture(scope="module")
def _outputs_ready() -> None:
    subprocess.run(["python3", str(RUNNER_PATH)], check=True)


def test_simulation_script_and_runner_exist() -> None:
    assert SIM_008_SCRIPT.exists(), f"phase_406_missing_script:{SIM_008_SCRIPT}"
    assert RUNNER_PATH.exists(), f"phase_406_missing_runner:{RUNNER_PATH}"


def test_runner_executes_and_populates_output_root(_outputs_ready: None) -> None:
    del _outputs_ready
    assert SIM_008_ROOT.exists(), f"phase_406_missing_output_root:{SIM_008_ROOT}"
    present = {path.name for path in SIM_008_ROOT.iterdir() if path.is_file()}
    assert EXPECTED_FILES.issubset(present), f"phase_406_missing_output_files:{EXPECTED_FILES - present}"


def test_results_csv_has_required_columns_and_rows(_outputs_ready: None) -> None:
    del _outputs_ready

    sim_008_csv = SIM_008_ROOT / "results.csv"
    with sim_008_csv.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))

    assert rows, f"phase_406_empty_csv:{sim_008_csv}"
    assert SIM_008_COLUMNS.issubset(rows[0].keys()), "phase_406_sim_008_missing_columns"


def test_deterministic_rerun_manifest_and_sim_id_hygiene(_outputs_ready: None) -> None:
    del _outputs_ready

    tracked = [
        SIM_008_ROOT / "results.csv",
        SIM_008_ROOT / "results.tsv",
        SIM_008_ROOT / "summary_table.md",
        SIM_008_ROOT / "requirements_summary.md",
        SIM_008_ROOT / "run_manifest.json",
    ]
    before = {path.as_posix(): _sha256(path) for path in tracked}
    subprocess.run(["python3", str(RUNNER_PATH)], check=True)
    after = {path.as_posix(): _sha256(path) for path in tracked}
    assert before == after

    manifest = json.loads((SIM_008_ROOT / "run_manifest.json").read_text(encoding="utf-8"))
    assert manifest["phase"] == 406
    assert manifest["sim_id"] == "SIM-008"
    assert manifest["epoch_context"]["epoch_type"] == "issuance_epoch"
    assert manifest["epoch_context"]["epoch_duration_canonical"] == "1 month"
    assert RECOMMENDATION_KEYS.issubset(manifest["key_metrics"].keys())

    serialized = json.dumps(manifest, sort_keys=True)
    assert re.search(r"SIM-009", serialized) is None, "phase_406_manifest_references_sim_009"


def test_commissioning_artifact_has_required_sections_and_tokens() -> None:
    assert COMMISSIONING_PATH.exists()
    text = COMMISSIONING_PATH.read_text(encoding="utf-8")

    for heading in (
        "## 1. Scope and non-ratifying boundary",
        "## 2. Implemented simulation module and late-economy modeling scope",
        "## 3. Parameter grid and issuance-epoch model context",
        "## 4. Output artifacts and reproducibility declaration",
        "## 5. Recommended bounty-cap and ECU-deadline results",
        "## 6. Recommended burn-floor and velocity-threshold results",
        "## 7. Carry-forward constraints for Window 414+ economic CDLs",
        "## 8. Out-of-scope and non-goals",
    ):
        assert heading in text

    for token in (
        "Modeled outputs are non-ratifying evidence inputs.",
        "SIM-008 epoch context is issuance_epoch and all late-economy projections are monthly cadence projections.",
        "SIM-009 remains out-of-scope in Phase 406.",
        "SIM-008 recommends a per-epoch bounty issuance cap candidate of 0.15 * B_e for Treasury Governance CDL planning.",
        "SIM-008 recommends an ECU mandatory conversion deadline candidate of 4 issuance epochs for future CDL opening.",
        "SIM-008 recommends a late-economy fee-burn floor candidate of 0.05 and a velocity alert floor candidate of 0.91.",
        "Treasury Governance CDL cluster and ECU mandatory conversion deadline CDL remain deferred to Window 414+; Phase 406 commissions evidence only.",
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


def _resolve_phase_406_commit_ref_or_fail() -> str:
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
        "simulations/run_phase_406_sim_008.py",
        "docs/specs/ilc_sim_008_commissioning_results_406_v0.1.md",
        "tests/test_phase_406_sim_008_commissioning.py",
        "out/simulations/sim_008_post_issuance_transition/run_manifest.json",
    }
    for commit_ref in matching_commits:
        changed = _changed_paths_for_commit(commit_ref)
        if required_paths.issubset(changed):
            return commit_ref

    if matching_commits:
        raise AssertionError("phase_406_commit_subject_present_but_no_qualifying_sim_commit")
    raise AssertionError("phase_406_commit_not_present_in_local_history")


def test_phase_406_commit_touched_required_paths_and_not_decision_log() -> None:
    commit_ref = _resolve_phase_406_commit_ref_or_fail()
    changed = _changed_paths_for_commit(commit_ref)
    assert DECISION_LOG_PATH not in changed


def test_phase_406_commit_touched_no_ilc_core_paths() -> None:
    commit_ref = _resolve_phase_406_commit_ref_or_fail()
    changed = _changed_paths_for_commit(commit_ref)
    forbidden = [path for path in changed if path.startswith("ilc_core/")]
    assert not forbidden, f"phase_406_runtime_mutations:{forbidden}"
