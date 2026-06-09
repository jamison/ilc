#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
"""CCSS CLI — machine-readable sender interface for AI agents and scripts.

Designed for non-human callers: every code path emits JSON to stdout.
Errors go to stderr.  Exit 0 = success, non-zero = failure.

CLI usage
─────────
  # List configured contacts
  python tools/ccss_send/ccss_cli.py contacts

  # Check Tor + relay reachability
  python tools/ccss_send/ccss_cli.py status

  # Send a message (message as argument)
  python tools/ccss_send/ccss_cli.py send genesis "Hello from an agent"

  # Send a message (message from stdin — pipe-friendly)
  echo "Hello" | python tools/ccss_send/ccss_cli.py send genesis -

  # List received envelopes in inbox
  python tools/ccss_send/ccss_cli.py inbox

Library usage
─────────────
  from tools.ccss_send.ccss_cli import CCSSSender

  s = CCSSSender()
  print(s.contacts())
  print(s.send("genesis", "Hello from an agent"))
  print(s.status())
  print(s.inbox())

All methods return plain dicts (JSON-serialisable).  No side-effects beyond
the Tor network send and the sent-log write.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import socket
import sys
import time
from pathlib import Path
from typing import Any

_DEFAULT_CONTACTS = (
    Path(__file__).resolve().parent.parent.parent
    / "docs" / "contact" / "ccss_contacts.json"
)
_DEFAULT_INBOX = Path.home() / ".ccss_inbox" / "genesis"
_DEFAULT_SENT  = Path.home() / ".ccss_inbox" / "sent"
_TOR_HOST = "127.0.0.1"
_TOR_PORT = 9050
_RELAY_HOST = "127.0.0.1"
_RELAY_PORT = 8420
_OUTER_ENVELOPE_BYTES = 4156
_MAX_MESSAGE_BYTES = 2000


# ---------------------------------------------------------------------------
# Core send logic (shared with chat UI)
# ---------------------------------------------------------------------------

def _socks5_send(onion: str, path: str, body: bytes, timeout: int = 30) -> dict[str, Any]:
    """POST body to onion:80/path via Tor SOCKS5.  Returns parsed JSON response."""
    host_b = onion.encode()
    with socket.create_connection((_TOR_HOST, _TOR_PORT), timeout=timeout) as s:
        s.sendall(b"\x05\x01\x00")
        if s.recv(2) != b"\x05\x00":
            raise RuntimeError("SOCKS5 auth negotiation failed")
        s.sendall(b"\x05\x01\x00\x03" + bytes([len(host_b)]) + host_b + b"\x00\x50")
        resp = s.recv(10)
        if resp[1] != 0x00:
            raise RuntimeError(f"SOCKS5 CONNECT failed: code {resp[1]}")
        req = (
            f"POST {path} HTTP/1.0\r\nHost: {onion}\r\n"
            f"Content-Type: application/octet-stream\r\n"
            f"Content-Length: {len(body)}\r\n\r\n"
        ).encode() + body
        s.sendall(req)
        raw = b""
        while True:
            chunk = s.recv(4096)
            if not chunk:
                break
            raw += chunk
    _, _, resp_body = raw.partition(b"\r\n\r\n")
    status_line = raw.split(b"\r\n")[0]
    code = int(status_line.split(b" ")[1])
    if code not in (200, 202):
        raise RuntimeError(f"Relay returned HTTP {code}")
    return json.loads(resp_body)


def _seal(message: str, pubkey_hex: str) -> bytes:
    _root = Path(__file__).resolve().parent.parent.parent
    if str(_root) not in sys.path:
        sys.path.insert(0, str(_root))
    from tools.ccss_send.ccss_encrypt import seal_message  # type: ignore
    return seal_message(message, pubkey_hex)


def _write_sent(sent_dir: Path, contact_id: str, record: dict[str, Any]) -> None:
    """Atomically write sent-message record to disk."""
    import tempfile
    d = sent_dir / contact_id
    d.mkdir(parents=True, exist_ok=True)
    ts      = record["ts"]
    receipt = record["receipt"]
    out     = d / f"{ts}_{receipt[:8]}.json"
    fd, tmp = tempfile.mkstemp(dir=d)
    try:
        with os.fdopen(fd, "w") as fh:
            json.dump(record, fh, sort_keys=True)
        os.replace(tmp, out)
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass


# ---------------------------------------------------------------------------
# CCSSSender — importable library class
# ---------------------------------------------------------------------------

class CCSSSender:
    """Programmatic CCSS sender for agent / script use.

    All public methods return JSON-serialisable dicts and raise on hard
    errors (network failure, bad config).  Callers can catch and handle.

    Example
    -------
    >>> s = CCSSSender()
    >>> s.contacts()
    [{"id": "genesis", "name": "Genesis Agent", "configured": False, ...}]
    >>> s.send("genesis", "Hello")   # raises if not configured
    {"ok": True, "receipt": "abc123...", "ts": 1700000000, "contact_id": "genesis"}
    """

    def __init__(
        self,
        contacts_path: Path | str = _DEFAULT_CONTACTS,
        inbox_dir:     Path | str = _DEFAULT_INBOX,
        sent_dir:      Path | str = _DEFAULT_SENT,
    ) -> None:
        self.contacts_path = Path(contacts_path)
        self.inbox_dir     = Path(inbox_dir)
        self.sent_dir      = Path(sent_dir)

    # ── contacts ─────────────────────────────────────────────────────────

    def contacts(self) -> list[dict[str, Any]]:
        """Return list of contacts.  Pubkey is stripped (never leaves process)."""
        try:
            raw = json.loads(self.contacts_path.read_text())
        except FileNotFoundError:
            return []
        result = []
        for c in raw:
            ph    = c.get("ccss_recipient_pubkey", "")
            onion = c.get("ccss_contact_onion", "")
            configured = (
                bool(ph)    and "PLACEHOLDER" not in ph.upper()
                and bool(onion) and "PLACEHOLDER" not in onion.upper()
            )
            result.append({
                "id":          c.get("id", ""),
                "name":        c.get("name", ""),
                "description": c.get("description", ""),
                "agent_id":    c.get("agent_id", ""),
                "onion":       onion if configured else None,
                "configured":  configured,
            })
        return result

    # ── status ────────────────────────────────────────────────────────────

    def status(self) -> dict[str, Any]:
        """Return Tor SOCKS5 reachability + local relay health + inbox count."""
        tor_ok = False
        try:
            with socket.create_connection((_TOR_HOST, _TOR_PORT), timeout=3):
                tor_ok = True
        except OSError as exc:
            tor_err = str(exc)
        else:
            tor_err = None

        relay_ok = False
        relay_err = None
        try:
            with socket.create_connection((_RELAY_HOST, _RELAY_PORT), timeout=2) as s:
                s.sendall(b"GET /health HTTP/1.0\r\nHost: 127.0.0.1\r\n\r\n")
                raw = s.recv(512)
            relay_ok = b'"status":"ok"' in raw or b'"status": "ok"' in raw
        except OSError as exc:
            relay_err = str(exc)

        inbox_count = 0
        if self.inbox_dir.is_dir():
            inbox_count = sum(
                1 for f in self.inbox_dir.iterdir() if f.suffix == ".envelope"
            )

        return {
            "tor":         {"ok": tor_ok, "error": tor_err},
            "relay":       {"ok": relay_ok, "error": relay_err},
            "inbox_count": inbox_count,
        }

    # ── send ──────────────────────────────────────────────────────────────

    def send(self, contact_id: str, message: str) -> dict[str, Any]:
        """Encrypt and send message to contact via Tor.

        Args:
            contact_id: id field from contacts list (e.g. "genesis")
            message:    UTF-8 text, max 2000 bytes encoded

        Returns:
            {"ok": True, "receipt": "<hex>", "ts": <unix>, "contact_id": "<id>"}

        Raises:
            ValueError:   contact not found / not configured / message too long
            RuntimeError: encryption or network failure
        """
        msg_bytes = message.encode("utf-8")
        if len(msg_bytes) > _MAX_MESSAGE_BYTES:
            raise ValueError(
                f"message too long: {len(msg_bytes)} bytes (max {_MAX_MESSAGE_BYTES})"
            )

        # Lookup contact (read pubkey on server side only)
        try:
            raw_contacts = json.loads(self.contacts_path.read_text())
        except FileNotFoundError:
            raise ValueError(f"contacts file not found: {self.contacts_path}")

        contact = next((c for c in raw_contacts if c.get("id") == contact_id), None)
        if contact is None:
            raise ValueError(f"contact not found: {contact_id!r}")

        pubkey = contact.get("ccss_recipient_pubkey", "")
        onion  = contact.get("ccss_contact_onion", "")

        if not pubkey or "PLACEHOLDER" in pubkey.upper():
            raise ValueError(f"contact {contact_id!r}: ccss_recipient_pubkey not configured")
        if not onion or "PLACEHOLDER" in onion.upper():
            raise ValueError(f"contact {contact_id!r}: ccss_contact_onion not configured")

        envelope = _seal(message, pubkey)
        result   = _socks5_send(onion, "/submit", envelope)
        receipt  = result.get("receipt_token", hashlib.sha256(envelope).hexdigest())
        ts       = int(time.time())

        record = {
            "ts":         ts,
            "contact_id": contact_id,
            "message":    message,
            "receipt":    receipt,
        }
        _write_sent(self.sent_dir, contact_id, record)

        return {"ok": True, "receipt": receipt, "ts": ts, "contact_id": contact_id}

    # ── inbox ─────────────────────────────────────────────────────────────

    def inbox(self) -> list[dict[str, Any]]:
        """List received envelopes (sealed, unread)."""
        if not self.inbox_dir.is_dir():
            return []
        envs = []
        for f in self.inbox_dir.iterdir():
            if f.suffix != ".envelope":
                continue
            sz = f.stat().st_size
            envs.append({
                "receipt":  f.stem,
                "size":     sz,
                "size_ok":  sz == _OUTER_ENVELOPE_BYTES,
                "received": int(f.stat().st_mtime),
            })
        return sorted(envs, key=lambda e: e["received"], reverse=True)

    # ── sent log ──────────────────────────────────────────────────────────

    def sent(self, contact_id: str) -> list[dict[str, Any]]:
        """Return sent-message log for a contact."""
        d = self.sent_dir / contact_id
        msgs = []
        if d.is_dir():
            for f in d.iterdir():
                if f.suffix == ".json":
                    try:
                        msgs.append(json.loads(f.read_text()))
                    except Exception:
                        pass
        return sorted(msgs, key=lambda m: m.get("ts", 0))


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def _out(data: Any) -> None:
    print(json.dumps(data, sort_keys=True, indent=2))


def _err(msg: str, code: int = 1) -> None:
    print(json.dumps({"ok": False, "error": msg}, sort_keys=True), file=sys.stderr)
    sys.exit(code)


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(
        prog="ccss_cli",
        description="CCSS CLI — machine-readable CCSS sender for agents and scripts",
    )
    ap.add_argument("--contacts", default=str(_DEFAULT_CONTACTS),
                    help="Path to ccss_contacts.json")
    ap.add_argument("--inbox",    default=str(_DEFAULT_INBOX),
                    help="Inbox directory (received envelopes)")
    ap.add_argument("--sent",     default=str(_DEFAULT_SENT),
                    help="Sent log directory")

    sub = ap.add_subparsers(dest="cmd", required=True)

    # contacts
    sub.add_parser("contacts", help="List configured contacts as JSON")

    # status
    sub.add_parser("status", help="Check Tor + relay reachability")

    # send
    sp = sub.add_parser("send", help="Send a message to a contact")
    sp.add_argument("contact_id", help="Contact id (e.g. genesis)")
    sp.add_argument("message",
                    help='Message text, or "-" to read from stdin')

    # inbox
    sub.add_parser("inbox", help="List received envelopes")

    # sent
    sp2 = sub.add_parser("sent", help="Show sent-message log for a contact")
    sp2.add_argument("contact_id", help="Contact id")

    args = ap.parse_args(argv)
    s = CCSSSender(
        contacts_path=args.contacts,
        inbox_dir=args.inbox,
        sent_dir=args.sent,
    )

    if args.cmd == "contacts":
        _out(s.contacts())

    elif args.cmd == "status":
        _out(s.status())

    elif args.cmd == "send":
        msg = sys.stdin.read().strip() if args.message == "-" else args.message
        if not msg:
            _err("empty message")
        try:
            result = s.send(args.contact_id, msg)
            _out(result)
        except (ValueError, RuntimeError) as exc:
            _err(str(exc))

    elif args.cmd == "inbox":
        _out(s.inbox())

    elif args.cmd == "sent":
        _out(s.sent(args.contact_id))


if __name__ == "__main__":
    main()
