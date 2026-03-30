from __future__ import annotations

import subprocess
from pathlib import Path

from ilc_core.epistemic import reuse_centrality_runtime as runtime
from ilc_core.epistemic.node_submission_runtime import EpistemicSubmissionError

RUNTIME_PATH = Path('ilc_core/epistemic/reuse_centrality_runtime.py')
PHASE_478_TEST_PATH = Path('tests/test_phase_478_cdl_052_epistemic_runtime_part_2.py')
TEST_PATH = Path('tests/test_phase_537_reuse_centrality_runtime_algorithm.py')
DECISION_LOG_PATH = Path('docs/specs/ilc_constitutional_decision_log_v0.1.md')
PHASE_537_SUBJECT_TOKEN = 'phase 537 reuse centrality runtime algorithm'
EXACT_REQUIRED_MAIN_PATHS = {
    str(RUNTIME_PATH),
    str(PHASE_478_TEST_PATH),
    str(TEST_PATH),
}


def _read(path: Path) -> str:
    return path.read_text(encoding='utf-8')


def _changed_paths_for_commit(commit_ref: str) -> set[str]:
    result = subprocess.run(
        ['git', 'show', '--name-only', '--pretty=', commit_ref],
        capture_output=True,
        check=True,
        text=True,
    )
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


def _resolve_phase_537_commit_ref() -> str:
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
        if PHASE_537_SUBJECT_TOKEN not in subject.lower():
            continue
        matching.append(commit_hash)
    for commit_ref in matching:
        if _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS:
            return commit_ref
    if matching:
        raise AssertionError('phase_537_commit_subject_present_but_no_qualifying_runtime_commit')
    raise AssertionError('phase_537_commit_not_present_in_local_history')


def _assert_runtime_mutation_scope(commit_ref: str) -> None:
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert 'ilc_core/epistemic/__init__.py' not in changed_paths
    assert str(RUNTIME_PATH) in changed_paths
    assert all(
        path == str(RUNTIME_PATH) or not path.startswith('ilc_core/')
        for path in changed_paths
    )


def test_module_exports_required_constants() -> None:
    assert runtime.REUSE_CENTRALITY_RUNTIME_VERSION == 'reuse_centrality_runtime_537.v0.1'
    assert runtime.CDL_052_DEPENDENCY == 'cdl_052_ratified_466.v0.1'
    assert runtime.U_FLOOR == 0.05
    assert runtime.COMPUTATION_BACKEND_V1 == 'incremental_direct_use_v1'


def test_exact_version_and_dependency_values_are_locked() -> None:
    assert runtime.REUSE_CENTRALITY_RUNTIME_VERSION == 'reuse_centrality_runtime_537.v0.1'
    assert runtime.CDL_052_DEPENDENCY == 'cdl_052_ratified_466.v0.1'


def test_u_floor_and_backend_constants_are_exact() -> None:
    assert runtime.U_FLOOR == 0.05
    assert runtime.COMPUTATION_BACKEND_V1 == 'incremental_direct_use_v1'


def test_query_without_usage_data_is_backward_compatible() -> None:
    result = runtime.query_reuse_centrality({'cid': 'cid-alpha', 'agent_id': 'agent-alpha'})
    assert result.centrality_score == 0.0
    assert result.computation_backend == 'incremental_direct_use_v1'


def test_query_with_usage_data_above_floor_returns_ratio() -> None:
    result = runtime.query_reuse_centrality(
        {
            'cid': 'cid-alpha',
            'agent_id': 'agent-alpha',
            'usage_data': {'direct_use_count': 3, 'total_pool_size': 10},
        }
    )
    assert result.centrality_score == 0.3
    assert result.computation_backend == 'incremental_direct_use_v1'


def test_query_with_usage_data_below_floor_returns_zero() -> None:
    result = runtime.query_reuse_centrality(
        {
            'cid': 'cid-alpha',
            'agent_id': 'agent-alpha',
            'usage_data': {'direct_use_count': 1, 'total_pool_size': 100},
        }
    )
    assert result.centrality_score == 0.0


def test_query_at_u_floor_boundary_is_non_zero() -> None:
    result = runtime.query_reuse_centrality(
        {
            'cid': 'cid-alpha',
            'agent_id': 'agent-alpha',
            'usage_data': {'direct_use_count': 1, 'total_pool_size': 20},
        }
    )
    assert result.centrality_score == 0.05


def test_query_with_malformed_usage_data_raises_submission_error() -> None:
    bad_queries = (
        {
            'cid': 'cid-alpha',
            'agent_id': 'agent-alpha',
            'usage_data': {'direct_use_count': -1, 'total_pool_size': 10},
        },
        {
            'cid': 'cid-alpha',
            'agent_id': 'agent-alpha',
            'usage_data': {'direct_use_count': 1, 'total_pool_size': 0},
        },
        {
            'cid': 'cid-alpha',
            'agent_id': 'agent-alpha',
            'usage_data': {'total_pool_size': 10},
        },
        {
            'cid': 'cid-alpha',
            'agent_id': 'agent-alpha',
            'usage_data': {'direct_use_count': 1},
        },
        {
            'cid': 'cid-alpha',
            'agent_id': 'agent-alpha',
            'usage_data': {'direct_use_count': '1', 'total_pool_size': 10},
        },
        {
            'cid': 'cid-alpha',
            'agent_id': 'agent-alpha',
            'usage_data': {'direct_use_count': 1, 'total_pool_size': True},
        },
    )
    for query in bad_queries:
        try:
            runtime.query_reuse_centrality(query)
        except EpistemicSubmissionError as exc:
            assert exc.token == 'REUSE_CENTRALITY_MALFORMED_QUERY'
        else:
            raise AssertionError('expected malformed usage_data to raise EpistemicSubmissionError')


def test_phase_478_historicalization_comment_is_present() -> None:
    text = _read(PHASE_478_TEST_PATH)
    assert '# The Phase-478 stub_deferred check is a historical prelock reference.' in text


def test_validate_query_preserves_existing_required_fields() -> None:
    for query in ({'agent_id': 'agent-alpha'}, {'cid': 'cid-alpha'}):
        try:
            runtime.validate_epistemic_reuse_centrality_query(query)  # type: ignore[arg-type]
        except EpistemicSubmissionError as exc:
            assert exc.token == 'REUSE_CENTRALITY_MALFORMED_QUERY'
        else:
            raise AssertionError('expected missing field validation error')


def test_runtime_mutation_scope_is_limited_to_runtime_and_tests() -> None:
    commit_ref = _resolve_phase_537_commit_ref()
    _assert_runtime_mutation_scope(commit_ref)


def test_phase_537_commit_resolver_matches_exact_paths() -> None:
    commit_ref = _resolve_phase_537_commit_ref()
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS
