from __future__ import annotations

import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from simulations import sim_treasury_scenario5_oscillator_recovery_rule as current_oscillator

OUTPUT_DIR = Path('out/strike_path/oscillator_search_2026-03-26')


@dataclass(frozen=True)
class CandidateEstimate:
    candidate_id: str
    oscillation_period: int
    oscillation_amplitude: float
    phase_offset: str
    organic_ecu_production_rate: float
    pe_clamp_respect_rate: float
    intervention_duration_epochs: int
    intervention_cost_units: float
    organic_gap_vs_short: float
    clamp_gap_vs_short: float
    organic_slack_vs_threshold: float
    clamp_slack_vs_threshold: float
    threshold_slack: float
    score: float


def _interp(points: list[tuple[float, float]], x: float) -> float:
    if x <= points[0][0]:
        return points[0][1]
    if x >= points[-1][0]:
        return points[-1][1]
    for (x0, y0), (x1, y1) in zip(points, points[1:]):
        if x0 <= x <= x1:
            if x1 == x0:
                return y0
            t = (x - x0) / (x1 - x0)
            return y0 + t * (y1 - y0)
    raise AssertionError('interpolation_failed')


def estimate_metrics(period: int, amplitude: float, phase_offset: str) -> dict[str, float | int]:
    if phase_offset not in {'enforce_first', 'release_first'}:
        raise ValueError(f'unsupported_phase_offset:{phase_offset}')

    period_org_points = [(2, 0.03), (3, 0.05), (4, 0.06), (5, 0.07), (6, 0.08), (7, 0.04), (8, -0.01), (9, -0.03)]
    amp_org_points = [(0.04, -0.02), (0.05, -0.01), (0.06, 0.00), (0.07, 0.01), (0.08, 0.03), (0.09, 0.04), (0.10, 0.05), (0.11, 0.045), (0.12, 0.03)]
    period_clamp_points = [(2, 0.00), (3, 0.01), (4, 0.03), (5, 0.04), (6, 0.045), (7, 0.04), (8, 0.03), (9, 0.02)]
    amp_clamp_points = [(0.04, 0.00), (0.05, 0.005), (0.06, 0.00), (0.07, 0.00), (0.08, 0.01), (0.09, 0.02), (0.10, 0.025), (0.11, 0.02), (0.12, 0.015)]
    period_duration_points = [(2, 8.0), (3, 8.5), (4, 9.0), (5, 9.0), (6, 10.0), (7, 11.0), (8, 12.0), (9, 13.0)]
    period_cost_points = [(2, 0.23), (3, 0.235), (4, 0.245), (5, 0.25), (6, 0.255), (7, 0.265), (8, 0.27), (9, 0.28)]
    amp_cost_points = [(0.04, 0.01), (0.05, 0.012), (0.06, 0.015), (0.07, 0.01), (0.08, 0.012), (0.09, 0.01), (0.10, 0.012), (0.11, 0.018), (0.12, 0.022)]

    phase_org_bonus = 0.01 if phase_offset == 'enforce_first' else -0.01
    phase_clamp_bonus = 0.01 if phase_offset == 'enforce_first' else -0.01
    phase_duration_bonus = 0.5 if phase_offset == 'release_first' else 0.0
    phase_cost_bonus = 0.01 if phase_offset == 'release_first' else 0.0

    organic = 0.83 + _interp(period_org_points, period) + _interp(amp_org_points, amplitude) + phase_org_bonus
    clamp = 0.82 + _interp(period_clamp_points, period) + _interp(amp_clamp_points, amplitude) + phase_clamp_bonus
    duration = int(round(_interp(period_duration_points, period) + (0.5 if amplitude >= 0.10 else 0.0) + phase_duration_bonus))
    cost = _interp(period_cost_points, period) + _interp(amp_cost_points, amplitude) + phase_cost_bonus

    return {
        'organic_ecu_production_rate': round(max(0.0, min(1.0, organic)), 3),
        'pe_clamp_respect_rate': round(max(0.0, min(1.0, clamp)), 3),
        'intervention_duration_epochs': duration,
        'intervention_cost_units': round(cost, 3),
    }


def evaluate_search_space() -> list[CandidateEstimate]:
    short = current_oscillator.evaluate_recovery_rule(
        'oscillating_production_band_short_period',
        current_oscillator.get_candidate_definition('oscillating_production_band_short_period').parameters,
    )
    current_tuned = current_oscillator.evaluate_recovery_rule(
        'oscillating_production_band_tuned_period',
        current_oscillator.get_candidate_definition('oscillating_production_band_tuned_period').parameters,
    )
    baseline_score = {
        'organic': current_tuned['organic_ecu_production_rate'] - short['organic_ecu_production_rate'],
        'clamp': current_tuned['pe_clamp_respect_rate'] - short['pe_clamp_respect_rate'],
    }

    estimates: list[CandidateEstimate] = []
    for period in range(2, 10):
        for amplitude_i in range(4, 13):
            amplitude = amplitude_i / 100.0
            for phase_offset in ('enforce_first', 'release_first'):
                metrics = estimate_metrics(period, amplitude, phase_offset)
                organic_gap = metrics['organic_ecu_production_rate'] - short['organic_ecu_production_rate']
                clamp_gap = metrics['pe_clamp_respect_rate'] - short['pe_clamp_respect_rate']
                organic_slack = organic_gap - 0.10
                clamp_slack = clamp_gap - 0.05
                threshold_slack = min(organic_slack, clamp_slack)
                score = (
                    threshold_slack * 100.0
                    + organic_gap * 15.0
                    + clamp_gap * 12.0
                    - 0.8 * (metrics['intervention_duration_epochs'] - current_tuned['intervention_duration_epochs'])
                    - 25.0 * (metrics['intervention_cost_units'] - current_tuned['intervention_cost_units'])
                )
                estimates.append(
                    CandidateEstimate(
                        candidate_id=f'oscillating_production_band_p{period}_a{amplitude_i:02d}_{phase_offset}',
                        oscillation_period=period,
                        oscillation_amplitude=amplitude,
                        phase_offset=phase_offset,
                        organic_ecu_production_rate=float(metrics['organic_ecu_production_rate']),
                        pe_clamp_respect_rate=float(metrics['pe_clamp_respect_rate']),
                        intervention_duration_epochs=int(metrics['intervention_duration_epochs']),
                        intervention_cost_units=float(metrics['intervention_cost_units']),
                        organic_gap_vs_short=round(organic_gap, 3),
                        clamp_gap_vs_short=round(clamp_gap, 3),
                        organic_slack_vs_threshold=round(organic_slack, 3),
                        clamp_slack_vs_threshold=round(clamp_slack, 3),
                        threshold_slack=round(threshold_slack, 3),
                        score=round(score, 3),
                    )
                )

    estimates.sort(key=lambda item: (item.threshold_slack, item.score), reverse=True)
    return estimates


def _write_outputs(estimates: Iterable[CandidateEstimate]) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    estimates = list(estimates)
    top10 = estimates[:10]
    payload = {
        'method': 'Strike Path: Oscillator Search',
        'baseline_leader': 'oscillating_production_band_tuned_period',
        'baseline_best_remaining_alternative': 'oscillating_production_band_short_period',
        'top_10': [asdict(item) for item in top10],
    }
    (OUTPUT_DIR / 'leaderboard.json').write_text(json.dumps(payload, indent=2) + '\n', encoding='utf-8')

    lines = [
        '# Strike Path Oscillator Search Leaderboard',
        '',
        '| Rank | Candidate | Org | Clamp | Org gap vs short | Clamp gap vs short | Slack | Duration | Cost |',
        '| --- | --- | --- | --- | --- | --- | --- | --- | --- |',
    ]
    for rank, item in enumerate(top10, start=1):
        lines.append(
            f'| {rank} | `{item.candidate_id}` | {item.organic_ecu_production_rate:.3f} | {item.pe_clamp_respect_rate:.3f} | '
            f'{item.organic_gap_vs_short:.3f} | {item.clamp_gap_vs_short:.3f} | {item.threshold_slack:.3f} | '
            f'{item.intervention_duration_epochs} | {item.intervention_cost_units:.3f} |'
        )
    (OUTPUT_DIR / 'leaderboard.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')


def main() -> int:
    estimates = evaluate_search_space()
    _write_outputs(estimates)
    leader = estimates[0]
    print('Strike Path: Oscillator Search')
    print(f'Best candidate: {leader.candidate_id}')
    print(
        'Projected metrics: '
        f"org={leader.organic_ecu_production_rate:.3f}, "
        f"clamp={leader.pe_clamp_respect_rate:.3f}, "
        f"duration={leader.intervention_duration_epochs}, "
        f"cost={leader.intervention_cost_units:.3f}"
    )
    print(
        'Projected gaps vs current short-period challenger: '
        f"org={leader.organic_gap_vs_short:.3f}, clamp={leader.clamp_gap_vs_short:.3f}, "
        f"threshold_slack={leader.threshold_slack:.3f}"
    )
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
