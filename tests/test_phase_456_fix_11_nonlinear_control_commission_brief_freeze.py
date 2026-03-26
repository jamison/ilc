from __future__ import annotations

import re
import subprocess
from pathlib import Path

from ilc_core.testing.ratification_mutation_scope_guardrail import (
    assert_head_commit_touched_no_runtime_files,
    parse_decision_register_rows,
)

BRIEF_PATH = Path('docs/specs/ilc_treasury_sim_t_nonlinear_control_commission_brief_456_fix_11_v0.1.md')
TEST_PATH = Path('tests/test_phase_456_fix_11_nonlinear_control_commission_brief_freeze.py')
WALKTHROUGH_PATH = Path('docs/phases/phase_456_fix_11_g8_nonlinear_control_commission_brief_freeze_walkthrough.md')
STATUS_PATH = Path('docs/phases/STATUS.md')
DECISION_LOG_PATH = Path('docs/specs/ilc_constitutional_decision_log_v0.1.md')
PHASE_SUBJECT = 'docs(g8): phase 456 fix 11 nonlinear-control commission brief freeze'
FORBIDDEN_TREASURY_TOKEN = 'ILC_CDL_MUTATION_' + 'AUTHORIZED'
EXACT_REQUIRED_PATHS = {
    str(BRIEF_PATH),
    str(TEST_PATH),
    str(WALKTHROUGH_PATH),
    str(STATUS_PATH),
}
REQUIRED_FILE_PATHS = (
    BRIEF_PATH,
    TEST_PATH,
    WALKTHROUGH_PATH,
    STATUS_PATH,
)


def _read(path: Path) -> str:
    return path.read_text(encoding='utf-8')


def _section_body(text: str, heading: str) -> str:
    escaped = re.escape(heading)
    match = re.search(rf'{escaped}\n\n(.*?)(?=\n## |\Z)', text, flags=re.S)
    if not match:
        raise AssertionError(f'section_not_found:{heading}')
    return match.group(1).strip()


def _changed_paths_for_commit(commit_ref: str) -> set[str]:
    result = subprocess.run(['git', 'show', '--name-only', '--pretty=', commit_ref], capture_output=True, check=True, text=True)
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


def _read_file_at_ref(ref: str, path: str) -> str:
    result = subprocess.run(['git', 'show', f'{ref}:{path}'], capture_output=True, check=False, text=True)
    if result.returncode != 0:
        raise AssertionError(f'unable_to_read_file_at_ref:{ref}:{path}:{result.stderr.strip()}')
    return result.stdout


def _resolve_commit_ref() -> str:
    result = subprocess.run(['git', 'log', '--format=%H%x09%s'], capture_output=True, check=True, text=True)
    matches: list[str] = []
    for line in result.stdout.splitlines():
        if '\t' not in line:
            continue
        commit_hash, subject = line.split('\t', 1)
        if subject.strip() == PHASE_SUBJECT:
            matches.append(commit_hash)
    for commit_ref in matches:
        if _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_PATHS:
            return commit_ref
    if matches:
        raise AssertionError('phase_456_fix_11_commit_subject_present_but_no_qualifying_commission_brief_commit')
    raise AssertionError('phase_456_fix_11_commit_not_present_in_local_history')


def test_commission_brief_exists_and_contains_required_headings() -> None:
    assert BRIEF_PATH.exists()
    text = _read(BRIEF_PATH)
    headings = (
        '## 1. Mechanism surface reference',
        '## 2. Reference stack and paper basis',
        '## 3. Fix-12 candidate field',
        '## 4. Local-to-aggregate control interpretation',
        '## 5. Parameter freeze',
        '## 6. Success criteria and thresholds',
        '## 7. Non-execution and non-authorization statement',
    )
    for heading in headings:
        assert heading in text
        body = _section_body(text, heading)
        assert body
        assert len([line for line in body.splitlines() if line.strip()]) >= 2


def test_commission_brief_contains_reference_titles_mechanism_tokens_and_evidence_boundary() -> None:
    text = _read(BRIEF_PATH)
    required_tokens = (
        'simulations/sim_treasury_scenario5_waggle_dance_recovery_rule.py',
        'waggle_dance_codename=Waggle Dance',
        'nonlinear_control_curve',
        'nonlinear_control_curve_status=implemented',
        'A model of collective nectar source selection by honey bees: Self-organization through simple rules',
        'How Information-Mapping Patterns Determine Foraging Behaviour of a Honey Bee Colony',
        'Multiagent Decision-Making Dynamics Inspired by Honeybees',
        'Ovarian Control of Nectar Collection in the Honey Bee (Apis mellifera)',
        'How to Model Honeybee Colonies',
        'The paper stack motivates the family framing but does not substitute for measured Scenario-5 evidence.',
    )
    for token in required_tokens:
        assert token in text


def test_commission_brief_records_local_to_aggregate_interpretation_and_no_adjacency_overclaim() -> None:
    text = _read(BRIEF_PATH)
    assert 'Local linear response may aggregate into nonlinear recruitment across the graph.' in text
    assert 'Graph-indexed recruitment is a motivating interpretation for the Waggle Dance family, constrained to the implemented Fix-10 surface in Fix 11.' in text
    assert 'Graph-indexed recruitment is conceptual support for the family and not a claim that explicit adjacency-state execution already exists in Fix 10.' in text
    assert 'absolute percentage-point difference' in text
    assert 'best remaining alternative in the full candidate field frozen in this brief' in text


def test_commission_brief_freezes_fix12_field_and_non_authorization_tokens() -> None:
    text = _read(BRIEF_PATH)
    for token in (
        'nonlinear_curve_k56_g18_f22_frontier_first',
        'nonlinear_curve_k58_g18_f22_frontier_first',
        'nonlinear_curve_k60_g18_f22_frontier_first',
        'mixed_queue_and_production',
        'The Fix-12 field is frozen to the three implemented Waggle Dance candidates plus mixed_queue_and_production.',
        'Legacy production-band carry-forwards and oscillator candidates remain outside the Fix 12 field.',
        'Fix 11 does not reinterpret Window 450-459 as passed.',
        'Fix 11 does not authorize Fix 12 execution by itself.',
        'Fix 12 may execute only the candidate field frozen in this brief.',
    ):
        assert token in text


def test_walkthrough_and_status_point_to_fix12() -> None:
    walkthrough = _read(WALKTHROUGH_PATH)
    status = _read(STATUS_PATH)
    assert 'Phase 456 Fix 12 — nonlinear-control execution under the Fix-11 brief' in walkthrough
    assert 'Phase 456 Fix 12 — nonlinear-control execution under the Fix-11 brief' in status
    assert '## Phase 456 (Fix 11)' in status


def test_all_deliverables_preserve_non_authorization_boundary_and_forbidden_token_absence() -> None:
    for path in REQUIRED_FILE_PATHS:
        assert FORBIDDEN_TREASURY_TOKEN not in _read(path)
    walkthrough = _read(WALKTHROUGH_PATH)
    status = _read(STATUS_PATH)
    assert 'No Scenario-5 execution was run in Phase 456 Fix 11.' in walkthrough
    assert 'No `simulations/` or `ilc_core/` files were changed.' in walkthrough
    assert 'CDL-050 remains unopened.' in walkthrough
    assert 'CDL-050 remained unopened.' in status


def test_main_commit_touches_expected_paths_only() -> None:
    commit_ref = _resolve_commit_ref()
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_PATHS
    assert_head_commit_touched_no_runtime_files(commit_ref)


def test_commit_does_not_open_cdl_050_and_preserves_cdl_051() -> None:
    commit_ref = _resolve_commit_ref()
    before_rows = parse_decision_register_rows(_read_file_at_ref(f'{commit_ref}^', str(DECISION_LOG_PATH)))
    after_rows = parse_decision_register_rows(_read_file_at_ref(commit_ref, str(DECISION_LOG_PATH)))
    assert before_rows == after_rows
    assert before_rows['CDL-051']['status'] == 'ratified'
    assert 'CDL-050' not in before_rows
    assert 'CDL-050' not in after_rows
