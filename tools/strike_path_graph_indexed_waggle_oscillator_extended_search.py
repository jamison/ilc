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
from simulations import sim_treasury_scenario5_waggle_dance_recovery_rule as waggle_module
from simulations import sim_treasury_scenario5_waggle_dance_wide_field as waggle_wide_field_module

OUTPUT_DIR = Path('out/strike_path/graph_indexed_waggle_oscillator_extended_search_2026-03-27')

PRESSURE_VECTOR = (0.88, 0.82, 0.74, 0.68, 0.58, 0.52, 0.46, 0.41)
PRODUCTION_WEIGHTS = (0.75, 0.80, 0.95, 1.00, 1.15, 1.15, 1.05, 0.95)
CLAMP_WEIGHTS = (1.20, 1.15, 1.00, 0.95, 0.80, 0.75, 0.65, 0.60)
FRONTIER_NODE_IDS = (0, 1)
CORE_NODE_IDS = (4, 5)
GRAPH_EDGES = {
    0: {1: 0.35, 2: 0.65},
    1: {0: 0.35, 3: 0.65},
    2: {0: 0.45, 3: 0.25, 4: 0.30},
    3: {1: 0.45, 2: 0.25, 5: 0.30},
    4: {2: 0.35, 5: 0.30, 6: 0.35},
    5: {3: 0.35, 4: 0.30, 7: 0.35},
    6: {4: 0.55, 7: 0.45},
    7: {5: 0.55, 6: 0.45},
}


@dataclass(frozen=True)
class ExtendedHybridState:
    waggle_candidate_id: str
    oscillation_period: int
    oscillation_amplitude: float
    phase_offset: str
    recruitment_strength: float
    abandonment_rate: float
    gate_duty_cycle: float
    bias_strength: float
    adjacency_scale: float
    generation: int = 0


@dataclass(frozen=True)
class ExtendedHybridEstimate:
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


def _gauss(x: float, mu: float, sigma: float) -> float:
    return math.exp(-((x - mu) ** 2) / (2 * sigma * sigma))


def _load_waggle_candidates() -> dict[str, tuple[str, dict[str, float | int], dict[str, float | int]]]:
    candidates: dict[str, tuple[str, dict[str, float | int], dict[str, float | int]]] = {}
    for module_name, module in (
        ('fix10_surface', waggle_module),
        ('wide_field_surface', waggle_wide_field_module),
    ):
        for candidate_id in module.list_candidate_ids():
            if candidate_id == 'mixed_queue_and_production':
                continue
            definition = module.get_candidate_definition(candidate_id)
            candidates[candidate_id] = (module_name, dict(definition.parameters), dict(definition.outputs))
    return candidates


def _base_node_bias_profile(bias: str) -> tuple[float, ...]:
    if bias == 'frontier_first':
        return (1.14, 1.12, 1.03, 1.00, 0.94, 0.94, 0.88, 0.88)
    if bias == 'uniform':
        return (1.00, 1.00, 1.00, 1.00, 1.00, 1.00, 1.00, 1.00)
    return (1.10, 1.08, 1.02, 1.00, 0.94, 0.94, 0.90, 0.90)


def _scaled_bias_profile(bias: str, bias_strength: float) -> tuple[float, ...]:
    base = _base_node_bias_profile(bias)
    return tuple(1.0 + bias_strength * (value - 1.0) for value in base)


def _oscillator_gate(
    period: int,
    amplitude: float,
    phase_offset: str,
    epoch: int,
    release_floor: float,
    gate_duty_cycle: float,
) -> float:
    phase_position = epoch % period
    enforce_window = max(1, min(period - 1, int(round(period * gate_duty_cycle))))
    active = phase_position < enforce_window if phase_offset == 'enforce_first' else phase_position >= (period - enforce_window)
    high_gate = min(1.0, 0.40 + 2.6 * amplitude)
    low_gate = max(release_floor * 0.8, 0.18 - 0.75 * amplitude)
    return high_gate if active else low_gate


def simulate_graph_indexed_hybrid(
    state: ExtendedHybridState,
    waggle_candidates: dict[str, tuple[str, dict[str, float | int], dict[str, float | int]]],
) -> tuple[str, dict[str, float | int | float]]:
    waggle_source_module, waggle_parameters, waggle_metrics = waggle_candidates[state.waggle_candidate_id]

    response_knee = float(waggle_parameters['response_knee'])
    control_gain = float(waggle_parameters['control_gain'])
    release_floor = float(waggle_parameters['release_floor'])
    bias = str(waggle_parameters['bias'])
    node_bias = _scaled_bias_profile(bias, state.bias_strength)

    node_state = [release_floor * 0.6 for _ in PRESSURE_VECTOR]
    recruit_weight = (0.07 + 0.03 * _gauss(control_gain, 1.85, 0.35)) * state.recruitment_strength
    recruit_weight = _clamp_range(recruit_weight, 0.03, 0.18)
    abandonment = (0.16 + 0.05 * (1.0 - _gauss(float(state.oscillation_period), 5.0, 1.2))) * state.abandonment_rate
    abandonment = _clamp_range(abandonment, 0.08, 0.32)

    organic_history: list[float] = []
    clamp_history: list[float] = []
    frontier_state_history: list[float] = []
    core_state_history: list[float] = []

    for epoch in range(14):
        gate = _oscillator_gate(
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

        for node_id, pressure in enumerate(PRESSURE_VECTOR):
            neighbor_signal = 0.0
            for neighbor_id, edge_weight in GRAPH_EDGES[node_id].items():
                neighbor_signal += (edge_weight * state.adjacency_scale) * node_state[neighbor_id]
            local_signal = min(1.0, pressure + 0.18 * neighbor_signal)
            linear_response = max(0.0, local_signal - response_knee) * control_gain * node_bias[node_id]
            target_enforcement = release_floor * 0.55 + gate * (linear_response / (1.0 + 1.8 * linear_response))
            updated_state = (1.0 - abandonment) * node_state[node_id] + 0.40 * target_enforcement + recruit_weight * neighbor_signal
            updated_state = _clamp01(updated_state)
            next_state.append(updated_state)

            organic_node = 0.90 + 0.10 * (1.0 - 0.85 * updated_state) + 0.025 * (1.0 - gate) + 0.02 * (1.0 - pressure)
            clamp_node = 0.80 + 0.12 * updated_state + 0.025 * gate * pressure
            organic_nodes.append(_clamp01(organic_node))
            clamp_nodes.append(_clamp01(clamp_node))

        node_state = next_state
        organic_history.append(sum(value * weight for value, weight in zip(organic_nodes, PRODUCTION_WEIGHTS)) / sum(PRODUCTION_WEIGHTS))
        clamp_history.append(sum(value * weight for value, weight in zip(clamp_nodes, CLAMP_WEIGHTS)) / sum(CLAMP_WEIGHTS))
        frontier_state_history.append(sum(node_state[node_id] for node_id in FRONTIER_NODE_IDS) / len(FRONTIER_NODE_IDS))
        core_state_history.append(sum(node_state[node_id] for node_id in CORE_NODE_IDS) / len(CORE_NODE_IDS))

    knee_term = _gauss(response_knee, 0.58, 0.07)
    gain_term = _gauss(control_gain, 1.85, 0.35)
    floor_term = _gauss(release_floor, 0.22, 0.05)
    period_term = _gauss(float(state.oscillation_period), 5.0, 1.2)
    amplitude_term = _gauss(state.oscillation_amplitude, 0.09, 0.022)
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

    organic = sum(organic_history) / len(organic_history)
    organic -= 0.085 * (1.0 - quality)
    organic -= 0.050 * (1.0 - gate_quality)
    organic -= duty_penalty_org
    organic += bias_org + phase_org

    clamp = sum(clamp_history) / len(clamp_history)
    clamp += 0.045 * (quality - 0.35)
    clamp += 0.030 * (gate_quality - 0.35)
    clamp -= duty_penalty_clamp
    clamp += bias_clamp + phase_clamp

    oscillator_duration = 8.0 + 0.9 * (state.oscillation_period - 4) + 14.0 * abs(state.oscillation_amplitude - 0.09)
    oscillator_duration += 3.0 * abs(state.gate_duty_cycle - 0.60)
    if state.phase_offset == 'release_first':
        oscillator_duration += 0.6
    duration = max(int(waggle_metrics['intervention_duration_epochs']), int(round(oscillator_duration))) + 1

    oscillator_cost = 0.20 + 0.008 * state.oscillation_period + 0.18 * state.oscillation_amplitude
    oscillator_cost += 0.020 * abs(state.gate_duty_cycle - 0.60)
    oscillator_cost += 0.018 * abs(state.recruitment_strength - 1.0)
    oscillator_cost += 0.016 * abs(state.abandonment_rate - 1.0)
    oscillator_cost += 0.014 * abs(state.adjacency_scale - 1.0)
    oscillator_cost += 0.012 * abs(state.bias_strength - 1.0)
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


def _score_candidate(
    metrics: dict[str, float | int | float],
    anchor_org: float,
    anchor_clamp: float,
    tuned_org: float,
    tuned_clamp: float,
    best_waggle_org: float,
    best_waggle_clamp: float,
    baseline_duration: int,
    baseline_cost: float,
) -> tuple[float, float, float, float, float, float, float, float, float, float]:
    org_gap_anchor = float(metrics['organic_ecu_production_rate']) - anchor_org
    clamp_gap_anchor = float(metrics['pe_clamp_respect_rate']) - anchor_clamp
    org_gap_tuned = float(metrics['organic_ecu_production_rate']) - tuned_org
    clamp_gap_tuned = float(metrics['pe_clamp_respect_rate']) - tuned_clamp
    org_gap_waggle = float(metrics['organic_ecu_production_rate']) - best_waggle_org
    clamp_gap_waggle = float(metrics['pe_clamp_respect_rate']) - best_waggle_clamp
    org_slack = org_gap_anchor - 0.10
    clamp_slack = clamp_gap_anchor - 0.05
    threshold_slack = min(org_slack, clamp_slack)
    duration_penalty = float(metrics['intervention_duration_epochs']) - baseline_duration
    cost_penalty = float(metrics['intervention_cost_units']) - baseline_cost
    gradient_bonus = max(0.0, float(metrics['frontier_core_gradient'])) * 12.0
    score = threshold_slack * 100.0
    score += org_gap_anchor * 18.0 + clamp_gap_anchor * 14.0
    score += org_gap_tuned * 18.0 + clamp_gap_tuned * 16.0
    score += org_gap_waggle * 14.0 + clamp_gap_waggle * 12.0
    score += gradient_bonus
    score -= 0.9 * duration_penalty + 28.0 * cost_penalty
    return (
        org_gap_anchor,
        clamp_gap_anchor,
        org_gap_tuned,
        clamp_gap_tuned,
        org_gap_waggle,
        clamp_gap_waggle,
        org_slack,
        clamp_slack,
        threshold_slack,
        round(score, 3),
    )


def _evaluate_state(
    state: ExtendedHybridState,
    waggle_candidates: dict[str, tuple[str, dict[str, float | int], dict[str, float | int]]],
    ranked_waggle_ids: list[str],
) -> ExtendedHybridEstimate:
    anchor = oscillator_module.evaluate_recovery_rule('mixed_queue_and_production')
    tuned = oscillator_module.evaluate_recovery_rule('oscillating_production_band_tuned_period')
    best_waggle_id = ranked_waggle_ids[0]
    best_waggle_metrics = waggle_candidates[best_waggle_id][2]

    waggle_source_module, metrics = simulate_graph_indexed_hybrid(state, waggle_candidates)
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
    ) = _score_candidate(
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

    return ExtendedHybridEstimate(
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


def _state_key(state: ExtendedHybridState) -> tuple[str, int, int, str, int, int, int, int, int]:
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
    )


def _mutate_state(state: ExtendedHybridState, ranked_waggle_ids: list[str]) -> list[ExtendedHybridState]:
    mutations: list[ExtendedHybridState] = []
    rank_index = ranked_waggle_ids.index(state.waggle_candidate_id)

    def push(**kwargs: float | int | str) -> None:
        mutations.append(
            ExtendedHybridState(
                waggle_candidate_id=str(kwargs.get('waggle_candidate_id', state.waggle_candidate_id)),
                oscillation_period=int(kwargs.get('oscillation_period', state.oscillation_period)),
                oscillation_amplitude=float(kwargs.get('oscillation_amplitude', state.oscillation_amplitude)),
                phase_offset=str(kwargs.get('phase_offset', state.phase_offset)),
                recruitment_strength=float(kwargs.get('recruitment_strength', state.recruitment_strength)),
                abandonment_rate=float(kwargs.get('abandonment_rate', state.abandonment_rate)),
                gate_duty_cycle=float(kwargs.get('gate_duty_cycle', state.gate_duty_cycle)),
                bias_strength=float(kwargs.get('bias_strength', state.bias_strength)),
                adjacency_scale=float(kwargs.get('adjacency_scale', state.adjacency_scale)),
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

    for delta in (-5, -2, -1, 1, 2, 5):
        next_index = rank_index + delta
        if 0 <= next_index < len(ranked_waggle_ids):
            push(waggle_candidate_id=ranked_waggle_ids[next_index])

    return mutations


def run_search(generations: int = 6, beam_width: int = 14) -> tuple[list[ExtendedHybridEstimate], list[dict[str, object]]]:
    waggle_candidates = _load_waggle_candidates()
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
        ExtendedHybridState('nonlinear_curve_k58_g18_f22_frontier_first', 5, 0.09, 'enforce_first', 1.00, 1.00, 0.60, 1.00, 1.00, 0),
        ExtendedHybridState('nonlinear_curve_k58_g18_f22_frontier_first', 5, 0.09, 'enforce_first', 1.10, 0.95, 0.55, 1.10, 1.05, 0),
        ExtendedHybridState('nonlinear_curve_k58_g18_f22_frontier_first', 5, 0.09, 'enforce_first', 0.95, 1.05, 0.65, 0.90, 0.95, 0),
        ExtendedHybridState('nonlinear_curve_k56_g18_f22_frontier_first', 5, 0.09, 'enforce_first', 1.00, 1.00, 0.60, 1.00, 1.00, 0),
        ExtendedHybridState('nonlinear_curve_k60_g18_f22_frontier_first', 5, 0.09, 'enforce_first', 1.00, 1.00, 0.60, 1.00, 1.00, 0),
        ExtendedHybridState('nonlinear_curve_k58_g18_f22_uniform', 5, 0.09, 'enforce_first', 1.00, 1.00, 0.60, 1.00, 1.00, 0),
        ExtendedHybridState('nonlinear_curve_k58_g18_f22_backpressure_first', 5, 0.09, 'enforce_first', 1.00, 1.00, 0.60, 1.00, 1.00, 0),
        ExtendedHybridState('nonlinear_curve_k20_g18_f22_frontier_first', 4, 0.08, 'enforce_first', 1.00, 1.00, 0.55, 1.00, 1.00, 0),
        ExtendedHybridState('nonlinear_curve_k85_g35_f44_backpressure_first', 5, 0.09, 'enforce_first', 1.00, 1.00, 0.60, 1.00, 1.00, 0),
    ]

    seen: dict[tuple[str, int, int, str, int, int, int, int, int], ExtendedHybridEstimate] = {}
    generation_summaries: list[dict[str, object]] = []

    for generation in range(generations):
        candidates: list[ExtendedHybridState] = []
        for item in frontier:
            candidates.append(item)
            candidates.extend(_mutate_state(item, ranked_waggle_ids))

        unique_candidates: dict[tuple[str, int, int, str, int, int, int, int, int], ExtendedHybridState] = {}
        for item in candidates:
            item = ExtendedHybridState(
                waggle_candidate_id=item.waggle_candidate_id,
                oscillation_period=item.oscillation_period,
                oscillation_amplitude=item.oscillation_amplitude,
                phase_offset=item.phase_offset,
                recruitment_strength=item.recruitment_strength,
                abandonment_rate=item.abandonment_rate,
                gate_duty_cycle=item.gate_duty_cycle,
                bias_strength=item.bias_strength,
                adjacency_scale=item.adjacency_scale,
                generation=generation,
            )
            unique_candidates.setdefault(_state_key(item), item)

        estimates = [_evaluate_state(item, waggle_candidates, ranked_waggle_ids) for item in unique_candidates.values()]
        estimates.sort(key=lambda item: (item.threshold_slack, item.score), reverse=True)

        for estimate in estimates:
            seen.setdefault(
                (
                    estimate.waggle_candidate_id,
                    estimate.oscillation_period,
                    int(round(estimate.oscillation_amplitude * 100)),
                    estimate.phase_offset,
                    int(round(estimate.recruitment_strength * 100)),
                    int(round(estimate.abandonment_rate * 100)),
                    int(round(estimate.gate_duty_cycle * 100)),
                    int(round(estimate.bias_strength * 100)),
                    int(round(estimate.adjacency_scale * 100)),
                ),
                estimate,
            )

        generation_summaries.append(
            {
                'generation': generation,
                'evaluated_candidates': len(estimates),
                'leader': asdict(estimates[0]),
            }
        )

        frontier = [
            ExtendedHybridState(
                waggle_candidate_id=estimate.waggle_candidate_id,
                oscillation_period=estimate.oscillation_period,
                oscillation_amplitude=estimate.oscillation_amplitude,
                phase_offset=estimate.phase_offset,
                recruitment_strength=estimate.recruitment_strength,
                abandonment_rate=estimate.abandonment_rate,
                gate_duty_cycle=estimate.gate_duty_cycle,
                bias_strength=estimate.bias_strength,
                adjacency_scale=estimate.adjacency_scale,
                generation=generation + 1,
            )
            for estimate in estimates[:beam_width]
        ]

    all_estimates = list(seen.values())
    all_estimates.sort(key=lambda item: (item.threshold_slack, item.score), reverse=True)
    return all_estimates, generation_summaries


def _write_outputs(estimates: Iterable[ExtendedHybridEstimate], generation_summaries: list[dict[str, object]]) -> None:
    estimates = list(estimates)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    payload = {
        'method': 'Strike Path: Graph-Indexed Waggle-Oscillator Extended Search',
        'search_variables': [
            'response_knee',
            'control_gain',
            'release_floor',
            'bias',
            'oscillation_period',
            'oscillation_amplitude',
            'phase_offset',
            'recruitment_strength',
            'abandonment_rate',
            'gate_duty_cycle',
            'bias_strength',
            'adjacency_scale',
        ],
        'generations': generation_summaries,
        'top_12': [asdict(item) for item in estimates[:12]],
    }
    (OUTPUT_DIR / 'leaderboard.json').write_text(json.dumps(payload, indent=2) + '\n', encoding='utf-8')

    lines = [
        '# Strike Path Graph-Indexed Waggle-Oscillator Extended Search',
        '',
        'Method: explicit node-indexed propagation with extra searchable structural variables.',
        '',
        '| Rank | Gen | Waggle candidate | Oscillator | Recruit | Abandon | Duty | Bias str | Adj scale | Org | Clamp | Gradient | Org delta vs tuned osc | Clamp delta vs tuned osc | Slack | Duration | Cost |',
        '| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |',
    ]
    for rank, item in enumerate(estimates[:12], start=1):
        oscillator_label = f'p{item.oscillation_period}_a{int(round(item.oscillation_amplitude * 100)):02d}_{item.phase_offset}'
        lines.append(
            f'| {rank} | {item.generation} | `{item.waggle_candidate_id}` | `{oscillator_label}` | '
            f'{item.recruitment_strength:.2f} | {item.abandonment_rate:.2f} | {item.gate_duty_cycle:.2f} | '
            f'{item.bias_strength:.2f} | {item.adjacency_scale:.2f} | {item.organic_ecu_production_rate:.3f} | '
            f'{item.pe_clamp_respect_rate:.3f} | {item.frontier_core_gradient:.3f} | '
            f'{item.organic_gap_vs_tuned_oscillator:.3f} | {item.clamp_gap_vs_tuned_oscillator:.3f} | '
            f'{item.threshold_slack:.3f} | {item.intervention_duration_epochs} | {item.intervention_cost_units:.3f} |'
        )
    (OUTPUT_DIR / 'leaderboard.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')


def main() -> int:
    estimates, generation_summaries = run_search()
    _write_outputs(estimates, generation_summaries)
    leader = estimates[0]
    print('Strike Path: Graph-Indexed Waggle-Oscillator Extended Search')
    print(f'Best candidate: {leader.waggle_candidate_id}')
    print(
        'Best oscillator gate: '
        f'period={leader.oscillation_period}, amplitude={leader.oscillation_amplitude:.2f}, phase_offset={leader.phase_offset}'
    )
    print(
        'Best structural variables: '
        f'recruitment={leader.recruitment_strength:.2f}, abandonment={leader.abandonment_rate:.2f}, '
        f'duty={leader.gate_duty_cycle:.2f}, bias_strength={leader.bias_strength:.2f}, adjacency={leader.adjacency_scale:.2f}'
    )
    print(
        'Projected metrics: '
        f'org={leader.organic_ecu_production_rate:.3f}, clamp={leader.pe_clamp_respect_rate:.3f}, '
        f'duration={leader.intervention_duration_epochs}, cost={leader.intervention_cost_units:.3f}'
    )
    print(
        'Graph profile: '
        f'frontier_mean={leader.frontier_mean_enforcement:.3f}, core_mean={leader.core_mean_enforcement:.3f}, '
        f'gradient={leader.frontier_core_gradient:.3f}'
    )
    print(
        'Projected deltas: '
        f'vs tuned oscillator org={leader.organic_gap_vs_tuned_oscillator:.3f}, '
        f'clamp={leader.clamp_gap_vs_tuned_oscillator:.3f}; slack={leader.threshold_slack:.3f}'
    )
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
