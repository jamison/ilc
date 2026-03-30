from __future__ import annotations

import subprocess
from pathlib import Path

from ilc_core.testing.ratification_mutation_scope_guardrail import parse_decision_register_rows

SYNTHESIS_PATH = Path('docs/specs/ilc_adr_0023_simulation_synthesis_528_v0.1.md')
DECISION_LOG_PATH = Path('docs/specs/ilc_constitutional_decision_log_v0.1.md')
TEST_PATH = Path('tests/test_phase_528_adr_0023_simulation_synthesis.py')
PHASE_528_SUBJECT_TOKEN = 'phase 528 adr-0023 simulation synthesis'
EXACT_REQUIRED_MAIN_PATHS = {
    str(SYNTHESIS_PATH),
    str(TEST_PATH),
}
REQUIRED_HEADINGS = (
    '## 1. Synthesis purpose',
    '## 2. SIM-AESTHETIC-01 summary',
    '## 3. SIM-CENTRALITY-01 and SIM-NOVELTY-01 summary',
    '## 4. CDL-059 authorization decision',
    '## 5. CDL-059 opening scope (if authorized)',
    '## 6. Deferred items boundary',
)


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


def _resolve_phase_528_commit_ref() -> str:
    result = subprocess.run(
        ['git', 'log', '--format=%H%x09%s'],
        capture_output=True,
        check=True,
        text=True,
    )
    matching: list[str] = []
    for line in result.stdout.splitlines():
        if '\t' not in line:
            continue
        commit_hash, subject = line.split('\t', 1)
        if PHASE_528_SUBJECT_TOKEN not in subject.lower():
            continue
        matching.append(commit_hash)
    for commit_ref in matching:
        if _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS:
            return commit_ref
    if matching:
        raise AssertionError('phase_528_commit_subject_present_but_no_qualifying_synthesis_commit')
    raise AssertionError('phase_528_commit_not_present_in_local_history')


def test_synthesis_document_contains_required_headings() -> None:
    text = _read(SYNTHESIS_PATH)
    for heading in REQUIRED_HEADINGS:
        assert heading in text


def test_synthesis_document_contains_exactly_one_authorization_token() -> None:
    text = _read(SYNTHESIS_PATH)
    authorized = 'cdl_059_opening_authorized' in text
    deferred = 'cdl_059_opening_deferred' in text
    assert authorized ^ deferred


def test_synthesis_document_states_no_decision_log_mutation() -> None:
    text = _read(SYNTHESIS_PATH)
    assert 'No decision-log mutation occurs in Phase 528.' in text
    assert 'adr_0023_simulation_synthesis' in text


def test_live_decision_log_preserves_required_statuses_and_absences() -> None:
    rows = parse_decision_register_rows(_read(DECISION_LOG_PATH))
    assert rows['CDL-055']['status'] == 'ratified'
    assert rows['CDL-056']['status'] == 'ratified'
    assert rows['CDL-057']['status'] == 'ratified'
    assert rows['CDL-058']['status'] == 'ratified'
    assert 'CDL-053' not in rows
    assert 'CDL-059' not in rows


def test_head_commit_touches_no_ilc_core_runtime_files() -> None:
    changed_paths = {
        path.strip()
        for path in subprocess.run(
            ['git', 'diff', 'HEAD', '--name-only', '--', 'ilc_core/'],
            capture_output=True,
            check=True,
            text=True,
        ).stdout.splitlines()
        if path.strip()
    }
    assert changed_paths == set()


def test_phase_528_main_commit_touches_expected_paths_only() -> None:
    commit_ref = _resolve_phase_528_commit_ref()
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS


def test_phase_528_main_commit_does_not_touch_cdl_log_and_cdl_059_remains_absent() -> None:
    commit_ref = _resolve_phase_528_commit_ref()
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert str(DECISION_LOG_PATH) not in changed_paths
    rows = parse_decision_register_rows(_read(DECISION_LOG_PATH))
    assert 'CDL-059' not in rows
