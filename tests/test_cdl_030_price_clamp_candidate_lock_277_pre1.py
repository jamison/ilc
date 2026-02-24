from __future__ import annotations

import csv
import hashlib
import json
import subprocess
from pathlib import Path

import pytest

from ilc_core.testing.phase_commit_manifest import resolve_phase_commit_ref_or_skip

from ilc_core.testing.ratification_mutation_scope_guardrail import (
    assert_head_commit_touched_no_runtime_files,
)


SCRIPT_PATH = Path("simulations/sim_cdl_030_price_clamp_candidate_sweep_277_pre1.py")
CSV_PATH = Path("out/phase_277_pre1/cdl_030_price_clamp_candidate_sweep.csv")
JSON_PATH = Path("out/phase_277_pre1/cdl_030_price_clamp_candidate_selection.json")
EVIDENCE_PATH = Path("docs/specs/ilc_cdl_030_ecu_price_clamp_candidate_lock_277_pre1_v0.1.md")
DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _run_script() -> None:
    subprocess.run(["python3", str(SCRIPT_PATH)], check=True)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _resolve_phase_277_pre1_commit_ref() -> str:
    return resolve_phase_commit_ref_or_skip("phase_277_pre1")


def test_simulation_script_exists_and_runs() -> None:
    assert SCRIPT_PATH.exists()
    _run_script()
    assert CSV_PATH.exists()
    assert JSON_PATH.exists()


def test_output_csv_has_required_columns_and_valid_candidate_floor() -> None:
    _run_script()
    with CSV_PATH.open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))

    required_columns = {
        "p_min",
        "p_max",
        "clamp_width",
        "scenario_count",
        "bound_respect_score",
        "clamp_stability_score",
        "convergence_score",
        "anti_oscillation_score",
        "utility_continuity_score",
        "composite_score",
        "passes_hard_constraints",
    }
    assert rows
    assert required_columns.issubset(set(rows[0].keys()))
    assert len(rows) >= 40


def test_all_csv_rows_satisfy_validity_filters() -> None:
    _run_script()
    with CSV_PATH.open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))

    for row in rows:
        p_min = float(row["p_min"])
        p_max = float(row["p_max"])
        width = float(row["clamp_width"])
        assert p_max > p_min
        assert width >= 0.20
        assert width <= 0.90


def test_output_json_has_required_keys_and_matches_csv_candidate() -> None:
    _run_script()
    payload = json.loads(_read_text(JSON_PATH))
    required_keys = {
        "selected_candidate",
        "seed",
        "composite_score",
        "schedule_anchor",
        "search_space",
        "valid_candidate_count",
    }
    assert required_keys.issubset(set(payload.keys()))

    with CSV_PATH.open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))

    csv_candidates = {
        (float(row["p_min"]), float(row["p_max"]), float(row["clamp_width"]))
        for row in rows
    }
    selected = payload["selected_candidate"]
    selected_tuple = (
        float(selected["p_min"]),
        float(selected["p_max"]),
        float(selected["clamp_width"]),
    )
    assert selected_tuple in csv_candidates


def test_schedule_anchor_is_phase_276_ratified_tokens() -> None:
    _run_script()
    payload = json.loads(_read_text(JSON_PATH))
    anchor = payload["schedule_anchor"]
    assert anchor["formulation"] == "halving"
    assert anchor["constant"] == "H=48"
    assert anchor["epoch_duration"] == "1 month"


def test_deterministic_rerun_produces_identical_outputs() -> None:
    _run_script()
    csv_hash_first = _sha256(CSV_PATH)
    json_hash_first = _sha256(JSON_PATH)

    _run_script()
    csv_hash_second = _sha256(CSV_PATH)
    json_hash_second = _sha256(JSON_PATH)

    assert csv_hash_first == csv_hash_second
    assert json_hash_first == json_hash_second


def test_evidence_artifact_exists_with_required_sections() -> None:
    assert EVIDENCE_PATH.exists()
    text = _read_text(EVIDENCE_PATH)
    headings = [
        "## 1. Purpose and non-ratifying boundary",
        "## 2. Ratified schedule dependency anchor (Phase 276)",
        "## 3. Parameter-envelope rationale and validity filters",
        "## 4. Modeling coverage against Phase-275 CDL-030 methodology",
        "## 5. Candidate sweep setup and deterministic methodology",
        "## 6. Robustness summary over top-ranked valid candidates",
        "## 7. Selected canonical `P_min` / `P_max` candidate for Phase 277 ratification input",
        "## 8. Residual evidence gaps and downstream treatment",
        "## 9. Canonical anchors",
    ]
    for heading in headings:
        assert heading in text


def test_evidence_artifact_has_required_boundary_and_selected_values() -> None:
    text = _read_text(EVIDENCE_PATH)
    assert "non-ratifying" in text
    assert "No decision-log mutation occurred in this phase." in text

    payload = json.loads(_read_text(JSON_PATH))
    selected = payload["selected_candidate"]
    assert f"`P_min = {selected['p_min']:.2f}`" in text
    assert f"`P_max = {selected['p_max']:.2f}`" in text


def test_no_decision_log_mutation_is_instructed_in_this_phase() -> None:
    text = _read_text(EVIDENCE_PATH)
    assert "No decision-log mutation occurred in this phase." in text

    decision_log = _read_text(DECISION_LOG_PATH)
    assert "ratified_phase: 277-pre1" not in decision_log


def test_no_runtime_files_touched_in_this_phase_commit() -> None:
    commit_ref = _resolve_phase_277_pre1_commit_ref()
    assert_head_commit_touched_no_runtime_files(commit_ref=commit_ref)
