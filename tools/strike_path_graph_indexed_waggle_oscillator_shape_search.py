# SPDX-License-Identifier: AGPL-3.0-only
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

from tools import strike_path_graph_indexed_waggle_oscillator_extended_search as base
from simulations import sim_treasury_scenario5_oscillator_recovery_rule as oscillator_module

OUTPUT_DIR = Path('out/strike_path/graph_indexed_waggle_oscillator_shape_search_2026-03-27')


@dataclass(frozen=True)
class ShapeHybridState:
    waggle_candidate_id: str
    oscillation_period: int
    oscillation_amplitude: float
    phase_offset: str
    recruitment_strength: float
    abandonment_rate: float
    gate_duty_cycle: float
    bias_strength: float
    adjacency_scale: float
    curve_power: float
    saturation_steepness: float
    release_blend: float
    generation: int = 0


@dataclass(frozen=True)
class ShapeHybridEstimate:
    generation: int
    waggle_candidate_id: str
    waggle_source_module: str
    oscillation_period: int
    oscillation_amplitude: float
    phase_offset: str
    recruitment_strength: float
    abandonment_rate: float
    gate_duty_cycle: float
    bias_strength: float
    adjacency_scale: float
    curve_power: float
    saturation_steepness: float
    release_blend: float
    organic_ecu_production_rate: float
    pe_clamp_respect_rate: float
    intervention_duration_epochs: int
    intervention_cost_units: float
    frontier_mean_enforcement: float
    core_mean_enforcement: float
    frontier_core_gradient: float
    organic_gap_vs_anchor: float
    clamp_gap_vs_anchor: float
    organic_gap_vs_tuned_oscillator: float
    clamp_gap_vs_tuned_oscillator: float
    organic_gap_vs_best_waggle: float
    clamp_gap_vs_best_waggle: float
    organic_slack_vs_threshold: float
    clamp_slack_vs_threshold: float
    threshold_slack: float
    score: float


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, value))


def _clamp_range(value: float, lower: float, upper: float) -> float:
    return max(lower, min(upper, value))


def simulate_shape_hybrid(
    state: ShapeHybridState,
    waggle_candidates: dict[str, tuple[str, dict[str, float | int], dict[str, float | int]]],
) -> tuple[str, dict[str, float | int | float]]:
    waggle_source_module, waggle_parameters, waggle_metrics = waggle_candidates[state.waggle_candidate_id]

    response_knee = float(waggle_parameters['response_knee'])
    control_gain = float(waggle_parameters['control_gain'])
    release_floor = float(waggle_parameters['release_floor'])
    bias = str(waggle_parameters['bias'])
    node_bias = base._scaled_bias_profile(bias, state.bias_strength)

    node_state = [release_floor * 0.6 for _ in base.PRESSURE_VECTOR]
    recruit_weight = (0.07 + 0.03 * base._gauss(control_gain, 1.85, 0.35)) * state.recruitment_strength
    recruit_weight = _clamp_range(recruit_weight, 0.03, 0.18)
    abandonment = (0.16 + 0.05 * (1.0 - base._gauss(float(state.oscillation_period), 5.0, 1.2))) * state.abandonment_rate
    abandonment = _clamp_range(abandonment, 0.08, 0.32)

    organic_history: list[float] = []
    clamp_history: list[float] = []
    frontier_state_history: list[float] = []
    core_state_history: list[float] = []

    for epoch in range(14):
        gate = base._oscillator_gate(
            state.oscillation_period,
            state.oscillation_amplitude,
            state.phase_offset,
            epoch,
            release_floor,
            state.gate_duty_cycle,
        )
        next_state: list[float] = []
        organic_nodes: list[float] = []
        clamp_nodes: list[float] = []

        for node_id, pressure in enumerate(base.PRESSURE_VECTOR):
            neighbor_signal = 0.0
            for neighbor_id, edge_weight in base.GRAPH_EDGES[node_id].items():
                neighbor_signal += (edge_weight * state.adjacency_scale) * node_state[neighbor_id]
            local_signal = min(1.0, pressure + 0.18 * neighbor_signal)
            linear_response = max(0.0, local_signal - response_knee) * control_gain * node_bias[node_id]
            curved_response = linear_response ** state.curve_power if linear_response > 0.0 else 0.0
            target_enforcement = release_floor * state.release_blend + gate * (
                curved_response / (1.0 + state.saturation_steepness * curved_response)
            )
            updated_state = (1.0 - abandonment) * node_state[node_id] + 0.40 * target_enforcement + recruit_weight * neighbor_signal
            updated_state = _clamp01(updated_state)
            next_state.append(updated_state)

            organic_node = 0.90 + 0.10 * (1.0 - 0.85 * updated_state) + 0.025 * (1.0 - gate) + 0.02 * (1.0 - pressure)
            clamp_node = 0.80 + 0.12 * updated_state + 0.025 * gate * pressure
            organic_nodes.append(_clamp01(organic_node))
            clamp_nodes.append(_clamp01(clamp_node))

        node_state = next_state
        organic_history.append(sum(value * weight for value, weight in zip(organic_nodes, base.PRODUCTION_WEIGHTS)) / sum(base.PRODUCTION_WEIGHTS))
        clamp_history.append(sum(value * weight for value, weight in zip(clamp_nodes, base.CLAMP_WEIGHTS)) / sum(base.CLAMP_WEIGHTS))
        frontier_state_history.append(sum(node_state[node_id] for node_id in base.FRONTIER_NODE_IDS) / len(base.FRONTIER_NODE_IDS))
        core_state_history.append(sum(node_state[node_id] for node_id in base.CORE_NODE_IDS) / len(base.CORE_NODE_IDS))

    knee_term = base._gauss(response_knee, 0.58, 0.07)
    gain_term = base._gauss(control_gain, 1.85, 0.35)
    floor_term = base._gauss(release_floor, 0.22, 0.05)
    period_term = base._gauss(float(state.oscillation_period), 5.0, 1.2)
    amplitude_term = base._gauss(state.oscillation_amplitude, 0.09, 0.022)
    quality = 0.45 * knee_term + 0.35 * gain_term + 0.20 * floor_term
    gate_quality = 0.60 * period_term + 0.40 * amplitude_term

    if bias == 'frontier_first':
        bias_org = 0.007 * state.bias_strength
        bias_clamp = 0.005 * state.bias_strength
    elif bias == 'uniform':
        bias_org = -0.001
        bias_clamp = 0.001
    else:
        bias_org = -0.009 * state.bias_strength
        bias_clamp = -0.005 * state.bias_strength

    phase_org = -0.004 if state.phase_offset == 'release_first' else 0.0
    phase_clamp = -0.003 if state.phase_offset == 'release_first' else 0.0
    duty_penalty_org = 0.025 * abs(state.gate_duty_cycle - 0.60)
    duty_penalty_clamp = 0.018 * abs(state.gate_duty_cycle - 0.60)
    shape_penalty_org = 0.020 * abs(state.curve_power - 1.0) + 0.010 * abs(state.release_blend - 0.55)
    shape_penalty_clamp = 0.012 * abs(state.saturation_steepness - 1.80) + 0.008 * abs(state.release_blend - 0.55)
    shape_bonus_org = 0.006 * max(0.0, 1.0 - abs(state.curve_power - 0.95) / 0.10)
    shape_bonus_clamp = 0.005 * max(0.0, 1.0 - abs(state.saturation_steepness - 1.60) / 0.40)

    organic = sum(organic_history) / len(organic_history)
    organic -= 0.085 * (1.0 - quality)
    organic -= 0.050 * (1.0 - gate_quality)
    organic -= duty_penalty_org + shape_penalty_org
    organic += bias_org + phase_org + shape_bonus_org

    clamp = sum(clamp_history) / len(clamp_history)
    clamp += 0.045 * (quality - 0.35)
    clamp += 0.030 * (gate_quality - 0.35)
    clamp -= duty_penalty_clamp + shape_penalty_clamp
    clamp += bias_clamp + phase_clamp + shape_bonus_clamp

    oscillator_duration = 8.0 + 0.9 * (state.oscillation_period - 4) + 14.0 * abs(state.oscillation_amplitude - 0.09)
    oscillator_duration += 3.0 * abs(state.gate_duty_cycle - 0.60)
    oscillator_duration += 2.0 * abs(state.curve_power - 1.0)
    if state.phase_offset == 'release_first':
        oscillator_duration += 0.6
    duration = max(int(waggle_metrics['intervention_duration_epochs']), int(round(oscillator_duration))) + 1

    oscillator_cost = 0.20 + 0.008 * state.oscillation_period + 0.18 * state.oscillation_amplitude
    oscillator_cost += 0.020 * abs(state.gate_duty_cycle - 0.60)
    oscillator_cost += 0.018 * abs(state.recruitment_strength - 1.0)
    oscillator_cost += 0.016 * abs(state.abandonment_rate - 1.0)
    oscillator_cost += 0.014 * abs(state.adjacency_scale - 1.0)
    oscillator_cost += 0.012 * abs(state.bias_strength - 1.0)
    oscillator_cost += 0.010 * abs(state.curve_power - 1.0)
    oscillator_cost += 0.008 * abs(state.saturation_steepness - 1.8)
    oscillator_cost += 0.008 * abs(state.release_blend - 0.55)
    cost = max(float(waggle_metrics['intervention_cost_units']), oscillator_cost) + 0.012
    if state.phase_offset == 'release_first':
        cost += 0.006

    frontier_mean = sum(frontier_state_history) / len(frontier_state_history)
    core_mean = sum(core_state_history) / len(core_state_history)

    return waggle_source_module, {
        'organic_ecu_production_rate': round(_clamp01(organic), 3),
        'pe_clamp_respect_rate': round(_clamp01(clamp), 3),
        'intervention_duration_epochs': duration,
        'intervention_cost_units': round(cost, 3),
        'frontier_mean_enforcement': round(frontier_mean, 3),
        'core_mean_enforcement': round(core_mean, 3),
        'frontier_core_gradient': round(frontier_mean - core_mean, 3),
    }


def _evaluate_state(
    state: ShapeHybridState,
    waggle_candidates: dict[str, tuple[str, dict[str, float | int], dict[str, float | int]]],
    ranked_waggle_ids: list[str],
) -> ShapeHybridEstimate:
    anchor = oscillator_module.evaluate_recovery_rule('mixed_queue_and_production')
    tuned = oscillator_module.evaluate_recovery_rule('oscillating_production_band_tuned_period')
    best_waggle_id = ranked_waggle_ids[0]
    best_waggle_metrics = waggle_candidates[best_waggle_id][2]

    waggle_source_module, metrics = simulate_shape_hybrid(state, waggle_candidates)
    (
        org_gap_anchor,
        clamp_gap_anchor,
        org_gap_tuned,
        clamp_gap_tuned,
        org_gap_waggle,
        clamp_gap_waggle,
        org_slack,
        clamp_slack,
        threshold_slack,
        score,
    ) = base._score_candidate(
        metrics,
        float(anchor['organic_ecu_production_rate']),
        float(anchor['pe_clamp_respect_rate']),
        float(tuned['organic_ecu_production_rate']),
        float(tuned['pe_clamp_respect_rate']),
        float(best_waggle_metrics['organic_ecu_production_rate']),
        float(best_waggle_metrics['pe_clamp_respect_rate']),
        int(tuned['intervention_duration_epochs']),
        float(tuned['intervention_cost_units']),
    )

    return ShapeHybridEstimate(
        generation=state.generation,
        waggle_candidate_id=state.waggle_candidate_id,
        waggle_source_module=waggle_source_module,
        oscillation_period=state.oscillation_period,
        oscillation_amplitude=state.oscillation_amplitude,
        phase_offset=state.phase_offset,
        recruitment_strength=state.recruitment_strength,
        abandonment_rate=state.abandonment_rate,
        gate_duty_cycle=state.gate_duty_cycle,
        bias_strength=state.bias_strength,
        adjacency_scale=state.adjacency_scale,
        curve_power=state.curve_power,
        saturation_steepness=state.saturation_steepness,
        release_blend=state.release_blend,
        organic_ecu_production_rate=float(metrics['organic_ecu_production_rate']),
        pe_clamp_respect_rate=float(metrics['pe_clamp_respect_rate']),
        intervention_duration_epochs=int(metrics['intervention_duration_epochs']),
        intervention_cost_units=float(metrics['intervention_cost_units']),
        frontier_mean_enforcement=float(metrics['frontier_mean_enforcement']),
        core_mean_enforcement=float(metrics['core_mean_enforcement']),
        frontier_core_gradient=float(metrics['frontier_core_gradient']),
        organic_gap_vs_anchor=round(org_gap_anchor, 3),
        clamp_gap_vs_anchor=round(clamp_gap_anchor, 3),
        organic_gap_vs_tuned_oscillator=round(org_gap_tuned, 3),
        clamp_gap_vs_tuned_oscillator=round(clamp_gap_tuned, 3),
        organic_gap_vs_best_waggle=round(org_gap_waggle, 3),
        clamp_gap_vs_best_waggle=round(clamp_gap_waggle, 3),
        organic_slack_vs_threshold=round(org_slack, 3),
        clamp_slack_vs_threshold=round(clamp_slack, 3),
        threshold_slack=round(threshold_slack, 3),
        score=score,
    )


def _state_key(state: ShapeHybridState) -> tuple[int, ...] | tuple[str, ...]:
    return (
        state.waggle_candidate_id,
        state.oscillation_period,
        int(round(state.oscillation_amplitude * 100)),
        state.phase_offset,
        int(round(state.recruitment_strength * 100)),
        int(round(state.abandonment_rate * 100)),
        int(round(state.gate_duty_cycle * 100)),
        int(round(state.bias_strength * 100)),
        int(round(state.adjacency_scale * 100)),
        int(round(state.curve_power * 100)),
        int(round(state.saturation_steepness * 100)),
        int(round(state.release_blend * 100)),
    )


def _mutate_state(state: ShapeHybridState, ranked_waggle_ids: list[str]) -> list[ShapeHybridState]:
    mutations: list[ShapeHybridState] = []
    rank_index = ranked_waggle_ids.index(state.waggle_candidate_id)

    def push(**kwargs: float | int | str) -> None:
        mutations.append(
            ShapeHybridState(
                waggle_candidate_id=str(kwargs.get('waggle_candidate_id', state.waggle_candidate_id)),
                oscillation_period=int(kwargs.get('oscillation_period', state.oscillation_period)),
                oscillation_amplitude=float(kwargs.get('oscillation_amplitude', state.oscillation_amplitude)),
                phase_offset=str(kwargs.get('phase_offset', state.phase_offset)),
                recruitment_strength=float(kwargs.get('recruitment_strength', state.recruitment_strength)),
                abandonment_rate=float(kwargs.get('abandonment_rate', state.abandonment_rate)),
                gate_duty_cycle=float(kwargs.get('gate_duty_cycle', state.gate_duty_cycle)),
                bias_strength=float(kwargs.get('bias_strength', state.bias_strength)),
                adjacency_scale=float(kwargs.get('adjacency_scale', state.adjacency_scale)),
                curve_power=float(kwargs.get('curve_power', state.curve_power)),
                saturation_steepness=float(kwargs.get('saturation_steepness', state.saturation_steepness)),
                release_blend=float(kwargs.get('release_blend', state.release_blend)),
                generation=state.generation + 1,
            )
        )

    for delta in (-1, 1):
        period = state.oscillation_period + delta
        if 2 <= period <= 8:
            push(oscillation_period=period)

    for delta in (-0.01, 0.01):
        amplitude = round(state.oscillation_amplitude + delta, 2)
        if 0.04 <= amplitude <= 0.12:
            push(oscillation_amplitude=amplitude)

    push(phase_offset='release_first' if state.phase_offset == 'enforce_first' else 'enforce_first')

    for delta in (-0.05, 0.05):
        value = round(state.recruitment_strength + delta, 2)
        if 0.85 <= value <= 1.25:
            push(recruitment_strength=value)

    for delta in (-0.05, 0.05):
        value = round(state.abandonment_rate + delta, 2)
        if 0.85 <= value <= 1.20:
            push(abandonment_rate=value)

    for delta in (-0.05, 0.05):
        value = round(state.gate_duty_cycle + delta, 2)
        if 0.35 <= value <= 0.70:
            push(gate_duty_cycle=value)

    for delta in (-0.10, 0.10):
        value = round(state.bias_strength + delta, 2)
        if 0.50 <= value <= 1.50:
            push(bias_strength=value)

    for delta in (-0.10, 0.10):
        value = round(state.adjacency_scale + delta, 2)
        if 0.70 <= value <= 1.30:
            push(adjacency_scale=value)

    for delta in (-0.05, 0.05):
        value = round(state.curve_power + delta, 2)
        if 0.85 <= value <= 1.20:
            push(curve_power=value)

    for delta in (-0.20, 0.20):
        value = round(state.saturation_steepness + delta, 2)
        if 1.20 <= value <= 2.40:
            push(saturation_steepness=value)

    for delta in (-0.05, 0.05):
        value = round(state.release_blend + delta, 2)
        if 0.35 <= value <= 0.75:
            push(release_blend=value)

    for delta in (-5, -2, -1, 1, 2, 5):
        next_index = rank_index + delta
        if 0 <= next_index < len(ranked_waggle_ids):
            push(waggle_candidate_id=ranked_waggle_ids[next_index])

    return mutations


def run_search(generations: int = 6, beam_width: int = 14) -> tuple[list[ShapeHybridEstimate], list[dict[str, object]]]:
    waggle_candidates = base._load_waggle_candidates()
    ranked_waggle_ids = sorted(
        waggle_candidates,
        key=lambda candidate_id: (
            float(waggle_candidates[candidate_id][2]['organic_ecu_production_rate']),
            float(waggle_candidates[candidate_id][2]['pe_clamp_respect_rate']),
            -float(waggle_candidates[candidate_id][2]['intervention_cost_units']),
        ),
        reverse=True,
    )

    frontier = [
        ShapeHybridState('nonlinear_curve_k58_g18_f22_frontier_first', 5, 0.09, 'enforce_first', 1.00, 1.00, 0.60, 1.40, 0.90, 1.00, 1.80, 0.55, 0),
        ShapeHybridState('nonlinear_curve_k58_g18_f22_frontier_first', 5, 0.09, 'enforce_first', 1.00, 1.00, 0.60, 1.40, 0.90, 0.95, 1.60, 0.50, 0),
        ShapeHybridState('nonlinear_curve_k58_g18_f22_frontier_first', 5, 0.09, 'enforce_first', 1.00, 1.00, 0.60, 1.30, 0.90, 1.05, 2.00, 0.60, 0),
        ShapeHybridState('nonlinear_curve_k56_g18_f22_frontier_first', 5, 0.09, 'enforce_first', 1.00, 1.00, 0.60, 1.40, 0.90, 1.00, 1.80, 0.55, 0),
        ShapeHybridState('nonlinear_curve_k60_g18_f22_frontier_first', 5, 0.09, 'enforce_first', 1.00, 1.00, 0.60, 1.40, 0.90, 1.00, 1.80, 0.55, 0),
        ShapeHybridState('nonlinear_curve_k58_g18_f22_uniform', 5, 0.09, 'enforce_first', 1.00, 1.00, 0.60, 1.00, 0.90, 1.00, 1.80, 0.55, 0),
        ShapeHybridState('nonlinear_curve_k20_g18_f22_frontier_first', 4, 0.08, 'enforce_first', 1.00, 1.00, 0.55, 1.10, 1.00, 1.00, 1.80, 0.55, 0),
    ]

    seen: dict[tuple[int, ...] | tuple[str, ...], ShapeHybridEstimate] = {}
    generation_summaries: list[dict[str, object]] = []

    for generation in range(generations):
        candidates: list[ShapeHybridState] = []
        for item in frontier:
            candidates.append(item)
            candidates.extend(_mutate_state(item, ranked_waggle_ids))

        unique_candidates: dict[tuple[int, ...] | tuple[str, ...], ShapeHybridState] = {}
        for item in candidates:
            item = ShapeHybridState(
                waggle_candidate_id=item.waggle_candidate_id,
                oscillation_period=item.oscillation_period,
                oscillation_amplitude=item.oscillation_amplitude,
                phase_offset=item.phase_offset,
                recruitment_strength=item.recruitment_strength,
                abandonment_rate=item.abandonment_rate,
                gate_duty_cycle=item.gate_duty_cycle,
                bias_strength=item.bias_strength,
                adjacency_scale=item.adjacency_scale,
                curve_power=item.curve_power,
                saturation_steepness=item.saturation_steepness,
                release_blend=item.release_blend,
                generation=generation,
            )
            unique_candidates.setdefault(_state_key(item), item)

        estimates = [_evaluate_state(item, waggle_candidates, ranked_waggle_ids) for item in unique_candidates.values()]
        estimates.sort(key=lambda item: (item.threshold_slack, item.score), reverse=True)

        for estimate in estimates:
            seen.setdefault(_state_key(
                ShapeHybridState(
                    waggle_candidate_id=estimate.waggle_candidate_id,
                    oscillation_period=estimate.oscillation_period,
                    oscillation_amplitude=estimate.oscillation_amplitude,
                    phase_offset=estimate.phase_offset,
                    recruitment_strength=estimate.recruitment_strength,
                    abandonment_rate=estimate.abandonment_rate,
                    gate_duty_cycle=estimate.gate_duty_cycle,
                    bias_strength=estimate.bias_strength,
                    adjacency_scale=estimate.adjacency_scale,
                    curve_power=estimate.curve_power,
                    saturation_steepness=estimate.saturation_steepness,
                    release_blend=estimate.release_blend,
                    generation=estimate.generation,
                )
            ), estimate)

        generation_summaries.append({'generation': generation, 'evaluated_candidates': len(estimates), 'leader': asdict(estimates[0])})

        frontier = [
            ShapeHybridState(
                waggle_candidate_id=estimate.waggle_candidate_id,
                oscillation_period=estimate.oscillation_period,
                oscillation_amplitude=estimate.oscillation_amplitude,
                phase_offset=estimate.phase_offset,
                recruitment_strength=estimate.recruitment_strength,
                abandonment_rate=estimate.abandonment_rate,
                gate_duty_cycle=estimate.gate_duty_cycle,
                bias_strength=estimate.bias_strength,
                adjacency_scale=estimate.adjacency_scale,
                curve_power=estimate.curve_power,
                saturation_steepness=estimate.saturation_steepness,
                release_blend=estimate.release_blend,
                generation=generation + 1,
            )
            for estimate in estimates[:beam_width]
        ]

    all_estimates = list(seen.values())
    all_estimates.sort(key=lambda item: (item.threshold_slack, item.score), reverse=True)
    return all_estimates, generation_summaries


def _write_outputs(estimates: Iterable[ShapeHybridEstimate], generation_summaries: list[dict[str, object]]) -> None:
    estimates = list(estimates)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    payload = {
        'method': 'Strike Path: Graph-Indexed Waggle-Oscillator Shape Search',
        'shape_variables': ['curve_power', 'saturation_steepness', 'release_blend'],
        'generations': generation_summaries,
        'top_12': [asdict(item) for item in estimates[:12]],
    }
    (OUTPUT_DIR / 'leaderboard.json').write_text(json.dumps(payload, indent=2) + '\n', encoding='utf-8')

    lines = [
        '# Strike Path Graph-Indexed Waggle-Oscillator Shape Search',
        '',
        'Method: graph-indexed hybrid search with response-curve-shape variables exposed.',
        '',
        '| Rank | Gen | Waggle candidate | Oscillator | Power | Saturation | Release blend | Org | Clamp | Gradient | Org delta vs tuned osc | Clamp delta vs tuned osc | Slack | Duration | Cost |',
        '| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |',
    ]
    for rank, item in enumerate(estimates[:12], start=1):
        oscillator_label = f'p{item.oscillation_period}_a{int(round(item.oscillation_amplitude * 100)):02d}_{item.phase_offset}'
        lines.append(
            f'| {rank} | {item.generation} | `{item.waggle_candidate_id}` | `{oscillator_label}` | '
            f'{item.curve_power:.2f} | {item.saturation_steepness:.2f} | {item.release_blend:.2f} | '
            f'{item.organic_ecu_production_rate:.3f} | {item.pe_clamp_respect_rate:.3f} | {item.frontier_core_gradient:.3f} | '
            f'{item.organic_gap_vs_tuned_oscillator:.3f} | {item.clamp_gap_vs_tuned_oscillator:.3f} | '
            f'{item.threshold_slack:.3f} | {item.intervention_duration_epochs} | {item.intervention_cost_units:.3f} |'
        )
    (OUTPUT_DIR / 'leaderboard.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')


def main() -> int:
    estimates, generation_summaries = run_search()
    _write_outputs(estimates, generation_summaries)
    leader = estimates[0]
    print('Strike Path: Graph-Indexed Waggle-Oscillator Shape Search')
    print(f'Best candidate: {leader.waggle_candidate_id}')
    print(
        'Best oscillator gate: '
        f'period={leader.oscillation_period}, amplitude={leader.oscillation_amplitude:.2f}, phase_offset={leader.phase_offset}'
    )
    print(
        'Best shape variables: '
        f'curve_power={leader.curve_power:.2f}, saturation={leader.saturation_steepness:.2f}, release_blend={leader.release_blend:.2f}'
    )
    print(
        'Projected metrics: '
        f'org={leader.organic_ecu_production_rate:.3f}, clamp={leader.pe_clamp_respect_rate:.3f}, '
        f'duration={leader.intervention_duration_epochs}, cost={leader.intervention_cost_units:.3f}'
    )
    print(
        'Projected deltas: '
        f'vs tuned oscillator org={leader.organic_gap_vs_tuned_oscillator:.3f}, '
        f'clamp={leader.clamp_gap_vs_tuned_oscillator:.3f}; slack={leader.threshold_slack:.3f}'
    )
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
