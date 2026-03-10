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


EVIDENCE_PATH = Path("docs/specs/ilc_cdl_041_shard_lifecycle_ratification_evidence_394_v0.1.md")
DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
PHASE_384_TEST_PATH = Path("tests/test_cdl_041_open_and_shard_lifecycle_prelock_384.py")
PHASE_385_TEST_PATH = Path("tests/test_cdl_043_open_and_storage_economics_prelock_385.py")
PHASE_394_COMMIT_SUBJECT_TOKEN = "docs(g8): phase 394 cdl-041 ratification"

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

_PRE_394_CDL_041_ROW = (
    "| CDL-041 | SIM-004 / CDL-V3 / CDL-039 | Shard lifecycle operations for creation, merge, and split under "
    "partition and privacy constraints | open | merge-first lifecycle with highest_ecu_wins reconciliation, split-first "
    "elastic lifecycle with delayed merge reconciliation | merge-first lifecycle with highest_ecu_wins reconciliation "
    "(proposed) | SIM-004 reconciliation anchor, CDL-V3 diversity dependency clause, CDL-039 non-inferrability clause, "
    "CDL-042 defer note |"
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


def _resolve_phase_394_commit_ref() -> str:
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
        if PHASE_394_COMMIT_SUBJECT_TOKEN in subject.lower():
            matching_commits.append(commit_hash)

    required_paths = {
        str(DECISION_LOG_PATH),
        str(EVIDENCE_PATH),
        "tests/test_cdl_041_ratification_394.py",
        str(PHASE_384_TEST_PATH),
        str(PHASE_385_TEST_PATH),
    }
    for commit_ref in matching_commits:
        changed_paths = _changed_paths_for_commit(commit_ref)
        if required_paths.issubset(changed_paths):
            return commit_ref

    if matching_commits:
        raise AssertionError("phase_394_commit_subject_present_but_no_qualifying_ratification_commit")
    raise AssertionError("phase_394_commit_not_present_in_local_history")


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
        "## 2. Ratified decision",
        "## 3. Evidence basis",
        "## 4. Section-3 authoritative evidence checklist satisfaction",
        "## 5. Calibration constants resolution",
        "## 6. Shard-lifecycle constitutional closure",
        "## 7. Carry-forward constraints",
        "## 8. Runtime deferral boundary",
        "## 9. Canonical anchors",
    ):
        assert heading in text

    for token in (
        "CDL-041 ratifies merge-first shard lifecycle with highest_ecu_wins reconciliation under SIM-004 partition evidence constraints.",
        "Shard creation remains constrained by CDL-V3 diversity-floor requirements.",
        "Shard lifecycle operations remain bound by CDL-039 cluster membership non-inferrability requirements.",
        "No runtime implementation of CDL-041 is ratified in Phase 394.",
        "CDL-042 opening remains sequenced after CDL-041 and CDL-043 ratification completion.",
        "docs/specs/ilc_cdl_041_shard_lifecycle_prelock_384_v0.1.md",
        "docs/specs/ilc_phase_392_401_sequence_lock_v0.1.md",
        "docs/specs/ilc_cdl_039_p2p_transport_and_topology_privacy_ratification_evidence_379_v0.1.md",
        "docs/specs/ilc_cdl_040_admission_control_and_identity_envelope_ratification_evidence_393_v0.1.md",
        "docs/specs/ilc_sim_004_partition_resilience_commissioning_results_369_v0.1.md",
    ):
        assert token in text


def test_calibration_section_is_structured_and_resolves_all_parameter_groups() -> None:
    text = _read(EVIDENCE_PATH)
    section = _extract_calibration_section(text)
    outside = text.replace(section, "", 1)
    for token in (
        "merge_conflict_window_months",
        "split_divergence_guard_months",
        "shard_creation_diversity_floor",
    ):
        assert token in section
        assert token not in outside

    for placeholder in ("TBD", "TBA", "under review"):
        assert placeholder not in section


def test_phase_384_and_385_prelock_tests_are_historicalized() -> None:
    phase_384_text = _read(PHASE_384_TEST_PATH)
    assert '# The Phase-384 `CDL-041` row is a historical prelock reference.' in phase_384_text
    assert "_decision_log_text_at_ref(_resolve_phase_384_commit_ref())" in phase_384_text

    phase_385_text = _read(PHASE_385_TEST_PATH)
    assert '# The Phase-385 `CDL-041` dependency is a historical prelock reference.' in phase_385_text
    assert "_decision_log_text_at_ref(_resolve_phase_385_commit_ref())" in phase_385_text


def test_decision_log_cdl_041_is_ratified_with_expected_metadata_and_live_neighbor_state() -> None:
    rows = parse_decision_register_rows(_read(DECISION_LOG_PATH))
    row = rows["CDL-041"]
    assert row["status"] == "ratified"
    assert row["current_candidate"] == "merge-first lifecycle with highest_ecu_wins reconciliation"
    assert row["ratified_phase"] == "394"
    ratified_date = datetime.date.fromisoformat(row["ratified_date"])
    assert ratified_date.isoformat() == row["ratified_date"]
    assert row["evidence_document"] == str(EVIDENCE_PATH)
    assert rows["CDL-040"]["status"] == "ratified"
    assert rows["CDL-043"]["status"] == "open"
    assert_no_non_target_rows_marked_with_phase(rows, phase="394", target_cdls={"CDL-041"})


def test_mutation_scope_guardrail_allows_only_ratification_fields_for_cdl_041() -> None:
    rows = parse_decision_register_rows(_read(DECISION_LOG_PATH))
    old_register = _mini_register(_PRE_394_CDL_041_ROW)
    new_register = _mini_register(_register_row_text(rows["CDL-041"]))
    assert_only_allowed_row_mutations(
        old_register,
        new_register,
        cdl_id="CDL-041",
        allowed_fields=_ALLOWED_FIELDS,
    )


def test_full_non_target_row_mutation_guard_for_phase_394() -> None:
    commit_ref = _resolve_phase_394_commit_ref()
    old_text = _decision_log_text_at_ref(f"{commit_ref}^1")
    new_text = _decision_log_text_at_ref(commit_ref)
    old_rows = parse_decision_register_rows(old_text)
    new_rows = parse_decision_register_rows(new_text)
    assert set(old_rows.keys()) == set(new_rows.keys())

    target_old = _mini_register(_register_row_text(old_rows["CDL-041"]))
    target_new = _mini_register(_register_row_text(new_rows["CDL-041"]))
    assert_only_allowed_row_mutations(
        target_old,
        target_new,
        cdl_id="CDL-041",
        allowed_fields=_ALLOWED_FIELDS,
    )

    for cdl_id in old_rows:
        if cdl_id == "CDL-041":
            continue
        assert old_rows[cdl_id] == new_rows[cdl_id], f"row_{cdl_id}_unlawfully_mutated_in_phase_394"


def test_phase_394_commit_touched_no_runtime_files() -> None:
    commit_ref = _resolve_phase_394_commit_ref()
    assert_head_commit_touched_no_runtime_files(commit_ref=commit_ref)
