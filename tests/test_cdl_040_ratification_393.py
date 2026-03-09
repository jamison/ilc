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


EVIDENCE_PATH = Path(
    "docs/specs/ilc_cdl_040_admission_control_and_identity_envelope_ratification_evidence_393_v0.1.md"
)
DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
PHASE_383_TEST_PATH = Path("tests/test_cdl_040_open_and_admission_control_identity_envelope_prelock_383.py")
PHASE_393_COMMIT_SUBJECT = "docs(g8): phase 393 cdl-040 ratification"

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

_PRE_393_CDL_040_ROW = (
    "| CDL-040 | ADR-0014 / CDL-034 / CDL-039 | Admission control policy and identity-envelope semantics | "
    "open | identity-envelope extension of authored payload, fourth-envelope plus CDL-034 companion amendment | "
    "identity-envelope extension of authored payload (proposed) | ADR-0014 anchor, admission-control scope boundary clause, "
    "CDL-039 dependency clause |"
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


def _resolve_phase_393_commit_ref() -> str:
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
        if subject.strip() == PHASE_393_COMMIT_SUBJECT:
            matching_commits.append(commit_hash)

    required_paths = {
        str(DECISION_LOG_PATH),
        str(EVIDENCE_PATH),
        "tests/test_cdl_040_ratification_393.py",
        str(PHASE_383_TEST_PATH),
    }
    for commit_ref in matching_commits:
        changed_paths = _changed_paths_for_commit(commit_ref)
        if required_paths.issubset(changed_paths):
            return commit_ref

    if matching_commits:
        raise AssertionError("phase_393_commit_subject_present_but_no_qualifying_ratification_commit")
    raise AssertionError("phase_393_commit_not_present_in_local_history")


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
        "## 6. Scope boundary and dependency closure",
        "## 7. Carry-forward constraints",
        "## 8. Runtime deferral boundary",
        "## 9. Canonical anchors",
    ):
        assert heading in text

    for token in (
        "CDL-040 ratifies Option A: identity envelope is a structured extension of the Authored Payload envelope under CDL-034; no fourth envelope type is introduced.",
        "Admission control remains network-layer governance and does not constitute knowledge-claim acceptance under CDL-V7 or 7+1 panel semantics.",
        "CDL-040 enforceability remains conditional on CDL-039 transport privacy invariants ratified in Phase 379.",
        "No runtime implementation of CDL-040 is ratified in Phase 393.",
        "CDL-042 opening remains sequenced after CDL-040, CDL-041, and CDL-043 ratification steps defined in the Phase-392 sequence lock.",
        "docs/specs/ilc_cdl_040_admission_control_and_identity_envelope_prelock_383_v0.1.md",
        "docs/specs/ilc_phase_392_401_sequence_lock_v0.1.md",
        "docs/specs/ilc_cdl_039_p2p_transport_and_topology_privacy_ratification_evidence_379_v0.1.md",
        "docs/specs/ilc_window_378_391_handoff_391_v0.1.md",
        "docs/adr/ADR_0014_Identity_Sybil_and_Admission_Control_Envelope.md",
    ):
        assert token in text


def test_calibration_section_is_structured_and_resolves_all_parameter_groups() -> None:
    text = _read(EVIDENCE_PATH)
    section = _extract_calibration_section(text)
    for token in (
        "identity_binding_grace_epochs",
        "admission_stake_floor",
        "admission_quorum_floor",
    ):
        assert token in section
    assert "bounded_range" not in section


def test_phase_383_prelock_test_is_historicalized() -> None:
    text = _read(PHASE_383_TEST_PATH)
    assert '# The Phase-383 `CDL-040` row is a historical prelock reference.' in text
    assert "_decision_log_text_at_ref(_resolve_phase_383_commit_ref())" in text


def test_decision_log_cdl_040_is_ratified_with_expected_metadata_and_scope() -> None:
    rows = parse_decision_register_rows(_read(DECISION_LOG_PATH))
    row = rows["CDL-040"]
    assert row["status"] == "ratified"
    assert row["current_candidate"] == "identity-envelope extension of authored payload"
    assert row["ratified_phase"] == "393"
    ratified_date = datetime.date.fromisoformat(row["ratified_date"])
    assert ratified_date.isoformat() == row["ratified_date"]
    assert row["evidence_document"] == str(EVIDENCE_PATH)
    assert_no_non_target_rows_marked_with_phase(rows, phase="393", target_cdls={"CDL-040"})


def test_mutation_scope_guardrail_allows_only_ratification_fields_for_cdl_040() -> None:
    rows = parse_decision_register_rows(_read(DECISION_LOG_PATH))
    old_register = _mini_register(_PRE_393_CDL_040_ROW)
    new_register = _mini_register(_register_row_text(rows["CDL-040"]))
    assert_only_allowed_row_mutations(
        old_register,
        new_register,
        cdl_id="CDL-040",
        allowed_fields=_ALLOWED_FIELDS,
    )


def test_full_non_target_row_mutation_guard_for_phase_393() -> None:
    commit_ref = _resolve_phase_393_commit_ref()
    old_text = _decision_log_text_at_ref(f"{commit_ref}^1")
    new_text = _decision_log_text_at_ref(commit_ref)
    old_rows = parse_decision_register_rows(old_text)
    new_rows = parse_decision_register_rows(new_text)
    assert set(old_rows.keys()) == set(new_rows.keys())

    target_old = _mini_register(_register_row_text(old_rows["CDL-040"]))
    target_new = _mini_register(_register_row_text(new_rows["CDL-040"]))
    assert_only_allowed_row_mutations(
        target_old,
        target_new,
        cdl_id="CDL-040",
        allowed_fields=_ALLOWED_FIELDS,
    )

    for cdl_id in old_rows:
        if cdl_id == "CDL-040":
            continue
        assert old_rows[cdl_id] == new_rows[cdl_id], f"row_{cdl_id}_unlawfully_mutated_in_phase_393"


def test_phase_393_commit_touched_no_runtime_files() -> None:
    commit_ref = _resolve_phase_393_commit_ref()
    assert_head_commit_touched_no_runtime_files(commit_ref=commit_ref)
