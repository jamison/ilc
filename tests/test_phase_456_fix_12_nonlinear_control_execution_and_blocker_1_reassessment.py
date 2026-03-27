from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

from ilc_core.testing.ratification_mutation_scope_guardrail import (
    assert_head_commit_touched_no_runtime_files,
    parse_decision_register_rows,
)

EVIDENCE_PATH = Path('docs/specs/ilc_treasury_sim_t_nonlinear_control_evidence_package_456_fix_12_v0.1.md')
SYNTHESIS_PATH = Path('docs/specs/ilc_treasury_sim_t_nonlinear_control_comparative_synthesis_456_fix_12_v0.1.md')
REASSESSMENT_PATH = Path('docs/specs/ilc_cdl_050_blocker_1_reassessment_456_fix_12_v0.1.md')
MANIFEST_PATH = Path('out/treasury_sim/phase_456_fix_12/run_manifest.json')
CSV_PATH = Path('out/treasury_sim/phase_456_fix_12/scenario_5_results.csv')
TSV_PATH = Path('out/treasury_sim/phase_456_fix_12/scenario_5_results.tsv')
SUMMARY_PATH = Path('out/treasury_sim/phase_456_fix_12/summary_table.md')
TEST_PATH = Path('tests/test_phase_456_fix_12_nonlinear_control_execution_and_blocker_1_reassessment.py')
WALKTHROUGH_PATH = Path('docs/phases/phase_456_fix_12_g8_nonlinear_control_execution_walkthrough.md')
STATUS_PATH = Path('docs/phases/STATUS.md')
DECISION_LOG_PATH = Path('docs/specs/ilc_constitutional_decision_log_v0.1.md')
PHASE_SUBJECT = 'docs(g8): phase 456 fix 12 nonlinear-control execution comparative synthesis and blocker-1 reassessment'
FORBIDDEN_TREASURY_TOKEN = 'ILC_CDL_MUTATION_' + 'AUTHORIZED'
EXACT_REQUIRED_PATHS = {
    str(EVIDENCE_PATH),
    str(SYNTHESIS_PATH),
    str(REASSESSMENT_PATH),
    str(MANIFEST_PATH),
    str(CSV_PATH),
    str(TSV_PATH),
    str(SUMMARY_PATH),
    str(TEST_PATH),
    str(WALKTHROUGH_PATH),
    str(STATUS_PATH),
}
REQUIRED_FILE_PATHS = (
    EVIDENCE_PATH,
    SYNTHESIS_PATH,
    REASSESSMENT_PATH,
    MANIFEST_PATH,
    CSV_PATH,
    TSV_PATH,
    SUMMARY_PATH,
    TEST_PATH,
    WALKTHROUGH_PATH,
    STATUS_PATH,
)
CANDIDATES = (
    'nonlinear_curve_k56_g18_f22_frontier_first',
    'nonlinear_curve_k58_g18_f22_frontier_first',
    'nonlinear_curve_k60_g18_f22_frontier_first',
    'mixed_queue_and_production',
)


def _read(path: Path) -> str:
    return path.read_text(encoding='utf-8')


def _section_body(text: str, heading: str) -> str:
    escaped = re.escape(heading)
    match = re.search(rf'{escaped}\n\n(.*?)(?=\n## |\Z)', text, flags=re.S)
    if not match:
        raise AssertionError(f'section_not_found:{heading}')
    return match.group(1).strip()


def _changed_paths_for_commit(commit_ref: str) -> set[str]:
    result = subprocess.run(['git', 'show', '--name-only', '--pretty=', commit_ref], capture_output=True, check=True, text=True)
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


def _read_file_at_ref(ref: str, path: str) -> str:
    result = subprocess.run(['git', 'show', f'{ref}:{path}'], capture_output=True, check=False, text=True)
    if result.returncode != 0:
        raise AssertionError(f'unable_to_read_file_at_ref:{ref}:{path}:{result.stderr.strip()}')
    return result.stdout


def _resolve_commit_ref() -> str:
    result = subprocess.run(['git', 'log', '--format=%H%x09%s'], capture_output=True, check=True, text=True)
    matches: list[str] = []
    for line in result.stdout.splitlines():
        if '\t' not in line:
            continue
        commit_hash, subject = line.split('\t', 1)
        if subject.strip() == PHASE_SUBJECT:
            matches.append(commit_hash)
    for commit_ref in matches:
        changed = _changed_paths_for_commit(commit_ref)
        if changed == EXACT_REQUIRED_PATHS:
            return commit_ref
    if matches:
        raise AssertionError('phase_456_fix_12_commit_subject_present_but_no_qualifying_nonlinear_control_execution_commit')
    raise AssertionError('phase_456_fix_12_commit_not_present_in_local_history')


def test_evidence_package_exists_and_contains_required_headings() -> None:
    assert EVIDENCE_PATH.exists()
    text = _read(EVIDENCE_PATH)
    headings = (
        '## 1. Commission brief reference',
        '## 2. Scenario 5 candidate field executed',
        '## 3. Manifest and reproducibility record',
        '## 4. Raw output summary',
        '## 5. Observable measurements',
        '## 6. Field leader',
        '## 7. Non-authorization statement',
    )
    for heading in headings:
        body = _section_body(text, heading)
        assert body
        assert len([line for line in body.splitlines() if line.strip()]) >= 2


def test_evidence_package_contains_candidates_measurements_and_field_leader() -> None:
    text = _read(EVIDENCE_PATH)
    for token in CANDIDATES + (
        'Scenario 5 only',
        'No Scenarios 1-4 were executed in Phase 456 Fix 12.',
        'organic ECU production rate',
        'P_e clamp-respect rate',
        'absolute percentage-point difference',
        'Execution in Fix 12 is limited to the implemented Fix-10 surface and does not add explicit adjacency-state graph simulation.',
        'Field leader:',
    ):
        assert token in text


def test_comparative_synthesis_exists_and_contains_required_headings() -> None:
    assert SYNTHESIS_PATH.exists()
    text = _read(SYNTHESIS_PATH)
    headings = (
        '## 1. Evidence base',
        '## 2. Candidate ranking',
        '## 3. Threshold evaluation',
        '## 4. Outcome declaration',
        '## 5. Non-authorization statement',
    )
    for heading in headings:
        body = _section_body(text, heading)
        assert body
        assert len([line for line in body.splitlines() if line.strip()]) >= 2


def test_comparative_synthesis_contains_candidates_threshold_tokens_and_single_outcome() -> None:
    text = _read(SYNTHESIS_PATH)
    for token in CANDIDATES + (
        'absolute percentage-point difference',
        'best remaining alternative in the full candidate field frozen in this brief',
        'Execution in Fix 12 is limited to the implemented Fix-10 surface and does not add explicit adjacency-state graph simulation.',
        'Fix 12 used only the implemented Fix-10 surface and did not add explicit adjacency-state graph simulation.',
        'Selected outcome: `Outcome A - Blocker 1 remains open`',
    ):
        assert token in text
    assert text.count('Selected outcome: `Outcome A - Blocker 1 remains open`') == 1


def test_reassessment_exists_and_contains_single_verdict_and_non_authorization_boundary() -> None:
    text = _read(REASSESSMENT_PATH)
    for heading in (
        '## 1. Lead candidate',
        '## 2. Threshold evaluation',
        '## 3. Blocker-1 verdict',
        '## 4. Non-authorization statement',
    ):
        body = _section_body(text, heading)
        assert body
        assert len([line for line in body.splitlines() if line.strip()]) >= 2
    assert 'blocker_1_fix_12_verdict=' in text
    assert text.count('blocker_1_fix_12_verdict=remains_open') == 1
    assert 'Fix-12 success does not automatically reopen CDL-050.' in text
    assert 'No CDL-050 opening or ratification occurs in Phase 456 Fix 12.' in text


def test_raw_outputs_exist_include_all_candidates_and_boundaries_hold() -> None:
    manifest = json.loads(_read(MANIFEST_PATH))
    assert tuple(manifest['field']) == CANDIDATES
    for path in (CSV_PATH, TSV_PATH, SUMMARY_PATH):
        assert path.exists()
        text = _read(path)
        for candidate_id in CANDIDATES:
            assert candidate_id in text
    for path in REQUIRED_FILE_PATHS:
        assert path.exists()
        assert FORBIDDEN_TREASURY_TOKEN not in _read(path)
    walkthrough = _read(WALKTHROUGH_PATH)
    status = _read(STATUS_PATH)
    assert 'Post-Fix-12 blocker disposition review before any further nonlinear-control authorization.' in walkthrough
    assert 'Post-Fix-12 blocker disposition review before any further nonlinear-control authorization.' in status


def test_main_commit_touches_expected_paths_only() -> None:
    commit_ref = _resolve_commit_ref()
    changed = _changed_paths_for_commit(commit_ref)
    assert changed == EXACT_REQUIRED_PATHS
    assert_head_commit_touched_no_runtime_files(commit_ref)


def test_commit_does_not_open_cdl_050_and_preserves_cdl_051() -> None:
    commit_ref = _resolve_commit_ref()
    before_rows = parse_decision_register_rows(_read_file_at_ref(f'{commit_ref}^', str(DECISION_LOG_PATH)))
    after_rows = parse_decision_register_rows(_read_file_at_ref(commit_ref, str(DECISION_LOG_PATH)))
    assert before_rows == after_rows
    assert before_rows['CDL-051']['status'] == 'ratified'
    assert 'CDL-050' not in before_rows
    assert 'CDL-050' not in after_rows
