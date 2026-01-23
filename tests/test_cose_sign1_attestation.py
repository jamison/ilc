"""
Tests for COSE Sign1 attestation blocks.

Verifies:
- Sign/verify roundtrip
- Tampering detection
- Wrong key rejection
- Canonical encoding enforcement
- NodeID computation
"""

import pytest

from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.exceptions import InvalidSignature

from ilc_core.encoding.dag_cbor import encode_dag_cbor, decode_dag_cbor
from ilc_core.encoding.cidv1 import node_id_from_bytes, node_id_from_obj
from ilc_core.crypto.cbor_canonical import cbor_dumps_canonical, cbor_loads
from ilc_core.crypto.cose_sign1 import (
    cose_sign1_sign,
    cose_sign1_decode,
    cose_sign1_verify,
    validate_canonical_cose_sign1_bytes,
    COSE_TAG_SIGN1,
    COSE_ALG_EDDSA,
)


# Fixed test keys (deterministic for reproducibility)
TEST_PRIVATE_KEY_BYTES = bytes.fromhex(
    "9d61b19deffd5a60ba844af492ec2cc44449c5697b326919703bac031cae7f60"
)
TEST_PRIVATE_KEY = ed25519.Ed25519PrivateKey.from_private_bytes(TEST_PRIVATE_KEY_BYTES)
TEST_PUBLIC_KEY = TEST_PRIVATE_KEY.public_key()

# Different key pair for wrong-key tests
OTHER_PRIVATE_KEY = ed25519.Ed25519PrivateKey.generate()
OTHER_PUBLIC_KEY = OTHER_PRIVATE_KEY.public_key()


class TestCoseSign1Roundtrip:
    """Tests for sign/verify roundtrip."""

    def test_sign_verify_roundtrip_ok(self):
        """Sign and verify a payload successfully."""
        payload = encode_dag_cbor({"a": 1, "b": [2, 3]})
        
        cose_bytes = cose_sign1_sign(payload, TEST_PRIVATE_KEY)
        result = cose_sign1_verify(cose_bytes, TEST_PUBLIC_KEY)
        
        assert result["payload"] == payload
        assert result["alg"] == COSE_ALG_EDDSA
        assert result["nodeid"] == node_id_from_bytes(payload)

    def test_verify_returns_correct_nodeid(self):
        """Verify returns NodeID matching node_id_from_obj."""
        obj = {"hello": "world", "count": 42}
        payload = encode_dag_cbor(obj)
        
        cose_bytes = cose_sign1_sign(payload, TEST_PRIVATE_KEY)
        result = cose_sign1_verify(cose_bytes, TEST_PUBLIC_KEY)
        
        assert result["nodeid"] == node_id_from_obj(obj)


class TestCoseSign1TamperDetection:
    """Tests for tampering detection."""

    def test_verify_rejects_tampered_payload(self):
        """Flipping a byte in payload causes signature failure."""
        payload = encode_dag_cbor({"secret": "data"})
        cose_bytes = cose_sign1_sign(payload, TEST_PRIVATE_KEY)
        
        # Decode, tamper, re-encode
        from cbor2 import CBORTag
        obj = cbor_loads(cose_bytes)
        cose_array = list(obj.value)
        tampered_payload = bytes([cose_array[2][0] ^ 0xFF]) + cose_array[2][1:]
        cose_array[2] = tampered_payload
        tampered_cose = cbor_dumps_canonical(CBORTag(COSE_TAG_SIGN1, cose_array))
        
        with pytest.raises((InvalidSignature, ValueError)):
            cose_sign1_verify(tampered_cose, TEST_PUBLIC_KEY)

    def test_verify_rejects_tampered_signature(self):
        """Flipping a byte in signature causes verification failure."""
        payload = encode_dag_cbor({"a": 1})
        cose_bytes = cose_sign1_sign(payload, TEST_PRIVATE_KEY)
        
        from cbor2 import CBORTag
        obj = cbor_loads(cose_bytes)
        cose_array = list(obj.value)
        tampered_sig = bytes([cose_array[3][0] ^ 0xFF]) + cose_array[3][1:]
        cose_array[3] = tampered_sig
        tampered_cose = cbor_dumps_canonical(CBORTag(COSE_TAG_SIGN1, cose_array))
        
        with pytest.raises(InvalidSignature):
            cose_sign1_verify(tampered_cose, TEST_PUBLIC_KEY)


class TestCoseSign1WrongKey:
    """Tests for wrong key rejection."""

    def test_verify_rejects_wrong_key(self):
        """Verify with different public key must fail."""
        payload = encode_dag_cbor({"a": 1})
        cose_bytes = cose_sign1_sign(payload, TEST_PRIVATE_KEY)
        
        with pytest.raises(InvalidSignature):
            cose_sign1_verify(cose_bytes, OTHER_PUBLIC_KEY)


class TestCoseSign1CanonicalEnforcement:
    """Tests for canonical encoding enforcement."""

    def test_decode_rejects_non_canonical_outer_cbor(self):
        """Non-canonical outer CBOR is rejected."""
        payload = encode_dag_cbor({"a": 1})
        cose_bytes = cose_sign1_sign(payload, TEST_PRIVATE_KEY)
        
        # Create non-canonical by adding padding (extra 0 byte)
        non_canonical = cose_bytes + b"\x00"
        
        with pytest.raises(ValueError):
            cose_sign1_decode(non_canonical)

    def test_decode_rejects_non_tag18(self):
        """Wrong tag number is rejected."""
        payload = encode_dag_cbor({"a": 1})
        
        # Create valid array but with wrong tag
        from cbor2 import CBORTag
        protected = cbor_dumps_canonical({1: -8})
        cose_array = [protected, {}, payload, b"\x00" * 64]
        wrong_tag = cbor_dumps_canonical(CBORTag(99, cose_array))
        
        with pytest.raises(ValueError, match="tag 18"):
            cose_sign1_decode(wrong_tag)

    def test_decode_rejects_wrong_shape(self):
        """Wrong array length is rejected."""
        from cbor2 import CBORTag
        cose_array = [b"", {}, b""]  # Only 3 elements
        wrong_shape = cbor_dumps_canonical(CBORTag(COSE_TAG_SIGN1, cose_array))
        
        with pytest.raises(ValueError, match="4 elements"):
            cose_sign1_decode(wrong_shape)

    def test_decode_rejects_payload_not_bstr(self):
        """Payload not bytes is rejected."""
        from cbor2 import CBORTag
        protected = cbor_dumps_canonical({1: -8})
        cose_array = [protected, {}, "not bytes", b"\x00" * 64]
        bad = cbor_dumps_canonical(CBORTag(COSE_TAG_SIGN1, cose_array))
        
        with pytest.raises(ValueError, match="payload must be bstr"):
            cose_sign1_decode(bad)


class TestCoseSign1PayloadValidation:
    """Tests for ILC payload validation."""

    def test_sign_rejects_non_canonical_ilc_payload(self):
        """Non-canonical DAG-CBOR payload is rejected during signing."""
        # Create non-canonical by encoding with wrong key order
        # (our encoder is always canonical, so we craft raw bytes)
        # Map {b:1, a:2} in wrong order: a2 61 62 01 61 61 02
        non_canonical_payload = b"\xa2\x61\x62\x01\x61\x61\x02"
        
        with pytest.raises(ValueError, match="[Nn]on-canonical"):
            cose_sign1_sign(non_canonical_payload, TEST_PRIVATE_KEY)

    def test_verify_rejects_payload_with_bytes_keys(self):
        """Payload with bytes keys is rejected during verification."""
        # Create payload with bytes key using permissive encoder
        # CBOR: map(1){bytes("a"): 1} = a1 41 61 01
        bytes_key_payload = b"\xa1\x41\x61\x01"
        
        with pytest.raises(ValueError, match="str"):
            cose_sign1_sign(bytes_key_payload, TEST_PRIVATE_KEY)


class TestCoseSign1Determinism:
    """Tests for deterministic output."""

    def test_determinism_same_input_same_output(self):
        """Signing twice yields identical COSE bytes."""
        payload = encode_dag_cbor({"x": 123, "y": [4, 5, 6]})
        
        cose1 = cose_sign1_sign(payload, TEST_PRIVATE_KEY)
        cose2 = cose_sign1_sign(payload, TEST_PRIVATE_KEY)
        
        assert cose1 == cose2

    def test_determinism_with_kid(self):
        """Signing with kid is also deterministic."""
        payload = encode_dag_cbor({"a": 1})
        kid = b"my-key-id"
        
        cose1 = cose_sign1_sign(payload, TEST_PRIVATE_KEY, kid=kid)
        cose2 = cose_sign1_sign(payload, TEST_PRIVATE_KEY, kid=kid)
        
        assert cose1 == cose2


class TestCoseSign1Kid:
    """Tests for key identifier (kid) handling."""

    def test_kid_is_protected_and_roundtrips(self):
        """Kid is stored in protected header and roundtrips."""
        payload = encode_dag_cbor({"a": 1})
        kid = b"my-key-id"
        
        cose_bytes = cose_sign1_sign(payload, TEST_PRIVATE_KEY, kid=kid)
        result = cose_sign1_verify(cose_bytes, TEST_PUBLIC_KEY)
        
        assert result["kid"] == kid
        assert result["protected"][4] == kid  # Header label 4 = kid

    def test_kid_none_when_not_provided(self):
        """Kid is None when not provided."""
        payload = encode_dag_cbor({"a": 1})
        
        cose_bytes = cose_sign1_sign(payload, TEST_PRIVATE_KEY)
        result = cose_sign1_verify(cose_bytes, TEST_PUBLIC_KEY)
        
        assert result["kid"] is None


class TestCoseSign1MVPGuardrails:
    """Tests for ILC MVP restrictions (Phase 66B-FIX1)."""

    def test_decode_rejects_nonempty_unprotected_header(self):
        """Non-empty unprotected header is rejected per MVP policy."""
        from cbor2 import CBORTag
        
        payload = encode_dag_cbor({"a": 1})
        protected = cbor_dumps_canonical({1: -8})  # alg = EdDSA
        # Non-empty unprotected header (kid in wrong place)
        unprotected = {4: b"some-key-id"}
        cose_array = [protected, unprotected, payload, b"\x00" * 64]
        bad_cose = cbor_dumps_canonical(CBORTag(COSE_TAG_SIGN1, cose_array))
        
        with pytest.raises(ValueError, match="unprotected headers must be empty"):
            cose_sign1_decode(bad_cose)

    def test_decode_rejects_alg_in_unprotected_even_if_protected_correct(self):
        """Even if protected header is correct, non-empty unprotected is rejected."""
        from cbor2 import CBORTag
        
        payload = encode_dag_cbor({"test": "data"})
        protected = cbor_dumps_canonical({1: -8})
        # Redundant alg in unprotected (attack vector)
        unprotected = {1: -8}
        cose_array = [protected, unprotected, payload, b"\x00" * 64]
        bad_cose = cbor_dumps_canonical(CBORTag(COSE_TAG_SIGN1, cose_array))
        
        with pytest.raises(ValueError, match="unprotected headers must be empty"):
            cose_sign1_decode(bad_cose)

    def test_sign_produces_canonical_cose_bytes(self):
        """Signed COSE bytes pass canonical CBOR validation."""
        from ilc_core.crypto.cbor_canonical import validate_canonical_cbor_bytes
        
        payload = encode_dag_cbor({"x": 1, "y": 2})
        cose_bytes = cose_sign1_sign(payload, TEST_PRIVATE_KEY)
        
        # Should not raise
        validate_canonical_cbor_bytes(cose_bytes)

    def test_sign_produces_empty_unprotected_header(self):
        """Signing always produces empty unprotected header."""
        payload = encode_dag_cbor({"a": 1})
        cose_bytes = cose_sign1_sign(payload, TEST_PRIVATE_KEY)
        
        result = cose_sign1_decode(cose_bytes)
        assert result["unprotected"] == {}

