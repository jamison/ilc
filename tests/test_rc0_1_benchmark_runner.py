from __future__ import annotations

import json
from pathlib import Path

from tools.testbed import run_rc0_1_benchmarks as benchmark_runner


def test_parse_graph_sizes_requires_ascending_positive_values() -> None:
    assert benchmark_runner._parse_graph_sizes("5,10,25") == [5, 10, 25]


def test_synthetic_graph_growth_emits_requested_rows() -> None:
    rows = benchmark_runner._synthetic_graph_growth([3, 5])

    assert [row["node_count"] for row in rows] == [3, 5]
    assert all(row["link_count"] >= 0 for row in rows)
    assert all(row["rss_bytes"] > 0 for row in rows)


def test_run_benchmarks_aggregates_scenario_metrics(monkeypatch, tmp_path: Path) -> None:
    hosts_path = tmp_path / "hosts.json"
    scenario_path = tmp_path / "scenario.json"
    hosts_path.write_text("{}\n", encoding="utf-8")
    scenario_path.write_text("{}\n", encoding="utf-8")

    call_index = {"value": 0}

    def _fake_run_scenario(*, scenario_path: Path, hosts_path: Path, output_root: Path) -> dict[str, object]:
        call_index["value"] += 1
        panel_ms = 10.0 * call_index["value"]
        output_root.mkdir(parents=True, exist_ok=True)
        manifest = {
            "benchmark_metrics": {
                "panel_evaluation_ms": panel_ms,
                "submission_to_panel_verdict_ms": panel_ms + 5.0,
                "submission_to_network_visibility_ms": panel_ms + 10.0,
                "agent_submission_runtime_ms": [1.0, 2.0, 3.0],
                "claim_submission_delivery_metrics": {
                    "duplicate_endpoint_delivery_ratio": 0.0,
                    "estimated_inbound_bytes_per_artifact": 512.0,
                    "endpoint_delivery_count": 14,
                    "delivery_latencies_ms": [0.5, 0.75],
                },
            },
        }
        (output_root / "scenario_manifest.json").write_text(
            json.dumps(manifest, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        return manifest

    monkeypatch.setattr(benchmark_runner.scenario_runner, "run_scenario", _fake_run_scenario)

    output_root = tmp_path / "benchmarks"
    manifest = benchmark_runner.run_benchmarks(
        scenario_path=scenario_path,
        hosts_path=hosts_path,
        output_root=output_root,
        iterations=2,
        graph_sizes=[2, 4],
    )

    assert manifest["iteration_count"] == 2
    assert manifest["panel_latency_distribution"]["count"] == 2
    assert manifest["panel_latency_distribution"]["p99_ms"] == 20.0
    assert manifest["quorum_visibility_latency_distribution"]["submission_to_panel_verdict"]["p50_ms"] == 15.0
    assert manifest["claim_transport_distribution"]["endpoint_delivery_count"]["p50_ms"] == 14.0
    assert manifest["graph_rss_growth"]["graph_sizes"] == [2, 4]
    assert (output_root / "manifest.json").is_file()
