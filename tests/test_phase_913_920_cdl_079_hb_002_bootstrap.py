"""Phase 913–920 — CDL-079 HB-002 bootstrap distribution protocol tests.

Covers all 8 hard pass conditions from the Window 913-920 sequence lock:
  1. bootstrap_fetch_runtime.py exists
  2. BOOTSTRAP_FETCH_RUNTIME_VERSION and CDL-079/077/073 dep tokens
  3. fetch_bootstrap_bundle() fetches bundle via CDL-077 WANT-HAVE/WANT-BLOCK
  4. verify_bootstrap_bundle_signature() verifies ML-DSA-65 signature
  5. node_startup_runtime.py patched: bootstrap mode via env vars
  6. Static peer config fallback preserved
  7. No DHT, no swarm discovery in source
  8. CDL-079 opened in CDL master log
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

from ilc_core.network.d2d.bootstrap_fetch_runtime import (
    BOOTSTRAP_FETCH_RUNTIME_VERSION,
    CDL_073_DEPENDENCY,
    CDL_077_DEPENDENCY,
    CDL_079_DEPENDENCY,
    BootstrapBundleError,
    extract_peer_endpoints,
    fetch_bootstrap_bundle,
    validate_bootstrap_bundle_schema,
    verify_bootstrap_bundle_signature,
)
from ilc_core.node.node_startup_runtime import (
    CDL_079_DEPENDENCY as STARTUP_CDL_079_DEPENDENCY,
    BootstrapError,
    bootstrap_node_startup,
    detect_bootstrap_mode,
)

PHASE_917_COMMIT_SUBJECT = "feat(g8): phase 914-917 cdl-079 hb-002 bootstrap distribution protocol"
RUNTIME_PATH = Path("ilc_core/network/d2d/bootstrap_fetch_runtime.py")
CDL_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")

# Minimal valid bootstrap bundle (signature verification bypassed in tests)
GENESIS_PUBKEY = "aabbcc" * 20   # fake pubkey hex
VALID_BUNDLE = {
    "schema_version": "bootstrap_bundle_v1",
    "bundle_cid": "bafyreiabc001",
    "genesis_cid": "bafyreigenesis",
    "peers": [
        {"endpoint": "https://peer1.ilc.example", "node_id": "bafyreipeer1"},
        {"endpoint": "https://peer2.ilc.example", "node_id": "bafyreipeer2"},
    ],
    "signed_by": GENESIS_PUBKEY,
    "signature": "ddeeff" * 20,
    "cdl_version": "cdl_079_bootstrap_bundle_v1",
}


class _RejectingOqsSignature:
    def __init__(self, _algorithm: str) -> None:
        pass

    def verify(
        self,
        _signed_bytes: bytes,
        _sig_bytes: bytes,
        _pubkey_bytes: bytes,
    ) -> bool:
        return False


class _RejectingOqsModule:
    Signature = _RejectingOqsSignature


class _CapturingOqsSignature:
    captured_signed_bytes: bytes | None = None

    def __init__(self, _algorithm: str) -> None:
        pass

    def verify(
        self,
        signed_bytes: bytes,
        _sig_bytes: bytes,
        _pubkey_bytes: bytes,
    ) -> bool:
        type(self).captured_signed_bytes = signed_bytes
        return True


class _CapturingOqsModule:
    Signature = _CapturingOqsSignature


def _install_rejecting_oqs(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setitem(sys.modules, "oqs", _RejectingOqsModule())


# ---------------------------------------------------------------------------
# Group 1: Module existence + tokens
# ---------------------------------------------------------------------------


def test_bootstrap_fetch_runtime_exists():
    assert RUNTIME_PATH.exists(), f"Missing: {RUNTIME_PATH}"


def test_bootstrap_fetch_runtime_version_token():
    assert BOOTSTRAP_FETCH_RUNTIME_VERSION == "bootstrap_fetch_runtime_915.v0.1"


def test_cdl_079_dependency_token():
    assert CDL_079_DEPENDENCY == "cdl_079_hb_002_bootstrap_distribution.v0.1"


def test_cdl_077_dependency_token_in_bootstrap_runtime():
    assert CDL_077_DEPENDENCY == "cdl_077_want_have_want_block_fetch.v0.1"


def test_cdl_073_dependency_token_in_bootstrap_runtime():
    assert CDL_073_DEPENDENCY == "cdl_073_homoiconic_bootstrap_schema_ratified.v0.1"


def test_cdl_079_dependency_in_node_startup():
    assert STARTUP_CDL_079_DEPENDENCY == "cdl_079_hb_002_bootstrap_distribution.v0.1"


# ---------------------------------------------------------------------------
# Group 2: fetch_bootstrap_bundle — CDL-077 wiring
# ---------------------------------------------------------------------------


def test_fetch_bootstrap_bundle_success():
    """200 path: WANT-HAVE → positive, WANT-BLOCK → returns bundle dict."""
    bundle_bytes = json.dumps(VALID_BUNDLE, sort_keys=True).encode()
    with patch("ilc_core.network.d2d.bootstrap_fetch_runtime.want_have") as mock_wh, \
         patch("ilc_core.network.d2d.bootstrap_fetch_runtime.want_block") as mock_wb:
        mock_wh.return_value = {"have": True, "node_id": "bafyreiabc001"}
        mock_wb.return_value = bundle_bytes
        result = fetch_bootstrap_bundle("https://seed.ilc.example", "bafyreiabc001")
    assert result is not None
    assert result["bundle_cid"] == "bafyreiabc001"
    mock_wh.assert_called_once_with("bafyreiabc001", "https://seed.ilc.example")
    mock_wb.assert_called_once_with("bafyreiabc001", "https://seed.ilc.example")


def test_fetch_bootstrap_bundle_not_found_returns_none():
    """WANT-HAVE says no → returns None without calling WANT-BLOCK."""
    with patch("ilc_core.network.d2d.bootstrap_fetch_runtime.want_have") as mock_wh, \
         patch("ilc_core.network.d2d.bootstrap_fetch_runtime.want_block") as mock_wb:
        mock_wh.return_value = {"have": False, "node_id": "bafyreiabc001"}
        result = fetch_bootstrap_bundle("https://seed.ilc.example", "bafyreiabc001")
    assert result is None
    mock_wb.assert_not_called()


def test_fetch_bootstrap_bundle_want_block_none_returns_none():
    """WANT-HAVE positive but WANT-BLOCK returns None → returns None."""
    with patch("ilc_core.network.d2d.bootstrap_fetch_runtime.want_have") as mock_wh, \
         patch("ilc_core.network.d2d.bootstrap_fetch_runtime.want_block") as mock_wb:
        mock_wh.return_value = {"have": True, "node_id": "bafyreiabc001"}
        mock_wb.return_value = None
        result = fetch_bootstrap_bundle("https://seed.ilc.example", "bafyreiabc001")
    assert result is None


def test_fetch_bootstrap_bundle_invalid_json_raises():
    """WANT-BLOCK returns non-JSON → raises BootstrapBundleError."""
    with patch("ilc_core.network.d2d.bootstrap_fetch_runtime.want_have") as mock_wh, \
         patch("ilc_core.network.d2d.bootstrap_fetch_runtime.want_block") as mock_wb:
        mock_wh.return_value = {"have": True, "node_id": "bafyreiabc001"}
        mock_wb.return_value = b"not json {{{"
        with pytest.raises(BootstrapBundleError) as exc_info:
            fetch_bootstrap_bundle("https://seed.ilc.example", "bafyreiabc001")
    assert "bootstrap_bundle_invalid_json" in exc_info.value.token


def test_fetch_bootstrap_bundle_rejects_non_finite_json_constant():
    """WANT-BLOCK JSON NaN/Infinity tokens are rejected at the wire parser."""
    with patch("ilc_core.network.d2d.bootstrap_fetch_runtime.want_have") as mock_wh, \
         patch("ilc_core.network.d2d.bootstrap_fetch_runtime.want_block") as mock_wb:
        mock_wh.return_value = {"have": True, "node_id": "bafyreiabc001"}
        mock_wb.return_value = b'{"schema_version":NaN}'
        with pytest.raises(BootstrapBundleError) as exc_info:
            fetch_bootstrap_bundle("https://seed.ilc.example", "bafyreiabc001")
    assert exc_info.value.token == "bootstrap_bundle_float_not_allowed"


def test_fetch_bootstrap_bundle_bad_seed_peer_raises():
    """Empty seed peer endpoint raises BootstrapBundleError."""
    with pytest.raises(BootstrapBundleError):
        fetch_bootstrap_bundle("", "bafyreiabc001")


def test_fetch_bootstrap_bundle_bad_bundle_cid_raises():
    """Empty bundle CID raises BootstrapBundleError."""
    with pytest.raises(BootstrapBundleError):
        fetch_bootstrap_bundle("https://seed.ilc.example", "")


# ---------------------------------------------------------------------------
# Group 3: verify_bootstrap_bundle_signature
# ---------------------------------------------------------------------------


def test_verify_signature_wrong_signed_by_returns_false():
    """signed_by does not match genesis_authority_pubkey → False."""
    bundle = dict(VALID_BUNDLE)
    bundle["signed_by"] = "000000" * 20  # different key
    result = verify_bootstrap_bundle_signature(bundle, GENESIS_PUBKEY)
    assert result is False


def test_verify_signature_wrong_schema_version_returns_false():
    bundle = dict(VALID_BUNDLE)
    bundle["schema_version"] = "bootstrap_bundle_v0"
    result = verify_bootstrap_bundle_signature(bundle, GENESIS_PUBKEY)
    assert result is False


def test_verify_signature_wrong_cdl_version_returns_false():
    bundle = dict(VALID_BUNDLE)
    bundle["cdl_version"] = "cdl_078_relay_incentive"
    result = verify_bootstrap_bundle_signature(bundle, GENESIS_PUBKEY)
    assert result is False


def test_verify_signature_missing_signature_field_returns_false():
    bundle = {k: v for k, v in VALID_BUNDLE.items() if k != "signature"}
    result = verify_bootstrap_bundle_signature(bundle, GENESIS_PUBKEY)
    assert result is False


def test_verify_signature_not_a_dict_returns_false():
    result = verify_bootstrap_bundle_signature("not a dict", GENESIS_PUBKEY)  # type: ignore
    assert result is False


def test_verify_signature_env_bypass_not_accepted(monkeypatch):
    """ILC_BOOTSTRAP_SKIP_SIG_VERIFY must not bypass production signature checks."""
    monkeypatch.setenv("ILC_BOOTSTRAP_SKIP_SIG_VERIFY", "1")
    _install_rejecting_oqs(monkeypatch)
    result = verify_bootstrap_bundle_signature(VALID_BUNDLE, GENESIS_PUBKEY)
    assert result is False


def test_verify_signature_uses_compact_canonical_json(monkeypatch):
    _CapturingOqsSignature.captured_signed_bytes = None
    monkeypatch.setitem(sys.modules, "oqs", _CapturingOqsModule())

    result = verify_bootstrap_bundle_signature(VALID_BUNDLE, GENESIS_PUBKEY)

    payload = {k: v for k, v in VALID_BUNDLE.items() if k != "signature"}
    expected = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("utf-8")
    assert result is True
    assert _CapturingOqsSignature.captured_signed_bytes == expected


def test_verify_signature_uses_ascii_escaped_canonical_json(monkeypatch):
    _CapturingOqsSignature.captured_signed_bytes = None
    monkeypatch.setitem(sys.modules, "oqs", _CapturingOqsModule())
    bundle = dict(VALID_BUNDLE)
    bundle["description"] = "naive-cafe-\u00e9"

    result = verify_bootstrap_bundle_signature(bundle, GENESIS_PUBKEY)

    payload = {k: v for k, v in bundle.items() if k != "signature"}
    expected = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("utf-8")
    assert result is True
    assert _CapturingOqsSignature.captured_signed_bytes == expected
    assert b"\\u00e9" in expected


# ---------------------------------------------------------------------------
# Group 4: extract_peer_endpoints
# ---------------------------------------------------------------------------


def test_extract_peer_endpoints_returns_valid():
    endpoints = extract_peer_endpoints(VALID_BUNDLE)
    assert len(endpoints) == 2
    assert all(ep.startswith("https://") for ep in endpoints)


def test_extract_peer_endpoints_skips_invalid():
    bundle = dict(VALID_BUNDLE)
    bundle["peers"] = [
        {"endpoint": "https://valid.ilc.example", "node_id": "bafyreiok"},
        {"endpoint": "not-https", "node_id": "bafyreibad"},
        {"endpoint": "", "node_id": "bafyreiempty"},
        "not_a_dict",
        {"no_endpoint": True},
    ]
    endpoints = extract_peer_endpoints(bundle)
    assert len(endpoints) == 1
    assert "https://valid.ilc.example" in endpoints[0]


def test_extract_peer_endpoints_empty_peers():
    bundle = dict(VALID_BUNDLE)
    bundle["peers"] = []
    assert extract_peer_endpoints(bundle) == []


def test_extract_peer_endpoints_not_a_dict_returns_empty():
    assert extract_peer_endpoints("bad input") == []  # type: ignore


# ---------------------------------------------------------------------------
# Group 5: validate_bootstrap_bundle_schema
# ---------------------------------------------------------------------------


def test_validate_bundle_schema_valid():
    assert validate_bootstrap_bundle_schema(VALID_BUNDLE) is True


def test_validate_bundle_schema_missing_field():
    bundle = {k: v for k, v in VALID_BUNDLE.items() if k != "genesis_cid"}
    assert validate_bootstrap_bundle_schema(bundle) is False


@pytest.mark.parametrize(
    "peers",
    [
        "not-a-list",
        {"endpoint": "https://peer.ilc.example", "node_id": "node"},
        None,
        [1],
        [{"endpoint": " https://peer.ilc.example", "node_id": "node"}],
        [{"endpoint": "https://peer.ilc.example", "node_id": ""}],
    ],
)
def test_validate_bundle_schema_rejects_malformed_peer_list(peers):
    bundle = dict(VALID_BUNDLE)
    bundle["peers"] = peers
    assert validate_bootstrap_bundle_schema(bundle) is False


# ---------------------------------------------------------------------------
# Group 6: node_startup_runtime bootstrap mode
# ---------------------------------------------------------------------------


def test_detect_bootstrap_mode_both_set(monkeypatch):
    monkeypatch.setenv("ILC_BOOTSTRAP_SEED_PEER", "https://seed.ilc.example")
    monkeypatch.setenv("ILC_BOOTSTRAP_BUNDLE_CID", "bafyreiabc001")
    result = detect_bootstrap_mode()
    assert result == ("https://seed.ilc.example", "bafyreiabc001")


def test_detect_bootstrap_mode_neither_set(monkeypatch):
    monkeypatch.delenv("ILC_BOOTSTRAP_SEED_PEER", raising=False)
    monkeypatch.delenv("ILC_BOOTSTRAP_BUNDLE_CID", raising=False)
    result = detect_bootstrap_mode()
    assert result is None


def test_detect_bootstrap_mode_only_seed_raises(monkeypatch):
    monkeypatch.setenv("ILC_BOOTSTRAP_SEED_PEER", "https://seed.ilc.example")
    monkeypatch.delenv("ILC_BOOTSTRAP_BUNDLE_CID", raising=False)
    with pytest.raises(ValueError) as exc_info:
        detect_bootstrap_mode()
    assert "bootstrap_mode_requires_both_seed_peer_and_bundle_cid" in str(exc_info.value)


def test_detect_bootstrap_mode_only_cid_raises(monkeypatch):
    monkeypatch.delenv("ILC_BOOTSTRAP_SEED_PEER", raising=False)
    monkeypatch.setenv("ILC_BOOTSTRAP_BUNDLE_CID", "bafyreiabc001")
    with pytest.raises(ValueError) as exc_info:
        detect_bootstrap_mode()
    assert "bootstrap_mode_requires_both_seed_peer_and_bundle_cid" in str(exc_info.value)


def test_bootstrap_node_startup_success(monkeypatch):
    """Full bootstrap path: fetch → verify → extract → return endpoints."""
    with patch("ilc_core.network.d2d.bootstrap_fetch_runtime.want_have") as mock_wh, \
         patch("ilc_core.network.d2d.bootstrap_fetch_runtime.want_block") as mock_wb, \
         patch(
             "ilc_core.network.d2d.bootstrap_fetch_runtime.verify_bootstrap_bundle_signature"
         ) as mock_verify:
        mock_wh.return_value = {"have": True, "node_id": "bafyreiabc001"}
        mock_wb.return_value = json.dumps(VALID_BUNDLE, sort_keys=True).encode()
        mock_verify.return_value = True
        endpoints = bootstrap_node_startup(
            "https://seed.ilc.example",
            "bafyreiabc001",
            GENESIS_PUBKEY,
        )
    assert len(endpoints) == 2
    mock_verify.assert_called_once()


def test_bootstrap_node_startup_bundle_not_found_raises(monkeypatch):
    """Bundle not found → BootstrapError."""
    with patch("ilc_core.network.d2d.bootstrap_fetch_runtime.want_have") as mock_wh:
        mock_wh.return_value = {"have": False, "node_id": "bafyreiabc001"}
        with pytest.raises(BootstrapError) as exc_info:
            bootstrap_node_startup("https://seed.ilc.example", "bafyreiabc001", GENESIS_PUBKEY)
    assert "bootstrap_bundle_not_found" in exc_info.value.token


def test_bootstrap_node_startup_signature_invalid_raises():
    """Valid bundle but wrong key → BootstrapError (signature invalid)."""
    with patch("ilc_core.network.d2d.bootstrap_fetch_runtime.want_have") as mock_wh, \
         patch("ilc_core.network.d2d.bootstrap_fetch_runtime.want_block") as mock_wb:
        mock_wh.return_value = {"have": True, "node_id": "bafyreiabc001"}
        mock_wb.return_value = json.dumps(VALID_BUNDLE, sort_keys=True).encode()
        with pytest.raises(BootstrapError) as exc_info:
            bootstrap_node_startup(
                "https://seed.ilc.example",
                "bafyreiabc001",
                "wrong_key_hex",  # doesn't match GENESIS_PUBKEY
            )
    assert "bootstrap_bundle_signature_invalid" in exc_info.value.token


# ---------------------------------------------------------------------------
# Group 7: No DHT/swarm in source
# ---------------------------------------------------------------------------


def test_no_dht_in_bootstrap_fetch_runtime():
    # Scan non-comment, non-docstring lines for active DHT/swarm usage
    source = RUNTIME_PATH.read_text(encoding="utf-8")
    # Strip docstrings (triple-quoted) and comment lines before scanning
    import re as _re
    stripped = _re.sub(r'""".*?"""', '', source, flags=_re.DOTALL)
    stripped = _re.sub(r"'''.*?'''", '', stripped, flags=_re.DOTALL)
    code_lines = [l for l in stripped.splitlines() if not l.strip().startswith('#')]
    code_only = '\n'.join(code_lines).lower()
    forbidden = ["kademlia", "swarm_discovery", "mdns", "announce_peer",
                 "import dht", "from dht"]
    for term in forbidden:
        assert term not in code_only, (
            f"Forbidden term '{term}' found in bootstrap_fetch_runtime.py code"
        )


# ---------------------------------------------------------------------------
# Group 8: CDL-079 in master log
# ---------------------------------------------------------------------------


def test_cdl_079_row_in_master_log():
    text = CDL_LOG_PATH.read_text(encoding="utf-8")
    assert "CDL-079" in text, "CDL-079 row not found in CDL master log"
    assert "opened_phase: 914" in text


# ---------------------------------------------------------------------------
# Group 9: Commit scope guard
# ---------------------------------------------------------------------------


def _resolve_phase_917_commit_ref() -> str | None:
    result = subprocess.run(
        ["git", "log", "--oneline", "--all"],
        capture_output=True, text=True, check=False,
    )
    for line in result.stdout.splitlines():
        if PHASE_917_COMMIT_SUBJECT in line:
            return line.split()[0]
    return None


def test_phase_917_commit_scope_guard():
    ref = _resolve_phase_917_commit_ref()
    if ref is None:
        pytest.skip("Phase 917 commit not yet present")

    result = subprocess.run(
        ["git", "diff-tree", "--no-commit-id", "-r", "--name-only", ref],
        capture_output=True, text=True, check=False,
    )
    changed = [f.strip() for f in result.stdout.splitlines() if f.strip()]
    allowed_prefixes = ("ilc_core/network/d2d/", "ilc_core/node/", "tests/", "docs/")
    forbidden = [f for f in changed if not any(f.startswith(p) for p in allowed_prefixes)]
    assert not forbidden, f"Phase 917 commit touches out-of-scope files: {forbidden}"
