"""Phase 901–905 — CDL-077 WANT-HAVE/WANT-BLOCK two-phase fetch tests.

Covers all 10 hard pass conditions from the Window 899-905 sequence lock:
  1. truth_primitive_fetch_runtime.py exists
  2. TRUTH_PRIMITIVE_FETCH_RUNTIME_VERSION and CDL-077/075/042 dep tokens
  3. WANT_HAVE_PATH and WANT_BLOCK_PATH constants declared
  4. Client want_have() returns {have: bool, node_id: str}
  5. Client want_block() returns bytes | None
  6. Server handle_want_have_request() responds with {have: bool, node_id}
  7. Server handle_want_block_request() → bytes / 404 / 429 / 503 / 400
  8. FetchRateLimiter with WANT_BLOCK_RATE_LIMIT_PER_MINUTE; over-limit → token
  9. http_fetch_transport_runtime.py exists; server starts and handles fetch paths
  10. CDL-077 opened in CDL master log (ratification verified at Phase 904)
"""

from __future__ import annotations

import json
import os
import subprocess
import time
import urllib.request
import ssl
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from ilc_core.network.d2d.truth_primitive_fetch_runtime import (
    CDL_042_DEPENDENCY,
    CDL_075_DEPENDENCY,
    CDL_077_DEPENDENCY,
    TRUTH_PRIMITIVE_FETCH_RUNTIME_VERSION,
    WANT_BLOCK_PATH,
    WANT_BLOCK_RATE_LIMIT_PER_MINUTE,
    WANT_HAVE_PATH,
    FetchRateLimitError,
    FetchRateLimiter,
    FetchTransportError,
    fetch_truth_primitive,
    handle_want_block_request,
    handle_want_have_request,
    want_block,
    want_have,
)
from ilc_core.network.d2d.http_fetch_transport_runtime import (
    HTTP_FETCH_TRANSPORT_RUNTIME_VERSION,
    CDL_077_DEPENDENCY as HTTP_CDL_077_DEPENDENCY,
    FETCH_RUNTIME_DEPENDENCY,
    FetchTransportConfig,
    HttpFetchTransportRuntime,
)

PHASE_903_COMMIT_SUBJECT = "feat(g8): phase 899-903 cdl-077 want-have want-block fetch protocol"
FETCH_RUNTIME_PATH = Path("ilc_core/network/d2d/truth_primitive_fetch_runtime.py")
HTTP_TRANSPORT_PATH = Path("ilc_core/network/d2d/http_fetch_transport_runtime.py")
CDL_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def mock_store_with_node():
    """A mock store that has exactly one node."""
    store = MagicMock()
    record = {
        "schema": "ilc.truth_primitive_node@v1",
        "primitive": "assert.truth",
        "node_id": "bafytest001",
        "agent_id": "agent-001",
        "epoch": 1,
    }
    store.get_node.side_effect = lambda nid: record if nid == "bafytest001" else None
    return store


@pytest.fixture()
def mock_store_empty():
    """A mock store with no nodes."""
    store = MagicMock()
    store.get_node.return_value = None
    return store


@pytest.fixture()
def rate_limiter_default():
    return FetchRateLimiter()


# ---------------------------------------------------------------------------
# Group 1: Module existence + tokens
# ---------------------------------------------------------------------------


def test_fetch_runtime_module_exists():
    assert FETCH_RUNTIME_PATH.exists(), f"Missing: {FETCH_RUNTIME_PATH}"


def test_http_fetch_transport_module_exists():
    assert HTTP_TRANSPORT_PATH.exists(), f"Missing: {HTTP_TRANSPORT_PATH}"


def test_fetch_runtime_version_token():
    assert TRUTH_PRIMITIVE_FETCH_RUNTIME_VERSION == "truth_primitive_fetch_runtime_901.v0.1"


def test_http_transport_version_token():
    assert HTTP_FETCH_TRANSPORT_RUNTIME_VERSION == "http_fetch_transport_runtime_902.v0.1"


def test_cdl_077_dependency_token_in_fetch_runtime():
    assert CDL_077_DEPENDENCY == "cdl_077_want_have_want_block_fetch.v0.1"


def test_cdl_077_dependency_token_in_http_transport():
    assert HTTP_CDL_077_DEPENDENCY == "cdl_077_want_have_want_block_fetch.v0.1"


def test_fetch_runtime_dependency_in_http_transport():
    assert FETCH_RUNTIME_DEPENDENCY == "truth_primitive_fetch_runtime_901.v0.1"


def test_cdl_075_dependency_token():
    assert CDL_075_DEPENDENCY == "cdl_075_truth_primitive_graph_persistence.v0.1"


def test_cdl_042_dependency_token():
    assert CDL_042_DEPENDENCY == "cdl_042_ratified_407.v0.1"


# ---------------------------------------------------------------------------
# Group 2: Path constants
# ---------------------------------------------------------------------------


def test_want_have_path_constant():
    assert WANT_HAVE_PATH == "/fetch/want-have"


def test_want_block_path_constant():
    assert WANT_BLOCK_PATH == "/fetch/want-block"


def test_want_block_rate_limit_constant():
    assert isinstance(WANT_BLOCK_RATE_LIMIT_PER_MINUTE, int)
    assert WANT_BLOCK_RATE_LIMIT_PER_MINUTE >= 1


# ---------------------------------------------------------------------------
# Group 3: FetchRateLimiter
# ---------------------------------------------------------------------------


def test_rate_limiter_allows_under_limit():
    limiter = FetchRateLimiter(limit_per_minute=3)
    assert limiter.check_and_consume("agent-a") is True
    assert limiter.check_and_consume("agent-a") is True
    assert limiter.check_and_consume("agent-a") is True


def test_rate_limiter_blocks_over_limit():
    limiter = FetchRateLimiter(limit_per_minute=2)
    limiter.check_and_consume("agent-b")
    limiter.check_and_consume("agent-b")
    assert limiter.check_and_consume("agent-b") is False


def test_rate_limiter_identities_are_independent():
    limiter = FetchRateLimiter(limit_per_minute=1)
    limiter.check_and_consume("agent-x")
    # agent-x is blocked, agent-y is not
    assert limiter.check_and_consume("agent-x") is False
    assert limiter.check_and_consume("agent-y") is True


# ---------------------------------------------------------------------------
# Group 4: Server — handle_want_have_request
# ---------------------------------------------------------------------------


def test_want_have_handler_node_found(mock_store_with_node):
    body = json.dumps({"node_id": "bafytest001", "requester_id": "agent-001"}).encode()
    status, resp = handle_want_have_request(body, mock_store_with_node)
    assert status == 200
    parsed = json.loads(resp)
    assert parsed["have"] is True
    assert parsed["node_id"] == "bafytest001"


def test_want_have_handler_node_absent(mock_store_empty):
    body = json.dumps({"node_id": "bafymissing", "requester_id": "agent-001"}).encode()
    status, resp = handle_want_have_request(body, mock_store_empty)
    assert status == 200
    assert json.loads(resp)["have"] is False


def test_want_have_handler_store_none():
    body = json.dumps({"node_id": "bafytest001", "requester_id": "agent-001"}).encode()
    status, resp = handle_want_have_request(body, None)
    assert status == 200
    assert json.loads(resp)["have"] is False


def test_want_have_handler_malformed_body():
    status, resp = handle_want_have_request(b"not json", None)
    assert status == 400
    assert "token" in json.loads(resp)


def test_want_have_handler_missing_node_id():
    body = json.dumps({"requester_id": "agent-001"}).encode()
    status, resp = handle_want_have_request(body, None)
    assert status == 400
    assert json.loads(resp)["token"] == "fetch_request_node_id_missing"


# ---------------------------------------------------------------------------
# Group 5: Server — handle_want_block_request
# ---------------------------------------------------------------------------


def test_want_block_handler_node_found(mock_store_with_node, rate_limiter_default):
    body = json.dumps({"node_id": "bafytest001", "requester_id": "agent-001"}).encode()
    status, resp = handle_want_block_request(body, mock_store_with_node, rate_limiter_default)
    assert status == 200
    parsed = json.loads(resp)
    assert parsed["primitive"] == "assert.truth"


def test_want_block_handler_node_absent(mock_store_empty, rate_limiter_default):
    body = json.dumps({"node_id": "bafymissing", "requester_id": "agent-001"}).encode()
    status, resp = handle_want_block_request(body, mock_store_empty, rate_limiter_default)
    assert status == 404
    assert json.loads(resp)["token"] == "fetch_node_not_found"


def test_want_block_handler_rate_limited(mock_store_with_node):
    limiter = FetchRateLimiter(limit_per_minute=1)
    body = json.dumps({"node_id": "bafytest001", "requester_id": "agent-throttled"}).encode()
    # First request allowed
    handle_want_block_request(body, mock_store_with_node, limiter)
    # Second request blocked
    status, resp = handle_want_block_request(body, mock_store_with_node, limiter)
    assert status == 429
    assert json.loads(resp)["token"] == "fetch_rate_limit_exceeded"


def test_want_block_handler_store_none(rate_limiter_default):
    body = json.dumps({"node_id": "bafytest001", "requester_id": "agent-001"}).encode()
    status, resp = handle_want_block_request(body, None, rate_limiter_default)
    assert status == 503
    assert json.loads(resp)["token"] == "fetch_store_not_configured"


def test_want_block_handler_malformed_body(rate_limiter_default):
    status, resp = handle_want_block_request(b"{invalid}", None, rate_limiter_default)
    assert status == 400


# ---------------------------------------------------------------------------
# Group 6: HTTP transport server — starts and routes correctly
# ---------------------------------------------------------------------------


def test_http_fetch_server_starts_and_stops():
    config = FetchTransportConfig(bind_host="127.0.0.1", bind_port=0, store_path="")
    runtime = HttpFetchTransportRuntime(config)
    runtime.start()
    try:
        assert runtime.state["running"] is True
        assert runtime.state["bound_port"] > 0
    finally:
        runtime.stop()
    assert runtime.state["running"] is False


def test_http_fetch_server_want_have_no_store():
    """WANT-HAVE with no store returns {have: false}."""
    config = FetchTransportConfig(bind_host="127.0.0.1", bind_port=0, store_path="")
    runtime = HttpFetchTransportRuntime(config)
    runtime.start()
    port = runtime.state["bound_port"]
    try:
        body = json.dumps({"node_id": "bafytest001", "requester_id": "agent-001"}).encode()
        req = urllib.request.Request(
            f"http://127.0.0.1:{port}/fetch/want-have",
            data=body,
            method="POST",
            headers={"Content-Type": "application/json", "Content-Length": str(len(body))},
        )
        with urllib.request.urlopen(req, timeout=3) as resp:
            parsed = json.loads(resp.read())
        assert parsed["have"] is False
    finally:
        runtime.stop()


def test_http_fetch_server_unknown_path_returns_404():
    config = FetchTransportConfig(bind_host="127.0.0.1", bind_port=0, store_path="")
    runtime = HttpFetchTransportRuntime(config)
    runtime.start()
    port = runtime.state["bound_port"]
    try:
        body = b"{}"
        req = urllib.request.Request(
            f"http://127.0.0.1:{port}/fetch/unknown",
            data=body,
            method="POST",
            headers={"Content-Type": "application/json", "Content-Length": str(len(body))},
        )
        try:
            urllib.request.urlopen(req, timeout=3)
            assert False, "expected 404"
        except urllib.error.HTTPError as exc:
            assert exc.code == 404
    finally:
        runtime.stop()


def test_http_fetch_server_want_block_no_store_returns_503():
    config = FetchTransportConfig(bind_host="127.0.0.1", bind_port=0, store_path="")
    runtime = HttpFetchTransportRuntime(config)
    runtime.start()
    port = runtime.state["bound_port"]
    try:
        body = json.dumps({"node_id": "bafytest001", "requester_id": "agent-001"}).encode()
        req = urllib.request.Request(
            f"http://127.0.0.1:{port}/fetch/want-block",
            data=body,
            method="POST",
            headers={"Content-Type": "application/json", "Content-Length": str(len(body))},
        )
        try:
            urllib.request.urlopen(req, timeout=3)
            assert False, "expected 503"
        except urllib.error.HTTPError as exc:
            assert exc.code == 503
            assert json.loads(exc.read())["token"] == "fetch_store_not_configured"
    finally:
        runtime.stop()


# ---------------------------------------------------------------------------
# Group 7: Client — fetch_truth_primitive with no peers configured
# ---------------------------------------------------------------------------


def test_fetch_truth_primitive_no_peers_returns_none(monkeypatch):
    monkeypatch.delenv("ILC_D2D_GOSSIP_PEERS", raising=False)
    result = fetch_truth_primitive("bafytest001")
    assert result is None


def test_fetch_truth_primitive_peer_has_node(monkeypatch):
    """Mock want_have to say yes, mock want_block to return bytes."""
    monkeypatch.setenv("ILC_D2D_GOSSIP_PEERS", "https://peer1.example.com")

    def _mock_want_have(_node_id, _peer):
        return {"have": True, "node_id": _node_id}

    def _mock_want_block(_node_id, _peer):
        return b'{"primitive": "assert.truth"}'

    with patch(
        "ilc_core.network.d2d.truth_primitive_fetch_runtime.want_have", _mock_want_have
    ), patch(
        "ilc_core.network.d2d.truth_primitive_fetch_runtime.want_block", _mock_want_block
    ):
        result = fetch_truth_primitive("bafytest001")
    assert result == b'{"primitive": "assert.truth"}'


def test_fetch_truth_primitive_first_peer_no_second_yes(monkeypatch):
    """First peer says have=false, second peer says have=true and returns block."""
    monkeypatch.setenv(
        "ILC_D2D_GOSSIP_PEERS", "https://peer1.example.com,https://peer2.example.com"
    )
    call_count = {"have": 0}

    def _mock_want_have(_node_id, peer):
        call_count["have"] += 1
        return {"have": "peer2" in peer, "node_id": _node_id}

    def _mock_want_block(_node_id, _peer):
        return b'{"primitive": "assert.truth"}'

    with patch(
        "ilc_core.network.d2d.truth_primitive_fetch_runtime.want_have", _mock_want_have
    ), patch(
        "ilc_core.network.d2d.truth_primitive_fetch_runtime.want_block", _mock_want_block
    ):
        result = fetch_truth_primitive("bafytest001")
    assert result == b'{"primitive": "assert.truth"}'
    assert call_count["have"] == 2


# ---------------------------------------------------------------------------
# Group 8: CDL master log — CDL-077 opened
# ---------------------------------------------------------------------------


def test_cdl_077_row_in_master_log():
    text = CDL_LOG_PATH.read_text(encoding="utf-8")
    assert "CDL-077" in text, "CDL-077 row not found in CDL master log"
    assert "WANT-HAVE" in text or "want_have" in text.lower()
    assert "opened_phase: 900" in text


# ---------------------------------------------------------------------------
# Group 9: Commit scope guard — Phase 903 commit
# ---------------------------------------------------------------------------


def _resolve_phase_903_commit_ref() -> str | None:
    result = subprocess.run(
        ["git", "log", "--oneline", "--all"],
        capture_output=True,
        text=True,
        check=False,
    )
    for line in result.stdout.splitlines():
        if PHASE_903_COMMIT_SUBJECT in line:
            return line.split()[0]
    return None


def test_phase_903_commit_scope_guard():
    """Phase 903 commit must only touch d2d/, tests/, and docs/ directories."""
    ref = _resolve_phase_903_commit_ref()
    if ref is None:
        pytest.skip("Phase 903 commit not yet present")

    result = subprocess.run(
        ["git", "diff-tree", "--no-commit-id", "-r", "--name-only", ref],
        capture_output=True,
        text=True,
        check=False,
    )
    changed = [f.strip() for f in result.stdout.splitlines() if f.strip()]
    allowed_prefixes = (
        "ilc_core/network/d2d/",
        "tests/",
        "docs/",
    )
    forbidden = [f for f in changed if not any(f.startswith(p) for p in allowed_prefixes)]
    assert not forbidden, f"Phase 903 commit touches out-of-scope files: {forbidden}"
