from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

SEQ_LOCK_PATH = Path('docs/specs/ilc_phase_607_612_sequence_lock_v0.1.md')
DECISION_LOG_PATH = Path('docs/specs/ilc_constitutional_decision_log_v0.1.md')
TEST_PATH = Path('tests/test_phase_607_window_607_612_sequence_lock.py')
WALKTHROUGH_PATH = Path(
    'docs/phases/phase_607_g8_window_607_612_sequence_lock_and_settlement_substrate_issue_framing_walkthrough.md'
)
STATUS_PATH = Path('docs/phases/STATUS.md')
PHASE_607_SUBJECT_TOKEN = 'phase 607 window 607-612 sequence lock'
PHASE_607_BACKFILL_SUBJECT_TOKEN = 'phase 607 walkthrough and status backfill'
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
    '## 3. Mandatory dependency bundle',
    '## 4. Pre-lock blockers',
    '## 5. Phase table',
    '## 6. Locked implementation decisions',
    '## 7. Protected boundaries and anti-pattern exclusions',
    '## 8. Sequence integrity rule',
)
REQUIRED_TOKENS = (
    'window_607_612_settlement_substrate_reconciliation_primary_gate',
    'current_rc_runtime_internal_epoch_settled_ledger_is_not_final_substrate_by_implication',
    'december_2025_off_chain_first_later_chain_direction_must_be_reconciled_against_current_authority',
    'ecu_and_ilc_layers_must_be_separated_before_public_settlement_claims',
    'public_auditability_and_identity_privacy_must_be_designed_together',
    'wallet_agnostic_signing_does_not_settle_final_token_substrate',
    'no_payment_lane_progress_before_settlement_substrate_issue_framing',
    'broader_window_607_615_is_superseded_pending_reconciliation_first_lane',
    'current_capsule_language_must_not_overgeneralize_rc_runtime_posture',
    'historical_chain_backed_settlement_option_must_be_classified_not_assumed',
    'no_wallet_authority_widening_inside_reconciliation_window',
    'phase_607_sequence_lock_sets_reconciliation_before_expansion',
)
EXPECTED_PHASE_ROWS = (
    '| 607 | Window 607-612 sequence lock and issue framing | `ilc_phase_607_612_sequence_lock_v0.1.md` | YES |',
    '| 608 | Historical lineage and authority audit | historical lineage audit artifact | No |',
    '| 609 | ECU / ILC / runtime-boundary reconciliation | reconciliation memo | No |',
    '| 610 | Public-ledger substrate options and rejection matrix | substrate options matrix | No |',
    '| 611 | Governance vehicle selection and prelock | governance vehicle selection artifact | **conditional** |',
    '| 612 | Closure synthesis and downstream replan | closure handoff + downstream replan | YES |',
)
REQUIRED_REFERENCES = (
    '`docs/specs/ilc_window_607_612_candidate_phase_grouping_v0.1.md`',
    '`docs/specs/ilc_window_607_615_candidate_phase_grouping_v0.1.md`',
    '`docs/specs/ilc_window_596_605_handoff_605_v0.1.md`',
    '`docs/specs/ilc_phase_596_605_sequence_lock_v0.1.md`',
    '`docs/specs/ilc_antigravity_context_capsule_v0.4.md`',
    '`docs/specs/ilc_antigravity_context_capsule_v0.5.md`',
    '`docs/specs/ilc_antigravity_context_capsule_v3.2.md`',
    '`docs/specs/ilc_wallet_agnostic_signing_strategy_codex_handoff_v0.1.md`',
    '`docs/specs/ilc_rc0_1_settlement_wallet_boundary_lock_576_v0.1.md`',
    '`docs/specs/ilc_rc0_1_ecu_settlement_wallet_query_integration_581_v0.1.md`',
    '`docs/specs/ilc_genesis_accrual_governor_provenance_reconciliation_599_v0.1.md`',
    '`docs/specs/ilc_deterministic_genesis_economics_evidence_and_parameter_closure_600_v0.1.md`',
    '`docs/specs/ilc_topological_exemption_boundary_and_public_tokenomics_statement_602_v0.1.md`',
    '`docs/specs/ilc_economic_architecture_comprehensive_v0.1.md`',
    '`docs/specs/ilc_agent_sdk_boundary_contract_draft_v0.1.md`',
    '`docs/specs/ilc_claude_extraction_brief_v0.1.md`',
    '`docs/adr/ADR_0013_External_Payment_Boundary_and_Third_Party_Independence.md`',
    '`docs/adr/ADR_0026_Protocol_vs_Harness_Product_Boundary.md`',
    '`whitepaper/2025_12_03_ILC_whitepaper_v5_2.md`',
    '`docs/specs/ilc_constitutional_decision_log_v0.1.md`',
    '`CDL-001`',
    '`CDL-003`',
    '`CDL-004`',
    '`CDL-013`',
    '`CDL-022`',
    '`CDL-023`',
    '`CDL-026`',
    '`CDL-027`',
    '`CDL-028`',
    '`CDL-029`',
    '`CDL-030`',
    '`CDL-031`',
    '`CDL-045`',
    '`CDL-V6`',
)
REQUIRED_BLOCKERS = (
    'the 585-595 public and bounded-RC boundaries remain frozen inherited law',
    'the read-only wallet/query posture remains frozen inherited law',
    'the broader 607-615 continuation draft is superseded pending this narrower',
    'no historical whitepaper or chat material may be treated as current canon by',
    'The ILC coin (ECU) is protocol-native.',
    'older capsule phrase `ILC is NOT a blockchain` must be treated as',
    'no payment lane, wallet authority, or public RC planning may advance inside',
    'public auditability must be distinguished from public identity exposure',
)
LOCKED_DECISION_RULES = (
    'Window 607-612 is a settlement-substrate reconciliation lane, not a generic',
    'current RC/runtime implementation is an internal epoch-settled ledger with',
    'that current posture does not settle the forever substrate for `ILC` by',
    'the December 2025 off-chain-first / later-chain direction remains legitimate',
    'wallet-agnostic signing is about signing keys and provider compatibility, not',
    '`ECU` and `ILC` must be treated as distinct layers in this reconciliation.',
    'no broader 607+ implementation planning resumes until this window closes.',
    'explicit keep/defer/reject rationale',
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


def _find_commit_ref(*, subject_token: str) -> str | None:
    result = subprocess.run(
        ['git', 'log', '--format=%H%x09%s'],
        capture_output=True,
        check=True,
        text=True,
    )
    for line in result.stdout.splitlines():
        if '\t' not in line:
            continue
        commit_hash, subject = line.split('\t', 1)
        if subject_token in subject.lower():
            return commit_hash
    return None


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


def _require_commit_or_skip(subject_token: str) -> None:
    if _find_commit_ref(subject_token=subject_token) is None:
        pytest.skip(f'commit_not_yet_present:{subject_token}')


def test_sequence_lock_document_exists_and_contains_required_headings() -> None:
    text = _read(SEQ_LOCK_PATH)
    for heading in REQUIRED_HEADINGS:
        assert heading in text


def test_sequence_lock_document_contains_required_tokens() -> None:
    text = _read(SEQ_LOCK_PATH)
    for token in REQUIRED_TOKENS:
        assert token in text


def test_phase_table_contains_exactly_six_rows_for_phases_607_612_in_order() -> None:
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


def test_dependency_bundle_contains_all_required_references() -> None:
    text = _read(SEQ_LOCK_PATH)
    for item in REQUIRED_REFERENCES:
        assert item in text


def test_pre_lock_blockers_section_contains_all_required_blockers() -> None:
    text = _read(SEQ_LOCK_PATH)
    for item in REQUIRED_BLOCKERS:
        assert item in text


def test_locked_implementation_decisions_record_internal_ledger_and_unresolved_substrate_distinction() -> None:
    text = _read(SEQ_LOCK_PATH)
    for item in LOCKED_DECISION_RULES:
        assert item in text


def test_phase_607_main_commit_touches_expected_paths_only() -> None:
    _require_commit_or_skip(PHASE_607_SUBJECT_TOKEN)
    commit_ref = _resolve_commit_ref(
        subject_token=PHASE_607_SUBJECT_TOKEN,
        expected_paths=EXACT_REQUIRED_MAIN_PATHS,
    )
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS


def test_phase_607_main_commit_touches_no_adr_cdl_path_and_no_ilc_core_path() -> None:
    _require_commit_or_skip(PHASE_607_SUBJECT_TOKEN)
    commit_ref = _resolve_commit_ref(
        subject_token=PHASE_607_SUBJECT_TOKEN,
        expected_paths=EXACT_REQUIRED_MAIN_PATHS,
    )
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert not any(path.startswith('docs/adr/') for path in changed_paths)
    assert not any(path.startswith('docs/specs/ilc_cdl_') for path in changed_paths)
    assert not any(path.startswith('docs/specs/ilc_cdl-') for path in changed_paths)
    assert not any('/ilc_cdl_' in path for path in changed_paths)
    assert not any(path.startswith('ilc_core/') for path in changed_paths)


def test_phase_607_backfill_commit_touches_expected_paths_only() -> None:
    _require_commit_or_skip(PHASE_607_BACKFILL_SUBJECT_TOKEN)
    commit_ref = _resolve_commit_ref(
        subject_token=PHASE_607_BACKFILL_SUBJECT_TOKEN,
        expected_paths=EXACT_REQUIRED_BACKFILL_PATHS,
    )
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_BACKFILL_PATHS


def test_phase_607_backfill_commit_touches_no_adr_cdl_path_and_no_ilc_core_path() -> None:
    _require_commit_or_skip(PHASE_607_BACKFILL_SUBJECT_TOKEN)
    commit_ref = _resolve_commit_ref(
        subject_token=PHASE_607_BACKFILL_SUBJECT_TOKEN,
        expected_paths=EXACT_REQUIRED_BACKFILL_PATHS,
    )
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert not any(path.startswith('docs/adr/') for path in changed_paths)
    assert not any(path.startswith('docs/specs/ilc_cdl_') for path in changed_paths)
    assert not any(path.startswith('docs/specs/ilc_cdl-') for path in changed_paths)
    assert not any('/ilc_cdl_' in path for path in changed_paths)
    assert not any(path.startswith('ilc_core/') for path in changed_paths)
