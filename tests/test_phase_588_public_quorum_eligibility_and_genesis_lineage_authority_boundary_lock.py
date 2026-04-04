from __future__ import annotations

import subprocess
from pathlib import Path

DOC_PATH = Path('docs/specs/ilc_public_quorum_eligibility_and_genesis_lineage_authority_boundary_lock_588_v0.1.md')
DECISION_LOG_PATH = Path('docs/specs/ilc_constitutional_decision_log_v0.1.md')
TEST_PATH = Path('tests/test_phase_588_public_quorum_eligibility_and_genesis_lineage_authority_boundary_lock.py')
WALKTHROUGH_PATH = Path('docs/phases/phase_588_g8_public_quorum_eligibility_genesis_lineage_authority_boundary_lock_walkthrough.md')
STATUS_PATH = Path('docs/phases/STATUS.md')
PHASE_588_SUBJECT_TOKEN = 'phase 588 public quorum authority boundary lock'
PHASE_588_BACKFILL_SUBJECT_TOKEN = 'phase 588 walkthrough and status backfill'
EXACT_REQUIRED_MAIN_PATHS = {
    str(DOC_PATH),
    str(TEST_PATH),
}
EXACT_REQUIRED_BACKFILL_PATHS = {
    str(WALKTHROUGH_PATH),
    str(STATUS_PATH),
}
REQUIRED_HEADINGS = (
    '## 1. Public quorum authority target',
    '## 2. Dependency and inherited canon',
    '## 3. Public quorum eligibility boundary',
    '## 4. Canonical snapshot and diversity binding',
    '## 5. Genesis-lineage and ordinary-authority distinction',
    '## 6. Forbidden interpretations and exclusions',
    '## 7. Explicit deferrals to later phases',
)
REQUIRED_TOKENS = (
    'public_quorum_authority_requires_eligibility_receipt_or_proof',
    'quorum_eligibility_must_bind_to_activated_identity_lineage',
    'quorum_eligibility_must_bind_to_canonical_snapshot_or_epoch_root',
    'bootstrap_validator_set_or_quorum_seed_lineage_required_for_public_quorum_authority',
    'unactivated_or_unproven_identity_is_not_public_quorum_authority',
    'public_quorum_authority_must_preserve_cdl_v3_diversity_boundary',
    'public_quorum_authority_must_remain_compatible_with_cdl_051_quorum_record_chain',
    'genesis_rooted_bootstrap_lineage_required_for_public_quorum_authority',
    'cdl_v6_extraordinary_intervention_not_ordinary_quorum_eligibility',
    'seven_plus_one_panel_case_evaluation_not_constitutional_governance',
    'activation_and_quorum_authority_must_respect_cdl_001_canonical_authority_state_gating',
    'supporting_panel_selection_context_not_equal_canon',
    'exact_selection_algorithm_deferred_but_not_ad_hoc',
)
DEPENDENCY_ITEMS = (
    '`docs/specs/ilc_window_585_594_candidate_phase_grouping_v0.1.md`',
    '`docs/specs/ilc_phase_585_594_sequence_lock_v0.1.md`',
    '`docs/specs/ilc_public_receipt_representation_cluster_lock_586_v0.1.md`',
    '`docs/specs/ilc_public_identity_activation_and_namespace_boundary_lock_587_v0.1.md`',
    '`docs/specs/ilc_phase_585_genesis_authority_and_sunset_dependency_note_v0.1.md`',
    '`docs/adr/ADR_0014_Identity_Sybil_and_Admission_Control_Envelope.md`',
    '`docs/adr/ADR_0027_Canonical_Self_Describing_Bootstrap_and_Receipt_Boundary.md`',
    '`docs/specs/ilc_cdl_v3_quorum_diversity_ratification_evidence_332_v0.1.md`',
    '`docs/specs/ilc_cdl_051_constitutional_consensus_and_epoch_finality_ratification_evidence_443_v0.1.md`',
    '`docs/specs/ilc_cdl_045_operational_emergency_response_ratification_evidence_408_v0.1.md`',
    '`docs/specs/ilc_cdl_v6_genesis_intervention_protocol_ratification_evidence_334_v0.1.md`',
    '`docs/specs/ilc_cdl_001_signer_lineage_trust_root_contract_v0.1.md`',
    '`docs/specs/ilc_adm_003_reference_agent_architecture_v0.2.md`',
)
SUPPORTING_CONTEXT_RULES = (
    '`docs/specs/ilc_antigravity_context_capsule_v3.0.md` and earlier capsule',
    '`docs/specs/ilc_rc0_1_7_plus_1_panel_live_submission_integration_580_v0.1.md`',
    'supporting_panel_selection_context_not_equal_canon',
)
SECTION_THREE_RULES = (
    'Canonical public quorum authority requires an eligibility receipt or proof.',
    'Public quorum eligibility must bind to activated identity lineage.',
    'Public quorum eligibility must bind to a canonical snapshot or epoch root',
    'An unactivated identity, or an activated identity without an eligibility proof,',
    'The public quorum eligibility surface is a public-authority gate, not a local',
)
SECTION_FOUR_RULES = (
    'Any public quorum authority surface must preserve the ratified CDL-V3 diversity',
    'Any public quorum eligibility proof must remain compatible with the CDL-051',
    'Public quorum eligibility proof must preserve stable references for the',
    '`validator_set_hash`, `quorum_record_seed`, or',
    'Exact panel seating or VRF algorithm is not closed here, but any later',
)
SECTION_FIVE_RULES = (
    'Ordinary public quorum authority must remain continuous with the canonical',
    'CDL-V6 extraordinary intervention is not ordinary public quorum eligibility.',
    'The 7+1 panel remains case-evaluation machinery, not constitutional governance.',
    'Ordinary public quorum authority must flow through admitted activation lineage',
)
FORBIDDEN_RULES = (
    '- treating raw panel participation as equivalent to canonical public quorum authority',
    '- treating Genesis extraordinary authority as ordinary quorum eligibility',
    '- allowing unactivated identities to become public quorum participants',
    '- allowing operator-local or harness-local panel assignment rules to substitute for canonical eligibility proof',
    '- treating supporting-context 7+1 or VRF language as equal canon by silence',
    '- treating local snapshot convenience as equivalent to canonical snapshot or epoch-root lineage',
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


def test_section_two_labels_supporting_panel_selection_context_as_non_equal_canon() -> None:
    text = _read(DOC_PATH)
    for item in SUPPORTING_CONTEXT_RULES:
        assert item in text


def test_section_three_contains_public_quorum_eligibility_boundary_rules() -> None:
    text = _read(DOC_PATH)
    for item in SECTION_THREE_RULES:
        assert item in text


def test_section_four_contains_canonical_snapshot_and_diversity_binding_rules() -> None:
    text = _read(DOC_PATH)
    for item in SECTION_FOUR_RULES:
        assert item in text


def test_section_five_contains_genesis_lineage_and_ordinary_authority_distinction_rules() -> None:
    text = _read(DOC_PATH)
    for item in SECTION_FIVE_RULES:
        assert item in text


def test_section_six_contains_all_forbidden_interpretation_exclusions() -> None:
    text = _read(DOC_PATH)
    for item in FORBIDDEN_RULES:
        assert item in text


def test_phase_588_main_commit_touches_expected_paths_only() -> None:
    commit_ref = _resolve_commit_ref(
        subject_token=PHASE_588_SUBJECT_TOKEN,
        expected_paths=EXACT_REQUIRED_MAIN_PATHS,
    )
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS


def test_phase_588_main_commit_touches_no_adr_cdl_path_and_no_ilc_core_path() -> None:
    commit_ref = _resolve_commit_ref(
        subject_token=PHASE_588_SUBJECT_TOKEN,
        expected_paths=EXACT_REQUIRED_MAIN_PATHS,
    )
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert not any(path.startswith('docs/adr/') for path in changed_paths)
    assert not any(path.startswith('docs/specs/ilc_cdl_') for path in changed_paths)
    assert not any(path.startswith('docs/specs/ilc_cdl-') for path in changed_paths)
    assert not any('/ilc_cdl_' in path for path in changed_paths)
    assert not any(path.startswith('ilc_core/') for path in changed_paths)


def test_phase_588_backfill_commit_touches_expected_paths_only() -> None:
    commit_ref = _resolve_commit_ref(
        subject_token=PHASE_588_BACKFILL_SUBJECT_TOKEN,
        expected_paths=EXACT_REQUIRED_BACKFILL_PATHS,
    )
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_BACKFILL_PATHS


def test_phase_588_backfill_commit_touches_no_adr_cdl_path_and_no_ilc_core_path() -> None:
    commit_ref = _resolve_commit_ref(
        subject_token=PHASE_588_BACKFILL_SUBJECT_TOKEN,
        expected_paths=EXACT_REQUIRED_BACKFILL_PATHS,
    )
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert not any(path.startswith('docs/adr/') for path in changed_paths)
    assert not any(path.startswith('docs/specs/ilc_cdl_') for path in changed_paths)
    assert not any(path.startswith('docs/specs/ilc_cdl-') for path in changed_paths)
    assert not any('/ilc_cdl_' in path for path in changed_paths)
    assert not any(path.startswith('ilc_core/') for path in changed_paths)
