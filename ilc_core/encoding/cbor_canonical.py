"""
Canonical CBOR utilities for COSE structures.

This module provides canonical CBOR encoding/decoding for COSE blocks,
which use integer-labeled header maps (NOT subject to ILC strict key rules).

Uses cbor2 with canonical=True for deterministic output.
"""

from __future__ import annotations
from typing import Any

import cbor2


def cbor_dumps_canonical(obj: Any) -> bytes:
    """Encode object to canonical CBOR bytes.
    
    Uses RFC 7049 deterministic encoding:
    - Map keys sorted by length then lexicographically
    - Minimal integer encoding
    - No indefinite lengths
    
    Args:
        obj: Python object to encode.
        
    Returns:
        Canonical CBOR bytes.
    """
    return cbor2.dumps(obj, canonical=True)


def cbor_loads(data: bytes) -> Any:
    """Decode CBOR bytes to Python object.
    
    Args:
        data: CBOR encoded bytes.
        
    Returns:
        Decoded Python object.
        
    Raises:
        cbor2.CBORDecodeError: If data is malformed.
    """
    return cbor2.loads(data)


def validate_canonical_cbor_bytes(data: bytes) -> None:
    """Validate that CBOR bytes are in canonical form.
    
    Canonical means decode -> re-encode yields identical bytes.
    
    Args:
        data: CBOR encoded bytes.
        
    Raises:
        ValueError: If bytes are not canonical.
    """
    if not data:
        raise ValueError("Empty CBOR data")
    
    try:
        obj = cbor_loads(data)
    except Exception as e:
        raise ValueError(f"Invalid CBOR: {e}")
    
    reencoded = cbor_dumps_canonical(obj)
    if reencoded != data:
        raise ValueError("Non-canonical CBOR bytes")


def is_canonical_cbor(data: bytes) -> bool:
    """Return True if data is canonical CBOR bytes."""
    try:
        validate_canonical_cbor_bytes(data)
    except ValueError:
        return False
    return True
