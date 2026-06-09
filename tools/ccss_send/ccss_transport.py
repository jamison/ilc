#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
"""CCSS transport abstraction — send a sealed envelope to any reachable endpoint.

Three transports, same interface:

  TorTransport    — SOCKS5 → Tor hidden service (current default)
  DirectTransport — raw TCP to host:port (no Tor; for directly-reachable peers)
  D2dTransport    — ILC D2d peer network routing by agent_id (future; stub)

Callers:

    transport, endpoint = resolve_transport(contact_dict)
    receipt = transport.send(envelope_bytes, endpoint)

contact_dict fields (from ccss_contacts.json):
    ccss_peer_endpoint   host:port   → DirectTransport  (fastest; try first)
    ccss_contact_onion   xxx.onion   → TorTransport     (anonymous fallback)
    agent_id             <hex>       → D2dTransport      (future; D2d must be live)

Priority: peer endpoint > onion > D2d (stub).
"""

from __future__ import annotations

import json
import socket
import time
from abc import ABC, abstractmethod
from typing import Any

_TOR_HOST = "127.0.0.1"
_TOR_PORT = 9050
_OUTER_ENVELOPE_BYTES = 4156

# ---------------------------------------------------------------------------
# Base
# ---------------------------------------------------------------------------

class Transport(ABC):
    """Send a sealed CCSS-003 envelope.  Raise on failure."""

    @abstractmethod
    def send(self, envelope: bytes, endpoint: str) -> dict[str, Any]:
        """Deliver envelope to endpoint.  Returns receipt dict from relay.

        Args:
            envelope: exactly 4156-byte CCSS-003 outer envelope
            endpoint: transport-specific address string
        """

    @property
    @abstractmethod
    def name(self) -> str:
        """Short human-readable transport name."""


# ---------------------------------------------------------------------------
# Tor SOCKS5 transport
# ---------------------------------------------------------------------------

class TorTransport(Transport):
    """Send via Tor SOCKS5 proxy to a .onion hidden service.

    endpoint format: "exampleonionaddress.onion"
    Tor must be running locally on 127.0.0.1:9050.
    """

    name = "tor"

    def __init__(self, socks_host: str = _TOR_HOST, socks_port: int = _TOR_PORT,
                 timeout: int = 30) -> None:
        self._host    = socks_host
        self._port    = socks_port
        self._timeout = timeout

    def send(self, envelope: bytes, endpoint: str) -> dict[str, Any]:
        if len(envelope) != _OUTER_ENVELOPE_BYTES:
            raise ValueError(
                f"envelope must be {_OUTER_ENVELOPE_BYTES} bytes, got {len(envelope)}"
            )
        return _socks5_post(endpoint, "/submit", envelope,
                            self._host, self._port, self._timeout)


def _socks5_post(onion: str, path: str, body: bytes,
                 socks_host: str, socks_port: int, timeout: int) -> dict[str, Any]:
    host_b = onion.encode()
    with socket.create_connection((socks_host, socks_port), timeout=timeout) as s:
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
    code = int(raw.split(b"\r\n")[0].split(b" ")[1])
    if code not in (200, 202):
        raise RuntimeError(f"relay returned HTTP {code}")
    return json.loads(resp_body)


# ---------------------------------------------------------------------------
# Direct TCP transport (no Tor)
# ---------------------------------------------------------------------------

class DirectTransport(Transport):
    """Send directly to a TCP peer receiver — no Tor required.

    endpoint format: "host:port"  e.g. "192.168.1.5:9001" or "agent.example.com:9001"

    The peer receiver (ccss_peer_receiver.py) accepts exactly 4156-byte envelopes
    over a raw TCP connection and returns a JSON receipt line.

    Since the envelope is already end-to-end encrypted to the recipient's pubkey,
    the transport itself does not need to be anonymous — just authenticated enough
    that you know you are connecting to the right host (DNS/TLS at the network layer,
    or Noise handshake in a future iteration).

    Use case: agents with direct IP reachability (LAN, VPN, fixed server).
    This is the Option C bootstrap path before the D2d gossip layer is live.
    """

    name = "direct"

    def __init__(self, timeout: int = 15) -> None:
        self._timeout = timeout

    def send(self, envelope: bytes, endpoint: str) -> dict[str, Any]:
        if len(envelope) != _OUTER_ENVELOPE_BYTES:
            raise ValueError(
                f"envelope must be {_OUTER_ENVELOPE_BYTES} bytes, got {len(envelope)}"
            )
        host, _, port_s = endpoint.rpartition(":")
        if not host or not port_s:
            raise ValueError(f"invalid direct endpoint (expected host:port): {endpoint!r}")
        port = int(port_s)

        with socket.create_connection((host, port), timeout=self._timeout) as s:
            # Wire format: 4156 raw bytes, then read JSON receipt line
            s.sendall(envelope)
            s.shutdown(socket.SHUT_WR)   # signal EOF so receiver knows we're done
            raw = b""
            while True:
                chunk = s.recv(512)
                if not chunk:
                    break
                raw += chunk

        if not raw:
            raise RuntimeError("peer receiver returned empty response")
        return json.loads(raw.decode().strip())


# ---------------------------------------------------------------------------
# D2d transport stub (future)
# ---------------------------------------------------------------------------

class D2dTransport(Transport):
    """Route via ILC D2d peer network by agent_id.

    NOT YET LIVE.  The ILC D2d gossip layer must be running with a live
    peer network before this transport can deliver envelopes.

    When implemented, the flow will be:
      1. Wrap CCSS-003 envelope in a D2d CCSS_ENVELOPE message type
      2. Route by recipient agent_id through the gossip layer
      3. Receiving peer unwraps and delivers to local inbox
      4. No per-agent Tor hidden service required

    endpoint format: agent_id hex string (32 bytes)
    See: docs/specs/ccss_d2d_transport_spec_v0.1.md
    """

    name = "d2d"

    def send(self, envelope: bytes, endpoint: str) -> dict[str, Any]:
        raise NotImplementedError(
            "D2d peer routing is not yet live. "
            "Configure ccss_peer_endpoint (host:port) for direct transport "
            "or ccss_contact_onion for Tor transport. "
            "See docs/specs/ccss_d2d_transport_spec_v0.1.md for the Option C roadmap."
        )


# ---------------------------------------------------------------------------
# Transport resolution
# ---------------------------------------------------------------------------

def resolve_transport(contact: dict[str, Any]) -> tuple[Transport, str]:
    """Choose the best available transport for a contact.

    Priority
    --------
    1. DirectTransport — if ccss_peer_endpoint is set and not a placeholder
    2. TorTransport    — if ccss_contact_onion is set and not a placeholder
    3. D2dTransport    — if agent_id is set (stub; raises NotImplementedError)

    Returns
    -------
    (transport_instance, endpoint_string)

    Raises
    ------
    ValueError  if no reachable endpoint is configured
    """
    def _live(val: str) -> bool:
        return bool(val) and "PLACEHOLDER" not in val.upper()

    peer_ep  = contact.get("ccss_peer_endpoint", "")
    onion    = contact.get("ccss_contact_onion", "")
    agent_id = contact.get("agent_id", "")

    if _live(peer_ep):
        return DirectTransport(), peer_ep
    if _live(onion):
        return TorTransport(), onion
    if _live(agent_id):
        # Future path — returns stub that raises on send
        return D2dTransport(), agent_id

    raise ValueError(
        f"contact {contact.get('id', '?')!r}: no reachable endpoint configured "
        "(set ccss_peer_endpoint or ccss_contact_onion)"
    )


__all__ = [
    "Transport",
    "TorTransport",
    "DirectTransport",
    "D2dTransport",
    "resolve_transport",
]
