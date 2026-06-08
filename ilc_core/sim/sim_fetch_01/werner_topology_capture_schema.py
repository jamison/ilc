"""Phase 1506p Werner topology capture schema and validator.

PUBLIC_RC_EXCLUDE: werner_topology_capture_schema_private
PUBLIC_RC_EXCLUDE_REASON: Private pre-public simulation/evidence schema. Not a public runtime surface.

This module is schema and fixture support only. It does not execute a capture
run, run SIM-FETCH, open CDL-096, activate Werner flow-governor policy, mint
ECU, settle ILC, or authorize public network serving.
"""

from __future__ import annotations

import json
from typing import Any, Mapping

JsonMapping = Mapping[str, object]

WERNER_TOPOLOGY_CAPTURE_SCHEMA_VERSION = (
    "werner_topology_capture_schema_phase_1506p.v0.1"
)
OBL_035_WERNER_DATA_CAPTURE_SCHEMA_TOKEN = (
    "obl_035_werner_data_capture_schema_committed_phase_1506p"
)
WERNER_CAPTURE_OPTION_A_TOKEN = (
    "werner_capture_option_a_network_level_simulator_selected_phase_1506p"
)
WERNER_CAPTURE_OPTION_B_TOKEN = (
    "werner_capture_option_b_live_private_testbed_selected_phase_1506p"
)
WERNER_CAPTURE_SCHEMA_VALIDATOR_TOKEN = (
    "werner_capture_schema_validator_added_phase_1506p"
)
PHASE_1506P_FOUR_NODE_TAILSCALE_TOPOLOGY_TOKEN = (
    "phase_1506p_four_node_tailscale_topology_selected"
)
NO_WERNER_CAPTURE_RUN_PHASE_1506P_TOKEN = "no_werner_capture_run_phase_1506p"
NO_CDL_096_OPENING_PHASE_1506P_TOKEN = "no_cdl_096_opening_phase_1506p"

TOPOLOGY_SOURCE_NETWORK_LEVEL_SIMULATOR = "network_level_simulator"
TOPOLOGY_SOURCE_LIVE_PRIVATE_TESTBED = "live_private_testbed"
CAPTURE_MODE_OPTION_A = "option_a_network_level_simulator"
CAPTURE_MODE_OPTION_B = "option_b_live_private_testbed"

ALLOWED_TOPOLOGY_SOURCES = frozenset(
    {TOPOLOGY_SOURCE_NETWORK_LEVEL_SIMULATOR, TOPOLOGY_SOURCE_LIVE_PRIVATE_TESTBED}
)
ALLOWED_CAPTURE_MODES_BY_SOURCE = {
    TOPOLOGY_SOURCE_NETWORK_LEVEL_SIMULATOR: frozenset({CAPTURE_MODE_OPTION_A}),
    TOPOLOGY_SOURCE_LIVE_PRIVATE_TESTBED: frozenset({CAPTURE_MODE_OPTION_B}),
}
ALLOWED_ADMISSION_STATUSES = frozenset({"admitted", "rejected", "unknown"})
ALLOWED_EDGE_TYPES = frozenset(
    {"fetch", "serve", "retry", "gossip_announce", "gossip_pull"}
)
ALLOWED_TIERS = frozenset({"A", "B", "C"})
ALLOWED_LATENCY_BUCKETS = frozenset(
    {"lt_10ms", "10_50ms", "50_250ms", "250_1000ms", "gt_1000ms", "timeout"}
)
DEFAULT_WERNER_CAPTURE_MAX_BYTES = 5_000_000

COMMON_REQUIRED_TOKENS = (
    WERNER_TOPOLOGY_CAPTURE_SCHEMA_VERSION,
    OBL_035_WERNER_DATA_CAPTURE_SCHEMA_TOKEN,
    WERNER_CAPTURE_SCHEMA_VALIDATOR_TOKEN,
    NO_WERNER_CAPTURE_RUN_PHASE_1506P_TOKEN,
    NO_CDL_096_OPENING_PHASE_1506P_TOKEN,
)
PHASE_1506_SELECTED_TOPOLOGY_TOKENS = (
    WERNER_CAPTURE_OPTION_B_TOKEN,
    PHASE_1506P_FOUR_NODE_TAILSCALE_TOPOLOGY_TOKEN,
)
REQUIRED_TOKENS = COMMON_REQUIRED_TOKENS + PHASE_1506_SELECTED_TOPOLOGY_TOKENS


def _reject_float_tree(value: Any, path: str) -> None:
    if isinstance(value, float):
        raise ValueError(f"werner_capture_float_forbidden:{path}")
    if isinstance(value, Mapping):
        for key, item in value.items():
            if not isinstance(key, str):
                raise ValueError("werner_capture_mapping_keys_must_be_strings")
            _reject_float_tree(item, f"{path}.{key}")
        return
    if isinstance(value, (list, tuple)):
        for index, item in enumerate(value):
            _reject_float_tree(item, f"{path}[{index}]")


def _require_mapping(value: Any, path: str) -> JsonMapping:
    if not isinstance(value, Mapping):
        raise ValueError(f"werner_capture_expected_mapping:{path}")
    return value


def _require_list(value: Any, path: str) -> list[Any]:
    if not isinstance(value, list):
        raise ValueError(f"werner_capture_expected_list:{path}")
    return value


def _require_non_empty_string(value: Any, token: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(token)
    return value


def _require_non_negative_int(value: Any, token: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(token)
    return value


def _require_bool(value: Any, token: str) -> bool:
    if not isinstance(value, bool):
        raise ValueError(token)
    return value


def _validate_provenance(payload: JsonMapping) -> None:
    provenance = _require_mapping(payload.get("provenance"), "provenance")
    for key in (
        "capture_command",
        "config_hash",
        "commit_hash",
        "node_config_provenance",
    ):
        _require_non_empty_string(
            provenance.get(key),
            f"werner_capture_provenance_{key}_required",
        )
    for key in (
        "no_public_endpoint",
        "no_real_ecu",
        "no_ilc_settlement",
        "no_production_key",
    ):
        required = _require_bool(
            provenance.get(key),
            f"werner_capture_provenance_{key}_required",
        )
        if required is not True:
            raise ValueError(f"werner_capture_provenance_{key}_must_be_true")


def _validate_nodes(payload: JsonMapping) -> set[str]:
    nodes = _require_list(payload.get("nodes"), "nodes")
    if len(nodes) < 4:
        raise ValueError("werner_capture_minimum_four_nodes_required")
    node_ids: set[str] = set()
    for index, node_value in enumerate(nodes):
        node = _require_mapping(node_value, f"nodes[{index}]")
        node_id = _require_non_empty_string(
            node.get("node_id"),
            "werner_capture_node_id_required",
        )
        if node_id in node_ids:
            raise ValueError("werner_capture_node_ids_must_be_unique")
        node_ids.add(node_id)
        _require_non_empty_string(
            node.get("transport_principal"),
            "werner_capture_transport_principal_required",
        )
        admission_status = _require_non_empty_string(
            node.get("admission_status"),
            "werner_capture_admission_status_required",
        )
        if admission_status not in ALLOWED_ADMISSION_STATUSES:
            raise ValueError("werner_capture_admission_status_unsupported")
    return node_ids


def _validate_edge(edge_value: Any, node_ids: set[str], path: str) -> None:
    edge = _require_mapping(edge_value, path)
    source = _require_non_empty_string(
        edge.get("source_node_id"),
        "werner_capture_edge_source_required",
    )
    target = _require_non_empty_string(
        edge.get("target_node_id"),
        "werner_capture_edge_target_required",
    )
    if source not in node_ids or target not in node_ids:
        raise ValueError("werner_capture_edge_node_unknown")
    if source == target:
        raise ValueError("werner_capture_edge_self_loop_forbidden")
    _require_non_empty_string(
        edge.get("artifact_or_request_class"),
        "werner_capture_edge_artifact_or_request_class_required",
    )
    tier = _require_non_empty_string(edge.get("tier"), "werner_capture_edge_tier_required")
    if tier not in ALLOWED_TIERS:
        raise ValueError("werner_capture_edge_tier_unsupported")
    edge_type = _require_non_empty_string(
        edge.get("edge_type"),
        "werner_capture_edge_type_required",
    )
    if edge_type not in ALLOWED_EDGE_TYPES:
        raise ValueError("werner_capture_edge_type_unsupported")
    _require_bool(edge.get("success"), "werner_capture_edge_success_required")


def _validate_pressure(pressure_value: Any, node_ids: set[str], path: str) -> None:
    pressure = _require_mapping(pressure_value, path)
    node_id = _require_non_empty_string(
        pressure.get("node_id"),
        "werner_capture_pressure_node_id_required",
    )
    if node_id not in node_ids:
        raise ValueError("werner_capture_pressure_node_unknown")
    for key in ("fetch_count", "serve_count", "failure_count", "retry_count"):
        _require_non_negative_int(
            pressure.get(key),
            f"werner_capture_pressure_{key}_must_be_non_negative_int",
        )
    latency_bucket = _require_non_empty_string(
        pressure.get("bounded_latency_bucket"),
        "werner_capture_pressure_latency_bucket_required",
    )
    if latency_bucket not in ALLOWED_LATENCY_BUCKETS:
        raise ValueError("werner_capture_pressure_latency_bucket_unsupported")


def _validate_observation_windows(payload: JsonMapping, node_ids: set[str]) -> None:
    windows = _require_list(payload.get("observation_windows"), "observation_windows")
    if len(windows) < 3:
        raise ValueError("werner_capture_minimum_three_windows_required")
    window_ids: set[str] = set()
    for window_index, window_value in enumerate(windows):
        window = _require_mapping(window_value, f"observation_windows[{window_index}]")
        window_id = _require_non_empty_string(
            window.get("window_id"),
            "werner_capture_window_id_required",
        )
        if window_id in window_ids:
            raise ValueError("werner_capture_window_ids_must_be_unique")
        window_ids.add(window_id)
        _require_non_negative_int(
            window.get("epoch_index"),
            "werner_capture_window_epoch_index_required",
        )
        edges = _require_list(window.get("edges"), f"observation_windows[{window_index}].edges")
        if not edges:
            raise ValueError("werner_capture_window_edges_required")
        for edge_index, edge in enumerate(edges):
            _validate_edge(
                edge,
                node_ids,
                f"observation_windows[{window_index}].edges[{edge_index}]",
            )
        pressure = _require_list(
            window.get("pressure_by_node"),
            f"observation_windows[{window_index}].pressure_by_node",
        )
        if len(pressure) != len(node_ids):
            raise ValueError("werner_capture_pressure_must_cover_all_nodes")
        seen_pressure_nodes: set[str] = set()
        for pressure_index, pressure_item in enumerate(pressure):
            _validate_pressure(
                pressure_item,
                node_ids,
                f"observation_windows[{window_index}].pressure_by_node[{pressure_index}]",
            )
            seen_pressure_nodes.add(pressure_item["node_id"])
        if seen_pressure_nodes != node_ids:
            raise ValueError("werner_capture_pressure_node_set_mismatch")


def validate_werner_topology_capture_package(payload: JsonMapping) -> dict[str, Any]:
    """Validate a Phase 1506p-compatible Werner topology capture package."""

    if not isinstance(payload, Mapping):
        raise ValueError("werner_capture_payload_must_be_mapping")
    _reject_float_tree(payload, "payload")
    if payload.get("schema_version") != WERNER_TOPOLOGY_CAPTURE_SCHEMA_VERSION:
        raise ValueError("werner_capture_schema_version_mismatch")
    topology_source = _require_non_empty_string(
        payload.get("topology_source"),
        "werner_capture_topology_source_required",
    )
    if topology_source not in ALLOWED_TOPOLOGY_SOURCES:
        raise ValueError("werner_capture_topology_source_unsupported")
    capture_mode = _require_non_empty_string(
        payload.get("capture_mode"),
        "werner_capture_mode_required",
    )
    if capture_mode not in ALLOWED_CAPTURE_MODES_BY_SOURCE[topology_source]:
        raise ValueError("werner_capture_mode_source_mismatch")
    _validate_provenance(payload)
    node_ids = _validate_nodes(payload)
    _validate_observation_windows(payload, node_ids)
    tokens = tuple(_require_list(payload.get("tokens"), "tokens"))
    mode_tokens = {
        CAPTURE_MODE_OPTION_A: (WERNER_CAPTURE_OPTION_A_TOKEN,),
        CAPTURE_MODE_OPTION_B: PHASE_1506_SELECTED_TOPOLOGY_TOKENS,
    }[capture_mode]
    for token in COMMON_REQUIRED_TOKENS + mode_tokens:
        if token not in tokens:
            raise ValueError(f"werner_capture_required_token_missing:{token}")
    return {
        "capture_mode": capture_mode,
        "node_count": len(node_ids),
        "schema_version": WERNER_TOPOLOGY_CAPTURE_SCHEMA_VERSION,
        "topology_source": topology_source,
        "tokens": list(tokens),
        "window_count": len(payload["observation_windows"]),
    }


def _build_fixture_windows(nodes: list[dict[str, Any]], window_count: int) -> list[dict[str, Any]]:
    windows: list[dict[str, Any]] = []
    latency_cycle = ("lt_10ms", "10_50ms", "50_250ms", "250_1000ms")
    node_count = len(nodes)
    for window_index in range(window_count):
        edges: list[dict[str, Any]] = []
        pressure: list[dict[str, Any]] = []
        for node_index in range(node_count):
            source_index = node_index
            target_index = (node_index + 1 + window_index) % node_count
            if target_index == source_index:
                target_index = (target_index + 1) % node_count
            fetch_count = (window_index + 1) * (node_index + 2)
            serve_count = (window_index + 1) * (node_index + 1)
            failure_count = (window_index + node_index) % 2
            retry_count = failure_count + (1 if node_index == 0 and window_index > 0 else 0)
            edges.append(
                {
                    "artifact_or_request_class": "tier_b_bundle_fetch",
                    "edge_type": "fetch",
                    "source_node_id": nodes[source_index]["node_id"],
                    "success": failure_count == 0,
                    "target_node_id": nodes[target_index]["node_id"],
                    "tier": "B",
                }
            )
            pressure.append(
                {
                    "bounded_latency_bucket": latency_cycle[
                        (window_index + node_index) % len(latency_cycle)
                    ],
                    "failure_count": failure_count,
                    "fetch_count": fetch_count,
                    "node_id": nodes[node_index]["node_id"],
                    "retry_count": retry_count,
                    "serve_count": serve_count,
                }
            )
        windows.append(
            {
                "edges": edges,
                "epoch_index": window_index,
                "pressure_by_node": pressure,
                "window_id": f"schema-fixture-window-{window_index + 1}",
            }
        )
    return windows


def build_option_a_network_level_fixture(
    *,
    node_count: int = 4,
    window_count: int = 3,
) -> dict[str, Any]:
    """Build a deterministic Option A fixture for schema tests and Phase 1507p input design."""

    if isinstance(node_count, bool) or node_count < 4:
        raise ValueError("werner_capture_fixture_minimum_four_nodes_required")
    if isinstance(window_count, bool) or window_count < 3:
        raise ValueError("werner_capture_fixture_minimum_three_windows_required")
    nodes = [
        {
            "admission_status": "admitted",
            "node_id": f"sim-node-{index + 1}",
            "transport_principal": f"transport:sim-node-{index + 1}",
        }
        for index in range(node_count)
    ]
    payload = {
        "capture_mode": CAPTURE_MODE_OPTION_A,
        "nodes": nodes,
        "observation_windows": _build_fixture_windows(nodes, window_count),
        "provenance": {
            "capture_command": "phase_1507p_to_run_option_a_network_level_simulator",
            "commit_hash": "phase_1506p_schema_fixture_not_a_capture_run",
            "config_hash": "sha256:phase_1506p_schema_fixture",
            "no_ilc_settlement": True,
            "no_production_key": True,
            "no_public_endpoint": True,
            "no_real_ecu": True,
            "node_config_provenance": "deterministic_phase_1506p_fixture",
        },
        "schema_version": WERNER_TOPOLOGY_CAPTURE_SCHEMA_VERSION,
        "tokens": list(COMMON_REQUIRED_TOKENS + (WERNER_CAPTURE_OPTION_A_TOKEN,)),
        "topology_source": TOPOLOGY_SOURCE_NETWORK_LEVEL_SIMULATOR,
    }
    validate_werner_topology_capture_package(payload)
    return payload


def build_option_b_live_private_testbed_fixture(
    *,
    window_count: int = 3,
) -> dict[str, Any]:
    """Build the selected four-node Tailscale fixture for schema tests.

    The fixture records the topology shape only. It is not a Phase 1507p capture
    run and does not assert that any host was contacted.
    """

    if isinstance(window_count, bool) or window_count < 3:
        raise ValueError("werner_capture_fixture_minimum_three_windows_required")
    nodes = [
        {
            "admission_status": "admitted",
            "host_class": "local_control_host",
            "node_id": "main-computer",
            "tailscale_name": "main-computer",
            "transport_principal": "transport:main-computer",
        },
        {
            "admission_status": "admitted",
            "host_class": "vps",
            "node_id": "ilc-node-2",
            "tailscale_name": "ilc-node-2",
            "transport_principal": "transport:ilc-node-2",
        },
        {
            "admission_status": "admitted",
            "host_class": "vps",
            "node_id": "ilc-node-3",
            "tailscale_name": "ilc-node-3",
            "transport_principal": "transport:ilc-node-3",
        },
        {
            "admission_status": "admitted",
            "host_class": "vps",
            "node_id": "ilc-node-6",
            "tailscale_name": "ilc-node-6",
            "transport_principal": "transport:ilc-node-6",
        },
    ]
    payload = {
        "capture_mode": CAPTURE_MODE_OPTION_B,
        "nodes": nodes,
        "observation_windows": _build_fixture_windows(nodes, window_count),
        "provenance": {
            "capture_command": "phase_1507p_to_run_live_private_tailscale_capture",
            "commit_hash": "phase_1506p_schema_fixture_not_a_capture_run",
            "config_hash": "sha256:phase_1506p_option_b_schema_fixture",
            "no_ilc_settlement": True,
            "no_production_key": True,
            "no_public_endpoint": True,
            "no_real_ecu": True,
            "node_config_provenance": "three_vps_plus_main_computer_tailscale_topology",
        },
        "schema_version": WERNER_TOPOLOGY_CAPTURE_SCHEMA_VERSION,
        "tokens": list(REQUIRED_TOKENS),
        "topology_source": TOPOLOGY_SOURCE_LIVE_PRIVATE_TESTBED,
    }
    validate_werner_topology_capture_package(payload)
    return payload


def export_werner_topology_capture_json(
    payload: JsonMapping,
    *,
    max_bytes: int = DEFAULT_WERNER_CAPTURE_MAX_BYTES,
) -> str:
    """Return canonical bounded JSON for a validated Werner topology capture package."""

    if isinstance(max_bytes, bool) or not isinstance(max_bytes, int) or max_bytes < 1:
        raise ValueError("werner_capture_invalid_json_max_bytes")
    validated = validate_werner_topology_capture_package(payload)
    body = json.dumps(
        payload,
        sort_keys=True,
        allow_nan=False,
        separators=(",", ":"),
    )
    if len(body.encode("utf-8")) > max_bytes:
        raise ValueError("werner_capture_json_max_bytes_exceeded")
    if validated["node_count"] < 4 or validated["window_count"] < 3:
        raise ValueError("werner_capture_validated_package_below_minimums")
    return body
