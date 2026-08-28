# SPDX-License-Identifier: AGPL-3.0-only
"""Network-doctor CLI helper for deterministic connectivity diagnostics."""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from collections.abc import Mapping
from typing import Any

from ilc_core.network.connectivity_mode import (
    CONNECTIVITY_PROBE_RUNTIME_NOT_ACTIVATED,
    ConnectivityMode,
    ConnectivityReceipt,
    ProbeResult,
    connectivity_mode_from_probe_result,
)


NETWORK_DOCTOR_CLI_TOKEN = "network_doctor_cli_committed_GAP_INSTALL_NETWORK_DOCTOR_00"
NETWORK_DOCTOR_STUB_WARNING = (
    "CONNECTIVITY_PROBE_RUNTIME_NOT_ACTIVATED=True; live network probes are "
    "not active, returning an outbound_only stub receipt."
)
UPNP_RELAY_TIP = (
    "Tip: Relay mode active (higher latency than direct). If your home or office router\n"
    "supports UPnP, you may be able to establish a direct connection by rerunning with\n"
    "--enable-upnp. Security note: UPnP port mapping has known protocol-level security\n"
    "trade-offs (no router-side authentication). Enable only on trusted networks and only\n"
    "if you understand the implications. Not recommended for production validators or\n"
    "shared/enterprise networks — use manual port forwarding instead."
)


def build_network_doctor_payload(
    *,
    text: bool = False,
    output_path: str | None = None,
    enable_upnp: bool = False,
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

    if output_path:
        _atomic_write_bytes(Path(output_path), receipt.to_canonical_json() + b"\n")

    data: dict[str, Any] = {
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
            has_outbound_connectivity=True,
        )
        receipt = _receipt_from_mode(connectivity_mode_from_probe_result(probe_result))

        class _StubReport:
            connectivity_receipt = receipt
            firewall_mutation_attempted = False
            probe_result = probe_result
            router_mapping = None
            warnings: tuple[str, ...] = ()

        return _StubReport()

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
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("network_doctor_relay_admission_material_must_be_object")
    return payload


__all__ = [
    "NETWORK_DOCTOR_CLI_TOKEN",
    "NETWORK_DOCTOR_STUB_WARNING",
    "UPNP_RELAY_TIP",
    "build_network_doctor_payload",
]
