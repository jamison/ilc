from __future__ import annotations

import subprocess
from pathlib import Path

from ilc_core.testing.ratification_mutation_scope_guardrail import parse_decision_register_rows

ARTIFACT_PATH = Path('docs/specs/ilc_phase_475_484_sequence_lock_v0.1.md')
DECISION_LOG_PATH = Path('docs/specs/ilc_constitutional_decision_log_v0.1.md')
TEST_PATH = Path('tests/test_phase_475_window_sequence_lock.py')
PHASE_475_SUBJECT_TOKEN = 'phase 475 window 475-484 sequence lock and scope freeze'
EXACT_REQUIRED_MAIN_PATHS = {
    str(ARTIFACT_PATH),
    str(TEST_PATH),
}
REQUIRED_HEADINGS = (
    '## 1. Window identity',
    '## 2. Scope freeze',
    '## 3. Non-goals',
    '## 4. Phase sequence and gate dependencies',
    '## 5. Entry conditions from Window 469-474',
)
REQUIRED_TOKENS = (
    'Window 475-484 is open as of Phase 475.',
    'Track B covers CDL-052 epistemic evaluation runtime (Phases 476-478).',
    'Track C covers genesis validator bootstrap (Phases 479-481).',
    'Mode 3 auditor-review execution hooks are out of scope for Window 475-484.',
    'Staking constants remain TBD pending a future simulation lane.',
    'Validator network join and recovery flow is out of scope for Window 475-484.',
    'Phase 483 capsule v2.2 must cover Window 469-474 deliverables retroactively.',
    'No decision-log mutation occurs in Phase 475.',
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
        ['git', 'show', f'{commit_ref}:{path}'],
        capture_output=True,
        check=True,
        text=True,
    )
    return result.stdout


def _resolve_phase_475_commit_ref() -> str:
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
        if PHASE_475_SUBJECT_TOKEN not in subject.lower():
            continue
        matching.append(commit_hash)
    for commit_ref in matching:
        if _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS:
            return commit_ref
    if matching:
        raise AssertionError('phase_475_commit_subject_present_but_no_qualifying_sequence_lock_commit')
    raise AssertionError('phase_475_commit_not_present_in_local_history')


def test_sequence_lock_artifact_exists_and_contains_required_headings() -> None:
    text = _read(ARTIFACT_PATH)
    for heading in REQUIRED_HEADINGS:
        assert heading in text


def test_sequence_lock_artifact_contains_required_tokens() -> None:
    text = _read(ARTIFACT_PATH)
    for token in REQUIRED_TOKENS:
        assert token in text


def test_phase_table_lists_all_ten_phases_and_spec_before_runtime_rules() -> None:
    text = _read(ARTIFACT_PATH)
    for phase in range(475, 485):
        assert f'| {phase} |' in text
    assert 'Phase 476 must complete before Phases 477-478' in text
    assert 'Phase 479 must complete before Phases 480-481' in text


def test_entry_conditions_record_prior_window_closure_and_capsule_presence() -> None:
    text = _read(ARTIFACT_PATH)
    assert 'Window 469-474 is closed.' in text
    assert '`docs/specs/ilc_antigravity_context_capsule_v2.1.md` exists.' in text


def test_phase_475_main_commit_snapshot_preserves_cdl_inventory_and_expected_paths() -> None:
    commit_ref = _resolve_phase_475_commit_ref()
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert changed_paths == EXACT_REQUIRED_MAIN_PATHS
    assert str(DECISION_LOG_PATH) not in changed_paths
    rows = parse_decision_register_rows(_commit_text(str(DECISION_LOG_PATH), commit_ref))
    assert rows['CDL-050']['status'] == 'ratified'
    assert rows['CDL-051']['status'] == 'ratified'
    assert rows['CDL-052']['status'] == 'ratified'
    assert 'CDL-053' not in rows


def test_phase_475_main_commit_does_not_touch_ilc_core() -> None:
    commit_ref = _resolve_phase_475_commit_ref()
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert not any(path.startswith('ilc_core/') for path in changed_paths)
