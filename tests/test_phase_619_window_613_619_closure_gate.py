from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest

GATE_PATH = Path('tools/run_window_613_619_closure_gate_phase_619.sh')
HANDOFF_PATH = Path('docs/specs/ilc_window_613_619_handoff_619_v0.1.md')
WALKTHROUGH_PATH = Path(
    'docs/phases/phase_619_g8_window_613_619_closure_gate_and_handoff_walkthrough.md'
)
STATUS_PATH = Path('docs/phases/STATUS.md')
DECISION_LOG_PATH = Path('docs/specs/ilc_constitutional_decision_log_v0.1.md')
PROMPT_VALIDATION_COMMAND = '.venv/bin/python3.14 tools/validate_phase_prompt.py docs/antigravity_tasks/antigravity_prompt__phase_613_g8_window_613_619_sequence_lock.md && .venv/bin/python3.14 tools/validate_phase_prompt.py docs/antigravity_tasks/antigravity_prompt__phase_614_g8_public_init_admission_contract_spec.md && .venv/bin/python3.14 tools/validate_phase_prompt.py docs/antigravity_tasks/antigravity_prompt__phase_615_g8_ecu_to_ilc_lifecycle_contract_spec.md && .venv/bin/python3.14 tools/validate_phase_prompt.py docs/antigravity_tasks/antigravity_prompt__phase_616_g8_public_receipt_schema_and_query_contract_spec.md && .venv/bin/python3.14 tools/validate_phase_prompt.py docs/antigravity_tasks/antigravity_prompt__phase_617_g8_public_wallet_surface_contract_spec.md && .venv/bin/python3.14 tools/validate_phase_prompt.py docs/antigravity_tasks/antigravity_prompt__phase_618_g8_mvp_gate_synthesis_and_coherence_report.md && .venv/bin/python3.14 tools/validate_phase_prompt.py docs/antigravity_tasks/antigravity_prompt__phase_619_g8_window_613_619_closure_gate_and_handoff.md'
MVP_SPEC_BAND_TEST_COMMAND = 'PATH=.venv/bin:$PATH .venv/bin/pytest tests/test_phase_614_public_init_admission_contract_spec.py tests/test_phase_615_ecu_to_ilc_lifecycle_contract_spec.py tests/test_phase_616_public_receipt_schema_and_query_contract_spec.py tests/test_phase_617_public_wallet_surface_contract_spec.py -q'
SYNTHESIS_COHERENCE_TEST_COMMAND = 'PATH=.venv/bin:$PATH .venv/bin/pytest tests/test_phase_613_window_613_619_sequence_lock.py tests/test_phase_618_mvp_gate_synthesis_and_coherence_report.py -q'
CANARY_COMMAND = '.venv/bin/python3.14 tools/run_mutation_canary_phase_297.py'
CLI_CONTRACT_COMMAND = 'PATH=.venv/bin:$PATH .venv/bin/pytest tests/test_phase_619_window_613_619_closure_gate.py -q'
WALKTHROUGH_COMMAND = 'PATH=.venv/bin:$PATH .venv/bin/pytest tests/test_no_ellipses_in_walkthroughs.py -q -k phase_walkthroughs'
EXPECTED_DRY_RUN_LINES = [
    '[1/6] prompt_contract_validation',
    PROMPT_VALIDATION_COMMAND,
    '[2/6] mvp_spec_band_tests',
    MVP_SPEC_BAND_TEST_COMMAND,
    '[3/6] synthesis_and_coherence_tests',
    SYNTHESIS_COHERENCE_TEST_COMMAND,
    '[4/6] mutation_canary',
    CANARY_COMMAND,
    '[5/6] closure_gate_cli_contract',
    CLI_CONTRACT_COMMAND,
    '[6/6] walkthrough_hygiene',
    WALKTHROUGH_COMMAND,
]
REQUIRED_HEADINGS = (
    '## 1. Window identity and closure basis',
    '## 2. Inputs and closure inheritance',
    '## 3. Closure verdict summary',
    '## 4. Carry-forward items and residual blockers',
    '## 5. Next-window entry criteria and routing',
    '## 6. MemPalace refresh disposition',
    '## 7. Option-B graduation checklist: window 613-619 delta',
)
REQUIRED_TOKENS = (
    'window_613_619_handoff_619_v0_1_closed',
    'mvp_gate_spec_lane_status=pass',
    'cdl_062_remains_not_authorized',
    'option_d_posture_carried_forward',
    'wallet_boundary_576_581_unchanged',
    'agent_skills_deferred_to_post_619_window',
    'handoff_records_option_b_graduation_checklist_delta',
    'option_b_selection_remains_unauthorized_after_613_619',
    'cdl_053_werner_credit_architecture_deferred_pending_lt_evidence',
    'legal_positioning_memo_passive_ecu_and_validator_rewards_pre_rc_prerequisite',
    'bft_variant_selection_deferred_engineering_decision',
    'mvp_gate_runtime_form_window_623_plus_blocked_pending_spec_form_pass',
)
SECTION_7_ROWS = (
    '| 1. public init/admission flow tied to canonical receipts | partial | spec_closed_runtime_pending | 614 |',
    '| 2. machine-legible public receipt issuance and query/runtime contract | not_started | spec_closed_runtime_pending | 616 |',
    '| 3. user and agent visible `ECU` to `ILC` lifecycle contract | partial | spec_closed_runtime_pending | 615 |',
    '| 4. public wallet surface contract sufficient for a first participant-touch economic loop | partial | spec_closed_runtime_pending | 617 |',
    '| 5. privacy-preserving public legitimacy mechanism at the settlement layer | not_started | not_started | later lane |',
    '| 6. coupling invariants that keep protocol truth and graph legitimacy upstream of settlement backend choice | partial | partial | later lane |',
    '| 7. censorship-resistance requirement for public legitimacy surfaces | partial | partial | later lane |',
    '| 8. independence from external constitutional centers as a future-substrate selection criterion | partial | partial | later lane |',
    '| 9. transport and discovery operational maturity threshold for public participant use | partial | partial | later lane |',
)
PHASE_619_SUBJECT_TOKENS = ('phase 619', 'closure gate')
PHASE_619_BACKFILL_SUBJECT_TOKENS = ('phase 619', 'walkthrough', 'backfill')
EXACT_REQUIRED_MAIN_PATHS = {
    str(GATE_PATH),
    'tests/test_phase_619_window_613_619_closure_gate.py',
    str(HANDOFF_PATH),
}
EXACT_REQUIRED_BACKFILL_PATHS = {
    str(WALKTHROUGH_PATH),
    str(STATUS_PATH),
}


def _run_gate(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ['bash', str(GATE_PATH)] + args,
        capture_output=True,
        text=True,
        check=False,
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


def _section(text: str, heading: str, next_heading: str | None = None) -> str:
    start = text.index(heading)
    end = text.index(next_heading, start) if next_heading else len(text)
    return text[start:end]


def test_gate_script_exists_and_contains_all_required_category_labels() -> None:
    text = _read(GATE_PATH)
    assert GATE_PATH.exists()
    assert GATE_PATH.stat().st_mode & 0o111
    for label in (
        'prompt_contract_validation',
        'mvp_spec_band_tests',
        'synthesis_and_coherence_tests',
        'mutation_canary',
        'closure_gate_cli_contract',
        'walkthrough_hygiene',
    ):
        assert label in text
    assert 'ILC_PHASE_619_GATE_SELFTEST=1' in text
    assert 'run_command "${commands[$idx]}" ILC_PHASE_619_GATE_SELFTEST=1' in text

    help_result = _run_gate(['--help'])
    assert help_result.returncode == 0
    assert 'Usage: tools/run_window_613_619_closure_gate_phase_619.sh' in help_result.stdout

    dry_run = _run_gate(['--dry-run'])
    assert dry_run.returncode == 0
    assert [line.strip() for line in dry_run.stdout.splitlines() if line.strip()] == EXPECTED_DRY_RUN_LINES

    if os.environ.get('ILC_PHASE_619_GATE_SELFTEST') == '1':
        pytest.skip('phase_619_selftest_context_skip_full_gate')
    full_run = _run_gate([])
    assert full_run.returncode == 0
    assert 'phase_619_window_state=pass' in full_run.stdout
    assert 'phase_619_verdict=pass' in full_run.stdout


def test_gate_script_category_2_contains_all_four_mvp_spec_tests_in_single_pytest_call() -> None:
    text = _read(GATE_PATH)
    assert MVP_SPEC_BAND_TEST_COMMAND in text
    for path in (
        'tests/test_phase_614_public_init_admission_contract_spec.py',
        'tests/test_phase_615_ecu_to_ilc_lifecycle_contract_spec.py',
        'tests/test_phase_616_public_receipt_schema_and_query_contract_spec.py',
        'tests/test_phase_617_public_wallet_surface_contract_spec.py',
    ):
        assert path in text


def test_handoff_document_exists_and_contains_all_7_required_section_headings() -> None:
    text = _read(HANDOFF_PATH)
    for heading in REQUIRED_HEADINGS:
        assert heading in text


def test_handoff_document_contains_all_required_tokens() -> None:
    text = _read(HANDOFF_PATH)
    for token in REQUIRED_TOKENS:
        assert token in text


def test_handoff_section_3_records_verdict_agent_skills_deferred_and_option_b_readiness_delta_without_option_d_change() -> None:
    text = _read(HANDOFF_PATH)
    section = _section(
        text,
        '## 3. Closure verdict summary',
        '## 4. Carry-forward items and residual blockers',
    )
    assert 'MVP gate spec lane is closed in spec form across all five touchpoints.' in section
    assert 'Agent Skills remains deferred to a post-619 window' in section
    assert (
        'Window 613-619 advanced Option-B graduation checklist rows 1-4 to spec_closed_runtime_pending without selecting Option B or changing the active Option-D posture.'
        in section
    )


def test_handoff_section_5_records_next_window_entry_criteria_and_routing_constraints() -> None:
    text = _read(HANDOFF_PATH)
    section = _section(
        text,
        '## 5. Next-window entry criteria and routing',
        '## 6. MemPalace refresh disposition',
    )
    assert 'interface/runtime form of the five MVP touchpoints remains required' in section
    assert 'Broader public RC claims remain blocked until both spec form and interface/runtime form are complete' in section
    assert 'its post-619 authorization depends on explicit human assessment of the Phase 612 priority rule' in section
    assert 'CDL-062 and sovereign substrate execution remain not authorized' in section


def test_handoff_section_6_contains_required_mempalace_refresh_disposition_fields() -> None:
    text = _read(HANDOFF_PATH)
    section = _section(
        text,
        '## 6. MemPalace refresh disposition',
        '## 7. Option-B graduation checklist: window 613-619 delta',
    )
    assert 'Disposition: required' in section
    assert 'Active working set impacted: yes' in section
    assert 'Working-set descriptor: docs/tools/mempalace/ilc_mempalace_active_working_set_v0.1.json' in section
    assert 'Manifest: docs/tools/mempalace/ilc_mempalace_current_frontier_manifest_v0.1.json' in section
    assert 'Rebuild command: bash tools/mempalace/build_active_working_set.sh' in section


def test_phase_619_main_commit_touches_exactly_gate_script_gate_test_and_handoff() -> None:
    _require_commit_or_skip(PHASE_619_SUBJECT_TOKENS)
    commit_ref = _resolve_commit_ref(
        subject_tokens=PHASE_619_SUBJECT_TOKENS,
        expected_paths=EXACT_REQUIRED_MAIN_PATHS,
    )
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert changed_paths == EXACT_REQUIRED_MAIN_PATHS


def test_phase_619_main_commit_touches_no_cdl_no_adr_and_no_ilc_core_paths() -> None:
    _require_commit_or_skip(PHASE_619_SUBJECT_TOKENS)
    commit_ref = _resolve_commit_ref(
        subject_tokens=PHASE_619_SUBJECT_TOKENS,
        expected_paths=EXACT_REQUIRED_MAIN_PATHS,
    )
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert not any(path.startswith('docs/adr/') for path in changed_paths)
    assert not any(path.startswith('docs/specs/ilc_cdl_') for path in changed_paths)
    assert not any(path.startswith('docs/specs/ilc_cdl-') for path in changed_paths)
    assert not any('/ilc_cdl_' in path for path in changed_paths)
    assert not any(path.startswith('ilc_core/') for path in changed_paths)


def test_phase_619_backfill_commit_touches_exactly_walkthrough_and_status() -> None:
    _require_commit_or_skip(PHASE_619_BACKFILL_SUBJECT_TOKENS)
    commit_ref = _resolve_commit_ref(
        subject_tokens=PHASE_619_BACKFILL_SUBJECT_TOKENS,
        expected_paths=EXACT_REQUIRED_BACKFILL_PATHS,
    )
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert changed_paths == EXACT_REQUIRED_BACKFILL_PATHS


def test_handoff_section_7_contains_full_9_row_checklist_delta_and_does_not_claim_option_b_selected_or_rows_5_through_9_closed() -> None:
    text = _read(HANDOFF_PATH)
    section = _section(text, '## 7. Option-B graduation checklist: window 613-619 delta')
    assert 'handoff_records_option_b_graduation_checklist_delta' in section
    assert 'option_b_selection_remains_unauthorized_after_613_619' in section
    assert '| Row | Before window 613-619 | After window 613-619 | Phase |' in section
    for row in SECTION_7_ROWS:
        assert row in section
    assert (
        'Window 613-619 advanced rows 1-4 of the Option-B graduation checklist to spec_closed_runtime_pending without selecting Option B or changing the active Option-D posture.'
        in section
    )
    assert 'Option B is selected' not in section
    assert 'rows 5-9 are closed' not in section.lower()
