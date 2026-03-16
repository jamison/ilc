from __future__ import annotations

import subprocess
from pathlib import Path

from ilc_core.testing.ratification_mutation_scope_guardrail import (
    assert_head_commit_touched_no_runtime_files,
    parse_decision_register_rows,
)


DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
CARRY_FORWARD_PATH = Path("docs/specs/ilc_pe_stabilization_carry_forward_decision_431_v0.1.md")
PHASE_431_TEST_PATH = Path("tests/test_phase_431_pe_stabilization_carry_forward_decision.py")
PHASE_430_SYNTHESIS_PATH = Path("docs/specs/ilc_sim_009_results_synthesis_and_pe_stabilization_disposition_430_v0.1.md")
PHASE_429_COMMISSIONING_PATH = Path("docs/specs/ilc_sim_009_pe_stabilization_commissioning_429_v0.1.md")
PHASE_426_REVIEW_PATH = Path("docs/specs/ilc_treasury_pe_stabilization_governance_review_426_v0.1.md")
SUMMARY_TABLE_PATH = Path("out/simulations/sim_009_pe_stabilization/summary_table.md")
MANIFEST_PATH = Path("out/simulations/sim_009_pe_stabilization/run_manifest.json")
RESULTS_CSV_PATH = Path("out/simulations/sim_009_pe_stabilization/results.csv")
RESULTS_TSV_PATH = Path("out/simulations/sim_009_pe_stabilization/results.tsv")
PHASE_431_SUBJECT_TOKEN = "docs(g8): phase 431 pe stabilization carry-forward decision"
MAIN_COMMIT_PATHS = {
    str(CARRY_FORWARD_PATH),
    str(PHASE_431_TEST_PATH),
}
REQUIRED_HEADINGS = (
    "## 1. Scope and non-ratifying boundary",
    "## 2. Window 424-433 P_e branch summary",
    "## 3. SIM-009 established findings",
    "## 4. Prerequisites for P_e constitutional lane advancement",
    "## 5. Carry-forward decision",
    "## 6. Non-goals and canonical anchors",
)
REQUIRED_TOKENS = (
    "Phase 431 is a non-ratifying carry-forward decision publication and does not open, amend, or ratify any CDL row.",
    "Scenario B is the authorized tail path for Window 424-433 as determined by Phase 426.",
    "The SIM-009 recommendation pair 0.2 / 0.02 is a provisional planning anchor for the P_e constitutional lane.",
    "Treasury P_e trigger and limit constants are not constitutionally justified for immediate locking on the basis of SIM-009 alone.",
    "The P_e constitutional lane carries into Window 434+ as the default continuation target.",
    "CDL-049 remains independent of the Treasury P_e lane and is unaffected by Phase 431.",
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


def _resolve_phase_431_commit_ref() -> str:
    result = subprocess.run(["git", "log", "--format=%H %s"], capture_output=True, check=True, text=True)
    for line in result.stdout.splitlines():
        if " " not in line:
            continue
        commit_hash, subject_line = line.split(" ", 1)
        if subject_line != PHASE_431_SUBJECT_TOKEN:
            continue
        changed_paths = _changed_paths_for_commit(commit_hash)
        if changed_paths == MAIN_COMMIT_PATHS:
            return commit_hash
    raise AssertionError("phase_431_commit_not_present_in_local_history")


def test_carry_forward_artifact_exists_and_contains_required_headings_and_tokens() -> None:
    assert CARRY_FORWARD_PATH.exists()
    text = _read(CARRY_FORWARD_PATH)
    for heading in REQUIRED_HEADINGS:
        assert heading in text
    for token in REQUIRED_TOKENS:
        assert token in text


def test_scenario_b_path_and_non_ratifying_boundary_are_documented() -> None:
    text = _read(CARRY_FORWARD_PATH)
    assert "Scenario B is the authorized tail path for Window 424-433 as determined by Phase 426." in text
    assert "Phase 429" in text
    assert "Phase 430" in text
    assert "CDL-050 is open" not in text
    assert "CDL-050 ratified" not in text


def test_sim_009_provisional_anchor_is_not_treated_as_constitutional_lock() -> None:
    text = _read(CARRY_FORWARD_PATH)
    assert "The SIM-009 recommendation pair 0.2 / 0.02 is a provisional planning anchor for the P_e constitutional lane." in text
    assert "Treasury P_e trigger and limit constants are not constitutionally justified for immediate locking on the basis of SIM-009 alone." in text
    assert "The P_e constitutional lane carries into Window 434+ as the default continuation target." in text


def test_prerequisites_for_advancement_are_all_stated() -> None:
    text = _read(CARRY_FORWARD_PATH)
    assert "a recovery criterion decoupled from the trigger threshold" in text
    assert "an explicit treasury-risk tolerance judgment" in text
    assert "additional simulation evidence that directly discriminates intervention-limit trade-offs" in text


def test_cdl_independence_and_non_mutation_statement() -> None:
    text = _read(CARRY_FORWARD_PATH)
    assert "CDL-049 remains independent of the Treasury P_e lane and is unaffected by Phase 431." in text
    assert "No decision-log mutation occurred. No ilc_core runtime files were changed." in text


def test_phase_431_commit_touched_no_decision_log_or_prior_artifacts() -> None:
    commit_ref = _resolve_phase_431_commit_ref()

    old_rows = parse_decision_register_rows(_read_file_at_ref(f"{commit_ref}^1", str(DECISION_LOG_PATH)))
    new_rows = parse_decision_register_rows(_read_file_at_ref(commit_ref, str(DECISION_LOG_PATH)))
    assert old_rows == new_rows, "phase_431_commit_modified_decision_log_unlawfully"

    old_phase_430 = _read_file_at_ref(f"{commit_ref}^1", str(PHASE_430_SYNTHESIS_PATH))
    new_phase_430 = _read_file_at_ref(commit_ref, str(PHASE_430_SYNTHESIS_PATH))
    assert old_phase_430 == new_phase_430, "phase_431_commit_modified_phase_430_synthesis_unlawfully"

    old_phase_429 = _read_file_at_ref(f"{commit_ref}^1", str(PHASE_429_COMMISSIONING_PATH))
    new_phase_429 = _read_file_at_ref(commit_ref, str(PHASE_429_COMMISSIONING_PATH))
    assert old_phase_429 == new_phase_429, "phase_431_commit_modified_phase_429_commissioning_unlawfully"

    old_phase_426 = _read_file_at_ref(f"{commit_ref}^1", str(PHASE_426_REVIEW_PATH))
    new_phase_426 = _read_file_at_ref(commit_ref, str(PHASE_426_REVIEW_PATH))
    assert old_phase_426 == new_phase_426, "phase_431_commit_modified_phase_426_review_unlawfully"

    old_summary = _read_file_at_ref(f"{commit_ref}^1", str(SUMMARY_TABLE_PATH))
    new_summary = _read_file_at_ref(commit_ref, str(SUMMARY_TABLE_PATH))
    assert old_summary == new_summary, "phase_431_commit_modified_sim_009_summary_unlawfully"

    old_manifest = _read_file_at_ref(f"{commit_ref}^1", str(MANIFEST_PATH))
    new_manifest = _read_file_at_ref(commit_ref, str(MANIFEST_PATH))
    assert old_manifest == new_manifest, "phase_431_commit_modified_sim_009_manifest_unlawfully"

    old_results_csv = _read_file_at_ref(f"{commit_ref}^1", str(RESULTS_CSV_PATH))
    new_results_csv = _read_file_at_ref(commit_ref, str(RESULTS_CSV_PATH))
    assert old_results_csv == new_results_csv, "phase_431_commit_modified_sim_009_results_unlawfully"

    old_results_tsv = _read_file_at_ref(f"{commit_ref}^1", str(RESULTS_TSV_PATH))
    new_results_tsv = _read_file_at_ref(commit_ref, str(RESULTS_TSV_PATH))
    assert old_results_tsv == new_results_tsv, "phase_431_commit_modified_sim_009_results_tsv_unlawfully"


def test_phase_431_commit_touched_no_runtime_files() -> None:
    commit_ref = _resolve_phase_431_commit_ref()
    assert_head_commit_touched_no_runtime_files(commit_ref=commit_ref)
