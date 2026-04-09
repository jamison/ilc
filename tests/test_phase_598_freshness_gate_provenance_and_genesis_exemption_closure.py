from __future__ import annotations

import subprocess
from pathlib import Path

DOC_PATH = Path('docs/specs/ilc_freshness_gate_provenance_and_genesis_exemption_closure_598_v0.1.md')
DECISION_LOG_PATH = Path('docs/specs/ilc_constitutional_decision_log_v0.1.md')
TEST_PATH = Path('tests/test_phase_598_freshness_gate_provenance_and_genesis_exemption_closure.py')
WALKTHROUGH_PATH = Path('docs/phases/phase_598_g8_freshness_gate_provenance_and_genesis_exemption_closure_walkthrough.md')
STATUS_PATH = Path('docs/phases/STATUS.md')
PHASE_598_SUBJECT_TOKEN = 'phase 598 freshness provenance closure'
PHASE_598_BACKFILL_SUBJECT_TOKEN = 'phase 598 walkthrough and status backfill'
EXACT_REQUIRED_MAIN_PATHS = {
    str(DOC_PATH),
    str(TEST_PATH),
}
EXACT_REQUIRED_BACKFILL_PATHS = {
    str(WALKTHROUGH_PATH),
    str(STATUS_PATH),
}
REQUIRED_HEADINGS = (
    '## 1. Freshness closure target',
    '## 2. Dependency tiers and inherited canon',
    '## 3. Current freshness posture and provenance gap',
    '## 4. Disposition of the Genesis exemption posture',
    '## 5. Genesis centrality, reuse, and persistence boundary',
    '## 6. Residual non-closure and explicit defer discipline',
    '## 7. Forbidden interpretations and exclusions',
    '## 8. Explicit deferrals to later phases',
)
REQUIRED_TOKENS = (
    'freshness_gate_provenance_closure_exits_supporting_context',
    'genesis_exempt_posture_must_be_ratified_supplemented_or_reopened_explicitly',
    'genesis_reuse_persistence_not_same_as_permanent_governance_privilege',
    'decay_vs_reuse_boundary_must_be_explicit',
    'cfr_002_context_gap_must_be_dispositioned',
    'freshness_closure_must_not_reopen_phase_597_governance_rules',
    'topological_exemption_remains_rationale_unless_explicitly_elevated',
    'phase_599_accrual_reconciliation_must_consume_phase_598_freshness_closure',
)
DEPENDENCY_ITEMS = (
    '`docs/specs/ilc_phase_596_605_sequence_lock_v0.1.md`',
    '`docs/specs/ilc_window_596_605_candidate_phase_grouping_v0.1.md`',
    '`docs/specs/ilc_genesis_governance_dilution_and_brake_semantics_closure_597_v0.1.md`',
    '`docs/specs/ilc_phase_585_genesis_authority_and_sunset_dependency_note_v0.1.md`',
    '`docs/specs/ilc_genesis_authority_sunset_and_fork_legitimacy_coherence_lock_590_v0.1.md`',
    '`docs/specs/ilc_freshness_gate_contract_v0.1.md`',
    '`docs/specs/ilc_constitutional_context_audit_v0.1.md`',
    '`docs/specs/ilc_epistemological_foundations_canonical_v0.1.md`',
    '`whitepaper/02_design_principles.md`',
)
SECTION_TWO_RULES = (
    'was supporting context only',
    'supporting explanatory context only and is not a self-executing',
    'whitepaper and epistemological rationale remain explanatory context only',
    'Phase 597 governance closure is frozen inherited canon for this window',
    '`phase_598_freshness_provenance_must_consume_phase_597_governance_closure`',
)
SECTION_THREE_RULES = (
    'The current freshness posture is the deterministic exponential-decay contract',
    '`decay_lambda = 0.25`',
    '`freshness_floor = 0.85`',
    '`genesis_exempt = true`',
    'The provenance gap was not that the posture was unknown.',
    'reuse-led persistence is',
    'not a substitute for deterministic freshness decay',
)
SECTION_FOUR_RULES = (
    'This phase chooses evidence-supplemented closure.',
    'The Genesis exemption posture is ratified here without changing the existing',
    '`ilc_core/analysis/freshness_gate.py`',
    '`tests/test_freshness_gate_phase_217.py`',
    'Phase 212 refutation-profitability invariant preserved through the safety',
    '`CDL-029` allocation split surface',
    'What is proven by this closure:',
    'What is not proven by this closure and therefore remains tolerated',
)
SECTION_FIVE_RULES = (
    'Genesis reuse persistence, foundational centrality, and canonical bootstrap',
    'freshness exemption for Genesis scoring does not create public-governance',
    'freshness/reuse language does not silently settle Genesis economic-allocation',
    'Topological Exemption remains rationale only and may not be used as a',
    'freshness_closure_must_not_reopen_phase_597_governance_rules',
)
SECTION_SIX_RULES = (
    'This phase closes decisively:',
    '- the CFR-002 decay-vs-reuse context gap,',
    '- the explicit ratification of the Genesis freshness exemption posture,',
    'This phase leaves as supporting context only:',
    'This phase leaves as explicit later-lane defer only:',
    'If later evidence shows the current freshness constants are incompatible',
)
FORBIDDEN_RULES = (
    '- treating freshness persistence as permanent governance privilege,',
    '- treating the former draft freshness contract as already-ratified law by',
    '- using Topological Exemption rhetoric as a substitute for explicit freshness',
    '- reopening governance-dilution rules already closed in Phase 597,',
    '- treating Genesis freshness exemption as if it directly settles Genesis 5',
    '- treating reuse-persistence rhetoric as a replacement for deterministic decay',
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


def test_section_three_contains_current_freshness_posture_and_provenance_gap_rules() -> None:
    text = _read(DOC_PATH)
    for item in SECTION_THREE_RULES:
        assert item in text


def test_section_four_contains_exemption_disposition_rules() -> None:
    text = _read(DOC_PATH)
    for item in SECTION_FOUR_RULES:
        assert item in text


def test_section_five_contains_centrality_reuse_boundary_rules() -> None:
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


def test_phase_598_main_commit_touches_expected_paths_only() -> None:
    commit_ref = _resolve_commit_ref(
        subject_token=PHASE_598_SUBJECT_TOKEN,
        expected_paths=EXACT_REQUIRED_MAIN_PATHS,
    )
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS


def test_phase_598_main_commit_touches_no_adr_cdl_path_and_no_ilc_core_path() -> None:
    commit_ref = _resolve_commit_ref(
        subject_token=PHASE_598_SUBJECT_TOKEN,
        expected_paths=EXACT_REQUIRED_MAIN_PATHS,
    )
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert not any(path.startswith('docs/adr/') for path in changed_paths)
    assert not any(path.startswith('docs/specs/ilc_cdl_') for path in changed_paths)
    assert not any(path.startswith('docs/specs/ilc_cdl-') for path in changed_paths)
    assert not any('/ilc_cdl_' in path for path in changed_paths)
    assert not any(path.startswith('ilc_core/') for path in changed_paths)


def test_phase_598_backfill_commit_touches_expected_paths_only() -> None:
    commit_ref = _resolve_commit_ref(
        subject_token=PHASE_598_BACKFILL_SUBJECT_TOKEN,
        expected_paths=EXACT_REQUIRED_BACKFILL_PATHS,
    )
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_BACKFILL_PATHS


def test_phase_598_backfill_commit_touches_no_adr_cdl_path_and_no_ilc_core_path() -> None:
    commit_ref = _resolve_commit_ref(
        subject_token=PHASE_598_BACKFILL_SUBJECT_TOKEN,
        expected_paths=EXACT_REQUIRED_BACKFILL_PATHS,
    )
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert not any(path.startswith('docs/adr/') for path in changed_paths)
    assert not any(path.startswith('docs/specs/ilc_cdl_') for path in changed_paths)
    assert not any(path.startswith('docs/specs/ilc_cdl-') for path in changed_paths)
    assert not any('/ilc_cdl_' in path for path in changed_paths)
    assert not any(path.startswith('ilc_core/') for path in changed_paths)
