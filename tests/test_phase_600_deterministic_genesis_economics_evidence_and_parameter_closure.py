from __future__ import annotations

import json
import subprocess
from pathlib import Path

from tools.check_phase_600_genesis_economics_parameter_closure import (
    Phase600CheckError,
    check_phase_600_parameter_closure,
)
from tools.run_phase_600_genesis_economics_parameter_closure import _mode_summary, run_phase_600

DOC_PATH = Path('docs/specs/ilc_deterministic_genesis_economics_evidence_and_parameter_closure_600_v0.1.md')
RUNNER_PATH = Path('tools/run_phase_600_genesis_economics_parameter_closure.py')
CHECKER_PATH = Path('tools/check_phase_600_genesis_economics_parameter_closure.py')
TEST_PATH = Path('tests/test_phase_600_deterministic_genesis_economics_evidence_and_parameter_closure.py')
WALKTHROUGH_PATH = Path('docs/phases/phase_600_g8_deterministic_genesis_economics_evidence_and_parameter_closure_walkthrough.md')
STATUS_PATH = Path('docs/phases/STATUS.md')
DECISION_LOG_PATH = Path('docs/specs/ilc_constitutional_decision_log_v0.1.md')
PHASE_600_SUBJECT_TOKEN = 'phase 600 genesis economics'
PHASE_600_BACKFILL_SUBJECT_TOKEN = 'phase 600 walkthrough and status backfill'
EXACT_REQUIRED_MAIN_PATHS = {
    str(DOC_PATH),
    str(RUNNER_PATH),
    str(CHECKER_PATH),
    str(TEST_PATH),
}
EXACT_REQUIRED_BACKFILL_PATHS = {
    str(WALKTHROUGH_PATH),
    str(STATUS_PATH),
}
REQUIRED_HEADINGS = (
    '## 1. Evidence closure target',
    '## 2. Dependency tiers and inherited canon',
    '## 3. Deterministic evidence matrix and replay contract',
    '## 4. Parameter-closure findings and authoritative outputs',
    '## 5. Closure decisions versus evidence-limited deferments',
    '## 6. Forbidden interpretations and exclusions',
    '## 7. Explicit deferrals to later phases',
)
REQUIRED_TOKENS = (
    'deterministic_genesis_economics_evidence_required_for_target_plus_cap_confirmation',
    'ratified_realization_surface_must_drive_phase_600_evidence_matrix',
    'full_genesis_5pct_tranche_realization_must_be_tested_against_reproducible_outputs',
    'subsidy_factor_and_multiplier_interactions_must_be_evidence_bounded',
    'genesis_fade_away_language_must_be_backed_by_reproducible_outputs',
    'phase_600_evidence_must_not_outrun_phase_599_reconciliation',
    'phase_600_evidence_outputs_must_be_machine_legible_and_replayable',
    'phase_600_must_not_reopen_phase_599_reconciliation',
    'future_genesis_ecu_realization_controller_if_any_must_remain_separate_from_natural_centrality_measurement',
    'phase_601_capability_proof_disposition_must_consume_phase_600_parameter_state',
)
REQUIRED_FAILURE_TOKENS = (
    'phase_600_input_contract_missing',
    'phase_600_deterministic_replay_failed',
    'phase_600_parameter_matrix_incomplete',
    'phase_600_provenance_alignment_missing',
    'phase_600_full_tranche_realization_not_demonstrated',
    'phase_600_unbounded_public_tokenomics_claim',
)
DEPENDENCY_ITEMS = (
    '`docs/specs/ilc_phase_596_605_sequence_lock_v0.1.md`',
    '`docs/specs/ilc_genesis_accrual_governor_provenance_reconciliation_599_v0.1.md`',
    '`docs/specs/ilc_phase_305_genesis_accumulation_canonicalization_checklist_v0.1.md`',
    '`docs/specs/ilc_genesis_accrual_governor_contract_v0.1.md`',
    '`docs/specs/ilc_genesis_accrual_reconciliation_8pct_vs_theta_hard_266_v0.1.md`',
    '`docs/specs/ilc_genesis_accumulation_dynamics_analysis_298_v0.3.md`',
    '`docs/specs/ilc_constitutional_decision_log_v0.1.md`',
)
SECTION_THREE_RULES = (
    'authoritative realization surface `fixed_tranche_against_cmax`',
    'authoritative governor mode `theoretical_cap`',
    'supporting sensitivity mode `issued_to_date`',
    'machine-legible manifest plus authoritative and supporting summary JSON files',
    'supporting sensitivity context only and not reopened closure candidates',
    'attached to reproducible outputs rather than prose alone',
)
SECTION_FOUR_RULES = (
    'full-tranche realization count on the authoritative surface: `4,374 / 4,374`',
    'supporting issued-to-date realization count within 480 epochs: `0 / 4,374`',
    '`phase_600_genesis_economics_parameter_closure_ok`',
    '`phase_600_parameter_matrix_incomplete`',
    'does not rewrite natural centrality measurement',
)
SECTION_FIVE_RULES = (
    'This phase closes decisively on evidence:',
    'This phase closes only as evidence-supplemented boundary language:',
    'This phase leaves as explicit defer because evidence is insufficient or the question exceeds this packet:',
    'No parameter question may remain unnamed after this phase',
    'failed closed into an explicit named follow-on obligation rather than softening the semantics by silence',
)
FORBIDDEN_RULES = (
    '- treating one simulation run as self-executing law without closure',
    '- using evidence outputs to override ratified CDL surfaces,',
    '- using analysis-only artifacts as substitute for deterministic evidence,',
    '- reopening accrual-governor or parameter reconciliation conclusions already',
    '- using evidence outputs to quietly restore issued-to-date ratio as the',
    '- treating a future Genesis-only ECU realization controller as already-ratified',
    '- claiming direct Genesis mint or an unratified controller as if it were already',
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


def _resolve_commit_ref(*, subject_token: str, expected_paths: set[str]) -> str:
    result = subprocess.run(
        ['git', 'log', '--format=%H%x09%s'],
        capture_output=True,
        check=True,
        text=True,
    )
    candidates: list[str] = []
    for line in result.stdout.splitlines():
        if '\t' not in line:
            continue
        commit_hash, subject = line.split('\t', 1)
        if subject_token not in subject.lower():
            continue
        candidates.append(commit_hash)
    for commit_ref in candidates:
        if _changed_paths_for_commit(commit_ref) == expected_paths:
            return commit_ref
    raise AssertionError(f'commit_not_present_in_local_history:{subject_token}')


def _synthetic_manifest(tmp_path: Path) -> Path:
    authoritative_summary_path = tmp_path / 'authoritative_summary.json'
    supporting_summary_path = tmp_path / 'supporting_summary.json'
    authoritative_summary_path.write_text(
        json.dumps(
            {
                'governor_mode': 'theoretical_cap',
                'realization_surface': 'fixed_tranche_against_cmax',
                'summary': {
                    'scenario_count': 4,
                    'full_tranche_realization_count': 4,
                    'reach_target_epoch_p50': 22,
                    'final_genesis_cumulative_ilc_p50': 1296000.0,
                },
            }
        ),
        encoding='utf-8',
    )
    supporting_summary_path.write_text(
        json.dumps(
            {
                'governor_mode': 'issued_to_date',
                'summary': {
                    'scenario_count': 4,
                    'full_tranche_realization_count': 0,
                    'reach_target_epoch_p50': None,
                    'final_genesis_cumulative_ilc_p50': 1241995.6909391996,
                },
            }
        ),
        encoding='utf-8',
    )
    manifest = {
        'phase': 600,
        'version': 'phase_600_genesis_economics_parameter_closure_v0.1',
        'success_marker': 'phase_600_genesis_economics_parameter_closure_ok',
        'required_failure_tokens': list(REQUIRED_FAILURE_TOKENS),
        'emitted_failure_tokens': ['phase_600_parameter_matrix_incomplete'],
        'parameter_matrix': {
            'authoritative_realization_surface': 'fixed_tranche_against_cmax',
            'authoritative_governor_mode': 'theoretical_cap',
            'supporting_sensitivity_mode': 'issued_to_date',
            'subsidy_factors': [0.2, 0.3, 0.4],
            'multiplier_factors': [1.0, 1.2],
        },
        'evidence_roots': {
            'authoritative_summary_path': str(authoritative_summary_path),
            'supporting_sensitivity_summary_path': str(supporting_summary_path),
        },
        'findings': {
            'full_tranche_realization_demonstrated_on_authoritative_surface': True,
            'authoritative_reach_target_epoch_p50': 22,
            'supporting_issued_to_date_reaches_within_horizon': False,
            'supporting_issued_to_date_final_genesis_cumulative_ilc_p50': 1241995.6909391996,
            'future_controller_boundary_preserved': True,
        },
        'closure_decisions': {
            'status': 'decisive_closure_with_evidence_limited_defers',
            'decisive_closures': ['full-tranche realization is demonstrated'],
            'evidence_supplemented_closures': ['timing remains bounded'],
            'explicit_defers': ['Phase 305 canonical output package remains incomplete'],
            'bounded_public_statement': 'Genesis has a fixed economic tranche equal to 5 percent of C_max.',
        },
        'replay_contract': {
            'status': 'passed',
            'deterministic_hash': 'abc',
            'matrix_hash': 'def',
        },
    }
    manifest_path = tmp_path / 'manifest.json'
    manifest_path.write_text(json.dumps(manifest), encoding='utf-8')
    return manifest_path


def test_document_exists_and_contains_required_section_headings() -> None:
    text = _read(DOC_PATH)
    for heading in REQUIRED_HEADINGS:
        assert heading in text


def test_all_required_governance_tokens_are_present() -> None:
    text = _read(DOC_PATH)
    for token in REQUIRED_TOKENS:
        assert token in text


def test_runner_exists_and_checker_exists() -> None:
    assert RUNNER_PATH.is_file()
    assert CHECKER_PATH.is_file()


def test_required_success_marker_and_failure_tokens_are_present_in_runner_and_checker_sources() -> None:
    runner_text = _read(RUNNER_PATH)
    checker_text = _read(CHECKER_PATH)
    assert 'phase_600_genesis_economics_parameter_closure_ok' in runner_text
    assert 'phase_600_genesis_economics_parameter_closure_ok' in checker_text
    for token in REQUIRED_FAILURE_TOKENS:
        assert token in runner_text or token in checker_text


def test_section_two_carries_the_mandatory_dependency_bundle() -> None:
    text = _read(DOC_PATH)
    for item in DEPENDENCY_ITEMS:
        assert item in text


def test_section_three_contains_the_deterministic_evidence_matrix_rules() -> None:
    text = _read(DOC_PATH)
    for item in SECTION_THREE_RULES:
        assert item in text


def test_section_four_contains_the_authoritative_output_and_finding_rules() -> None:
    text = _read(DOC_PATH)
    for item in SECTION_FOUR_RULES:
        assert item in text


def test_section_five_contains_closure_versus_defer_discipline() -> None:
    text = _read(DOC_PATH)
    for item in SECTION_FIVE_RULES:
        assert item in text


def test_section_six_contains_all_forbidden_interpretation_exclusions() -> None:
    text = _read(DOC_PATH)
    for item in FORBIDDEN_RULES:
        assert item in text


def test_checker_accepts_a_synthetic_valid_manifest(tmp_path: Path) -> None:
    manifest_path = _synthetic_manifest(tmp_path)
    payload = check_phase_600_parameter_closure(spec_path=DOC_PATH, manifest_path=manifest_path)
    assert payload['marker'] == 'phase_600_genesis_economics_parameter_closure_ok'


def test_checker_rejects_a_synthetic_manifest_missing_replay_contract(tmp_path: Path) -> None:
    manifest_path = _synthetic_manifest(tmp_path)
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    manifest.pop('replay_contract')
    manifest_path.write_text(json.dumps(manifest), encoding='utf-8')
    try:
        check_phase_600_parameter_closure(spec_path=DOC_PATH, manifest_path=manifest_path)
    except Phase600CheckError as exc:
        assert exc.token == 'phase_600_deterministic_replay_failed'
    else:
        raise AssertionError('expected_checker_failure_for_missing_replay_contract')


def test_checker_rejects_a_synthetic_manifest_missing_subsidy_factors(tmp_path: Path) -> None:
    manifest_path = _synthetic_manifest(tmp_path)
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    manifest['parameter_matrix'].pop('subsidy_factors')
    manifest_path.write_text(json.dumps(manifest), encoding='utf-8')
    try:
        check_phase_600_parameter_closure(spec_path=DOC_PATH, manifest_path=manifest_path)
    except Phase600CheckError as exc:
        assert exc.token == 'phase_600_parameter_matrix_incomplete'
    else:
        raise AssertionError('expected_checker_failure_for_missing_subsidy_factors')


def test_checker_rejects_a_synthetic_manifest_with_inconsistent_summary_or_escaped_paths(tmp_path: Path) -> None:
    manifest_path = _synthetic_manifest(tmp_path)
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    escaped_summary_path = tmp_path.parent / 'escaped_supporting_summary.json'
    escaped_summary_path.write_text('{}\n', encoding='utf-8')
    manifest['evidence_roots']['supporting_sensitivity_summary_path'] = str(escaped_summary_path)
    manifest_path.write_text(json.dumps(manifest), encoding='utf-8')
    try:
        check_phase_600_parameter_closure(spec_path=DOC_PATH, manifest_path=manifest_path)
    except Phase600CheckError as exc:
        assert exc.token == 'phase_600_input_contract_missing'
    else:
        raise AssertionError('expected_checker_failure_for_escaped_summary_path')

    manifest_path = _synthetic_manifest(tmp_path)
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    authoritative_summary_path = Path(manifest['evidence_roots']['authoritative_summary_path'])
    authoritative_summary = json.loads(authoritative_summary_path.read_text(encoding='utf-8'))
    authoritative_summary['summary']['full_tranche_realization_count'] = 3
    authoritative_summary_path.write_text(json.dumps(authoritative_summary), encoding='utf-8')
    try:
        check_phase_600_parameter_closure(spec_path=DOC_PATH, manifest_path=manifest_path)
    except Phase600CheckError as exc:
        assert exc.token == 'phase_600_provenance_alignment_missing'
    else:
        raise AssertionError('expected_checker_failure_for_inconsistent_summary')


def test_runner_promotes_closure_status_when_authoritative_full_tranche_is_demonstrated(tmp_path: Path) -> None:
    payload = run_phase_600(output_root=tmp_path)
    assert payload['closure_decisions']['status'] == 'decisive_closure_with_evidence_limited_defers'
    assert payload['findings']['full_tranche_realization_demonstrated_on_authoritative_surface'] is True
    assert 'rerun_hash' not in payload['replay_contract']


def test_mode_summary_uses_consistent_median_semantics_for_even_length_inputs() -> None:
    rows = [
        {'reach_target_epoch': 10, 'final_genesis_cumulative_ilc': 100.0, 'full_tranche_realized': True},
        {'reach_target_epoch': 20, 'final_genesis_cumulative_ilc': 200.0, 'full_tranche_realized': True},
        {'reach_target_epoch': 30, 'final_genesis_cumulative_ilc': 300.0, 'full_tranche_realized': True},
        {'reach_target_epoch': 40, 'final_genesis_cumulative_ilc': 400.0, 'full_tranche_realized': False},
    ]
    summary = _mode_summary(rows)
    assert summary['reach_target_epoch_p50'] == 25
    assert summary['final_genesis_cumulative_ilc_p50'] == 250.0


def test_main_commit_touches_exactly_the_required_paths() -> None:
    commit_ref = _resolve_commit_ref(subject_token=PHASE_600_SUBJECT_TOKEN, expected_paths=EXACT_REQUIRED_MAIN_PATHS)
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS


def test_main_commit_touches_no_adr_path_no_cdl_path_and_no_ilc_core_path() -> None:
    commit_ref = _resolve_commit_ref(subject_token=PHASE_600_SUBJECT_TOKEN, expected_paths=EXACT_REQUIRED_MAIN_PATHS)
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert not any(path.startswith('docs/adr/') for path in changed_paths)
    assert not any(path.startswith('docs/specs/ilc_cdl_') for path in changed_paths)
    assert not any(path.startswith('docs/specs/ilc_cdl-') for path in changed_paths)
    assert not any('/ilc_cdl_' in path for path in changed_paths)
    assert not any(path.startswith('ilc_core/') for path in changed_paths)


def test_backfill_commit_touches_exactly_walkthrough_and_status_and_no_forbidden_paths() -> None:
    commit_ref = _resolve_commit_ref(subject_token=PHASE_600_BACKFILL_SUBJECT_TOKEN, expected_paths=EXACT_REQUIRED_BACKFILL_PATHS)
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert changed_paths == EXACT_REQUIRED_BACKFILL_PATHS
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert not any(path.startswith('docs/adr/') for path in changed_paths)
    assert not any(path.startswith('docs/specs/ilc_cdl_') for path in changed_paths)
    assert not any(path.startswith('docs/specs/ilc_cdl-') for path in changed_paths)
    assert not any('/ilc_cdl_' in path for path in changed_paths)
    assert not any(path.startswith('ilc_core/') for path in changed_paths)
