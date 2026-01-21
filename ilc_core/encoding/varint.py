"""
Unsigned variable-length integer (uvarint) encoding.

LEB128-style encoding where each byte uses 7 bits for data
and bit 7 (0x80) as a continuation flag.
"""

from __future__ import annotations


def encode_uvarint(n: int) -> bytes:
    """Encode an unsigned integer as a variable-length byte sequence.
    
    Args:
        n: Non-negative integer to encode.
        
    Returns:
        Bytes representing the uvarint encoding.
        
    Raises:
        ValueError: If n is negative.
    """
    if n < 0:
        raise ValueError(f"uvarint requires non-negative integer, got {n}")
    
    if n == 0:
        return b"\x00"
    
    result = []
    while n > 0:
        byte = n & 0x7F  # Low 7 bits
        n >>= 7
        if n > 0:
            byte |= 0x80  # Set continuation bit
        result.append(byte)
    
    return bytes(result)


def decode_uvarint(data: bytes, offset: int = 0) -> tuple[int, int]:
    """Decode a uvarint from bytes starting at offset.
    
    Args:
        data: Bytes containing the uvarint.
        offset: Starting position in data.
        
    Returns:
        Tuple of (decoded_value, bytes_consumed).
        
    Raises:
        ValueError: If data is truncated or varint is malformed.
    """
    if offset >= len(data):
        raise ValueError("Truncated varint: no data at offset")
    
    result = 0
    shift = 0
    bytes_consumed = 0
    
    while True:
        if offset + bytes_consumed >= len(data):
            raise ValueError("Truncated varint: unexpected end of data")
        
        byte = data[offset + bytes_consumed]
        bytes_consumed += 1
        
        # Add the 7 data bits
        result |= (byte & 0x7F) << shift
        shift += 7
        
        # Check continuation bit
        if not (byte & 0x80):
            break
        
        # Guard against overflow (more than 10 bytes for 64-bit)
        if bytes_consumed > 10:
            raise ValueError("Varint too long (overflow)")
    
    return result, bytes_consumed
