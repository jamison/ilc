# SPDX-License-Identifier: AGPL-3.0-only
"""Phase 894 — CDL-076 truth primitive announcement gossip runtime.

Implements the "soft push-signal" leg of the CDL-036 dissemination contract for
truth primitive nodes persisted under CDL-075.

A lightweight announcement {node_id, primitive, agent_id, epoch, cdl_version} is
gossiped via the CDL-061 envelope to peers configured in ILC_D2D_GOSSIP_PEERS after
a confirmed CDL-075 persist.  Full-payload push is explicitly excluded per CDL-036.
The CID-addressed pull fetch leg is deferred to CDL-077.

Activation:
    ILC_D2D_GOSSIP_PEERS — comma-separated HTTPS peer endpoints.  If absent or
    empty, gossip is silently skipped and the receipt reflects "deferred".

This module does not start or bind an HTTP server.  It makes outbound-only HTTP
POST calls using the CDL-061 header contract.
"""

from __future__ import annotations

import json
import os
import ssl
import urllib.request
from typing import Any

from ilc_core.network.d2d import gossip_transport
from ilc_core.network.d2d.gossip_peer_registry import validate_peer_endpoint

TRUTH_PRIMITIVE_GOSSIP_RUNTIME_VERSION = "truth_primitive_gossip_runtime_894.v0.1"
CDL_076_DEPENDENCY = "cdl_076_truth_primitive_announcement_gossip.v0.1"
CDL_061_DEPENDENCY = "cdl_061_ratified_561.v0.1"
CDL_075_DEPENDENCY = "cdl_075_truth_primitive_graph_persistence.v0.1"
TRUTH_PRIMITIVE_GOSSIP_TYPE = "truth_primitive_announced"
TRUTH_PRIMITIVE_GOSSIP_CHANNEL = (
    "cid:0760000000000000000000000000000000000000000000000000000000000000"
)
_GOSSIP_TIMEOUT_SECONDS = 2.0
_UNSIGNED_SIGNATURE = "UNSIGNED"
_GOSSIP_TLS_INSECURE_ENV = "ILC_D2D_INSECURE_SKIP_TLS_VERIFY"

if gossip_transport.GOSSIP_TRANSPORT_RUNTIME_VERSION != "gossip_transport_runtime_558.v0.1":
    raise RuntimeError(
        f"truth_primitive_gossip_dep_chain_mismatch: "
        f"gossip_transport={gossip_transport.GOSSIP_TRANSPORT_RUNTIME_VERSION!r}"
    )


class GossipAnnouncementError(Exception):
    """Typed error for gossip announcement failures."""

    def __init__(self, token: str, message: str) -> None:
        super().__init__(message)
        self.token = token
        self.message = message


class _NoRedirectHandler(urllib.request.HTTPRedirectHandler):
    """Reject redirects so malicious peers cannot retarget gossip POSTs."""

    def redirect_request(
        self,
        _req: urllib.request.Request,
        _fp: object,
        code: int,
        _msg: str,
        _headers: object,
        newurl: str,
    ) -> None:
        raise GossipAnnouncementError(
            "truth_primitive_gossip_redirect_not_permitted",
            f"peer returned redirect {code} to {newurl}",
        )


def _load_peers() -> list[str]:
    """Read and validate ILC_D2D_GOSSIP_PEERS env var.

    Returns a list of validated HTTPS peer endpoints, or an empty list if the
    env var is absent or empty.
    """
    raw = os.environ.get("ILC_D2D_GOSSIP_PEERS", "").strip()
    if not raw:
        return []
    peers = []
    for part in raw.split(","):
        part = part.strip()
        if not part:
            continue
        peers.append(validate_peer_endpoint(part))
    return peers


def _build_announcement_payload(write_receipt: dict[str, Any], envelope: dict[str, Any]) -> bytes:
    """Build the CDL-076 announcement payload.

    Payload is exactly {node_id, primitive, agent_id, epoch, cdl_version}.
    No full node record content — soft push-signal only per CDL-036.
    """
    payload = {
        "node_id": write_receipt["node_id"],
        "primitive": write_receipt["primitive"],
        "agent_id": envelope["agent_id"],
        "epoch": envelope["epoch"],
        "cdl_version": CDL_076_DEPENDENCY,
    }
    return json.dumps(payload, sort_keys=True).encode("utf-8")


def _client_ssl_context() -> ssl.SSLContext:
    """Outbound TLS context. Verification is disabled only by explicit testbed opt-out."""
    context = ssl.create_default_context()
    if os.environ.get(_GOSSIP_TLS_INSECURE_ENV) == "1":
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
    return context


def _send_to_peer(peer_endpoint: str, payload_bytes: bytes, epoch: int) -> bool:
    """Send a single CDL-061 gossip announcement to one peer.

    Returns True on HTTP 2xx, False on any error.  Errors are swallowed to
    ensure one failing peer does not block remaining peers.
    """
    headers = gossip_transport.build_gossip_headers(
        gossip_type=TRUTH_PRIMITIVE_GOSSIP_TYPE,
        channel=TRUTH_PRIMITIVE_GOSSIP_CHANNEL,
        epoch=epoch,
        hop_count=gossip_transport.HOP_COUNT_SINGLE,
        signature=_UNSIGNED_SIGNATURE,
        content_type="application/json",
    )
    request_path = gossip_transport.gossip_request_path(TRUTH_PRIMITIVE_GOSSIP_TYPE)
    request = urllib.request.Request(
        url=f"{peer_endpoint}{request_path}",
        data=payload_bytes,
        headers=headers,
        method="POST",
    )
    try:
        opener = urllib.request.build_opener(
            _NoRedirectHandler,
            urllib.request.HTTPSHandler(context=_client_ssl_context()),
        )
        with opener.open(request, timeout=_GOSSIP_TIMEOUT_SECONDS) as response:
            return 200 <= int(response.getcode()) < 300
    except Exception:  # noqa: BLE001
        return False


def announce_truth_primitive(
    write_receipt: dict[str, Any],
    envelope: dict[str, Any],
) -> dict[str, Any]:
    """Gossip a lightweight truth primitive announcement to configured peers.

    Fires after write_truth_primitive_result() confirms CDL-075 persistence.
    Uses CDL-061 gossip headers over direct HTTPS POST per peer.

    Args:
        write_receipt: dict returned by write_truth_primitive_result() — must
            contain at least {node_id, primitive}.
        envelope: CDL-073 submission envelope — provides agent_id and epoch.

    Returns:
        Receipt dict: {gossip_delivery, peers_attempted, peers_succeeded, version}
    """
    node_id = write_receipt.get("node_id")
    if not node_id:
        # Edge-only primitives produce no node; nothing to announce.
        return {
            "gossip_delivery": "deferred — no node_id (edge-only primitive)",
            "peers_attempted": 0,
            "peers_succeeded": 0,
            "version": TRUTH_PRIMITIVE_GOSSIP_RUNTIME_VERSION,
        }

    peers = _load_peers()
    if not peers:
        return {
            "gossip_delivery": "deferred — gossip peers not configured",
            "peers_attempted": 0,
            "peers_succeeded": 0,
            "version": TRUTH_PRIMITIVE_GOSSIP_RUNTIME_VERSION,
        }

    epoch = int(envelope.get("epoch", 0))
    payload_bytes = _build_announcement_payload(write_receipt, envelope)

    succeeded = 0
    for peer in peers:
        if _send_to_peer(peer, payload_bytes, epoch):
            succeeded += 1

    delivery_status = (
        f"announced to {succeeded}/{len(peers)} peers"
        if succeeded > 0
        else f"announcement failed — 0/{len(peers)} peers reachable"
    )

    return {
        "gossip_delivery": delivery_status,
        "peers_attempted": len(peers),
        "peers_succeeded": succeeded,
        "version": TRUTH_PRIMITIVE_GOSSIP_RUNTIME_VERSION,
    }
