from __future__ import annotations

import re
import subprocess
from pathlib import Path

from ilc_core.testing.ratification_mutation_scope_guardrail import (
    assert_head_commit_touched_no_runtime_files,
    parse_decision_register_rows,
)

ARTIFACT_PATH = Path('docs/specs/ilc_cdl_050_blocker_clearance_gate_456_v0.1.md')
TEST_PATH = Path('tests/test_phase_456_cdl_050_blocker_clearance_gate.py')
WALKTHROUGH_PATH = Path('docs/phases/phase_456_cdl_050_blocker_clearance_gate_walkthrough.md')
STATUS_PATH = Path('docs/phases/STATUS.md')
DECISION_LOG_PATH = Path('docs/specs/ilc_constitutional_decision_log_v0.1.md')
PHASE_456_SUBJECT = 'docs(g8): phase 456 cdl-050 blocker-clearance gate'
FORBIDDEN_TREASURY_TOKEN = 'ILC_CDL_MUTATION_' + 'AUTHORIZED'
EXACT_REQUIRED_PATHS = {
    str(ARTIFACT_PATH),
    str(TEST_PATH),
    str(WALKTHROUGH_PATH),
    str(STATUS_PATH),
}
EXACT_REQUIRED_FILE_PATHS = (
    ARTIFACT_PATH,
    TEST_PATH,
    WALKTHROUGH_PATH,
    STATUS_PATH,
)
EXPECTED_VERDICTS = {
    'phase_456_blocker_1_verdict': 'remains_open',
    'phase_456_blocker_2_verdict': 'cleared',
    'phase_456_blocker_3_verdict': 'cleared',
    'phase_456_l1_l2_verdict': 'cleared',
    'phase_456_overall_verdict': 'fail',
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


def _resolve_phase_456_commit_ref() -> str:
    result = subprocess.run(['git', 'log', '--format=%H%x09%s'], capture_output=True, check=True, text=True)
    matches: list[str] = []
    for line in result.stdout.splitlines():
        if '\t' not in line:
            continue
        commit_hash, subject = line.split('\t', 1)
        if subject.strip() == PHASE_456_SUBJECT:
            matches.append(commit_hash)

    for commit_ref in matches:
        changed = _changed_paths_for_commit(commit_ref)
        if changed == EXACT_REQUIRED_PATHS:
            return commit_ref

    if matches:
        raise AssertionError('phase_456_commit_subject_present_but_no_qualifying_blocker_clearance_commit')
    raise AssertionError('phase_456_commit_not_present_in_local_history')


def test_artifact_exists_and_contains_required_headings() -> None:
    assert ARTIFACT_PATH.exists()
    text = _read(ARTIFACT_PATH)
    headings = (
        '## 1. Gate conditions evaluated',
        '## 2. Blocker 1 verdict',
        '## 3. Blocker 2 verdict',
        '## 4. Blocker 3 verdict',
        '## 5. L1/L2 prerequisite verdict',
        '## 6. Overall gate verdict',
        '## 7. Authorization or carry-forward',
    )
    for heading in headings:
        assert heading in text
        body = _section_body(text, heading)
        assert body
        assert len([line for line in body.splitlines() if line.strip()]) >= 2


def test_verdict_tokens_match_expected_phase_456_results() -> None:
    text = _read(ARTIFACT_PATH)
    for token, expected in EXPECTED_VERDICTS.items():
        assert f'{token}={expected}' in text


def test_gate_sections_contain_substantive_reasoning() -> None:
    text = _read(ARTIFACT_PATH)
    assert 'docs/specs/ilc_treasury_objective_function_and_observables_contract_451_v0.1.md' in text
    assert 'docs/specs/ilc_cdl_050_l1_l2_prerequisite_disposition_452_v0.1.md' in text
    assert 'docs/specs/ilc_treasury_sim_t_commission_brief_453_v0.1.md' in text
    assert 'docs/specs/ilc_treasury_sim_t_evidence_package_454_v0.1.md' in text
    assert 'docs/specs/ilc_treasury_sim_t_comparative_synthesis_455_v0.1.md' in text
    blocker_1 = _section_body(text, '## 2. Blocker 1 verdict')
    assert 'organic ECU production' in blocker_1
    assert 'clamp-respect' in blocker_1
    assert 'Duration and cost do separate inside the family.' in blocker_1
    assert '18 epochs / 0.49 units' in _section_body(text, '## 3. Blocker 2 verdict')
    assert '`19` percentage points' in _section_body(text, '## 4. Blocker 3 verdict')


def test_fail_branch_tokens_and_carry_forward_statement_present() -> None:
    text = _read(ARTIFACT_PATH)
    assert 'Phases 457-459 must not proceed.' in text
    assert 'CDL-050 carry-forward memo:' in text
    assert 'Any future attempt to reopen the lane requires a new sequence lock' in text
    assert 'All gates cleared. Phases 457-459 are authorized to proceed.' not in text


def test_walkthrough_and_status_record_fail_gate_and_next_pointer() -> None:
    walkthrough = _read(WALKTHROUGH_PATH)
    status = _read(STATUS_PATH)
    assert 'overall gate verdict: fail' in walkthrough.lower()
    assert 'Blocker 1 remains open' in walkthrough
    assert 'CDL-050 remains unopened' in walkthrough
    assert 'carry-forward outside Window 450-459' in walkthrough
    assert '## Phase 456' in status
    assert 'gate verdict `fail`' in status.lower()


def test_no_forbidden_treasury_mutation_token_appears() -> None:
    for path in EXACT_REQUIRED_FILE_PATHS:
        assert FORBIDDEN_TREASURY_TOKEN not in _read(path)


def test_phase_456_commit_touches_expected_paths_only() -> None:
    commit_ref = _resolve_phase_456_commit_ref()
    changed = _changed_paths_for_commit(commit_ref)
    assert changed == EXACT_REQUIRED_PATHS
    assert_head_commit_touched_no_runtime_files(commit_ref=commit_ref)


def test_phase_456_commit_does_not_open_cdl_050() -> None:
    commit_ref = _resolve_phase_456_commit_ref()
    before_rows = parse_decision_register_rows(_read_file_at_ref(f'{commit_ref}^1', str(DECISION_LOG_PATH)))
    after_rows = parse_decision_register_rows(_read_file_at_ref(commit_ref, str(DECISION_LOG_PATH)))
    assert before_rows == after_rows
    assert before_rows['CDL-051']['status'] == 'ratified'
    assert 'CDL-050' not in before_rows
    assert 'CDL-050' not in after_rows
