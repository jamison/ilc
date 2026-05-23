# SPDX-License-Identifier: AGPL-3.0-or-later
"""
EVE Capsule verification utilities.

Implements minimal capsule integrity verification per ADR-0006:
- Manifest loading and validation
- COSE Sign1 signature verification
- Capsule field validation

See: docs/specs/eve_capsule_format_v0.1.md
"""

from __future__ import annotations

import base64
import binascii
import json
from pathlib import Path
from typing import Any, Union

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric import ed25519

from ilc_core.crypto.cose_sign1 import cose_sign1_decode, cose_sign1_verify


# Required manifest fields
REQUIRED_MANIFEST_FIELDS = frozenset([
    "capsule_id",
    "version",
    "predecessor",
    "publisher_key_id",
    "created_at",
    "entries",
])

# Required entry fields
REQUIRED_ENTRY_FIELDS = frozenset([
    "kind",
    "cid",
    "content_type",
])


def load_capsule_manifest(path: Union[str, Path]) -> dict:
    """Load a capsule manifest from a file.
    
    Supports JSON format for development/debugging.
    Production capsules use DAG-CBOR but JSON is accepted for testing.
    
    Args:
        path: Path to manifest file (JSON).
        
    Returns:
        Manifest dict.
        
    Raises:
        FileNotFoundError: If file does not exist.
        ValueError: If file cannot be parsed.
    """
    path = Path(path)
    data = path.read_text(encoding="utf-8")
    try:
        manifest = json.loads(data)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON manifest: {e}") from e
    return manifest


def validate_capsule_manifest(manifest: dict) -> None:
    """Validate that a manifest has all required fields.
    
    Args:
        manifest: Manifest dict to validate.
        
    Raises:
        ValueError: If required fields are missing or invalid.
    """
    if not isinstance(manifest, dict):
        raise ValueError("Manifest must be a dict")
    
    # Check required top-level fields
    missing = REQUIRED_MANIFEST_FIELDS - set(manifest.keys())
    if missing:
        raise ValueError(f"Manifest missing required fields: {sorted(missing)}")
    
    # Validate version
    if not isinstance(manifest["version"], int) or manifest["version"] < 1:
        raise ValueError("Manifest version must be a positive integer")
    
    # Validate entries is a non-empty list
    entries = manifest["entries"]
    if not isinstance(entries, list):
        raise ValueError("Manifest entries must be a list")
    if len(entries) == 0:
        raise ValueError("Manifest entries must not be empty")
    
    # Validate each entry
    for i, entry in enumerate(entries):
        if not isinstance(entry, dict):
            raise ValueError(f"Entry {i} must be a dict")
        entry_missing = REQUIRED_ENTRY_FIELDS - set(entry.keys())
        if entry_missing:
            raise ValueError(
                f"Entry {i} missing required fields: {sorted(entry_missing)}"
            )


def verify_capsule_signature(
    manifest: dict,
    cose_sign1_b64u: str,
    public_key_bytes: bytes,
) -> bool:
    """Verify a capsule signature.
    
    Args:
        manifest: Manifest dict (for reference, not directly verified).
        cose_sign1_b64u: Base64url-encoded COSE Sign1 signature bytes.
        public_key_bytes: Raw Ed25519 public key bytes (32 bytes).
        
    Returns:
        True if signature is valid, False otherwise.
        
    Note:
        The COSE Sign1 payload should be the canonical serialization
        of the manifest. This function verifies that the signature
        is valid for whatever payload is in the COSE structure.
    """
    try:
        # Decode base64url
        # Python's base64.urlsafe_b64decode requires padding
        padded = cose_sign1_b64u + "=" * (-len(cose_sign1_b64u) % 4)
        cose_bytes = base64.urlsafe_b64decode(padded)
        
        # Load public key
        public_key = ed25519.Ed25519PublicKey.from_public_bytes(public_key_bytes)
        
        # Verify signature
        cose_sign1_verify(cose_bytes, public_key)
        return True
    except (binascii.Error, ValueError, TypeError, InvalidSignature):
        return False


def load_capsule_manifest_cbor(path: Union[str, Path]) -> dict:
    """Load a capsule manifest from a DAG-CBOR file.
    
    Args:
        path: Path to manifest file (DAG-CBOR encoded).
        
    Returns:
        Manifest dict.
        
    Raises:
        FileNotFoundError: If file does not exist.
        ValueError: If file cannot be decoded.
    """
    from ilc_core.encoding.dag_cbor import decode_dag_cbor
    
    path = Path(path)
    data = path.read_bytes()
    try:
        manifest = decode_dag_cbor(data)
    except (ValueError, TypeError) as e:
        raise ValueError(f"Invalid DAG-CBOR manifest: {e}") from e
    
    if not isinstance(manifest, dict):
        raise ValueError("DAG-CBOR manifest must decode to a dict")
    
    return manifest


def verify_manifest_cid(manifest: dict, cose_sign1_bytes: bytes) -> bool:
    """Verify that manifest capsule_id matches the signed payload.
    
    Verifies two things:
    1. The signed manifest is internally consistent (capsule_id matches content hash)
    2. The *provided* manifest matches the signed manifest
    
    Args:
        manifest: Manifest dict to verify.
        cose_sign1_bytes: Raw COSE Sign1 bytes (not base64).
        
    Returns:
        True if valid and matches, False otherwise.

    Note:
        This function does NOT verify the COSE signature. Call
        verify_capsule_signature() first when full verification is required.
    """
    from ilc_core.crypto.cose_sign1 import cose_sign1_decode
    from ilc_core.encoding.dag_cbor import decode_dag_cbor, encode_dag_cbor
    from ilc_core.encoding.cidv1 import node_id_from_bytes
    
    try:
        # Decode the signed payload
        decoded = cose_sign1_decode(cose_sign1_bytes)
        payload = decoded["payload"]
        
        # Decode manifest from payload
        signed_manifest = decode_dag_cbor(payload)
        
        # 1. Verify internal consistency
        manifest_for_cid = dict(signed_manifest)
        manifest_for_cid["capsule_id"] = ""
        cid_payload = encode_dag_cbor(manifest_for_cid)
        expected_cid = node_id_from_bytes(cid_payload)
        
        if signed_manifest.get("capsule_id") != expected_cid:
            return False
            
        # 2. Verify provided manifest matches signed manifest
        # (This ensures the signature actually applies to the manifest we have)
        if manifest != signed_manifest:
            return False
            
        return True
    except (ValueError, TypeError, KeyError):
        return False
