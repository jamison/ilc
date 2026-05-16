from __future__ import annotations

import importlib
import subprocess
from pathlib import Path

import ilc_core.epoch as epoch_pkg
from ilc_core.validator import staking_liveness_runtime
from ilc_core.epoch import epoch_boundary_witness_runtime

MODULE_PATH = Path('ilc_core/epoch/epoch_boundary_witness_runtime.py')
TEST_PATH = Path('tests/test_phase_516_epoch_boundary_witness_runtime.py')
DECISION_LOG_PATH = Path('docs/specs/ilc_constitutional_decision_log_v0.1.md')
PHASE_516_SUBJECT_TOKEN = 'phase 516 cdl-057 epoch boundary witness runtime'
EXACT_REQUIRED_MAIN_PATHS = {
    str(MODULE_PATH),
    str(TEST_PATH),
}


def _changed_paths_for_commit(commit_ref: str) -> set[str]:
    result = subprocess.run(
        ['git', 'show', '--name-only', '--pretty=', commit_ref],
        capture_output=True,
        check=True,
        text=True,
    )
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


def _resolve_phase_516_commit_ref() -> str:
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
        if PHASE_516_SUBJECT_TOKEN not in subject.lower():
            continue
        matching.append(commit_hash)
    for commit_ref in matching:
        if _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS:
            return commit_ref
    if matching:
        raise AssertionError('phase_516_commit_subject_present_but_no_qualifying_runtime_commit')
    raise AssertionError('phase_516_commit_not_present_in_local_history')


def test_module_imports() -> None:
    module = importlib.import_module('ilc_core.epoch.epoch_boundary_witness_runtime')
    assert module.EPOCH_BOUNDARY_WITNESS_RUNTIME_VERSION == 'epoch_boundary_witness_blocking_active_phase_1364.v0.1'


def test_runtime_version_constant_value() -> None:
    assert (
        epoch_boundary_witness_runtime.EPOCH_BOUNDARY_WITNESS_RUNTIME_VERSION
        == 'epoch_boundary_witness_blocking_active_phase_1364.v0.1'
    )


def test_cdl_057_dependency_constant_value() -> None:
    assert epoch_boundary_witness_runtime.CDL_057_DEPENDENCY == 'cdl_057_ratified_511.v0.1'


def test_cdl_055_staking_dependency_chain() -> None:
    assert (
        epoch_boundary_witness_runtime.CDL_055_STAKING_DEPENDENCY
        == staking_liveness_runtime.STAKING_LIVENESS_RUNTIME_VERSION
    )


def test_blocking_authority_deferred_is_false_after_phase_1364() -> None:
    assert epoch_boundary_witness_runtime.BLOCKING_AUTHORITY_DEFERRED is False


def test_is_blocking_authority_active_is_true_after_phase_1364() -> None:
    assert epoch_boundary_witness_runtime.is_blocking_authority_active() is True


def test_record_epoch_boundary_witness_returns_expected_payload() -> None:
    assert epoch_boundary_witness_runtime.record_epoch_boundary_witness('validator-1', '42', 'cid-1') == {
        'status': 'witnessed',
        'batch_cid': 'cid-1',
        'provenance_tag': 'validator-1@epoch_42',
    }


def test_record_epoch_boundary_witness_accepts_integer_epoch_id() -> None:
    assert epoch_boundary_witness_runtime.record_epoch_boundary_witness('validator-1', 42, 'cid-1') == {
        'status': 'witnessed',
        'batch_cid': 'cid-1',
        'provenance_tag': 'validator-1@epoch_42',
    }


def test_record_epoch_boundary_witness_rejects_empty_validator_id() -> None:
    try:
        epoch_boundary_witness_runtime.record_epoch_boundary_witness('', '42', 'cid-1')
    except ValueError as exc:
        assert str(exc) == 'validator_id_must_be_non_empty_string'
    else:
        raise AssertionError('expected ValueError for empty validator_id')


def test_record_epoch_boundary_witness_rejects_empty_epoch_id() -> None:
    try:
        epoch_boundary_witness_runtime.record_epoch_boundary_witness('validator-1', '', 'cid-1')
    except ValueError as exc:
        assert str(exc) == 'epoch_id_must_be_non_empty_string'
    else:
        raise AssertionError('expected ValueError for empty epoch_id')


def test_record_epoch_boundary_witness_rejects_non_numeric_epoch_id() -> None:
    try:
        epoch_boundary_witness_runtime.record_epoch_boundary_witness('validator-1', 'not-a-number', 'cid-1')
    except ValueError as exc:
        assert str(exc) == 'epoch_id_must_be_non_negative_int_or_digit_string'
    else:
        raise AssertionError('expected ValueError for non-numeric epoch_id')


def test_record_epoch_boundary_witness_rejects_empty_batch_cid() -> None:
    try:
        epoch_boundary_witness_runtime.record_epoch_boundary_witness('validator-1', '42', '')
    except ValueError as exc:
        assert str(exc) == 'batch_cid_must_be_non_empty_string'
    else:
        raise AssertionError('expected ValueError for empty batch_cid')


def test_phase_516_main_commit_touches_expected_paths_only() -> None:
    commit_ref = _resolve_phase_516_commit_ref()
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS


def test_phase_516_main_commit_respects_scope_and_cdl_log() -> None:
    commit_ref = _resolve_phase_516_commit_ref()
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert 'ilc_core/epoch/epoch_snapshot_runtime.py' not in changed_paths
    assert 'ilc_core/epoch/__init__.py' not in changed_paths


def test_epoch_package_re_exports_witness_runtime_surface() -> None:
    assert epoch_pkg.EPOCH_BOUNDARY_WITNESS_RUNTIME_VERSION == 'epoch_boundary_witness_blocking_active_phase_1364.v0.1'
    assert epoch_pkg.CDL_057_DEPENDENCY == 'cdl_057_ratified_511.v0.1'
    assert epoch_pkg.BLOCKING_AUTHORITY_DEFERRED is False
    assert epoch_pkg.is_blocking_authority_active() is True
    assert epoch_pkg.record_epoch_boundary_witness('validator-1', '42', 'cid-1') == {
        'status': 'witnessed',
        'batch_cid': 'cid-1',
        'provenance_tag': 'validator-1@epoch_42',
    }
