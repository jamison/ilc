from __future__ import annotations

import re
import subprocess
from pathlib import Path

from ilc_core.testing.ratification_mutation_scope_guardrail import (
    assert_head_commit_touched_no_runtime_files,
    parse_decision_register_rows,
)

SURFACE_PATH = Path('docs/specs/ilc_phase_456_fix_3_pre1_recovery_rule_mechanism_surface_definition_v0.1.md')
CONTRACT_PATH = Path('docs/specs/ilc_phase_456_fix_3_pre1_recovery_rule_family_admissibility_and_prerequisite_contract_v0.1.md')
TEST_PATH = Path('tests/test_phase_456_fix_3_pre1_recovery_rule_mechanism_prerequisite_lock.py')
WALKTHROUGH_PATH = Path(
    'docs/phases/phase_456_fix_3_pre1_g8_recovery_rule_mechanism_prerequisite_lock_walkthrough.md'
)
STATUS_PATH = Path('docs/phases/STATUS.md')
DECISION_LOG_PATH = Path('docs/specs/ilc_constitutional_decision_log_v0.1.md')
PHASE_456_FIX_3_PRE1_SUBJECT = 'docs(g8): phase 456 fix 3 pre1 recovery-rule mechanism prerequisite lock'
FORBIDDEN_TREASURY_TOKEN = 'ILC_CDL_MUTATION_' + 'AUTHORIZED'
EXACT_REQUIRED_PATHS = {
    str(SURFACE_PATH),
    str(CONTRACT_PATH),
    str(TEST_PATH),
    str(WALKTHROUGH_PATH),
    str(STATUS_PATH),
}
REQUIRED_FILE_PATHS = (
    SURFACE_PATH,
    CONTRACT_PATH,
    TEST_PATH,
    WALKTHROUGH_PATH,
    STATUS_PATH,
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


def _resolve_phase_456_fix_3_pre1_commit_ref() -> str:
    result = subprocess.run(['git', 'log', '--format=%H%x09%s'], capture_output=True, check=True, text=True)
    matches: list[str] = []
    for line in result.stdout.splitlines():
        if '\t' not in line:
            continue
        commit_hash, subject = line.split('\t', 1)
        if subject.strip() == PHASE_456_FIX_3_PRE1_SUBJECT:
            matches.append(commit_hash)

    for commit_ref in matches:
        changed = _changed_paths_for_commit(commit_ref)
        if changed == EXACT_REQUIRED_PATHS:
            return commit_ref

    if matches:
        raise AssertionError('phase_456_fix_3_pre1_commit_subject_present_but_no_qualifying_prerequisite_lock_commit')
    raise AssertionError('phase_456_fix_3_pre1_commit_not_present_in_local_history')


def test_prerequisite_docs_exist_and_contain_required_headings() -> None:
    for path, headings in (
        (
            SURFACE_PATH,
            (
                '## 1. Current repository state',
                '## 2. Missing mechanism surfaces',
                '## 3. Candidate mechanism classes',
                '## 4. Measurement-window and parameterization requirements',
                '## 5. Non-authorization statement',
            ),
        ),
        (
            CONTRACT_PATH,
            (
                '## 1. Admissible carry-forward baseline',
                '## 2. Oscillator admissibility rule',
                '## 3. Fixed weak-field challenger policy',
                '## 4. Implementation exit criteria',
                '## 5. Non-authorization statement',
            ),
        ),
    ):
        assert path.exists()
        text = _read(path)
        for heading in headings:
            assert heading in text
            body = _section_body(text, heading)
            assert body
            assert len([line for line in body.splitlines() if line.strip()]) >= 2


def test_prerequisite_docs_contain_required_tokens() -> None:
    surface = _read(SURFACE_PATH)
    contract = _read(CONTRACT_PATH)
    for token in (
        'No executable Treasury recovery-rule mechanism exists in ilc_core today.',
        'mixed_queue_and_production',
        'oscillation_period',
        'oscillation_amplitude',
        'phase_offset',
        'No CDL-050 opening or ratification occurs in Phase 456 Fix 3 Pre1.',
    ):
        assert token in surface
    for token in (
        'Subfamily A - epoch-window variants',
        'Subfamily B - clamp-floor variants',
        'oscillating_production_band_short_period',
        'oscillating_production_band_long_period',
        'Fix 5 field composition decision',
        'Retaining strong production-band carry-forwards may make the 10 percentage-point organic-production threshold structurally unachievable.',
        'Fix 4 must record whether strong production-band carry-forwards remain in the Fix 5 comparison field.',
        'Fix 4 must not freeze an oscillator family unless the executable mechanism surface exists first.',
        'No CDL-050 opening or ratification occurs in Phase 456 Fix 3 Pre1.',
    ):
        assert token in contract


def test_prerequisite_docs_preserve_non_authorization_boundary() -> None:
    for path in REQUIRED_FILE_PATHS:
        if path.exists():
            assert FORBIDDEN_TREASURY_TOKEN not in _read(path)
    assert 'No CDL-050 opening or ratification occurs in Phase 456 Fix 3 Pre1.' in _read(SURFACE_PATH)
    assert 'No CDL-050 opening or ratification occurs in Phase 456 Fix 3 Pre1.' in _read(CONTRACT_PATH)


def test_walkthrough_and_status_point_to_phase_456_fix_3_implementation() -> None:
    walkthrough = _read(WALKTHROUGH_PATH)
    status = _read(STATUS_PATH)
    assert 'Phase 456 Fix 3 — recovery-rule mechanism implementation' in walkthrough
    assert 'Phase 456 Fix 3 — recovery-rule mechanism implementation' in status
    assert '## Phase 456 (Fix 3 Pre1)' in status


def test_phase_456_fix_3_pre1_commit_touches_expected_paths_only() -> None:
    commit_ref = _resolve_phase_456_fix_3_pre1_commit_ref()
    changed = _changed_paths_for_commit(commit_ref)
    assert changed == EXACT_REQUIRED_PATHS
    assert str(DECISION_LOG_PATH) not in changed
    assert_head_commit_touched_no_runtime_files(commit_ref=commit_ref)


def test_phase_456_fix_3_pre1_commit_does_not_open_cdl_050_and_preserves_cdl_051() -> None:
    commit_ref = _resolve_phase_456_fix_3_pre1_commit_ref()
    before_rows = parse_decision_register_rows(_read_file_at_ref(f'{commit_ref}^1', str(DECISION_LOG_PATH)))
    after_rows = parse_decision_register_rows(_read_file_at_ref(commit_ref, str(DECISION_LOG_PATH)))
    assert before_rows == after_rows
    assert before_rows['CDL-051']['status'] == 'ratified'
    assert 'CDL-050' not in before_rows
    assert 'CDL-050' not in after_rows
