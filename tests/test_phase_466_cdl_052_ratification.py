from __future__ import annotations

import subprocess
from pathlib import Path

from ilc_core.testing.ratification_mutation_scope_guardrail import parse_decision_register_rows

ARTIFACT_PATH = Path('docs/specs/ilc_cdl_052_epistemic_evaluation_architecture_ratification_evidence_466_v0.1.md')
CAPSULE_PATH = Path('docs/specs/ilc_antigravity_context_capsule_v2.1.md')
DECISION_LOG_PATH = Path('docs/specs/ilc_constitutional_decision_log_v0.1.md')
TEST_PATH = Path('tests/test_phase_466_cdl_052_ratification.py')
PHASE_466_SUBJECT_TOKEN = 'phase 466 cdl-052 ratification and epistemic model closure'
EXACT_REQUIRED_MAIN_PATHS = {
    str(DECISION_LOG_PATH),
    str(ARTIFACT_PATH),
    str(CAPSULE_PATH),
    str(TEST_PATH),
}
FORBIDDEN_TREASURY_TOKEN = 'ILC_CDL_MUTATION_' + 'AUTHORIZED'
REQUIRED_HEADINGS = (
    '## 1. Ratification declaration',
    '## 2. Evidence chain',
    '## 3. Ratified constitutional contract',
    '## 4. CDL-050 and CDL-051 independence assertion',
)
REQUIRED_TOKENS = (
    'CDL-052 is ratified in Phase 466.',
    'CDL-050 and CDL-051 are ratified and remain unaffected by CDL-052 ratification.',
    'CDL-052 implementation in ilc_core/ does not occur in Phase 466.',
)


def _read(path: Path) -> str:
    return path.read_text(encoding='utf-8')


def _changed_paths_for_commit(commit_ref: str) -> set[str]:
    result = subprocess.run(['git', 'show', '--name-only', '--pretty=', commit_ref], capture_output=True, check=True, text=True)
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


def _resolve_phase_466_commit_ref() -> str:
    result = subprocess.run(['git', 'log', '--format=%H%x09%s'], capture_output=True, check=True, text=True)
    matching: list[str] = []
    for line in result.stdout.splitlines():
        if '\t' not in line:
            continue
        commit_hash, subject = line.split('\t', 1)
        if PHASE_466_SUBJECT_TOKEN not in subject.lower():
            continue
        matching.append(commit_hash)
    for commit_ref in matching:
        if _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS:
            return commit_ref
    if matching:
        raise AssertionError('phase_466_commit_subject_present_but_no_qualifying_ratification_commit')
    raise AssertionError('phase_466_commit_not_present_in_local_history')


def test_ratification_evidence_artifact_exists_and_contains_required_headings() -> None:
    text = _read(ARTIFACT_PATH)
    for heading in REQUIRED_HEADINGS:
        assert heading in text


def test_ratification_evidence_artifact_contains_required_tokens() -> None:
    text = _read(ARTIFACT_PATH)
    for token in REQUIRED_TOKENS:
        assert token in text


def test_current_decision_log_shows_cdl_052_ratified() -> None:
    rows = parse_decision_register_rows(_read(DECISION_LOG_PATH))
    assert rows['CDL-052']['status'] == 'ratified'


def test_current_decision_log_preserves_cdl_050_and_cdl_051_ratified() -> None:
    rows = parse_decision_register_rows(_read(DECISION_LOG_PATH))
    assert rows['CDL-050']['status'] == 'ratified'
    assert rows['CDL-051']['status'] == 'ratified'


def test_capsule_v21_exists_with_required_tokens() -> None:
    text = _read(CAPSULE_PATH)
    assert 'Supersedes: docs/specs/ilc_antigravity_context_capsule_v2.0.md' in text
    assert 'This capsule is self-contained.' in text
    assert 'CDL-052 is ratified. CDL-050 is ratified. CDL-051 is ratified.' in text
    assert 'Phase 467 is the next authorized phase.' in text


def test_no_forbidden_treasury_mutation_token_in_artifacts_or_test_file() -> None:
    assert FORBIDDEN_TREASURY_TOKEN not in _read(ARTIFACT_PATH)
    assert FORBIDDEN_TREASURY_TOKEN not in _read(CAPSULE_PATH)
    assert FORBIDDEN_TREASURY_TOKEN not in _read(TEST_PATH)


def test_phase_466_main_commit_touches_expected_paths_and_decision_log() -> None:
    commit_ref = _resolve_phase_466_commit_ref()
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert changed_paths == EXACT_REQUIRED_MAIN_PATHS
    assert not any(path.startswith('ilc_core/') for path in changed_paths)


def test_phase_466_commit_subject_is_present_in_local_history() -> None:
    assert _resolve_phase_466_commit_ref()
