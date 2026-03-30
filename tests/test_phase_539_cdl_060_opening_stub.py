from __future__ import annotations

import subprocess
from pathlib import Path

from ilc_core.testing.ratification_mutation_scope_guardrail import parse_decision_register_rows

OPENING_STUB_PATH = Path('docs/specs/ilc_cdl_060_gossip_centrality_extension_opening_stub_539_v0.1.md')
DECISION_LOG_PATH = Path('docs/specs/ilc_constitutional_decision_log_v0.1.md')
PHASE_535_TEST_PATH = Path('tests/test_phase_535_sequence_lock_and_carry_forward_intake.py')
PHASE_536_TEST_PATH = Path('tests/test_phase_536_cdl_060_gossip_extension_scoping.py')
PHASE_538_TEST_PATH = Path('tests/test_phase_538_sim_centrality_02_gossip_propagation.py')
TEST_PATH = Path('tests/test_phase_539_cdl_060_opening_stub.py')
PHASE_538_SUBJECT_TOKEN = 'phase 538 sim-centrality-02 gossip propagation'
PHASE_539_SUBJECT_TOKEN = 'phase 539 cdl-060 gossip centrality extension opening'
EXACT_REQUIRED_MAIN_PATHS = {
    str(OPENING_STUB_PATH),
    str(DECISION_LOG_PATH),
    str(PHASE_535_TEST_PATH),
    str(PHASE_536_TEST_PATH),
    str(PHASE_538_TEST_PATH),
    str(TEST_PATH),
}
REQUIRED_HEADINGS = (
    '## 1. Lane identity',
    '## 2. Problem statement',
    '## 3. Candidate options',
    '## 4. Selected option',
    '## 5. Evidence anchors',
    '## 6. Governance tokens',
    '## 7. Forward obligations',
)
REQUIRED_TOKENS = (
    'cdl_060_governs_centrality_delta_gossip',
    'cdl_039_privacy_preserved',
    'single_hop_scope_locked',
    'cdl_036_related_clause',
    'sim_centrality_02_evidence_anchored',
    'CDL-060 remains status: open in Phase 539.',
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


def _resolve_phase_538_commit_ref() -> str:
    result = subprocess.run(
        ['git', 'log', '--format=%H%x09%s'],
        capture_output=True,
        check=True,
        text=True,
    )
    for line in result.stdout.splitlines():
        if '\t' not in line:
            continue
        commit_hash, subject = line.split('\t', 1)
        if PHASE_538_SUBJECT_TOKEN in subject.lower():
            if _changed_paths_for_commit(commit_hash) == {
                'docs/specs/ilc_sim_centrality_02_gossip_propagation_calibration_538_v0.1.md',
                'tests/test_phase_538_sim_centrality_02_gossip_propagation.py',
            }:
                return commit_hash
    raise AssertionError('phase_538_commit_not_present_in_local_history')


def _resolve_phase_539_commit_ref() -> str:
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
        if PHASE_539_SUBJECT_TOKEN not in subject.lower():
            continue
        matching.append(commit_hash)
    for commit_ref in matching:
        if str(DECISION_LOG_PATH) not in _changed_paths_for_commit(commit_ref):
            continue
        if _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS:
            return commit_ref
    if matching:
        raise AssertionError('phase_539_commit_subject_present_but_no_qualifying_opening_commit')
    raise AssertionError('phase_539_commit_not_present_in_local_history')


def _decision_row(markdown: str, cdl_id: str) -> str:
    prefix = f'| {cdl_id} |'
    for line in markdown.splitlines():
        if line.startswith(prefix):
            return line
    raise AssertionError(f'{cdl_id}_row_not_found')


def test_opening_stub_contains_required_headings() -> None:
    text = _read(OPENING_STUB_PATH)
    for heading in REQUIRED_HEADINGS:
        assert heading in text


def test_opening_stub_contains_required_governance_tokens() -> None:
    text = _read(OPENING_STUB_PATH)
    for token in REQUIRED_TOKENS:
        assert token in text


def test_live_decision_log_contains_open_cdl_060_row_and_preserves_other_rows() -> None:
    rows = parse_decision_register_rows(_read(DECISION_LOG_PATH))
    assert rows['CDL-036']['status'] == 'ratified'
    assert rows['CDL-039']['status'] == 'ratified'
    assert rows['CDL-052']['status'] == 'ratified'
    assert rows['CDL-059']['status'] == 'ratified'
    assert rows['CDL-060']['status'] == 'open'
    assert 'ratified_phase' not in rows['CDL-060']
    assert 'ratified_date' not in rows['CDL-060']
    assert 'evidence_document' not in rows['CDL-060']
    assert 'CDL-053' not in rows


def test_phase_535_historicalization_comment_is_present() -> None:
    assert '# The Phase-535 CDL-060 absent check is a historical prelock reference.' in _read(PHASE_535_TEST_PATH)


def test_phase_536_and_phase_538_historicalization_comments_are_present() -> None:
    assert '# The Phase-536 CDL-060 absent check is a historical prelock reference.' in _read(PHASE_536_TEST_PATH)
    assert '# The Phase-538 CDL-060 absent check is a historical prelock reference.' in _read(PHASE_538_TEST_PATH)


def test_phase_539_main_commit_touches_expected_paths_only() -> None:
    commit_ref = _resolve_phase_539_commit_ref()
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS


def test_cdl_log_at_commit_shows_cdl_060_open_and_preserved_priors() -> None:
    phase_538_ref = _resolve_phase_538_commit_ref()
    phase_539_ref = _resolve_phase_539_commit_ref()
    old_text = _commit_text(str(DECISION_LOG_PATH), phase_538_ref)
    new_text = _commit_text(str(DECISION_LOG_PATH), phase_539_ref)
    old_rows = parse_decision_register_rows(old_text)
    new_rows = parse_decision_register_rows(new_text)
    assert new_rows['CDL-060']['status'] == 'open'
    assert 'CDL-053' not in new_rows
    for cdl_id in ('CDL-036', 'CDL-039', 'CDL-052', 'CDL-059'):
        assert _decision_row(old_text, cdl_id) == _decision_row(new_text, cdl_id)
