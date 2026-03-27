from __future__ import annotations

import subprocess
from pathlib import Path

from ilc_core.testing.ratification_mutation_scope_guardrail import parse_decision_register_rows

ARTIFACT_PATH = Path('docs/specs/ilc_refutation_criterion_schema_specification_462_v0.1.md')
TEST_PATH = Path('tests/test_phase_462_refutation_criterion_schema_specification.py')
PHASE_462_SUBJECT_TOKEN = 'phase 462 refutation criterion formal schema specification'
EXACT_REQUIRED_MAIN_PATHS = {
    str(ARTIFACT_PATH),
    str(TEST_PATH),
}
FORBIDDEN_TREASURY_TOKEN = 'ILC_CDL_MUTATION_' + 'AUTHORIZED'
REQUIRED_HEADINGS = (
    '## 1. Field definition',
    '## 2. Authored envelope placement (CDL-034 conformance)',
    '## 3. Required elements',
    '## 4. Validation rules',
    '## 5. Interaction with normative: true metadata',
    '## 6. Gate 2 clearance statement',
)
REQUIRED_TOKENS = (
    'refutation_criterion is an optional field in the authored envelope.',
    'Gate 2 cleared.',
    'No CDL-052 opening occurs in Phase 462.',
    'refutation_criterion implementation in ilc_core/ is deferred until after CDL-052 ratification.',
)


def _read(path: Path) -> str:
    return path.read_text(encoding='utf-8')


def _changed_paths_for_commit(commit_ref: str) -> set[str]:
    result = subprocess.run(['git', 'show', '--name-only', '--pretty=', commit_ref], capture_output=True, check=True, text=True)
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


def _show_file_at_commit(commit_ref: str, path: str) -> str:
    result = subprocess.run(['git', 'show', f'{commit_ref}:{path}'], capture_output=True, check=True, text=True)
    return result.stdout


def _resolve_phase_462_commit_ref() -> str:
    result = subprocess.run(['git', 'log', '--format=%H%x09%s'], capture_output=True, check=True, text=True)
    matching: list[str] = []
    for line in result.stdout.splitlines():
        if '\t' not in line:
            continue
        commit_hash, subject = line.split('\t', 1)
        if PHASE_462_SUBJECT_TOKEN not in subject.lower():
            continue
        matching.append(commit_hash)
    for commit_ref in matching:
        if _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS:
            return commit_ref
    if matching:
        raise AssertionError('phase_462_commit_subject_present_but_no_qualifying_schema_commit')
    raise AssertionError('phase_462_commit_not_present_in_local_history')


def test_schema_spec_artifact_exists_and_contains_required_headings() -> None:
    text = _read(ARTIFACT_PATH)
    for heading in REQUIRED_HEADINGS:
        assert heading in text


def test_schema_spec_contains_required_tokens_including_gate_2_clearance() -> None:
    text = _read(ARTIFACT_PATH)
    for token in REQUIRED_TOKENS:
        assert token in text


def test_required_elements_section_references_minimum_three_required_elements() -> None:
    text = _read(ARTIFACT_PATH)
    assert 'the claim being refuted' in text
    assert 'the type of evidence required for a valid refutation' in text
    assert 'the scope boundary of the claim' in text


def test_no_forbidden_treasury_mutation_token_appears() -> None:
    assert FORBIDDEN_TREASURY_TOKEN not in _read(ARTIFACT_PATH)
    assert FORBIDDEN_TREASURY_TOKEN not in _read(TEST_PATH)


def test_phase_462_commit_touches_expected_paths_and_snapshot_keeps_cdl_052_absent() -> None:
    commit_ref = _resolve_phase_462_commit_ref()
    changed_paths = _changed_paths_for_commit(commit_ref)
    decision_log = _show_file_at_commit(commit_ref, 'docs/specs/ilc_constitutional_decision_log_v0.1.md')
    rows = parse_decision_register_rows(decision_log)
    assert changed_paths == EXACT_REQUIRED_MAIN_PATHS
    assert 'CDL-052' not in rows
    assert not any(path.startswith('docs/specs/ilc_constitutional_decision_log') for path in changed_paths)
    assert not any(path.startswith('ilc_core/') for path in changed_paths)


def test_phase_462_commit_does_not_open_cdl_052() -> None:
    commit_ref = _resolve_phase_462_commit_ref()
    text = _show_file_at_commit(commit_ref, str(ARTIFACT_PATH))
    assert 'No CDL-052 opening occurs in Phase 462.' in text
