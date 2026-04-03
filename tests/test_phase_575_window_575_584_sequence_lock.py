from __future__ import annotations

import subprocess
from pathlib import Path

SEQ_LOCK_PATH = Path('docs/specs/ilc_phase_575_584_sequence_lock_v0.1.md')
DECISION_LOG_PATH = Path('docs/specs/ilc_constitutional_decision_log_v0.1.md')
TEST_PATH = Path('tests/test_phase_575_window_575_584_sequence_lock.py')
WALKTHROUGH_PATH = Path('docs/phases/phase_575_g8_window_575_584_sequence_lock_walkthrough.md')
STATUS_PATH = Path('docs/phases/STATUS.md')
PHASE_575_SUBJECT_TOKEN = 'phase 575 window 575-584 sequence lock'
PHASE_575_BACKFILL_SUBJECT_TOKEN = 'phase 575 walkthrough and status backfill'
EXACT_REQUIRED_MAIN_PATHS = {
    str(SEQ_LOCK_PATH),
    str(TEST_PATH),
}
EXACT_REQUIRED_BACKFILL_PATHS = {
    str(WALKTHROUGH_PATH),
    str(STATUS_PATH),
}
REQUIRED_HEADINGS = (
    '## 1. Window summary',
    '## 2. Hard pass condition',
    '## 3. Phase table',
    '## 4. Locked implementation decisions',
    '## 5. Carry-forward inputs from Window 565-574',
    '## 6. Protected boundaries and anti-pattern exclusions',
    '## 7. Sequence integrity rule',
)
REQUIRED_TOKENS = (
    'rc0_1_testnet_window_575_584_primary_gate',
    'settlement_wallet_boundary_precedes_agent_loop_runtime',
    'persisted_graph_contract_precedes_live_submission_cutover',
    'curated_genesis_lineage_testnet_only',
    'wallet_visibility_accounting_only_in_rc0_1',
    'cdl_v7_reproducibility_disposition_required_before_phase_584',
    'outbound_http_machine_payment_skill_support_lane_only',
    'outbound_http_machine_payment_skill_may_close_as_explicit_defer',
    'public_genesis_and_minting_stabilization_deferred_to_585_plus',
    'no_public_release_claim_before_585_594',
)
CARRY_FORWARD_ITEMS = (
    'Server TLS plus `ILC-Signature` remains the active posture.',
    'Mutual TLS remains deferred.',
    'Automatic fallback remains deferred.',
    'Dynamic discovery, DHT, and multi-hop remain deferred.',
    'The three-machine substrate remains the active RC0.1 execution base.',
)
RUNTIME_BASELINE_ITEMS = (
    '`tools/agent_loop_v1.py`',
    '`tools/query_rc0_1_economic_state.py`',
    '`tools/run_rc0_1_economic_proof.py`',
    'Phases 579-581 harden and authorize cutover over this baseline rather than',
)
EXPECTED_PHASE_ROWS = (
    '| 575 | Window 575-584 sequence lock | `ilc_phase_575_584_sequence_lock_v0.1.md` | No |',
    '| 576 | RC0.1 settlement + wallet boundary lock | `ilc_rc0_1_settlement_wallet_boundary_lock_576_v0.1.md` | No |',
    '| 577 | RC0.1 persisted graph contract lock | `ilc_rc0_1_persisted_graph_contract_lock_577_v0.1.md` | No |',
    '| 578 | RC0.1 curated genesis/bootstrap lineage lock | `ilc_rc0_1_curated_genesis_bootstrap_lineage_lock_578_v0.1.md` | No |',
    '| 579 | Agent behavioral loop runtime cutover | `tools/agent_loop_v1.py` | YES |',
    '| 580 | 7+1 panel and live submission integration | panel wiring + submission runtime | YES |',
    '| 581 | ECU attribution, settlement, and wallet query integration | durable economic runtime updates | YES |',
    '| 582 | Reproducibility disposition + outbound HTTP machine-payment skill defer-or-attach | reproducibility artifact + outbound skill attachment or explicit defer | YES |',
    '| 583 | Coherence report + capsule v3.1 | report + capsule | No |',
    '| 584 | Window 575-584 closure gate and handoff | gate script + handoff | YES |',
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


def _resolve_commit_ref(*, subject_token: str, expected_paths: set[str]) -> str:
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
        if subject_token not in subject.lower():
            continue
        matches.append(commit_hash)
    for commit_ref in matches:
        if _changed_paths_for_commit(commit_ref) == expected_paths:
            return commit_ref
    raise AssertionError(f'commit_not_present_in_local_history:{subject_token}')


def test_sequence_lock_document_exists_and_contains_required_headings() -> None:
    text = _read(SEQ_LOCK_PATH)
    for heading in REQUIRED_HEADINGS:
        assert heading in text


def test_sequence_lock_document_contains_required_tokens() -> None:
    text = _read(SEQ_LOCK_PATH)
    for token in REQUIRED_TOKENS:
        assert token in text


def test_phase_table_contains_exactly_ten_rows_for_phases_575_584_in_order() -> None:
    text = _read(SEQ_LOCK_PATH)
    rows: list[str] = []
    in_phase_table = False
    for line in text.splitlines():
        if line == '| Phase | Description | Primary output | Sensitive? |':
            in_phase_table = True
            continue
        if not in_phase_table:
            continue
        if line in EXPECTED_PHASE_ROWS:
            rows.append(line)
            continue
        if rows:
            break
    assert tuple(rows) == EXPECTED_PHASE_ROWS


def test_carry_forward_section_contains_required_items() -> None:
    text = _read(SEQ_LOCK_PATH)
    for item in CARRY_FORWARD_ITEMS:
        assert item in text


def test_locked_decisions_record_existing_runtime_baseline() -> None:
    text = _read(SEQ_LOCK_PATH)
    for item in RUNTIME_BASELINE_ITEMS:
        assert item in text


def test_phase_575_main_commit_touches_expected_paths_only() -> None:
    commit_ref = _resolve_commit_ref(
        subject_token=PHASE_575_SUBJECT_TOKEN,
        expected_paths=EXACT_REQUIRED_MAIN_PATHS,
    )
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS


def test_phase_575_main_commit_touches_no_adr_cdl_path_and_no_ilc_core_path() -> None:
    commit_ref = _resolve_commit_ref(
        subject_token=PHASE_575_SUBJECT_TOKEN,
        expected_paths=EXACT_REQUIRED_MAIN_PATHS,
    )
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert not any(path.startswith('docs/adr/') for path in changed_paths)
    assert not any(path.startswith('docs/specs/ilc_cdl_') for path in changed_paths)
    assert not any(path.startswith('docs/specs/ilc_cdl-') for path in changed_paths)
    assert not any('/ilc_cdl_' in path for path in changed_paths)
    assert not any(path.startswith('ilc_core/') for path in changed_paths)


def test_phase_575_backfill_commit_touches_expected_paths_only() -> None:
    commit_ref = _resolve_commit_ref(
        subject_token=PHASE_575_BACKFILL_SUBJECT_TOKEN,
        expected_paths=EXACT_REQUIRED_BACKFILL_PATHS,
    )
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_BACKFILL_PATHS


def test_phase_575_backfill_commit_touches_no_adr_cdl_path_and_no_ilc_core_path() -> None:
    commit_ref = _resolve_commit_ref(
        subject_token=PHASE_575_BACKFILL_SUBJECT_TOKEN,
        expected_paths=EXACT_REQUIRED_BACKFILL_PATHS,
    )
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert not any(path.startswith('docs/adr/') for path in changed_paths)
    assert not any(path.startswith('docs/specs/ilc_cdl_') for path in changed_paths)
    assert not any(path.startswith('docs/specs/ilc_cdl-') for path in changed_paths)
    assert not any('/ilc_cdl_' in path for path in changed_paths)
    assert not any(path.startswith('ilc_core/') for path in changed_paths)
