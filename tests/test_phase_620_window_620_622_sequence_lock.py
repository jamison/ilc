from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

SEQ_LOCK_PATH = Path('docs/specs/ilc_phase_620_622_sequence_lock_v0.1.md')
DECISION_LOG_PATH = Path('docs/specs/ilc_constitutional_decision_log_v0.1.md')
TEST_PATH = Path('tests/test_phase_620_window_620_622_sequence_lock.py')
WALKTHROUGH_PATH = Path(
    'docs/phases/phase_620_g8_window_620_622_sequence_lock_walkthrough.md'
)
STATUS_PATH = Path('docs/phases/STATUS.md')
PHASE_620_SUBJECT_TOKEN = 'phase 620 window 620-622 sequence lock'
PHASE_620_BACKFILL_SUBJECT_TOKEN = 'phase 620 walkthrough and status backfill'
EXACT_REQUIRED_MAIN_PATHS = {
    str(SEQ_LOCK_PATH),
    str(TEST_PATH),
}
EXACT_REQUIRED_BACKFILL_PATHS = {
    str(WALKTHROUGH_PATH),
    str(STATUS_PATH),
}
REQUIRED_HEADINGS = (
    '## 1. Window identity and authorization basis',
    '## 2. Phase map and hard pass conditions',
    '## 3. AG-gate design basis',
    '## 4. Inherited boundary state',
    '## 5. Per-phase scope constraints',
    '## 6. Window-level exclusions',
)
REQUIRED_TOKENS = (
    'window_620_622_sequence_lock_primary_gate',
    'agent_skills_planning_lane_authorized_post_619',
    'ag_gates_registered_as_planning_filter_for_window_620_622',
    'window_620_622_parallel_to_window_623_plus',
    'tier_3_skill_node_deferred_per_adr_0024',
    'ecu_exchange_model_spec_form_only_runtime_deferred',
    'cdl_062_remains_not_authorized_in_window_620_622',
    'option_d_posture_active_in_window_620_622',
    'wallet_boundary_576_581_unchanged_in_window_620_622',
    'cdl_053_deferred_pending_lt_evidence_not_prerequisite_for_622',
)
REQUIRED_SCOPE_PHASE_MARKERS = (
    '| 620 |',
    '| 621 |',
    '| 622 |',
)
REQUIRED_AUTHORIZATION_SNIPPETS = (
    'agent_skills_deferred_to_post_619_window',
    'post-619 activation requires explicit human assessment rather',
    'Human authorization 2026-04-13 opened the Agent Skills planning lane',
    'Human assessment 2026-04-13 treats the Phase 612 priority rule as satisfied',
    'runtime form in Window 623+ is still required before broader public RC claims',
)
REQUIRED_HARD_PASS_SNIPPETS = (
    'Phase 621 Agent Skills surface spec file exists and passes its tests',
    'Phase 622 bounded ECU exchange model spec file exists and passes its tests',
    'All phase tests within the window pass with no CDL mutation, no `ilc_core/`',
    'Each phase AG-gate assessment table records at least one advance gate and',
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
REQUIRED_INHERITED_BOUNDARY_SNIPPETS = (
    'Phase 576 and Phase 581 read-only wallet boundary remains frozen',
    'Phase 609 ECU / ILC / runtime layer separation remains the controlling',
    'Phase 612 two-form MVP gate requirement remains active',
    'ADR-0028 keeps `Option D` as the active posture',
)
REQUIRED_EXCLUSION_SNIPPETS = (
    'No decision-log mutation in any Window 620-622 phase.',
    'No `ilc_core/` mutation in any Window 620-622 phase.',
    'No `CDL-062` opening; `cdl_062_remains_not_authorized_in_window_620_622`.',
    'No `Option B` selection claim.',
    'No prescription about Window 623+ runtime sequencing or timing.',
    'No Tier 3 skill_node work; `tier_3_skill_node_deferred_per_adr_0024`.',
    'No external skill import from agentskills.io or community catalogs.',
    'CDL-053 Werner credit architecture remains deferred to its own evidence track;',
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


def _find_commit_ref(*, subject_token: str) -> str | None:
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
        if subject_token in subject.lower():
            return commit_hash
    return None


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


def _require_commit_or_skip(subject_token: str) -> None:
    if _find_commit_ref(subject_token=subject_token) is None:
        pytest.skip(f'commit_not_yet_present:{subject_token}')


def test_sequence_lock_document_exists_contains_required_headings_and_scope_map() -> None:
    text = _read(SEQ_LOCK_PATH)
    for heading in REQUIRED_HEADINGS:
        assert heading in text
    for marker in REQUIRED_SCOPE_PHASE_MARKERS:
        assert marker in text


def test_sequence_lock_document_contains_required_tokens() -> None:
    text = _read(SEQ_LOCK_PATH)
    for token in REQUIRED_TOKENS:
        assert token in text


def test_section_one_records_required_authorization_basis() -> None:
    text = _read(SEQ_LOCK_PATH)
    for item in REQUIRED_AUTHORIZATION_SNIPPETS:
        assert item in text


def test_section_two_states_all_hard_pass_criteria() -> None:
    text = _read(SEQ_LOCK_PATH)
    for item in REQUIRED_HARD_PASS_SNIPPETS:
        assert item in text


def test_section_three_contains_all_ag_gate_rows_and_no_fail_assessments() -> None:
    text = _read(SEQ_LOCK_PATH)
    for row in AG_GATE_ROWS:
        assert row in text
    assert '| AG-4 ECU-ILC separation | neutral | Phase 622 must stay within Phase 609 separation boundaries; ECU exchange != ILC payment' in text
    ag_rows = [line for line in text.splitlines() if line.startswith('| AG-')]
    assert ag_rows
    assert not any('| FAIL |' in line or ' FAIL ' in line for line in ag_rows)


def test_section_four_confirms_all_inherited_boundaries_unchanged() -> None:
    text = _read(SEQ_LOCK_PATH)
    for item in REQUIRED_INHERITED_BOUNDARY_SNIPPETS:
        assert item in text


def test_section_six_contains_all_window_level_exclusions() -> None:
    text = _read(SEQ_LOCK_PATH)
    for item in REQUIRED_EXCLUSION_SNIPPETS:
        assert item in text


def test_phase_620_main_commit_touches_expected_paths_only_and_no_prohibited_paths() -> None:
    _require_commit_or_skip(PHASE_620_SUBJECT_TOKEN)
    commit_ref = _resolve_commit_ref(
        subject_token=PHASE_620_SUBJECT_TOKEN,
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


def test_phase_620_backfill_commit_touches_expected_paths_only_and_no_prohibited_paths() -> None:
    _require_commit_or_skip(PHASE_620_BACKFILL_SUBJECT_TOKEN)
    commit_ref = _resolve_commit_ref(
        subject_token=PHASE_620_BACKFILL_SUBJECT_TOKEN,
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
