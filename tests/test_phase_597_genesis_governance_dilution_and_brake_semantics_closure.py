from __future__ import annotations

import subprocess
from pathlib import Path

DOC_PATH = Path('docs/specs/ilc_genesis_governance_dilution_and_brake_semantics_closure_597_v0.1.md')
DECISION_LOG_PATH = Path('docs/specs/ilc_constitutional_decision_log_v0.1.md')
TEST_PATH = Path('tests/test_phase_597_genesis_governance_dilution_and_brake_semantics_closure.py')
WALKTHROUGH_PATH = Path('docs/phases/phase_597_g8_genesis_governance_dilution_and_brake_semantics_closure_walkthrough.md')
STATUS_PATH = Path('docs/phases/STATUS.md')
PHASE_597_SUBJECT_TOKEN = 'phase 597 genesis governance dilution closure'
PHASE_597_BACKFILL_SUBJECT_TOKEN = 'phase 597 walkthrough and status backfill'
EXACT_REQUIRED_MAIN_PATHS = {
    str(DOC_PATH),
    str(TEST_PATH),
}
EXACT_REQUIRED_BACKFILL_PATHS = {
    str(WALKTHROUGH_PATH),
    str(STATUS_PATH),
}
REQUIRED_HEADINGS = (
    '## 1. Governance closure target',
    '## 2. Dependency tiers and inherited canon',
    '## 3. Genesis governance dilution boundary',
    '## 4. Brake-semantics and bounded specialness disposition',
    '## 5. CDL-013 compatibility and later-governance rule',
    '## 6. Residual non-closure and explicit defer discipline',
    '## 7. Forbidden interpretations and exclusions',
    '## 8. Explicit deferrals to later phases',
)
REQUIRED_TOKENS = (
    'genesis_governance_dilution_closure_exits_supporting_context',
    'genesis_bootstrap_specialness_does_not_imply_permanent_governance_floor',
    'cdl_013_global_normalization_remains_authoritative',
    'temporary_suspensive_genesis_constitutional_veto_if_retained_must_be_bootstrap_only',
    'genesis_constitutional_veto_must_use_trigger_sunset_and_hard_epoch_ceiling',
    'no_standing_genesis_governance_bonus_survives_closure',
    'genesis_governance_guardrail_must_not_become_parallel_ordinary_vote',
    'genesis_governance_fade_away_must_be_explicit_not_poetic',
    'phase_597_governance_closure_must_not_reopen_phase_590_fork_boundary',
    'phase_598_freshness_provenance_must_consume_phase_597_governance_closure',
)
DEPENDENCY_ITEMS = (
    '`docs/specs/ilc_phase_596_605_sequence_lock_v0.1.md`',
    '`docs/specs/ilc_window_596_605_candidate_phase_grouping_v0.1.md`',
    '`docs/specs/ilc_phase_585_genesis_authority_and_sunset_dependency_note_v0.1.md`',
    '`docs/specs/ilc_genesis_authority_sunset_and_fork_legitimacy_coherence_lock_590_v0.1.md`',
    '`docs/specs/ilc_window_585_594_handoff_594_v0.1.md`',
    '`docs/specs/ilc_rc0_1_strike_force_consolidation_and_runtime_hardening_595_v0.1.md`',
    '`docs/adr/ADR_0008_Node_Usefulness_vs_Governance_Weight_and_Genesis_Dilution.md`',
    '`docs/specs/ilc_constitutional_decision_log_v0.1.md`',
)
SECTION_TWO_RULES = (
    'remains supporting context only unless and until this phase narrows or',
    'Phase 590 is frozen inherited canon for canonical-vs-fork consequence,',
    'Phase 595 is frozen inherited canon for the bounded RC0.1 lane and is not a',
    'it is either closed here or named as an explicit later-lane',
    '`window_596_605_genesis_carry_forward_primary_gate`',
    '`genesis_dilution_caps_and_emergency_bounds_not_silent_discretion`',
    '`supporting_genesis_context_not_equal_canon`',
)
SECTION_THREE_RULES = (
    'Genesis governance influence dilutes under globally normalized governance',
    'Historical bootstrap specialness does not create a standing Genesis',
    'CDL-013 remains authoritative for global normalization.',
    'older baseline language must not be read as a permanent privileged governance',
    'no standing Genesis governance baseline survives as a public-governance',
    'any retained Genesis specialness is limited to the separate bootstrap-only,',
)
SECTION_FOUR_RULES = (
    'temporary suspensive Genesis constitutional veto only as a',
    'maximum one invocation per proposal identifier,',
    'maximum suspension duration of one epoch per invocation,',
    'maximum three total lifetime invocations before permanent extinction.',
    'the guardrail expires at the earliest of:',
    'epoch 60 from canonical Genesis activation,',
    'every invocation must produce a signed audit record,',
    'The retained guardrail is suspensive only.',
)
SECTION_FIVE_RULES = (
    'CDL-013 remains authoritative for globally normalized governance weight and may',
    'any retained Genesis constitutional veto is not ordinary governance weight and',
    'later governance must extend Genesis-rooted lineage without remaining captive',
    'CDL-V6 remains extraordinary emergency intervention only and must not be',
    'the retained bootstrap constitutional veto remains distinct from CDL-V6 and',
    'This phase does not reopen the Phase 590 fork consequence, the Genesis-rooted',
)
SECTION_SIX_RULES = (
    'This phase closes decisively:',
    '- the governance-dilution rule,',
    '- the exact disposition of any retained Genesis constitutional veto.',
    'This phase leaves as supporting context only:',
    'This phase leaves as explicit later-lane defer only:',
    'No governance-dilution sub-question remains silently open after this packet.',
)
FORBIDDEN_RULES = (
    '- treating Genesis bootstrap necessity as permanent governance floor,',
    '- treating any retained Genesis constitutional veto as informal founder',
    '- treating any retained Genesis constitutional veto as a veto over ordinary',
    '- treating `CDL-V6` as ordinary governance weight,',
    '- treating poetic fade-away language as equivalent to explicit governance',
    '- treating Genesis economic allocation as if it were an ordinary governance',
    '- reopening the Phase 590 fork-legitimacy consequence,',
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


def test_section_three_contains_genesis_governance_dilution_rules() -> None:
    text = _read(DOC_PATH)
    for item in SECTION_THREE_RULES:
        assert item in text


def test_section_four_contains_brake_semantics_disposition_rules() -> None:
    text = _read(DOC_PATH)
    for item in SECTION_FOUR_RULES:
        assert item in text


def test_section_five_contains_cdl_013_compatibility_and_later_governance_rules() -> None:
    text = _read(DOC_PATH)
    for item in SECTION_FIVE_RULES:
        assert item in text


def test_section_six_contains_explicit_closure_vs_defer_discipline() -> None:
    text = _read(DOC_PATH)
    for item in SECTION_SIX_RULES:
        assert item in text


def test_section_seven_contains_all_forbidden_interpretation_exclusions() -> None:
    text = _read(DOC_PATH)
    for item in FORBIDDEN_RULES:
        assert item in text


def test_phase_597_main_commit_touches_expected_paths_only() -> None:
    commit_ref = _resolve_commit_ref(
        subject_token=PHASE_597_SUBJECT_TOKEN,
        expected_paths=EXACT_REQUIRED_MAIN_PATHS,
    )
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS


def test_phase_597_main_commit_touches_no_adr_cdl_path_and_no_ilc_core_path() -> None:
    commit_ref = _resolve_commit_ref(
        subject_token=PHASE_597_SUBJECT_TOKEN,
        expected_paths=EXACT_REQUIRED_MAIN_PATHS,
    )
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert not any(path.startswith('docs/adr/') for path in changed_paths)
    assert not any(path.startswith('docs/specs/ilc_cdl_') for path in changed_paths)
    assert not any(path.startswith('docs/specs/ilc_cdl-') for path in changed_paths)
    assert not any('/ilc_cdl_' in path for path in changed_paths)
    assert not any(path.startswith('ilc_core/') for path in changed_paths)


def test_phase_597_backfill_commit_touches_expected_paths_only() -> None:
    commit_ref = _resolve_commit_ref(
        subject_token=PHASE_597_BACKFILL_SUBJECT_TOKEN,
        expected_paths=EXACT_REQUIRED_BACKFILL_PATHS,
    )
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_BACKFILL_PATHS


def test_phase_597_backfill_commit_touches_no_adr_cdl_path_and_no_ilc_core_path() -> None:
    commit_ref = _resolve_commit_ref(
        subject_token=PHASE_597_BACKFILL_SUBJECT_TOKEN,
        expected_paths=EXACT_REQUIRED_BACKFILL_PATHS,
    )
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert not any(path.startswith('docs/adr/') for path in changed_paths)
    assert not any(path.startswith('docs/specs/ilc_cdl_') for path in changed_paths)
    assert not any(path.startswith('docs/specs/ilc_cdl-') for path in changed_paths)
    assert not any('/ilc_cdl_' in path for path in changed_paths)
    assert not any(path.startswith('ilc_core/') for path in changed_paths)
