from __future__ import annotations

import re
import subprocess
from pathlib import Path

from ilc_core.testing.ratification_mutation_scope_guardrail import (
    assert_head_commit_touched_no_runtime_files,
    parse_decision_register_rows,
)

BRIEF_PATH = Path('docs/specs/ilc_treasury_sim_t_oscillator_commission_brief_456_fix_7_v0.1.md')
TEST_PATH = Path('tests/test_phase_456_fix_7_oscillator_commission_brief_freeze.py')
WALKTHROUGH_PATH = Path('docs/phases/phase_456_fix_7_g8_oscillator_commission_brief_freeze_walkthrough.md')
STATUS_PATH = Path('docs/phases/STATUS.md')
DECISION_LOG_PATH = Path('docs/specs/ilc_constitutional_decision_log_v0.1.md')
PHASE_SUBJECT = 'docs(g8): phase 456 fix 7 oscillator commission brief freeze'
FORBIDDEN_TREASURY_TOKEN = 'ILC_CDL_MUTATION_' + 'AUTHORIZED'
EXACT_REQUIRED_PATHS = {
    str(BRIEF_PATH),
    str(TEST_PATH),
    str(WALKTHROUGH_PATH),
    str(STATUS_PATH),
}
REQUIRED_FILE_PATHS = (BRIEF_PATH, TEST_PATH, WALKTHROUGH_PATH, STATUS_PATH)


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
        raise AssertionError('phase_456_fix_7_commit_subject_present_but_no_qualifying_brief_freeze_commit')
    raise AssertionError('phase_456_fix_7_commit_not_present_in_local_history')


def test_brief_exists_and_contains_required_headings() -> None:
    assert BRIEF_PATH.exists()
    text = _read(BRIEF_PATH)
    headings = (
        '## 1. Mechanism surface reference',
        '## 2. Fix-8 candidate field',
        '## 3. Field-composition decision',
        '## 4. Parameter freeze',
        '## 5. Success criteria and thresholds',
        '## 6. Non-execution and non-authorization statement',
    )
    for heading in headings:
        body = _section_body(text, heading)
        assert body
        assert len([line for line in body.splitlines() if line.strip()]) >= 2


def test_brief_contains_all_frozen_candidates_and_status_token() -> None:
    text = _read(BRIEF_PATH)
    for token in (
        'simulations/sim_treasury_scenario5_oscillator_recovery_rule.py',
        'oscillator_mechanism_status=implemented',
        'oscillating_production_band_short_period',
        'oscillating_production_band_tuned_period',
        'oscillating_production_band_long_period',
        'mixed_queue_and_production',
        'Fix 8 may execute only the candidate field frozen in this brief.',
    ):
        assert token in text


def test_brief_preserves_legacy_exclusion_and_weak_field_challenger_rule() -> None:
    text = _read(BRIEF_PATH)
    assert 'Legacy production-band carry-forwards remain excluded from the oscillator execution field.' in text
    assert '`mixed_queue_and_production` remains the default weak-field challenger for the oscillator lane.' in text


def test_brief_preserves_threshold_contract() -> None:
    text = _read(BRIEF_PATH)
    assert 'Primary-observable threshold evaluation remains based on absolute percentage-point difference.' in text
    assert 'The lead candidate must clear the registered Phase-453 thresholds against the best remaining alternative in the full candidate field frozen in this brief.' in text
    assert 'Duration and cost remain secondary observables and may break ties only after primary-observable threshold clearance.' in text


def test_walkthrough_and_status_point_to_fix_8() -> None:
    walkthrough = _read(WALKTHROUGH_PATH)
    status = _read(STATUS_PATH)
    assert 'Legacy production-band carry-forwards remain excluded.' in walkthrough
    assert 'No Scenario-5 execution was run in Phase 456 Fix 7.' in walkthrough
    assert 'CDL-050 remains unopened.' in walkthrough
    assert 'Phase 456 Fix 8 — oscillator execution, comparative synthesis, and Blocker-1 reassessment' in walkthrough
    assert '## Phase 456 (Fix 7)' in status
    assert 'Phase 456 Fix 8 — oscillator execution, comparative synthesis, and Blocker-1 reassessment' in status


def test_all_required_deliverables_preserve_non_authorization_boundary_and_forbidden_token_absence() -> None:
    for path in REQUIRED_FILE_PATHS:
        assert path.exists()
        assert FORBIDDEN_TREASURY_TOKEN not in _read(path)
    brief = _read(BRIEF_PATH)
    assert 'No Scenario-5 execution occurs in Phase 456 Fix 7.' in brief
    assert 'No CDL-050 opening or ratification occurs in Phase 456 Fix 7.' in brief


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
