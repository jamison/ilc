"""Phase 901 — CDL-077 WANT-HAVE/WANT-BLOCK two-phase fetch runtime.

Implements the pull side of the CDL-036 dissemination contract for truth
primitive nodes persisted under CDL-075.

Client side:
    want_have(node_id, peer_endpoint)   → {have: bool, node_id: str}
    want_block(node_id, peer_endpoint)  → node record bytes | None
    fetch_truth_primitive(node_id)      → bytes | None (tries all peers)

Server handler side (called by http_fetch_transport_runtime):
    handle_want_have_request(body, store)              → (status, response_bytes)
    handle_want_block_request(body, store, limiter)    → (status, response_bytes)

Rate limiting:
    FetchRateLimiter — in-process per-identity token bucket for WANT-BLOCK.
    WANT_BLOCK_RATE_LIMIT_PER_MINUTE requests per requester_id.
    Over limit: HTTP 429, token fetch_rate_limit_exceeded.
    Not persistent across process restarts (RC phase scope).

Activation:
    ILC_D2D_GOSSIP_PEERS — comma-separated HTTPS peer endpoints (reused from CDL-076).
    Absent → fetch_truth_primitive() returns None without error.
    ILC_TRUTH_GRAPH_STORE_PATH — required on server side to serve records.
    Absent → server returns fetch_store_not_configured (503).
"""

from __future__ import annotations

import json
import os
import ssl
import threading
import time
import urllib.error
import urllib.request
from typing import Any

from ilc_core.network.d2d import gossip_transport
from ilc_core.network.d2d.gossip_peer_registry import validate_peer_endpoint

TRUTH_PRIMITIVE_FETCH_RUNTIME_VERSION = "truth_primitive_fetch_runtime_901.v0.1"
TRANSPORT_SECURITY_HARDENING_TOKEN = "transport_security_hardening_1218b"
CDL_077_DEPENDENCY = "cdl_077_want_have_want_block_fetch.v0.1"
CDL_075_DEPENDENCY = "cdl_075_truth_primitive_graph_persistence.v0.1"
CDL_042_DEPENDENCY = "cdl_042_ratified_407.v0.1"
CDL_078_DEPENDENCY = "cdl_078_relay_incentive_constitutional_lock.v0.1"

WANT_HAVE_PATH = "/fetch/want-have"
WANT_BLOCK_PATH = "/fetch/want-block"
WANT_BLOCK_RATE_LIMIT_PER_MINUTE = 10
_FETCH_TIMEOUT_SECONDS = 5.0
_MAX_RESPONSE_BYTES = 1_048_576  # 1 MiB — OOM guard on inbound

# Dep-chain guard
if gossip_transport.GOSSIP_TRANSPORT_RUNTIME_VERSION != "gossip_transport_runtime_558.v0.1":
    raise RuntimeError("truth_primitive_fetch_runtime_gossip_transport_dep_mismatch")


# ---------------------------------------------------------------------------
# SSRF redirect guard
# ---------------------------------------------------------------------------


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
        raise FetchTransportError(
            "fetch_redirect_not_permitted",
            f"peer returned redirect {code} to {newurl}",
        )


# ---------------------------------------------------------------------------
# Typed exceptions
# ---------------------------------------------------------------------------


class FetchTransportError(Exception):
    """Network or protocol failure in fetch client."""

    def __init__(self, token: str, detail: str = "") -> None:
        super().__init__(detail or token)
        self.token = token


class FetchRateLimitError(FetchTransportError):
    """Peer returned 429 — WANT-BLOCK rate limit exceeded."""

    def __init__(self, peer_endpoint: str) -> None:
        super().__init__(
            "fetch_rate_limit_exceeded",
            f"WANT-BLOCK rate limit exceeded by peer {peer_endpoint}",
        )


# ---------------------------------------------------------------------------
# Rate limiter (server-side, in-process)
# ---------------------------------------------------------------------------


class FetchRateLimiter:
    """In-process per-identity token bucket rate limiter for WANT-BLOCK requests.

    Each requester_id receives WANT_BLOCK_RATE_LIMIT_PER_MINUTE credits per
    60-second window.  Windows are rolling per-identity (last-reset timestamp).

    Thread-safe via a single re-entrant lock.
    """

    def __init__(self, limit_per_minute: int = WANT_BLOCK_RATE_LIMIT_PER_MINUTE) -> None:
        if limit_per_minute < 1:
            raise ValueError("limit_per_minute must be >= 1")
        self._limit = limit_per_minute
        self._buckets: dict[str, tuple[int, float]] = {}  # requester_id → (count, window_start)
        self._lock = threading.Lock()

    def check_and_consume(self, requester_id: str) -> bool:
        """Return True if the request is allowed; False if rate limit exceeded."""
        now = time.monotonic()
        with self._lock:
            count, window_start = self._buckets.get(requester_id, (0, now))
            if now - window_start >= 60.0:
                # New window — reset count
                count = 0
                window_start = now
            if count >= self._limit:
                self._buckets[requester_id] = (count, window_start)
                return False
            self._buckets[requester_id] = (count + 1, window_start)
            return True


# ---------------------------------------------------------------------------
# Client — WANT-HAVE probe
# ---------------------------------------------------------------------------


def want_have(node_id: str, peer_endpoint: str) -> dict[str, Any]:
    """Send a WANT-HAVE probe to a single peer.

    Returns {have: bool, node_id: str}.
    Raises FetchTransportError on network or protocol failure.
    """
    normalized = validate_peer_endpoint(peer_endpoint)
    url = f"{normalized}{WANT_HAVE_PATH}"
    body = json.dumps({"node_id": node_id, "requester_id": "local"}, sort_keys=True).encode()

    ssl_ctx = ssl.create_default_context()
    ssl_ctx.check_hostname = False
    ssl_ctx.verify_mode = ssl.CERT_NONE

    req = urllib.request.Request(
        url,
        data=body,
        method="POST",
        headers={"Content-Type": "application/json"},
    )
    _opener = urllib.request.build_opener(_NoRedirectHandler, urllib.request.HTTPSHandler(context=ssl_ctx))
    try:
        with _opener.open(req, timeout=_FETCH_TIMEOUT_SECONDS) as resp:
            raw = resp.read(_MAX_RESPONSE_BYTES)
            parsed = json.loads(raw)
            if not isinstance(parsed, dict) or "have" not in parsed:
                raise FetchTransportError(
                    "fetch_want_have_invalid_response",
                    f"peer {peer_endpoint} returned unexpected body",
                )
            return {"have": bool(parsed["have"]), "node_id": str(parsed.get("node_id", node_id))}
    except FetchTransportError:
        raise
    except urllib.error.HTTPError as exc:
        raise FetchTransportError(
            "fetch_want_have_http_error",
            f"peer {peer_endpoint} returned HTTP {exc.code}",
        ) from exc
    except Exception as exc:
        raise FetchTransportError(
            "fetch_want_have_transport_error",
            f"peer {peer_endpoint}: {exc}",
        ) from exc


# ---------------------------------------------------------------------------
# Client — WANT-BLOCK content fetch
# ---------------------------------------------------------------------------


def want_block(node_id: str, peer_endpoint: str) -> bytes | None:
    """Send a WANT-BLOCK request to a single peer.

    Returns raw node record bytes (JSON-encoded dict) if the peer has the node.
    Returns None if the peer returns 404 (node not found).
    Raises FetchRateLimitError if the peer returns 429.
    Raises FetchTransportError on network or protocol failure.
    """
    normalized = validate_peer_endpoint(peer_endpoint)
    url = f"{normalized}{WANT_BLOCK_PATH}"
    body = json.dumps({"node_id": node_id, "requester_id": "local"}, sort_keys=True).encode()

    ssl_ctx = ssl.create_default_context()
    ssl_ctx.check_hostname = False
    ssl_ctx.verify_mode = ssl.CERT_NONE

    req = urllib.request.Request(
        url,
        data=body,
        method="POST",
        headers={"Content-Type": "application/json"},
    )
    _opener = urllib.request.build_opener(_NoRedirectHandler, urllib.request.HTTPSHandler(context=ssl_ctx))
    try:
        with _opener.open(req, timeout=_FETCH_TIMEOUT_SECONDS) as resp:
            raw = resp.read(_MAX_RESPONSE_BYTES)
            return raw
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return None
        if exc.code == 429:
            raise FetchRateLimitError(peer_endpoint) from exc
        raise FetchTransportError(
            "fetch_want_block_http_error",
            f"peer {peer_endpoint} returned HTTP {exc.code}",
        ) from exc
    except FetchTransportError:
        raise
    except Exception as exc:
        raise FetchTransportError(
            "fetch_want_block_transport_error",
            f"peer {peer_endpoint}: {exc}",
        ) from exc


# ---------------------------------------------------------------------------
# Client — composite fetch_truth_primitive
# ---------------------------------------------------------------------------


def fetch_truth_primitive(node_id: str) -> bytes | None:
    """Attempt to fetch a truth primitive node record from any configured peer.

    Reads ILC_D2D_GOSSIP_PEERS (comma-separated HTTPS endpoints).
    For each peer: sends WANT-HAVE probe; if positive, sends WANT-BLOCK.
    Returns node record bytes from the first willing peer, or None if not found.

    ILC_D2D_GOSSIP_PEERS absent → returns None without error.
    Rate-limit errors from a peer are logged and the next peer is tried.
    """
    raw_peers = os.environ.get("ILC_D2D_GOSSIP_PEERS", "").strip()
    if not raw_peers:
        return None

    peers = [p.strip() for p in raw_peers.split(",") if p.strip()]
    for peer_endpoint in peers:
        try:
            have_resp = want_have(node_id, peer_endpoint)
        except FetchTransportError:
            continue
        if not have_resp.get("have"):
            continue
        try:
            record_bytes = want_block(node_id, peer_endpoint)
            if record_bytes is not None:
                return record_bytes
        except FetchRateLimitError:
            continue
        except FetchTransportError:
            continue
    return None


# ---------------------------------------------------------------------------
# Server handlers (called by http_fetch_transport_runtime)
# ---------------------------------------------------------------------------


def _parse_request_body(body: bytes) -> dict[str, Any]:
    """Parse and validate a fetch request body. Raises ValueError with token on failure."""
    try:
        parsed = json.loads(body)
    except json.JSONDecodeError as exc:
        raise ValueError("fetch_request_invalid_json") from exc
    if not isinstance(parsed, dict):
        raise ValueError("fetch_request_not_object")
    node_id = parsed.get("node_id")
    if not isinstance(node_id, str) or not node_id.strip():
        raise ValueError("fetch_request_node_id_missing")
    requester_id = parsed.get("requester_id")
    if not isinstance(requester_id, str) or not requester_id.strip():
        raise ValueError("fetch_request_requester_id_missing")
    return parsed


def handle_want_have_request(body: bytes, store: Any) -> tuple[int, bytes]:
    """Server-side WANT-HAVE handler.

    Checks whether the node_id is present in the store (presence check).
    Returns (200, JSON {have: bool, node_id: str}) or (400, error JSON).
    Store absent (None): returns (200, {have: false}) — store not configured is
    equivalent to not having the node.
    """
    try:
        parsed = _parse_request_body(body)
    except ValueError as exc:
        token = str(exc)
        resp = json.dumps({"token": token}, sort_keys=True).encode()
        return 400, resp

    node_id = parsed["node_id"]

    if store is None:
        resp = json.dumps({"have": False, "node_id": node_id}, sort_keys=True).encode()
        return 200, resp

    try:
        record = store.get_node(node_id)
        have = record is not None
    except Exception:
        have = False

    resp = json.dumps({"have": have, "node_id": node_id}, sort_keys=True).encode()
    return 200, resp


def handle_want_block_request(
    body: bytes,
    store: Any,
    rate_limiter: FetchRateLimiter,
    rate_limit_key: str | None = None,
) -> tuple[int, bytes]:
    """Server-side WANT-BLOCK handler.

    Rate-checks the requester using rate_limit_key (preferred: transport-layer IP
    from client_address[0]) to prevent identity spoofing via unauthenticated body.
    Falls back to requester_id from body when rate_limit_key is None (direct callers,
    tests). The requester_id from the body is included in 429 responses for audit
    logging only — it is not used as the rate-limit identity when rate_limit_key
    is provided.

    Returns:
        (200, record_bytes) if found and not rate-limited
        (404, error JSON) if node not found
        (429, error JSON) if requester is rate-limited
        (503, error JSON) if store not configured
        (400, error JSON) if request malformed
    """
    try:
        parsed = _parse_request_body(body)
    except ValueError as exc:
        token = str(exc)
        resp = json.dumps({"token": token}, sort_keys=True).encode()
        return 400, resp

    node_id = parsed["node_id"]
    requester_id = parsed["requester_id"]
    # Use transport-supplied key (IP) when available; fall back to body for direct callers.
    effective_key = rate_limit_key if rate_limit_key is not None else requester_id

    if store is None:
        resp = json.dumps(
            {"token": "fetch_store_not_configured"}, sort_keys=True
        ).encode()
        return 503, resp

    if not rate_limiter.check_and_consume(effective_key):
        resp = json.dumps(
            {"token": "fetch_rate_limit_exceeded", "requester_id": requester_id},
            sort_keys=True,
        ).encode()
        return 429, resp

    try:
        record = store.get_node(node_id)
    except Exception:
        record = None

    if record is None:
        resp = json.dumps(
            {"token": "fetch_node_not_found", "node_id": node_id}, sort_keys=True
        ).encode()
        return 404, resp

    try:
        record_bytes = json.dumps(record, sort_keys=True).encode()
    except (TypeError, ValueError):
        resp = json.dumps({"token": "fetch_record_serialization_error"}, sort_keys=True).encode()
        return 500, resp

    # CDL-078: record successful serve event for routing reputation (best-effort).
    try:
        from ilc_core.network.d2d.routing_reputation_runtime import (
            record_serve_event,
            _global_reputation_state,
        )
        record_serve_event(node_id, int(time.time() // 60), _global_reputation_state)
    except Exception:  # noqa: BLE001
        pass  # best-effort; WANT-BLOCK response is not affected

    return 200, record_bytes
