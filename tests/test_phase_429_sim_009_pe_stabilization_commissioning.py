from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest


RUNNER_PATH = Path("simulations/run_phase_429_sim_009.py")
COMMISSIONING_PATH = Path("docs/specs/ilc_sim_009_pe_stabilization_commissioning_429_v0.1.md")
DECISION_LOG_PATH = "docs/specs/ilc_constitutional_decision_log_v0.1.md"
SIM_009_ROOT = Path("out/simulations/sim_009_pe_stabilization")
SIM_009_SCRIPT = Path("simulations/sim_009_pe_stabilization_429.py")
PHASE_429_SUBJECT_TOKEN = "docs(g8): phase 429 sim-009 pe stabilization commissioning"
EXPECTED_FILES = {
    "results.csv",
    "results.tsv",
    "summary_table.md",
    "run_manifest.json",
}
EXPECTED_COLUMNS = {
    "pe_shock_magnitude",
    "shock_direction",
    "pe_trigger_threshold",
    "pe_intervention_limit_fraction",
    "economic_scenario",
    "pe_recovery_epochs",
    "treasury_drawdown_fraction",
    "overshoot_episodes",
    "policy_score",
}
EXPECTED_HEADINGS = (
    "## 1. Scope and non-ratifying boundary",
    "## 2. Implemented simulation module and P_e modeling scope",
    "## 3. Parameter grid and intervention model context",
    "## 4. Output artifacts and reproducibility declaration",
    "## 5. Recommended P_e trigger threshold results",
    "## 6. Recommended P_e intervention limit results",
    "## 7. Carry-forward constraints for Phase 430 synthesis and P_e constitutional lane planning",
    "## 8. Out-of-scope and non-goals",
)
REQUIRED_TOKENS = (
    "Phase 429 commissions SIM-009 as the Treasury P_e stabilization calibration evidence lane for Phase 430 synthesis.",
    "Modeled outputs are non-ratifying evidence inputs for Phase 430 synthesis and P_e stabilization disposition.",
    "SIM-009 does not open, amend, or ratify any CDL row.",
    "CDL-030 sets the P_e clamp range [0.75, 1.30] but does not set trigger or limit constants for intervention.",
    "docs/specs/ilc_treasury_pe_stabilization_governance_review_426_v0.1.md",
    "docs/specs/ilc_sim_008_commissioning_results_406_v0.1.md",
    "SIM-009 recommends a P_e trigger threshold candidate of",
    "SIM-009 recommends a P_e intervention limit fraction candidate of",
    "No decision-log mutation occurred. No ilc_core runtime files were changed.",
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


@pytest.fixture(scope="module")
def _outputs_ready() -> None:
    subprocess.run(["python3", str(RUNNER_PATH)], check=True)


def _load_sim_module():
    simulations_dir = str(SIM_009_SCRIPT.parent.resolve())
    sys.path.insert(0, simulations_dir)
    try:
        spec = importlib.util.spec_from_file_location("sim_009_pe_stabilization_429", SIM_009_SCRIPT)
        if spec is None or spec.loader is None:
            raise AssertionError(f"phase_429_unable_to_load_module:{SIM_009_SCRIPT}")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    finally:
        if sys.path and sys.path[0] == simulations_dir:
            sys.path.pop(0)


def _changed_paths_for_commit(commit_ref: str) -> set[str]:
    result = subprocess.run(
        ["git", "show", "--name-only", "--pretty=", commit_ref],
        capture_output=True,
        check=True,
        text=True,
    )
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


def _resolve_phase_429_commit_ref_or_fail() -> str:
    result = subprocess.run(["git", "log", "--format=%H%x09%s"], capture_output=True, check=True, text=True)
    matches: list[str] = []
    for line in result.stdout.splitlines():
        if "\t" not in line:
            continue
        commit_hash, subject = line.split("\t", 1)
        if subject.strip().lower() == PHASE_429_SUBJECT_TOKEN.lower():
            matches.append(commit_hash)

    required_paths = {
        "simulations/sim_009_pe_stabilization_429.py",
        "simulations/run_phase_429_sim_009.py",
        "docs/specs/ilc_sim_009_pe_stabilization_commissioning_429_v0.1.md",
        "tests/test_phase_429_sim_009_pe_stabilization_commissioning.py",
        "out/simulations/sim_009_pe_stabilization/results.csv",
        "out/simulations/sim_009_pe_stabilization/results.tsv",
        "out/simulations/sim_009_pe_stabilization/summary_table.md",
        "out/simulations/sim_009_pe_stabilization/run_manifest.json",
    }
    for commit_ref in matches:
        changed = _changed_paths_for_commit(commit_ref)
        if required_paths.issubset(changed):
            return commit_ref
    raise AssertionError("phase_429_commit_not_present_in_local_history")


def _read_results_rows() -> list[dict[str, str]]:
    with (SIM_009_ROOT / "results.csv").open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _recompute_recommendation(rows: list[dict[str, str]]) -> tuple[float, float]:
    grouped: dict[tuple[float, float], list[float]] = {}
    for row in rows:
        key = (float(row["pe_trigger_threshold"]), float(row["pe_intervention_limit_fraction"]))
        grouped.setdefault(key, []).append(float(row["policy_score"]))
    ranked = sorted(
        (
            (
                trigger_threshold,
                intervention_limit_fraction,
                sum(scores) / len(scores),
            )
            for (trigger_threshold, intervention_limit_fraction), scores in grouped.items()
        ),
        key=lambda item: (-item[2], item[0], item[1]),
    )
    best = ranked[0]
    return best[0], best[1]


def test_simulation_script_runner_and_module_constants_lock_exact_values() -> None:
    assert SIM_009_SCRIPT.exists()
    assert RUNNER_PATH.exists()
    module = _load_sim_module()
    assert module.SIM_ID == "SIM-009"
    assert module.SEED == 429009
    assert module.MODEL_VERSION == "sim_009_pe_stabilization_429.v0.1"
    assert module.OUTPUT_DIR == Path("out/simulations/sim_009_pe_stabilization")
    assert module.SIMULATION_HORIZON_EPOCHS == 20
    assert module.PE_TARGET == 1.0
    assert module.PE_SHOCK_MAGNITUDES == [0.10, 0.20, 0.30, 0.40]
    assert module.SHOCK_DIRECTIONS == ["negative", "positive"]
    assert module.PE_TRIGGER_THRESHOLDS == [0.05, 0.10, 0.15, 0.20]
    assert module.PE_INTERVENTION_LIMIT_FRACTIONS == [0.02, 0.05, 0.10, 0.15]
    assert module.ECONOMIC_SCENARIOS == ["low_activity", "medium_activity", "high_activity"]
    assert module.ECONOMIC_SCENARIO_BUDGET_MULTIPLIERS == {
        "low_activity": 0.8,
        "medium_activity": 1.0,
        "high_activity": 1.2,
    }
    assert module.EPOCH_CONTEXT == {
        "epoch_type": "issuance_epoch",
        "epoch_duration_canonical": "1 month",
        "epoch_duration_source": "CDL-027 issuance cadence",
        "wall_clock_note": "SIM-009 projects P_e shock-and-recovery dynamics over monthly issuance epochs.",
    }


def test_runner_executes_and_populates_output_root(_outputs_ready: None) -> None:
    del _outputs_ready
    assert SIM_009_ROOT.exists()
    present = {path.name for path in SIM_009_ROOT.iterdir() if path.is_file()}
    assert EXPECTED_FILES.issubset(present)


def test_results_csv_has_required_columns_rows_and_directional_grid(_outputs_ready: None) -> None:
    del _outputs_ready
    rows = _read_results_rows()
    assert rows
    assert EXPECTED_COLUMNS.issubset(rows[0].keys())
    assert len(rows) == 384
    assert {float(row["pe_shock_magnitude"]) for row in rows} == {0.10, 0.20, 0.30, 0.40}
    assert {row["shock_direction"] for row in rows} == {"negative", "positive"}
    assert {float(row["pe_trigger_threshold"]) for row in rows} == {0.05, 0.10, 0.15, 0.20}
    assert {float(row["pe_intervention_limit_fraction"]) for row in rows} == {0.02, 0.05, 0.10, 0.15}
    assert {row["economic_scenario"] for row in rows} == {"low_activity", "medium_activity", "high_activity"}


def test_deterministic_rerun_manifest_and_recommendation_hygiene(_outputs_ready: None) -> None:
    del _outputs_ready
    tracked = [
        SIM_009_ROOT / "results.csv",
        SIM_009_ROOT / "results.tsv",
        SIM_009_ROOT / "summary_table.md",
        SIM_009_ROOT / "run_manifest.json",
    ]
    before = {path.as_posix(): _sha256(path) for path in tracked}
    subprocess.run(["python3", str(RUNNER_PATH)], check=True)
    after = {path.as_posix(): _sha256(path) for path in tracked}
    assert before == after

    manifest = json.loads((SIM_009_ROOT / "run_manifest.json").read_text(encoding="utf-8"))
    assert manifest["phase"] == 429
    assert manifest["sim_id"] == "SIM-009"
    assert manifest["epoch_context"]["epoch_type"] == "issuance_epoch"
    assert manifest["epoch_context"]["epoch_duration_canonical"] == "1 month"
    assert {"recommended_pe_trigger_threshold", "recommended_pe_intervention_limit_fraction"}.issubset(manifest["key_metrics"].keys())

    rows = _read_results_rows()
    expected_trigger, expected_limit = _recompute_recommendation(rows)
    assert float(manifest["key_metrics"]["recommended_pe_trigger_threshold"]) == expected_trigger
    assert float(manifest["key_metrics"]["recommended_pe_intervention_limit_fraction"]) == expected_limit


def test_commissioning_artifact_has_required_sections_and_tokens() -> None:
    assert COMMISSIONING_PATH.exists()
    text = COMMISSIONING_PATH.read_text(encoding="utf-8")
    for heading in EXPECTED_HEADINGS:
        assert heading in text
    for token in REQUIRED_TOKENS:
        assert token in text


def test_phase_429_commit_touched_required_paths_and_not_decision_log() -> None:
    commit_ref = _resolve_phase_429_commit_ref_or_fail()
    changed = _changed_paths_for_commit(commit_ref)
    assert DECISION_LOG_PATH not in changed


def test_phase_429_commit_touched_no_ilc_core_paths() -> None:
    commit_ref = _resolve_phase_429_commit_ref_or_fail()
    changed = _changed_paths_for_commit(commit_ref)
    forbidden = [path for path in changed if path.startswith("ilc_core/")]
    assert not forbidden, f"phase_429_runtime_mutations:{forbidden}"
