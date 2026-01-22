"""
Tests for deterministic DAG-CBOR encoding.

Verifies:
- Determinism across insertion order
- Canonical key ordering (length then lexicographic on encoded bytes)
- Type restrictions (no floats, only str/bytes keys)
- Roundtrip encode/decode
"""

import pytest

from ilc_core.encoding.dag_cbor import (
    encode_dag_cbor,
    decode_dag_cbor,
    validate_canonical_dag_cbor,
    is_canonical_dag_cbor,
)


class TestDagCborDeterminism:
    """Tests for encoding determinism."""

    def test_dict_order_does_not_affect_encoding(self):
        """Same dict with different insertion order produces identical bytes."""
        a = {"b": 2, "a": 1}
        b = {"a": 1, "b": 2}
        assert encode_dag_cbor(a) == encode_dag_cbor(b)

    def test_nested_dict_determinism(self):
        """Nested dicts are also deterministic."""
        a = {"outer": {"z": 1, "a": 2}, "inner": [3, 2, 1]}
        b = {"inner": [3, 2, 1], "outer": {"a": 2, "z": 1}}
        assert encode_dag_cbor(a) == encode_dag_cbor(b)

    def test_multiple_encodings_identical(self):
        """Repeated encoding produces identical bytes."""
        obj = {"key": [1, 2, 3], "other": b"hello"}
        first = encode_dag_cbor(obj)
        second = encode_dag_cbor(obj)
        third = encode_dag_cbor(obj)
        assert first == second == third


class TestCanonicalKeyOrdering:
    """Tests for canonical map key ordering."""

    def test_keys_sorted_by_encoded_length_first(self):
        """Shorter encoded keys come before longer ones."""
        # "b" encodes shorter than "aa"
        obj = {"aa": 1, "b": 2}
        encoded = encode_dag_cbor(obj)
        decoded = decode_dag_cbor(encoded)
        # When we iterate the decoded dict, order should be b, aa
        keys = list(decoded.keys())
        assert keys == ["b", "aa"]

    def test_keys_sorted_lexicographically_within_same_length(self):
        """Keys of same encoded length are sorted lexicographically."""
        obj = {"ab": 1, "aa": 2, "ac": 3}
        encoded = encode_dag_cbor(obj)
        decoded = decode_dag_cbor(encoded)
        keys = list(decoded.keys())
        assert keys == ["aa", "ab", "ac"]

    def test_mixed_length_keys(self):
        """Complex key ordering with varying lengths."""
        obj = {"aaa": 1, "b": 2, "aa": 3, "c": 4}
        encoded = encode_dag_cbor(obj)
        decoded = decode_dag_cbor(encoded)
        keys = list(decoded.keys())
        # Single char keys first (b, c), then two char (aa), then three char (aaa)
        assert keys == ["b", "c", "aa", "aaa"]

    def test_bytes_keys_ordering(self):
        """Bytes keys are also canonically ordered."""
        obj = {b"bb": 1, b"a": 2, b"aa": 3}
        encoded = encode_dag_cbor(obj)
        decoded = decode_dag_cbor(encoded)
        keys = list(decoded.keys())
        # Single byte first, then two bytes sorted lexicographically
        assert keys == [b"a", b"aa", b"bb"]


class TestTypeBans:
    """Tests for unsupported type handling."""

    def test_float_raises_type_error(self):
        """Floats are not supported in DAG-CBOR subset."""
        with pytest.raises(TypeError, match="does not support floats"):
            encode_dag_cbor(3.14)

    def test_float_in_list_raises_type_error(self):
        """Float nested in list is rejected."""
        with pytest.raises(TypeError, match="does not support floats"):
            encode_dag_cbor([1, 2.5, 3])

    def test_float_in_dict_value_raises_type_error(self):
        """Float as dict value is rejected."""
        with pytest.raises(TypeError, match="does not support floats"):
            encode_dag_cbor({"key": 1.0})

    def test_int_key_raises_type_error(self):
        """Integer dict keys are not allowed."""
        with pytest.raises(TypeError, match="must be str or bytes"):
            encode_dag_cbor({1: "value"})

    def test_tuple_key_raises_type_error(self):
        """Tuple dict keys are not allowed."""
        with pytest.raises(TypeError, match="must be str or bytes"):
            encode_dag_cbor({("a", "b"): "value"})

    def test_set_raises_type_error(self):
        """Sets are not supported."""
        with pytest.raises(TypeError, match="Unsupported type"):
            encode_dag_cbor({1, 2, 3})


class TestRoundtrip:
    """Tests for encode/decode roundtrip."""

    def test_simple_types_roundtrip(self):
        """Simple types roundtrip correctly."""
        for obj in [None, True, False, 0, 1, -1, 42, -1000]:
            assert decode_dag_cbor(encode_dag_cbor(obj)) == obj

    def test_bytes_roundtrip(self):
        """Bytes roundtrip correctly."""
        for obj in [b"", b"hello", b"\x00\x01\x02", b"\xff" * 100]:
            assert decode_dag_cbor(encode_dag_cbor(obj)) == obj

    def test_string_roundtrip(self):
        """Strings roundtrip correctly."""
        for obj in ["", "hello", "unicode: \u00e9\u00e8\u00ea", "emoji: \U0001f600"]:
            assert decode_dag_cbor(encode_dag_cbor(obj)) == obj

    def test_list_roundtrip(self):
        """Lists roundtrip correctly."""
        obj = [1, "two", b"three", None, True, [4, 5]]
        assert decode_dag_cbor(encode_dag_cbor(obj)) == obj

    def test_tuple_becomes_list(self):
        """Tuples encode as arrays and decode as lists."""
        obj = (1, 2, 3)
        decoded = decode_dag_cbor(encode_dag_cbor(obj))
        assert decoded == [1, 2, 3]
        assert isinstance(decoded, list)

    def test_dict_roundtrip(self):
        """Dicts roundtrip correctly."""
        obj = {"x": [1, True, None, b"\x00"], "y": "hi"}
        assert decode_dag_cbor(encode_dag_cbor(obj)) == obj

    def test_complex_nested_roundtrip(self):
        """Complex nested structures roundtrip correctly."""
        obj = {
            "level1": {
                "level2": {
                    "list": [1, 2, {"inner": b"bytes"}],
                    "bool": True,
                }
            },
            "null": None,
            "bytes_key_map": {b"key": "value"},
        }
        assert decode_dag_cbor(encode_dag_cbor(obj)) == obj


class TestIntegerRange:
    """Tests for integer range handling."""

    def test_max_positive_64bit(self):
        """Maximum positive 64-bit signed integer."""
        obj = 2**63 - 1
        assert decode_dag_cbor(encode_dag_cbor(obj)) == obj

    def test_min_negative_64bit(self):
        """Minimum negative 64-bit signed integer."""
        obj = -(2**63)
        assert decode_dag_cbor(encode_dag_cbor(obj)) == obj

    def test_positive_overflow_raises(self):
        """Positive integer beyond 64-bit range raises error."""
        with pytest.raises(ValueError, match="out of signed 64-bit range"):
            encode_dag_cbor(2**63)

    def test_negative_overflow_raises(self):
        """Negative integer beyond 64-bit range raises error."""
        with pytest.raises(ValueError, match="out of signed 64-bit range"):
            encode_dag_cbor(-(2**63) - 1)


class TestDecodeErrors:
    """Tests for decoder error handling."""

    def test_empty_data_raises(self):
        """Empty bytes raises error."""
        with pytest.raises(ValueError, match="Empty CBOR data"):
            decode_dag_cbor(b"")

    def test_truncated_data_raises(self):
        """Truncated data raises error."""
        # Start of a map but no contents
        with pytest.raises(ValueError):
            decode_dag_cbor(b"\xa1")  # Map with 1 item, but no key/value

    def test_trailing_data_raises(self):
        """Trailing data after valid CBOR raises error."""
        valid = encode_dag_cbor(42)
        with pytest.raises(ValueError, match="Trailing data"):
            decode_dag_cbor(valid + b"\x00")

    def test_duplicate_map_key_raises(self):
        """Duplicate map keys are rejected."""
        # {"a": 1, "a": 2} encoded directly
        data = b"\xa2\x61\x61\x01\x61\x61\x02"
        with pytest.raises(ValueError, match="Duplicate map key"):
            decode_dag_cbor(data)


class TestCanonicalValidation:
    """Tests for canonical DAG-CBOR validation."""

    def test_non_canonical_key_order_fails(self):
        """Non-canonical map key order fails canonical validation."""
        # {"b": 1, "a": 2} in non-canonical order
        data = b"\xa2\x61\x62\x01\x61\x61\x02"
        decoded = decode_dag_cbor(data)
        assert decoded == {"b": 1, "a": 2}
        with pytest.raises(ValueError, match="Non-canonical DAG-CBOR bytes"):
            validate_canonical_dag_cbor(data)
        assert is_canonical_dag_cbor(data) is False

    def test_canonical_bytes_pass(self):
        """Canonical bytes produced by encoder pass validation."""
        obj = {"a": 2, "b": 1}
        data = encode_dag_cbor(obj)
        validate_canonical_dag_cbor(data)
        assert is_canonical_dag_cbor(data) is True
