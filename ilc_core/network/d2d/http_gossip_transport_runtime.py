# SPDX-License-Identifier: AGPL-3.0-only
"""Phase 568 real HTTP transport wrapper runtime.

This module operationalizes the ratified CDL-061 envelope over real HTTP I/O
without redesigning the node orchestration layer. The first proof lane uses the
explicit ADR-0025 `kind=http` binding and delegates envelope construction and
validation to `gossip_transport.py`.
"""

from __future__ import annotations

import collections
import hashlib
import os
import socket
import ssl
import threading
import urllib.request
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

from ilc_core.network.d2d import gossip_transport
from ilc_core.network.d2d.gossip_peer_registry import (
    GOSSIP_PEER_REGISTRY_VERSION as _GOSSIP_PEER_REGISTRY_CHECK,
    validate_peer_endpoint,
)
from ilc_core.network.d2d.tls_policy import (
    D2D_PUBLIC_MODE_ENV,
    should_disable_tls_verification,
)


HTTP_GOSSIP_TRANSPORT_RUNTIME_VERSION = "http_gossip_transport_runtime_568.v0.1"
TRANSPORT_SECURITY_HARDENING_TOKEN = "transport_security_hardening_1218b"
CDL_061_DEPENDENCY = "cdl_061_ratified_561.v0.1"
GOSSIP_TRANSPORT_DEPENDENCY = "gossip_transport_runtime_558.v0.1"
GOSSIP_PEER_REGISTRY_DEPENDENCY = "gossip_peer_registry_1571.v0.1"
TRANSPORT_KIND_QUIC = "quic"
TRANSPORT_KIND_HTTP = "http"
MAX_INBOUND_PAYLOAD_BYTES = 1_048_576
MAX_INBOUND_READ_CHUNK_BYTES = 64 * 1024
PAYLOAD_TOO_LARGE_TOKEN = "gossip_payload_too_large"
PAYLOAD_READ_TIMEOUT_TOKEN = "gossip_payload_read_timeout"
PAYLOAD_INCOMPLETE_TOKEN = "gossip_payload_incomplete"
CONTENT_LENGTH_INVALID_TOKEN = "gossip_content_length_invalid"
TRANSFER_ENCODING_UNSUPPORTED_TOKEN = "gossip_transfer_encoding_not_supported"
_EVENT_LOG_MAX = 10_000

if gossip_transport.GOSSIP_TRANSPORT_RUNTIME_VERSION != GOSSIP_TRANSPORT_DEPENDENCY:
    import json as _json, sys as _sys
    _sys.stdout.write(
        _json.dumps(
            {
                "ok": False,
                "error": "http_gossip_transport_dep_chain_mismatch",
                "dependency": "gossip_transport_runtime",
                "expected": GOSSIP_TRANSPORT_DEPENDENCY,
                "got": gossip_transport.GOSSIP_TRANSPORT_RUNTIME_VERSION,
            },
            sort_keys=True,
        )
        + "\n"
    )
    _sys.stdout.flush()
    raise RuntimeError("http_gossip_transport_gossip_transport_dependency_mismatch")

if _GOSSIP_PEER_REGISTRY_CHECK != GOSSIP_PEER_REGISTRY_DEPENDENCY:
    import json as _json, sys as _sys
    _sys.stdout.write(
        _json.dumps(
            {
                "ok": False,
                "error": "http_gossip_transport_dep_chain_mismatch",
                "dependency": "gossip_peer_registry",
                "expected": GOSSIP_PEER_REGISTRY_DEPENDENCY,
                "got": _GOSSIP_PEER_REGISTRY_CHECK,
            },
            sort_keys=True,
        )
        + "\n"
    )
    _sys.stdout.flush()
    raise RuntimeError("http_gossip_transport_gossip_peer_registry_dependency_mismatch")


class TransportRuntimeError(RuntimeError):
    """Structured transport runtime failure surface for operator-visible errors."""

    def __init__(self, token: str, transport_kind: str, detail: str) -> None:
        super().__init__(token)
        self.token = token
        self.transport_kind = transport_kind
        self.detail = detail


class _NoRedirectHandler(urllib.request.HTTPRedirectHandler):
    """Reject all HTTP redirects — prevents SSRF via malicious peer redirect responses."""

    def redirect_request(
        self,
        _req: urllib.request.Request,
        _fp: object,
        code: int,
        _msg: str,
        _headers: object,
        newurl: str,
    ) -> None:
        raise TransportRuntimeError(
            "transport_redirect_not_permitted",
            "http",
            f"peer returned redirect {code} to {newurl}",
        )


@dataclass(frozen=True)
class TransportRuntimeConfig:
    transport_kind: str
    bind_host: str
    bind_port: int
    tls_cert_path: str
    tls_key_path: str
    request_timeout_seconds: float = 2.0
    verify_peer_tls: bool = True
    allow_private_peer_endpoints_for_tests: bool = False


def _encode_gossip_payload(payload: bytes | str) -> bytes:
    if isinstance(payload, str):
        return payload.encode("utf-8")
    if isinstance(payload, bytes):
        return payload
    raise ValueError("gossip_payload_must_be_bytes_or_string")


def _canonicalize_headers(headers: dict[str, str]) -> dict[str, str]:
    canonical_by_lower = {key.lower(): key for key in gossip_transport.REQUIRED_HEADERS}
    normalized: dict[str, str] = {}
    for key, value in headers.items():
        if isinstance(key, str):
            normalized[canonical_by_lower.get(key.lower(), key)] = value
        else:
            normalized[key] = value
    return normalized


def _validated_content_length(value: Any) -> int:
    if value is None:
        return 0
    try:
        normalized = int(str(value).strip())
    except (TypeError, ValueError) as exc:
        raise ValueError(CONTENT_LENGTH_INVALID_TOKEN) from exc
    if normalized < 0:
        raise ValueError(CONTENT_LENGTH_INVALID_TOKEN)
    return normalized


def _read_request_body(stream: Any, content_length: int) -> bytes:
    chunks: list[bytes] = []
    remaining = content_length
    while remaining > 0:
        chunk = stream.read(min(MAX_INBOUND_READ_CHUNK_BYTES, remaining))
        if not chunk:
            raise ConnectionError(PAYLOAD_INCOMPLETE_TOKEN)
        chunks.append(chunk)
        remaining -= len(chunk)
    return b"".join(chunks)


def _require_path(value: str, missing_token: str, not_found_token: str) -> Path:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(missing_token)
    path = Path(value)
    if not path.is_file():
        raise ValueError(not_found_token)
    return path


class HttpGossipTransportRuntime:
    """Minimal real-HTTP wrapper around the ratified envelope helpers."""

    def __init__(self, config: TransportRuntimeConfig) -> None:
        self.config = config
        self.state: dict[str, Any] = {
            "transport_kind": config.transport_kind,
            "event_log": collections.deque(maxlen=_EVENT_LOG_MAX),
            "last_error": None,
            "last_status_code": None,
            "bound_port": None,
            "running": False,
        }
        self._server: ThreadingHTTPServer | None = None
        self._thread: threading.Thread | None = None

    def _record(self, event: str, **payload: Any) -> None:
        entry = {"event": event, **payload}
        self.state["event_log"].append(entry)

    def _record_transport_error(self, token: str, detail: str) -> None:
        payload = {
            "token": token,
            "transport_kind": self.state["transport_kind"],
            "detail": detail,
        }
        self.state["last_error"] = payload
        self._record("transport_error", **payload)

    def _normalize_transport_kind(self) -> str:
        kind = self.config.transport_kind
        if not isinstance(kind, str) or not kind.strip():
            raise ValueError("transport_kind_unsupported")
        normalized = kind.strip()
        if normalized not in {TRANSPORT_KIND_HTTP, TRANSPORT_KIND_QUIC}:
            raise ValueError("transport_kind_unsupported")
        return normalized

    def _validated_content_length(self, value: Any) -> int:
        return _validated_content_length(value)

    def _server_ssl_context(self) -> ssl.SSLContext:
        cert_path = _require_path(
            self.config.tls_cert_path,
            "tls_cert_path_required",
            "tls_cert_path_not_found",
        )
        key_path = _require_path(
            self.config.tls_key_path,
            "tls_key_path_required",
            "tls_key_path_not_found",
        )
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        try:
            context.load_cert_chain(str(cert_path), str(key_path))
        except ssl.SSLError as exc:
            raise ValueError("tls_context_load_failed") from exc
        return context

    def _client_ssl_context(self) -> ssl.SSLContext:
        _require_path(
            self.config.tls_cert_path,
            "tls_cert_path_required",
            "tls_cert_path_not_found",
        )
        _require_path(
            self.config.tls_key_path,
            "tls_key_path_required",
            "tls_key_path_not_found",
        )
        context = ssl.create_default_context()
        if should_disable_tls_verification(
            insecure_requested=not self.config.verify_peer_tls,
            stacklevel=2,
        ):
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
        elif not self.config.verify_peer_tls and os.environ.get(D2D_PUBLIC_MODE_ENV) == "1":
            self._record(
                "tls_insecure_bypass_ignored",
                reason="public_mode_requires_tls_verification",
            )
        return context

    def start(self) -> None:
        kind = self._normalize_transport_kind()
        if kind == TRANSPORT_KIND_QUIC:
            raise ValueError("transport_kind_quic_not_operationalized")
        if self._server is not None:
            return
        ssl_context = self._server_ssl_context()
        self._record("listener_starting", transport_kind=kind)
        runtime = self

        class _TimedThreadingHTTPServer(ThreadingHTTPServer):
            daemon_threads = True

            def get_request(self) -> tuple[socket.socket, tuple[str, int]]:
                request, client_address = super().get_request()
                request.settimeout(runtime.config.request_timeout_seconds)
                return request, client_address

        class _Handler(BaseHTTPRequestHandler):
            def do_POST(self) -> None:  # noqa: N802
                headers = {key: value for key, value in self.headers.items()}
                transfer_encoding = self.headers.get("Transfer-Encoding")
                if transfer_encoding is not None:
                    runtime._record(
                        "incoming_envelope_rejected",
                        token=TRANSFER_ENCODING_UNSUPPORTED_TOKEN,
                        transfer_encoding=str(transfer_encoding),
                    )
                    runtime.state["last_status_code"] = gossip_transport.HTTP_STATUS_ENVELOPE_ERROR
                    self.close_connection = True
                    self.send_response(gossip_transport.HTTP_STATUS_ENVELOPE_ERROR)
                    self.end_headers()
                    return
                try:
                    content_length = _validated_content_length(self.headers.get("Content-Length"))
                except ValueError as exc:
                    token = str(exc)
                    runtime._record("incoming_envelope_rejected", token=token)
                    runtime.state["last_status_code"] = gossip_transport.HTTP_STATUS_ENVELOPE_ERROR
                    self.send_response(gossip_transport.HTTP_STATUS_ENVELOPE_ERROR)
                    self.end_headers()
                    return
                if content_length > MAX_INBOUND_PAYLOAD_BYTES:
                    runtime._record(
                        "incoming_envelope_rejected",
                        token=PAYLOAD_TOO_LARGE_TOKEN,
                        content_length=content_length,
                    )
                    runtime.state["last_status_code"] = gossip_transport.HTTP_STATUS_ENVELOPE_ERROR
                    self.close_connection = True
                    self.send_response(gossip_transport.HTTP_STATUS_ENVELOPE_ERROR)
                    self.end_headers()
                    return
                payload = b""
                if content_length:
                    try:
                        payload = _read_request_body(self.rfile, content_length)
                    except socket.timeout:
                        runtime._record(
                            "incoming_envelope_rejected",
                            token=PAYLOAD_READ_TIMEOUT_TOKEN,
                            content_length=content_length,
                        )
                        runtime.state["last_status_code"] = gossip_transport.HTTP_STATUS_ENVELOPE_ERROR
                        status_code = gossip_transport.HTTP_STATUS_ENVELOPE_ERROR
                    except ConnectionError:
                        runtime._record(
                            "incoming_envelope_rejected",
                            token=PAYLOAD_INCOMPLETE_TOKEN,
                            content_length=content_length,
                        )
                        runtime.state["last_status_code"] = gossip_transport.HTTP_STATUS_ENVELOPE_ERROR
                        status_code = gossip_transport.HTTP_STATUS_ENVELOPE_ERROR
                    else:
                        status_code = runtime.handle_gossip_request(
                            self.path,
                            headers,
                            content_length=content_length,
                            payload=payload,
                        )
                else:
                    status_code = runtime.handle_gossip_request(
                        self.path,
                        headers,
                        content_length=content_length,
                        payload=payload,
                    )
                self.close_connection = True
                self.send_response(status_code)
                self.end_headers()

            def log_message(self, format: str, *args: object) -> None:  # noqa: A002
                return

        server = _TimedThreadingHTTPServer((self.config.bind_host, self.config.bind_port), _Handler)
        server.socket = ssl_context.wrap_socket(server.socket, server_side=True)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        self._server = server
        self._thread = thread
        self.state["bound_port"] = int(server.server_address[1])
        self.state["running"] = True
        self.state["explicit_fallback_proof"] = kind == TRANSPORT_KIND_HTTP
        self._record(
            "listener_ready",
            transport_kind=kind,
            bind_host=self.config.bind_host,
            bind_port=self.state["bound_port"],
        )

    def stop(self) -> None:
        if self._server is None:
            self.state["running"] = False
            return
        self._record("listener_stopping", transport_kind=self.state["transport_kind"])
        self._server.shutdown()
        self._server.server_close()
        if self._thread is not None:
            self._thread.join(timeout=2.0)
        self._server = None
        self._thread = None
        self.state["running"] = False

    def handle_gossip_request(
        self,
        path: str,
        headers: dict[str, str],
        *,
        content_length: int | None = None,
        payload: bytes | None = None,
    ) -> int:
        normalized_headers = _canonicalize_headers(headers)
        if content_length is not None and content_length > MAX_INBOUND_PAYLOAD_BYTES:
            self._record(
                "incoming_envelope_rejected",
                token=PAYLOAD_TOO_LARGE_TOKEN,
                content_length=content_length,
            )
            self.state["last_status_code"] = gossip_transport.HTTP_STATUS_ENVELOPE_ERROR
            return gossip_transport.HTTP_STATUS_ENVELOPE_ERROR
        if payload is not None:
            if not isinstance(payload, bytes):
                self._record("incoming_envelope_rejected", token="gossip_payload_must_be_bytes")
                self.state["last_status_code"] = gossip_transport.HTTP_STATUS_ENVELOPE_ERROR
                return gossip_transport.HTTP_STATUS_ENVELOPE_ERROR
            if content_length is not None and len(payload) != content_length:
                self._record(
                    "incoming_envelope_rejected",
                    token=PAYLOAD_INCOMPLETE_TOKEN,
                    content_length=content_length,
                    payload_bytes=len(payload),
                )
                self.state["last_status_code"] = gossip_transport.HTTP_STATUS_ENVELOPE_ERROR
                return gossip_transport.HTTP_STATUS_ENVELOPE_ERROR
            if len(payload) > MAX_INBOUND_PAYLOAD_BYTES:
                self._record(
                    "incoming_envelope_rejected",
                    token=PAYLOAD_TOO_LARGE_TOKEN,
                    content_length=len(payload),
                )
                self.state["last_status_code"] = gossip_transport.HTTP_STATUS_ENVELOPE_ERROR
                return gossip_transport.HTTP_STATUS_ENVELOPE_ERROR
        try:
            gossip_type = str(normalized_headers["ILC-Gossip-Type"]).strip()
            expected_path = gossip_transport.gossip_request_path(gossip_type)
            if path != expected_path:
                self._record("incoming_envelope_rejected", token="gossip_request_path_mismatch")
                self.state["last_status_code"] = gossip_transport.HTTP_STATUS_ENVELOPE_ERROR
                return gossip_transport.HTTP_STATUS_ENVELOPE_ERROR
            gossip_transport.validate_gossip_headers(normalized_headers)
        except (KeyError, ValueError) as exc:
            token = str(exc) or exc.__class__.__name__
            self._record("incoming_envelope_rejected", token=token)
            self.state["last_status_code"] = gossip_transport.HTTP_STATUS_ENVELOPE_ERROR
            return gossip_transport.HTTP_STATUS_ENVELOPE_ERROR

        event_payload: dict[str, Any] = {"path": path}
        if payload is not None:
            event_payload.update(
                {
                    "payload_bytes": len(payload),
                    "payload_sha256": hashlib.sha256(payload).hexdigest(),
                    "signature_sha256": hashlib.sha256(
                        str(normalized_headers["ILC-Signature"]).encode("utf-8")
                    ).hexdigest(),
                }
            )
        self._record("incoming_envelope_buffered", **event_payload)
        self.state["last_status_code"] = gossip_transport.HTTP_STATUS_BUFFERED
        return gossip_transport.HTTP_STATUS_BUFFERED

    def send_gossip(
        self,
        peer_endpoint: str,
        gossip_type: str,
        channel: str,
        epoch: int,
        signature: str,
        payload: bytes | str = b"",
        *,
        content_type: str = "application/cbor",
    ) -> int:
        kind = self._normalize_transport_kind()
        if kind == TRANSPORT_KIND_QUIC:
            raise ValueError("transport_kind_quic_not_operationalized")
        if kind != TRANSPORT_KIND_HTTP:
            raise ValueError("transport_kind_unsupported")

        normalized_endpoint = validate_peer_endpoint(
            peer_endpoint,
            allow_private_address_literals=self.config.allow_private_peer_endpoints_for_tests,
        )
        request_path = gossip_transport.gossip_request_path(gossip_type)
        headers = gossip_transport.build_gossip_headers(
            gossip_type=gossip_type,
            channel=channel,
            epoch=epoch,
            hop_count=gossip_transport.HOP_COUNT_SINGLE,
            signature=signature,
            content_type=content_type,
        )
        request_body = _encode_gossip_payload(payload)

        request = urllib.request.Request(
            url=f"{normalized_endpoint}{request_path}",
            data=request_body,
            headers=headers,
            method="POST",
        )
        ssl_context = self._client_ssl_context()
        _opener = urllib.request.build_opener(
            _NoRedirectHandler,
            urllib.request.HTTPSHandler(context=ssl_context),
        )
        try:
            with _opener.open(request, timeout=self.config.request_timeout_seconds) as response:
                status_code = int(response.getcode())
        except Exception as exc:  # pragma: no cover - exercised in transport hardening tests
            self._record_transport_error("transport_request_failed", exc.__class__.__name__)
            raise TransportRuntimeError(
                "transport_request_failed",
                kind,
                exc.__class__.__name__,
            ) from exc

        self.state["last_status_code"] = status_code
        self._record(
            "outgoing_gossip_sent",
            endpoint=normalized_endpoint,
            path=request_path,
            status_code=status_code,
            transport_kind=kind,
        )
        return status_code
