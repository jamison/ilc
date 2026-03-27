from __future__ import annotations

import subprocess
from pathlib import Path

from ilc_core.testing.ratification_mutation_scope_guardrail import parse_decision_register_rows

OPENING_STUB_PATH = Path('docs/specs/ilc_cdl_052_epistemic_evaluation_architecture_opening_stub_464_v0.1.md')
DECISION_LOG_PATH = Path('docs/specs/ilc_constitutional_decision_log_v0.1.md')
TEST_PATH = Path('tests/test_phase_464_cdl_052_opening.py')
PHASE_464_SUBJECT_TOKEN = 'phase 464 cdl-052 opening'
EXACT_REQUIRED_MAIN_PATHS = {
    str(DECISION_LOG_PATH),
    str(OPENING_STUB_PATH),
    str(TEST_PATH),
}
FORBIDDEN_TREASURY_TOKEN = 'ILC_CDL_MUTATION_' + 'AUTHORIZED'
REQUIRED_HEADINGS = (
    '## 1. Opening declaration',
    '## 2. Scope of CDL-052',
    '## 3. Dependency clauses',
    '## 4. Gate clearance references',
    '## 5. Prelock target',
)
REQUIRED_TOKENS = (
    'CDL-052 is opened in Phase 464 following clean Gate 1, Gate 2, and Gate 3 clearances.',
    'CDL-052 governs the three-mode epistemic evaluation architecture for knowledge graph nodes.',
    'CDL-052 does not govern CDL-V7 agent decomposition admissibility, CDL-V3 quorum diversity, CDL-V2 Sybil resistance, or CDL-V1 temporal decay.',
    'Prelock hardening occurs in Phase 465.',
    'Ratification occurs in Phase 466 if and only if the prelock phase remains clean.',
)


def _read(path: Path) -> str:
    return path.read_text(encoding='utf-8')


def _changed_paths_for_commit(commit_ref: str) -> set[str]:
    result = subprocess.run(['git', 'show', '--name-only', '--pretty=', commit_ref], capture_output=True, check=True, text=True)
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


def _show_file_at_commit(commit_ref: str, path: str) -> str:
    result = subprocess.run(['git', 'show', f'{commit_ref}:{path}'], capture_output=True, check=True, text=True)
    return result.stdout


def _resolve_phase_464_commit_ref() -> str:
    result = subprocess.run(['git', 'log', '--format=%H%x09%s'], capture_output=True, check=True, text=True)
    matching: list[str] = []
    for line in result.stdout.splitlines():
        if '\t' not in line:
            continue
        commit_hash, subject = line.split('\t', 1)
        if PHASE_464_SUBJECT_TOKEN not in subject.lower():
            continue
        matching.append(commit_hash)
    for commit_ref in matching:
        if _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS:
            return commit_ref
    if matching:
        raise AssertionError('phase_464_commit_subject_present_but_no_qualifying_opening_commit')
    raise AssertionError('phase_464_commit_not_present_in_local_history')


def test_opening_stub_exists_and_contains_required_headings() -> None:
    text = _read(OPENING_STUB_PATH)
    for heading in REQUIRED_HEADINGS:
        assert heading in text


def test_opening_stub_contains_required_tokens() -> None:
    text = _read(OPENING_STUB_PATH)
    for token in REQUIRED_TOKENS:
        assert token in text


def test_current_decision_log_contains_cdl_052_row_and_opening_stub_reference() -> None:
    rows = parse_decision_register_rows(_read(DECISION_LOG_PATH))
    assert 'CDL-052' in rows
    assert 'docs/specs/ilc_cdl_052_epistemic_evaluation_architecture_opening_stub_464_v0.1.md' in rows['CDL-052']['required_artifacts']


def test_current_decision_log_preserves_cdl_050_and_cdl_051_ratified_state() -> None:
    rows = parse_decision_register_rows(_read(DECISION_LOG_PATH))
    assert rows['CDL-050']['status'] == 'ratified'
    assert rows['CDL-051']['status'] == 'ratified'


def test_no_forbidden_treasury_mutation_token_in_stub_or_test_file() -> None:
    assert FORBIDDEN_TREASURY_TOKEN not in _read(OPENING_STUB_PATH)
    assert FORBIDDEN_TREASURY_TOKEN not in _read(TEST_PATH)


def test_current_decision_log_keeps_cdl_050_cdl_051_cdl_052_in_order() -> None:
    text = _read(DECISION_LOG_PATH)
    assert text.index('| CDL-050 |') < text.index('| CDL-051 |') < text.index('| CDL-052 |')


def test_phase_464_commit_touches_exact_required_paths_and_snapshot_opens_cdl_052() -> None:
    commit_ref = _resolve_phase_464_commit_ref()
    changed_paths = _changed_paths_for_commit(commit_ref)
    rows = parse_decision_register_rows(_show_file_at_commit(commit_ref, str(DECISION_LOG_PATH)))
    assert changed_paths == EXACT_REQUIRED_MAIN_PATHS
    assert rows['CDL-052']['status'] == 'open'
    assert 'docs/specs/ilc_cdl_052_epistemic_evaluation_architecture_opening_stub_464_v0.1.md' in rows['CDL-052']['required_artifacts']
    assert not any(path.startswith('ilc_core/') for path in changed_paths)


def test_phase_464_commit_subject_is_present_in_local_history() -> None:
    assert _resolve_phase_464_commit_ref()
