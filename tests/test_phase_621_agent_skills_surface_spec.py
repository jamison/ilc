from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

SPEC_PATH = Path('docs/specs/ilc_agent_skills_surface_spec_621_v0.1.md')
TEST_PATH = Path('tests/test_phase_621_agent_skills_surface_spec.py')
WALKTHROUGH_PATH = Path(
    'docs/phases/phase_621_g8_agent_skills_surface_spec_walkthrough.md'
)
STATUS_PATH = Path('docs/phases/STATUS.md')
DECISION_LOG_PATH = Path('docs/specs/ilc_constitutional_decision_log_v0.1.md')
PHASE_621_SUBJECT_TOKENS = ('phase 621', 'agent skills')
PHASE_621_BACKFILL_SUBJECT_TOKENS = ('phase 621', 'walkthrough', 'backfill')
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
    '## 2. Tier 1 workflow skills invocation contract',
    '## 3. Tier 2 scaffold skills invocation contract',
    '## 4. CDL-033 extension requirements for ILC graph interaction',
    '## 5. AG-gate assessment',
    '## 6. Deferred items and exclusions',
)
REQUIRED_TOKENS = (
    'agent_skills_surface_spec_621_locked',
    'tier_1_skills_invocation_contract_locked',
    'tier_2_skills_invocation_contract_locked',
    'cdl_033_extension_requirements_surfaced',
    'tier_3_skill_node_deferred_per_adr_0024',
    'agent_skills_spec_form_only_no_implementation',
    'skills_root_directory_canonical_source_path',
)
TIER_1_REQUIRED_SNIPPETS = (
    '### `phase-validate`',
    '{"status": "valid|error", "file": "docs/antigravity_tasks/...", "errors": [{"line": 1, "message": "..."}]}',
    '### `phase-commit`',
    '{"main_commit": "sha-or-null", "backfill_commit": "sha-or-null", "clean": true',
    '### `run-canary`',
    '{"result": "pass|fail", "probes": [{"name": "probe_name", "status": "pass|fail", "details": "..."}]}',
    '### `cdl-status`',
    '[{"cdl": "CDL-033", "status": "ratified", "phase": "291"}]',
    '### `selftest-audit`',
    '{"gates": [{"path": "tests/test_phase_...", "selftest_guard_present": true, "env_var": "ILC_SELFTEST_GUARD"}]}',
    '### `pre-flight-check`',
    '{"ilc_core_clean": true, "cdl_env_vars_unset": true, "decision_log_clean": true}',
    '### `cdl-open`',
    'one pipe-delimited CDL row string suitable for insertion into',
)
TIER_2_REQUIRED_SKILLS = (
    '### `phase-test-scaffold`',
    '### `cdl-evidence-scaffold`',
    '### `sim-doc-scaffold`',
    '### `gate-scaffold`',
    '### `coherence-scaffold`',
)
TIER_2_REFERENCE_PATHS = (
    'tests/test_phase_620_window_620_622_sequence_lock.py',
    'tests/test_phase_616_public_receipt_schema_and_query_contract_spec.py',
    'docs/specs/ilc_cdl_033_openclaw_skill_publication_ratification_evidence_291_v0.1.md',
    'tests/test_cdl_033_ratification_291.py',
    'docs/specs/ilc_sim_passive_ecu_01_attribution_formula_calibration_542_v0.1.md',
    'tests/test_phase_542_sim_passive_ecu_01_attribution_formula.py',
    'tools/run_window_613_619_closure_gate_phase_619.sh',
    'tests/test_phase_619_window_613_619_closure_gate.py',
    'docs/specs/ilc_window_613_619_coherence_report_618_v0.1.md',
    'docs/specs/ilc_antigravity_context_capsule_v3.3.md',
    'tests/test_phase_618_mvp_gate_synthesis_and_coherence_report.py',
)
SECTION_4_SNIPPETS = (
    'CDL-033, ratified in Phase 291, governs the OpenClaw skill publication contract',
    'authored-envelope submission verbs',
    'refutation submission verbs',
    'novelty-check status query',
    'reuse-centrality query',
    'none of the seven Tier 1 workflow skills require live graph-submission or',
    'none of the five Tier 2 scaffold skills require live graph-submission or',
    'No CDL is opened in this phase to address these requirements.',
    'input to a later CDL opening in a post-622 lane',
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


def test_section_2_defines_all_seven_tier_1_skill_contracts_with_machine_legible_output() -> None:
    text = _read(SPEC_PATH)
    for snippet in TIER_1_REQUIRED_SNIPPETS:
        assert snippet in text
    assert text.count('Machine-legible output format:') >= 7


def test_section_3_defines_all_five_tier_2_scaffold_contracts_with_reference_paths() -> None:
    text = _read(SPEC_PATH)
    for skill in TIER_2_REQUIRED_SKILLS:
        assert skill in text
    for path in TIER_2_REFERENCE_PATHS:
        assert path in text
    assert text.count('Reference example paths:') >= 5


def test_section_4_states_cdl_033_extension_requirements_and_no_cdl_opening() -> None:
    text = _read(SPEC_PATH)
    for snippet in SECTION_4_SNIPPETS:
        assert snippet in text


def test_section_5_contains_all_ag_gate_rows_and_correct_ag5_note_with_no_fail() -> None:
    text = _read(SPEC_PATH)
    for row in AG_GATE_ROWS:
        assert row in text
    assert 'root `skills/` is the canonical source path; harness-specific discovery configuration may still be required.' in text
    assert 'automatic native discovery is guaranteed across all tools' not in text
    ag_rows = [line for line in text.splitlines() if line.startswith('| AG-')]
    assert ag_rows
    assert not any('| FAIL |' in line or ' FAIL ' in line for line in ag_rows)


def test_phase_621_main_commit_touches_exactly_spec_and_test_and_no_adr_cdl_or_ilc_core_paths() -> None:
    _require_commit_or_skip(PHASE_621_SUBJECT_TOKENS)
    commit_ref = _resolve_commit_ref(
        subject_tokens=PHASE_621_SUBJECT_TOKENS,
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


def test_phase_621_backfill_commit_touches_exactly_walkthrough_and_status_and_no_adr_cdl_or_ilc_core_paths() -> None:
    _require_commit_or_skip(PHASE_621_BACKFILL_SUBJECT_TOKENS)
    commit_ref = _resolve_commit_ref(
        subject_tokens=PHASE_621_BACKFILL_SUBJECT_TOKENS,
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
