"""
CIDv1 generation and parsing for NodeID.

Creates content identifiers using:
- CID version 1
- DAG-CBOR codec (0x71)
- SHA2-256 multihash (0x12)
- Base32 lowercase multibase encoding ('b' prefix)
"""

from __future__ import annotations
import hashlib
import base64
from typing import Any

from .varint import encode_uvarint, decode_uvarint
from .dag_cbor import encode_dag_cbor


# Multiformat constants
CIDV1_VERSION = 1
CODEC_DAG_CBOR = 0x71
MH_SHA2_256 = 0x12
SHA2_256_LEN = 32


def sha2_256_multihash(payload: bytes) -> bytes:
    """Create a SHA2-256 multihash of payload.
    
    Format: uvarint(hash_code) + uvarint(digest_length) + digest
    
    Args:
        payload: Raw bytes to hash.
        
    Returns:
        Multihash-encoded digest.
    """
    digest = hashlib.sha256(payload).digest()
    return encode_uvarint(MH_SHA2_256) + encode_uvarint(SHA2_256_LEN) + digest


def cidv1_bytes(codec_code: int, multihash: bytes) -> bytes:
    """Construct raw CIDv1 bytes.
    
    Format: uvarint(version) + uvarint(codec) + multihash
    
    Args:
        codec_code: Multicodec code for the content type.
        multihash: Multihash-encoded digest.
        
    Returns:
        Raw CID bytes (not yet base-encoded).
    """
    return encode_uvarint(CIDV1_VERSION) + encode_uvarint(codec_code) + multihash


def cidv1_to_str(cid_bytes: bytes) -> str:
    """Encode CID bytes to multibase base32 lowercase string.
    
    Uses 'b' prefix for base32 lowercase (RFC 4648, no padding).
    
    Args:
        cid_bytes: Raw CID bytes.
        
    Returns:
        Multibase-encoded CID string starting with 'b'.
    """
    # base64.b32encode returns uppercase with padding
    b32 = base64.b32encode(cid_bytes).decode("ascii")
    # Convert to lowercase and strip padding
    return "b" + b32.lower().rstrip("=")


def cidv1_from_str(cid_str: str) -> bytes:
    """Decode a multibase base32 lowercase CID string to bytes.
    
    Args:
        cid_str: CID string starting with 'b'.
        
    Returns:
        Raw CID bytes.
        
    Raises:
        ValueError: If string doesn't start with 'b' or is invalid base32.
    """
    if not cid_str.startswith("b"):
        raise ValueError(f"Expected base32lower multibase prefix 'b', got '{cid_str[:1]}'")
    
    b32_part = cid_str[1:].upper()
    
    # Restore padding
    padding_needed = (8 - len(b32_part) % 8) % 8
    b32_padded = b32_part + "=" * padding_needed
    
    try:
        return base64.b32decode(b32_padded)
    except Exception as e:
        raise ValueError(f"Invalid base32 encoding: {e}")


def parse_cidv1(cid_str: str) -> dict:
    """Parse a CIDv1 string into its components.
    
    Args:
        cid_str: CID string (multibase encoded).
        
    Returns:
        Dict with keys: version, codec, mh_code, digest_len, digest_hex
        
    Raises:
        ValueError: If CID is malformed or not version 1.
    """
    cid_bytes = cidv1_from_str(cid_str)
    
    offset = 0
    
    # Parse version
    version, consumed = decode_uvarint(cid_bytes, offset)
    offset += consumed
    
    if version != CIDV1_VERSION:
        raise ValueError(f"Expected CIDv1, got version {version}")
    
    # Parse codec
    codec, consumed = decode_uvarint(cid_bytes, offset)
    offset += consumed
    
    # Parse multihash: hash_code + digest_len + digest
    mh_code, consumed = decode_uvarint(cid_bytes, offset)
    offset += consumed
    
    digest_len, consumed = decode_uvarint(cid_bytes, offset)
    offset += consumed
    
    if offset + digest_len != len(cid_bytes):
        raise ValueError(
            f"Multihash digest length mismatch: expected {digest_len}, "
            f"got {len(cid_bytes) - offset}"
        )
    
    digest = cid_bytes[offset:offset + digest_len]
    
    return {
        "version": version,
        "codec": codec,
        "mh_code": mh_code,
        "digest_len": digest_len,
        "digest_hex": digest.hex(),
    }


def node_id_from_obj(obj: Any) -> str:
    """Generate a NodeID (CIDv1 string) from a Python object.
    
    The object is encoded to deterministic DAG-CBOR, hashed with SHA2-256,
    wrapped in a multihash, and encoded as a CIDv1 base32 lowercase string.
    
    Args:
        obj: Python object to generate ID for.
        
    Returns:
        CIDv1 string (multibase base32 lowercase, 'b' prefix).
        
    Raises:
        TypeError: If obj contains unsupported types for DAG-CBOR.
        ValueError: If integers are out of range.
    """
    dag_bytes = encode_dag_cbor(obj)
    mh = sha2_256_multihash(dag_bytes)
    cid_bytes = cidv1_bytes(CODEC_DAG_CBOR, mh)
    return cidv1_to_str(cid_bytes)
