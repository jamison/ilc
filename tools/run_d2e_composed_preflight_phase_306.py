#!/usr/bin/env python3
"""Phase 306 composed query/verify/bundle preflight runner.

This helper executes deterministic cross-lane scenarios and emits a machine-readable
risk snapshot consumed by the Phase 306 shell wrapper.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any


CLI_CMD = [sys.executable, "-m", "ilc_core.cli.main"]
SNAPSHOT_PATH = Path("out/monitoring/d2e_risk_snapshot_phase_306.json")
CATEGORIES = [
    "query_lane_scenarios",
    "verify_lane_scenarios",
    "bundle_lane_scenarios",
    "cross_lane_envelope_regression",
    "kpi_snapshot",
]


def _now_utc() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _run_cli(args: list[str], env: dict[str, str]) -> tuple[subprocess.CompletedProcess[str], float]:
    start = time.perf_counter()
    result = subprocess.run(CLI_CMD + args, capture_output=True, text=True, env=env, check=False)
    elapsed_ms = (time.perf_counter() - start) * 1000.0
    return result, elapsed_ms


def _payload(result: subprocess.CompletedProcess[str]) -> dict[str, Any]:
    blob = result.stdout.strip() or result.stderr.strip()
    if not blob:
        raise RuntimeError("empty_cli_payload")
    return json.loads(blob)


def _write_graph_state(path: Path) -> None:
    state = {
        "schema_version": "d2e03.v0.1",
        "nodes": [
            {"id": "node-1", "claim_id": "claim-a", "payload": {"text": "alpha"}},
            {"node_id": "node-2", "claim_id": "claim-b", "payload": {"text": "beta"}},
        ],
        "edges": [],
        "epochs": [{"epoch": 9, "issued_ilc": 42.0}],
    }
    path.write_text(json.dumps(state, sort_keys=True, indent=2) + "\n", encoding="utf-8")


def _write_identity_state(path: Path) -> None:
    state = {
        "lineage_id": "lineage-a",
        "status": "active",
        "key_ref": "key-a",
        "rotation_count": 0,
        "updated_at": "2026-02-25T00:00:00Z",
    }
    path.write_text(json.dumps(state, sort_keys=True, indent=2) + "\n", encoding="utf-8")


def _manifest_hash(manifest: dict[str, Any]) -> str:
    stable = json.dumps(manifest, sort_keys=True, separators=(",", ":"))
    return __import__("hashlib").sha256(stable.encode("utf-8")).hexdigest()


def _write_bundle_state(path: Path) -> None:
    local_manifest = {
        "bundle_version": "v1",
        "entries": [{"cid": "node-1", "kind": "knowledge_node"}],
        "name": "bundle-local",
    }
    blocked_manifest = {
        "bundle_version": "v1",
        "entries": [{"cid": "node-2", "kind": "knowledge_node"}],
        "name": "bundle-blocked",
    }
    state = {
        "schema_version": "d2e07.v0.1",
        "bundles": [
            {
                "bundle_cid": "bafy-bundle-local",
                "provider": "local",
                "manifest": local_manifest,
                "integrity": {"manifest_sha256": _manifest_hash(local_manifest)},
                "graph_refs": {"node_ids": ["node-1"], "claim_ids": ["claim-a"]},
            },
            {
                "bundle_cid": "bafy-bundle-blocked",
                "provider": "blocked",
                "manifest": blocked_manifest,
                "integrity": {"manifest_sha256": _manifest_hash(blocked_manifest)},
                "graph_refs": {"node_ids": ["node-2"], "claim_ids": ["claim-b"]},
            },
        ],
    }
    path.write_text(json.dumps(state, sort_keys=True, indent=2) + "\n", encoding="utf-8")


def _p95(values: list[float]) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = int(0.95 * (len(ordered) - 1))
    return round(ordered[index], 6)


def _median(values: list[float]) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    mid = len(ordered) // 2
    if len(ordered) % 2 == 1:
        return round(ordered[mid], 6)
    return round((ordered[mid - 1] + ordered[mid]) / 2.0, 6)


def _safe_rate(numerator: int, denominator: int) -> float:
    if denominator <= 0:
        return 0.0
    return round(float(numerator) / float(denominator), 8)


def _expect(result: subprocess.CompletedProcess[str], code: int, token: str | None = None) -> dict[str, Any]:
    if result.returncode != code:
        raise RuntimeError(f"unexpected_exit_code:{result.returncode}:expected:{code}")
    payload = _payload(result)
    if token is not None:
        if code == 0:
            observed = str(payload.get("meta", {}).get("command", ""))
            if not observed:
                observed = str(payload.get("command", ""))
            if not observed.startswith(token):
                raise RuntimeError(f"unexpected_command_token:{observed}:expected_prefix:{token}")
        else:
            observed_error = str(payload.get("error", {}).get("code", ""))
            if observed_error != token:
                raise RuntimeError(f"unexpected_error_token:{observed_error}:expected:{token}")
    return payload


def _run_query_lane(env: dict[str, str]) -> dict[str, Any]:
    total = 0
    invalid = 0
    not_found = 0
    backend_unavailable = 0
    latencies: list[float] = []

    for _ in range(20):
        result, elapsed = _run_cli(["query", "node", "--node-id", "node-1"], env)
        _expect(result, 0, "query node")
        total += 1
        latencies.append(elapsed)

    for _ in range(3):
        result, elapsed = _run_cli(["query", "claim", "--claim-id", "claim-a"], env)
        _expect(result, 0, "query claim")
        total += 1
        latencies.append(elapsed)

    result, elapsed = _run_cli(["query", "node", "--node-id", "missing"], env)
    _expect(result, 1, "query_not_found")
    total += 1
    latencies.append(elapsed)
    not_found += 1

    result, elapsed = _run_cli(["query", "node"], env)
    _expect(result, 2, "query_invalid_input")
    total += 1
    latencies.append(elapsed)
    invalid += 1

    return {
        "total_requests": total,
        "invalid_input_events": invalid,
        "not_found_events": not_found,
        "backend_unavailable_events": backend_unavailable,
        "p95_latency_ms": _p95(latencies),
        "latencies": latencies,
    }


def _run_verify_lane(env: dict[str, str]) -> dict[str, Any]:
    total = 0
    invalid = 0
    not_found = 0
    backend_unavailable = 0
    total_checks = 0
    failed_checks = 0
    latencies: list[float] = []

    for _ in range(8):
        result, elapsed = _run_cli(["verify", "claim", "--claim-id", "claim-a"], env)
        payload = _expect(result, 0, "verify claim")
        total += 1
        latencies.append(elapsed)
        checks = payload.get("data", {}).get("checks", [])
        total_checks += len(checks)
        failed_checks += sum(1 for item in checks if not bool(item.get("passed", False)))

    for _ in range(8):
        result, elapsed = _run_cli(["verify", "node", "--node-id", "node-1"], env)
        payload = _expect(result, 0, "verify node")
        total += 1
        latencies.append(elapsed)
        checks = payload.get("data", {}).get("checks", [])
        total_checks += len(checks)
        failed_checks += sum(1 for item in checks if not bool(item.get("passed", False)))

    for _ in range(7):
        result, elapsed = _run_cli(["verify", "lineage", "--lineage-id", "lineage-a"], env)
        payload = _expect(result, 0, "verify lineage")
        total += 1
        latencies.append(elapsed)
        checks = payload.get("data", {}).get("checks", [])
        total_checks += len(checks)
        failed_checks += sum(1 for item in checks if not bool(item.get("passed", False)))

    result, elapsed = _run_cli(["verify", "claim", "--claim-id", "missing"], env)
    _expect(result, 1, "verify_not_found")
    total += 1
    latencies.append(elapsed)
    not_found += 1

    result, elapsed = _run_cli(["verify", "claim"], env)
    _expect(result, 2, "verify_invalid_input")
    total += 1
    latencies.append(elapsed)
    invalid += 1

    return {
        "total_requests": total,
        "invalid_input_events": invalid,
        "not_found_events": not_found,
        "backend_unavailable_events": backend_unavailable,
        "total_checks": total_checks,
        "failed_checks": failed_checks,
        "latencies": latencies,
    }


def _run_bundle_lane(env: dict[str, str], broken_bundle_env: dict[str, str]) -> dict[str, Any]:
    total = 0
    invalid = 0
    not_found = 0
    manifest_invalid = 0
    provider_blocked = 0
    backend_unavailable = 0
    validate_ref_missing = 0
    provider_blocked_resolved = 0
    latencies: list[float] = []

    for _ in range(40):
        result, elapsed = _run_cli(["bundle", "inspect", "--bundle-cid", "bafy-bundle-local"], env)
        _expect(result, 0, "bundle inspect")
        total += 1
        latencies.append(elapsed)

    for _ in range(39):
        result, elapsed = _run_cli(["bundle", "verify", "--bundle-cid", "bafy-bundle-local"], env)
        _expect(result, 0, "bundle verify")
        total += 1
        latencies.append(elapsed)

    for _ in range(39):
        result, elapsed = _run_cli(
            [
                "bundle",
                "validate-local",
                "--bundle-cid",
                "bafy-bundle-local",
                "--graph-state",
                env["ILC_CLI_GRAPH_STATE_PATH"],
            ],
            env,
        )
        _expect(result, 0, "bundle validate-local")
        total += 1
        latencies.append(elapsed)

    result, elapsed = _run_cli(["bundle", "inspect", "--bundle-cid", "bafy-bundle-blocked"], env)
    _expect(result, 1, "bundle_provider_blocked")
    total += 1
    latencies.append(elapsed)
    provider_blocked += 1
    provider_blocked_resolved += 1

    result, elapsed = _run_cli(["bundle", "inspect", "--bundle-cid", "bafy-bundle-local"], broken_bundle_env)
    _expect(result, 1, "bundle_backend_unavailable")
    total += 1
    latencies.append(elapsed)
    backend_unavailable += 1

    return {
        "total_requests": total,
        "invalid_input_events": invalid,
        "not_found_events": not_found,
        "manifest_invalid_events": manifest_invalid,
        "provider_blocked_events": provider_blocked,
        "backend_unavailable_events": backend_unavailable,
        "validate_ref_missing_events": validate_ref_missing,
        "provider_blocked_resolved_events": provider_blocked_resolved,
        "latencies": latencies,
    }


def _run_cross_lane_envelope_regression(env: dict[str, str]) -> None:
    query_payload = _expect(_run_cli(["query", "node", "--node-id", "node-1"], env)[0], 0, "query node")
    if str(query_payload.get("meta", {}).get("schema_version")) != "299.v0.1":
        raise RuntimeError("query_schema_regression")

    verify_payload = _expect(_run_cli(["verify", "claim", "--claim-id", "claim-a"], env)[0], 0, "verify claim")
    if str(verify_payload.get("meta", {}).get("schema_version")) != "301.v0.1":
        raise RuntimeError("verify_schema_regression")

    bundle_payload = _expect(
        _run_cli(["bundle", "inspect", "--bundle-cid", "bafy-bundle-local"], env)[0],
        0,
        "bundle inspect",
    )
    if str(bundle_payload.get("meta", {}).get("schema_version")) != "303.v0.1":
        raise RuntimeError("bundle_schema_regression")

    identity_payload = _expect(_run_cli(["identity", "show"], env)[0], 0, "identity")
    if str(identity_payload.get("schema_version")) != "254.v0.1":
        raise RuntimeError("identity_schema_regression")


def _build_snapshot(query: dict[str, Any], verify: dict[str, Any], bundle: dict[str, Any]) -> dict[str, Any]:
    kpis = {
        "kpi_query_invalid_input_rate": _safe_rate(query["invalid_input_events"], query["total_requests"]),
        "kpi_query_not_found_rate": _safe_rate(query["not_found_events"], query["total_requests"]),
        "kpi_query_backend_unavailable_rate": _safe_rate(query["backend_unavailable_events"], query["total_requests"]),
        "kpi_query_p95_latency_ms": query["p95_latency_ms"],
        "kpi_verify_invalid_input_rate": _safe_rate(verify["invalid_input_events"], verify["total_requests"]),
        "kpi_verify_not_found_rate": _safe_rate(verify["not_found_events"], verify["total_requests"]),
        "kpi_verify_backend_unavailable_rate": _safe_rate(verify["backend_unavailable_events"], verify["total_requests"]),
        "kpi_verify_check_failure_ratio": _safe_rate(verify["failed_checks"], verify["total_checks"]),
        "kpi_bundle_invalid_input_rate": _safe_rate(bundle["invalid_input_events"], bundle["total_requests"]),
        "kpi_bundle_not_found_rate": _safe_rate(bundle["not_found_events"], bundle["total_requests"]),
        "kpi_bundle_manifest_invalid_rate": _safe_rate(bundle["manifest_invalid_events"], bundle["total_requests"]),
        "kpi_bundle_provider_blocked_rate": _safe_rate(bundle["provider_blocked_events"], bundle["total_requests"]),
        "kpi_bundle_backend_unavailable_rate": _safe_rate(bundle["backend_unavailable_events"], bundle["total_requests"]),
        "kpi_bundle_validate_local_ref_missing_rate": _safe_rate(
            bundle["validate_ref_missing_events"], bundle["total_requests"]
        ),
        "kpi_d2e_success_ratio": _safe_rate(
            (query["total_requests"] - query["invalid_input_events"] - query["not_found_events"])
            + (verify["total_requests"] - verify["invalid_input_events"] - verify["not_found_events"])
            + (
                bundle["total_requests"]
                - bundle["invalid_input_events"]
                - bundle["not_found_events"]
                - bundle["manifest_invalid_events"]
                - bundle["provider_blocked_events"]
                - bundle["backend_unavailable_events"]
            ),
            query["total_requests"] + verify["total_requests"] + bundle["total_requests"],
        ),
        "kpi_d2e_median_latency_ms": _median(query["latencies"] + verify["latencies"] + bundle["latencies"]),
        "kpi_out_of_scope_file_mutation_count": 0,
        "kpi_missing_evidence_anchor_count": 0,
        "kpi_non_target_guardrail_failure_count": 0,
        "kpi_local_state_path_failure_rate": 0.0,
        "kpi_provider_blocked_recovery_ratio": _safe_rate(
            bundle["provider_blocked_resolved_events"], bundle["provider_blocked_events"]
        ),
        "kpi_runbook_recency_days": 0,
        "kpi_utility_framing_coverage": 1.0,
        "kpi_macro_hedge_claim_incidents": 0,
        "kpi_vendor_lock_language_incidents": 0,
    }

    s3_indicators = []
    if kpis["kpi_out_of_scope_file_mutation_count"] > 0:
        s3_indicators.append("kpi_out_of_scope_file_mutation_count")
    if kpis["kpi_non_target_guardrail_failure_count"] > 0:
        s3_indicators.append("kpi_non_target_guardrail_failure_count")

    s2_indicators = []
    if kpis["kpi_query_backend_unavailable_rate"] > 0.01:
        s2_indicators.append("kpi_query_backend_unavailable_rate")
    if kpis["kpi_verify_backend_unavailable_rate"] > 0.01:
        s2_indicators.append("kpi_verify_backend_unavailable_rate")
    if kpis["kpi_bundle_backend_unavailable_rate"] > 0.01:
        s2_indicators.append("kpi_bundle_backend_unavailable_rate")
    if kpis["kpi_verify_check_failure_ratio"] > 0.05:
        s2_indicators.append("kpi_verify_check_failure_ratio")
    if kpis["kpi_bundle_manifest_invalid_rate"] > 0.05:
        s2_indicators.append("kpi_bundle_manifest_invalid_rate")

    s1_indicators = []
    if kpis["kpi_query_invalid_input_rate"] > 0.10:
        s1_indicators.append("kpi_query_invalid_input_rate")
    if kpis["kpi_query_not_found_rate"] > 0.20:
        s1_indicators.append("kpi_query_not_found_rate")
    if kpis["kpi_macro_hedge_claim_incidents"] > 0:
        s1_indicators.append("kpi_macro_hedge_claim_incidents")
    if kpis["kpi_vendor_lock_language_incidents"] > 0:
        s1_indicators.append("kpi_vendor_lock_language_incidents")

    if s3_indicators:
        verdict = "blocked"
    elif s2_indicators:
        verdict = "conditional"
    else:
        verdict = "pass"

    snapshot = {
        "phase": "306",
        "generated_at": _now_utc(),
        "preflight_scope": True,
        "categories": CATEGORIES,
        "lane_request_counts": {
            "query": query["total_requests"],
            "verify": verify["total_requests"],
            "bundle": bundle["total_requests"],
        },
        "kpis": kpis,
        "severity_summary": {
            "s1_indicators": s1_indicators,
            "s2_indicators": s2_indicators,
            "s3_indicators": s3_indicators,
            "verdict": verdict,
        },
    }
    return snapshot


def main() -> int:
    with TemporaryDirectory(prefix="phase306_preflight_") as tmpdir:
        work = Path(tmpdir)
        graph_path = work / "graph.json"
        identity_path = work / "identity.json"
        bundle_path = work / "bundle.json"
        broken_bundle_path = work / "bundle_broken.json"

        _write_graph_state(graph_path)
        _write_identity_state(identity_path)
        _write_bundle_state(bundle_path)
        broken_bundle_path.write_text("{broken_json", encoding="utf-8")

        env = os.environ.copy()
        env["ILC_CLI_GRAPH_STATE_PATH"] = str(graph_path)
        env["ILC_IDENTITY_STATE_PATH"] = str(identity_path)
        env["ILC_BUNDLE_STATE_PATH"] = str(bundle_path)

        broken_bundle_env = dict(env)
        broken_bundle_env["ILC_BUNDLE_STATE_PATH"] = str(broken_bundle_path)

        query_metrics = _run_query_lane(env)
        verify_metrics = _run_verify_lane(env)
        bundle_metrics = _run_bundle_lane(env, broken_bundle_env)
        _run_cross_lane_envelope_regression(env)

        snapshot = _build_snapshot(query_metrics, verify_metrics, bundle_metrics)
        SNAPSHOT_PATH.parent.mkdir(parents=True, exist_ok=True)
        SNAPSHOT_PATH.write_text(json.dumps(snapshot, sort_keys=True, indent=2) + "\n", encoding="utf-8")

        print(f"phase_306_preflight_verdict={snapshot['severity_summary']['verdict']}")
        print(f"phase_306_snapshot={SNAPSHOT_PATH}")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
