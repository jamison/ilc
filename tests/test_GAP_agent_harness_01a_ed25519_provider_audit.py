from __future__ import annotations

import pytest
from cbor2 import CBORTag
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric import ed25519

from ilc_core.crypto.cbor_canonical import cbor_dumps_canonical, cbor_loads
from ilc_core.crypto.cose_sign1 import (
    COSE_ALG_EDDSA,
    COSE_HDR_ALG,
    COSE_TAG_SIGN1,
    cose_sign1_decode,
    cose_sign1_sign,
    cose_sign1_verify,
)
from ilc_core.encoding.dag_cbor import encode_dag_cbor


TEST_PRIVATE_KEY_BYTES = bytes.fromhex(
    "9d61b19deffd5a60ba844af492ec2cc44449c5697b326919703bac031cae7f60"
)
TEST_PRIVATE_KEY = ed25519.Ed25519PrivateKey.from_private_bytes(TEST_PRIVATE_KEY_BYTES)
TEST_PUBLIC_KEY = TEST_PRIVATE_KEY.public_key()


def _payload() -> bytes:
    return encode_dag_cbor({"audit": "gap-agent-harness-01a", "seq": 1})


def _replace_cose_field(cose_bytes: bytes, *, index: int, value: object) -> bytes:
    obj = cbor_loads(cose_bytes)
    cose_array = list(obj.value)
    cose_array[index] = value
    return cbor_dumps_canonical(CBORTag(COSE_TAG_SIGN1, cose_array))


def test_ed25519_sign_and_verify_round_trip() -> None:
    payload = _payload()

    cose_bytes = cose_sign1_sign(payload, TEST_PRIVATE_KEY)
    verified = cose_sign1_verify(cose_bytes, TEST_PUBLIC_KEY)

    assert verified["payload"] == payload
    assert verified["alg"] == COSE_ALG_EDDSA
    assert isinstance(verified["nodeid"], str)


def test_tampered_payload_fails_verify() -> None:
    cose_bytes = cose_sign1_sign(_payload(), TEST_PRIVATE_KEY)
    tampered_payload = encode_dag_cbor({"audit": "gap-agent-harness-01a", "seq": 2})
    tampered_cose = _replace_cose_field(cose_bytes, index=2, value=tampered_payload)

    with pytest.raises(InvalidSignature):
        cose_sign1_verify(tampered_cose, TEST_PUBLIC_KEY)


def test_algorithm_guard_rejects_non_eddsa() -> None:
    protected = cbor_dumps_canonical({COSE_HDR_ALG: -7})
    cose_array = [protected, {}, _payload(), b"\x00" * 64]
    bad_alg_cose = cbor_dumps_canonical(CBORTag(COSE_TAG_SIGN1, cose_array))

    with pytest.raises(ValueError, match="EdDSA|-8"):
        cose_sign1_verify(bad_alg_cose, TEST_PUBLIC_KEY)


def test_invalid_signature_length_fails() -> None:
    cose_bytes = cose_sign1_sign(_payload(), TEST_PRIVATE_KEY)
    bad_length_cose = _replace_cose_field(cose_bytes, index=3, value=b"\x00" * 32)

    with pytest.raises(ValueError, match="64 bytes"):
        cose_sign1_verify(bad_length_cose, TEST_PUBLIC_KEY)


def test_sign_decode_round_trip_matches_input() -> None:
    payload = _payload()
    cose_bytes = cose_sign1_sign(payload, TEST_PRIVATE_KEY)
    decoded = cose_sign1_decode(cose_bytes)

    assert decoded["payload"] == payload
    assert decoded["alg"] == COSE_ALG_EDDSA


def test_kid_preserved_in_protected_header() -> None:
    payload = _payload()
    kid = b"gap-agent-harness-01a-key"
    cose_bytes = cose_sign1_sign(payload, TEST_PRIVATE_KEY, kid=kid)
    decoded = cose_sign1_decode(cose_bytes)

    assert decoded["kid"] == kid
    assert decoded["protected"][4] == kid


def test_external_aad_contributes_to_signature() -> None:
    cose_bytes = cose_sign1_sign(
        _payload(),
        TEST_PRIVATE_KEY,
        external_aad=b"gap-agent-harness-01a",
    )

    with pytest.raises(InvalidSignature):
        cose_sign1_verify(cose_bytes, TEST_PUBLIC_KEY, external_aad=b"wrong-aad")
