from __future__ import annotations

import subprocess
from pathlib import Path

from ilc_core.epistemic import aesthetic_panel_runtime as runtime

RUNTIME_PATH = Path('ilc_core/epistemic/aesthetic_panel_runtime.py')
DECISION_LOG_PATH = Path('docs/specs/ilc_constitutional_decision_log_v0.1.md')
TEST_PATH = Path('tests/test_phase_532_aesthetic_panel_runtime.py')
PHASE_532_SUBJECT_TOKEN = 'phase 532 cdl-059 aesthetic panel runtime'
EXACT_REQUIRED_MAIN_PATHS = {
    str(RUNTIME_PATH),
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


def _resolve_phase_532_commit_ref() -> str:
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
        if PHASE_532_SUBJECT_TOKEN not in subject.lower():
            continue
        matching.append(commit_hash)
    for commit_ref in matching:
        if _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS:
            return commit_ref
    if matching:
        raise AssertionError('phase_532_commit_subject_present_but_no_qualifying_runtime_commit')
    raise AssertionError('phase_532_commit_not_present_in_local_history')


def _assert_runtime_mutation_scope(commit_ref: str) -> None:
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert changed_paths == EXACT_REQUIRED_MAIN_PATHS
    assert 'ilc_core/epistemic/__init__.py' not in changed_paths


def test_module_exports_required_constants_and_functions() -> None:
    assert hasattr(runtime, 'AESTHETIC_PANEL_RUNTIME_VERSION')
    assert hasattr(runtime, 'CDL_059_DEPENDENCY')
    assert hasattr(runtime, 'BLOCKING_AUTHORITY_ACTIVE')
    assert hasattr(runtime, 'compose_aesthetic_panel')
    assert hasattr(runtime, 'compute_aesthetic_score')
    assert hasattr(runtime, 'format_transparency_label')
    assert hasattr(runtime, 'is_blocking_authority_active')


def test_version_and_dependency_tokens_are_exact() -> None:
    assert runtime.AESTHETIC_PANEL_RUNTIME_VERSION == 'aesthetic_panel_runtime_532.v0.1'
    assert runtime.CDL_059_DEPENDENCY == 'cdl_059_ratified_531.v0.1'


def test_blocking_authority_is_hard_locked_false() -> None:
    assert runtime.BLOCKING_AUTHORITY_ACTIVE is False
    assert runtime.is_blocking_authority_active() is False


def test_compose_aesthetic_panel_selects_panel_from_diverse_pool() -> None:
    pool = [
        {'agent_id': 'a1', 'model_type': 'm1'},
        {'agent_id': 'a2', 'model_type': 'm2'},
        {'agent_id': 'a3', 'model_type': 'm3'},
        {'agent_id': 'a4', 'model_type': 'm1'},
    ]
    selected = runtime.compose_aesthetic_panel(pool, 3, seed=7)
    assert len(selected) == 3
    assert len(set(selected)) == 3
    assert set(selected).issubset({'a1', 'a2', 'a3', 'a4'})


def test_compose_aesthetic_panel_maximizes_model_type_diversity() -> None:
    pool = [
        {'agent_id': 'a1', 'model_type': 'm1'},
        {'agent_id': 'a2', 'model_type': 'm1'},
        {'agent_id': 'b1', 'model_type': 'm2'},
        {'agent_id': 'b2', 'model_type': 'm2'},
        {'agent_id': 'c1', 'model_type': 'm3'},
        {'agent_id': 'c2', 'model_type': 'm3'},
    ]
    selected = runtime.compose_aesthetic_panel(pool, 4, seed=11)
    type_map = {item['agent_id']: item['model_type'] for item in pool}
    selected_types = [type_map[agent_id] for agent_id in selected]
    assert len(set(selected_types)) == 3
    assert max(selected_types.count(model_type) for model_type in set(selected_types)) <= 2


def test_compose_aesthetic_panel_raises_for_insufficient_pool() -> None:
    pool = [{'agent_id': 'a1', 'model_type': 'm1'}]
    try:
        runtime.compose_aesthetic_panel(pool, 2)
    except ValueError as exc:
        assert str(exc) == 'insufficient_agent_pool_size'
    else:
        raise AssertionError('expected ValueError for insufficient pool size')


def test_compose_aesthetic_panel_raises_for_missing_required_keys() -> None:
    pool = [{'agent_id': 'a1'}, {'agent_id': 'a2', 'model_type': 'm2'}]
    try:
        runtime.compose_aesthetic_panel(pool, 1)
    except ValueError as exc:
        assert str(exc) == 'agent_pool_entries_require_agent_id_and_model_type'
    else:
        raise AssertionError('expected ValueError for missing keys')


def test_compose_aesthetic_panel_rejects_duplicate_agent_ids() -> None:
    pool = [
        {'agent_id': 'a1', 'model_type': 'm1'},
        {'agent_id': 'a1', 'model_type': 'm2'},
    ]
    try:
        runtime.compose_aesthetic_panel(pool, 1)
    except ValueError as exc:
        assert str(exc) == 'duplicate_agent_id_in_pool'
    else:
        raise AssertionError('expected ValueError for duplicate agent ids')


def test_compute_aesthetic_score_returns_mean_and_rejects_empty_votes() -> None:
    assert runtime.compute_aesthetic_score([0.25, 0.75]) == 0.5
    try:
        runtime.compute_aesthetic_score([])
    except ValueError as exc:
        assert str(exc) == 'votes_must_be_non_empty'
    else:
        raise AssertionError('expected ValueError for empty votes')


def test_format_transparency_label_returns_required_fields() -> None:
    label = runtime.format_transparency_label(0.6)
    assert label['panel_type'] == 'digital_agent_aesthetic_consensus'
    assert label['not_objective_truth'] is True
    assert label['score'] == 0.6


def test_format_transparency_label_rejects_out_of_range_score() -> None:
    try:
        runtime.format_transparency_label(1.2)
    except ValueError as exc:
        assert str(exc) == 'score_out_of_range'
    else:
        raise AssertionError('expected ValueError for out-of-range score')


def test_runtime_mutation_scope_is_limited_to_runtime_and_test() -> None:
    commit_ref = _resolve_phase_532_commit_ref()
    _assert_runtime_mutation_scope(commit_ref)


def test_phase_532_commit_resolver_matches_exact_paths() -> None:
    commit_ref = _resolve_phase_532_commit_ref()
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS
