# SPDX-License-Identifier: AGPL-3.0-only
"""Network-doctor CLI helper for deterministic connectivity diagnostics."""

from __future__ import annotations

import json
import math
import os
import re
import tempfile
from pathlib import Path
from collections.abc import Mapping
from types import SimpleNamespace
from typing import Any

from ilc_core.network.connectivity_mode import (
    CONNECTIVITY_PROBE_RUNTIME_NOT_ACTIVATED,
    ConnectivityMode,
    ConnectivityReceipt,
    ProbeResult,
    connectivity_mode_from_probe_result,
)
from ilc_core.crypto.pq_signature_verify import _MLDSA_PK_HEX_LENGTH


NETWORK_DOCTOR_CLI_TOKEN = "network_doctor_cli_committed_GAP_INSTALL_NETWORK_DOCTOR_00"
NETWORK_DOCTOR_STUB_WARNING = (
    "CONNECTIVITY_PROBE_RUNTIME_NOT_ACTIVATED=True; live network probes are "
    "not active, returning a local_only stub receipt."
)
UPNP_RELAY_TIP = (
    "Tip: Relay mode active (higher latency than direct). If your home or office router\n"
    "supports UPnP, you may be able to establish a direct connection by rerunning with\n"
    "--enable-upnp. Security note: UPnP port mapping has known protocol-level security\n"
    "trade-offs (no router-side authentication). Enable only on trusted networks and only\n"
    "if you understand the implications. Not recommended for production validators or\n"
    "shared/enterprise networks — use manual port forwarding instead."
)
MAX_RELAY_ADMISSION_MATERIAL_BYTES = 65_536
MAX_NETWORK_DOCTOR_BOOTSTRAP_FETCH_PEERS = 16
MAX_NETWORK_DOCTOR_JSON_DEPTH = 64
MAX_NETWORK_DOCTOR_JSON_NODES = 4096
_LOWER_HEX_RE = re.compile(r"^[0-9a-f]+$")


def build_network_doctor_payload(
    *,
    text: bool = False,
    output_path: str | None = None,
    enable_upnp: bool = False,
    fetch_peers: bool = False,
    bootstrap_seed_peer: str | None = None,
    bootstrap_bundle_cid: str | None = None,
    genesis_authority_pubkey_hex: str | None = None,
    probe_epoch: int = 0,
    probe_observers: tuple[str, ...] = (),
    relay_server_url: str | None = None,
    relay_admission_material_path: str | None = None,
    relay_admission_material: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build the CLI payload for `ilc network-doctor`."""

    admission_material = dict(relay_admission_material or {})
    if relay_admission_material_path:
        admission_material = _load_relay_admission_material(relay_admission_material_path)
    report = _current_probe_report(
        attempt_router_mapping=enable_upnp,
        probe_epoch=probe_epoch,
        probe_observers=tuple(probe_observers),
        relay_server_url=relay_server_url,
        relay_admission_material=admission_material,
    )
    probe = report.probe_result
    mode = connectivity_mode_from_probe_result(probe)
    receipt = report.connectivity_receipt
    receipt_payload = receipt.to_dict()
    warnings = list(report.warnings)
    if CONNECTIVITY_PROBE_RUNTIME_NOT_ACTIVATED:
        warnings.append(NETWORK_DOCTOR_STUB_WARNING)

    bootstrap_fetch = _network_doctor_bootstrap_fetch(
        fetch_peers=fetch_peers,
        bootstrap_seed_peer=bootstrap_seed_peer,
        bootstrap_bundle_cid=bootstrap_bundle_cid,
        genesis_authority_pubkey_hex=genesis_authority_pubkey_hex,
    )

    if output_path:
        _atomic_write_bytes(Path(output_path), receipt.to_canonical_json() + b"\n")

    data: dict[str, Any] = {
        "bootstrap_fetch": bootstrap_fetch,
        "connectivity_mode": mode.value,
        "firewall_mutation_attempted": report.firewall_mutation_attempted,
        "receipt": receipt_payload,
        "router_mapping": report.router_mapping,
        "warnings": warnings,
    }
    if text:
        data["_raw"] = _format_network_doctor_text(receipt, warnings)
    return data


def _current_probe_report(
    *,
    attempt_router_mapping: bool,
    probe_epoch: int,
    probe_observers: tuple[str, ...] = (),
    relay_server_url: str | None = None,
    relay_admission_material: Mapping[str, Any] | None = None,
):
    if CONNECTIVITY_PROBE_RUNTIME_NOT_ACTIVATED:
        probe_result = ProbeResult(
            has_public_ip=False,
            observed_ip=None,
            observed_port=None,
            relay_available=False,
            validator_participation_enabled=False,
            has_outbound_connectivity=False,
        )
        receipt = _receipt_from_mode(connectivity_mode_from_probe_result(probe_result))
        return SimpleNamespace(
            connectivity_receipt=receipt,
            firewall_mutation_attempted=False,
            probe_result=probe_result,
            router_mapping=None,
            warnings=(),
        )

    from ilc_core.network.nat_probe import NatProbeEngine

    engine = NatProbeEngine(
        observers=tuple(probe_observers),
        relay_server_url=relay_server_url,
        relay_admission_material=relay_admission_material,
    )
    return engine.run_probe(
        attempt_router_mapping=attempt_router_mapping,
        probe_epoch=probe_epoch,
    )


def _current_probe_result() -> ProbeResult:
    return _current_probe_report(
        attempt_router_mapping=False,
        probe_epoch=0,
    ).probe_result


def _receipt_from_mode(mode: ConnectivityMode) -> ConnectivityReceipt:
    return ConnectivityReceipt(
        mode=mode,
        observed_endpoint="203.0.113.10:50151"
        if mode
        in {
            ConnectivityMode.NAT_TRAVERSED_DIRECT,
            ConnectivityMode.DIRECT_PUBLIC,
            ConnectivityMode.VALIDATOR_OBSERVER_DIRECT,
            ConnectivityMode.VALIDATOR_DIRECT,
        }
        else None,
        relay_endpoint="relay.ilc.invalid:50151"
        if mode
        in {
            ConnectivityMode.RELAY_REACHABLE,
            ConnectivityMode.VALIDATOR_OBSERVER_RELAY,
            ConnectivityMode.VALIDATOR_RELAY,
        }
        else None,
        probe_observer_agent_id=None,
        probe_epoch=0,
    )


def _format_network_doctor_text(
    receipt: ConnectivityReceipt,
    warnings: list[str],
) -> str:
    lines = [
        "ILC network doctor",
        f"connectivity_mode: {receipt.mode.value}",
        f"probe_epoch: {receipt.probe_epoch}",
    ]
    if receipt.observed_endpoint:
        lines.append(f"observed_endpoint: {receipt.observed_endpoint}")
    if receipt.relay_endpoint:
        lines.append(f"relay_endpoint: {receipt.relay_endpoint}")
    for warning in warnings:
        lines.append(f"warning: {warning}")
    if receipt.mode is ConnectivityMode.RELAY_REACHABLE:
        lines.append(UPNP_RELAY_TIP)
    return "\n".join(lines)


def _atomic_write_bytes(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=path.name + ".", dir=str(path.parent))
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp, path)
    except Exception:
        try:
            os.unlink(tmp)
        except FileNotFoundError:
            pass
        raise


def _load_relay_admission_material(path_value: str) -> dict[str, Any]:
    if not isinstance(path_value, str) or not path_value.strip():
        raise ValueError("network_doctor_relay_admission_material_path_invalid")
    path = Path(path_value).expanduser().resolve()
    raw = _read_bounded_file(
        path,
        max_bytes=MAX_RELAY_ADMISSION_MATERIAL_BYTES,
        too_large_token="network_doctor_relay_admission_material_too_large",
    )
    try:
        payload = json.loads(
            raw.decode("utf-8"),
            parse_constant=lambda _constant: (_ for _ in ()).throw(
                ValueError("network_doctor_relay_admission_material_json_invalid")
            ),
        )
    except UnicodeDecodeError as exc:
        raise ValueError("network_doctor_relay_admission_material_json_invalid") from exc
    if not isinstance(payload, dict):
        raise ValueError("network_doctor_relay_admission_material_must_be_object")
    _reject_non_protocol_numbers(payload)
    return payload


def _read_bounded_file(path: Path, *, max_bytes: int, too_large_token: str) -> bytes:
    with path.open("rb") as handle:
        raw = handle.read(max_bytes + 1)
    if len(raw) > max_bytes:
        raise ValueError(too_large_token)
    return raw


def _network_doctor_bootstrap_fetch(
    *,
    fetch_peers: bool,
    bootstrap_seed_peer: str | None,
    bootstrap_bundle_cid: str | None,
    genesis_authority_pubkey_hex: str | None,
) -> dict[str, Any]:
    material = {
        "bootstrap_bundle_cid": bootstrap_bundle_cid,
        "genesis_authority_pubkey_hex": genesis_authority_pubkey_hex,
        "seed_peer_endpoint": bootstrap_seed_peer,
    }
    present = {key for key, value in material.items() if value is not None}
    if not fetch_peers:
        if any(value not in (None, "") for value in material.values()):
            raise ValueError("network_doctor_bootstrap_fetch_flag_required")
        return {
            "peer_count": 0,
            "peer_endpoints": [],
            "status": "skipped_not_requested",
        }
    if present != set(material):
        raise ValueError("network_doctor_bootstrap_fetch_material_incomplete")
    seed_peer_endpoint = _require_non_empty_string(
        bootstrap_seed_peer,
        "network_doctor_bootstrap_seed_peer_invalid",
    )
    from ilc_core.network.d2d.gossip_peer_registry import validate_peer_endpoint

    try:
        seed_peer_endpoint = validate_peer_endpoint(seed_peer_endpoint)
    except Exception as exc:
        raise ValueError("network_doctor_bootstrap_seed_peer_invalid") from exc
    bundle_cid = _require_non_empty_string(
        bootstrap_bundle_cid,
        "network_doctor_bootstrap_bundle_cid_invalid",
    )
    authority_pubkey_hex = _require_genesis_authority_pubkey_hex(
        genesis_authority_pubkey_hex,
    )

    from ilc_core.network.d2d.bootstrap_fetch_runtime import (
        BootstrapBundleError,
        FetchTransportError,
        extract_peer_endpoints,
        fetch_bootstrap_bundle,
        verify_bootstrap_bundle_signature,
    )

    try:
        bundle = fetch_bootstrap_bundle(seed_peer_endpoint, bundle_cid)
    except (BootstrapBundleError, FetchTransportError) as exc:
        raise ValueError("network_doctor_bootstrap_bundle_fetch_failed") from exc
    if bundle is None:
        raise ValueError("network_doctor_bootstrap_bundle_not_found")
    _reject_non_protocol_numbers(bundle)
    if not verify_bootstrap_bundle_signature(bundle, authority_pubkey_hex):
        raise ValueError("network_doctor_bootstrap_bundle_signature_invalid")
    peer_endpoints = extract_peer_endpoints(bundle)
    if not peer_endpoints:
        raise ValueError("network_doctor_bootstrap_fetch_no_valid_peers")
    if len(peer_endpoints) > MAX_NETWORK_DOCTOR_BOOTSTRAP_FETCH_PEERS:
        raise ValueError("network_doctor_bootstrap_fetch_peer_endpoints_too_many")
    return {
        "bundle_cid": bundle_cid,
        "peer_count": len(peer_endpoints),
        "peer_endpoints": peer_endpoints,
        "seed_peer_endpoint": seed_peer_endpoint,
        "status": "fetched",
    }


def _require_non_empty_string(value: object, token: str) -> str:
    if not isinstance(value, str) or not value or value.strip() != value:
        raise ValueError(token)
    return value


def _require_genesis_authority_pubkey_hex(value: object) -> str:
    if (
        not isinstance(value, str)
        or len(value) != _MLDSA_PK_HEX_LENGTH
        or _LOWER_HEX_RE.fullmatch(value) is None
    ):
        raise ValueError("network_doctor_genesis_authority_pubkey_invalid")
    return value


def _reject_non_protocol_numbers(value: object) -> None:
    node_count = 0

    def visit(item: object, depth: int) -> None:
        nonlocal node_count
        node_count += 1
        if node_count > MAX_NETWORK_DOCTOR_JSON_NODES or depth > MAX_NETWORK_DOCTOR_JSON_DEPTH:
            raise ValueError("network_doctor_relay_admission_material_json_too_deep")
        if isinstance(item, bool) or item is None or isinstance(item, str):
            return
        if isinstance(item, int):
            return
        if isinstance(item, float):
            if not math.isfinite(item):
                raise ValueError("network_doctor_relay_admission_material_json_invalid")
            raise ValueError("network_doctor_relay_admission_material_float_forbidden")
        if isinstance(item, list):
            for child in item:
                visit(child, depth + 1)
            return
        if isinstance(item, dict):
            for child in item.values():
                visit(child, depth + 1)
            return
        raise ValueError("network_doctor_relay_admission_material_json_invalid")

    visit(value, 0)


__all__ = [
    "NETWORK_DOCTOR_CLI_TOKEN",
    "NETWORK_DOCTOR_STUB_WARNING",
    "MAX_RELAY_ADMISSION_MATERIAL_BYTES",
    "MAX_NETWORK_DOCTOR_JSON_DEPTH",
    "MAX_NETWORK_DOCTOR_JSON_NODES",
    "UPNP_RELAY_TIP",
    "build_network_doctor_payload",
]
