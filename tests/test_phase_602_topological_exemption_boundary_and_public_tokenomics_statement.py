from __future__ import annotations

import subprocess
from pathlib import Path

DOC_PATH = Path('docs/specs/ilc_topological_exemption_boundary_and_public_tokenomics_statement_602_v0.1.md')
TEST_PATH = Path('tests/test_phase_602_topological_exemption_boundary_and_public_tokenomics_statement.py')
WALKTHROUGH_PATH = Path('docs/phases/phase_602_g8_topological_exemption_boundary_and_public_tokenomics_statement_walkthrough.md')
STATUS_PATH = Path('docs/phases/STATUS.md')
DECISION_LOG_PATH = Path('docs/specs/ilc_constitutional_decision_log_v0.1.md')
PHASE_602_SUBJECT_TOKEN = 'phase 602 public tokenomics'
PHASE_602_BACKFILL_SUBJECT_TOKEN = 'phase 602 walkthrough and status backfill'
EXACT_REQUIRED_MAIN_PATHS = {
    str(DOC_PATH),
    str(TEST_PATH),
}
EXACT_REQUIRED_BACKFILL_PATHS = {
    str(WALKTHROUGH_PATH),
    str(STATUS_PATH),
}
REQUIRED_HEADINGS = (
    '## 1. Tokenomics statement target',
    '## 2. Dependency tiers and inherited canon',
    '## 3. Topological Exemption legal-tier boundary',
    '## 4. Public tokenomics statement over ratified governor surfaces',
    '## 5. Genesis generation, accrual, and fade-away language discipline',
    '## 6. Residual non-closure and explicit defer discipline',
    '## 7. Forbidden interpretations and exclusions',
    '## 8. Explicit deferrals to later phases',
)
REQUIRED_TOKENS = (
    'topological_exemption_rationale_not_self_executing_tokenomics_law',
    'genesis_fixed_issuance_tranche_is_5pct_target_plus_cap_distinct_from_governance_privilege',
    'public_tokenomics_statement_must_track_ratified_allocation_cap_decay_and_target_surfaces',
    'public_tokenomics_statement_must_not_use_historical_8pct_as_cap_or_target',
    'genesis_generation_and_accrual_language_must_match_597_600_closure_state',
    'public_tokenomics_statement_must_not_claim_direct_mint_or_unratified_ecu_realization_mechanism',
    'public_tokenomics_statement_must_not_silently_import_capability_proof_or_payment_ingress',
    'hard_cap_tail_emission_or_other_supply_language_must_be_explicitly_bounded',
    'phase_602_statement_must_not_outrun_evidence_or_ratified_surfaces',
    'phase_603_synthesis_must_consume_phase_597_602_closure_state',
)
DEPENDENCY_ITEMS = (
    '`docs/specs/ilc_phase_596_605_sequence_lock_v0.1.md`',
    '`docs/specs/ilc_genesis_governance_dilution_and_brake_semantics_closure_597_v0.1.md`',
    '`docs/specs/ilc_freshness_gate_provenance_and_genesis_exemption_closure_598_v0.1.md`',
    '`docs/specs/ilc_genesis_accrual_governor_provenance_reconciliation_599_v0.1.md`',
    '`docs/specs/ilc_deterministic_genesis_economics_evidence_and_parameter_closure_600_v0.1.md`',
    '`docs/specs/ilc_post_genesis_capability_proof_disposition_and_bootstrap_transition_boundary_601_v0.1.md`',
    '`docs/specs/ilc_phase_585_genesis_authority_and_sunset_dependency_note_v0.1.md`',
    '`docs/specs/ilc_constitutional_decision_log_v0.1.md`',
    '`whitepaper/02_design_principles.md`',
)
SECTION_TWO_RULES = (
    'ratified issuance/governor surfaces come from the CDL and the Phase 597-600',
    'evidence-backed bounded language comes from Phase 600 replay outputs',
    'whitepaper language is rationale and non-equal-canon rhetorical context',
    'Topological Exemption remains explanatory value-flow rhetoric unless a later',
    '`phase_602_public_tokenomics_statement_must_consume_phase_601_capability_boundary`',
)
SECTION_THREE_RULES = (
    'topological_exemption_rationale_not_self_executing_tokenomics_law',
    'whitepaper rationale and explanatory tokenomics context',
    'not ratified issuance law',
    'not self-executing tokenomics law',
    'explanatory value-flow rhetoric does not replace explicit issuance law',
)
SECTION_FOUR_RULES = (
    'genesis_fixed_issuance_tranche_is_5pct_target_plus_cap_distinct_from_governance_privilege',
    'public_tokenomics_statement_must_track_ratified_allocation_cap_decay_and_target_surfaces',
    'public_tokenomics_statement_must_not_use_historical_8pct_as_cap_or_target',
    'hard_cap_tail_emission_or_other_supply_language_must_be_explicitly_bounded',
    'Authorized public tokenomics statement:',
    'Genesis has a fixed economic tranche equal to 5 percent of total supply',
    'the ratified governor surface blocks Genesis issuance above that bound',
    'deterministic Phase 600 evidence demonstrates full-tranche realization',
)
SECTION_FIVE_RULES = (
    'genesis_generation_and_accrual_language_must_match_597_600_closure_state',
    'public_tokenomics_statement_must_not_claim_direct_mint_or_unratified_ecu_realization_mechanism',
    'public_tokenomics_statement_must_not_silently_import_capability_proof_or_payment_ingress',
    'governance fade-away language must not be used to weaken or blur the',
    'any later Genesis-only ECU realization controller remains an implementation',
    'capability-proof and payment-ingress lanes remain outside current tokenomics',
)
SECTION_SIX_RULES = (
    'This phase authorizes the following public language now:',
    'This phase keeps explicitly bounded or curated:',
    'Later lanes still required before stronger public or mainnet-facing claims are:',
)
FORBIDDEN_RULES = (
    '- treating Topological Exemption as self-executing law,',
    '- using public tokenomics language that outruns the ratified governor stack,',
    '- silently importing capability-proof, inbound payment ingress, or product',
    '- treating Genesis fade-away wording as stronger than the evidence and closure',
    '- using vague `special privilege` language where the law has separated',
    '- claiming direct Genesis mint or an unratified ECU-anchor/controller mechanism',
    '- weakening a ratified fixed-tranche Genesis statement into mere optional',
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
    candidates: list[str] = []
    for line in result.stdout.splitlines():
        if '\t' not in line:
            continue
        commit_hash, subject = line.split('\t', 1)
        if subject_token not in subject.lower():
            continue
        candidates.append(commit_hash)
    for commit_ref in candidates:
        if _changed_paths_for_commit(commit_ref) == expected_paths:
            return commit_ref
    raise AssertionError(f'commit_not_present_in_local_history:{subject_token}')


def test_document_exists_and_contains_required_section_headings() -> None:
    text = _read(DOC_PATH)
    for heading in REQUIRED_HEADINGS:
        assert heading in text


def test_all_required_governance_tokens_are_present() -> None:
    text = _read(DOC_PATH)
    for token in REQUIRED_TOKENS:
        assert token in text


def test_section_two_carries_mandatory_dependency_bundle_and_tier_labels() -> None:
    text = _read(DOC_PATH)
    for item in DEPENDENCY_ITEMS:
        assert item in text
    for item in SECTION_TWO_RULES:
        assert item in text


def test_section_three_contains_topological_exemption_legal_tier_boundary_rules() -> None:
    text = _read(DOC_PATH)
    for item in SECTION_THREE_RULES:
        assert item in text


def test_section_four_contains_public_tokenomics_statement_rules() -> None:
    text = _read(DOC_PATH)
    for item in SECTION_FOUR_RULES:
        assert item in text


def test_section_five_contains_genesis_generation_accrual_language_discipline_rules() -> None:
    text = _read(DOC_PATH)
    for item in SECTION_FIVE_RULES:
        assert item in text


def test_section_six_contains_explicit_safe_language_versus_defer_discipline() -> None:
    text = _read(DOC_PATH)
    for item in SECTION_SIX_RULES:
        assert item in text


def test_section_seven_contains_all_forbidden_interpretation_exclusions() -> None:
    text = _read(DOC_PATH)
    for item in FORBIDDEN_RULES:
        assert item in text


def test_main_commit_touches_exactly_doc_and_test() -> None:
    commit_ref = _resolve_commit_ref(subject_token=PHASE_602_SUBJECT_TOKEN, expected_paths=EXACT_REQUIRED_MAIN_PATHS)
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS


def test_main_commit_touches_no_adr_path_no_cdl_path_and_no_ilc_core_path() -> None:
    commit_ref = _resolve_commit_ref(subject_token=PHASE_602_SUBJECT_TOKEN, expected_paths=EXACT_REQUIRED_MAIN_PATHS)
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert not any(path.startswith('docs/adr/') for path in changed_paths)
    assert not any(path.startswith('docs/specs/ilc_cdl_') for path in changed_paths)
    assert not any(path.startswith('docs/specs/ilc_cdl-') for path in changed_paths)
    assert not any('/ilc_cdl_' in path for path in changed_paths)
    assert not any(path.startswith('ilc_core/') for path in changed_paths)


def test_backfill_commit_touches_exactly_walkthrough_and_status_and_no_forbidden_paths() -> None:
    commit_ref = _resolve_commit_ref(subject_token=PHASE_602_BACKFILL_SUBJECT_TOKEN, expected_paths=EXACT_REQUIRED_BACKFILL_PATHS)
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert changed_paths == EXACT_REQUIRED_BACKFILL_PATHS
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert not any(path.startswith('docs/adr/') for path in changed_paths)
    assert not any(path.startswith('docs/specs/ilc_cdl_') for path in changed_paths)
    assert not any(path.startswith('docs/specs/ilc_cdl-') for path in changed_paths)
    assert not any('/ilc_cdl_' in path for path in changed_paths)
    assert not any(path.startswith('ilc_core/') for path in changed_paths)
