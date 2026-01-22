"""
Deterministic DAG-CBOR subset encoder and decoder.

This implements a minimal subset of CBOR (RFC 8949) with DAG-CBOR
deterministic constraints:
- Definite lengths only (no indefinite)
- No tags
- No floats
- Canonical map key ordering (by encoded key length, then lexicographic)
- Minimal integer encoding

Supported types:
- None, bool
- int (signed 64-bit range)
- bytes
- str (UTF-8)
- list, tuple
- dict (keys must be str or bytes only)
"""

from __future__ import annotations
from typing import Any


# CBOR major types
_MT_UNSIGNED = 0
_MT_NEGATIVE = 1
_MT_BYTES = 2
_MT_TEXT = 3
_MT_ARRAY = 4
_MT_MAP = 5
_MT_SIMPLE = 7

# Simple values
_SIMPLE_FALSE = 20
_SIMPLE_TRUE = 21
_SIMPLE_NULL = 22


def _encode_type_and_len(major: int, n: int) -> bytes:
    """Encode a CBOR type header with minimal integer encoding."""
    if n < 0:
        raise ValueError(f"Length cannot be negative: {n}")
    
    head = major << 5
    
    if n <= 23:
        return bytes([head | n])
    elif n <= 0xFF:
        return bytes([head | 24, n])
    elif n <= 0xFFFF:
        return bytes([head | 25, (n >> 8) & 0xFF, n & 0xFF])
    elif n <= 0xFFFFFFFF:
        return bytes([head | 26, (n >> 24) & 0xFF, (n >> 16) & 0xFF,
                      (n >> 8) & 0xFF, n & 0xFF])
    elif n <= 0xFFFFFFFFFFFFFFFF:
        return bytes([head | 27,
                      (n >> 56) & 0xFF, (n >> 48) & 0xFF,
                      (n >> 40) & 0xFF, (n >> 32) & 0xFF,
                      (n >> 24) & 0xFF, (n >> 16) & 0xFF,
                      (n >> 8) & 0xFF, n & 0xFF])
    else:
        raise ValueError(f"Value too large for CBOR: {n}")


def _encode_int(n: int) -> bytes:
    """Encode a signed integer."""
    if n >= 0:
        return _encode_type_and_len(_MT_UNSIGNED, n)
    else:
        # CBOR negative: -1 - n, so for n=-1, encode 0; for n=-10, encode 9
        return _encode_type_and_len(_MT_NEGATIVE, -1 - n)


def _encode_bytes(b: bytes) -> bytes:
    """Encode a byte string."""
    return _encode_type_and_len(_MT_BYTES, len(b)) + b


def _encode_text(s: str) -> bytes:
    """Encode a UTF-8 text string."""
    encoded = s.encode("utf-8")
    return _encode_type_and_len(_MT_TEXT, len(encoded)) + encoded


def _encode_value(obj: Any) -> bytes:
    """Recursively encode a Python value to DAG-CBOR bytes."""
    if obj is None:
        return bytes([(_MT_SIMPLE << 5) | _SIMPLE_NULL])
    
    if obj is False:
        return bytes([(_MT_SIMPLE << 5) | _SIMPLE_FALSE])
    
    if obj is True:
        return bytes([(_MT_SIMPLE << 5) | _SIMPLE_TRUE])
    
    if isinstance(obj, int) and not isinstance(obj, bool):
        # Check 64-bit signed range
        if obj < -(2**63) or obj > 2**63 - 1:
            raise ValueError(f"Integer out of signed 64-bit range: {obj}")
        return _encode_int(obj)
    
    if isinstance(obj, float):
        raise TypeError("DAG-CBOR subset does not support floats")
    
    if isinstance(obj, bytes):
        return _encode_bytes(obj)
    
    if isinstance(obj, str):
        return _encode_text(obj)
    
    if isinstance(obj, (list, tuple)):
        parts = [_encode_type_and_len(_MT_ARRAY, len(obj))]
        for item in obj:
            parts.append(_encode_value(item))
        return b"".join(parts)
    
    if isinstance(obj, dict):
        # Validate keys and encode them
        encoded_keys = []
        for key in obj.keys():
            if isinstance(key, str):
                key_bytes = _encode_text(key)
            elif isinstance(key, bytes):
                key_bytes = _encode_bytes(key)
            else:
                raise TypeError(
                    f"DAG-CBOR map keys must be str or bytes, got {type(key).__name__}"
                )
            encoded_keys.append((key_bytes, key))
        
        # Sort by: (length of encoded key, encoded key bytes)
        encoded_keys.sort(key=lambda x: (len(x[0]), x[0]))
        
        parts = [_encode_type_and_len(_MT_MAP, len(obj))]
        for key_bytes, key in encoded_keys:
            parts.append(key_bytes)
            parts.append(_encode_value(obj[key]))
        return b"".join(parts)
    
    raise TypeError(f"Unsupported type for DAG-CBOR: {type(obj).__name__}")


def encode_dag_cbor(obj: Any) -> bytes:
    """Encode a Python object to deterministic DAG-CBOR bytes.
    
    Args:
        obj: A Python object (None, bool, int, bytes, str, list, tuple, dict).
        
    Returns:
        Canonical DAG-CBOR encoded bytes.
        
    Raises:
        TypeError: If obj contains unsupported types (float, set, etc.)
                   or dict keys that are not str/bytes.
        ValueError: If integers are out of signed 64-bit range.
    """
    return _encode_value(obj)


# --- Decoder ---

def _decode_type_and_len(data: bytes, offset: int) -> tuple[int, int, int]:
    """Decode CBOR type header, returning (major_type, value, bytes_consumed)."""
    if offset >= len(data):
        raise ValueError("Truncated CBOR: unexpected end of data")
    
    initial = data[offset]
    major = initial >> 5
    additional = initial & 0x1F
    
    if additional <= 23:
        return major, additional, 1
    elif additional == 24:
        if offset + 1 >= len(data):
            raise ValueError("Truncated CBOR: missing 1-byte length")
        return major, data[offset + 1], 2
    elif additional == 25:
        if offset + 2 >= len(data):
            raise ValueError("Truncated CBOR: missing 2-byte length")
        val = (data[offset + 1] << 8) | data[offset + 2]
        return major, val, 3
    elif additional == 26:
        if offset + 4 >= len(data):
            raise ValueError("Truncated CBOR: missing 4-byte length")
        val = (data[offset + 1] << 24) | (data[offset + 2] << 16) | \
              (data[offset + 3] << 8) | data[offset + 4]
        return major, val, 5
    elif additional == 27:
        if offset + 8 >= len(data):
            raise ValueError("Truncated CBOR: missing 8-byte length")
        val = 0
        for i in range(8):
            val = (val << 8) | data[offset + 1 + i]
        return major, val, 9
    elif additional in (28, 29, 30):
        raise ValueError(f"Reserved additional info: {additional}")
    elif additional == 31:
        raise ValueError("Indefinite length not supported in DAG-CBOR")
    else:
        raise ValueError(f"Invalid additional info: {additional}")


def _decode_value(data: bytes, offset: int) -> tuple[Any, int]:
    """Decode a single CBOR value, returning (value, bytes_consumed)."""
    major, val, header_len = _decode_type_and_len(data, offset)
    pos = offset + header_len
    
    if major == _MT_UNSIGNED:
        return val, header_len
    
    if major == _MT_NEGATIVE:
        return -1 - val, header_len
    
    if major == _MT_BYTES:
        if pos + val > len(data):
            raise ValueError("Truncated CBOR: byte string extends past end")
        return data[pos:pos + val], header_len + val
    
    if major == _MT_TEXT:
        if pos + val > len(data):
            raise ValueError("Truncated CBOR: text string extends past end")
        try:
            text = data[pos:pos + val].decode("utf-8")
        except UnicodeDecodeError as e:
            raise ValueError(f"Invalid UTF-8 in text string: {e}")
        return text, header_len + val
    
    if major == _MT_ARRAY:
        result = []
        total_consumed = header_len
        for _ in range(val):
            item, consumed = _decode_value(data, offset + total_consumed)
            result.append(item)
            total_consumed += consumed
        return result, total_consumed
    
    if major == _MT_MAP:
        result = {}
        total_consumed = header_len
        for _ in range(val):
            key, key_consumed = _decode_value(data, offset + total_consumed)
            total_consumed += key_consumed
            if not isinstance(key, (str, bytes)):
                raise ValueError(f"DAG-CBOR map key must be str or bytes, got {type(key)}")
            if key in result:
                raise ValueError(f"Duplicate map key: {key!r}")
            value, value_consumed = _decode_value(data, offset + total_consumed)
            total_consumed += value_consumed
            result[key] = value
        return result, total_consumed
    
    if major == _MT_SIMPLE:
        if val == _SIMPLE_FALSE:
            return False, header_len
        elif val == _SIMPLE_TRUE:
            return True, header_len
        elif val == _SIMPLE_NULL:
            return None, header_len
        else:
            raise ValueError(f"Unsupported simple value: {val}")
    
    # Major type 6 (tags) not supported
    raise ValueError(f"Unsupported CBOR major type: {major}")


def decode_dag_cbor(data: bytes) -> Any:
    """Decode DAG-CBOR bytes to a Python object.
    
    Args:
        data: DAG-CBOR encoded bytes.
        
    Returns:
        Decoded Python object.
        
    Raises:
        ValueError: If data is malformed, uses unsupported features,
                    or contains invalid encoding.
    """
    if not data:
        raise ValueError("Empty CBOR data")
    
    value, consumed = _decode_value(data, 0)
    
    if consumed != len(data):
        raise ValueError(
            f"Trailing data after CBOR value: {len(data) - consumed} bytes"
        )
    
    return value


def validate_canonical_dag_cbor(data: bytes) -> None:
    """Validate that DAG-CBOR bytes are in canonical form.

    Canonical means decode -> re-encode yields identical bytes.
    """
    obj = decode_dag_cbor(data)
    reencoded = encode_dag_cbor(obj)
    if reencoded != data:
        raise ValueError("Non-canonical DAG-CBOR bytes")


def is_canonical_dag_cbor(data: bytes) -> bool:
    """Return True if data is canonical DAG-CBOR bytes."""
    try:
        validate_canonical_dag_cbor(data)
    except ValueError:
        return False
    return True


# --- ILC Strict Key Validation ---

def _validate_keys_str_only_recursive(obj: Any, path: str) -> None:
    """Recursive helper for validate_ilc_object_keys_str_only."""
    if isinstance(obj, dict):
        for key, value in obj.items():
            if not isinstance(key, str):
                raise ValueError(
                    f"ILC object map keys must be str, got {type(key).__name__} "
                    f"at path {path}.{key!r}"
                )
            child_path = f"{path}.{key}" if path else f"$.{key}"
            _validate_keys_str_only_recursive(value, child_path)
    elif isinstance(obj, (list, tuple)):
        for i, item in enumerate(obj):
            child_path = f"{path}[{i}]"
            _validate_keys_str_only_recursive(item, child_path)
    # Primitives (int, bool, None, str, bytes) have no nested keys to check


def validate_ilc_object_keys_str_only(obj: Any) -> None:
    """Recursively enforce that all map keys are Python str (CBOR text string).
    
    ILC canonical objects require text-string keys only for cross-language
    determinism and interoperability. Bytes are allowed as values but not keys.
    
    Args:
        obj: Python object to validate.
        
    Raises:
        ValueError: If any dict key is not a str, with path to offending key.
    """
    _validate_keys_str_only_recursive(obj, "$")


def is_ilc_object_keys_str_only(obj: Any) -> bool:
    """Return True if all map keys in obj are str."""
    try:
        validate_ilc_object_keys_str_only(obj)
    except ValueError:
        return False
    return True


def decode_dag_cbor_strict(data: bytes) -> Any:
    """Decode DAG-CBOR with ILC strict object rules.
    
    Enforces:
    - No duplicate keys (already enforced by decoder)
    - All map keys must be str (not bytes)
    
    Args:
        data: DAG-CBOR encoded bytes.
        
    Returns:
        Decoded Python object.
        
    Raises:
        ValueError: If data is malformed or contains bytes keys.
    """
    obj = decode_dag_cbor(data)
    validate_ilc_object_keys_str_only(obj)
    return obj


def validate_canonical_ilc_dag_cbor(data: bytes) -> None:
    """Validate that DAG-CBOR bytes are in canonical ILC form.
    
    This is the strict validator for ILC consensus objects:
    - All map keys must be str (text strings)
    - Canonical encoding (decode -> re-encode = identical bytes)
    
    Args:
        data: DAG-CBOR encoded bytes.
        
    Raises:
        ValueError: If data is non-canonical or uses bytes keys.
    """
    obj = decode_dag_cbor_strict(data)
    reencoded = encode_dag_cbor(obj)
    if reencoded != data:
        raise ValueError("Non-canonical ILC DAG-CBOR bytes")


def is_canonical_ilc_dag_cbor(data: bytes) -> bool:
    """Return True if data is canonical ILC DAG-CBOR bytes (str keys only)."""
    try:
        validate_canonical_ilc_dag_cbor(data)
    except ValueError:
        return False
    return True
