from __future__ import annotations

import csv
import json
import re
import subprocess
from pathlib import Path

from ilc_core.testing.ratification_mutation_scope_guardrail import (
    assert_head_commit_touched_no_runtime_files,
    parse_decision_register_rows,
)

EVIDENCE_PATH = Path('docs/specs/ilc_treasury_sim_t_recovery_rule_evidence_package_456_fix_2_v0.1.md')
SYNTHESIS_PATH = Path('docs/specs/ilc_treasury_sim_t_recovery_rule_comparative_synthesis_456_fix_2_v0.1.md')
REASSESSMENT_PATH = Path('docs/specs/ilc_cdl_050_blocker_1_reassessment_456_fix_2_v0.1.md')
TEST_PATH = Path('tests/test_phase_456_fix_2_recovery_rule_execution_and_blocker_1_reassessment.py')
WALKTHROUGH_PATH = Path('docs/phases/phase_456_fix_2_g8_recovery_rule_execution_walkthrough.md')
STATUS_PATH = Path('docs/phases/STATUS.md')
DECISION_LOG_PATH = Path('docs/specs/ilc_constitutional_decision_log_v0.1.md')
OUTPUT_ROOT = Path('out/treasury_sim/phase_456_fix_2')
MANIFEST_PATH = OUTPUT_ROOT / 'run_manifest.json'
RESULTS_CSV_PATH = OUTPUT_ROOT / 'scenario_5_results.csv'
RESULTS_TSV_PATH = OUTPUT_ROOT / 'scenario_5_results.tsv'
SUMMARY_PATH = OUTPUT_ROOT / 'summary_table.md'
PHASE_456_FIX_2_SUBJECT = 'docs(g8): phase 456 fix 2 recovery-rule execution comparative synthesis and blocker-1 reassessment'
FORBIDDEN_TREASURY_TOKEN = 'ILC_CDL_MUTATION_' + 'AUTHORIZED'
FIXED_REQUIRED_PATHS = {
    str(EVIDENCE_PATH),
    str(SYNTHESIS_PATH),
    str(REASSESSMENT_PATH),
    str(TEST_PATH),
    str(WALKTHROUGH_PATH),
    str(STATUS_PATH),
}
ALLOWED_OUTPUT_PREFIX = 'out/treasury_sim/phase_456_fix_2/'
REQUIRED_OUTPUT_FILES = {
    str(MANIFEST_PATH),
    str(RESULTS_CSV_PATH),
    str(RESULTS_TSV_PATH),
    str(SUMMARY_PATH),
}
REQUIRED_FILE_PATHS = (
    EVIDENCE_PATH,
    SYNTHESIS_PATH,
    REASSESSMENT_PATH,
    TEST_PATH,
    WALKTHROUGH_PATH,
    STATUS_PATH,
)


def _read(path: Path) -> str:
    return path.read_text(encoding='utf-8')


def _section_body(text: str, heading: str) -> str:
    escaped = re.escape(heading)
    match = re.search(rf'{escaped}\n\n(.*?)(?=\n## |\Z)', text, flags=re.S)
    if not match:
        raise AssertionError(f'section_not_found:{heading}')
    return match.group(1).strip()


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


def _qualifying_phase_456_fix_2_change_set(changed: set[str]) -> bool:
    if not FIXED_REQUIRED_PATHS.issubset(changed):
        return False
    output_paths = {path for path in changed if path.startswith(ALLOWED_OUTPUT_PREFIX)}
    if not output_paths:
        return False
    if not REQUIRED_OUTPUT_FILES.issubset(changed):
        return False
    return changed == FIXED_REQUIRED_PATHS | output_paths


def _resolve_phase_456_fix_2_commit_ref() -> str:
    result = subprocess.run(['git', 'log', '--format=%H%x09%s'], capture_output=True, check=True, text=True)
    matches: list[str] = []
    for line in result.stdout.splitlines():
        if '\t' not in line:
            continue
        commit_hash, subject = line.split('\t', 1)
        if subject.strip() == PHASE_456_FIX_2_SUBJECT:
            matches.append(commit_hash)

    for commit_ref in matches:
        changed = _changed_paths_for_commit(commit_ref)
        if _qualifying_phase_456_fix_2_change_set(changed):
            return commit_ref

    if matches:
        raise AssertionError(
            'phase_456_fix_2_commit_subject_present_but_no_qualifying_recovery_rule_execution_commit'
        )
    raise AssertionError('phase_456_fix_2_commit_not_present_in_local_history')


def test_evidence_package_exists_and_contains_required_headings() -> None:
    assert EVIDENCE_PATH.exists()
    text = _read(EVIDENCE_PATH)
    headings = (
        '## 1. Commission brief reference',
        '## 2. Scenario 5 candidate families executed',
        '## 3. Manifest and reproducibility record',
        '## 4. Raw output summary',
        '## 5. Observable measurements',
        '## 6. Intra-subfamily leaders',
        '## 7. Non-authorization statement',
    )
    for heading in headings:
        assert heading in text
        body = _section_body(text, heading)
        assert body
        assert len([line for line in body.splitlines() if line.strip()]) >= 2
    observables_body = _section_body(text, '## 5. Observable measurements')
    assert 'Subfamily A - epoch-window variants' in observables_body
    assert 'Subfamily B - clamp-floor variants' in observables_body


def test_evidence_package_contains_all_candidates_measurement_tokens_and_structured_outputs() -> None:
    text = _read(EVIDENCE_PATH)
    required_tokens = (
        'Scenario 5 only',
        'No Scenarios 1-4 were executed in Phase 456 Fix 2.',
        'Subfamily A - epoch-window variants',
        'Subfamily B - clamp-floor variants',
        'production_band_5_epoch',
        'production_band_6_epoch',
        'production_band_7_epoch',
        'production_band_8_epoch',
        'production_band_10_epoch',
        'production_band_5_epoch_with_clamp_floor_low',
        'production_band_5_epoch_with_clamp_floor_high',
        'organic ECU production rate',
        'P_e clamp-respect rate',
        'absolute percentage-point difference',
        'Raw outputs are reproducible from the manifests recorded in this artifact.',
        'No CDL-050 opening or ratification occurs in Phase 456 Fix 2.',
        'docs/specs/ilc_treasury_sim_t_recovery_rule_commission_brief_456_fix_1_v0.1.md',
    )
    for token in required_tokens:
        assert token in text

    assert OUTPUT_ROOT.exists()
    assert all(Path(path).exists() for path in REQUIRED_OUTPUT_FILES)
    manifest = json.loads(MANIFEST_PATH.read_text(encoding='utf-8'))
    assert manifest['phase'] == 456
    assert manifest['fix'] == 2
    assert manifest['outcome'] == 'Outcome A - Blocker 1 remains open'
    assert manifest['blocker_1_fix_2_verdict'] == 'remains_open'
    assert manifest['scenario_manifest']['row_count'] == 7
    with RESULTS_CSV_PATH.open('r', encoding='utf-8', newline='') as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 7
    assert {row['scenario_family'] for row in rows} == {'Scenario 5 - Recovery criterion exit validation'}
    assert {
        'candidate_id',
        'subfamily',
        'pe_clamp_respect_rate',
        'organic_ecu_production_rate',
        'intervention_duration_epochs',
        'intervention_cost_units',
    }.issubset(rows[0].keys())


def test_comparative_synthesis_exists_and_contains_required_headings() -> None:
    assert SYNTHESIS_PATH.exists()
    text = _read(SYNTHESIS_PATH)
    headings = (
        '## 1. Evidence base',
        '## 2. Subfamily A ranking',
        '## 3. Subfamily B ranking',
        '## 4. Cross-subfamily evaluation',
        '## 5. Outcome declaration',
        '## 6. Non-authorization statement',
    )
    for heading in headings:
        assert heading in text
        body = _section_body(text, heading)
        assert body
        assert len([line for line in body.splitlines() if line.strip()]) >= 2


def test_comparative_synthesis_contains_cross_subfamily_rule_tokens_and_explicit_outcome() -> None:
    text = _read(SYNTHESIS_PATH)
    required_tokens = (
        'Subfamily A - epoch-window variants',
        'Subfamily B - clamp-floor variants',
        'absolute percentage-point difference',
        'best remaining alternative in the full registered candidate set',
        'If exactly one subfamily produces a threshold-clearing leader, that leader is the Fix-2 recommendation without requiring cross-subfamily tie-break.',
        'Outcome A - Blocker 1 remains open',
        'Blocker 1 remains open.',
        'No CDL-050 opening or ratification occurs in Phase 456 Fix 2.',
    )
    for token in required_tokens:
        assert token in text


def test_blocker_1_reassessment_exists_contains_verdict_and_preserves_non_authorization_boundary() -> None:
    assert REASSESSMENT_PATH.exists()
    text = _read(REASSESSMENT_PATH)
    headings = (
        '## 1. Lead candidate',
        '## 2. Threshold evaluation',
        '## 3. Blocker-1 verdict',
        '## 4. Non-authorization statement',
    )
    for heading in headings:
        assert heading in text
        body = _section_body(text, heading)
        assert body
        assert len([line for line in body.splitlines() if line.strip()]) >= 2
    for token in (
        'Lead candidate identifier:',
        'organic ECU production rate',
        'P_e clamp-respect rate',
        'blocker_1_fix_2_verdict=',
        'blocker_1_fix_2_verdict=remains_open',
        'No CDL-050 opening or ratification occurs in Phase 456 Fix 2.',
    ):
        assert token in text


def test_all_deliverables_preserve_non_authorization_boundary_and_forbidden_token_absence() -> None:
    for path in REQUIRED_FILE_PATHS:
        assert FORBIDDEN_TREASURY_TOKEN not in _read(path)

    assert all(path.exists() for path in (MANIFEST_PATH, RESULTS_CSV_PATH, RESULTS_TSV_PATH, SUMMARY_PATH))
    walkthrough = _read(WALKTHROUGH_PATH)
    status = _read(STATUS_PATH)
    assert 'Actual result after the main commit:' in walkthrough
    assert 'CDL-050 remains unopened regardless of Blocker-1 verdict' in walkthrough
    assert '## Phase 456 (Fix 2)' in status
    assert 'blocker_1_fix_2_verdict=remains_open' in status


def test_phase_456_fix_2_main_commit_touches_expected_paths_only() -> None:
    commit_ref = _resolve_phase_456_fix_2_commit_ref()
    changed = _changed_paths_for_commit(commit_ref)
    assert _qualifying_phase_456_fix_2_change_set(changed)
    assert str(DECISION_LOG_PATH) not in changed
    assert_head_commit_touched_no_runtime_files(commit_ref=commit_ref)


def test_phase_456_fix_2_commit_does_not_open_cdl_050_and_preserves_cdl_051() -> None:
    commit_ref = _resolve_phase_456_fix_2_commit_ref()
    before_rows = parse_decision_register_rows(_read_file_at_ref(f'{commit_ref}^1', str(DECISION_LOG_PATH)))
    after_rows = parse_decision_register_rows(_read_file_at_ref(commit_ref, str(DECISION_LOG_PATH)))
    assert before_rows == after_rows
    assert before_rows['CDL-051']['status'] == 'ratified'
    assert 'CDL-050' not in before_rows
    assert 'CDL-050' not in after_rows
