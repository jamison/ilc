from __future__ import annotations

import subprocess
from pathlib import Path

DOC_PATH = Path('docs/specs/ilc_rc0_1_persisted_graph_contract_lock_577_v0.1.md')
DECISION_LOG_PATH = Path('docs/specs/ilc_constitutional_decision_log_v0.1.md')
TEST_PATH = Path('tests/test_phase_577_rc0_1_persisted_graph_contract_lock.py')
PHASE_577_SUBJECT_TOKEN = 'phase 577 rc0.1 persisted graph contract lock'
EXACT_REQUIRED_MAIN_PATHS = {
    str(DOC_PATH),
    str(TEST_PATH),
}
REQUIRED_HEADINGS = (
    '## 1. Bounded RC target',
    '## 2. Minimum persisted record set',
    '## 3. Node and link contract',
    '## 4. Quorum, attribution, and epoch-commit contract',
    '## 5. Runtime-store integrity rule',
    '## 6. Explicit deferrals to RC0.1+',
)
REQUIRED_TOKENS = (
    'minimum_persisted_graph_contract_rc0_1',
    'claim_support_refute_quorum_attribution_epoch_commit_required_record_set',
    'persisted_graph_contract_precedes_live_submission_cutover',
    'runtime_store_and_manifest_identity_must_align',
    'query_surfaces_must_read_durable_state_not_projection_only',
    'graph_linkage_traceability_public_contract_deferred_post_rc0_1',
)
REQUIRED_RECORD_SET = (
    '- claim node',
    '- support edge',
    '- refute edge',
    '- quorum record',
    '- attribution record',
    '- epoch-commit record',
)
INTEGRITY_RULES = (
    'Runtime-store identity and manifest identity must align deterministically.',
    'Durable query surfaces must read from runtime state rather than projection-only',
    'Missing, mismatched, or corrupted graph-state identity must fail closed with',
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


def _resolve_phase_577_commit_ref() -> str:
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
        if PHASE_577_SUBJECT_TOKEN not in subject.lower():
            continue
        matches.append(commit_hash)
    for commit_ref in matches:
        if _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS:
            return commit_ref
    raise AssertionError('phase_577_commit_not_present_in_local_history')


def test_document_exists_and_contains_required_headings() -> None:
    text = _read(DOC_PATH)
    for heading in REQUIRED_HEADINGS:
        assert heading in text


def test_document_contains_required_governance_tokens() -> None:
    text = _read(DOC_PATH)
    for token in REQUIRED_TOKENS:
        assert token in text


def test_section_two_contains_full_required_record_set() -> None:
    text = _read(DOC_PATH)
    for item in REQUIRED_RECORD_SET:
        assert item in text


def test_section_five_contains_runtime_store_integrity_rules() -> None:
    text = _read(DOC_PATH)
    for rule in INTEGRITY_RULES:
        assert rule in text


def test_phase_577_commit_touches_expected_paths_only() -> None:
    commit_ref = _resolve_phase_577_commit_ref()
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS


def test_phase_577_commit_touches_no_cdl_path_and_no_ilc_core_path() -> None:
    commit_ref = _resolve_phase_577_commit_ref()
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert not any(path.startswith('ilc_core/') for path in changed_paths)
