#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
"""CCSS relay server — Genesis Agent inbound sealed-envelope endpoint.

Accepts CCSS-003 outer envelopes (exactly 4156 bytes) via HTTP POST /submit.
Listens on 127.0.0.1 only; a Tor v3 hidden service routes external connections
here, providing network-layer sender anonymization.

Security properties:
- Loopback-only listener (127.0.0.1); never binds a public interface.
- Does not decrypt envelope content (relay is content-blind).
- Does not log client IP (Tor exit node anyway, but enforced here).
- Enforces exact H013 outer envelope size (4156 bytes); rejects all others.
- Hard inbox cap (1024 envelopes per CCSS-003 queue bound); returns 503 when full.
- Atomic writes: tmp file in inbox dir, then os.replace to final path.

Envelope naming:  <sha256_of_envelope>.envelope
Receipt token:    sha256 hex of raw envelope bytes

Usage:
    python tools/ccss_relay/ccss_relay_server.py [--inbox <dir>] [--port <port>]

Defaults:
    --inbox  ~/.ccss_inbox/genesis
    --port   8420

Deployment:
    Tor hidden service maps :80 → 127.0.0.1:8420.
    See deploy/tor/torrc.template and deploy/systemd/ccss-relay.service.
"""

from __future__ import annotations

import argparse
import hashlib
import http.server
import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any

# H013 fixed outer envelope size — matches CCSS-003 _H013_OUTER_ENVELOPE_BYTES
_OUTER_ENVELOPE_BYTES = 4156

# Matches CCSS-003 _MAX_LOCAL_DELIVERY_QUEUE_BOUND
_MAX_INBOX_CAPACITY = 1024

_LOOPBACK_HOST = "127.0.0.1"
_DEFAULT_PORT = 8420
_DEFAULT_INBOX = Path.home() / ".ccss_inbox" / "genesis"


# ---------------------------------------------------------------------------
# HTTP handler
# ---------------------------------------------------------------------------


def _json_body(body: dict[str, Any]) -> bytes:
    return json.dumps(body, separators=(",", ":"), sort_keys=True).encode("utf-8")


def _make_handler(inbox_path: Path) -> type[http.server.BaseHTTPRequestHandler]:
    class CCSSRelayHandler(http.server.BaseHTTPRequestHandler):

        def log_message(self, fmt: str, *args: object) -> None:
            # Suppress default access log — do not record client addresses.
            pass

        def _send_json(self, status: int, body: dict[str, Any]) -> None:
            encoded = _json_body(body)
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(encoded)))
            # Close connection after each response; keeps state simple.
            self.send_header("Connection", "close")
            self.end_headers()
            self.wfile.write(encoded)

        def do_GET(self) -> None:
            if self.path == "/health":
                self._send_json(200, {"service": "ccss_relay", "status": "ok"})
            else:
                self._send_json(404, {"error": "not_found"})

        def do_POST(self) -> None:
            if self.path != "/submit":
                self._send_json(404, {"error": "not_found"})
                return

            # Validate Content-Length before reading any body bytes.
            try:
                content_length = int(self.headers.get("Content-Length", "0"))
            except ValueError:
                self._send_json(400, {"error": "invalid_content_length"})
                return

            if content_length != _OUTER_ENVELOPE_BYTES:
                self._send_json(400, {
                    "error": "invalid_envelope_size",
                    "expected_bytes": _OUTER_ENVELOPE_BYTES,
                    "received_content_length": content_length,
                })
                return

            # Read exactly the declared (and validated) number of bytes.
            envelope = self.rfile.read(_OUTER_ENVELOPE_BYTES)
            if len(envelope) != _OUTER_ENVELOPE_BYTES:
                self._send_json(400, {"error": "incomplete_envelope_body"})
                return

            # Check capacity before touching disk.
            try:
                pending_count = sum(1 for _ in inbox_path.glob("*.envelope"))
            except OSError:
                self._send_json(500, {"error": "inbox_read_error"})
                return

            if pending_count >= _MAX_INBOX_CAPACITY:
                self._send_json(503, {
                    "error": "inbox_capacity_exceeded",
                    "capacity": _MAX_INBOX_CAPACITY,
                })
                return

            # Receipt token = sha256 of raw envelope bytes.
            receipt_token = hashlib.sha256(envelope).hexdigest()
            final_path = inbox_path / f"{receipt_token}.envelope"

            # Atomic write: write to tmp in same directory, then os.replace.
            try:
                inbox_path.mkdir(parents=True, exist_ok=True)
                fd, tmp_path_str = tempfile.mkstemp(dir=inbox_path, suffix=".tmp")
                try:
                    os.write(fd, envelope)
                finally:
                    os.close(fd)
                os.replace(tmp_path_str, final_path)
            except OSError:
                self._send_json(500, {"error": "inbox_write_error"})
                return

            self._send_json(200, {
                "receipt_token": receipt_token,
                "status": "accepted",
            })

    return CCSSRelayHandler


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="CCSS relay server for Genesis Agent sealed-envelope delivery."
    )
    parser.add_argument(
        "--inbox",
        type=Path,
        default=_DEFAULT_INBOX,
        metavar="DIR",
        help="Directory to store received envelopes (default: ~/.ccss_inbox/genesis)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=_DEFAULT_PORT,
        metavar="PORT",
        help=f"Loopback port to listen on (default: {_DEFAULT_PORT})",
    )
    args = parser.parse_args(argv)

    inbox_path: Path = args.inbox.resolve()
    inbox_path.mkdir(parents=True, exist_ok=True)

    handler_class = _make_handler(inbox_path)
    server = http.server.HTTPServer((_LOOPBACK_HOST, args.port), handler_class)

    print(f"CCSS relay: listening on {_LOOPBACK_HOST}:{args.port}", flush=True)
    print(f"CCSS relay: inbox at {inbox_path}", flush=True)
    print(f"CCSS relay: accepting {_OUTER_ENVELOPE_BYTES}-byte H013 outer envelopes", flush=True)
    print("CCSS relay: waiting for sealed envelopes (Tor hidden service routes here)...", flush=True)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nCCSS relay: stopped.", flush=True)

    return 0


if __name__ == "__main__":
    sys.exit(main())
