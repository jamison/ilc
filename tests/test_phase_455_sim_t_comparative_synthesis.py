from __future__ import annotations

import re
import subprocess
from pathlib import Path

from ilc_core.testing.ratification_mutation_scope_guardrail import (
    assert_head_commit_touched_no_runtime_files,
    parse_decision_register_rows,
)

SYNTHESIS_PATH = Path('docs/specs/ilc_treasury_sim_t_comparative_synthesis_455_v0.1.md')
TEST_PATH = Path('tests/test_phase_455_sim_t_comparative_synthesis.py')
WALKTHROUGH_PATH = Path(
    'docs/phases/phase_455_g8_sim_t_execution_ii_comparative_synthesis_and_candidate_ranking_walkthrough.md'
)
STATUS_PATH = Path('docs/phases/STATUS.md')
DECISION_LOG_PATH = Path('docs/specs/ilc_constitutional_decision_log_v0.1.md')
PHASE_454_EVIDENCE_PATH = 'docs/specs/ilc_treasury_sim_t_evidence_package_454_v0.1.md'
PHASE_453_BRIEF_PATH = 'docs/specs/ilc_treasury_sim_t_commission_brief_453_v0.1.md'
PHASE_455_SUBJECT = 'docs(g8): phase 455 sim-t execution ii comparative synthesis and candidate ranking'
FORBIDDEN_TREASURY_TOKEN = 'ILC_CDL_MUTATION_' + 'AUTHORIZED'
EXACT_REQUIRED_PATHS = {
    str(SYNTHESIS_PATH),
    str(TEST_PATH),
    str(WALKTHROUGH_PATH),
    str(STATUS_PATH),
}


def _read(path: Path) -> str:
    return path.read_text(encoding='utf-8')


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


def _resolve_phase_455_commit_ref() -> str:
    result = subprocess.run(['git', 'log', '--format=%H%x09%s'], capture_output=True, check=True, text=True)
    matches: list[str] = []
    for line in result.stdout.splitlines():
        if '\t' not in line:
            continue
        commit_hash, subject = line.split('\t', 1)
        if subject.strip() == PHASE_455_SUBJECT:
            matches.append(commit_hash)

    for commit_ref in matches:
        changed = _changed_paths_for_commit(commit_ref)
        if changed == EXACT_REQUIRED_PATHS:
            return commit_ref

    if matches:
        raise AssertionError('phase_455_commit_subject_present_but_no_qualifying_comparative_synthesis_commit')
    raise AssertionError('phase_455_commit_not_present_in_local_history')


def test_synthesis_exists_and_contains_required_headings() -> None:
    assert SYNTHESIS_PATH.exists()
    text = _read(SYNTHESIS_PATH)
    for heading in (
        '## 1. Evidence base',
        '## 2. Candidate comparison',
        '## 3. Discrimination assessment',
        '## 4. Candidate ranking',
        '## 5. Blocker 3 disposition',
        '## 6. Non-authorization statement',
    ):
        assert heading in text


def test_synthesis_contains_required_tokens_and_blocker_disposition() -> None:
    text = _read(SYNTHESIS_PATH)
    assert re.search(r'Blocker 3 disposition:\s+(cleared|remains open)', text)
    for token in (
        'No comparison criteria outside the Phase 453 commission brief were applied.',
        'No CDL-050 opening or ratification occurs in Phase 455.',
    ):
        assert token in text


def test_synthesis_references_phase_454_and_phase_453_inputs() -> None:
    text = _read(SYNTHESIS_PATH)
    assert PHASE_454_EVIDENCE_PATH in text
    assert PHASE_453_BRIEF_PATH in text
    for family in (
        'Scenario 1 - Escrow multiplier discrimination',
        'Scenario 2 - Vesting lock duration discrimination',
        'Scenario 3 - L1/L2 contagion isolation test',
        'Scenario 4 - Long-tail zero-issuance stress test',
        'Scenario 5 - Recovery criterion exit validation',
    ):
        assert family in text


def test_no_forbidden_treasury_mutation_token_appears() -> None:
    for path in (SYNTHESIS_PATH, TEST_PATH):
        assert FORBIDDEN_TREASURY_TOKEN not in _read(path)


def test_phase_455_commit_touches_expected_paths_only() -> None:
    commit_ref = _resolve_phase_455_commit_ref()
    changed = _changed_paths_for_commit(commit_ref)
    assert changed == EXACT_REQUIRED_PATHS
    assert str(DECISION_LOG_PATH) not in changed
    assert_head_commit_touched_no_runtime_files(commit_ref=commit_ref)


def test_phase_455_commit_does_not_open_cdl_050() -> None:
    commit_ref = _resolve_phase_455_commit_ref()
    before_rows = parse_decision_register_rows(_read_file_at_ref(f'{commit_ref}^1', str(DECISION_LOG_PATH)))
    after_rows = parse_decision_register_rows(_read_file_at_ref(commit_ref, str(DECISION_LOG_PATH)))
    assert before_rows == after_rows
    assert before_rows['CDL-051']['status'] == 'ratified'
    assert 'CDL-050' not in before_rows
    assert 'CDL-050' not in after_rows
