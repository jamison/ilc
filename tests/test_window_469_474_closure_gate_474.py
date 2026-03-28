from __future__ import annotations

import hashlib
import os
import subprocess
from pathlib import Path

import pytest

from ilc_core.testing.ratification_mutation_scope_guardrail import parse_decision_register_rows

HANDOFF_PATH = Path('docs/specs/ilc_window_469_474_handoff_474_v0.1.md')
GATE_PATH = Path('tools/check_window_469_474_closure_gate_phase_474.sh')
DECISION_LOG_PATH = Path('docs/specs/ilc_constitutional_decision_log_v0.1.md')
SNAPSHOT_PATH = Path('out/monitoring/infrastructure_risk_snapshot_phase_316.json')
MEASUREMENT_REPORT_PATH = Path('out/consensus_measurement/phase_471_report.json')
MEASUREMENT_SUMMARY_PATH = Path('out/consensus_measurement/phase_471_summary.md')
BRIDGE_REPORT_PATH = Path('out/consensus_bridge/phase_472_report.json')
BRIDGE_SUMMARY_PATH = Path('out/consensus_bridge/phase_472_summary.md')
TEST_PATH = Path('tests/test_window_469_474_closure_gate_474.py')
PHASE_474_SUBJECT_TOKEN = 'phase 474 window 469-474 closure gate and handoff'
EXACT_REQUIRED_MAIN_PATHS = {
    str(HANDOFF_PATH),
    str(GATE_PATH),
    str(TEST_PATH),
}
EXPECTED_DRY_RUN_LINES = [
    '[1/6] prompt_contract_validation',
    'python3 tools/validate_phase_prompt.py docs/antigravity_tasks/antigravity_prompt__phase_474_g8_window_469_474_closure_gate_and_handoff.md',
    '[2/6] lane_contract_tests',
    'python3 -m pytest tests/test_phase_469_window_sequence_lock.py tests/test_phase_470_consensus_diversity_floor_finality_runtime.py tests/test_phase_471_distributed_degraded_measurement_harness.py tests/test_phase_472_bridge_realism_and_adversarial_transport.py tests/test_phase_473_consensus_adversarial_hardening_and_findings.py -q',
    '[3/6] cross_phase_regression',
    'python3 -m pytest tests/test_window_460_468_closure_gate_468.py -q',
    '[4/6] mutation_canary',
    'python3 tools/run_mutation_canary_phase_297.py',
    '[5/6] closure_gate_cli_contract',
    'python3 -m pytest tests/test_window_469_474_closure_gate_474.py -q',
    '[6/6] walkthrough_hygiene',
    'python3 -m pytest tests/test_no_ellipses_in_walkthroughs.py -q',
]


def _read(path: Path) -> str:
    return path.read_text(encoding='utf-8')


def _run_gate(args: list[str], env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(['bash', str(GATE_PATH)] + args, capture_output=True, text=True, env=env, check=False)


def _fingerprint(path: Path) -> tuple[str, int]:
    raw = path.read_bytes()
    return hashlib.sha256(raw).hexdigest(), path.stat().st_mtime_ns


def _clean_gate_env() -> dict[str, str]:
    blocked = {'ILC_PHASE_474_GATE_SELFTEST', 'ILC_PHASE_468_GATE_SELFTEST', 'ILC_PHASE_474_SNAPSHOT_PATH'}
    return {key: value for key, value in os.environ.items() if key not in blocked}


def _changed_paths_for_commit(commit_ref: str) -> set[str]:
    result = subprocess.run(['git', 'show', '--name-only', '--pretty=', commit_ref], capture_output=True, check=True, text=True)
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


def _resolve_phase_474_commit_ref() -> str:
    result = subprocess.run(['git', 'log', '--format=%H%x09%s'], capture_output=True, check=True, text=True)
    matching: list[str] = []
    for line in result.stdout.splitlines():
        if '\t' not in line:
            continue
        commit_hash, subject = line.split('\t', 1)
        if PHASE_474_SUBJECT_TOKEN not in subject.lower():
            continue
        matching.append(commit_hash)
    for commit_ref in matching:
        if _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS:
            return commit_ref
    if matching:
        raise AssertionError('phase_474_commit_subject_present_but_no_qualifying_closure_commit')
    raise AssertionError('phase_474_commit_not_present_in_local_history')


def test_gate_script_exists_and_passes_dry_run() -> None:
    assert GATE_PATH.exists()
    dry_run = _run_gate(['--dry-run'])
    assert dry_run.returncode == 0
    assert [line.strip() for line in dry_run.stdout.splitlines() if line.strip()] == EXPECTED_DRY_RUN_LINES


def test_gate_help_and_unknown_arg_contract() -> None:
    assert _run_gate(['--help']).returncode == 0
    assert _run_gate(['-h']).returncode == 0
    assert _run_gate(['--unknown-arg']).returncode == 2


def test_full_gate_run_passes_and_preserves_snapshot_isolation() -> None:
    if os.environ.get('ILC_PHASE_474_GATE_SELFTEST') == '1':
        pytest.skip('phase_474_selftest_context_skip_full_gate')
    before = SNAPSHOT_PATH.read_bytes()
    before_mtime = SNAPSHOT_PATH.stat().st_mtime_ns
    before_sha = hashlib.sha256(before).hexdigest()
    tracked_output_fingerprints = {
        path: _fingerprint(path)
        for path in (
            MEASUREMENT_REPORT_PATH,
            MEASUREMENT_SUMMARY_PATH,
            BRIDGE_REPORT_PATH,
            BRIDGE_SUMMARY_PATH,
        )
    }
    result = _run_gate([], env=_clean_gate_env())
    assert result.returncode == 0
    assert 'phase_474_verdict=pass' in result.stdout
    assert SNAPSHOT_PATH.read_bytes() == before
    assert SNAPSHOT_PATH.stat().st_mtime_ns == before_mtime
    assert hashlib.sha256(SNAPSHOT_PATH.read_bytes()).hexdigest() == before_sha
    for path, fingerprint in tracked_output_fingerprints.items():
        assert _fingerprint(path) == fingerprint


def test_handoff_artifact_exists_with_required_headings_and_tokens() -> None:
    text = _read(HANDOFF_PATH)
    for heading in (
        '## 1. Window summary (469-474 completion state)',
        '## 2. Deliverable matrix for phases 469-473',
        '## 3. Diversity-floor runtime summary',
        '## 4. Measurement and bridge summary',
        '## 5. Next-window controls and non-authorizations',
        '## 6. Canonical anchors and next-window pointer',
    ):
        assert heading in text
    for token in (
        'Window 469-474 is closed.',
        'CDL-050 is ratified.',
        'CDL-051 is ratified.',
        'CDL-052 is ratified.',
        'No decision-log mutation occurred in Window 469-474.',
        'No new CDL row was opened in Window 469-474.',
        'Phase 475 is the next numbered phase.',
        'Phase 474 does not authorize Phase 475+ by itself; any move beyond Window 469-474 requires a new sequence lock or amendment.',
    ):
        assert token in text


def test_live_decision_log_preserves_cdl_050_cdl_051_cdl_052_ratified() -> None:
    rows = parse_decision_register_rows(_read(DECISION_LOG_PATH))
    assert rows['CDL-050']['status'] == 'ratified'
    assert rows['CDL-051']['status'] == 'ratified'
    assert rows['CDL-052']['status'] == 'ratified'


def test_dry_run_output_is_exact_12_line_block() -> None:
    dry_run = _run_gate(['--dry-run'])
    lines = [line.strip() for line in dry_run.stdout.splitlines() if line.strip()]
    assert len(lines) == 12
    assert lines == EXPECTED_DRY_RUN_LINES


def test_phase_474_main_commit_touches_expected_paths() -> None:
    if os.environ.get('ILC_PHASE_474_GATE_SELFTEST') == '1':
        pytest.skip('phase_474_selftest_context_skip_commit_resolution')
    commit_ref = _resolve_phase_474_commit_ref()
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS


def test_phase_474_commit_does_not_touch_decision_log_or_ilc_core() -> None:
    if os.environ.get('ILC_PHASE_474_GATE_SELFTEST') == '1':
        pytest.skip('phase_474_selftest_context_skip_commit_resolution')
    commit_ref = _resolve_phase_474_commit_ref()
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert not any(path.startswith('ilc_core/') for path in changed_paths)
