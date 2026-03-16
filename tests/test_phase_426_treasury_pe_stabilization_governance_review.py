from __future__ import annotations

import subprocess
from pathlib import Path

from ilc_core.testing.ratification_mutation_scope_guardrail import (
    assert_head_commit_touched_no_runtime_files,
    parse_decision_register_rows,
)


DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
REVIEW_PATH = Path("docs/specs/ilc_treasury_pe_stabilization_governance_review_426_v0.1.md")
SEQUENCE_LOCK_PATH = Path("docs/specs/ilc_phase_424_433_sequence_lock_v0.1.md")
CDL_049_STUB_PATH = Path("docs/specs/ilc_cdl_049_bounded_existential_alignment_opening_stub_424_v0.1.md")
PHASE_425_HARDENING_PATH = Path("docs/specs/ilc_cdl_049_bounded_existential_alignment_prelock_hardening_425_v0.1.md")
SIM_008_RESULTS_PATH = Path("docs/specs/ilc_sim_008_commissioning_results_406_v0.1.md")
CDL_047_EVIDENCE_PATH = Path("docs/specs/ilc_cdl_047_treasury_governance_ratification_evidence_418_v0.1.md")
CDL_030_PATH = Path("docs/specs/ilc_cdl_030_ecu_price_clamp_candidate_lock_277_pre1_v0.1.md")
PHASE_426_SUBJECT_TOKEN = "phase 426 treasury pe stabilization governance review"
REQUIRED_HEADINGS = (
    "## 1. Scope and non-ratifying boundary",
    "## 2. Review corpus and methodology",
    "## 3. SIM-008 P_e calibration basis assessment",
    "## 4. Treasury P_e governance question: trigger and limit constants",
    "## 5. Disposition verdict and authorized scenario",
    "## 6. Phase 429-431 forward assignment",
    "## 7. CDL-049 track independence",
    "## 8. Non-goals and canonical anchors",
)
REQUIRED_TOKENS = (
    "Phase 426 is a non-ratifying governance review and does not open, amend, or ratify any CDL row.",
    "SIM-008 does not directly calibrate Treasury P_e trigger or limit constants.",
    "Phase 426 disposition verdict: SIM-009 is warranted to generate P_e-specific calibration data before locking P_e trigger and limit constants.",
    "The CDL-049 constitutional track is independent of the Treasury P_e branch; Phases 427 and 428 proceed regardless of the Phase 426 verdict.",
    "Phase 429: SIM-009 commissioning.",
    "Phase 430: SIM-009 results synthesis and P_e stabilization disposition.",
    "Phase 431: P_e constitutional lane carry-forward decision publication.",
    "If the P_e constitutional lane cannot complete within Phases 429-431 without compressing constitutional lane discipline, P_e stabilization carries into Window 434+.",
    "CDL-030 sets the P_e clamp range [0.75, 1.30] but does not set trigger or limit constants for intervention.",
    "docs/specs/ilc_sim_008_commissioning_results_406_v0.1.md",
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


def _resolve_phase_426_commit_ref() -> str:
    result = subprocess.run(
        ["git", "log", "--format=%H%x09%s"],
        capture_output=True,
        check=True,
        text=True,
    )
    matching: list[str] = []
    for line in result.stdout.splitlines():
        if "\t" not in line:
            continue
        commit_hash, subject = line.split("\t", 1)
        if PHASE_426_SUBJECT_TOKEN in subject.lower():
            matching.append(commit_hash)
    required_paths = {
        str(REVIEW_PATH),
        "tests/test_phase_426_treasury_pe_stabilization_governance_review.py",
    }
    for commit_ref in matching:
        changed_paths = _changed_paths_for_commit(commit_ref)
        if required_paths.issubset(changed_paths):
            return commit_ref
    if matching:
        raise AssertionError("phase_426_commit_subject_present_but_no_review_artifact_commit")
    raise AssertionError("phase_426_commit_not_present_in_local_history")


def test_review_artifact_exists_and_contains_required_headings_and_tokens() -> None:
    assert REVIEW_PATH.exists()
    text = _read(REVIEW_PATH)
    for heading in REQUIRED_HEADINGS:
        assert heading in text
    for token in REQUIRED_TOKENS:
        assert token in text


def test_cdl_049_remains_open_and_phase_424_425_artifacts_present() -> None:
    # The Phase-426 CDL-049 open-state check is a historical prelock reference.
    rows = parse_decision_register_rows(_read_file_at_ref(_resolve_phase_426_commit_ref(), str(DECISION_LOG_PATH)))
    assert rows["CDL-049"]["status"] == "open"
    assert CDL_049_STUB_PATH.exists()
    assert PHASE_425_HARDENING_PATH.exists()


def test_sim_008_evidence_basis_and_pe_calibration_gap_recorded() -> None:
    text = _read(REVIEW_PATH)
    assert "SIM-008 does not directly calibrate Treasury P_e trigger or limit constants." in text
    assert "docs/specs/ilc_sim_008_commissioning_results_406_v0.1.md" in text
    assert "CDL-030 sets the P_e clamp range [0.75, 1.30] but does not set trigger or limit constants for intervention." in text


def test_disposition_verdict_is_scenario_b_and_forward_assignment_complete() -> None:
    text = _read(REVIEW_PATH)
    assert "Phase 426 disposition verdict: SIM-009 is warranted to generate P_e-specific calibration data before locking P_e trigger and limit constants." in text
    assert "Phase 429: SIM-009 commissioning." in text
    assert "Phase 430: SIM-009 results synthesis and P_e stabilization disposition." in text
    assert "Phase 431: P_e constitutional lane carry-forward decision publication." in text
    assert "If the P_e constitutional lane cannot complete within Phases 429-431 without compressing constitutional lane discipline, P_e stabilization carries into Window 434+." in text


def test_cdl_049_track_independence_confirmed() -> None:
    text = _read(REVIEW_PATH)
    assert "The CDL-049 constitutional track is independent of the Treasury P_e branch; Phases 427 and 428 proceed regardless of the Phase 426 verdict." in text


def test_phase_426_commit_touched_no_decision_log_or_prior_phase_artifacts() -> None:
    commit_ref = _resolve_phase_426_commit_ref()
    old_rows = parse_decision_register_rows(_read_file_at_ref(f"{commit_ref}^1", str(DECISION_LOG_PATH)))
    new_rows = parse_decision_register_rows(_read_file_at_ref(commit_ref, str(DECISION_LOG_PATH)))
    assert set(old_rows) == set(new_rows), "phase_426_commit_modified_decision_log_unlawfully"
    for cdl_id in old_rows:
        assert old_rows[cdl_id] == new_rows[cdl_id], "phase_426_commit_modified_decision_log_unlawfully"

    old_stub = _read_file_at_ref(f"{commit_ref}^1", str(CDL_049_STUB_PATH))
    new_stub = _read_file_at_ref(commit_ref, str(CDL_049_STUB_PATH))
    assert old_stub == new_stub, "phase_426_commit_modified_phase_424_opening_stub_unlawfully"

    old_hardening = _read_file_at_ref(f"{commit_ref}^1", str(PHASE_425_HARDENING_PATH))
    new_hardening = _read_file_at_ref(commit_ref, str(PHASE_425_HARDENING_PATH))
    assert old_hardening == new_hardening, "phase_426_commit_modified_phase_425_hardening_unlawfully"

    old_lock = _read_file_at_ref(f"{commit_ref}^1", str(SEQUENCE_LOCK_PATH))
    new_lock = _read_file_at_ref(commit_ref, str(SEQUENCE_LOCK_PATH))
    assert old_lock == new_lock, "phase_426_commit_modified_phase_424_sequence_lock_unlawfully"

    old_sim = _read_file_at_ref(f"{commit_ref}^1", str(SIM_008_RESULTS_PATH))
    new_sim = _read_file_at_ref(commit_ref, str(SIM_008_RESULTS_PATH))
    assert old_sim == new_sim, "phase_426_commit_modified_sim_008_results_unlawfully"

    old_cdl_047 = _read_file_at_ref(f"{commit_ref}^1", str(CDL_047_EVIDENCE_PATH))
    new_cdl_047 = _read_file_at_ref(commit_ref, str(CDL_047_EVIDENCE_PATH))
    assert old_cdl_047 == new_cdl_047, "phase_426_commit_modified_cdl_047_evidence_unlawfully"

    old_cdl_030 = _read_file_at_ref(f"{commit_ref}^1", str(CDL_030_PATH))
    new_cdl_030 = _read_file_at_ref(commit_ref, str(CDL_030_PATH))
    assert old_cdl_030 == new_cdl_030, "phase_426_commit_modified_cdl_030_clamp_artifact_unlawfully"


def test_phase_426_commit_touched_no_runtime_files() -> None:
    commit_ref = _resolve_phase_426_commit_ref()
    assert_head_commit_touched_no_runtime_files(commit_ref=commit_ref)
