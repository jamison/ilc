from __future__ import annotations

import re
import subprocess
from pathlib import Path

from ilc_core.testing.ratification_mutation_scope_guardrail import (
    assert_head_commit_touched_no_runtime_files,
    parse_decision_register_rows,
)

REVIEW_PATH = Path('docs/specs/ilc_phase_456_fix_13_post_nonlinear_control_blocker_disposition_review_v0.1.md')
TEST_PATH = Path('tests/test_phase_456_fix_13_post_nonlinear_control_blocker_disposition_review.py')
WALKTHROUGH_PATH = Path('docs/phases/phase_456_fix_13_g8_post_nonlinear_control_blocker_disposition_review_walkthrough.md')
STATUS_PATH = Path('docs/phases/STATUS.md')
DECISION_LOG_PATH = Path('docs/specs/ilc_constitutional_decision_log_v0.1.md')
PHASE_SUBJECT = 'docs(g8): phase 456 fix 13 post-nonlinear-control blocker disposition review'
FORBIDDEN_TREASURY_TOKEN = 'ILC_CDL_MUTATION_' + 'AUTHORIZED'
EXACT_REQUIRED_PATHS = {
    str(REVIEW_PATH),
    str(TEST_PATH),
    str(WALKTHROUGH_PATH),
    str(STATUS_PATH),
}
REQUIRED_FILE_PATHS = (REVIEW_PATH, TEST_PATH, WALKTHROUGH_PATH, STATUS_PATH)


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
        raise AssertionError('phase_456_fix_13_commit_subject_present_but_no_qualifying_review_commit')
    raise AssertionError('phase_456_fix_13_commit_not_present_in_local_history')


def test_review_exists_and_contains_required_headings() -> None:
    assert REVIEW_PATH.exists()
    text = _read(REVIEW_PATH)
    headings = (
        '## 1. Fix-12 evidence reference',
        '## 2. Post-nonlinear-control blocker disposition',
        '## 3. Gate-level implication',
        '## 4. Non-authorization statement',
    )
    for heading in headings:
        body = _section_body(text, heading)
        assert body
        assert len([line for line in body.splitlines() if line.strip()]) >= 2


def test_review_contains_fix_12_outcome_and_remains_open_tokens() -> None:
    text = _read(REVIEW_PATH)
    assert 'Outcome A - Blocker 1 remains open' in text
    assert 'blocker_1_fix_12_verdict=remains_open' in text
    assert 'blocker_1_post_fix_12_disposition=remains_open' in text


def test_review_records_cleared_oscillator_state_remains_on_record() -> None:
    text = _read(REVIEW_PATH)
    assert 'The post-oscillator cleared state from Phase 456 Fix 9 remains on record.' in text


def test_review_records_gate_level_implication_and_stop_condition() -> None:
    text = _read(REVIEW_PATH)
    assert 'No further nonlinear-control authorization should proceed on the current implemented Waggle Dance field without a fresh prerequisite or field redesign.' in text
    assert 'Fresh CDL-050 blocker-clearance gate rerun authorization if Treasury closure work resumes, using the cleared oscillator evidence chain.' in text
    assert 'No CDL-050 opening or ratification occurs in Phase 456 Fix 13.' in text


def test_walkthrough_and_status_point_to_gate_rerun_via_oscillator_chain() -> None:
    walkthrough = _read(WALKTHROUGH_PATH)
    status = _read(STATUS_PATH)
    next_pointer = 'Fresh CDL-050 blocker-clearance gate rerun authorization if Treasury closure work resumes, using the cleared oscillator evidence chain'
    assert 'blocker_1_post_fix_12_disposition=remains_open' in walkthrough
    assert 'The post-oscillator cleared state remains on record.' in walkthrough
    assert 'CDL-050 remains unopened.' in walkthrough
    assert next_pointer in walkthrough
    assert '## Phase 456 (Fix 13)' in status
    assert 'blocker_1_post_fix_12_disposition=remains_open' in status
    assert next_pointer in status


def test_all_required_deliverables_preserve_non_authorization_boundary_and_forbidden_token_absence() -> None:
    for path in REQUIRED_FILE_PATHS:
        assert path.exists()
        assert FORBIDDEN_TREASURY_TOKEN not in _read(path)
    assert 'No CDL-050 opening or ratification occurs in Phase 456 Fix 13.' in _read(REVIEW_PATH)


def test_main_commit_touches_expected_paths_only() -> None:
    commit_ref = _resolve_commit_ref()
    changed = _changed_paths_for_commit(commit_ref)
    assert changed == EXACT_REQUIRED_PATHS
    assert_head_commit_touched_no_runtime_files(commit_ref)


def test_commit_does_not_open_cdl_050_and_preserves_cdl_051() -> None:
    commit_ref = _resolve_commit_ref()
    before_rows = parse_decision_register_rows(_read_file_at_ref(f'{commit_ref}^', str(DECISION_LOG_PATH)))
    assert before_rows['CDL-051']['status'] == 'ratified'
    assert 'CDL-050' not in before_rows
    for path in EXACT_REQUIRED_PATHS:
        assert FORBIDDEN_TREASURY_TOKEN not in _read_file_at_ref(commit_ref, path)
