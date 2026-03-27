from __future__ import annotations

import subprocess
from pathlib import Path

ARTIFACT_PATH = Path('docs/specs/ilc_tla_plus_cdl_051_shell_specification_467_v0.1.md')
TEST_PATH = Path('tests/test_phase_467_tla_plus_cdl_051_shell_specification.py')
DECISION_LOG_PATH = Path('docs/specs/ilc_constitutional_decision_log_v0.1.md')
PHASE_467_SUBJECT_TOKEN = 'phase 467 tla-plus cdl-051 shell specification'
EXACT_REQUIRED_MAIN_PATHS = {
    str(ARTIFACT_PATH),
    str(TEST_PATH),
}
FORBIDDEN_TREASURY_TOKEN = 'ILC_CDL_MUTATION_' + 'AUTHORIZED'
REQUIRED_HEADINGS = (
    '## 1. Specification scope',
    '## 2. State variables',
    '## 3. Safety property',
    '## 4. Liveness condition',
    '## 5. Tunable parameters',
    '## 6. CDL-051 invariant mapping',
    '## 7. Limitations and open items',
)
REQUIRED_TOKENS = (
    'This is a specification document only. No ilc_core/ implementation occurs in Phase 467.',
    'CDL-051 semantics are formalized in this TLA+ shell.',
    'NoTwoHonestNodesFinalizeDifferentBlocks',
    'QUORUM_THRESHOLD',
    'CLUSTER_COUNT',
    'DIVERSITY_FLOOR',
    'VALIDATOR_COUNT',
    'CDL-051 is not amended by this specification.',
)
REQUIRED_STATE_VARIABLES = (
    'validators',
    'cluster_membership',
    'vote_weights',
    'epoch_records',
    'finality_state',
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


def _resolve_phase_467_commit_ref() -> str:
    result = subprocess.run(['git', 'log', '--format=%H%x09%s'], capture_output=True, check=True, text=True)
    matching: list[str] = []
    for line in result.stdout.splitlines():
        if '\t' not in line:
            continue
        commit_hash, subject = line.split('\t', 1)
        if PHASE_467_SUBJECT_TOKEN not in subject.lower():
            continue
        matching.append(commit_hash)
    for commit_ref in matching:
        if _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS:
            return commit_ref
    if matching:
        raise AssertionError('phase_467_commit_subject_present_but_no_qualifying_tlaplus_commit')
    raise AssertionError('phase_467_commit_not_present_in_local_history')


def test_shell_specification_exists_and_contains_required_headings() -> None:
    text = _read(ARTIFACT_PATH)
    for heading in REQUIRED_HEADINGS:
        assert heading in text


def test_shell_specification_contains_required_tokens() -> None:
    text = _read(ARTIFACT_PATH)
    for token in REQUIRED_TOKENS:
        assert token in text


def test_state_variables_section_references_all_required_variables() -> None:
    text = _read(ARTIFACT_PATH)
    marker = '## 2. State variables'
    start = text.index(marker)
    next_section = text.index('## 3. Safety property')
    section = text[start:next_section]
    for variable in REQUIRED_STATE_VARIABLES:
        assert variable in section


def test_no_forbidden_treasury_mutation_token_appears() -> None:
    assert FORBIDDEN_TREASURY_TOKEN not in _read(ARTIFACT_PATH)
    assert FORBIDDEN_TREASURY_TOKEN not in _read(TEST_PATH)


def test_phase_467_main_commit_touches_expected_paths_and_does_not_touch_decision_log_or_ilc_core() -> None:
    commit_ref = _resolve_phase_467_commit_ref()
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert changed_paths == EXACT_REQUIRED_MAIN_PATHS
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert not any(path.startswith('ilc_core/') for path in changed_paths)


def test_phase_467_commit_subject_is_present_and_does_not_amend_cdl_051() -> None:
    commit_ref = _resolve_phase_467_commit_ref()
    assert commit_ref
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert str(DECISION_LOG_PATH) not in changed_paths
