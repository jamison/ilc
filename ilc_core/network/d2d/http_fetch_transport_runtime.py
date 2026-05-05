"""Phase 902 — CDL-077 fetch HTTP transport runtime.

Exposes WANT-HAVE and WANT-BLOCK fetch endpoints over HTTP, handling exactly
two POST paths:
    /fetch/want-have   — lightweight availability probe (no rate limit)
    /fetch/want-block  — full record delivery (rate-limited per requester_id)

Follows the same design patterns as http_gossip_transport_runtime (Phase 568)
but serves fetch paths only.  Runs as a separate server from the gossip server
because CDL-061 gossip routing is gossip-type-keyed and cannot dispatch fetch
paths.

Configuration via environment:
    ILC_TRUTH_GRAPH_STORE_PATH — path to LMDB store (required to serve records)
    HTTP_FETCH_BIND_HOST       — bind host (default: 127.0.0.1)
    HTTP_FETCH_BIND_PORT       — bind port (default: 0 = OS assigns)
"""

from __future__ import annotations

import json
import socket
import threading
from dataclasses import dataclass, field
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

from ilc_core.network.d2d import truth_primitive_fetch_runtime as _fetch_rt
from ilc_core.network.d2d.persistent_fetch_rate_limiter_runtime import (
    PersistentFetchRateLimiter,
)

HTTP_FETCH_TRANSPORT_RUNTIME_VERSION = "http_fetch_transport_runtime_1212.v0.2"
CDL_077_DEPENDENCY = "cdl_077_want_have_want_block_fetch.v0.1"
FETCH_RUNTIME_DEPENDENCY = "truth_primitive_fetch_runtime_901.v0.1"
PERSISTENT_RATE_LIMITER_DEPENDENCY = "persistent_fetch_rate_limiter_runtime_1202.v0.1"
PERSISTENT_RATE_LIMITER_TRANSPORT_WIRING_TOKEN = (
    "persistent_rate_limiter_transport_wiring_committed_phase_1212"
)
TRANSPORT_ABUSE_CIRCUIT_BREAKER_TOKEN = (
    "transport_abuse_circuit_breaker_not_final_scaling_policy"
)
RECIPROCAL_FETCH_ADMISSION_CARRY_FORWARD = "reciprocal_fetch_admission_model_required"

_MAX_INBOUND_BYTES = 65_536  # 64 KiB — request body OOM guard
_CONTENT_LENGTH_MISSING_TOKEN = "fetch_content_length_missing"
_CONTENT_LENGTH_INVALID_TOKEN = "fetch_content_length_invalid"
_CONTENT_TOO_LARGE_TOKEN = "fetch_content_too_large"

# Dep-chain guard
if _fetch_rt.TRUTH_PRIMITIVE_FETCH_RUNTIME_VERSION != FETCH_RUNTIME_DEPENDENCY:
    raise RuntimeError("http_fetch_transport_runtime_fetch_dep_mismatch")


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------


@dataclass
class FetchTransportConfig:
    bind_host: str = "127.0.0.1"
    bind_port: int = 0  # 0 → OS assigns free port
    store_path: str = ""
    rate_limit_per_minute: int = _fetch_rt.WANT_BLOCK_RATE_LIMIT_PER_MINUTE
    rate_limit_window_id: int = 0
    persistent_limiter_path: Path | None = None
    request_timeout_seconds: float = 5.0
    event_log: list[dict[str, Any]] = field(default_factory=list)


class _PersistentFetchRateLimiterAdapter:
    """Adapter matching the in-memory limiter API expected by the fetch handler."""

    def __init__(
        self,
        limiter: PersistentFetchRateLimiter,
        path: Path,
        window_id: int,
    ) -> None:
        self.limiter = limiter
        self.path = path
        self.window_id = window_id

    def check_and_consume(self, requester_id: str) -> bool:
        allowed = self.limiter.check_and_consume(requester_id, self.window_id)
        if allowed:
            self.limiter.save(self.path)
        return allowed


# ---------------------------------------------------------------------------
# Runtime
# ---------------------------------------------------------------------------


class HttpFetchTransportRuntime:
    """Threaded HTTP server for CDL-077 fetch endpoints.

    Usage:
        config = FetchTransportConfig(store_path="path/to/store.lmdb")
        runtime = HttpFetchTransportRuntime(config)
        runtime.start()
        # ... tests / service use ...
        runtime.stop()

    state["bound_port"] is set after start() and reflects the actual port.
    state["running"] is True while the server is active.
    """

    def __init__(self, config: FetchTransportConfig) -> None:
        self.config = config
        self.state: dict[str, Any] = {
            "running": False,
            "bound_port": config.bind_port,
            "last_status_code": None,
            "requests_served": 0,
        }
        self._server: ThreadingHTTPServer | None = None
        self._thread: threading.Thread | None = None
        self._persistent_limiter_path = config.persistent_limiter_path
        self._persistent_rate_limiter: PersistentFetchRateLimiter | None = None
        self._rate_limiter = self._build_rate_limiter()
        self._store: Any = None  # opened lazily on start() if store_path is set

    def _record(self, event: str, **kwargs: Any) -> None:
        entry = {"event": event, **kwargs}
        self.config.event_log.append(entry)

    def _build_rate_limiter(self) -> Any:
        if self._persistent_limiter_path is None:
            return _fetch_rt.FetchRateLimiter(self.config.rate_limit_per_minute)
        if (
            not isinstance(self.config.rate_limit_window_id, int)
            or isinstance(self.config.rate_limit_window_id, bool)
            or self.config.rate_limit_window_id < 0
        ):
            raise ValueError("fetch_rate_limit_window_id_invalid")

        path = Path(self._persistent_limiter_path)
        state_file_existed = path.exists()
        limiter = PersistentFetchRateLimiter.load(path)
        self._persistent_rate_limiter = limiter
        if not state_file_existed or limiter.fail_closed:
            self._record(
                "fetch_rate_limiter_degraded",
                token="persistent_rate_limiter_state_reset_on_load_failure",
            )
        return _PersistentFetchRateLimiterAdapter(
            limiter,
            path,
            self.config.rate_limit_window_id,
        )

    def _open_store(self) -> Any:
        """Open LMDB store if store_path is configured, else return None."""
        if not self.config.store_path:
            return None
        from ilc_core.epistemic.truth_primitive_graph_store import TruthPrimitiveGraphStore
        return TruthPrimitiveGraphStore(self.config.store_path)

    def start(self) -> None:
        """Start the fetch HTTP server on a background thread."""
        self._store = self._open_store()
        runtime = self

        class _TimedServer(ThreadingHTTPServer):
            def get_request(self) -> tuple[socket.socket, tuple[str, int]]:
                request, client_address = super().get_request()
                request.settimeout(runtime.config.request_timeout_seconds)
                return request, client_address

        class _Handler(BaseHTTPRequestHandler):
            def do_POST(self) -> None:  # noqa: N802
                content_length_raw = self.headers.get("Content-Length")
                if content_length_raw is None:
                    runtime._record("fetch_request_rejected", token=_CONTENT_LENGTH_MISSING_TOKEN)
                    self.send_response(400)
                    self.end_headers()
                    return
                try:
                    content_length = int(content_length_raw)
                    if content_length < 0:
                        raise ValueError("negative")
                except (ValueError, TypeError):
                    runtime._record("fetch_request_rejected", token=_CONTENT_LENGTH_INVALID_TOKEN)
                    self.send_response(400)
                    self.end_headers()
                    return
                if content_length > _MAX_INBOUND_BYTES:
                    runtime._record("fetch_request_rejected", token=_CONTENT_TOO_LARGE_TOKEN)
                    self.send_response(413)
                    self.end_headers()
                    return

                try:
                    body = self.rfile.read(content_length)
                except Exception:
                    self.send_response(400)
                    self.end_headers()
                    return

                path = self.path
                if path == _fetch_rt.WANT_HAVE_PATH:
                    status, resp_body = _fetch_rt.handle_want_have_request(
                        body, runtime._store
                    )
                elif path == _fetch_rt.WANT_BLOCK_PATH:
                    status, resp_body = _fetch_rt.handle_want_block_request(
                        body, runtime._store, runtime._rate_limiter
                    )
                else:
                    resp_body = json.dumps(
                        {"token": "fetch_unknown_path", "path": path}, sort_keys=True
                    ).encode()
                    status = 404

                runtime.state["last_status_code"] = status
                runtime.state["requests_served"] += 1
                runtime._record("fetch_request_served", path=path, status=status)

                self.send_response(status)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(resp_body)))
                self.end_headers()
                self.wfile.write(resp_body)

            def log_message(self, format: str, *args: object) -> None:  # noqa: A002
                return  # suppress default stderr logging

        server = _TimedServer((self.config.bind_host, self.config.bind_port), _Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        self._server = server
        self._thread = thread
        self.state["bound_port"] = int(server.server_address[1])
        self.state["running"] = True
        self._record(
            "fetch_listener_ready",
            bind_host=self.config.bind_host,
            bind_port=self.state["bound_port"],
            store_configured=bool(self.config.store_path),
        )

    def stop(self) -> None:
        """Stop the fetch HTTP server and close the store."""
        if self._server is None:
            self.state["running"] = False
            return
        self._record("fetch_listener_stopping")
        self._server.shutdown()
        self._server.server_close()
        if self._thread is not None:
            self._thread.join(timeout=2.0)
        self._server = None
        self._thread = None
        if self._store is not None:
            try:
                self._store.close()
            except Exception:
                pass
            self._store = None
        self.state["running"] = False

    def handle_want_have(self, body: bytes) -> tuple[int, bytes]:
        """Delegate to fetch runtime handler (for direct testing without HTTP)."""
        return _fetch_rt.handle_want_have_request(body, self._store)

    def handle_want_block(self, body: bytes) -> tuple[int, bytes]:
        """Delegate to fetch runtime handler (for direct testing without HTTP)."""
        return _fetch_rt.handle_want_block_request(body, self._store, self._rate_limiter)
