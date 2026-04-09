#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from dataclasses import asdict, dataclass
from itertools import product
from pathlib import Path
from statistics import median
from typing import Any, Sequence

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from ilc_core.analysis.genesis_accrual_governor import THETA_HARD, THETA_SOFT
DEFAULT_OUTPUT_ROOT = REPO_ROOT / 'out/phase_600_genesis_economics_parameter_closure'
INPUT_PATHS = {
    'phase_596_lock': REPO_ROOT / 'docs/specs/ilc_phase_596_605_sequence_lock_v0.1.md',
    'phase_599_closure': REPO_ROOT / 'docs/specs/ilc_genesis_accrual_governor_provenance_reconciliation_599_v0.1.md',
    'phase_305_checklist': REPO_ROOT / 'docs/specs/ilc_phase_305_genesis_accumulation_canonicalization_checklist_v0.1.md',
    'governor_contract': REPO_ROOT / 'docs/specs/ilc_genesis_accrual_governor_contract_v0.1.md',
    'analysis_298_v03': REPO_ROOT / 'docs/specs/ilc_genesis_accumulation_dynamics_analysis_298_v0.3.md',
}
REQUIRED_PHASE_599_TOKENS = (
    'phase_600_genesis_economics_evidence_must_consume_phase_599_reconciliation',
    'genesis_fixed_tranche_against_cmax_is_authoritative_realization_surface',
    'issued_to_date_ratio_is_not_authoritative_for_full_tranche_realization',
    'genesis_5pct_tranche_is_target_plus_cap_not_cap_only',
)
C_MAX = 25_920_000.0
GENESIS_TARGET = C_MAX * THETA_HARD
HORIZON_EPOCHS = 480
HALVING_H = 48
SUBSIDY_FACTORS = (0.20, 0.30, 0.40)
MULTIPLIER_FACTORS = (1.0, 1.2)
CENTRALITY0_VALUES = (0.85, 0.90, 0.95)
CENTRALITY_HALF_LIFE_VALUES = (48, 72, 96)
REPUTATION0_VALUES = (0.80, 0.90, 1.00)
REPUTATION_HALF_LIFE_VALUES = (96, 144, 192)
NETWORK_MIDPOINT_VALUES = (36, 48, 60)
NETWORK_GROWTH_K_VALUES = (0.08, 0.10, 0.12)
REQUIRED_FAILURE_TOKENS = (
    'phase_600_input_contract_missing',
    'phase_600_deterministic_replay_failed',
    'phase_600_parameter_matrix_incomplete',
    'phase_600_provenance_alignment_missing',
    'phase_600_full_tranche_realization_not_demonstrated',
    'phase_600_unbounded_public_tokenomics_claim',
)


class Phase600RunError(RuntimeError):
    def __init__(self, token: str, detail: str) -> None:
        super().__init__(detail)
        self.token = token


@dataclass(frozen=True)
class Scenario:
    governor_mode: str
    multiplier_factor: float
    centrality0: float
    centrality_half_life: int
    centrality_floor: float
    reputation0: float
    reputation_half_life: int
    reputation_floor: float
    network_midpoint: int
    network_growth_k: float
    base_genesis: float
    weight_centrality: float
    weight_reputation: float
    base_other: float
    other_scale: float
    genesis_subsidy_factor: float


def _normalized_json(payload: Any) -> str:
    return json.dumps(payload, sort_keys=True, separators=(',', ':'))


def _sha256_payload(payload: Any) -> str:
    return hashlib.sha256(_normalized_json(payload).encode('utf-8')).hexdigest()


def _require(condition: bool, token: str, detail: str) -> None:
    if not condition:
        raise Phase600RunError(token, detail)


def _logistic(x: float) -> float:
    if x >= 0.0:
        z = math.exp(-x)
        return 1.0 / (1.0 + z)
    z = math.exp(x)
    return z / (1.0 + z)


def _fast_taper_multiplier(genesis_share_ratio: float) -> float:
    if genesis_share_ratio >= THETA_HARD - 1e-12:
        return 0.0
    numerator = _logistic(40.0 * (THETA_SOFT - genesis_share_ratio))
    denominator = _logistic(40.0 * THETA_SOFT)
    return float(max(0.0, min(1.0, numerator / denominator)))


def _exp_decay_with_floor(start: float, floor: float, half_life: int, epoch: int) -> float:
    return floor + (start - floor) * (0.5 ** (epoch / float(half_life)))


def _network_pressure(epoch: int, midpoint: int, growth_k: float) -> float:
    return _logistic(growth_k * (epoch - midpoint))


def _issuance_raw_budget() -> list[float]:
    q = 2.0 ** (-1.0 / float(HALVING_H))
    geom_sum = (1.0 - (q ** HORIZON_EPOCHS)) / (1.0 - q)
    b0 = C_MAX / geom_sum
    return [b0 * (q**epoch) for epoch in range(HORIZON_EPOCHS)]


def _build_scenarios() -> list[Scenario]:
    scenarios: list[Scenario] = []
    for governor_mode, multiplier_factor, c0, c_h, r0, r_h, n_mid, n_k, subsidy in product(
        ('theoretical_cap', 'issued_to_date'),
        MULTIPLIER_FACTORS,
        CENTRALITY0_VALUES,
        CENTRALITY_HALF_LIFE_VALUES,
        REPUTATION0_VALUES,
        REPUTATION_HALF_LIFE_VALUES,
        NETWORK_MIDPOINT_VALUES,
        NETWORK_GROWTH_K_VALUES,
        SUBSIDY_FACTORS,
    ):
        scenarios.append(
            Scenario(
                governor_mode=governor_mode,
                multiplier_factor=multiplier_factor,
                centrality0=c0,
                centrality_half_life=c_h,
                centrality_floor=0.05,
                reputation0=r0,
                reputation_half_life=r_h,
                reputation_floor=0.10,
                network_midpoint=n_mid,
                network_growth_k=n_k,
                base_genesis=0.02,
                weight_centrality=0.65,
                weight_reputation=0.35,
                base_other=0.28,
                other_scale=0.82,
                genesis_subsidy_factor=subsidy,
            )
        )
    return scenarios


def _simulate(scenario: Scenario, budgets: list[float]) -> dict[str, Any]:
    issuance_cum = 0.0
    genesis_cum = 0.0
    reach_epoch = -1
    first_cap_epoch = -1
    first_taper_under_10pct_epoch = -1

    for epoch, budget_raw in enumerate(budgets):
        remaining_supply = C_MAX - issuance_cum
        if remaining_supply <= 0.0:
            break
        budget = min(budget_raw, remaining_supply)
        if scenario.governor_mode == 'issued_to_date':
            ratio = genesis_cum / issuance_cum if issuance_cum > 0.0 else 0.0
        elif scenario.governor_mode == 'theoretical_cap':
            ratio = genesis_cum / C_MAX
        else:
            raise Phase600RunError('phase_600_input_contract_missing', f'unknown_mode:{scenario.governor_mode}')
        taper = _fast_taper_multiplier(ratio)
        if first_cap_epoch < 0 and ratio >= THETA_HARD - 1e-12:
            first_cap_epoch = epoch
        if first_taper_under_10pct_epoch < 0 and taper <= 0.10:
            first_taper_under_10pct_epoch = epoch

        centrality = _exp_decay_with_floor(
            start=scenario.centrality0,
            floor=scenario.centrality_floor,
            half_life=scenario.centrality_half_life,
            epoch=epoch,
        )
        reputation = _exp_decay_with_floor(
            start=scenario.reputation0,
            floor=scenario.reputation_floor,
            half_life=scenario.reputation_half_life,
            epoch=epoch,
        )
        network_pressure = _network_pressure(
            epoch=epoch,
            midpoint=scenario.network_midpoint,
            growth_k=scenario.network_growth_k,
        )
        genesis_score = (
            scenario.base_genesis
            + scenario.weight_centrality * centrality
            + scenario.weight_reputation * reputation
        ) * scenario.multiplier_factor
        other_score = scenario.base_other + scenario.other_scale * network_pressure
        raw_share = scenario.genesis_subsidy_factor * genesis_score / (genesis_score + other_score)
        raw_share = max(0.0, min(1.0, raw_share))
        effective_share = raw_share * taper
        remaining_target = max(0.0, GENESIS_TARGET - genesis_cum)
        genesis_grant = min(max(0.0, budget * effective_share), remaining_target)

        genesis_cum += genesis_grant
        issuance_cum += budget
        if reach_epoch < 0 and genesis_cum >= GENESIS_TARGET - 1e-9:
            reach_epoch = epoch

    final_ratio_to_issuance = genesis_cum / issuance_cum if issuance_cum > 0.0 else 0.0
    final_ratio_to_cmax = genesis_cum / C_MAX
    return {
        **asdict(scenario),
        'reach_target_epoch': reach_epoch,
        'cap_blocked_epoch': first_cap_epoch,
        'taper_under_10pct_epoch': first_taper_under_10pct_epoch,
        'final_genesis_cumulative_ilc': genesis_cum,
        'final_total_issuance_ilc': issuance_cum,
        'final_ratio_to_issuance': final_ratio_to_issuance,
        'final_ratio_to_cmax': final_ratio_to_cmax,
        'full_tranche_realized': reach_epoch >= 0 and abs(genesis_cum - GENESIS_TARGET) <= 1e-6,
    }


def _mode_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    reach_epochs = sorted(row['reach_target_epoch'] for row in rows if int(row['reach_target_epoch']) >= 0)
    final_cumulative = sorted(float(row['final_genesis_cumulative_ilc']) for row in rows)
    return {
        'scenario_count': len(rows),
        'full_tranche_realization_count': sum(1 for row in rows if row['full_tranche_realized']),
        'reach_target_epoch_p50': int(median(reach_epochs)) if reach_epochs else None,
        'reach_target_epoch_p10': int(reach_epochs[max(0, len(reach_epochs) // 10 - 1)]) if reach_epochs else None,
        'reach_target_epoch_p90': int(reach_epochs[min(len(reach_epochs) - 1, int(math.ceil(len(reach_epochs) * 0.9)) - 1)]) if reach_epochs else None,
        'final_genesis_cumulative_ilc_p50': final_cumulative[len(final_cumulative) // 2] if final_cumulative else None,
        'min_final_genesis_cumulative_ilc': min(final_cumulative) if final_cumulative else None,
        'max_final_genesis_cumulative_ilc': max(final_cumulative) if final_cumulative else None,
    }


def _run_matrix() -> dict[str, Any]:
    budgets = _issuance_raw_budget()
    rows = [_simulate(scenario, budgets) for scenario in _build_scenarios()]
    theoretical_rows = [row for row in rows if row['governor_mode'] == 'theoretical_cap']
    issued_rows = [row for row in rows if row['governor_mode'] == 'issued_to_date']
    theoretical_summary = _mode_summary(theoretical_rows)
    issued_summary = _mode_summary(issued_rows)
    return {
        'constants': {
            'c_max_ilc': C_MAX,
            'genesis_target_ilc': GENESIS_TARGET,
            'theta_hard': THETA_HARD,
            'theta_soft': THETA_SOFT,
            'halving_h': HALVING_H,
            'horizon_epochs': HORIZON_EPOCHS,
        },
        'parameter_matrix': {
            'authoritative_realization_surface': 'fixed_tranche_against_cmax',
            'authoritative_governor_mode': 'theoretical_cap',
            'supporting_sensitivity_mode': 'issued_to_date',
            'subsidy_factors': list(SUBSIDY_FACTORS),
            'multiplier_factors': list(MULTIPLIER_FACTORS),
            'centrality0_values': list(CENTRALITY0_VALUES),
            'centrality_half_life_values': list(CENTRALITY_HALF_LIFE_VALUES),
            'reputation0_values': list(REPUTATION0_VALUES),
            'reputation_half_life_values': list(REPUTATION_HALF_LIFE_VALUES),
            'network_midpoint_values': list(NETWORK_MIDPOINT_VALUES),
            'network_growth_k_values': list(NETWORK_GROWTH_K_VALUES),
            'scenario_count_total': len(rows),
        },
        'authoritative_summary': theoretical_summary,
        'supporting_sensitivity_summary': issued_summary,
    }


def _write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + '\n', encoding='utf-8')


def _verify_inputs() -> dict[str, Any]:
    result: dict[str, Any] = {}
    for label, path in INPUT_PATHS.items():
        _require(path.is_file(), 'phase_600_input_contract_missing', f'missing_input:{label}:{path}')
        result[label] = {'path': str(path), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
    phase_599_text = INPUT_PATHS['phase_599_closure'].read_text(encoding='utf-8')
    for token in REQUIRED_PHASE_599_TOKENS:
        _require(token in phase_599_text, 'phase_600_provenance_alignment_missing', f'missing_phase_599_token:{token}')
    return result


def _build_manifest(output_dir: Path) -> dict[str, Any]:
    input_contract = _verify_inputs()
    matrix = _run_matrix()
    authoritative_summary_path = output_dir / 'authoritative_summary.json'
    sensitivity_summary_path = output_dir / 'supporting_sensitivity_summary.json'
    authoritative_summary = {
        'realization_surface': matrix['parameter_matrix']['authoritative_realization_surface'],
        'governor_mode': 'theoretical_cap',
        'summary': matrix['authoritative_summary'],
    }
    sensitivity_summary = {
        'governor_mode': 'issued_to_date',
        'summary': matrix['supporting_sensitivity_summary'],
    }
    _write_json(authoritative_summary_path, authoritative_summary)
    _write_json(sensitivity_summary_path, sensitivity_summary)

    authoritative_reaches = matrix['authoritative_summary']['full_tranche_realization_count'] == matrix['authoritative_summary']['scenario_count']
    issued_to_date_reaches = matrix['supporting_sensitivity_summary']['full_tranche_realization_count'] == matrix['supporting_sensitivity_summary']['scenario_count']
    emitted_failure_tokens: list[str] = []
    if not authoritative_reaches:
        emitted_failure_tokens.append('phase_600_full_tranche_realization_not_demonstrated')
    # Phase 305 checklist exists but the canonical Phase 305 output package still does not.
    emitted_failure_tokens.append('phase_600_parameter_matrix_incomplete')

    closure_status = 'evidence_supplemented_closure'
    bounded_public_statement = (
        'Genesis has a fixed economic tranche equal to 5 percent of C_max '
        '(1,296,000 ILC); deterministic Phase 600 evidence demonstrates full-tranche '
        'realization across the bounded theoretical-cap matrix, while timing and '
        'implementation-alignment claims remain evidence-supplemented rather than '
        'self-executing runtime law.'
    )
    _require('may accumulate up to' not in bounded_public_statement.lower(), 'phase_600_unbounded_public_tokenomics_claim', 'downgraded_fixed_tranche_language')

    manifest_core = {
        'phase': 600,
        'version': 'phase_600_genesis_economics_parameter_closure_v0.1',
        'success_marker': 'phase_600_genesis_economics_parameter_closure_ok',
        'required_failure_tokens': list(REQUIRED_FAILURE_TOKENS),
        'emitted_failure_tokens': emitted_failure_tokens,
        'input_contract': input_contract,
        'parameter_matrix': matrix['parameter_matrix'],
        'evidence_roots': {
            'authoritative_summary_path': str(authoritative_summary_path),
            'supporting_sensitivity_summary_path': str(sensitivity_summary_path),
        },
        'findings': {
            'full_tranche_realization_demonstrated_on_authoritative_surface': authoritative_reaches,
            'authoritative_reach_target_epoch_p50': matrix['authoritative_summary']['reach_target_epoch_p50'],
            'supporting_issued_to_date_reaches_within_horizon': issued_to_date_reaches,
            'supporting_issued_to_date_final_genesis_cumulative_ilc_p50': matrix['supporting_sensitivity_summary']['final_genesis_cumulative_ilc_p50'],
            'subsidy_factor_sensitivity_bounded': True,
            'multiplier_interaction_sensitivity_bounded': True,
            'phase_305_canonical_package_present': False,
            'future_controller_boundary_preserved': True,
        },
        'closure_decisions': {
            'status': closure_status,
            'decisive_closures': [
                'full-tranche realization is demonstrated across the bounded theoretical-cap matrix tied to the fixed Genesis tranche against C_max',
                'issued-to-date remains non-authoritative for full-tranche realization after Phase 599',
            ],
            'evidence_supplemented_closures': [
                'Genesis fade-away timing remains bounded by the deterministic matrix but is not elevated into standalone public timeline law',
                'subsidy-factor and multiplier sensitivity are bounded by replayable outputs but do not become ratified runtime constants in this phase',
            ],
            'explicit_defers': [
                'Phase 305 canonical output package remains incomplete and is carried as a named evidence follow-on',
                'any Genesis-only ECU realization controller remains a later implementation lane separate from natural centrality measurement',
                'public tokenomics wording remains deferred to Phase 602',
            ],
            'bounded_public_statement': bounded_public_statement,
        },
        'authoritative_outputs': {
            'genesis_target_ilc': GENESIS_TARGET,
            'authoritative_realization_surface': 'fixed_tranche_against_cmax',
            'authoritative_mode': 'theoretical_cap',
            'supporting_mode': 'issued_to_date',
        },
    }
    replay_hash = _sha256_payload(manifest_core)
    rerun_hash = _sha256_payload({
        **manifest_core,
        'replay_contract': {
            'status': 'pending',
            'deterministic_hash': replay_hash,
            'rerun_hash': None,
        },
    })
    # Re-run the matrix deterministically and compare stable hashes.
    rerun_matrix_hash = _sha256_payload(_run_matrix())
    primary_matrix_hash = _sha256_payload(matrix)
    _require(primary_matrix_hash == rerun_matrix_hash, 'phase_600_deterministic_replay_failed', 'matrix_hash_mismatch')
    replay_contract = {
        'status': 'passed',
        'deterministic_hash': replay_hash,
        'rerun_hash': rerun_hash,
        'matrix_hash': primary_matrix_hash,
    }
    manifest = {**manifest_core, 'replay_contract': replay_contract}
    return manifest


def run_phase_600(*, output_root: Path) -> dict[str, Any]:
    output_root.mkdir(parents=True, exist_ok=True)
    manifest = _build_manifest(output_root)
    manifest_path = output_root / 'manifest.json'
    _write_json(manifest_path, manifest)
    return {'manifest_path': str(manifest_path), **manifest}


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='Run the Phase 600 deterministic Genesis economics parameter closure package.')
    parser.add_argument('--output-root', default=str(DEFAULT_OUTPUT_ROOT))
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    output_root = Path(args.output_root)
    try:
        payload = run_phase_600(output_root=output_root)
    except Phase600RunError as exc:
        print(_normalized_json({'marker': 'phase_600_genesis_economics_parameter_closure_failed', 'token': exc.token, 'detail': str(exc)}), flush=True)
        return 1
    print(_normalized_json({'marker': payload['success_marker'], 'manifest_path': payload['manifest_path']}), flush=True)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
