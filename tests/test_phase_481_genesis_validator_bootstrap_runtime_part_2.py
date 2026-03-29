from __future__ import annotations

import base64
import hashlib
import subprocess
from pathlib import Path

from ilc_core.genesis.admission_control_bootstrap import (
    CDL_040_DEPENDENCY,
    GENESIS_BOOTSTRAP_PART1_DEPENDENCY,
    GENESIS_BOOTSTRAP_PART2_VERSION,
    build_genesis_admission_control_bundle,
    enforce_genesis_admission,
    verify_admission_control_bundle,
)
from ilc_core.genesis.validator_bootstrap_runtime import (
    GENESIS_BOOTSTRAP_VERSION,
    GenesisBootstrapError,
    generate_validator_enrollment_record,
    materialize_epoch_zero_state,
)

HANDOFF_PATH = Path('docs/specs/ilc_genesis_validator_bootstrap_runtime_part_2_handoff_481_v0.1.md')
TEST_PATH = Path('tests/test_phase_481_genesis_validator_bootstrap_runtime_part_2.py')
PHASE_481_SUBJECT_TOKEN = 'phase 481 genesis validator bootstrap runtime part 2'
EXACT_REQUIRED_MAIN_PATHS = {
    'ilc_core/genesis/admission_control_bootstrap.py',
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


def _resolve_phase_481_commit_ref() -> str:
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
        if PHASE_481_SUBJECT_TOKEN not in subject.lower():
            continue
        matching.append(commit_hash)
    for commit_ref in matching:
        if _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS:
            return commit_ref
    if matching:
        raise AssertionError('phase_481_commit_subject_present_but_no_qualifying_runtime_commit')
    raise AssertionError('phase_481_commit_not_present_in_local_history')


def _public_key_b64url(byte_value: int) -> str:
    return base64.urlsafe_b64encode(bytes([byte_value]) * 32).decode('ascii').rstrip('=')


def _bundle() -> tuple[dict, str]:
    record = generate_validator_enrollment_record(
        public_key_b64url=_public_key_b64url(1),
        cluster_id='cluster-a',
        vote_weight=1,
        enrolled_by='genesis-authority',
        display_name='validator-a',
    )
    state = materialize_epoch_zero_state('block-alpha', [record])
    return build_genesis_admission_control_bundle([record], state), record['validator_id']


def test_version_and_dependency_tokens_exist() -> None:
    assert GENESIS_BOOTSTRAP_PART2_VERSION == 'genesis_admission_control_bootstrap_481.v0.1'
    assert GENESIS_BOOTSTRAP_PART1_DEPENDENCY == 'genesis_validator_bootstrap_runtime_480.v0.1'
    assert CDL_040_DEPENDENCY == 'cdl_040_ratified_393.v0.1'
    assert GENESIS_BOOTSTRAP_PART1_DEPENDENCY == GENESIS_BOOTSTRAP_VERSION


def test_build_genesis_admission_control_bundle_produces_integrity_hash() -> None:
    bundle, validator_id = _bundle()
    assert isinstance(bundle['bundle_integrity_hash'], str) and bundle['bundle_integrity_hash']
    assert bundle['admitted_validator_ids'] == [validator_id]


def test_verify_admission_control_bundle_raises_when_hash_or_epoch_state_mismatched() -> None:
    bundle, _ = _bundle()
    bundle['bundle_integrity_hash'] = 'deadbeef'
    try:
        verify_admission_control_bundle(bundle)
    except GenesisBootstrapError as exc:
        assert exc.token == 'ADMISSION_BUNDLE_HASH_MISMATCH'
    else:
        raise AssertionError('expected_hash_mismatch_error')
    bundle, _ = _bundle()
    bundle['epoch_zero_state'] = dict(bundle['epoch_zero_state'])
    bundle['epoch_zero_state']['validator_set_hash'] = 'deadbeef'
    bundle['epoch_zero_state']['quorum_record_seed'] = hashlib.sha256(
        f"{bundle['epoch_zero_state']['genesis_block_cid']}:deadbeef".encode('utf-8')
    ).hexdigest()
    try:
        verify_admission_control_bundle(bundle)
    except GenesisBootstrapError as exc:
        assert exc.token == 'ADMISSION_BUNDLE_EPOCH_STATE_MISMATCH'
    else:
        raise AssertionError('expected_epoch_state_mismatch_error')


def test_enforce_genesis_admission_returns_true_for_enrolled_validator_id() -> None:
    bundle, validator_id = _bundle()
    assert enforce_genesis_admission(validator_id, bundle) is True


def test_enforce_genesis_admission_returns_false_for_unenrolled_validator_id() -> None:
    bundle, _ = _bundle()
    unknown_record = generate_validator_enrollment_record(
        public_key_b64url=_public_key_b64url(2),
        cluster_id='cluster-b',
        vote_weight=1,
        enrolled_by='genesis-authority',
        display_name='validator-b',
    )
    assert enforce_genesis_admission(unknown_record['validator_id'], bundle) is False


def test_enforce_genesis_admission_raises_for_none_bundle() -> None:
    try:
        enforce_genesis_admission('validator-alpha', None)
    except GenesisBootstrapError as exc:
        assert exc.token == 'ADMISSION_BUNDLE_NOT_INITIALIZED'
    else:
        raise AssertionError('expected_not_initialized_error')


def test_phase_481_main_commit_touches_expected_paths_and_only_genesis_package() -> None:
    commit_ref = _resolve_phase_481_commit_ref()
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert changed_paths == EXACT_REQUIRED_MAIN_PATHS


def test_phase_481_main_commit_does_not_touch_decision_log_or_non_genesis_ilc_core() -> None:
    commit_ref = _resolve_phase_481_commit_ref()
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert 'docs/specs/ilc_constitutional_decision_log_v0.1.md' not in changed_paths
    assert all(path.startswith('ilc_core/genesis/') or not path.startswith('ilc_core/') for path in changed_paths)
