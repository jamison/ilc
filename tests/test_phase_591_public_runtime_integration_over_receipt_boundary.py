from __future__ import annotations

import subprocess
from pathlib import Path

DOC_PATH = Path('docs/specs/ilc_public_runtime_integration_over_receipt_boundary_591_v0.1.md')
DECISION_LOG_PATH = Path('docs/specs/ilc_constitutional_decision_log_v0.1.md')
TEST_PATH = Path('tests/test_phase_591_public_runtime_integration_over_receipt_boundary.py')
WALKTHROUGH_PATH = Path('docs/phases/phase_591_g8_public_runtime_integration_over_receipt_boundary_walkthrough.md')
STATUS_PATH = Path('docs/phases/STATUS.md')
PHASE_591_SUBJECT_TOKEN = 'phase 591 public runtime integration boundary'
PHASE_591_BACKFILL_SUBJECT_TOKEN = 'phase 591 walkthrough and status backfill'
EXACT_REQUIRED_MAIN_PATHS = {
    str(DOC_PATH),
    str(TEST_PATH),
}
EXACT_REQUIRED_BACKFILL_PATHS = {
    str(WALKTHROUGH_PATH),
    str(STATUS_PATH),
}
REQUIRED_HEADINGS = (
    '## 1. Public-runtime integration target',
    '## 2. Dependency tiers, inherited canon, and runtime anchors',
    '## 3. Runtime mapping to the frozen public boundary',
    '## 4. Bounded release-candidate evidence and proof lane',
    '## 5. Operator-visible outputs and non-claim discipline',
    '## 6. Forbidden interpretations and exclusions',
    '## 7. Explicit deferrals to later phases',
)
REQUIRED_TOKENS = (
    'public_runtime_integration_must_consume_frozen_587_590_boundary',
    'runtime_evidence_surfaces_must_map_to_activation_quorum_settlement_genesis_chain',
    'rc0_1_runtime_is_bounded_bridge_not_final_public_authority_runtime',
    'release_candidate_manifest_and_claim_are_operator_evidence_not_by_themselves_public_legitimacy',
    'public_runtime_integration_must_preserve_receipt_boundary_names_and_slots',
    'readiness_delta_is_claim_discipline_not_legitimacy_substitute',
    'public_runtime_integration_must_preserve_claim_batch_and_wallet_query_anchors',
    'public_runtime_integration_must_fail_closed_on_lineage_or_settlement_gap',
    'publication_pending_and_post_rc_scope_must_remain_machine_legible',
    'harness_boundary_from_adr_0026_remains_in_force',
    'bounded_runtime_visibility_not_public_legitimacy_by_itself',
    'no_runtime_shortcut_across_frozen_public_boundary',
    'phase_592_operator_honesty_package_must_consume_phase_591_runtime_boundary',
)
DEPENDENCY_ITEMS = (
    '`docs/specs/ilc_window_585_594_candidate_phase_grouping_v0.1.md`',
    '`docs/specs/ilc_phase_585_594_sequence_lock_v0.1.md`',
    '`docs/specs/ilc_public_receipt_representation_cluster_lock_586_v0.1.md`',
    '`docs/specs/ilc_public_identity_activation_and_namespace_boundary_lock_587_v0.1.md`',
    '`docs/specs/ilc_public_quorum_eligibility_and_genesis_lineage_authority_boundary_lock_588_v0.1.md`',
    '`docs/specs/ilc_settlement_linked_public_legitimacy_and_payout_traceability_lock_589_v0.1.md`',
    '`docs/specs/ilc_genesis_authority_sunset_and_fork_legitimacy_coherence_lock_590_v0.1.md`',
    '`docs/adr/ADR_0026_Protocol_vs_Harness_Product_Boundary.md`',
    '`docs/adr/ADR_0027_Canonical_Self_Describing_Bootstrap_and_Receipt_Boundary.md`',
    '`docs/specs/ilc_rc0_1_settlement_wallet_boundary_lock_576_v0.1.md`',
    '`docs/specs/ilc_rc0_1_ecu_settlement_wallet_query_integration_581_v0.1.md`',
    '`tools/run_rc0_1_release_candidate.py`',
    '`tools/run_rc0_1_release_claim.py`',
    '`tools/check_rc0_1_release_claim.py`',
    '`tools/render_rc0_1_readiness_delta.py`',
    '`tools/query_rc0_1_economic_state.py`',
)
BOUNDED_CONTEXT_RULES = (
    '`tools/run_rc0_1_release_candidate.py`, `tools/run_rc0_1_release_claim.py`,',
    '`tools/query_rc0_1_economic_state.py` is operator/query visibility tooling,',
    'harness_boundary_from_adr_0026_remains_in_force',
)
SECTION_THREE_RULES = (
    'The runtime/proof lane must map its public surfaces back to the frozen',
    'The bridge lane preserves the receipt-boundary names and machine-legible slots',
    'The bounded RC0.1 runtime anchors for `task_id`, `epoch_id` or `epoch_index`,',
    'The bridge lane must fail closed if lineage continuity, settled receipt-chain',
)
SECTION_FOUR_RULES = (
    'The current RC0.1 runtime is a bounded bridge over the frozen public boundary.',
    'The release-candidate manifest and release claim are operator-evidence surfaces',
    'The readiness delta is claim discipline, not a legitimacy substitute.',
    '`PUBLICATION_PENDING_ITEMS` and `POST_RC_DEFERRED_SCOPE` remain mandatory',
)
SECTION_FIVE_RULES = (
    'Operator-visible wallet, claim, query, bundle, or release output is not by',
    'Runtime visibility may expose the current bridge state only insofar as it',
)
FORBIDDEN_RULES = (
    '- treating release-candidate manifests, release claims, or readiness deltas as independent public-legitimacy roots',
    '- treating runtime visibility or wallet query visibility as public claimability by itself',
    '- treating the RC0.1 bridge runtime as equivalent to final public-authority runtime',
    '- reopening protocol meaning through harness/product tooling',
    '- inventing new authority slots that bypass the frozen receipt boundary',
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


def test_section_two_labels_runtime_release_tooling_as_bounded_implementation_context() -> None:
    text = _read(DOC_PATH)
    for item in BOUNDED_CONTEXT_RULES:
        assert item in text


def test_section_three_contains_runtime_mapping_rules() -> None:
    text = _read(DOC_PATH)
    for item in SECTION_THREE_RULES:
        assert item in text


def test_section_four_contains_bounded_release_candidate_evidence_and_proof_lane_rules() -> None:
    text = _read(DOC_PATH)
    for item in SECTION_FOUR_RULES:
        assert item in text


def test_section_five_contains_operator_visible_output_and_non_claim_discipline_rules() -> None:
    text = _read(DOC_PATH)
    for item in SECTION_FIVE_RULES:
        assert item in text


def test_section_six_contains_all_forbidden_interpretation_exclusions() -> None:
    text = _read(DOC_PATH)
    for item in FORBIDDEN_RULES:
        assert item in text


def test_phase_591_main_commit_touches_expected_paths_only() -> None:
    commit_ref = _resolve_commit_ref(
        subject_token=PHASE_591_SUBJECT_TOKEN,
        expected_paths=EXACT_REQUIRED_MAIN_PATHS,
    )
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS


def test_phase_591_main_commit_touches_no_adr_cdl_path_and_no_ilc_core_path() -> None:
    commit_ref = _resolve_commit_ref(
        subject_token=PHASE_591_SUBJECT_TOKEN,
        expected_paths=EXACT_REQUIRED_MAIN_PATHS,
    )
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert not any(path.startswith('docs/adr/') for path in changed_paths)
    assert not any(path.startswith('docs/specs/ilc_cdl_') for path in changed_paths)
    assert not any(path.startswith('docs/specs/ilc_cdl-') for path in changed_paths)
    assert not any('/ilc_cdl_' in path for path in changed_paths)
    assert not any(path.startswith('ilc_core/') for path in changed_paths)


def test_phase_591_backfill_commit_touches_expected_paths_only() -> None:
    commit_ref = _resolve_commit_ref(
        subject_token=PHASE_591_BACKFILL_SUBJECT_TOKEN,
        expected_paths=EXACT_REQUIRED_BACKFILL_PATHS,
    )
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_BACKFILL_PATHS


def test_phase_591_backfill_commit_touches_no_adr_cdl_path_and_no_ilc_core_path() -> None:
    commit_ref = _resolve_commit_ref(
        subject_token=PHASE_591_BACKFILL_SUBJECT_TOKEN,
        expected_paths=EXACT_REQUIRED_BACKFILL_PATHS,
    )
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert not any(path.startswith('docs/adr/') for path in changed_paths)
    assert not any(path.startswith('docs/specs/ilc_cdl_') for path in changed_paths)
    assert not any(path.startswith('docs/specs/ilc_cdl-') for path in changed_paths)
    assert not any('/ilc_cdl_' in path for path in changed_paths)
    assert not any(path.startswith('ilc_core/') for path in changed_paths)
