"""
Bundle Record Verification.

Phase 66C: Transport-to-commitment binding for NDJSON bundle records.

Verifies that a bundle record correctly binds to:
1. Valid COSE_Sign1 bytes (canonical CBOR)
2. Ed25519 signature verification
3. Strict DAG-CBOR payload (str keys only)
4. NodeID match between payload and record field
"""

from __future__ import annotations

from cryptography.hazmat.primitives.asymmetric import ed25519

from ..crypto.cose_sign1 import (
    cose_sign1_verify,
    validate_canonical_cose_sign1_bytes,
)
from ..encoding.dag_cbor import decode_dag_cbor_strict
from ..encoding.cidv1 import node_id_from_obj

from .ndjson_bundle import b64u_decode


def verify_bundle_record(
    record: dict,
    *,
    public_key: ed25519.Ed25519PublicKey,
) -> dict:
    """Verify transport record binds to commitment layer.
    
    Performs full verification:
    1. Base64url decode COSE bytes
    2. Validate canonical CBOR structure
    3. Verify COSE_Sign1 signature (Ed25519/EdDSA)
       - alg must be -8 (EdDSA)
       - unprotected must be {}
    4. Strict-decode DAG-CBOR payload (str keys only)
    5. Recompute NodeID from payload object
    6. Verify record["node_id"] matches recomputed NodeID
    
    Args:
        record: Bundle record dict (must have node_id, cose_sign1_b64u).
        public_key: Ed25519 public key for signature verification.
    
    Returns:
        {
            "seq": int,
            "node_id": str,
            "payload_obj": dict (the decoded payload),
            "cose_bytes": bytes
        }
    
    Raises:
        ValueError: If any verification step fails.
        cryptography.exceptions.InvalidSignature: If signature invalid.
    """
    # Extract fields
    seq = record.get("seq")
    node_id = record.get("node_id")
    cose_b64 = record.get("cose_sign1_b64u")
    
    if seq is None or node_id is None or cose_b64 is None:
        raise ValueError("Record missing required fields (seq, node_id, cose_sign1_b64u)")
    
    # Step 1: Decode base64url
    try:
        cose_bytes = b64u_decode(cose_b64)
    except ValueError as e:
        raise ValueError(f"Invalid base64url in cose_sign1_b64u: {e}")
    
    # Step 2: Validate canonical CBOR structure
    try:
        validate_canonical_cose_sign1_bytes(cose_bytes)
    except ValueError as e:
        raise ValueError(f"COSE bytes not canonical: {e}")
    
    # Step 3: Verify COSE_Sign1 signature
    # This enforces:
    # - alg = -8 (EdDSA)
    # - unprotected = {}
    # - canonical protected header
    # - signature verification
    verified = cose_sign1_verify(cose_bytes, public_key)
    
    # Step 4: Strict-decode payload (str keys only)
    payload_bytes = verified["payload"]
    try:
        payload_obj = decode_dag_cbor_strict(payload_bytes)
    except ValueError as e:
        raise ValueError(f"Payload not strict DAG-CBOR: {e}")
    
    # Step 5: Recompute NodeID
    computed_node_id = node_id_from_obj(payload_obj)
    
    # Step 6: Verify NodeID match
    if node_id != computed_node_id:
        raise ValueError(
            f"NodeID mismatch: record says '{node_id}', "
            f"payload computes to '{computed_node_id}'"
        )
    
    return {
        "seq": seq,
        "node_id": node_id,
        "payload_obj": payload_obj,
        "cose_bytes": cose_bytes,
    }


def verify_bundle_record_from_bytes(
    record: dict,
    *,
    public_key_bytes: bytes,
) -> dict:
    """Convenience wrapper accepting raw public key bytes."""
    public_key = ed25519.Ed25519PublicKey.from_public_bytes(public_key_bytes)
    return verify_bundle_record(record, public_key=public_key)
