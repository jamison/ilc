from __future__ import annotations

import subprocess
from pathlib import Path

DOC_PATH = Path('docs/specs/ilc_genesis_carry_forward_synthesis_and_readiness_delta_addendum_603_v0.1.md')
TEST_PATH = Path('tests/test_phase_603_genesis_carry_forward_synthesis_and_readiness_delta_addendum.py')
WALKTHROUGH_PATH = Path('docs/phases/phase_603_g8_genesis_carry_forward_synthesis_and_readiness_delta_addendum_walkthrough.md')
STATUS_PATH = Path('docs/phases/STATUS.md')
DECISION_LOG_PATH = Path('docs/specs/ilc_constitutional_decision_log_v0.1.md')
PHASE_603_SUBJECT_TOKEN = 'phase 603 carry forward synthesis'
PHASE_603_BACKFILL_SUBJECT_TOKEN = 'phase 603 walkthrough and status backfill'
EXACT_REQUIRED_MAIN_PATHS = {
    str(DOC_PATH),
    str(TEST_PATH),
}
EXACT_REQUIRED_BACKFILL_PATHS = {
    str(WALKTHROUGH_PATH),
    str(STATUS_PATH),
}
REQUIRED_HEADINGS = (
    '## 1. Synthesis target and inherited boundary',
    '## 2. Closure-state intake from phases 597-602',
    '## 3. Public-honesty and readiness-delta implications',
    '## 4. Remaining later-lane defers',
    '## 5. Forbidden interpretations and exclusions',
    '## 6. Next-lane handoff token set',
)
REQUIRED_TOKENS = (
    'genesis_carry_forward_synthesis_integrates_597_602_without_reopening_them',
    'public_honesty_surfaces_must_now_reference_597_602_closure_state',
    'remaining_later_lane_defers_must_be_enumerated_not_implied',
    'readiness_delta_addendum_must_not_overclaim_mainnet_or_public_authority_closure',
    'phase_604_coherence_report_must_consume_phase_603_synthesis',
)
INTAKE_ITEMS = (
    '`docs/specs/ilc_genesis_governance_dilution_and_brake_semantics_closure_597_v0.1.md`',
    '`docs/specs/ilc_freshness_gate_provenance_and_genesis_exemption_closure_598_v0.1.md`',
    '`docs/specs/ilc_genesis_accrual_governor_provenance_reconciliation_599_v0.1.md`',
    '`docs/specs/ilc_deterministic_genesis_economics_evidence_and_parameter_closure_600_v0.1.md`',
    '`docs/specs/ilc_post_genesis_capability_proof_disposition_and_bootstrap_transition_boundary_601_v0.1.md`',
    '`docs/specs/ilc_topological_exemption_boundary_and_public_tokenomics_statement_602_v0.1.md`',
)
SECTION_THREE_RULES = (
    'public_honesty_surfaces_must_now_reference_597_602_closure_state',
    'readiness_delta_addendum_must_not_overclaim_mainnet_or_public_authority_closure',
    'public-honesty language must now state that Genesis governance privilege has',
    'bounded RC/public statements may say deterministic Phase 600 evidence shows',
    'Topological Exemption at rationale tier',
    'it does not claim that Phase 603 itself re-ratifies the underlying law',
)
SECTION_FOUR_RULES = (
    'remaining_later_lane_defers_must_be_enumerated_not_implied',
    'completion of the Phase 305 canonical output package',
    'any Genesis economics runtime-alignment packet',
    'any Genesis-only ECU realization-controller implementation packet',
    'the actual capability-proof runtime activation lane',
    'Phase 604 coherence report and capsule update',
    'Phase 605 closure gate and handoff',
)
SECTION_SIX_RULES = (
    'phase_604_coherence_report_must_consume_phase_603_synthesis',
    'Phase 604 must consume this synthesis addendum',
    'Phase 605 must consume the resulting coherence state',
    'canonical intake summary for the remaining',
    'coherence/gate lane',
    'not a replacement for the six closure artifacts',
)
FORBIDDEN_RULES = (
    '- reopening or weakening Phases 597-602 by summary language,',
    '- using synthesis as substitute for the closure artifacts themselves,',
    '- overclaiming mainnet readiness or public authority closure beyond the actual',
    '- using this addendum to silently restore historical `8%` language,',
    '- using this addendum to silently elevate Topological Exemption into law,',
    '- using this addendum to imply that capability-proof or Genesis-only ECU',
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


def test_section_two_references_all_six_prior_closure_outputs() -> None:
    text = _read(DOC_PATH)
    for item in INTAKE_ITEMS:
        assert item in text
    assert 'Closed decisively across the intake stack:' in text
    assert 'Closed only with bounded evidence language:' in text
    assert 'Explicit later-lane defer still surviving after the intake:' in text


def test_section_three_contains_public_honesty_and_readiness_delta_implications() -> None:
    text = _read(DOC_PATH)
    for item in SECTION_THREE_RULES:
        assert item in text


def test_section_four_enumerates_remaining_later_lane_defers() -> None:
    text = _read(DOC_PATH)
    for item in SECTION_FOUR_RULES:
        assert item in text


def test_section_six_contains_the_next_lane_handoff_token_set() -> None:
    text = _read(DOC_PATH)
    for item in SECTION_SIX_RULES:
        assert item in text


def test_section_five_contains_all_forbidden_interpretation_exclusions() -> None:
    text = _read(DOC_PATH)
    for item in FORBIDDEN_RULES:
        assert item in text


def test_main_commit_touches_exactly_doc_and_test() -> None:
    commit_ref = _resolve_commit_ref(subject_token=PHASE_603_SUBJECT_TOKEN, expected_paths=EXACT_REQUIRED_MAIN_PATHS)
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS


def test_main_commit_touches_no_adr_path_no_cdl_path_and_no_ilc_core_path() -> None:
    commit_ref = _resolve_commit_ref(subject_token=PHASE_603_SUBJECT_TOKEN, expected_paths=EXACT_REQUIRED_MAIN_PATHS)
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert not any(path.startswith('docs/adr/') for path in changed_paths)
    assert not any(path.startswith('docs/specs/ilc_cdl_') for path in changed_paths)
    assert not any(path.startswith('docs/specs/ilc_cdl-') for path in changed_paths)
    assert not any('/ilc_cdl_' in path for path in changed_paths)
    assert not any(path.startswith('ilc_core/') for path in changed_paths)


def test_backfill_commit_touches_exactly_walkthrough_and_status_and_no_forbidden_paths() -> None:
    commit_ref = _resolve_commit_ref(subject_token=PHASE_603_BACKFILL_SUBJECT_TOKEN, expected_paths=EXACT_REQUIRED_BACKFILL_PATHS)
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert changed_paths == EXACT_REQUIRED_BACKFILL_PATHS
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert not any(path.startswith('docs/adr/') for path in changed_paths)
    assert not any(path.startswith('docs/specs/ilc_cdl_') for path in changed_paths)
    assert not any(path.startswith('docs/specs/ilc_cdl-') for path in changed_paths)
    assert not any('/ilc_cdl_' in path for path in changed_paths)
    assert not any(path.startswith('ilc_core/') for path in changed_paths)
