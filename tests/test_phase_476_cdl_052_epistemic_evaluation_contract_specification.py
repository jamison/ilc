from __future__ import annotations

import subprocess
from pathlib import Path

ARTIFACT_PATH = Path('docs/specs/ilc_cdl_052_epistemic_evaluation_contract_specification_476_v0.1.md')
TEST_PATH = Path('tests/test_phase_476_cdl_052_epistemic_evaluation_contract_specification.py')
PHASE_476_SUBJECT_TOKEN = 'phase 476 cdl-052 epistemic evaluation contract specification'
EXACT_REQUIRED_MAIN_PATHS = {
    str(ARTIFACT_PATH),
    str(TEST_PATH),
}
REQUIRED_HEADINGS = (
    '## 1. EpistemicNodeSubmission envelope',
    '## 2. EpistemicRefutationSubmission envelope',
    '## 3. EpistemicNoveltyCheckQuery envelope',
    '## 4. EpistemicReuseCentralityQuery envelope',
    '## 5. Mode-routing decision table',
    '## 6. Error codes and mode-boundary violations',
    '## 7. CDL-033 extension obligations',
    '## 8. Naming disambiguation',
    '## 9. Implementation boundary',
)
REQUIRED_TOKENS = (
    'EpistemicNodeSubmission is the typed submission envelope for CDL-052 graph node entry.',
    'EpistemicRefutationSubmission is the typed submission envelope for CDL-052 refutation entry.',
    'EpistemicNoveltyCheckQuery is the typed query envelope for CDL-052 novelty-check status.',
    'EpistemicReuseCentralityQuery is the typed query envelope for CDL-052 reuse-centrality.',
    'EpistemicWorkTask is a genesis-layer construct in ilc_core/genesis/ and is architecturally distinct from CDL-052 evaluation-surface envelopes.',
    'ilc_core/epistemic/ does not exist in Phase 476. Phase 477 creates the package.',
    'No ilc_core/ implementation occurs in Phase 476.',
    'No decision-log mutation occurs in Phase 476.',
    'Phase 477 is the next authorized phase.',
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


def _path_exists_at_commit(path: str, commit_ref: str) -> bool:
    result = subprocess.run(
        ['git', 'cat-file', '-e', f'{commit_ref}:{path}'],
        capture_output=True,
        text=True,
    )
    return result.returncode == 0


def _resolve_phase_476_commit_ref() -> str:
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
        if PHASE_476_SUBJECT_TOKEN not in subject.lower():
            continue
        matching.append(commit_hash)
    for commit_ref in matching:
        if _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS:
            return commit_ref
    if matching:
        raise AssertionError('phase_476_commit_subject_present_but_no_qualifying_contract_spec_commit')
    raise AssertionError('phase_476_commit_not_present_in_local_history')


def test_contract_spec_artifact_exists_and_contains_required_headings() -> None:
    text = _read(ARTIFACT_PATH)
    for heading in REQUIRED_HEADINGS:
        assert heading in text


def test_contract_spec_contains_required_tokens() -> None:
    text = _read(ARTIFACT_PATH)
    for token in REQUIRED_TOKENS:
        assert token in text


def test_naming_disambiguation_references_epistemic_work_task_in_genesis() -> None:
    text = _read(ARTIFACT_PATH)
    assert 'EpistemicWorkTask' in text
    assert 'ilc_core/genesis/' in text


def test_implementation_boundary_states_phase_477_creates_package() -> None:
    text = _read(ARTIFACT_PATH)
    assert 'Phase 477 creates the package' in text
    assert 'future `ilc_core/epistemic/`' in text or 'future `ilc_core/epistemic/` runtime package' in text


def test_phase_476_main_commit_touches_expected_paths_and_package_absent_at_snapshot() -> None:
    commit_ref = _resolve_phase_476_commit_ref()
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert changed_paths == EXACT_REQUIRED_MAIN_PATHS
    assert not _path_exists_at_commit('ilc_core/epistemic/__init__.py', commit_ref)
    assert not _path_exists_at_commit('ilc_core/epistemic/node_submission_runtime.py', commit_ref)


def test_phase_476_main_commit_does_not_touch_ilc_core_or_decision_log() -> None:
    commit_ref = _resolve_phase_476_commit_ref()
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert 'docs/specs/ilc_constitutional_decision_log_v0.1.md' not in changed_paths
    assert not any(path.startswith('ilc_core/') for path in changed_paths)
