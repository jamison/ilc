from __future__ import annotations

import re
import subprocess
from pathlib import Path

MEMO_PATH = Path('docs/specs/ilc_cdl_052_genesis_integration_findings_memo_482_v0.1.md')
TEST_PATH = Path('tests/test_phase_482_cdl_052_genesis_integration_findings_memo.py')
PHASE_482_SUBJECT_TOKEN = 'phase 482 cdl-052 genesis integration findings memo'
EXACT_REQUIRED_MAIN_PATHS = {
    str(MEMO_PATH),
    str(TEST_PATH),
}
REQUIRED_HEADINGS = (
    '## 1. CDL-052 epistemic runtime completeness',
    '## 2. Genesis validator bootstrap completeness',
    '## 3. Cross-track dependency review',
    '## 4. Deferred items and governance-priority list',
    '## 5. Adversarial hardening relevance review',
    '## 6. Window 475-484 integration verdict',
)
REQUIRED_TOKENS = (
    'Staking constants are symbolically deferred pending a future simulation lane.',
    'Reuse-centrality computation backend is a stub pending a future implementation lane.',
    'Mode 3 auditor-review execution is deferred beyond Window 475-484.',
    'Validator network join and recovery flow is deferred beyond Window 475-484.',
    'Phase 476-481 regression bundle results are recorded in this memo.',
    'No ilc_core/ implementation occurs in Phase 482.',
    'No decision-log mutation occurs in Phase 482.',
    'Phase 483 is the next authorized phase.',
)


def _changed_paths_for_commit(commit_ref: str) -> set[str]:
    result = subprocess.run(
        ['git', 'show', '--name-only', '--pretty=', commit_ref],
        capture_output=True,
        check=True,
        text=True,
    )
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


def _resolve_phase_482_commit_ref() -> str:
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
        if PHASE_482_SUBJECT_TOKEN not in subject.lower():
            continue
        matching.append(commit_hash)
    for commit_ref in matching:
        if _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS:
            return commit_ref
    if matching:
        raise AssertionError('phase_482_commit_subject_present_but_no_qualifying_findings_memo_commit')
    raise AssertionError('phase_482_commit_not_present_in_local_history')


def test_integration_findings_memo_exists_and_contains_required_headings() -> None:
    assert MEMO_PATH.exists()
    text = MEMO_PATH.read_text(encoding='utf-8')
    for heading in REQUIRED_HEADINGS:
        assert heading in text, f'missing_heading:{heading}'


def test_required_deferred_item_tokens_and_regression_evidence_are_present() -> None:
    text = MEMO_PATH.read_text(encoding='utf-8')
    for token in REQUIRED_TOKENS:
        assert token in text, f'missing_token:{token}'
    for phase, count in ((476, 6), (477, 8), (478, 8), (479, 6), (480, 8), (481, 8)):
        assert f'Phase {phase}: `{count} passed`' in text
    assert 'Aggregate recorded result: `44 passed`' in text


def test_governance_priority_list_contains_at_least_three_items() -> None:
    text = MEMO_PATH.read_text(encoding='utf-8')
    section = text.split('## 4. Deferred items and governance-priority list', 1)[1].split(
        '## 5. Adversarial hardening relevance review', 1
    )[0]
    items = [line for line in section.splitlines() if line.startswith('- `')]
    assert len(items) >= 3
    assert any('CRITICAL' in item for item in items)
    assert any('MODERATE' in item for item in items)


def test_no_ilc_core_files_changed_at_phase_482_commit_snapshot() -> None:
    text = MEMO_PATH.read_text(encoding='utf-8')
    assert 'No ilc_core/ implementation occurs in Phase 482.' in text
    current_diff = subprocess.run(
        ['git', 'diff', '--name-only', 'HEAD~1', 'HEAD'],
        capture_output=True,
        check=True,
        text=True,
    ).stdout.splitlines()
    assert all(not path.startswith('ilc_core/') for path in current_diff if path)


def test_phase_482_main_commit_touches_expected_paths_only() -> None:
    commit_ref = _resolve_phase_482_commit_ref()
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS


def test_phase_482_main_commit_does_not_touch_ilc_core_or_decision_log() -> None:
    commit_ref = _resolve_phase_482_commit_ref()
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert 'docs/specs/ilc_constitutional_decision_log_v0.1.md' not in changed_paths
    assert all(not path.startswith('ilc_core/') for path in changed_paths)
