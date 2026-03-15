from __future__ import annotations

import re
import subprocess
from pathlib import Path

from ilc_core.testing.ratification_mutation_scope_guardrail import (
    assert_head_commit_touched_no_runtime_files,
    parse_decision_register_rows,
)


DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
SEQUENCE_LOCK_PATH = Path("docs/specs/ilc_phase_414_423_sequence_lock_v0.1.md")
HARDENING_PATH = Path("docs/specs/ilc_cdl_047_treasury_governance_prelock_hardening_415_v0.1.md")
CDL_047_STUB_PATH = Path("docs/specs/ilc_cdl_047_treasury_governance_opening_stub_414_v0.1.md")
EXPECTED_CDL_047_ROW = (
    "| CDL-047 | ADR-0016 / ADR-0017 / CDL-028 / SIM-008 | Treasury governance framework for bounty issuance "
    "cap, late-economy burn floor, velocity alert, and counter-cyclical authorization | open | fixed treasury "
    "constants without adaptive governance, governed treasury framework with bounty-cap, burn-floor, "
    "velocity-alert, and counter-cyclical authorization, defer treasury governance indefinitely pending later "
    "study | governed treasury framework with bounty-cap, burn-floor, velocity-alert, and counter-cyclical "
    "authorization (proposed) | SIM-008 calibration anchors, ADR-0017 counter-cyclical treasury rationale, "
    "CDL-028 layering clause, governance parameter hardening artifact |"
)
PHASE_415_SUBJECT_TOKEN = "phase 415 cdl-047 treasury governance prelock hardening"
REQUIRED_HEADINGS = (
    "## 1. Scope and non-ratifying boundary",
    "## 2. CDL-047 open-state evidence anchor",
    "## 3. Candidate discrimination and winning candidate confirmation",
    "## 4. Section-7 ratification readiness evidence checklist satisfaction",
    "## 5. SIM-008 bounty-cap calibration anchor",
    "## 6. SIM-008 burn-floor calibration anchor",
    "## 7. SIM-008 velocity-alert calibration anchor",
    "## 8. Upstream dependency chain",
    "## 9. Non-goals",
)
REQUIRED_TOKENS = (
    "status: open",
    "CDL-047 prelock hardening confirms the proposed candidate: governed treasury framework with bounty-cap, burn-floor, velocity-alert, and counter-cyclical authorization.",
    "No CDL row mutation occurs in Phase 415.",
    "Phase 418 is the targeted CDL-047 ratification lane; this hardening artifact constitutes the primary prelock evidence.",
    "Fixed treasury constants without adaptive governance is rejected because the genesis fee-burn default does not provide a constitutional mechanism for late-economy adjustment as the issuance-to-fee transition progresses.",
    "Defer treasury governance indefinitely pending later study is rejected because SIM-008 provides a sufficient calibrated evidence base for constitutional opening, and indefinite deferral leaves a governance gap during the issuance-to-fee transition period.",
    "CDL-047 layers on CDL-028 without amending the 10% genesis fee-burn default.",
    "CDL-047 authorizes an adaptive governance mechanism that allows the burn ratio to be reduced below 10% by governance action as the economy matures, subject to a constitutional burn floor of 0.05.",
    "bounty_cap = 0.15 × B_e",
    "burn_floor = 0.05",
    "velocity_alert_floor = 0.91",
    "These SIM-008 calibration anchors are prelock inputs and do not become constitutional constants until CDL-047 ratification in Phase 418.",
)
REQUIRED_SECTION_4_ITEMS = (
    "1. The governed treasury framework with bounty-cap, burn-floor, velocity-alert, and counter-cyclical authorization is confirmed as the proposed candidate and both rejected candidates remain excluded.",
    "2. SIM-008 bounty-cap calibration anchor is locked: bounty_cap = 0.15 × B_e, as the per-epoch bounty issuance cap prelock input.",
    "3. SIM-008 burn-floor and velocity-alert calibration anchors are locked: burn_floor = 0.05 and velocity_alert_floor = 0.91, as the late-economy policy floor prelock inputs.",
    "4. CDL-028 layering clause is satisfied: CDL-047 layers on CDL-028 without amending the 10% genesis fee-burn default; CDL-047 authorizes the adaptive governance mechanism only.",
    "5. Counter-cyclical authorization scope is constitutionally bounded to late-economy stabilization; fixed-parameter and indefinitely-deferred candidates remain excluded.",
)
REQUIRED_DEPENDENCY_ANCHORS = (
    "docs/adr/ADR_0016_Productive_ECU_Expansion_Bounty_Mechanism.md",
    "docs/adr/ADR_0017_Post_Issuance_Economic_Transition.md",
    "CDL-028",
    "CDL-030",
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


def _resolve_phase_415_commit_ref() -> str:
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
        if PHASE_415_SUBJECT_TOKEN in subject.lower():
            matching.append(commit_hash)
    required_paths = {
        str(HARDENING_PATH),
        "tests/test_phase_415_cdl_047_treasury_governance_prelock_hardening.py",
    }
    for commit_ref in matching:
        changed_paths = _changed_paths_for_commit(commit_ref)
        if required_paths.issubset(changed_paths):
            return commit_ref
    if matching:
        raise AssertionError("phase_415_commit_subject_present_but_no_hardening_artifact_commit")
    raise AssertionError("phase_415_commit_not_present_in_local_history")


def _extract_section(text: str, heading: str) -> str:
    start = text.index(heading)
    rest = text[start + len(heading):]
    match = re.search(r"\n## \d+\. ", rest)
    if match:
        return rest[: match.start()]
    return rest


def test_hardening_artifact_exists_and_contains_required_headings_tokens_checklist_and_dependencies() -> None:
    assert HARDENING_PATH.exists()
    text = _read(HARDENING_PATH)
    for heading in REQUIRED_HEADINGS:
        assert heading in text
    for token in REQUIRED_TOKENS:
        assert token in text
    for item in REQUIRED_SECTION_4_ITEMS:
        assert item in text
    for anchor in REQUIRED_DEPENDENCY_ANCHORS:
        assert anchor in text
    section_4 = _extract_section(text, "## 4. Section-7 ratification readiness evidence checklist satisfaction")
    assert len(re.findall(r"^\d+\. ", section_4, flags=re.MULTILINE)) == 5


def test_phase_414_cdl_047_opening_stub_is_preserved() -> None:
    assert CDL_047_STUB_PATH.exists()
    text = _read(CDL_047_STUB_PATH)
    assert "Phase-415 is the targeted prelock hardening lane for CDL-047." in text
    assert "status: open" in text
    assert "CDL-047 layers on CDL-028 without amending the 10% genesis fee-burn default." in text


def test_cdl_047_and_cdl_048_register_order_preserved() -> None:
    lines = _read(DECISION_LOG_PATH).splitlines()
    cdl_046_index = next(i for i, line in enumerate(lines) if line.startswith("| CDL-046 "))
    cdl_047_index = next(i for i, line in enumerate(lines) if line.startswith("| CDL-047 "))
    cdl_048_index = next(i for i, line in enumerate(lines) if line.startswith("| CDL-048 "))
    assert cdl_047_index == cdl_046_index + 1
    assert cdl_048_index == cdl_047_index + 1


def test_cdl_047_row_is_open() -> None:
    # The Phase-415 `CDL-047` row is a historical prelock reference.
    historical_text = _read_file_at_ref(_resolve_phase_415_commit_ref(), str(DECISION_LOG_PATH))
    rows = parse_decision_register_rows(historical_text)
    assert rows["CDL-047"]["status"] == "open"
    assert EXPECTED_CDL_047_ROW in historical_text


def test_cdl_047_has_no_premature_ratification_metadata() -> None:
    # The Phase-415 `CDL-047` row is a historical prelock reference.
    historical_text = _read_file_at_ref(_resolve_phase_415_commit_ref(), str(DECISION_LOG_PATH))
    rows = parse_decision_register_rows(historical_text)
    assert rows["CDL-047"]["status"] != "ratified"
    assert "ratified_date" not in rows["CDL-047"]
    assert "ratified_phase" not in rows["CDL-047"]


def test_phase_415_commit_no_cdl_row_mutation_stub_immutable_and_sequence_lock_immutable() -> None:
    commit_ref = _resolve_phase_415_commit_ref()
    old_rows = parse_decision_register_rows(_read_file_at_ref(f"{commit_ref}^1", str(DECISION_LOG_PATH)))
    new_rows = parse_decision_register_rows(_read_file_at_ref(commit_ref, str(DECISION_LOG_PATH)))
    assert set(old_rows) == set(new_rows), "phase_415_commit_unlawfully_added_or_removed_cdl_rows"
    for cdl_id in old_rows:
        assert old_rows[cdl_id] == new_rows[cdl_id], f"row_{cdl_id}_unlawfully_mutated_in_phase_415"
    old_stub = _read_file_at_ref(f"{commit_ref}^1", str(CDL_047_STUB_PATH))
    new_stub = _read_file_at_ref(commit_ref, str(CDL_047_STUB_PATH))
    assert old_stub == new_stub, "phase_415_commit_modified_phase_414_opening_stub_unlawfully"
    old_lock = _read_file_at_ref(f"{commit_ref}^1", str(SEQUENCE_LOCK_PATH))
    new_lock = _read_file_at_ref(commit_ref, str(SEQUENCE_LOCK_PATH))
    assert old_lock == new_lock, "phase_415_commit_modified_phase_414_sequence_lock_unlawfully"


def test_phase_415_commit_touched_no_runtime_files() -> None:
    commit_ref = _resolve_phase_415_commit_ref()
    assert_head_commit_touched_no_runtime_files(commit_ref=commit_ref)
