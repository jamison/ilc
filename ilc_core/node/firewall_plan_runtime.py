# SPDX-License-Identifier: AGPL-3.0-only
"""Provider-neutral operator firewall plan generation.

This module emits firewall artifacts only. It does not apply rules, call cloud
APIs, store credentials, or probe the network.
"""

from __future__ import annotations

import ipaddress
import json
import os
import tempfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - exercised by system Python 3.9 smoke checks
    tomllib = None  # type: ignore[assignment]


FIREWALL_PLAN_RUNTIME_VERSION = "firewall_plan_runtime_gap_public_node_firewall_00.v0.1"
PROPOSAL_IDENTITY_NOTE = (
    "Peer-authenticated proposal ingress: submit to validator X using a PEER "
    "validator cert, not your own."
)
PROVIDERS = frozenset({"digitalocean", "generic", "ufw"})
SOURCE_MODES = frozenset({"public-testnet", "validator-set", "controller-only"})
ADVISORY_TEXT = (
    "gRPC is mTLS-authenticated; TCP reachability alone is not proof of "
    "authorization. QUIC/UDP has no connection state; allow inbound UDP to the "
    "listed port. "
    f"{PROPOSAL_IDENTITY_NOTE} "
    "If UDP is blocked, D2D gossip has a ratified HTTP/2 over TCP fallback "
    "(kind=http per CDL-024 / ADR-0025), but direct QUIC validator consensus "
    "sessions will fail. Opening only TCP is partial; open TCP and UDP for full "
    "production capability."
)
DIGITALOCEAN_ROLLBACK_NOTE = (
    "DigitalOcean rollback: delete the applied firewall by ID via "
    "DELETE https://api.digitalocean.com/v2/firewalls/{firewall_id}. "
    "Docs: https://docs.digitalocean.com/reference/api/digitalocean/#tag/Firewalls"
)


@dataclass(frozen=True)
class FirewallPort:
    purpose: str
    protocol: Literal["tcp", "udp"]
    port: int
    direction: Literal["inbound"] = "inbound"

    def to_dict(self) -> dict[str, Any]:
        return {
            "direction": self.direction,
            "port": self.port,
            "protocol": self.protocol,
            "purpose": self.purpose,
        }


@dataclass(frozen=True)
class FirewallPlan:
    artifact: str
    content_type: str
    output: str
    provider: str
    runtime_version: str
    wrote_output_path: str | None = None

    def to_dict(self) -> dict[str, Any]:
        payload = {
            "artifact": self.artifact,
            "content_type": self.content_type,
            "output": self.output,
            "provider": self.provider,
            "runtime_version": self.runtime_version,
        }
        if self.wrote_output_path is not None:
            payload["wrote_output_path"] = self.wrote_output_path
        return payload


def build_firewall_plan(
    *,
    config_path: Path,
    provider: str = "generic",
    source_mode: str = "public-testnet",
    controller_ip: str | None = None,
    validator_ips: str | list[str] | None = None,
    generated_at_utc: str | None = None,
) -> FirewallPlan:
    provider = _require_member(provider or "generic", PROVIDERS, "node_firewall_provider_invalid")
    source_mode = _require_member(source_mode or "public-testnet", SOURCE_MODES, "node_firewall_source_mode_invalid")
    config = _load_node_config(Path(config_path))
    extracted = _extract_firewall_inputs(config)
    validator_ip_list = _parse_ip_list(validator_ips)
    controller = _parse_optional_ip(controller_ip, "node_firewall_controller_ip_invalid")
    _validate_source_mode_requirements(
        source_mode=source_mode,
        controller_ip=controller,
        validator_ips=validator_ip_list,
    )
    generated_at = generated_at_utc or _now_utc()
    common = _common_payload(
        config_path=Path(config_path),
        extracted=extracted,
        source_mode=source_mode,
        controller_ip=controller,
        validator_ips=validator_ip_list,
        generated_at_utc=generated_at,
    )
    if provider == "digitalocean":
        output = _render_json(_digitalocean_payload(common))
        content_type = "application/json"
    elif provider == "ufw":
        output = _render_ufw(common)
        content_type = "text/x-shellscript"
    else:
        output = _render_json(_generic_payload(common))
        content_type = "application/json"
    return FirewallPlan(
        artifact="ilc_node_firewall_plan",
        content_type=content_type,
        output=output,
        provider=provider,
        runtime_version=FIREWALL_PLAN_RUNTIME_VERSION,
    )


def build_and_optionally_write_firewall_plan(
    *,
    config_path: Path,
    provider: str = "generic",
    source_mode: str = "public-testnet",
    controller_ip: str | None = None,
    validator_ips: str | list[str] | None = None,
    output_path: Path | None = None,
) -> FirewallPlan:
    plan = build_firewall_plan(
        config_path=config_path,
        provider=provider,
        source_mode=source_mode,
        controller_ip=controller_ip,
        validator_ips=validator_ips,
    )
    if output_path is None:
        return plan
    path = atomic_write_text(Path(output_path), plan.output)
    return FirewallPlan(
        artifact=plan.artifact,
        content_type=plan.content_type,
        output=plan.output,
        provider=plan.provider,
        runtime_version=plan.runtime_version,
        wrote_output_path=str(path),
    )


def atomic_write_text(path: Path, text: str, *, mode: int = 0o644) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=str(path.parent))
    tmp_path = Path(tmp_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(text)
            if not text.endswith("\n"):
                handle.write("\n")
        os.chmod(tmp_path, mode)
        os.replace(tmp_path, path)
    finally:
        if tmp_path.exists():
            tmp_path.unlink()
    return path


def parse_endpoint(endpoint: str) -> tuple[str, int]:
    if not isinstance(endpoint, str) or not endpoint.strip() or ":" not in endpoint:
        raise ValueError("node_firewall_endpoint_invalid")
    host, port_text = endpoint.rsplit(":", maxsplit=1)
    if not host or not port_text:
        raise ValueError("node_firewall_endpoint_invalid")
    try:
        port = int(port_text)
    except ValueError as exc:
        raise ValueError("node_firewall_endpoint_invalid") from exc
    if port < 1 or port > 65535:
        raise ValueError("node_firewall_endpoint_invalid")
    return host, port


def _load_node_config(config_path: Path) -> dict[str, Any]:
    if not config_path.is_file():
        raise ValueError("node_firewall_config_missing")
    try:
        text = config_path.read_text(encoding="utf-8")
        payload = tomllib.loads(text) if tomllib is not None else _parse_generated_node_toml(text)
    except OSError as exc:
        raise ValueError("node_firewall_config_invalid_toml") from exc
    except Exception as exc:
        if exc.__class__.__name__ == "TOMLDecodeError":
            raise ValueError("node_firewall_config_invalid_toml") from exc
        raise
    if not isinstance(payload, dict):
        raise ValueError("node_firewall_config_invalid")
    return payload


def _parse_generated_node_toml(text: str) -> dict[str, Any]:
    """Parse the limited TOML subset emitted by `ilc node init`.

    This fallback keeps the planning command usable on system Python 3.9 without
    pulling optional crypto/package dependencies just to render firewall rules.
    """

    config: dict[str, Any] = {}
    current: dict[str, Any] | None = None
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("[") and line.endswith("]"):
            section = line[1:-1].strip()
            if not section:
                raise ValueError("node_firewall_config_invalid_toml")
            current = {}
            config[section] = current
            continue
        if current is None or "=" not in line:
            raise ValueError("node_firewall_config_invalid_toml")
        key, raw_value = (part.strip() for part in line.split("=", 1))
        if not key:
            raise ValueError("node_firewall_config_invalid_toml")
        current[key] = _parse_generated_node_toml_value(raw_value)
    return config


def _parse_generated_node_toml_value(raw_value: str) -> Any:
    if raw_value.startswith("[") and raw_value.endswith("]"):
        inner = raw_value[1:-1].strip()
        if not inner:
            return []
        return [json.loads(part.strip()) for part in inner.split(",") if part.strip()]
    if raw_value.startswith('"') and raw_value.endswith('"'):
        return json.loads(raw_value)
    raise ValueError("node_firewall_config_invalid_toml")


def _extract_firewall_inputs(config: dict[str, Any]) -> dict[str, Any]:
    network = _section(config, "network")
    grpc = _section(config, "grpc")
    p2p = _section(config, "p2p")
    validator = _section(config, "validator")
    network_id = _string(network.get("network_id"), "node_firewall_network_id_missing")
    grpc_endpoint = _string(validator.get("grpc_endpoint"), "node_firewall_grpc_endpoint_missing")
    endpoint_host, endpoint_grpc_port = parse_endpoint(grpc_endpoint)
    _listen_host, grpc_port = parse_endpoint(_string(grpc.get("grpc_listen_addr"), "node_firewall_grpc_listen_addr_missing"))
    _p2p_host, p2p_port = parse_endpoint(_string(p2p.get("p2p_listen_addr"), "node_firewall_p2p_listen_addr_missing"))
    public_endpoint = p2p.get("public_endpoint")
    udp_ports = [FirewallPort("ilc-node QUIC/P2P", "udp", p2p_port)]
    if public_endpoint is not None:
        _public_host, public_port = parse_endpoint(
            _string(public_endpoint, "node_firewall_public_endpoint_invalid")
        )
        if public_port != p2p_port:
            udp_ports.append(FirewallPort("ilc-node QUIC/P2P public endpoint", "udp", public_port))
    return {
        "endpoint_host": endpoint_host,
        "endpoint_grpc_port": endpoint_grpc_port,
        "grpc_port": grpc_port,
        "network_id": network_id,
        "ports": [FirewallPort("ilc-node gRPC ingress", "tcp", grpc_port), *udp_ports],
    }


def _common_payload(
    *,
    config_path: Path,
    extracted: dict[str, Any],
    source_mode: str,
    controller_ip: str | None,
    validator_ips: list[str],
    generated_at_utc: str,
) -> dict[str, Any]:
    return {
        "advisory": ADVISORY_TEXT,
        "config_source": str(config_path),
        "controller_ip": controller_ip,
        "digitalocean_rollback_note": DIGITALOCEAN_ROLLBACK_NOTE,
        "endpoint_host": extracted["endpoint_host"],
        "generated_at_utc": generated_at_utc,
        "network_id": extracted["network_id"],
        "ports": [port.to_dict() for port in extracted["ports"]],
        "runtime_version": FIREWALL_PLAN_RUNTIME_VERSION,
        "source_mode": source_mode,
        "validator_ips": validator_ips,
        "verification_hint": f"nc -z -w 3 {extracted['endpoint_host']} {extracted['grpc_port']}",
    }


def _digitalocean_payload(common: dict[str, Any]) -> dict[str, Any]:
    return {
        "advisory": common["advisory"],
        "comment": "ilc-node firewall plan - generated by ilc node firewall-plan",
        "config_source": common["config_source"],
        "digitalocean_rollback_note": common["digitalocean_rollback_note"],
        "generated_at_utc": common["generated_at_utc"],
        "inbound_rules": [_digitalocean_rule(port, common) for port in common["ports"]],
        "network_id": common["network_id"],
        "port_table": common["ports"],
        "runtime_version": common["runtime_version"],
        "source_mode": common["source_mode"],
        "verification_hint": common["verification_hint"],
    }


def _generic_payload(common: dict[str, Any]) -> dict[str, Any]:
    return {
        "advisory": common["advisory"],
        "config_source": common["config_source"],
        "generated_at_utc": common["generated_at_utc"],
        "network_id": common["network_id"],
        "port_table": common["ports"],
        "provider": "generic",
        "runtime_version": common["runtime_version"],
        "source_mode": common["source_mode"],
        "verification_hint": common["verification_hint"],
    }


def _digitalocean_rule(port: dict[str, Any], common: dict[str, Any]) -> dict[str, Any]:
    return {
        "ports": str(port["port"]),
        "protocol": port["protocol"],
        "sources": {"addresses": _sources_for_port(port, common)},
    }


def _sources_for_port(port: dict[str, Any], common: dict[str, Any]) -> list[str]:
    source_mode = common["source_mode"]
    if source_mode == "public-testnet":
        return ["0.0.0.0/0", "::/0"]
    if source_mode == "validator-set":
        return list(common["validator_ips"])
    if source_mode == "controller-only" and port["protocol"] == "tcp":
        controller_ip = common["controller_ip"]
        if controller_ip is None:
            raise ValueError("node_firewall_controller_ip_required")
        return [controller_ip]
    return list(common["validator_ips"])


def _render_ufw(common: dict[str, Any]) -> str:
    lines = [
        "# ilc-node firewall plan - generated by ilc node firewall-plan",
        f"# network_id: {common['network_id']}",
        f"# Generated at: {common['generated_at_utc']}",
        "# Review carefully before running. These commands modify local UFW rules.",
        "# gRPC is mTLS-authenticated; TCP reachability alone is not authorization.",
        f"# {PROPOSAL_IDENTITY_NOTE}",
        "# UDP/QUIC requires stateless inbound UDP allow rules.",
        "# If UDP is blocked, HTTP/2 TCP fallback may serve D2D gossip only; direct QUIC consensus degrades or fails.",
        "",
    ]
    for port in common["ports"]:
        if common["source_mode"] == "public-testnet":
            lines.append(_ufw_rule(port, None, common["source_mode"]))
        else:
            for source in _sources_for_port(port, common):
                lines.append(_ufw_rule(port, source, common["source_mode"]))
    lines.extend(
        [
            "",
            "# Advisory:",
            f"# {common['advisory']}",
            "",
            "# Verify after applying:",
            "# sudo ufw status numbered",
            f"# {common['verification_hint']} && echo PASS || echo FAIL",
        ]
    )
    return "\n".join(lines) + "\n"


def _ufw_rule(port: dict[str, Any], source: str | None, source_mode: str) -> str:
    purpose = "ilc-node gRPC ingress" if port["protocol"] == "tcp" else "ilc-node QUIC/P2P"
    if source_mode == "public-testnet":
        return f"sudo ufw allow {port['port']}/{port['protocol']} comment '{purpose}'"
    if source is None:
        raise ValueError("node_firewall_ufw_source_missing")
    return (
        f"sudo ufw allow from {source} to any port {port['port']} "
        f"proto {port['protocol']} comment '{purpose}'"
    )


def _render_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n"


def _section(config: dict[str, Any], name: str) -> dict[str, Any]:
    value = config.get(name)
    if not isinstance(value, dict):
        raise ValueError(f"node_firewall_{name}_section_missing")
    return value


def _string(value: Any, token: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(token)
    return value


def _require_member(value: str, allowed: frozenset[str], token: str) -> str:
    if value not in allowed:
        raise ValueError(token)
    return value


def _parse_ip_list(values: str | list[str] | None) -> list[str]:
    if values is None:
        return []
    if isinstance(values, str):
        parts = [part.strip() for part in values.split(",") if part.strip()]
    else:
        parts = [str(part).strip() for part in values if str(part).strip()]
    seen: set[str] = set()
    normalized: list[str] = []
    for part in parts:
        ip = _parse_optional_ip(part, "node_firewall_validator_ip_invalid")
        if ip is None:
            raise ValueError("node_firewall_validator_ip_invalid")
        if ip not in seen:
            normalized.append(ip)
            seen.add(ip)
    return normalized


def _parse_optional_ip(value: str | None, token: str) -> str | None:
    if value is None or value == "":
        return None
    try:
        return str(ipaddress.ip_address(value))
    except ValueError as exc:
        raise ValueError(token) from exc


def _validate_source_mode_requirements(
    *,
    source_mode: str,
    controller_ip: str | None,
    validator_ips: list[str],
) -> None:
    if source_mode == "validator-set" and not validator_ips:
        raise ValueError("node_firewall_validator_ips_required")
    if source_mode == "controller-only":
        if controller_ip is None:
            raise ValueError("node_firewall_controller_ip_required")
        if not validator_ips:
            raise ValueError("node_firewall_validator_ips_required")


def _now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).strftime("%Y-%m-%dT%H:%M:%SZ")
