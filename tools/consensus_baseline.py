#!/usr/bin/env python3
"""Consensus-only runtime baseline.

Runs only the four consensus measurements (quorum-record generation,
epoch-state generation, finality evaluation, fork resolution) without
requiring FastAPI, ILCNodeV0, or any other full-stack dependency.

This is a standalone alternative to ``runtime_baseline.py`` for
environments that only have the consensus runtime installed.  The
measurement functions here are intentionally duplicated from
``runtime_baseline.py`` so that this script has no dependency on it.
The Phase 446 test contract requires that ``runtime_baseline.py``
remains unchanged; this script provides the consensus-only entry point
without disturbing that contract.

Output format mirrors the ``consensus`` sub-report in ``runtime_baseline.py``
but is written to ``out/consensus_baseline/`` by default.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ilc_core.consensus.epoch_state_runtime import (
    canonical_epoch_state_vectors,
    generate_epoch_state_record,
    generate_quorum_record,
)
from ilc_core.consensus.finality_evaluator import (
    evaluate_epoch_finality,
    resolve_fork,
)


CONSENSUS_BUDGETS_MS = {
    "quorum_record_generation_ms": 10.0,
    "epoch_state_generation_ms": 10.0,
    "finality_evaluation_ms": 10.0,
    "fork_resolution_ms": 10.0,
}


def _measure_ms(iterations: int, fn: Callable[[], Any]) -> dict[str, Any]:
    samples_ms: list[float] = []
    for _ in range(iterations):
        start = time.perf_counter()
        fn()
        elapsed_ms = (time.perf_counter() - start) * 1000.0
        samples_ms.append(elapsed_ms)

    return {
        "iterations": iterations,
        "min_ms": round(min(samples_ms), 3),
        "max_ms": round(max(samples_ms), 3),
        "avg_ms": round(sum(samples_ms) / len(samples_ms), 3),
        "samples_ms": [round(sample, 3) for sample in samples_ms],
    }


def _consensus_quorum_record_measurement(iterations: int) -> dict[str, Any]:
    vector = canonical_epoch_state_vectors()[0]
    raw_record = vector["quorum_records"][0]

    def _run() -> None:
        record = generate_quorum_record(raw_record)
        assert record["record_digest"]

    return _measure_ms(iterations, _run)


def _consensus_epoch_state_measurement(iterations: int) -> dict[str, Any]:
    vector = canonical_epoch_state_vectors()[0]
    raw_state = vector["epoch_state"]

    def _run() -> None:
        state = generate_epoch_state_record(raw_state)
        assert state["state_digest"]

    return _measure_ms(iterations, _run)


def _consensus_finality_measurement(iterations: int) -> dict[str, Any]:
    vector = canonical_epoch_state_vectors()[1]
    quorum_records = vector["quorum_records"]
    quorum_threshold = vector["epoch_state"]["quorum_threshold"]

    def _run() -> None:
        result = evaluate_epoch_finality(quorum_records, quorum_threshold)
        assert result["finality_status"] == "conflict"

    return _measure_ms(iterations, _run)


def _consensus_fork_resolution_measurement(iterations: int) -> dict[str, Any]:
    vector = canonical_epoch_state_vectors()[1]
    base_state = dict(vector["epoch_state"])
    candidate_a = generate_epoch_state_record(base_state)

    competing_state = dict(base_state)
    competing_state["candidate_block_hash"] = "block-gamma"
    competing_state["quorum_record_digests"] = sorted(
        {f"{digest}-alt" for digest in base_state["quorum_record_digests"]}
    )
    candidate_b = generate_epoch_state_record(competing_state)

    def _run() -> None:
        result = resolve_fork([candidate_a, candidate_b])
        assert result["selected_state_digest"] in {
            candidate_a["state_digest"],
            candidate_b["state_digest"],
        }

    return _measure_ms(iterations, _run)


def build_consensus_baseline_section(iterations: int) -> dict[str, Any]:
    """Return the consensus baseline section dict.

    Identical contract to ``runtime_baseline.build_consensus_baseline_section``.
    """
    measurements = {
        "quorum_record_generation_ms": _consensus_quorum_record_measurement(iterations),
        "epoch_state_generation_ms": _consensus_epoch_state_measurement(iterations),
        "finality_evaluation_ms": _consensus_finality_measurement(iterations),
        "fork_resolution_ms": _consensus_fork_resolution_measurement(iterations),
    }

    budgets = {}
    for key, budget_ms in CONSENSUS_BUDGETS_MS.items():
        budgets[key] = {
            "budget_ms": budget_ms,
            "observed_avg_ms": measurements[key]["avg_ms"],
            "within_budget": measurements[key]["avg_ms"] <= budget_ms,
        }

    return {
        "budgets": budgets,
        "measurements": measurements,
    }


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Consensus-only runtime baseline (no FastAPI / full-stack dependencies)."
    )
    parser.add_argument(
        "--iterations", type=int, default=5, help="Iterations per measurement."
    )
    parser.add_argument(
        "--report-path",
        default="out/consensus_baseline/report.json",
        help="Path to write the JSON report.",
    )
    parser.add_argument(
        "--enforce-budgets",
        action="store_true",
        help="Exit non-zero if any observed average exceeds its budget.",
    )
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    section = build_consensus_baseline_section(args.iterations)

    report = {
        "tool": "consensus_baseline.py",
        "iterations": args.iterations,
        **section,
    }

    report_path = Path(args.report_path)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, indent=2, sort_keys=True))

    if args.enforce_budgets and not all(
        item["within_budget"] for item in report["budgets"].values()
    ):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
