from __future__ import annotations

import re
import subprocess
from pathlib import Path

from ilc_core.testing.ratification_mutation_scope_guardrail import (
    assert_head_commit_touched_no_runtime_files,
    parse_decision_register_rows,
)

REVIEW_PATH = Path('docs/specs/ilc_phase_456_post_fix_5_blocker_disposition_review_v0.1.md')
TEST_PATH = Path('tests/test_phase_456_post_fix_5_blocker_disposition_review.py')
WALKTHROUGH_PATH = Path('docs/phases/phase_456_post_fix_5_g8_blocker_disposition_review_walkthrough.md')
STATUS_PATH = Path('docs/phases/STATUS.md')
DECISION_LOG_PATH = Path('docs/specs/ilc_constitutional_decision_log_v0.1.md')
PHASE_456_POST_FIX_5_SUBJECT = 'docs(g8): phase 456 post-fix-5 blocker disposition review'
FORBIDDEN_TREASURY_TOKEN = 'ILC_CDL_MUTATION_' + 'AUTHORIZED'
EXACT_REQUIRED_PATHS = {
    str(REVIEW_PATH),
    str(TEST_PATH),
    str(WALKTHROUGH_PATH),
    str(STATUS_PATH),
}
REQUIRED_FILE_PATHS = (
    REVIEW_PATH,
    TEST_PATH,
    WALKTHROUGH_PATH,
    STATUS_PATH,
)
NEXT_POINTER = 'New recovery-rule work requires a fresh prerequisite/mechanism authorization path; otherwise Treasury closure work remains paused.'


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


def _resolve_commit_ref() -> str:
    result = subprocess.run(['git', 'log', '--format=%H%x09%s'], capture_output=True, check=True, text=True)
    matches: list[str] = []
    for line in result.stdout.splitlines():
        if '\t' not in line:
            continue
        commit_hash, subject = line.split('\t', 1)
        if subject.strip() == PHASE_456_POST_FIX_5_SUBJECT:
            matches.append(commit_hash)

    for commit_ref in matches:
        changed = _changed_paths_for_commit(commit_ref)
        if changed == EXACT_REQUIRED_PATHS:
            return commit_ref

    if matches:
        raise AssertionError('phase_456_post_fix_5_commit_subject_present_but_no_qualifying_review_commit')
    raise AssertionError('phase_456_post_fix_5_commit_not_present_in_local_history')


def test_review_exists_and_contains_required_headings() -> None:
    assert REVIEW_PATH.exists()
    text = _read(REVIEW_PATH)
    headings = (
        '## 1. Evidence chain reviewed',
        '## 2. Disposition',
        '## 3. Authorization boundary',
        '## 4. Permitted future paths',
        '## 5. Recommended default',
        '## 6. Non-authorization statement',
    )
    for heading in headings:
        assert heading in text
        body = _section_body(text, heading)
        assert body
        assert len([line for line in body.splitlines() if line.strip()]) >= 2


def test_review_contains_required_disposition_tokens() -> None:
    text = _read(REVIEW_PATH)
    required_tokens = (
        'blocker_1_post_fix_5_disposition=remains_open',
        'The narrowed four-candidate field did not clear the registered thresholds.',
        'Strong production-band carry-forwards were removed and the blocker still remained open.',
        'CDL-050 remains unopened.',
        'Window 450-459 remains failed and closed.',
        'Phases 457-459 remain unauthorized.',
        'No further recovery-rule authorization should proceed on the current mechanism family without a new explicit prerequisite and brief-freeze path.',
        'oscillator_mechanism_status=stubbed',
        'Any future oscillator lane requires a new implemented mechanism surface before brief freeze.',
        NEXT_POINTER,
    )
    for token in required_tokens:
        assert token in text


def test_review_references_the_fix5_evidence_chain() -> None:
    text = _read(REVIEW_PATH)
    required_refs = (
        'docs/specs/ilc_cdl_050_blocker_clearance_gate_456_v0.1.md',
        'docs/specs/ilc_cdl_050_blocker_1_reassessment_456_fix_2_v0.1.md',
        'docs/specs/ilc_cdl_050_blocker_1_reassessment_456_fix_5_v0.1.md',
        'docs/specs/ilc_treasury_sim_t_recovery_rule_commission_brief_456_fix_4_v0.1.md',
        'docs/specs/ilc_phase_456_fix_3_recovery_rule_mechanism_surface_attestation_v0.1.md',
    )
    for ref in required_refs:
        assert ref in text


def test_review_preserves_narrow_scope_to_blocker_1() -> None:
    text = _read(REVIEW_PATH)
    assert 'does not reopen the already cleared Blockers 2, 3, or the L1/L2 prerequisite' in text
    assert 'open a new prerequisite lane for a materially different mechanism class' in text
    assert 'pause Treasury closure work and leave Blocker 1 open pending a later architecture change' in text


def test_walkthrough_and_status_point_to_same_post_fix5_next_pointer() -> None:
    walkthrough = _read(WALKTHROUGH_PATH)
    status = _read(STATUS_PATH)
    assert '## Phase 456 (Post-Fix-5 Review)' in status
    assert NEXT_POINTER in walkthrough
    assert NEXT_POINTER in status


def test_all_required_deliverables_preserve_non_authorization_boundary_and_forbidden_token_absence() -> None:
    for path in REQUIRED_FILE_PATHS:
        assert FORBIDDEN_TREASURY_TOKEN not in _read(path)
    walkthrough = _read(WALKTHROUGH_PATH)
    status = _read(STATUS_PATH)
    assert 'CDL-050 remains unopened.' in walkthrough
    assert 'CDL-050 remained unopened.' in status


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
