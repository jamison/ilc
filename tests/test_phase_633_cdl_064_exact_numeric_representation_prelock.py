from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

PRELOCK_PATH = Path("docs/specs/ilc_cdl_064_exact_numeric_representation_prelock_633_v0.1.md")
SIM_PATH = Path("docs/specs/ilc_sim_numeric_01_representation_evaluation_633_v0.1.md")
DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
TEST_PATH = Path("tests/test_phase_633_cdl_064_exact_numeric_representation_prelock.py")
WALKTHROUGH_PATH = Path(
    "docs/phases/phase_633_g8_cdl_064_prelock_and_sim_numeric_01_walkthrough.md"
)
STATUS_PATH = Path("docs/phases/STATUS.md")
PHASE_633_SUBJECT_TOKEN = "phase 633 cdl-064 prelock and sim-numeric-01"
PHASE_633_BACKFILL_SUBJECT_TOKEN = "phase 633 walkthrough and status backfill"
EXACT_REQUIRED_MAIN_PATHS = {
    str(PRELOCK_PATH),
    str(SIM_PATH),
    str(TEST_PATH),
}
EXACT_REQUIRED_BACKFILL_PATHS = {
    str(WALKTHROUGH_PATH),
    str(STATUS_PATH),
}
REQUIRED_HEADINGS = (
    "## 1. Authorization basis and prelock target",
    "## 2. Representation options and evaluation criteria",
    "## 3. Selected exact-numeric direction",
    "## 4. Tier-0 migration invariants",
    "## 5. Constitutional clause draft",
    "## 6. Forward pointer to ratification and runtime migration",
)
REQUIRED_TOKENS = (
    "cdl_064_prelock_633_locked",
    "sim_numeric_01_consumed_for_prelock",
    "representation_options_evaluated",
    "exact_numeric_direction_selected_for_ratification",
    "tier0_migration_invariants_defined",
    "float_retention_rejected_for_tier0",
    "window_631_636_moves_to_cdl_064_ratification",
)
SIM_REQUIRED_HEADINGS = (
    "## 1. Simulation identity and question",
    "## 2. Parameters and assumptions",
    "## 3. Analysis",
    "## 4. Results",
    "## 5. Governance dispositions",
    "## 6. Forward pointer",
)
SIM_REQUIRED_SNIPPETS = (
    "option A: `retain-float-rounding-and-tolerance`",
    "option B: `exact-decimal-runtime-contract`",
    "option C: `fixed-point-minor-unit-contract`",
    "deterministic replay behavior",
    "arithmetic exactness",
    "canonical serialization stability",
    "storage/export compatibility",
    "migration complexity",
    "cross-language portability",
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


def _find_commit_ref(*, subject_token: str) -> str | None:
    result = subprocess.run(
        ["git", "log", "--format=%H%x09%s"],
        capture_output=True,
        check=True,
        text=True,
    )
    for line in result.stdout.splitlines():
        if "\t" not in line:
            continue
        commit_hash, subject = line.split("\t", 1)
        if subject_token in subject.lower():
            return commit_hash
    return None


def _resolve_commit_ref(*, subject_token: str, expected_paths: set[str]) -> str:
    result = subprocess.run(
        ["git", "log", "--format=%H%x09%s"],
        capture_output=True,
        check=True,
        text=True,
    )
    matches: list[str] = []
    for line in result.stdout.splitlines():
        if "\t" not in line:
            continue
        commit_hash, subject = line.split("\t", 1)
        if subject_token not in subject.lower():
            continue
        matches.append(commit_hash)
    for commit_ref in matches:
        if _changed_paths_for_commit(commit_ref) == expected_paths:
            return commit_ref
    raise AssertionError(f"commit_not_present_in_local_history:{subject_token}")


def _require_commit_or_skip(subject_token: str) -> None:
    if _find_commit_ref(subject_token=subject_token) is None:
        pytest.skip(f"commit_not_yet_present:{subject_token}")


def test_prelock_document_exists_and_contains_required_headings() -> None:
    text = _read(PRELOCK_PATH)
    for heading in REQUIRED_HEADINGS:
        assert heading in text


def test_prelock_document_contains_all_required_tokens() -> None:
    text = _read(PRELOCK_PATH)
    for token in REQUIRED_TOKENS:
        assert token in text


def test_sim_numeric_01_file_exists_and_evaluates_options_against_required_criteria() -> None:
    text = _read(SIM_PATH)
    for heading in SIM_REQUIRED_HEADINGS:
        assert heading in text
    for snippet in SIM_REQUIRED_SNIPPETS:
        assert snippet in text
    assert "Simulation verdict:" in text


def test_prelock_section_three_selects_exact_decimal_and_rejects_float_retention() -> None:
    text = _read(PRELOCK_PATH)
    assert "Phase 633 selects option B: `exact-decimal-runtime-contract`" in text
    assert "Option A is rejected." in text
    assert "float plus rounding/tolerance remains a non-exact contract" in text
    assert "Option C is not selected for CDL-064 v1." in text


def test_prelock_section_four_defines_required_migration_invariants() -> None:
    text = _read(PRELOCK_PATH)
    assert "No float in Tier-0 internal balances, stake totals, reward totals, or" in text
    assert "No epsilon-based equality in Tier-0 settlement correctness checks" in text
    assert "Canonical machine serialization rule:" in text
    assert "Tier-0 exact numeric values serialize as normalized base-10 strings" in text
    assert "simulations, analytics, research helpers, and public runtime widening stay" in text


def test_prelock_section_five_drafts_all_constitutional_clause_classes() -> None:
    text = _read(PRELOCK_PATH)
    assert "Clause class 1 — exact numeric representation requirement:" in text
    assert "Clause class 2 — exact arithmetic requirement:" in text
    assert "Clause class 3 — canonical serialization requirement:" in text
    assert "Clause class 4 — migration boundary and non-goals:" in text


def test_phase_633_main_commit_touches_expected_paths_only_and_no_cdl_or_runtime_mutation() -> None:
    _require_commit_or_skip(PHASE_633_SUBJECT_TOKEN)
    commit_ref = _resolve_commit_ref(
        subject_token=PHASE_633_SUBJECT_TOKEN,
        expected_paths=EXACT_REQUIRED_MAIN_PATHS,
    )
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert changed_paths == EXACT_REQUIRED_MAIN_PATHS
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert not any(path.startswith("ilc_core/") for path in changed_paths)


def test_phase_633_backfill_commit_touches_expected_paths_only() -> None:
    _require_commit_or_skip(PHASE_633_BACKFILL_SUBJECT_TOKEN)
    commit_ref = _resolve_commit_ref(
        subject_token=PHASE_633_BACKFILL_SUBJECT_TOKEN,
        expected_paths=EXACT_REQUIRED_BACKFILL_PATHS,
    )
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert changed_paths == EXACT_REQUIRED_BACKFILL_PATHS
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert not any(path.startswith("ilc_core/") for path in changed_paths)
