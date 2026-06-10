#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
"""CCSS Epistemic Graph UI — graph-native operator dashboard (human interface).

Transport is selected automatically per-contact via ccss_transport.resolve_transport:
  DirectTransport (ccss_peer_endpoint host:port) — fastest, no Tor
  TorTransport    (ccss_contact_onion  .onion)   — anonymous fallback
  D2dTransport    (agent_id)                      — future ILC peer routing

Graph model:
  - Self (operator) node on the left.
  - Contact (agent) nodes fanned to the right.
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
_DEFAULT_CONTACTS = (
    Path(__file__).resolve().parent.parent.parent
    / "docs" / "contact" / "ccss_contacts.json"
)
_DEFAULT_INBOX = Path.home() / ".ccss_inbox" / "genesis"
_DEFAULT_SENT  = Path.home() / ".ccss_inbox" / "sent"
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
            "/":             self._serve_html,
            "/api/status":   self._api_status,
            "/api/contacts": self._api_contacts,
            "/api/inbox":    self._api_inbox,
            "/api/sent":     self._api_sent,
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
        if not contact_id or not message:
            self._json({"ok": False, "error": "missing fields"}, 400)
            return
        if len(message.encode()) > _MAX_MESSAGE_BYTES:
            self._json({"ok": False, "error": "message too long"}, 400)
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
        # Resolve transport (direct peer → tor → d2d stub)
        try:
            resolve = _load_transport()
            transport, endpoint = resolve(contact)
        except ValueError as exc:
            self._json({"ok": False, "error": str(exc)}, 400)
            return
        try:
            envelope = _seal(message, pubkey)
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

/* ── canvas ── */
#canvas{position:absolute;inset:0 0 28px 0;overflow:hidden}
#graph-svg{width:100%;height:100%;display:block}

/* ── agent nodes (HTML divs positioned over SVG) ── */
.node{position:absolute;transform:translate(-50%,-50%);pointer-events:all;cursor:default}

.agent-ring{
  border-radius:50%;display:flex;align-items:center;justify-content:center;
  position:relative;transition:box-shadow 0.25s,transform 0.2s,border-color 0.25s;
}

/* Self / operator node */
.node-self .agent-ring{
  width:68px;height:68px;
  background:radial-gradient(circle at 35% 35%,#2a1800,#0e0800);
  border:2px solid #b87c08;
  box-shadow:0 0 24px 8px rgba(184,124,8,0.3),inset 0 1px 0 rgba(255,200,60,0.15);
  animation:self-pulse 3s ease-in-out infinite;
}
@keyframes self-pulse{
  0%,100%{box-shadow:0 0 24px 8px rgba(184,124,8,0.3),inset 0 1px 0 rgba(255,200,60,0.15)}
  50%{box-shadow:0 0 38px 14px rgba(184,124,8,0.45),inset 0 1px 0 rgba(255,200,60,0.2)}
}
.node-self .agent-avatar{font-size:1.4rem;font-weight:700;color:#e8b840;letter-spacing:-1px}
.node-self .node-label{color:#906010;font-size:0.6rem}

/* Contact node */
.node-contact .agent-ring{
  width:54px;height:54px;cursor:pointer;
  background:radial-gradient(circle at 35% 35%,#0c1e30,#060e18);
  border:2px solid #183a56;
  box-shadow:0 0 14px 4px rgba(24,58,86,0.3);
}
.node-contact.configured .agent-ring{
  border-color:#1472a0;
  box-shadow:0 0 18px 6px rgba(20,114,160,0.3);
}
.node-contact.active .agent-ring,
.node-contact:hover .agent-ring{
  border-color:#40a8d8;
  box-shadow:0 0 28px 10px rgba(64,168,216,0.4);
  transform:scale(1.08);
}
.node-contact .agent-avatar{font-size:1.15rem;font-weight:700;color:#a0c8e0}
.node-contact.configured .agent-avatar{color:#c0e0f8}

/* status dot */
.status-dot{
  position:absolute;bottom:2px;right:2px;
  width:10px;height:10px;border-radius:50%;border:2px solid #07090f;
}
.status-dot.ok{background:#28d87a}
.status-dot.off{background:#304050}

/* inbox badge on self */
#inbox-badge{
  position:absolute;top:-3px;right:-3px;
  min-width:18px;height:18px;padding:0 4px;
  background:#c83030;border-radius:9px;border:2px solid #07090f;
  font-size:0.6rem;font-weight:700;color:#fff;
  display:none;align-items:center;justify-content:center;
}

/* shared label */
.node-label{
  position:absolute;top:calc(100% + 7px);left:50%;transform:translateX(-50%);
  white-space:nowrap;font-size:0.6rem;color:#3a6070;letter-spacing:0.04em;
  pointer-events:none;
}

/* ── conversation nodes ── */
.conv-node{
  position:absolute;transform:translate(-50%,-50%);cursor:pointer;
  transition:transform 0.2s;
}
.conv-node:hover{transform:translate(-50%,-50%) scale(1.15)}
.conv-node.active{transform:translate(-50%,-50%) scale(1.15)}

.conv-ring{
  width:36px;height:36px;border-radius:8px;
  display:flex;align-items:center;justify-content:center;
  background:radial-gradient(circle at 35% 35%,#140a28,#080414);
  border:1.5px solid #3a1870;
  box-shadow:0 0 12px 3px rgba(58,24,112,0.3);
  transition:box-shadow 0.25s,border-color 0.25s;
  position:relative;
}
.conv-node.active .conv-ring,
.conv-node:hover .conv-ring{
  border-color:#8858e0;
  box-shadow:0 0 22px 8px rgba(136,88,224,0.5);
}
.conv-node.configured .conv-ring{
  border-color:#5030b0;
  box-shadow:0 0 14px 4px rgba(80,48,176,0.35);
}

.conv-icon{font-size:0.8rem;opacity:0.7;user-select:none}
.conv-node.active .conv-icon,
.conv-node:hover .conv-icon{opacity:1}

.conv-count{
  position:absolute;top:-5px;right:-5px;
  min-width:16px;height:16px;padding:0 3px;
  background:#5030b0;border-radius:8px;border:1.5px solid #07090f;
  font-size:0.55rem;font-weight:700;color:#d0b8ff;
  display:none;align-items:center;justify-content:center;
}
.conv-node.has-msgs .conv-count{display:flex}

.conv-label{
  position:absolute;top:calc(100% + 6px);left:50%;transform:translateX(-50%);
  white-space:nowrap;font-size:0.55rem;color:#2a1858;letter-spacing:0.04em;
  pointer-events:none;
}
.conv-node.active .conv-label,
.conv-node:hover .conv-label{color:#6040a0}

/* ── compose panel ── */
#panel{
  position:fixed;top:0;right:0;bottom:28px;width:340px;
  background:#080e18;border-left:1px solid #101c2c;
  display:flex;flex-direction:column;z-index:10;
  transform:translateX(100%);transition:transform 0.32s cubic-bezier(0.25,0.8,0.25,1);
}
#panel.open{transform:translateX(0)}

#panel-header{
  padding:18px 18px 14px;border-bottom:1px solid #101c2c;
  display:flex;align-items:flex-start;gap:10px;flex-shrink:0;
}
#panel-av{
  width:38px;height:38px;border-radius:8px;flex-shrink:0;
  background:radial-gradient(circle,#140a28,#07090f);
  border:1.5px solid #5030b0;
  display:flex;align-items:center;justify-content:center;
  font-size:1rem;font-weight:700;color:#c0a8f8;
}
#panel-meta{flex:1;min-width:0}
#panel-name{font-size:0.88rem;color:#c0d4e4;font-weight:600;margin-bottom:2px}
#panel-agent{font-size:0.58rem;color:#2a4a6a;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
#panel-onion{font-size:0.56rem;color:#1e3a52;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;margin-top:1px}
#panel-close{background:none;border:none;color:#2a4a6a;font-size:1.1rem;cursor:pointer;flex-shrink:0;padding:2px}
#panel-close:hover{color:#c0d4e4}

#thread{
  flex:1;overflow-y:auto;padding:14px;
  display:flex;flex-direction:column;gap:10px;
}
#thread::-webkit-scrollbar{width:3px}
#thread::-webkit-scrollbar-thumb{background:#101c2c;border-radius:2px}

.bubble{
  align-self:flex-end;max-width:90%;
  background:#0e2438;border:1px solid #162e48;
  border-radius:10px 10px 2px 10px;padding:8px 11px;
}
.bubble-text{font-size:0.76rem;color:#c8e0f8;line-height:1.5;word-break:break-word}
.bubble-meta{margin-top:4px;font-size:0.56rem;color:#2a4a6a;text-align:right}
.bubble-receipt{font-size:0.52rem;color:#1e3a52;text-align:right;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.thread-empty{font-size:0.7rem;color:#1e3050;text-align:center;padding:24px 0;font-style:italic}

#compose{padding:12px;border-top:1px solid #101c2c;flex-shrink:0}
#compose-ta{
  width:100%;min-height:68px;max-height:130px;
  background:#04080e;border:1px solid #182a3e;border-radius:7px;
  color:#c0d4e4;font-family:inherit;font-size:0.76rem;
  padding:9px;resize:vertical;outline:none;line-height:1.5;
}
#compose-ta:focus{border-color:#1e5070}
#compose-foot{display:flex;align-items:center;justify-content:space-between;margin-top:7px}
#byte-ctr{font-size:0.6rem;color:#2a4a6a}
#byte-ctr.warn{color:#c07830}
#byte-ctr.over{color:#c03030}
#send-btn{
  background:#0e2e48;border:1px solid #1a5070;border-radius:6px;
  color:#60b8e0;font-size:0.72rem;font-family:inherit;
  padding:5px 14px;cursor:pointer;transition:background 0.2s;
}
#send-btn:hover:not(:disabled){background:#163a5a;color:#90d0f0}
#send-btn:disabled{opacity:0.3;cursor:not-allowed}
#send-status{font-size:0.6rem;margin-top:5px;min-height:13px;color:#28a060}

/* ── status bar ── */
#sb{
  position:fixed;bottom:0;left:0;right:0;height:28px;
  background:#04060c;border-top:1px solid #0c1420;
  display:flex;align-items:center;padding:0 14px;gap:14px;
  font-size:0.58rem;color:#1e3050;z-index:15;
}
.sb-dot{width:6px;height:6px;border-radius:50%;display:inline-block;margin-right:4px}
.sb-dot.ok{background:#28d87a}
.sb-dot.off{background:#c03030}
#sb-onion{max-width:260px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;color:#1a3858}
#sb-inbox-btn{cursor:pointer;margin-left:auto;color:#1e3050}
#sb-inbox-btn:hover{color:#60a0c8}

/* ── inbox drawer ── */
#inbox-drawer{
  position:fixed;bottom:28px;left:0;width:280px;
  background:#080e18;border-right:1px solid #101c2c;border-top:1px solid #101c2c;
  max-height:50vh;overflow-y:auto;z-index:12;
  transform:translateY(100%);transition:transform 0.28s;
}
#inbox-drawer.open{transform:translateY(0)}
#inbox-drawer::-webkit-scrollbar{width:3px}
#inbox-drawer::-webkit-scrollbar-thumb{background:#101c2c;border-radius:2px}
.idh{padding:9px 12px;font-size:0.65rem;color:#3a6888;border-bottom:1px solid #0c1828;
  display:flex;justify-content:space-between;align-items:center}
.idh button{background:none;border:none;color:#2a4060;cursor:pointer;font-size:0.8rem}
.env-row{padding:9px 12px;border-bottom:1px solid #090e18;font-size:0.6rem}
.env-rct{color:#2a4060;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.env-sz{font-size:0.55rem;margin-top:2px}
</style>
</head>
<body>

<!-- SVG canvas: zone circles + edges -->
<div id="canvas">
<svg id="graph-svg" viewBox="0 0 1000 660" preserveAspectRatio="xMidYMid meet">
<defs>
  <radialGradient id="zSelf" cx="50%" cy="50%" r="50%">
    <stop offset="0%" stop-color="#082840" stop-opacity="1"/>
    <stop offset="100%" stop-color="#082840" stop-opacity="0"/>
  </radialGradient>
  <radialGradient id="zConv" cx="50%" cy="50%" r="50%">
    <stop offset="0%" stop-color="#1a0840" stop-opacity="1"/>
    <stop offset="100%" stop-color="#1a0840" stop-opacity="0"/>
  </radialGradient>
  <radialGradient id="zContact" cx="50%" cy="50%" r="50%">
    <stop offset="0%" stop-color="#041830" stop-opacity="1"/>
    <stop offset="100%" stop-color="#041830" stop-opacity="0"/>
  </radialGradient>
  <filter id="zblur"><feGaussianBlur stdDeviation="40"/></filter>
</defs>

<!-- background zone ellipses -->
<ellipse cx="240" cy="330" rx="240" ry="250" fill="url(#zSelf)"
         filter="url(#zblur)" opacity="0.55"/>
<ellipse cx="500" cy="330" rx="200" ry="230" fill="url(#zConv)"
         filter="url(#zblur)" opacity="0.5"/>
<ellipse cx="740" cy="330" rx="230" ry="250" fill="url(#zContact)"
         filter="url(#zblur)" opacity="0.5"/>

<!-- zone outlines -->
<ellipse cx="240" cy="330" rx="230" ry="242" fill="none"
         stroke="#082840" stroke-width="0.7" stroke-dasharray="5 10" opacity="0.3"/>
<ellipse cx="500" cy="330" rx="192" ry="222" fill="none"
         stroke="#1a0840" stroke-width="0.7" stroke-dasharray="5 10" opacity="0.25"/>
<ellipse cx="740" cy="330" rx="222" ry="242" fill="none"
         stroke="#041830" stroke-width="0.7" stroke-dasharray="5 10" opacity="0.25"/>

<!-- zone labels -->
<text x="90"  y="105" font-family="monospace" font-size="8" fill="#082840"
      opacity="0.6" letter-spacing="2.5">OPERATOR</text>
<text x="440" y="108" font-family="monospace" font-size="8" fill="#1a0840"
      opacity="0.55" letter-spacing="2.5">CONVERSATION</text>
<text x="635" y="105" font-family="monospace" font-size="8" fill="#082840"
      opacity="0.5" letter-spacing="2.5">CONTACT AGENTS</text>

<!-- edges + conv nodes drawn by JS -->
<g id="edges"></g>
</svg>
</div>

<!-- node container (HTML positioned over SVG) -->
<div id="nodes"></div>

<!-- compose panel -->
<div id="panel">
  <div id="panel-header">
    <div id="panel-av">?</div>
    <div id="panel-meta">
      <div id="panel-name">—</div>
      <div id="panel-agent"></div>
      <div id="panel-onion"></div>
    </div>
    <button id="panel-close" onclick="closePanel()">✕</button>
  </div>
  <div id="thread"></div>
  <div id="compose">
    <textarea id="compose-ta" placeholder="Message (max 2000 bytes)…"
              oninput="onType()" rows="3"></textarea>
    <div id="compose-foot">
      <span id="byte-ctr">0 / 2000</span>
      <button id="send-btn" onclick="doSend()" disabled>Send →</button>
    </div>
    <div id="send-status"></div>
  </div>
</div>

<!-- inbox drawer -->
<div id="inbox-drawer">
  <div class="idh">
    <span>Sealed Envelopes</span>
    <button onclick="toggleInbox()">✕</button>
  </div>
  <div id="inbox-list"></div>
</div>

<!-- status bar -->
<div id="sb">
  <span><span class="sb-dot off" id="sb-tor"></span><span id="sb-tor-lbl">Tor</span></span>
  <span id="sb-onion"></span>
  <span id="sb-inbox-btn" onclick="toggleInbox()">
    ▲ Inbox (<span id="sb-inbox-n">0</span>)
  </span>
</div>

<script>
// ── layout constants (in SVG viewBox 1000 × 660) ─────────────────────────
const SELF_X = 240, SELF_Y = 330;
const CONTACT_X = 740;           // contacts' x column
const V_GAP = 110;               // vertical spacing between contacts

let contacts = [];
let active = null;   // contact id currently selected
let inboxOpen = false;

// ── boot ──────────────────────────────────────────────────────────────────
async function boot() {
  await loadContacts();
  pollStatus();
  setInterval(pollStatus, 5000);
}

// ── contacts & render ─────────────────────────────────────────────────────
async function loadContacts() {
  const r = await fetch('/api/contacts');
  contacts = await r.json();
  render();
}

function contactPos(i, n) {
  const totalH = (n - 1) * V_GAP;
  const startY  = SELF_Y - totalH / 2;
  return { x: CONTACT_X, y: startY + i * V_GAP };
}

function convPos(cx, cy) {
  return { x: (SELF_X + cx) / 2, y: (SELF_Y + cy) / 2 };
}

function render() {
  document.getElementById('edges').innerHTML = '';
  document.getElementById('nodes').innerHTML  = '';

  // self node
  placeNode(makeAgentNode('self', 'Y', 'You', true, false, null),
            SELF_X, SELF_Y, 1000, 660);

  const n = contacts.length;
  contacts.forEach((c, i) => {
    const cp  = contactPos(i, n);
    const mp  = convPos(cp.x, cp.y);

    // edge
    const line = svgEl('line', {
      id: 'edge-' + c.id,
      class: 'edge',
      x1: SELF_X, y1: SELF_Y, x2: cp.x, y2: cp.y,
    });
    // default edge style inline
    line.style.stroke = '#182838';
    line.style.strokeWidth = '1.2';
    line.style.strokeDasharray = '5 6';
    line.style.fill = 'none';
    line.style.opacity = '0.4';
    line.style.transition = 'stroke 0.3s,opacity 0.3s';
    document.getElementById('edges').appendChild(line);

    // contact agent node
    const el = makeAgentNode(c.id, (c.name||'?')[0].toUpperCase(),
                              c.name, c.configured, true, c);
    placeNode(el, cp.x, cp.y, 1000, 660);

    // conversation node
    const cv = makeConvNode(c.id, c.configured);
    placeConvNode(cv, mp.x, mp.y, 1000, 660);
  });
}

function makeAgentNode(id, letter, label, configured, isContact, contact) {
  const wrap = div('node ' + (isContact ? 'node-contact' : 'node-self')
                   + (configured ? ' configured' : ''));
  wrap.id = 'node-' + id;

  const ring = div('agent-ring');
  const av   = div('agent-avatar');
  av.textContent = letter;
  ring.appendChild(av);

  if (isContact) {
    const dot = div('status-dot ' + (configured ? 'ok' : 'off'));
    ring.appendChild(dot);
    wrap.onclick = () => selectContact(id);
  } else {
    // inbox badge on self
    const badge = div('');
    badge.id = 'inbox-badge';
    badge.style.cssText = 'position:absolute;top:-3px;right:-3px;min-width:18px;height:18px;padding:0 4px;background:#c83030;border-radius:9px;border:2px solid #07090f;font-size:0.6rem;font-weight:700;color:#fff;display:none;align-items:center;justify-content:center';
    ring.appendChild(badge);
  }

  wrap.appendChild(ring);
  const lbl = div('node-label');
  lbl.textContent = label;
  wrap.appendChild(lbl);
  return wrap;
}

function makeConvNode(contactId, configured) {
  const wrap = div('conv-node' + (configured ? ' configured' : ''));
  wrap.id = 'conv-' + contactId;
  const ring = div('conv-ring');
  const icon = div('conv-icon');
  icon.textContent = '◈';
  ring.appendChild(icon);
  const cnt = div('conv-count');
  cnt.id = 'conv-cnt-' + contactId;
  ring.appendChild(cnt);
  wrap.appendChild(ring);
  const lbl = div('conv-label');
  lbl.textContent = 'conversation';
  wrap.appendChild(lbl);
  wrap.onclick = () => selectContact(contactId);
  return wrap;
}

function placeNode(el, svgX, svgY, vbW, vbH) {
  el.style.left = pct(svgX, vbW);
  el.style.top  = pct(svgY, vbH);
  document.getElementById('nodes').appendChild(el);
}

function placeConvNode(el, svgX, svgY, vbW, vbH) {
  el.style.left = pct(svgX, vbW);
  el.style.top  = pct(svgY, vbH);
  document.getElementById('nodes').appendChild(el);
}

// ── selection ─────────────────────────────────────────────────────────────
async function selectContact(id) {
  // clear previous
  if (active) {
    document.getElementById('node-' + active)?.classList.remove('active');
    document.getElementById('conv-' + active)?.classList.remove('active');
    const edge = document.getElementById('edge-' + active);
    if (edge) { edge.style.stroke = '#182838'; edge.style.opacity = '0.4'; }
  }
  active = id;

  // highlight
  document.getElementById('node-' + id)?.classList.add('active');
  document.getElementById('conv-' + id)?.classList.add('active');
  const edge = document.getElementById('edge-' + id);
  if (edge) { edge.style.stroke = '#8858e0'; edge.style.opacity = '0.7'; }

  const c = contacts.find(x => x.id === id);
  if (!c) return;

  // panel header
  document.getElementById('panel-av').textContent = (c.name||'?')[0].toUpperCase();
  document.getElementById('panel-name').textContent = c.name || id;
  document.getElementById('panel-agent').textContent = c.agent_id || '(agent_id not configured)';
  document.getElementById('panel-onion').textContent = c.onion || '(onion not configured)';
  document.getElementById('sb-onion').textContent =
    c.onion ? c.onion.slice(0,44) + '…' : '';

  document.getElementById('compose-ta').value = '';
  document.getElementById('send-status').textContent = '';
  onType();

  const btn = document.getElementById('send-btn');
  btn.disabled = !c.configured;
  if (!c.configured) {
    document.getElementById('send-status').style.color = '#806020';
    document.getElementById('send-status').textContent = 'Contact not configured (placeholders)';
  } else {
    document.getElementById('send-status').style.color = '#28a060';
    document.getElementById('send-status').textContent = '';
  }

  await loadSent(id);
  document.getElementById('panel').classList.add('open');
}

function closePanel() {
  document.getElementById('panel').classList.remove('open');
  if (active) {
    document.getElementById('node-' + active)?.classList.remove('active');
    document.getElementById('conv-' + active)?.classList.remove('active');
    const edge = document.getElementById('edge-' + active);
    if (edge) { edge.style.stroke = '#182838'; edge.style.opacity = '0.4'; }
  }
  active = null;
  document.getElementById('sb-onion').textContent = '';
}

// ── thread ────────────────────────────────────────────────────────────────
async function loadSent(id) {
  const r    = await fetch('/api/sent?id=' + encodeURIComponent(id));
  const msgs = await r.json();
  const th   = document.getElementById('thread');
  // update conv count badge
  const badge = document.getElementById('conv-cnt-' + id);
  const node  = document.getElementById('conv-' + id);
  if (badge) {
    badge.textContent = msgs.length || '';
    node?.classList.toggle('has-msgs', msgs.length > 0);
  }
  if (!msgs.length) {
    th.innerHTML = '<div class="thread-empty">No messages sent yet<br>Type below and send →</div>';
    return;
  }
  th.innerHTML = msgs.map(m => {
    const dt = new Date(m.ts * 1000).toLocaleString();
    const body = m.plaintext_stored
      ? esc(m.message || '')
      : '<span style="color:#486070">Plaintext not retained locally; '
        + esc(String(m.message_bytes || 0)) + ' bytes, sha256 '
        + esc(String(m.message_sha256 || '').slice(0,16)) + '…</span>';
    return `<div class="bubble">
      <div class="bubble-text">${body}</div>
      <div class="bubble-meta">${esc(dt)}</div>
      <div class="bubble-receipt">${esc(m.receipt||'').slice(0,32)}…</div>
    </div>`;
  }).join('');
  th.scrollTop = th.scrollHeight;
}

// ── compose ───────────────────────────────────────────────────────────────
function onType() {
  const ta    = document.getElementById('compose-ta');
  const bytes = new TextEncoder().encode(ta.value).length;
  const ctr   = document.getElementById('byte-ctr');
  ctr.textContent = bytes + ' / 2000';
  ctr.className = bytes > 2000 ? 'over' : bytes > 1800 ? 'warn' : '';
  const c = contacts.find(x => x.id === active);
  document.getElementById('send-btn').disabled =
    !ta.value.trim() || bytes > 2000 || !c?.configured;
}

async function doSend() {
  const ta  = document.getElementById('compose-ta');
  const msg = ta.value.trim();
  if (!msg || !active) return;
  const btn = document.getElementById('send-btn');
  const st  = document.getElementById('send-status');
  btn.disabled = true;
  st.style.color = '#4090b0';
  st.textContent = 'Sealing envelope and routing via Tor…';

  try {
    const r    = await fetch('/api/send', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({contact_id: active, message: msg}),
    });
    const data = await r.json();
    if (data.ok) {
      st.style.color = '#28d87a';
      st.textContent = '✓ Delivered — ' + (data.receipt||'').slice(0,18) + '…';
      ta.value = '';
      onType();
      // flash edge green
      const edge = document.getElementById('edge-' + active);
      if (edge) {
        const prev = edge.style.stroke;
        edge.style.stroke = '#28d87a';
        setTimeout(() => { edge.style.stroke = prev; }, 1400);
      }
      await loadSent(active);
    } else {
      st.style.color = '#c04030';
      st.textContent = 'Error: ' + (data.error||'unknown');
      btn.disabled = false;
    }
  } catch (e) {
    st.style.color = '#c04030';
    st.textContent = 'Network: ' + e.message;
    btn.disabled = false;
  }
}

// ── inbox ─────────────────────────────────────────────────────────────────
function toggleInbox() {
  inboxOpen = !inboxOpen;
  document.getElementById('inbox-drawer').classList.toggle('open', inboxOpen);
  if (inboxOpen) loadInbox();
}

async function loadInbox() {
  const r    = await fetch('/api/inbox');
  const envs = await r.json();
  const list = document.getElementById('inbox-list');
  if (!envs.length) {
    list.innerHTML = '<div style="padding:10px 12px;font-size:0.6rem;color:#1e3050">No envelopes</div>';
    return;
  }
  list.innerHTML = envs.map(e => {
    const dt  = new Date(e.received * 1000).toLocaleString();
    const col = e.size_ok ? '#1a6040' : '#806020';
    const sz  = e.size_ok ? '✓ 4156 B' : '⚠ ' + e.size + ' B';
    return `<div class="env-row">
      <div class="env-rct">${esc(e.receipt)}</div>
      <div class="env-sz" style="color:${col}">${sz} · ${esc(dt)}</div>
    </div>`;
  }).join('');
}

// ── status ────────────────────────────────────────────────────────────────
async function pollStatus() {
  try {
    const d = await (await fetch('/api/status')).json();
    const dot = document.getElementById('sb-tor');
    dot.className = 'sb-dot ' + (d.tor ? 'ok' : 'off');
    document.getElementById('sb-tor-lbl').textContent =
      d.tor ? 'Tor connected' : 'Tor offline';
    const n = d.inbox_count || 0;
    document.getElementById('sb-inbox-n').textContent = n;
    const badge = document.getElementById('inbox-badge');
    if (badge) { badge.style.display = n ? 'flex' : 'none'; badge.textContent = n; }
  } catch (_) {}
}

// ── helpers ───────────────────────────────────────────────────────────────
function div(cls) {
  const el = document.createElement('div');
  if (cls) el.className = cls;
  return el;
}
function svgEl(tag, attrs) {
  const el = document.createElementNS('http://www.w3.org/2000/svg', tag);
  for (const [k, v] of Object.entries(attrs)) el.setAttribute(k, v);
  return el;
}
function pct(v, total) { return (v / total * 100).toFixed(3) + '%'; }
function esc(s) {
  return String(s)
    .replace(/&/g,'&amp;').replace(/</g,'&lt;')
    .replace(/>/g,'&gt;').replace(/"/g,'&quot;');
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
