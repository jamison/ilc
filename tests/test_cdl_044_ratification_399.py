from __future__ import annotations

import datetime
import subprocess
from pathlib import Path

from ilc_core.testing.ratification_mutation_scope_guardrail import (
    ALLOWED_RATIFICATION_MUTATION_FIELDS,
    assert_head_commit_touched_no_runtime_files,
    assert_no_non_target_rows_marked_with_phase,
    assert_only_allowed_row_mutations,
    parse_decision_register_rows,
)


EVIDENCE_PATH = Path("docs/specs/ilc_cdl_044_retention_epochs_amendment_ratification_evidence_399_v0.1.md")
DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
PHASE_392_TEST_PATH = Path("tests/test_phase_392_retention_epochs_cdl_amendment_open.py")
PHASE_385_TEST_PATH = Path("tests/test_cdl_043_open_and_storage_economics_prelock_385.py")
PHASE_395_TEST_PATH = Path("tests/test_cdl_043_ratification_395.py")
PHASE_399_COMMIT_SUBJECT_TOKEN = "docs(g8): phase 399 cdl-044 retention-epochs ratification"

_BASE_HEADERS = [
    "decision_id",
    "related_clause",
    "decision_topic",
    "status",
    "options",
    "current_candidate",
    "required_artifacts",
]

_ALLOWED_FIELDS = set(ALLOWED_RATIFICATION_MUTATION_FIELDS) | {"current_candidate"}

_PRE_399_CDL_044_ROW = (
    "| CDL-044 | CDL-039 / SIM-003 / Phase-391 Handoff 391 v0.1 | retention_epochs operational amendment for "
    "CDL-039 deployment boundary | open | retain deferred obligation without amendment row, open dedicated "
    "amendment row with bounded-range prelock, open dedicated amendment row with fixed constant prelock | open "
    "dedicated amendment row with bounded-range prelock (proposed) | Phase-379 retention obligation token, "
    "SIM-003 retention calibration anchor, Phase-391 handoff carry-forward token |"
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _mini_register(row: str) -> str:
    return "\n".join(
        [
            "## Decision Register",
            "",
            "| decision_id | related_clause | decision_topic | status | options | current_candidate | required_artifacts |",
            "|---|---|---|---|---|---|---|",
            row,
            "",
            "## Scoped Ratification Record",
        ]
    )


def _register_row_text(row: dict[str, str]) -> str:
    cells = [row[header] for header in _BASE_HEADERS]
    if "ratified_phase" in row:
        cells.append(f"ratified_phase: {row['ratified_phase']}")
    if "ratified_date" in row:
        cells.append(f"ratified_date: {row['ratified_date']}")
    if "evidence_document" in row:
        cells.append(f"evidence_document: {row['evidence_document']}")
    return "| " + " | ".join(cells) + " |"


def _extract_calibration_section(text: str) -> str:
    lines = text.splitlines()
    start = None
    end = None
    for idx, line in enumerate(lines):
        if line.startswith("## ") and "calibration" in line.lower():
            start = idx
            continue
        if start is not None and line.startswith("## "):
            end = idx
            break
    if start is None:
        raise AssertionError("calibration_section_not_found")
    if end is None:
        end = len(lines)
    return "\n".join(lines[start:end])


def _changed_paths_for_commit(commit_ref: str) -> set[str]:
    result = subprocess.run(
        ["git", "show", "--name-only", "--pretty=", commit_ref],
        capture_output=True,
        check=True,
        text=True,
    )
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


def _resolve_phase_399_commit_ref() -> str:
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
        if PHASE_399_COMMIT_SUBJECT_TOKEN in subject.lower():
            matching_commits.append(commit_hash)

    required_paths = {
        str(DECISION_LOG_PATH),
        str(EVIDENCE_PATH),
        "tests/test_cdl_044_ratification_399.py",
        str(PHASE_392_TEST_PATH),
        str(PHASE_385_TEST_PATH),
        str(PHASE_395_TEST_PATH),
    }
    for commit_ref in matching_commits:
        changed_paths = _changed_paths_for_commit(commit_ref)
        if required_paths.issubset(changed_paths):
            return commit_ref

    if matching_commits:
        raise AssertionError("phase_399_commit_subject_present_but_no_qualifying_ratification_commit")
    raise AssertionError("phase_399_commit_not_present_in_local_history")


def _decision_log_text_at_ref(ref: str) -> str:
    result = subprocess.run(
        ["git", "show", f"{ref}:{DECISION_LOG_PATH}"],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise AssertionError(f"unable_to_read_decision_log_at_ref:{ref}: {result.stderr.strip()}")
    return result.stdout


def test_ratification_evidence_exists_and_has_required_content() -> None:
    assert EVIDENCE_PATH.exists()
    text = _read(EVIDENCE_PATH)
    for heading in (
        "## 1. Purpose and scope",
        "## 2. Ratified amendment decision",
        "## 3. Evidence basis",
        "## 4. CDL-039 forward-obligation closure statement",
        "## 5. Calibration constants resolution",
        "## 6. Epoch-type interpretation closure",
        "## 7. Carry-forward constraints",
        "## 8. Runtime deferral boundary",
        "## 9. Canonical anchors",
    ):
        assert heading in text

    for token in (
        "CDL-044 ratifies retention_epochs operational constant as 1 issuance_epoch (1 month) for CDL-039 deployment boundary enforcement.",
        "CDL-044 closes the CDL-039 forward obligation requiring a named subsequent CDL amendment before deployment.",
        "retention_epochs is issuance-epoch scoped and must not be interpreted on validation-epoch timescale.",
        "No runtime implementation is ratified in Phase 399.",
        "Phase-400 coherence and capsule v1.4 must carry forward a runtime-integrity note: CDL-V1/V2/V3/V7 validators reject non-finite numeric inputs (NaN/Inf).",
        "docs/specs/ilc_cdl_044_retention_epochs_amendment_open_prelock_392_v0.1.md",
        "docs/specs/ilc_phase_392_401_sequence_lock_v0.1.md",
        "docs/specs/ilc_cdl_039_p2p_transport_and_topology_privacy_ratification_evidence_379_v0.1.md",
        "docs/specs/ilc_window_378_391_handoff_391_v0.1.md",
        "docs/specs/ilc_sim_001_002_003_commissioning_results_365_v0.1.md",
        "docs/specs/ilc_sim_003_004_005_interpretation_and_cdl_039_risk_closure_371_v0.1.md",
        "docs/specs/ilc_cdl_v3_diversity_floor_runtime_handoff_397_v0.1.md",
        "docs/specs/ilc_cdl_v7_popperian_gate_runtime_handoff_398_v0.1.md",
    ):
        assert token in text


def test_calibration_section_is_structured_and_resolves_retention_epochs() -> None:
    text = _read(EVIDENCE_PATH)
    section = _extract_calibration_section(text)
    outside = text.replace(section, "", 1)

    for token in (
        "`retention_epochs = 1`",
        "`epoch_type = issuance_epoch`",
        "`epoch_duration = 1 month`",
        "`wall_clock_interpretation = 1 month retention window`",
    ):
        assert token in section
        assert token not in outside

    for disallowed in ("TBD", "TBA", "under review", "bounded_range"):
        assert disallowed not in section


def test_phase_392_385_395_tests_are_historicalized_for_cdl_044() -> None:
    phase_392_text = _read(PHASE_392_TEST_PATH)
    assert '# The Phase-392 `CDL-044` row is a historical amendment-open reference.' in phase_392_text
    assert "_decision_log_text_at_ref(_resolve_phase_392_commit_ref())" in phase_392_text

    phase_385_text = _read(PHASE_385_TEST_PATH)
    assert '# The Phase-385 `CDL-044` neighbor-state check is a historical amendment-open reference.' in phase_385_text
    assert "_decision_log_text_at_ref(_resolve_phase_385_commit_ref())" in phase_385_text

    phase_395_text = _read(PHASE_395_TEST_PATH)
    assert '# The Phase-395 `CDL-044` neighbor-open assertion is a historical amendment-open reference.' in phase_395_text
    assert "_decision_log_text_at_ref(_resolve_phase_395_commit_ref())" in phase_395_text


def test_decision_log_cdl_044_is_ratified_with_expected_metadata_and_scope() -> None:
    rows = parse_decision_register_rows(_read(DECISION_LOG_PATH))
    row = rows["CDL-044"]
    assert row["status"] == "ratified"
    assert row["current_candidate"] == "open dedicated amendment row with fixed constant prelock"
    assert row["ratified_phase"] == "399"
    ratified_date = datetime.date.fromisoformat(row["ratified_date"])
    assert ratified_date.isoformat() == row["ratified_date"]
    assert row["evidence_document"] == str(EVIDENCE_PATH)
    assert rows["CDL-043"]["status"] == "ratified"
    assert_no_non_target_rows_marked_with_phase(rows, phase="399", target_cdls={"CDL-044"})


def test_mutation_scope_guardrail_allows_only_ratification_fields_for_cdl_044() -> None:
    rows = parse_decision_register_rows(_read(DECISION_LOG_PATH))
    old_register = _mini_register(_PRE_399_CDL_044_ROW)
    new_register = _mini_register(_register_row_text(rows["CDL-044"]))
    assert_only_allowed_row_mutations(
        old_register,
        new_register,
        cdl_id="CDL-044",
        allowed_fields=_ALLOWED_FIELDS,
    )


def test_phase_399_commit_non_target_guard() -> None:
    commit_ref = _resolve_phase_399_commit_ref()
    old_text = _decision_log_text_at_ref(f"{commit_ref}^1")
    new_text = _decision_log_text_at_ref(commit_ref)
    old_rows = parse_decision_register_rows(old_text)
    new_rows = parse_decision_register_rows(new_text)
    assert set(old_rows.keys()) == set(new_rows.keys())

    target_old = _mini_register(_register_row_text(old_rows["CDL-044"]))
    target_new = _mini_register(_register_row_text(new_rows["CDL-044"]))
    assert_only_allowed_row_mutations(
        target_old,
        target_new,
        cdl_id="CDL-044",
        allowed_fields=_ALLOWED_FIELDS,
    )

    for cdl_id in old_rows:
        if cdl_id == "CDL-044":
            continue
        assert old_rows[cdl_id] == new_rows[cdl_id], f"row_{cdl_id}_unlawfully_mutated_in_phase_399"


def test_phase_399_commit_touched_no_runtime_files() -> None:
    commit_ref = _resolve_phase_399_commit_ref()
    assert_head_commit_touched_no_runtime_files(commit_ref=commit_ref)
