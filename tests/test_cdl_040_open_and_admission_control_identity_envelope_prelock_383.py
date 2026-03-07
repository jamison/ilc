from __future__ import annotations

import subprocess
from pathlib import Path

from ilc_core.testing.ratification_mutation_scope_guardrail import (
    assert_head_commit_touched_no_runtime_files,
    parse_decision_register_rows,
)


DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
ARTIFACT_PATH = Path("docs/specs/ilc_cdl_040_admission_control_and_identity_envelope_prelock_383_v0.1.md")
PHASE_383_SUBJECT_TOKEN = "phase 383 cdl-040 open and admission control identity envelope prelock"
EXPECTED_ROW = (
    "| CDL-040 | ADR-0014 / CDL-034 / CDL-039 | Admission control policy and identity-envelope semantics | "
    "open | identity-envelope extension of authored payload, fourth-envelope plus CDL-034 companion amendment | "
    "identity-envelope extension of authored payload (proposed) | ADR-0014 anchor, admission-control scope boundary clause, "
    "CDL-039 dependency clause |"
)
CALIBRATION_TOKENS = (
    "identity_binding_grace_epochs",
    "admission_stake_floor",
    "admission_quorum_floor",
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


def _resolve_phase_383_commit_ref() -> str:
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
        if PHASE_383_SUBJECT_TOKEN in subject.lower():
            matching.append(commit_hash)

    required_paths = {
        str(DECISION_LOG_PATH),
        str(ARTIFACT_PATH),
        "tests/test_cdl_040_open_and_admission_control_identity_envelope_prelock_383.py",
    }
    for commit_ref in matching:
        changed_paths = _changed_paths_for_commit(commit_ref)
        if required_paths.issubset(changed_paths):
            return commit_ref

    if matching:
        raise AssertionError("phase_383_commit_subject_present_but_no_constitutional_opening_commit")
    raise AssertionError("phase_383_commit_not_present_in_local_history")


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


def _section_body(text: str, heading: str) -> str:
    marker = f"## {heading}"
    if marker not in text:
        raise AssertionError(f"section_missing:{heading}")
    after = text.split(marker, 1)[1]
    if "\n## " in after:
        return after.split("\n## ", 1)[0]
    return after


def test_artifact_exists_and_has_required_headings() -> None:
    assert ARTIFACT_PATH.exists()
    text = _read(ARTIFACT_PATH)
    for heading in (
        "## 1. Purpose and scope",
        "## 2. CDL-040 opening state",
        "## 3. Identity-envelope disambiguation",
        "## 4. Admission-control scope boundary",
        "## 5. Calibration constants and exclusivity boundary",
        "## 6. CDL-039 dependency and enforceability",
        "## 7. Deferral and phase-boundary constraints",
        "## 8. Canonical anchors",
    ):
        assert heading in text


def test_artifact_has_required_tokens() -> None:
    text = _read(ARTIFACT_PATH)
    for token in (
        "CDL-040 identity envelope is a structured extension of the Authored Payload envelope defined in CDL-034, not a fourth envelope type; CDL-034's authorship attribution requirement is inherited without modification.",
        "Admission control is a network-layer governance mechanism and is explicitly separate from knowledge-claim evaluation governed by CDL-V7 and the 7+1 evaluation panel; admission does not constitute knowledge-claim acceptance.",
        "CDL-040 admission control enforceability is conditional on CDL-039 ratification providing Transport Envelope privacy invariants; CDL-039 is ratified in Phase 379.",
        "docs/adr/ADR_0014_Identity_Sybil_and_Admission_Control_Envelope.md",
        "status: open",
        "No runtime implementation occurs in Phase 383.",
    ):
        assert token in text


def test_calibration_section_tokens_are_scoped_to_section_five_only() -> None:
    text = _read(ARTIFACT_PATH)
    section_five = _section_body(text, "5. Calibration constants and exclusivity boundary")
    outside = text.replace(section_five, "", 1)

    for token in CALIBRATION_TOKENS:
        assert token in section_five
        assert token not in outside


def test_decision_log_contains_exact_new_row_and_open_state() -> None:
    text = _read(DECISION_LOG_PATH)
    assert EXPECTED_ROW in text
    rows = parse_decision_register_rows(text)
    assert rows["CDL-040"]["status"] == "open"


def test_cdl_039_row_remains_ratified_in_live_decision_log() -> None:
    rows = parse_decision_register_rows(_read(DECISION_LOG_PATH))
    assert rows["CDL-039"]["status"] == "ratified"


def test_phase_383_commit_additive_only_non_target_shield_and_new_row_guard() -> None:
    commit_ref = _resolve_phase_383_commit_ref()
    old_rows = parse_decision_register_rows(_decision_log_text_at_ref(f"{commit_ref}^1"))
    new_rows = parse_decision_register_rows(_decision_log_text_at_ref(commit_ref))
    added_ids = set(new_rows) - set(old_rows)
    assert added_ids == {"CDL-040"}
    for cdl_id in old_rows:
        assert old_rows[cdl_id] == new_rows[cdl_id], f"row_{cdl_id}_unlawfully_mutated_in_phase_383"


def test_phase_383_commit_touched_no_runtime_files() -> None:
    commit_ref = _resolve_phase_383_commit_ref()
    assert_head_commit_touched_no_runtime_files(commit_ref=commit_ref)
