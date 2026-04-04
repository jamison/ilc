from __future__ import annotations

import subprocess
from pathlib import Path

DOC_PATH = Path('docs/specs/ilc_public_release_claim_and_operator_honesty_package_592_v0.1.md')
DECISION_LOG_PATH = Path('docs/specs/ilc_constitutional_decision_log_v0.1.md')
TEST_PATH = Path('tests/test_phase_592_public_release_claim_and_operator_honesty_package.py')
WALKTHROUGH_PATH = Path('docs/phases/phase_592_g8_public_release_claim_and_operator_honesty_package_walkthrough.md')
STATUS_PATH = Path('docs/phases/STATUS.md')
PHASE_592_SUBJECT_TOKEN = 'phase 592 public release claim honesty package'
PHASE_592_BACKFILL_SUBJECT_TOKEN = 'phase 592 walkthrough and status backfill'
EXACT_REQUIRED_MAIN_PATHS = {
    str(DOC_PATH),
    str(TEST_PATH),
}
EXACT_REQUIRED_BACKFILL_PATHS = {
    str(WALKTHROUGH_PATH),
    str(STATUS_PATH),
}
REQUIRED_HEADINGS = (
    '## 1. Public release-claim target',
    '## 2. Dependency tiers and bounded evidence inputs',
    '## 3. Authorized bounded public claims',
    '## 4. Mandatory non-claims and deferred scope',
    '## 5. Operator honesty and machine-legible disclosure rules',
    '## 6. Forbidden interpretations and exclusions',
    '## 7. Explicit deferrals to later phases',
)
REQUIRED_TOKENS = (
    'public_release_claim_must_bind_to_phase_591_runtime_boundary',
    'bounded_public_rc_claim_not_mainnet_equivalence_claim',
    'candidate_manifest_release_claim_and_delta_must_remain_machine_legible',
    'operator_honesty_requires_explicit_pending_and_deferred_scope',
    'publication_pending_items_must_be_disclosed_not_implied_complete',
    'post_rc_deferred_scope_must_be_disclosed_not_silently_omitted',
    'economic_claim_summary_must_match_checked_runtime_evidence',
    'curated_operator_controlled_boundary_must_be_disclosed',
    'public_release_claim_must_not_overclaim_genesis_or_governance_closure',
    'public_release_claim_must_not_overclaim_hostile_internet_or_permissionless_admission',
    'harness_agnostic_boundary_must_be_preserved_in_public_claim_package',
    'operator_honesty_package_not_public_legitimacy_substitute',
    'phase_593_coherence_report_must_consume_phase_592_honesty_package',
)
DEPENDENCY_ITEMS = (
    '`docs/specs/ilc_window_585_594_candidate_phase_grouping_v0.1.md`',
    '`docs/specs/ilc_phase_585_594_sequence_lock_v0.1.md`',
    '`docs/specs/ilc_public_runtime_integration_over_receipt_boundary_591_v0.1.md`',
    '`docs/specs/ilc_genesis_authority_sunset_and_fork_legitimacy_coherence_lock_590_v0.1.md`',
    '`docs/adr/ADR_0026_Protocol_vs_Harness_Product_Boundary.md`',
    '`docs/adr/ADR_0027_Canonical_Self_Describing_Bootstrap_and_Receipt_Boundary.md`',
    '`tools/run_rc0_1_release_candidate.py`',
    '`tools/run_rc0_1_release_claim.py`',
    '`tools/check_rc0_1_release_claim.py`',
    '`tools/render_rc0_1_readiness_delta.py`',
)
BOUNDED_CONTEXT_RULES = (
    'the release-candidate, release-claim, and readiness-delta toolchain is bounded evidence tooling rather than public law by itself',
    '`tools/run_rc0_1_release_candidate.py`, `tools/run_rc0_1_release_claim.py`, `tools/check_rc0_1_release_claim.py`, and `tools/render_rc0_1_readiness_delta.py` remain machine-check surfaces',
)
SECTION_THREE_RULES = (
    'The bounded public release claim must bind to the Phase 591 runtime boundary.',
    'The current RC0.1 package is a bounded public RC claim, not a mainnet',
    'The candidate manifest, release claim, and readiness delta must remain',
    'The economic claim summary must match checked runtime evidence from the current',
    'including deterministic substrate closure, release gate, release claim,',
)
SECTION_FOUR_RULES = (
    'Operator honesty requires explicit pending and deferred scope.',
    'Publication-pending items must be disclosed and not implied complete.',
    'Post-RC deferred scope must be disclosed and not silently omitted.',
    'The public release claim must not overclaim Genesis or governance closure.',
    'The public release claim must not overclaim hostile-internet readiness,',
)
SECTION_FIVE_RULES = (
    'The package preserves the harness-agnostic boundary.',
    'The operator honesty package is not a public legitimacy substitute.',
    'The honesty package preserves machine-legible references to the candidate',
    'The honesty package distinguishes clearly between what the package proves,',
)
FORBIDDEN_RULES = (
    '- treating the RC0.1 package as a mainnet-equivalence claim',
    '- treating publication-pending items as already complete merely because the package exists',
    '- treating post-RC deferred items as silently in scope',
    '- treating the honesty package as independent public legitimacy',
    '- reopening harness-specific packaging or product surfaces through the claim language',
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


def test_section_two_labels_release_toolchain_as_bounded_evidence_context() -> None:
    text = _read(DOC_PATH)
    for item in BOUNDED_CONTEXT_RULES:
        assert item in text


def test_section_three_contains_authorized_bounded_public_claim_rules() -> None:
    text = _read(DOC_PATH)
    for item in SECTION_THREE_RULES:
        assert item in text


def test_section_four_contains_mandatory_non_claim_and_deferred_scope_rules() -> None:
    text = _read(DOC_PATH)
    for item in SECTION_FOUR_RULES:
        assert item in text


def test_section_five_contains_operator_honesty_and_disclosure_rules() -> None:
    text = _read(DOC_PATH)
    for item in SECTION_FIVE_RULES:
        assert item in text


def test_section_six_contains_all_forbidden_interpretation_exclusions() -> None:
    text = _read(DOC_PATH)
    for item in FORBIDDEN_RULES:
        assert item in text


def test_phase_592_main_commit_touches_expected_paths_only() -> None:
    commit_ref = _resolve_commit_ref(
        subject_token=PHASE_592_SUBJECT_TOKEN,
        expected_paths=EXACT_REQUIRED_MAIN_PATHS,
    )
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS


def test_phase_592_main_commit_touches_no_adr_cdl_path_and_no_ilc_core_path() -> None:
    commit_ref = _resolve_commit_ref(
        subject_token=PHASE_592_SUBJECT_TOKEN,
        expected_paths=EXACT_REQUIRED_MAIN_PATHS,
    )
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert not any(path.startswith('docs/adr/') for path in changed_paths)
    assert not any(path.startswith('docs/specs/ilc_cdl_') for path in changed_paths)
    assert not any(path.startswith('docs/specs/ilc_cdl-') for path in changed_paths)
    assert not any('/ilc_cdl_' in path for path in changed_paths)
    assert not any(path.startswith('ilc_core/') for path in changed_paths)


def test_phase_592_backfill_commit_touches_expected_paths_only() -> None:
    commit_ref = _resolve_commit_ref(
        subject_token=PHASE_592_BACKFILL_SUBJECT_TOKEN,
        expected_paths=EXACT_REQUIRED_BACKFILL_PATHS,
    )
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_BACKFILL_PATHS


def test_phase_592_backfill_commit_touches_no_adr_cdl_path_and_no_ilc_core_path() -> None:
    commit_ref = _resolve_commit_ref(
        subject_token=PHASE_592_BACKFILL_SUBJECT_TOKEN,
        expected_paths=EXACT_REQUIRED_BACKFILL_PATHS,
    )
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert not any(path.startswith('docs/adr/') for path in changed_paths)
    assert not any(path.startswith('docs/specs/ilc_cdl_') for path in changed_paths)
    assert not any(path.startswith('docs/specs/ilc_cdl-') for path in changed_paths)
    assert not any('/ilc_cdl_' in path for path in changed_paths)
    assert not any(path.startswith('ilc_core/') for path in changed_paths)
