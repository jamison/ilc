#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
"""CCSS Epistemic Graph UI — graph-native operator dashboard.

Agents appear as nodes in an epistemic graph.  Genesis (self) sits at the
intersection of three overlapping protocol zones.  Contact nodes orbit the
center.  Click a node to compose a message; inbox envelopes appear as count
badges on the Genesis node.

Served on 127.0.0.1:8422.  Loopback only.

Usage:
    python tools/ccss_send/ccss_chat_ui.py [--contacts <path>] [--inbox <dir>]
                                            [--sent <dir>] [--port <port>]
Defaults:
    --contacts  docs/contact/ccss_contacts.json
    --inbox     ~/.ccss_inbox/genesis
    --sent      ~/.ccss_inbox/sent
    --port      8422
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
_TOR_HOST = "127.0.0.1"
_TOR_PORT = 9050
_OUTER_ENVELOPE_BYTES = 4156
_MAX_MESSAGE_BYTES = 2000

# ---------------------------------------------------------------------------
# Minimal SOCKS5 + HTTP-over-Tor
# ---------------------------------------------------------------------------

def _socks5_send(onion: str, path: str, body: bytes) -> dict[str, Any]:
    """Send body via SOCKS5 → Tor to onion:80/path.  Returns parsed JSON."""
    host_b = onion.encode()
    with socket.create_connection((_TOR_HOST, _TOR_PORT), timeout=30) as s:
        s.sendall(b"\x05\x01\x00")
        if s.recv(2) != b"\x05\x00":
            raise RuntimeError("SOCKS5 auth negotiation failed")
        s.sendall(b"\x05\x01\x00\x03" + bytes([len(host_b)]) + host_b + b"\x00\x50")
        resp = s.recv(10)
        if resp[1] != 0x00:
            raise RuntimeError(f"SOCKS5 CONNECT failed: code {resp[1]}")
        req = (
            f"POST {path} HTTP/1.0\r\n"
            f"Host: {onion}\r\n"
            f"Content-Type: application/octet-stream\r\n"
            f"Content-Length: {len(body)}\r\n"
            f"\r\n"
        ).encode() + body
        s.sendall(req)
        raw = b""
        while True:
            chunk = s.recv(4096)
            if not chunk:
                break
            raw += chunk
    header, _, resp_body = raw.partition(b"\r\n\r\n")
    status_line = header.split(b"\r\n")[0]
    code = int(status_line.split(b" ")[1])
    if code not in (200, 202):
        raise RuntimeError(f"Relay returned HTTP {code}")
    return json.loads(resp_body)


# ---------------------------------------------------------------------------
# Envelope encryption import
# ---------------------------------------------------------------------------

def _seal(message: str, pubkey_hex: str) -> bytes:
    try:
        from tools.ccss_send.ccss_encrypt import seal_message
    except ImportError:
        _root = Path(__file__).resolve().parent.parent.parent
        sys.path.insert(0, str(_root))
        from tools.ccss_send.ccss_encrypt import seal_message  # type: ignore
    return seal_message(message, pubkey_hex)


# ---------------------------------------------------------------------------
# Request handler
# ---------------------------------------------------------------------------

class _Handler(http.server.BaseHTTPRequestHandler):
    contacts_path: Path
    inbox_dir:     Path
    sent_dir:      Path

    def log_message(self, fmt: str, *args: Any) -> None:  # suppress access log
        pass

    # ── routing ──────────────────────────────────────────────────────────────

    def do_GET(self) -> None:
        p = self.path.split("?")[0]
        if p == "/":
            self._serve_html()
        elif p == "/api/status":
            self._api_status()
        elif p == "/api/contacts":
            self._api_contacts()
        elif p == "/api/inbox":
            self._api_inbox()
        elif p == "/api/sent":
            self._api_sent()
        else:
            self.send_error(404)

    def do_POST(self) -> None:
        if self.path == "/api/send":
            self._api_send()
        else:
            self.send_error(404)

    # ── HTML page ─────────────────────────────────────────────────────────────

    def _serve_html(self) -> None:
        body = _HTML.encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    # ── /api/status ───────────────────────────────────────────────────────────

    def _api_status(self) -> None:
        tor_ok = self._tor_live()
        inbox_count = self._count_inbox()
        self._json({"tor": tor_ok, "inbox_count": inbox_count})

    @staticmethod
    def _tor_live() -> bool:
        try:
            with socket.create_connection((_TOR_HOST, _TOR_PORT), timeout=2):
                return True
        except OSError:
            return False

    def _count_inbox(self) -> int:
        d = self.inbox_dir
        if not d.is_dir():
            return 0
        return len([f for f in d.iterdir() if f.suffix == ".envelope"])

    # ── /api/contacts ─────────────────────────────────────────────────────────

    def _api_contacts(self) -> None:
        try:
            raw = json.loads(self.contacts_path.read_text())
        except Exception:
            raw = []
        # Strip pubkey — never sent to JS
        safe = []
        for c in raw:
            ph = c.get("ccss_recipient_pubkey", "")
            onion = c.get("ccss_contact_onion", "")
            configured = (
                ph and "PLACEHOLDER" not in ph.upper()
                and onion and "PLACEHOLDER" not in onion.upper()
            )
            safe.append({
                "id":          c.get("id", ""),
                "name":        c.get("name", ""),
                "description": c.get("description", ""),
                "agent_id":    c.get("agent_id", ""),
                "onion":       onion if configured else "",
                "configured":  configured,
            })
        self._json(safe)

    # ── /api/inbox ────────────────────────────────────────────────────────────

    def _api_inbox(self) -> None:
        d = self.inbox_dir
        envelopes = []
        if d.is_dir():
            for f in sorted(d.iterdir()):
                if f.suffix != ".envelope":
                    continue
                size = f.stat().st_size
                envelopes.append({
                    "receipt":   f.stem,
                    "size":      size,
                    "size_ok":   size == _OUTER_ENVELOPE_BYTES,
                    "received":  int(f.stat().st_mtime),
                })
        self._json(sorted(envelopes, key=lambda e: e["received"], reverse=True)[:50])

    # ── /api/sent ─────────────────────────────────────────────────────────────

    def _api_sent(self) -> None:
        from urllib.parse import parse_qs, urlparse
        qs = parse_qs(urlparse(self.path).query)
        contact_id = (qs.get("id") or [""])[0]
        d = self.sent_dir / contact_id
        msgs = []
        if d.is_dir():
            for f in sorted(d.iterdir()):
                if f.suffix != ".json":
                    continue
                try:
                    msgs.append(json.loads(f.read_text()))
                except Exception:
                    pass
        msgs.sort(key=lambda m: m.get("ts", 0))
        self._json(msgs[-50:])

    # ── /api/send ─────────────────────────────────────────────────────────────

    def _api_send(self) -> None:
        length = int(self.headers.get("Content-Length", 0))
        if length > 8192:
            self.send_error(400, "payload too large")
            return
        payload = json.loads(self.rfile.read(length))
        contact_id = payload.get("contact_id", "")
        message    = payload.get("message", "")
        if not contact_id or not message:
            self._json({"ok": False, "error": "missing fields"}, 400)
            return
        if len(message.encode()) > _MAX_MESSAGE_BYTES:
            self._json({"ok": False, "error": "message too long"}, 400)
            return

        # Look up contact from disk (pubkey never travels to JS)
        try:
            contacts = json.loads(self.contacts_path.read_text())
        except Exception:
            self._json({"ok": False, "error": "contacts unavailable"}, 500)
            return
        contact = next((c for c in contacts if c.get("id") == contact_id), None)
        if contact is None:
            self._json({"ok": False, "error": "contact not found"}, 404)
            return
        pubkey = contact.get("ccss_recipient_pubkey", "")
        onion  = contact.get("ccss_contact_onion", "")
        if not pubkey or "PLACEHOLDER" in pubkey.upper():
            self._json({"ok": False, "error": "contact not configured: pubkey placeholder"}, 400)
            return
        if not onion or "PLACEHOLDER" in onion.upper():
            self._json({"ok": False, "error": "contact not configured: onion placeholder"}, 400)
            return

        try:
            envelope = _seal(message, pubkey)
        except Exception as exc:
            self._json({"ok": False, "error": f"encrypt error: {exc}"}, 500)
            return

        try:
            result = _socks5_send(onion, "/submit", envelope)
        except Exception as exc:
            self._json({"ok": False, "error": f"send error: {exc}"}, 502)
            return

        receipt = result.get("receipt_token", hashlib.sha256(envelope).hexdigest())
        ts = int(time.time())
        record = {
            "ts":          ts,
            "contact_id":  contact_id,
            "message":     message,
            "receipt":     receipt,
        }
        sent_dir = self.sent_dir / contact_id
        sent_dir.mkdir(parents=True, exist_ok=True)
        out_path = sent_dir / f"{ts}_{receipt[:8]}.json"
        import tempfile
        tmp_fd, tmp_path = tempfile.mkstemp(dir=sent_dir)
        try:
            with os.fdopen(tmp_fd, "w") as fh:
                json.dump(record, fh)
            os.replace(tmp_path, out_path)
        except Exception:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass

        self._json({"ok": True, "receipt": receipt})

    # ── helpers ───────────────────────────────────────────────────────────────

    def _json(self, data: Any, code: int = 200) -> None:
        body = json.dumps(data, sort_keys=True).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


# ---------------------------------------------------------------------------
# HTML / CSS / JS
# ---------------------------------------------------------------------------

_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>CCSS — Epistemic Graph</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
html,body{width:100%;height:100%;background:#080c12;overflow:hidden;font-family:'SF Mono',ui-monospace,monospace;color:#c8d8e8}

/* ── graph canvas ── */
#canvas{position:absolute;inset:0;overflow:hidden}
#graph-svg{width:100%;height:100%}

/* zone circles */
.zone{opacity:0.13;filter:blur(48px)}

/* edges */
.edge{stroke:#2a5a7a;stroke-width:1.5;stroke-dasharray:6 5;fill:none;opacity:0.5;transition:opacity 0.3s,stroke 0.3s}
.edge.active{stroke:#4ea8d2;stroke-dasharray:6 5;opacity:0.9}

/* ── nodes ── */
.node{position:absolute;transform:translate(-50%,-50%);cursor:pointer;user-select:none}
.node-ring{border-radius:50%;display:flex;align-items:center;justify-content:center;position:relative;transition:box-shadow 0.3s,transform 0.2s}
.node:hover .node-ring{transform:scale(1.1)}
.node.selected .node-ring{transform:scale(1.12)}

/* Genesis (self) */
.node-genesis .node-ring{
  width:72px;height:72px;
  background:radial-gradient(circle,#3a2a00,#1a1000);
  border:2px solid #c8910a;
  box-shadow:0 0 28px 8px rgba(200,145,10,0.35),0 0 0 1px rgba(200,145,10,0.2);
}
.node-genesis .node-ring.pulse{animation:genesis-pulse 2.8s ease-in-out infinite}
@keyframes genesis-pulse{
  0%,100%{box-shadow:0 0 28px 8px rgba(200,145,10,0.35),0 0 0 1px rgba(200,145,10,0.2)}
  50%{box-shadow:0 0 44px 14px rgba(200,145,10,0.5),0 0 0 2px rgba(200,145,10,0.3)}
}

/* Contact nodes */
.node-contact .node-ring{
  width:54px;height:54px;
  background:radial-gradient(circle,#0d1e2e,#060e18);
  border:2px solid #1e4a68;
  box-shadow:0 0 16px 4px rgba(30,74,104,0.3);
  transition:box-shadow 0.3s,border-color 0.3s,transform 0.2s;
}
.node-contact.configured .node-ring{
  border-color:#1a7a9a;
  box-shadow:0 0 20px 6px rgba(26,122,154,0.35);
}
.node-contact.selected .node-ring,
.node-contact:hover .node-ring{
  border-color:#4ea8d2;
  box-shadow:0 0 28px 10px rgba(78,168,210,0.45);
}

.node-avatar{font-size:1.35rem;font-weight:700;color:#c8d8e8;letter-spacing:0}
.node-genesis .node-avatar{font-size:1.55rem;color:#e8c060}

.node-label{position:absolute;top:calc(100% + 8px);left:50%;transform:translateX(-50%);
  white-space:nowrap;font-size:0.65rem;color:#7090a8;letter-spacing:0.05em;pointer-events:none}
.node-genesis .node-label{color:#a08040;font-size:0.68rem}
.node-contact.configured .node-label{color:#5090b0}

/* status dot on contact node */
.node-dot{position:absolute;width:10px;height:10px;border-radius:50%;bottom:2px;right:2px;border:2px solid #080c12}
.node-dot.ok{background:#28c87a}
.node-dot.off{background:#384858}

/* inbox badge on genesis */
#inbox-badge{
  position:absolute;top:-4px;right:-4px;
  min-width:20px;height:20px;padding:0 5px;
  background:#d04040;border-radius:10px;
  font-size:0.62rem;font-weight:700;color:#fff;
  display:none;align-items:center;justify-content:center;
  border:2px solid #080c12;
}

/* ── compose panel ── */
#panel{
  position:fixed;top:0;right:0;width:340px;height:100vh;
  background:#0b1520;border-left:1px solid #162030;
  display:flex;flex-direction:column;
  transform:translateX(100%);transition:transform 0.35s cubic-bezier(0.25,0.8,0.25,1);
  z-index:10;
}
#panel.open{transform:translateX(0)}

#panel-header{
  padding:20px 20px 16px;border-bottom:1px solid #162030;
  display:flex;align-items:flex-start;gap:12px;
}
#panel-avatar{
  width:40px;height:40px;border-radius:50%;
  background:radial-gradient(circle,#0d1e2e,#060e18);
  border:1.5px solid #1a7a9a;
  display:flex;align-items:center;justify-content:center;
  font-size:1.1rem;font-weight:700;color:#c8d8e8;flex-shrink:0;
}
#panel-meta{flex:1;min-width:0}
#panel-name{font-size:0.92rem;color:#c8d8e8;font-weight:600;margin-bottom:3px}
#panel-agent{font-size:0.6rem;color:#3a6888;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;margin-bottom:2px}
#panel-onion{font-size:0.58rem;color:#2a5068;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
#panel-close{background:none;border:none;color:#3a6888;font-size:1.2rem;cursor:pointer;padding:4px;flex-shrink:0;line-height:1}
#panel-close:hover{color:#c8d8e8}

/* sent thread */
#thread{flex:1;overflow-y:auto;padding:16px;display:flex;flex-direction:column;gap:10px}
#thread::-webkit-scrollbar{width:4px}
#thread::-webkit-scrollbar-track{background:transparent}
#thread::-webkit-scrollbar-thumb{background:#162030;border-radius:2px}
.msg-bubble{
  align-self:flex-end;max-width:88%;
  background:#0f2a42;border:1px solid #1a4a6a;border-radius:12px 12px 3px 12px;
  padding:8px 12px;
}
.msg-text{font-size:0.78rem;color:#d0e8f8;line-height:1.5;word-break:break-word}
.msg-meta{margin-top:4px;font-size:0.58rem;color:#3a6888;text-align:right}
.msg-receipt{font-size:0.55rem;color:#2a4a62;margin-top:1px;text-align:right;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.thread-empty{font-size:0.72rem;color:#2a4a62;text-align:center;padding:20px 0;font-style:italic}

/* compose */
#compose{padding:14px;border-top:1px solid #162030}
#compose-area{
  width:100%;min-height:72px;max-height:140px;
  background:#060e18;border:1px solid #1a3a52;border-radius:8px;
  color:#c8d8e8;font-family:inherit;font-size:0.78rem;
  padding:10px;resize:vertical;outline:none;line-height:1.5;
}
#compose-area:focus{border-color:#1a6080}
#compose-footer{display:flex;align-items:center;justify-content:space-between;margin-top:8px}
#byte-counter{font-size:0.62rem;color:#3a6888}
#byte-counter.warn{color:#d08040}
#byte-counter.over{color:#d04040}
#send-btn{
  background:#0f3a5a;border:1px solid #1a6080;border-radius:6px;
  color:#70c0e8;font-size:0.75rem;font-family:inherit;
  padding:6px 16px;cursor:pointer;transition:background 0.2s,color 0.2s;
}
#send-btn:hover:not(:disabled){background:#1a5078;color:#a8d8f8}
#send-btn:disabled{opacity:0.35;cursor:not-allowed}
#send-status{font-size:0.62rem;margin-top:6px;min-height:14px;color:#3a8858}

/* ── status bar ── */
#statusbar{
  position:fixed;bottom:0;left:0;right:0;height:28px;
  background:#060c14;border-top:1px solid #0f1e2c;
  display:flex;align-items:center;padding:0 16px;gap:16px;
  font-size:0.6rem;color:#2a4a62;z-index:5;
}
.sb-dot{width:7px;height:7px;border-radius:50%;display:inline-block;margin-right:5px}
.sb-dot.ok{background:#28c87a}
.sb-dot.off{background:#d04040}
#sb-onion{color:#1a4a62;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;max-width:240px}

/* ── inbox drawer ── */
#inbox-panel{
  position:fixed;bottom:28px;left:0;width:300px;
  background:#0b1520;border-right:1px solid #162030;border-top:1px solid #162030;
  max-height:50vh;overflow-y:auto;
  transform:translateY(100%);transition:transform 0.3s;
  z-index:8;
}
#inbox-panel.open{transform:translateY(0)}
#inbox-panel::-webkit-scrollbar{width:4px}
#inbox-panel::-webkit-scrollbar-thumb{background:#162030;border-radius:2px}
#inbox-header{padding:10px 14px;font-size:0.68rem;color:#5090b0;border-bottom:1px solid #162030;display:flex;justify-content:space-between;align-items:center}
#inbox-header button{background:none;border:none;color:#3a6888;cursor:pointer;font-size:0.8rem}
.env-card{padding:10px 14px;border-bottom:1px solid #0f1e2c;font-size:0.62rem}
.env-receipt{color:#3a6888;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;font-size:0.58rem}
.env-size{font-size:0.58rem;color:#2a5a42;margin-top:2px}
</style>
</head>
<body>

<!-- graph canvas -->
<div id="canvas">
  <svg id="graph-svg" viewBox="0 0 1000 700" preserveAspectRatio="xMidYMid meet">
    <defs>
      <radialGradient id="zone1" cx="50%" cy="50%" r="50%">
        <stop offset="0%" stop-color="#0a4a6a" stop-opacity="1"/>
        <stop offset="100%" stop-color="#0a4a6a" stop-opacity="0"/>
      </radialGradient>
      <radialGradient id="zone2" cx="50%" cy="50%" r="50%">
        <stop offset="0%" stop-color="#3a1a6a" stop-opacity="1"/>
        <stop offset="100%" stop-color="#3a1a6a" stop-opacity="0"/>
      </radialGradient>
      <radialGradient id="zone3" cx="50%" cy="50%" r="50%">
        <stop offset="0%" stop-color="#1a4a2a" stop-opacity="1"/>
        <stop offset="100%" stop-color="#1a4a2a" stop-opacity="0"/>
      </radialGradient>
      <filter id="soft-blur">
        <feGaussianBlur stdDeviation="32"/>
      </filter>
      <marker id="arrowhead" markerWidth="6" markerHeight="6" refX="5" refY="3" orient="auto">
        <path d="M0,0 L0,6 L6,3 z" fill="#2a5a7a" opacity="0.6"/>
      </marker>
    </defs>
    <!-- zone circles -->
    <ellipse class="zone" cx="380" cy="310" rx="260" ry="240" fill="url(#zone1)" filter="url(#soft-blur)"/>
    <ellipse class="zone" cx="620" cy="310" rx="240" ry="230" fill="url(#zone2)" filter="url(#soft-blur)"/>
    <ellipse class="zone" cx="500" cy="470" rx="250" ry="220" fill="url(#zone3)" filter="url(#soft-blur)"/>
    <!-- zone ring outlines -->
    <ellipse cx="380" cy="310" rx="250" ry="232" fill="none" stroke="#0a4a6a" stroke-width="0.8" stroke-dasharray="4 8" opacity="0.25"/>
    <ellipse cx="620" cy="310" rx="232" ry="222" fill="none" stroke="#3a1a6a" stroke-width="0.8" stroke-dasharray="4 8" opacity="0.2"/>
    <ellipse cx="500" cy="470" rx="242" ry="212" fill="none" stroke="#1a4a2a" stroke-width="0.8" stroke-dasharray="4 8" opacity="0.22"/>
    <!-- zone labels -->
    <text x="195" y="155" font-family="monospace" font-size="9" fill="#0a4a6a" opacity="0.6" letter-spacing="2">PROTOCOL LAYER L0</text>
    <text x="700" y="148" font-family="monospace" font-size="9" fill="#3a1a6a" opacity="0.5" letter-spacing="2">EPISTEMIC LAYER L3</text>
    <text x="370" y="665" font-family="monospace" font-size="9" fill="#1a4a2a" opacity="0.5" letter-spacing="2">GENESIS DOMAIN</text>
    <!-- edge group — populated by JS -->
    <g id="edges"></g>
  </svg>
</div>

<!-- node container — positioned over SVG -->
<div id="nodes"></div>

<!-- compose panel -->
<div id="panel">
  <div id="panel-header">
    <div id="panel-avatar">?</div>
    <div id="panel-meta">
      <div id="panel-name">—</div>
      <div id="panel-agent"></div>
      <div id="panel-onion"></div>
    </div>
    <button id="panel-close" onclick="closePanel()">✕</button>
  </div>
  <div id="thread"></div>
  <div id="compose">
    <textarea id="compose-area" placeholder="Message (max 2000 bytes)…" oninput="onType()" rows="3"></textarea>
    <div id="compose-footer">
      <span id="byte-counter">0 / 2000</span>
      <button id="send-btn" onclick="doSend()" disabled>Send →</button>
    </div>
    <div id="send-status"></div>
  </div>
</div>

<!-- inbox drawer -->
<div id="inbox-panel">
  <div id="inbox-header">
    <span>Sealed Envelopes</span>
    <button onclick="toggleInbox()">✕</button>
  </div>
  <div id="inbox-list"></div>
</div>

<!-- status bar -->
<div id="statusbar">
  <span><span class="sb-dot off" id="sb-tor-dot"></span><span id="sb-tor-label">Tor</span></span>
  <span id="sb-onion"></span>
  <span style="flex:1"></span>
  <span id="sb-inbox-btn" onclick="toggleInbox()" style="cursor:pointer;color:#3a6888">
    ▲ Inbox (<span id="sb-inbox-count">0</span>)
  </span>
</div>

<script>
// ── state ─────────────────────────────────────────────────────────────────
let contacts = [];
let selected = null;   // contact id
let inboxOpen = false;
const CENTER = {x: 500, y: 360};
const ORBIT_R = 210;

// ── boot ──────────────────────────────────────────────────────────────────
async function boot() {
  await loadContacts();
  pollStatus();
  setInterval(pollStatus, 5000);
}

// ── contacts ──────────────────────────────────────────────────────────────
async function loadContacts() {
  const r = await fetch('/api/contacts');
  contacts = await r.json();
  renderNodes();
}

function renderNodes() {
  const svg = document.getElementById('edges');
  const container = document.getElementById('nodes');
  svg.innerHTML = '';
  container.innerHTML = '';

  // Genesis node (self)
  const gEl = makeNode('genesis', 'G', 'Genesis', true, true);
  gEl.style.left = pct(CENTER.x, 1000) + '%';
  gEl.style.top  = pct(CENTER.y, 700)  + '%';
  gEl.classList.add('node-genesis');
  // inbox badge
  const badge = document.createElement('div');
  badge.id = 'inbox-badge';
  badge.style.cssText = 'position:absolute;top:-4px;right:-4px;min-width:20px;height:20px;padding:0 5px;background:#d04040;border-radius:10px;font-size:0.62rem;font-weight:700;color:#fff;display:none;align-items:center;justify-content:center;border:2px solid #080c12';
  badge.id = 'inbox-badge';
  gEl.querySelector('.node-ring').appendChild(badge);
  container.appendChild(gEl);

  // Contact nodes
  const n = contacts.length;
  contacts.forEach((c, i) => {
    const angle = (i / n) * 2 * Math.PI - Math.PI / 2;
    const cx = CENTER.x + ORBIT_R * Math.cos(angle);
    const cy = CENTER.y + ORBIT_R * Math.sin(angle);

    // SVG edge
    const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
    line.id = 'edge-' + c.id;
    line.setAttribute('class', 'edge');
    line.setAttribute('x1', CENTER.x); line.setAttribute('y1', CENTER.y);
    line.setAttribute('x2', cx);       line.setAttribute('y2', cy);
    svg.appendChild(line);

    // Node div
    const letter = (c.name || '?')[0].toUpperCase();
    const el = makeNode(c.id, letter, c.name, c.configured, false);
    el.style.left = pct(cx, 1000) + '%';
    el.style.top  = pct(cy, 700)  + '%';
    el.classList.add('node-contact');
    if (c.configured) el.classList.add('configured');
    el.onclick = () => selectContact(c.id);
    container.appendChild(el);
  });
}

function makeNode(id, letter, label, configured, isGenesis) {
  const el = document.createElement('div');
  el.className = 'node';
  el.id = 'node-' + id;
  const ring = document.createElement('div');
  ring.className = 'node-ring' + (isGenesis ? ' pulse' : '');
  const av = document.createElement('div');
  av.className = 'node-avatar';
  av.textContent = letter;
  ring.appendChild(av);
  if (!isGenesis) {
    const dot = document.createElement('div');
    dot.className = 'node-dot ' + (configured ? 'ok' : 'off');
    ring.appendChild(dot);
  }
  el.appendChild(ring);
  const lbl = document.createElement('div');
  lbl.className = 'node-label';
  lbl.textContent = label;
  el.appendChild(lbl);
  return el;
}

function pct(v, total) { return (v / total * 100).toFixed(3); }

// ── select / panel ────────────────────────────────────────────────────────
async function selectContact(id) {
  // deselect old
  if (selected) {
    document.getElementById('node-' + selected)?.classList.remove('selected');
    document.getElementById('edge-' + selected)?.classList.remove('active');
  }
  selected = id;
  document.getElementById('node-' + id)?.classList.add('selected');
  document.getElementById('edge-' + id)?.classList.add('active');

  const c = contacts.find(x => x.id === id);
  if (!c) return;

  // populate panel
  document.getElementById('panel-avatar').textContent = (c.name || '?')[0].toUpperCase();
  document.getElementById('panel-name').textContent = c.name || id;
  document.getElementById('panel-agent').textContent = c.agent_id || '(agent_id not configured)';
  document.getElementById('panel-onion').textContent = c.onion  || '(onion not configured)';

  // update status bar onion
  document.getElementById('sb-onion').textContent = c.onion ? c.onion.slice(0, 40) + '…' : '';

  // load sent
  await loadSent(id);

  // open panel
  document.getElementById('panel').classList.add('open');
  document.getElementById('compose-area').value = '';
  onType();
  document.getElementById('send-status').textContent = '';
  document.getElementById('send-btn').disabled = !c.configured;
  if (!c.configured) {
    document.getElementById('send-status').style.color = '#806040';
    document.getElementById('send-status').textContent = 'Contact not configured — placeholders still set';
  }
}

function closePanel() {
  document.getElementById('panel').classList.remove('open');
  if (selected) {
    document.getElementById('node-' + selected)?.classList.remove('selected');
    document.getElementById('edge-' + selected)?.classList.remove('active');
  }
  selected = null;
  document.getElementById('sb-onion').textContent = '';
}

// ── thread ────────────────────────────────────────────────────────────────
async function loadSent(id) {
  const r = await fetch('/api/sent?id=' + encodeURIComponent(id));
  const msgs = await r.json();
  const thread = document.getElementById('thread');
  if (!msgs.length) {
    thread.innerHTML = '<div class="thread-empty">No messages sent yet</div>';
    return;
  }
  thread.innerHTML = msgs.map(m => {
    const dt = new Date(m.ts * 1000).toLocaleString();
    return `<div class="msg-bubble">
      <div class="msg-text">${esc(m.message)}</div>
      <div class="msg-meta">${esc(dt)}</div>
      <div class="msg-receipt">${esc(m.receipt || '')}</div>
    </div>`;
  }).join('');
  thread.scrollTop = thread.scrollHeight;
}

// ── compose ───────────────────────────────────────────────────────────────
function onType() {
  const ta = document.getElementById('compose-area');
  const bytes = new TextEncoder().encode(ta.value).length;
  const counter = document.getElementById('byte-counter');
  counter.textContent = bytes + ' / 2000';
  counter.className = bytes > 2000 ? 'over' : bytes > 1800 ? 'warn' : '';
  const c = contacts.find(x => x.id === selected);
  document.getElementById('send-btn').disabled =
    !ta.value.trim() || bytes > 2000 || !c?.configured;
}

async function doSend() {
  const ta = document.getElementById('compose-area');
  const msg = ta.value.trim();
  if (!msg || !selected) return;
  const btn = document.getElementById('send-btn');
  const status = document.getElementById('send-status');
  btn.disabled = true;
  status.style.color = '#5090a0';
  status.textContent = 'Sealing and routing via Tor…';

  try {
    const r = await fetch('/api/send', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({contact_id: selected, message: msg}),
    });
    const data = await r.json();
    if (data.ok) {
      status.style.color = '#28c87a';
      status.textContent = 'Delivered — ' + (data.receipt || '').slice(0, 16) + '…';
      ta.value = '';
      onType();
      // animate edge
      const edge = document.getElementById('edge-' + selected);
      if (edge) {
        edge.style.stroke = '#28c87a';
        setTimeout(() => { edge.style.stroke = ''; }, 1500);
      }
      await loadSent(selected);
    } else {
      status.style.color = '#d06040';
      status.textContent = 'Error: ' + (data.error || 'unknown');
      btn.disabled = false;
    }
  } catch (e) {
    status.style.color = '#d06040';
    status.textContent = 'Network error: ' + e.message;
    btn.disabled = false;
  }
}

// ── inbox ─────────────────────────────────────────────────────────────────
function toggleInbox() {
  inboxOpen = !inboxOpen;
  document.getElementById('inbox-panel').classList.toggle('open', inboxOpen);
  if (inboxOpen) loadInbox();
}

async function loadInbox() {
  const r = await fetch('/api/inbox');
  const envs = await r.json();
  const list = document.getElementById('inbox-list');
  if (!envs.length) {
    list.innerHTML = '<div style="padding:12px 14px;font-size:0.62rem;color:#2a4a62">No envelopes</div>';
    return;
  }
  list.innerHTML = envs.map(e => {
    const dt = new Date(e.received * 1000).toLocaleString();
    const sizeLabel = e.size_ok ? '✓ 4156 B' : '⚠ ' + e.size + ' B';
    const sizeColor = e.size_ok ? '#2a7a52' : '#8a7030';
    return `<div class="env-card">
      <div class="env-receipt">${esc(e.receipt)}</div>
      <div class="env-size" style="color:${sizeColor}">${sizeLabel} · ${esc(dt)}</div>
    </div>`;
  }).join('');
}

// ── status poll ───────────────────────────────────────────────────────────
async function pollStatus() {
  try {
    const r = await fetch('/api/status');
    const d = await r.json();

    const dot = document.getElementById('sb-tor-dot');
    dot.className = 'sb-dot ' + (d.tor ? 'ok' : 'off');
    document.getElementById('sb-tor-label').textContent = d.tor ? 'Tor connected' : 'Tor offline';

    const count = d.inbox_count || 0;
    document.getElementById('sb-inbox-count').textContent = count;

    const badge = document.getElementById('inbox-badge');
    if (badge) {
      badge.style.display = count > 0 ? 'flex' : 'none';
      badge.textContent = count;
    }
  } catch (_) {}
}

// ── util ──────────────────────────────────────────────────────────────────
function esc(s) {
  return String(s)
    .replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')
    .replace(/"/g,'&quot;');
}

boot();
</script>
</body>
</html>
"""


# ---------------------------------------------------------------------------
# Server bootstrap
# ---------------------------------------------------------------------------

def _make_server(
    contacts_path: Path,
    inbox_dir: Path,
    sent_dir: Path,
    port: int,
) -> http.server.HTTPServer:
    class _BoundHandler(_Handler):
        pass
    _BoundHandler.contacts_path = contacts_path
    _BoundHandler.inbox_dir     = inbox_dir
    _BoundHandler.sent_dir      = sent_dir
    return http.server.HTTPServer((_LOOPBACK, port), _BoundHandler)


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
    print(f"Contacts:  {contacts_path}")
    print(f"Inbox:     {inbox_dir}")
    print(f"Sent:      {sent_dir}")
    print("Ctrl-C to stop.")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        srv.server_close()


if __name__ == "__main__":
    main()
