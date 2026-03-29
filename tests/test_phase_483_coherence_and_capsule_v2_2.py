from __future__ import annotations

import subprocess
from pathlib import Path

COHERENCE_PATH = Path('docs/specs/ilc_integration_coherence_report_483_v0.1.md')
CAPSULE_V21_PATH = Path('docs/specs/ilc_antigravity_context_capsule_v2.1.md')
CAPSULE_V22_PATH = Path('docs/specs/ilc_antigravity_context_capsule_v2.2.md')
TEST_PATH = Path('tests/test_phase_483_coherence_and_capsule_v2_2.py')
PHASE_483_SUBJECT_TOKEN = 'phase 483 coherence report and capsule v2.2'
EXACT_REQUIRED_MAIN_PATHS = {
    str(COHERENCE_PATH),
    str(CAPSULE_V22_PATH),
    str(TEST_PATH),
}


def _changed_paths_for_commit(commit_ref: str) -> set[str]:
    result = subprocess.run(
        ['git', 'show', '--name-only', '--pretty=', commit_ref],
        capture_output=True,
        check=True,
        text=True,
    )
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


def _resolve_phase_483_commit_ref() -> str:
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
        if PHASE_483_SUBJECT_TOKEN not in subject.lower():
            continue
        matching.append(commit_hash)
    for commit_ref in matching:
        if _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS:
            return commit_ref
    if matching:
        raise AssertionError('phase_483_commit_subject_present_but_no_qualifying_coherence_commit')
    raise AssertionError('phase_483_commit_not_present_in_local_history')


def test_coherence_report_exists_and_contains_required_headings_and_tokens() -> None:
    text = COHERENCE_PATH.read_text(encoding='utf-8')
    for heading in (
        '## 1. Window 475-484 completion state',
        '## 2. CDL-052 epistemic runtime status',
        '## 3. Genesis validator bootstrap status',
        '## 4. Constitutional consistency check',
        '## 5. Deferred items carry-forward',
    ):
        assert heading in text
    for token in (
        'CDL-052 epistemic evaluation runtime is complete within the authorized scope of Window 475-484.',
        'Genesis validator bootstrap runtime is complete within the authorized scope of Window 475-484.',
        'No decision-log mutation occurred in Window 475-484.',
    ):
        assert token in text


def test_capsule_v2_2_exists_supersedes_v2_1_and_contains_required_headings() -> None:
    text = CAPSULE_V22_PATH.read_text(encoding='utf-8')
    assert 'Supersedes: docs/specs/ilc_antigravity_context_capsule_v2.1.md' in text
    for heading in (
        '## 1. Current window state',
        '## 2. CDL status summary',
        '## 3. Window 469-474 retroactive summary',
        '## 4. Window 475-484 summary',
        '## 5. ADR-0022 disposition',
        '## 6. Deferred items',
    ):
        assert heading in text


def test_capsule_v2_2_contains_window_469_474_retroactive_summary_section() -> None:
    text = CAPSULE_V22_PATH.read_text(encoding='utf-8')
    assert 'Capsule v2.1 covered Window 460-468 only and did not reflect Window 469-474 deliverables.' in text
    assert 'Capsule v2.2 retroactively records the Window 469-474 completion state.' in text
    assert 'Window 469-474 is closed.' in text


def test_capsule_v2_2_section_5_addresses_adr_0022() -> None:
    text = CAPSULE_V22_PATH.read_text(encoding='utf-8')
    section = text.split('## 5. ADR-0022 disposition', 1)[1].split('## 6. Deferred items', 1)[0]
    assert 'ADR-0022 remains the active local-first and private-use boundary.' in section
    assert 'CDL-053 is not activated by Window 475-484 and remains a separate future constitutional lane.' in section
    assert 'Shard-header hardening, access-right hardening, and rights/licensing hardening remain future' in section


def test_capsule_v2_1_is_not_modified_and_remains_historical() -> None:
    text = CAPSULE_V21_PATH.read_text(encoding='utf-8')
    assert 'Window 460-468 is active.' in text
    assert 'Phase 467 is the next authorized phase.' in text
    assert 'Window 469-474' not in text


def test_phase_483_main_commit_touches_expected_paths_and_not_ilc_core() -> None:
    commit_ref = _resolve_phase_483_commit_ref()
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert changed_paths == EXACT_REQUIRED_MAIN_PATHS
    assert all(not path.startswith('ilc_core/') for path in changed_paths)


def test_phase_483_main_commit_does_not_touch_decision_log() -> None:
    commit_ref = _resolve_phase_483_commit_ref()
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert 'docs/specs/ilc_constitutional_decision_log_v0.1.md' not in changed_paths
