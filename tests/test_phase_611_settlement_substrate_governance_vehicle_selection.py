from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

MEMO_PATH = Path('docs/specs/ilc_settlement_substrate_governance_vehicle_selection_611_v0.1.md')
ADR_PATH = Path('docs/adr/ADR_0028_Settlement_Substrate_Graduation_and_Governance_Route.md')
CDL_STUB_PATH = Path(
    'docs/specs/ilc_cdl_062_settlement_substrate_boundary_and_public_ledger_posture_opening_stub_611_v0.1.md'
)
DECISION_LOG_PATH = Path('docs/specs/ilc_constitutional_decision_log_v0.1.md')
TEST_PATH = Path('tests/test_phase_611_settlement_substrate_governance_vehicle_selection.py')
WALKTHROUGH_PATH = Path(
    'docs/phases/phase_611_g8_window_607_612_settlement_substrate_governance_vehicle_selection_walkthrough.md'
)
STATUS_PATH = Path('docs/phases/STATUS.md')
PHASE_611_SUBJECT_TOKEN = 'phase 611 settlement substrate governance vehicle selection'
PHASE_611_BACKFILL_SUBJECT_TOKEN = 'phase 611 walkthrough and status backfill'
MAIN_PATHS_MEMO_ONLY = {str(MEMO_PATH), str(TEST_PATH)}
MAIN_PATHS_MEMO_ADR = {str(MEMO_PATH), str(TEST_PATH), str(ADR_PATH)}
MAIN_PATHS_CDL = {
    str(MEMO_PATH),
    str(TEST_PATH),
    str(CDL_STUB_PATH),
    str(DECISION_LOG_PATH),
}
BACKFILL_PATHS = {str(WALKTHROUGH_PATH), str(STATUS_PATH)}
REQUIRED_HEADINGS = (
    '## 1. Decision target and inherited state',
    '## 2. Design lemma and prohibited failure modes',
    '## 3. Governance vehicle options and decision rule',
    '## 4. Selected route and justification',
    '## 5. Option-B graduation checklist',
    '## 6. Blocker matrix, owner lanes, and earliest phases',
    '## 7. Carry-forward constraints into Phase 612',
)
REQUIRED_TOKENS = (
    'phase_611_selects_governance_vehicle_without_ratifying_final_substrate',
    'design_lemma_local_graph_work_fast_settlement_hard_to_fake',
    'waterfall_overbuild_and_protocol_first_paralysis_are_both_prohibited',
    'default_route_must_be_lowest_authority_vehicle_sufficient_for_the_required_lock',
    'phase_611_treats_censorship_resistance_as_named_substrate_constraint',
    'option_b_graduation_requires_explicit_checklist_not_inertia',
    'blocker_matrix_assigns_owner_lane_required_artifact_dependency_and_earliest_phase',
    'phase_612_must_be_mvp_gated_and_may_not_open_new_sub_lanes',
    'scenario_a_requires_no_decision_log_mutation',
    'scenario_b_requires_go_token_and_precommit_authorization',
)
SECTION_2_STRINGS = (
    'local intelligence and graph work should be cheap, fast, and abundant',
    'canonical legitimacy and settlement should be scarce, auditable, and hard to',
    'waterfall overbuild',
    'protocol-first paralysis',
)
SECTION_3_STRINGS = (
    'memo-only',
    'memo plus ADR',
    'conditional CDL opening stub',
    'select the lowest-authority vehicle sufficient to lock the required rule set',
)
SECTION_4_STRINGS = (
    'Selected route for Phase 611: memo plus ADR.',
    'memo-only is unnecessary now because it is too soft',
    'conditional CDL opening is unnecessary now because memo and ADR are not both exhausted',
)
CHECKLIST_STRINGS = (
    '| Criterion | Current state | Notes |',
    'public init/admission flow tied to canonical receipts',
    'machine-legible public receipt issuance and query/runtime contract',
    'user and agent visible `ECU` to `ILC` lifecycle contract',
    'public wallet surface contract sufficient for a first participant-touch economic loop',
    'privacy-preserving public legitimacy mechanism at the settlement layer',
    'coupling invariants that keep protocol truth and graph legitimacy upstream of settlement backend choice',
    'censorship-resistance requirement for public legitimacy surfaces',
    'independence from external constitutional centers as a future-substrate selection criterion',
    'transport and discovery operational maturity threshold for public participant use',
    '`closed`',
    '`partial`',
    '`not_started`',
)
BLOCKER_MATRIX_STRINGS = (
    '| blocker | class | why blocked now | owner lane | required artifact | dependency | earliest phase |',
    'governance vehicle for D -> B graduation',
    'public init/admission flow contract',
    'machine-legible public receipt runtime',
    'visible ECU -> ILC lifecycle contract',
    'public wallet surface beyond read-only accounting',
    'transport and discovery operational maturity',
    'privacy-preserving public legitimacy mechanism',
    'sovereign substrate selection and execution',
    'A = closable now with governance/spec work',
    'B = follow-on interface or runtime work after governance selection',
    'C = dependent on prior closure, later substrate choice, or later public-legitimacy mechanism work',
)
SECTION_7_STRINGS = (
    'Phase 612 must be MVP-gated and may not open new sub-lanes.',
    'Phase 612 must define the minimum participant-touch package rather than a broad',
    'init/admission,',
    'receipt issuance/query,',
    'ECU visibility,',
    'delayed ILC visibility,',
    'wallet/query touchpoints.',
)
ADR_REQUIRED_STRINGS = (
    '# ADR-0028: Settlement Substrate Graduation and Governance Route',
    '**Status:** Accepted',
    'Phase 611 selects memo plus ADR as the current governance route',
    'A future `CDL-062` opening is not authorized by this ADR.',
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


def _selected_route() -> str:
    text = _read(MEMO_PATH)
    if 'Selected route for Phase 611: memo plus ADR.' in text:
        return 'memo_plus_adr'
    if 'Selected route for Phase 611: memo-only.' in text:
        return 'memo_only'
    if 'Selected route for Phase 611: conditional CDL opening stub.' in text:
        return 'cdl_opening'
    raise AssertionError('selected_route_not_detectable')


def test_governance_memo_exists_and_contains_required_headings() -> None:
    text = _read(MEMO_PATH)
    for heading in REQUIRED_HEADINGS:
        assert heading in text


def test_governance_memo_contains_required_governance_tokens() -> None:
    text = _read(MEMO_PATH)
    for token in REQUIRED_TOKENS:
        assert token in text


def test_section_2_includes_design_lemma_and_both_prohibited_failure_modes() -> None:
    text = _read(MEMO_PATH)
    for item in SECTION_2_STRINGS:
        assert item in text


def test_section_3_evaluates_three_governance_routes_and_defines_lowest_authority_rule() -> None:
    text = _read(MEMO_PATH)
    for item in SECTION_3_STRINGS:
        assert item in text


def test_section_4_selects_one_route_and_justifies_why_rejected_routes_are_unnecessary_now() -> None:
    text = _read(MEMO_PATH)
    for item in SECTION_4_STRINGS:
        assert item in text


def test_section_5_contains_option_b_graduation_checklist_with_current_state_labels() -> None:
    text = _read(MEMO_PATH)
    for item in CHECKLIST_STRINGS:
        assert item in text


def test_section_6_contains_blocker_matrix_with_required_columns_and_class_definitions() -> None:
    text = _read(MEMO_PATH)
    for item in BLOCKER_MATRIX_STRINGS:
        assert item in text


def test_section_7_preserves_phase_612_as_mvp_gated_and_prohibits_new_sub_lanes() -> None:
    text = _read(MEMO_PATH)
    for item in SECTION_7_STRINGS:
        assert item in text


def test_selected_route_artifacts_exist_for_the_active_scenario() -> None:
    route = _selected_route()
    if route == 'memo_plus_adr':
        assert ADR_PATH.exists()
        adr_text = _read(ADR_PATH)
        for item in ADR_REQUIRED_STRINGS:
            assert item in adr_text
        assert not CDL_STUB_PATH.exists()
    elif route == 'memo_only':
        assert not ADR_PATH.exists()
        assert not CDL_STUB_PATH.exists()
    else:
        assert CDL_STUB_PATH.exists()


def test_phase_611_main_commit_touches_expected_paths_only_for_selected_route() -> None:
    _require_commit_or_skip(PHASE_611_SUBJECT_TOKEN)
    route = _selected_route()
    expected_paths = {
        'memo_only': MAIN_PATHS_MEMO_ONLY,
        'memo_plus_adr': MAIN_PATHS_MEMO_ADR,
        'cdl_opening': MAIN_PATHS_CDL,
    }[route]
    commit_ref = _resolve_commit_ref(
        subject_token=PHASE_611_SUBJECT_TOKEN,
        expected_paths=expected_paths,
    )
    assert _changed_paths_for_commit(commit_ref) == expected_paths


def test_phase_611_main_commit_respects_scope_for_selected_route() -> None:
    _require_commit_or_skip(PHASE_611_SUBJECT_TOKEN)
    route = _selected_route()
    expected_paths = {
        'memo_only': MAIN_PATHS_MEMO_ONLY,
        'memo_plus_adr': MAIN_PATHS_MEMO_ADR,
        'cdl_opening': MAIN_PATHS_CDL,
    }[route]
    commit_ref = _resolve_commit_ref(
        subject_token=PHASE_611_SUBJECT_TOKEN,
        expected_paths=expected_paths,
    )
    changed_paths = _changed_paths_for_commit(commit_ref)
    if route in {'memo_only', 'memo_plus_adr'}:
        assert str(DECISION_LOG_PATH) not in changed_paths
        assert not any(path.startswith('docs/specs/ilc_cdl_') for path in changed_paths)
        assert not any(path.startswith('docs/specs/ilc_cdl-') for path in changed_paths)
    if route == 'memo_only':
        assert not any(path.startswith('docs/adr/') for path in changed_paths)
    if route == 'memo_plus_adr':
        assert changed_paths == MAIN_PATHS_MEMO_ADR
    if route == 'cdl_opening':
        assert not any(path.startswith('docs/adr/') for path in changed_paths)
    assert not any(path.startswith('ilc_core/') for path in changed_paths)


def test_phase_611_backfill_commit_touches_expected_paths_only() -> None:
    _require_commit_or_skip(PHASE_611_BACKFILL_SUBJECT_TOKEN)
    commit_ref = _resolve_commit_ref(
        subject_token=PHASE_611_BACKFILL_SUBJECT_TOKEN,
        expected_paths=BACKFILL_PATHS,
    )
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert changed_paths == BACKFILL_PATHS


def test_phase_611_backfill_commit_touches_no_adr_cdl_or_ilc_core() -> None:
    _require_commit_or_skip(PHASE_611_BACKFILL_SUBJECT_TOKEN)
    commit_ref = _resolve_commit_ref(
        subject_token=PHASE_611_BACKFILL_SUBJECT_TOKEN,
        expected_paths=BACKFILL_PATHS,
    )
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert not any(path.startswith('docs/adr/') for path in changed_paths)
    assert not any(path.startswith('docs/specs/ilc_cdl_') for path in changed_paths)
    assert not any(path.startswith('docs/specs/ilc_cdl-') for path in changed_paths)
    assert not any(path.startswith('ilc_core/') for path in changed_paths)
