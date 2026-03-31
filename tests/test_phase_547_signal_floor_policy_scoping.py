from __future__ import annotations

import subprocess
from pathlib import Path

from ilc_core.testing.ratification_mutation_scope_guardrail import parse_decision_register_rows

SCOPING_DOC_PATH = Path('docs/specs/ilc_signal_floor_policy_consistency_scoping_547_v0.1.md')
DECISION_LOG_PATH = Path('docs/specs/ilc_constitutional_decision_log_v0.1.md')
TEST_PATH = Path('tests/test_phase_547_signal_floor_policy_scoping.py')
PHASE_547_SUBJECT_TOKEN = 'phase 547 signal-floor policy'
EXACT_REQUIRED_MAIN_PATHS = {
    str(SCOPING_DOC_PATH),
    str(TEST_PATH),
}
REQUIRED_HEADINGS = (
    '## 1. Scoping purpose',
    '## 2. Current signal-floor inventory',
    '## 3. Cross-module constraint analysis',
    '## 4. Governance disposition',
    '## 5. Window 555+ forward obligations',
)
DISPOSITION_TOKENS = (
    'signal_floor_governance_adm_only',
    'signal_floor_cdl_warranted',
)


def _read(path: Path) -> str:
    return path.read_text(encoding='utf-8')


def _commit_text(path_str: str, commit_ref: str) -> str:
    result = subprocess.run(
        ['git', 'show', f'{commit_ref}:{path_str}'],
        capture_output=True,
        check=True,
        text=True,
    )
    return result.stdout


def _changed_paths_for_commit(commit_ref: str) -> set[str]:
    result = subprocess.run(
        ['git', 'show', '--name-only', '--pretty=', commit_ref],
        capture_output=True,
        check=True,
        text=True,
    )
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


def _resolve_phase_547_commit_ref() -> str:
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
        if PHASE_547_SUBJECT_TOKEN not in subject.lower():
            continue
        matching.append(commit_hash)
    for commit_ref in matching:
        if _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS:
            return commit_ref
    if matching:
        raise AssertionError('phase_547_commit_subject_present_but_no_qualifying_scoping_commit')
    raise AssertionError('phase_547_commit_not_present_in_local_history')


def test_scoping_document_exists_and_contains_required_headings() -> None:
    text = _read(SCOPING_DOC_PATH)
    for heading in REQUIRED_HEADINGS:
        assert heading in text


def test_scoping_document_contains_signal_floor_policy_scoped_token() -> None:
    text = _read(SCOPING_DOC_PATH)
    assert 'signal_floor_policy_scoped' in text


def test_scoping_document_contains_exactly_one_disposition_token() -> None:
    text = _read(SCOPING_DOC_PATH)
    present = [token for token in DISPOSITION_TOKENS if token in text]
    assert len(present) == 1


def test_scoping_document_enumerates_all_four_expected_floor_sources() -> None:
    text = _read(SCOPING_DOC_PATH)
    for token in ('U_FLOOR', 'recommended_decay_floor', 'CDL-V1', 'CDL-V2'):
        assert token in text


def test_live_cdl_inventory_preserves_required_statuses_and_absences() -> None:
    commit_ref = _resolve_phase_547_commit_ref()
    rows = parse_decision_register_rows(_commit_text(str(DECISION_LOG_PATH), commit_ref))
    assert rows['CDL-036']['status'] == 'ratified'
    assert rows['CDL-039']['status'] == 'ratified'
    assert rows['CDL-052']['status'] == 'ratified'
    assert rows['CDL-059']['status'] == 'ratified'
    assert rows['CDL-060']['status'] == 'ratified'
    assert 'CDL-053' not in rows
    # The Phase-547 CDL-061 absent check is a historical prelock reference.
    assert 'CDL-061' not in rows


def test_phase_547_main_commit_touches_expected_paths_only() -> None:
    commit_ref = _resolve_phase_547_commit_ref()
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS


def test_phase_547_main_commit_does_not_touch_cdl_log_or_any_ilc_core_path() -> None:
    commit_ref = _resolve_phase_547_commit_ref()
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert not any(path.startswith('ilc_core/') for path in changed_paths)
