from __future__ import annotations

import subprocess
from pathlib import Path

DOC_PATH = Path('docs/specs/ilc_post_genesis_capability_proof_disposition_and_bootstrap_transition_boundary_601_v0.1.md')
TEST_PATH = Path('tests/test_phase_601_post_genesis_capability_proof_disposition_and_bootstrap_transition_boundary.py')
WALKTHROUGH_PATH = Path('docs/phases/phase_601_g8_post_genesis_capability_proof_disposition_and_bootstrap_transition_boundary_walkthrough.md')
STATUS_PATH = Path('docs/phases/STATUS.md')
DECISION_LOG_PATH = Path('docs/specs/ilc_constitutional_decision_log_v0.1.md')
PHASE_601_SUBJECT_TOKEN = 'phase 601 capability proof'
PHASE_601_BACKFILL_SUBJECT_TOKEN = 'phase 601 walkthrough and status backfill'
EXACT_REQUIRED_MAIN_PATHS = {
    str(DOC_PATH),
    str(TEST_PATH),
}
EXACT_REQUIRED_BACKFILL_PATHS = {
    str(WALKTHROUGH_PATH),
    str(STATUS_PATH),
}
REQUIRED_HEADINGS = (
    '## 1. Capability-proof disposition target',
    '## 2. Dependency tiers and inherited canon',
    '## 3. Separate-lane disposition and current non-import rule',
    '## 4. Genesis bootstrap baseline and transition boundary',
    '## 5. Snapshot, fast-bootstrap, and provenance implications',
    '## 6. Residual non-closure and explicit defer discipline',
    '## 7. Forbidden interpretations and exclusions',
    '## 8. Explicit deferrals to later phases',
)
REQUIRED_TOKENS = (
    'capability_proof_lane_is_explicit_future_lane_not_current_public_law',
    'capproof_does_not_directly_mint_additional_ilc',
    'genesis_capability_baseline_if_any_must_be_bootstrap_only_and_transitioned',
    'capability_proof_transition_must_end_in_non_privileged_reference_state',
    'snapshot_and_fast_bootstrap_provenance_must_be_explicit_where_relevant',
    'capability_proof_lane_must_not_reopen_585_595_frozen_boundaries',
    'phase_602_public_tokenomics_statement_must_consume_phase_601_capability_boundary',
)
DEPENDENCY_ITEMS = (
    '`docs/specs/ilc_phase_596_605_sequence_lock_v0.1.md`',
    '`docs/specs/ilc_window_596_605_candidate_phase_grouping_v0.1.md`',
    '`docs/specs/ilc_deterministic_genesis_economics_evidence_and_parameter_closure_600_v0.1.md`',
    '`docs/specs/ilc_phase_585_genesis_authority_and_sunset_dependency_note_v0.1.md`',
    '`docs/specs/ilc_pre_epoch_capability_proofs_v0.1.md`',
    '`docs/specs/ilc_post_genesis_capability_proof_activation_sequence_230_239_v0.1.md`',
    '`docs/specs/ilc_constitutional_decision_log_v0.1.md`',
)
SECTION_TWO_RULES = (
    'supporting context until dispositioned here and is not self-executing current law',
    'historical planning context rather than self-executing current law',
    'the 585-595 boundary stack is frozen inherited canon not reopened by this phase',
    '`phase_601_capability_proof_disposition_must_consume_phase_600_parameter_state`',
)
SECTION_THREE_RULES = (
    'capability_proof_lane_is_explicit_future_lane_not_current_public_law',
    'capproof_does_not_directly_mint_additional_ilc',
    'dedicated later approved post-605 capability-proof activation cluster',
    'no current governance, minting, or public-release claim may silently depend',
    'not a current public-release requirement by silence',
)
SECTION_FOUR_RULES = (
    'genesis_capability_baseline_if_any_must_be_bootstrap_only_and_transitioned',
    'capability_proof_transition_must_end_in_non_privileged_reference_state',
    'any Genesis capability baseline is an epoch-0 or bootstrap-start reference only',
    'the non-privileged reference state must be rolling, synthetic, or governance-updated',
    'permanent Genesis reference status is forbidden',
)
SECTION_FIVE_RULES = (
    'snapshot_and_fast_bootstrap_provenance_must_be_explicit_where_relevant',
    '`CDL-023` snapshot and fast-bootstrap provenance must be made explicit',
    'snapshot provenance may matter for transition integrity',
    'snapshot provenance does not become a new public-legitimacy shortcut',
)
SECTION_SIX_RULES = (
    'This phase dispositions decisively:',
    'This phase leaves as explicit later-lane defer:',
    'This phase refuses to settle because it belongs to future capability-proof',
)
FORBIDDEN_RULES = (
    '- silently importing capability-proof semantics into current governance or',
    '- treating capability proofs as current public-release requirement by silence,',
    '- treating Genesis bootstrap baseline as permanent privileged reference state,',
    '- using capability-proof planning as substitute for explicit Genesis closure',
    '- using capability-proof planning to reopen 585-595 frozen boundaries,',
    '- treating snapshot provenance as a new public-legitimacy or minting shortcut,',
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


def test_section_three_contains_separate_lane_and_non_import_rules() -> None:
    text = _read(DOC_PATH)
    for item in SECTION_THREE_RULES:
        assert item in text


def test_section_four_contains_bootstrap_baseline_and_transition_rules() -> None:
    text = _read(DOC_PATH)
    for item in SECTION_FOUR_RULES:
        assert item in text


def test_section_five_contains_snapshot_fast_bootstrap_and_provenance_rules() -> None:
    text = _read(DOC_PATH)
    for item in SECTION_FIVE_RULES:
        assert item in text


def test_section_six_contains_explicit_disposition_versus_defer_discipline() -> None:
    text = _read(DOC_PATH)
    for item in SECTION_SIX_RULES:
        assert item in text


def test_section_seven_contains_all_forbidden_interpretation_exclusions() -> None:
    text = _read(DOC_PATH)
    for item in FORBIDDEN_RULES:
        assert item in text


def test_main_commit_touches_exactly_doc_and_test() -> None:
    commit_ref = _resolve_commit_ref(subject_token=PHASE_601_SUBJECT_TOKEN, expected_paths=EXACT_REQUIRED_MAIN_PATHS)
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS


def test_main_commit_touches_no_adr_path_no_cdl_path_and_no_ilc_core_path() -> None:
    commit_ref = _resolve_commit_ref(subject_token=PHASE_601_SUBJECT_TOKEN, expected_paths=EXACT_REQUIRED_MAIN_PATHS)
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert not any(path.startswith('docs/adr/') for path in changed_paths)
    assert not any(path.startswith('docs/specs/ilc_cdl_') for path in changed_paths)
    assert not any(path.startswith('docs/specs/ilc_cdl-') for path in changed_paths)
    assert not any('/ilc_cdl_' in path for path in changed_paths)
    assert not any(path.startswith('ilc_core/') for path in changed_paths)


def test_backfill_commit_touches_exactly_walkthrough_and_status_and_no_forbidden_paths() -> None:
    commit_ref = _resolve_commit_ref(subject_token=PHASE_601_BACKFILL_SUBJECT_TOKEN, expected_paths=EXACT_REQUIRED_BACKFILL_PATHS)
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert changed_paths == EXACT_REQUIRED_BACKFILL_PATHS
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert not any(path.startswith('docs/adr/') for path in changed_paths)
    assert not any(path.startswith('docs/specs/ilc_cdl_') for path in changed_paths)
    assert not any(path.startswith('docs/specs/ilc_cdl-') for path in changed_paths)
    assert not any('/ilc_cdl_' in path for path in changed_paths)
    assert not any(path.startswith('ilc_core/') for path in changed_paths)
