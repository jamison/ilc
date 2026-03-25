from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

from ilc_core.testing.ratification_mutation_scope_guardrail import (
    assert_head_commit_touched_no_runtime_files,
    parse_decision_register_rows,
)

EVIDENCE_PATH = Path('docs/specs/ilc_treasury_sim_t_oscillator_evidence_package_456_fix_8_v0.1.md')
SYNTHESIS_PATH = Path('docs/specs/ilc_treasury_sim_t_oscillator_comparative_synthesis_456_fix_8_v0.1.md')
REASSESSMENT_PATH = Path('docs/specs/ilc_cdl_050_blocker_1_reassessment_456_fix_8_v0.1.md')
MANIFEST_PATH = Path('out/treasury_sim/phase_456_fix_8/run_manifest.json')
CSV_PATH = Path('out/treasury_sim/phase_456_fix_8/scenario_5_results.csv')
TSV_PATH = Path('out/treasury_sim/phase_456_fix_8/scenario_5_results.tsv')
SUMMARY_PATH = Path('out/treasury_sim/phase_456_fix_8/summary_table.md')
TEST_PATH = Path('tests/test_phase_456_fix_8_oscillator_execution_and_blocker_1_reassessment.py')
WALKTHROUGH_PATH = Path('docs/phases/phase_456_fix_8_g8_oscillator_execution_walkthrough.md')
STATUS_PATH = Path('docs/phases/STATUS.md')
DECISION_LOG_PATH = Path('docs/specs/ilc_constitutional_decision_log_v0.1.md')
PHASE_SUBJECT = 'docs(g8): phase 456 fix 8 oscillator execution comparative synthesis and blocker-1 reassessment'
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
    'oscillating_production_band_short_period',
    'oscillating_production_band_tuned_period',
    'oscillating_production_band_long_period',
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
        raise AssertionError('phase_456_fix_8_commit_subject_present_but_no_qualifying_execution_commit')
    raise AssertionError('phase_456_fix_8_commit_not_present_in_local_history')


def test_evidence_package_exists_and_contains_required_headings_and_tokens() -> None:
    assert EVIDENCE_PATH.exists()
    text = _read(EVIDENCE_PATH)
    headings = (
        '## 1. Frozen execution field',
        '## 2. Raw Scenario-5 measurements',
        '## 3. Intra-field observations',
        '## 4. Non-authorization statement',
    )
    for heading in headings:
        body = _section_body(text, heading)
        assert body
        assert len([line for line in body.splitlines() if line.strip()]) >= 2
    for token in CANDIDATES + (
        'organic ECU production rate',
        'P_e clamp-respect rate',
        'Legacy production-band carry-forwards remain excluded from the oscillator execution field.',
        'No CDL-050 opening or ratification occurs in Phase 456 Fix 8.',
    ):
        assert token in text


def test_comparative_synthesis_exists_and_contains_required_headings_and_tokens() -> None:
    assert SYNTHESIS_PATH.exists()
    text = _read(SYNTHESIS_PATH)
    headings = (
        '## 1. Ranking summary',
        '## 2. Best-remaining-alternative comparison',
        '## 3. Threshold verdict',
        '## 4. Non-authorization statement',
    )
    for heading in headings:
        body = _section_body(text, heading)
        assert body
        assert len([line for line in body.splitlines() if line.strip()]) >= 2
    for token in CANDIDATES + (
        'Outcome A - Blocker 1 remains open',
        'Outcome B - Blocker 1 evidence closes',
        'Outcome C - Oscillator field remains internally ambiguous',
        'Selected outcome: `Outcome B - Blocker 1 evidence closes`',
        'Primary-observable threshold evaluation remains based on absolute percentage-point difference.',
        'The leader must be evaluated against the best remaining alternative in the full four-candidate frozen field.',
        'No CDL-050 opening or ratification occurs in Phase 456 Fix 8.',
    ):
        assert token in text


def test_reassessment_contains_verdict_and_non_authorization_boundary() -> None:
    assert REASSESSMENT_PATH.exists()
    text = _read(REASSESSMENT_PATH)
    for heading in (
        '## 1. Lead candidate',
        '## 2. Organic ECU production threshold check',
        '## 3. P_e clamp-respect threshold check',
        '## 4. Blocker-1 verdict',
        '## 5. Non-authorization statement',
    ):
        body = _section_body(text, heading)
        assert body
        assert len([line for line in body.splitlines() if line.strip()]) >= 2
    assert 'blocker_1_fix_8_verdict=' in text
    assert 'blocker_1_fix_8_verdict=cleared' in text
    assert 'No CDL-050 opening or ratification occurs in Phase 456 Fix 8.' in text


def test_raw_output_files_exist_and_include_all_four_candidates() -> None:
    assert MANIFEST_PATH.exists()
    manifest = json.loads(_read(MANIFEST_PATH))
    assert tuple(manifest['field']) == CANDIDATES
    for path in (CSV_PATH, TSV_PATH, SUMMARY_PATH):
        assert path.exists()
        text = _read(path)
        for candidate_id in CANDIDATES:
            assert candidate_id in text


def test_walkthrough_and_status_point_to_post_fix_8_review() -> None:
    walkthrough = _read(WALKTHROUGH_PATH)
    status = _read(STATUS_PATH)
    assert 'Outcome B - Blocker 1 evidence closes' in walkthrough
    assert 'blocker_1_fix_8_verdict=cleared' in walkthrough
    assert 'Legacy production-band carry-forwards remained excluded.' in walkthrough
    assert 'CDL-050 remains unopened.' in walkthrough
    assert 'Post-Fix-8 blocker disposition review before any further recovery-rule authorization' in walkthrough
    assert '## Phase 456 (Fix 8)' in status
    assert 'Outcome B - Blocker 1 evidence closes' in status
    assert 'blocker_1_fix_8_verdict=cleared' in status
    assert 'Post-Fix-8 blocker disposition review before any further recovery-rule authorization' in status


def test_all_required_deliverables_preserve_non_authorization_boundary_and_forbidden_token_absence() -> None:
    for path in REQUIRED_FILE_PATHS:
        assert path.exists()
        assert FORBIDDEN_TREASURY_TOKEN not in _read(path)
    for path in (EVIDENCE_PATH, SYNTHESIS_PATH, REASSESSMENT_PATH):
        assert 'No CDL-050 opening or ratification occurs in Phase 456 Fix 8.' in _read(path)


def test_main_commit_touches_expected_paths_only() -> None:
    commit_ref = _resolve_commit_ref()
    changed = _changed_paths_for_commit(commit_ref)
    assert changed == EXACT_REQUIRED_PATHS
    assert_head_commit_touched_no_runtime_files(commit_ref)


def test_commit_does_not_open_cdl_050_and_preserves_cdl_051() -> None:
    commit_ref = _resolve_commit_ref()
    before_ref = f'{commit_ref}^'
    before_rows = parse_decision_register_rows(_read_file_at_ref(before_ref, str(DECISION_LOG_PATH)))
    assert before_rows['CDL-051']['status'] == 'ratified'
    assert 'CDL-050' not in before_rows
    for path in EXACT_REQUIRED_PATHS:
        assert FORBIDDEN_TREASURY_TOKEN not in _read_file_at_ref(commit_ref, path)
