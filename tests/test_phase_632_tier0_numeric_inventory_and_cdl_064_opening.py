from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from ilc_core.testing.ratification_mutation_scope_guardrail import (
    parse_decision_register_rows,
)

INVENTORY_PATH = Path(
    "docs/specs/ilc_tier0_numeric_surface_inventory_and_risk_classification_632_v0.1.md"
)
DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
TEST_PATH = Path("tests/test_phase_632_tier0_numeric_inventory_and_cdl_064_opening.py")
WALKTHROUGH_PATH = Path(
    "docs/phases/phase_632_g8_tier0_numeric_inventory_and_cdl_064_opening_walkthrough.md"
)
STATUS_PATH = Path("docs/phases/STATUS.md")
PHASE_631_TEST_PATH = Path("tests/test_phase_631_window_631_636_sequence_lock.py")
PHASE_631_SUBJECT_TOKEN = "phase 631 window 631-636 sequence lock"
PHASE_632_SUBJECT_TOKEN = "phase 632 tier0 numeric inventory and cdl-064 opening stub"
PHASE_632_BACKFILL_SUBJECT_TOKEN = "phase 632 walkthrough and status backfill"
EXACT_REQUIRED_MAIN_PATHS = {
    str(INVENTORY_PATH),
    str(TEST_PATH),
    str(DECISION_LOG_PATH),
}
EXACT_REQUIRED_BACKFILL_PATHS = {
    str(WALKTHROUGH_PATH),
    str(STATUS_PATH),
}
REQUIRED_HEADINGS = (
    "## 1. Authorization basis and inventory scope",
    "## 2. Tier-0 surface inventory",
    "## 3. Risk classification",
    "## 4. Migration-class grouping",
    "## 5. CDL-064 opening rationale",
    "## 6. Forward pointer to prelock and simulation",
)
REQUIRED_TOKENS = (
    "tier0_numeric_inventory_632_locked",
    "cdl_064_opened_as_stub",
    "tier0_float_surface_inventory_complete",
    "tier0_risk_classes_defined",
    "tier0_migration_classes_defined",
    "float_retention_not_acceptable_tier0_inventory_conclusion",
    "window_631_636_moves_to_cdl_064_prelock",
)
REQUIRED_PATHS = (
    "`ilc_core/ledger/backend.py`",
    "`ilc_core/ledger/stake_snapshot.py`",
    "`ilc_core/ledger/settlement_verification.py`",
    "`ilc_core/ledger/lmdb_backend.py`",
    "`ilc_core/ledger/persistent_backend.py`",
    "`ilc_core/ledger/ledger_export.py`",
    "`ilc_core/ledger/canon_export.py`",
    "`ilc_core/ledger/ecu_active_layer_runtime.py`",
    "`ilc_core/rc/economic_cycle_runtime.py`",
    "`ilc_core/validator/staking_liveness_runtime.py`",
    "`ilc_core/types.py`",
)
REQUIRED_RISK_CLASS_SNIPPETS = (
    "`R1`: consensus/settlement/economic replay critical",
    "`R2`: runtime-export or validator-state critical",
    "`R3`: adjacent or lower-risk Tier-0 companion",
)
REQUIRED_MIGRATION_CLASS_SNIPPETS = (
    "`M1`: internal state primitive replacement",
    "`M2`: serialization/export contract update",
    "`M3`: validation/tolerance logic replacement",
)
REQUIRED_RATIONALE_SNIPPETS = (
    "machine-legible protocol outputs",
    "replay and settlement verification expectations",
    "persistence and export shapes",
    "cross-language implementation assumptions",
    "what exact representation is canonical for Tier-0 economic values",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _commit_text(path: str, commit_ref: str) -> str:
    result = subprocess.run(
        ["git", "show", f"{commit_ref}:{path}"],
        capture_output=True,
        check=True,
        text=True,
    )
    return result.stdout


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


def test_inventory_document_exists_and_contains_required_headings() -> None:
    text = _read(INVENTORY_PATH)
    for heading in REQUIRED_HEADINGS:
        assert heading in text


def test_inventory_document_contains_all_required_tokens() -> None:
    text = _read(INVENTORY_PATH)
    for token in REQUIRED_TOKENS:
        assert token in text


def test_section_two_inventories_required_tier0_path_classes() -> None:
    text = _read(INVENTORY_PATH)
    for required_path in REQUIRED_PATHS:
        assert required_path in text
    assert "Risk class" in text
    assert "Migration class" in text


def test_section_three_defines_all_risk_classes() -> None:
    text = _read(INVENTORY_PATH)
    for snippet in REQUIRED_RISK_CLASS_SNIPPETS:
        assert snippet in text


def test_section_four_defines_all_migration_classes() -> None:
    text = _read(INVENTORY_PATH)
    for snippet in REQUIRED_MIGRATION_CLASS_SNIPPETS:
        assert snippet in text
    assert "Rows may carry more than one migration class" in text


def test_section_five_explains_why_cdl_064_is_constitutional_vehicle() -> None:
    text = _read(INVENTORY_PATH)
    for snippet in REQUIRED_RATIONALE_SNIPPETS:
        assert snippet in text
    assert "float retention is no longer acceptable" in text


def test_cdl_064_row_exists_in_decision_log_with_expected_open_state() -> None:
    _require_commit_or_skip(PHASE_632_SUBJECT_TOKEN)
    phase_631_ref = _resolve_commit_ref(
        subject_token=PHASE_631_SUBJECT_TOKEN,
        expected_paths={
            "docs/specs/ilc_phase_631_636_sequence_lock_v0.1.md",
            str(PHASE_631_TEST_PATH),
        },
    )
    phase_632_ref = _resolve_commit_ref(
        subject_token=PHASE_632_SUBJECT_TOKEN,
        expected_paths=EXACT_REQUIRED_MAIN_PATHS,
    )
    old_rows = parse_decision_register_rows(_commit_text(str(DECISION_LOG_PATH), phase_631_ref))
    new_rows = parse_decision_register_rows(_commit_text(str(DECISION_LOG_PATH), phase_632_ref))
    assert "CDL-064" not in old_rows
    assert "CDL-064" in new_rows
    assert new_rows["CDL-064"]["status"] == "open"
    assert (
        new_rows["CDL-064"]["related_clause"]
        == "Phase-619 / Phase-630 / Tier-0 runtime numeric determinism"
    )
    assert (
        new_rows["CDL-064"]["decision_topic"]
        == "Canonical economic numeric representation and exact arithmetic boundary for Tier-0 runtime-critical economic, ledger, and staking surfaces"
    )
    assert (
        new_rows["CDL-064"]["options"]
        == "retain-float-rounding-and-tolerance, exact-decimal-runtime-contract, fixed-point-minor-unit-contract"
    )
    assert new_rows["CDL-064"]["current_candidate"] == "open"
    assert (
        new_rows["CDL-064"]["required_artifacts"]
        == "docs/specs/ilc_phase_631_636_sequence_lock_v0.1.md, docs/specs/ilc_tier0_numeric_surface_inventory_and_risk_classification_632_v0.1.md, docs/specs/ilc_cdl_064_exact_numeric_representation_prelock_633_v0.1.md"
    )
    assert "ratified_phase" not in new_rows["CDL-064"]
    assert "ratified_date" not in new_rows["CDL-064"]
    assert "evidence_document" not in new_rows["CDL-064"]
    for cdl_id, old_row in old_rows.items():
        assert new_rows[cdl_id] == old_row


def test_phase_632_main_and_backfill_commits_touch_expected_paths_only() -> None:
    _require_commit_or_skip(PHASE_632_BACKFILL_SUBJECT_TOKEN)
    main_ref = _resolve_commit_ref(
        subject_token=PHASE_632_SUBJECT_TOKEN,
        expected_paths=EXACT_REQUIRED_MAIN_PATHS,
    )
    backfill_ref = _resolve_commit_ref(
        subject_token=PHASE_632_BACKFILL_SUBJECT_TOKEN,
        expected_paths=EXACT_REQUIRED_BACKFILL_PATHS,
    )
    assert _changed_paths_for_commit(main_ref) == EXACT_REQUIRED_MAIN_PATHS
    assert str(DECISION_LOG_PATH) in _changed_paths_for_commit(main_ref)
    assert not any(path.startswith("ilc_core/") for path in _changed_paths_for_commit(main_ref))
    assert _changed_paths_for_commit(backfill_ref) == EXACT_REQUIRED_BACKFILL_PATHS
    assert not any(path.startswith("ilc_core/") for path in _changed_paths_for_commit(backfill_ref))
