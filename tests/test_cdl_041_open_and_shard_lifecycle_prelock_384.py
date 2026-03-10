from __future__ import annotations

import subprocess
from pathlib import Path

from ilc_core.testing.ratification_mutation_scope_guardrail import (
    assert_head_commit_touched_no_runtime_files,
    parse_decision_register_rows,
)


DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
ARTIFACT_PATH = Path("docs/specs/ilc_cdl_041_shard_lifecycle_prelock_384_v0.1.md")
PHASE_384_SUBJECT_TOKEN = "phase 384 cdl-041 open and shard lifecycle prelock"
EXPECTED_ROW = (
    "| CDL-041 | SIM-004 / CDL-V3 / CDL-039 | Shard lifecycle operations for creation, merge, and split under "
    "partition and privacy constraints | open | merge-first lifecycle with highest_ecu_wins reconciliation, split-first "
    "elastic lifecycle with delayed merge reconciliation | merge-first lifecycle with highest_ecu_wins reconciliation "
    "(proposed) | SIM-004 reconciliation anchor, CDL-V3 diversity dependency clause, CDL-039 non-inferrability clause, "
    "CDL-042 defer note |"
)
CALIBRATION_TOKENS = (
    "merge_conflict_window_months",
    "split_divergence_guard_months",
    "shard_creation_diversity_floor",
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


def _resolve_phase_384_commit_ref() -> str:
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
        if PHASE_384_SUBJECT_TOKEN in subject.lower():
            matching.append(commit_hash)

    required_paths = {
        str(DECISION_LOG_PATH),
        str(ARTIFACT_PATH),
        "tests/test_cdl_041_open_and_shard_lifecycle_prelock_384.py",
    }
    for commit_ref in matching:
        changed_paths = _changed_paths_for_commit(commit_ref)
        if required_paths.issubset(changed_paths):
            return commit_ref

    if matching:
        raise AssertionError("phase_384_commit_subject_present_but_no_constitutional_opening_commit")
    raise AssertionError("phase_384_commit_not_present_in_local_history")


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
        "## 2. CDL-041 opening state",
        "## 3. SIM-004 reconciliation and partition-window anchor",
        "## 4. Shard lifecycle diversity and privacy constraints",
        "## 5. Calibration constants and exclusivity boundary",
        "## 6. CDL-042 forward pointer and deferral boundary",
        "## 7. Deferral and phase-boundary constraints",
        "## 8. Canonical anchors",
    ):
        assert heading in text


def test_artifact_has_required_tokens() -> None:
    text = _read(ARTIFACT_PATH)
    for token in (
        "Shard merge semantics are constrained by SIM-004's highest_ecu_wins reconciliation rule for issuance-epoch partition divergence; shard splits must not create irreconcilable divergence paths in the T=34-month partition threshold window established by SIM-004.",
        "Shard creation requires satisfaction of CDL-V3 cluster diversity floor; V-series enforcement runtime authorization determines when this requirement is computationally enforced.",
        "Shard lifecycle operations (creation, merge, split) must not allow passive observers to infer cluster membership in violation of CDL-039's cluster membership non-inferrability invariant.",
        "CDL-042 (agent identity namespace) addresses per-agent identity within shard contexts; CDL-042 is deferred to Window 392+ pending CDL-039/040 scope resolution.",
        "status: open",
        "No runtime implementation occurs in Phase 384.",
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
    # The Phase-384 `CDL-041` row is a historical prelock reference.
    historical_text = _decision_log_text_at_ref(_resolve_phase_384_commit_ref())
    assert EXPECTED_ROW in historical_text
    rows = parse_decision_register_rows(historical_text)
    assert rows["CDL-041"]["status"] == "open"


def test_cdl_040_row_is_historical_open_reference_for_phase_384() -> None:
    historical_rows = parse_decision_register_rows(_decision_log_text_at_ref(_resolve_phase_384_commit_ref()))
    assert historical_rows["CDL-040"]["status"] == "open"


def test_phase_384_commit_additive_only_non_target_shield_and_new_row_guard() -> None:
    commit_ref = _resolve_phase_384_commit_ref()
    old_rows = parse_decision_register_rows(_decision_log_text_at_ref(f"{commit_ref}^1"))
    new_rows = parse_decision_register_rows(_decision_log_text_at_ref(commit_ref))
    added_ids = set(new_rows) - set(old_rows)
    assert added_ids == {"CDL-041"}
    for cdl_id in old_rows:
        assert old_rows[cdl_id] == new_rows[cdl_id], f"row_{cdl_id}_unlawfully_mutated_in_phase_384"


def test_phase_384_commit_touched_no_runtime_files() -> None:
    commit_ref = _resolve_phase_384_commit_ref()
    assert_head_commit_touched_no_runtime_files(commit_ref=commit_ref)
