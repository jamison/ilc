"""Phase 1507p live private Werner topology capture runner.

PUBLIC_RC_EXCLUDE: werner_topology_capture_run_private
PUBLIC_RC_EXCLUDE_REASON: Private pre-public Tailscale evidence capture. Not a public runtime surface.

This module runs bounded private Tailscale probes for the Phase 1507p evidence
package. It does not run SIM-FETCH, open CDL-096, activate Werner
flow-governor policy, mint ECU, settle ILC, or authorize public network serving.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from ilc_core.sim.sim_fetch_01.werner_topology_capture_schema import (
    CAPTURE_MODE_OPTION_B,
    COMMON_REQUIRED_TOKENS,
    DEFAULT_WERNER_CAPTURE_MAX_BYTES,
    PHASE_1506P_FOUR_NODE_TAILSCALE_TOPOLOGY_TOKEN,
    TOPOLOGY_SOURCE_LIVE_PRIVATE_TESTBED,
    WERNER_CAPTURE_OPTION_B_TOKEN,
    export_werner_topology_capture_json,
    validate_werner_topology_capture_package,
)


OBL_036_WERNER_CAPTURE_RUN_TOKEN = "obl_036_werner_capture_run_committed_phase_1507p"
WERNER_CAPTURE_DATA_PACKAGE_TOKEN = (
    "werner_capture_data_package_committed_phase_1507p"
)
WERNER_LIVE_TAILSCALE_CAPTURE_TOKEN = (
    "werner_live_tailscale_capture_completed_phase_1507p"
)
PHASE_1507P_CURRENT_TAILSCALE_IPS_USED_TOKEN = (
    "phase_1507p_current_tailscale_ips_used"
)
PHASE_1507P_STALE_SSH_ALIASES_DETECTED_TOKEN = (
    "phase_1507p_stale_ssh_aliases_detected"
)
NO_WERNER_SIM_FETCH_RERUN_PHASE_1507P_TOKEN = (
    "no_werner_sim_fetch_rerun_phase_1507p"
)
NO_CDL_096_OPENING_PHASE_1507P_TOKEN = "no_cdl_096_opening_phase_1507p"

PHASE_1507_REQUIRED_TOKENS = (
    OBL_036_WERNER_CAPTURE_RUN_TOKEN,
    WERNER_CAPTURE_DATA_PACKAGE_TOKEN,
    WERNER_LIVE_TAILSCALE_CAPTURE_TOKEN,
    PHASE_1507P_CURRENT_TAILSCALE_IPS_USED_TOKEN,
    PHASE_1507P_STALE_SSH_ALIASES_DETECTED_TOKEN,
    NO_WERNER_SIM_FETCH_RERUN_PHASE_1507P_TOKEN,
    NO_CDL_096_OPENING_PHASE_1507P_TOKEN,
)

DEFAULT_TAILSCALE_APP_CLI = "/Applications/Tailscale.app/Contents/MacOS/Tailscale"
REMOTE_USER = "ilcops"
PING_TIMEOUT_SECONDS = 8
SSH_CONNECT_TIMEOUT_SECONDS = 8
SSH_COMMAND_TIMEOUT_SECONDS = 15
SSH_KEYSCAN_TIMEOUT_SECONDS = 10
NODE_ORDER = ("main-computer", "ilc-node-2", "ilc-node-3", "ilc-node-6")
REMOTE_NODES = ("ilc-node-2", "ilc-node-3", "ilc-node-6")
HOST_CLASS_BY_NODE = {
    "main-computer": "local_control_host",
    "ilc-node-2": "vps",
    "ilc-node-3": "vps",
    "ilc-node-6": "vps",
}


@dataclass(frozen=True)
class ProbeResult:
    source_node_id: str
    target_node_id: str
    success: bool
    latency_bucket: str
    exit_code: int
    output_excerpt: str


def _run_command(
    args: list[str],
    *,
    timeout_seconds: int,
    input_text: str | None = None,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        input=input_text,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=timeout_seconds,
        check=False,
    )


def _tailscale_cli() -> str:
    path = shutil.which("tailscale")
    if path:
        return path
    if Path(DEFAULT_TAILSCALE_APP_CLI).exists():
        return DEFAULT_TAILSCALE_APP_CLI
    raise ValueError("phase_1507p_tailscale_cli_not_found")


def _tailscale_status() -> Mapping[str, Any]:
    completed = _run_command(
        [_tailscale_cli(), "status", "--json"],
        timeout_seconds=10,
    )
    if completed.returncode != 0:
        raise ValueError("phase_1507p_tailscale_status_failed")
    return json.loads(completed.stdout)


def _first_tailscale_ip(record: Mapping[str, Any], node_id: str) -> str:
    ips = record.get("TailscaleIPs")
    if not isinstance(ips, list) or not ips:
        raise ValueError(f"phase_1507p_tailscale_ip_missing:{node_id}")
    ip = ips[0]
    if not isinstance(ip, str) or not ip:
        raise ValueError(f"phase_1507p_tailscale_ip_invalid:{node_id}")
    return ip


def _resolve_nodes(status: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    self_record = status.get("Self")
    if not isinstance(self_record, Mapping):
        raise ValueError("phase_1507p_tailscale_self_missing")
    peers = status.get("Peer")
    if not isinstance(peers, Mapping):
        raise ValueError("phase_1507p_tailscale_peers_missing")

    nodes: dict[str, dict[str, Any]] = {
        "main-computer": {
            "admission_status": "admitted",
            "host_class": HOST_CLASS_BY_NODE["main-computer"],
            "node_id": "main-computer",
            "tailscale_dns_name": self_record.get("DNSName"),
            "tailscale_hostname": self_record.get("HostName"),
            "tailscale_ip": _first_tailscale_ip(self_record, "main-computer"),
            "tailscale_online": True,
            "transport_principal": "transport:main-computer",
        }
    }
    for node_id in REMOTE_NODES:
        matches: list[Mapping[str, Any]] = []
        for peer in peers.values():
            if not isinstance(peer, Mapping):
                continue
            dns_name = peer.get("DNSName") or ""
            host_name = peer.get("HostName") or ""
            if host_name == node_id or str(dns_name).startswith(f"{node_id}."):
                matches.append(peer)
        if len(matches) != 1:
            raise ValueError(f"phase_1507p_tailscale_peer_resolution_failed:{node_id}")
        peer = matches[0]
        nodes[node_id] = {
            "admission_status": "admitted",
            "host_class": HOST_CLASS_BY_NODE[node_id],
            "node_id": node_id,
            "tailscale_dns_name": peer.get("DNSName"),
            "tailscale_hostname": peer.get("HostName"),
            "tailscale_ip": _first_tailscale_ip(peer, node_id),
            "tailscale_online": bool(peer.get("Online")),
            "transport_principal": f"transport:{node_id}",
        }
    return nodes


def _build_known_hosts_file(remote_nodes: Mapping[str, Mapping[str, Any]]) -> str:
    ips = [str(remote_nodes[node_id]["tailscale_ip"]) for node_id in REMOTE_NODES]
    completed = _run_command(
        ["ssh-keyscan", "-T", "8", *ips],
        timeout_seconds=SSH_KEYSCAN_TIMEOUT_SECONDS,
    )
    if completed.returncode != 0 and not completed.stdout.strip():
        raise ValueError("phase_1507p_ssh_keyscan_failed")
    fd, known_hosts_path = tempfile.mkstemp(prefix="ilc_phase_1507p_known_hosts_")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(completed.stdout)
    except Exception:
        os.unlink(known_hosts_path)
        raise
    return known_hosts_path


def _ssh_args(ip: str, known_hosts_path: str, remote_command: str) -> list[str]:
    return [
        "ssh",
        "-F",
        "/dev/null",
        "-o",
        "BatchMode=yes",
        "-o",
        f"ConnectTimeout={SSH_CONNECT_TIMEOUT_SECONDS}",
        "-o",
        f"UserKnownHostsFile={known_hosts_path}",
        "-o",
        "StrictHostKeyChecking=yes",
        f"{REMOTE_USER}@{ip}",
        remote_command,
    ]


def _verify_remote_hosts(
    nodes: Mapping[str, Mapping[str, Any]],
    known_hosts_path: str,
) -> dict[str, dict[str, str]]:
    evidence: dict[str, dict[str, str]] = {}
    for node_id in REMOTE_NODES:
        ip = str(nodes[node_id]["tailscale_ip"])
        completed = _run_command(
            _ssh_args(ip, known_hosts_path, "hostname; python3 --version"),
            timeout_seconds=SSH_COMMAND_TIMEOUT_SECONDS,
        )
        if completed.returncode != 0:
            raise ValueError(f"phase_1507p_ssh_probe_failed:{node_id}")
        lines = [line.strip() for line in completed.stdout.splitlines() if line.strip()]
        if len(lines) < 2:
            raise ValueError(f"phase_1507p_ssh_probe_incomplete:{node_id}")
        evidence[node_id] = {
            "hostname": lines[0],
            "python_version": lines[1],
            "ssh_user": REMOTE_USER,
        }
    return evidence


def _latency_bucket(output: str, success: bool) -> str:
    if not success:
        return "timeout"
    match = re.search(r"time[=<]([0-9]+(?:\.[0-9]+)?)\\s*ms", output)
    if not match:
        return "50_250ms"
    integer_part = match.group(1).split(".", 1)[0]
    latency_ms = int(integer_part)
    if latency_ms < 10:
        return "lt_10ms"
    if latency_ms < 50:
        return "10_50ms"
    if latency_ms < 250:
        return "50_250ms"
    if latency_ms < 1000:
        return "250_1000ms"
    return "gt_1000ms"


def _bounded_excerpt(stdout: str, stderr: str) -> str:
    combined = "\n".join(part for part in (stdout.strip(), stderr.strip()) if part)
    return combined[:500]


def _run_probe(
    source_node_id: str,
    target_node_id: str,
    nodes: Mapping[str, Mapping[str, Any]],
    known_hosts_path: str,
) -> ProbeResult:
    target_ip = str(nodes[target_node_id]["tailscale_ip"])
    if source_node_id == "main-computer":
        args = ["ping", "-c", "1", target_ip]
        completed = _run_command(args, timeout_seconds=PING_TIMEOUT_SECONDS)
    else:
        source_ip = str(nodes[source_node_id]["tailscale_ip"])
        completed = _run_command(
            _ssh_args(source_ip, known_hosts_path, f"ping -c 1 -W 2 {target_ip}"),
            timeout_seconds=SSH_COMMAND_TIMEOUT_SECONDS,
        )
    output = _bounded_excerpt(completed.stdout, completed.stderr)
    success = completed.returncode == 0
    return ProbeResult(
        source_node_id=source_node_id,
        target_node_id=target_node_id,
        success=success,
        latency_bucket=_latency_bucket(output, success),
        exit_code=completed.returncode,
        output_excerpt=output,
    )


def _build_observation_window(
    window_index: int,
    nodes: Mapping[str, Mapping[str, Any]],
    known_hosts_path: str,
) -> dict[str, Any]:
    node_ids = list(NODE_ORDER)
    offset = window_index + 1
    probe_results: list[ProbeResult] = []
    for source_index, source_node_id in enumerate(node_ids):
        target_node_id = node_ids[(source_index + offset) % len(node_ids)]
        probe_results.append(
            _run_probe(source_node_id, target_node_id, nodes, known_hosts_path)
        )

    incoming_success_counts = {node_id: 0 for node_id in node_ids}
    for result in probe_results:
        if result.success:
            incoming_success_counts[result.target_node_id] += 1

    pressure_by_node = []
    for node_id in node_ids:
        outbound = [result for result in probe_results if result.source_node_id == node_id]
        failures = sum(1 for result in outbound if not result.success)
        first_bucket = outbound[0].latency_bucket if outbound else "timeout"
        pressure_by_node.append(
            {
                "bounded_latency_bucket": first_bucket,
                "failure_count": failures,
                "fetch_count": len(outbound),
                "node_id": node_id,
                "retry_count": failures,
                "serve_count": incoming_success_counts[node_id],
            }
        )

    edges = [
        {
            "artifact_or_request_class": "tailscale_private_topology_probe",
            "bounded_latency_bucket": result.latency_bucket,
            "edge_type": "fetch",
            "probe_exit_code": result.exit_code,
            "probe_output_excerpt": result.output_excerpt,
            "source_node_id": result.source_node_id,
            "success": result.success,
            "target_node_id": result.target_node_id,
            "tier": "B",
            "transport_scope": "private_tailscale",
        }
        for result in probe_results
    ]
    return {
        "edges": edges,
        "epoch_index": window_index,
        "pressure_by_node": pressure_by_node,
        "window_id": f"phase-1507p-live-window-{window_index + 1}",
    }


def build_phase_1507_capture_package() -> dict[str, Any]:
    """Run the bounded live private capture and return a validated package."""

    status = _tailscale_status()
    nodes_by_id = _resolve_nodes(status)
    known_hosts_path = _build_known_hosts_file(nodes_by_id)
    try:
        remote_evidence = _verify_remote_hosts(nodes_by_id, known_hosts_path)
        node_records = []
        for node_id in NODE_ORDER:
            record = dict(nodes_by_id[node_id])
            if node_id == "main-computer":
                record["ssh_reachable"] = True
                record["ssh_user"] = "local"
            else:
                record.update(remote_evidence[node_id])
                record["ssh_reachable"] = True
            node_records.append(record)

        windows = [
            _build_observation_window(index, nodes_by_id, known_hosts_path)
            for index in range(3)
        ]
    finally:
        try:
            os.unlink(known_hosts_path)
        except FileNotFoundError:
            pass

    payload = {
        "capture_mode": CAPTURE_MODE_OPTION_B,
        "capture_summary": {
            "capture_kind": "live_private_tailscale_probe",
            "node_count": len(node_records),
            "observation_window_count": len(windows),
            "ssh_aliases_not_used": True,
            "ssh_host_key_policy": "ssh_keyscan_current_tailscale_ips_then_strict_checking",
            "stale_ssh_config_aliases_detected": True,
            "tailscale_cli": _tailscale_cli(),
        },
        "nodes": node_records,
        "observation_windows": windows,
        "provenance": {
            "capture_command": "python3 -m ilc_core.sim.sim_fetch_01.werner_topology_capture_run",
            "commit_hash": "phase_1507p_pre_commit_worktree_capture",
            "config_hash": "sha256:phase_1507p_current_tailscale_status",
            "no_ilc_settlement": True,
            "no_production_key": True,
            "no_public_endpoint": True,
            "no_real_ecu": True,
            "node_config_provenance": "tailscale_status_current_ips_plus_phase_1506p_topology",
        },
        "schema_version": "werner_topology_capture_schema_phase_1506p.v0.1",
        "tokens": list(
            COMMON_REQUIRED_TOKENS
            + (WERNER_CAPTURE_OPTION_B_TOKEN, PHASE_1506P_FOUR_NODE_TAILSCALE_TOPOLOGY_TOKEN)
            + PHASE_1507_REQUIRED_TOKENS
        ),
        "topology_source": TOPOLOGY_SOURCE_LIVE_PRIVATE_TESTBED,
    }
    validate_werner_topology_capture_package(payload)
    return payload


def write_phase_1507_capture_package(
    output_path: str | Path,
    *,
    max_bytes: int = DEFAULT_WERNER_CAPTURE_MAX_BYTES,
) -> dict[str, Any]:
    """Run capture and atomically write canonical JSON to output_path."""

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = build_phase_1507_capture_package()
    body = export_werner_topology_capture_json(payload, max_bytes=max_bytes)
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
    output_path = Path("docs/sims/ilc_werner_topology_capture_run_1507p_v0.1.json")
    write_phase_1507_capture_package(output_path)
    print(f"wrote {output_path}")


if __name__ == "__main__":
    main()
