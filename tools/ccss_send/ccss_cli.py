#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
"""CCSS CLI — machine-readable sender interface for AI agents and scripts.

Designed for non-human callers: every code path emits JSON to stdout.
Errors go to stderr.  Exit 0 = success, non-zero = failure.

Transport selection (automatic, in priority order):
  1. DirectTransport  — if contact has ccss_peer_endpoint (host:port)
  2. TorTransport     — if contact has ccss_contact_onion (.onion)
  3. D2dTransport     — if contact has agent_id (future; raises until D2d is live)

CLI usage
─────────
  python tools/ccss_send/ccss_cli.py contacts
  python tools/ccss_send/ccss_cli.py status
  python tools/ccss_send/ccss_cli.py send genesis "Hello"
  echo "Hello" | python tools/ccss_send/ccss_cli.py send genesis -
  python tools/ccss_send/ccss_cli.py inbox
  python tools/ccss_send/ccss_cli.py sent genesis

Library usage
─────────────
  from tools.ccss_send.ccss_cli import CCSSSender
  s = CCSSSender()
  s.send("genesis", "Hello from an agent")
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import socket
import sys
import tempfile
import time
from pathlib import Path
from typing import Any

_DEFAULT_CONTACTS = (
    Path(__file__).resolve().parent.parent.parent
    / "docs" / "contact" / "ccss_contacts.json"
)
_DEFAULT_INBOX = Path.home() / ".ccss_inbox" / "genesis"
_DEFAULT_SENT  = Path.home() / ".ccss_inbox" / "sent"
_TOR_HOST  = "127.0.0.1"
_TOR_PORT  = 9050
_RELAY_HOST = "127.0.0.1"
_RELAY_PORT = 8420
_PEER_PORT  = 9001
_OUTER_ENVELOPE_BYTES = 4156
_MAX_MESSAGE_BYTES    = 2000


# ---------------------------------------------------------------------------
# Transport import
# ---------------------------------------------------------------------------

def _load_transport():
    _root = Path(__file__).resolve().parent.parent.parent
    if str(_root) not in sys.path:
        sys.path.insert(0, str(_root))
    from tools.ccss_send.ccss_transport import resolve_transport  # type: ignore
    return resolve_transport


def _seal(message: str, pubkey_hex: str) -> bytes:
    _root = Path(__file__).resolve().parent.parent.parent
    if str(_root) not in sys.path:
        sys.path.insert(0, str(_root))
    from tools.ccss_send.ccss_encrypt import seal_message  # type: ignore
    return seal_message(message, pubkey_hex)


def _write_sent(sent_dir: Path, contact_id: str, record: dict[str, Any]) -> None:
    d = sent_dir / contact_id
    d.mkdir(parents=True, exist_ok=True)
    ts, receipt = record["ts"], record["receipt"]
    out = d / f"{ts}_{receipt[:8]}.json"
    fd, tmp = tempfile.mkstemp(dir=d)
    try:
        with os.fdopen(fd, "w") as fh:
            json.dump(record, fh, allow_nan=False, sort_keys=True)
        os.replace(tmp, out)
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass


def _build_sent_record(
    *,
    ts: int,
    contact_id: str,
    message: str,
    receipt: str,
    transport: str,
) -> dict[str, Any]:
    """Build a privacy-preserving sent-log record.

    Plaintext sent-message retention is disabled by default. Operators can opt in
    for local debugging with CCSS_STORE_SENT_PLAINTEXT=1.
    """
    message_bytes = message.encode("utf-8")
    record: dict[str, Any] = {
        "ts": ts,
        "contact_id": contact_id,
        "message_bytes": len(message_bytes),
        "message_sha256": hashlib.sha256(message_bytes).hexdigest(),
        "plaintext_stored": False,
        "receipt": receipt,
        "transport": transport,
    }
    if os.environ.get("CCSS_STORE_SENT_PLAINTEXT") == "1":
        record["message"] = message
        record["plaintext_stored"] = True
    return record


# ---------------------------------------------------------------------------
# CCSSSender
# ---------------------------------------------------------------------------

class CCSSSender:
    """Programmatic CCSS sender.  All methods return JSON-serialisable dicts.

    Transport is chosen automatically per-contact:
      DirectTransport (host:port) → fastest, no Tor needed
      TorTransport (.onion)       → anonymous fallback
      D2dTransport (agent_id)     → future ILC peer routing (stub)
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
        """List contacts with transport availability. Pubkey never returned."""
        try:
            raw = json.loads(self.contacts_path.read_text())
        except FileNotFoundError:
            return []
        result = []
        for c in raw:
            ph       = c.get("ccss_recipient_pubkey", "")
            onion    = c.get("ccss_contact_onion", "")
            peer_ep  = c.get("ccss_peer_endpoint", "")
            agent_id = c.get("agent_id", "")

            def _live(v: str) -> bool:
                return bool(v) and "PLACEHOLDER" not in v.upper()

            pubkey_ok = _live(ph)
            transports = []
            if _live(peer_ep):
                transports.append("direct")
            if _live(onion):
                transports.append("tor")
            if _live(agent_id):
                transports.append("d2d(stub)")

            configured = pubkey_ok and bool(transports)
            result.append({
                "id":            c.get("id", ""),
                "name":          c.get("name", ""),
                "description":   c.get("description", ""),
                "agent_id":      agent_id,
                "onion":         onion if _live(onion) else None,
                "peer_endpoint": peer_ep if _live(peer_ep) else None,
                "transports":    transports,
                "configured":    configured,
            })
        return result

    # ── status ────────────────────────────────────────────────────────────

    def status(self) -> dict[str, Any]:
        """Check all transport endpoints + inbox count."""
        # Tor SOCKS5
        tor_ok, tor_err = False, None
        try:
            with socket.create_connection((_TOR_HOST, _TOR_PORT), timeout=3):
                tor_ok = True
        except OSError as exc:
            tor_err = str(exc)

        # Tor relay (HTTP)
        relay_ok, relay_err = False, None
        try:
            with socket.create_connection((_RELAY_HOST, _RELAY_PORT), timeout=2) as s:
                s.sendall(b"GET /health HTTP/1.0\r\nHost: 127.0.0.1\r\n\r\n")
                raw = s.recv(512)
            relay_ok = b'"status":"ok"' in raw or b'"status": "ok"' in raw
        except OSError as exc:
            relay_err = str(exc)

        # Direct peer receiver
        peer_ok, peer_err = False, None
        try:
            with socket.create_connection((_RELAY_HOST, _PEER_PORT), timeout=1):
                peer_ok = True
        except OSError as exc:
            peer_err = str(exc)

        inbox_count = sum(
            1 for f in self.inbox_dir.iterdir() if f.suffix == ".envelope"
        ) if self.inbox_dir.is_dir() else 0

        return {
            "transports": {
                "tor":    {"ok": tor_ok,   "socks5": f"{_TOR_HOST}:{_TOR_PORT}",    "error": tor_err},
                "relay":  {"ok": relay_ok, "http":   f"{_RELAY_HOST}:{_RELAY_PORT}", "error": relay_err},
                "direct": {"ok": peer_ok,  "tcp":    f"{_RELAY_HOST}:{_PEER_PORT}",  "error": peer_err},
                "d2d":    {"ok": False,    "note":   "not yet live — see ccss_d2d_transport_spec_v0.1.md"},
            },
            "inbox_count": inbox_count,
        }

    # ── send ──────────────────────────────────────────────────────────────

    def send(self, contact_id: str, message: str) -> dict[str, Any]:
        """Encrypt and deliver message.  Transport chosen automatically.

        Returns {"ok": True, "receipt": "…", "ts": …, "transport": "…", "contact_id": "…"}
        Raises ValueError (bad args / not configured) or RuntimeError (network).
        """
        if len(message.encode("utf-8")) > _MAX_MESSAGE_BYTES:
            raise ValueError(
                f"message too long (max {_MAX_MESSAGE_BYTES} bytes UTF-8)"
            )
        try:
            raw_contacts = json.loads(self.contacts_path.read_text())
        except FileNotFoundError:
            raise ValueError(f"contacts file not found: {self.contacts_path}")

        contact = next((c for c in raw_contacts if c.get("id") == contact_id), None)
        if contact is None:
            raise ValueError(f"contact not found: {contact_id!r}")

        pubkey = contact.get("ccss_recipient_pubkey", "")
        if not pubkey or "PLACEHOLDER" in pubkey.upper():
            raise ValueError(f"contact {contact_id!r}: ccss_recipient_pubkey not configured")

        resolve = _load_transport()
        transport, endpoint = resolve(contact)

        envelope = _seal(message, pubkey)
        result   = transport.send(envelope, endpoint)
        receipt  = result.get("receipt_token", hashlib.sha256(envelope).hexdigest())
        ts       = int(time.time())

        record = _build_sent_record(
            ts=ts,
            contact_id=contact_id,
            message=message,
            receipt=receipt,
            transport=transport.name,
        )
        _write_sent(self.sent_dir, contact_id, record)

        return {
            "ok":         True,
            "receipt":    receipt,
            "ts":         ts,
            "transport":  transport.name,
            "contact_id": contact_id,
        }

    # ── inbox ─────────────────────────────────────────────────────────────

    def inbox(self) -> list[dict[str, Any]]:
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
# CLI
# ---------------------------------------------------------------------------

def _out(data: Any) -> None:
    print(json.dumps(data, sort_keys=True, indent=2))

def _err(msg: str, code: int = 1) -> None:
    print(json.dumps({"ok": False, "error": msg}, sort_keys=True), file=sys.stderr)
    sys.exit(code)


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(
        prog="ccss_cli",
        description="CCSS CLI — machine-readable sender (DirectTransport / TorTransport / D2dTransport)",
    )
    ap.add_argument("--contacts", default=str(_DEFAULT_CONTACTS))
    ap.add_argument("--inbox",    default=str(_DEFAULT_INBOX))
    ap.add_argument("--sent",     default=str(_DEFAULT_SENT))
    sub = ap.add_subparsers(dest="cmd", required=True)

    sub.add_parser("contacts", help="List contacts + transport availability")
    sub.add_parser("status",   help="Check all transport endpoints")
    sp = sub.add_parser("send", help="Send to a contact (transport auto-selected)")
    sp.add_argument("contact_id")
    sp.add_argument("message", help='Text or "-" for stdin')
    sub.add_parser("inbox",    help="List received envelopes")
    sp2 = sub.add_parser("sent", help="Show sent log for a contact")
    sp2.add_argument("contact_id")

    args = ap.parse_args(argv)
    s = CCSSSender(args.contacts, args.inbox, args.sent)

    if args.cmd == "contacts":
        _out(s.contacts())
    elif args.cmd == "status":
        _out(s.status())
    elif args.cmd == "send":
        msg = sys.stdin.read().strip() if args.message == "-" else args.message
        if not msg:
            _err("empty message")
        try:
            _out(s.send(args.contact_id, msg))
        except (ValueError, RuntimeError, NotImplementedError) as exc:
            _err(str(exc))
    elif args.cmd == "inbox":
        _out(s.inbox())
    elif args.cmd == "sent":
        _out(s.sent(args.contact_id))


if __name__ == "__main__":
    main()
