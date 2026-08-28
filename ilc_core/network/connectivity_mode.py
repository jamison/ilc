# SPDX-License-Identifier: Apache-2.0
"""Pure connectivity mode schema and classifier.

This module records local connectivity evidence. It does not perform network
I/O, mutate router state, open sockets, clear activation guards, or grant
validator authority.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
import ipaddress
import json
import re
from typing import Any


CONNECTIVITY_MODE_RUNTIME_VERSION = "gap_connectivity_mode_runtime_00.v0.1"
CONNECTIVITY_MODE_RUNTIME_TOKEN = (
    "connectivity_mode_runtime_committed_GAP_CONNECTIVITY_MODE_RUNTIME_00"
)
CONNECTIVITY_PROBE_RUNTIME_NOT_ACTIVATED = False

_AGENT_ID_RE = re.compile(r"^[0-9a-f]{96}$")
_MAX_EPOCH = (1 << 64) - 1
_MAX_ENDPOINT_CHARS = 512


class ConnectivityMode(str, Enum):
    """Canonical 9-mode reachability taxonomy."""

    LOCAL_ONLY = "local_only"
    OUTBOUND_ONLY = "outbound_only"
    NAT_TRAVERSED_DIRECT = "nat_traversed_direct"
    RELAY_REACHABLE = "relay_reachable"
    DIRECT_PUBLIC = "direct_public"
    VALIDATOR_OBSERVER_RELAY = "validator_observer_relay"
    VALIDATOR_OBSERVER_DIRECT = "validator_observer_direct"
    VALIDATOR_DIRECT = "validator_direct"
    VALIDATOR_RELAY = "validator_relay"


class ConnectivityModeValidationError(ValueError):
    """Raised when connectivity mode schema input is malformed."""


@dataclass(frozen=True)
class ProbeResult:
    """Observed probe state sufficient to classify one connectivity mode."""

    has_public_ip: bool
    observed_ip: str | None
    observed_port: int | None
    relay_available: bool
    validator_participation_enabled: bool
    has_outbound_connectivity: bool = False
    direct_mapping_candidate: bool = False
    validator_admitted: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "has_public_ip",
            "relay_available",
            "validator_participation_enabled",
            "has_outbound_connectivity",
            "direct_mapping_candidate",
            "validator_admitted",
        ):
            _require_bool(getattr(self, field_name), field_name)

        if self.validator_admitted and not self.validator_participation_enabled:
            raise ConnectivityModeValidationError(
                "validator_admitted_requires_participation_enabled"
            )

        if self.has_public_ip or self.direct_mapping_candidate:
            _require_observed_endpoint(self.observed_ip, self.observed_port)
        elif self.observed_ip is not None or self.observed_port is not None:
            raise ConnectivityModeValidationError(
                "observed_endpoint_requires_direct_evidence"
            )

        if self.has_public_ip and self.direct_mapping_candidate:
            raise ConnectivityModeValidationError(
                "verified_direct_and_candidate_direct_are_exclusive"
            )


@dataclass(frozen=True)
class ConnectivityReceipt:
    """Deterministic receipt for a completed connectivity probe."""

    mode: ConnectivityMode
    observed_endpoint: str | None
    relay_endpoint: str | None
    probe_observer_agent_id: str | None
    probe_epoch: int

    def __post_init__(self) -> None:
        mode = _coerce_mode(self.mode)
        object.__setattr__(self, "mode", mode)

        _require_optional_endpoint(self.observed_endpoint, "observed_endpoint")
        _require_optional_endpoint(self.relay_endpoint, "relay_endpoint")
        _require_optional_agent_id(
            self.probe_observer_agent_id, "probe_observer_agent_id"
        )
        _require_epoch(self.probe_epoch, "probe_epoch")

        if mode in {
            ConnectivityMode.DIRECT_PUBLIC,
            ConnectivityMode.VALIDATOR_OBSERVER_DIRECT,
            ConnectivityMode.VALIDATOR_DIRECT,
            ConnectivityMode.NAT_TRAVERSED_DIRECT,
        } and self.observed_endpoint is None:
            raise ConnectivityModeValidationError(
                "direct_mode_requires_observed_endpoint"
            )

        if mode in {
            ConnectivityMode.RELAY_REACHABLE,
            ConnectivityMode.VALIDATOR_OBSERVER_RELAY,
            ConnectivityMode.VALIDATOR_RELAY,
        } and self.relay_endpoint is None:
            raise ConnectivityModeValidationError("relay_mode_requires_endpoint")

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["mode"] = self.mode.value
        payload["schema_version"] = CONNECTIVITY_MODE_RUNTIME_VERSION
        return payload

    def to_canonical_json(self) -> bytes:
        return json.dumps(
            self.to_dict(),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
            allow_nan=False,
        ).encode("utf-8")


def connectivity_mode_from_probe_result(result: ProbeResult) -> ConnectivityMode:
    """Classify probe evidence into exactly one canonical connectivity mode."""

    if not isinstance(result, ProbeResult):
        raise ConnectivityModeValidationError("probe_result_required")

    if result.validator_admitted:
        if result.has_public_ip:
            return ConnectivityMode.VALIDATOR_DIRECT
        if result.relay_available:
            return ConnectivityMode.VALIDATOR_RELAY

    if result.validator_participation_enabled:
        if result.has_public_ip:
            return ConnectivityMode.VALIDATOR_OBSERVER_DIRECT
        if result.relay_available:
            return ConnectivityMode.VALIDATOR_OBSERVER_RELAY

    if result.direct_mapping_candidate:
        return ConnectivityMode.NAT_TRAVERSED_DIRECT
    if result.has_public_ip:
        return ConnectivityMode.DIRECT_PUBLIC
    if result.relay_available:
        return ConnectivityMode.RELAY_REACHABLE
    if result.has_outbound_connectivity:
        return ConnectivityMode.OUTBOUND_ONLY
    return ConnectivityMode.LOCAL_ONLY


def _coerce_mode(value: ConnectivityMode | str) -> ConnectivityMode:
    if isinstance(value, ConnectivityMode):
        return value
    if isinstance(value, str):
        try:
            return ConnectivityMode(value)
        except ValueError as exc:
            raise ConnectivityModeValidationError("unknown_connectivity_mode") from exc
    raise ConnectivityModeValidationError("connectivity_mode_required")


def _require_bool(value: object, field_name: str) -> None:
    if not isinstance(value, bool):
        raise ConnectivityModeValidationError(f"{field_name}_must_be_bool")


def _require_epoch(value: object, field_name: str) -> None:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ConnectivityModeValidationError(f"{field_name}_must_be_uint64")
    if value < 0 or value > _MAX_EPOCH:
        raise ConnectivityModeValidationError(f"{field_name}_must_be_uint64")


def _require_optional_agent_id(value: object, field_name: str) -> None:
    if value is None:
        return
    if not isinstance(value, str) or _AGENT_ID_RE.fullmatch(value) is None:
        raise ConnectivityModeValidationError(f"{field_name}_must_be_agent_id_hex")


def _require_observed_endpoint(ip_value: object, port_value: object) -> None:
    if not isinstance(ip_value, str) or not ip_value.strip():
        raise ConnectivityModeValidationError("observed_ip_required")
    try:
        ipaddress.ip_address(ip_value)
    except ValueError as exc:
        raise ConnectivityModeValidationError("observed_ip_invalid") from exc
    if isinstance(port_value, bool) or not isinstance(port_value, int):
        raise ConnectivityModeValidationError("observed_port_required")
    if port_value < 1 or port_value > 65535:
        raise ConnectivityModeValidationError("observed_port_out_of_range")


def _require_optional_endpoint(value: object, field_name: str) -> None:
    if value is None:
        return
    if not isinstance(value, str):
        raise ConnectivityModeValidationError(f"{field_name}_must_be_string")
    if len(value) > _MAX_ENDPOINT_CHARS or not value.strip():
        raise ConnectivityModeValidationError(f"{field_name}_invalid")
    host, separator, port_text = value.rpartition(":")
    if not separator or not host or not port_text:
        raise ConnectivityModeValidationError(f"{field_name}_must_be_host_port")
    try:
        port = int(port_text)
    except ValueError as exc:
        raise ConnectivityModeValidationError(f"{field_name}_port_invalid") from exc
    if port < 1 or port > 65535:
        raise ConnectivityModeValidationError(f"{field_name}_port_out_of_range")


__all__ = [
    "CONNECTIVITY_MODE_RUNTIME_TOKEN",
    "CONNECTIVITY_MODE_RUNTIME_VERSION",
    "CONNECTIVITY_PROBE_RUNTIME_NOT_ACTIVATED",
    "ConnectivityMode",
    "ConnectivityModeValidationError",
    "ConnectivityReceipt",
    "ProbeResult",
    "connectivity_mode_from_probe_result",
]
