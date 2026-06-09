#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
"""CCSS peer receiver — direct TCP inbox, no Tor required.

Accepts exactly 4156-byte CCSS-003 envelopes over raw TCP connections from
any directly-reachable ILC peer.  Stores them in the same inbox directory
as the Tor relay server so both transports share a single inbox.

This is the Option C bootstrap transport.  Once the ILC D2d gossip layer is
live, envelopes arrive through the peer network instead; this server becomes
an adapter at the edge of that network rather than a standalone listener.

Usage:
    python tools/ccss_relay/ccss_peer_receiver.py [--host 0.0.0.0] [--port 9001]
                                                   [--inbox ~/.ccss_inbox/genesis]

Wire protocol (intentionally minimal):
    Sender → 4156 raw bytes (CCSS-003 outer envelope)
    Sender → TCP FIN (shutdown SHUT_WR)
    Receiver → JSON receipt line: {"receipt_token":"<sha256hex>","status":"accepted"}
    Receiver → TCP FIN

Security properties:
  - Envelope is already E2E encrypted; receiver stores opaque blob
  - No IP logging (only receipt SHA-256 is recorded)
  - Atomic writes via tempfile + os.replace
  - Hard inbox cap (1024 envelopes) to prevent storage exhaustion
  - Size validation: exactly 4156 bytes, no more no less
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import socket
import socketserver
import sys
import tempfile
from pathlib import Path
from typing import Any

_DEFAULT_HOST  = "0.0.0.0"
_DEFAULT_PORT  = 9001
_DEFAULT_INBOX = Path.home() / ".ccss_inbox" / "genesis"
_OUTER_ENVELOPE_BYTES = 4156
_INBOX_CAP = 1024


class _Handler(socketserver.BaseRequestHandler):
    """Handle one incoming peer connection."""

    inbox_dir: Path   # set by factory

    def handle(self) -> None:
        conn: socket.socket = self.request
        conn.settimeout(15)

        try:
            envelope = self._read_exactly(_OUTER_ENVELOPE_BYTES + 1, conn)
        except (OSError, TimeoutError) as exc:
            self._reply_err(conn, f"read error: {exc}")
            return

        if len(envelope) != _OUTER_ENVELOPE_BYTES:
            self._reply_err(conn,
                f"invalid envelope size: got {len(envelope)}, "
                f"expected {_OUTER_ENVELOPE_BYTES}")
            return

        # Inbox cap
        d = self.inbox_dir
        d.mkdir(parents=True, exist_ok=True)
        existing = [f for f in d.iterdir() if f.suffix == ".envelope"]
        if len(existing) >= _INBOX_CAP:
            self._reply_err(conn, "inbox full")
            return

        receipt = hashlib.sha256(envelope).hexdigest()
        out     = d / f"{receipt}.envelope"

        if out.exists():
            # Duplicate — still acknowledge (idempotent)
            self._reply_ok(conn, receipt)
            return

        fd, tmp = tempfile.mkstemp(dir=d)
        try:
            with os.fdopen(fd, "wb") as fh:
                fh.write(envelope)
            os.replace(tmp, out)
        except Exception as exc:
            try:
                os.unlink(tmp)
            except OSError:
                pass
            self._reply_err(conn, f"write error: {exc}")
            return

        self._reply_ok(conn, receipt)

    @staticmethod
    def _read_exactly(max_bytes: int, conn: socket.socket) -> bytes:
        """Read until peer shuts down write side or we hit max_bytes."""
        buf = b""
        while len(buf) < max_bytes:
            chunk = conn.recv(min(4096, max_bytes - len(buf)))
            if not chunk:
                break
            buf += chunk
        return buf

    @staticmethod
    def _reply_ok(conn: socket.socket, receipt: str) -> None:
        msg = json.dumps({"receipt_token": receipt, "status": "accepted"},
                         sort_keys=True)
        try:
            conn.sendall((msg + "\n").encode())
        except OSError:
            pass

    @staticmethod
    def _reply_err(conn: socket.socket, error: str) -> None:
        msg = json.dumps({"status": "error", "error": error}, sort_keys=True)
        try:
            conn.sendall((msg + "\n").encode())
        except OSError:
            pass


def _make_server(host: str, port: int, inbox_dir: Path) -> socketserver.TCPServer:
    class H(_Handler):
        pass
    H.inbox_dir = inbox_dir

    socketserver.TCPServer.allow_reuse_address = True
    return socketserver.TCPServer((host, port), H)


def main() -> None:
    ap = argparse.ArgumentParser(
        description="CCSS peer receiver — direct TCP inbox (no Tor)"
    )
    ap.add_argument("--host",  default=_DEFAULT_HOST,
                    help="Bind address (default 0.0.0.0; use 127.0.0.1 for loopback only)")
    ap.add_argument("--port",  type=int, default=_DEFAULT_PORT,
                    help="TCP port (default 9001)")
    ap.add_argument("--inbox", default=str(_DEFAULT_INBOX),
                    help="Inbox directory (shared with Tor relay)")
    args = ap.parse_args()

    inbox_dir = Path(args.inbox)
    inbox_dir.mkdir(parents=True, exist_ok=True)

    srv = _make_server(args.host, args.port, inbox_dir)
    print(f"CCSS peer receiver  →  {args.host}:{args.port}")
    print(f"Inbox:  {inbox_dir}")
    print(f"Transport: DirectTransport (no Tor required)")
    print("Ctrl-C to stop.")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        srv.server_close()


if __name__ == "__main__":
    main()
