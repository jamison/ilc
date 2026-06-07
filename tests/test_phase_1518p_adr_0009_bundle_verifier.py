"""Phase 1518p ADR-0009 independent bundle verifier tests.

PUBLIC_RC_EXCLUDE: phase_1518p_private_runtime_selftest
PUBLIC_RC_EXCLUDE_REASON: Private ADR-0009 verifier/test-vector selftest. Not a public RC artifact.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from cryptography.hazmat.primitives.asymmetric import ed25519

from ilc_core.bundle.bundle_verifier import verify_adr_0009_bundle, verify_adr_0009_layer
from ilc_core.crypto.cbor_canonical import MAX_CANONICAL_CBOR_INPUT_BYTES


FIXTURE_DIR = Path(__file__).parent / "fixtures" / "adr_0009"


def _fixture(name: str) -> dict:
    with (FIXTURE_DIR / name).open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise TypeError("fixture_root_must_be_object")
    return payload


def _public_key(fixture: dict) -> ed25519.Ed25519PublicKey:
    value = fixture.get("public_key_hex")
    if not isinstance(value, str):
        raise TypeError("fixture_missing_public_key_hex")
    return ed25519.Ed25519PublicKey.from_public_bytes(bytes.fromhex(value))


def _public_keys_by_layer(fixture: dict) -> dict[int, ed25519.Ed25519PublicKey]:
    public_key = _public_key(fixture)
    return {0: public_key, 1: public_key, 2: public_key, 3: public_key}


def test_verifier_module_does_not_import_layer_builders() -> None:
    source = Path("ilc_core/bundle/bundle_verifier.py").read_text(encoding="utf-8")
    assert "from ilc_core.bundle.layer" not in source
    assert "import ilc_core.bundle.layer" not in source
    assert "from .layer" not in source


def test_layer0_valid_test_vector_verifies() -> None:
    fixture = _fixture("bundle_layer0_valid.json")
    layer = fixture["layer"]
    verified = verify_adr_0009_layer(0, layer, public_key=_public_key(fixture))

    assert verified.layer == 0
    assert verified.cidv1 == layer["cidv1"]
    assert verified.payload["layer"] == 0


def test_four_layer_chain_valid_test_vector_verifies() -> None:
    fixture = _fixture("bundle_four_layer_chain_valid.json")
    verified = verify_adr_0009_bundle(fixture, public_keys_by_layer=_public_keys_by_layer(fixture))

    assert [layer.layer for layer in verified.layers] == [0, 1, 2, 3]
    assert verified.layer1.payload["layer0_protocol_bundle_cidv1"] == verified.layer0.cidv1
    assert verified.layer2.payload["layer0_protocol_bundle_cidv1"] == verified.layer0.cidv1
    assert verified.layer2.payload["layer1_genesis_bundle_cidv1"] == verified.layer1.cidv1
    assert verified.layer3.payload["layer2_epoch_snapshot_cidv1"] == verified.layer2.cidv1


def test_tampered_layer1_test_vector_rejected() -> None:
    fixture = _fixture("bundle_tampered_layer1.json")

    with pytest.raises(ValueError, match="adr_0009_bundle_cid_mismatch"):
        verify_adr_0009_bundle(fixture, public_keys_by_layer=_public_keys_by_layer(fixture))


def test_wrong_cose_key_rejected() -> None:
    fixture = _fixture("bundle_four_layer_chain_valid.json")
    wrong_public_key = ed25519.Ed25519PrivateKey.from_private_bytes(bytes(reversed(range(32)))).public_key()

    with pytest.raises(ValueError, match="adr_0009_bundle_cose_signature_invalid"):
        verify_adr_0009_bundle(
            fixture,
            public_keys_by_layer={0: wrong_public_key, 1: wrong_public_key, 2: wrong_public_key, 3: wrong_public_key},
        )


def test_wrong_layer3_cid_linkage_rejected() -> None:
    fixture = _fixture("bundle_wrong_layer3_linkage.json")

    with pytest.raises(ValueError, match="adr_0009_bundle_layer3_layer2_cid_mismatch"):
        verify_adr_0009_bundle(fixture, public_keys_by_layer=_public_keys_by_layer(fixture))


def test_oversized_dag_cbor_hex_rejected_before_allocation() -> None:
    fixture = _fixture("bundle_layer0_valid.json")
    oversized_layer = dict(fixture["layer"])
    oversized_layer["dag_cbor_hex"] = "00" * (MAX_CANONICAL_CBOR_INPUT_BYTES + 1)

    with pytest.raises(ValueError, match="adr_0009_bundle_hex_input_exceeds_max_chars"):
        verify_adr_0009_layer(0, oversized_layer, public_key=_public_key(fixture))


@pytest.mark.parametrize("bad_hex", ["0", "AA", "aa aa"])
def test_dag_cbor_hex_must_be_even_lowercase_contiguous(bad_hex: str) -> None:
    fixture = _fixture("bundle_layer0_valid.json")
    bad_layer = dict(fixture["layer"])
    bad_layer["dag_cbor_hex"] = bad_hex

    with pytest.raises(ValueError, match="adr_0009_bundle_invalid_dag_cbor_hex"):
        verify_adr_0009_layer(0, bad_layer, public_key=_public_key(fixture))
