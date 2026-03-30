from __future__ import annotations

import subprocess
from pathlib import Path

from ilc_core.testing.ratification_mutation_scope_guardrail import parse_decision_register_rows

OPENING_STUB_PATH = Path('docs/specs/ilc_cdl_059_aesthetic_panel_governance_opening_stub_529_v0.1.md')
DECISION_LOG_PATH = Path('docs/specs/ilc_constitutional_decision_log_v0.1.md')
PHASE_522_TEST_PATH = Path('tests/test_phase_522_adr_0023_cdl_scoping_analysis.py')
PHASE_523_TEST_PATH = Path('tests/test_phase_523_coherence_report_and_capsule_v2_5.py')
PHASE_525_TEST_PATH = Path('tests/test_phase_525_sequence_lock_and_carry_forward_intake.py')
TEST_PATH = Path('tests/test_phase_529_cdl_059_opening_stub.py')
PHASE_529_SUBJECT_TOKEN = 'phase 529 cdl-059 aesthetic panel governance opening'
EXACT_REQUIRED_MAIN_PATHS = {
    str(OPENING_STUB_PATH),
    str(DECISION_LOG_PATH),
    str(PHASE_522_TEST_PATH),
    str(PHASE_523_TEST_PATH),
    str(PHASE_525_TEST_PATH),
    str(TEST_PATH),
}
REQUIRED_HEADINGS = (
    '## 1. Lane identity',
    '## 2. Problem statement',
    '## 3. Candidate options',
    '## 4. Selected option',
    '## 5. Evidence anchors',
    '## 6. Governance tokens',
    '## 7. Forward obligations',
)
REQUIRED_TOKENS = (
    'cdl_059_governs_aesthetic_panel_governance',
    'selected_option: diversity_maximizing_aesthetic_panel',
    'sim_aesthetic_01_evidence_anchored',
    'layer_2_informational_only',
    'cdl_v7_7_plus_1_panel_orthogonal',
    'cdl_052_layer_3_orthogonal',
    'CDL-059 remains status: open in Phase 529.',
)


def _read(path: Path) -> str:
    return path.read_text(encoding='utf-8')


def _commit_text(path: str, commit_ref: str) -> str:
    result = subprocess.run(
        ['git', 'show', f'{commit_ref}:{path}'],
        capture_output=True,
        check=True,
        text=True,
    )
    return result.stdout


def _changed_paths_for_commit(commit_ref: str) -> set[str]:
    result = subprocess.run(
        ['git', 'show', '--name-only', '--pretty=', commit_ref],
        capture_output=True,
        check=True,
        text=True,
    )
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


def _resolve_phase_529_commit_ref() -> str:
    result = subprocess.run(
        ['git', 'log', '--format=%H%x09%s'],
        capture_output=True,
        check=True,
        text=True,
    )
    matching: list[str] = []
    for line in result.stdout.splitlines():
        if '\t' not in line:
            continue
        commit_hash, subject = line.split('\t', 1)
        if PHASE_529_SUBJECT_TOKEN not in subject.lower():
            continue
        matching.append(commit_hash)
    for commit_ref in matching:
        if _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS:
            return commit_ref
    if matching:
        raise AssertionError('phase_529_commit_subject_present_but_no_qualifying_opening_commit')
    raise AssertionError('phase_529_commit_not_present_in_local_history')


def test_opening_stub_contains_required_headings() -> None:
    text = _read(OPENING_STUB_PATH)
    for heading in REQUIRED_HEADINGS:
        assert heading in text


def test_opening_stub_contains_required_governance_tokens() -> None:
    text = _read(OPENING_STUB_PATH)
    for token in REQUIRED_TOKENS:
        assert token in text


def test_opening_stub_anchors_phase_526_and_phase_528_evidence() -> None:
    text = _read(OPENING_STUB_PATH)
    assert 'Phase 526 established the composition rule.' in text
    assert 'cdl_059_opening_authorized' in text


def test_live_decision_log_contains_open_cdl_059_row_and_preserves_other_rows() -> None:
    rows = parse_decision_register_rows(_read(DECISION_LOG_PATH))
    assert rows['CDL-055']['status'] == 'ratified'
    assert rows['CDL-056']['status'] == 'ratified'
    assert rows['CDL-057']['status'] == 'ratified'
    assert rows['CDL-058']['status'] == 'ratified'
    assert rows['CDL-059']['status'] == 'open'
    assert 'ratified_phase' not in rows['CDL-059']
    assert 'ratified_date' not in rows['CDL-059']
    assert 'CDL-053' not in rows


def test_cross_cdl_hardening_patches_are_active() -> None:
    phase_522_text = _read(PHASE_522_TEST_PATH)
    phase_523_text = _read(PHASE_523_TEST_PATH)
    phase_525_text = _read(PHASE_525_TEST_PATH)
    assert phase_522_text.count('# The Phase-522 CDL-059 absent check is a historical prelock reference.') == 2
    assert '# The Phase-523 CDL-059 absent check is a historical prelock reference.' in phase_523_text
    assert '# The Phase-525 CDL-059 absent check is a historical prelock reference.' in phase_525_text
    assert 'def _commit_text(' in phase_522_text


def test_phase_529_main_commit_touches_expected_paths_only() -> None:
    commit_ref = _resolve_phase_529_commit_ref()
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS


def test_cdl_log_at_commit_shows_cdl_059_open_and_preserved_priors() -> None:
    commit_ref = _resolve_phase_529_commit_ref()
    rows = parse_decision_register_rows(_commit_text(str(DECISION_LOG_PATH), commit_ref))
    assert rows['CDL-055']['status'] == 'ratified'
    assert rows['CDL-056']['status'] == 'ratified'
    assert rows['CDL-057']['status'] == 'ratified'
    assert rows['CDL-058']['status'] == 'ratified'
    assert rows['CDL-059']['status'] == 'open'
    assert 'CDL-053' not in rows
