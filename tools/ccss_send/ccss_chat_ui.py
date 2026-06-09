#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
"""CCSS Chat UI — three-column operator dashboard.

Left:   contacts (agents you can send to)
Center: conversation with selected contact (sent history + compose)
Right:  inbox (sealed envelopes received)

Served on 127.0.0.1:8422. Loopback only.

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
import struct
import sys
import time
from datetime import datetime, timezone
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
# Data helpers
# ---------------------------------------------------------------------------

def _check_tor() -> dict[str, Any]:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(2)
    try:
        s.connect((_TOR_HOST, _TOR_PORT))
        return {"ok": True}
    except OSError as exc:
        return {"ok": False, "error": str(exc)}
    finally:
        s.close()


def _load_contacts(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    try:
        contacts = json.loads(path.read_text())
    except Exception:
        return []
    result = []
    for c in contacts:
        pubkey = c.get("ccss_recipient_pubkey", "")
        onion  = c.get("ccss_contact_onion", "")
        configured = (
            bool(pubkey) and "PLACEHOLDER" not in pubkey.upper()
            and bool(onion)  and "PLACEHOLDER" not in onion.upper()
        )
        result.append({
            "id":          c.get("id", ""),
            "name":        c.get("name", "Unknown"),
            "description": c.get("description", ""),
            "agent_id":    c.get("agent_id", ""),
            "configured":  configured,
            "onion":       onion if configured else None,
            # don't expose pubkey to JS
        })
    return result


def _sent_for(sent_dir: Path, contact_id: str) -> list[dict[str, Any]]:
    conv_dir = sent_dir / contact_id
    if not conv_dir.exists():
        return []
    msgs = []
    for p in sorted(conv_dir.glob("*.json"), key=lambda f: f.stat().st_mtime):
        try:
            data = json.loads(p.read_text())
            msgs.append(data)
        except Exception:
            pass
    return msgs


def _inbox_entries(inbox: Path) -> list[dict[str, Any]]:
    if not inbox.exists():
        return []
    entries = []
    for p in sorted(
        inbox.glob("*.envelope"),
        key=lambda f: f.stat().st_mtime,
        reverse=True,
    ):
        stat = p.stat()
        entries.append({
            "token":       p.stem,
            "token_short": p.stem[:10] + "…",
            "received_at": datetime.fromtimestamp(
                stat.st_mtime, tz=timezone.utc
            ).isoformat(),
            "size_bytes":  stat.st_size,
            "size_ok":     stat.st_size == _OUTER_ENVELOPE_BYTES,
        })
    return entries


def _save_sent(sent_dir: Path, contact_id: str, message: str, receipt: str) -> None:
    conv_dir = sent_dir / contact_id
    conv_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(tz=timezone.utc).isoformat()
    fname = f"{int(time.time() * 1000)}_{receipt[:8]}.json"
    record = {
        "contact_id":    contact_id,
        "message":       message,
        "sent_at":       ts,
        "receipt_token": receipt,
    }
    tmp = conv_dir / (fname + ".tmp")
    tmp.write_text(json.dumps(record, sort_keys=True))
    tmp.rename(conv_dir / fname)


def _socks5_send(onion: str, envelope: bytes, timeout: int = 30) -> dict[str, Any]:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout)
    try:
        s.connect((_TOR_HOST, _TOR_PORT))
        s.sendall(b"\x05\x01\x00")
        _, method = s.recv(2)
        if method != 0x00:
            raise OSError(f"SOCKS5 auth failed: {method:#x}")
        host_b = onion.encode("ascii")
        s.sendall(
            bytes([0x05, 0x01, 0x00, 0x03, len(host_b)])
            + host_b + struct.pack(">H", 80)
        )
        resp = s.recv(10)
        if resp[1] != 0x00:
            raise OSError(f"SOCKS5 CONNECT failed: {resp[1]:#x}")
        req = (
            f"POST /submit HTTP/1.0\r\nHost: {onion}\r\n"
            f"Content-Type: application/octet-stream\r\n"
            f"Content-Length: {len(envelope)}\r\nConnection: close\r\n\r\n"
        ).encode() + envelope
        s.sendall(req)
        chunks = []
        while True:
            chunk = s.recv(4096)
            if not chunk:
                break
            chunks.append(chunk)
    finally:
        s.close()
    raw = b"".join(chunks).decode("utf-8", errors="replace")
    header_end = raw.find("\r\n\r\n")
    status_code = 0
    try:
        status_code = int(raw.split("\r\n", 1)[0].split()[1])
    except (IndexError, ValueError):
        pass
    body_text = raw[header_end + 4:] if header_end != -1 else ""
    try:
        body = json.loads(body_text)
    except Exception:
        body = {"raw": body_text[:200]}
    return {"http_status": status_code, "body": body}


# ---------------------------------------------------------------------------
# HTML
# ---------------------------------------------------------------------------

_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>CCSS — Secure Coordination</title>
<style>
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

:root {
  --bg:       #0d0f14;
  --bg2:      #161b22;
  --bg3:      #1c2128;
  --border:   #21262d;
  --border2:  #30363d;
  --text:     #c9d1d9;
  --text2:    #8b949e;
  --text3:    #6e7681;
  --text4:    #484f58;
  --blue:     #1f6feb;
  --blue2:    #388bfd;
  --blue3:    #79c0ff;
  --green:    #3fb950;
  --red:      #f85149;
  --yellow:   #d29922;
  --mono:     'SF Mono','Fira Code','Courier New',monospace;
}

html, body { height: 100%; }

body {
  background: var(--bg);
  color: var(--text);
  font-family: var(--mono);
  font-size: 13px;
  display: flex;
  flex-direction: column;
  height: 100vh;
  overflow: hidden;
}

/* ── Top bar ── */
.topbar {
  background: var(--bg2);
  border-bottom: 1px solid var(--border);
  padding: 0 16px;
  height: 44px;
  display: flex;
  align-items: center;
  gap: 20px;
  flex-shrink: 0;
}
.topbar h1 { font-size: 13px; font-weight: 600; color: #e6edf3; letter-spacing:.02em; }
.topbar .spacer { flex: 1; }
.status-pill {
  display: flex; align-items: center; gap: 6px;
  font-size: 11px; color: var(--text2);
}
.dot {
  width: 7px; height: 7px; border-radius: 50%; flex-shrink: 0;
}
.dot.green { background: var(--green); box-shadow: 0 0 5px #3fb95055; }
.dot.red   { background: var(--red);   box-shadow: 0 0 5px #f8514955; }
.dot.grey  { background: var(--text4); }
.dot.pulse { animation: pulse 2s ease-in-out infinite; }
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:.35} }

/* ── Three-column grid ── */
.columns {
  flex: 1;
  display: grid;
  grid-template-columns: 220px 1fr 280px;
  min-height: 0;
}

/* ══ LEFT — Contacts ══ */
.col-contacts {
  background: var(--bg2);
  border-right: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
.col-contacts .col-header {
  padding: 10px 14px 8px;
  font-size: 11px;
  font-weight: 600;
  color: var(--text3);
  letter-spacing: .08em;
  text-transform: uppercase;
  border-bottom: 1px solid var(--border);
  flex-shrink: 0;
}
.contacts-list {
  flex: 1;
  overflow-y: auto;
  padding: 6px 0;
}
.contacts-list::-webkit-scrollbar { width: 4px; }
.contacts-list::-webkit-scrollbar-thumb { background: var(--border2); border-radius: 2px; }

.contact-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 9px 14px;
  cursor: pointer;
  border-left: 3px solid transparent;
  transition: background .1s;
}
.contact-item:hover { background: var(--bg3); }
.contact-item.active {
  background: var(--bg3);
  border-left-color: var(--blue2);
}
.contact-avatar {
  width: 34px; height: 34px;
  border-radius: 50%;
  background: var(--bg3);
  border: 1px solid var(--border2);
  display: flex; align-items: center; justify-content: center;
  font-size: 14px; font-weight: 600; color: var(--blue3);
  flex-shrink: 0;
}
.contact-info { flex: 1; min-width: 0; }
.contact-name {
  font-size: 13px; font-weight: 500; color: #e6edf3;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.contact-desc {
  font-size: 10px; color: var(--text3);
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
  margin-top: 1px;
}
.contact-status { flex-shrink: 0; }

.col-contacts-footer {
  padding: 10px 14px;
  border-top: 1px solid var(--border);
  flex-shrink: 0;
}
.add-btn {
  width: 100%;
  background: transparent;
  border: 1px dashed var(--border2);
  border-radius: 6px;
  color: var(--text4);
  font-family: var(--mono);
  font-size: 11px;
  padding: 6px;
  cursor: default;
  text-align: center;
}

/* ══ CENTER — Conversation ══ */
.col-convo {
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background: var(--bg);
}
.convo-header {
  height: 44px;
  border-bottom: 1px solid var(--border);
  padding: 0 16px;
  display: flex;
  align-items: center;
  gap: 10px;
  flex-shrink: 0;
  background: var(--bg2);
}
.convo-header .convo-name {
  font-size: 13px; font-weight: 600; color: #e6edf3;
}
.convo-header .convo-id {
  font-size: 10px; color: var(--text4); margin-left: 4px;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
  max-width: 220px;
}
.convo-header .convo-onion {
  font-size: 10px; color: var(--blue3);
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
  max-width: 180px; margin-left: auto;
}

.messages {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.messages::-webkit-scrollbar { width: 4px; }
.messages::-webkit-scrollbar-thumb { background: var(--border2); border-radius: 2px; }

.msg-row {
  display: flex;
  justify-content: flex-end;
}
.msg-bubble {
  background: var(--blue);
  border-radius: 12px 12px 3px 12px;
  padding: 9px 13px;
  max-width: 72%;
  line-height: 1.55;
  font-size: 13px;
  color: #e6edf3;
  word-break: break-word;
}
.msg-meta {
  font-size: 10px; color: var(--text4);
  margin-top: 3px;
  text-align: right;
  padding-right: 2px;
}
.msg-receipt {
  font-size: 9px; color: var(--text4);
  text-align: right;
}

.empty-convo {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 10px;
  color: var(--text4);
  text-align: center;
  padding: 40px;
}
.empty-convo .icon { font-size: 28px; }
.empty-convo p { font-size: 12px; line-height: 1.6; }

/* Compose area */
.compose {
  border-top: 1px solid var(--border);
  padding: 12px 16px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  flex-shrink: 0;
  background: var(--bg2);
}
.compose textarea {
  background: var(--bg3);
  border: 1px solid var(--border2);
  border-radius: 8px;
  color: var(--text);
  font-family: var(--mono);
  font-size: 13px;
  line-height: 1.5;
  padding: 10px 12px;
  resize: none;
  outline: none;
  min-height: 72px;
  max-height: 140px;
  width: 100%;
  transition: border-color .15s;
}
.compose textarea:focus { border-color: var(--blue); }
.compose textarea::placeholder { color: var(--text4); }
.compose-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}
.char-count { font-size: 11px; color: var(--text3); }
.char-count.warn { color: var(--yellow); }
.char-count.over { color: var(--red); }
.send-btn {
  margin-left: auto;
  background: var(--blue);
  border: none;
  border-radius: 6px;
  color: #e6edf3;
  font-family: var(--mono);
  font-size: 12px;
  font-weight: 600;
  padding: 7px 18px;
  cursor: pointer;
  transition: background .15s;
}
.send-btn:hover:not(:disabled) { background: var(--blue2); }
.send-btn:disabled {
  background: var(--bg3);
  color: var(--text4);
  cursor: not-allowed;
  border: 1px solid var(--border2);
}

.send-error {
  font-size: 11px; color: var(--red);
  padding: 0 2px;
  display: none;
}

/* ══ RIGHT — Inbox ══ */
.col-inbox {
  border-left: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background: var(--bg2);
}
.col-inbox .col-header {
  padding: 10px 14px 8px;
  font-size: 11px;
  font-weight: 600;
  color: var(--text3);
  letter-spacing: .08em;
  text-transform: uppercase;
  border-bottom: 1px solid var(--border);
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}
.inbox-badge {
  background: var(--blue);
  border-radius: 10px;
  font-size: 10px;
  color: #e6edf3;
  padding: 1px 7px;
  font-weight: 600;
  display: none;
}
.inbox-badge.show { display: inline; }
.inbox-list {
  flex: 1;
  overflow-y: auto;
  padding: 6px 0;
}
.inbox-list::-webkit-scrollbar { width: 4px; }
.inbox-list::-webkit-scrollbar-thumb { background: var(--border2); border-radius: 2px; }

.inbox-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  gap: 8px;
  color: var(--text4);
  text-align: center;
  height: 100%;
}
.inbox-empty .icon { font-size: 22px; }
.inbox-empty p { font-size: 11px; line-height: 1.6; }

.envelope-card {
  padding: 10px 14px;
  border-bottom: 1px solid var(--border);
  cursor: default;
  transition: background .1s;
}
.envelope-card:hover { background: var(--bg3); }
.envelope-card.selected { background: var(--bg3); }

.env-top {
  display: flex; align-items: center; gap: 6px; margin-bottom: 4px;
}
.sealed-badge {
  background: var(--bg3);
  border: 1px solid var(--border2);
  border-radius: 3px;
  font-size: 9px;
  color: var(--text3);
  padding: 1px 6px;
  letter-spacing: .06em;
  text-transform: uppercase;
}
.env-token {
  font-size: 11px; color: var(--blue3);
  overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
  flex: 1;
}
.env-time { font-size: 10px; color: var(--text4); }
.env-size {
  font-size: 10px; color: var(--text4);
}
.env-size.ok { color: var(--green); }
.env-size.warn { color: var(--yellow); }
</style>
</head>
<body>

<!-- Top bar -->
<div class="topbar">
  <h1>CCSS</h1>
  <div class="status-pill">
    <div class="dot grey" id="tor-dot"></div>
    <span id="tor-label">Tor</span>
  </div>
  <div class="status-pill" id="onion-pill" style="display:none">
    <span style="color:var(--text3)">via</span>
    <span id="onion-short" style="color:var(--blue3);font-size:11px"></span>
  </div>
  <div class="spacer"></div>
  <span style="font-size:10px;color:var(--text4)">loopback only</span>
</div>

<div class="columns">

  <!-- LEFT: Contacts -->
  <div class="col-contacts">
    <div class="col-header">Agents</div>
    <div class="contacts-list" id="contacts-list"></div>
    <div class="col-contacts-footer">
      <div class="add-btn">+ Add contact (coming soon)</div>
    </div>
  </div>

  <!-- CENTER: Conversation -->
  <div class="col-convo">
    <div class="convo-header" id="convo-header">
      <span class="convo-name" id="convo-name" style="color:var(--text4)">
        Select an agent →
      </span>
    </div>
    <div id="convo-body" style="flex:1;display:flex;flex-direction:column;overflow:hidden;">
      <div class="empty-convo" id="empty-convo">
        <div class="icon">⬡</div>
        <p>Select an agent on the left<br>to start a conversation.</p>
      </div>
      <div class="messages" id="messages" style="display:none"></div>
    </div>
    <div class="compose" id="compose" style="display:none">
      <textarea id="msg-input" placeholder="Write a sealed message…"
                oninput="onInput()"></textarea>
      <div class="compose-actions">
        <span class="char-count" id="char-count">0 / 2000 B</span>
        <span class="send-error" id="send-error"></span>
        <button class="send-btn" id="send-btn" disabled onclick="sendMsg()">
          Send →
        </button>
      </div>
    </div>
  </div>

  <!-- RIGHT: Inbox -->
  <div class="col-inbox">
    <div class="col-header">
      Inbox
      <span class="inbox-badge" id="inbox-badge">0</span>
    </div>
    <div class="inbox-list" id="inbox-list"></div>
  </div>

</div>

<script>
const MAX_BYTES = 2000;
let _state = {
  contacts: [],
  activeId: null,
  tor: false,
  sentMap: {},        // contact_id -> [msgs]
  inbox: [],
};

// ── Byte length ──
function byteLen(s) {
  return new TextEncoder().encode(s).length;
}

// ── Char counter ──
function onInput() {
  const v = document.getElementById('msg-input').value;
  const b = byteLen(v);
  const el = document.getElementById('char-count');
  el.textContent = b + ' / 2000 B';
  el.className = 'char-count' + (b > MAX_BYTES ? ' over' : b > MAX_BYTES * .9 ? ' warn' : '');
  updateSendBtn();
}

function updateSendBtn() {
  const btn = document.getElementById('send-btn');
  const msg = (document.getElementById('msg-input').value || '').trim();
  const contact = _state.contacts.find(c => c.id === _state.activeId);
  const ready = _state.tor && contact && contact.configured && msg.length > 0
                && byteLen(msg) <= MAX_BYTES;
  btn.disabled = !ready;
  if (!contact || !contact.configured) {
    btn.title = 'Recipient not configured';
  } else if (!_state.tor) {
    btn.title = 'Tor not detected';
  } else {
    btn.title = '';
  }
}

// ── Contacts ──
function renderContacts() {
  const list = document.getElementById('contacts-list');
  if (_state.contacts.length === 0) {
    list.innerHTML = '<div style="padding:16px 14px;font-size:11px;color:var(--text4)">No contacts configured.<br>Edit ccss_contacts.json</div>';
    return;
  }
  list.innerHTML = _state.contacts.map(c => {
    const initial = c.name.charAt(0).toUpperCase();
    const statusClass = c.configured ? 'green' : 'grey';
    const activeClass = c.id === _state.activeId ? ' active' : '';
    return `<div class="contact-item${activeClass}" onclick="selectContact('${c.id}')">
      <div class="contact-avatar">${initial}</div>
      <div class="contact-info">
        <div class="contact-name">${c.name}</div>
        <div class="contact-desc">${c.description || c.id}</div>
      </div>
      <div class="contact-status"><div class="dot ${statusClass}"></div></div>
    </div>`;
  }).join('');
}

// ── Select contact ──
function selectContact(id) {
  _state.activeId = id;
  const contact = _state.contacts.find(c => c.id === id);
  renderContacts();

  // Update header
  const nameEl = document.getElementById('convo-name');
  nameEl.style.color = '';
  nameEl.textContent = contact ? contact.name : id;

  const header = document.getElementById('convo-header');
  // Remove stale extra spans
  while (header.children.length > 1) header.removeChild(header.lastChild);

  if (contact) {
    if (contact.agent_id) {
      const idSpan = document.createElement('span');
      idSpan.className = 'convo-id';
      idSpan.textContent = contact.agent_id.slice(0, 24) + '…';
      header.appendChild(idSpan);
    }
    if (contact.onion) {
      const onionSpan = document.createElement('span');
      onionSpan.className = 'convo-onion';
      onionSpan.textContent = contact.onion;
      header.appendChild(onionSpan);
    }
  }

  // Show compose
  document.getElementById('empty-convo').style.display = 'none';
  document.getElementById('messages').style.display = 'flex';
  document.getElementById('compose').style.display = '';

  renderMessages(id);
  updateSendBtn();
}

// ── Messages ──
function renderMessages(contactId) {
  const msgs = _state.sentMap[contactId] || [];
  const el = document.getElementById('messages');
  if (msgs.length === 0) {
    el.innerHTML = '<div class="empty-convo" style="flex:1"><div class="icon">⬡</div><p>No messages sent yet.</p></div>';
    return;
  }
  el.innerHTML = msgs.map(m => {
    const dt = new Date(m.sent_at).toLocaleString();
    const receipt = m.receipt_token ? m.receipt_token.slice(0,12) + '…' : '';
    return `<div class="msg-row">
      <div>
        <div class="msg-bubble">${escHtml(m.message)}</div>
        <div class="msg-meta">${dt}</div>
        ${receipt ? `<div class="msg-receipt">receipt: ${receipt}</div>` : ''}
      </div>
    </div>`;
  }).join('');
  el.scrollTop = el.scrollHeight;
}

// ── Inbox ──
function renderInbox() {
  const list = document.getElementById('inbox-list');
  const badge = document.getElementById('inbox-badge');
  const items = _state.inbox;

  badge.textContent = items.length;
  badge.className = 'inbox-badge' + (items.length > 0 ? ' show' : '');

  if (items.length === 0) {
    list.innerHTML = `<div class="inbox-empty">
      <div class="icon">⬡</div>
      <p>No sealed envelopes<br>received yet.</p>
    </div>`;
    return;
  }
  list.innerHTML = items.map(env => {
    const dt = new Date(env.received_at).toLocaleString();
    const sizeClass = env.size_ok ? 'ok' : 'warn';
    const sizeText  = env.size_ok ? env.size_bytes + 'B ✓' : env.size_bytes + 'B ⚠';
    return `<div class="envelope-card">
      <div class="env-top">
        <span class="sealed-badge">sealed</span>
        <span class="env-token">${env.token_short}</span>
      </div>
      <div class="env-time">${dt}</div>
      <div class="env-size ${sizeClass}">${sizeText} — H013 outer</div>
    </div>`;
  }).join('');
}

// ── Status bar ──
function renderStatus(s) {
  const torDot   = document.getElementById('tor-dot');
  const torLabel = document.getElementById('tor-label');
  const pill     = document.getElementById('onion-pill');
  const short    = document.getElementById('onion-short');

  _state.tor = s.tor.ok;
  torDot.className = 'dot ' + (s.tor.ok ? 'green pulse' : 'red');
  torLabel.textContent = s.tor.ok ? 'Tor' : 'Tor offline';

  // Show onion of active contact
  const active = _state.contacts.find(c => c.id === _state.activeId);
  if (active && active.onion) {
    pill.style.display = 'flex';
    short.textContent = active.onion.slice(0, 16) + '…';
  } else {
    pill.style.display = 'none';
  }
  updateSendBtn();
}

// ── Send ──
async function sendMsg() {
  const btn = document.getElementById('send-btn');
  const errEl = document.getElementById('send-error');
  const input = document.getElementById('msg-input');
  const msg = input.value.trim();
  errEl.style.display = 'none';
  btn.disabled = true;
  btn.textContent = 'Sealing…';

  try {
    const r = await fetch('/api/send', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ contact_id: _state.activeId, message: msg }),
    });
    const data = await r.json();
    if (data.ok) {
      input.value = '';
      document.getElementById('char-count').textContent = '0 / 2000 B';
      document.getElementById('char-count').className = 'char-count';
      await fetchSent();
      renderMessages(_state.activeId);
    } else {
      errEl.textContent = data.error || 'send failed';
      errEl.style.display = 'inline';
    }
  } catch (e) {
    errEl.textContent = 'Network error: ' + e.message;
    errEl.style.display = 'inline';
  } finally {
    btn.textContent = 'Send →';
    updateSendBtn();
  }
}

// ── Fetch helpers ──
async function fetchStatus() {
  const r = await fetch('/api/status');
  const s = await r.json();
  _state.contacts = s.contacts;
  renderStatus(s);
  renderContacts();
}

async function fetchSent() {
  if (!_state.activeId) return;
  const r = await fetch('/api/sent?id=' + encodeURIComponent(_state.activeId));
  const data = await r.json();
  _state.sentMap[_state.activeId] = data.messages || [];
}

async function fetchInbox() {
  const r = await fetch('/api/inbox');
  const data = await r.json();
  _state.inbox = data.envelopes || [];
  renderInbox();
}

async function refresh() {
  await fetchStatus();
  await fetchInbox();
  if (_state.activeId) {
    await fetchSent();
    renderMessages(_state.activeId);
  }
}

// ── Escape ──
function escHtml(s) {
  return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')
          .replace(/"/g,'&quot;').replace(/\\n/g,'<br>');
}

setInterval(refresh, 5000);
refresh();
</script>
</body>
</html>
"""


# ---------------------------------------------------------------------------
# Handler
# ---------------------------------------------------------------------------

def _make_handler(
    contacts_path: Path,
    inbox_path: Path,
    sent_dir: Path,
) -> type[http.server.BaseHTTPRequestHandler]:

    class ChatHandler(http.server.BaseHTTPRequestHandler):
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
            qs = self.path[len(path)+1:] if "?" in self.path else ""

            if path in ("/", "/index.html"):
                self._send(200, "text/html; charset=utf-8", _HTML.encode())

            elif path == "/api/status":
                self._json(200, {
                    "tor":      _check_tor(),
                    "contacts": _load_contacts(contacts_path),
                })

            elif path == "/api/inbox":
                self._json(200, {"envelopes": _inbox_entries(inbox_path)})

            elif path == "/api/sent":
                # ?id=<contact_id>
                contact_id = ""
                for part in qs.split("&"):
                    if part.startswith("id="):
                        contact_id = part[3:]
                msgs = _sent_for(sent_dir, contact_id) if contact_id else []
                self._json(200, {"messages": msgs})

            else:
                self._json(404, {"error": "not_found"})

        def do_POST(self) -> None:
            if self.path != "/api/send":
                self._json(404, {"error": "not_found"})
                return

            try:
                length = int(self.headers.get("Content-Length", "0"))
                payload = json.loads(self.rfile.read(min(length, 65536)))
            except Exception as exc:
                self._json(400, {"ok": False, "error": f"bad request: {exc}"})
                return

            contact_id = payload.get("contact_id", "")
            message    = payload.get("message", "")

            if not isinstance(message, str) or not message.strip():
                self._json(400, {"ok": False, "error": "message required"})
                return
            if len(message.encode("utf-8")) > _MAX_MESSAGE_BYTES:
                self._json(400, {"ok": False, "error": "message exceeds 2000 bytes"})
                return

            # Find contact
            contacts = _load_contacts(contacts_path)
            contact = next((c for c in contacts if c["id"] == contact_id), None)
            if not contact or not contact.get("configured"):
                self._json(503, {"ok": False, "error": "contact not configured"})
                return

            # Read pubkey from contacts file (not exposed to JS)
            try:
                raw = json.loads(contacts_path.read_text())
                raw_contact = next(c for c in raw if c["id"] == contact_id)
                pubkey_hex = raw_contact["ccss_recipient_pubkey"]
                onion = raw_contact["ccss_contact_onion"]
            except Exception as exc:
                self._json(500, {"ok": False, "error": f"config read error: {exc}"})
                return

            # Encrypt
            try:
                _root = Path(__file__).resolve().parent.parent.parent
                if str(_root) not in sys.path:
                    sys.path.insert(0, str(_root))
                from tools.ccss_send.ccss_encrypt import seal_message
                envelope = seal_message(message, pubkey_hex)
            except Exception as exc:
                self._json(500, {"ok": False, "error": f"encryption failed: {exc}"})
                return

            # Send via Tor
            try:
                result = _socks5_send(onion, envelope)
            except Exception as exc:
                self._json(502, {"ok": False, "error": f"tor delivery failed: {exc}"})
                return

            if result["http_status"] == 200:
                receipt = result["body"].get("receipt_token", "")
                _save_sent(sent_dir, contact_id, message, receipt)
                self._json(200, {"ok": True, "receipt_token": receipt})
            else:
                self._json(502, {
                    "ok": False,
                    "error": f"relay returned {result['http_status']}",
                })

    return ChatHandler


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="CCSS three-column chat UI.")
    parser.add_argument("--contacts", type=Path, default=_DEFAULT_CONTACTS)
    parser.add_argument("--inbox",    type=Path, default=_DEFAULT_INBOX)
    parser.add_argument("--sent",     type=Path, default=_DEFAULT_SENT)
    parser.add_argument("--port",     type=int,  default=_DEFAULT_PORT)
    args = parser.parse_args(argv)

    handler = _make_handler(
        args.contacts.resolve(),
        args.inbox.resolve(),
        args.sent.resolve(),
    )
    server = http.server.HTTPServer((_LOOPBACK, args.port), handler)

    url = f"http://{_LOOPBACK}:{args.port}"
    print(f"CCSS chat UI:  {url}", flush=True)
    print(f"  Contacts: {args.contacts}", flush=True)
    print(f"  Inbox:    {args.inbox}", flush=True)
    print(f"  Sent:     {args.sent}", flush=True)
    print(f"Open {url} in your browser.", flush=True)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nCCSS chat UI: stopped.", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
