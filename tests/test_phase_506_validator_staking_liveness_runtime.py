from __future__ import annotations

import importlib
import subprocess
from decimal import Decimal
from pathlib import Path

import ilc_core.validator as validator_pkg
from ilc_core.validator import staking_liveness_runtime

MODULE_PATH = Path('ilc_core/validator/staking_liveness_runtime.py')
INIT_PATH = Path('ilc_core/validator/__init__.py')
TEST_PATH = Path('tests/test_phase_506_validator_staking_liveness_runtime.py')
DECISION_LOG_PATH = Path('docs/specs/ilc_constitutional_decision_log_v0.1.md')
PHASE_506_SUBJECT_TOKEN = 'phase 506 cdl-055 validator staking liveness runtime'
EXACT_REQUIRED_MAIN_PATHS = {
    str(INIT_PATH),
    str(MODULE_PATH),
    str(TEST_PATH),
}
FORBIDDEN_TOKEN = 're_admission_boundary'
FORBIDDEN_PREFIXES = (
    'ilc_core/consensus/',
    'ilc_core/security/',
    'ilc_core/ledger/',
    'ilc_core/issuance/',
    'ilc_core/schema/',
    'ilc_core/genesis/',
    'ilc_core/epoch/',
    'ilc_core/d2e/',
    'ilc_core/cli/',
    'ilc_core/identity/',
    'ilc_core/reputation/',
    'ilc_core/network/',
    'ilc_core/node/',
)


def _changed_paths_for_commit(commit_ref: str) -> set[str]:
    result = subprocess.run(
        ['git', 'show', '--name-only', '--pretty=', commit_ref],
        capture_output=True,
        check=True,
        text=True,
    )
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


def _resolve_phase_506_commit_ref() -> str:
    result = subprocess.run(
        ['git', 'log', '--format=%H%x09%s'],
        capture_output=True,
        check=True,
        text=True,
    )
    matching: list[str] = []
    for line in result.stdout.splitlines():
        if '\t' not in line:
            continue
        commit_hash, subject = line.split('\t', 1)
        if PHASE_506_SUBJECT_TOKEN not in subject.lower():
            continue
        matching.append(commit_hash)
    for commit_ref in matching:
        if _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS:
            return commit_ref
    if matching:
        raise AssertionError('phase_506_commit_subject_present_but_no_qualifying_runtime_commit')
    raise AssertionError('phase_506_commit_not_present_in_local_history')


def test_validator_package_and_module_import() -> None:
    importlib.import_module('ilc_core.validator.staking_liveness_runtime')
    assert validator_pkg.STAKING_LIVENESS_RUNTIME_VERSION == 'staking_liveness_runtime_506.v0.1'
    assert validator_pkg.LIVENESS_PENALTY_FRACTION == Decimal("0.25")


def test_runtime_version_constant_value() -> None:
    assert staking_liveness_runtime.STAKING_LIVENESS_RUNTIME_VERSION == 'staking_liveness_runtime_506.v0.1'


def test_dependency_constant_value() -> None:
    assert staking_liveness_runtime.CDL_055_DEPENDENCY == 'cdl_055_ratified_496.v0.1'


def test_genesis_stake_amount_positive() -> None:
    assert staking_liveness_runtime.GENESIS_STAKE_AMOUNT == Decimal("400")
    assert staking_liveness_runtime.GENESIS_STAKE_AMOUNT > 0


def test_liveness_miss_threshold_positive_integer() -> None:
    assert staking_liveness_runtime.LIVENESS_MISS_THRESHOLD == 8
    assert isinstance(staking_liveness_runtime.LIVENESS_MISS_THRESHOLD, int)
    assert staking_liveness_runtime.LIVENESS_MISS_THRESHOLD > 0


def test_penalty_fraction_constants() -> None:
    assert staking_liveness_runtime.EQUIVOCATION_FULL_SLASH == Decimal("1")
    assert staking_liveness_runtime.LIVENESS_PENALTY_FRACTION == Decimal("0.25")


def test_active_state_validation() -> None:
    result = staking_liveness_runtime.validate_staking_and_liveness_state(Decimal("400"), 0, False)
    assert result == {'status': 'active', 'penalty_fraction': '0'}


def test_liveness_penalty_state() -> None:
    result = staking_liveness_runtime.validate_staking_and_liveness_state(Decimal("400"), 8, False)
    assert result == {'status': 'liveness_penalty', 'penalty_fraction': '0.25'}


def test_equivocation_slash_state() -> None:
    result = staking_liveness_runtime.validate_staking_and_liveness_state(Decimal("400"), 0, True)
    assert result == {'status': 'equivocation_slash', 'penalty_fraction': '1'}


def test_validate_staking_and_liveness_state_rejects_invalid_inputs() -> None:
    invalid_cases = (
        ((True, 0, False), 'stake_must_be_positive'),
        ((0.0, 0, False), 'stake_must_be_positive'),
        ((400.0, 0, False), 'stake_must_be_positive'),
        ((Decimal("400"), -1, False), 'consecutive_missed_epochs_must_be_non_negative_int'),
        ((Decimal("400"), 0, 'no'), 'equivocation_state_must_be_bool'),
    )
    for args, expected_token in invalid_cases:
        try:
            staking_liveness_runtime.validate_staking_and_liveness_state(*args)
        except ValueError as exc:
            assert str(exc) == expected_token
        else:
            raise AssertionError(f'expected ValueError for args={args!r}')


def test_validate_staking_and_liveness_state_accepts_exact_string_stake() -> None:
    result = staking_liveness_runtime.validate_staking_and_liveness_state("400", 0, False)
    assert result == {"status": "active", "penalty_fraction": "0"}


def test_forbidden_token_absent_from_module_source() -> None:
    source = MODULE_PATH.read_text(encoding='utf-8')
    assert FORBIDDEN_TOKEN not in source


def test_phase_506_main_commit_touches_expected_paths_only() -> None:
    commit_ref = _resolve_phase_506_commit_ref()
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS


def test_phase_506_main_commit_respects_scope_and_cdl_log() -> None:
    commit_ref = _resolve_phase_506_commit_ref()
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert all(not path.startswith(prefix) for prefix in FORBIDDEN_PREFIXES for path in changed_paths)
