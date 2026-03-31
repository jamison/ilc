from __future__ import annotations

import subprocess
from pathlib import Path

from ilc_core.testing.ratification_mutation_scope_guardrail import parse_decision_register_rows

EVIDENCE_PATH = Path('docs/specs/ilc_cdl_061_gossip_http_envelope_ratification_evidence_561_v0.1.md')
DECISION_LOG_PATH = Path('docs/specs/ilc_constitutional_decision_log_v0.1.md')
TRANSPORT_PATH = Path('ilc_core/network/d2d/gossip_transport.py')
CANARY_PATH = Path('tools/run_mutation_canary_phase_297.py')
PHASE_557_TEST_PATH = Path('tests/test_phase_557_cdl_061_prelock.py')
PHASE_558_TEST_PATH = Path('tests/test_phase_558_gossip_transport_adapter.py')
TEST_PATH = Path('tests/test_phase_561_cdl_061_ratification.py')
RUNTIME_COMMIT_PATHS = {
    str(TRANSPORT_PATH),
    str(CANARY_PATH),
    str(PHASE_557_TEST_PATH),
    str(PHASE_558_TEST_PATH),
    str(TEST_PATH),
    str(EVIDENCE_PATH),
}
CDL_COMMIT_PATHS = {str(DECISION_LOG_PATH)}
REQUIRED_HEADINGS = (
    '## 1. CDL-061 ratification summary',
    '## 2. Candidate form selected',
    '## 3. Implementation evidence',
    '## 4. CDL-039 enforcement evidence',
    '## 5. CDL-060 hop-count enforcement evidence',
    '## 6. Status code semantics evidence',
    '## 7. Ratification readiness evidence checklist satisfaction',
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


def _resolve_phase_561_runtime_commit_ref() -> str:
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
        lowered = subject.lower()
        if 'phase 561' not in lowered:
            continue
        if 'runtime dep chain and canary' not in lowered:
            continue
        matching.append(commit_hash)
    for commit_ref in matching:
        if _changed_paths_for_commit(commit_ref) == RUNTIME_COMMIT_PATHS:
            return commit_ref
    if matching:
        raise AssertionError('phase_561_commit_subject_present_but_no_qualifying_runtime_commit')
    raise AssertionError('phase_561_commit_not_present_in_local_history')


def _resolve_phase_561_cdl_commit_ref() -> str:
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
        lowered = subject.lower()
        if 'phase 561' not in lowered or 'cdl-061' not in lowered:
            continue
        matching.append(commit_hash)
    for commit_ref in matching:
        if _changed_paths_for_commit(commit_ref) == CDL_COMMIT_PATHS:
            return commit_ref
    if matching:
        raise AssertionError('phase_561_commit_subject_present_but_no_qualifying_cdl_commit')
    raise AssertionError('phase_561_commit_not_present_in_local_history')


def test_cdl_061_is_ratified_in_live_decision_log() -> None:
    rows = parse_decision_register_rows(_read(DECISION_LOG_PATH))
    assert rows['CDL-061']['status'] == 'ratified'
    assert rows['CDL-061']['ratified_phase'] == '561'
    assert rows['CDL-061']['evidence_document'] == str(EVIDENCE_PATH)


def test_ratification_evidence_artifact_contains_required_headings() -> None:
    text = _read(EVIDENCE_PATH)
    for heading in REQUIRED_HEADINGS:
        assert heading in text


def test_ratification_evidence_artifact_contains_required_governance_token() -> None:
    assert 'cdl_061_ratification_evidence_complete' in _read(EVIDENCE_PATH)


def test_gossip_transport_dep_string_is_ratified_token() -> None:
    text = _read(TRANSPORT_PATH)
    assert 'CDL_061_DEPENDENCY = "cdl_061_ratified_561.v0.1"' in text
    assert 'CDL_061_DEPENDENCY = "cdl_061_prelock_557.v0.1"' not in text


def test_phase_557_prelock_test_is_historicalized() -> None:
    assert '# The Phase-557 CDL-061 open-state check is a historical prelock reference.' in _read(PHASE_557_TEST_PATH)


def test_phase_561_runtime_commit_touches_expected_paths_only() -> None:
    commit_ref = _resolve_phase_561_runtime_commit_ref()
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert changed_paths == RUNTIME_COMMIT_PATHS
    assert str(DECISION_LOG_PATH) not in changed_paths


def test_phase_561_cdl_commit_touches_only_decision_log() -> None:
    commit_ref = _resolve_phase_561_cdl_commit_ref()
    assert _changed_paths_for_commit(commit_ref) == CDL_COMMIT_PATHS
