from __future__ import annotations

import json
import subprocess
from pathlib import Path

from ilc_core.testing.ratification_mutation_scope_guardrail import (
    assert_head_commit_touched_no_runtime_files,
    parse_decision_register_rows,
)


DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
SYNTHESIS_PATH = Path("docs/specs/ilc_sim_009_results_synthesis_and_pe_stabilization_disposition_430_v0.1.md")
PHASE_429_COMMISSIONING_PATH = Path("docs/specs/ilc_sim_009_pe_stabilization_commissioning_429_v0.1.md")
PHASE_426_REVIEW_PATH = Path("docs/specs/ilc_treasury_pe_stabilization_governance_review_426_v0.1.md")
SUMMARY_TABLE_PATH = Path("out/simulations/sim_009_pe_stabilization/summary_table.md")
MANIFEST_PATH = Path("out/simulations/sim_009_pe_stabilization/run_manifest.json")
RESULTS_CSV_PATH = Path("out/simulations/sim_009_pe_stabilization/results.csv")
RESULTS_TSV_PATH = Path("out/simulations/sim_009_pe_stabilization/results.tsv")
PHASE_430_SUBJECT_TOKEN = "phase 430 sim-009 results synthesis and pe stabilization disposition"
MAIN_COMMIT_PATHS = {
    str(SYNTHESIS_PATH),
    "tests/test_phase_430_sim_009_results_synthesis_and_disposition.py",
}
REQUIRED_HEADINGS = (
    "## 1. Scope and non-ratifying boundary",
    "## 2. SIM-009 headline results recap",
    "## 3. Recovery-criterion coupling limitation",
    "## 4. Limit-fraction differentiation assessment",
    "## 5. Floating-point trigger-boundary note",
    "## 6. Disposition verdict for the Treasury P_e constitutional lane",
    "## 7. Phase 431 carry-forward constraints",
    "## 8. Non-goals and canonical anchors",
)
REQUIRED_TOKENS = (
    "Phase 430 is a non-ratifying synthesis phase and does not open, amend, or ratify any CDL row.",
    "SIM-009 recommends a P_e trigger threshold candidate of 0.2 and a P_e intervention limit fraction candidate of 0.02 under the commissioned model.",
    "SIM-009's recovery criterion is trigger-coupled: pe_recovery_epochs is defined by |P_e - PE_TARGET| < pe_trigger_threshold.",
    "This coupling creates a built-in scoring advantage for higher trigger thresholds and weakens the constitutional force of the recommended pair.",
    "The score spread among trigger = 0.20 intervention-limit candidates is too small to treat 0.02 as a constitutionally robust winner.",
    "Resolving the sub-choice among trigger = 0.20 intervention-limit candidates requires either a recovery criterion decoupled from the trigger threshold, an explicit treasury-risk tolerance judgment, or additional simulation evidence that directly discriminates intervention-limit trade-offs.",
    "Floating-point boundary behavior means shock_magnitude = 0.10 and pe_trigger_threshold = 0.10 behaves as a no-intervention case in the current deterministic implementation.",
    "Phase 430 disposition: SIM-009 is insufficient for in-window constitutional locking of Treasury P_e trigger and limit constants.",
    "Phase 431 should publish the carry-forward decision for the Treasury P_e constitutional lane with Window 434+ as the default continuation target.",
    "CDL-049 remains independent of the Treasury P_e lane and is unaffected by Phase 430.",
    "No decision-log mutation occurred. No ilc_core runtime files were changed.",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _read_file_at_ref(ref: str, path: str) -> str:
    result = subprocess.run(
        ["git", "show", f"{ref}:{path}"],
        capture_output=True,
        check=False,
        text=True,
    )
    if result.returncode != 0:
        raise AssertionError(f"unable_to_read_file_at_ref:{ref}:{path}:{result.stderr.strip()}")
    return result.stdout


def _changed_paths_for_commit(commit_ref: str) -> set[str]:
    result = subprocess.run(
        ["git", "show", "--name-only", "--pretty=", commit_ref],
        capture_output=True,
        check=True,
        text=True,
    )
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


def _resolve_phase_430_commit_ref() -> str:
    result = subprocess.run(["git", "log", "--format=%H%x09%s"], capture_output=True, check=True, text=True)
    matches: list[str] = []
    for line in result.stdout.splitlines():
        if "\t" not in line:
            continue
        commit_hash, subject = line.split("\t", 1)
        if PHASE_430_SUBJECT_TOKEN in subject.lower():
            matches.append(commit_hash)
    for commit_ref in matches:
        changed = _changed_paths_for_commit(commit_ref)
        if changed == MAIN_COMMIT_PATHS:
            return commit_ref
    raise AssertionError("phase_430_commit_not_present_in_local_history")


def test_synthesis_artifact_exists_and_contains_required_headings_and_tokens() -> None:
    assert SYNTHESIS_PATH.exists()
    text = _read(SYNTHESIS_PATH)
    for heading in REQUIRED_HEADINGS:
        assert heading in text
    for token in REQUIRED_TOKENS:
        assert token in text


def test_phase_429_recommendation_pair_matches_manifest() -> None:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    assert float(manifest["key_metrics"]["recommended_pe_trigger_threshold"]) == 0.2
    assert float(manifest["key_metrics"]["recommended_pe_intervention_limit_fraction"]) == 0.02
    assert "SIM-009 recommends a P_e trigger threshold candidate of 0.2 and a P_e intervention limit fraction candidate of 0.02 under the commissioned model." in _read(SYNTHESIS_PATH)


def test_recovery_coupling_limitation_is_explicit() -> None:
    text = _read(SYNTHESIS_PATH)
    assert "SIM-009's recovery criterion is trigger-coupled: pe_recovery_epochs is defined by |P_e - PE_TARGET| < pe_trigger_threshold." in text
    assert "This coupling creates a built-in scoring advantage for higher trigger thresholds and weakens the constitutional force of the recommended pair." in text


def test_limit_fraction_and_floating_point_findings_are_explicit() -> None:
    text = _read(SYNTHESIS_PATH)
    assert "The score spread among trigger = 0.20 intervention-limit candidates is too small to treat 0.02 as a constitutionally robust winner." in text
    assert "Resolving the sub-choice among trigger = 0.20 intervention-limit candidates requires either a recovery criterion decoupled from the trigger threshold, an explicit treasury-risk tolerance judgment, or additional simulation evidence that directly discriminates intervention-limit trade-offs." in text
    assert "Floating-point boundary behavior means shock_magnitude = 0.10 and pe_trigger_threshold = 0.10 behaves as a no-intervention case in the current deterministic implementation." in text


def test_disposition_verdict_and_phase_431_carry_forward_are_explicit() -> None:
    text = _read(SYNTHESIS_PATH)
    assert "Phase 430 disposition: SIM-009 is insufficient for in-window constitutional locking of Treasury P_e trigger and limit constants." in text
    assert "Phase 431 should publish the carry-forward decision for the Treasury P_e constitutional lane with Window 434+ as the default continuation target." in text
    assert "CDL-049 remains independent of the Treasury P_e lane and is unaffected by Phase 430." in text


def test_phase_430_commit_touched_no_decision_log_or_sim_009_inputs() -> None:
    commit_ref = _resolve_phase_430_commit_ref()
    old_rows = parse_decision_register_rows(_read_file_at_ref(f"{commit_ref}^1", str(DECISION_LOG_PATH)))
    new_rows = parse_decision_register_rows(_read_file_at_ref(commit_ref, str(DECISION_LOG_PATH)))
    assert old_rows == new_rows, "phase_430_commit_modified_decision_log_unlawfully"

    old_phase_429 = _read_file_at_ref(f"{commit_ref}^1", str(PHASE_429_COMMISSIONING_PATH))
    new_phase_429 = _read_file_at_ref(commit_ref, str(PHASE_429_COMMISSIONING_PATH))
    assert old_phase_429 == new_phase_429, "phase_430_commit_modified_phase_429_commissioning_artifact_unlawfully"

    old_phase_426 = _read_file_at_ref(f"{commit_ref}^1", str(PHASE_426_REVIEW_PATH))
    new_phase_426 = _read_file_at_ref(commit_ref, str(PHASE_426_REVIEW_PATH))
    assert old_phase_426 == new_phase_426, "phase_430_commit_modified_phase_426_review_unlawfully"

    old_summary = _read_file_at_ref(f"{commit_ref}^1", str(SUMMARY_TABLE_PATH))
    new_summary = _read_file_at_ref(commit_ref, str(SUMMARY_TABLE_PATH))
    assert old_summary == new_summary, "phase_430_commit_modified_sim_009_summary_unlawfully"

    old_manifest = _read_file_at_ref(f"{commit_ref}^1", str(MANIFEST_PATH))
    new_manifest = _read_file_at_ref(commit_ref, str(MANIFEST_PATH))
    assert old_manifest == new_manifest, "phase_430_commit_modified_sim_009_manifest_unlawfully"

    old_results = _read_file_at_ref(f"{commit_ref}^1", str(RESULTS_CSV_PATH))
    new_results = _read_file_at_ref(commit_ref, str(RESULTS_CSV_PATH))
    assert old_results == new_results, "phase_430_commit_modified_sim_009_results_unlawfully"

    old_results_tsv = _read_file_at_ref(f"{commit_ref}^1", str(RESULTS_TSV_PATH))
    new_results_tsv = _read_file_at_ref(commit_ref, str(RESULTS_TSV_PATH))
    assert old_results_tsv == new_results_tsv, "phase_430_commit_modified_sim_009_results_tsv_unlawfully"


def test_phase_430_commit_touched_no_runtime_files() -> None:
    commit_ref = _resolve_phase_430_commit_ref()
    assert_head_commit_touched_no_runtime_files(commit_ref=commit_ref)
