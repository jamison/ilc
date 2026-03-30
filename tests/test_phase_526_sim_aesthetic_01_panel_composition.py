from __future__ import annotations

import subprocess
from pathlib import Path

from ilc_core.testing.ratification_mutation_scope_guardrail import parse_decision_register_rows

SIM_DOC_PATH = Path('docs/specs/ilc_sim_aesthetic_01_panel_composition_526_v0.1.md')
DECISION_LOG_PATH = Path('docs/specs/ilc_constitutional_decision_log_v0.1.md')
TEST_PATH = Path('tests/test_phase_526_sim_aesthetic_01_panel_composition.py')
PHASE_526_SUBJECT_TOKEN = 'phase 526 sim-aesthetic-01 panel composition'
EXACT_REQUIRED_MAIN_PATHS = {
    str(SIM_DOC_PATH),
    str(TEST_PATH),
}
REQUIRED_HEADINGS = (
    '## 1. Simulation purpose and scope',
    '## 2. Register 2 content characterization',
    '## 3. Panel composition alternatives analysis',
    '## 4. Diversity-maximizing composition validation',
    '## 5. CDL-V7 7+1 panel orthogonality',
    '## 6. Simulation sufficiency declaration',
)
REQUIRED_TOKENS = (
    'sim_aesthetic_01_sufficient',
    'diversity_prediction_theorem',
    'layer_2_informational_only',
    'aesthetic_panel_diversity_maximizing',
    'register_2_expressive_content',
    'cdl_v7_panel_orthogonal',
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


def _commit_text(path: str, commit_ref: str) -> str:
    result = subprocess.run(
        ["git", "show", f"{commit_ref}:{path}"],
        capture_output=True,
        check=True,
        text=True,
    )
    return result.stdout


def _resolve_phase_526_commit_ref() -> str:
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
        if PHASE_526_SUBJECT_TOKEN not in subject.lower():
            continue
        matching.append(commit_hash)
    for commit_ref in matching:
        if _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS:
            return commit_ref
    if matching:
        raise AssertionError('phase_526_commit_subject_present_but_no_qualifying_sim_commit')
    raise AssertionError('phase_526_commit_not_present_in_local_history')


def test_sim_document_contains_required_headings() -> None:
    text = _read(SIM_DOC_PATH)
    for heading in REQUIRED_HEADINGS:
        assert heading in text


def test_sim_document_contains_required_governance_tokens() -> None:
    text = _read(SIM_DOC_PATH)
    for token in REQUIRED_TOKENS:
        assert token in text


def test_sim_document_states_rejection_rationale_for_non_selected_alternatives() -> None:
    text = _read(SIM_DOC_PATH)
    assert 'veritative-preferential mismatch' in text
    assert 'filter-bubble / average-taste pathology' in text
    assert 'Diversity-maximizing panel: selected' in text


def test_live_decision_log_preserves_required_statuses_and_absences() -> None:
    commit_ref = _resolve_phase_526_commit_ref()
    # The Phase-526 CDL-059 absent check is a historical prelock reference.
    rows = parse_decision_register_rows(_commit_text(str(DECISION_LOG_PATH), commit_ref))
    assert rows['CDL-055']['status'] == 'ratified'
    assert rows['CDL-056']['status'] == 'ratified'
    assert rows['CDL-057']['status'] == 'ratified'
    assert rows['CDL-058']['status'] == 'ratified'
    assert 'CDL-053' not in rows
    assert 'CDL-059' not in rows


def test_head_commit_touches_no_ilc_core_runtime_files() -> None:
    commit_ref = _resolve_phase_526_commit_ref()
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert not any(path.startswith('ilc_core/') for path in changed_paths)


def test_phase_526_main_commit_touches_expected_paths_only() -> None:
    commit_ref = _resolve_phase_526_commit_ref()
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS


def test_phase_526_main_commit_does_not_touch_cdl_log_and_cdl_059_remains_absent() -> None:
    commit_ref = _resolve_phase_526_commit_ref()
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert str(DECISION_LOG_PATH) not in changed_paths
    # The Phase-526 CDL-059 absent check is a historical prelock reference.
    rows = parse_decision_register_rows(_commit_text(str(DECISION_LOG_PATH), commit_ref))
    assert 'CDL-059' not in rows
