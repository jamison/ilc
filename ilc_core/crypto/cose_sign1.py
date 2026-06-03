# SPDX-License-Identifier: AGPL-3.0-only
"""
COSE Sign1 attestation block implementation.

Implements minimal COSE_Sign1 (RFC 8152) for ILC attestations:
- Ed25519 signatures (algorithm -8, EdDSA)
- Canonical CBOR encoding for determinism
- Payload must be canonical ILC DAG-CBOR (strict profile)

COSE headers use integer labels (COSE-native), NOT subject to ILC strict key rules.
"""

from __future__ import annotations
from typing import Any

from cryptography.hazmat.primitives.asymmetric import ed25519
from cbor2 import CBORTag

from .cbor_canonical import (
    cbor_dumps_canonical,
    cbor_loads,
    validate_canonical_cbor_bytes,
)
from ..encoding.dag_cbor import validate_canonical_ilc_dag_cbor
from ..encoding.cidv1 import node_id_from_bytes


# COSE constants
COSE_TAG_SIGN1 = 18
COSE_HDR_ALG = 1
COSE_HDR_KID = 4
COSE_ALG_EDDSA = -8

# Ed25519 signatures are always exactly 64 bytes (RFC 8032 §5.1.6).
_EDDSA_SIG_LENGTH = 64


def cose_sign1_sign(
    payload: bytes,
    private_key: ed25519.Ed25519PrivateKey,
    kid: bytes | None = None,
    external_aad: bytes = b"",
) -> bytes:
    """Create a COSE_Sign1 attestation block.
    
    Signs the payload using Ed25519 (EdDSA, algorithm -8) and encodes
    as a canonical CBOR COSE_Sign1 structure (tag 18).
    
    Args:
        payload: Canonical ILC DAG-CBOR bytes to sign.
        private_key: Ed25519 private key for signing.
        kid: Optional key identifier (stored in protected header).
        external_aad: External additional authenticated data (default empty).
        
    Returns:
        COSE_Sign1 encoded bytes (canonical CBOR, tag 18).
        
    Raises:
        ValueError: If payload is not canonical ILC DAG-CBOR.
    """
    # Validate payload is canonical ILC DAG-CBOR (strict profile)
    validate_canonical_ilc_dag_cbor(payload)
    
    # Build protected header map
    protected_map: dict[int, Any] = {COSE_HDR_ALG: COSE_ALG_EDDSA}
    if kid is not None:
        protected_map[COSE_HDR_KID] = kid
    
    # Encode protected header to canonical bytes
    protected_bstr = cbor_dumps_canonical(protected_map)
    
    # Unprotected header (empty for MVP)
    unprotected_map: dict[int, Any] = {}
    
    # Build Sig_structure for "Signature1"
    # Sig_structure = ["Signature1", protected, external_aad, payload]
    sig_structure = ["Signature1", protected_bstr, external_aad, payload]
    to_be_signed = cbor_dumps_canonical(sig_structure)
    
    # Sign with Ed25519
    signature = private_key.sign(to_be_signed)
    
    # Build COSE_Sign1 array: [protected, unprotected, payload, signature]
    cose_array = [protected_bstr, unprotected_map, payload, signature]
    
    # Wrap in tag 18 and encode canonically
    cose_tagged = CBORTag(COSE_TAG_SIGN1, cose_array)
    return cbor_dumps_canonical(cose_tagged)


def cose_sign1_decode(cose_bytes: bytes) -> dict:
    """Decode a COSE_Sign1 structure.
    
    Validates canonical CBOR encoding but does NOT verify the signature.
    Use cose_sign1_verify() for full verification.
    
    Args:
        cose_bytes: COSE_Sign1 encoded bytes.
        
    Returns:
        Dict with keys:
        - protected_bstr: Raw protected header bytes
        - protected: Decoded protected header map
        - unprotected: Unprotected header map
        - payload: Payload bytes
        - signature: Signature bytes
        - alg: Algorithm label (should be -8 for EdDSA)
        - kid: Key ID bytes or None
        
    Raises:
        ValueError: If structure is malformed or non-canonical.
    """
    # Validate outer CBOR is canonical
    validate_canonical_cbor_bytes(cose_bytes)
    
    # Decode
    obj = cbor_loads(cose_bytes)
    
    # Must be tag 18
    if not isinstance(obj, CBORTag):
        raise ValueError("COSE_Sign1 must be a CBOR tag")
    if obj.tag != COSE_TAG_SIGN1:
        raise ValueError(f"Expected COSE_Sign1 tag 18, got tag {obj.tag}")
    
    # Unwrap array
    cose_array = obj.value
    if not isinstance(cose_array, list) or len(cose_array) != 4:
        raise ValueError("COSE_Sign1 must be an array of 4 elements")
    
    protected_bstr, unprotected_map, payload, signature = cose_array
    
    # Validate types
    if not isinstance(protected_bstr, bytes):
        raise ValueError("COSE_Sign1 protected header must be bstr")
    if not isinstance(unprotected_map, dict):
        raise ValueError("COSE_Sign1 unprotected header must be map")
    
    # MVP restriction: unprotected headers must be empty
    # This prevents ambiguity in header placement and simplifies verification.
    # Future ILC versions may relax this if needed.
    if unprotected_map != {}:
        raise ValueError("Invalid COSE_Sign1: unprotected headers must be empty for ILC MVP")
    
    if not isinstance(payload, bytes):
        raise ValueError("COSE_Sign1 payload must be bstr")
    if not isinstance(signature, bytes):
        raise ValueError("COSE_Sign1 signature must be bstr")
    
    # Validate protected header is canonical CBOR
    validate_canonical_cbor_bytes(protected_bstr)
    protected_map = cbor_loads(protected_bstr)
    
    if not isinstance(protected_map, dict):
        raise ValueError("COSE protected header must decode to map")
    
    # Extract algorithm and kid
    alg = protected_map.get(COSE_HDR_ALG)
    kid = protected_map.get(COSE_HDR_KID)
    
    return {
        "protected_bstr": protected_bstr,
        "protected": protected_map,
        "unprotected": unprotected_map,
        "payload": payload,
        "signature": signature,
        "alg": alg,
        "kid": kid,
    }


def cose_sign1_verify(
    cose_bytes: bytes,
    public_key: ed25519.Ed25519PublicKey,
    external_aad: bytes = b"",
) -> dict:
    """Verify a COSE_Sign1 attestation block.
    
    Performs full verification:
    1. Validates canonical COSE encoding
    2. Validates payload is canonical ILC DAG-CBOR (strict profile)
    3. Verifies Ed25519 signature
    4. Computes and returns NodeID for the payload
    
    Args:
        cose_bytes: COSE_Sign1 encoded bytes.
        public_key: Ed25519 public key for verification.
        external_aad: External additional authenticated data (must match signing).
        
    Returns:
        Decoded dict with additional "nodeid" field.
        
    Raises:
        ValueError: If structure is malformed, non-canonical, or wrong algorithm.
        cryptography.exceptions.InvalidSignature: If signature verification fails.
    """
    # Decode and validate structure
    decoded = cose_sign1_decode(cose_bytes)
    
    # Require EdDSA algorithm
    if decoded["alg"] != COSE_ALG_EDDSA:
        raise ValueError(
            f"Expected EdDSA algorithm (-8), got {decoded['alg']}"
        )

    # Validate signature length before handing to cryptography library.
    # A malformed length produces an opaque InvalidSignature from the library;
    # surfacing a clear ValueError here keeps the error contract consistent.
    if len(decoded["signature"]) != _EDDSA_SIG_LENGTH:
        raise ValueError(
            f"EdDSA signature must be {_EDDSA_SIG_LENGTH} bytes, "
            f"got {len(decoded['signature'])}"
        )

    # Validate payload is canonical ILC DAG-CBOR (strict profile)
    validate_canonical_ilc_dag_cbor(decoded["payload"])
    
    # Rebuild Sig_structure for verification
    sig_structure = [
        "Signature1",
        decoded["protected_bstr"],
        external_aad,
        decoded["payload"],
    ]
    to_be_signed = cbor_dumps_canonical(sig_structure)
    
    # Verify signature (raises InvalidSignature on failure)
    public_key.verify(decoded["signature"], to_be_signed)
    
    # Compute NodeID from payload bytes
    nodeid = node_id_from_bytes(decoded["payload"])
    
    # Add nodeid to result
    result = dict(decoded)
    result["nodeid"] = nodeid
    return result


def validate_canonical_cose_sign1_bytes(data: bytes) -> None:
    """Validate that data is a well-formed canonical COSE_Sign1.
    
    Does NOT verify the signature, only structural validity.
    
    Args:
        data: Bytes to validate.
        
    Raises:
        ValueError: If data is not a valid canonical COSE_Sign1.
    """
    cose_sign1_decode(data)  # Raises on any issue
