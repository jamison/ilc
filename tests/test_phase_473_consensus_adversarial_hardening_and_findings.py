from __future__ import annotations

import json
import subprocess
from pathlib import Path

from ilc_core.consensus.finality_evaluator import ConsensusFinalityEvaluatorError, evaluate_epoch_finality_with_diversity
from ilc_core.consensus.epoch_state_runtime import canonical_epoch_state_vectors

FINDINGS_PATH = Path('docs/specs/ilc_consensus_adversarial_hardening_findings_473_v0.1.md')
MEASUREMENT_REPORT_PATH = Path('out/consensus_measurement/phase_471_report.json')
BRIDGE_REPORT_PATH = Path('out/consensus_bridge/phase_472_report.json')
DECISION_LOG_PATH = Path('docs/specs/ilc_constitutional_decision_log_v0.1.md')
TEST_PATH = Path('tests/test_phase_473_consensus_adversarial_hardening_and_findings.py')
PHASE_473_SUBJECT_TOKEN = 'phase 473 consensus adversarial hardening and findings memo'
EXACT_REQUIRED_MAIN_PATHS = {
    str(FINDINGS_PATH),
    str(TEST_PATH),
}


def _read(path: Path) -> str:
    return path.read_text(encoding='utf-8')


def _changed_paths_for_commit(commit_ref: str) -> set[str]:
    result = subprocess.run(['git', 'show', '--name-only', '--pretty=', commit_ref], capture_output=True, check=True, text=True)
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


def _resolve_phase_473_commit_ref() -> str:
    result = subprocess.run(['git', 'log', '--format=%H%x09%s'], capture_output=True, check=True, text=True)
    matching: list[str] = []
    for line in result.stdout.splitlines():
        if '\t' not in line:
            continue
        commit_hash, subject = line.split('\t', 1)
        if PHASE_473_SUBJECT_TOKEN not in subject.lower():
            continue
        matching.append(commit_hash)
    for commit_ref in matching:
        if _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS:
            return commit_ref
    if matching:
        raise AssertionError('phase_473_commit_subject_present_but_no_qualifying_findings_commit')
    raise AssertionError('phase_473_commit_not_present_in_local_history')


def test_findings_memo_headings_and_tokens() -> None:
    text = _read(FINDINGS_PATH)
    for heading in (
        '## 1. Executive summary',
        '## 2. Closed adversarial cases',
        '## 3. Remaining open risks',
        '## 4. Governance-priority rule',
        '## 5. Phase 474 pointer',
    ):
        assert heading in text
    for token in (
        'Consensus adversarial hardening is complete as of Phase 473.',
        'Semantics, diversity, and auditability outrank micro-benchmark gains.',
        'No decision-log mutation occurred in Phase 473.',
        'Phase 474 is the next authorized phase.',
    ):
        assert token in text


def test_measurement_report_and_bridge_report_are_referenced_by_presence() -> None:
    assert MEASUREMENT_REPORT_PATH.exists()
    assert BRIDGE_REPORT_PATH.exists()
    assert json.loads(_read(MEASUREMENT_REPORT_PATH))['phase'] == 471
    assert json.loads(_read(BRIDGE_REPORT_PATH))['phase'] == 472


def test_diversity_aware_insufficient_diversity_case_remains_covered() -> None:
    vector = canonical_epoch_state_vectors()[0]
    records = [dict(item) for item in vector['quorum_records']]
    records[0]['validator_id'] = 'validator-a'
    records[1]['validator_id'] = 'validator-b'
    result = evaluate_epoch_finality_with_diversity(
        records,
        {'numerator': 2, 'denominator': 3},
        {'validator-a': 'cluster-x', 'validator-b': 'cluster-x'},
        {'distinct_cluster_floor': 2, 'max_cluster_share_ceiling': 0.60},
    )
    assert result['finality_status'] == 'insufficient_diversity'


def test_malformed_cluster_map_case_is_covered() -> None:
    vector = canonical_epoch_state_vectors()[0]
    records = [dict(item) for item in vector['quorum_records']]
    records[0]['validator_id'] = 'validator-a'
    records[1]['validator_id'] = 'validator-b'
    try:
        evaluate_epoch_finality_with_diversity(
            records,
            {'numerator': 2, 'denominator': 3},
            {'validator-a': 'cluster-x'},
            {'distinct_cluster_floor': 2, 'max_cluster_share_ceiling': 0.60},
        )
    except ConsensusFinalityEvaluatorError as exc:
        assert exc.token == 'consensus_diversity_finality_validator_cluster_missing'
    else:
        raise AssertionError('expected_validator_cluster_missing_error')


def test_reordered_and_duplicate_bridge_cases_are_covered() -> None:
    report = json.loads(_read(BRIDGE_REPORT_PATH))
    indexed = {entry['case_name']: entry for entry in report['cases']}
    assert indexed['reordered_delivery']['determinism_preserved'] is True
    assert indexed['duplicate_delivery']['determinism_preserved'] is True


def test_governance_priority_token_is_present() -> None:
    assert 'Semantics, diversity, and auditability outrank micro-benchmark gains.' in _read(FINDINGS_PATH)


def test_phase_473_main_commit_touches_expected_paths() -> None:
    commit_ref = _resolve_phase_473_commit_ref()
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS


def test_phase_473_commit_does_not_touch_decision_log_tools_or_ilc_core() -> None:
    commit_ref = _resolve_phase_473_commit_ref()
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert not any(path.startswith('tools/') for path in changed_paths)
    assert not any(path.startswith('ilc_core/') for path in changed_paths)
