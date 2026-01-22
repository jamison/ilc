"""
Tests for CIDv1 NodeID generation and parsing.

Verifies:
- NodeID stability (same object always produces same ID)
- NodeID determinism (insertion order doesn't matter)
- Mutation detection (different objects produce different IDs)
- Parse correctness (CID components can be extracted)
"""

import base64
import pytest

from ilc_core.encoding.cidv1 import (
    node_id_from_obj,
    parse_cidv1,
    parse_nodeid_strict,
    is_nodeid,
    CODEC_DAG_CBOR,
    MH_SHA2_256,
    SHA2_256_LEN,
)
from ilc_core.encoding.varint import encode_uvarint


class TestNodeIdStability:
    """Tests for NodeID stability and determinism."""

    def test_same_object_produces_same_id(self):
        """Repeated calls produce identical NodeID."""
        obj = {"a": 1, "b": [2, 3]}
        id1 = node_id_from_obj(obj)
        id2 = node_id_from_obj(obj)
        id3 = node_id_from_obj(obj)
        assert id1 == id2 == id3

    def test_insertion_order_does_not_affect_id(self):
        """Dict insertion order doesn't change NodeID."""
        a = {"a": 1, "b": 2}
        b = {"b": 2, "a": 1}
        assert node_id_from_obj(a) == node_id_from_obj(b)

    def test_nested_dict_order_independent(self):
        """Nested dict insertion order doesn't change NodeID."""
        a = {"outer": {"z": 1, "a": 2}}
        b = {"outer": {"a": 2, "z": 1}}
        assert node_id_from_obj(a) == node_id_from_obj(b)


class TestNodeIdMutationDetection:
    """Tests that mutations produce different IDs."""

    def test_value_change_changes_id(self):
        """Changing a value produces a different NodeID."""
        assert node_id_from_obj({"a": 1}) != node_id_from_obj({"a": 2})

    def test_key_change_changes_id(self):
        """Changing a key produces a different NodeID."""
        assert node_id_from_obj({"a": 1}) != node_id_from_obj({"b": 1})

    def test_added_field_changes_id(self):
        """Adding a field produces a different NodeID."""
        assert node_id_from_obj({"a": 1}) != node_id_from_obj({"a": 1, "b": 2})

    def test_removed_field_changes_id(self):
        """Removing a field produces a different NodeID."""
        assert node_id_from_obj({"a": 1, "b": 2}) != node_id_from_obj({"a": 1})

    def test_type_change_changes_id(self):
        """Changing type produces a different NodeID."""
        assert node_id_from_obj({"a": 1}) != node_id_from_obj({"a": "1"})
        assert node_id_from_obj([1, 2]) != node_id_from_obj((1, 2, 3))


class TestParseCorrectness:
    """Tests for CID parsing."""

    def test_parse_returns_correct_version(self):
        """Parsed CID has version 1."""
        cid = node_id_from_obj({"a": 1})
        info = parse_cidv1(cid)
        assert info["version"] == 1

    def test_parse_returns_correct_codec(self):
        """Parsed CID has DAG-CBOR codec."""
        cid = node_id_from_obj({"a": 1})
        info = parse_cidv1(cid)
        assert info["codec"] == CODEC_DAG_CBOR

    def test_parse_returns_correct_hash_code(self):
        """Parsed CID has SHA2-256 hash code."""
        cid = node_id_from_obj({"a": 1})
        info = parse_cidv1(cid)
        assert info["mh_code"] == MH_SHA2_256

    def test_parse_returns_correct_digest_length(self):
        """Parsed CID has 32-byte digest."""
        cid = node_id_from_obj({"a": 1})
        info = parse_cidv1(cid)
        assert info["digest_len"] == SHA2_256_LEN

    def test_parse_returns_hex_digest(self):
        """Parsed CID includes hex-encoded digest."""
        cid = node_id_from_obj({"a": 1})
        info = parse_cidv1(cid)
        assert len(info["digest_hex"]) == 64  # 32 bytes = 64 hex chars
        # Should be valid hex
        int(info["digest_hex"], 16)


class TestCidFormat:
    """Tests for CID string format."""

    def test_cid_starts_with_b(self):
        """CID starts with 'b' (base32 lowercase multibase prefix)."""
        cid = node_id_from_obj({"test": True})
        assert cid.startswith("b")

    def test_cid_is_lowercase(self):
        """CID is lowercase (except for 'b' prefix which is also lowercase)."""
        cid = node_id_from_obj({"test": True})
        assert cid == cid.lower()

    def test_cid_has_no_padding(self):
        """CID has no base32 padding characters."""
        cid = node_id_from_obj({"test": True})
        assert "=" not in cid

    def test_cid_roundtrip_through_parse(self):
        """CID can be parsed and the digest extracted."""
        obj = {"complex": [1, 2, {"nested": b"data"}]}
        cid = node_id_from_obj(obj)
        info = parse_cidv1(cid)
        
        # Verify structure
        assert info["version"] == 1
        assert info["codec"] == CODEC_DAG_CBOR
        assert info["mh_code"] == MH_SHA2_256
        assert info["digest_len"] == 32


class TestErrorHandling:
    """Tests for error handling."""

    def test_invalid_multibase_prefix_raises(self):
        """Non-'b' multibase prefix raises error."""
        with pytest.raises(ValueError, match="Expected base32lower"):
            parse_cidv1("z" + "a" * 50)

    def test_invalid_base32_raises(self):
        """Invalid base32 characters raise error."""
        with pytest.raises(ValueError, match="Invalid base32"):
            parse_cidv1("b" + "!!invalid!!")


class TestNodeIdStrictness:
    """Tests for strict NodeID parsing and validation."""

    def _cid_str(self, version, codec, mh_code, digest_len):
        digest = b"\x00" * digest_len
        raw = (
            encode_uvarint(version)
            + encode_uvarint(codec)
            + encode_uvarint(mh_code)
            + encode_uvarint(digest_len)
            + digest
        )
        b32 = base64.b32encode(raw).decode("ascii").lower().rstrip("=")
        return "b" + b32

    def test_wrong_codec_fails(self):
        """Non-dag-cbor codec is rejected."""
        cid = self._cid_str(1, 0x70, MH_SHA2_256, SHA2_256_LEN)
        with pytest.raises(ValueError, match="expected codec dag-cbor"):
            parse_nodeid_strict(cid)

    def test_wrong_multihash_code_fails(self):
        """Non-sha2-256 multihash is rejected."""
        cid = self._cid_str(1, CODEC_DAG_CBOR, 0x13, SHA2_256_LEN)
        with pytest.raises(ValueError, match="expected multihash sha2-256"):
            parse_nodeid_strict(cid)

    def test_wrong_digest_length_fails(self):
        """Non-32-byte digest length is rejected."""
        cid = self._cid_str(1, CODEC_DAG_CBOR, MH_SHA2_256, 16)
        with pytest.raises(ValueError, match="expected digest length"):
            parse_nodeid_strict(cid)

    def test_wrong_version_fails(self):
        """Non-v1 CID is rejected."""
        cid = self._cid_str(0, CODEC_DAG_CBOR, MH_SHA2_256, SHA2_256_LEN)
        with pytest.raises(ValueError, match="expected CIDv1"):
            parse_nodeid_strict(cid)

    def test_is_nodeid_true_for_valid(self):
        """is_nodeid returns True for valid NodeIDs."""
        cid = node_id_from_obj({"a": 1})
        assert is_nodeid(cid) is True

    def test_is_nodeid_false_for_invalid(self):
        """is_nodeid returns False for invalid NodeIDs."""
        cid = self._cid_str(1, 0x70, MH_SHA2_256, SHA2_256_LEN)
        assert is_nodeid(cid) is False
