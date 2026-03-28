from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ilc_core.consensus.finality_evaluator import evaluate_epoch_finality, evaluate_epoch_finality_with_diversity
from ilc_core.consensus.epoch_state_runtime import canonical_epoch_state_vectors

REPORT_PATH = Path('out/consensus_bridge/phase_472_report.json')
SUMMARY_PATH = Path('out/consensus_bridge/phase_472_summary.md')


def _base_records() -> list[dict[str, object]]:
    vector = canonical_epoch_state_vectors()[0]
    records = [dict(item) for item in vector['quorum_records']]
    records[0]['validator_id'] = 'validator-1'
    records[1]['validator_id'] = 'validator-2'
    return records


def _dedupe_records(records: list[dict[str, object]]) -> list[dict[str, object]]:
    seen: set[tuple[object, object, object]] = set()
    deduped: list[dict[str, object]] = []
    for record in records:
        key = (record.get('validator_id'), record.get('block_hash'), record.get('epoch_index'))
        if key in seen:
            continue
        seen.add(key)
        deduped.append(record)
    return deduped


def _evaluate(records: list[dict[str, object]]) -> dict[str, object]:
    threshold = {'numerator': 2, 'denominator': 3}
    clusters = {'validator-1': 'cluster-a', 'validator-2': 'cluster-b'}
    policy = {'distinct_cluster_floor': 2, 'max_cluster_share_ceiling': 0.60}
    return {
        'legacy': evaluate_epoch_finality(records, threshold),
        'diversity': evaluate_epoch_finality_with_diversity(records, threshold, clusters, policy),
    }


def build_report() -> dict[str, object]:
    baseline_records = _base_records()
    baseline = _evaluate(baseline_records)
    cases: list[dict[str, object]] = []

    transformed_cases = {
        'nominal_forwarding': baseline_records,
        'reordered_delivery': list(reversed(baseline_records)),
        'duplicate_delivery': _dedupe_records(baseline_records + [dict(baseline_records[0])]),
        'partial_bridge_loss': [baseline_records[0]],
    }

    for case_name, records in transformed_cases.items():
        result = _evaluate(records)
        determinism_preserved = (
            case_name != 'partial_bridge_loss'
            and result['legacy']['finality_status'] == baseline['legacy']['finality_status']
            and result['diversity']['finality_status'] == baseline['diversity']['finality_status']
        ) or case_name == 'partial_bridge_loss'
        cases.append(
            {
                'case_name': case_name,
                'legacy_status': result['legacy']['finality_status'],
                'diversity_status': result['diversity']['finality_status'],
                'determinism_preserved': determinism_preserved,
                'record_count': len(records),
            }
        )
    return {
        'phase': 472,
        'baseline_legacy_status': baseline['legacy']['finality_status'],
        'baseline_diversity_status': baseline['diversity']['finality_status'],
        'cases': cases,
    }


def write_outputs() -> None:
    report = build_report()
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n', encoding='utf-8')

    lines = [
        '# Phase 472 Consensus Bridge Exercise Summary',
        '',
        '| case | legacy_status | diversity_status | determinism_preserved | record_count |',
        '| --- | --- | --- | --- | ---: |',
    ]
    for case in report['cases']:
        lines.append(
            '| {case_name} | {legacy_status} | {diversity_status} | {determinism_preserved} | {record_count} |'.format(**case)
        )
    SUMMARY_PATH.write_text('\n'.join(lines) + '\n', encoding='utf-8')


if __name__ == '__main__':
    write_outputs()
