"""Phase 1508p Werner SIM-FETCH re-run over Phase 1507p capture data.

PUBLIC_RC_EXCLUDE: werner_capture_sim_fetch_rerun_private
PUBLIC_RC_EXCLUDE_REASON: Private pre-public Werner condition-1 simulation evidence. Not a public runtime surface.

This module validates the Phase 1507p topology capture package, derives a
bounded SIM-FETCH scenario from it, and runs the existing Werner topology
pressure profile. It does not open CDL-096, activate Werner flow-governor
policy, mint ECU, settle ILC, or authorize public network serving.
"""

from __future__ import annotations

import json
import os
import tempfile
from decimal import Decimal
from pathlib import Path
from typing import Any, Mapping

from ilc_core.sim.sim_fetch_01.werner_topology_capture_schema import (
    validate_werner_topology_capture_package,
)
from ilc_core.sim.sim_fetch_01.werner_topology_pressure_profile import (
    TOPOLOGY_PRESSURE_MODEL_WERNER_V1,
    export_werner_topology_pressure_profile_json,
    run_werner_topology_pressure_profile,
)


OBL_037_WERNER_SIM_FETCH_RERUN_TOKEN = (
    "obl_037_werner_sim_fetch_rerun_complete_phase_1508p"
)
WERNER_CONDITION_1_TOPOLOGY_PRESSURE_COVERED_TOKEN = (
    "werner_condition_1_topology_pressure_covered_phase_1508p"
)
WERNER_CONDITION_1_STILL_BLOCKED_TOKEN = (
    "werner_condition_1_still_blocked_phase_1508p"
)
WERNER_CAPTURE_PACKAGE_REPLAYED_TOKEN = (
    "werner_capture_package_replayed_phase_1508p"
)
WERNER_ROUTED_SIM_FETCH_PASS_TOKEN = "werner_routed_sim_fetch_pass_phase_1508p"
NO_CDL_096_OPENING_PHASE_1508P_TOKEN = "no_cdl_096_opening_phase_1508p"
NO_WERNER_FLOW_GOVERNOR_ACTIVATION_PHASE_1508P_TOKEN = (
    "no_werner_flow_governor_activation_phase_1508p"
)

PHASE_1508_COMMON_TOKENS = (
    OBL_037_WERNER_SIM_FETCH_RERUN_TOKEN,
    WERNER_CAPTURE_PACKAGE_REPLAYED_TOKEN,
    NO_CDL_096_OPENING_PHASE_1508P_TOKEN,
    NO_WERNER_FLOW_GOVERNOR_ACTIVATION_PHASE_1508P_TOKEN,
)

DEFAULT_CAPTURE_PATH = Path("docs/sims/ilc_werner_topology_capture_run_1507p_v0.1.json")
DEFAULT_OUTPUT_PATH = Path("docs/sims/ilc_werner_sim_fetch_rerun_1508p_v0.1.json")
DEFAULT_MAX_BYTES = 5_000_000


def _load_capture_package(path: str | Path = DEFAULT_CAPTURE_PATH) -> dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    validate_werner_topology_capture_package(payload)
    return payload


def _decimal_ratio(numerator: int, denominator: int) -> str:
    if denominator < 1:
        return "0.000000"
    return str((Decimal(numerator) / Decimal(denominator)).quantize(Decimal("0.000000")))


def analyze_capture_package(payload: Mapping[str, Any]) -> dict[str, Any]:
    """Return deterministic topology-pressure coverage metrics from capture data."""

    summary = validate_werner_topology_capture_package(payload)
    node_ids = {str(node["node_id"]) for node in payload["nodes"]}
    windows = payload["observation_windows"]
    total_edges = 0
    success_edges = 0
    failure_edges = 0
    directed_pairs: set[tuple[str, str]] = set()
    pressure_coverage_ok = True
    for window in windows:
        window_pressure_nodes = {str(item["node_id"]) for item in window["pressure_by_node"]}
        if window_pressure_nodes != node_ids:
            pressure_coverage_ok = False
        for edge in window["edges"]:
            total_edges += 1
            source = str(edge["source_node_id"])
            target = str(edge["target_node_id"])
            directed_pairs.add((source, target))
            if edge["success"] is True:
                success_edges += 1
            else:
                failure_edges += 1
    success_rate = _decimal_ratio(success_edges, total_edges)
    package_verdict = (
        "pass"
        if (
            summary["node_count"] >= 4
            and summary["window_count"] >= 3
            and total_edges >= summary["node_count"] * summary["window_count"]
            and Decimal(success_rate) >= Decimal("0.800000")
            and pressure_coverage_ok
        )
        else "fail"
    )
    return {
        "capture_mode": summary["capture_mode"],
        "condition_1_package_verdict": package_verdict,
        "directed_pair_count": len(directed_pairs),
        "failure_edge_count": failure_edges,
        "node_count": summary["node_count"],
        "pressure_coverage_ok": pressure_coverage_ok,
        "success_edge_count": success_edges,
        "success_rate": success_rate,
        "topology_source": summary["topology_source"],
        "total_edge_count": total_edges,
        "window_count": summary["window_count"],
    }


def build_sim_fetch_config_from_capture(payload: Mapping[str, Any]) -> dict[str, Any]:
    """Build a bounded SIM-FETCH Werner replay config from the capture package."""

    analysis = analyze_capture_package(payload)
    node_count = int(analysis["node_count"])
    window_count = int(analysis["window_count"])
    total_edges = int(analysis["total_edge_count"])
    scaled_agents = max(100, node_count * 100)
    return {
        "avg_requests_per_agent": "3",
        "cache_capacity_per_peer": max(20, total_edges),
        "directory_staleness_rate": "0",
        "max_requests_per_epoch": max(5000, total_edges * 100),
        "max_retry_hops": 2,
        "n_agents": scaled_agents,
        "n_epochs": window_count,
        "n_serving_peers": node_count,
        "seed": 1508,
        "tier_a_artifact_count": 1,
        "tier_a_request_rate": "0.20",
        "tier_b_artifact_count": max(1, total_edges),
        "tier_b_exact_holder_count_per_artifact": max(1, min(3, node_count - 1)),
        "tier_b_request_rate": "0.80",
        "tier_c_artifact_count": 1,
        "tier_c_request_rate": "0.00",
        "werner_cooling_signal_threshold": 0,
        "werner_heat_signal_threshold": 100,
        "werner_pressure_tiers": ["B"],
        "werner_smoothing_alpha": "0.50",
        "zipf_exponent_tier_a": "0.5",
        "zipf_exponent_tier_b": "0.5",
    }


def _evaluate_sim_fetch_result(sim_payload: Mapping[str, Any]) -> dict[str, Any]:
    aggregate = sim_payload["sim_result"]["aggregate_over_epochs"]
    routed_failure = Decimal(str(aggregate["routed_effective_tier_ab_failure_rate"]))
    routed_holder_hit_rate = Decimal(str(aggregate["routed_holder_hit_rate"]))
    routed_verdict = str(aggregate["routed_tier_service_verdict"])
    retry_exhausted = int(aggregate["routed_retry_exhausted_count"])
    mint_authorized = bool(aggregate["werner_ecu_pressure_mint_authorized"])
    settlement_authorized = bool(aggregate["werner_ilc_settlement_authorized"])
    routed_pass = (
        routed_verdict == "pass"
        and routed_failure <= Decimal("0.100000")
        and routed_holder_hit_rate >= Decimal("0.800000")
        and retry_exhausted == 0
        and mint_authorized is False
        and settlement_authorized is False
    )
    return {
        "aggregate_null_model_verdict": sim_payload["sim_result"]["aggregate_verdict"],
        "routed_effective_tier_ab_failure_rate": str(routed_failure),
        "routed_holder_hit_rate": str(routed_holder_hit_rate),
        "routed_retry_exhausted_count": retry_exhausted,
        "routed_sim_fetch_verdict": routed_verdict,
        "routed_werner_pressure_pass": routed_pass,
        "werner_ecu_pressure_mint_authorized": mint_authorized,
        "werner_ilc_settlement_authorized": settlement_authorized,
    }


def build_phase_1508_rerun_result(
    capture_path: str | Path = DEFAULT_CAPTURE_PATH,
) -> dict[str, Any]:
    """Build the complete Phase 1508p rerun result."""

    capture_payload = _load_capture_package(capture_path)
    capture_analysis = analyze_capture_package(capture_payload)
    sim_config = build_sim_fetch_config_from_capture(capture_payload)
    sim_payload = run_werner_topology_pressure_profile(
        sim_config,
        topology_pressure_model=TOPOLOGY_PRESSURE_MODEL_WERNER_V1,
    )
    sim_evaluation = _evaluate_sim_fetch_result(sim_payload)
    scenario_a = (
        capture_analysis["condition_1_package_verdict"] == "pass"
        and sim_evaluation["routed_werner_pressure_pass"] is True
    )
    outcome_token = (
        WERNER_CONDITION_1_TOPOLOGY_PRESSURE_COVERED_TOKEN
        if scenario_a
        else WERNER_CONDITION_1_STILL_BLOCKED_TOKEN
    )
    tokens = list(PHASE_1508_COMMON_TOKENS)
    if scenario_a:
        tokens.extend(
            (
                WERNER_ROUTED_SIM_FETCH_PASS_TOKEN,
                WERNER_CONDITION_1_TOPOLOGY_PRESSURE_COVERED_TOKEN,
            )
        )
    else:
        tokens.append(WERNER_CONDITION_1_STILL_BLOCKED_TOKEN)
    return {
        "capture_analysis": capture_analysis,
        "capture_package": str(capture_path),
        "condition_1_outcome": "scenario_a_covered" if scenario_a else "scenario_b_blocked",
        "condition_1_outcome_token": outcome_token,
        "non_authorization": {
            "cdl_096_opened": False,
            "ecu_mint_authorized": False,
            "ilc_settlement_authorized": False,
            "public_p2p_authorized": False,
            "werner_flow_governor_activated": False,
        },
        "sim_evaluation": sim_evaluation,
        "sim_fetch_profile_result": sim_payload,
        "tokens": tokens,
        "version": "werner_sim_fetch_rerun_phase_1508p.v0.1",
    }


def export_phase_1508_rerun_json(
    payload: Mapping[str, Any],
    *,
    max_bytes: int = DEFAULT_MAX_BYTES,
) -> str:
    return export_werner_topology_pressure_profile_json(payload, max_bytes=max_bytes)


def write_phase_1508_rerun_result(
    output_path: str | Path = DEFAULT_OUTPUT_PATH,
    *,
    capture_path: str | Path = DEFAULT_CAPTURE_PATH,
    max_bytes: int = DEFAULT_MAX_BYTES,
) -> dict[str, Any]:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = build_phase_1508_rerun_result(capture_path)
    body = export_phase_1508_rerun_json(payload, max_bytes=max_bytes)
    fd, tmp_path = tempfile.mkstemp(
        prefix=f".{path.name}.",
        suffix=".tmp",
        dir=str(path.parent),
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(body)
            handle.write("\n")
        os.replace(tmp_path, path)
    except Exception:
        try:
            os.unlink(tmp_path)
        except FileNotFoundError:
            pass
        raise
    return payload


def main() -> None:
    output_path = DEFAULT_OUTPUT_PATH
    write_phase_1508_rerun_result(output_path)
    print(f"wrote {output_path}")


if __name__ == "__main__":
    main()
