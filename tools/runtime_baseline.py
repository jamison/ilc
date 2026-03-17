#!/usr/bin/env python3
"""Measure small runtime baselines for local ILC execution paths."""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
import time
from pathlib import Path
from typing import Any, Callable

from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ilc_core.epoch.epoch_snapshot_runtime import (
    canonical_epoch_snapshot_vectors,
    generate_epoch_snapshot,
    verify_epoch_snapshot,
)
from ilc_core.network.peer import PeerManager
from ilc_core.node.node_v0 import ILCNodeV0
from ilc_core.server import create_app


DEFAULT_BUDGETS_MS = {
    "protocol_claim_ingest_ms": 50.0,
    "peer_fanout_ms": 50.0,
    "epoch_snapshot_roundtrip_ms": 25.0,
    "event_export_ms": 100.0,
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

    return {
        "tool": "runtime_baseline.py",
        "iterations": iterations,
        "fanout_peers": fanout_peers,
        "budgets": budgets,
        "measurements": measurements,
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

    if args.enforce_budgets and not all(item["within_budget"] for item in report["budgets"].values()):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
