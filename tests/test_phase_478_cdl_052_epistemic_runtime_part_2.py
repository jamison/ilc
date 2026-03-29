from __future__ import annotations

import subprocess
from pathlib import Path

from ilc_core.epistemic import (
    EPISTEMIC_PART1_DEPENDENCY,
    EPISTEMIC_RUNTIME_PART2_VERSION,
    REFUTATION_STAKE_AMOUNT_TBD,
    SUBMISSION_STAKE_AMOUNT_TBD,
    check_novelty,
    query_reuse_centrality,
    validate_epistemic_refutation_submission,
)

HANDOFF_PATH = Path('docs/specs/ilc_cdl_052_epistemic_runtime_part_2_handoff_478_v0.1.md')
REFUTATION_SOURCE_PATH = Path('ilc_core/epistemic/refutation_runtime.py')
TEST_PATH = Path('tests/test_phase_478_cdl_052_epistemic_runtime_part_2.py')
PHASE_478_SUBJECT_TOKEN = 'phase 478 cdl-052 epistemic runtime part 2'
EXACT_REQUIRED_MAIN_PATHS = {
    'ilc_core/epistemic/refutation_runtime.py',
    'ilc_core/epistemic/novelty_check_runtime.py',
    'ilc_core/epistemic/reuse_centrality_runtime.py',
    'ilc_core/epistemic/__init__.py',
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


def _resolve_phase_478_commit_ref() -> str:
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
        if PHASE_478_SUBJECT_TOKEN not in subject.lower():
            continue
        matching.append(commit_hash)
    for commit_ref in matching:
        if _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS:
            return commit_ref
    if matching:
        raise AssertionError('phase_478_commit_subject_present_but_no_qualifying_runtime_commit')
    raise AssertionError('phase_478_commit_not_present_in_local_history')


def test_version_and_dependency_tokens_exist() -> None:
    assert EPISTEMIC_RUNTIME_PART2_VERSION == 'epistemic_refutation_novelty_reuse_runtime_478.v0.1'
    assert EPISTEMIC_PART1_DEPENDENCY == 'epistemic_node_submission_runtime_477.v0.1'


def test_novelty_check_returns_novel_for_new_cid() -> None:
    result = check_novelty({'cid': 'cid-new', 'agent_id': 'agent-alpha'})
    assert result.novel is True
    assert result.duplicate_cid is None
    assert result.failure_token is None


def test_novelty_check_returns_duplicate_token_for_known_duplicate() -> None:
    result = check_novelty({'cid': 'dup-known-cid', 'agent_id': 'agent-alpha'})
    assert result.novel is False
    assert result.failure_token == 'NOVELTY_CHECK_DUPLICATE'


def test_refutation_submission_validates_envelope_structure() -> None:
    validate_epistemic_refutation_submission(
        {
            'target_cid': 'cid-target',
            'agent_id': 'agent-alpha',
            'authored_envelope': {},
            'refutation_criterion': {
                'claim': 'claim-alpha',
                'evidence_type': 'empirical',
                'scope_boundary': 'scope-alpha',
            },
        }
    )


def test_reuse_centrality_query_returns_stub_backend() -> None:
    result = query_reuse_centrality({'cid': 'cid-alpha', 'agent_id': 'agent-alpha'})
    assert result.centrality_score == 0.0
    assert result.computation_backend == 'stub_deferred'


def test_symbolic_stake_constants_and_tbd_markers_exist() -> None:
    source = REFUTATION_SOURCE_PATH.read_text(encoding='utf-8')
    assert SUBMISSION_STAKE_AMOUNT_TBD == 'submission_stake_amount_tbd'
    assert REFUTATION_STAKE_AMOUNT_TBD == 'refutation_stake_amount_tbd'
    assert '# TBD: pending future simulation lane' in source


def test_phase_478_main_commit_touches_expected_paths_and_no_forbidden_paths() -> None:
    commit_ref = _resolve_phase_478_commit_ref()
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert changed_paths == EXACT_REQUIRED_MAIN_PATHS


def test_phase_478_main_commit_does_not_touch_decision_log_or_non_epistemic_ilc_core() -> None:
    commit_ref = _resolve_phase_478_commit_ref()
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert 'docs/specs/ilc_constitutional_decision_log_v0.1.md' not in changed_paths
    assert all(path.startswith('ilc_core/epistemic/') or not path.startswith('ilc_core/') for path in changed_paths)
