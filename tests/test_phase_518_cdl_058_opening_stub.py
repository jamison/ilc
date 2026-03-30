from __future__ import annotations

import subprocess
from pathlib import Path

from ilc_core.testing.ratification_mutation_scope_guardrail import parse_decision_register_rows

ARTIFACT_PATH = Path("docs/specs/ilc_cdl_058_re_admission_boundary_opening_stub_518_v0.1.md")
DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
PHASE_505_TEST_PATH = Path("tests/test_phase_505_sequence_lock_and_carry_forward_intake.py")
PHASE_512_TEST_PATH = Path("tests/test_phase_512_re_admission_boundary_cdl_scoping.py")
PHASE_513_TEST_PATH = Path("tests/test_phase_513_coherence_report_and_capsule_v2_4.py")
PHASE_517_TEST_PATH = Path("tests/test_phase_517_sim_011_re_admission_calibration.py")
TEST_PATH = Path("tests/test_phase_518_cdl_058_opening_stub.py")
PHASE_518_SUBJECT_TOKEN = "phase 518 cdl-058 re_admission boundary opening"
EXACT_REQUIRED_MAIN_PATHS = {
    str(ARTIFACT_PATH),
    str(DECISION_LOG_PATH),
    str(PHASE_517_TEST_PATH),
    str(TEST_PATH),
}
REQUIRED_HEADINGS = (
    "## 1. Lane identity",
    "## 2. Problem statement",
    "## 3. Candidate options",
    "## 4. Selected option",
    "## 5. Evidence anchors",
    "## 6. Governance tokens",
    "## 7. Forward obligations",
)
REQUIRED_TOKENS = (
    "cdl_058_governs_re_admission_boundary",
    "selected_option: cooldown_period_per_exit_reason",
    "sim_011_calibrated_constants_required",
    "cdl_046_timed_out_orthogonal",
    "re_admission_cooldown_epoch_type: issuance_epoch",
    "CDL-058 remains status: open in Phase 518.",
)
PHASE_505_COMMENT = "# The Phase-505 CDL-058 absent check is a historical prelock reference."
PHASE_512_COMMENT = "# The Phase-512 CDL-058 absent check is a historical prelock reference."
PHASE_513_COMMENT = "# The Phase-513 CDL-058 absent check is a historical prelock reference."
PHASE_517_COMMENT = "# The Phase-517 CDL-058 absent check is a historical prelock reference."


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _changed_paths_for_commit(commit_ref: str) -> set[str]:
    result = subprocess.run(
        ["git", "show", "--name-only", "--pretty=", commit_ref],
        capture_output=True,
        check=True,
        text=True,
    )
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


def _commit_text(path: str, commit_ref: str) -> str:
    result = subprocess.run(
        ["git", "show", f"{commit_ref}:{path}"],
        capture_output=True,
        check=True,
        text=True,
    )
    return result.stdout


def _resolve_phase_518_commit_ref() -> str:
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
        if PHASE_518_SUBJECT_TOKEN not in subject.lower():
            continue
        matching.append(commit_hash)
    for commit_ref in matching:
        if _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS:
            return commit_ref
    if matching:
        raise AssertionError("phase_518_commit_subject_present_but_no_qualifying_opening_commit")
    raise AssertionError("phase_518_commit_not_present_in_local_history")


def test_opening_stub_contains_required_headings() -> None:
    text = _read(ARTIFACT_PATH)
    for heading in REQUIRED_HEADINGS:
        assert heading in text


def test_opening_stub_contains_required_governance_tokens() -> None:
    text = _read(ARTIFACT_PATH)
    for token in REQUIRED_TOKENS:
        assert token in text


def test_opening_stub_anchors_phase_512_scoping_and_phase_517_sim_011() -> None:
    text = _read(ARTIFACT_PATH)
    assert "docs/specs/ilc_cdl_058_re_admission_boundary_scoping_512_v0.1.md" in text
    assert "docs/specs/ilc_sim_011_re_admission_boundary_calibration_517_v0.1.md" in text
    assert "recommended_cooldown_epochs_liveness_miss: 2" in text
    assert "recommended_cooldown_epochs_equivocation: 12" in text
    assert "recommended_cooldown_epochs_voluntary_exit: 1" in text


def test_live_decision_log_contains_open_cdl_058_row() -> None:
    commit_ref = _resolve_phase_518_commit_ref()
    # The Phase-518 CDL-058 open-state check is a historical prelock reference.
    rows = parse_decision_register_rows(_commit_text(str(DECISION_LOG_PATH), commit_ref))
    assert rows["CDL-055"]["status"] == "ratified"
    assert rows["CDL-056"]["status"] == "ratified"
    assert rows["CDL-057"]["status"] == "ratified"
    assert rows["CDL-058"]["status"] == "open"
    assert "CDL-053" not in rows
    assert "ratified_phase" not in rows["CDL-058"]
    assert "ratified_date" not in rows["CDL-058"]


def test_cross_cdl_hardening_patches_active() -> None:
    assert PHASE_505_COMMENT in _read(PHASE_505_TEST_PATH)
    assert _read(PHASE_512_TEST_PATH).count(PHASE_512_COMMENT) == 2
    assert PHASE_513_COMMENT in _read(PHASE_513_TEST_PATH)
    phase_517_text = _read(PHASE_517_TEST_PATH)
    assert phase_517_text.count(PHASE_517_COMMENT) == 2
    assert "def _commit_text(path: str, commit_ref: str) -> str:" in phase_517_text


def test_phase_518_main_commit_touches_expected_paths_only() -> None:
    commit_ref = _resolve_phase_518_commit_ref()
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS


def test_phase_518_main_commit_opens_cdl_058_and_preserves_non_target_rows() -> None:
    commit_ref = _resolve_phase_518_commit_ref()
    committed_rows = parse_decision_register_rows(_commit_text(str(DECISION_LOG_PATH), commit_ref))
    baseline_rows = parse_decision_register_rows(_commit_text(str(DECISION_LOG_PATH), f"{commit_ref}^"))
    assert committed_rows["CDL-055"] == baseline_rows["CDL-055"]
    assert committed_rows["CDL-056"] == baseline_rows["CDL-056"]
    assert committed_rows["CDL-057"] == baseline_rows["CDL-057"]
    assert committed_rows["CDL-058"]["status"] == "open"
    assert "ratified_phase" not in committed_rows["CDL-058"]
    assert "ratified_date" not in committed_rows["CDL-058"]
    assert "CDL-053" not in committed_rows
