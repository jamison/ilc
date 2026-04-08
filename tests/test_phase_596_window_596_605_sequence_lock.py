from __future__ import annotations

import subprocess
from pathlib import Path

SEQ_LOCK_PATH = Path('docs/specs/ilc_phase_596_605_sequence_lock_v0.1.md')
DECISION_LOG_PATH = Path('docs/specs/ilc_constitutional_decision_log_v0.1.md')
TEST_PATH = Path('tests/test_phase_596_window_596_605_sequence_lock.py')
WALKTHROUGH_PATH = Path('docs/phases/phase_596_g8_window_596_605_sequence_lock_walkthrough.md')
STATUS_PATH = Path('docs/phases/STATUS.md')
PHASE_596_SUBJECT_TOKEN = 'phase 596 window 596-605 sequence lock'
PHASE_596_BACKFILL_SUBJECT_TOKEN = 'phase 596 walkthrough and status backfill'
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
    'window_596_605_genesis_carry_forward_primary_gate',
    'phase_595_bounded_rc0_1_closure_remains_frozen_input',
    'window_596_605_closes_remaining_genesis_support_canon',
    'genesis_governance_dilution_must_not_remain_supporting_context_by_silence',
    'freshness_gate_provenance_must_be_dispositioned',
    'genesis_accrual_governor_provenance_must_be_reconciled',
    'genesis_generation_and_fade_away_semantics_must_be_explicit',
    'capability_proof_lane_must_be_dispositioned_not_implicitly_imported',
    'topological_exemption_rationale_boundary_must_be_explicit',
    'tokenomics_public_statement_must_match_ratified_governor_surfaces',
    'window_596_605_preserves_585_595_frozen_public_and_rc_boundaries',
    'no_inbound_payment_ingress_or_harness_drift_inside_genesis_carry_forward_window',
)
EXPECTED_PHASE_ROWS = (
    '| 596 | Window 596-605 sequence lock and dependency freeze | `ilc_phase_596_605_sequence_lock_v0.1.md` | No |',
    '| 597 | Genesis governance dilution and brake-semantics closure | Genesis governance closure artifact | YES |',
    '| 598 | Freshness-gate provenance and Genesis exemption closure | freshness provenance closure artifact | YES |',
    '| 599 | Genesis accrual-governor provenance reconciliation | Genesis accrual reconciliation lock | YES |',
    '| 600 | Deterministic Genesis economics evidence and parameter closure | Genesis economics evidence pack | YES |',
    '| 601 | Post-Genesis capability-proof disposition and bootstrap transition boundary | capability-proof disposition artifact | YES |',
    '| 602 | Topological Exemption boundary and public tokenomics statement | rationale boundary + tokenomics statement | YES |',
    '| 603 | Genesis carry-forward synthesis and readiness-delta addendum | synthesis + readiness-delta addendum | No |',
    '| 604 | Coherence report and capsule v3.2 | report + capsule | No |',
    '| 605 | Window 596-605 closure gate and handoff | gate script + handoff | YES |',
)
REQUIRED_REFERENCES = (
    '`docs/specs/ilc_window_596_605_candidate_phase_grouping_v0.1.md`',
    '`docs/specs/ilc_phase_585_genesis_authority_and_sunset_dependency_note_v0.1.md`',
    '`docs/specs/ilc_genesis_authority_sunset_and_fork_legitimacy_coherence_lock_590_v0.1.md`',
    '`docs/specs/ilc_window_585_594_handoff_594_v0.1.md`',
    '`docs/specs/ilc_rc0_1_strike_force_consolidation_and_runtime_hardening_595_v0.1.md`',
    '`docs/specs/ilc_integration_coherence_report_593_v0.1.md`',
    '`docs/adr/ADR_0006_EVE_Canonical_Capsule_Integrity.md`',
    '`docs/adr/ADR_0026_Protocol_vs_Harness_Product_Boundary.md`',
    '`docs/adr/ADR_0027_Canonical_Self_Describing_Bootstrap_and_Receipt_Boundary.md`',
    '`docs/research/ilc_rc_phase_575_execution_packets_v0.1.md`',
    '`docs/research/ilc_cryptographic_economic_coupling_memo_v0.1.md`',
    '`docs/specs/ilc_constitutional_decision_log_v0.1.md`',
    '`docs/adr/ADR_0008_Node_Usefulness_vs_Governance_Weight_and_Genesis_Dilution.md`',
    '`docs/specs/ilc_freshness_gate_contract_v0.1.md`',
    '`docs/specs/ilc_genesis_accrual_governor_contract_v0.1.md`',
    '`docs/specs/ilc_genesis_accumulation_dynamics_analysis_298_v0.3.md`',
    '`docs/specs/ilc_genesis_accrual_reconciliation_8pct_vs_theta_hard_266_v0.1.md`',
    '`docs/specs/ilc_phase_305_genesis_accumulation_canonicalization_checklist_v0.1.md`',
    '`docs/specs/ilc_constitutional_context_audit_v0.1.md`',
    '`docs/specs/ilc_pre_epoch_capability_proofs_v0.1.md`',
    '`docs/specs/ilc_post_genesis_capability_proof_activation_sequence_230_239_v0.1.md`',
    '`docs/research/ilc_genesis_authority_and_sunset_canon_briefing_v0.1.md`',
    '`whitepaper/02_design_principles.md`',
    '`CDL-001`',
    '`CDL-003`',
    '`CDL-004`',
    '`CDL-013`',
    '`CDL-019`',
    '`CDL-022`',
    '`CDL-023`',
    '`CDL-026`',
    '`CDL-027`',
    '`CDL-029`',
    '`CDL-030`',
    '`CDL-031`',
    '`CDL-045`',
    '`CDL-V4`',
    '`CDL-V6`',
)
REQUIRED_BLOCKERS = (
    'Phase 590, Phase 594, and Phase 595 are frozen inherited boundaries',
    'every carry-forward item in this window must end as ratified closure,',
    'deterministic evidence is mandatory for any simulation or parameter-closure',
    'no boundary widening into inbound payments, transport/security hardening,',
    'supporting context may inform the window but may not be treated as equal',
)
LOCKED_DECISION_RULES = (
    'Window 596-605 is the dedicated Genesis carry-forward closure lane after the',
    'the public boundary from Phases 585-594 remains frozen and is not reopened by',
    'the Phase 595 bounded RC0.1 runtime/testnet closure remains frozen and is not',
    'Genesis bootstrap specialness remains bootstrap-only and bounded.',
    'capability-proof planning remains a separate lane unless and until explicitly',
    'Topological Exemption remains rationale unless a ratified artifact elevates',
    'inbound HTTP machine-payment ingress remains outside this window.',
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


def test_phase_table_contains_exactly_ten_rows_for_phases_596_605_in_order() -> None:
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


def test_locked_implementation_decisions_record_frozen_585_595_boundary_rule() -> None:
    text = _read(SEQ_LOCK_PATH)
    for item in LOCKED_DECISION_RULES:
        assert item in text


def test_phase_596_main_commit_touches_expected_paths_only() -> None:
    commit_ref = _resolve_commit_ref(
        subject_token=PHASE_596_SUBJECT_TOKEN,
        expected_paths=EXACT_REQUIRED_MAIN_PATHS,
    )
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS


def test_phase_596_main_commit_touches_no_adr_cdl_path_and_no_ilc_core_path() -> None:
    commit_ref = _resolve_commit_ref(
        subject_token=PHASE_596_SUBJECT_TOKEN,
        expected_paths=EXACT_REQUIRED_MAIN_PATHS,
    )
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert not any(path.startswith('docs/adr/') for path in changed_paths)
    assert not any(path.startswith('docs/specs/ilc_cdl_') for path in changed_paths)
    assert not any(path.startswith('docs/specs/ilc_cdl-') for path in changed_paths)
    assert not any('/ilc_cdl_' in path for path in changed_paths)
    assert not any(path.startswith('ilc_core/') for path in changed_paths)


def test_phase_596_backfill_commit_touches_expected_paths_only() -> None:
    commit_ref = _resolve_commit_ref(
        subject_token=PHASE_596_BACKFILL_SUBJECT_TOKEN,
        expected_paths=EXACT_REQUIRED_BACKFILL_PATHS,
    )
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_BACKFILL_PATHS


def test_phase_596_backfill_commit_touches_no_adr_cdl_path_and_no_ilc_core_path() -> None:
    commit_ref = _resolve_commit_ref(
        subject_token=PHASE_596_BACKFILL_SUBJECT_TOKEN,
        expected_paths=EXACT_REQUIRED_BACKFILL_PATHS,
    )
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert not any(path.startswith('docs/adr/') for path in changed_paths)
    assert not any(path.startswith('docs/specs/ilc_cdl_') for path in changed_paths)
    assert not any(path.startswith('docs/specs/ilc_cdl-') for path in changed_paths)
    assert not any('/ilc_cdl_' in path for path in changed_paths)
    assert not any(path.startswith('ilc_core/') for path in changed_paths)
