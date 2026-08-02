from __future__ import annotations

import json
from decimal import Decimal

import pytest

from ilc_core.ccss import runtime as ccss_runtime
from ilc_core.economics.werner_runtime import (
    compute_degree_centrality,
    compute_flow_budget,
)
from ilc_core.genesis.serving_receipt import (
    MAX_SERVING_RESPONSE_BYTES,
    ServingReceiptError,
    _read_bounded_response,
)
from ilc_core.network.d2d import http_gossip_transport_runtime as http_runtime


class _PartialSocksSocket:
    def __init__(self, response_body: bytes) -> None:
        self._chunks = [
            b"\x05",
            b"\x00",
            b"\x05\x00\x00\x01",
            b"\x7f\x00\x00\x01\x23\x28",
            b"HTTP/1.0 200 OK\r\nContent-Length: "
            + str(len(response_body)).encode("ascii")
            + b"\r\n\r\n"
            + response_body,
            b"",
        ]
        self.sent: list[bytes] = []

    def __enter__(self) -> "_PartialSocksSocket":
        return self

    def __exit__(self, *_args: object) -> None:
        return None

    def sendall(self, payload: bytes) -> None:
        self.sent.append(payload)

    def recv(self, _size: int) -> bytes:
        return self._chunks.pop(0)


class _ChunkedResponse:
    def __init__(self, chunks: list[bytes]) -> None:
        self._chunks = chunks

    def read(self, _size: int) -> bytes:
        if not self._chunks:
            return b""
        return self._chunks.pop(0)


def test_tor_send_handles_partial_socks5_reads(monkeypatch: pytest.MonkeyPatch) -> None:
    fake = _PartialSocksSocket(json.dumps({"status": "accepted"}).encode("utf-8"))
    monkeypatch.setattr(
        ccss_runtime.socket,
        "create_connection",
        lambda *_args, **_kwargs: fake,
    )

    result = ccss_runtime._tor_send(b"x" * 32, "exampleabcdefghijklmnop.onion")

    assert result == {"status": "accepted"}


def test_tor_send_wraps_malformed_json(monkeypatch: pytest.MonkeyPatch) -> None:
    fake = _PartialSocksSocket(b"{not-json")
    monkeypatch.setattr(
        ccss_runtime.socket,
        "create_connection",
        lambda *_args, **_kwargs: fake,
    )

    with pytest.raises(ccss_runtime.CCSSRuntimeError, match="tor_receipt_json_invalid"):
        ccss_runtime._tor_send(b"x" * 32, "exampleabcdefghijklmnop.onion")


def test_werner_flow_budget_quantizes_to_twelve_places() -> None:
    result = compute_flow_budget(
        candidate_priority=Decimal("1.2345678901234"),
        runtime_policy_cap=Decimal("9"),
    )

    assert result == Decimal("1.234567890123")


def test_werner_degree_centrality_rejects_non_string_neighbors() -> None:
    with pytest.raises(ValueError, match="werner_adjacency_neighbor_values_must_be_strings"):
        compute_degree_centrality({"a": ["b", 1], "b": ["a"]})


def test_gossip_signed_context_rejects_oversized_identity_headers() -> None:
    headers = {
        "Content-Type": "application/octet-stream",
        "ILC-Channel": "invite-nullifier",
        "ILC-Epoch": "1",
        "ILC-Gossip-Type": "invite_nullifier",
        "ILC-Hop-Count": "1",
        "ILC-Key-Id": "k" * 257,
        "ILC-Sender-Peer-Id": "peer-a",
    }

    with pytest.raises(ValueError, match="gossip_key_id_too_long"):
        http_runtime._build_gossip_signed_context(headers, b"payload")


def test_serving_response_reader_streams_and_rejects_oversized_response() -> None:
    chunks = [b"a" * (MAX_SERVING_RESPONSE_BYTES // 2), b"b" * (MAX_SERVING_RESPONSE_BYTES // 2 + 1)]

    with pytest.raises(ServingReceiptError, match="serving_receipt_response_too_large"):
        _read_bounded_response(_ChunkedResponse(chunks))
