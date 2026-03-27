from __future__ import annotations

import csv
import json
import subprocess
from pathlib import Path

ARTIFACT_EVIDENCE = Path('docs/specs/ilc_treasury_sim_t_waggle_oscillator_hybrid_contrast_evidence_package_459_post3_v0.1.md')
ARTIFACT_SYNTHESIS = Path('docs/specs/ilc_treasury_sim_t_waggle_oscillator_hybrid_contrast_comparative_synthesis_459_post3_v0.1.md')
ARTIFACT_REASSESS = Path('docs/specs/ilc_cdl_050_blocker_1_post_window_hybrid_reassessment_459_post3_v0.1.md')
MANIFEST_PATH = Path('out/treasury_sim/phase_459_post3/run_manifest.json')
CSV_PATH = Path('out/treasury_sim/phase_459_post3/scenario_5_results.csv')
TSV_PATH = Path('out/treasury_sim/phase_459_post3/scenario_5_results.tsv')
SUMMARY_PATH = Path('out/treasury_sim/phase_459_post3/summary_table.md')
WALKTHROUGH_PATH = Path('docs/phases/phase_459_post3_g8_waggle_oscillator_hybrid_contrast_execution_and_post_window_blocker_reassessment_walkthrough.md')
STATUS_PATH = Path('docs/phases/STATUS.md')
TEST_PATH = Path('tests/test_phase_459_post3_waggle_oscillator_hybrid_contrast_execution_and_post_window_blocker_reassessment.py')
PHASE_459_POST3_SUBJECT_TOKEN = 'phase 459 post3 hybrid contrast execution and blocker reassessment'
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
LEADER = 'hybrid_nonlinear_curve_k58_g18_f22_frontier_first_p5_a09_enforce_first_rq100_ab100_dc060_cp095_ss160_rb050_bs150_adj100'
ORG_BRA = 'hybrid_nonlinear_curve_k85_g06_f06_uniform_p7_a13_release_first_rq085_ab115_dc075_cp105_ss200_rb065_bs080_adj120'
CLAMP_BRA = 'hybrid_nonlinear_curve_k85_g35_f44_backpressure_first_p7_a13_release_first_rq085_ab115_dc075_cp105_ss200_rb065_bs080_adj120'
REQUIRED_TOKENS = (
    'Window 450-459 remains closed.',
    'CDL-050 remains ratified.',
    'CDL-051 remains ratified.',
    'Outcome B - Post-window hybrid evidence closes Blocker 1',
    'blocker_1_post_window_hybrid_verdict=cleared',
    f'Field leader: {LEADER}',
    f'Organic best remaining alternative: {ORG_BRA}',
    f'Clamp best remaining alternative: {CLAMP_BRA}',
    'No constitutional record is amended by Phase 459 Post3.',
    'Post-window hybrid evidence does not mutate or supersede the ratified Window 450-459 record by itself.',
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


def _resolve_phase_459_post3_commit_ref() -> str:
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
        if PHASE_459_POST3_SUBJECT_TOKEN not in subject.lower():
            continue
        matching.append(commit_hash)

    for commit_ref in matching:
        if _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS:
            return commit_ref

    if matching:
        raise AssertionError('phase_459_post3_commit_subject_present_but_no_qualifying_hybrid_execution_commit')
    raise AssertionError('phase_459_post3_commit_not_present_in_local_history')


def test_evidence_synthesis_and_reassessment_artifacts_contain_required_tokens() -> None:
    text = '\n'.join((_read(ARTIFACT_EVIDENCE), _read(ARTIFACT_SYNTHESIS), _read(ARTIFACT_REASSESS)))
    for token in REQUIRED_TOKENS:
        assert token in text


def test_manifest_records_expected_field_and_gap_values() -> None:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding='utf-8'))
    assert manifest['leader'] == LEADER
    assert manifest['organic_best_remaining_alternative'] == ORG_BRA
    assert manifest['clamp_best_remaining_alternative'] == CLAMP_BRA
    assert manifest['organic_gap_pp'] == 12.6
    assert manifest['clamp_gap_pp'] == 7.7


def test_csv_and_tsv_results_exist_and_cover_all_frozen_candidates() -> None:
    with CSV_PATH.open(encoding='utf-8', newline='') as f:
        csv_rows = list(csv.DictReader(f))
    with TSV_PATH.open(encoding='utf-8', newline='') as f:
        tsv_rows = list(csv.DictReader(f, delimiter='\t'))
    assert len(csv_rows) == 5
    assert len(tsv_rows) == 5
    ids = {row['candidate_id'] for row in csv_rows}
    assert LEADER in ids and ORG_BRA in ids and CLAMP_BRA in ids and 'mixed_queue_and_production' in ids


def test_summary_table_records_leader_bras_and_gap_values() -> None:
    text = _read(SUMMARY_PATH)
    assert f'Field leader: `{LEADER}`' in text
    assert f'Organic best remaining alternative: `{ORG_BRA}`' in text
    assert f'Clamp best remaining alternative: `{CLAMP_BRA}`' in text
    assert 'Organic gap: 12.6pp' in text
    assert 'Clamp gap: 7.7pp' in text


def test_walkthrough_and_status_record_post_window_boundary_and_next_pointer() -> None:
    walkthrough = _read(WALKTHROUGH_PATH)
    status = _read(STATUS_PATH)
    assert 'Window 450-459 remains closed.' in walkthrough
    assert 'CDL-050 remains ratified and unchanged.' in walkthrough
    assert 'CDL-051 remains ratified and unchanged.' in walkthrough
    assert 'Scenario-5 execution used only the Post2 frozen contrast field.' in walkthrough
    assert 'No decision-log mutation occurred.' in walkthrough
    assert '## Phase 459 Post3' in status
    assert 'HYBRID_CODENAME=Waggle-Oscillator Hybrid' in status
    assert 'Phase 460 — Window 460-468 sequence lock and CDL-052 scope freeze' in status


def test_reassessment_records_conservative_per_dimension_bra_evaluation() -> None:
    text = _read(ARTIFACT_SYNTHESIS) + '\n' + _read(ARTIFACT_REASSESS)
    assert 'conservative per-dimension BRA evaluation' in text
    assert '12.6pp' in text
    assert '7.7pp' in text


def test_phase_459_post3_commit_touches_exact_required_paths() -> None:
    commit_ref = _resolve_phase_459_post3_commit_ref()
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert changed_paths == EXACT_REQUIRED_MAIN_PATHS
    assert not any(path.startswith('docs/specs/ilc_constitutional_decision_log') for path in changed_paths)
    assert not any(path.startswith('ilc_core/') for path in changed_paths)


def test_phase_459_post3_commit_subject_is_present_in_local_history() -> None:
    assert _resolve_phase_459_post3_commit_ref()
