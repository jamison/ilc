from __future__ import annotations

import subprocess
from pathlib import Path

from ilc_core.testing.ratification_mutation_scope_guardrail import (
    assert_head_commit_touched_no_runtime_files,
    parse_decision_register_rows,
)


DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
SEQUENCE_LOCK_PATH = Path("docs/specs/ilc_phase_414_423_sequence_lock_v0.1.md")
CDL_047_STUB_PATH = Path("docs/specs/ilc_cdl_047_treasury_governance_opening_stub_414_v0.1.md")
CDL_048_STUB_PATH = Path("docs/specs/ilc_cdl_048_ecu_mandatory_conversion_deadline_opening_stub_414_v0.1.md")
PHASE_414_SUBJECT_TOKEN = "phase 414 window sequence lock and cdl-047 cdl-048 opening"
EXPECTED_CDL_047_ROW = (
    "| CDL-047 | ADR-0016 / ADR-0017 / CDL-028 / SIM-008 | Treasury governance framework for bounty issuance "
    "cap, late-economy burn floor, velocity alert, and counter-cyclical authorization | open | fixed treasury "
    "constants without adaptive governance, governed treasury framework with bounty-cap, burn-floor, "
    "velocity-alert, and counter-cyclical authorization, defer treasury governance indefinitely pending later "
    "study | governed treasury framework with bounty-cap, burn-floor, velocity-alert, and counter-cyclical "
    "authorization (proposed) | SIM-008 calibration anchors, ADR-0017 counter-cyclical treasury rationale, "
    "CDL-028 layering clause, governance parameter hardening artifact |"
)
EXPECTED_CDL_048_ROW = (
    "| CDL-048 | ADR-0017 / CDL-V1 / CDL-035 / SIM-008 | ECU mandatory conversion deadline and circulation "
    "enforcement | open | indefinite ECU retention, governed conversion deadline with anti-hoarding forced "
    "circulation, discretionary operator conversion windows | governed conversion deadline with anti-hoarding "
    "forced circulation (proposed) | SIM-008 deadline calibration anchor, CDL-V1 temporal-decay complement "
    "clause, CDL-035 lifecycle attachment clause, no-reputation-carry-forward clause |"
)


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


def _resolve_phase_414_commit_ref() -> str:
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
        if PHASE_414_SUBJECT_TOKEN in subject.lower():
            matching.append(commit_hash)

    required_paths = {
        str(DECISION_LOG_PATH),
        str(SEQUENCE_LOCK_PATH),
        str(CDL_047_STUB_PATH),
        str(CDL_048_STUB_PATH),
        "tests/test_phase_414_cdl_047_and_cdl_048_opening.py",
    }
    for commit_ref in matching:
        changed_paths = _changed_paths_for_commit(commit_ref)
        if required_paths.issubset(changed_paths):
            return commit_ref

    if matching:
        raise AssertionError("phase_414_commit_subject_present_but_no_constitutional_opening_commit")
    raise AssertionError("phase_414_commit_not_present_in_local_history")


def _decision_log_text_at_ref(ref: str) -> str:
    result = subprocess.run(
        ["git", "show", f"{ref}:{DECISION_LOG_PATH}"],
        capture_output=True,
        check=False,
        text=True,
    )
    if result.returncode != 0:
        raise AssertionError(f"unable_to_read_decision_log_at_ref:{ref}: {result.stderr.strip()}")
    return result.stdout


def test_sequence_lock_exists_and_contains_required_headings_and_tokens() -> None:
    assert SEQUENCE_LOCK_PATH.exists()
    text = _read(SEQUENCE_LOCK_PATH)

    for heading in (
        "## 1. Window identity and scope",
        "## 2. Inputs and closure inheritance",
        "## 3. Economic-CDL opening authorization and calibration boundary",
        "## 4. Locked phase table (414-423)",
        "## 5. Constitutional first-action: two-CDL opening batch",
        "## 6. Sequencing constraints and Phase-417 blocking rule",
        "## 7. D2e CLI track independence and Window-424+ boundary",
        "## 8. Canonical anchors and non-goals",
    ):
        assert heading in text

    for token in (
        "Window 414-423 is the Economic CDL and D2e CLI Integration Block.",
        "CDL-039, CDL-040, CDL-041, CDL-042, CDL-043, CDL-044, CDL-045, and CDL-046 are ratified at Window 414-423 entry.",
        "CDL-V1, CDL-V2, CDL-V3, and CDL-V7 runtime lanes remain implemented and carry forward without additional V-series governance action in this window.",
        "D2e runtime carry-forward remains active: ilc_core/identity/agent_id_runtime.py and ilc_core/node/timed_out_lifecycle_runtime_411.py are implemented at window entry.",
        "SIM-008 evidence is available; CDL-047 and CDL-048 opening is authorized in Phase 414.",
        "Phase 417 Popperian review is non-ratifying and does not itself open, amend, or ratify any CDL row.",
        "CRITICAL findings in CDL-047 or CDL-048 during Phase 417 block ratification until the corresponding prelock artifact is patched and re-reviewed.",
        "D2e CLI integration is an independent track and is not blocked by CDL-047 or CDL-048 ratification.",
        "CDL-049 is not pre-authorized and may open only if Phase 417 identifies a required constitutional amendment lane.",
        "Phase 414 opens CDL-047 and CDL-048 as a two-CDL opening batch.",
    ):
        assert token in text


def test_cdl_047_opening_stub_exists_and_contains_required_headings_and_tokens() -> None:
    assert CDL_047_STUB_PATH.exists()
    text = _read(CDL_047_STUB_PATH)

    for heading in (
        "## 1. Purpose and scope",
        "## 2. CDL-047 opening state",
        "## 3. Treasury governance scope and CDL-028 layering",
        "## 4. SIM-008 calibration anchors",
        "## 5. Counter-cyclical authorization framing",
        "## 6. Upstream dependencies and sequencing note",
        "## 7. Out-of-scope and deferred tracks",
        "## 8. Canonical anchors",
    ):
        assert heading in text

    for token in (
        "status: open",
        "CDL-047 opens as the treasury governance framework lane for bounty-cap, burn-floor, velocity-alert, and counter-cyclical treasury authorization review.",
        "CDL-047 layers on CDL-028 without amending the 10% genesis fee-burn default.",
        "SIM-008 provides the opening calibration anchors: bounty_cap = 0.15 × B_e, burn_floor = 0.05, velocity_alert_floor = 0.91.",
        "Phase-415 is the targeted prelock hardening lane for CDL-047.",
        "No ratification or runtime implementation occurs in Phase 414.",
    ):
        assert token in text


def test_cdl_048_opening_stub_exists_and_contains_required_headings_and_tokens() -> None:
    assert CDL_048_STUB_PATH.exists()
    text = _read(CDL_048_STUB_PATH)

    for heading in (
        "## 1. Purpose and scope",
        "## 2. CDL-048 opening state",
        "## 3. ECU circulation intent and constitutional framing",
        "## 4. SIM-008 deadline anchor",
        "## 5. Temporal decay, lifecycle, and no-carry-forward constraints",
        "## 6. Upstream dependencies and sequencing note",
        "## 7. Out-of-scope and deferred tracks",
        "## 8. Canonical anchors",
    ):
        assert heading in text

    for token in (
        "status: open",
        "CDL-048 opens as the ECU mandatory conversion deadline lane for forced circulation and anti-hoarding policy review.",
        "SIM-008 provides the opening deadline anchor: ecu_conversion_deadline = 4 issuance epochs.",
        "CDL-048 complements CDL-V1 temporal decay and CDL-035 lifecycle governance rather than replacing them.",
        "Phase-416 is the targeted prelock hardening lane for CDL-048.",
        "No ratification or runtime implementation occurs in Phase 414.",
    ):
        assert token in text


def test_decision_log_contains_exact_cdl_047_and_cdl_048_opening_rows() -> None:
    # The Phase-414 `CDL-047` row is a historical opening reference.
    historical_text = _decision_log_text_at_ref(_resolve_phase_414_commit_ref())
    assert EXPECTED_CDL_047_ROW in historical_text
    rows = parse_decision_register_rows(historical_text)
    assert rows["CDL-047"]["status"] == "open"

    # The Phase-414 `CDL-048` row is a historical opening reference.
    assert EXPECTED_CDL_048_ROW in historical_text
    assert rows["CDL-048"]["status"] == "open"


def test_cdl_047_and_cdl_048_rows_appended_after_cdl_046_in_correct_order() -> None:
    lines = _read(DECISION_LOG_PATH).splitlines()
    cdl_046_index = next(i for i, line in enumerate(lines) if line.startswith("| CDL-046 "))
    cdl_047_index = next(i for i, line in enumerate(lines) if line.startswith("| CDL-047 "))
    cdl_048_index = next(i for i, line in enumerate(lines) if line.startswith("| CDL-048 "))
    assert cdl_047_index == cdl_046_index + 1
    assert cdl_048_index == cdl_047_index + 1


def test_phase_414_commit_additive_only_non_target_shield() -> None:
    commit_ref = _resolve_phase_414_commit_ref()
    old_rows = parse_decision_register_rows(_decision_log_text_at_ref(f"{commit_ref}^1"))
    new_rows = parse_decision_register_rows(_decision_log_text_at_ref(commit_ref))
    added_ids = set(new_rows) - set(old_rows)
    assert added_ids == {"CDL-047", "CDL-048"}
    for cdl_id in old_rows:
        assert old_rows[cdl_id] == new_rows[cdl_id], f"row_{cdl_id}_unlawfully_mutated_in_phase_414"


def test_phase_414_commit_touched_no_runtime_files() -> None:
    commit_ref = _resolve_phase_414_commit_ref()
    assert_head_commit_touched_no_runtime_files(commit_ref=commit_ref)
