from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

SPEC_PATH = Path("docs/specs/ilc_tier0_exact_numeric_runtime_migration_635_v0.1.md")
TEST_PATH = Path("tests/test_phase_635_tier0_exact_numeric_runtime_migration.py")
WALKTHROUGH_PATH = Path(
    "docs/phases/phase_635_g8_tier0_exact_numeric_runtime_migration_walkthrough.md"
)
STATUS_PATH = Path("docs/phases/STATUS.md")
DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
PHASE_635_SUBJECT_TOKEN = "phase 635 tier0 exact numeric runtime migration"
PHASE_635_BACKFILL_SUBJECT_TOKEN = "phase 635 walkthrough and status backfill"
REQUIRED_HEADINGS = (
    "## 1. Ratified dependency and migration target",
    "## 2. Tier-0 modules migrated",
    "## 3. Exact arithmetic and serialization implementation",
    "## 4. Removed float/tolerance surfaces",
    "## 5. Verification and residual defers",
)
REQUIRED_TOKENS = (
    "tier0_exact_numeric_runtime_migration_635_locked",
    "cdl_064_dependency_consumed",
    "tier0_internal_float_accounting_removed",
    "tier0_tolerance_equality_removed",
    "tier0_exact_serialization_runtime_applied",
    "tier0_runtime_migration_verification_defined",
    "window_631_636_moves_to_numeric_hardening_gate",
)
MIGRATED_MODULES = (
    "ilc_core/ledger/exact_numeric.py",
    "ilc_core/ledger/backend.py",
    "ilc_core/ledger/stake_snapshot.py",
    "ilc_core/ledger/settlement_verification.py",
    "ilc_core/ledger/ledger_export.py",
    "ilc_core/ledger/canon_export.py",
    "ilc_core/ledger/lmdb_backend.py",
    "ilc_core/ledger/persistent_backend.py",
    "ilc_core/rc/economic_cycle_runtime.py",
    "ilc_core/validator/staking_liveness_runtime.py",
    "ilc_core/protocol/event_log.py",
    "ilc_core/protocol/schemas/commit_epoch_event_schema_v0.1.json",
    "tools/query_rc0_1_economic_state.py",
    "tools/check_rc0_1_economic_state.py",
    "tools/testbed/run_economic_negative_path_drills.py",
    "tools/testbed/run_economic_replay_drills.py",
)
LEGACY_FLOAT_PATTERNS = {
    "ilc_core/ledger/backend.py": (
        "self.balances: dict[str, float] = {}",
        'rewards = float(payload["summary"]["reward_total"])',
        "reward_value = summary.get(\"reward_total\", 0.0)",
    ),
    "ilc_core/ledger/stake_snapshot.py": (
        "stakes: Dict[str, float]",
        "total_stake: float",
        "1e-9",
    ),
    "ilc_core/ledger/settlement_verification.py": (
        "eps = 1e-6",
        "abs(total_delta - expected_total) <= eps",
        "float(summary.get(\"reward_total\", 0.0))",
    ),
    "ilc_core/rc/economic_cycle_runtime.py": (
        "claim_totals: dict[str, float] = {}",
        "round(sum(claim_totals.values()), 12)",
        "abs(reward_total - float(rewards_paid)) > 1e-9",
        "row[\"ecu_claim_total\"] = round(float(row[\"ecu_claim_total\"]) + float(amount), 12)",
        "\"balance_ilc\": round(float(balance), 12)",
        "\"reward_delta_ilc\": round(float(row[\"ecu_claim_total\"]), 12)",
    ),
    "ilc_core/validator/staking_liveness_runtime.py": (
        "GENESIS_STAKE_AMOUNT = 400.0",
        "EQUIVOCATION_FULL_SLASH = 1.0",
        "LIVENESS_PENALTY_FRACTION = 0.25",
    ),
}
TOLERANCE_REMOVAL_TARGETS = {
    "ilc_core/ledger/stake_snapshot.py",
    "ilc_core/ledger/settlement_verification.py",
    "ilc_core/rc/economic_cycle_runtime.py",
}
FORBIDDEN_TOLERANCE_SNIPPETS = ("1e-9", "1e-6", "epsilon", "round(..., 12)")


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


def _require_commit_or_skip(subject_token: str) -> None:
    if _find_commit_ref(subject_token=subject_token) is None:
        pytest.skip(f"commit_not_yet_present:{subject_token}")


def test_runtime_migration_spec_exists_and_contains_required_headings() -> None:
    text = _read(SPEC_PATH)
    for heading in REQUIRED_HEADINGS:
        assert heading in text


def test_runtime_migration_spec_contains_required_tokens() -> None:
    text = _read(SPEC_PATH)
    for token in REQUIRED_TOKENS:
        assert token in text


def test_migrated_tier0_implementation_removes_known_legacy_float_accounting_patterns() -> None:
    for path_str, legacy_patterns in LEGACY_FLOAT_PATTERNS.items():
        text = _read(Path(path_str))
        for legacy_pattern in legacy_patterns:
            assert legacy_pattern not in text, f"legacy_float_pattern_present:{path_str}:{legacy_pattern}"


def test_migrated_settlement_correctness_files_no_longer_use_tolerance_equality() -> None:
    for path_str in sorted(TOLERANCE_REMOVAL_TARGETS):
        text = _read(Path(path_str))
        assert "1e-9" not in text
        assert "1e-6" not in text
        assert "epsilon" not in text.lower()
        assert "round(sum(claim_totals.values()), 12)" not in text


def test_runtime_migration_spec_section_two_names_all_migrated_modules() -> None:
    text = _read(SPEC_PATH)
    for module_path in MIGRATED_MODULES:
        assert f"- `{module_path}`" in text


def test_runtime_migration_spec_section_three_states_canonical_serialization_rule() -> None:
    text = _read(SPEC_PATH)
    assert "exact numeric values serialize as normalized base-10 decimal strings" in text
    assert "no exponent notation" in text
    assert "no negative zero" in text
    assert "trailing fractional zeros stripped" in text
    assert "integral values serialized without a trailing decimal point" in text


def test_phase_635_main_commit_touches_spec_test_and_runtime_paths_without_decision_log_or_adr_mutation() -> None:
    _require_commit_or_skip(PHASE_635_SUBJECT_TOKEN)
    commit_ref = _find_commit_ref(subject_token=PHASE_635_SUBJECT_TOKEN)
    assert commit_ref is not None
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert str(SPEC_PATH) in changed_paths
    assert str(TEST_PATH) in changed_paths
    assert any(path.startswith("ilc_core/") for path in changed_paths)
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert not any(path.startswith("docs/adr/") for path in changed_paths)


def test_phase_635_backfill_commit_touches_walkthrough_and_status_only() -> None:
    _require_commit_or_skip(PHASE_635_BACKFILL_SUBJECT_TOKEN)
    commit_ref = _find_commit_ref(subject_token=PHASE_635_BACKFILL_SUBJECT_TOKEN)
    assert commit_ref is not None
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert changed_paths == {str(WALKTHROUGH_PATH), str(STATUS_PATH)}
