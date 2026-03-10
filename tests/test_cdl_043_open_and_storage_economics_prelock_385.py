from __future__ import annotations

import subprocess
from pathlib import Path

from ilc_core.testing.ratification_mutation_scope_guardrail import (
    assert_head_commit_touched_no_runtime_files,
    parse_decision_register_rows,
)


DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
ARTIFACT_PATH = Path("docs/specs/ilc_cdl_043_storage_economics_prelock_385_v0.1.md")
PHASE_385_SUBJECT_TOKEN = "phase 385 cdl-043 open and storage economics prelock"
EXPECTED_ROW = (
    "| CDL-043 | SIM-003 / CDL-V2 / CDL-V3 | Storage economics, graph pruning policy, and active-graph retention "
    "constraints | open | fixed-threshold pruning with static retention, adaptive pruning with bounded retention windows | "
    "adaptive pruning with bounded retention windows (proposed) | SIM-003 calibration anchor, non-centralization constraint "
    "clause, CDL-042 defer note |"
)
CALIBRATION_TOKENS = (
    "ecu_score_floor",
    "retention_epochs",
    "snapshot_interval",
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


def _resolve_phase_385_commit_ref() -> str:
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
        if PHASE_385_SUBJECT_TOKEN in subject.lower():
            matching.append(commit_hash)

    required_paths = {
        str(DECISION_LOG_PATH),
        str(ARTIFACT_PATH),
        "tests/test_cdl_043_open_and_storage_economics_prelock_385.py",
    }
    for commit_ref in matching:
        changed_paths = _changed_paths_for_commit(commit_ref)
        if required_paths.issubset(changed_paths):
            return commit_ref

    if matching:
        raise AssertionError("phase_385_commit_subject_present_but_no_constitutional_opening_commit")
    raise AssertionError("phase_385_commit_not_present_in_local_history")


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
        "## 2. CDL-043 opening state",
        "## 3. Non-centralization constraint basis",
        "## 4. CDL-042 deferral and sequencing note",
        "## 5. Calibration constants and exclusivity boundary",
        "## 6. Ratification-lane carry-forward notes",
        "## 7. Deferral and phase-boundary constraints",
        "## 8. Canonical anchors",
    ):
        assert heading in text


def test_artifact_has_required_tokens() -> None:
    text = _read(ARTIFACT_PATH)
    for token in (
        "CDL-043 storage economics prelock treats SIM-003 outputs as authoritative calibration evidence: ecu_score_floor=0.5, retention_epochs=1, snapshot_interval=50.",
        "CDL-043 storage economics must not create resource-concentration incentives incompatible with CDL-V3's cluster diversity floor or CDL-V2's sybil resistance requirements; pruning parameters that could systematically advantage large-stake clusters over small-stake clusters require explicit justification against these ratified constraints.",
        "CDL-043 is opened directly after CDL-041; CDL-042 (agent identity namespace) is deferred to Window 392+ pending CDL-039/040 scope resolution.",
        "status: open",
        "No runtime implementation occurs in Phase 385.",
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
    # The Phase-385 `CDL-043` row is a historical prelock reference.
    historical_text = _decision_log_text_at_ref(_resolve_phase_385_commit_ref())
    assert EXPECTED_ROW in historical_text
    rows = parse_decision_register_rows(historical_text)
    assert rows["CDL-043"]["status"] == "open"


def test_cdl_041_dependency_is_historical_reference_and_live_neighbor_state_is_current() -> None:
    # The Phase-385 `CDL-041` dependency is a historical prelock reference.
    historical_rows = parse_decision_register_rows(_decision_log_text_at_ref(_resolve_phase_385_commit_ref()))
    assert historical_rows["CDL-041"]["status"] == "open"

    live_rows = parse_decision_register_rows(_read(DECISION_LOG_PATH))
    assert live_rows["CDL-041"]["status"] == "ratified"
    assert live_rows["CDL-044"]["status"] == "open"


def test_phase_385_commit_additive_only_non_target_shield_and_new_row_guard() -> None:
    commit_ref = _resolve_phase_385_commit_ref()
    old_rows = parse_decision_register_rows(_decision_log_text_at_ref(f"{commit_ref}^1"))
    new_rows = parse_decision_register_rows(_decision_log_text_at_ref(commit_ref))
    added_ids = set(new_rows) - set(old_rows)
    assert added_ids == {"CDL-043"}
    for cdl_id in old_rows:
        assert old_rows[cdl_id] == new_rows[cdl_id], f"row_{cdl_id}_unlawfully_mutated_in_phase_385"


def test_phase_385_commit_touched_no_runtime_files() -> None:
    commit_ref = _resolve_phase_385_commit_ref()
    assert_head_commit_touched_no_runtime_files(commit_ref=commit_ref)
