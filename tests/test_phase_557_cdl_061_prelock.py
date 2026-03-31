from __future__ import annotations

import subprocess
from pathlib import Path

from ilc_core.testing.ratification_mutation_scope_guardrail import parse_decision_register_rows

PRELOCK_PATH = Path('docs/specs/ilc_cdl_061_gossip_http_envelope_prelock_557_v0.1.md')
DECISION_LOG_PATH = Path('docs/specs/ilc_constitutional_decision_log_v0.1.md')
TEST_PATH = Path('tests/test_phase_557_cdl_061_prelock.py')
PHASE_557_SUBJECT_TOKEN = 'phase 557 cdl-061 gossip http envelope prelock'
EXACT_REQUIRED_MAIN_PATHS = {
    str(DECISION_LOG_PATH),
    str(PRELOCK_PATH),
    str(TEST_PATH),
}
REQUIRED_HEADINGS = (
    '## 1. CDL-061 scope and purpose',
    '## 2. Candidate forms',
    '## 3. Invariants to lock at ratification',
    '## 4. Required header field set',
    '## 5. CDL-039 required exclusions',
    '## 6. CDL-060 hop-count enforcement',
    '## 7. HTTP status code semantics',
    '## 8. Payload encoding',
    '## 9. CDL-024 kind canonical representation',
    '## 10. Prelock governance tokens',
)
REQUIRED_TOKENS = (
    'cdl_061_gossip_http_envelope_prelock',
    'cdl_061_ratification_deferred_to_phase_561',
    'gossip_http_envelope_invariants_locked_at_prelock',
    'cdl_039_exclusions_enforced_at_header_layer',
)
REQUIRED_EXCLUSIONS = (
    '`creator_agent_id` MUST NOT appear in any ILC gossip header.',
    '`node_id` of the originating node MUST NOT appear in transport headers.',
    '`ILC-Channel` value MUST be opaque: no semantically interpretable content',
)


def _read(path: Path) -> str:
    return path.read_text(encoding='utf-8')


def _commit_text(path: str, commit_ref: str) -> str:
    result = subprocess.run(
        ['git', 'show', f'{commit_ref}:{path}'],
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


def _resolve_phase_557_commit_ref() -> str:
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
        lowered = subject.lower()
        if 'phase 557' not in lowered or 'cdl-061' not in lowered:
            continue
        matching.append(commit_hash)
    for commit_ref in matching:
        changed_paths = _changed_paths_for_commit(commit_ref)
        if str(DECISION_LOG_PATH) not in changed_paths or str(PRELOCK_PATH) not in changed_paths:
            continue
        if changed_paths == EXACT_REQUIRED_MAIN_PATHS:
            return commit_ref
    if matching:
        raise AssertionError('phase_557_commit_subject_present_but_no_qualifying_prelock_commit')
    raise AssertionError('phase_557_commit_not_present_in_local_history')


def _decision_row(markdown: str, cdl_id: str) -> str:
    prefix = f'| {cdl_id} |'
    for line in markdown.splitlines():
        if line.startswith(prefix):
            return line
    raise AssertionError(f'{cdl_id}_row_not_found')


def _parent_commit(commit_ref: str) -> str:
    result = subprocess.run(
        ['git', 'rev-parse', f'{commit_ref}^'],
        capture_output=True,
        check=True,
        text=True,
    )
    return result.stdout.strip()


def test_cdl_061_row_is_present_and_open() -> None:
    # The Phase-557 CDL-061 open-state check is a historical prelock reference.
    rows = parse_decision_register_rows(
        _commit_text(str(DECISION_LOG_PATH), _resolve_phase_557_commit_ref())
    )
    assert rows['CDL-061']['status'] == 'open'
    assert 'ratified_phase' not in rows['CDL-061']
    assert 'ratified_date' not in rows['CDL-061']


def test_cdl_061_row_has_expected_related_clauses_and_evidence() -> None:
    # The Phase-557 CDL-061 evidence check is a historical prelock reference.
    rows = parse_decision_register_rows(
        _commit_text(str(DECISION_LOG_PATH), _resolve_phase_557_commit_ref())
    )
    assert rows['CDL-061']['related_clause'] == 'CDL-024 / CDL-039 / CDL-060 / ADR-0025'
    assert rows['CDL-061']['evidence_document'] == str(PRELOCK_PATH)
    assert rows['CDL-061']['dependencies'] == (
        'CDL-024 ratified, CDL-039 ratified, CDL-060 ratified, ADR-0025 accepted'
    )


def test_prelock_artifact_contains_all_required_section_headings() -> None:
    text = _read(PRELOCK_PATH)
    for heading in REQUIRED_HEADINGS:
        assert heading in text


def test_prelock_artifact_contains_all_required_governance_tokens() -> None:
    text = _read(PRELOCK_PATH)
    for token in REQUIRED_TOKENS:
        assert token in text


def test_prelock_artifact_contains_cdl_039_exclusions_verbatim() -> None:
    text = _read(PRELOCK_PATH)
    for exclusion in REQUIRED_EXCLUSIONS:
        assert exclusion in text


def test_phase_557_main_commit_touches_expected_paths_only() -> None:
    commit_ref = _resolve_phase_557_commit_ref()
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS


def test_phase_557_commit_adds_cdl_061_without_modifying_existing_rows_or_ilc_core() -> None:
    commit_ref = _resolve_phase_557_commit_ref()
    parent_ref = _parent_commit(commit_ref)
    old_text = _commit_text(str(DECISION_LOG_PATH), parent_ref)
    new_text = _commit_text(str(DECISION_LOG_PATH), commit_ref)
    old_rows = parse_decision_register_rows(old_text)
    new_rows = parse_decision_register_rows(new_text)
    assert 'CDL-061' not in old_rows
    assert new_rows['CDL-061']['status'] == 'open'
    for cdl_id in old_rows:
        assert _decision_row(old_text, cdl_id) == _decision_row(new_text, cdl_id)
    assert not any(path.startswith('ilc_core/') for path in _changed_paths_for_commit(commit_ref))
