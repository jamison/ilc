# SPDX-License-Identifier: AGPL-3.0-only
"""Phase 915 — CDL-079 HB-002 bootstrap distribution protocol runtime.

Implements peer-to-peer bootstrap for ILC nodes: a new node with one
operator-provided seed peer endpoint and bootstrap bundle CID can fetch,
verify, and extract peers from a signed bootstrap bundle via CDL-077
WANT-HAVE/WANT-BLOCK — without requiring out-of-band GitHub distribution.

Bootstrap bundle schema (`bootstrap_bundle_v1`):
    {
        "schema_version": "bootstrap_bundle_v1",
        "bundle_cid":    "<CIDv1 of this bundle>",
        "genesis_cid":   "<CIDv1 of genesis record>",
        "peers": [{"endpoint": "https://...", "node_id": "<CIDv1>"}, ...],
        "signed_by":     "<ML-DSA-65 genesis authority pubkey hex>",
        "signature":     "<ML-DSA-65 signature hex>",
        "cdl_version":   "cdl_079_bootstrap_bundle_v1"
    }

Trust chain: genesis_authority_key (CDL-073) → bundle signature → peer list.

Scope:
    - Curated model: explicit-promotion only; no DHT; no swarm discovery.
    - ML-DSA-65 signature verification via oqs (pq crypto library).
    - fetch_bootstrap_bundle() reuses CDL-077 want_have / want_block client.
    - verify_bootstrap_bundle_signature() is best-effort (never raises).
    - extract_peer_endpoints() skips invalid entries silently.
"""

from __future__ import annotations

import json
from typing import Any

from ilc_core.network.d2d.truth_primitive_fetch_runtime import (
    TRUTH_PRIMITIVE_FETCH_RUNTIME_VERSION as _CDL_077_CHECK,
    FetchTransportError,
    want_block,
    want_have,
)

BOOTSTRAP_FETCH_RUNTIME_VERSION = "bootstrap_fetch_runtime_915.v0.1"
CDL_079_DEPENDENCY = "cdl_079_hb_002_bootstrap_distribution.v0.1"
CDL_077_DEPENDENCY = "cdl_077_want_have_want_block_fetch.v0.1"
CDL_073_DEPENDENCY = "cdl_073_homoiconic_bootstrap_schema_ratified.v0.1"

BOOTSTRAP_BUNDLE_SCHEMA_VERSION = "bootstrap_bundle_v1"
BOOTSTRAP_BUNDLE_CDL_VERSION = "cdl_079_bootstrap_bundle_v1"

# Dep-chain guard
if _CDL_077_CHECK != "truth_primitive_fetch_runtime_901.v0.1":
    raise RuntimeError("bootstrap_fetch_runtime_cdl_077_dep_mismatch")


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------


class BootstrapBundleError(Exception):
    """Bootstrap bundle fetch or verification failure."""

    def __init__(self, token: str, detail: str = "") -> None:
        super().__init__(detail or token)
        self.token = token


# ---------------------------------------------------------------------------
# Core functions
# ---------------------------------------------------------------------------


def fetch_bootstrap_bundle(
    seed_peer_endpoint: str,
    bundle_cid: str,
) -> dict[str, Any] | None:
    """Fetch the bootstrap bundle from a seed peer via CDL-077 WANT-BLOCK.

    Protocol:
        1. WANT-HAVE probe: seed_peer_endpoint + /fetch/want-have
        2. If peer has bundle: WANT-BLOCK: seed_peer_endpoint + /fetch/want-block
        3. Parse JSON response → return bundle dict

    Args:
        seed_peer_endpoint: Normalized HTTPS endpoint of the seed peer.
        bundle_cid:         CIDv1 of the bootstrap bundle.

    Returns:
        Parsed bundle dict if found and valid JSON, None if peer reports 404.

    Raises:
        FetchTransportError: On network or protocol failure.
        BootstrapBundleError: If response is not a valid JSON object.
    """
    if not isinstance(seed_peer_endpoint, str) or not seed_peer_endpoint.strip():
        raise BootstrapBundleError("bootstrap_invalid_seed_peer_endpoint")
    if not isinstance(bundle_cid, str) or not bundle_cid.strip():
        raise BootstrapBundleError("bootstrap_invalid_bundle_cid")

    # WANT-HAVE probe
    try:
        have_resp = want_have(bundle_cid, seed_peer_endpoint)
    except FetchTransportError:
        raise

    if not have_resp.get("have"):
        return None

    # WANT-BLOCK fetch
    raw = want_block(bundle_cid, seed_peer_endpoint)
    if raw is None:
        return None

    try:
        parsed = json.loads(raw, parse_constant=_reject_json_constant)
    except (json.JSONDecodeError, ValueError) as exc:
        raise BootstrapBundleError(
            "bootstrap_bundle_invalid_json",
            f"bundle_cid={bundle_cid}: {exc}",
        ) from exc

    if not isinstance(parsed, dict):
        raise BootstrapBundleError(
            "bootstrap_bundle_not_object",
            f"bundle_cid={bundle_cid}: expected dict, got {type(parsed).__name__}",
        )

    return parsed


def verify_bootstrap_bundle_signature(
    bundle: dict[str, Any],
    genesis_authority_pubkey_hex: str,
) -> bool:
    """Verify the ML-DSA-65 signature on a bootstrap bundle.

    Signed payload (canonical form):
        payload = {k: v for k, v in bundle.items() if k != "signature"}
        signed_bytes = json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
            allow_nan=False,
        ).encode("utf-8")

    The `signed_by` field must match `genesis_authority_pubkey_hex`.

    Best-effort: returns False on any error rather than raising.

    Args:
        bundle:                       Parsed bundle dict.
        genesis_authority_pubkey_hex: ML-DSA-65 genesis authority public key (hex).

    Returns:
        True if signature valid and signed_by matches; False otherwise.
    """
    try:
        if not isinstance(bundle, dict):
            return False
        if not isinstance(genesis_authority_pubkey_hex, str):
            return False

        schema_version = bundle.get("schema_version")
        if schema_version != BOOTSTRAP_BUNDLE_SCHEMA_VERSION:
            return False

        cdl_version = bundle.get("cdl_version")
        if cdl_version != BOOTSTRAP_BUNDLE_CDL_VERSION:
            return False

        signed_by = bundle.get("signed_by")
        if not isinstance(signed_by, str) or not signed_by.strip():
            return False

        signature_hex = bundle.get("signature")
        if not isinstance(signature_hex, str) or not signature_hex.strip():
            return False

        # signed_by must match the genesis authority key
        if signed_by != genesis_authority_pubkey_hex:
            return False

        # Reconstruct signed payload (exclude signature field)
        payload = {k: v for k, v in bundle.items() if k != "signature"}
        signed_bytes = json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8")

        # ML-DSA-65 signature verification via oqs. Some oqs Python builds try
        # to install liboqs at import time and may raise SystemExit; fail closed.
        try:
            import oqs  # type: ignore[import]
        except (ImportError, RuntimeError, SystemExit):
            return False

        try:
            sig_bytes = bytes.fromhex(signature_hex)
            pubkey_bytes = bytes.fromhex(genesis_authority_pubkey_hex)
            verifier = oqs.Signature("ML-DSA-65")
            return bool(verifier.verify(signed_bytes, sig_bytes, pubkey_bytes))
        except (RuntimeError, TypeError, ValueError):
            return False

    except Exception:  # noqa: BLE001
        return False  # best-effort — never propagate


def _reject_json_constant(value: str) -> None:
    raise BootstrapBundleError(
        "bootstrap_bundle_float_not_allowed",
        f"non-finite JSON constant rejected: {value}",
    )


def extract_peer_endpoints(bundle: dict[str, Any]) -> list[str]:
    """Extract normalized HTTPS peer endpoints from a verified bootstrap bundle.

    Skips invalid entries silently (wrong type, non-HTTPS, missing field).

    Args:
        bundle: Verified bootstrap bundle dict.

    Returns:
        List of normalized HTTPS endpoint strings (may be empty).
    """
    try:
        from ilc_core.network.d2d.gossip_peer_registry import validate_peer_endpoint

        peers_raw = bundle.get("peers") if isinstance(bundle, dict) else None
        if not isinstance(peers_raw, list):
            return []

        endpoints: list[str] = []
        for peer in peers_raw:
            if not isinstance(peer, dict):
                continue
            endpoint = peer.get("endpoint")
            if not isinstance(endpoint, str) or not endpoint.strip():
                continue
            try:
                normalized = validate_peer_endpoint(endpoint)
                endpoints.append(normalized)
            except Exception:  # noqa: BLE001
                continue  # skip invalid endpoint
        return endpoints
    except Exception:  # noqa: BLE001
        return []


def validate_bootstrap_bundle_schema(bundle: dict[str, Any]) -> bool:
    """Return True if bundle has all required fields for bootstrap_bundle_v1.

    Does NOT verify signature — use verify_bootstrap_bundle_signature() for that.
    """
    if not isinstance(bundle, dict):
        return False
    required = {
        "schema_version",
        "bundle_cid",
        "genesis_cid",
        "peers",
        "signed_by",
        "signature",
        "cdl_version",
    }
    if not required.issubset(bundle.keys()):
        return False
    if bundle.get("schema_version") != BOOTSTRAP_BUNDLE_SCHEMA_VERSION:
        return False
    if bundle.get("cdl_version") != BOOTSTRAP_BUNDLE_CDL_VERSION:
        return False
    for field in ("bundle_cid", "genesis_cid", "signed_by", "signature"):
        value = bundle.get(field)
        if not isinstance(value, str) or not value.strip() or value.strip() != value:
            return False
    peers = bundle.get("peers")
    if not isinstance(peers, list):
        return False
    for peer in peers:
        if not isinstance(peer, dict):
            return False
        endpoint = peer.get("endpoint")
        node_id = peer.get("node_id")
        if (
            not isinstance(endpoint, str)
            or not endpoint.strip()
            or endpoint.strip() != endpoint
            or not isinstance(node_id, str)
            or not node_id.strip()
            or node_id.strip() != node_id
        ):
            return False
    return True
