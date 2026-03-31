from __future__ import annotations

import subprocess
from pathlib import Path

from ilc_core.testing.ratification_mutation_scope_guardrail import parse_decision_register_rows

COHERENCE_PATH = Path('docs/specs/ilc_integration_coherence_report_543_v0.1.md')
CAPSULE_PATH = Path('docs/specs/ilc_antigravity_context_capsule_v2.7.md')
DECISION_LOG_PATH = Path('docs/specs/ilc_constitutional_decision_log_v0.1.md')
TEST_PATH = Path('tests/test_phase_543_coherence_report_and_capsule_v2_7.py')
PHASE_543_SUBJECT_TOKEN = 'phase 543 coherence report and capsule v2.7'
EXACT_REQUIRED_MAIN_PATHS = {
    str(COHERENCE_PATH),
    str(CAPSULE_PATH),
    str(TEST_PATH),
}
COHERENCE_HEADINGS = (
    '## 1. Window 535-544 summary',
    '## 2. CDL-060 lifecycle record',
    '## 3. Reuse centrality runtime advancement',
    '## 4. Simulation evidence chain',
    '## 5. Carry-forward obligations',
    '## 6. Snapshot isolation verification',
)
COHERENCE_TOKENS = (
    'CDL-060 was ratified in Phase 541.',
    'REUSE_CENTRALITY_RUNTIME_VERSION = "reuse_centrality_runtime_537.v0.1"',
    'U_FLOOR = 0.05',
    'computation_backend = "incremental_direct_use_v1"',
    'sim_centrality_02_sufficient',
    'sim_passive_ecu_01_sufficient',
    'Window 545+ must decide epoch-boundary commit semantics for `centrality_delta` accumulation',
    'must preserve the invariant `recommended_decay_floor >= recommended_u_floor`',
    'must also state attribution-cap application at the passive-ECU output layer',
    'CDL-053 remains reserved and unopened.',
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


def _resolve_phase_543_commit_ref() -> str:
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
        if PHASE_543_SUBJECT_TOKEN not in subject.lower():
            continue
        matching.append(commit_hash)
    for commit_ref in matching:
        if _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS:
            return commit_ref
    if matching:
        raise AssertionError('phase_543_commit_subject_present_but_no_qualifying_synthesis_commit')
    raise AssertionError('phase_543_commit_not_present_in_local_history')


def test_coherence_report_contains_required_headings_and_tokens() -> None:
    text = _read(COHERENCE_PATH)
    for heading in COHERENCE_HEADINGS:
        assert heading in text
    for token in COHERENCE_TOKENS:
        assert token in text


def test_capsule_v2_7_contains_current_window_marker() -> None:
    text = _read(CAPSULE_PATH)
    assert 'Supersedes: docs/specs/ilc_antigravity_context_capsule_v2.6.md' in text
    assert 'Window 535-544 remains active at Phase 543.' in text
    assert 'Phase 544 is the next authorized phase.' in text


def test_capsule_v2_7_contains_cdl_060_and_window_545_guidance() -> None:
    text = _read(CAPSULE_PATH)
    assert 'CDL-060 is ratified (Phase 541).' in text
    assert 'CDL-059 is ratified (Phase 531).' in text
    assert 'CDL-060 gossip runtime is a Window 545+ carry-forward via the D2d gossip surface.' in text
    assert 'Passive ECU attribution runtime is a Window 545+ carry-forward.' in text
    assert 'Multi-hop centrality remains a Window 545+ carry-forward.' in text
    assert 'Window 545+ must decide epoch-boundary commit semantics before the CDL-060 gossip runtime is' in text
    assert 'Signal-floor policy consistency beyond the aligned `0.05` floor remains a Window 545+' in text
    assert 'CDL-053 remains reserved and unopened.' in text


def test_live_decision_log_preserves_required_statuses_and_absences() -> None:
    rows = parse_decision_register_rows(_read(DECISION_LOG_PATH))
    # The Phase-543 CDL-060 inventory check will be historicalized when CDL-061 opens.
    assert rows['CDL-036']['status'] == 'ratified'
    assert rows['CDL-039']['status'] == 'ratified'
    assert rows['CDL-052']['status'] == 'ratified'
    assert rows['CDL-059']['status'] == 'ratified'
    assert rows['CDL-060']['status'] == 'ratified'
    assert 'CDL-053' not in rows


def test_exact_required_main_paths_contain_no_ilc_core_path() -> None:
    assert not any(path.startswith('ilc_core/') for path in EXACT_REQUIRED_MAIN_PATHS)


def test_phase_543_main_commit_touches_expected_paths_only() -> None:
    commit_ref = _resolve_phase_543_commit_ref()
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS


def test_phase_543_main_commit_does_not_touch_cdl_log_or_ilc_core() -> None:
    commit_ref = _resolve_phase_543_commit_ref()
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert not any(path.startswith('ilc_core/') for path in changed_paths)
