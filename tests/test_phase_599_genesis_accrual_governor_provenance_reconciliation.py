from __future__ import annotations

import subprocess
from pathlib import Path

DOC_PATH = Path('docs/specs/ilc_genesis_accrual_governor_provenance_reconciliation_599_v0.1.md')
DECISION_LOG_PATH = Path('docs/specs/ilc_constitutional_decision_log_v0.1.md')
TEST_PATH = Path('tests/test_phase_599_genesis_accrual_governor_provenance_reconciliation.py')
WALKTHROUGH_PATH = Path('docs/phases/phase_599_g8_genesis_accrual_governor_provenance_reconciliation_walkthrough.md')
STATUS_PATH = Path('docs/phases/STATUS.md')
PHASE_599_SUBJECT_TOKEN = 'phase 599 genesis accrual governor reconciliation'
PHASE_599_BACKFILL_SUBJECT_TOKEN = 'phase 599 walkthrough and status backfill'
EXACT_REQUIRED_MAIN_PATHS = {
    str(DOC_PATH),
    str(TEST_PATH),
}
EXACT_REQUIRED_BACKFILL_PATHS = {
    str(WALKTHROUGH_PATH),
    str(STATUS_PATH),
}
REQUIRED_HEADINGS = (
    '## 1. Accrual-governor closure target',
    '## 2. Dependency tiers and inherited canon',
    '## 3. Ratified issuance and cap surfaces carried into the governor stack',
    '## 4. Contract-versus-analysis provenance reconciliation',
    '## 5. Open parameter and realization-surface questions',
    '## 6. Residual non-closure and explicit defer discipline',
    '## 7. Forbidden interpretations and exclusions',
    '## 8. Explicit deferrals to later phases',
)
REQUIRED_TOKENS = (
    'genesis_accrual_governor_provenance_closure_exits_analysis_only_state',
    'genesis_economic_tranche_is_distinct_from_governance_privilege',
    'genesis_5pct_tranche_is_target_plus_cap_not_cap_only',
    'theta_hard_theta_soft_and_allocation_surfaces_must_be_provenance_aligned',
    'historical_8pct_language_is_analysis_only_not_hard_cap_or_target',
    'genesis_fixed_tranche_against_cmax_is_authoritative_realization_surface',
    'issued_to_date_ratio_is_not_authoritative_for_full_tranche_realization',
    'future_genesis_ecu_realization_controller_if_used_must_be_separate_from_natural_centrality_measurement',
    'subsidy_factor_and_multiplier_interactions_must_be_named_for_phase_600_evidence',
    'genesis_generation_and_accrual_language_must_match_ratified_target_plus_cap',
    'phase_599_reconciliation_must_not_reopen_phase_597_598_closures',
    'phase_600_genesis_economics_evidence_must_consume_phase_599_reconciliation',
)
DEPENDENCY_ITEMS = (
    '`docs/specs/ilc_phase_596_605_sequence_lock_v0.1.md`',
    '`docs/specs/ilc_window_596_605_candidate_phase_grouping_v0.1.md`',
    '`docs/specs/ilc_genesis_governance_dilution_and_brake_semantics_closure_597_v0.1.md`',
    '`docs/specs/ilc_freshness_gate_provenance_and_genesis_exemption_closure_598_v0.1.md`',
    '`docs/specs/ilc_genesis_authority_sunset_and_fork_legitimacy_coherence_lock_590_v0.1.md`',
    '`docs/specs/ilc_genesis_accrual_governor_contract_v0.1.md`',
    '`docs/specs/ilc_genesis_accrual_reconciliation_8pct_vs_theta_hard_266_v0.1.md`',
    '`docs/specs/ilc_genesis_accumulation_dynamics_analysis_298_v0.3.md`',
    '`docs/specs/ilc_phase_305_genesis_accumulation_canonicalization_checklist_v0.1.md`',
    '`docs/specs/ilc_constitutional_decision_log_v0.1.md`',
)
SECTION_TWO_RULES = (
    'supporting context only before this phase',
    'analysis only and is not self-executing protocol law',
    'Phase 597 and Phase 598 are inherited canon for governance/freshness boundaries',
    '`phase_599_accrual_reconciliation_must_consume_phase_598_freshness_closure`',
)
SECTION_THREE_RULES = (
    'genesis_fixed_tranche_against_cmax_is_authoritative_realization_surface',
    'issued_to_date_ratio_is_not_authoritative_for_full_tranche_realization',
    '`0.05 * C_max = 1,296,000 ILC`',
    'governance privilege and economic tranche realization remain distinct',
    'this phase does not ratify direct Genesis mint as the only permissible',
)
SECTION_FOUR_RULES = (
    'genesis_accrual_governor_provenance_closure_exits_analysis_only_state',
    'historical_8pct_language_is_analysis_only_not_hard_cap_or_target',
    'the draft governor contract records a current conformance shape using',
    'that issued-to-date ratio may remain an implementation-context or sensitivity',
    'the dynamics analysis remains analysis-only evidence',
)
SECTION_FIVE_RULES = (
    'The authoritative realization surface closes here rather than drifting into',
    'future_genesis_ecu_realization_controller_if_used_must_be_separate_from_natural_centrality_measurement',
    'it is a later implementation surface, not presently ratified active law',
    'it must be separate from natural centrality measurement',
    'it must not be described as direct mint',
)
SECTION_SIX_RULES = (
    'This phase closes decisively:',
    'the constitutional realization surface for the Genesis tranche,',
    'This phase leaves as supporting context only:',
    'This phase leaves as explicit evidence-dependent follow-on to Phase 600:',
    'This phase leaves as explicit later-lane defer only:',
    'No provenance question affecting the constitutional realization surface remains',
)
FORBIDDEN_RULES = (
    '- using historical `8%` language as override of ratified issuance surfaces,',
    '- using draft governor-contract language as self-executing law by silence,',
    '- reopening governance-dilution or freshness conclusions already closed in',
    '- treating issued-to-date ratio as authoritative for full-tranche realization',
    '- treating any future Genesis-only ECU realization controller as if it were',
    '- rewriting natural centrality measurement as a hidden tranche controller',
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


def test_section_two_carries_mandatory_dependency_bundle_and_tier_labels() -> None:
    text = _read(DOC_PATH)
    for item in DEPENDENCY_ITEMS:
        assert item in text
    for item in SECTION_TWO_RULES:
        assert item in text


def test_section_three_contains_ratified_issuance_and_cap_linkage_rules() -> None:
    text = _read(DOC_PATH)
    for item in SECTION_THREE_RULES:
        assert item in text


def test_section_four_contains_contract_versus_analysis_reconciliation_rules() -> None:
    text = _read(DOC_PATH)
    for item in SECTION_FOUR_RULES:
        assert item in text


def test_section_five_contains_realization_surface_disposition_rules() -> None:
    text = _read(DOC_PATH)
    for item in SECTION_FIVE_RULES:
        assert item in text


def test_section_six_contains_explicit_closure_vs_evidence_vs_defer_discipline() -> None:
    text = _read(DOC_PATH)
    for item in SECTION_SIX_RULES:
        assert item in text


def test_section_seven_contains_all_forbidden_interpretation_exclusions() -> None:
    text = _read(DOC_PATH)
    for item in FORBIDDEN_RULES:
        assert item in text


def test_phase_599_main_commit_touches_expected_paths_only() -> None:
    commit_ref = _resolve_commit_ref(
        subject_token=PHASE_599_SUBJECT_TOKEN,
        expected_paths=EXACT_REQUIRED_MAIN_PATHS,
    )
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS


def test_phase_599_main_commit_touches_no_adr_cdl_path_and_no_ilc_core_path() -> None:
    commit_ref = _resolve_commit_ref(
        subject_token=PHASE_599_SUBJECT_TOKEN,
        expected_paths=EXACT_REQUIRED_MAIN_PATHS,
    )
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert not any(path.startswith('docs/adr/') for path in changed_paths)
    assert not any(path.startswith('docs/specs/ilc_cdl_') for path in changed_paths)
    assert not any(path.startswith('docs/specs/ilc_cdl-') for path in changed_paths)
    assert not any('/ilc_cdl_' in path for path in changed_paths)
    assert not any(path.startswith('ilc_core/') for path in changed_paths)


def test_phase_599_backfill_commit_touches_expected_paths_only() -> None:
    commit_ref = _resolve_commit_ref(
        subject_token=PHASE_599_BACKFILL_SUBJECT_TOKEN,
        expected_paths=EXACT_REQUIRED_BACKFILL_PATHS,
    )
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_BACKFILL_PATHS


def test_phase_599_backfill_commit_touches_no_adr_cdl_path_and_no_ilc_core_path() -> None:
    commit_ref = _resolve_commit_ref(
        subject_token=PHASE_599_BACKFILL_SUBJECT_TOKEN,
        expected_paths=EXACT_REQUIRED_BACKFILL_PATHS,
    )
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert not any(path.startswith('docs/adr/') for path in changed_paths)
    assert not any(path.startswith('docs/specs/ilc_cdl_') for path in changed_paths)
    assert not any(path.startswith('docs/specs/ilc_cdl-') for path in changed_paths)
    assert not any('/ilc_cdl_' in path for path in changed_paths)
    assert not any(path.startswith('ilc_core/') for path in changed_paths)
