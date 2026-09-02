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
from urllib.error import URLError
from urllib.parse import urlparse
from urllib.request import HTTPRedirectHandler, build_opener

from ilc_core.network.connectivity_mode import (
    ConnectivityModeValidationError,
    ConnectivityReceipt,
    ProbeResult,
    connectivity_mode_from_probe_result,
)


NAT_PROBE_ENGINE_TOKEN = "nat_probe_engine_committed_GAP_AUTO_NAT_TRAVERSAL_IMPL_00"
CONNECTIVITY_AUDIT_FIX_TOKEN = (
    "connectivity_audit_fix_committed_GAP_CONNECTIVITY_AUDIT_FIX_00"
)
NAT_PROBE_SCHEMA_VERSION = "nat_probe_engine_GAP_AUTO_NAT_TRAVERSAL_IMPL_00.v0.1"
NAT_TRAVERSAL_POLICY_VERSION = (
    "ilc_auto_nat_traversal_policy_GAP_AUTO_NAT_TRAVERSAL_POLICY_00.v0.1"
)
UPNP_SIDECAR_UNAVAILABLE = "UPnP sidecar not available — reinstall ilc-core"

_DEFAULT_TIMEOUT_SECONDS = 3.0
_DEFAULT_INTERNAL_PORT = 50151
_MIN_PROTOCOL_PORT = 1
_MAX_OBSERVER_RESPONSE_BYTES = 8192
_MAX_ENDPOINT_CHARS = 512
_AGENT_ID_HEX_LENGTH = 96
_MAX_EPOCH = (1 << 64) - 1
_ATTEMPT_METHODS = frozenset(
    {"ilc_observer_detection", "pcp", "nat_pmp", "upnp_igd", "relay_fallback"}
)
_ATTEMPT_RESULTS = frozenset({"success", "failure", "not_attempted", "skipped_no_opt_in"})
_RELAY_CLIENT_INIT_FIELDS = frozenset(
    {
        "agent_id",
        "invite_id",
        "invite_nullifier",
        "invite_pop",
        "invite_pop_epoch",
        "network_id",
        "software_version",
        "tls_cert_der_sha256",
    }
)


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
class NatTraversalAttemptReceipt:
    """Policy receipt for one observer, relay, or explicit router-mapping attempt."""

    agent_id: str | None
    attempt_timestamp_epoch: int
    method: str
    result: str
    external_endpoint: str | None
    internal_port: int
    lease_seconds: int
    rollback_instruction: dict[str, Any] | None
    observer_ref: str | None
    firewall_mutation_attempted: bool
    policy_version: str = NAT_TRAVERSAL_POLICY_VERSION

    def __post_init__(self) -> None:
        if self.agent_id is not None:
            _require_agent_id(self.agent_id, "agent_id")
        _require_epoch(self.attempt_timestamp_epoch, "attempt_timestamp_epoch")
        if self.method not in _ATTEMPT_METHODS:
            raise NatProbeError("nat_traversal_attempt_method_invalid")
        if self.result not in _ATTEMPT_RESULTS:
            raise NatProbeError("nat_traversal_attempt_result_invalid")
        if self.external_endpoint is not None:
            _require_endpoint_string(self.external_endpoint, "external_endpoint")
        _require_port(self.internal_port, "internal_port")
        if isinstance(self.lease_seconds, bool) or not isinstance(self.lease_seconds, int):
            raise NatProbeError("lease_seconds_must_be_int")
        if self.lease_seconds < 0:
            raise NatProbeError("lease_seconds_out_of_range")
        if self.rollback_instruction is not None and not isinstance(
            self.rollback_instruction,
            dict,
        ):
            raise NatProbeError("rollback_instruction_must_be_object")
        if self.observer_ref is not None and (
            not isinstance(self.observer_ref, str) or not self.observer_ref.strip()
        ):
            raise NatProbeError("observer_ref_invalid")
        _require_bool(self.firewall_mutation_attempted, "firewall_mutation_attempted")
        if self.firewall_mutation_attempted and self.rollback_instruction is None:
            raise NatProbeError("firewall_mutation_requires_rollback_instruction")
        if self.firewall_mutation_attempted and self.method not in {
            "pcp",
            "nat_pmp",
            "upnp_igd",
        }:
            raise NatProbeError("firewall_mutation_method_invalid")
        if self.result in {"not_attempted", "skipped_no_opt_in"}:
            if self.external_endpoint is not None:
                raise NatProbeError("non_attempt_endpoint_forbidden")
            if self.rollback_instruction is not None:
                raise NatProbeError("non_attempt_rollback_forbidden")
            if self.firewall_mutation_attempted:
                raise NatProbeError("non_attempt_mutation_forbidden")
            if self.lease_seconds != 0:
                raise NatProbeError("non_attempt_lease_forbidden")
        if self.result == "skipped_no_opt_in" and self.method not in {
            "pcp",
            "nat_pmp",
            "upnp_igd",
        }:
            raise NatProbeError("skipped_no_opt_in_method_invalid")
        if self.result == "not_attempted" and self.method != "ilc_observer_detection":
            raise NatProbeError("not_attempted_method_invalid")
        if self.lease_seconds > 0 and self.method not in {"pcp", "nat_pmp", "upnp_igd"}:
            raise NatProbeError("lease_seconds_method_invalid")
        if (
            self.result == "success"
            and self.method == "relay_fallback"
            and self.external_endpoint is None
        ):
            raise NatProbeError("relay_success_endpoint_required")
        if self.policy_version != NAT_TRAVERSAL_POLICY_VERSION:
            raise NatProbeError("nat_traversal_policy_version_invalid")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class NatProbeReport:
    """Deterministic local receipt for one NAT probe run."""

    connectivity_receipt: ConnectivityReceipt
    probe_result: ProbeResult
    observer_endpoint_url: str | None
    firewall_mutation_attempted: bool
    router_mapping: dict[str, Any] | None
    attempt_receipts: tuple[NatTraversalAttemptReceipt, ...]
    warnings: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "attempt_receipts": [
                attempt_receipt.to_dict() for attempt_receipt in self.attempt_receipts
            ],
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
        agent_id: str | None = None,
    ) -> None:
        self.observers = tuple(_coerce_observer(observer) for observer in observers)
        if relay_endpoint is not None:
            _require_endpoint_string(relay_endpoint, "relay_endpoint")
        self.relay_endpoint = relay_endpoint
        self.relay_server_url = relay_server_url
        self.relay_admission_material = dict(relay_admission_material or {})
        self._relay_client_factory = relay_client_factory
        if agent_id is not None:
            _require_agent_id(agent_id, "agent_id")
        self.agent_id = agent_id
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

        attempt_router_mapping = _require_bool(
            attempt_router_mapping,
            "attempt_router_mapping",
        )
        _require_epoch(probe_epoch, "probe_epoch")
        warnings: list[str] = []
        attempt_receipts: list[NatTraversalAttemptReceipt] = []
        observed_ip: str | None = None
        observed_port: int | None = None
        observer_agent_id: str | None = None
        observer_url: str | None = None
        has_public_ip = False
        has_outbound_connectivity = False

        for observer in self.observers:
            try:
                payload = self._observer_fetcher(observer.endpoint_url, self.timeout_seconds)
                observed_ip, observed_port = _parse_observer_payload(payload)
                has_outbound_connectivity = True
                observer_agent_id = payload.get("observer_agent_id") or observer.observer_agent_id
                if observer_agent_id is not None:
                    _require_agent_id(observer_agent_id, "observer_agent_id")
                observer_url = observer.endpoint_url
                if self._hole_puncher(observed_ip, observed_port, self.timeout_seconds):
                    has_public_ip = True
                    attempt_receipts.append(
                        self._attempt_receipt(
                            method="ilc_observer_detection",
                            result="success",
                            probe_epoch=probe_epoch,
                            external_endpoint=_endpoint(observed_ip, observed_port),
                            observer_ref=observer_agent_id or observer.endpoint_url,
                        )
                    )
                else:
                    warnings.append("probe_observer_endpoint_not_confirmed_direct")
                    attempt_receipts.append(
                        self._attempt_receipt(
                            method="ilc_observer_detection",
                            result="success",
                            probe_epoch=probe_epoch,
                            observer_ref=observer_agent_id or observer.endpoint_url,
                        )
                    )
                    observed_ip = None
                    observed_port = None
                break
            except (NatProbeError, OSError, TimeoutError, URLError) as exc:
                warnings.append(f"probe_observer_failed:{observer.endpoint_url}:{type(exc).__name__}")
                attempt_receipts.append(
                    self._attempt_receipt(
                        method="ilc_observer_detection",
                        result="failure",
                        probe_epoch=probe_epoch,
                        observer_ref=observer.observer_agent_id or observer.endpoint_url,
                    )
                )

        router_mapping_payload: dict[str, Any] | None = None
        firewall_mutation_attempted = False
        direct_mapping_candidate = False

        if not has_public_ip and attempt_router_mapping:
            mapping = self._attempt_router_mapping(warnings)
            router_mapping_payload = mapping.to_dict()
            firewall_mutation_attempted = mapping.firewall_mutation_attempted
            if mapping.success:
                warnings.append("router_mapping_created_external_verification_pending")
                attempt_receipts.append(
                    self._attempt_receipt(
                        method=mapping.method_used,
                        result="success",
                        probe_epoch=probe_epoch,
                        lease_seconds=mapping.lease_seconds,
                        rollback_instruction=mapping.rollback_instruction,
                        firewall_mutation_attempted=mapping.firewall_mutation_attempted,
                    )
                )
            else:
                attempt_receipts.append(
                    self._attempt_receipt(
                        method=mapping.method_used or "upnp_igd",
                        result="failure",
                        probe_epoch=probe_epoch,
                        lease_seconds=mapping.lease_seconds,
                        rollback_instruction=mapping.rollback_instruction,
                        firewall_mutation_attempted=mapping.firewall_mutation_attempted,
                    )
                )
        elif not attempt_router_mapping:
            attempt_receipts.append(
                self._attempt_receipt(
                    method="upnp_igd",
                    result="skipped_no_opt_in",
                    probe_epoch=probe_epoch,
                )
            )

        if not self.observers:
            warnings.append("no_ilc_probe_observer_configured")
            attempt_receipts.append(
                self._attempt_receipt(
                    method="ilc_observer_detection",
                    result="not_attempted",
                    probe_epoch=probe_epoch,
                )
            )

        relay_endpoint = None
        if self.relay_endpoint is not None:
            warnings.append("configured_relay_endpoint_unverified")
        if (
            not has_public_ip
            and not direct_mapping_candidate
            and relay_endpoint is None
        ):
            relay_endpoint = self._request_relay_slot_if_active(probe_epoch, warnings)
            if relay_endpoint is not None:
                has_outbound_connectivity = True
                attempt_receipts.append(
                    self._attempt_receipt(
                        method="relay_fallback",
                        result="success",
                        probe_epoch=probe_epoch,
                        external_endpoint=relay_endpoint,
                    )
                )
            elif self.relay_server_url or self.relay_admission_material:
                attempt_receipts.append(
                    self._attempt_receipt(
                        method="relay_fallback",
                        result="failure",
                        probe_epoch=probe_epoch,
                    )
                )

        probe_result = ProbeResult(
            has_public_ip=has_public_ip,
            observed_ip=observed_ip,
            observed_port=observed_port,
            relay_available=relay_endpoint is not None,
            validator_participation_enabled=self.validator_participation_enabled,
            has_outbound_connectivity=has_outbound_connectivity,
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
            attempt_receipts=tuple(attempt_receipts),
            warnings=tuple(warnings),
        )

    def _attempt_receipt(
        self,
        *,
        method: str,
        result: str,
        probe_epoch: int,
        external_endpoint: str | None = None,
        lease_seconds: int = 0,
        rollback_instruction: dict[str, Any] | None = None,
        observer_ref: str | None = None,
        firewall_mutation_attempted: bool = False,
    ) -> NatTraversalAttemptReceipt:
        return NatTraversalAttemptReceipt(
            agent_id=self.agent_id,
            attempt_timestamp_epoch=probe_epoch,
            method=method,
            result=result,
            external_endpoint=external_endpoint,
            internal_port=self.internal_port,
            lease_seconds=lease_seconds,
            rollback_instruction=rollback_instruction,
            observer_ref=observer_ref,
            firewall_mutation_attempted=firewall_mutation_attempted,
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
            relay_material, admission_signature = self._relay_client_material(
                relay_module,
                probe_epoch=probe_epoch,
            )
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
        except (relay_module.RelayClientError, OSError, TimeoutError) as exc:
            error = str(exc) or type(exc).__name__
            warnings.append(f"relay_slot_request_failed:{error}")
            return None

    def _relay_client_material(
        self,
        relay_module: Any,
        *,
        probe_epoch: int,
    ) -> tuple[dict[str, Any], str | None]:
        relay_material = dict(self.relay_admission_material)
        admission_signature = relay_material.pop("relay_admission_signature", None)
        relay_material.pop("relay_admission_payload_ref", None)
        material_base_url = relay_material.pop("relay_base_url", None)
        if material_base_url is not None and material_base_url != self.relay_server_url:
            raise relay_module.RelayClientError("relay_material_base_url_mismatch")
        material_port = relay_material.pop("requested_internal_port", None)
        if material_port is not None and material_port != self.internal_port:
            raise relay_module.RelayClientError("relay_material_internal_port_mismatch")
        material_protocol = relay_material.pop("requested_protocol", None)
        if material_protocol is not None and material_protocol != "quic":
            raise relay_module.RelayClientError("relay_material_protocol_mismatch")
        material_epoch = relay_material.pop("admission_epoch", None)
        if material_epoch is not None and material_epoch != probe_epoch:
            raise relay_module.RelayClientError("relay_material_admission_epoch_mismatch")
        unknown_fields = sorted(set(relay_material) - _RELAY_CLIENT_INIT_FIELDS)
        if unknown_fields:
            raise relay_module.RelayClientError("relay_material_unknown_fields")
        return relay_material, admission_signature

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
            has_outbound_connectivity=False,
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
    ip_address = ipaddress.ip_address(ip_value)
    family = socket.AF_INET6 if ip_address.version == 6 else socket.AF_INET
    with socket.socket(family, socket.SOCK_DGRAM) as sock:
        sock.settimeout(timeout_seconds)
        address: tuple[Any, ...] = (
            (ip_value, port_value, 0, 0)
            if family == socket.AF_INET6
            else (ip_value, port_value)
        )
        sock.sendto(b"ilc-nat-probe-v1", address)
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
    try:
        parsed = ipaddress.ip_address(ip_value)
    except ValueError as exc:
        raise NatProbeError("endpoint_ip_invalid") from exc
    if isinstance(parsed, ipaddress.IPv6Address):
        return f"[{ip_value}]:{port_value}"
    return f"{ip_value}:{port_value}"


def _require_endpoint_string(value: object, field_name: str) -> None:
    if not isinstance(value, str):
        raise NatProbeError(f"{field_name}_must_be_host_port")
    if len(value) > _MAX_ENDPOINT_CHARS or not value.strip():
        raise NatProbeError(f"{field_name}_invalid")
    host, port_text = _split_host_port(value, field_name)
    if any(char.isspace() for char in host) or any(char in host for char in "/?#@"):
        raise NatProbeError(f"{field_name}_host_invalid")
    _require_port(int(port_text) if port_text.isdecimal() else port_text, field_name)


def _sidecar_unavailable_result() -> Any:
    class _UnavailableResult:
        firewall_mutation_attempted = False
        success = False
        external_port = None
        internal_port = None
        lease_seconds = 0
        method_used = None
        protocol = None
        rollback_instruction = None
        rollback_token = None

        def to_dict(self) -> dict[str, Any]:
            return {
                "error": UPNP_SIDECAR_UNAVAILABLE,
                "external_port": self.external_port,
                "firewall_mutation_attempted": self.firewall_mutation_attempted,
                "internal_port": self.internal_port,
                "lease_seconds": self.lease_seconds,
                "method_used": self.method_used,
                "protocol": self.protocol,
                "rollback_instruction": self.rollback_instruction,
                "rollback_token": self.rollback_token,
                "success": self.success,
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
    # NAT probe endpoint validation accepts the full protocol port range.
    # Router-mapping mutation is stricter and rejects privileged ports in the
    # UPnP sidecar before any firewall mutation can be attempted.
    if value < _MIN_PROTOCOL_PORT or value > 65535:
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


def _split_host_port(value: str, field_name: str) -> tuple[str, str]:
    if value.startswith("["):
        closing = value.find("]")
        if closing <= 1 or closing + 1 >= len(value) or value[closing + 1] != ":":
            raise NatProbeError(f"{field_name}_must_be_host_port")
        return value[1:closing], value[closing + 2 :]
    host, separator, port_text = value.rpartition(":")
    if not separator or not host or not port_text or ":" in host:
        raise NatProbeError(f"{field_name}_must_be_host_port")
    return host, port_text


class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, *_args: object, **_kwargs: object) -> None:
        raise NatProbeError("probe_observer_redirect_forbidden")


def _urlopen_no_redirect(url: str, timeout_seconds: float) -> Any:
    return build_opener(_NoRedirect).open(url, timeout=timeout_seconds)


__all__ = [
    "NAT_PROBE_ENGINE_TOKEN",
    "NAT_PROBE_SCHEMA_VERSION",
    "NAT_TRAVERSAL_POLICY_VERSION",
    "CONNECTIVITY_AUDIT_FIX_TOKEN",
    "UPNP_SIDECAR_UNAVAILABLE",
    "NatProbeEngine",
    "NatProbeError",
    "NatProbeReport",
    "NatTraversalAttemptReceipt",
    "ProbeObserver",
]
