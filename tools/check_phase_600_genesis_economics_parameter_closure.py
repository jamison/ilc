#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Sequence

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
SPEC_PATH = REPO_ROOT / 'docs/specs/ilc_deterministic_genesis_economics_evidence_and_parameter_closure_600_v0.1.md'
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


class Phase600CheckError(RuntimeError):
    def __init__(self, token: str, detail: str) -> None:
        super().__init__(detail)
        self.token = token


def _require(condition: bool, token: str, detail: str) -> None:
    if not condition:
        raise Phase600CheckError(token, detail)


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding='utf-8'))


def _resolve_evidence_artifact_path(*, manifest_path: Path, raw_path: Any, field: str) -> Path:
    _require(isinstance(raw_path, str) and raw_path, 'phase_600_input_contract_missing', f'evidence_root_missing:{field}')
    candidate = Path(raw_path)
    if candidate.is_absolute():
        resolved = candidate.resolve()
    else:
        resolved = (REPO_ROOT / candidate).resolve()
    manifest_dir = manifest_path.resolve().parent
    _require(
        resolved == manifest_dir or manifest_dir in resolved.parents,
        'phase_600_input_contract_missing',
        f'evidence_root_outside_manifest_dir:{field}:{resolved}',
    )
    _require(resolved.is_file(), 'phase_600_input_contract_missing', f'evidence_root_not_found:{field}:{resolved}')
    return resolved


def check_phase_600_parameter_closure(*, spec_path: Path, manifest_path: Path) -> dict[str, Any]:
    spec_text = spec_path.read_text(encoding='utf-8')
    for heading in REQUIRED_HEADINGS:
        _require(heading in spec_text, 'phase_600_input_contract_missing', f'missing_heading:{heading}')
    for token in REQUIRED_TOKENS:
        _require(token in spec_text, 'phase_600_provenance_alignment_missing', f'missing_token:{token}')

    manifest = _load_json(manifest_path)
    _require(manifest.get('success_marker') == 'phase_600_genesis_economics_parameter_closure_ok', 'phase_600_provenance_alignment_missing', 'success_marker_invalid')

    replay_contract = manifest.get('replay_contract', {})
    _require(replay_contract.get('status') == 'passed', 'phase_600_deterministic_replay_failed', 'replay_status_invalid')
    _require(bool(replay_contract.get('deterministic_hash')), 'phase_600_deterministic_replay_failed', 'deterministic_hash_missing')
    _require(bool(replay_contract.get('matrix_hash')), 'phase_600_deterministic_replay_failed', 'matrix_hash_missing')

    parameter_matrix = manifest.get('parameter_matrix', {})
    _require(parameter_matrix.get('authoritative_realization_surface') == 'fixed_tranche_against_cmax', 'phase_600_provenance_alignment_missing', 'authoritative_surface_invalid')
    _require(parameter_matrix.get('authoritative_governor_mode') == 'theoretical_cap', 'phase_600_provenance_alignment_missing', 'authoritative_mode_invalid')
    _require(parameter_matrix.get('supporting_sensitivity_mode') == 'issued_to_date', 'phase_600_provenance_alignment_missing', 'supporting_mode_invalid')
    _require(isinstance(parameter_matrix.get('subsidy_factors'), list) and parameter_matrix.get('subsidy_factors'), 'phase_600_parameter_matrix_incomplete', 'subsidy_factors_missing')
    _require(isinstance(parameter_matrix.get('multiplier_factors'), list) and parameter_matrix.get('multiplier_factors'), 'phase_600_parameter_matrix_incomplete', 'multiplier_factors_missing')

    evidence_roots = manifest.get('evidence_roots', {})
    authoritative_summary_path = _resolve_evidence_artifact_path(
        manifest_path=manifest_path,
        raw_path=evidence_roots.get('authoritative_summary_path'),
        field='authoritative_summary_path',
    )
    supporting_summary_path = _resolve_evidence_artifact_path(
        manifest_path=manifest_path,
        raw_path=evidence_roots.get('supporting_sensitivity_summary_path'),
        field='supporting_sensitivity_summary_path',
    )
    authoritative_summary = _load_json(authoritative_summary_path)
    supporting_summary = _load_json(supporting_summary_path)
    _require(
        authoritative_summary.get('governor_mode') == parameter_matrix.get('authoritative_governor_mode'),
        'phase_600_provenance_alignment_missing',
        'authoritative_summary_mode_invalid',
    )
    _require(
        authoritative_summary.get('realization_surface') == parameter_matrix.get('authoritative_realization_surface'),
        'phase_600_provenance_alignment_missing',
        'authoritative_summary_surface_invalid',
    )
    _require(
        supporting_summary.get('governor_mode') == parameter_matrix.get('supporting_sensitivity_mode'),
        'phase_600_provenance_alignment_missing',
        'supporting_summary_mode_invalid',
    )

    findings = manifest.get('findings', {})
    _require('full_tranche_realization_demonstrated_on_authoritative_surface' in findings, 'phase_600_provenance_alignment_missing', 'full_tranche_field_missing')
    _require('supporting_issued_to_date_reaches_within_horizon' in findings, 'phase_600_provenance_alignment_missing', 'issued_to_date_field_missing')
    _require(findings.get('future_controller_boundary_preserved') is True, 'phase_600_provenance_alignment_missing', 'future_controller_boundary_missing')
    authoritative_stats = authoritative_summary.get('summary', {})
    supporting_stats = supporting_summary.get('summary', {})
    _require(isinstance(authoritative_stats, dict), 'phase_600_provenance_alignment_missing', 'authoritative_summary_stats_missing')
    _require(isinstance(supporting_stats, dict), 'phase_600_provenance_alignment_missing', 'supporting_summary_stats_missing')
    _require(
        authoritative_stats.get('scenario_count') == authoritative_stats.get('full_tranche_realization_count'),
        'phase_600_provenance_alignment_missing',
        'authoritative_summary_full_tranche_count_mismatch',
    )
    _require(
        findings.get('full_tranche_realization_demonstrated_on_authoritative_surface')
        is (authoritative_stats.get('scenario_count', 0) == authoritative_stats.get('full_tranche_realization_count')),
        'phase_600_provenance_alignment_missing',
        'authoritative_summary_findings_mismatch',
    )
    _require(
        findings.get('supporting_issued_to_date_reaches_within_horizon')
        is (supporting_stats.get('scenario_count', 0) == supporting_stats.get('full_tranche_realization_count')),
        'phase_600_provenance_alignment_missing',
        'supporting_summary_findings_mismatch',
    )
    if 'authoritative_reach_target_epoch_p50' in findings:
        _require(
            findings.get('authoritative_reach_target_epoch_p50') == authoritative_stats.get('reach_target_epoch_p50'),
            'phase_600_provenance_alignment_missing',
            'authoritative_summary_p50_mismatch',
        )
    if 'supporting_issued_to_date_final_genesis_cumulative_ilc_p50' in findings:
        _require(
            findings.get('supporting_issued_to_date_final_genesis_cumulative_ilc_p50') == supporting_stats.get('final_genesis_cumulative_ilc_p50'),
            'phase_600_provenance_alignment_missing',
            'supporting_summary_p50_mismatch',
        )

    closure_decisions = manifest.get('closure_decisions', {})
    _require(isinstance(closure_decisions.get('status'), str) and closure_decisions.get('status'), 'phase_600_provenance_alignment_missing', 'closure_status_missing')
    for field in ('decisive_closures', 'evidence_supplemented_closures', 'explicit_defers'):
        _require(isinstance(closure_decisions.get(field), list), 'phase_600_provenance_alignment_missing', f'closure_field_missing:{field}')
    statement = closure_decisions.get('bounded_public_statement')
    _require(isinstance(statement, str) and statement, 'phase_600_unbounded_public_tokenomics_claim', 'bounded_public_statement_missing')
    lowered_statement = statement.lower()
    _require('may accumulate up to' not in lowered_statement, 'phase_600_unbounded_public_tokenomics_claim', 'downgraded_to_may_language')
    _require('direct mint' not in lowered_statement, 'phase_600_unbounded_public_tokenomics_claim', 'direct_mint_claim_present')
    if 'will' in lowered_statement:
        _require(findings.get('full_tranche_realization_demonstrated_on_authoritative_surface') is True, 'phase_600_unbounded_public_tokenomics_claim', 'will_claim_without_demonstration')

    required_failure_tokens = manifest.get('required_failure_tokens')
    _require(isinstance(required_failure_tokens, list), 'phase_600_provenance_alignment_missing', 'required_failure_tokens_missing')
    for token in REQUIRED_FAILURE_TOKENS:
        _require(token in required_failure_tokens, 'phase_600_provenance_alignment_missing', f'missing_failure_token:{token}')

    return {
        'marker': 'phase_600_genesis_economics_parameter_closure_ok',
        'manifest_path': str(manifest_path),
        'closure_status': closure_decisions.get('status'),
        'authoritative_mode': parameter_matrix.get('authoritative_governor_mode'),
        'authoritative_surface': parameter_matrix.get('authoritative_realization_surface'),
        'full_tranche_realization_demonstrated_on_authoritative_surface': findings.get('full_tranche_realization_demonstrated_on_authoritative_surface'),
        'emitted_failure_tokens': manifest.get('emitted_failure_tokens', []),
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='Check the Phase 600 deterministic Genesis economics closure manifest.')
    parser.add_argument('--manifest', required=True)
    parser.add_argument('--spec-path', default=str(SPEC_PATH))
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        payload = check_phase_600_parameter_closure(spec_path=Path(args.spec_path), manifest_path=Path(args.manifest))
    except (Phase600CheckError, OSError, json.JSONDecodeError, ValueError) as exc:
        token = exc.token if isinstance(exc, Phase600CheckError) else exc.__class__.__name__
        print(json.dumps({'marker': 'phase_600_genesis_economics_parameter_closure_failed', 'token': token, 'detail': str(exc)}, sort_keys=True, separators=(',', ':')), flush=True)
        return 1
    print(json.dumps(payload, sort_keys=True, separators=(',', ':')), flush=True)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
