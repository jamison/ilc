#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
"""CCSS Admin UI — local dashboard for Genesis Agent's sealed-envelope inbox.

Serves a dark-theme chat-style web UI on 127.0.0.1:8421.
Never exposes anything outside loopback.

Panels:
  - Status bar: relay health (127.0.0.1:8420) + Tor onion address
  - Inbox: each received envelope as a message entry (receipt token, time, size)
  - Decryption: pending until sender SDK is available; raw envelope byte count shown

Usage:
    python tools/ccss_relay/ccss_admin_ui.py [--inbox <dir>] [--port <port>]
                                              [--relay-port <port>]
                                              [--tor-hs-dir <path>]
Defaults:
    --inbox        ~/.ccss_inbox/genesis
    --port         8421
    --relay-port   8420
    --tor-hs-dir   /var/lib/tor/ccss_hs
"""

from __future__ import annotations

import argparse
import hashlib
import http.client
import http.server
import json
import os
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_LOOPBACK = "127.0.0.1"
_DEFAULT_UI_PORT = 8421
_DEFAULT_RELAY_PORT = 8420
_DEFAULT_INBOX = Path.home() / ".ccss_inbox" / "genesis"
_DEFAULT_TOR_HS_DIR = Path("/var/lib/tor/ccss_hs")
_OUTER_ENVELOPE_BYTES = 4156


# ---------------------------------------------------------------------------
# API helpers
# ---------------------------------------------------------------------------

def _relay_health(relay_port: int) -> dict[str, Any]:
    try:
        conn = http.client.HTTPConnection(_LOOPBACK, relay_port, timeout=2)
        conn.request("GET", "/health")
        resp = conn.getresponse()
        body = json.loads(resp.read().decode())
        return {"ok": resp.status == 200, "status": resp.status, "body": body}
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


def _tor_status(hs_dir: Path) -> dict[str, Any]:
    hostname_file = hs_dir / "hostname"
    if hostname_file.exists():
        try:
            onion = hostname_file.read_text().strip()
            return {"ok": True, "onion": onion}
        except OSError as exc:
            return {"ok": False, "error": str(exc)}
    return {"ok": False, "error": "hostname file not found — tor not started or HS dir not configured"}


def _inbox_entries(inbox: Path) -> list[dict[str, Any]]:
    if not inbox.exists():
        return []
    entries = []
    for path in sorted(inbox.glob("*.envelope"), key=lambda p: p.stat().st_mtime, reverse=True):
        stat = path.stat()
        size = stat.st_size
        mtime = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat()
        token = path.stem
        size_ok = size == _OUTER_ENVELOPE_BYTES
        entries.append({
            "token": token,
            "token_short": token[:12] + "…",
            "received_at": mtime,
            "size_bytes": size,
            "size_ok": size_ok,
            "filename": path.name,
        })
    return entries


# ---------------------------------------------------------------------------
# HTML page
# ---------------------------------------------------------------------------

_HTML = """\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>CCSS Inbox — Genesis Agent</title>
<style>
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

  body {
    background: #0d0f14;
    color: #c9d1d9;
    font-family: 'SF Mono', 'Fira Code', 'Courier New', monospace;
    font-size: 13px;
    height: 100vh;
    display: flex;
    flex-direction: column;
  }

  /* ── Header ── */
  header {
    background: #161b22;
    border-bottom: 1px solid #21262d;
    padding: 12px 20px;
    display: flex;
    align-items: center;
    gap: 16px;
    flex-shrink: 0;
  }
  header h1 {
    font-size: 14px;
    font-weight: 600;
    color: #e6edf3;
    letter-spacing: 0.02em;
  }
  header .subtitle {
    font-size: 11px;
    color: #6e7681;
  }

  /* ── Status bar ── */
  .status-bar {
    background: #161b22;
    border-bottom: 1px solid #21262d;
    padding: 8px 20px;
    display: flex;
    gap: 24px;
    align-items: center;
    flex-shrink: 0;
  }
  .status-item {
    display: flex;
    align-items: center;
    gap: 7px;
    font-size: 12px;
    color: #8b949e;
  }
  .status-item .label { color: #6e7681; }
  .status-item .value { color: #c9d1d9; }
  .dot {
    width: 8px; height: 8px;
    border-radius: 50%;
    flex-shrink: 0;
  }
  .dot.green  { background: #3fb950; box-shadow: 0 0 6px #3fb95066; }
  .dot.red    { background: #f85149; box-shadow: 0 0 6px #f8514966; }
  .dot.grey   { background: #484f58; }
  .dot.pulse  { animation: pulse 2s ease-in-out infinite; }
  @keyframes pulse {
    0%, 100% { opacity: 1; }
    50%       { opacity: 0.4; }
  }
  .onion-addr {
    font-family: inherit;
    font-size: 11px;
    color: #79c0ff;
    word-break: break-all;
  }

  /* ── Toolbar ── */
  .toolbar {
    padding: 8px 20px;
    display: flex;
    align-items: center;
    gap: 12px;
    border-bottom: 1px solid #21262d;
    flex-shrink: 0;
    background: #0d0f14;
  }
  .toolbar .count {
    font-size: 12px;
    color: #8b949e;
  }
  .toolbar .count strong { color: #e6edf3; }
  .refresh-btn {
    margin-left: auto;
    background: #21262d;
    border: 1px solid #30363d;
    border-radius: 6px;
    color: #c9d1d9;
    font-family: inherit;
    font-size: 12px;
    padding: 4px 12px;
    cursor: pointer;
  }
  .refresh-btn:hover { background: #30363d; }
  .last-refresh { font-size: 11px; color: #484f58; }

  /* ── Message list ── */
  .messages {
    flex: 1;
    overflow-y: auto;
    padding: 16px 20px;
    display: flex;
    flex-direction: column;
    gap: 12px;
  }
  .messages::-webkit-scrollbar { width: 6px; }
  .messages::-webkit-scrollbar-track { background: transparent; }
  .messages::-webkit-scrollbar-thumb { background: #30363d; border-radius: 3px; }

  /* ── Empty state ── */
  .empty {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 10px;
    color: #484f58;
    padding: 40px;
    text-align: center;
  }
  .empty .icon { font-size: 32px; }
  .empty p { font-size: 13px; line-height: 1.6; }

  /* ── Envelope card ── */
  .envelope {
    background: #161b22;
    border: 1px solid #21262d;
    border-radius: 8px;
    padding: 14px 16px;
    display: flex;
    flex-direction: column;
    gap: 8px;
    transition: border-color 0.15s;
  }
  .envelope:hover { border-color: #388bfd44; }
  .envelope.size-warn { border-color: #f8514933; }

  .env-header {
    display: flex;
    align-items: center;
    gap: 10px;
  }
  .env-badge {
    background: #1c2128;
    border: 1px solid #30363d;
    border-radius: 4px;
    padding: 2px 8px;
    font-size: 10px;
    color: #8b949e;
    letter-spacing: 0.06em;
    text-transform: uppercase;
  }
  .env-token {
    font-size: 12px;
    color: #79c0ff;
    font-family: inherit;
    flex: 1;
  }
  .env-token .full { display: none; }
  .env-token:hover .short { display: none; }
  .env-token:hover .full  { display: inline; }

  .env-meta {
    display: flex;
    gap: 16px;
    font-size: 11px;
    color: #6e7681;
  }
  .env-meta span strong { color: #8b949e; }

  .env-status {
    font-size: 11px;
    padding: 4px 10px;
    border-radius: 4px;
    background: #1c2128;
    border: 1px solid #21262d;
    color: #484f58;
    display: inline-flex;
    align-items: center;
    gap: 6px;
  }
  .env-status.ok { color: #3fb950; border-color: #3fb95033; }
  .env-status.warn { color: #d29922; border-color: #d2992233; }

  /* ── Footer ── */
  footer {
    border-top: 1px solid #21262d;
    padding: 8px 20px;
    font-size: 11px;
    color: #484f58;
    flex-shrink: 0;
    display: flex;
    gap: 20px;
  }
  footer a { color: #58a6ff; text-decoration: none; }
  footer a:hover { text-decoration: underline; }
</style>
</head>
<body>

<header>
  <div>
    <h1>CCSS Inbox</h1>
    <div class="subtitle">Genesis Agent — sealed inbound envelopes</div>
  </div>
</header>

<div class="status-bar" id="status-bar">
  <div class="status-item">
    <div class="dot grey" id="relay-dot"></div>
    <span class="label">Relay</span>
    <span class="value" id="relay-label">checking…</span>
  </div>
  <div class="status-item">
    <div class="dot grey" id="tor-dot"></div>
    <span class="label">Tor HS</span>
    <span class="value" id="tor-label">checking…</span>
  </div>
  <div class="status-item" id="onion-item" style="display:none">
    <span class="label">Onion</span>
    <span class="onion-addr" id="onion-addr"></span>
  </div>
</div>

<div class="toolbar">
  <span class="count">Envelopes: <strong id="count">—</strong></span>
  <span class="last-refresh" id="last-refresh"></span>
  <button class="refresh-btn" onclick="refresh()">↻ Refresh</button>
</div>

<div id="view"></div>

<footer>
  <span>Local admin UI — loopback only</span>
  <a href="/api/status" target="_blank">/api/status</a>
  <a href="/api/inbox" target="_blank">/api/inbox</a>
</footer>

<script>
async function refresh() {
  try {
    const [statusResp, inboxResp] = await Promise.all([
      fetch('/api/status'),
      fetch('/api/inbox'),
    ]);
    const status = await statusResp.json();
    const inbox  = await inboxResp.json();
    renderStatus(status);
    renderInbox(inbox);
    document.getElementById('last-refresh').textContent =
      'Last refresh: ' + new Date().toLocaleTimeString();
  } catch (e) {
    console.error('Refresh failed:', e);
  }
}

function renderStatus(s) {
  const relayDot   = document.getElementById('relay-dot');
  const relayLabel = document.getElementById('relay-label');
  const torDot     = document.getElementById('tor-dot');
  const torLabel   = document.getElementById('tor-label');
  const onionItem  = document.getElementById('onion-item');
  const onionAddr  = document.getElementById('onion-addr');

  if (s.relay.ok) {
    relayDot.className = 'dot green pulse';
    relayLabel.textContent = 'online :' + s.relay_port;
  } else {
    relayDot.className = 'dot red';
    relayLabel.textContent = 'offline — ' + (s.relay.error || 'not responding');
  }

  if (s.tor.ok) {
    torDot.className = 'dot green';
    torLabel.textContent = 'connected';
    onionItem.style.display = 'flex';
    onionAddr.textContent = s.tor.onion;
  } else {
    torDot.className = 'dot grey';
    torLabel.textContent = s.tor.error || 'not configured';
    onionItem.style.display = 'none';
  }
}

function renderInbox(inbox) {
  const view  = document.getElementById('view');
  const count = document.getElementById('count');
  const items = inbox.envelopes || [];
  count.textContent = items.length;

  if (items.length === 0) {
    view.innerHTML = \`
      <div class="empty">
        <div class="icon">⬡</div>
        <p>No sealed envelopes received yet.<br>
           Waiting for senders via Tor hidden service.</p>
      </div>\`;
    return;
  }

  const cards = items.map(env => {
    const sizeOk = env.size_ok;
    const dt = new Date(env.received_at).toLocaleString();
    const statusClass = sizeOk ? 'ok' : 'warn';
    const statusText  = sizeOk
      ? '✓ ' + env.size_bytes + 'B  H013 outer envelope'
      : '⚠ unexpected size: ' + env.size_bytes + 'B (expected 4156)';
    return \`
      <div class="envelope \${sizeOk ? '' : 'size-warn'}">
        <div class="env-header">
          <span class="env-badge">sealed</span>
          <span class="env-token">
            <span class="short">\${env.token_short}</span>
            <span class="full">\${env.token}</span>
          </span>
        </div>
        <div class="env-meta">
          <span><strong>Received:</strong> \${dt}</span>
          <span><strong>File:</strong> \${env.filename}</span>
        </div>
        <div class="env-status \${statusClass}">\${statusText}</div>
      </div>\`;
  }).join('');

  view.innerHTML = '<div class="messages">' + cards + '</div>';
}

// Auto-refresh every 5 seconds
setInterval(refresh, 5000);
refresh();
</script>
</body>
</html>
"""


# ---------------------------------------------------------------------------
# HTTP handler
# ---------------------------------------------------------------------------

def _make_handler(
    inbox: Path,
    relay_port: int,
    tor_hs_dir: Path,
) -> type[http.server.BaseHTTPRequestHandler]:

    class AdminUIHandler(http.server.BaseHTTPRequestHandler):
        def log_message(self, fmt: str, *args: object) -> None:
            pass

        def _send(self, status: int, content_type: str, body: bytes) -> None:
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Connection", "close")
            self.end_headers()
            self.wfile.write(body)

        def _send_json(self, status: int, data: Any) -> None:
            body = json.dumps(data, separators=(",", ":"), sort_keys=True).encode()
            self._send(status, "application/json", body)

        def do_GET(self) -> None:
            path = self.path.split("?")[0]

            if path == "/" or path == "/index.html":
                self._send(200, "text/html; charset=utf-8", _HTML.encode())

            elif path == "/api/status":
                self._send_json(200, {
                    "relay": _relay_health(relay_port),
                    "relay_port": relay_port,
                    "tor": _tor_status(tor_hs_dir),
                })

            elif path == "/api/inbox":
                self._send_json(200, {
                    "envelopes": _inbox_entries(inbox),
                    "inbox_path": str(inbox),
                })

            else:
                self._send_json(404, {"error": "not_found"})

    return AdminUIHandler


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="CCSS admin UI — local dashboard for Genesis Agent's inbox."
    )
    parser.add_argument("--inbox", type=Path, default=_DEFAULT_INBOX)
    parser.add_argument("--port", type=int, default=_DEFAULT_UI_PORT)
    parser.add_argument("--relay-port", type=int, default=_DEFAULT_RELAY_PORT)
    parser.add_argument("--tor-hs-dir", type=Path, default=_DEFAULT_TOR_HS_DIR)
    args = parser.parse_args(argv)

    inbox = args.inbox.resolve()
    tor_hs_dir = args.tor_hs_dir

    handler = _make_handler(inbox, args.relay_port, tor_hs_dir)
    server = http.server.HTTPServer((_LOOPBACK, args.port), handler)

    url = f"http://{_LOOPBACK}:{args.port}"
    print(f"CCSS admin UI: {url}", flush=True)
    print(f"  Inbox:      {inbox}", flush=True)
    print(f"  Relay:      {_LOOPBACK}:{args.relay_port}", flush=True)
    print(f"  Tor HS dir: {tor_hs_dir}", flush=True)
    print(f"Open {url} in your browser.", flush=True)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nCCSS admin UI: stopped.", flush=True)

    return 0


if __name__ == "__main__":
    sys.exit(main())
