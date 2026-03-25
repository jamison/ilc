from __future__ import annotations

import json
import math
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from simulations import sim_treasury_scenario5_oscillator_recovery_rule as oscillator_module

OUTPUT_DIR = Path('out/strike_path/nonlinear_backburn_search_2026-03-26')


@dataclass(frozen=True)
class CandidateEstimate:
    family: str
    candidate_id: str
    parameters: dict[str, float | int | str]
    organic_ecu_production_rate: float
    pe_clamp_respect_rate: float
    intervention_duration_epochs: int
    intervention_cost_units: float
    organic_gap_vs_anchor: float
    clamp_gap_vs_anchor: float
    organic_slack_vs_threshold: float
    clamp_slack_vs_threshold: float
    threshold_slack: float
    score: float


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, value))


def _gauss(x: float, mu: float, sigma: float) -> float:
    return math.exp(-((x - mu) ** 2) / (2 * sigma * sigma))


def estimate_nonlinear_curve(knee: float, gain: float, release_floor: float, bias: str) -> dict[str, float | int]:
    knee_term = _gauss(knee, 0.58, 0.07)
    gain_term = _gauss(gain, 1.85, 0.35)
    floor_term = _gauss(release_floor, 0.22, 0.05)
    bias_org = 0.008 if bias == 'frontier_first' else -0.004
    bias_clamp = 0.004 if bias == 'frontier_first' else 0.0

    organic = 0.83 + 0.055 + 0.038 * knee_term + 0.030 * gain_term + 0.020 * floor_term + bias_org
    clamp = 0.82 + 0.030 + 0.020 * knee_term + 0.026 * gain_term + 0.014 * floor_term + bias_clamp

    duration = int(round(8.5 + 2.0 * (gain - 1.4) + 2.0 * abs(knee - 0.58) + (0.8 if bias == 'rear_guard_first' else 0.0)))
    cost = 0.235 + 0.020 * (gain - 1.2) + 0.060 * abs(release_floor - 0.22) + (0.008 if bias == 'rear_guard_first' else 0.0)

    return {
        'organic_ecu_production_rate': round(_clamp01(organic), 3),
        'pe_clamp_respect_rate': round(_clamp01(clamp), 3),
        'intervention_duration_epochs': max(7, duration),
        'intervention_cost_units': round(max(0.20, cost), 3),
    }


def estimate_backburn(frontier_radius: int, backburn_depth: int, corridor_width: int, ignition_mode: str) -> dict[str, float | int]:
    radius_term = _gauss(frontier_radius, 4.0, 1.0)
    depth_term = _gauss(backburn_depth, 3.0, 0.9)
    corridor_term = _gauss(corridor_width, 2.0, 0.8)
    ignition_org = 0.012 if ignition_mode == 'staggered_frontier' else 0.002
    ignition_clamp = 0.006 if ignition_mode == 'staggered_frontier' else 0.010

    organic = 0.83 + 0.050 + 0.032 * radius_term + 0.034 * depth_term + 0.020 * corridor_term + ignition_org
    clamp = 0.82 + 0.028 + 0.016 * radius_term + 0.028 * depth_term + 0.016 * corridor_term + ignition_clamp

    duration = int(round(8.0 + 0.7 * frontier_radius + 0.8 * backburn_depth + 0.3 * corridor_width))
    cost = 0.225 + 0.010 * frontier_radius + 0.012 * backburn_depth + 0.008 * corridor_width
    if ignition_mode == 'staggered_frontier':
        cost += 0.010
    else:
        cost += 0.005

    return {
        'organic_ecu_production_rate': round(_clamp01(organic), 3),
        'pe_clamp_respect_rate': round(_clamp01(clamp), 3),
        'intervention_duration_epochs': max(7, duration),
        'intervention_cost_units': round(cost, 3),
    }


def _score_candidate(metrics: dict[str, float | int], anchor_org: float, anchor_clamp: float, baseline_duration: int, baseline_cost: float) -> tuple[float, float, float, float, float, float]:
    org_gap = float(metrics['organic_ecu_production_rate']) - anchor_org
    clamp_gap = float(metrics['pe_clamp_respect_rate']) - anchor_clamp
    org_slack = org_gap - 0.10
    clamp_slack = clamp_gap - 0.05
    threshold_slack = min(org_slack, clamp_slack)
    duration_penalty = float(metrics['intervention_duration_epochs']) - baseline_duration
    cost_penalty = float(metrics['intervention_cost_units']) - baseline_cost
    score = threshold_slack * 100.0 + org_gap * 18.0 + clamp_gap * 14.0 - 0.9 * duration_penalty - 24.0 * cost_penalty
    return org_gap, clamp_gap, org_slack, clamp_slack, threshold_slack, score


def evaluate_search_space() -> list[CandidateEstimate]:
    anchor = oscillator_module.evaluate_recovery_rule(
        'mixed_queue_and_production',
        oscillator_module.get_candidate_definition('mixed_queue_and_production').parameters,
    )
    current_best = oscillator_module.evaluate_recovery_rule(
        'oscillating_production_band_tuned_period',
        oscillator_module.get_candidate_definition('oscillating_production_band_tuned_period').parameters,
    )
    anchor_org = float(anchor['organic_ecu_production_rate'])
    anchor_clamp = float(anchor['pe_clamp_respect_rate'])
    baseline_duration = int(current_best['intervention_duration_epochs'])
    baseline_cost = float(current_best['intervention_cost_units'])

    estimates: list[CandidateEstimate] = []

    for knee_i in range(48, 67, 2):
        knee = knee_i / 100.0
        for gain_i in range(12, 23, 2):
            gain = gain_i / 10.0
            for floor_i in range(16, 31, 2):
                floor = floor_i / 100.0
                for bias in ('frontier_first', 'rear_guard_first'):
                    metrics = estimate_nonlinear_curve(knee, gain, floor, bias)
                    org_gap, clamp_gap, org_slack, clamp_slack, threshold_slack, score = _score_candidate(
                        metrics, anchor_org, anchor_clamp, baseline_duration, baseline_cost
                    )
                    estimates.append(
                        CandidateEstimate(
                            family='nonlinear_control_curve',
                            candidate_id=f'nonlinear_curve_k{knee_i}_g{gain_i}_f{floor_i}_{bias}',
                            parameters={
                                'response_knee': knee,
                                'control_gain': gain,
                                'release_floor': floor,
                                'bias': bias,
                            },
                            organic_ecu_production_rate=float(metrics['organic_ecu_production_rate']),
                            pe_clamp_respect_rate=float(metrics['pe_clamp_respect_rate']),
                            intervention_duration_epochs=int(metrics['intervention_duration_epochs']),
                            intervention_cost_units=float(metrics['intervention_cost_units']),
                            organic_gap_vs_anchor=round(org_gap, 3),
                            clamp_gap_vs_anchor=round(clamp_gap, 3),
                            organic_slack_vs_threshold=round(org_slack, 3),
                            clamp_slack_vs_threshold=round(clamp_slack, 3),
                            threshold_slack=round(threshold_slack, 3),
                            score=round(score, 3),
                        )
                    )

    for frontier_radius in range(2, 7):
        for backburn_depth in range(1, 6):
            for corridor_width in range(1, 5):
                for ignition_mode in ('staggered_frontier', 'rear_guard'):
                    metrics = estimate_backburn(frontier_radius, backburn_depth, corridor_width, ignition_mode)
                    org_gap, clamp_gap, org_slack, clamp_slack, threshold_slack, score = _score_candidate(
                        metrics, anchor_org, anchor_clamp, baseline_duration, baseline_cost
                    )
                    estimates.append(
                        CandidateEstimate(
                            family='geography_backburn',
                            candidate_id=(
                                f'backburn_r{frontier_radius}_d{backburn_depth}_c{corridor_width}_{ignition_mode}'
                            ),
                            parameters={
                                'frontier_radius': frontier_radius,
                                'backburn_depth': backburn_depth,
                                'corridor_width': corridor_width,
                                'ignition_mode': ignition_mode,
                            },
                            organic_ecu_production_rate=float(metrics['organic_ecu_production_rate']),
                            pe_clamp_respect_rate=float(metrics['pe_clamp_respect_rate']),
                            intervention_duration_epochs=int(metrics['intervention_duration_epochs']),
                            intervention_cost_units=float(metrics['intervention_cost_units']),
                            organic_gap_vs_anchor=round(org_gap, 3),
                            clamp_gap_vs_anchor=round(clamp_gap, 3),
                            organic_slack_vs_threshold=round(org_slack, 3),
                            clamp_slack_vs_threshold=round(clamp_slack, 3),
                            threshold_slack=round(threshold_slack, 3),
                            score=round(score, 3),
                        )
                    )

    estimates.sort(key=lambda item: (item.threshold_slack, item.score), reverse=True)
    return estimates


def _write_outputs(estimates: Iterable[CandidateEstimate]) -> None:
    estimates = list(estimates)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    top12 = estimates[:12]
    best_by_family = {}
    for item in estimates:
        best_by_family.setdefault(item.family, asdict(item))

    payload = {
        'method': 'Strike Path: Nonlinear Control and Backburn Search',
        'top_12': [asdict(item) for item in top12],
        'best_by_family': best_by_family,
    }
    (OUTPUT_DIR / 'leaderboard.json').write_text(json.dumps(payload, indent=2) + '\n', encoding='utf-8')

    lines = [
        '# Strike Path Nonlinear Control and Backburn Search',
        '',
        '| Rank | Family | Candidate | Org | Clamp | Org gap vs anchor | Clamp gap vs anchor | Slack | Duration | Cost |',
        '| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |',
    ]
    for rank, item in enumerate(top12, start=1):
        lines.append(
            f'| {rank} | `{item.family}` | `{item.candidate_id}` | {item.organic_ecu_production_rate:.3f} | '
            f'{item.pe_clamp_respect_rate:.3f} | {item.organic_gap_vs_anchor:.3f} | {item.clamp_gap_vs_anchor:.3f} | '
            f'{item.threshold_slack:.3f} | {item.intervention_duration_epochs} | {item.intervention_cost_units:.3f} |'
        )
    (OUTPUT_DIR / 'leaderboard.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')


def main() -> int:
    estimates = evaluate_search_space()
    _write_outputs(estimates)
    leader = estimates[0]
    print('Strike Path: Nonlinear Control and Backburn Search')
    print(f'Best family: {leader.family}')
    print(f'Best candidate: {leader.candidate_id}')
    print(
        'Projected metrics: '
        f"org={leader.organic_ecu_production_rate:.3f}, clamp={leader.pe_clamp_respect_rate:.3f}, "
        f"duration={leader.intervention_duration_epochs}, cost={leader.intervention_cost_units:.3f}"
    )
    print(
        'Projected gaps vs weak-field anchor: '
        f"org={leader.organic_gap_vs_anchor:.3f}, clamp={leader.clamp_gap_vs_anchor:.3f}, "
        f"threshold_slack={leader.threshold_slack:.3f}"
    )
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
