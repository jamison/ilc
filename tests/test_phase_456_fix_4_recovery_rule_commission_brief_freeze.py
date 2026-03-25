from __future__ import annotations

import re
import subprocess
from pathlib import Path

from ilc_core.testing.ratification_mutation_scope_guardrail import (
    assert_head_commit_touched_no_runtime_files,
    parse_decision_register_rows,
)

BRIEF_PATH = Path('docs/specs/ilc_treasury_sim_t_recovery_rule_commission_brief_456_fix_4_v0.1.md')
TEST_PATH = Path('tests/test_phase_456_fix_4_recovery_rule_commission_brief_freeze.py')
WALKTHROUGH_PATH = Path('docs/phases/phase_456_fix_4_g8_recovery_rule_commission_brief_freeze_walkthrough.md')
STATUS_PATH = Path('docs/phases/STATUS.md')
DECISION_LOG_PATH = Path('docs/specs/ilc_constitutional_decision_log_v0.1.md')
PHASE_456_FIX_4_SUBJECT = 'docs(g8): phase 456 fix 4 recovery-rule commission brief freeze'
FORBIDDEN_TREASURY_TOKEN = 'ILC_CDL_MUTATION_' + 'AUTHORIZED'
EXACT_REQUIRED_PATHS = {
    str(BRIEF_PATH),
    str(TEST_PATH),
    str(WALKTHROUGH_PATH),
    str(STATUS_PATH),
}
REQUIRED_FILE_PATHS = (
    BRIEF_PATH,
    TEST_PATH,
    WALKTHROUGH_PATH,
    STATUS_PATH,
)
VALID_FIELD_DECISION_TOKENS = {
    'strong production-band carry-forwards remain in the Fix 5 comparison field.',
    'strong production-band carry-forwards are removed from the Fix 5 comparison field.',
}


def _read(path: Path) -> str:
    return path.read_text(encoding='utf-8')


def _section_body(text: str, heading: str) -> str:
    escaped = re.escape(heading)
    match = re.search(rf'{escaped}\n\n(.*?)(?=\n## |\Z)', text, flags=re.S)
    if not match:
        raise AssertionError(f'section_not_found:{heading}')
    return match.group(1).strip()


def _changed_paths_for_commit(commit_ref: str) -> set[str]:
    result = subprocess.run(
        ['git', 'show', '--name-only', '--pretty=', commit_ref],
        capture_output=True,
        check=True,
        text=True,
    )
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


def _read_file_at_ref(ref: str, path: str) -> str:
    result = subprocess.run(['git', 'show', f'{ref}:{path}'], capture_output=True, check=False, text=True)
    if result.returncode != 0:
        raise AssertionError(f'unable_to_read_file_at_ref:{ref}:{path}:{result.stderr.strip()}')
    return result.stdout


def _resolve_phase_456_fix_4_commit_ref() -> str:
    result = subprocess.run(['git', 'log', '--format=%H%x09%s'], capture_output=True, check=True, text=True)
    matches: list[str] = []
    for line in result.stdout.splitlines():
        if '\t' not in line:
            continue
        commit_hash, subject = line.split('\t', 1)
        if subject.strip() == PHASE_456_FIX_4_SUBJECT:
            matches.append(commit_hash)

    for commit_ref in matches:
        changed = _changed_paths_for_commit(commit_ref)
        if changed == EXACT_REQUIRED_PATHS:
            return commit_ref

    if matches:
        raise AssertionError('phase_456_fix_4_commit_subject_present_but_no_qualifying_commission_brief_commit')
    raise AssertionError('phase_456_fix_4_commit_not_present_in_local_history')


def test_commission_brief_exists_and_contains_required_headings() -> None:
    assert BRIEF_PATH.exists()
    text = _read(BRIEF_PATH)
    headings = (
        '## 1. Mechanism surface reference',
        '## 2. Fix-5 candidate field',
        '## 3. Field-composition decision',
        '## 4. Oscillator admissibility disposition',
        '## 5. Parameter freeze',
        '## 6. Success criteria and thresholds',
        '## 7. Non-execution and non-authorization statement',
    )
    for heading in headings:
        assert heading in text
        body = _section_body(text, heading)
        assert body
        assert len([line for line in body.splitlines() if line.strip()]) >= 2


def test_commission_brief_contains_mechanism_reference_threshold_and_field_tokens() -> None:
    text = _read(BRIEF_PATH)
    required_tokens = (
        'simulations/sim_treasury_scenario5_recovery_rule.py',
        'mixed_queue_and_production',
        'absolute percentage-point difference',
        'best remaining alternative in the full candidate field frozen in this brief',
        'Fix 5 field composition decision',
        'Retaining strong production-band carry-forwards may make the 10 percentage-point organic-production threshold structurally unachievable.',
        'Fix 5 may execute only the candidate field frozen in this brief.',
    )
    for token in required_tokens:
        assert token in text


def test_commission_brief_records_stubbed_oscillator_status_and_excludes_oscillator_candidates() -> None:
    text = _read(BRIEF_PATH)
    assert 'oscillator_mechanism_status=stubbed' in text
    assert 'Oscillator candidates are excluded from Fix 5 because oscillator_mechanism_status=stubbed.' in text
    assert 'No Scenario-5 execution occurs in Phase 456 Fix 4.' in text
    assert 'No CDL-050 opening or ratification occurs in Phase 456 Fix 4.' in text


def test_commission_brief_records_valid_field_composition_decision_and_fix5_boundary() -> None:
    text = _read(BRIEF_PATH)
    assert any(token in text for token in VALID_FIELD_DECISION_TOKENS)
    assert 'Fix 5 may execute only the candidate field frozen in this brief.' in text
    assert 'Fix 4 does not authorize Fix 5 execution by itself.' in text


def test_walkthrough_and_status_point_to_fix5() -> None:
    walkthrough = _read(WALKTHROUGH_PATH)
    status = _read(STATUS_PATH)
    assert 'Phase 456 Fix 5 — recovery-rule execution under the Fix-4 brief' in walkthrough
    assert 'Phase 456 Fix 5 — recovery-rule execution under the Fix-4 brief' in status
    assert '## Phase 456 (Fix 4)' in status


def test_all_deliverables_preserve_non_authorization_boundary_and_forbidden_token_absence() -> None:
    for path in REQUIRED_FILE_PATHS:
        assert FORBIDDEN_TREASURY_TOKEN not in _read(path)
    walkthrough = _read(WALKTHROUGH_PATH)
    status = _read(STATUS_PATH)
    assert 'No Scenario-5 execution was run in Phase 456 Fix 4.' in walkthrough
    assert 'No `ilc_core/` runtime files were changed.' in walkthrough
    assert 'CDL-050 remains unopened.' in walkthrough
    assert 'CDL-050 remained unopened.' in status


def test_phase_456_fix_4_main_commit_touches_expected_paths_only() -> None:
    commit_ref = _resolve_phase_456_fix_4_commit_ref()
    changed = _changed_paths_for_commit(commit_ref)
    assert changed == EXACT_REQUIRED_PATHS
    assert_head_commit_touched_no_runtime_files(commit_ref=commit_ref)


def test_phase_456_fix_4_commit_does_not_open_cdl_050_and_preserves_cdl_051() -> None:
    commit_ref = _resolve_phase_456_fix_4_commit_ref()
    before_rows = parse_decision_register_rows(_read_file_at_ref(f'{commit_ref}^1', str(DECISION_LOG_PATH)))
    after_rows = parse_decision_register_rows(_read_file_at_ref(commit_ref, str(DECISION_LOG_PATH)))
    assert before_rows == after_rows
    assert before_rows['CDL-051']['status'] == 'ratified'
    assert 'CDL-050' not in before_rows
    assert 'CDL-050' not in after_rows
