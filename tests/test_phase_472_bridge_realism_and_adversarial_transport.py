from __future__ import annotations

import json
import subprocess
from pathlib import Path

ARTIFACT_PATH = Path('docs/specs/ilc_consensus_bridge_realism_exercise_472_v0.1.md')
TOOL_PATH = Path('tools/consensus_bridge_realism_exercise_472.py')
REPORT_PATH = Path('out/consensus_bridge/phase_472_report.json')
SUMMARY_PATH = Path('out/consensus_bridge/phase_472_summary.md')
DECISION_LOG_PATH = Path('docs/specs/ilc_constitutional_decision_log_v0.1.md')
TEST_PATH = Path('tests/test_phase_472_bridge_realism_and_adversarial_transport.py')
PHASE_472_SUBJECT_TOKEN = 'phase 472 bridge realism and adversarial transport exercise'
EXACT_REQUIRED_MAIN_PATHS = {
    str(TOOL_PATH),
    str(ARTIFACT_PATH),
    str(REPORT_PATH),
    str(SUMMARY_PATH),
    str(TEST_PATH),
}
EXPECTED_CASES = {'nominal_forwarding', 'reordered_delivery', 'duplicate_delivery', 'partial_bridge_loss'}
FORBIDDEN_TREASURY_TOKEN = 'ILC_CDL_MUTATION_' + 'AUTHORIZED'


def _read(path: Path) -> str:
    return path.read_text(encoding='utf-8')


def _changed_paths_for_commit(commit_ref: str) -> set[str]:
    result = subprocess.run(['git', 'show', '--name-only', '--pretty=', commit_ref], capture_output=True, check=True, text=True)
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


def _resolve_phase_472_commit_ref() -> str:
    result = subprocess.run(['git', 'log', '--format=%H%x09%s'], capture_output=True, check=True, text=True)
    matching: list[str] = []
    for line in result.stdout.splitlines():
        if '\t' not in line:
            continue
        commit_hash, subject = line.split('\t', 1)
        if PHASE_472_SUBJECT_TOKEN not in subject.lower():
            continue
        matching.append(commit_hash)
    for commit_ref in matching:
        if _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS:
            return commit_ref
    if matching:
        raise AssertionError('phase_472_commit_subject_present_but_no_qualifying_bridge_commit')
    raise AssertionError('phase_472_commit_not_present_in_local_history')


def test_exercise_artifact_headings_and_tokens() -> None:
    text = _read(ARTIFACT_PATH)
    for heading in (
        '## 1. Exercise scope',
        '## 2. Simulated transport adversity matrix',
        '## 3. Report contract',
        '## 4. Explicit non-goals',
    ):
        assert heading in text
    for token in (
        'Bridge-realism and adversarial transport exercise is complete as of Phase 472.',
        'No native P2P transport implementation occurs in Phase 472.',
        'No decision-log mutation occurred in Phase 472.',
        'Phase 473 is the next authorized phase.',
    ):
        assert token in text


def test_tool_exists_and_is_runnable() -> None:
    assert TOOL_PATH.exists()
    result = subprocess.run(['python3', str(TOOL_PATH)], capture_output=True, text=True, check=False)
    assert result.returncode == 0


def test_report_json_exists_with_all_required_cases() -> None:
    report = json.loads(_read(REPORT_PATH))
    assert {entry['case_name'] for entry in report['cases']} == EXPECTED_CASES


def test_summary_markdown_exists_with_all_case_names() -> None:
    text = _read(SUMMARY_PATH)
    for case_name in EXPECTED_CASES:
        assert case_name in text


def test_report_records_deterministic_verdict_fields() -> None:
    report = json.loads(_read(REPORT_PATH))
    for case in report['cases']:
        assert 'legacy_status' in case
        assert 'diversity_status' in case
        assert 'determinism_preserved' in case


def test_no_forbidden_treasury_mutation_token_appears() -> None:
    assert FORBIDDEN_TREASURY_TOKEN not in _read(ARTIFACT_PATH)
    assert FORBIDDEN_TREASURY_TOKEN not in _read(TEST_PATH)


def test_phase_472_main_commit_touches_expected_paths() -> None:
    commit_ref = _resolve_phase_472_commit_ref()
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS


def test_phase_472_commit_does_not_touch_decision_log_or_ilc_core() -> None:
    commit_ref = _resolve_phase_472_commit_ref()
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert not any(path.startswith('ilc_core/') for path in changed_paths)
