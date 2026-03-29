from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

TOOL_PATH = Path('tools/run_sim_010_validator_incentive_economics.py')
OUTPUT_DIR = Path('out/sim_010/phase_487')
MANIFEST_PATH = OUTPUT_DIR / 'run_manifest.json'
RESULTS_PATH = OUTPUT_DIR / 'results.csv'
SUMMARY_PATH = OUTPUT_DIR / 'summary_table.md'
EVIDENCE_PATH = Path('docs/specs/ilc_sim_010_validator_incentive_economics_evidence_package_487_v0.1.md')
SYNTHESIS_PATH = Path('docs/specs/ilc_sim_010_validator_incentive_economics_synthesis_487_v0.1.md')
TEST_PATH = Path('tests/test_phase_487_sim_010_validator_incentive_economics_execution_and_evidence.py')
PHASE_487_SUBJECT_TOKEN = 'phase 487 sim-010 validator incentive economics execution and evidence'
EXACT_REQUIRED_MAIN_PATHS = {
    str(TOOL_PATH),
    str(MANIFEST_PATH),
    str(RESULTS_PATH),
    str(SUMMARY_PATH),
    str(EVIDENCE_PATH),
    str(SYNTHESIS_PATH),
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


def _resolve_phase_487_commit_ref() -> str:
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
        if PHASE_487_SUBJECT_TOKEN not in subject.lower():
            continue
        matching.append(commit_hash)
    for commit_ref in matching:
        if _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS:
            return commit_ref
    if matching:
        raise AssertionError('phase_487_commit_subject_present_but_no_qualifying_execution_commit')
    raise AssertionError('phase_487_commit_not_present_in_local_history')


def test_tool_exists_and_is_runnable_with_override_dir(tmp_path: Path) -> None:
    env = dict(os.environ)
    env['ILC_SIM_010_OUTPUT_DIR'] = str(tmp_path)
    result = subprocess.run(['python3', str(TOOL_PATH)], capture_output=True, text=True, env=env)
    assert result.returncode == 0
    assert (tmp_path / 'run_manifest.json').exists()
    assert (tmp_path / 'results.csv').exists()
    assert (tmp_path / 'summary_table.md').exists()


def test_execution_outputs_exist_at_canonical_paths() -> None:
    assert MANIFEST_PATH.exists()
    assert RESULTS_PATH.exists()
    assert SUMMARY_PATH.exists()
    manifest = json.loads(_read(MANIFEST_PATH))
    assert manifest['verdict'] == 'pass'


def test_evidence_and_synthesis_documents_contain_required_outputs() -> None:
    evidence = _read(EVIDENCE_PATH)
    synthesis = _read(SYNTHESIS_PATH)
    for token in (
        'recommended_validator_reward_fraction',
        'recommended_genesis_stake_amount',
        'recommended_liveness_miss_threshold',
        'SIM-010 verdict: pass',
    ):
        assert token in evidence or token in synthesis
    assert 'SIM-010 verdict: pass' in synthesis


def test_results_cover_all_four_scenarios() -> None:
    text = _read(RESULTS_PATH)
    for scenario in (
        'reward_fraction_scan',
        'staking_sizing',
        'liveness_threshold_sensitivity',
        'participation_equilibrium',
    ):
        assert scenario in text


def test_summary_table_records_recommendations() -> None:
    text = _read(SUMMARY_PATH)
    assert 'recommended_validator_reward_fraction: 0.02' in text
    assert 'recommended_genesis_stake_amount: 400.0' in text
    assert 'recommended_liveness_miss_threshold: 8' in text


def test_phase_487_main_commit_snapshot_touches_expected_paths_only() -> None:
    commit_ref = _resolve_phase_487_commit_ref()
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert changed_paths == EXACT_REQUIRED_MAIN_PATHS


def test_phase_487_main_commit_does_not_touch_ilc_core_or_decision_log() -> None:
    commit_ref = _resolve_phase_487_commit_ref()
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert 'docs/specs/ilc_constitutional_decision_log_v0.1.md' not in changed_paths
    assert not any(path.startswith('ilc_core/') for path in changed_paths)


def test_synthesis_authorizes_constitutional_follow_on() -> None:
    text = _read(SYNTHESIS_PATH)
    assert 'authorizes the validator economic and staking lanes to proceed' in text
