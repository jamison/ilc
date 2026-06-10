#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
"""CCSS Epistemic Graph UI — graph-native operator dashboard (human interface).

Transport is selected automatically per-contact via ccss_transport.resolve_transport:
  DirectTransport (ccss_peer_endpoint host:port) — fastest, no Tor
  TorTransport    (ccss_contact_onion  .onion)   — anonymous fallback
  D2dTransport    (agent_id)                      — future ILC peer routing

Graph model:
  - Self (operator) node in the center.
  - Contact (agent) nodes orbit outward.
  - Conversation node sits on the edge midpoint between each pair.
  - Click a conversation node to compose / view sent history.

Served on 127.0.0.1:8422.  Loopback only.

Usage:
    python tools/ccss_send/ccss_chat_ui.py [--contacts <path>] [--inbox <dir>]
                                            [--sent <dir>] [--port <port>]
"""

from __future__ import annotations

import argparse
import hashlib
import http.server
import json
import os
import socket
import sys
import time
from pathlib import Path
from typing import Any

_LOOPBACK = "127.0.0.1"
_DEFAULT_PORT = 8422
_DEFAULT_HOME = Path.home() / ".ilc" / "ccss"
_DEFAULT_CONTACTS = _DEFAULT_HOME / "contacts.json"
_DEFAULT_INBOX = _DEFAULT_HOME / "inbox"
_DEFAULT_SENT = _DEFAULT_HOME / "sent"
_OUTER_ENVELOPE_BYTES = 4156
_MAX_MESSAGE_BYTES = 2000


# ---------------------------------------------------------------------------
# Transport (delegates to ccss_transport module)
# ---------------------------------------------------------------------------

def _load_transport():
    _root = Path(__file__).resolve().parent.parent.parent
    if str(_root) not in sys.path:
        sys.path.insert(0, str(_root))
    from tools.ccss_send.ccss_transport import resolve_transport  # type: ignore
    return resolve_transport


def _seal(message: str, pubkey_hex: str) -> bytes:
    try:
        from tools.ccss_send.ccss_encrypt import seal_message
    except ImportError:
        sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
        from tools.ccss_send.ccss_encrypt import seal_message  # type: ignore
    return seal_message(message, pubkey_hex)


def _read_envelope_payload(
    envelope_path: Path,
    *,
    receipt: str,
    home: str | Path | None = None,
) -> dict[str, Any]:
    from ilc_core.ccss.runtime import unseal_message

    result = unseal_message(envelope_path.read_bytes(), home=home)
    return {
        "flags": list(result.get("flags", [])),
        "message": result.get("message", ""),
        "message_bytes": result.get("message_bytes", 0),
        "ok": True,
        "receipt": receipt,
        "safe": bool(result.get("safe", True)),
    }


def _live_contact_value(value: str) -> bool:
    return bool(value) and "PLACEHOLDER" not in value.upper()


def _contact_public_view(contact: dict[str, Any]) -> dict[str, Any]:
    pubkey = contact.get("ccss_recipient_pubkey", "")
    onion = contact.get("ccss_contact_onion", "")
    peer_endpoint = contact.get("ccss_peer_endpoint", "")
    agent_id = contact.get("agent_id", "")
    transports: list[str] = []
    if _live_contact_value(peer_endpoint):
        transports.append("direct")
    if _live_contact_value(onion):
        transports.append("tor")
    if _live_contact_value(agent_id):
        transports.append("d2d(stub)")
    return {
        "id": contact.get("id", ""),
        "name": contact.get("name", ""),
        "description": contact.get("description", ""),
        "agent_id": agent_id,
        "onion": onion if _live_contact_value(onion) else "",
        "peer_endpoint": (
            peer_endpoint if _live_contact_value(peer_endpoint) else ""
        ),
        "transports": transports,
        "configured": _live_contact_value(pubkey) and bool(transports),
    }


def _build_sent_record(
    *,
    ts: int,
    contact_id: str,
    message: str,
    receipt: str,
    transport: str,
) -> dict[str, Any]:
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
# HTTP handler
# ---------------------------------------------------------------------------

class _Handler(http.server.BaseHTTPRequestHandler):
    contacts_path: Path
    inbox_dir:     Path
    sent_dir:      Path

    def log_message(self, fmt: str, *args: Any) -> None:
        pass

    def do_GET(self) -> None:
        p = self.path.split("?")[0]
        dispatch = {
            "/":              self._serve_html,
            "/api/status":    self._api_status,
            "/api/identity":  self._api_identity,
            "/api/contacts":  self._api_contacts,
            "/api/inbox":     self._api_inbox,
            "/api/read":      self._api_read,
            "/api/sent":      self._api_sent,
        }
        fn = dispatch.get(p)
        if fn:
            fn()
        else:
            self.send_error(404)

    def do_POST(self) -> None:
        if self.path == "/api/send":
            self._api_send()
        else:
            self.send_error(404)

    def _serve_html(self) -> None:
        body = _HTML.encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _api_status(self) -> None:
        self._json({
            "tor":         self._tor_live(),
            "inbox_count": self._count_inbox(),
        })

    def _api_identity(self) -> None:
        try:
            _root = Path(__file__).resolve().parent.parent.parent
            if str(_root) not in sys.path:
                sys.path.insert(0, str(_root))
            from ilc_core.ccss.runtime import identity_path  # type: ignore
            ident = json.loads(identity_path().read_text(encoding="utf-8"))
            self._json({
                "endpoint": ident.get("ccss_peer_endpoint", ""),
                "agent_id": ident.get("agent_id", ""),
                "id": ident.get("id", ""),
                "name": ident.get("name", ""),
                "onion": ident.get("ccss_contact_onion", ""),
                "pubkey": ident.get("ccss_recipient_pubkey", ""),
            })
        except Exception as exc:
            self._json({"error": str(exc)}, 500)

    @staticmethod
    def _tor_live() -> bool:
        try:
            with socket.create_connection(("127.0.0.1", 9050), timeout=2):
                return True
        except OSError:
            return False

    def _count_inbox(self) -> int:
        d = self.inbox_dir
        if not d.is_dir():
            return 0
        return sum(1 for f in d.iterdir() if f.suffix == ".envelope")

    def _api_contacts(self) -> None:
        try:
            raw = json.loads(self.contacts_path.read_text())
        except Exception:
            raw = []
        safe = []
        for c in raw:
            safe.append(_contact_public_view(c))
        self._json(safe)

    def _api_inbox(self) -> None:
        d = self.inbox_dir
        envs = []
        if d.is_dir():
            for f in d.iterdir():
                if f.suffix != ".envelope":
                    continue
                sz = f.stat().st_size
                envs.append({
                    "receipt":  f.stem,
                    "size":     sz,
                    "size_ok":  sz == _OUTER_ENVELOPE_BYTES,
                    "received": int(f.stat().st_mtime),
                })
        self._json(sorted(envs, key=lambda e: e["received"], reverse=True)[:50])

    def _api_read(self) -> None:
        from urllib.parse import parse_qs, urlparse
        qs      = parse_qs(urlparse(self.path).query)
        receipt = (qs.get("receipt") or [""])[0].strip()
        # basic sanity: hex string, sane length
        if not receipt or not all(c in "0123456789abcdefABCDEF" for c in receipt):
            self._json({"ok": False, "error": "invalid receipt"}, 400)
            return
        envelope_path = self.inbox_dir / f"{receipt}.envelope"
        if not envelope_path.is_file():
            self._json({"ok": False, "error": "envelope_not_found"}, 404)
            return
        try:
            self._json(_read_envelope_payload(envelope_path, receipt=receipt))
        except Exception as exc:
            self._json({"ok": False, "error": str(exc)}, 500)

    def _api_sent(self) -> None:
        from urllib.parse import parse_qs, urlparse
        qs  = parse_qs(urlparse(self.path).query)
        cid = (qs.get("id") or [""])[0]
        d   = self.sent_dir / cid
        msgs = []
        if d.is_dir():
            for f in d.iterdir():
                if f.suffix == ".json":
                    try:
                        msgs.append(json.loads(f.read_text()))
                    except Exception:
                        pass
        msgs.sort(key=lambda m: m.get("ts", 0))
        self._json(msgs[-50:])

    def _api_send(self) -> None:
        try:
            length = int(self.headers.get("Content-Length", 0))
        except ValueError:
            self._json({"ok": False, "error": "invalid content length"}, 400)
            return
        if length <= 0 or length > 8192:
            self.send_error(400, "payload too large")
            return
        try:
            payload = json.loads(self.rfile.read(length))
        except json.JSONDecodeError as exc:
            self._json({"ok": False, "error": f"invalid json: {exc}"}, 400)
            return
        contact_id = payload.get("contact_id", "")
        message    = payload.get("message", "")
        allow_reply = bool(payload.get("allow_reply", False))
        if not contact_id or not message:
            self._json({"ok": False, "error": "missing fields"}, 400)
            return
        if len(message.encode()) > _MAX_MESSAGE_BYTES:
            self._json({"ok": False, "error": "message too long"}, 400)
            return
        try:
            from ilc_core.ccss.runtime import _validate_message_content, CCSSRuntimeError as _CCSSRuntimeError
            _validate_message_content(message)
        except Exception as _exc:
            self._json({"ok": False, "error": f"message content rejected: {_exc}"}, 400)
            return
        try:
            contacts = json.loads(self.contacts_path.read_text())
        except Exception:
            self._json({"ok": False, "error": "contacts unavailable"}, 500)
            return
        contact = next((c for c in contacts if c.get("id") == contact_id), None)
        if not contact:
            self._json({"ok": False, "error": "contact not found"}, 404)
            return
        pubkey = contact.get("ccss_recipient_pubkey", "")
        if not pubkey or "PLACEHOLDER" in pubkey.upper():
            self._json({"ok": False, "error": "pubkey placeholder not set"}, 400)
            return
        wire_message = message
        if allow_reply:
            try:
                from ilc_core.ccss.runtime import build_allow_reply_message
                wire_message = build_allow_reply_message(message)
            except Exception as exc:
                self._json({"ok": False, "error": f"allow-reply: {exc}"}, 400)
                return
        # Resolve transport (direct peer → tor → d2d stub)
        try:
            resolve = _load_transport()
            transport, endpoint = resolve(contact)
        except ValueError as exc:
            self._json({"ok": False, "error": str(exc)}, 400)
            return
        try:
            envelope = _seal(wire_message, pubkey)
        except Exception as exc:
            self._json({"ok": False, "error": f"encrypt: {exc}"}, 500)
            return
        try:
            result = transport.send(envelope, endpoint)
        except Exception as exc:
            self._json({"ok": False, "error": f"send ({transport.name}): {exc}"}, 502)
            return
        receipt = result.get("receipt_token", hashlib.sha256(envelope).hexdigest())
        ts      = int(time.time())
        record = _build_sent_record(
            ts=ts,
            contact_id=contact_id,
            message=message,
            receipt=receipt,
            transport=transport.name,
        )
        sent_d  = self.sent_dir / contact_id
        sent_d.mkdir(parents=True, exist_ok=True)
        out     = sent_d / f"{ts}_{receipt[:8]}.json"
        import tempfile
        fd, tmp = tempfile.mkstemp(dir=sent_d)
        try:
            with os.fdopen(fd, "w") as fh:
                json.dump(record, fh, allow_nan=False, sort_keys=True)
            os.replace(tmp, out)
        except Exception:
            try:
                os.unlink(tmp)
            except OSError:
                pass
        self._json({"ok": True, "receipt": receipt, "transport": transport.name})

    def _json(self, data: Any, code: int = 200) -> None:
        body = json.dumps(data, sort_keys=True).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


# ---------------------------------------------------------------------------
# UI
# ---------------------------------------------------------------------------

_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>CCSS — Epistemic Graph</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
html,body{width:100%;height:100%;background:#07090f;overflow:hidden;
  font-family:'SF Mono',ui-monospace,monospace;color:#c0d4e4}

/* ══ GRAPH VIEW ══════════════════════════════════════════════════════════ */
#graph-view{position:absolute;inset:0;transition:opacity 0.3s,transform 0.3s}
#graph-view.hidden{opacity:0;pointer-events:none;transform:scale(0.97)}
#canvas{position:absolute;inset:0 0 24px 0;overflow:hidden}
#graph-svg{width:100%;height:100%;display:block}
#nodes{position:absolute;inset:0 0 24px 0;pointer-events:none}
.node{position:absolute;transform:translate(-50%,-50%);pointer-events:all}

/* self node */
.node-self{cursor:pointer}
.node-self .agent-ring{
  width:78px;height:78px;border-radius:50%;
  display:flex;align-items:center;justify-content:center;position:relative;
  background:radial-gradient(circle at 38% 35%,#2e1a00,#0e0800);
  border:2px solid #c88a10;
  box-shadow:0 0 32px 12px rgba(200,138,16,0.32),inset 0 1px 0 rgba(255,210,70,0.14);
  transition:box-shadow .25s,border-color .25s,transform .2s;
  animation:self-pulse 3.5s ease-in-out infinite;
}
.node-self:hover .agent-ring,.node-self.menu-open .agent-ring{
  border-color:#f0b020;transform:scale(1.08);
  box-shadow:0 0 44px 18px rgba(240,176,32,0.42);animation:none;
}
@keyframes self-pulse{
  0%,100%{box-shadow:0 0 32px 12px rgba(200,138,16,0.32)}
  50%{box-shadow:0 0 50px 20px rgba(200,138,16,0.48)}
}
.node-self .agent-avatar{font-size:1.55rem;font-weight:700;color:#f0c040}
.node-self .node-label{color:#7a5010;font-size:0.62rem}

/* outbound contact node (people you send to) */
.node-contact .agent-ring{
  width:56px;height:56px;border-radius:50%;cursor:pointer;
  display:flex;align-items:center;justify-content:center;position:relative;
  background:radial-gradient(circle at 35% 35%,#0c1e30,#060e18);
  border:2px solid #183a56;box-shadow:0 0 14px 4px rgba(24,58,86,0.28);
  transition:box-shadow .25s,transform .2s,border-color .25s;
}
.node-contact.configured .agent-ring{border-color:#1472a0;box-shadow:0 0 20px 7px rgba(20,114,160,0.3)}
.node-contact:hover .agent-ring{border-color:#40a8d8;box-shadow:0 0 30px 12px rgba(64,168,216,0.42);transform:scale(1.1)}
.node-contact .agent-avatar{font-size:1.2rem;font-weight:700;color:#a0c8e0}
.node-contact.configured .agent-avatar{color:#c4e4ff}

/* inbound identified sender node (they revealed themselves) */
.node-inbound .agent-ring{
  width:52px;height:52px;border-radius:50%;cursor:pointer;
  display:flex;align-items:center;justify-content:center;position:relative;
  background:radial-gradient(circle at 35% 35%,#1e1408,#0c0804);
  border:2px solid #3a2808;box-shadow:0 0 14px 4px rgba(80,50,10,0.3);
  transition:box-shadow .25s,transform .2s,border-color .25s;
}
.node-inbound:hover .agent-ring{border-color:#c08030;box-shadow:0 0 26px 10px rgba(192,128,48,0.4);transform:scale(1.1)}
.node-inbound .agent-avatar{font-size:1.1rem;font-weight:700;color:#c8a060}
.node-inbound .node-label{color:#5a4010}

/* anonymous node */
.node-anon .agent-ring{
  width:50px;height:50px;border-radius:50%;cursor:pointer;
  display:flex;align-items:center;justify-content:center;position:relative;
  background:radial-gradient(circle at 35% 35%,#141820,#08090f);
  border:1.5px dashed #1e2838;box-shadow:0 0 10px 3px rgba(20,24,32,0.3);
  transition:box-shadow .25s,transform .2s,border-color .25s;
}
.node-anon:hover .agent-ring{border-color:#304858;box-shadow:0 0 20px 8px rgba(48,72,88,0.4);transform:scale(1.08)}
.node-anon .agent-avatar{font-size:1.15rem;color:#304858}
.node-anon .node-label{color:#283040;font-size:0.58rem}

/* shared */
.status-dot{position:absolute;bottom:2px;right:2px;width:10px;height:10px;border-radius:50%;border:2px solid #07090f}
.status-dot.ok{background:#28d87a}.status-dot.off{background:#304050}
#inbox-badge{
  position:absolute;top:-4px;right:-4px;min-width:20px;height:20px;padding:0 4px;
  background:#c83030;border-radius:10px;border:2px solid #07090f;
  font-size:0.6rem;font-weight:700;color:#fff;
  display:none;align-items:center;justify-content:center;z-index:2;
}
.node-label{
  position:absolute;top:calc(100% + 8px);left:50%;transform:translateX(-50%);
  white-space:nowrap;font-size:0.6rem;color:#3a6070;letter-spacing:0.04em;
  pointer-events:none;text-align:center;
}
.node-self .node-label{color:#7a5010}

/* conversation node */
.conv-node{position:absolute;transform:translate(-50%,-50%);cursor:pointer;transition:transform .2s}
.conv-node:hover{transform:translate(-50%,-50%) scale(1.18)}
.conv-ring{
  width:34px;height:34px;border-radius:8px;position:relative;
  display:flex;align-items:center;justify-content:center;
  background:radial-gradient(circle at 35% 35%,#140a28,#080414);
  border:1.5px solid #3a1870;box-shadow:0 0 12px 3px rgba(58,24,112,0.28);
  transition:box-shadow .25s,border-color .25s;
}
.conv-node.configured .conv-ring{border-color:#5030b0;box-shadow:0 0 14px 5px rgba(80,48,176,0.35)}
.conv-node:hover .conv-ring{border-color:#8858e0;box-shadow:0 0 22px 9px rgba(136,88,224,0.5)}
.conv-icon{font-size:0.8rem;opacity:0.65;user-select:none}
.conv-node:hover .conv-icon{opacity:1}
.conv-badge{
  position:absolute;top:-5px;right:-5px;min-width:16px;height:16px;padding:0 3px;
  background:#5030b0;border-radius:8px;border:1.5px solid #07090f;
  font-size:0.55rem;font-weight:700;color:#d0b8ff;
  display:none;align-items:center;justify-content:center;
}
.conv-node.has-badge .conv-badge{display:flex}
/* anon conv node is a different color */
.conv-node.anon-conv .conv-ring{border-color:#1e2838}
.conv-node.anon-conv:hover .conv-ring{border-color:#406080;box-shadow:0 0 18px 7px rgba(40,80,120,0.4)}
.conv-node.anon-conv .conv-badge{background:#284060}
.conv-label{
  position:absolute;top:calc(100%+5px);left:50%;transform:translateX(-50%);
  white-space:nowrap;font-size:0.55rem;color:#2a1858;pointer-events:none;
}
.conv-node.anon-conv .conv-label{color:#1e2838}
.conv-node:hover .conv-label{color:#6040a0}
.conv-node.anon-conv:hover .conv-label{color:#406080}

/* self popup menu */
#self-menu{
  position:absolute;transform:translate(-50%,calc(-100% - 22px));
  background:#070d18;border:1px solid #1e3a58;border-radius:12px;
  padding:0;z-index:30;min-width:230px;
  box-shadow:0 8px 32px rgba(0,0,0,0.7);
  display:none;pointer-events:all;
}
#self-menu.open{display:block}
.sm-head{padding:14px 16px 10px;border-bottom:1px solid #0e2030;display:flex;align-items:flex-start;gap:10px}
.sm-av{width:34px;height:34px;border-radius:8px;flex-shrink:0;
  background:radial-gradient(circle,#2e1a00,#07090f);border:1.5px solid #c88a10;
  display:flex;align-items:center;justify-content:center;font-size:0.9rem;font-weight:700;color:#f0c040}
.sm-meta{flex:1;min-width:0}
.sm-name{font-size:0.82rem;font-weight:700;color:#f0c040}
.sm-you{font-size:0.6rem;color:#7a5010;margin-top:1px}
.sm-id{font-size:0.52rem;color:#1e3858;margin-top:4px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;font-family:monospace}
.sm-close{background:none;border:none;color:#2a4060;cursor:pointer;font-size:1rem;padding:2px;flex-shrink:0}
.sm-close:hover{color:#c0d4e4}
.sm-items{padding:6px 0 8px}
.sm-item{display:flex;align-items:center;gap:10px;padding:9px 16px;cursor:pointer;font-size:0.72rem;color:#4a7090;transition:background .15s,color .15s}
.sm-item:hover{background:#0a1828;color:#90c8e8}
.sm-item-icon{font-size:1rem;width:20px;text-align:center;flex-shrink:0}
.sm-item-badge{background:#c83030;border-radius:8px;padding:1px 6px;font-size:0.58rem;font-weight:700;color:#fff}
.sm-item-badge.zero{background:#1e3040;color:#3a6070}
.sm-sep{height:1px;background:#0a1828;margin:4px 0}

/* status bar */
#sb{position:fixed;bottom:0;left:0;right:0;height:24px;background:#04060c;border-top:1px solid #0a1018;
  display:flex;align-items:center;padding:0 12px;gap:12px;font-size:0.56rem;color:#1e3050;z-index:5}
.sb-dot{width:5px;height:5px;border-radius:50%;display:inline-block;margin-right:3px}
.sb-dot.ok{background:#28d87a}.sb-dot.off{background:#c03030}

/* ══ CHAT VIEW ════════════════════════════════════════════════════════════ */
#chat-view{
  position:absolute;inset:0;display:flex;flex-direction:column;
  opacity:0;pointer-events:none;
  transition:opacity 0.3s,transform 0.3s;transform:translateY(18px);
}
#chat-view.open{opacity:1;pointer-events:all;transform:translateY(0)}
#chat-header{
  display:flex;align-items:center;gap:12px;
  padding:0 16px;height:56px;flex-shrink:0;
  background:#070d18;border-bottom:1px solid #0e2030;z-index:2;
}
#chat-back{background:none;border:none;color:#3a7090;cursor:pointer;font-size:1.2rem;padding:4px 8px 4px 0;transition:color .15s}
#chat-back:hover{color:#80c8e8}
#chat-av{
  width:38px;height:38px;border-radius:50%;flex-shrink:0;
  display:flex;align-items:center;justify-content:center;
  font-size:1rem;font-weight:700;
}
#chat-av.type-contact{background:radial-gradient(circle at 35%35%,#0c1e30,#060e18);border:2px solid #1472a0;color:#c4e4ff}
#chat-av.type-inbound{background:radial-gradient(circle at 35%35%,#1e1408,#0c0804);border:2px solid #c08030;color:#c8a060}
#chat-av.type-anon{background:radial-gradient(circle at 35%35%,#141820,#08090f);border:1.5px dashed #304858;color:#304858;font-size:1.3rem}
#chat-meta{flex:1;min-width:0}
#chat-name{font-size:0.86rem;font-weight:600;color:#c0d4e4}
#chat-sub{font-size:0.56rem;color:#2a4a6a;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;margin-top:2px}
#chat-thread{
  flex:1;overflow-y:auto;padding:16px 14px 8px;
  display:flex;flex-direction:column;gap:6px;background:#07090f;
}
#chat-thread::-webkit-scrollbar{width:3px}
#chat-thread::-webkit-scrollbar-thumb{background:#101c2c;border-radius:2px}
.bubble-sent{
  align-self:flex-end;max-width:72%;
  background:#0d2e4a;border:1px solid #163c5a;
  border-radius:14px 14px 3px 14px;padding:9px 13px;
}
.bubble-sent .btext{font-size:0.76rem;color:#c8e0f8;line-height:1.55;word-break:break-word}
.bubble-sent .bmeta{margin-top:4px;font-size:0.54rem;color:#2a5070;text-align:right}
.bubble-recv{
  align-self:flex-start;max-width:72%;
  background:#0c1a26;border:1px solid #102030;
  border-radius:14px 14px 14px 3px;padding:9px 13px;
}
.bubble-recv.identified{background:#1a1006;border-color:#2a1c08}
.bubble-recv .btext{font-size:0.76rem;color:#7a9aaa;line-height:1.55;word-break:break-word;font-style:italic}
.bubble-recv.revealed .btext{color:#a0c0d8;font-style:normal}
.bubble-recv.identified.revealed .btext{color:#c8a060;font-style:normal}
.safety-warn{margin-top:6px;padding:5px 8px;border-radius:5px;background:#2a0a08;border:1px solid #7a2018;color:#e08070;font-size:0.62rem;line-height:1.5}
.safety-warn code{background:#1a0604;border-radius:3px;padding:1px 4px;color:#e09080;font-size:0.6rem}
.bubble-recv .bmeta{margin-top:4px;font-size:0.54rem;color:#1e3a52;display:flex;align-items:center;gap:8px;flex-wrap:wrap}
.decrypt-btn{
  background:#081828;border:1px solid #1a4060;border-radius:4px;
  color:#3a80b0;font-size:0.56rem;padding:2px 8px;cursor:pointer;font-family:inherit;
}
.decrypt-btn:hover{background:#0c2438;color:#60a8d0}
.reply-btn{
  background:#1a1008;border:1px solid #3a2408;border-radius:4px;
  color:#c08030;font-size:0.56rem;padding:2px 8px;cursor:pointer;font-family:inherit;
}
.reply-btn:hover{background:#221408;color:#e0a050}
.day-sep{
  align-self:center;font-size:0.56rem;color:#1e3050;
  padding:2px 10px;background:#0a1020;border-radius:8px;margin:6px 0;
}
/* compose */
#chat-compose{flex-shrink:0;background:#070d18;border-top:1px solid #0e2030}
#reply-row{
  display:flex;align-items:center;gap:7px;
  padding:7px 14px 0;
}
#reply-check{width:13px;height:13px;cursor:pointer;accent-color:#1472a0;flex-shrink:0}
#reply-label{font-size:0.6rem;color:#2a5070;cursor:pointer;user-select:none}
#reply-label:hover{color:#4a90b8}
.info-icon{font-size:0.65rem;color:#1a3858;cursor:help;position:relative}
.info-icon .tip{
  display:none;position:absolute;bottom:calc(100%+8px);left:50%;transform:translateX(-50%);
  width:260px;background:#060d18;border:1px solid #1e3a58;border-radius:8px;
  padding:10px 12px;font-size:0.62rem;color:#5a90b8;line-height:1.6;
  box-shadow:0 6px 24px rgba(0,0,0,0.7);pointer-events:none;z-index:50;white-space:normal;
}
.info-icon .tip b{color:#7ab8e0}
.info-icon .tip::after{content:'';position:absolute;top:100%;left:50%;transform:translateX(-50%);
  border:5px solid transparent;border-top-color:#1e3a58}
.info-icon:hover .tip{display:block}
#compose-row{display:flex;align-items:flex-end;gap:10px;padding:8px 14px 12px}
#compose-ta{
  flex:1;min-height:40px;max-height:120px;
  background:#04080e;border:1px solid #182a3e;border-radius:20px;
  color:#c0d4e4;font-family:inherit;font-size:0.76rem;
  padding:9px 14px;resize:none;outline:none;line-height:1.5;overflow-y:auto;
}
#compose-ta:focus{border-color:#1e5070}
#compose-ta::placeholder{color:#1e3050}
#send-btn{
  width:38px;height:38px;flex-shrink:0;border-radius:50%;
  background:#0e2e48;border:1.5px solid #1a5070;
  color:#60b8e0;font-size:1rem;cursor:pointer;
  display:flex;align-items:center;justify-content:center;
  transition:background .2s,transform .15s;
}
#send-btn:hover:not(:disabled){background:#163a5a;color:#90d0f0;transform:scale(1.08)}
#send-btn:disabled{opacity:0.25;cursor:not-allowed}
#byte-ctr{font-size:0.54rem;color:#1e3050;align-self:center;min-width:56px;text-align:right}
#byte-ctr.warn{color:#c07830}
#byte-ctr.over{color:#c03030}
</style>
</head>
<body>

<!-- ══ GRAPH VIEW ══════════════════════════════════════════════════════════ -->
<div id="graph-view">
  <div id="canvas">
  <svg id="graph-svg" viewBox="0 0 1000 680" preserveAspectRatio="xMidYMid meet">
  <defs>
    <radialGradient id="gSelf" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#1a0e00" stop-opacity="0.9"/>
      <stop offset="100%" stop-color="#1a0e00" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="gOuter" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#050e1e" stop-opacity="0.7"/>
      <stop offset="100%" stop-color="#050e1e" stop-opacity="0"/>
    </radialGradient>
    <filter id="blur40"><feGaussianBlur stdDeviation="40"/></filter>
  </defs>
  <circle cx="500" cy="340" r="200" fill="url(#gSelf)" filter="url(#blur40)" opacity="0.8"/>
  <circle cx="500" cy="340" r="380" fill="url(#gOuter)" filter="url(#blur40)" opacity="0.5"/>
  <circle cx="500" cy="340" r="260" fill="none" stroke="#0e2030"
          stroke-width="0.8" stroke-dasharray="4 9" opacity="0.35"/>
  <g id="edges"></g>
  </svg>
  </div>
  <div id="nodes"></div>
  <div id="self-menu">
    <div class="sm-head">
      <div class="sm-av" id="sm-av">?</div>
      <div class="sm-meta">
        <div class="sm-name" id="sm-name">—</div>
        <div class="sm-you">(you)</div>
        <div class="sm-id" id="sm-id"></div>
      </div>
      <button class="sm-close" onclick="closeSelfMenu()">✕</button>
    </div>
    <div class="sm-items">
      <div class="sm-item" onclick="openChat('__anon__')">
        <span class="sm-item-icon">👤</span>
        <span class="sm-item-label">Anonymous messages</span>
        <span class="sm-item-badge zero" id="sm-inbox-badge">0</span>
      </div>
      <div class="sm-sep"></div>
      <div class="sm-item" style="cursor:default;opacity:0.4">
        <span class="sm-item-icon">🔑</span>
        <span class="sm-item-label" id="sm-pubkey" style="font-size:0.56rem;font-family:monospace;color:#1a3050">—</span>
      </div>
    </div>
  </div>
</div>

<!-- ══ CHAT VIEW ══════════════════════════════════════════════════════════ -->
<div id="chat-view">
  <div id="chat-header">
    <button id="chat-back" onclick="closeChat()">←</button>
    <div id="chat-av" class="type-contact">?</div>
    <div id="chat-meta">
      <div id="chat-name">—</div>
      <div id="chat-sub"></div>
    </div>
  </div>
  <div id="chat-thread"></div>
  <div id="chat-compose">
    <div id="reply-row">
      <input type="checkbox" id="reply-check">
      <label id="reply-label" for="reply-check">Allow reply to this message</label>
      <span class="info-icon">ⓘ
        <span class="tip">By default all messages are sealed and the recipient
cannot identify you or respond. Checking <b>Allow reply</b> includes your
public key and endpoint inside this encrypted message only, so the recipient
can write back.<br><br>
<b>Note:</b> once a recipient has received your key in any message, they have
it permanently — sending anonymously later does not un-share it with them.</span>
      </span>
    </div>
    <div id="compose-row">
      <textarea id="compose-ta" placeholder="Message…" rows="1"
                oninput="onType()" onkeydown="onKey(event)"></textarea>
      <span id="byte-ctr"></span>
      <button id="send-btn" onclick="doSend()" disabled>↑</button>
    </div>
  </div>
</div>

<!-- status bar -->
<div id="sb">
  <span><span class="sb-dot off" id="sb-tor"></span><span id="sb-tor-lbl">Tor offline</span></span>
</div>

<script>
const VBW = 1000, VBH = 680, SELF_X = 500, SELF_Y = 340, ORBIT_R = 260;
const ANON_ID = '__anon__';

let contacts        = [];   // outbound contacts from /api/contacts
let selfIdent       = {};   // our own identity
let inboundSenders  = {};   // { senderId: { replyTo, receipts:Set } } — revealed this session
let decryptCache    = {};   // { receipt: { plaintext, replyTo } }
let inboxEnvelopes  = [];   // latest /api/inbox result
let activeId        = null;
let selfMenuOpen    = false;

// ── boot ──────────────────────────────────────────────────────────────────
async function boot() {
  await Promise.all([loadContacts(), loadIdentity(), refreshInbox()]);
  pollStatus();
  setInterval(pollStatus, 6000);
  setInterval(refreshInbox, 8000);
}

async function loadIdentity() {
  try {
    const r = await fetch('/api/identity');
    selfIdent = await r.json();
    const lbl = document.getElementById('self-label');
    if (lbl) lbl.textContent = (selfIdent.name||selfIdent.id||'you') + ' (you)';
    const av = document.getElementById('self-avatar');
    if (av) av.textContent = (selfIdent.name||'Y')[0].toUpperCase();
  } catch(_) {}
}

async function refreshInbox() {
  try {
    const r = await fetch('/api/inbox');
    inboxEnvelopes = await r.json();
    updateAnonBadge();
  } catch(_) {}
}

// ── graph render ──────────────────────────────────────────────────────────
async function loadContacts() {
  const r  = await fetch('/api/contacts');
  contacts = await r.json();
  renderGraph();
}

function allGraphNodes() {
  // outbound contacts + inbound identified senders + anonymous node
  const inbound = Object.entries(inboundSenders).map(([id, s]) => ({
    _type: 'inbound', id, name: s.replyTo.name || id.slice(0,12)+'…',
    replyTo: s.replyTo, receipts: s.receipts,
    configured: !!(s.replyTo.pubkey && s.replyTo.endpoint),
  }));
  const anon = { _type:'anon', id: ANON_ID, name:'Anonymous', configured: false };
  return [...contacts.map(c => ({...c, _type:'contact'})), ...inbound, anon];
}

function nodePos(i, total) {
  const angle = (i * (2*Math.PI/total)) - Math.PI/2;
  return { x: SELF_X + ORBIT_R*Math.cos(angle), y: SELF_Y + ORBIT_R*Math.sin(angle) };
}
function midpoint(cx, cy) { return { x:(SELF_X+cx)/2, y:(SELF_Y+cy)/2 }; }

function renderGraph() {
  document.getElementById('edges').innerHTML = '';
  document.getElementById('nodes').innerHTML  = '';

  placeEl(makeSelfNode(), SELF_X, SELF_Y);

  const nodes = allGraphNodes();
  nodes.forEach((n, i) => {
    const cp = nodePos(i, nodes.length);
    const mp = midpoint(cp.x, cp.y);

    // edge
    const line = svgEl('line', {id:'edge-'+n.id, x1:SELF_X,y1:SELF_Y,x2:cp.x,y2:cp.y});
    const edgeColor = n._type==='anon' ? '#0a1520' : n._type==='inbound' ? '#1a1008' : '#0e2030';
    Object.assign(line.style,{stroke:edgeColor,strokeWidth:'1.2',strokeDasharray:'5 7',
      fill:'none',opacity:'0.5',transition:'stroke .3s,opacity .3s'});
    document.getElementById('edges').appendChild(line);

    placeEl(makeNodeEl(n), cp.x, cp.y);

    const cv = makeConvNode(n.id, n._type);
    placeEl(cv, mp.x, mp.y);
  });

  // reposition self-menu
  const menu = document.getElementById('self-menu');
  menu.style.left = pct(SELF_X, VBW);
  menu.style.top  = pct(SELF_Y, VBH);

  updateAnonBadge();
}

function makeSelfNode() {
  const wrap = div('node node-self'); wrap.id='node-self'; wrap.onclick=toggleSelfMenu;
  const ring = div('agent-ring');
  const av   = div('agent-avatar'); av.id='self-avatar';
  av.textContent = (selfIdent.name||'Y')[0]?.toUpperCase()||'Y';
  ring.appendChild(av);
  const badge = div(''); badge.id='inbox-badge'; ring.appendChild(badge);
  wrap.appendChild(ring);
  const lbl = div('node-label'); lbl.id='self-label';
  lbl.textContent = selfIdent.name ? selfIdent.name+' (you)' : '… (you)';
  wrap.appendChild(lbl);
  return wrap;
}

function makeNodeEl(n) {
  let cls = 'node ';
  if      (n._type==='anon')    cls += 'node-anon';
  else if (n._type==='inbound') cls += 'node-inbound';
  else                          cls += 'node-contact' + (n.configured?' configured':'');
  const wrap = div(cls); wrap.id='node-'+n.id;
  const ring = div('agent-ring');
  const av   = div('agent-avatar');
  av.textContent = n._type==='anon' ? '👤' : (n.name||'?')[0].toUpperCase();
  ring.appendChild(av);
  if (n._type!=='anon') {
    const dot = div('status-dot '+(n.configured?'ok':'off')); ring.appendChild(dot);
  }
  wrap.appendChild(ring);
  const lbl = div('node-label'); lbl.textContent = n.name; wrap.appendChild(lbl);
  wrap.onclick = () => openChat(n.id);
  return wrap;
}

function makeConvNode(nodeId, nodeType) {
  const isAnon = nodeType==='anon';
  const wrap = div('conv-node'+(isAnon?' anon-conv configured':' configured'));
  wrap.id = 'conv-'+nodeId;
  const ring = div('conv-ring');
  const icon = div('conv-icon'); icon.textContent='◈'; ring.appendChild(icon);
  const badge = div('conv-badge'); badge.id='cbadge-'+nodeId; ring.appendChild(badge);
  wrap.appendChild(ring);
  const lbl = div('conv-label');
  lbl.textContent = isAnon ? 'anonymous' : 'conversation';
  wrap.appendChild(lbl);
  wrap.onclick = () => openChat(nodeId);
  return wrap;
}

function placeEl(el, svgX, svgY) {
  el.style.left = pct(svgX, VBW); el.style.top = pct(svgY, VBH);
  document.getElementById('nodes').appendChild(el);
}

function updateAnonBadge() {
  const n = inboxEnvelopes.length;
  // inbox badge on self node ring
  const badge = document.getElementById('inbox-badge');
  if (badge) {
    badge.style.cssText = n
      ? 'position:absolute;top:-4px;right:-4px;min-width:20px;height:20px;padding:0 4px;background:#c83030;border-radius:10px;border:2px solid #07090f;font-size:0.6rem;font-weight:700;color:#fff;display:flex;align-items:center;justify-content:center;z-index:2'
      : 'display:none';
    badge.textContent = n;
  }
  // conv badge on anon node
  const cb = document.getElementById('cbadge-'+ANON_ID);
  if (cb) {
    cb.textContent = n;
    const convNode = document.getElementById('conv-'+ANON_ID);
    convNode?.classList.toggle('has-badge', n>0);
  }
  // self-menu badge
  const smb = document.getElementById('sm-inbox-badge');
  if (smb) { smb.textContent = n; smb.className='sm-item-badge'+(n?'':' zero'); }
}

// ── self menu ─────────────────────────────────────────────────────────────
function toggleSelfMenu(e) {
  e?.stopPropagation();
  selfMenuOpen = !selfMenuOpen;
  document.getElementById('self-menu').classList.toggle('open', selfMenuOpen);
  document.getElementById('node-self').classList.toggle('menu-open', selfMenuOpen);
  if (selfMenuOpen) {
    const name = selfIdent.name||selfIdent.id||'Unknown';
    document.getElementById('sm-av').textContent   = name[0].toUpperCase();
    document.getElementById('sm-name').textContent = name;
    document.getElementById('sm-id').textContent   = selfIdent.agent_id
      ? selfIdent.agent_id.slice(0,40)+'…' : '';
    document.getElementById('sm-pubkey').textContent = selfIdent.pubkey
      ? selfIdent.pubkey.slice(0,32)+'…' : '(pubkey)';
  }
}
function closeSelfMenu() {
  selfMenuOpen = false;
  document.getElementById('self-menu').classList.remove('open');
  document.getElementById('node-self').classList.remove('menu-open');
}
document.addEventListener('click', e => {
  if (selfMenuOpen
      && !document.getElementById('self-menu').contains(e.target)
      && !document.getElementById('node-self').contains(e.target))
    closeSelfMenu();
});

// ── chat view ─────────────────────────────────────────────────────────────
function showChatView() {
  document.getElementById('graph-view').classList.add('hidden');
  document.getElementById('chat-view').classList.add('open');
}
function closeChat() {
  document.getElementById('chat-view').classList.remove('open');
  document.getElementById('graph-view').classList.remove('hidden');
  activeId = null;
  document.getElementById('compose-ta').value = '';
  document.getElementById('byte-ctr').textContent = '';
  document.getElementById('send-btn').disabled = true;
  if (document.getElementById('reply-check'))
    document.getElementById('reply-check').checked = false;
}

async function openChat(id) {
  closeSelfMenu();
  activeId = id;

  const av   = document.getElementById('chat-av');
  const name = document.getElementById('chat-name');
  const sub  = document.getElementById('chat-sub');

  if (id === ANON_ID) {
    av.className = 'type-anon'; av.textContent = '👤';
    name.textContent = 'Anonymous messages';
    sub.textContent  = 'Sealed envelopes from unknown senders — tap to decrypt';
    document.getElementById('chat-compose').style.display = 'none';
  } else {
    document.getElementById('chat-compose').style.display = '';
    if (document.getElementById('reply-check'))
      document.getElementById('reply-check').checked = false;

    const inbound = inboundSenders[id];
    if (inbound) {
      av.className = 'type-inbound';
      av.textContent = (inbound.replyTo.name||'?')[0].toUpperCase();
      name.textContent = inbound.replyTo.name || id;
      sub.textContent  = inbound.replyTo.endpoint || inbound.replyTo.agent_id || '(identified sender)';
    } else {
      const c = contacts.find(x => x.id===id) || {};
      av.className = 'type-contact';
      av.textContent = (c.name||'?')[0].toUpperCase();
      name.textContent = c.name || id;
      sub.textContent  = c.peer_endpoint || c.agent_id || '(not configured)';
    }

    document.getElementById('compose-ta').value = '';
    onType();
    const isConfigured = id in inboundSenders
      ? !!(inboundSenders[id].replyTo.pubkey && inboundSenders[id].replyTo.endpoint)
      : !!(contacts.find(x=>x.id===id)?.configured);
    document.getElementById('send-btn').disabled = !isConfigured;
    if (!isConfigured) {
      // show send status explanation? just leave disabled for now
    }
  }

  showChatView();
  await renderThread(id);
  if (id !== ANON_ID) document.getElementById('compose-ta').focus();
}

// ── thread rendering ──────────────────────────────────────────────────────
async function renderThread(id) {
  const th = document.getElementById('chat-thread');
  th.innerHTML = '<div class="day-sep">loading…</div>';

  if (id === ANON_ID) {
    await refreshInbox();
    renderAnonThread(th);
    return;
  }

  const inbound = inboundSenders[id];
  if (inbound) {
    renderInboundThread(th, id, inbound);
    return;
  }

  // outbound contact: sent (right) + all inbox (left, since unattributed)
  const [sentR] = await Promise.all([
    fetch('/api/sent?id='+encodeURIComponent(id)),
  ]);
  const sent = await sentR.json();

  const items = [
    ...sent.map(m  => ({dir:'out', ts:m.ts,         data:m})),
    ...inboxEnvelopes.map(e => ({dir:'in', ts:e.received, data:e})),
  ].sort((a,b)=>a.ts-b.ts);

  th.innerHTML = items.length ? renderItems(items) :
    '<div class="day-sep" style="margin-top:40px">No messages yet</div>';
  th.scrollTop = th.scrollHeight;
}

function renderAnonThread(th) {
  if (!inboxEnvelopes.length) {
    th.innerHTML = '<div class="day-sep" style="margin-top:40px">No anonymous messages</div>';
    return;
  }
  const items = inboxEnvelopes.map(e => ({dir:'in', ts:e.received, data:e}))
    .sort((a,b)=>a.ts-b.ts);
  th.innerHTML = renderItems(items);
  th.scrollTop = th.scrollHeight;
  // re-apply cached decrypts
  for (const [rct, cached] of Object.entries(decryptCache)) {
    applyDecrypt(rct, cached.plaintext, cached.replyTo, false);
  }
}

function renderInboundThread(th, id, inbound) {
  const items = [...inbound.receipts].map(rct => {
    const e = inboxEnvelopes.find(x=>x.receipt===rct);
    return { dir:'in', ts: e?.received || 0, data: e || {receipt:rct,size:4156,size_ok:true,received:0} };
  }).sort((a,b)=>a.ts-b.ts);
  th.innerHTML = items.length ? renderItems(items) :
    '<div class="day-sep" style="margin-top:40px">No messages from this sender yet</div>';
  th.scrollTop = th.scrollHeight;
  for (const rct of inbound.receipts) {
    const cached = decryptCache[rct];
    if (cached) applyDecrypt(rct, cached.plaintext, cached.replyTo, false);
  }
}

function renderItems(items) {
  let lastDay = '';
  return items.map(item => {
    const dt  = new Date(item.ts*1000);
    const day = dt.toLocaleDateString();
    let sep = '';
    if (day !== lastDay) { sep=`<div class="day-sep">${esc(day)}</div>`; lastDay=day; }
    const time = dt.toLocaleTimeString([],{hour:'2-digit',minute:'2-digit'});
    if (item.dir==='out') {
      const m=item.data;
      const body = m.plaintext_stored
        ? esc(m.message||'')
        : `<span style="color:#4a7090">sealed · ${esc(String(m.message_bytes||0))} B</span>`;
      return sep+`<div class="bubble-sent">
        <div class="btext">${body}</div>
        <div class="bmeta">${esc(time)} · ${esc(m.transport||'?')}</div>
      </div>`;
    } else {
      const e=item.data, rct=esc(e.receipt);
      return sep+`<div class="bubble-recv" id="brecv-${rct}">
        <div class="btext" id="btext-${rct}" style="color:#2a4060;font-style:italic">
          sealed · ${e.size_ok?'✓':'⚠'} ${e.size} B
        </div>
        <div class="bmeta" id="bmeta-${rct}">
          <span>${esc(time)}</span>
          <button class="decrypt-btn" id="dbtn-${rct}" onclick="decryptBubble('${rct}')">Decrypt</button>
        </div>
      </div>`;
    }
  }).join('');
}

// ── decrypt ───────────────────────────────────────────────────────────────
async function decryptBubble(receipt) {
  const btn = document.getElementById('dbtn-'+receipt);
  if (!btn) return;
  btn.disabled=true; btn.textContent='…';
  try {
    const r    = await fetch('/api/read?receipt='+encodeURIComponent(receipt));
    const data = await r.json();
    if (data.ok) {
      let plaintext=data.message, replyTo=null;
      try {
        const p=JSON.parse(data.message);
        if (p&&p.v===1&&p.msg){ plaintext=p.msg; replyTo=p.reply_to||null; }
      } catch(_) {}
      const safe  = data.safe !== false;   // default true if field absent
      const flags = Array.isArray(data.flags) ? data.flags : [];
      decryptCache[receipt]={plaintext, replyTo, safe, flags};
      applyDecrypt(receipt, plaintext, replyTo, true, safe, flags);
    } else { btn.textContent='err'; btn.disabled=false; }
  } catch(_) { btn.textContent='!'; btn.disabled=false; }
}

function applyDecrypt(receipt, plaintext, replyTo, updateGraph, safe=true, flags=[]) {
  const text   = document.getElementById('btext-'+receipt);
  const meta   = document.getElementById('bmeta-'+receipt);
  const bubble = document.getElementById('brecv-'+receipt);
  const btn    = document.getElementById('dbtn-'+receipt);
  if (text) {
    const color = replyTo ? '#c8a060' : '#a0c0d8';
    // Use DOM textContent — the browser treats the string as literal characters,
    // never as HTML or script. No filter is required because nothing executes.
    text.textContent = '';
    const span = document.createElement('span');
    span.style.color = color;
    span.textContent = plaintext;   // ← raw text, always inert
    text.appendChild(span);
    // Safety warning banner — shown when the content inspector flagged threats.
    // This is informational; the primary protection is textContent above.
    const existingWarn = bubble?.querySelector('.safety-warn');
    if (existingWarn) existingWarn.remove();
    if (!safe && flags.length) {
      const warn = document.createElement('div');
      warn.className = 'safety-warn';
      const flagTags = flags.map(f => `<code>${esc(f)}</code>`).join(' ');
      warn.innerHTML = `⚠ Content flagged — review before acting: ${flagTags}`;
      text.insertAdjacentElement('afterend', warn);
    }
    bubble?.classList.add('revealed');
    if (replyTo) bubble?.classList.add('identified');
  }
  if (btn) { btn.textContent='✓'; btn.style.opacity='0.4'; btn.style.cursor='default'; btn.disabled=true; }

  if (replyTo && replyTo.pubkey) {
    // add reply button
    if (meta && !meta.querySelector('.reply-btn')) {
      const rb = document.createElement('button');
      rb.className='reply-btn';
      rb.textContent = '↩ ' + esc(replyTo.name || replyTo.pubkey.slice(0,10)+'…');
      rb.onclick = () => promoteInboundSender(receipt, replyTo);
      meta.appendChild(rb);
    }
    // register inbound sender and re-render graph
    if (updateGraph) {
      const sid = 'in-'+replyTo.pubkey.slice(0,12);
      if (!inboundSenders[sid]) {
        inboundSenders[sid] = { replyTo, receipts: new Set() };
      }
      inboundSenders[sid].receipts.add(receipt);
      renderGraph();  // adds new node to orbit
    }
  }
}

function promoteInboundSender(receipt, replyTo) {
  const sid = 'in-'+replyTo.pubkey.slice(0,12);
  if (!inboundSenders[sid]) inboundSenders[sid]={replyTo,receipts:new Set()};
  inboundSenders[sid].receipts.add(receipt);
  renderGraph();
  openChat(sid);
}

// ── compose ───────────────────────────────────────────────────────────────
function onType() {
  const ta    = document.getElementById('compose-ta');
  const bytes = new TextEncoder().encode(ta.value).length;
  const ctr   = document.getElementById('byte-ctr');
  ta.style.height='auto';
  ta.style.height=Math.min(ta.scrollHeight,120)+'px';
  ctr.textContent = bytes>1800 ? bytes+'/2000' : '';
  ctr.className   = bytes>2000?'over':bytes>1800?'warn':'';
  const configured =
    activeId in inboundSenders
      ? !!(inboundSenders[activeId].replyTo.pubkey && inboundSenders[activeId].replyTo.endpoint)
      : !!(contacts.find(x=>x.id===activeId)?.configured);
  document.getElementById('send-btn').disabled = !ta.value.trim()||bytes>2000||!configured;
}
function onKey(e) { if (e.key==='Enter'&&!e.shiftKey){e.preventDefault();doSend();} }

async function doSend() {
  const ta          = document.getElementById('compose-ta');
  const allowReply  = document.getElementById('reply-check')?.checked;
  const msg = ta.value.trim();
  if (!msg || !activeId) return;
  const btn = document.getElementById('send-btn');
  btn.disabled = true;

  // optimistic bubble — use DOM API so sent text is always inert characters
  const now=Date.now(), th=document.getElementById('chat-thread');
  const tmp=div('bubble-sent'); tmp.id='tmp-'+now;
  const btxt=div('btext'); btxt.textContent=msg;
  const bmeta=div('bmeta'); bmeta.style.color='#1a4a70';
  bmeta.textContent='sending…'+(allowReply?' · reply allowed':'');
  tmp.appendChild(btxt); tmp.appendChild(bmeta);
  th.appendChild(tmp); th.scrollTop=th.scrollHeight;
  ta.value='';
  if (document.getElementById('reply-check'))
    document.getElementById('reply-check').checked=false;
  onType();

  try {
    const r    = await fetch('/api/send',{
      method:'POST',headers:{'Content-Type':'application/json'},
      body:JSON.stringify({allow_reply:!!allowReply,contact_id:activeId,message:msg}),
    });
    const data = await r.json();
    const el   = document.getElementById('tmp-'+now);
    if (data.ok) {
      if (el) el.querySelector('.bmeta').textContent =
        new Date().toLocaleTimeString([],{hour:'2-digit',minute:'2-digit'})
        + ' · '+(data.transport||'?')+(allowReply?' · reply allowed':'');
      const edge=document.getElementById('edge-'+activeId);
      if (edge){const p=edge.style.stroke;edge.style.stroke='#28d87a';setTimeout(()=>{edge.style.stroke=p;},1400);}
    } else {
      if (el) el.querySelector('.bmeta').innerHTML=
        `<span style="color:#c04030">failed: ${esc(data.error||'?')}</span>`;
      btn.disabled=false;
    }
  } catch(e) {
    btn.disabled=false;
    const el=document.getElementById('tmp-'+now);
    if (el) el.querySelector('.bmeta').innerHTML=`<span style="color:#c04030">network error</span>`;
  }
}

// ── status ────────────────────────────────────────────────────────────────
async function pollStatus() {
  try {
    const d=await (await fetch('/api/status')).json();
    document.getElementById('sb-tor').className='sb-dot '+(d.tor?'ok':'off');
    document.getElementById('sb-tor-lbl').textContent=d.tor?'Tor connected':'Tor offline';
  } catch(_) {}
}

// ── helpers ───────────────────────────────────────────────────────────────
function div(cls){const el=document.createElement('div');if(cls)el.className=cls;return el;}
function svgEl(tag,attrs){
  const el=document.createElementNS('http://www.w3.org/2000/svg',tag);
  for(const [k,v] of Object.entries(attrs))el.setAttribute(k,v);return el;
}
function pct(v,total){return (v/total*100).toFixed(3)+'%';}
function esc(s){
  return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

boot();
</script>
</body>
</html>
"""


# ---------------------------------------------------------------------------
# Server
# ---------------------------------------------------------------------------

def _make_server(contacts_path, inbox_dir, sent_dir, port):
    class H(_Handler):
        pass
    H.contacts_path = contacts_path
    H.inbox_dir     = inbox_dir
    H.sent_dir      = sent_dir
    return http.server.HTTPServer((_LOOPBACK, port), H)


def main() -> None:
    ap = argparse.ArgumentParser(description="CCSS Epistemic Graph UI")
    ap.add_argument("--contacts", default=str(_DEFAULT_CONTACTS))
    ap.add_argument("--inbox",    default=str(_DEFAULT_INBOX))
    ap.add_argument("--sent",     default=str(_DEFAULT_SENT))
    ap.add_argument("--port",     type=int, default=_DEFAULT_PORT)
    args = ap.parse_args()

    contacts_path = Path(args.contacts)
    inbox_dir     = Path(args.inbox)
    sent_dir      = Path(args.sent)
    inbox_dir.mkdir(parents=True, exist_ok=True)
    sent_dir.mkdir(parents=True, exist_ok=True)

    srv = _make_server(contacts_path, inbox_dir, sent_dir, args.port)
    url = f"http://{_LOOPBACK}:{args.port}/"
    print(f"CCSS Epistemic Graph  →  {url}")
    print(f"Contacts: {contacts_path}")
    print(f"Ctrl-C to stop.")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        srv.server_close()


if __name__ == "__main__":
    main()
