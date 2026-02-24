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


SCRIPT_PATH = Path("simulations/sim_cdl_028_fee_burn_candidate_sweep_274_fix1.py")
CSV_PATH = Path("out/phase_274_fix1/cdl_028_fee_burn_candidate_sweep.csv")
JSON_PATH = Path("out/phase_274_fix1/cdl_028_candidate_selection.json")
EVIDENCE_PATH = Path("docs/specs/ilc_cdl_028_fee_burn_split_candidate_lock_274_fix1_v0.1.md")
DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _run_script() -> None:
    subprocess.run(["python3", str(SCRIPT_PATH)], check=True)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _resolve_phase_274_fix1_commit_ref() -> str:
    return resolve_phase_commit_ref_or_skip("phase_274_fix1")


def test_simulation_script_exists_and_runs() -> None:
    assert SCRIPT_PATH.exists()
    _run_script()
    assert CSV_PATH.exists()
    assert JSON_PATH.exists()


def test_output_csv_has_required_columns_and_candidate_count() -> None:
    _run_script()
    with CSV_PATH.open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))

    required_columns = {
        "candidate_burn",
        "selected_option",
        "scenario_count",
        "sustainability_score",
        "cap_sensitivity_score",
        "adversarial_incentive_score",
        "allocation_resilience_score",
        "clamp_stability_score",
        "composite_score",
        "passes_hard_constraints",
    }
    assert rows
    assert required_columns.issubset(set(rows[0].keys()))
    assert len(rows) == 6


def test_output_json_has_required_keys_and_matches_csv_candidate() -> None:
    _run_script()
    payload = json.loads(_read_text(JSON_PATH))
    required_keys = {"selected_candidate", "selected_option", "seed", "composite_score"}
    assert required_keys.issubset(set(payload.keys()))

    with CSV_PATH.open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))

    csv_candidates = {float(row["candidate_burn"]) for row in rows}
    assert float(payload["selected_candidate"]) in csv_candidates


def test_selected_option_token_is_valid() -> None:
    _run_script()
    payload = json.loads(_read_text(JSON_PATH))
    assert payload["selected_option"] in {"30% burn", "50% burn", "other percentages"}


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
        "## 2. Historical simulation provenance anchors",
        "## 3. Modeling coverage against Phase-256 requirement set",
        "## 4. Candidate sweep setup and deterministic methodology",
        "## 5. Selected canonical candidate for Phase 274 ratification input",
        "## 6. Residual evidence gaps and downstream treatment",
        "## 7. Canonical anchors",
    ]
    for heading in headings:
        assert heading in text


def test_evidence_artifact_has_explicit_non_ratifying_boundary() -> None:
    text = _read_text(EVIDENCE_PATH)
    assert "non-ratifying" in text
    assert "No decision-log mutation occurred in this phase." in text


def test_no_decision_log_mutation_is_instructed_in_this_phase() -> None:
    text = _read_text(EVIDENCE_PATH)
    assert "No decision-log mutation occurred in this phase." in text

    decision_log = _read_text(DECISION_LOG_PATH)
    assert "ratified_phase: 274-fix1" not in decision_log


def test_no_runtime_files_touched_in_this_phase_commit() -> None:
    commit_ref = _resolve_phase_274_fix1_commit_ref()
    assert_head_commit_touched_no_runtime_files(commit_ref=commit_ref)
