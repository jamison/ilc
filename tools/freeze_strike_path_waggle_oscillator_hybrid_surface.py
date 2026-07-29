# SPDX-License-Identifier: AGPL-3.0-only
from __future__ import annotations

import json
import sys
from dataclasses import asdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools import strike_path_graph_indexed_waggle_oscillator_shape_search as shape_search

OUTPUT_DIR = Path('out/strike_path/waggle_oscillator_hybrid_constrained_surface_2026-03-27')


def build_candidate_id(candidate: dict[str, object]) -> str:
    return (
        f"hybrid_{candidate['waggle_candidate_id']}_"
        f"p{candidate['oscillation_period']}_"
        f"a{int(round(float(candidate['oscillation_amplitude']) * 100)):02d}_"
        f"{candidate['phase_offset']}_"
        f"rq{int(round(float(candidate['recruitment_strength']) * 100)):03d}_"
        f"ab{int(round(float(candidate['abandonment_rate']) * 100)):03d}_"
        f"dc{int(round(float(candidate['gate_duty_cycle']) * 100)):03d}_"
        f"cp{int(round(float(candidate['curve_power']) * 100)):03d}_"
        f"ss{int(round(float(candidate['saturation_steepness']) * 100)):03d}_"
        f"rb{int(round(float(candidate['release_blend']) * 100)):03d}_"
        f"bs{int(round(float(candidate['bias_strength']) * 100)):03d}_"
        f"adj{int(round(float(candidate['adjacency_scale']) * 100)):03d}"
    )


def main() -> int:
    estimates, _ = shape_search.run_search()
    frozen_field = []
    seen_candidate_ids: set[str] = set()
    for estimate in estimates:
        candidate = asdict(estimate)
        candidate_id = build_candidate_id(candidate)
        if candidate_id in seen_candidate_ids:
            continue
        seen_candidate_ids.add(candidate_id)
        frozen_field.append(
            {
                'candidate_id': candidate_id,
                'waggle_candidate_id': candidate['waggle_candidate_id'],
                'oscillator': {
                    'period': candidate['oscillation_period'],
                    'amplitude': candidate['oscillation_amplitude'],
                    'phase_offset': candidate['phase_offset'],
                },
                'structural_variables': {
                    'recruitment_strength': candidate['recruitment_strength'],
                    'abandonment_rate': candidate['abandonment_rate'],
                    'gate_duty_cycle': candidate['gate_duty_cycle'],
                    'bias_strength': candidate['bias_strength'],
                    'adjacency_scale': candidate['adjacency_scale'],
                    'curve_power': candidate['curve_power'],
                    'saturation_steepness': candidate['saturation_steepness'],
                    'release_blend': candidate['release_blend'],
                },
                'projected_metrics': {
                    'organic_ecu_production_rate': candidate['organic_ecu_production_rate'],
                    'pe_clamp_respect_rate': candidate['pe_clamp_respect_rate'],
                    'intervention_duration_epochs': candidate['intervention_duration_epochs'],
                    'intervention_cost_units': candidate['intervention_cost_units'],
                    'frontier_core_gradient': candidate['frontier_core_gradient'],
                },
            }
        )
        if len(frozen_field) == 6:
            break

    payload = {
        'method': 'Strike Path constrained hybrid surface freeze',
        'source_tool': 'tools/strike_path_graph_indexed_waggle_oscillator_shape_search.py',
        'frozen_field': frozen_field,
    }

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / 'frozen_field.json').write_text(json.dumps(payload, indent=2) + '\n', encoding='utf-8')

    lines = [
        '# Strike Path Waggle-Oscillator Hybrid Constrained Surface',
        '',
        '| Rank | Candidate | Waggle | Oscillator | Recruit | Abandon | Duty | Power | Saturation | Release blend | Bias str | Adj scale | Org | Clamp | Gradient | Duration | Cost |',
        '| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |',
    ]
    for rank, candidate in enumerate(frozen_field, start=1):
        oscillator = candidate['oscillator']
        structural = candidate['structural_variables']
        metrics = candidate['projected_metrics']
        lines.append(
            f"| {rank} | `{candidate['candidate_id']}` | `{candidate['waggle_candidate_id']}` | "
            f"`p{oscillator['period']}_a{int(round(float(oscillator['amplitude']) * 100)):02d}_{oscillator['phase_offset']}` | "
            f"{float(structural['recruitment_strength']):.2f} | {float(structural['abandonment_rate']):.2f} | "
            f"{float(structural['gate_duty_cycle']):.2f} | {float(structural['curve_power']):.2f} | {float(structural['saturation_steepness']):.2f} | "
            f"{float(structural['release_blend']):.2f} | {float(structural['bias_strength']):.2f} | "
            f"{float(structural['adjacency_scale']):.2f} | "
            f"{float(metrics['organic_ecu_production_rate']):.3f} | {float(metrics['pe_clamp_respect_rate']):.3f} | "
            f"{float(metrics['frontier_core_gradient']):.3f} | {int(metrics['intervention_duration_epochs'])} | {float(metrics['intervention_cost_units']):.3f} |"
        )
    (OUTPUT_DIR / 'frozen_field.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')

    print('Strike Path: Waggle-Oscillator Hybrid Constrained Surface')
    print(f'Frozen candidates: {len(frozen_field)}')
    print(f"Leader: {frozen_field[0]['candidate_id']}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
