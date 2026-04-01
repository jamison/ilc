from __future__ import annotations

import subprocess
from pathlib import Path

SEQ_LOCK_PATH = Path('docs/specs/ilc_phase_565_574_sequence_lock_v0.1.md')
DECISION_LOG_PATH = Path('docs/specs/ilc_constitutional_decision_log_v0.1.md')
TEST_PATH = Path('tests/test_phase_565_window_565_574_sequence_lock.py')
PHASE_565_SUBJECT_TOKEN = 'phase 565 window 565-574 sequence lock'
EXACT_REQUIRED_MAIN_PATHS = {
    str(SEQ_LOCK_PATH),
    str(TEST_PATH),
}
REQUIRED_HEADINGS = (
    '## 1. Window summary',
    '## 2. Hard pass condition',
    '## 3. Phase table',
    '## 4. Locked implementation decisions',
    '## 5. Carry-forward inputs from Window 555-564',
    '## 6. Protected boundaries and anti-pattern exclusions',
    '## 7. Sequence integrity rule',
)
REQUIRED_TOKENS = (
    'three_machine_http_transport_primary_gate',
    'packaging_and_genesis_secondary_lane',
    'json_static_peer_config_v1',
    'http2_fallback_explicit_config_only',
    'server_tls_plus_ilc_signature_testbed_v1',
    'node_orchestration_redesign_deferred_post_574',
    'http_machine_payment_skill_deferred_to_575_584',
    'http_machine_payment_ingress_deferred_to_595_plus',
)
CARRY_FORWARD_ITEMS = (
    'CDL-061 remains ratified and bounded to the envelope contract only.',
    '`gossip_transport.py` remains the canonical envelope helper surface.',
    '`gossip_peer_registry.py` remains `static_v1` with no DHT or dynamic discovery.',
    '`recommended_decay_floor >= recommended_u_floor` remains documented in ADR-0023.',
    'Multi-hop remains deferred under `sim_multi_hop_01_insufficient`.',
)
EXPECTED_PHASE_ROWS = (
    '| 565 | Window 565-574 sequence lock | `ilc_phase_565_574_sequence_lock_v0.1.md` | No |',
    '| 566 | Transport operationalization boundary lock | `ilc_transport_operationalization_boundary_lock_566_v0.1.md` | No |',
    '| 567 | Genesis, package, and lifecycle scoping | `ilc_genesis_package_lifecycle_scoping_567_v0.1.md` | No |',
    '| 568 | Real HTTP transport wrapper runtime | `ilc_core/network/d2d/http_gossip_transport_runtime.py` | YES |',
    '| 569 | Transport hardening and explicit fallback activation | Hardening tests + canary update | YES |',
    '| 570 | Static peer-config JSON loader and startup wiring | `ilc_core/node/node_startup_runtime.py` | YES |',
    '| 571 | venv + systemd packaging and lifecycle runtime | service runner + unit file(s) | YES |',
    '| 572 | Deterministic three-machine smoke harness | smoke harness + fixtures | YES |',
    '| 573 | Coherence report + capsule v3.0 | report + capsule | No |',
    '| 574 | Window 565-574 closure gate and handoff | gate script + handoff | YES |',
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


def _resolve_phase_565_commit_ref() -> str:
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
        if PHASE_565_SUBJECT_TOKEN not in subject.lower():
            continue
        matches.append(commit_hash)
    for commit_ref in matches:
        if _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS:
            return commit_ref
    raise AssertionError('phase_565_commit_not_present_in_local_history')


def test_sequence_lock_document_exists_and_contains_required_headings() -> None:
    text = _read(SEQ_LOCK_PATH)
    for heading in REQUIRED_HEADINGS:
        assert heading in text


def test_sequence_lock_document_contains_required_tokens() -> None:
    text = _read(SEQ_LOCK_PATH)
    for token in REQUIRED_TOKENS:
        assert token in text


def test_phase_table_contains_exactly_ten_rows_for_phases_565_574_in_order() -> None:
    text = _read(SEQ_LOCK_PATH)
    rows: list[str] = []
    in_phase_table = False
    for line in text.splitlines():
        if line == '| Phase | Description | Primary output | Sensitive? |':
            in_phase_table = True
            continue
        if not in_phase_table:
            continue
        if line.startswith('| 56') or line.startswith('| 57'):
            rows.append(line)
            continue
        if rows:
            break
    assert tuple(rows) == EXPECTED_PHASE_ROWS


def test_carry_forward_section_contains_required_items() -> None:
    text = _read(SEQ_LOCK_PATH)
    for item in CARRY_FORWARD_ITEMS:
        assert item in text


def test_phase_565_commit_touches_expected_paths_only() -> None:
    commit_ref = _resolve_phase_565_commit_ref()
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS


def test_phase_565_commit_touches_no_cdl_path_and_no_ilc_core_path() -> None:
    commit_ref = _resolve_phase_565_commit_ref()
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert not any(path.startswith('ilc_core/') for path in changed_paths)
