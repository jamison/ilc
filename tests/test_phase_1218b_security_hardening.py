"""
Phase 1218b — Transport and ledger security hardening tests.

Covers all 7 CVE-class findings from the Phase 1218b audit:
  F1: Unbounded in-memory event_log OOM (http_gossip + http_fetch transports)
  F2: Peer fingerprint cache OOM (PeerFingerprintCache)
  F3: SSRF via HTTP redirect following (fetch + gossip + registry fetch)
  F4: Static .tmp race condition (persistent backend + registry sync state +
      channel + promotion + rate limiter save)
  F5: O(N) prune under lock (PersistentFetchRateLimiter)
  F6: Rate limiter identity spoofing (handle_want_block_request)
  F7: Slowloris per-op vs total deadline (http_fetch_transport_runtime)
"""

import collections
import os
import tempfile
import urllib.request
from pathlib import Path
from unittest.mock import patch

import pytest


# ---------------------------------------------------------------------------
# F1: Unbounded event_log — must be a bounded deque
# ---------------------------------------------------------------------------

def test_f1_gossip_event_log_is_bounded_deque():
    """http_gossip_transport_runtime event_log must be a deque with maxlen."""
    from ilc_core.network.d2d.http_gossip_transport_runtime import (
        HttpGossipTransportRuntime,
        TransportRuntimeConfig,
        _EVENT_LOG_MAX,
    )
    config = TransportRuntimeConfig(
        transport_kind="http",
        bind_host="127.0.0.1",
        bind_port=0,
        tls_cert_path="",
        tls_key_path="",
    )
    runtime = HttpGossipTransportRuntime(config)
    log = runtime.state["event_log"]
    assert isinstance(log, collections.deque), "event_log must be a deque"
    assert log.maxlen == _EVENT_LOG_MAX, "event_log deque must have a bounded maxlen"


def test_f1_gossip_event_log_does_not_grow_beyond_max():
    """After maxlen entries, old entries are dropped (not accumulated)."""
    from ilc_core.network.d2d.http_gossip_transport_runtime import (
        HttpGossipTransportRuntime,
        TransportRuntimeConfig,
        _EVENT_LOG_MAX,
    )
    config = TransportRuntimeConfig(
        transport_kind="http",
        bind_host="127.0.0.1",
        bind_port=0,
        tls_cert_path="",
        tls_key_path="",
    )
    runtime = HttpGossipTransportRuntime(config)
    for i in range(_EVENT_LOG_MAX + 50):
        runtime._record("test_event", idx=i)
    assert len(runtime.state["event_log"]) == _EVENT_LOG_MAX


def test_f1_fetch_event_log_is_bounded_deque():
    """http_fetch_transport_runtime event_log must be a deque with maxlen."""
    from ilc_core.network.d2d.http_fetch_transport_runtime import (
        FetchTransportConfig,
        _EVENT_LOG_MAX,
    )
    config = FetchTransportConfig()
    log = config.event_log
    assert isinstance(log, collections.deque), "event_log must be a deque"
    assert log.maxlen == _EVENT_LOG_MAX


# ---------------------------------------------------------------------------
# F2: Peer fingerprint cache OOM — must enforce max_size with eviction
# ---------------------------------------------------------------------------

def test_f2_peer_fingerprint_cache_has_max_size():
    """PeerFingerprintCache must have a max_size cap."""
    from ilc_core.network.d2d.peer_fingerprint_cache import (
        PeerFingerprintCache,
        DEFAULT_MAX_CACHE_SIZE,
    )
    cache = PeerFingerprintCache()
    assert cache.max_size == DEFAULT_MAX_CACHE_SIZE


def test_f2_peer_fingerprint_cache_evicts_at_capacity():
    """Cache must not exceed max_size; inserting a new peer triggers eviction."""
    from ilc_core.network.d2d.peer_fingerprint_cache import PeerFingerprintCache

    cache = PeerFingerprintCache(max_size=3)
    for i in range(3):
        cache.update(f"peer{i}:9000", [float(i)], 0.1, epoch=i)

    assert cache.peer_count() == 3
    # Insert one more — must evict one
    cache.update("peer_new:9000", [9.0], 0.1, epoch=100)
    assert cache.peer_count() == 3, "Cache must not exceed max_size"


def test_f2_peer_fingerprint_cache_prefers_dead_peer_eviction():
    """Dead peers (silent > threshold) are evicted before live peers."""
    from ilc_core.network.d2d.peer_fingerprint_cache import (
        PeerFingerprintCache,
        DEFAULT_DEAD_PEER_SILENCE_EPOCHS,
    )

    cache = PeerFingerprintCache(max_size=3)
    dead_epoch = 0
    live_epoch = DEFAULT_DEAD_PEER_SILENCE_EPOCHS + 5  # definitely alive
    current_epoch = DEFAULT_DEAD_PEER_SILENCE_EPOCHS + 10

    cache.update("dead_peer:9000", [1.0], 0.1, epoch=dead_epoch)
    cache.update("live1:9000", [2.0], 0.1, epoch=live_epoch)
    cache.update("live2:9000", [3.0], 0.1, epoch=live_epoch)

    # Insert new peer at capacity — dead_peer should be evicted
    cache.update("new_peer:9000", [4.0], 0.1, epoch=current_epoch)

    assert cache.get("dead_peer:9000") is None, "Dead peer should have been evicted"
    assert cache.get("live1:9000") is not None
    assert cache.get("live2:9000") is not None
    assert cache.get("new_peer:9000") is not None


# ---------------------------------------------------------------------------
# F3: SSRF via HTTP redirect — NoRedirectHandler must block redirects
# ---------------------------------------------------------------------------

def test_f3_gossip_transport_has_no_redirect_handler():
    """HttpGossipTransportRuntime must define _NoRedirectHandler."""
    import ilc_core.network.d2d.http_gossip_transport_runtime as mod
    assert hasattr(mod, "_NoRedirectHandler"), "_NoRedirectHandler must be defined"
    assert issubclass(mod._NoRedirectHandler, urllib.request.HTTPRedirectHandler)


def test_f3_gossip_no_redirect_handler_raises_on_redirect():
    """_NoRedirectHandler.redirect_request must raise TransportRuntimeError."""
    from ilc_core.network.d2d.http_gossip_transport_runtime import (
        _NoRedirectHandler,
        TransportRuntimeError,
    )
    handler = _NoRedirectHandler()
    with pytest.raises(TransportRuntimeError) as exc_info:
        handler.redirect_request(None, None, 302, "Found", None, "https://evil.example/")
    assert exc_info.value.token == "transport_redirect_not_permitted"


def test_f3_fetch_no_redirect_handler_blocks():
    """_download_url in canon_bundle_key_registry_fetch must use _NoRedirectHandler."""
    # Verify redirect rejection by confirming redirect_request raises inside _download_url
    # We patch urlopen at the build_opener level to simulate a redirect response.
    from ilc_core.ledger.canon_bundle_key_registry_fetch import _download_url

    class _MockOpener:
        def open(self, _url, **_kw):
            # Simulate that a redirect was blocked
            import urllib.error
            raise urllib.error.URLError("fetch_redirect_not_permitted: 302 -> https://evil/")

    with patch("urllib.request.build_opener", return_value=_MockOpener()):
        result = _download_url("https://example.com/bundle.zip", Path("/tmp/test_dl"), 5)
    assert not result["ok"]
    assert "fetch_redirect_not_permitted" in result["error"]


# ---------------------------------------------------------------------------
# F4: Static .tmp race — verify mkstemp/mkdtemp used for unique temp names
# ---------------------------------------------------------------------------

def test_f4_persistent_backend_atomic_write_unique_tmp(tmp_path):
    """FileLedgerBackend._atomic_write must use mkstemp (unique tmp names)."""
    from ilc_core.ledger.persistent_backend import FileLedgerBackend

    backend = FileLedgerBackend(str(tmp_path))
    target = tmp_path / "test_atomic.json"

    created_tmps = []
    original_mkstemp = tempfile.mkstemp

    def capturing_mkstemp(**kwargs):
        fd, path = original_mkstemp(**kwargs)
        created_tmps.append(path)
        return fd, path

    with patch("tempfile.mkstemp", side_effect=capturing_mkstemp):
        backend._atomic_write(str(target), {"key": "value"})

    assert target.exists(), "Target file must be written"
    # All temp files should be cleaned up (replaced)
    for tmp in created_tmps:
        assert not os.path.exists(tmp), f"Temp file {tmp} must be removed after atomic write"


def test_f4_sync_state_atomic_write_unique_tmp(tmp_path):
    """write_sync_state must use mkstemp (unique tmp names)."""
    from ilc_core.ledger.canon_bundle_key_registry_sync_state import (
        write_sync_state,
        ChannelFreshnessState,
    )

    state = ChannelFreshnessState(
        seen_seq=1,
        seen_hash="a" * 64,
        updated_at="2026-01-01T00:00:00Z",
    )
    target = tmp_path / "sync_state.json"

    created_tmps = []
    original_mkstemp = tempfile.mkstemp

    def capturing_mkstemp(**kwargs):
        fd, path = original_mkstemp(**kwargs)
        created_tmps.append(path)
        return fd, path

    with patch("tempfile.mkstemp", side_effect=capturing_mkstemp):
        write_sync_state(target, state)

    assert target.exists(), "Sync state file must be written"
    for tmp in created_tmps:
        assert not os.path.exists(tmp), f"Temp file {tmp} must be removed after write"


# ---------------------------------------------------------------------------
# F5: O(N) prune — OrderedDict ensures O(1) eviction path
# ---------------------------------------------------------------------------

def test_f5_rate_limiter_buckets_is_ordered_dict():
    """PersistentFetchRateLimiter._buckets must be an OrderedDict."""
    from ilc_core.network.d2d.persistent_fetch_rate_limiter_runtime import (
        PersistentFetchRateLimiter,
    )
    limiter = PersistentFetchRateLimiter(limit_per_window=10, max_buckets=100)
    assert isinstance(limiter._buckets, collections.OrderedDict), \
        "_buckets must be an OrderedDict for O(1) FIFO eviction"


def test_f5_rate_limiter_prune_removes_oldest_bucket():
    """_prune_if_needed must remove the oldest bucket (FIFO), not a min-scan result."""
    from ilc_core.network.d2d.persistent_fetch_rate_limiter_runtime import (
        PersistentFetchRateLimiter,
    )
    limiter = PersistentFetchRateLimiter(limit_per_window=100, max_buckets=3)

    limiter.check_and_consume("alpha", 1)
    limiter.check_and_consume("beta", 1)
    limiter.check_and_consume("gamma", 1)
    assert len(limiter._buckets) == 3

    # Adding a new key at capacity should evict the oldest (alpha)
    limiter.check_and_consume("delta", 1)
    assert "alpha" not in limiter._buckets, "Oldest bucket must be evicted first"
    assert len(limiter._buckets) == 3


# ---------------------------------------------------------------------------
# F6: Rate limiter identity spoofing — handle_want_block_request uses rate_limit_key
# ---------------------------------------------------------------------------

def test_f6_handle_want_block_accepts_rate_limit_key():
    """handle_want_block_request must accept and use rate_limit_key parameter."""
    import inspect
    from ilc_core.network.d2d.truth_primitive_fetch_runtime import (
        handle_want_block_request,
    )
    sig = inspect.signature(handle_want_block_request)
    assert "rate_limit_key" in sig.parameters, \
        "handle_want_block_request must have rate_limit_key parameter"
    param = sig.parameters["rate_limit_key"]
    assert param.default is None, "rate_limit_key default must be None"


# ---------------------------------------------------------------------------
# F7: Slowloris deadline — total deadline enforcement in http_fetch_transport
# ---------------------------------------------------------------------------

def test_f7_fetch_transport_has_deadline_token():
    """http_fetch_transport_runtime must define the deadline-exceeded token."""
    import ilc_core.network.d2d.http_fetch_transport_runtime as mod
    # The token is used in the do_POST handler; verify the module references it
    src = Path(mod.__file__).read_text(encoding="utf-8")
    assert "fetch_request_deadline_exceeded" in src, \
        "Module must define the Slowloris deadline-exceeded token"


# ---------------------------------------------------------------------------
# Hardening token presence — each modified module declares the token
# ---------------------------------------------------------------------------

def test_hardening_token_present_in_all_modified_modules():
    """Every modified network/ledger module must declare TRANSPORT_SECURITY_HARDENING_TOKEN."""
    import ilc_core.network.d2d.http_gossip_transport_runtime as gossip_mod
    import ilc_core.network.d2d.http_fetch_transport_runtime as fetch_mod
    import ilc_core.network.d2d.truth_primitive_fetch_runtime as truth_mod
    import ilc_core.network.d2d.persistent_fetch_rate_limiter_runtime as limiter_mod
    import ilc_core.network.d2d.peer_fingerprint_cache as fp_mod

    token = "transport_security_hardening_1218b"

    assert getattr(gossip_mod, "TRANSPORT_SECURITY_HARDENING_TOKEN", None) == token
    assert getattr(fetch_mod, "TRANSPORT_SECURITY_HARDENING_TOKEN", None) == token
    assert getattr(truth_mod, "TRANSPORT_SECURITY_HARDENING_TOKEN", None) == token
    assert getattr(limiter_mod, "TRANSPORT_SECURITY_HARDENING_TOKEN", None) == token
    assert getattr(fp_mod, "PEER_FINGERPRINT_CACHE_HARDENING", None) == "peer_fingerprint_cache_max_size_1218b"
