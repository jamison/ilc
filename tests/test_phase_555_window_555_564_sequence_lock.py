from __future__ import annotations

import re
import subprocess
from pathlib import Path

SEQ_LOCK_PATH = Path('docs/specs/ilc_phase_555_564_sequence_lock_v0.1.md')
DECISION_LOG_PATH = Path('docs/specs/ilc_constitutional_decision_log_v0.1.md')
TEST_PATH = Path('tests/test_phase_555_window_555_564_sequence_lock.py')
PHASE_555_SUBJECT_TOKEN = 'phase 555 window 555-564 sequence lock'
EXACT_REQUIRED_MAIN_PATHS = {
    str(SEQ_LOCK_PATH),
    str(TEST_PATH),
}
REQUIRED_HEADINGS = (
    '## 1. Window summary',
    '## 2. Phase table',
    '## 3. CDL track',
    '## 4. Architectural decisions locked',
    '## 5. Carry-forward tokens from Window 545-554',
    '## 6. Non-negotiable constraints',
    '## 7. Sequence integrity rule',
)
REQUIRED_TOKENS = (
    'gossip_transport_http3_binding_selected',
    'cdl_061_gossip_http_envelope_to_open_phase_557',
    'adr_023_invariant_update_phase_556',
    'kind_quic_http3_production_kind_http_http2_fallback',
    'cdl_061_ratification_after_implementation',
    'static_peer_config_no_dht_v1',
)
CARRY_FORWARD_TOKENS = (
    'phase_547_adr_023_invariant_obligation',
    'phase_548_1_epoch_attribution_lag_design_property',
    'phase_548_crash_recovery_graceful_zero',
    'cdl_061_prelock_dep_token',
)
EXPECTED_PHASE_ROWS = (
    '| 555 | Window 555-564 sequence lock | `ilc_phase_555_564_sequence_lock_v0.1.md` | No |',
    '| 556 | ADR-0023 signal floor invariant update | Updated `ADR_0023_Multi_Layer_Quality_Signal_Architecture.md` | No |',
    '| 557 | CDL-061 open + prelock (gossip HTTP envelope) | CDL row + `ilc_cdl_061_gossip_http_envelope_prelock_557_v0.1.md` | YES |',
    '| 558 | HTTP gossip transport adapter | `ilc_core/network/d2d/gossip_transport.py` | YES |',
    '| 559 | Transport adapter hardening | `tests/test_phase_559_gossip_transport_hardening.py` + canary update | No |',
    '| 560 | Canary probes for transport-layer invariants | Updated `tools/run_mutation_canary_phase_297.py` | No |',
    '| 561 | CDL-061 ratification | CDL row update + dep-chain update in `gossip_transport.py` | YES |',
    '| 562 | Static peer registry | `ilc_core/network/d2d/gossip_peer_registry.py` | YES |',
    '| 563 | Coherence report + capsule v2.9 | `ilc_integration_coherence_report_563_v0.1.md` + capsule | No |',
    '| 564 | Window 555-564 closure gate + handoff | Gate script + handoff doc | YES |',
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


def _resolve_phase_555_commit_ref() -> str:
    result = subprocess.run(
        ['git', 'log', '--format=%H%x09%s'],
        capture_output=True,
        check=True,
        text=True,
    )
    matches: list[str] = []
    for line in result.stdout.splitlines():
        if '\t' not in line:
            continue
        commit_hash, subject = line.split('\t', 1)
        if PHASE_555_SUBJECT_TOKEN not in subject.lower():
            continue
        matches.append(commit_hash)
    for commit_ref in matches:
        if _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS:
            return commit_ref
    raise AssertionError('phase_555_commit_not_present_in_local_history')


def test_sequence_lock_document_exists_and_contains_required_section_headings() -> None:
    text = _read(SEQ_LOCK_PATH)
    for heading in REQUIRED_HEADINGS:
        assert heading in text


def test_sequence_lock_document_contains_required_tokens() -> None:
    text = _read(SEQ_LOCK_PATH)
    for token in REQUIRED_TOKENS:
        assert token in text


def test_phase_table_contains_exactly_ten_rows_for_phases_555_564_in_order() -> None:
    text = _read(SEQ_LOCK_PATH)
    rows = tuple(re.findall(r'^\| 55\d .*$', text, flags=re.MULTILINE)) + tuple(
        re.findall(r'^\| 56[0-4] .*$', text, flags=re.MULTILINE)
    )
    assert rows == EXPECTED_PHASE_ROWS


def test_carry_forward_section_enumerates_all_four_required_items() -> None:
    text = _read(SEQ_LOCK_PATH)
    for token in CARRY_FORWARD_TOKENS:
        assert token in text


def test_phase_555_commit_touches_expected_paths_only() -> None:
    commit_ref = _resolve_phase_555_commit_ref()
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS


def test_phase_555_commit_leaves_cdl_log_and_ilc_core_untouched() -> None:
    commit_ref = _resolve_phase_555_commit_ref()
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert not any(path.startswith('ilc_core/') for path in changed_paths)
