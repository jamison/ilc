# SPDX-License-Identifier: AGPL-3.0-only
"""ILC-native NAT probe engine.

The probe engine uses ILC-configured observer endpoints, not third-party STUN.
Router mutation is delegated to the UPnP router-mapping sidecar only when the
caller explicitly opts in.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import ipaddress
import json
import math
import socket
from collections.abc import Mapping
from typing import Any, Callable
from urllib.parse import urlparse
from urllib.request import HTTPRedirectHandler, build_opener

from ilc_core.network.connectivity_mode import (
    ConnectivityModeValidationError,
    ConnectivityReceipt,
    ProbeResult,
    connectivity_mode_from_probe_result,
)


NAT_PROBE_ENGINE_TOKEN = "nat_probe_engine_committed_GAP_AUTO_NAT_TRAVERSAL_IMPL_00"
NAT_PROBE_SCHEMA_VERSION = "nat_probe_engine_GAP_AUTO_NAT_TRAVERSAL_IMPL_00.v0.1"
UPNP_SIDECAR_UNAVAILABLE = "UPnP sidecar not available — reinstall ilc-core"

_DEFAULT_TIMEOUT_SECONDS = 3.0
_DEFAULT_INTERNAL_PORT = 50151
_MAX_OBSERVER_RESPONSE_BYTES = 8192
_MAX_ENDPOINT_CHARS = 512
_AGENT_ID_HEX_LENGTH = 96
_MAX_EPOCH = (1 << 64) - 1


class NatProbeError(ValueError):
    """Raised when NAT probe input or observer data is malformed."""


@dataclass(frozen=True)
class ProbeObserver:
    """ILC bootstrap observer endpoint used for external endpoint detection."""

    endpoint_url: str
    observer_agent_id: str | None = None

    def __post_init__(self) -> None:
        _require_observer_url(self.endpoint_url)
        if self.observer_agent_id is not None:
            _require_agent_id(self.observer_agent_id, "observer_agent_id")


@dataclass(frozen=True)
class NatProbeReport:
    """Deterministic local receipt for one NAT probe run."""

    connectivity_receipt: ConnectivityReceipt
    probe_result: ProbeResult
    observer_endpoint_url: str | None
    firewall_mutation_attempted: bool
    router_mapping: dict[str, Any] | None
    warnings: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "connectivity_receipt": self.connectivity_receipt.to_dict(),
            "firewall_mutation_attempted": self.firewall_mutation_attempted,
            "observer_endpoint_url": self.observer_endpoint_url,
            "probe_result": asdict(self.probe_result),
            "router_mapping": self.router_mapping,
            "schema_version": NAT_PROBE_SCHEMA_VERSION,
            "warnings": list(self.warnings),
        }

    def to_canonical_json(self) -> bytes:
        return json.dumps(
            self.to_dict(),
            allow_nan=False,
            ensure_ascii=True,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")


ObserverFetcher = Callable[[str, float], dict[str, Any]]
HolePuncher = Callable[[str, int, float], bool]
RelayClientFactory = Callable[..., Any]


class NatProbeEngine:
    """Run ILC-native observer detection and optional router mapping."""

    def __init__(
        self,
        *,
        observers: tuple[ProbeObserver | str, ...] = (),
        relay_endpoint: str | None = None,
        validator_participation_enabled: bool = False,
        validator_admitted: bool = False,
        internal_port: int = _DEFAULT_INTERNAL_PORT,
        timeout_seconds: float = _DEFAULT_TIMEOUT_SECONDS,
        observer_fetcher: ObserverFetcher | None = None,
        hole_puncher: HolePuncher | None = None,
        relay_server_url: str | None = None,
        relay_admission_material: Mapping[str, Any] | None = None,
        relay_client_factory: RelayClientFactory | None = None,
    ) -> None:
        self.observers = tuple(_coerce_observer(observer) for observer in observers)
        if relay_endpoint is not None:
            _require_endpoint_string(relay_endpoint, "relay_endpoint")
        self.relay_endpoint = relay_endpoint
        self.relay_server_url = relay_server_url
        self.relay_admission_material = dict(relay_admission_material or {})
        self._relay_client_factory = relay_client_factory
        self.validator_participation_enabled = _require_bool(
            validator_participation_enabled,
            "validator_participation_enabled",
        )
        self.validator_admitted = _require_bool(validator_admitted, "validator_admitted")
        _require_port(internal_port, "internal_port")
        self.internal_port = internal_port
        self.timeout_seconds = _require_timeout(timeout_seconds)
        self._observer_fetcher = observer_fetcher or _fetch_observer_payload
        self._hole_puncher = hole_puncher or _udp_hole_punch_attempt

    def run_probe(
        self,
        *,
        attempt_router_mapping: bool = False,
        probe_epoch: int = 0,
    ) -> NatProbeReport:
        """Return deterministic connectivity evidence for one protocol epoch."""

        _require_epoch(probe_epoch, "probe_epoch")
        warnings: list[str] = []
        observed_ip: str | None = None
        observed_port: int | None = None
        observer_agent_id: str | None = None
        observer_url: str | None = None
        has_public_ip = False

        for observer in self.observers:
            try:
                payload = self._observer_fetcher(observer.endpoint_url, self.timeout_seconds)
                observed_ip, observed_port = _parse_observer_payload(payload)
                observer_agent_id = payload.get("observer_agent_id") or observer.observer_agent_id
                if observer_agent_id is not None:
                    _require_agent_id(observer_agent_id, "observer_agent_id")
                observer_url = observer.endpoint_url
                if self._hole_puncher(observed_ip, observed_port, self.timeout_seconds):
                    has_public_ip = True
                else:
                    warnings.append("probe_observer_endpoint_not_confirmed_direct")
                    observed_ip = None
                    observed_port = None
                break
            except Exception as exc:  # Try the next ILC observer; report failure deterministically.
                warnings.append(f"probe_observer_failed:{observer.endpoint_url}:{type(exc).__name__}")

        router_mapping_payload: dict[str, Any] | None = None
        firewall_mutation_attempted = False
        direct_mapping_candidate = False

        if not has_public_ip and attempt_router_mapping:
            mapping = self._attempt_router_mapping(warnings)
            router_mapping_payload = mapping.to_dict()
            firewall_mutation_attempted = mapping.firewall_mutation_attempted
            if mapping.success:
                warnings.append("router_mapping_created_external_verification_pending")

        if not self.observers:
            warnings.append("no_ilc_probe_observer_configured")

        relay_endpoint = self.relay_endpoint
        if (
            not has_public_ip
            and not direct_mapping_candidate
            and relay_endpoint is None
        ):
            relay_endpoint = self._request_relay_slot_if_active(probe_epoch, warnings)

        probe_result = ProbeResult(
            has_public_ip=has_public_ip,
            observed_ip=observed_ip,
            observed_port=observed_port,
            relay_available=relay_endpoint is not None,
            validator_participation_enabled=self.validator_participation_enabled,
            has_outbound_connectivity=True,
            direct_mapping_candidate=direct_mapping_candidate,
            validator_admitted=self.validator_admitted,
        )
        mode = connectivity_mode_from_probe_result(probe_result)
        receipt = ConnectivityReceipt(
            mode=mode,
            observed_endpoint=_endpoint(observed_ip, observed_port),
            relay_endpoint=relay_endpoint,
            probe_observer_agent_id=observer_agent_id,
            probe_epoch=probe_epoch,
        )
        return NatProbeReport(
            connectivity_receipt=receipt,
            probe_result=probe_result,
            observer_endpoint_url=observer_url,
            firewall_mutation_attempted=firewall_mutation_attempted,
            router_mapping=router_mapping_payload,
            warnings=tuple(warnings),
        )

    def _request_relay_slot_if_active(
        self,
        probe_epoch: int,
        warnings: list[str],
    ) -> str | None:
        try:
            from ilc_core.network.relay import relay_client as relay_module
        except ImportError:
            warnings.append("relay_client_unavailable")
            return None

        if relay_module.RELAY_CLIENT_NOT_ACTIVATED:
            return None
        if not self.relay_server_url:
            warnings.append("relay_server_url_missing")
            return None
        if not self.relay_admission_material:
            warnings.append("relay_admission_material_missing")
            return None
        try:
            factory = self._relay_client_factory or relay_module.RelayClient
            relay_material = dict(self.relay_admission_material)
            admission_signature = relay_material.pop("relay_admission_signature", None)
            relay_material.pop("relay_admission_payload_ref", None)
            client = factory(
                relay_base_url=self.relay_server_url,
                requested_internal_port=self.internal_port,
                timeout_seconds=self.timeout_seconds,
                **relay_material,
            )
            grant = client.request_slot(
                admission_epoch=probe_epoch,
                relay_admission_signature=admission_signature,
            )
            return grant.relay_endpoint.as_host_port()
        except Exception as exc:
            warnings.append(f"relay_slot_request_failed:{type(exc).__name__}")
            return None

    def _attempt_router_mapping(self, warnings: list[str]) -> Any:
        try:
            from ilc_core.sidecars.upnp_router_mapping import (
                RouterMappingRequest,
                attempt_router_mapping_via_sidecar,
            )
        except ImportError:
            warnings.append(UPNP_SIDECAR_UNAVAILABLE)
            return _sidecar_unavailable_result()

        probe_result = ProbeResult(
            has_public_ip=False,
            observed_ip=None,
            observed_port=None,
            relay_available=self.relay_endpoint is not None,
            validator_participation_enabled=self.validator_participation_enabled,
            has_outbound_connectivity=True,
            validator_admitted=self.validator_admitted,
        )
        request = RouterMappingRequest(
            internal_port=self.internal_port,
            requested_external_port=self.internal_port,
            explicit_opt_in=True,
        )
        return attempt_router_mapping_via_sidecar(probe_result, request=request)


def _fetch_observer_payload(url: str, timeout_seconds: float) -> dict[str, Any]:
    _require_observer_url(url)
    response = _urlopen_no_redirect(url, timeout_seconds)
    try:
        if getattr(response, "status", 200) >= 400:
            raise NatProbeError("probe_observer_http_status_failed")
        payload = response.read(_MAX_OBSERVER_RESPONSE_BYTES + 1)
    finally:
        response.close()
    if len(payload) > _MAX_OBSERVER_RESPONSE_BYTES:
        raise NatProbeError("probe_observer_response_too_large")
    try:
        decoded = json.loads(payload.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise NatProbeError("probe_observer_response_json_invalid") from exc
    if not isinstance(decoded, dict):
        raise NatProbeError("probe_observer_response_must_be_object")
    return decoded


def _udp_hole_punch_attempt(ip_value: str, port_value: int, timeout_seconds: float) -> bool:
    _require_ip(ip_value, "observed_ip")
    _require_port(port_value, "observed_port")
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.settimeout(timeout_seconds)
        sock.sendto(b"ilc-nat-probe-v1", (ip_value, port_value))
    return False


def _parse_observer_payload(payload: dict[str, Any]) -> tuple[str, int]:
    observed_ip = payload.get("observed_ip")
    observed_port = payload.get("observed_port")
    _require_ip(observed_ip, "observed_ip")
    _require_port(observed_port, "observed_port")
    return str(observed_ip), int(observed_port)


def _coerce_observer(value: ProbeObserver | str) -> ProbeObserver:
    if isinstance(value, ProbeObserver):
        return value
    if isinstance(value, str):
        return ProbeObserver(endpoint_url=value)
    raise NatProbeError("probe_observer_required")


def _endpoint(ip_value: str | None, port_value: int | None) -> str | None:
    if ip_value is None or port_value is None:
        return None
    return f"{ip_value}:{port_value}"


def _require_endpoint_string(value: object, field_name: str) -> None:
    if not isinstance(value, str):
        raise NatProbeError(f"{field_name}_must_be_host_port")
    if len(value) > _MAX_ENDPOINT_CHARS or not value.strip():
        raise NatProbeError(f"{field_name}_invalid")
    host, separator, port_text = value.rpartition(":")
    if not separator or not host or not port_text:
        raise NatProbeError(f"{field_name}_must_be_host_port")
    _require_port(int(port_text) if port_text.isdecimal() else port_text, field_name)


def _sidecar_unavailable_result() -> Any:
    class _UnavailableResult:
        firewall_mutation_attempted = False
        success = False
        external_port = None

        def to_dict(self) -> dict[str, Any]:
            return {
                "error": UPNP_SIDECAR_UNAVAILABLE,
                "external_port": None,
                "firewall_mutation_attempted": False,
                "lease_seconds": 0,
                "method_used": None,
                "rollback_token": None,
                "success": False,
            }

    return _UnavailableResult()


def _require_observer_url(value: object) -> None:
    if not isinstance(value, str) or len(value) > _MAX_ENDPOINT_CHARS:
        raise NatProbeError("probe_observer_url_invalid")
    parsed = urlparse(value)
    if parsed.username is not None or parsed.password is not None:
        raise NatProbeError("probe_observer_url_credentials_forbidden")
    if parsed.query or parsed.fragment:
        raise NatProbeError("probe_observer_url_query_fragment_forbidden")
    try:
        parsed_port = parsed.port
    except ValueError as exc:
        raise NatProbeError("probe_observer_url_port_invalid") from exc
    if parsed_port is not None and (parsed_port < 1 or parsed_port > 65535):
        raise NatProbeError("probe_observer_url_port_invalid")
    if parsed.scheme == "https" and parsed.netloc and parsed.hostname:
        return
    if parsed.scheme == "http" and parsed.hostname in {"127.0.0.1", "::1", "localhost"}:
        return
    raise NatProbeError("probe_observer_must_be_ilc_https_or_loopback_test_url")


def _require_agent_id(value: object, field_name: str) -> None:
    if (
        not isinstance(value, str)
        or len(value) != _AGENT_ID_HEX_LENGTH
        or any(char not in "0123456789abcdef" for char in value)
    ):
        raise NatProbeError(f"{field_name}_must_be_agent_id_hex")


def _require_ip(value: object, field_name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise NatProbeError(f"{field_name}_required")
    try:
        ipaddress.ip_address(value)
    except ValueError as exc:
        raise NatProbeError(f"{field_name}_invalid") from exc


def _require_port(value: object, field_name: str) -> None:
    if isinstance(value, bool) or not isinstance(value, int):
        raise NatProbeError(f"{field_name}_must_be_port_int")
    if value < 1 or value > 65535:
        raise NatProbeError(f"{field_name}_out_of_range")


def _require_epoch(value: object, field_name: str) -> None:
    if isinstance(value, bool) or not isinstance(value, int):
        raise NatProbeError(f"{field_name}_must_be_uint64")
    if value < 0 or value > _MAX_EPOCH:
        raise NatProbeError(f"{field_name}_must_be_uint64")


def _require_timeout(value: object) -> float:
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise NatProbeError("probe_timeout_invalid")
    timeout = float(value)
    if not math.isfinite(timeout) or timeout <= 0 or timeout > 10:
        raise NatProbeError("probe_timeout_out_of_range")
    return timeout


def _require_bool(value: object, field_name: str) -> bool:
    if not isinstance(value, bool):
        raise NatProbeError(f"{field_name}_must_be_bool")
    return value


class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, *_args: object, **_kwargs: object) -> None:
        raise NatProbeError("probe_observer_redirect_forbidden")


def _urlopen_no_redirect(url: str, timeout_seconds: float) -> Any:
    return build_opener(_NoRedirect).open(url, timeout=timeout_seconds)


__all__ = [
    "NAT_PROBE_ENGINE_TOKEN",
    "NAT_PROBE_SCHEMA_VERSION",
    "UPNP_SIDECAR_UNAVAILABLE",
    "NatProbeEngine",
    "NatProbeError",
    "NatProbeReport",
    "ProbeObserver",
]
