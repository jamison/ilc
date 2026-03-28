from __future__ import annotations

import json
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


def test_measurement_tool_exists_and_is_runnable() -> None:
    assert TOOL_PATH.exists()
    result = subprocess.run(['python3', str(TOOL_PATH)], capture_output=True, text=True, check=False)
    assert result.returncode == 0


def test_report_json_exists_with_all_required_scenarios() -> None:
    report = json.loads(_read(REPORT_PATH))
    scenario_names = {entry['scenario_name'] for entry in report['scenarios']}
    assert scenario_names == EXPECTED_SCENARIOS


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
