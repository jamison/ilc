# SPDX-License-Identifier: AGPL-3.0-only
"""Read-only network-doctor CLI helper.

The live connectivity probe is intentionally not active in this phase. This
module only formats deterministic connectivity receipts from stub evidence.
"""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
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
) -> dict[str, Any]:
    """Build the CLI payload for `ilc network-doctor`."""

    probe = _current_probe_result()
    mode = connectivity_mode_from_probe_result(probe)
    receipt = _receipt_from_mode(mode)
    receipt_payload = receipt.to_dict()
    warnings = []
    if CONNECTIVITY_PROBE_RUNTIME_NOT_ACTIVATED:
        warnings.append(NETWORK_DOCTOR_STUB_WARNING)

    if output_path:
        _atomic_write_bytes(Path(output_path), receipt.to_canonical_json() + b"\n")

    data: dict[str, Any] = {
        "connectivity_mode": mode.value,
        "receipt": receipt_payload,
        "warnings": warnings,
    }
    if text:
        data["_raw"] = _format_network_doctor_text(receipt, warnings)
    return data


def _current_probe_result() -> ProbeResult:
    if CONNECTIVITY_PROBE_RUNTIME_NOT_ACTIVATED:
        return ProbeResult(
            has_public_ip=False,
            observed_ip=None,
            observed_port=None,
            relay_available=False,
            validator_participation_enabled=False,
            has_outbound_connectivity=True,
        )
    raise ValueError("connectivity_probe_runtime_unexpectedly_active")


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


__all__ = [
    "NETWORK_DOCTOR_CLI_TOKEN",
    "NETWORK_DOCTOR_STUB_WARNING",
    "UPNP_RELAY_TIP",
    "build_network_doctor_payload",
]
