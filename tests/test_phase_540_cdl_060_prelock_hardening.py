from __future__ import annotations

import subprocess
from pathlib import Path

from ilc_core.testing.ratification_mutation_scope_guardrail import parse_decision_register_rows

PRELOCK_PATH = Path('docs/specs/ilc_cdl_060_gossip_centrality_extension_prelock_hardening_540_v0.1.md')
DECISION_LOG_PATH = Path('docs/specs/ilc_constitutional_decision_log_v0.1.md')
PHASE_539_TEST_PATH = Path('tests/test_phase_539_cdl_060_opening_stub.py')
TEST_PATH = Path('tests/test_phase_540_cdl_060_prelock_hardening.py')
PHASE_540_SUBJECT_TOKEN = 'phase 540 cdl-060 prelock hardening'
EXACT_REQUIRED_MAIN_PATHS = {
    str(PRELOCK_PATH),
    str(PHASE_539_TEST_PATH),
    str(TEST_PATH),
}
REQUIRED_HEADINGS = (
    '## 1. Prelock scope',
    '## 2. CDL-039 topology privacy lock',
    '## 3. Gossip propagation parameter lock',
    '## 4. Rejected scope expansions',
    '## 5. Ratification readiness',
)
REQUIRED_TOKENS = (
    'cdl_060_prelock_complete',
    'cdl_039_privacy_locked',
    'single_hop_scope_locked',
    'bounded_fanout_locked',
    'CDL-060 remains status: open in Phase 540.',
)
REJECTED_ITEMS = (
    'multi-hop centrality',
    'direct modification of CDL-036 row',
    'CDL-039 topology privacy relaxation',
    'gossip runtime implementation',
    'passive ECU attribution formula',
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


def _resolve_phase_540_commit_ref() -> str:
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
        if PHASE_540_SUBJECT_TOKEN not in subject.lower():
            continue
        matching.append(commit_hash)
    for commit_ref in matching:
        if _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS:
            return commit_ref
    if matching:
        raise AssertionError('phase_540_commit_subject_present_but_no_qualifying_prelock_commit')
    raise AssertionError('phase_540_commit_not_present_in_local_history')


def test_prelock_document_contains_required_headings() -> None:
    text = _read(PRELOCK_PATH)
    for heading in REQUIRED_HEADINGS:
        assert heading in text


def test_prelock_document_contains_required_governance_tokens() -> None:
    text = _read(PRELOCK_PATH)
    for token in REQUIRED_TOKENS:
        assert token in text


def test_prelock_document_explicitly_states_rejected_scope_expansions() -> None:
    text = _read(PRELOCK_PATH)
    for item in REJECTED_ITEMS:
        assert item in text


def test_phase_539_test_historicalization_patch_is_active() -> None:
    text = _read(PHASE_539_TEST_PATH)
    assert '# The Phase-539 CDL-060 open-state check is a historical prelock reference.' in text


def test_live_decision_log_preserves_required_statuses_and_absences() -> None:
    commit_ref = _resolve_phase_540_commit_ref()
    rows = parse_decision_register_rows(_commit_text(str(DECISION_LOG_PATH), commit_ref))
    # The Phase-540 CDL-060 open-state check is a historical prelock reference.
    assert rows['CDL-036']['status'] == 'ratified'
    assert rows['CDL-039']['status'] == 'ratified'
    assert rows['CDL-052']['status'] == 'ratified'
    assert rows['CDL-059']['status'] == 'ratified'
    assert rows['CDL-060']['status'] == 'open'
    assert 'CDL-053' not in rows


def test_phase_540_main_commit_touches_expected_paths_only() -> None:
    commit_ref = _resolve_phase_540_commit_ref()
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS


def test_phase_540_main_commit_does_not_touch_cdl_log_or_any_ilc_core_path() -> None:
    commit_ref = _resolve_phase_540_commit_ref()
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert not any(path.startswith('ilc_core/') for path in changed_paths)
