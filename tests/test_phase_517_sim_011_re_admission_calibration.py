from __future__ import annotations

import re
import subprocess
from pathlib import Path

from ilc_core.testing.ratification_mutation_scope_guardrail import parse_decision_register_rows

ARTIFACT_PATH = Path('docs/specs/ilc_sim_011_re_admission_boundary_calibration_517_v0.1.md')
DECISION_LOG_PATH = Path('docs/specs/ilc_constitutional_decision_log_v0.1.md')
TEST_PATH = Path('tests/test_phase_517_sim_011_re_admission_calibration.py')
PHASE_517_SUBJECT_TOKEN = 'phase 517 sim-011 re_admission boundary calibration'
EXACT_REQUIRED_MAIN_PATHS = {
    str(ARTIFACT_PATH),
    str(TEST_PATH),
}
REQUIRED_HEADINGS = (
    '## 1. Simulation purpose and scope',
    '## 2. SIM-010 baseline constants',
    '## 3. Re-admission scenario modeling',
    '## 4. Recommended cooldown constants',
    '## 5. CDL-046 timed_out orthogonality',
    '## 6. Simulation sufficiency declaration',
)
REQUIRED_TOKENS = (
    'recommended_cooldown_epochs_liveness_miss',
    'recommended_cooldown_epochs_equivocation',
    'recommended_cooldown_epochs_voluntary_exit',
    'sim_011_sufficient',
    'cdl_046_timed_out_orthogonal',
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
        ['git', 'show', f'{commit_ref}:{path}'],
        capture_output=True,
        check=True,
        text=True,
    )
    return result.stdout


def _resolve_phase_517_commit_ref() -> str:
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
        if PHASE_517_SUBJECT_TOKEN not in subject.lower():
            continue
        matching.append(commit_hash)
    for commit_ref in matching:
        if _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS:
            return commit_ref
    if matching:
        raise AssertionError('phase_517_commit_subject_present_but_no_qualifying_calibration_commit')
    raise AssertionError('phase_517_commit_not_present_in_local_history')


def test_synthesis_document_contains_required_headings() -> None:
    text = _read(ARTIFACT_PATH)
    for heading in REQUIRED_HEADINGS:
        assert heading in text


def test_synthesis_document_contains_required_tokens() -> None:
    text = _read(ARTIFACT_PATH)
    for token in REQUIRED_TOKENS:
        assert token in text
    assert text.count('sim_011_sufficient') == 1


def test_synthesis_document_contains_three_cooldown_constants_with_valid_ordering() -> None:
    text = _read(ARTIFACT_PATH)
    values = {
        name: int(value)
        for name, value in re.findall(r'(recommended_cooldown_epochs_[a-z_]+):\s*(\d+)', text)
    }
    assert set(values) == {
        'recommended_cooldown_epochs_liveness_miss',
        'recommended_cooldown_epochs_equivocation',
        'recommended_cooldown_epochs_voluntary_exit',
    }
    assert values['recommended_cooldown_epochs_equivocation'] > values['recommended_cooldown_epochs_liveness_miss']
    assert 0 < values['recommended_cooldown_epochs_voluntary_exit'] < values['recommended_cooldown_epochs_liveness_miss']


def test_live_cdl_log_preserves_required_statuses_and_absences() -> None:
    commit_ref = _resolve_phase_517_commit_ref()
    # The Phase-517 CDL-058 absent check is a historical prelock reference.
    rows = parse_decision_register_rows(_commit_text(str(DECISION_LOG_PATH), commit_ref))
    assert rows['CDL-055']['status'] == 'ratified'
    assert rows['CDL-056']['status'] == 'ratified'
    assert rows['CDL-057']['status'] == 'ratified'
    assert 'CDL-053' not in rows
    assert 'CDL-058' not in rows


def test_head_commit_touches_no_ilc_core_files() -> None:
    changed_paths = {
        path.strip()
        for path in subprocess.run(
            ['git', 'diff', 'HEAD', '--name-only', '--', 'ilc_core/'],
            capture_output=True,
            check=True,
            text=True,
        ).stdout.splitlines()
        if path.strip()
    }
    assert changed_paths == set()


def test_phase_517_main_commit_touches_expected_paths_only() -> None:
    commit_ref = _resolve_phase_517_commit_ref()
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS


def test_phase_517_main_commit_does_not_touch_cdl_log_and_cdl_058_remains_absent() -> None:
    commit_ref = _resolve_phase_517_commit_ref()
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert str(DECISION_LOG_PATH) not in changed_paths
    # The Phase-517 CDL-058 absent check is a historical prelock reference.
    rows = parse_decision_register_rows(_commit_text(str(DECISION_LOG_PATH), commit_ref))
    assert 'CDL-058' not in rows
