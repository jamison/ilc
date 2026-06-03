# SPDX-License-Identifier: AGPL-3.0-only
"""
EVE Capsule builder and signing utilities.

Implements capsule creation and signing per ADR-0006:
- Build capsule manifest from entries
- Sign manifest using COSE Sign1
- Compute capsule_id from canonical DAG-CBOR bytes

See: docs/specs/eve_capsule_format_v0.1.md
"""

from __future__ import annotations

import base64
from datetime import datetime, timezone
from typing import Any

from cryptography.hazmat.primitives.asymmetric import ed25519

from ilc_core.encoding.dag_cbor import encode_dag_cbor
from ilc_core.encoding.cidv1 import node_id_from_bytes
from ilc_core.crypto.cose_sign1 import cose_sign1_sign


def build_capsule_manifest(
    entries: list[dict],
    publisher_key_id: str,
    predecessor: str | None = None,
    version: int = 1,
    created_at: str | None = None,
) -> dict:
    """Build a capsule manifest from entries.
    
    Creates a manifest structure with all required fields.
    The capsule_id will be set to a placeholder and must be
    computed after signing via sign_capsule_manifest.
    
    Args:
        entries: List of entry dicts with kind, cid, content_type.
        publisher_key_id: Key identifier (e.g., DID or fingerprint).
        predecessor: CID of previous version (None for v1).
        version: Version number (default 1).
        created_at: ISO 8601 timestamp (auto-generated if None).
        
    Returns:
        Manifest dict with placeholder capsule_id.
        
    Raises:
        ValueError: If entries is empty or invalid.
    """
    if not entries:
        raise ValueError("Entries must not be empty")
    
    # Validate entries have required fields
    required = {"kind", "cid", "content_type"}
    for i, entry in enumerate(entries):
        if not isinstance(entry, dict):
            raise ValueError(f"Entry {i} must be a dict")
        missing = required - set(entry.keys())
        if missing:
            raise ValueError(f"Entry {i} missing required fields: {sorted(missing)}")
    
    if created_at is None:
        created_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    
    manifest = {
        "capsule_id": "",  # Placeholder, computed after signing
        "version": version,
        "predecessor": predecessor,
        "publisher_key_id": publisher_key_id,
        "created_at": created_at,
        "entries": entries,
    }
    
    return manifest


def sign_capsule_manifest(
    manifest: dict,
    private_key_bytes: bytes,
    kid: bytes | None = None,
) -> tuple[dict, str]:
    """Sign a capsule manifest and compute its capsule_id.
    
    Signs the manifest using COSE Sign1 and computes the
    capsule_id from the canonical DAG-CBOR serialization.
    
    Args:
        manifest: Manifest dict (capsule_id will be updated).
        private_key_bytes: Raw Ed25519 private key bytes (32 bytes).
        kid: Optional key identifier for COSE header.
        
    Returns:
        Tuple of (manifest_with_capsule_id, cose_sign1_b64u).
        
    Raises:
        ValueError: If manifest is invalid.
    """
    # Load private key
    private_key = ed25519.Ed25519PrivateKey.from_private_bytes(private_key_bytes)
    
    # Create a copy without capsule_id for signing
    manifest_for_signing = dict(manifest)
    manifest_for_signing["capsule_id"] = ""  # Empty for signing
    
    # Encode to canonical DAG-CBOR
    payload = encode_dag_cbor(manifest_for_signing)
    
    # Compute capsule_id from payload
    capsule_id = node_id_from_bytes(payload)
    
    # Update manifest with computed capsule_id
    manifest_with_id = dict(manifest)
    manifest_with_id["capsule_id"] = capsule_id
    
    # Re-encode with capsule_id for final signature
    final_payload = encode_dag_cbor(manifest_with_id)
    
    # Sign with COSE Sign1
    cose_bytes = cose_sign1_sign(final_payload, private_key, kid=kid)
    
    # Encode as base64url (no padding)
    cose_b64u = base64.urlsafe_b64encode(cose_bytes).decode().rstrip("=")
    
    return manifest_with_id, cose_b64u
