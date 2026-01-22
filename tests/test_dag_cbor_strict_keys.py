"""
Tests for strict DAG-CBOR key validation (ILC consensus rules).

Verifies:
- Only str keys allowed (not bytes)
- Recursive validation with path reporting
- Strict decode wrapper rejects bytes-key CBOR
- NodeID generation rejects bytes keys
"""

import pytest

from ilc_core.encoding.dag_cbor import (
    validate_ilc_object_keys_str_only,
    is_ilc_object_keys_str_only,
    decode_dag_cbor_strict,
    decode_dag_cbor,
    encode_dag_cbor,
    validate_canonical_ilc_dag_cbor,
    is_canonical_ilc_dag_cbor,
)
from ilc_core.encoding.cidv1 import node_id_from_obj


class TestValidateIlcObjectKeysStrOnly:
    """Tests for validate_ilc_object_keys_str_only."""

    def test_bytes_key_rejected(self):
        """Single bytes key is rejected."""
        obj = {b"a": 1}
        with pytest.raises(ValueError, match="must be str"):
            validate_ilc_object_keys_str_only(obj)

    def test_mixed_keys_rejected(self):
        """Mixed str and bytes keys rejected."""
        obj = {"a": 1, b"b": 2}
        with pytest.raises(ValueError, match="must be str"):
            validate_ilc_object_keys_str_only(obj)

    def test_nested_dict_bytes_key_rejected_with_path(self):
        """Nested dict with bytes key shows path in error."""
        obj = {"a": {"b": {b"c": 1}}}
        with pytest.raises(ValueError, match=r"path.*\.a\.b"):
            validate_ilc_object_keys_str_only(obj)

    def test_list_contains_dict_bytes_key_rejected(self):
        """List containing dict with bytes key is rejected."""
        obj = {"a": [{"x": 1}, {b"y": 2}]}
        with pytest.raises(ValueError, match="must be str"):
            validate_ilc_object_keys_str_only(obj)

    def test_error_includes_key_type(self):
        """Error message includes the offending key type."""
        obj = {b"key": "value"}
        with pytest.raises(ValueError, match="bytes"):
            validate_ilc_object_keys_str_only(obj)

    def test_str_keys_pass(self):
        """All str keys pass validation."""
        obj = {"a": {"b": {"c": 1}}}
        validate_ilc_object_keys_str_only(obj)  # Should not raise

    def test_bytes_values_allowed(self):
        """Bytes are allowed as values, just not keys."""
        obj = {"a": b"\x00\x01\x02", "b": {"c": b"data"}}
        validate_ilc_object_keys_str_only(obj)  # Should not raise


class TestIsIlcObjectKeysStrOnly:
    """Tests for is_ilc_object_keys_str_only boolean helper."""

    def test_returns_false_for_bytes_keys(self):
        """Returns False for objects with bytes keys."""
        assert is_ilc_object_keys_str_only({b"a": 1}) is False

    def test_returns_true_for_str_keys(self):
        """Returns True for objects with only str keys."""
        assert is_ilc_object_keys_str_only({"a": 1}) is True

    def test_returns_true_for_primitives(self):
        """Returns True for primitives (no keys to check)."""
        assert is_ilc_object_keys_str_only(42) is True
        assert is_ilc_object_keys_str_only("hello") is True
        assert is_ilc_object_keys_str_only(None) is True


class TestDecodeDagCborStrict:
    """Tests for decode_dag_cbor_strict."""

    def test_rejects_bytes_key_cbor(self):
        """Strict decode rejects CBOR with bytes key.
        
        CBOR bytes: map(1){bytes("a"): 1}
        - a1 = map with 1 pair
        - 41 61 = bytes(1) containing 0x61 ('a')
        - 01 = unsigned int 1
        """
        cbor_bytes_key = b"\xa1\x41\x61\x01"
        with pytest.raises(ValueError, match="must be str"):
            decode_dag_cbor_strict(cbor_bytes_key)

    def test_permissive_decode_accepts_bytes_key(self):
        """Permissive decode allows bytes keys (for contrast)."""
        cbor_bytes_key = b"\xa1\x41\x61\x01"
        obj = decode_dag_cbor(cbor_bytes_key)
        assert obj == {b"a": 1}

    def test_strict_decode_accepts_str_keys(self):
        """Strict decode allows str keys."""
        obj = {"hello": "world"}
        encoded = encode_dag_cbor(obj)
        decoded = decode_dag_cbor_strict(encoded)
        assert decoded == obj


class TestValidateCanonicalIlcDagCbor:
    """Tests for validate_canonical_ilc_dag_cbor."""

    def test_rejects_bytes_key_even_if_canonical(self):
        """Strict canonical validator rejects bytes keys."""
        # Create CBOR with bytes key that would be "canonical"
        cbor_bytes_key = b"\xa1\x41\x61\x01"
        with pytest.raises(ValueError):
            validate_canonical_ilc_dag_cbor(cbor_bytes_key)

    def test_accepts_canonical_str_key_cbor(self):
        """Accepts canonical CBOR with str keys."""
        obj = {"a": 1, "b": 2}
        encoded = encode_dag_cbor(obj)
        validate_canonical_ilc_dag_cbor(encoded)  # Should not raise


class TestIsCanonicalIlcDagCbor:
    """Tests for is_canonical_ilc_dag_cbor."""

    def test_returns_false_for_bytes_keys(self):
        """Returns False for CBOR with bytes keys."""
        cbor_bytes_key = b"\xa1\x41\x61\x01"
        assert is_canonical_ilc_dag_cbor(cbor_bytes_key) is False

    def test_returns_true_for_canonical_str_keys(self):
        """Returns True for canonical CBOR with str keys."""
        obj = {"a": 1}
        encoded = encode_dag_cbor(obj)
        assert is_canonical_ilc_dag_cbor(encoded) is True


class TestNodeIdRejectsNonStrKeys:
    """Tests that NodeID generation rejects non-str keys."""

    def test_node_id_rejects_bytes_key(self):
        """node_id_from_obj rejects objects with bytes keys."""
        with pytest.raises(ValueError, match="must be str"):
            node_id_from_obj({b"a": 1})

    def test_node_id_rejects_nested_bytes_key(self):
        """node_id_from_obj rejects nested bytes keys."""
        with pytest.raises(ValueError, match="must be str"):
            node_id_from_obj({"outer": {b"inner": 1}})

    def test_node_id_accepts_bytes_values(self):
        """node_id_from_obj accepts bytes as values."""
        # Should not raise
        nid = node_id_from_obj({"data": b"\x00\x01\x02"})
        assert nid.startswith("b")

    def test_node_id_accepts_str_keys(self):
        """node_id_from_obj accepts str keys."""
        nid = node_id_from_obj({"a": 1, "b": 2})
        assert nid.startswith("b")


class TestTupleBypassPrevention:
    """Tests ensuring tuples cannot bypass the str-only key policy."""

    def test_validate_strict_rejects_bytes_key_inside_tuple(self):
        """Validator catches bytes keys inside tuple."""
        obj = ({"ok": 1}, {b"nope": 2})
        with pytest.raises(ValueError, match="must be str"):
            validate_ilc_object_keys_str_only(obj)

    def test_node_id_from_obj_rejects_bytes_key_inside_tuple(self):
        """NodeID hashing rejects tuple-wrapped bytes key."""
        obj = ({"a": 1}, {b"b": 2})
        with pytest.raises(ValueError, match="must be str"):
            node_id_from_obj(obj)

    def test_node_id_from_obj_allows_tuple_with_str_keys(self):
        """Valid tuple structure with str keys works."""
        obj = ({"a": 1}, {"b": 2})
        nid = node_id_from_obj(obj)
        assert isinstance(nid, str)
        assert nid.startswith("b")

    def test_deeply_nested_tuple_bytes_key_rejected(self):
        """Deeply nested bytes key inside tuple is rejected."""
        obj = {"outer": ({"inner": ({b"bad": 1},)},)}
        with pytest.raises(ValueError, match="must be str"):
            validate_ilc_object_keys_str_only(obj)

    def test_mixed_list_tuple_bytes_key_rejected(self):
        """Mixed list/tuple nesting with bytes key is rejected."""
        obj = [{"a": ({"b": [{b"c": 1}]},)}]
        with pytest.raises(ValueError, match="must be str"):
            validate_ilc_object_keys_str_only(obj)

