from __future__ import annotations

import subprocess
from pathlib import Path

DOC_PATH = Path('docs/specs/ilc_genesis_authority_sunset_and_fork_legitimacy_coherence_lock_590_v0.1.md')
DECISION_LOG_PATH = Path('docs/specs/ilc_constitutional_decision_log_v0.1.md')
TEST_PATH = Path('tests/test_phase_590_genesis_authority_sunset_and_fork_legitimacy_coherence_lock.py')
WALKTHROUGH_PATH = Path('docs/phases/phase_590_g8_genesis_authority_sunset_fork_legitimacy_coherence_lock_walkthrough.md')
STATUS_PATH = Path('docs/phases/STATUS.md')
PHASE_590_SUBJECT_TOKEN = 'phase 590 genesis sunset coherence lock'
PHASE_590_BACKFILL_SUBJECT_TOKEN = 'phase 590 walkthrough and status backfill'
EXACT_REQUIRED_MAIN_PATHS = {
    str(DOC_PATH),
    str(TEST_PATH),
}
EXACT_REQUIRED_BACKFILL_PATHS = {
    str(WALKTHROUGH_PATH),
    str(STATUS_PATH),
}
REQUIRED_HEADINGS = (
    '## 1. Genesis coherence target',
    '## 2. Dependency tiers and inherited canon',
    '## 3. Bounded Genesis authority boundary',
    '## 4. Sunset and recession boundary',
    '## 5. Canonical-vs-fork public consequence',
    '## 6. Non-equal-canon gaps and carry-forward discipline',
    '## 7. Forbidden interpretations and exclusions',
    '## 8. Explicit deferrals to later phases',
)
REQUIRED_TOKENS = (
    'genesis_bootstrap_specialness_bounded_not_informal',
    'cdl_v6_extraordinary_path_not_ordinary_governance',
    'genesis_authority_must_recede_through_ratified_mechanisms',
    'genesis_rooted_artifact_lineage_required_for_canonical_public_network',
    'different_genesis_root_means_noncanonical_fork',
    'stripped_public_legitimacy_chain_means_noncanonical_fork',
    'cdl_009_fork_signaling_cannot_override_canonical_lineage',
    'genesis_lineage_self_anchor_not_permanent_sovereign_override',
    'genesis_dilution_caps_and_emergency_bounds_not_silent_discretion',
    'supporting_genesis_context_not_equal_canon',
    'freshness_and_accrual_supporting_context_not_closed_public_law',
    'topological_exemption_rationale_not_self_executing_law',
    'later_governance_must_extend_not_replace_canonical_lineage',
)
DEPENDENCY_ITEMS = (
    '`docs/specs/ilc_window_585_594_candidate_phase_grouping_v0.1.md`',
    '`docs/specs/ilc_phase_585_594_sequence_lock_v0.1.md`',
    '`docs/specs/ilc_phase_585_genesis_authority_and_sunset_dependency_note_v0.1.md`',
    '`docs/specs/ilc_public_identity_activation_and_namespace_boundary_lock_587_v0.1.md`',
    '`docs/specs/ilc_public_quorum_eligibility_and_genesis_lineage_authority_boundary_lock_588_v0.1.md`',
    '`docs/specs/ilc_settlement_linked_public_legitimacy_and_payout_traceability_lock_589_v0.1.md`',
    '`docs/adr/ADR_0006_EVE_Canonical_Capsule_Integrity.md`',
    '`docs/adr/ADR_0027_Canonical_Self_Describing_Bootstrap_and_Receipt_Boundary.md`',
    '`docs/specs/ilc_cdl_v6_genesis_intervention_protocol_ratification_evidence_334_v0.1.md`',
    '`docs/specs/ilc_cdl_045_operational_emergency_response_ratification_evidence_408_v0.1.md`',
)
SUPPORTING_CONTEXT_RULES = (
    '`docs/adr/ADR_0008_Node_Usefulness_vs_Governance_Weight_and_Genesis_Dilution.md`',
    '`docs/specs/ilc_freshness_gate_contract_v0.1.md` is supporting context only',
    '`docs/specs/ilc_genesis_accumulation_dynamics_analysis_298_v0.1.md` is',
    '`docs/research/ilc_genesis_authority_and_sunset_canon_briefing_v0.1.md` is a',
    '`docs/specs/ilc_pre_epoch_capability_proofs_v0.1.md` remains supporting',
    'supporting_genesis_context_not_equal_canon',
)
SECTION_THREE_RULES = (
    'Genesis specialness is justified by bootstrap necessity and canonical-lineage',
    'CDL-V6 is a narrow extraordinary path for capture, constitutional violation, or',
    'Genesis is the recursive self-anchor for canonical public lineage, but that',
    'Genesis extraordinary intervention remains bounded by ratified trigger, audit,',
)
SECTION_FOUR_RULES = (
    'Genesis authority must recede through ratified mechanisms, not through vague',
    'Genesis governance dilution, operational caps, and emergency-path bounds are',
    'The current freshness and accrual artifacts remain supporting context and not',
    '- founder fade-out mechanics',
    '- founder operational caps',
    '- globally normalized governance share',
)
SECTION_FIVE_RULES = (
    'Canonical public ILC requires Genesis-rooted artifact lineage.',
    'A different Genesis root means a different network rather than an equivalent',
    'A stripped public-legitimacy chain that no longer traces through canonical',
    'Fork signaling, badges, or user-facing eligibility markers remain derivative of',
    'Later governance must extend the canonical lineage rather than replace it with',
)
SECTION_SIX_RULES = (
    'Topological Exemption remains rationale, not self-executing law.',
    'The remaining non-equal-canon Genesis items stay labeled as supporting context',
    '- Genesis governance dilution closure',
    '- freshness-gate provenance closure',
    '- Genesis accrual-governor provenance reconciliation',
)
FORBIDDEN_RULES = (
    '- describing Genesis authority as informal founder discretion',
    '- treating `CDL-V6` as a general parallel governance path',
    '- treating analysis artifacts as closed public-release law by silence',
    '- treating a different Genesis root as cosmetic configuration change only',
    '- treating Genesis bootstrap specialness as permanent sovereign override',
    '- using whitepaper Topological Exemption language as self-executing law',
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


def test_section_two_labels_supporting_genesis_context_as_non_equal_canon() -> None:
    text = _read(DOC_PATH)
    for item in SUPPORTING_CONTEXT_RULES:
        assert item in text


def test_section_three_contains_bounded_genesis_authority_rules() -> None:
    text = _read(DOC_PATH)
    for item in SECTION_THREE_RULES:
        assert item in text


def test_section_four_contains_sunset_and_recession_rules() -> None:
    text = _read(DOC_PATH)
    for item in SECTION_FOUR_RULES:
        assert item in text


def test_section_five_contains_canonical_vs_fork_consequence_rules() -> None:
    text = _read(DOC_PATH)
    for item in SECTION_FIVE_RULES:
        assert item in text


def test_section_six_contains_non_equal_canon_gap_and_carry_forward_discipline() -> None:
    text = _read(DOC_PATH)
    for item in SECTION_SIX_RULES:
        assert item in text


def test_section_seven_contains_all_forbidden_interpretation_exclusions() -> None:
    text = _read(DOC_PATH)
    for item in FORBIDDEN_RULES:
        assert item in text


def test_phase_590_main_commit_touches_expected_paths_only() -> None:
    commit_ref = _resolve_commit_ref(
        subject_token=PHASE_590_SUBJECT_TOKEN,
        expected_paths=EXACT_REQUIRED_MAIN_PATHS,
    )
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS


def test_phase_590_main_commit_touches_no_adr_cdl_path_and_no_ilc_core_path() -> None:
    commit_ref = _resolve_commit_ref(
        subject_token=PHASE_590_SUBJECT_TOKEN,
        expected_paths=EXACT_REQUIRED_MAIN_PATHS,
    )
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert not any(path.startswith('docs/adr/') for path in changed_paths)
    assert not any(path.startswith('docs/specs/ilc_cdl_') for path in changed_paths)
    assert not any(path.startswith('docs/specs/ilc_cdl-') for path in changed_paths)
    assert not any('/ilc_cdl_' in path for path in changed_paths)
    assert not any(path.startswith('ilc_core/') for path in changed_paths)


def test_phase_590_backfill_commit_touches_expected_paths_only() -> None:
    commit_ref = _resolve_commit_ref(
        subject_token=PHASE_590_BACKFILL_SUBJECT_TOKEN,
        expected_paths=EXACT_REQUIRED_BACKFILL_PATHS,
    )
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_BACKFILL_PATHS


def test_phase_590_backfill_commit_touches_no_adr_cdl_path_and_no_ilc_core_path() -> None:
    commit_ref = _resolve_commit_ref(
        subject_token=PHASE_590_BACKFILL_SUBJECT_TOKEN,
        expected_paths=EXACT_REQUIRED_BACKFILL_PATHS,
    )
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert not any(path.startswith('docs/adr/') for path in changed_paths)
    assert not any(path.startswith('docs/specs/ilc_cdl_') for path in changed_paths)
    assert not any(path.startswith('docs/specs/ilc_cdl-') for path in changed_paths)
    assert not any('/ilc_cdl_' in path for path in changed_paths)
    assert not any(path.startswith('ilc_core/') for path in changed_paths)
