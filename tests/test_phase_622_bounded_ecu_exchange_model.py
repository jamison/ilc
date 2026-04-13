from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

SPEC_PATH = Path('docs/specs/ilc_bounded_ecu_exchange_model_622_v0.1.md')
TEST_PATH = Path('tests/test_phase_622_bounded_ecu_exchange_model.py')
WALKTHROUGH_PATH = Path(
    'docs/phases/phase_622_g8_bounded_ecu_exchange_model_spec_walkthrough.md'
)
STATUS_PATH = Path('docs/phases/STATUS.md')
DECISION_LOG_PATH = Path('docs/specs/ilc_constitutional_decision_log_v0.1.md')
PHASE_622_SUBJECT_TOKENS = ('phase 622', 'ecu exchange')
PHASE_622_BACKFILL_SUBJECT_TOKENS = ('phase 622', 'walkthrough', 'backfill')
EXACT_REQUIRED_MAIN_PATHS = {
    str(SPEC_PATH),
    str(TEST_PATH),
}
EXACT_REQUIRED_BACKFILL_PATHS = {
    str(WALKTHROUGH_PATH),
    str(STATUS_PATH),
}
REQUIRED_HEADINGS = (
    '## 1. Authorization basis and scope',
    '## 2. ECU/ILC separation constraints (must-satisfy boundaries)',
    '## 3. Bounded agent-commissioning-agent loop model',
    '## 4. Bounded constraints under Option D',
    '## 5. Relationship to runtime and CDL-053',
    '## 6. AG-gate assessment',
    '## 7. Deferred items and exclusions',
)
REQUIRED_TOKENS = (
    'bounded_ecu_exchange_model_622_locked',
    'ecu_exchange_not_ilc_payment',
    'agent_commissioning_agent_loop_spec_form',
    'option_d_posture_active_in_622',
    'cdl_053_not_prerequisite_for_622_bounded_model',
    'ecu_exchange_runtime_deferred_post_623_plus',
    'wallet_boundary_576_581_unchanged_in_622',
)
SECTION_2_SNIPPETS = (
    'ECU is the local protocol-internal productive-credit layer. It is not ILC.',
    'W_e := ΔH / E_cost',
    'ILC is the hard settlement asset.',
    'The current internal epoch-settled ledger is a bounded current',
    'It is not a public payment rail.',
    'This phase does not create a spendable ECU account surface, direct debit',
    'Any ECU-to-ILC realization path runs through the existing epoch commit and',
    'ECU exchange is not ILC payment.',
)
LOOP_SEQUENCE_SNIPPETS = (
    "1. Agent A proposes a task with a declared ECU offer bounded by A's accrual",
    '2. Agent B accepts and performs the task.',
    '3. Agent B produces a deliverable: an ILC graph submission (authored envelope)',
    '4. The graph processes the submission through the normal validation epoch path.',
    '5. Upon epoch commit, ECU accrual is credited to Agent B per the normal',
    '6. Any reconciliation of Agent A\'s declared ECU sponsorship remains a later',
)
DOES_NOT_DO_SNIPPETS = (
    'It does not create a separate payment channel outside the epoch commit path.',
    "It does not allow Agent A to debit Agent B's accrual.",
    'It does not create direct spend, transfer, or debit authority over',
    'It does not bypass the Popperian validation path for the submitted',
    'It does not allow ILC to be transferred directly between agents.',
    'It does not require Agent B to accept any task it does not choose to accept.',
)
SECTION_4_SNIPPETS = (
    'This model operates entirely within the current bounded RC/runtime internal',
    'No ILC is transferred. Only ECU accrual paths are described.',
    'No direct ECU debit, transfer, or wallet write operation is defined in this',
    'The wallet boundary from Phase 576 and Phase 581 is unchanged.',
    '`claimability_state: deferred`',
    'This model does not change `claimability_state` and does not write to the',
)
SECTION_5_SNIPPETS = (
    'Runtime implementation of this model defers to post-623+.',
    'CDL-053 Werner credit architecture remains deferred pending LT evidence track.',
    'This spec does not depend on CDL-053.',
    'it is not a prerequisite for this spec.',
    'cdl_053_not_prerequisite_for_622_bounded_model',
)
AG_GATE_ROWS = (
    '| AG-1 Co-flourishing mission |',
    '| AG-2 W_e increase |',
    '| AG-3 Epistemic integrity |',
    '| AG-4 ECU-ILC separation |',
    '| AG-5 Harness-agnostic |',
    '| AG-6 Near-infinite scale |',
    '| AG-7 Machine-legible first |',
    '| AG-8 Outbound economic loop |',
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


def _subject_matches(subject: str, tokens: tuple[str, ...]) -> bool:
    lowered = subject.lower()
    return all(token in lowered for token in tokens)


def _find_commit_ref(*, subject_tokens: tuple[str, ...]) -> str | None:
    result = subprocess.run(
        ['git', 'log', '--format=%H%x09%s'],
        capture_output=True,
        check=True,
        text=True,
    )
    for line in result.stdout.splitlines():
        if '\t' not in line:
            continue
        commit_hash, subject = line.split('\t', 1)
        if _subject_matches(subject, subject_tokens):
            return commit_hash
    return None


def _resolve_commit_ref(
    *, subject_tokens: tuple[str, ...], expected_paths: set[str]
) -> str:
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
        if _subject_matches(subject, subject_tokens):
            matches.append(commit_hash)
    for commit_ref in matches:
        if _changed_paths_for_commit(commit_ref) == expected_paths:
            return commit_ref
    raise AssertionError(f'commit_not_present_in_local_history:{subject_tokens}')


def _require_commit_or_skip(subject_tokens: tuple[str, ...]) -> None:
    if _find_commit_ref(subject_tokens=subject_tokens) is None:
        pytest.skip(f'commit_not_yet_present:{subject_tokens}')


def test_spec_exists_and_contains_all_required_headings() -> None:
    text = _read(SPEC_PATH)
    for heading in REQUIRED_HEADINGS:
        assert heading in text


def test_spec_contains_all_required_tokens() -> None:
    text = _read(SPEC_PATH)
    for token in REQUIRED_TOKENS:
        assert token in text


def test_section_2_states_ecu_ilc_separation_constraints_and_explicit_non_payment_rule() -> None:
    text = _read(SPEC_PATH)
    for snippet in SECTION_2_SNIPPETS:
        assert snippet in text


def test_section_3_defines_all_six_loop_steps_and_explicit_not_do_list() -> None:
    text = _read(SPEC_PATH)
    for snippet in LOOP_SEQUENCE_SNIPPETS:
        assert snippet in text
    for snippet in DOES_NOT_DO_SNIPPETS:
        assert snippet in text


def test_section_4_confirms_wallet_boundary_unchanged_and_claimability_deferred() -> None:
    text = _read(SPEC_PATH)
    for snippet in SECTION_4_SNIPPETS:
        assert snippet in text


def test_section_5_explicitly_states_cdl_053_not_prerequisite() -> None:
    text = _read(SPEC_PATH)
    for snippet in SECTION_5_SNIPPETS:
        assert snippet in text


def test_section_6_contains_all_ag_gate_rows_and_ag4_and_ag8_claims_with_no_fail() -> None:
    text = _read(SPEC_PATH)
    for row in AG_GATE_ROWS:
        assert row in text
    assert 'ECU exchange is not ILC payment' in text
    assert '| AG-8 Outbound economic loop | advance |' in text
    ag_rows = [line for line in text.splitlines() if line.startswith('| AG-')]
    assert ag_rows
    assert not any('| FAIL |' in line or ' FAIL ' in line for line in ag_rows)


def test_phase_622_main_commit_touches_exactly_spec_and_test_and_no_adr_cdl_or_ilc_core_paths() -> None:
    _require_commit_or_skip(PHASE_622_SUBJECT_TOKENS)
    commit_ref = _resolve_commit_ref(
        subject_tokens=PHASE_622_SUBJECT_TOKENS,
        expected_paths=EXACT_REQUIRED_MAIN_PATHS,
    )
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert changed_paths == EXACT_REQUIRED_MAIN_PATHS
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert not any(path.startswith('docs/adr/') for path in changed_paths)
    assert not any(path.startswith('docs/specs/ilc_cdl_') for path in changed_paths)
    assert not any(path.startswith('docs/specs/ilc_cdl-') for path in changed_paths)
    assert not any('/ilc_cdl_' in path for path in changed_paths)
    assert not any(path.startswith('ilc_core/') for path in changed_paths)


def test_phase_622_backfill_commit_touches_exactly_walkthrough_and_status_and_no_adr_cdl_or_ilc_core_paths() -> None:
    _require_commit_or_skip(PHASE_622_BACKFILL_SUBJECT_TOKENS)
    commit_ref = _resolve_commit_ref(
        subject_tokens=PHASE_622_BACKFILL_SUBJECT_TOKENS,
        expected_paths=EXACT_REQUIRED_BACKFILL_PATHS,
    )
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert changed_paths == EXACT_REQUIRED_BACKFILL_PATHS
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert not any(path.startswith('docs/adr/') for path in changed_paths)
    assert not any(path.startswith('docs/specs/ilc_cdl_') for path in changed_paths)
    assert not any(path.startswith('docs/specs/ilc_cdl-') for path in changed_paths)
    assert not any('/ilc_cdl_' in path for path in changed_paths)
    assert not any(path.startswith('ilc_core/') for path in changed_paths)
