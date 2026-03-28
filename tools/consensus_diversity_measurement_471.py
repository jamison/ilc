from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ilc_core.consensus.finality_evaluator import (
    DIVERSITY_AWARE_FINALITY_VERSION,
    FINALITY_EVALUATOR_VERSION,
    evaluate_epoch_finality,
    evaluate_epoch_finality_with_diversity,
)
from ilc_core.consensus.epoch_state_runtime import canonical_epoch_state_vectors

REPORT_PATH = Path(os.environ.get('ILC_PHASE_471_REPORT_PATH', 'out/consensus_measurement/phase_471_report.json'))
SUMMARY_PATH = Path(os.environ.get('ILC_PHASE_471_SUMMARY_PATH', 'out/consensus_measurement/phase_471_summary.md'))
ITERATIONS = 200


def _scenario_payloads() -> list[dict[str, object]]:
    vector0 = canonical_epoch_state_vectors()[0]
    base_records = [dict(item) for item in vector0['quorum_records']]
    for index, record in enumerate(base_records, start=1):
        record['validator_id'] = f'validator-{index}'
    return [
        {
            'scenario_name': 'local_nominal',
            'records': base_records,
            'threshold': {'numerator': 2, 'denominator': 3},
            'clusters': {'validator-1': 'cluster-a', 'validator-2': 'cluster-b'},
            'policy': {'distinct_cluster_floor': 2, 'max_cluster_share_ceiling': 0.60},
        },
        {
            'scenario_name': 'degraded_latency',
            'records': base_records,
            'threshold': {'numerator': 2, 'denominator': 3},
            'clusters': {'validator-1': 'cluster-a', 'validator-2': 'cluster-b'},
            'policy': {'distinct_cluster_floor': 2, 'max_cluster_share_ceiling': 0.60},
        },
        {
            'scenario_name': 'cross_cluster_loss',
            'records': [base_records[0]],
            'threshold': {'numerator': 2, 'denominator': 3},
            'clusters': {'validator-1': 'cluster-a'},
            'policy': {'distinct_cluster_floor': 1, 'max_cluster_share_ceiling': 1.00},
        },
        {
            'scenario_name': 'concentration_edge',
            'records': [
                {
                    'block_hash': 'block-delta',
                    'epoch_index': 21,
                    'vote_weight': 0.40,
                    'validator_id': 'validator-1',
                },
                {
                    'block_hash': 'block-delta',
                    'epoch_index': 21,
                    'vote_weight': 0.35,
                    'validator_id': 'validator-2',
                },
                {
                    'block_hash': 'block-delta',
                    'epoch_index': 21,
                    'vote_weight': 0.10,
                    'validator_id': 'validator-3',
                },
            ],
            'threshold': {'numerator': 2, 'denominator': 3},
            'clusters': {
                'validator-1': 'cluster-a',
                'validator-2': 'cluster-a',
                'validator-3': 'cluster-a',
            },
            'policy': {'distinct_cluster_floor': 2, 'max_cluster_share_ceiling': 0.60},
        },
    ]


def _measure(fn, iterations: int) -> float:
    start = time.perf_counter()
    for _ in range(iterations):
        fn()
    end = time.perf_counter()
    return round(((end - start) * 1000.0) / iterations, 6)


def build_report() -> dict[str, object]:
    scenarios: list[dict[str, object]] = []
    for payload in _scenario_payloads():
        records = payload['records']
        threshold = payload['threshold']
        clusters = payload['clusters']
        policy = payload['policy']
        legacy_result = evaluate_epoch_finality(records, threshold)
        diversity_result = evaluate_epoch_finality_with_diversity(records, threshold, clusters, policy)
        legacy_avg = _measure(lambda: evaluate_epoch_finality(records, threshold), ITERATIONS)
        diversity_avg = _measure(
            lambda: evaluate_epoch_finality_with_diversity(records, threshold, clusters, policy),
            ITERATIONS,
        )
        scenarios.append(
            {
                'scenario_name': payload['scenario_name'],
                'legacy': {
                    'finality_status': legacy_result['finality_status'],
                    'canonical_block_hash': legacy_result['canonical_block_hash'],
                },
                'diversity': {
                    'finality_status': diversity_result['finality_status'],
                    'canonical_block_hash': diversity_result['canonical_block_hash'],
                    'diversity_status': diversity_result['diversity_status'],
                    'distinct_clusters': diversity_result['distinct_clusters'],
                    'max_cluster_share': diversity_result['max_cluster_share'],
                },
                'timings_ms': {
                    'legacy_avg_ms': legacy_avg,
                    'diversity_avg_ms': diversity_avg,
                    'diversity_overhead_ms': round(diversity_avg - legacy_avg, 6),
                },
            }
        )
    return {
        'phase': 471,
        'legacy_runtime_version': FINALITY_EVALUATOR_VERSION,
        'diversity_runtime_version': DIVERSITY_AWARE_FINALITY_VERSION,
        'iterations': ITERATIONS,
        'scenarios': scenarios,
    }


def write_outputs() -> None:
    report = build_report()
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n', encoding='utf-8')

    lines = [
        '# Phase 471 Consensus Diversity Measurement Summary',
        '',
        f'- legacy runtime: `{report["legacy_runtime_version"]}`',
        f'- diversity runtime: `{report["diversity_runtime_version"]}`',
        f'- iterations: `{report["iterations"]}`',
        '',
        '| scenario | legacy status | diversity status | legacy_avg_ms | diversity_avg_ms | diversity_overhead_ms |',
        '| --- | --- | --- | ---: | ---: | ---: |',
    ]
    for scenario in report['scenarios']:
        lines.append(
            '| {scenario} | {legacy} | {diversity} | {l:.6f} | {d:.6f} | {o:.6f} |'.format(
                scenario=scenario['scenario_name'],
                legacy=scenario['legacy']['finality_status'],
                diversity=scenario['diversity']['finality_status'],
                l=scenario['timings_ms']['legacy_avg_ms'],
                d=scenario['timings_ms']['diversity_avg_ms'],
                o=scenario['timings_ms']['diversity_overhead_ms'],
            )
        )
    SUMMARY_PATH.write_text('\n'.join(lines) + '\n', encoding='utf-8')


if __name__ == '__main__':
    write_outputs()
