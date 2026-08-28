# SPDX-License-Identifier: AGPL-3.0-only
"""Explicit-consent UPnP/NAT-PMP/PCP router mapping sidecar.

The sidecar has no import-time effects and never mutates router state unless
called with an explicit opt-in request. It is a local protocol sidecar bundled
with ilc-core, not a relay and not a consensus authority.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import ipaddress
import json
import math
import re
import socket
from collections.abc import Mapping
from typing import Any, Protocol
from urllib.parse import urljoin, urlparse
from urllib.request import HTTPRedirectHandler, Request, build_opener
from xml.sax.saxutils import quoteattr
import xml.etree.ElementTree as ET

from ilc_core.network.connectivity_mode import ProbeResult


ROUTER_MAPPING_NOT_ACTIVATED = False
UPNP_ROUTER_MAPPING_SIDECAR_VERSION = (
    "upnp_router_mapping_sidecar_GAP_AUTO_NAT_TRAVERSAL_IMPL_00.v0.1"
)

_MAX_LEASE_SECONDS = 3600
_MAX_REMOTE_BYTES = 1_000_000
_DEFAULT_TIMEOUT_SECONDS = 3.0
_MIN_PORT = 1024
_MAX_PORT = 65535
_ALLOWED_METHODS = ("pcp", "nat_pmp", "upnp_igd")
_SSDP_ADDR = ("239.255.255.250", 1900)
_UPNP_SERVICE_TYPE_RE = re.compile(
    r"^urn:schemas-upnp-org:service:WAN(?:IP|PPP)Connection:[1-9][0-9]*$"
)
_ALLOWED_PRIVATE_IPV4_GATEWAYS = (
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
)
_ALLOWED_PRIVATE_IPV6_GATEWAYS = (ipaddress.ip_network("fc00::/7"),)


class RouterMappingError(ValueError):
    """Raised when the router mapping request/result is malformed."""


@dataclass(frozen=True)
class RouterMappingRequest:
    """Explicit opt-in request for one bounded router mapping attempt."""

    internal_port: int
    requested_external_port: int | None = None
    lease_seconds: int = _MAX_LEASE_SECONDS
    methods: tuple[str, ...] = _ALLOWED_METHODS
    explicit_opt_in: bool = False
    protocol: str = "udp"
    timeout_seconds: float = _DEFAULT_TIMEOUT_SECONDS

    def __post_init__(self) -> None:
        _require_port(self.internal_port, "internal_port")
        if self.requested_external_port is not None:
            _require_port(self.requested_external_port, "requested_external_port")
        if isinstance(self.lease_seconds, bool) or not isinstance(self.lease_seconds, int):
            raise RouterMappingError("router_mapping_lease_must_be_int")
        if self.lease_seconds < 1 or self.lease_seconds > _MAX_LEASE_SECONDS:
            raise RouterMappingError("router_mapping_lease_out_of_range")
        if isinstance(self.explicit_opt_in, bool) is False:
            raise RouterMappingError("router_mapping_explicit_opt_in_must_be_bool")
        if not isinstance(self.protocol, str) or self.protocol.lower() not in {"tcp", "udp"}:
            raise RouterMappingError("router_mapping_protocol_invalid")
        if not isinstance(self.timeout_seconds, (int, float)) or isinstance(
            self.timeout_seconds, bool
        ):
            raise RouterMappingError("router_mapping_timeout_invalid")
        if (
            not math.isfinite(float(self.timeout_seconds))
            or self.timeout_seconds <= 0
            or self.timeout_seconds > 10
        ):
            raise RouterMappingError("router_mapping_timeout_out_of_range")
        methods = tuple(self.methods)
        if not methods or any(method not in _ALLOWED_METHODS for method in methods):
            raise RouterMappingError("router_mapping_method_invalid")
        object.__setattr__(self, "methods", methods)
        object.__setattr__(self, "protocol", self.protocol.lower())


@dataclass(frozen=True)
class RouterMappingResult:
    """Deterministic receipt for an attempted router mapping."""

    success: bool
    method_used: str | None
    external_port: int | None
    lease_seconds: int
    rollback_token: str | None
    internal_port: int | None = None
    protocol: str | None = None
    firewall_mutation_attempted: bool = False
    error: str | None = None
    rollback_instruction: dict[str, Any] | None = None

    def __post_init__(self) -> None:
        if isinstance(self.success, bool) is False:
            raise RouterMappingError("router_mapping_success_must_be_bool")
        if isinstance(self.firewall_mutation_attempted, bool) is False:
            raise RouterMappingError("router_mapping_mutation_flag_must_be_bool")
        if self.method_used is not None and self.method_used not in _ALLOWED_METHODS:
            raise RouterMappingError("router_mapping_method_used_invalid")
        if self.external_port is not None:
            _require_port(self.external_port, "external_port")
        if self.internal_port is not None:
            _require_port(self.internal_port, "internal_port")
        if self.protocol is not None:
            if (
                not isinstance(self.protocol, str)
                or self.protocol.lower() not in {"tcp", "udp"}
            ):
                raise RouterMappingError("router_mapping_protocol_invalid")
            object.__setattr__(self, "protocol", self.protocol.lower())
        if isinstance(self.lease_seconds, bool) or not isinstance(self.lease_seconds, int):
            raise RouterMappingError("router_mapping_result_lease_must_be_int")
        if self.lease_seconds < 0 or self.lease_seconds > _MAX_LEASE_SECONDS:
            raise RouterMappingError("router_mapping_result_lease_out_of_range")
        if self.rollback_token is not None and not _is_sha256_token(self.rollback_token):
            raise RouterMappingError("router_mapping_rollback_token_invalid")
        if self.error is not None and (
            not isinstance(self.error, str) or not self.error.strip()
        ):
            raise RouterMappingError("router_mapping_error_invalid")
        if self.success:
            if self.method_used is None:
                raise RouterMappingError("router_mapping_success_method_required")
            if self.external_port is None:
                raise RouterMappingError("router_mapping_success_external_port_required")
            if self.internal_port is None:
                raise RouterMappingError("router_mapping_success_internal_port_required")
            if self.protocol is None:
                raise RouterMappingError("router_mapping_success_protocol_required")
            if self.rollback_token is None:
                raise RouterMappingError("router_mapping_success_rollback_token_required")
            if self.firewall_mutation_attempted is not True:
                raise RouterMappingError("router_mapping_success_mutation_flag_required")
            if self.error is not None:
                raise RouterMappingError("router_mapping_success_error_forbidden")
            if self.rollback_instruction is None:
                raise RouterMappingError("router_mapping_success_rollback_instruction_required")
            _validate_rollback_instruction(
                self.rollback_instruction,
                method_used=self.method_used,
                internal_port=self.internal_port,
                external_port=self.external_port,
                lease_seconds=self.lease_seconds,
                protocol=self.protocol,
            )
            if self.rollback_token != _rollback_token_from_fields(
                method=self.method_used,
                internal_port=self.internal_port,
                external_port=self.external_port,
                lease_seconds=self.lease_seconds,
                protocol=self.protocol,
                rollback_instruction=self.rollback_instruction,
            ):
                raise RouterMappingError("router_mapping_rollback_token_mismatch")
        elif self.rollback_instruction is not None:
            _validate_rollback_instruction(self.rollback_instruction)

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["schema_version"] = UPNP_ROUTER_MAPPING_SIDECAR_VERSION
        return payload

    def to_canonical_json(self) -> bytes:
        return json.dumps(
            self.to_dict(),
            allow_nan=False,
            ensure_ascii=True,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")


class RouterMappingTransport(Protocol):
    """Injected transport interface used by tests to avoid real router contact."""

    def attempt_pcp(self, request: RouterMappingRequest) -> RouterMappingResult: ...

    def attempt_nat_pmp(self, request: RouterMappingRequest) -> RouterMappingResult: ...

    def attempt_upnp_igd(self, request: RouterMappingRequest) -> RouterMappingResult: ...


class StdlibRouterMappingTransport:
    """Best-effort stdlib transport for explicit local-router mapping attempts."""

    def attempt_pcp(self, request: RouterMappingRequest) -> RouterMappingResult:
        return _unsupported(request, "pcp", "pcp_gateway_discovery_not_configured")

    def attempt_nat_pmp(self, request: RouterMappingRequest) -> RouterMappingResult:
        return _unsupported(request, "nat_pmp", "nat_pmp_gateway_discovery_not_configured")

    def attempt_upnp_igd(self, request: RouterMappingRequest) -> RouterMappingResult:
        location = _discover_upnp_location(timeout_seconds=float(request.timeout_seconds))
        if location is None:
            return _unsupported(request, "upnp_igd", "upnp_igd_gateway_not_found")
        control_url, service_type = _load_upnp_control(location, request)
        internal_client = _send_upnp_add_port_mapping(control_url, service_type, request)
        external_port = request.requested_external_port or request.internal_port
        rollback_instruction = build_upnp_rollback_instruction(
            control_url=control_url,
            internal_client=internal_client,
            internal_port=request.internal_port,
            lease_seconds=request.lease_seconds,
            method_used="upnp_igd",
            service_type=service_type,
            external_port=external_port,
            protocol=request.protocol,
        )
        return RouterMappingResult(
            success=True,
            method_used="upnp_igd",
            external_port=external_port,
            lease_seconds=request.lease_seconds,
            rollback_token=_rollback_token(
                request,
                "upnp_igd",
                external_port=external_port,
                rollback_instruction=rollback_instruction,
            ),
            internal_port=request.internal_port,
            protocol=request.protocol,
            firewall_mutation_attempted=True,
            rollback_instruction=rollback_instruction,
        )


def attempt_router_mapping_via_sidecar(
    probe_result: ProbeResult,
    *,
    request: RouterMappingRequest | None = None,
    transport: RouterMappingTransport | None = None,
) -> RouterMappingResult:
    """Attempt a bounded router mapping only when the request opts in."""

    if not isinstance(probe_result, ProbeResult):
        raise RouterMappingError("probe_result_required")
    if request is None or request.explicit_opt_in is not True:
        return RouterMappingResult(
            success=False,
            method_used=None,
            external_port=None,
            lease_seconds=0,
            rollback_token=None,
            firewall_mutation_attempted=False,
            error="explicit_router_mapping_opt_in_required",
        )

    active_transport = transport or StdlibRouterMappingTransport()
    last_result: RouterMappingResult | None = None
    for method in request.methods:
        if method == "pcp":
            result = active_transport.attempt_pcp(request)
        elif method == "nat_pmp":
            result = active_transport.attempt_nat_pmp(request)
        elif method == "upnp_igd":
            result = active_transport.attempt_upnp_igd(request)
        else:  # __post_init__ prevents this branch.
            raise RouterMappingError("router_mapping_method_invalid")
        if not isinstance(result, RouterMappingResult):
            raise RouterMappingError("router_mapping_result_required")
        last_result = result
        if result.success:
            return result

    return last_result or RouterMappingResult(
        success=False,
        method_used=None,
        external_port=None,
        lease_seconds=0,
        rollback_token=None,
        firewall_mutation_attempted=False,
        error="router_mapping_no_method_attempted",
    )


def upnp_router_mapping_sidecar_manifest() -> dict[str, Any]:
    """Return deterministic sidecar manifest metadata."""

    return {
        "authority_gate": "explicit opt-in only via attempt_router_mapping=True",
        "component": "upnp_router_mapping",
        "implementation_status": "implemented_gap_auto_nat_traversal_impl_00",
        "no_import_time_router_mutation": True,
        "public_serving_enabled": False,
        "required_capabilities": [
            "bounded_lease_seconds",
            "explicit_opt_in_router_mapping",
            "machine_parseable_rollback_instruction",
            "port_allowlist_enforcement",
            "rollback_receipt_token",
        ],
        "router_mapping_not_activated": ROUTER_MAPPING_NOT_ACTIVATED,
        "sidecar_id": "upnp-router-mapping",
        "version": UPNP_ROUTER_MAPPING_SIDECAR_VERSION,
        "wiring_modes": ["in_process_import"],
    }


def _unsupported(
    request: RouterMappingRequest,
    method: str,
    error: str,
) -> RouterMappingResult:
    return RouterMappingResult(
        success=False,
        method_used=method,
        external_port=None,
        lease_seconds=request.lease_seconds,
        rollback_token=None,
        internal_port=request.internal_port,
        protocol=request.protocol,
        firewall_mutation_attempted=False,
        error=error,
    )


def _discover_upnp_location(*, timeout_seconds: float) -> str | None:
    message = (
        "M-SEARCH * HTTP/1.1\r\n"
        "HOST: 239.255.255.250:1900\r\n"
        'MAN: "ssdp:discover"\r\n'
        "MX: 1\r\n"
        "ST: urn:schemas-upnp-org:device:InternetGatewayDevice:1\r\n"
        "\r\n"
    ).encode("ascii")
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.settimeout(timeout_seconds)
        sock.sendto(message, _SSDP_ADDR)
        try:
            payload, sender = sock.recvfrom(4096)
        except TimeoutError:
            return None
    for line in payload.decode("iso-8859-1", errors="replace").splitlines():
        name, separator, value = line.partition(":")
        if separator and name.lower() == "location":
            location = value.strip()
            _require_local_http_url(location)
            _require_ssdp_location_sender(location, sender[0])
            return location
    return None


def _load_upnp_control(
    location: str,
    request: RouterMappingRequest,
) -> tuple[str, str]:
    _require_local_http_url(location)
    description = _read_url(location, timeout_seconds=float(request.timeout_seconds))
    _reject_xml_entities(description)
    try:
        root = ET.fromstring(description)
    except ET.ParseError as exc:
        raise RouterMappingError("upnp_description_xml_invalid") from exc
    for service in root.iter():
        if _local_name(service.tag) != "service":
            continue
        fields = {
            _local_name(child.tag): (child.text or "").strip()
            for child in list(service)
        }
        service_type = fields.get("serviceType", "")
        control_url = fields.get("controlURL", "")
        if "WANIPConnection" in service_type or "WANPPPConnection" in service_type:
            service_type = _require_upnp_service_type(service_type)
            if not control_url:
                raise RouterMappingError("upnp_control_url_missing")
            full_url = urljoin(location, control_url)
            _require_local_http_url(full_url)
            return full_url, service_type
    raise RouterMappingError("upnp_wan_connection_service_missing")


def _send_upnp_add_port_mapping(
    control_url: str,
    service_type: str,
    request: RouterMappingRequest,
) -> str:
    external_port = request.requested_external_port or request.internal_port
    internal_client = _local_lan_ip_for(control_url, timeout_seconds=float(request.timeout_seconds))
    body = (
        '<?xml version="1.0"?>'
        '<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" '
        's:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">'
        "<s:Body>"
        f"<u:AddPortMapping xmlns:u={quoteattr(service_type)}>"
        "<NewRemoteHost></NewRemoteHost>"
        f"<NewExternalPort>{external_port}</NewExternalPort>"
        f"<NewProtocol>{request.protocol.upper()}</NewProtocol>"
        f"<NewInternalPort>{request.internal_port}</NewInternalPort>"
        f"<NewInternalClient>{internal_client}</NewInternalClient>"
        "<NewEnabled>1</NewEnabled>"
        "<NewPortMappingDescription>ILC explicit opt-in mapping</NewPortMappingDescription>"
        f"<NewLeaseDuration>{request.lease_seconds}</NewLeaseDuration>"
        "</u:AddPortMapping>"
        "</s:Body>"
        "</s:Envelope>"
    ).encode("utf-8")
    http_request = Request(
        control_url,
        data=body,
        headers={
            "Content-Type": 'text/xml; charset="utf-8"',
            "SOAPAction": f'"{service_type}#AddPortMapping"',
        },
        method="POST",
    )
    response = _urlopen_no_redirect(http_request, float(request.timeout_seconds))
    try:
        if getattr(response, "status", 200) >= 400:
            raise RouterMappingError("upnp_add_port_mapping_failed")
        _reject_upnp_soap_fault(_read_response(response))
    finally:
        response.close()
    return internal_client


def remove_upnp_port_mapping(
    *,
    control_url: str,
    service_type: str,
    external_port: int,
    protocol: str,
    timeout_seconds: float = _DEFAULT_TIMEOUT_SECONDS,
) -> None:
    """Execute the machine-parseable rollback instruction for a UPnP mapping."""

    _require_local_http_url(control_url)
    service_type = _require_upnp_service_type(service_type)
    _require_port(external_port, "external_port")
    if not isinstance(protocol, str) or protocol.lower() not in {"tcp", "udp"}:
        raise RouterMappingError("router_mapping_protocol_invalid")
    if (
        isinstance(timeout_seconds, bool)
        or not isinstance(timeout_seconds, (int, float))
        or not math.isfinite(float(timeout_seconds))
        or float(timeout_seconds) <= 0
        or float(timeout_seconds) > 10
    ):
        raise RouterMappingError("router_mapping_timeout_out_of_range")
    body = (
        '<?xml version="1.0"?>'
        '<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" '
        's:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">'
        "<s:Body>"
        f"<u:DeletePortMapping xmlns:u={quoteattr(service_type)}>"
        "<NewRemoteHost></NewRemoteHost>"
        f"<NewExternalPort>{external_port}</NewExternalPort>"
        f"<NewProtocol>{protocol.upper()}</NewProtocol>"
        "</u:DeletePortMapping>"
        "</s:Body>"
        "</s:Envelope>"
    ).encode("utf-8")
    request = Request(
        control_url,
        data=body,
        headers={
            "Content-Type": 'text/xml; charset="utf-8"',
            "SOAPAction": f'"{service_type}#DeletePortMapping"',
        },
        method="POST",
    )
    response = _urlopen_no_redirect(request, float(timeout_seconds))
    try:
        if getattr(response, "status", 200) >= 400:
            raise RouterMappingError("upnp_delete_port_mapping_failed")
        _reject_upnp_soap_fault(_read_response(response))
    finally:
        response.close()


def build_upnp_rollback_instruction(
    *,
    control_url: str,
    internal_client: str | None = None,
    internal_port: int,
    lease_seconds: int,
    method_used: str,
    service_type: str,
    external_port: int,
    protocol: str,
) -> dict[str, Any]:
    """Return the executable DeletePortMapping instruction for rollback."""

    _require_local_http_url(control_url)
    if method_used not in _ALLOWED_METHODS:
        raise RouterMappingError("router_mapping_method_used_invalid")
    _require_port(internal_port, "internal_port")
    if isinstance(lease_seconds, bool) or not isinstance(lease_seconds, int):
        raise RouterMappingError("router_mapping_result_lease_must_be_int")
    if lease_seconds < 1 or lease_seconds > _MAX_LEASE_SECONDS:
        raise RouterMappingError("router_mapping_result_lease_out_of_range")
    if internal_client is not None:
        try:
            ipaddress.ip_address(internal_client)
        except ValueError as exc:
            raise RouterMappingError("router_mapping_internal_client_invalid") from exc
    service_type = _require_upnp_service_type(service_type)
    _require_port(external_port, "external_port")
    if not isinstance(protocol, str) or protocol.lower() not in {"tcp", "udp"}:
        raise RouterMappingError("router_mapping_protocol_invalid")
    return {
        "action": "DeletePortMapping",
        "control_url": control_url,
        "external_port": external_port,
        "internal_client": internal_client,
        "internal_port": internal_port,
        "lease_seconds": lease_seconds,
        "method_used": method_used,
        "protocol": protocol.lower(),
        "schema_version": UPNP_ROUTER_MAPPING_SIDECAR_VERSION,
        "service_type": service_type,
    }


def _read_url(url: str, *, timeout_seconds: float) -> bytes:
    response = _urlopen_no_redirect(url, timeout_seconds)
    try:
        if getattr(response, "status", 200) >= 400:
            raise RouterMappingError("router_mapping_http_status_failed")
        return _read_response(response)
    finally:
        response.close()


def _read_response(response: Any) -> bytes:
    payload = response.read(_MAX_REMOTE_BYTES + 1)
    if len(payload) > _MAX_REMOTE_BYTES:
        raise RouterMappingError("router_mapping_remote_payload_too_large")
    return payload


def _reject_xml_entities(payload: bytes) -> None:
    lowered = payload[:1024].lower()
    if b"<!doctype" in lowered or b"<!entity" in lowered:
        raise RouterMappingError("upnp_description_xml_entity_forbidden")


def _reject_upnp_soap_fault(payload: bytes) -> None:
    lowered = payload[:4096].lower()
    if b"<fault" in lowered or b":fault" in lowered or b"<errorcode>" in lowered:
        raise RouterMappingError("upnp_soap_fault_response")


def _local_lan_ip_for(control_url: str, *, timeout_seconds: float) -> str:
    parsed = urlparse(control_url)
    if parsed.hostname is None:
        raise RouterMappingError("upnp_control_host_missing")
    try:
        remote_ip = ipaddress.ip_address(parsed.hostname)
    except ValueError as exc:
        raise RouterMappingError("upnp_control_host_missing") from exc
    port = parsed.port or 80
    family = socket.AF_INET6 if isinstance(remote_ip, ipaddress.IPv6Address) else socket.AF_INET
    address: tuple[Any, ...]
    if family == socket.AF_INET6:
        address = (str(remote_ip), port, 0, 0)
    else:
        address = (str(remote_ip), port)
    with socket.socket(family, socket.SOCK_DGRAM) as sock:
        sock.settimeout(timeout_seconds)
        sock.connect(address)
        local_ip = sock.getsockname()[0]
    try:
        ipaddress.ip_address(local_ip)
    except ValueError as exc:
        raise RouterMappingError("upnp_local_lan_ip_invalid") from exc
    return local_ip


def _require_local_http_url(value: str) -> None:
    parsed = urlparse(value)
    if parsed.scheme != "http" or parsed.hostname is None:
        raise RouterMappingError("upnp_location_must_be_local_http_url")
    if parsed.username is not None or parsed.password is not None:
        raise RouterMappingError("upnp_location_credentials_forbidden")
    if parsed.query or parsed.fragment:
        raise RouterMappingError("upnp_location_query_fragment_forbidden")
    try:
        parsed_port = parsed.port
    except ValueError as exc:
        raise RouterMappingError("upnp_location_port_invalid") from exc
    if parsed_port is not None and (parsed_port < 1 or parsed_port > _MAX_PORT):
        raise RouterMappingError("upnp_location_port_invalid")
    try:
        host = ipaddress.ip_address(parsed.hostname)
    except ValueError as exc:
        raise RouterMappingError("upnp_location_host_must_be_ip") from exc
    if not _is_allowed_private_gateway_ip(host):
        raise RouterMappingError("upnp_location_private_gateway_required")


def _require_ssdp_location_sender(location: str, sender_host: str) -> None:
    parsed = urlparse(location)
    if parsed.hostname is None:
        raise RouterMappingError("upnp_location_host_must_be_ip")
    try:
        location_ip = ipaddress.ip_address(parsed.hostname)
        sender_ip = ipaddress.ip_address(sender_host)
    except ValueError as exc:
        raise RouterMappingError("upnp_location_sender_invalid") from exc
    if location_ip != sender_ip:
        raise RouterMappingError("upnp_location_sender_mismatch")


def _require_upnp_service_type(value: str) -> str:
    if not isinstance(value, str) or _UPNP_SERVICE_TYPE_RE.fullmatch(value) is None:
        raise RouterMappingError("upnp_service_type_invalid")
    return value


def _validate_rollback_instruction(
    value: Mapping[str, Any],
    *,
    method_used: str | None = None,
    internal_port: int | None = None,
    external_port: int | None = None,
    lease_seconds: int | None = None,
    protocol: str | None = None,
) -> None:
    if not isinstance(value, Mapping):
        raise RouterMappingError("router_mapping_rollback_instruction_invalid")
    if value.get("schema_version") != UPNP_ROUTER_MAPPING_SIDECAR_VERSION:
        raise RouterMappingError("router_mapping_rollback_instruction_invalid")
    if value.get("action") != "DeletePortMapping":
        raise RouterMappingError("router_mapping_rollback_instruction_invalid")
    _require_local_http_url(str(value.get("control_url", "")))
    _require_upnp_service_type(str(value.get("service_type", "")))
    _require_port(value.get("external_port"), "external_port")
    _require_port(value.get("internal_port"), "internal_port")
    if isinstance(value.get("lease_seconds"), bool) or not isinstance(
        value.get("lease_seconds"),
        int,
    ):
        raise RouterMappingError("router_mapping_rollback_instruction_invalid")
    if value["lease_seconds"] < 1 or value["lease_seconds"] > _MAX_LEASE_SECONDS:
        raise RouterMappingError("router_mapping_rollback_instruction_invalid")
    if value.get("method_used") not in _ALLOWED_METHODS:
        raise RouterMappingError("router_mapping_rollback_instruction_invalid")
    internal_client = value.get("internal_client")
    if internal_client is not None:
        try:
            ipaddress.ip_address(internal_client)
        except ValueError as exc:
            raise RouterMappingError("router_mapping_rollback_instruction_invalid") from exc
    actual_protocol = value.get("protocol")
    if not isinstance(actual_protocol, str) or actual_protocol not in {"tcp", "udp"}:
        raise RouterMappingError("router_mapping_rollback_instruction_invalid")
    expected = {
        "external_port": external_port,
        "internal_port": internal_port,
        "lease_seconds": lease_seconds,
        "method_used": method_used,
        "protocol": protocol,
    }
    for field_name, expected_value in expected.items():
        if expected_value is not None and value.get(field_name) != expected_value:
            raise RouterMappingError("router_mapping_rollback_instruction_mismatch")


def _is_allowed_private_gateway_ip(host: ipaddress._BaseAddress) -> bool:
    if host.is_loopback or host.is_link_local or host.is_unspecified or host.is_multicast:
        return False
    networks = (
        _ALLOWED_PRIVATE_IPV4_GATEWAYS
        if isinstance(host, ipaddress.IPv4Address)
        else _ALLOWED_PRIVATE_IPV6_GATEWAYS
    )
    return any(host in network for network in networks)


class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, *_args: object, **_kwargs: object) -> None:
        raise RouterMappingError("router_mapping_redirect_forbidden")


def _urlopen_no_redirect(request_or_url: Request | str, timeout_seconds: float) -> Any:
    return build_opener(_NoRedirect).open(request_or_url, timeout=timeout_seconds)


def _rollback_token(
    request: RouterMappingRequest,
    method: str,
    *,
    external_port: int,
    rollback_instruction: Mapping[str, Any],
) -> str:
    return _rollback_token_from_fields(
        method=method,
        internal_port=request.internal_port,
        external_port=external_port,
        lease_seconds=request.lease_seconds,
        protocol=request.protocol,
        rollback_instruction=rollback_instruction,
    )


def _rollback_token_from_fields(
    *,
    method: str,
    internal_port: int,
    external_port: int,
    lease_seconds: int,
    protocol: str,
    rollback_instruction: Mapping[str, Any],
) -> str:
    payload = {
        "external_port": external_port,
        "internal_port": internal_port,
        "lease_seconds": lease_seconds,
        "method": method,
        "protocol": protocol,
        "rollback_instruction": dict(rollback_instruction),
        "schema_version": UPNP_ROUTER_MAPPING_SIDECAR_VERSION,
    }
    encoded = json.dumps(
        payload,
        allow_nan=False,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _require_port(value: object, field_name: str) -> None:
    if isinstance(value, bool) or not isinstance(value, int):
        raise RouterMappingError(f"{field_name}_must_be_port_int")
    if value < _MIN_PORT or value > _MAX_PORT:
        raise RouterMappingError(f"{field_name}_out_of_range")


def _is_sha256_token(value: str) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(char in "0123456789abcdef" for char in value)
    )


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


__all__ = [
    "ROUTER_MAPPING_NOT_ACTIVATED",
    "RouterMappingError",
    "RouterMappingRequest",
    "RouterMappingResult",
    "RouterMappingTransport",
    "StdlibRouterMappingTransport",
    "UPNP_ROUTER_MAPPING_SIDECAR_VERSION",
    "attempt_router_mapping_via_sidecar",
    "build_upnp_rollback_instruction",
    "remove_upnp_port_mapping",
    "upnp_router_mapping_sidecar_manifest",
]
