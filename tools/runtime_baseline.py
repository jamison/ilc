#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
"""Measure small runtime baselines for local ILC execution paths."""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
import time
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ilc_core.epoch.epoch_snapshot_runtime import (
    canonical_epoch_snapshot_vectors,
    generate_epoch_snapshot,
    verify_epoch_snapshot,
)
from ilc_core.consensus.epoch_state_runtime import (
    canonical_epoch_state_vectors,
    generate_epoch_state_record,
    generate_quorum_record,
)
from ilc_core.consensus.finality_evaluator import (
    evaluate_epoch_finality,
    resolve_fork,
)
from ilc_core.network.peer import PeerManager


DEFAULT_BUDGETS_MS = {
    "protocol_claim_ingest_ms": 50.0,
    "peer_fanout_ms": 50.0,
    "epoch_snapshot_roundtrip_ms": 25.0,
    "event_export_ms": 100.0,
}

CONSENSUS_BUDGETS_MS = {
    "quorum_record_generation_ms": 10.0,
    "epoch_state_generation_ms": 10.0,
    "finality_evaluation_ms": 10.0,
    "fork_resolution_ms": 10.0,
}


class _Response:
    def __init__(self, status_code: int = 202) -> None:
        self.status_code = status_code
        self.ok = 200 <= status_code < 300


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


def _claim_ingest_measurement(iterations: int) -> dict[str, Any]:
    # Keep server and FastAPI imports local so the consensus-only baseline
    # section can be imported in environments without these dependencies.
    from ilc_core.server import create_app
    from fastapi.testclient import TestClient

    app = create_app()
    with TestClient(app) as client:
        client.get("/")

        def _run() -> None:
            payload = {
                "agent_id": "agent:baseline",
                "content": f"baseline-claim-{time.time_ns()}",
                "parent_ids": ["axiom:math:01"],
                "net_stake": 1.0,
            }
            response = client.post("/v1/protocol/claim", json=payload)
            assert response.status_code == 200

        return _measure_ms(iterations, _run)


def _peer_fanout_measurement(iterations: int, fanout_peers: int) -> dict[str, Any]:
    manager = PeerManager(
        local_port=8000,
        fanout_limit=fanout_peers,
        request_timeout_s=0.1,
        sender=lambda url, payload, timeout_s: _Response(202),
    )
    for index in range(fanout_peers):
        manager.add_peer(f"10.1.0.{index + 1}", 8100 + index)

    def _run() -> None:
        result = manager.broadcast("/gossip/receive", {"id": f"node-{time.time_ns()}"})
        assert result["attempted"] == fanout_peers
        assert result["failed"] == 0

    summary = _measure_ms(iterations, _run)
    attempts = iterations * fanout_peers
    total_seconds = max(sum(summary["samples_ms"]) / 1000.0, 1e-9)
    summary["deliveries_per_second"] = round(attempts / total_seconds, 3)
    summary["fanout_peers"] = fanout_peers
    return summary


def _epoch_snapshot_measurement(iterations: int) -> dict[str, Any]:
    vector = canonical_epoch_snapshot_vectors()[0]

    def _run() -> None:
        snapshot_record = generate_epoch_snapshot(vector)
        verified = verify_epoch_snapshot(snapshot_record)
        assert verified["valid"] is True

    return _measure_ms(iterations, _run)


def _event_export_measurement(iterations: int) -> dict[str, Any]:
    # Keep node import local so the consensus-only baseline section can be
    # imported in environments without the full protocol stack.
    from ilc_core.node.node_v0 import ILCNodeV0

    def _run() -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            node = ILCNodeV0(node_id="baseline-node", data_dir=tmp_path / "data")
            for index in range(25):
                node.record_claim(
                    {"id": f"claim-{index}", "agent_id": "agent:baseline", "content": f"claim-{index}"}
                )
                node.record_refutation(
                    {
                        "id": f"refute-{index}",
                        "target_id": f"claim-{index}",
                        "agent_id": "agent:baseline",
                    }
                )
            node.record_epoch_summary({"epoch": 1, "total_tasks": 50})
            node.export_event_log_csv(
                tasks_csv_path=tmp_path / "out" / "tasks.csv",
                epochs_csv_path=tmp_path / "out" / "epochs.csv",
                claims_csv_path=tmp_path / "out" / "claims.csv",
            )

    return _measure_ms(iterations, _run)


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


def build_runtime_baseline_report(iterations: int, fanout_peers: int) -> dict[str, Any]:
    measurements = {
        "protocol_claim_ingest_ms": _claim_ingest_measurement(iterations),
        "peer_fanout_ms": _peer_fanout_measurement(iterations, fanout_peers),
        "epoch_snapshot_roundtrip_ms": _epoch_snapshot_measurement(iterations),
        "event_export_ms": _event_export_measurement(iterations),
    }

    budgets = {}
    for key, budget_ms in DEFAULT_BUDGETS_MS.items():
        budgets[key] = {
            "budget_ms": budget_ms,
            "observed_avg_ms": measurements[key]["avg_ms"],
            "within_budget": measurements[key]["avg_ms"] <= budget_ms,
        }

    consensus = build_consensus_baseline_section(iterations)

    return {
        "tool": "runtime_baseline.py",
        "iterations": iterations,
        "fanout_peers": fanout_peers,
        "budgets": budgets,
        "measurements": measurements,
        "consensus": consensus,
    }


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Measure local ILC runtime baselines.")
    parser.add_argument("--iterations", type=int, default=5, help="Iterations per measurement.")
    parser.add_argument("--fanout-peers", type=int, default=3, help="Peer fanout size for fanout measurement.")
    parser.add_argument(
        "--report-path",
        default="out/runtime_baseline/report.json",
        help="Path to write the JSON report.",
    )
    parser.add_argument(
        "--enforce-budgets",
        action="store_true",
        help="Exit non-zero if any observed average exceeds its default budget.",
    )
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    report = build_runtime_baseline_report(args.iterations, args.fanout_peers)

    report_path = Path(args.report_path)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))

    all_budget_results = list(report["budgets"].values()) + list(report["consensus"]["budgets"].values())
    if args.enforce_budgets and not all(item["within_budget"] for item in all_budget_results):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
