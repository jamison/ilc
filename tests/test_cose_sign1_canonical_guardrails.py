"""
COSE Sign1 canonical guardrail tests.

Phase 66B-FIX2: Ensures COSE blocks stay canonical under MVP policy.
These tests verify that non-canonical encodings are rejected.
"""

import pytest
from cbor2 import CBORTag

from cryptography.hazmat.primitives.asymmetric import ed25519

from ilc_core.encoding.dag_cbor import encode_dag_cbor
from ilc_core.crypto.cbor_canonical import (
    cbor_dumps_canonical,
    cbor_loads,
    validate_canonical_cbor_bytes,
)
from ilc_core.crypto.cose_sign1 import (
    cose_sign1_sign,
    cose_sign1_decode,
    cose_sign1_verify,
    validate_canonical_cose_sign1_bytes,
    COSE_TAG_SIGN1,
    COSE_ALG_EDDSA,
    COSE_HDR_ALG,
    COSE_HDR_KID,
)


# Fixed test key for reproducibility
TEST_PRIVATE_KEY_BYTES = bytes.fromhex(
    "9d61b19deffd5a60ba844af492ec2cc44449c5697b326919703bac031cae7f60"
)
TEST_PRIVATE_KEY = ed25519.Ed25519PrivateKey.from_private_bytes(TEST_PRIVATE_KEY_BYTES)
TEST_PUBLIC_KEY = TEST_PRIVATE_KEY.public_key()


class TestCoseOuterNonCanonical:
    """Tests for outer COSE bytes canonicality."""

    def test_outer_cose_bytes_must_be_canonical(self):
        """Non-canonical outer CBOR encoding is rejected."""
        payload = encode_dag_cbor({"a": 1})
        cose_bytes = cose_sign1_sign(payload, TEST_PRIVATE_KEY)
        
        # Verify it passes first
        validate_canonical_cose_sign1_bytes(cose_bytes)
        
        # Create non-canonical by appending trailing bytes.
        # CBOR decoders should reject extra trailing data after a valid structure.
        non_canonical = cose_bytes + b"\x00"
        
        with pytest.raises(ValueError, match="[Nn]on-canonical|Invalid"):
            validate_canonical_cose_sign1_bytes(non_canonical)


class TestCoseProtectedHeaderCanonical:
    """Tests for protected header canonicality."""

    def test_protected_header_must_be_canonical(self):
        """Non-canonical protected header bytes are rejected."""
        payload = encode_dag_cbor({"x": 1})
        
        # Create a protected header with non-canonical encoding
        # Canonical: {1: -8} encodes as a1 01 27 (map(1), key 1, value -8)
        # Non-canonical: use 2-byte encoding for the key
        # {1: -8} with key 1 encoded as 0x18 0x01 instead of 0x01
        non_canonical_protected = b"\xa1\x18\x01\x27"  # map(1), 2-byte key 1, value -8
        
        # Build COSE structure with non-canonical protected header
        cose_array = [
            non_canonical_protected,  # Non-canonical protected
            {},                       # Empty unprotected
            payload,
            b"\x00" * 64,            # Fake signature
        ]
        bad_cose = cbor_dumps_canonical(CBORTag(COSE_TAG_SIGN1, cose_array))
        
        with pytest.raises(ValueError, match="[Nn]on-canonical"):
            cose_sign1_decode(bad_cose)


class TestCoseUnprotectedMustBeEmpty:
    """Tests for unprotected header MVP restriction."""

    def test_reject_nonempty_unprotected_header(self):
        """Non-empty unprotected header rejected per MVP policy."""
        payload = encode_dag_cbor({"a": 1})
        protected = cbor_dumps_canonical({COSE_HDR_ALG: COSE_ALG_EDDSA})
        
        # Non-empty unprotected header
        unprotected = {99: b"extra-data"}
        
        cose_array = [protected, unprotected, payload, b"\x00" * 64]
        bad_cose = cbor_dumps_canonical(CBORTag(COSE_TAG_SIGN1, cose_array))
        
        with pytest.raises(ValueError, match="unprotected headers must be empty"):
            cose_sign1_decode(bad_cose)

    def test_reject_even_standard_headers_in_unprotected(self):
        """Even standard COSE headers in unprotected are rejected for MVP."""
        payload = encode_dag_cbor({"test": "data"})
        protected = cbor_dumps_canonical({COSE_HDR_ALG: COSE_ALG_EDDSA})
        
        # Put content-type (3) in unprotected - valid COSE but rejected for ILC MVP
        unprotected = {3: "application/cbor"}
        
        cose_array = [protected, unprotected, payload, b"\x00" * 64]
        bad_cose = cbor_dumps_canonical(CBORTag(COSE_TAG_SIGN1, cose_array))
        
        with pytest.raises(ValueError, match="unprotected headers must be empty"):
            cose_sign1_decode(bad_cose)

    def test_reject_wrong_length_signature_at_decode_boundary(self):
        """Malformed Ed25519 signature lengths fail before cryptographic verify."""
        payload = encode_dag_cbor({"a": 1})
        protected = cbor_dumps_canonical({COSE_HDR_ALG: COSE_ALG_EDDSA})
        cose_array = [protected, {}, payload, b"\x00" * 63]
        bad_cose = cbor_dumps_canonical(CBORTag(COSE_TAG_SIGN1, cose_array))

        with pytest.raises(ValueError, match="EdDSA signature must be 64 bytes"):
            cose_sign1_decode(bad_cose)


class TestCosePayloadCanonical:
    """Tests for payload canonicality and ILC strict rules."""

    def test_payload_must_be_canonical_dag_cbor(self):
        """Non-canonical DAG-CBOR payload is rejected during verification."""
        # Create non-canonical payload: map {b:1, a:2} with wrong key order
        # Canonical order: a, b (shorter or lexicographically first)
        # This encodes {b:1, a:2} with b first, which is non-canonical
        non_canonical_payload = b"\xa2\x61\x62\x01\x61\x61\x02"
        
        with pytest.raises(ValueError, match="[Nn]on-canonical"):
            cose_sign1_sign(non_canonical_payload, TEST_PRIVATE_KEY)

    def test_payload_must_have_string_only_keys(self):
        """Payload with bytes keys is rejected."""
        # CBOR map with bytes key: {b"a": 1}
        # a1 41 61 01 = map(1), bstr(1) "a", int 1
        bytes_key_payload = b"\xa1\x41\x61\x01"
        
        with pytest.raises(ValueError, match="str"):
            cose_sign1_sign(bytes_key_payload, TEST_PRIVATE_KEY)

    def test_nested_bytes_keys_rejected(self):
        """Deeply nested bytes keys are also rejected."""
        # Create payload with nested structure containing bytes key
        # {"outer": {b"inner": 1}} - bytes key at second level
        # This is tricky to construct manually, so we verify via valid outer + invalid inner
        
        # The encoder should reject this, but let's verify via decode path
        # Map: {outer: {bytes("x"): 1}}
        # a1 65 6f 75 74 65 72  a1 41 78 01
        # map(1) str(5) "outer" map(1) bstr(1) "x" int(1)
        nested_bytes_key = b"\xa1\x65\x6f\x75\x74\x65\x72\xa1\x41\x78\x01"
        
        with pytest.raises(ValueError, match="str"):
            cose_sign1_sign(nested_bytes_key, TEST_PRIVATE_KEY)


class TestCoseSignProducesCanonical:
    """Tests that our sign function produces canonical output."""

    def test_sign_output_is_canonical_cbor(self):
        """cose_sign1_sign produces canonical CBOR bytes."""
        payload = encode_dag_cbor({"message": "hello", "seq": 42})
        cose_bytes = cose_sign1_sign(payload, TEST_PRIVATE_KEY)
        
        # Verify outer is canonical
        validate_canonical_cbor_bytes(cose_bytes)
        
        # Verify protected header is canonical
        decoded = cose_sign1_decode(cose_bytes)
        validate_canonical_cbor_bytes(decoded["protected_bstr"])

    def test_sign_determinism_roundtrip(self):
        """Same input produces byte-identical output (determinism)."""
        payload = encode_dag_cbor({"a": 1, "b": 2, "c": [3, 4, 5]})
        
        cose1 = cose_sign1_sign(payload, TEST_PRIVATE_KEY)
        cose2 = cose_sign1_sign(payload, TEST_PRIVATE_KEY)
        
        assert cose1 == cose2, "COSE signing must be deterministic"
