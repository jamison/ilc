# SPDX-License-Identifier: AGPL-3.0-only
"""Operator node readiness diagnostics.

This module is diagnostic-only. Network probes are opt-in and bounded by
explicit socket timeouts; no provider API, graph, LMDB, or cloud mutation occurs.
"""

from __future__ import annotations

import ipaddress
import socket
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


NODE_READINESS_RUNTIME_VERSION = "node_readiness_runtime_gap_public_node_readiness_00.v0.1"
PROPOSAL_IDENTITY_NOTE = (
    "Peer-authenticated proposal ingress: submit to validator X using a PEER "
    "validator cert, not your own."
)
TAILSCALE_CGNAT_CIDR = ipaddress.ip_network("100.64.0.0/10")
TCP_PROBE_TIMEOUT_SECONDS = 5.0
UDP_PROBE_TIMEOUT_SECONDS = 3.0
UDP_PROBE_PAYLOAD = b"ILC_NODE_READINESS_UDP_PROBE_V1"


def endpoint_host(endpoint: str) -> str:
    host, _port = parse_endpoint(endpoint)
    return host


def parse_endpoint(endpoint: str) -> tuple[str, int]:
    if not isinstance(endpoint, str) or not endpoint.strip() or ":" not in endpoint:
        raise ValueError("node_readiness_endpoint_invalid")
    host, port_text = endpoint.rsplit(":", maxsplit=1)
    host = _normalize_endpoint_host(host)
    if not host or not port_text:
        raise ValueError("node_readiness_endpoint_invalid")
    try:
        port = int(port_text)
    except ValueError as exc:
        raise ValueError("node_readiness_endpoint_invalid") from exc
    if port < 1 or port > 65535:
        raise ValueError("node_readiness_endpoint_invalid")
    return host, port


def host_is_tailscale_cidr(host: str) -> bool:
    try:
        ip = ipaddress.ip_address(host)
    except ValueError:
        return False
    return ip.version == 4 and ip in TAILSCALE_CGNAT_CIDR


def endpoint_is_wildcard(endpoint: str) -> bool:
    host, _port = parse_endpoint(endpoint)
    return host in {"0.0.0.0", "::"}


def tls_cert_days_remaining(not_after: datetime, *, now: datetime | None = None) -> int:
    current = now or datetime.now(timezone.utc)
    if current.tzinfo is None or not_after.tzinfo is None:
        raise ValueError("node_readiness_datetime_must_be_timezone_aware")
    delta_seconds = int((not_after - current).total_seconds())
    return max(0, delta_seconds // 86_400)


def tls_cert_seconds_remaining(not_after: datetime, *, now: datetime | None = None) -> int:
    current = now or datetime.now(timezone.utc)
    if current.tzinfo is None or not_after.tzinfo is None:
        raise ValueError("node_readiness_datetime_must_be_timezone_aware")
    return max(0, int((not_after - current).total_seconds()))


def extended_local_check_fields(
    *,
    grpc_listen_addr: str,
    endpoint_assertion_grpc_endpoint: str,
    tls_cert_not_after_utc: datetime,
    now: datetime | None = None,
) -> dict[str, Any]:
    endpoint_assertion_host = endpoint_host(endpoint_assertion_grpc_endpoint)
    days_remaining = tls_cert_days_remaining(tls_cert_not_after_utc, now=now)
    seconds_remaining = tls_cert_seconds_remaining(tls_cert_not_after_utc, now=now)
    endpoint_host_is_tailscale = host_is_tailscale_cidr(endpoint_assertion_host)
    warnings: list[str] = []
    if days_remaining < 30:
        warnings.append("tls_cert_expires_within_30_days")
    if endpoint_host_is_tailscale:
        warnings.append("endpoint_assertion_host_in_tailscale_cidr")
    return {
        "endpoint_assertion_host": endpoint_assertion_host,
        "endpoint_host_is_tailscale_cidr": endpoint_host_is_tailscale,
        "grpc_listen_is_wildcard": endpoint_is_wildcard(grpc_listen_addr),
        "proposal_identity_note": PROPOSAL_IDENTITY_NOTE,
        "tls_cert_days_remaining": days_remaining,
        "tls_cert_seconds_remaining": seconds_remaining,
        "warnings": warnings,
    }


def tcp_reachability_probe(
    endpoint: str,
    *,
    timeout_seconds: float = TCP_PROBE_TIMEOUT_SECONDS,
) -> dict[str, Any]:
    host, port = parse_endpoint(endpoint)
    if host in {"0.0.0.0", "::"}:
        return {
            "network_grpc_tcp_error": "network_probe_skipped_wildcard_host",
            "network_grpc_tcp_reachable": False,
            "warnings": ["network_probe_skipped_wildcard_host"],
        }
    start = time.monotonic()
    try:
        with socket.create_connection((host, port), timeout=timeout_seconds):
            latency_ms = int((time.monotonic() - start) * 1000)
            return {
                "network_grpc_tcp_latency_ms": max(0, latency_ms),
                "network_grpc_tcp_reachable": True,
            }
    except TimeoutError:
        return {
            "network_grpc_tcp_error": "network_grpc_tcp_timeout",
            "network_grpc_tcp_reachable": False,
        }
    except ConnectionRefusedError:
        return {
            "network_grpc_tcp_error": "network_grpc_tcp_connection_refused",
            "network_grpc_tcp_reachable": False,
        }
    except OSError as exc:
        return {
            "network_grpc_tcp_error": "network_grpc_tcp_error",
            "network_grpc_tcp_error_detail": exc.__class__.__name__,
            "network_grpc_tcp_reachable": False,
        }


def udp_quic_probe(
    peer_endpoint: str | None,
    *,
    timeout_seconds: float = UDP_PROBE_TIMEOUT_SECONDS,
) -> dict[str, Any]:
    if peer_endpoint is None:
        return {"network_quic_udp_probe": "skipped_no_peer"}
    host, port = parse_endpoint(peer_endpoint)
    started = time.monotonic()
    family = _socket_family_for_host(host)
    sock = socket.socket(family, socket.SOCK_DGRAM)
    try:
        sock.settimeout(timeout_seconds)
        sock.sendto(UDP_PROBE_PAYLOAD, (host, port))
        data, addr = sock.recvfrom(2048)
        latency_ms = int((time.monotonic() - started) * 1000)
        return {
            "network_quic_udp_latency_ms": max(0, latency_ms),
            "network_quic_udp_probe": "reachable",
            "network_quic_udp_response_addr": f"{addr[0]}:{addr[1]}",
            "network_quic_udp_response_bytes": len(data),
            "network_quic_udp_warning": "non_quic_response_received",
        }
    except TimeoutError:
        return {"network_quic_udp_probe": "timeout"}
    except OSError as exc:
        return {
            "network_quic_udp_error": exc.__class__.__name__,
            "network_quic_udp_probe": "unreachable",
        }
    finally:
        sock.close()


def build_readiness_report(
    *,
    config_path: Path,
    network: bool = False,
    peer: str | None = None,
    now: datetime | None = None,
) -> dict[str, Any]:
    from ilc_core.node.operator_init_runtime import check_node_config

    config_path = Path(config_path)
    warnings: list[str] = []
    network_checks: dict[str, Any] = {"enabled": bool(network)}
    try:
        local_checks = check_node_config(config_path, now=now)
    except ValueError as exc:
        return {
            "config_path": str(config_path),
            "local_checks": {"error": str(exc), "verdict": "fail"},
            "network_checks": {
                **network_checks,
                "skipped_due_to_local_failure": True,
            },
            "readiness_verdict": "fail",
            "runtime_version": NODE_READINESS_RUNTIME_VERSION,
            "warnings": [],
        }

    warnings.extend(str(value) for value in local_checks.get("warnings", []))

    if network:
        endpoint = str(local_checks["grpc_endpoint"])
        if local_checks.get("endpoint_host_is_tailscale_cidr") is True:
            network_checks.update(
                {
                    "network_grpc_tcp_error": "endpoint_assertion_host_in_tailscale_cidr",
                    "network_grpc_tcp_reachable": False,
                    "network_quic_udp_probe": "skipped_tailscale_endpoint",
                }
            )
        else:
            tcp_result = tcp_reachability_probe(endpoint)
            network_checks.update(tcp_result)
            warnings.extend(str(value) for value in tcp_result.get("warnings", []))
            udp_result = udp_quic_probe(peer)
            network_checks.update(udp_result)
            if peer is not None and udp_result.get("network_quic_udp_probe") != "reachable":
                warnings.append("network_quic_udp_probe_not_confirmed")
    else:
        network_checks["network_grpc_tcp_probe"] = "skipped_network_flag_absent"
        network_checks["network_quic_udp_probe"] = "skipped_network_flag_absent"

    warning_set = sorted(set(warnings))
    readiness_verdict = "pass"
    if local_checks.get("endpoint_host_is_tailscale_cidr") is True:
        readiness_verdict = "fail"
    elif network and network_checks.get("network_grpc_tcp_reachable") is False:
        readiness_verdict = "fail"
    elif network and network_checks.get("network_quic_udp_probe") == "unreachable":
        readiness_verdict = "fail"
    elif warning_set:
        readiness_verdict = "warn"

    return {
        "config_path": str(config_path),
        "local_checks": local_checks,
        "network_checks": network_checks,
        "readiness_verdict": readiness_verdict,
        "runtime_version": NODE_READINESS_RUNTIME_VERSION,
        "warnings": warning_set,
    }


def _normalize_endpoint_host(host: str) -> str:
    if host.startswith("[") or host.endswith("]"):
        if not (host.startswith("[") and host.endswith("]")):
            raise ValueError("node_readiness_endpoint_invalid")
        host = host[1:-1]
    if not host:
        raise ValueError("node_readiness_endpoint_invalid")
    return host


def _socket_family_for_host(host: str) -> socket.AddressFamily:
    try:
        ip = ipaddress.ip_address(host)
    except ValueError:
        return socket.AF_INET
    return socket.AF_INET6 if ip.version == 6 else socket.AF_INET
