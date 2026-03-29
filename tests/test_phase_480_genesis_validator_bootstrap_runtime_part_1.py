from __future__ import annotations

import base64
import subprocess
from pathlib import Path

from ilc_core.consensus.finality_evaluator import CDL_051_RATIFICATION_DEPENDENCY as SOURCE_CDL_051
from ilc_core.genesis.validator_bootstrap_runtime import (
    CDL_042_DEPENDENCY,
    CDL_051_RATIFICATION_DEPENDENCY,
    GENESIS_BOOTSTRAP_VERSION,
    GenesisBootstrapError,
    generate_validator_enrollment_record,
    materialize_epoch_zero_state,
    verify_epoch_zero_state,
    verify_genesis_enrollment,
)
from ilc_core.identity.agent_id_runtime import CDL_042_DEPENDENCY as SOURCE_CDL_042, derive_agent_id

HANDOFF_PATH = Path('docs/specs/ilc_genesis_validator_bootstrap_runtime_handoff_480_v0.1.md')
TEST_PATH = Path('tests/test_phase_480_genesis_validator_bootstrap_runtime_part_1.py')
PHASE_480_SUBJECT_TOKEN = 'phase 480 genesis validator bootstrap runtime part 1'
EXACT_REQUIRED_MAIN_PATHS = {
    'ilc_core/genesis/validator_bootstrap_runtime.py',
    'ilc_core/genesis/__init__.py',
    str(HANDOFF_PATH),
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


def _resolve_phase_480_commit_ref() -> str:
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
        if PHASE_480_SUBJECT_TOKEN not in subject.lower():
            continue
        matching.append(commit_hash)
    for commit_ref in matching:
        if _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS:
            return commit_ref
    if matching:
        raise AssertionError('phase_480_commit_subject_present_but_no_qualifying_runtime_commit')
    raise AssertionError('phase_480_commit_not_present_in_local_history')


def _public_key_b64url() -> str:
    return base64.urlsafe_b64encode(b'\x01' * 32).decode('ascii').rstrip('=')


def _enrollment_record() -> dict:
    return generate_validator_enrollment_record(
        public_key_b64url=_public_key_b64url(),
        cluster_id='cluster-a',
        vote_weight=1,
        enrolled_by='genesis-authority',
        display_name='validator-a',
    )


def test_version_and_dependency_tokens_match_source_modules() -> None:
    assert GENESIS_BOOTSTRAP_VERSION == 'genesis_validator_bootstrap_runtime_480.v0.1'
    assert CDL_051_RATIFICATION_DEPENDENCY == SOURCE_CDL_051
    assert CDL_042_DEPENDENCY == SOURCE_CDL_042


def test_generate_validator_enrollment_record_produces_required_fields() -> None:
    record = _enrollment_record()
    for field in (
        'validator_id',
        'public_key_b64url',
        'cluster_id',
        'vote_weight',
        'epoch_zero',
        'enrolled_by',
    ):
        assert field in record


def test_generate_validator_enrollment_record_delegates_validator_id_to_derive_agent_id() -> None:
    record = _enrollment_record()
    public_key_bytes = base64.urlsafe_b64decode(_public_key_b64url() + '==')
    assert record['validator_id'] == derive_agent_id(public_key_bytes)


def test_verify_genesis_enrollment_raises_for_missing_required_fields() -> None:
    record = _enrollment_record()
    del record['cluster_id']
    try:
        verify_genesis_enrollment(record)
    except GenesisBootstrapError as exc:
        assert exc.token == 'GENESIS_BOOTSTRAP_MISSING_REQUIRED_FIELD'
    else:
        raise AssertionError('expected_missing_required_field_error')


def test_materialize_epoch_zero_state_produces_deterministic_epoch_zero_record() -> None:
    state = materialize_epoch_zero_state('block-alpha', [_enrollment_record()])
    assert state['epoch'] == 0
    assert isinstance(state['validator_set_hash'], str) and state['validator_set_hash']
    assert isinstance(state['quorum_record_seed'], str) and state['quorum_record_seed']


def test_verify_epoch_zero_state_raises_for_non_zero_epoch_missing_seed_or_invalid_derivation() -> None:
    state = materialize_epoch_zero_state('block-alpha', [_enrollment_record()])
    bad_epoch = dict(state)
    bad_epoch['epoch'] = 1
    try:
        verify_epoch_zero_state(bad_epoch)
    except GenesisBootstrapError as exc:
        assert exc.token == 'GENESIS_BOOTSTRAP_INVALID_EPOCH_STATE'
    else:
        raise AssertionError('expected_invalid_epoch_error')
    missing_seed = dict(state)
    del missing_seed['quorum_record_seed']
    try:
        verify_epoch_zero_state(missing_seed)
    except GenesisBootstrapError as exc:
        assert exc.token == 'GENESIS_BOOTSTRAP_MISSING_REQUIRED_FIELD'
    else:
        raise AssertionError('expected_missing_seed_error')
    invalid_seed = dict(state)
    invalid_seed['quorum_record_seed'] = 'deadbeef'
    try:
        verify_epoch_zero_state(invalid_seed)
    except GenesisBootstrapError as exc:
        assert exc.token == 'GENESIS_BOOTSTRAP_INVALID_EPOCH_STATE'
    else:
        raise AssertionError('expected_invalid_seed_derivation_error')


def test_phase_480_main_commit_touches_expected_paths_and_only_genesis_package() -> None:
    commit_ref = _resolve_phase_480_commit_ref()
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert changed_paths == EXACT_REQUIRED_MAIN_PATHS


def test_phase_480_main_commit_does_not_touch_decision_log_or_non_genesis_ilc_core() -> None:
    commit_ref = _resolve_phase_480_commit_ref()
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert 'docs/specs/ilc_constitutional_decision_log_v0.1.md' not in changed_paths
    assert all(path.startswith('ilc_core/genesis/') or not path.startswith('ilc_core/') for path in changed_paths)
