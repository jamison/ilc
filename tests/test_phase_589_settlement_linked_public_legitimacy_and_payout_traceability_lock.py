from __future__ import annotations

import subprocess
from pathlib import Path

DOC_PATH = Path('docs/specs/ilc_settlement_linked_public_legitimacy_and_payout_traceability_lock_589_v0.1.md')
DECISION_LOG_PATH = Path('docs/specs/ilc_constitutional_decision_log_v0.1.md')
TEST_PATH = Path('tests/test_phase_589_settlement_linked_public_legitimacy_and_payout_traceability_lock.py')
WALKTHROUGH_PATH = Path('docs/phases/phase_589_g8_settlement_linked_public_legitimacy_payout_traceability_lock_walkthrough.md')
STATUS_PATH = Path('docs/phases/STATUS.md')
PHASE_589_SUBJECT_TOKEN = 'phase 589 public settlement legitimacy lock'
PHASE_589_BACKFILL_SUBJECT_TOKEN = 'phase 589 walkthrough and status backfill'
EXACT_REQUIRED_MAIN_PATHS = {
    str(DOC_PATH),
    str(TEST_PATH),
}
EXACT_REQUIRED_BACKFILL_PATHS = {
    str(WALKTHROUGH_PATH),
    str(STATUS_PATH),
}
REQUIRED_HEADINGS = (
    '## 1. Settlement-linked public legitimacy target',
    '## 2. Dependency and inherited canon',
    '## 3. Public legitimacy receipt-chain boundary',
    '## 4. Payout traceability and beneficiary identity boundary',
    '## 5. Promotion, provenance, and non-shortcut rules',
    '## 6. Forbidden interpretations and exclusions',
    '## 7. Explicit deferrals to later phases',
)
REQUIRED_TOKENS = (
    'settlement_linked_public_legitimacy_requires_settled_receipt_chain',
    'public_legitimacy_must_reference_activation_quorum_and_settlement_lineage',
    'panel_result_or_claim_batch_alone_not_public_legitimacy',
    'payout_traceability_must_reference_quorum_settlement_and_beneficiary_lineage',
    'payout_traceability_must_preserve_task_epoch_and_claim_batch_identity',
    'namespace_continuity_must_not_bypass_settlement_linked_legitimacy',
    'public_reward_or_attribution_requires_canonical_lineage_membership',
    'promotion_or_provenance_continuity_not_public_legitimacy_substitute',
    'validation_or_quarantine_state_not_settlement_legitimacy_by_itself',
    'settlement_legitimacy_must_fail_closed_on_quorum_or_lineage_mismatch',
    'receipt_envelope_candidate_is_supporting_context_only',
    'public_wallet_visibility_not_public_claimability',
    'reputation_carry_forward_and_minting_semantics_deferred',
)
DEPENDENCY_ITEMS = (
    '`docs/specs/ilc_window_585_594_candidate_phase_grouping_v0.1.md`',
    '`docs/specs/ilc_phase_585_594_sequence_lock_v0.1.md`',
    '`docs/specs/ilc_public_receipt_representation_cluster_lock_586_v0.1.md`',
    '`docs/specs/ilc_public_identity_activation_and_namespace_boundary_lock_587_v0.1.md`',
    '`docs/specs/ilc_public_quorum_eligibility_and_genesis_lineage_authority_boundary_lock_588_v0.1.md`',
    '`docs/adr/ADR_0027_Canonical_Self_Describing_Bootstrap_and_Receipt_Boundary.md`',
    '`docs/specs/ilc_cdl_035_validation_lifecycle_and_gate_verdict_attachment_ratification_evidence_350_v0.1.md`',
    '`docs/specs/ilc_cdl_038_private_to_public_promotion_and_promotion_receipt_ratification_evidence_353_v0.1.md`',
    '`docs/specs/ilc_rc0_1_settlement_wallet_boundary_lock_576_v0.1.md`',
    '`docs/specs/ilc_rc0_1_ecu_settlement_wallet_query_integration_581_v0.1.md`',
)
SUPPORTING_CONTEXT_RULES = (
    '`docs/specs/ilc_receipt_envelope_and_payout_trace_contract_candidate_v0.1.md`',
    'RC0.1 settlement/runtime artifacts are bounded implementation context, not by',
    'receipt_envelope_candidate_is_supporting_context_only',
)
SECTION_THREE_RULES = (
    'Settlement-linked public legitimacy requires a settled receipt chain.',
    'Public legitimacy must reference activation lineage, quorum lineage, and',
    'A panel result or a claim batch alone is not public legitimacy.',
    'Settlement-linked public legitimacy must fail closed on quorum mismatch,',
)
SECTION_FOUR_RULES = (
    'Public payout or attribution traceability must preserve machine-legible links',
    '`task_id`, `epoch_id` or `epoch_index`, and `claim_batch_sha256`',
    'The current RC0.1 runtime anchor for bounded claim-batch identity is',
    'Namespace continuity must not bypass settlement-linked legitimacy.',
    'Public wallet visibility or internal balance visibility is not public',
)
SECTION_FIVE_RULES = (
    'Promotion, provenance continuity, or publication continuity do not by',
    'Validation lifecycle state, quarantine state, or operator-visible state is not',
    '`CDL-038` promotion precedent may inform lineage continuity only.',
)
FORBIDDEN_RULES = (
    '- treating panel pass, claim-batch construction, or broadcast success as sufficient public legitimacy',
    '- treating wallet visibility or internal balance visibility as public claimability',
    '- treating promotion receipts or provenance continuity as public reward legitimacy',
    '- treating validation lifecycle state as equivalent to settlement-linked public legitimacy',
    '- using supporting payout-trace candidates as equal canon by silence',
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


def test_document_exists_and_contains_required_headings() -> None:
    text = _read(DOC_PATH)
    for heading in REQUIRED_HEADINGS:
        assert heading in text


def test_document_contains_required_governance_tokens() -> None:
    text = _read(DOC_PATH)
    for token in REQUIRED_TOKENS:
        assert token in text


def test_section_two_carries_mandatory_dependency_bundle() -> None:
    text = _read(DOC_PATH)
    for item in DEPENDENCY_ITEMS:
        assert item in text


def test_section_two_labels_supporting_payout_trace_context_as_non_equal_canon() -> None:
    text = _read(DOC_PATH)
    for item in SUPPORTING_CONTEXT_RULES:
        assert item in text


def test_section_three_contains_settlement_linked_public_legitimacy_rules() -> None:
    text = _read(DOC_PATH)
    for item in SECTION_THREE_RULES:
        assert item in text


def test_section_four_contains_payout_traceability_and_beneficiary_lineage_rules() -> None:
    text = _read(DOC_PATH)
    for item in SECTION_FOUR_RULES:
        assert item in text


def test_section_five_contains_promotion_provenance_non_shortcut_rules() -> None:
    text = _read(DOC_PATH)
    for item in SECTION_FIVE_RULES:
        assert item in text


def test_section_six_contains_all_forbidden_interpretation_exclusions() -> None:
    text = _read(DOC_PATH)
    for item in FORBIDDEN_RULES:
        assert item in text


def test_phase_589_main_commit_touches_expected_paths_only() -> None:
    commit_ref = _resolve_commit_ref(
        subject_token=PHASE_589_SUBJECT_TOKEN,
        expected_paths=EXACT_REQUIRED_MAIN_PATHS,
    )
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS


def test_phase_589_main_commit_touches_no_adr_cdl_path_and_no_ilc_core_path() -> None:
    commit_ref = _resolve_commit_ref(
        subject_token=PHASE_589_SUBJECT_TOKEN,
        expected_paths=EXACT_REQUIRED_MAIN_PATHS,
    )
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert not any(path.startswith('docs/adr/') for path in changed_paths)
    assert not any(path.startswith('docs/specs/ilc_cdl_') for path in changed_paths)
    assert not any(path.startswith('docs/specs/ilc_cdl-') for path in changed_paths)
    assert not any('/ilc_cdl_' in path for path in changed_paths)
    assert not any(path.startswith('ilc_core/') for path in changed_paths)


def test_phase_589_backfill_commit_touches_expected_paths_only() -> None:
    commit_ref = _resolve_commit_ref(
        subject_token=PHASE_589_BACKFILL_SUBJECT_TOKEN,
        expected_paths=EXACT_REQUIRED_BACKFILL_PATHS,
    )
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_BACKFILL_PATHS


def test_phase_589_backfill_commit_touches_no_adr_cdl_path_and_no_ilc_core_path() -> None:
    commit_ref = _resolve_commit_ref(
        subject_token=PHASE_589_BACKFILL_SUBJECT_TOKEN,
        expected_paths=EXACT_REQUIRED_BACKFILL_PATHS,
    )
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert not any(path.startswith('docs/adr/') for path in changed_paths)
    assert not any(path.startswith('docs/specs/ilc_cdl_') for path in changed_paths)
    assert not any(path.startswith('docs/specs/ilc_cdl-') for path in changed_paths)
    assert not any('/ilc_cdl_' in path for path in changed_paths)
    assert not any(path.startswith('ilc_core/') for path in changed_paths)
