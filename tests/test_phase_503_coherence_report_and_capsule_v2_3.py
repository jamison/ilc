from __future__ import annotations

import subprocess
from pathlib import Path

COHERENCE_PATH = Path('docs/specs/ilc_integration_coherence_report_503_v0.1.md')
CAPSULE_V22_PATH = Path('docs/specs/ilc_antigravity_context_capsule_v2.2.md')
CAPSULE_V23_PATH = Path('docs/specs/ilc_antigravity_context_capsule_v2.3.md')
DECISION_LOG_PATH = Path('docs/specs/ilc_constitutional_decision_log_v0.1.md')
TEST_PATH = Path('tests/test_phase_503_coherence_report_and_capsule_v2_3.py')
PHASE_503_SUBJECT_TOKEN = 'phase 503 coherence report and capsule v2.3'
EXACT_REQUIRED_MAIN_PATHS = {
    str(COHERENCE_PATH),
    str(CAPSULE_V23_PATH),
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


def _resolve_phase_503_commit_ref() -> str:
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
        if PHASE_503_SUBJECT_TOKEN not in subject.lower():
            continue
        matching.append(commit_hash)
    for commit_ref in matching:
        if _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS:
            return commit_ref
    if matching:
        raise AssertionError('phase_503_commit_subject_present_but_no_qualifying_coherence_commit')
    raise AssertionError('phase_503_commit_not_present_in_local_history')


def test_coherence_report_exists_and_contains_required_headings_and_tokens() -> None:
    text = COHERENCE_PATH.read_text(encoding='utf-8')
    for heading in (
        '## 1. Window summary',
        '## 2. CDL-055/056 integration review',
        '## 3. ADM-001 v0.3 integration',
        '## 4. Deferred carry-forwards',
        '## 5. Snapshot isolation proof',
    ):
        assert heading in text
    for token in (
        'CDL-053 remains deferred and reserved.',
        'Epoch-boundary CDL amendment is a Window 505+ carry-forward.',
        'CDL-055 and CDL-056 are ratified at Window 495-504 close.',
        'ADM-001 v0.3 is published at Window 495-504 close.',
    ):
        assert token in text


def test_capsule_v2_3_exists_supersedes_v2_2_and_contains_required_headings() -> None:
    text = CAPSULE_V23_PATH.read_text(encoding='utf-8')
    assert 'Supersedes: docs/specs/ilc_antigravity_context_capsule_v2.2.md' in text
    for heading in (
        '## 1. Current window state',
        '## 2. CDL status summary',
        '## 3. Window 495-504 summary',
        '## 4. Carry-forward items',
        '## 5. ADR-0022 and separate future lanes',
        '## 6. Next window state',
    ):
        assert heading in text


def test_capsule_v2_3_contains_required_tokens() -> None:
    text = CAPSULE_V23_PATH.read_text(encoding='utf-8')
    for token in (
        'Capsule v2.3 supersedes v2.2.',
        'CDL-055 ratified Phase 496.',
        'CDL-056 ratified Phase 501.',
        'ADM-001 v0.3 published Phase 502.',
        'validator enhancement roadmap carry-forward obligation acknowledged.',
        'CDL-055 runtime implementation is deferred to Window 505+.',
        'CDL-053 Werner credit architecture remains reserved and separate from validator work.',
    ):
        assert token in text


def test_coherence_report_and_capsule_reference_roadmap_and_adr_0022_boundaries() -> None:
    coherence = COHERENCE_PATH.read_text(encoding='utf-8')
    capsule = CAPSULE_V23_PATH.read_text(encoding='utf-8')
    assert 'validator enhancement roadmap remains the active planning source' in coherence
    assert 'ADR-0022 remains the active local-first and private-use boundary.' in capsule
    assert 'private/gated shard rights/access hardening lane remains separate' in capsule


def test_capsule_v2_2_remains_historical() -> None:
    text = CAPSULE_V22_PATH.read_text(encoding='utf-8')
    assert 'Capsule v2.1 covered Window 460-468 only and did not reflect Window 469-474 deliverables.' in text
    assert 'Capsule v2.3 supersedes v2.2.' not in text


def test_phase_503_main_commit_touches_expected_paths_only() -> None:
    commit_ref = _resolve_phase_503_commit_ref()
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS


def test_phase_503_main_commit_does_not_touch_decision_log_or_ilc_core() -> None:
    commit_ref = _resolve_phase_503_commit_ref()
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert all(not path.startswith('ilc_core/') for path in changed_paths)
