#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
"""CCSS Sender UI — compose and send sealed messages to Genesis Agent.

A minimal dark-theme web UI served on 127.0.0.1:8422.
Encrypts your message locally (X25519 + ChaCha20-Poly1305), then
routes the sealed envelope through the Tor SOCKS5 proxy (127.0.0.1:9050)
to Genesis Agent's onion address.

Usage:
    python tools/ccss_send/ccss_sender_ui.py [--identity <path>] [--port <port>]

Defaults:
    --identity  docs/contact/genesis_identity.json
    --port      8422

Requires:
    - cryptography >= 41.0 (already in requirements.txt)
    - Tor running locally with SOCKS5 at 127.0.0.1:9050
    - docs/contact/genesis_identity.json populated (run after deploy)
"""

from __future__ import annotations

import argparse
import hashlib
import http.server
import json
import os
import socket
import struct
import sys
from pathlib import Path
from typing import Any

_LOOPBACK = "127.0.0.1"
_DEFAULT_PORT = 8422
_DEFAULT_IDENTITY = Path(__file__).resolve().parent.parent.parent / "docs" / "contact" / "genesis_identity.json"
_TOR_PROXY_HOST = "127.0.0.1"
_TOR_PROXY_PORT = 9050
_RELAY_SUBMIT_PATH = "/submit"
_OUTER_ENVELOPE_BYTES = 4156
_MAX_MESSAGE_BYTES = 2000


# ---------------------------------------------------------------------------
# Tor SOCKS5 send (stdlib only — no PySocks needed)
# ---------------------------------------------------------------------------

def _socks5_send_envelope(onion: str, envelope: bytes, timeout: int = 30) -> dict[str, Any]:
    """Send envelope to onion:80/submit through Tor SOCKS5 proxy."""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout)
    try:
        s.connect((_TOR_PROXY_HOST, _TOR_PROXY_PORT))

        # SOCKS5 greeting — no auth
        s.sendall(b"\x05\x01\x00")
        ver, method = s.recv(2)
        if method != 0x00:
            raise OSError(f"SOCKS5: unexpected auth method {method:#x}")

        # SOCKS5 CONNECT to onion:80
        host_b = onion.encode("ascii")
        s.sendall(
            bytes([0x05, 0x01, 0x00, 0x03, len(host_b)])
            + host_b
            + struct.pack(">H", 80)
        )
        resp = s.recv(10)
        if resp[1] != 0x00:
            raise OSError(f"SOCKS5 CONNECT failed: {resp[1]:#x}")

        # HTTP POST
        body = envelope
        request = (
            f"POST {_RELAY_SUBMIT_PATH} HTTP/1.0\r\n"
            f"Host: {onion}\r\n"
            f"Content-Type: application/octet-stream\r\n"
            f"Content-Length: {len(body)}\r\n"
            f"Connection: close\r\n"
            f"\r\n"
        ).encode() + body
        s.sendall(request)

        # Read response
        chunks = []
        while True:
            chunk = s.recv(4096)
            if not chunk:
                break
            chunks.append(chunk)
        raw = b"".join(chunks).decode("utf-8", errors="replace")
    finally:
        s.close()

    # Parse HTTP response
    header_end = raw.find("\r\n\r\n")
    status_line = raw.split("\r\n", 1)[0]
    body_text = raw[header_end + 4:] if header_end != -1 else ""

    try:
        status_code = int(status_line.split()[1])
    except (IndexError, ValueError):
        status_code = 0

    try:
        resp_json = json.loads(body_text)
    except json.JSONDecodeError:
        resp_json = {"raw": body_text[:200]}

    return {"http_status": status_code, "body": resp_json}


def _check_tor() -> dict[str, Any]:
    """Return whether Tor SOCKS5 proxy is reachable."""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(2)
    try:
        s.connect((_TOR_PROXY_HOST, _TOR_PROXY_PORT))
        return {"ok": True}
    except OSError as exc:
        return {"ok": False, "error": str(exc)}
    finally:
        s.close()


def _load_identity(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"configured": False, "error": "identity file not found"}
    try:
        data = json.loads(path.read_text())
    except Exception as exc:
        return {"configured": False, "error": str(exc)}

    pubkey = data.get("ccss_recipient_pubkey", "")
    onion  = data.get("ccss_contact_onion", "")
    configured = (
        bool(pubkey) and "PLACEHOLDER" not in pubkey.upper()
        and bool(onion) and "PLACEHOLDER" not in onion.upper()
    )
    return {
        "configured": configured,
        "onion": onion if configured else None,
        "agent_id": data.get("agent_id", ""),
        "pubkey_set": bool(pubkey) and "PLACEHOLDER" not in pubkey.upper(),
    }


# ---------------------------------------------------------------------------
# HTML
# ---------------------------------------------------------------------------

_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Send to Genesis Agent — CCSS</title>
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

  header {
    background: #161b22;
    border-bottom: 1px solid #21262d;
    padding: 12px 20px;
    display: flex;
    align-items: center;
    gap: 16px;
    flex-shrink: 0;
  }
  header h1 { font-size: 14px; font-weight: 600; color: #e6edf3; }
  header .subtitle { font-size: 11px; color: #6e7681; }

  .status-bar {
    background: #161b22;
    border-bottom: 1px solid #21262d;
    padding: 8px 20px;
    display: flex;
    gap: 24px;
    align-items: center;
    flex-shrink: 0;
    flex-wrap: wrap;
  }
  .status-item { display: flex; align-items: center; gap: 7px; font-size: 12px; color: #8b949e; }
  .status-item .label { color: #6e7681; }
  .status-item .value { color: #c9d1d9; }
  .dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }
  .dot.green { background: #3fb950; box-shadow: 0 0 6px #3fb95066; }
  .dot.red   { background: #f85149; box-shadow: 0 0 6px #f8514966; }
  .dot.grey  { background: #484f58; }
  .dot.pulse { animation: pulse 2s ease-in-out infinite; }
  @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:.4} }
  .onion-addr { font-size: 11px; color: #79c0ff; word-break: break-all; }

  .compose-wrap {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 24px 20px;
    gap: 0;
  }

  .compose-card {
    width: 100%;
    max-width: 640px;
    background: #161b22;
    border: 1px solid #21262d;
    border-radius: 10px;
    overflow: hidden;
    display: flex;
    flex-direction: column;
  }

  .compose-to {
    padding: 10px 16px;
    border-bottom: 1px solid #21262d;
    font-size: 12px;
    color: #6e7681;
    display: flex;
    align-items: center;
    gap: 10px;
  }
  .compose-to .to-label { color: #484f58; }
  .compose-to .to-val { color: #79c0ff; }
  .compose-to .agent-id {
    margin-left: auto;
    font-size: 10px;
    color: #484f58;
    max-width: 200px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  textarea {
    background: transparent;
    border: none;
    outline: none;
    color: #c9d1d9;
    font-family: inherit;
    font-size: 13px;
    line-height: 1.6;
    padding: 16px;
    resize: none;
    min-height: 180px;
    width: 100%;
  }
  textarea::placeholder { color: #484f58; }

  .compose-footer {
    padding: 10px 16px;
    border-top: 1px solid #21262d;
    display: flex;
    align-items: center;
    gap: 10px;
  }
  .char-count { font-size: 11px; color: #6e7681; }
  .char-count.warn { color: #d29922; }
  .char-count.over { color: #f85149; }

  .send-btn {
    margin-left: auto;
    background: #1f6feb;
    border: 1px solid #388bfd44;
    border-radius: 6px;
    color: #e6edf3;
    font-family: inherit;
    font-size: 12px;
    font-weight: 600;
    padding: 6px 18px;
    cursor: pointer;
    transition: background 0.15s;
  }
  .send-btn:hover:not(:disabled) { background: #388bfd; }
  .send-btn:disabled {
    background: #21262d;
    color: #484f58;
    cursor: not-allowed;
    border-color: #21262d;
  }

  .result {
    width: 100%;
    max-width: 640px;
    margin-top: 12px;
    border-radius: 8px;
    padding: 12px 16px;
    font-size: 12px;
    line-height: 1.6;
    display: none;
  }
  .result.success {
    display: block;
    background: #1c2128;
    border: 1px solid #3fb95033;
    color: #3fb950;
  }
  .result.error {
    display: block;
    background: #1c2128;
    border: 1px solid #f8514933;
    color: #f85149;
  }
  .result .receipt {
    font-size: 10px;
    color: #8b949e;
    word-break: break-all;
    margin-top: 6px;
  }

  .notice {
    width: 100%;
    max-width: 640px;
    margin-top: 12px;
    font-size: 11px;
    color: #484f58;
    line-height: 1.6;
    text-align: center;
  }

  footer {
    border-top: 1px solid #21262d;
    padding: 8px 20px;
    font-size: 11px;
    color: #484f58;
    flex-shrink: 0;
  }
</style>
</head>
<body>

<header>
  <div>
    <h1>Send to Genesis Agent</h1>
    <div class="subtitle">CCSS sealed-sender — Tor-anonymized delivery</div>
  </div>
</header>

<div class="status-bar">
  <div class="status-item">
    <div class="dot grey" id="tor-dot"></div>
    <span class="label">Tor</span>
    <span class="value" id="tor-label">checking…</span>
  </div>
  <div class="status-item">
    <div class="dot grey" id="id-dot"></div>
    <span class="label">Recipient</span>
    <span class="value" id="id-label">checking…</span>
  </div>
  <div class="status-item" id="onion-item" style="display:none">
    <span class="label">Onion</span>
    <span class="onion-addr" id="onion-addr"></span>
  </div>
</div>

<div class="compose-wrap">
  <div class="compose-card">
    <div class="compose-to">
      <span class="to-label">To:</span>
      <span class="to-val">Genesis Agent</span>
      <span class="agent-id" id="agent-id-display">—</span>
    </div>
    <textarea id="msg" placeholder="Type your message here…" maxlength="6000"
              oninput="onInput()"></textarea>
    <div class="compose-footer">
      <span class="char-count" id="char-count">0 / 2000 bytes</span>
      <button class="send-btn" id="send-btn" disabled onclick="sendMsg()">
        Send sealed →
      </button>
    </div>
  </div>

  <div class="result" id="result"></div>

  <div class="notice">
    Messages are encrypted locally before leaving your machine.
    Your IP is hidden by Tor. The relay operator cannot read content.
  </div>
</div>

<footer>Sender sidecar — loopback only — CCSS-003</footer>

<script>
let _ready = false;
let _byteLen = 0;

const MAX_BYTES = 2000;

function byteLength(str) {
  return new TextEncoder().encode(str).length;
}

function onInput() {
  const msg = document.getElementById('msg').value;
  _byteLen = byteLength(msg);
  const cc = document.getElementById('char-count');
  cc.textContent = _byteLen + ' / ' + MAX_BYTES + ' bytes';
  cc.className = 'char-count' + (_byteLen > MAX_BYTES ? ' over' : _byteLen > MAX_BYTES * 0.9 ? ' warn' : '');
  updateSendBtn();
}

function updateSendBtn() {
  const btn = document.getElementById('send-btn');
  const msg = document.getElementById('msg').value.trim();
  btn.disabled = !(_ready && msg.length > 0 && _byteLen <= MAX_BYTES);
}

async function pollStatus() {
  try {
    const r = await fetch('/api/status');
    const s = await r.json();

    const torDot   = document.getElementById('tor-dot');
    const torLabel = document.getElementById('tor-label');
    const idDot    = document.getElementById('id-dot');
    const idLabel  = document.getElementById('id-label');
    const onionItem = document.getElementById('onion-item');
    const onionAddr = document.getElementById('onion-addr');
    const agentId   = document.getElementById('agent-id-display');

    torDot.className = 'dot ' + (s.tor.ok ? 'green pulse' : 'red');
    torLabel.textContent = s.tor.ok ? 'connected (127.0.0.1:9050)' : 'not detected — start Tor';

    idDot.className = 'dot ' + (s.identity.configured ? 'green' : 'grey');
    idLabel.textContent = s.identity.configured ? 'Genesis Agent' : 'not configured (placeholder)';

    if (s.identity.configured && s.identity.onion) {
      onionItem.style.display = 'flex';
      onionAddr.textContent = s.identity.onion;
    } else {
      onionItem.style.display = 'none';
    }

    if (s.identity.agent_id) {
      agentId.textContent = s.identity.agent_id.slice(0, 32) + '…';
    }

    _ready = s.tor.ok && s.identity.configured;
    updateSendBtn();
  } catch (e) {
    console.error('Status poll failed:', e);
  }
}

async function sendMsg() {
  const btn = document.getElementById('send-btn');
  const result = document.getElementById('result');
  const msg = document.getElementById('msg').value.trim();

  btn.disabled = true;
  btn.textContent = 'Sealing…';
  result.className = 'result';
  result.innerHTML = '';

  try {
    const r = await fetch('/api/send', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: msg }),
    });
    const data = await r.json();

    if (data.ok) {
      result.className = 'result success';
      result.innerHTML =
        '✓ Envelope delivered via Tor<br>' +
        '<span class="receipt">Receipt: ' + data.receipt_token + '</span>';
      document.getElementById('msg').value = '';
      _byteLen = 0;
      document.getElementById('char-count').textContent = '0 / 2000 bytes';
      document.getElementById('char-count').className = 'char-count';
    } else {
      result.className = 'result error';
      result.innerHTML = '✗ ' + (data.error || 'send failed');
    }
  } catch (e) {
    result.className = 'result error';
    result.innerHTML = '✗ Network error: ' + e.message;
  } finally {
    btn.textContent = 'Send sealed →';
    updateSendBtn();
  }
}

setInterval(pollStatus, 5000);
pollStatus();
</script>
</body>
</html>
"""


# ---------------------------------------------------------------------------
# HTTP handler
# ---------------------------------------------------------------------------

def _make_handler(
    identity_path: Path,
) -> type[http.server.BaseHTTPRequestHandler]:

    class SenderUIHandler(http.server.BaseHTTPRequestHandler):
        def log_message(self, fmt: str, *args: object) -> None:
            pass

        def _send(self, status: int, ct: str, body: bytes) -> None:
            self.send_response(status)
            self.send_header("Content-Type", ct)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Connection", "close")
            self.end_headers()
            self.wfile.write(body)

        def _json(self, status: int, data: Any) -> None:
            b = json.dumps(data, separators=(",", ":"), sort_keys=True).encode()
            self._send(status, "application/json", b)

        def do_GET(self) -> None:
            path = self.path.split("?")[0]
            if path in ("/", "/index.html"):
                self._send(200, "text/html; charset=utf-8", _HTML.encode())
            elif path == "/api/status":
                self._json(200, {
                    "tor": _check_tor(),
                    "identity": _load_identity(identity_path),
                })
            else:
                self._json(404, {"error": "not_found"})

        def do_POST(self) -> None:
            if self.path != "/api/send":
                self._json(404, {"error": "not_found"})
                return

            try:
                length = int(self.headers.get("Content-Length", "0"))
                raw = self.rfile.read(min(length, 65536))
                payload = json.loads(raw)
            except Exception as exc:
                self._json(400, {"ok": False, "error": f"bad request: {exc}"})
                return

            message = payload.get("message", "")
            if not isinstance(message, str) or not message.strip():
                self._json(400, {"ok": False, "error": "message is required"})
                return
            if len(message.encode("utf-8")) > _MAX_MESSAGE_BYTES:
                self._json(400, {"ok": False, "error": "message exceeds 2000 bytes"})
                return

            # Load identity
            identity = _load_identity(identity_path)
            if not identity.get("configured"):
                self._json(503, {"ok": False, "error": "recipient not configured — update genesis_identity.json"})
                return

            # Encrypt
            try:
                import json as _json
                id_data = _json.loads(identity_path.read_text())
                pubkey_hex = id_data["ccss_recipient_pubkey"]
                onion = id_data["ccss_contact_onion"]

                # Import here to keep startup fast
                import sys
                sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
                from tools.ccss_send.ccss_encrypt import seal_message

                envelope = seal_message(message, pubkey_hex)
            except Exception as exc:
                self._json(500, {"ok": False, "error": f"encryption failed: {exc}"})
                return

            # Send via Tor
            try:
                result = _socks5_send_envelope(onion, envelope)
            except Exception as exc:
                self._json(502, {"ok": False, "error": f"tor delivery failed: {exc}"})
                return

            if result["http_status"] == 200:
                receipt = result["body"].get("receipt_token", "unknown")
                self._json(200, {"ok": True, "receipt_token": receipt})
            else:
                self._json(502, {
                    "ok": False,
                    "error": f"relay returned {result['http_status']}",
                    "relay_body": result.get("body"),
                })

    return SenderUIHandler


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="CCSS sender UI — compose sealed messages to Genesis Agent."
    )
    parser.add_argument("--identity", type=Path, default=_DEFAULT_IDENTITY,
                        help="Path to genesis_identity.json")
    parser.add_argument("--port", type=int, default=_DEFAULT_PORT)
    args = parser.parse_args(argv)

    identity = args.identity.resolve()
    handler = _make_handler(identity)
    server = http.server.HTTPServer((_LOOPBACK, args.port), handler)

    url = f"http://{_LOOPBACK}:{args.port}"
    print(f"CCSS sender UI: {url}", flush=True)
    print(f"  Identity: {identity}", flush=True)
    print(f"  Tor:      {_TOR_PROXY_HOST}:{_TOR_PROXY_PORT}", flush=True)
    print(f"Open {url} in your browser.", flush=True)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nCCSS sender UI: stopped.", flush=True)

    return 0


if __name__ == "__main__":
    sys.exit(main())
