from __future__ import annotations

import subprocess
from pathlib import Path

from ilc_core.consensus import (
    CDL_045_DEPENDENCY,
    CDL_051_RATIFICATION_DEPENDENCY,
    CIRCUIT_BREAKER_INTERFACE_VERSION,
    CircuitBreakerInterfaceError,
    build_circuit_breaker_request,
    summarize_circuit_breaker_quorum_state,
    verify_circuit_breaker_request,
)

RUNTIME_PATH = Path('ilc_core/consensus/circuit_breaker_interface.py')
INIT_PATH = Path('ilc_core/consensus/__init__.py')
HANDOFF_PATH = Path('docs/specs/ilc_cdl_045_validator_circuit_breaker_surface_handoff_488_v0.1.md')
TEST_PATH = Path('tests/test_phase_488_cdl_045_validator_circuit_breaker_surface_runtime.py')
PHASE_488_SUBJECT_TOKEN = 'phase 488 cdl-045 validator circuit-breaker surface runtime'
EXACT_REQUIRED_MAIN_PATHS = {
    str(RUNTIME_PATH),
    str(INIT_PATH),
    str(HANDOFF_PATH),
    str(TEST_PATH),
}


def _votes() -> list[dict[str, object]]:
    return [
        {'validator_id': 'v1', 'cluster_id': 'a', 'vote_weight': 1.0, 'circuit_breaker_requested': True},
        {'validator_id': 'v2', 'cluster_id': 'b', 'vote_weight': 1.0, 'circuit_breaker_requested': True},
        {'validator_id': 'v3', 'cluster_id': 'b', 'vote_weight': 1.0, 'circuit_breaker_requested': True},
        {'validator_id': 'v4', 'cluster_id': 'c', 'vote_weight': 1.0, 'circuit_breaker_requested': True},
    ]


def _changed_paths_for_commit(commit_ref: str) -> set[str]:
    result = subprocess.run(
        ['git', 'show', '--name-only', '--pretty=', commit_ref],
        capture_output=True,
        check=True,
        text=True,
    )
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


def _resolve_phase_488_commit_ref() -> str:
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
        if PHASE_488_SUBJECT_TOKEN not in subject.lower():
            continue
        matching.append(commit_hash)
    for commit_ref in matching:
        if _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS:
            return commit_ref
    if matching:
        raise AssertionError('phase_488_commit_subject_present_but_no_qualifying_runtime_commit')
    raise AssertionError('phase_488_commit_not_present_in_local_history')


def test_runtime_surface_exports_dependency_tokens() -> None:
    assert CDL_045_DEPENDENCY == 'cdl_045_operational_emergency_response_408.v0.1'
    assert CDL_051_RATIFICATION_DEPENDENCY == 'cdl_051_constitutional_consensus_and_epoch_finality_443.v0.1'
    assert CIRCUIT_BREAKER_INTERFACE_VERSION == 'validator_circuit_breaker_surface_488.v0.1'


def test_quorum_summary_marks_valid_request_as_eligible() -> None:
    summary = summarize_circuit_breaker_quorum_state(_votes())
    assert summary['quorum_ok'] is True
    assert summary['distinct_ok'] is True
    assert summary['share_ok'] is True
    assert summary['eligible'] is True


def test_request_builder_and_verifier_accept_valid_request() -> None:
    request = build_circuit_breaker_request(
        epoch=8,
        canonical_block_hash='block-488',
        reason='clustered finality degradation',
        validator_votes=_votes(),
    )
    assert request['request_status'] == 'eligible'
    verify_circuit_breaker_request(request)


def test_handoff_contains_required_tokens() -> None:
    text = HANDOFF_PATH.read_text(encoding='utf-8')
    for token in (
        'CDL-045 already authorizes the circuit-breaker surface.',
        'No decision-log mutation occurs in Phase 488.',
        'Phase 489 is the next authorized phase.',
    ):
        assert token in text


def test_duplicate_validator_vote_is_rejected() -> None:
    invalid_votes = _votes() + [
        {'validator_id': 'v1', 'cluster_id': 'c', 'vote_weight': 1.0, 'circuit_breaker_requested': True}
    ]
    try:
        summarize_circuit_breaker_quorum_state(invalid_votes)
    except CircuitBreakerInterfaceError as exc:
        assert exc.token == 'circuit_breaker_duplicate_validator'
    else:
        raise AssertionError('expected CircuitBreakerInterfaceError for duplicate validator vote')


def test_runtime_file_exists_and_is_reexported() -> None:
    assert RUNTIME_PATH.exists()
    text = INIT_PATH.read_text(encoding='utf-8')
    assert 'from .circuit_breaker_interface import (' in text
    assert 'build_circuit_breaker_request' in text


def test_phase_488_main_commit_snapshot_touches_expected_paths_only() -> None:
    commit_ref = _resolve_phase_488_commit_ref()
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert changed_paths == EXACT_REQUIRED_MAIN_PATHS


def test_phase_488_main_commit_only_mutates_consensus_runtime_scope() -> None:
    commit_ref = _resolve_phase_488_commit_ref()
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert 'docs/specs/ilc_constitutional_decision_log_v0.1.md' not in changed_paths
    assert all(path.startswith('ilc_core/consensus/') or path.startswith('docs/specs/') or path.startswith('tests/') for path in changed_paths)
