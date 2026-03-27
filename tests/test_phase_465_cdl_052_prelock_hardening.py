from __future__ import annotations

import subprocess
from pathlib import Path

from ilc_core.testing.ratification_mutation_scope_guardrail import parse_decision_register_rows

ARTIFACT_PATH = Path('docs/specs/ilc_cdl_052_epistemic_evaluation_architecture_prelock_hardening_465_v0.1.md')
DECISION_LOG_PATH = Path('docs/specs/ilc_constitutional_decision_log_v0.1.md')
TEST_PATH = Path('tests/test_phase_465_cdl_052_prelock_hardening.py')
PHASE_465_SUBJECT_TOKEN = 'phase 465 cdl-052 prelock hardening and adversarial review'
EXACT_REQUIRED_MAIN_PATHS = {
    str(DECISION_LOG_PATH),
    str(ARTIFACT_PATH),
    str(TEST_PATH),
}
FORBIDDEN_TREASURY_TOKEN = 'ILC_CDL_MUTATION_' + 'AUTHORIZED'
REQUIRED_HEADINGS = (
    '## 1. Hardened constitutional language',
    '## 2. Mode boundary conditions',
    '## 3. Adversarial review findings',
    '## 4. CDL-V7 boundary consistency',
    '## 5. Scope-creep check',
    '## 6. Prelock authorization',
)
REQUIRED_TOKENS = (
    'CDL-052 prelock hardening is complete as of Phase 465.',
    'No uncapped refutation path remains.',
    'CDL-V7 boundary is explicit.',
    'Ratification proceeds in Phase 466 if and only if this prelock artifact remains clean.',
    'No Jubilee or long-horizon macro language was introduced in Phase 465.',
    'No ilc_core/ implementation occurred in Phase 465.',
)


def _read(path: Path) -> str:
    return path.read_text(encoding='utf-8')


def _changed_paths_for_commit(commit_ref: str) -> set[str]:
    result = subprocess.run(['git', 'show', '--name-only', '--pretty=', commit_ref], capture_output=True, check=True, text=True)
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


def _show_file_at_commit(commit_ref: str, path: str) -> str:
    result = subprocess.run(['git', 'show', f'{commit_ref}:{path}'], capture_output=True, check=True, text=True)
    return result.stdout


def _resolve_phase_465_commit_ref() -> str:
    result = subprocess.run(['git', 'log', '--format=%H%x09%s'], capture_output=True, check=True, text=True)
    matching: list[str] = []
    for line in result.stdout.splitlines():
        if '\t' not in line:
            continue
        commit_hash, subject = line.split('\t', 1)
        if PHASE_465_SUBJECT_TOKEN not in subject.lower():
            continue
        matching.append(commit_hash)
    for commit_ref in matching:
        if _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS:
            return commit_ref
    if matching:
        raise AssertionError('phase_465_commit_subject_present_but_no_qualifying_prelock_commit')
    raise AssertionError('phase_465_commit_not_present_in_local_history')


def test_prelock_hardening_artifact_exists_and_contains_required_headings() -> None:
    text = _read(ARTIFACT_PATH)
    for heading in REQUIRED_HEADINGS:
        assert heading in text


def test_prelock_hardening_artifact_contains_required_tokens() -> None:
    text = _read(ARTIFACT_PATH)
    for token in REQUIRED_TOKENS:
        assert token in text


def test_current_decision_log_contains_cdl_052_and_preserves_ratified_neighbors() -> None:
    rows = parse_decision_register_rows(_read(DECISION_LOG_PATH))
    assert 'CDL-052' in rows
    assert rows['CDL-050']['status'] == 'ratified'
    assert rows['CDL-051']['status'] == 'ratified'


def test_adversarial_review_section_is_non_empty_and_addresses_all_four_items() -> None:
    text = _read(ARTIFACT_PATH)
    assert 'Inwardness attack defense: pass.' in text
    assert 'Mode 3 activation threshold ambiguity: pass' in text
    assert 'corroborated_reuse designation loop: pass.' in text
    assert 'CDL-V7 boundary consistency: pass.' in text


def test_no_forbidden_treasury_mutation_token_in_artifacts_or_test_file() -> None:
    assert FORBIDDEN_TREASURY_TOKEN not in _read(ARTIFACT_PATH)
    assert FORBIDDEN_TREASURY_TOKEN not in _read(TEST_PATH)


def test_current_decision_log_keeps_cdl_050_cdl_051_cdl_052_in_order() -> None:
    text = _read(DECISION_LOG_PATH)
    assert text.index('| CDL-050 |') < text.index('| CDL-051 |') < text.index('| CDL-052 |')


def test_phase_465_commit_touches_expected_paths_and_snapshot_sets_prelock() -> None:
    commit_ref = _resolve_phase_465_commit_ref()
    changed_paths = _changed_paths_for_commit(commit_ref)
    rows = parse_decision_register_rows(_show_file_at_commit(commit_ref, str(DECISION_LOG_PATH)))
    assert changed_paths == EXACT_REQUIRED_MAIN_PATHS
    assert rows['CDL-052']['status'] == 'prelock'
    assert not any(path.startswith('ilc_core/') for path in changed_paths)


def test_phase_465_commit_subject_is_present_in_local_history() -> None:
    assert _resolve_phase_465_commit_ref()
