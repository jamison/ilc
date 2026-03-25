from __future__ import annotations

import re
import subprocess
from pathlib import Path

from ilc_core.testing.ratification_mutation_scope_guardrail import (
    assert_head_commit_touched_no_runtime_files,
    parse_decision_register_rows,
)

SURFACE_PATH = Path('docs/specs/ilc_phase_456_fix_10_pre1_nonlinear_control_mechanism_surface_definition_v0.1.md')
CONTRACT_PATH = Path('docs/specs/ilc_phase_456_fix_10_pre1_nonlinear_control_family_admissibility_and_prerequisite_contract_v0.1.md')
TEST_PATH = Path('tests/test_phase_456_fix_10_pre1_nonlinear_control_mechanism_prerequisite_lock.py')
WALKTHROUGH_PATH = Path('docs/phases/phase_456_fix_10_pre1_g8_nonlinear_control_mechanism_prerequisite_lock_walkthrough.md')
STATUS_PATH = Path('docs/phases/STATUS.md')
DECISION_LOG_PATH = Path('docs/specs/ilc_constitutional_decision_log_v0.1.md')
PHASE_SUBJECT = 'docs(g8): phase 456 fix 10 pre1 nonlinear-control mechanism prerequisite lock'
FORBIDDEN_TREASURY_TOKEN = 'ILC_CDL_MUTATION_' + 'AUTHORIZED'
EXACT_REQUIRED_PATHS = {
    str(SURFACE_PATH),
    str(CONTRACT_PATH),
    str(TEST_PATH),
    str(WALKTHROUGH_PATH),
    str(STATUS_PATH),
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
        if _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_PATHS:
            return commit_ref
    if matches:
        raise AssertionError('phase_456_fix_10_pre1_commit_subject_present_but_no_qualifying_prerequisite_commit')
    raise AssertionError('phase_456_fix_10_pre1_commit_not_present_in_local_history')


def test_surface_definition_exists_and_contains_required_headings_and_tokens() -> None:
    text = _read(SURFACE_PATH)
    for heading in (
        '## 1. Current state after Fix 9',
        '## 2. Admissible nonlinear-control mechanism class',
        '## 3. Candidate parameter surface',
        '## 4. Execution-field boundary',
        '## 5. Non-authorization statement',
    ):
        body = _section_body(text, heading)
        assert body
        assert len([line for line in body.splitlines() if line.strip()]) >= 2
    for token in (
        'blocker_1_post_fix_8_disposition=cleared',
        'nonlinear_control_curve',
        'response_knee',
        'control_gain',
        'release_floor',
        'bias',
        'mixed_queue_and_production',
        'Legacy production-band carry-forwards are not automatically included in the nonlinear-control execution field.',
        'No CDL-050 opening or ratification occurs in Phase 456 Fix 10 Pre1.',
    ):
        assert token in text


def test_admissibility_contract_exists_and_contains_required_headings_and_tokens() -> None:
    text = _read(CONTRACT_PATH)
    for heading in (
        '## 1. Admissible nonlinear-control candidates',
        '## 2. Field-composition rule',
        '## 3. Implementation exit criteria',
        '## 4. Brief-freeze prerequisite',
        '## 5. Non-authorization statement',
    ):
        body = _section_body(text, heading)
        assert body
        assert len([line for line in body.splitlines() if line.strip()]) >= 2
    for token in (
        'nonlinear_curve_k56_g18_f22_frontier_first',
        'nonlinear_curve_k58_g18_f22_frontier_first',
        'nonlinear_curve_k60_g18_f22_frontier_first',
        'mixed_queue_and_production remains the default weak-field challenger for the nonlinear-control lane.',
        'A later nonlinear-control brief may freeze candidates only after an implemented nonlinear-control mechanism surface exists in simulations/.',
        'No CDL-050 opening or ratification occurs in Phase 456 Fix 10 Pre1.',
    ):
        assert token in text


def test_review_preserves_cleared_state_while_opening_only_nonlinear_prerequisite_lane() -> None:
    assert 'blocker_1_post_fix_8_disposition=cleared' in _read(SURFACE_PATH)
    assert 'opens only the nonlinear-control mechanism path' in _read(CONTRACT_PATH)
    assert 'No CDL-050 opening or ratification occurs in Phase 456 Fix 10 Pre1.' in _read(SURFACE_PATH)
    assert 'No CDL-050 opening or ratification occurs in Phase 456 Fix 10 Pre1.' in _read(CONTRACT_PATH)


def test_walkthrough_and_status_point_to_fix_10() -> None:
    walkthrough = _read(WALKTHROUGH_PATH)
    status = _read(STATUS_PATH)
    assert 'Phase 456 Fix 10 — nonlinear-control mechanism implementation' in walkthrough
    assert 'Phase 456 Fix 10 — nonlinear-control mechanism implementation' in status
    assert '## Phase 456 (Fix 10 Pre1)' in status


def test_main_commit_touches_expected_paths_only() -> None:
    commit_ref = _resolve_commit_ref()
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_PATHS
    assert_head_commit_touched_no_runtime_files(commit_ref)


def test_commit_does_not_open_cdl_050_and_preserves_cdl_051() -> None:
    commit_ref = _resolve_commit_ref()
    before_rows = parse_decision_register_rows(_read_file_at_ref(f'{commit_ref}^', str(DECISION_LOG_PATH)))
    assert before_rows['CDL-051']['status'] == 'ratified'
    assert 'CDL-050' not in before_rows
    for path in EXACT_REQUIRED_PATHS:
        assert FORBIDDEN_TREASURY_TOKEN not in _read_file_at_ref(commit_ref, path)
