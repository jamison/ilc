from __future__ import annotations

import hashlib
import os
import subprocess
from pathlib import Path

import pytest

from ilc_core.testing.ratification_mutation_scope_guardrail import (
    assert_head_commit_touched_no_runtime_files,
    parse_decision_register_rows,
)

DECISION_LOG_PATH = Path('docs/specs/ilc_constitutional_decision_log_v0.1.md')
GENESIS_PATH = Path('docs/specs/ilc_genesis_validator_architecture_scoping_468_v0.1.md')
OPENCLAW_PATH = Path('docs/specs/ilc_openclaw_architecture_scoping_468_v0.1.md')
HANDOFF_PATH = Path('docs/specs/ilc_window_460_468_handoff_468_v0.1.md')
CAPSULE_PATH = Path('docs/specs/ilc_antigravity_context_capsule_v2.1.md')
GATE_PATH = Path('tools/check_window_460_468_closure_gate_phase_468.sh')
TEST_PATH = Path('tests/test_window_460_468_closure_gate_468.py')
SNAPSHOT_PATH = Path('out/monitoring/infrastructure_risk_snapshot_phase_316.json')
PHASE_468_SUBJECT_TOKEN = 'phase 468 genesis validator and openclaw scoping and window 460-468 closure gate'
EXACT_REQUIRED_MAIN_PATHS = {
    str(GENESIS_PATH),
    str(OPENCLAW_PATH),
    str(HANDOFF_PATH),
    str(GATE_PATH),
    str(TEST_PATH),
}
FORBIDDEN_TREASURY_TOKEN = 'ILC_CDL_MUTATION_' + 'AUTHORIZED'
REQUIRED_GENESIS_HEADINGS = (
    '## 1. Minimum viable configuration',
    '## 2. CDL-051 consensus dependency',
    '## 3. Admission control pre-population',
    '## 4. Deferred implementation items',
)
REQUIRED_OPENCLAW_HEADINGS = (
    '## 1. CDL-052 graph operations surface',
    '## 2. CDL-033 extension requirements',
    '## 3. SDK-level contracts required',
    '## 4. Deferred implementation items',
)
REQUIRED_HANDOFF_HEADINGS = (
    '## 1. Window summary (460-468 completion state)',
    '## 2. Deliverable matrix for phases 460-467',
    '## 3. CDL-052 ratification summary',
    '## 4. Research and architecture tracks summary',
    '## 5. Next-window controls and non-authorizations',
    '## 6. Canonical anchors and next-window pointer',
)
REQUIRED_HANDOFF_TOKENS = (
    'Window 460-468 is closed.',
    'CDL-052 is ratified.',
    'CDL-050 is ratified.',
    'CDL-051 is ratified.',
    'Phase 469 is the next numbered phase.',
    'No decision-log mutation occurred in Phase 468 beyond window closure.',
    'No new ilc_core runtime feature implementation occurred in Phase 468.',
    'Phase 468 does not authorize Phase 469+ by itself; any move beyond Window 460-468 requires a new sequence lock or amendment.',
)
REQUIRED_CAPSULE_TOKENS = (
    'Supersedes: docs/specs/ilc_antigravity_context_capsule_v2.0.md',
    'This capsule is self-contained.',
    'CDL-052 is ratified. CDL-050 is ratified. CDL-051 is ratified.',
    'Phase 467 is the next authorized phase.',
)
EXPECTED_DRY_RUN_LINES = [
    '[1/6] prompt_contract_validation',
    'python3 tools/validate_phase_prompt.py docs/antigravity_tasks/antigravity_prompt__phase_468_g8_genesis_validator_openclaw_scoping_and_window_closure_gate.md',
    '[2/6] lane_contract_tests',
    'python3 -m pytest tests/test_phase_460_window_sequence_lock.py tests/test_phase_461_adr_0021_epistemic_finality_claims.py tests/test_phase_462_refutation_criterion_schema_specification.py tests/test_phase_463_minimal_staking_contract_specification.py tests/test_phase_464_cdl_052_opening.py tests/test_phase_465_cdl_052_prelock_hardening.py tests/test_phase_466_cdl_052_ratification.py tests/test_phase_467_tla_plus_cdl_051_shell_specification.py -q',
    '[3/6] cross_phase_regression',
    'python3 -m pytest tests/test_window_450_459_closure_gate_459.py -q',
    '[4/6] mutation_canary',
    'python3 tools/run_mutation_canary_phase_297.py',
    '[5/6] closure_gate_cli_contract',
    'python3 -m pytest tests/test_window_460_468_closure_gate_468.py -q',
    '[6/6] walkthrough_hygiene',
    'python3 -m pytest tests/test_no_ellipses_in_walkthroughs.py -q',
]


def _read(path: Path) -> str:
    return path.read_text(encoding='utf-8')


def _run_gate(args: list[str], env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(['bash', str(GATE_PATH)] + args, capture_output=True, text=True, env=env, check=False)


def _clean_gate_env() -> dict[str, str]:
    blocked = {'ILC_PHASE_468_GATE_SELFTEST', 'ILC_PHASE_459_GATE_SELFTEST', 'ILC_PHASE_468_SNAPSHOT_PATH'}
    return {key: value for key, value in os.environ.items() if key not in blocked}


def _changed_paths_for_commit(commit_ref: str) -> set[str]:
    result = subprocess.run(
        ['git', 'show', '--name-only', '--pretty=', commit_ref],
        capture_output=True,
        check=True,
        text=True,
    )
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


def _resolve_phase_468_commit_ref() -> str:
    result = subprocess.run(['git', 'log', '--format=%H%x09%s'], capture_output=True, check=True, text=True)
    matching: list[str] = []
    for line in result.stdout.splitlines():
        if '\t' not in line:
            continue
        commit_hash, subject = line.split('\t', 1)
        if PHASE_468_SUBJECT_TOKEN not in subject.lower():
            continue
        matching.append(commit_hash)
    for commit_ref in matching:
        if _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS:
            return commit_ref
    if matching:
        raise AssertionError('phase_468_commit_subject_present_but_no_qualifying_closure_commit')
    raise AssertionError('phase_468_commit_not_present_in_local_history')


def test_genesis_scoping_artifact_exists_and_contains_required_contract() -> None:
    text = _read(GENESIS_PATH)
    for heading in REQUIRED_GENESIS_HEADINGS:
        assert heading in text
    assert 'Genesis validator architecture scoping is complete as of Phase 468.' in text
    assert 'Genesis validator implementation is deferred beyond Window 460-468.' in text
    assert FORBIDDEN_TREASURY_TOKEN not in text


def test_openclaw_scoping_artifact_exists_and_contains_required_contract() -> None:
    text = _read(OPENCLAW_PATH)
    for heading in REQUIRED_OPENCLAW_HEADINGS:
        assert heading in text
    assert 'OpenClaw architecture scoping is complete as of Phase 468.' in text
    assert 'OpenClaw CDL-052 implementation is deferred beyond Window 460-468.' in text
    assert FORBIDDEN_TREASURY_TOKEN not in text


def test_handoff_artifact_exists_and_contains_required_headings_and_tokens() -> None:
    text = _read(HANDOFF_PATH)
    for heading in REQUIRED_HANDOFF_HEADINGS:
        assert heading in text
    for token in REQUIRED_HANDOFF_TOKENS:
        assert token in text


def test_capsule_v21_exists_and_current_decision_log_ratification_state_is_preserved() -> None:
    text = _read(CAPSULE_PATH)
    for token in REQUIRED_CAPSULE_TOKENS:
        assert token in text
    rows = parse_decision_register_rows(_read(DECISION_LOG_PATH))
    assert rows['CDL-052']['status'] == 'ratified'
    assert rows['CDL-050']['status'] == 'ratified'
    assert rows['CDL-051']['status'] == 'ratified'


def test_gate_script_exists_and_honors_cli_contract_with_exact_dry_run() -> None:
    assert GATE_PATH.exists()
    help_result = _run_gate(['--help'])
    assert help_result.returncode == 0
    assert 'Usage:' in help_result.stdout
    help_alias = _run_gate(['-h'])
    assert help_alias.returncode == 0
    assert 'Usage:' in help_alias.stdout
    dry_run = _run_gate(['--dry-run'])
    assert dry_run.returncode == 0
    lines = [line.strip() for line in dry_run.stdout.splitlines() if line.strip()]
    assert lines == EXPECTED_DRY_RUN_LINES
    unknown = _run_gate(['--unknown-arg'])
    assert unknown.returncode == 2


def test_gate_full_run_passes_and_preserves_snapshot_isolation() -> None:
    if os.environ.get('ILC_PHASE_468_GATE_SELFTEST') == '1':
        pytest.skip('phase_468_selftest_context_skip_full_gate')
    before = SNAPSHOT_PATH.read_bytes()
    before_mtime = SNAPSHOT_PATH.stat().st_mtime_ns
    before_sha = hashlib.sha256(before).hexdigest()
    result = _run_gate([], env=_clean_gate_env())
    assert result.returncode == 0
    assert 'phase_468_verdict=pass' in result.stdout
    assert SNAPSHOT_PATH.read_bytes() == before
    assert SNAPSHOT_PATH.stat().st_mtime_ns == before_mtime
    assert hashlib.sha256(SNAPSHOT_PATH.read_bytes()).hexdigest() == before_sha


def test_phase_468_main_commit_touches_exact_required_paths() -> None:
    if os.environ.get('ILC_PHASE_468_GATE_SELFTEST') == '1':
        pytest.skip('phase_468_selftest_context_skip_commit_guardrails')
    commit_ref = _resolve_phase_468_commit_ref()
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert changed_paths == EXACT_REQUIRED_MAIN_PATHS
    assert str(DECISION_LOG_PATH) not in changed_paths


def test_phase_468_commit_does_not_touch_ilc_core() -> None:
    if os.environ.get('ILC_PHASE_468_GATE_SELFTEST') == '1':
        pytest.skip('phase_468_selftest_context_skip_commit_guardrails')
    commit_ref = _resolve_phase_468_commit_ref()
    assert_head_commit_touched_no_runtime_files(commit_ref=commit_ref)
