from __future__ import annotations

import subprocess
from pathlib import Path

COHERENCE_PATH = Path('docs/specs/ilc_integration_coherence_report_563_v0.1.md')
CAPSULE_PATH = Path('docs/specs/ilc_antigravity_context_capsule_v2.9.md')
TEST_PATH = Path('tests/test_phase_563_coherence_report_and_capsule.py')
DECISION_LOG_PATH = Path('docs/specs/ilc_constitutional_decision_log_v0.1.md')
PHASE_563_SUBJECT_TOKEN = 'phase 563 coherence report and capsule v2.9'
EXACT_REQUIRED_MAIN_PATHS = {
    str(COHERENCE_PATH),
    str(CAPSULE_PATH),
    str(TEST_PATH),
}
REQUIRED_HEADINGS = (
    '## 1. Window 555-564 summary',
    '## 2. CDL-061 ratification coherence',
    '## 3. Transport adapter dep chain',
    '## 4. Signal floor invariant closure (Phase 556)',
    '## 5. CDL-039 topology privacy enforcement surface',
    '## 6. Static peer registry scope and Window 565+ forward obligations',
    '## 7. Open items and forward obligations for Window 565-574',
)
REQUIRED_TOKENS = (
    'cdl_061_ratified_phase_561',
    'gossip_transport_dep_chain_cdl_060_to_cdl_061_complete',
    'signal_floor_invariant_documented_and_closed_phase_556',
    'static_peer_registry_v1_scope_no_dht',
    'cdl_039_topology_privacy_enforced_at_header_layer',
    'window_565_multi_machine_packaging_carry_forward',
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


def _resolve_phase_563_commit_ref() -> str:
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
        if 'phase 563' not in lowered or 'coherence' not in lowered:
            continue
        matching.append(commit_hash)
    for commit_ref in matching:
        if _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS:
            return commit_ref
    if matching:
        raise AssertionError('phase_563_commit_subject_present_but_no_qualifying_coherence_commit')
    raise AssertionError('phase_563_commit_not_present_in_local_history')


def test_coherence_report_contains_required_headings() -> None:
    text = _read(COHERENCE_PATH)
    for heading in REQUIRED_HEADINGS:
        assert heading in text


def test_coherence_report_contains_required_tokens() -> None:
    text = _read(COHERENCE_PATH)
    for token in REQUIRED_TOKENS:
        assert token in text


def test_capsule_v2_9_exists_and_supersedes_v2_8() -> None:
    text = _read(CAPSULE_PATH)
    assert CAPSULE_PATH.name == 'ilc_antigravity_context_capsule_v2.9.md'
    assert text.splitlines()[0] == '# ILC Antigravity Context Capsule v2.9'
    assert 'Supersedes: docs/specs/ilc_antigravity_context_capsule_v2.8.md' in text


def test_capsule_contains_cdl_061_ratification_and_adr_0025_note() -> None:
    text = _read(CAPSULE_PATH)
    assert 'CDL-061 (ILC gossip HTTP envelope — ratified Phase 561, http3_envelope_cbor + http2_fallback) is ratified.' in text
    assert 'ADR-0025 is Accepted.' in text


def test_phase_563_main_commit_touches_expected_paths_only() -> None:
    commit_ref = _resolve_phase_563_commit_ref()
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS


def test_phase_563_main_commit_does_not_touch_cdl_or_ilc_core() -> None:
    commit_ref = _resolve_phase_563_commit_ref()
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert not any(path.startswith('ilc_core/') for path in changed_paths)
