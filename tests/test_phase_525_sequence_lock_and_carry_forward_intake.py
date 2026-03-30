from __future__ import annotations

import subprocess
from pathlib import Path

from ilc_core.testing.ratification_mutation_scope_guardrail import parse_decision_register_rows

ARTIFACT_PATH = Path('docs/specs/ilc_phase_525_534_sequence_lock_v0.1.md')
DECISION_LOG_PATH = Path('docs/specs/ilc_constitutional_decision_log_v0.1.md')
TEST_PATH = Path('tests/test_phase_525_sequence_lock_and_carry_forward_intake.py')
PHASE_525_SUBJECT_TOKEN = 'phase 525 window 525-534 sequence lock'
EXACT_REQUIRED_MAIN_PATHS = {
    str(ARTIFACT_PATH),
    str(TEST_PATH),
}
REQUIRED_HEADINGS = (
    '## 1. Window identity',
    '## 2. Carry-forward freeze',
    '## 3. Non-goals',
    '## 4. Phase sequence and primary deliverables',
    '## 5. Entry conditions from Window 515-524',
)
REQUIRED_TOKENS = (
    'SIM-AESTHETIC-01 is required before CDL-059 can be opened.',
    'CDL-059 opening requires Phase 528 synthesis authorization gate.',
    'CDL-053 remains reserved and unopened throughout Window 525-534.',
    'CDL-036 gossip schema amendment is a Window 535+ carry-forward.',
    'Phase 534 is the closure gate.',
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


def _commit_text(path: str, commit_ref: str) -> str:
    result = subprocess.run(
        ["git", "show", f"{commit_ref}:{path}"],
        capture_output=True,
        check=True,
        text=True,
    )
    return result.stdout


def _resolve_phase_525_commit_ref() -> str:
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
        if PHASE_525_SUBJECT_TOKEN not in subject.lower():
            continue
        matching.append(commit_hash)
    for commit_ref in matching:
        if _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS:
            return commit_ref
    if matching:
        raise AssertionError('phase_525_commit_subject_present_but_no_qualifying_sequence_lock_commit')
    raise AssertionError('phase_525_commit_not_present_in_local_history')


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
    for phase in range(525, 535):
        assert f'| {phase} |' in text


def _phase_525_decision_log_text() -> str:
    commit_ref = _resolve_phase_525_commit_ref()
    return _commit_text(str(DECISION_LOG_PATH), commit_ref)


def test_cdl_inventory_matches_entry_conditions() -> None:
    # The Phase-525 CDL-059 absent check is a historical prelock reference.
    rows = parse_decision_register_rows(_phase_525_decision_log_text())
    assert rows['CDL-055']['status'] == 'ratified'
    assert rows['CDL-056']['status'] == 'ratified'
    assert rows['CDL-057']['status'] == 'ratified'
    assert rows['CDL-058']['status'] == 'ratified'
    assert 'CDL-053' not in rows
    assert 'CDL-059' not in rows


def test_phase_525_live_tree_has_no_ilc_core_runtime_changes() -> None:
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


def test_phase_525_main_commit_touches_expected_paths_only() -> None:
    commit_ref = _resolve_phase_525_commit_ref()
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS


def test_phase_525_main_commit_does_not_touch_cdl_log_or_any_ilc_core_path() -> None:
    commit_ref = _resolve_phase_525_commit_ref()
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert not any(path.startswith('ilc_core/') for path in changed_paths)
