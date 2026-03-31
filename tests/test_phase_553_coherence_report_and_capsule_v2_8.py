from __future__ import annotations

import subprocess
from pathlib import Path

from ilc_core.testing.ratification_mutation_scope_guardrail import parse_decision_register_rows

COHERENCE_PATH = Path('docs/specs/ilc_integration_coherence_report_553_v0.1.md')
CAPSULE_PATH = Path('docs/specs/ilc_antigravity_context_capsule_v2.8.md')
DECISION_LOG_PATH = Path('docs/specs/ilc_constitutional_decision_log_v0.1.md')
TEST_PATH = Path('tests/test_phase_553_coherence_report_and_capsule_v2_8.py')
PHASE_553_SUBJECT_TOKEN = 'phase 553 coherence report and capsule v2.8'
EXACT_REQUIRED_MAIN_PATHS = {
    str(COHERENCE_PATH),
    str(CAPSULE_PATH),
    str(TEST_PATH),
}
COHERENCE_HEADINGS = (
    '## 1. Window 545-554 summary',
    '## 2. CDL-060 gossip runtime record',
    '## 3. Passive ECU attribution runtime record',
    '## 4. Simulation evidence chain',
    '## 5. Signal-floor policy disposition',
    '## 6. Carry-forward obligations',
    '## 7. Snapshot isolation verification',
)
CAPSULE_HEADINGS = (
    '## 1. Current window state',
    '## 2. CDL status summary',
    '## 3. Window 545-554 summary',
    '## 4. Carry-forward items',
    '## 5. Separate lanes',
    '## 6. Next window state',
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


def _resolve_phase_553_commit_ref() -> str:
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
        if PHASE_553_SUBJECT_TOKEN not in subject.lower():
            continue
        matching.append(commit_hash)
    for commit_ref in matching:
        if _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS:
            return commit_ref
    raise AssertionError('phase_553_commit_not_present_in_local_history')


def test_coherence_report_exists_and_contains_all_required_section_headings() -> None:
    text = _read(COHERENCE_PATH)
    for heading in COHERENCE_HEADINGS:
        assert heading in text


def test_capsule_v2_8_exists_and_contains_all_required_section_headings() -> None:
    text = _read(CAPSULE_PATH)
    for heading in CAPSULE_HEADINGS:
        assert heading in text


def test_capsule_v2_8_contains_required_section_1_text() -> None:
    text = _read(CAPSULE_PATH)
    assert 'Capsule v2.8 supersedes v2.7.' in text
    assert 'Window 545-554 remains active at Phase 553.' in text
    assert 'Phase 554 is the next authorized phase.' in text


def test_coherence_report_contains_both_runtime_version_strings() -> None:
    text = _read(COHERENCE_PATH)
    assert 'CDL_060_GOSSIP_RUNTIME_VERSION = "cdl_060_gossip_runtime_548.v0.1"' in text
    assert 'PASSIVE_ECU_ATTRIBUTION_RUNTIME_VERSION = "passive_ecu_attribution_runtime_550.v0.1"' in text


def test_live_decision_log_preserves_required_statuses_and_absences() -> None:
    rows = parse_decision_register_rows(_read(DECISION_LOG_PATH))
    assert rows['CDL-036']['status'] == 'ratified'
    assert rows['CDL-039']['status'] == 'ratified'
    assert rows['CDL-052']['status'] == 'ratified'
    assert rows['CDL-059']['status'] == 'ratified'
    assert rows['CDL-060']['status'] == 'ratified'
    assert 'CDL-053' not in rows
    # The Phase-553 CDL-061 absent check will be historicalized when CDL-061 opens.
    assert 'CDL-061' not in rows


def test_phase_553_main_commit_touches_expected_paths_only() -> None:
    commit_ref = _resolve_phase_553_commit_ref()
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS


def test_phase_553_main_commit_does_not_touch_cdl_log_or_any_ilc_core_path() -> None:
    commit_ref = _resolve_phase_553_commit_ref()
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert not any(path.startswith('ilc_core/') for path in changed_paths)
