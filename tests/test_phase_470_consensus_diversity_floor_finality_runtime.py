from __future__ import annotations

import copy
from decimal import Decimal
import subprocess
from pathlib import Path

from ilc_core.consensus import (
    CDL_V3_DEPENDENCY,
    DIVERSITY_AWARE_FINALITY_VERSION,
    FINALITY_EVALUATOR_VERSION,
    ConsensusFinalityEvaluatorError,
    evaluate_epoch_finality,
    evaluate_epoch_finality_with_diversity,
)
from ilc_core.consensus.epoch_state_runtime import canonical_epoch_state_vectors

INIT_PATH = Path('ilc_core/consensus/__init__.py')
EVALUATOR_PATH = Path('ilc_core/consensus/finality_evaluator.py')
HANDOFF_PATH = Path('docs/specs/ilc_consensus_diversity_floor_finality_runtime_handoff_470_v0.1.md')
PHASE_447_TEST_PATH = Path('tests/test_phase_447_consensus_adversarial_regression.py')
DECISION_LOG_PATH = Path('docs/specs/ilc_constitutional_decision_log_v0.1.md')
PHASE_470_SUBJECT_TOKEN = 'runtime(g8): phase 470 consensus diversity-floor finality runtime'
EXACT_REQUIRED_MAIN_PATHS = {
    str(INIT_PATH),
    str(EVALUATOR_PATH),
    str(HANDOFF_PATH),
    str(Path('tests/test_phase_470_consensus_diversity_floor_finality_runtime.py')),
    str(PHASE_447_TEST_PATH),
}


def _read(path: Path) -> str:
    return path.read_text(encoding='utf-8')


def _changed_paths_for_commit(commit_ref: str) -> set[str]:
    result = subprocess.run(['git', 'show', '--name-only', '--pretty=', commit_ref], capture_output=True, check=True, text=True)
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


def _resolve_phase_470_commit_ref() -> str:
    result = subprocess.run(['git', 'log', '--format=%H%x09%s'], capture_output=True, check=True, text=True)
    matching: list[str] = []
    for line in result.stdout.splitlines():
        if '\t' not in line:
            continue
        commit_hash, subject = line.split('\t', 1)
        if PHASE_470_SUBJECT_TOKEN not in subject.lower():
            continue
        matching.append(commit_hash)
    for commit_ref in matching:
        if _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS:
            return commit_ref
    if matching:
        raise AssertionError('phase_470_commit_subject_present_but_no_qualifying_runtime_commit')
    raise AssertionError('phase_470_commit_not_present_in_local_history')


def test_runtime_exports_and_handoff_artifact_exist() -> None:
    text = _read(HANDOFF_PATH)
    assert INIT_PATH.exists()
    assert EVALUATOR_PATH.exists()
    assert DIVERSITY_AWARE_FINALITY_VERSION == 'finality_diversity_floor_runtime_470.v0.1'
    assert FINALITY_EVALUATOR_VERSION == 'finality_evaluator_445.v0.1'
    assert CDL_V3_DEPENDENCY == 'cdl_v3_diversity_floor_397.v0.1'
    for heading in (
        '## 1. Phase 470 runtime scope summary',
        '## 2. Ratified constitutional anchors',
        '## 3. Diversity-aware finality evaluation contract',
        '## 4. Deterministic failure-token catalog',
        '## 5. Historicalization boundary',
        '## 6. Non-goals and Phase 471 pointer',
    ):
        assert heading in text


def test_legacy_two_argument_finality_evaluation_behavior_remains_unchanged() -> None:
    quorum_records = [
        {'block_hash': 'block-a', 'epoch_index': 9, 'vote_weight': Decimal('0.45')},
        {'block_hash': 'block-a', 'epoch_index': 9, 'vote_weight': Decimal('0.30')},
        {'block_hash': 'block-b', 'epoch_index': 9, 'vote_weight': Decimal('0.10')},
    ]
    threshold = {'numerator': 2, 'denominator': 3}
    result = evaluate_epoch_finality(copy.deepcopy(quorum_records), threshold)
    assert result['finality_status'] == 'finalized'
    assert result['canonical_block_hash'] == 'block-a'
    assert result['runtime_version'] == 'finality_evaluator_445.v0.1'


def test_diversity_aware_evaluation_finalizes_when_quorum_and_diversity_both_pass() -> None:
    vector = canonical_epoch_state_vectors()[0]
    records = copy.deepcopy(vector['quorum_records'])
    records[0]['validator_id'] = 'validator-a'
    records[1]['validator_id'] = 'validator-b'
    result = evaluate_epoch_finality_with_diversity(
        records,
        {'numerator': 2, 'denominator': 3},
        {'validator-a': 'cluster-1', 'validator-b': 'cluster-2'},
        {'distinct_cluster_floor': 2, 'max_cluster_share_ceiling': 0.60},
    )
    assert result['finality_status'] == 'finalized'
    assert result['canonical_block_hash'] == 'block-alpha'
    assert result['diversity_status'] == 'diversity_pass'
    assert result['distinct_clusters'] == 2


def test_diversity_aware_evaluation_returns_insufficient_diversity_when_diversity_fails() -> None:
    vector = canonical_epoch_state_vectors()[0]
    records = copy.deepcopy(vector['quorum_records'])
    records[0]['validator_id'] = 'validator-a'
    records[1]['validator_id'] = 'validator-b'
    result = evaluate_epoch_finality_with_diversity(
        records,
        {'numerator': 2, 'denominator': 3},
        {'validator-a': 'cluster-1', 'validator-b': 'cluster-1'},
        {'distinct_cluster_floor': 2, 'max_cluster_share_ceiling': 0.60},
    )
    assert result['finality_status'] == 'insufficient_diversity'
    assert result['canonical_block_hash'] is None
    assert result['diversity_status'] == 'diversity_fail'


def test_missing_cluster_metadata_or_policy_raises_deterministic_tokens() -> None:
    vector = canonical_epoch_state_vectors()[0]
    records = copy.deepcopy(vector['quorum_records'])
    with_missing_validator = copy.deepcopy(records)
    with_missing_validator[0].pop('validator_id', None)
    try:
        evaluate_epoch_finality_with_diversity(
            with_missing_validator,
            {'numerator': 2, 'denominator': 3},
            {'validator-a': 'cluster-1'},
            {'distinct_cluster_floor': 2, 'max_cluster_share_ceiling': 0.60},
        )
    except ConsensusFinalityEvaluatorError as exc:
        assert exc.token == 'consensus_diversity_finality_validator_id_missing'
    else:
        raise AssertionError('expected_validator_id_missing_error')

    records[0]['validator_id'] = 'validator-a'
    records[1]['validator_id'] = 'validator-b'
    try:
        evaluate_epoch_finality_with_diversity(
            records,
            {'numerator': 2, 'denominator': 3},
            {'validator-a': 'cluster-1'},
            {'distinct_cluster_floor': 2, 'max_cluster_share_ceiling': 0.60},
        )
    except ConsensusFinalityEvaluatorError as exc:
        assert exc.token == 'consensus_diversity_finality_validator_cluster_missing'
    else:
        raise AssertionError('expected_validator_cluster_missing_error')


def test_phase_447_test_file_is_historicalized_against_its_commit_snapshot() -> None:
    text = _read(PHASE_447_TEST_PATH)
    assert 'def _evaluator_text_at_ref(ref: str) -> str:' in text
    assert 'historical_evaluator_text = _evaluator_text_at_ref(_resolve_phase_447_commit_ref())' in text
    assert 'assert "diversity_floor_runtime" not in historical_evaluator_text' in text


def test_phase_470_main_commit_touches_expected_paths() -> None:
    commit_ref = _resolve_phase_470_commit_ref()
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS


def test_phase_470_commit_does_not_mutate_decision_log_or_non_consensus_runtime_paths() -> None:
    commit_ref = _resolve_phase_470_commit_ref()
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert not any(path.startswith('ilc_core/') and not path.startswith('ilc_core/consensus/') for path in changed_paths)
