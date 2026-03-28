from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

CONTRACT_PATH = Path('docs/specs/ilc_consensus_diversity_measurement_contract_471_v0.1.md')
TOOL_PATH = Path('tools/consensus_diversity_measurement_471.py')
REPORT_PATH = Path('out/consensus_measurement/phase_471_report.json')
SUMMARY_PATH = Path('out/consensus_measurement/phase_471_summary.md')
DECISION_LOG_PATH = Path('docs/specs/ilc_constitutional_decision_log_v0.1.md')
TEST_PATH = Path('tests/test_phase_471_distributed_degraded_measurement_harness.py')
PHASE_471_SUBJECT_TOKEN = 'phase 471 distributed and degraded-network measurement harness'
EXACT_REQUIRED_MAIN_PATHS = {
    str(TOOL_PATH),
    str(CONTRACT_PATH),
    str(REPORT_PATH),
    str(SUMMARY_PATH),
    str(TEST_PATH),
}
EXPECTED_SCENARIOS = {'local_nominal', 'degraded_latency', 'cross_cluster_loss', 'concentration_edge'}
EXPECTED_SCENARIO_OUTCOMES = {
    'local_nominal': ('finalized', 'finalized', 'diversity_pass'),
    'degraded_latency': ('finalized', 'finalized', 'diversity_pass'),
    'cross_cluster_loss': ('finalized', 'insufficient_diversity', 'diversity_fail'),
    'concentration_edge': ('finalized', 'insufficient_diversity', 'diversity_fail'),
}
FORBIDDEN_TREASURY_TOKEN = 'ILC_CDL_MUTATION_' + 'AUTHORIZED'


def _read(path: Path) -> str:
    return path.read_text(encoding='utf-8')


def _changed_paths_for_commit(commit_ref: str) -> set[str]:
    result = subprocess.run(['git', 'show', '--name-only', '--pretty=', commit_ref], capture_output=True, check=True, text=True)
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


def _resolve_phase_471_commit_ref() -> str:
    result = subprocess.run(['git', 'log', '--format=%H%x09%s'], capture_output=True, check=True, text=True)
    matching: list[str] = []
    for line in result.stdout.splitlines():
        if '\t' not in line:
            continue
        commit_hash, subject = line.split('\t', 1)
        if PHASE_471_SUBJECT_TOKEN not in subject.lower():
            continue
        matching.append(commit_hash)
    for commit_ref in matching:
        if _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS:
            return commit_ref
    if matching:
        raise AssertionError('phase_471_commit_subject_present_but_no_qualifying_measurement_commit')
    raise AssertionError('phase_471_commit_not_present_in_local_history')


def test_contract_artifact_exists_with_required_headings_and_tokens() -> None:
    text = _read(CONTRACT_PATH)
    for heading in (
        '## 1. Harness scope',
        '## 2. Scenario matrix',
        '## 3. Report contract',
        '## 4. Non-goals',
    ):
        assert heading in text
    for token in (
        'Distributed and degraded-network measurement scoping is complete as of Phase 471.',
        'The Phase 471 harness compares flat and diversity-aware finality evaluation under deterministic scenarios.',
        'No decision-log mutation occurred in Phase 471.',
        'Phase 472 is the next authorized phase.',
    ):
        assert token in text


def test_measurement_tool_exists_and_is_runnable(tmp_path: Path) -> None:
    assert TOOL_PATH.exists()
    original_report = REPORT_PATH.read_bytes()
    original_summary = SUMMARY_PATH.read_bytes()
    env = dict(os.environ)
    env['ILC_PHASE_471_REPORT_PATH'] = str(tmp_path / 'phase_471_report.json')
    env['ILC_PHASE_471_SUMMARY_PATH'] = str(tmp_path / 'phase_471_summary.md')
    result = subprocess.run(['python3', str(TOOL_PATH)], capture_output=True, text=True, env=env, check=False)
    assert result.returncode == 0
    assert (tmp_path / 'phase_471_report.json').exists()
    assert (tmp_path / 'phase_471_summary.md').exists()
    assert REPORT_PATH.read_bytes() == original_report
    assert SUMMARY_PATH.read_bytes() == original_summary


def test_report_json_exists_with_all_required_scenarios() -> None:
    report = json.loads(_read(REPORT_PATH))
    indexed = {entry['scenario_name']: entry for entry in report['scenarios']}
    scenario_names = set(indexed)
    assert scenario_names == EXPECTED_SCENARIOS
    for entry in indexed.values():
        expected = EXPECTED_SCENARIO_OUTCOMES[entry['scenario_name']]
        assert entry['legacy']['finality_status'] == expected[0]
        assert entry['diversity']['finality_status'] == expected[1]
        assert entry['diversity']['diversity_status'] == expected[2]
        assert 'scenario_description' in entry
        assert 'aggregate_weights' in entry['legacy']
        assert 'threshold_fraction' in entry['legacy']
        assert 'aggregate_weights' in entry['diversity']
        assert 'threshold_fraction' in entry['diversity']
    assert indexed['local_nominal']['legacy']['aggregate_weights'] == {'block-alpha': 0.75}
    assert indexed['degraded_latency']['legacy']['aggregate_weights'] == {
        'block-alpha': 0.67,
        'block-beta': 0.15,
    }
    assert indexed['cross_cluster_loss']['diversity']['distinct_clusters'] == 1
    assert indexed['cross_cluster_loss']['diversity']['max_cluster_share'] == 1.0


def test_summary_markdown_exists_with_scenario_names_and_timing_keys() -> None:
    text = _read(SUMMARY_PATH)
    for scenario_name in EXPECTED_SCENARIOS:
        assert scenario_name in text
    for key in ('legacy_avg_ms', 'diversity_avg_ms', 'diversity_overhead_ms'):
        assert key in text


def test_diversity_aware_path_is_represented_in_each_scenario_record() -> None:
    report = json.loads(_read(REPORT_PATH))
    for entry in report['scenarios']:
        assert 'legacy' in entry
        assert 'diversity' in entry
        assert 'diversity_status' in entry['diversity']


def test_no_forbidden_treasury_mutation_token_appears() -> None:
    assert FORBIDDEN_TREASURY_TOKEN not in _read(CONTRACT_PATH)
    assert FORBIDDEN_TREASURY_TOKEN not in _read(TEST_PATH)


def test_phase_471_main_commit_touches_expected_paths() -> None:
    commit_ref = _resolve_phase_471_commit_ref()
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS


def test_phase_471_commit_does_not_touch_decision_log_or_ilc_core() -> None:
    commit_ref = _resolve_phase_471_commit_ref()
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert not any(path.startswith('ilc_core/') for path in changed_paths)
