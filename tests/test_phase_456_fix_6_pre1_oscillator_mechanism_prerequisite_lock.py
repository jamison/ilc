from __future__ import annotations

import re
import subprocess
from pathlib import Path

from ilc_core.testing.ratification_mutation_scope_guardrail import (
    assert_head_commit_touched_no_runtime_files,
    parse_decision_register_rows,
)

SURFACE_PATH = Path('docs/specs/ilc_phase_456_fix_6_pre1_oscillator_mechanism_surface_definition_v0.1.md')
CONTRACT_PATH = Path('docs/specs/ilc_phase_456_fix_6_pre1_oscillator_family_admissibility_and_prerequisite_contract_v0.1.md')
TEST_PATH = Path('tests/test_phase_456_fix_6_pre1_oscillator_mechanism_prerequisite_lock.py')
WALKTHROUGH_PATH = Path('docs/phases/phase_456_fix_6_pre1_g8_oscillator_mechanism_prerequisite_lock_walkthrough.md')
STATUS_PATH = Path('docs/phases/STATUS.md')
DECISION_LOG_PATH = Path('docs/specs/ilc_constitutional_decision_log_v0.1.md')
PHASE_SUBJECT = 'docs(g8): phase 456 fix 6 pre1 oscillator mechanism prerequisite lock'
FORBIDDEN_TREASURY_TOKEN = 'ILC_CDL_MUTATION_' + 'AUTHORIZED'
EXACT_REQUIRED_PATHS = {
    str(SURFACE_PATH),
    str(CONTRACT_PATH),
    str(TEST_PATH),
    str(WALKTHROUGH_PATH),
    str(STATUS_PATH),
}
REQUIRED_FILE_PATHS = (SURFACE_PATH, CONTRACT_PATH, TEST_PATH, WALKTHROUGH_PATH, STATUS_PATH)


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
        raise AssertionError('phase_456_fix_6_pre1_commit_subject_present_but_no_qualifying_prerequisite_commit')
    raise AssertionError('phase_456_fix_6_pre1_commit_not_present_in_local_history')


def test_surface_definition_exists_and_contains_required_headings_and_tokens() -> None:
    assert SURFACE_PATH.exists()
    text = _read(SURFACE_PATH)
    headings = (
        '## 1. Current state after Fix 5',
        '## 2. Admissible oscillator mechanism class',
        '## 3. Candidate parameter surface',
        '## 4. Execution-field boundary',
        '## 5. Non-authorization statement',
    )
    for heading in headings:
        assert heading in text
        body = _section_body(text, heading)
        assert body
        assert len([line for line in body.splitlines() if line.strip()]) >= 2
    for token in (
        'blocker_1_post_fix_5_disposition=remains_open',
        'oscillating_recovery_rule',
        'oscillation_period',
        'oscillation_amplitude',
        'phase_offset',
        'mixed_queue_and_production',
        'Legacy production-band carry-forwards are not automatically included in the oscillator execution field.',
        'No CDL-050 opening or ratification occurs in Phase 456 Fix 6 Pre1.',
    ):
        assert token in text


def test_admissibility_contract_exists_and_contains_required_headings_and_tokens() -> None:
    assert CONTRACT_PATH.exists()
    text = _read(CONTRACT_PATH)
    headings = (
        '## 1. Admissible oscillator candidates',
        '## 2. Field-composition rule',
        '## 3. Implementation exit criteria',
        '## 4. Brief-freeze prerequisite',
        '## 5. Non-authorization statement',
    )
    for heading in headings:
        assert heading in text
        body = _section_body(text, heading)
        assert body
        assert len([line for line in body.splitlines() if line.strip()]) >= 2
    for token in (
        'oscillating_production_band_short_period',
        'oscillating_production_band_tuned_period',
        'oscillating_production_band_long_period',
        'mixed_queue_and_production remains the default weak-field challenger for the oscillator lane.',
        'Legacy production-band carry-forwards are excluded unless a later brief re-admits them explicitly with structural-threshold justification.',
        'A later oscillator brief may freeze candidates only after an implemented oscillator mechanism surface exists in simulations/.',
        'No CDL-050 opening or ratification occurs in Phase 456 Fix 6 Pre1.',
    ):
        assert token in text


def test_review_preserves_legacy_family_pause_while_opening_only_oscillator_prerequisite_lane() -> None:
    surface = _read(SURFACE_PATH)
    contract = _read(CONTRACT_PATH)
    assert 'does not authorize implementation-free execution or any reopening of the legacy family' in surface
    assert 'does not authorize an execution phase yet' in contract
    assert 'The oscillator lane is allowed to define its own frozen field rather than inheriting the exhausted Fix-5 field automatically.' in contract


def test_walkthrough_and_status_point_to_fix6_oscillator_implementation() -> None:
    walkthrough = _read(WALKTHROUGH_PATH)
    status = _read(STATUS_PATH)
    assert 'Phase 456 Fix 6 — oscillator mechanism implementation' in walkthrough
    assert '## Phase 456 (Fix 6 Pre1)' in status
    assert 'Phase 456 Fix 6 — oscillator mechanism implementation' in status
    for path in REQUIRED_FILE_PATHS:
        assert FORBIDDEN_TREASURY_TOKEN not in _read(path)


def test_main_commit_touches_expected_paths_only() -> None:
    commit_ref = _resolve_commit_ref()
    changed = _changed_paths_for_commit(commit_ref)
    assert changed == EXACT_REQUIRED_PATHS
    assert_head_commit_touched_no_runtime_files(commit_ref=commit_ref)


def test_commit_does_not_open_cdl_050_and_preserves_cdl_051() -> None:
    commit_ref = _resolve_commit_ref()
    before_rows = parse_decision_register_rows(_read_file_at_ref(f'{commit_ref}^1', str(DECISION_LOG_PATH)))
    after_rows = parse_decision_register_rows(_read_file_at_ref(commit_ref, str(DECISION_LOG_PATH)))
    assert before_rows == after_rows
    assert before_rows['CDL-051']['status'] == 'ratified'
    assert 'CDL-050' not in before_rows
    assert 'CDL-050' not in after_rows
