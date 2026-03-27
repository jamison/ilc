from __future__ import annotations

import csv
import json
import subprocess
from pathlib import Path

ARTIFACT_EVIDENCE = Path('docs/specs/ilc_treasury_sim_t_local_hysteretic_oscillator_evidence_package_459_post5_v0.1.md')
ARTIFACT_SYNTHESIS = Path('docs/specs/ilc_treasury_sim_t_local_hysteretic_oscillator_comparative_synthesis_459_post5_v0.1.md')
ARTIFACT_REASSESS = Path('docs/specs/ilc_cdl_050_blocker_1_post_window_local_reassessment_459_post5_v0.1.md')
MANIFEST_PATH = Path('out/treasury_sim/phase_459_post5/run_manifest.json')
CSV_PATH = Path('out/treasury_sim/phase_459_post5/scenario_5_results.csv')
TSV_PATH = Path('out/treasury_sim/phase_459_post5/scenario_5_results.tsv')
SUMMARY_PATH = Path('out/treasury_sim/phase_459_post5/summary_table.md')
WALKTHROUGH_PATH = Path('docs/phases/phase_459_post5_g8_local_hysteretic_oscillator_execution_and_post_window_blocker_reassessment_walkthrough.md')
STATUS_PATH = Path('docs/phases/STATUS.md')
TEST_PATH = Path('tests/test_phase_459_post5_local_hysteretic_oscillator_execution_and_post_window_blocker_reassessment.py')
PHASE_459_POST5_SUBJECT_TOKEN = 'phase 459 post5 local execution and blocker reassessment'
EXACT_REQUIRED_MAIN_PATHS = {
    str(ARTIFACT_EVIDENCE),
    str(ARTIFACT_SYNTHESIS),
    str(ARTIFACT_REASSESS),
    str(MANIFEST_PATH),
    str(CSV_PATH),
    str(TSV_PATH),
    str(SUMMARY_PATH),
    str(TEST_PATH),
    str(WALKTHROUGH_PATH),
    str(STATUS_PATH),
}
LEADER = 'local_hysteretic_oscillator_t65_l45_g11_f12_e1_r2'
BRA = 'local_hysteretic_oscillator_t55_l30_g15_f04_e1_r4'
REQUIRED_TOKENS = (
    'Window 450-459 remains closed.',
    'CDL-050 remains ratified.',
    'CDL-051 remains ratified.',
    'Outcome B - Post-window local evidence closes Blocker 1',
    'blocker_1_post_window_local_verdict=cleared',
    f'Field leader: {LEADER}',
    f'Organic best remaining alternative: {BRA}',
    f'Clamp best remaining alternative: {BRA}',
    'Bounded randomized graph jumping is excluded from the default local rule.',
    'No constitutional record is amended by Phase 459 Post5.',
    'Post-window local evidence does not mutate or supersede the ratified Window 450-459 record by itself.',
)


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


def _resolve_phase_459_post5_commit_ref() -> str:
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
        if PHASE_459_POST5_SUBJECT_TOKEN not in subject.lower():
            continue
        matching.append(commit_hash)

    for commit_ref in matching:
        if _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS:
            return commit_ref

    if matching:
        raise AssertionError('phase_459_post5_commit_subject_present_but_no_qualifying_local_execution_commit')
    raise AssertionError('phase_459_post5_commit_not_present_in_local_history')


def test_evidence_synthesis_and_reassessment_artifacts_contain_required_tokens() -> None:
    text = '\n'.join((_read(ARTIFACT_EVIDENCE), _read(ARTIFACT_SYNTHESIS), _read(ARTIFACT_REASSESS)))
    for token in REQUIRED_TOKENS:
        assert token in text


def test_manifest_records_expected_field_and_gap_values() -> None:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding='utf-8'))
    assert manifest['leader'] == LEADER
    assert manifest['organic_best_remaining_alternative'] == BRA
    assert manifest['clamp_best_remaining_alternative'] == BRA
    assert manifest['organic_gap_pp'] == 11.2
    assert manifest['clamp_gap_pp'] == 5.8


def test_csv_and_tsv_results_exist_and_cover_all_frozen_candidates() -> None:
    with CSV_PATH.open(encoding='utf-8', newline='') as f:
        csv_rows = list(csv.DictReader(f))
    with TSV_PATH.open(encoding='utf-8', newline='') as f:
        tsv_rows = list(csv.DictReader(f, delimiter='\t'))
    assert len(csv_rows) == 5
    assert len(tsv_rows) == 5
    ids = {row['candidate_id'] for row in csv_rows}
    assert LEADER in ids and BRA in ids and 'mixed_queue_and_production' in ids


def test_summary_table_records_leader_bra_and_gap_values() -> None:
    text = _read(SUMMARY_PATH)
    assert f'Field leader: `{LEADER}`' in text
    assert f'Organic best remaining alternative: `{BRA}`' in text
    assert f'Clamp best remaining alternative: `{BRA}`' in text
    assert 'Organic gap: 11.2pp' in text
    assert 'Clamp gap: 5.8pp' in text


def test_walkthrough_and_status_record_post_window_boundary_and_next_pointer() -> None:
    walkthrough = _read(WALKTHROUGH_PATH)
    status = _read(STATUS_PATH)
    assert 'Window 450-459 remains closed.' in walkthrough
    assert 'CDL-050 remains ratified and unchanged.' in walkthrough
    assert 'CDL-051 remains ratified and unchanged.' in walkthrough
    assert 'Scenario-5 execution used only the Post4 frozen local field.' in walkthrough
    assert 'No decision-log mutation occurred.' in walkthrough
    assert 'Randomized nonlocal graph jumping is excluded from the default local rule.' in walkthrough
    assert '## Phase 459 Post5' in status
    assert 'LOCAL_CODENAME=Shard Thermostat' in status
    assert 'Phase 460 - Window 460-468 sequence lock and CDL-052 scope freeze' in status


def test_reassessment_records_conservative_per_dimension_bra_evaluation() -> None:
    text = _read(ARTIFACT_SYNTHESIS) + '\n' + _read(ARTIFACT_REASSESS)
    assert 'Conservative per-dimension BRA evaluation' in text
    assert '11.2pp' in text
    assert '5.8pp' in text


def test_phase_459_post5_commit_touches_exact_required_paths() -> None:
    commit_ref = _resolve_phase_459_post5_commit_ref()
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert changed_paths == EXACT_REQUIRED_MAIN_PATHS
    assert not any(path.startswith('docs/specs/ilc_constitutional_decision_log') for path in changed_paths)
    assert not any(path.startswith('ilc_core/') for path in changed_paths)


def test_phase_459_post5_commit_subject_is_present_in_local_history() -> None:
    assert _resolve_phase_459_post5_commit_ref()
