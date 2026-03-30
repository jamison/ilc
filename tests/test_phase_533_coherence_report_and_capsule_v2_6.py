from __future__ import annotations

import subprocess
from pathlib import Path

from ilc_core.testing.ratification_mutation_scope_guardrail import (
    assert_head_commit_touched_no_runtime_files,
    parse_decision_register_rows,
)

COHERENCE_PATH = Path('docs/specs/ilc_integration_coherence_report_533_v0.1.md')
CAPSULE_PATH = Path('docs/specs/ilc_antigravity_context_capsule_v2.6.md')
DECISION_LOG_PATH = Path('docs/specs/ilc_constitutional_decision_log_v0.1.md')
TEST_PATH = Path('tests/test_phase_533_coherence_report_and_capsule_v2_6.py')
PHASE_533_SUBJECT_TOKEN = 'phase 533 coherence report and capsule v2.6'
EXACT_REQUIRED_MAIN_PATHS = {
    str(COHERENCE_PATH),
    str(CAPSULE_PATH),
    str(TEST_PATH),
}
COHERENCE_HEADINGS = (
    '## 1. Simulation evidence chain',
    '## 2. CDL-059 lifecycle status',
    '## 3. Aesthetic panel runtime integration',
    '## 4. Deferred item boundaries',
    '## 5. Snapshot isolation',
)
COHERENCE_TOKENS = (
    'Window 525-534 remains active at Phase 533.',
    'CDL-059 lifecycle complete through Phase 532.',
    'Aesthetic panel runtime is implemented in Phase 532.',
    'CDL-036 gossip schema amendment remains a Window 535+ carry-forward.',
    'passive_ecu_attribution_formula_deferred',
    'CDL-053 remains reserved and unopened.',
    'No ilc_core/ mutation occurs in Phase 533.',
    'No decision-log mutation occurs in Phase 533.',
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


def _resolve_phase_533_commit_ref() -> str:
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
        if PHASE_533_SUBJECT_TOKEN not in subject.lower():
            continue
        matching.append(commit_hash)
    for commit_ref in matching:
        if _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS:
            return commit_ref
    if matching:
        raise AssertionError('phase_533_commit_subject_present_but_no_qualifying_synthesis_commit')
    raise AssertionError('phase_533_commit_not_present_in_local_history')


def test_coherence_report_contains_required_headings_and_tokens() -> None:
    text = _read(COHERENCE_PATH)
    for heading in COHERENCE_HEADINGS:
        assert heading in text
    for token in COHERENCE_TOKENS:
        assert token in text


def test_capsule_v2_6_supersedes_v2_5() -> None:
    text = _read(CAPSULE_PATH)
    assert 'Supersedes: docs/specs/ilc_antigravity_context_capsule_v2.5.md' in text
    assert 'Capsule v2.6 supersedes v2.5.' in text
    assert 'Window 525-534 remains active at Phase 533.' in text
    assert 'Phase 534 is the next authorized phase.' in text


def test_capsule_v2_6_contains_required_carry_forward_items() -> None:
    text = _read(CAPSULE_PATH)
    assert 'CDL-059 is ratified.' in text
    assert 'CDL-053 remains reserved and unopened.' in text
    assert 'CDL-036 gossip schema amendment remains a Window 535+ carry-forward.' in text
    assert 'Passive ECU attribution formula remains a Window 535+ carry-forward.' in text
    assert 'Multi-hop centrality remains a Window 535+ carry-forward.' in text


def test_live_decision_log_preserves_required_statuses_and_absences() -> None:
    rows = parse_decision_register_rows(_read(DECISION_LOG_PATH))
    assert rows['CDL-055']['status'] == 'ratified'
    assert rows['CDL-056']['status'] == 'ratified'
    assert rows['CDL-057']['status'] == 'ratified'
    assert rows['CDL-058']['status'] == 'ratified'
    assert rows['CDL-059']['status'] == 'ratified'
    assert 'CDL-053' not in rows


def test_head_commit_touches_no_runtime_files() -> None:
    commit_ref = _resolve_phase_533_commit_ref()
    assert_head_commit_touched_no_runtime_files(commit_ref=commit_ref)


def test_phase_533_main_commit_touches_expected_paths_only() -> None:
    commit_ref = _resolve_phase_533_commit_ref()
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS


def test_phase_533_main_commit_does_not_touch_cdl_log_or_ilc_core() -> None:
    commit_ref = _resolve_phase_533_commit_ref()
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert not any(path.startswith('ilc_core/') for path in changed_paths)
