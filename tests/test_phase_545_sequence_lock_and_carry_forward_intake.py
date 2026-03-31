from __future__ import annotations

import subprocess
from pathlib import Path

from ilc_core.testing.ratification_mutation_scope_guardrail import parse_decision_register_rows

ARTIFACT_PATH = Path('docs/specs/ilc_phase_545_554_sequence_lock_v0.1.md')
DECISION_LOG_PATH = Path('docs/specs/ilc_constitutional_decision_log_v0.1.md')
PHASE_542_TEST_PATH = Path('tests/test_phase_542_sim_passive_ecu_01_attribution_formula.py')
TEST_PATH = Path('tests/test_phase_545_sequence_lock_and_carry_forward_intake.py')
PHASE_545_SUBJECT_TOKEN = 'phase 545 window 545-554 sequence lock'
EXACT_REQUIRED_MAIN_PATHS = {
    str(ARTIFACT_PATH),
    str(TEST_PATH),
}
REQUIRED_HEADINGS = (
    '## 1. Window identity',
    '## 2. Carry-forward freeze',
    '## 3. Non-goals',
    '## 4. Phase sequence and primary deliverables',
    '## 5. Entry conditions from Window 535-544',
)
REQUIRED_TOKENS = (
    'epoch_boundary_commit_semantics_required_before_cdl_060_gossip_runtime',
    'passive_ecu_runtime_depends_on_cdl_060_gossip_runtime',
    'CDL-053 remains reserved and unopened throughout Window 545-554.',
    'Phase 554 is the closure gate.',
    'sim_multi_hop_01_deferred',
    'phase_542_exact_value_assertions_confirmed',
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


def _resolve_phase_545_commit_ref() -> str:
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
        if PHASE_545_SUBJECT_TOKEN not in subject.lower():
            continue
        matching.append(commit_hash)
    for commit_ref in matching:
        if _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS:
            return commit_ref
    if matching:
        raise AssertionError('phase_545_commit_subject_present_but_no_qualifying_sequence_lock_commit')
    raise AssertionError('phase_545_commit_not_present_in_local_history')


def test_sequence_lock_artifact_exists_and_contains_required_headings() -> None:
    text = _read(ARTIFACT_PATH)
    for heading in REQUIRED_HEADINGS:
        assert heading in text


def test_sequence_lock_contains_required_tokens() -> None:
    text = _read(ARTIFACT_PATH)
    for token in REQUIRED_TOKENS:
        assert token in text


def test_sequence_lock_lists_all_ten_phases() -> None:
    text = _read(ARTIFACT_PATH)
    for phase in range(545, 555):
        assert f'| {phase} |' in text


def test_live_cdl_inventory_matches_entry_conditions() -> None:
    commit_ref = _resolve_phase_545_commit_ref()
    rows = parse_decision_register_rows(_commit_text(str(DECISION_LOG_PATH), commit_ref))
    assert rows['CDL-036']['status'] == 'ratified'
    assert rows['CDL-039']['status'] == 'ratified'
    assert rows['CDL-052']['status'] == 'ratified'
    assert rows['CDL-059']['status'] == 'ratified'
    assert rows['CDL-060']['status'] == 'ratified'
    assert 'CDL-053' not in rows
    # The Phase-545 CDL-061 absent check is a historical prelock reference.
    assert 'CDL-061' not in rows


def test_phase_542_exact_value_assertion_baseline_is_active() -> None:
    text = _read(PHASE_542_TEST_PATH)
    assert 'float(passive_rate_match.group(1)) == 0.20' in text
    assert 'float(decay_floor_match.group(1)) == 0.05' in text
    assert 'float(attribution_cap_match.group(1)) == 0.15' in text


def test_phase_545_main_commit_touches_expected_paths_only() -> None:
    commit_ref = _resolve_phase_545_commit_ref()
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS


def test_phase_545_main_commit_does_not_touch_cdl_log_or_any_ilc_core_path() -> None:
    commit_ref = _resolve_phase_545_commit_ref()
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert not any(path.startswith('ilc_core/') for path in changed_paths)
