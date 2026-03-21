from __future__ import annotations

import csv
import json
import subprocess
from pathlib import Path

from ilc_core.testing.ratification_mutation_scope_guardrail import (
    assert_head_commit_touched_no_runtime_files,
    parse_decision_register_rows,
)

EVIDENCE_PATH = Path('docs/specs/ilc_treasury_sim_t_evidence_package_454_v0.1.md')
TEST_PATH = Path('tests/test_phase_454_sim_t_evidence_package.py')
DECISION_LOG_PATH = Path('docs/specs/ilc_constitutional_decision_log_v0.1.md')
OUTPUT_ROOT = Path('out/treasury_sim/phase_454')
MANIFEST_PATH = OUTPUT_ROOT / 'run_manifest.json'
RESULTS_CSV_PATH = OUTPUT_ROOT / 'scenario_results.csv'
RESULTS_TSV_PATH = OUTPUT_ROOT / 'scenario_results.tsv'
SUMMARY_PATH = OUTPUT_ROOT / 'summary_table.md'
PHASE_453_BRIEF_PATH = 'docs/specs/ilc_treasury_sim_t_commission_brief_453_v0.1.md'
PHASE_454_SUBJECT = 'docs(g8): phase 454 sim-t execution i scenario runs and manifest capture'
FORBIDDEN_TREASURY_TOKEN = 'ILC_CDL_MUTATION_' + 'AUTHORIZED'
FIXED_REQUIRED_PATHS = {
    str(EVIDENCE_PATH),
    str(TEST_PATH),
}
ALLOWED_OUTPUT_PREFIX = 'out/treasury_sim/phase_454/'
REQUIRED_OUTPUT_FILES = {
    str(MANIFEST_PATH),
    str(RESULTS_CSV_PATH),
    str(RESULTS_TSV_PATH),
    str(SUMMARY_PATH),
}


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


def _read_file_at_ref(ref: str, path: str) -> str:
    result = subprocess.run(['git', 'show', f'{ref}:{path}'], capture_output=True, check=False, text=True)
    if result.returncode != 0:
        raise AssertionError(f'unable_to_read_file_at_ref:{ref}:{path}:{result.stderr.strip()}')
    return result.stdout


def _qualifying_phase_454_change_set(changed: set[str]) -> bool:
    if not FIXED_REQUIRED_PATHS.issubset(changed):
        return False
    output_paths = {path for path in changed if path.startswith(ALLOWED_OUTPUT_PREFIX)}
    if not output_paths:
        return False
    if not REQUIRED_OUTPUT_FILES.issubset(changed):
        return False
    return changed == FIXED_REQUIRED_PATHS | output_paths


def _resolve_phase_454_commit_ref() -> str:
    result = subprocess.run(['git', 'log', '--format=%H%x09%s'], capture_output=True, check=True, text=True)
    matches: list[str] = []
    for line in result.stdout.splitlines():
        if '\t' not in line:
            continue
        commit_hash, subject = line.split('\t', 1)
        if subject.strip() == PHASE_454_SUBJECT:
            matches.append(commit_hash)

    for commit_ref in matches:
        changed = _changed_paths_for_commit(commit_ref)
        if _qualifying_phase_454_change_set(changed):
            return commit_ref

    if matches:
        raise AssertionError('phase_454_commit_subject_present_but_no_qualifying_evidence_package_commit')
    raise AssertionError('phase_454_commit_not_present_in_local_history')


def test_evidence_package_exists_and_contains_required_headings() -> None:
    assert EVIDENCE_PATH.exists()
    text = _read(EVIDENCE_PATH)
    for heading in (
        '## 1. Commission brief reference',
        '## 2. Scenario families executed',
        '## 3. Manifest and reproducibility record',
        '## 4. Raw output summary',
        '## 5. Observable measurements',
        '## 6. Non-authorization statement',
    ):
        assert heading in text


def test_evidence_package_contains_required_tokens() -> None:
    text = _read(EVIDENCE_PATH)
    for token in (
        'All scenario families registered in the Phase 453 commission brief were executed.',
        'Raw outputs are reproducible from the manifests recorded in this artifact.',
        'No scenario families not registered in the Phase 453 commission brief were run.',
        'Catastrophic cross-layer observations, if present, are recorded as boundary evidence and do not expand CDL-050 normal operating scope.',
        'No CDL-050 opening or ratification occurs in Phase 454.',
    ):
        assert token in text


def test_evidence_package_references_phase_453_brief_and_outputs_are_structured() -> None:
    text = _read(EVIDENCE_PATH)
    assert PHASE_453_BRIEF_PATH in text
    assert OUTPUT_ROOT.exists()
    assert all(Path(path).exists() for path in REQUIRED_OUTPUT_FILES)

    manifest = json.loads(MANIFEST_PATH.read_text(encoding='utf-8'))
    assert manifest['phase'] == 454
    assert manifest['sim_id'] == 'SIM-T'
    assert len(manifest['scenario_manifests']) == 5

    with RESULTS_CSV_PATH.open('r', encoding='utf-8', newline='') as handle:
        rows = list(csv.DictReader(handle))
    assert rows
    assert {row['scenario_family'] for row in rows} == {
        'Scenario 1 - Escrow multiplier discrimination',
        'Scenario 2 - Vesting lock duration discrimination',
        'Scenario 3 - L1/L2 contagion isolation test',
        'Scenario 4 - Long-tail zero-issuance stress test',
        'Scenario 5 - Recovery criterion exit validation',
    }
    assert {
        'pe_clamp_respect_rate',
        'organic_ecu_production_rate',
        'productive_backlog_queue_clearance_behavior',
        'release_shock_amplitude_after_time_lock_expiry',
        'intervention_duration_epochs',
        'intervention_cost_units',
    }.issubset(rows[0].keys())


def test_no_forbidden_treasury_mutation_token_appears() -> None:
    for path in (EVIDENCE_PATH, TEST_PATH):
        assert FORBIDDEN_TREASURY_TOKEN not in _read(path)


def test_phase_454_commit_touches_expected_paths_only() -> None:
    commit_ref = _resolve_phase_454_commit_ref()
    changed = _changed_paths_for_commit(commit_ref)
    assert _qualifying_phase_454_change_set(changed)
    assert str(DECISION_LOG_PATH) not in changed
    assert_head_commit_touched_no_runtime_files(commit_ref=commit_ref)


def test_phase_454_commit_does_not_open_cdl_050() -> None:
    commit_ref = _resolve_phase_454_commit_ref()
    before_rows = parse_decision_register_rows(_read_file_at_ref(f'{commit_ref}^1', str(DECISION_LOG_PATH)))
    after_rows = parse_decision_register_rows(_read_file_at_ref(commit_ref, str(DECISION_LOG_PATH)))
    assert before_rows == after_rows
    assert before_rows['CDL-051']['status'] == 'ratified'
    assert 'CDL-050' not in before_rows
    assert 'CDL-050' not in after_rows
