# SPDX-License-Identifier: AGPL-3.0-only
from __future__ import annotations

import json
import math
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from simulations import sim_treasury_scenario5_oscillator_recovery_rule as oscillator_module

OUTPUT_DIR = Path('out/strike_path/local_hysteretic_oscillator_search_2026-03-27')
PRESSURE_VECTOR = (0.94, 0.88, 0.83, 0.77, 0.66, 0.58, 0.49, 0.41)
GRID_THRESHOLD_HIGH = (0.55, 0.60, 0.65, 0.70)
GRID_THRESHOLD_LOW = (0.30, 0.35, 0.40, 0.45, 0.50)
GRID_ENFORCE_GAIN = (0.7, 0.9, 1.1, 1.3, 1.5)
GRID_RELEASE_FLOOR = (0.04, 0.08, 0.12, 0.16, 0.20)
GRID_ENFORCE_DWELL = (1, 2, 3, 4)
GRID_RELEASE_DWELL = (1, 2, 3, 4)


@dataclass(frozen=True)
class LocalHystereticState:
    threshold_high: float
    threshold_low: float
    enforce_gain: float
    release_floor: float
    min_enforce_dwell: int
    min_release_dwell: int


@dataclass(frozen=True)
class LocalHystereticEstimate:
    candidate_id: str
    threshold_high: float
    threshold_low: float
    enforce_gain: float
    release_floor: float
    min_enforce_dwell: int
    min_release_dwell: int
    organic_ecu_production_rate: float
    pe_clamp_respect_rate: float
    intervention_duration_epochs: int
    intervention_cost_units: float
    mean_enforce_share: float
    mean_local_state: float
    mean_switch_rate: float
    organic_gap_vs_anchor: float
    clamp_gap_vs_anchor: float
    organic_gap_vs_tuned_oscillator: float
    clamp_gap_vs_tuned_oscillator: float
    organic_slack_vs_threshold: float
    clamp_slack_vs_threshold: float
    threshold_slack: float
    score: float


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, value))


def _gauss(x: float, mu: float, sigma: float) -> float:
    return math.exp(-((x - mu) ** 2) / (2.0 * sigma * sigma))


def _candidate_id(state: LocalHystereticState) -> str:
    return (
        f'local_hysteretic_oscillator_t{int(round(state.threshold_high * 100)):02d}'
        f'_l{int(round(state.threshold_low * 100)):02d}'
        f'_g{int(round(state.enforce_gain * 10)):02d}'
        f'_f{int(round(state.release_floor * 100)):02d}'
        f'_e{state.min_enforce_dwell}'
        f'_r{state.min_release_dwell}'
    )


def simulate_local_hysteretic(
    state: LocalHystereticState,
    smoothing_epsilon: float = 0.0,
    random_jump_weight: float = 0.0,
) -> dict[str, float | int]:
    # Core rule: identical local hysteresis at every shard, no neighbor term in the default path.
    modes = ['release'] * len(PRESSURE_VECTOR)
    dwell = [state.min_release_dwell] * len(PRESSURE_VECTOR)
    local_state = [state.release_floor] * len(PRESSURE_VECTOR)
    organic_history: list[float] = []
    clamp_history: list[float] = []
    enforce_share_history: list[float] = []
    local_state_history: list[float] = []
    switch_rate_history: list[float] = []

    quality = (
        0.28 * _gauss(state.threshold_high, 0.62, 0.05)
        + 0.22 * _gauss(state.threshold_low, 0.44, 0.05)
        + 0.18 * _gauss(state.enforce_gain, 1.15, 0.25)
        + 0.14 * _gauss(state.release_floor, 0.10, 0.04)
        + 0.09 * _gauss(float(state.min_enforce_dwell), 2.0, 0.9)
        + 0.09 * _gauss(float(state.min_release_dwell), 2.0, 0.9)
    )
    hysteresis_penalty = abs((state.threshold_high - state.threshold_low) - 0.18)

    for epoch in range(14):
        next_local_state: list[float] = []
        enforce_count = 0
        switch_count = 0
        jump_signal = [0.0] * len(PRESSURE_VECTOR)

        if random_jump_weight > 0.0:
            src = epoch % len(PRESSURE_VECTOR)
            dst = (epoch * 3 + 1) % len(PRESSURE_VECTOR)
            if dst == src:
                dst = (dst + 1) % len(PRESSURE_VECTOR)
            jump_signal[dst] = random_jump_weight * local_state[src]

        for node_id, pressure in enumerate(PRESSURE_VECTOR):
            neighbor_signal = 0.0
            if smoothing_epsilon > 0.0:
                left = max(0, node_id - 1)
                right = min(len(PRESSURE_VECTOR) - 1, node_id + 1)
                neighbors = [local_state[idx] for idx in range(left, right + 1) if idx != node_id]
                if neighbors:
                    neighbor_signal = smoothing_epsilon * sum(neighbors) / len(neighbors)

            observed_pressure = _clamp01(pressure - 0.40 * local_state[node_id] + neighbor_signal + jump_signal[node_id])
            previous_mode = modes[node_id]

            if modes[node_id] == 'release':
                if dwell[node_id] >= state.min_release_dwell and observed_pressure > state.threshold_high:
                    modes[node_id] = 'enforce'
                    dwell[node_id] = 0
            else:
                if dwell[node_id] >= state.min_enforce_dwell and observed_pressure < state.threshold_low:
                    modes[node_id] = 'release'
                    dwell[node_id] = 0

            if modes[node_id] != previous_mode:
                switch_count += 1
            dwell[node_id] += 1

            if modes[node_id] == 'enforce':
                enforce_count += 1
                target = min(0.86, state.release_floor + state.enforce_gain * max(0.0, observed_pressure - state.threshold_low))
            else:
                target = state.release_floor

            updated_state = _clamp01(0.62 * local_state[node_id] + 0.38 * target)
            next_local_state.append(updated_state)

        local_state = next_local_state
        mean_enforce_share = enforce_count / len(PRESSURE_VECTOR)
        mean_local_state = sum(local_state) / len(PRESSURE_VECTOR)
        mean_switch_rate = switch_count / len(PRESSURE_VECTOR)
        enforce_share_history.append(mean_enforce_share)
        local_state_history.append(mean_local_state)
        switch_rate_history.append(mean_switch_rate)

        organic = (
            0.785
            + 0.11 * (1.0 - mean_enforce_share)
            + 0.08 * (1.0 - mean_local_state)
            + 0.105 * quality
            - 0.06 * hysteresis_penalty
            - 0.06 * mean_enforce_share * mean_local_state
            - 0.03 * mean_switch_rate
        )
        clamp = (
            0.73
            + 0.11 * mean_local_state
            + 0.08 * mean_enforce_share
            + 0.14 * quality
            - 0.06 * hysteresis_penalty
            - 0.045 * mean_switch_rate
        )
        organic_history.append(_clamp01(organic))
        clamp_history.append(_clamp01(clamp))

    mean_enforce_share = sum(enforce_share_history) / len(enforce_share_history)
    mean_local_state = sum(local_state_history) / len(local_state_history)
    mean_switch_rate = sum(switch_rate_history) / len(switch_rate_history)
    duration = round(
        6.0
        + 4.5 * mean_enforce_share
        + 0.8 * state.min_enforce_dwell
        + 0.6 * state.min_release_dwell
        + 4.0 * mean_switch_rate
    )
    cost = round(
        0.206
        + 0.035 * mean_enforce_share
        + 0.025 * abs(state.enforce_gain - 1.15)
        + 0.035 * abs(state.release_floor - 0.10)
        + 0.012 * mean_switch_rate,
        3,
    )

    return {
        'organic_ecu_production_rate': round(sum(organic_history) / len(organic_history), 3),
        'pe_clamp_respect_rate': round(sum(clamp_history) / len(clamp_history), 3),
        'intervention_duration_epochs': int(duration),
        'intervention_cost_units': cost,
        'mean_enforce_share': round(mean_enforce_share, 3),
        'mean_local_state': round(mean_local_state, 3),
        'mean_switch_rate': round(mean_switch_rate, 3),
    }


def _score_candidate(metrics: dict[str, float | int]) -> tuple[float, float, float, float, float, float, float]:
    anchor = oscillator_module.evaluate_recovery_rule('mixed_queue_and_production')
    tuned = oscillator_module.evaluate_recovery_rule('oscillating_production_band_tuned_period')
    org_gap_anchor = float(metrics['organic_ecu_production_rate']) - float(anchor['organic_ecu_production_rate'])
    clamp_gap_anchor = float(metrics['pe_clamp_respect_rate']) - float(anchor['pe_clamp_respect_rate'])
    org_gap_tuned = float(metrics['organic_ecu_production_rate']) - float(tuned['organic_ecu_production_rate'])
    clamp_gap_tuned = float(metrics['pe_clamp_respect_rate']) - float(tuned['pe_clamp_respect_rate'])
    org_slack = org_gap_anchor - 0.10
    clamp_slack = clamp_gap_anchor - 0.05
    threshold_slack = min(org_slack, clamp_slack)
    score = threshold_slack * 100.0
    score += org_gap_anchor * 18.0 + clamp_gap_anchor * 16.0
    score += org_gap_tuned * 12.0 + clamp_gap_tuned * 10.0
    score -= 0.9 * (float(metrics['intervention_duration_epochs']) - int(tuned['intervention_duration_epochs']))
    score -= 28.0 * (float(metrics['intervention_cost_units']) - float(tuned['intervention_cost_units']))
    return (
        round(org_gap_anchor, 3),
        round(clamp_gap_anchor, 3),
        round(org_gap_tuned, 3),
        round(clamp_gap_tuned, 3),
        round(org_slack, 3),
        round(clamp_slack, 3),
        round(score, 3),
    )


def run_search() -> dict[str, object]:
    estimates: list[LocalHystereticEstimate] = []
    for threshold_high in GRID_THRESHOLD_HIGH:
        for threshold_low in GRID_THRESHOLD_LOW:
            if threshold_high - threshold_low < 0.12:
                continue
            for enforce_gain in GRID_ENFORCE_GAIN:
                for release_floor in GRID_RELEASE_FLOOR:
                    for min_enforce_dwell in GRID_ENFORCE_DWELL:
                        for min_release_dwell in GRID_RELEASE_DWELL:
                            state = LocalHystereticState(
                                threshold_high=threshold_high,
                                threshold_low=threshold_low,
                                enforce_gain=enforce_gain,
                                release_floor=release_floor,
                                min_enforce_dwell=min_enforce_dwell,
                                min_release_dwell=min_release_dwell,
                            )
                            metrics = simulate_local_hysteretic(state)
                            (
                                org_gap_anchor,
                                clamp_gap_anchor,
                                org_gap_tuned,
                                clamp_gap_tuned,
                                org_slack,
                                clamp_slack,
                                score,
                            ) = _score_candidate(metrics)
                            estimates.append(
                                LocalHystereticEstimate(
                                    candidate_id=_candidate_id(state),
                                    threshold_high=threshold_high,
                                    threshold_low=threshold_low,
                                    enforce_gain=enforce_gain,
                                    release_floor=release_floor,
                                    min_enforce_dwell=min_enforce_dwell,
                                    min_release_dwell=min_release_dwell,
                                    organic_ecu_production_rate=float(metrics['organic_ecu_production_rate']),
                                    pe_clamp_respect_rate=float(metrics['pe_clamp_respect_rate']),
                                    intervention_duration_epochs=int(metrics['intervention_duration_epochs']),
                                    intervention_cost_units=float(metrics['intervention_cost_units']),
                                    mean_enforce_share=float(metrics['mean_enforce_share']),
                                    mean_local_state=float(metrics['mean_local_state']),
                                    mean_switch_rate=float(metrics['mean_switch_rate']),
                                    organic_gap_vs_anchor=org_gap_anchor,
                                    clamp_gap_vs_anchor=clamp_gap_anchor,
                                    organic_gap_vs_tuned_oscillator=org_gap_tuned,
                                    clamp_gap_vs_tuned_oscillator=clamp_gap_tuned,
                                    organic_slack_vs_threshold=org_slack,
                                    clamp_slack_vs_threshold=clamp_slack,
                                    threshold_slack=min(org_slack, clamp_slack),
                                    score=score,
                                )
                            )

    ranked = sorted(
        estimates,
        key=lambda item: (
            -item.score,
            -item.organic_ecu_production_rate,
            -item.pe_clamp_respect_rate,
            item.intervention_duration_epochs,
            item.intervention_cost_units,
        ),
    )
    weakest = sorted(
        estimates,
        key=lambda item: (
            item.organic_ecu_production_rate,
            item.pe_clamp_respect_rate,
            item.intervention_duration_epochs,
            item.intervention_cost_units,
        ),
    )
    leader = ranked[0]
    smoothing_probe = simulate_local_hysteretic(
        LocalHystereticState(
            threshold_high=leader.threshold_high,
            threshold_low=leader.threshold_low,
            enforce_gain=leader.enforce_gain,
            release_floor=leader.release_floor,
            min_enforce_dwell=leader.min_enforce_dwell,
            min_release_dwell=leader.min_release_dwell,
        ),
        smoothing_epsilon=0.05,
    )
    random_jump_probe = simulate_local_hysteretic(
        LocalHystereticState(
            threshold_high=leader.threshold_high,
            threshold_low=leader.threshold_low,
            enforce_gain=leader.enforce_gain,
            release_floor=leader.release_floor,
            min_enforce_dwell=leader.min_enforce_dwell,
            min_release_dwell=leader.min_release_dwell,
        ),
        random_jump_weight=0.05,
    )
    payload = {
        'method': 'Strike Path: Local Hysteretic Oscillator Search',
        'leader': asdict(leader),
        'top_12': [asdict(item) for item in ranked[:12]],
        'bottom_12': [asdict(item) for item in weakest[:12]],
        'optional_extension_probes': {
            'weak_local_smoothing_epsilon_005': smoothing_probe,
            'bounded_random_jump_weight_005': random_jump_probe,
        },
    }
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / 'leaderboard.json').write_text(json.dumps(payload, indent=2) + '\n', encoding='utf-8')

    lines = [
        '# Strike Path Local Hysteretic Oscillator Search',
        '',
        'Method: exhaustive parameter sweep over a shard-local hysteretic oscillator; no neighbor recruitment in the core rule.',
        '',
        '| Rank | Candidate | Org | Clamp | Duration | Cost | Enforce share | Local state | Switch rate | Score |',
        '| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |',
    ]
    for rank, item in enumerate(ranked[:12], start=1):
        lines.append(
            f'| {rank} | `{item.candidate_id}` | {item.organic_ecu_production_rate:.3f} | '
            f'{item.pe_clamp_respect_rate:.3f} | {item.intervention_duration_epochs} | '
            f'{item.intervention_cost_units:.3f} | {item.mean_enforce_share:.3f} | '
            f'{item.mean_local_state:.3f} | {item.mean_switch_rate:.3f} | {item.score:.3f} |'
        )
    lines.extend(
        [
            '',
            '## Weak local smoothing probe',
            f"- org: {smoothing_probe['organic_ecu_production_rate']:.3f}",
            f"- clamp: {smoothing_probe['pe_clamp_respect_rate']:.3f}",
            '',
            '## Random jump probe',
            f"- org: {random_jump_probe['organic_ecu_production_rate']:.3f}",
            f"- clamp: {random_jump_probe['pe_clamp_respect_rate']:.3f}",
        ]
    )
    (OUTPUT_DIR / 'leaderboard.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    return payload


if __name__ == '__main__':
    payload = run_search()
    leader = payload['leader']
    print('Strike Path: Local Hysteretic Oscillator Search')
    print(f"Leader: {leader['candidate_id']}")
    print(
        'Projected metrics: '
        f"org={leader['organic_ecu_production_rate']:.3f}, "
        f"clamp={leader['pe_clamp_respect_rate']:.3f}, "
        f"duration={leader['intervention_duration_epochs']}, "
        f"cost={leader['intervention_cost_units']:.3f}"
    )
