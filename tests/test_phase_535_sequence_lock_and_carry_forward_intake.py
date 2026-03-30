from __future__ import annotations

import subprocess
from pathlib import Path

from ilc_core.testing.ratification_mutation_scope_guardrail import parse_decision_register_rows

ARTIFACT_PATH = Path('docs/specs/ilc_phase_535_544_sequence_lock_v0.1.md')
DECISION_LOG_PATH = Path('docs/specs/ilc_constitutional_decision_log_v0.1.md')
TEST_PATH = Path('tests/test_phase_535_sequence_lock_and_carry_forward_intake.py')
PHASE_535_SUBJECT_TOKEN = 'phase 535 window 535-544 sequence lock'
EXACT_REQUIRED_MAIN_PATHS = {
    str(ARTIFACT_PATH),
    str(TEST_PATH),
}
REQUIRED_HEADINGS = (
    '## 1. Window identity',
    '## 2. Carry-forward freeze',
    '## 3. Non-goals',
    '## 4. Phase sequence and primary deliverables',
    '## 5. Entry conditions from Window 525-534',
)
REQUIRED_TOKENS = (
    'SIM-CENTRALITY-02 is required before CDL-060 can be opened.',
    'CDL-060 opening requires Phase 538 simulation calibration gate.',
    'CDL-053 remains reserved and unopened throughout Window 535-544.',
    'CDL-060 gossip runtime is a Window 545+ carry-forward.',
    'Phase 544 is the closure gate.',
    'multi_hop_centrality_deferred',
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


def _resolve_phase_535_commit_ref() -> str:
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
        if PHASE_535_SUBJECT_TOKEN not in subject.lower():
            continue
        matching.append(commit_hash)
    for commit_ref in matching:
        if _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS:
            return commit_ref
    if matching:
        raise AssertionError('phase_535_commit_subject_present_but_no_qualifying_sequence_lock_commit')
    raise AssertionError('phase_535_commit_not_present_in_local_history')


def test_sequence_lock_artifact_contains_required_headings() -> None:
    text = _read(ARTIFACT_PATH)
    for heading in REQUIRED_HEADINGS:
        assert heading in text


def test_sequence_lock_artifact_contains_required_tokens() -> None:
    text = _read(ARTIFACT_PATH)
    for token in REQUIRED_TOKENS:
        assert token in text


def test_sequence_lock_lists_all_ten_phases() -> None:
    text = _read(ARTIFACT_PATH)
    for phase in range(535, 545):
        assert f'| {phase} |' in text


def test_cdl_inventory_matches_entry_conditions() -> None:
    rows = parse_decision_register_rows(_read(DECISION_LOG_PATH))
    assert rows['CDL-036']['status'] == 'ratified'
    assert rows['CDL-039']['status'] == 'ratified'
    assert rows['CDL-052']['status'] == 'ratified'
    assert rows['CDL-059']['status'] == 'ratified'
    assert 'CDL-053' not in rows
    # The Phase-535 CDL-060 absent check will be historicalized when Phase 539 opens CDL-060.
    assert 'CDL-060' not in rows


def test_exact_required_main_paths_contain_no_ilc_core_path() -> None:
    assert not any(path.startswith('ilc_core/') for path in EXACT_REQUIRED_MAIN_PATHS)


def test_phase_535_main_commit_touches_expected_paths_only() -> None:
    commit_ref = _resolve_phase_535_commit_ref()
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS


def test_phase_535_main_commit_does_not_touch_cdl_log_or_any_ilc_core_path() -> None:
    commit_ref = _resolve_phase_535_commit_ref()
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert not any(path.startswith('ilc_core/') for path in changed_paths)
