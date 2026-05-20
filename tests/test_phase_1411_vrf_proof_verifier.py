from pathlib import Path

import pytest

from ilc_core.epistemic import vrf_proof_verifier as verifier
from ilc_core.epistemic import verify_vrf_proof, vrf_beta_from_proof


RFC_9381_APPENDIX_B4_VECTORS = (
    {
        "public_key": "d75a980182b10ab7d54bfed3c964073a0ee172f3daa62325af021a68f707511a",
        "alpha": "",
        "hashed_point": "b8066ebbb706c72b64390324e4a3276f129569eab100c26b9f05011200c1bad9",
        "pi": (
            "7d9c633ffeee27349264cf5c667579fc583b4bda63ab71d001f89c10003ab"
            "46f14adf9a3cd8b8412d9038531e865c341cafa73589b023d14311c331a9ad15ff"
            "2fb37831e00f0acaa6d73bc9997b06501"
        ),
        "beta": (
            "9d574bf9b8302ec0fc1e21c3ec5368269527b87b462ce36dab2d14ccf80"
            "c53cccf6758f058c5b1c856b116388152bbe509ee3b9ecfe63d93c3b4346c1fbc6"
            "c54"
        ),
    },
    {
        "public_key": "3d4017c3e843895a92b70aa74d1b7ebc9c982ccf2ec4968cc0cd55f12af4660c",
        "alpha": "72",
        "hashed_point": "76ac3ccb86158a9104dff819b1ca293426d305fd76b39b13c9356d9b58c08e57",
        "pi": (
            "47b327393ff2dd81336f8a2ef10339112401253b3c714eeda879f12c50907"
            "2ef055b48372bb82efbdce8e10c8cb9a2f9d60e93908f93df1623ad78a86a028d6"
            "bc064dbfc75a6a57379ef855dc6733801"
        ),
        "beta": (
            "38561d6b77b71d30eb97a062168ae12b667ce5c28caccdf76bc88e093e4"
            "635987cd96814ce55b4689b3dd2947f80e59aac7b7675f8083865b46c89b2ce9cc"
            "735"
        ),
    },
    {
        "public_key": "fc51cd8e6218a1a38da47ed00230f0580816ed13ba3303ac5deb911548908025",
        "alpha": "af82",
        "hashed_point": "13d2a8b5ca32db7e98094a61f656a08c6c964344e058879a386a947a4e189ed1",
        "pi": (
            "926e895d308f5e328e7aa159c06eddbe56d06846abf5d98c2512235eaa57f"
            "dce35b46edfc655bc828d44ad09d1150f31374e7ef73027e14760d42e77341fe05"
            "467bb286cc2c9d7fde29120a0b2320d04"
        ),
        "beta": (
            "121b7f9b9aaaa29099fc04a94ba52784d44eac976dd1a3cca458733be5c"
            "d090a7b5fbd148444f17f8daf1fb55cb04b1ae85a626e30a54b4b0f8abf4a43314"
            "a58"
        ),
    },
)


def _vector_bytes(vector: dict[str, str]) -> tuple[bytes, bytes, bytes, bytes]:
    return (
        bytes.fromhex(vector["public_key"]),
        bytes.fromhex(vector["alpha"]),
        bytes.fromhex(vector["pi"]),
        bytes.fromhex(vector["beta"]),
    )


def test_module_records_phase_1411_version_and_tokens() -> None:
    assert verifier.VRF_PROOF_VERIFIER_VERSION == "vrf_proof_verifier_phase_1411.v0.1"
    assert verifier._TOKEN_VRF_IMPLEMENTED == "vrf_proof_verifier_implemented_phase_1411"
    assert (
        verifier._TOKEN_VRF_NOT_ACTIVATED
        == "vrf_proof_verifier_not_activated_phase_1410"
    )
    assert verifier.ALGORITHM == "ECVRF-EDWARDS25519-SHA512-ELL2"
    assert verify_vrf_proof is verifier.verify_vrf_proof
    assert vrf_beta_from_proof is verifier.vrf_beta_from_proof


@pytest.mark.parametrize("vector", RFC_9381_APPENDIX_B4_VECTORS)
def test_verify_vrf_proof_accepts_rfc_9381_appendix_b4_vectors(
    vector: dict[str, str],
) -> None:
    public_key, alpha, pi, _beta = _vector_bytes(vector)

    assert verifier.verify_vrf_proof(pi=pi, public_key=public_key, alpha=alpha) is True


@pytest.mark.parametrize("vector", RFC_9381_APPENDIX_B4_VECTORS)
def test_vrf_beta_from_proof_returns_rfc_9381_appendix_b4_beta(
    vector: dict[str, str],
) -> None:
    public_key, alpha, pi, beta = _vector_bytes(vector)

    assert verifier.vrf_beta_from_proof(pi=pi, public_key=public_key, alpha=alpha) == beta


@pytest.mark.parametrize("vector", RFC_9381_APPENDIX_B4_VECTORS)
def test_encode_to_curve_matches_rfc_9381_appendix_b4_h_values(
    vector: dict[str, str],
) -> None:
    public_key, alpha, _pi, _beta = _vector_bytes(vector)

    point = verifier._encode_to_curve(public_key, alpha)

    assert verifier._encode_point(point).hex() == vector["hashed_point"]


def test_verify_vrf_proof_returns_false_for_tampered_challenge() -> None:
    public_key, alpha, pi, _beta = _vector_bytes(RFC_9381_APPENDIX_B4_VECTORS[0])
    tampered = bytearray(pi)
    tampered[32] ^= 1

    assert (
        verifier.verify_vrf_proof(
            pi=bytes(tampered), public_key=public_key, alpha=alpha
        )
        is False
    )


def test_vrf_beta_from_proof_raises_for_tampered_challenge() -> None:
    public_key, alpha, pi, _beta = _vector_bytes(RFC_9381_APPENDIX_B4_VECTORS[1])
    tampered = bytearray(pi)
    tampered[32] ^= 1

    with pytest.raises(
        verifier.VRFVerificationError, match="vrf_proof_invalid_phase_1411"
    ):
        verifier.vrf_beta_from_proof(
            pi=bytes(tampered), public_key=public_key, alpha=alpha
        )


def test_malformed_inputs_raise_stable_errors() -> None:
    public_key, alpha, pi, _beta = _vector_bytes(RFC_9381_APPENDIX_B4_VECTORS[0])

    with pytest.raises(verifier.VRFVerificationError, match="vrf_pi_wrong_length"):
        verifier.verify_vrf_proof(pi=pi[:-1], public_key=public_key, alpha=alpha)
    with pytest.raises(
        verifier.VRFVerificationError, match="vrf_public_key_wrong_length"
    ):
        verifier.verify_vrf_proof(pi=pi, public_key=public_key[:-1], alpha=alpha)
    with pytest.raises(verifier.VRFVerificationError, match="vrf_alpha_must_be_bytes"):
        verifier.verify_vrf_proof(pi=pi, public_key=public_key, alpha=bytearray(alpha))
    with pytest.raises(verifier.VRFVerificationError, match="vrf_alpha_too_long"):
        verifier.verify_vrf_proof(
            pi=pi, public_key=public_key, alpha=b"x" * (verifier.MAX_ALPHA_LENGTH + 1)
        )


def test_alpha_at_exactly_max_length_is_accepted() -> None:
    """alpha == MAX_ALPHA_LENGTH is valid; only MAX+1 raises."""
    public_key, _alpha, pi, _beta = _vector_bytes(RFC_9381_APPENDIX_B4_VECTORS[0])
    # A 4096-byte alpha won't produce a valid proof against this pi, but it must
    # not raise VRFVerificationError for the length check — it should return False.
    result = verifier.verify_vrf_proof(
        pi=pi, public_key=public_key, alpha=b"x" * verifier.MAX_ALPHA_LENGTH
    )
    assert result is False  # proof mismatch, not a length error


def test_pi_as_bytearray_raises_type_error() -> None:
    public_key, alpha, pi, _beta = _vector_bytes(RFC_9381_APPENDIX_B4_VECTORS[0])
    with pytest.raises(verifier.VRFVerificationError, match="vrf_pi_must_be_bytes"):
        verifier.verify_vrf_proof(
            pi=bytearray(pi), public_key=public_key, alpha=alpha
        )


def test_public_key_as_bytearray_raises_type_error() -> None:
    public_key, alpha, pi, _beta = _vector_bytes(RFC_9381_APPENDIX_B4_VECTORS[0])
    with pytest.raises(
        verifier.VRFVerificationError, match="vrf_public_key_must_be_bytes"
    ):
        verifier.verify_vrf_proof(
            pi=pi, public_key=bytearray(public_key), alpha=alpha
        )


def test_tampered_gamma_fails_verification() -> None:
    """Flipping a bit in the Gamma portion (pi bytes 0-31) must not return True.

    A tampered gamma encoding may either:
    - Produce an invalid point (no square root) → VRFVerificationError raised, or
    - Decode to a valid but wrong point → challenge mismatch → returns False.
    Both are correct rejections per ADR-0042 API contract.
    """
    public_key, alpha, pi, _beta = _vector_bytes(RFC_9381_APPENDIX_B4_VECTORS[2])
    tampered = bytearray(pi)
    tampered[0] ^= 1  # corrupt first byte of gamma

    try:
        result = verifier.verify_vrf_proof(
            pi=bytes(tampered), public_key=public_key, alpha=alpha
        )
        assert result is False
    except verifier.VRFVerificationError:
        pass  # invalid point encoding is also a correct rejection


def test_tampered_scalar_fails_verification() -> None:
    """Flipping a bit in the scalar portion (pi bytes 48-79) must fail."""
    public_key, alpha, pi, _beta = _vector_bytes(RFC_9381_APPENDIX_B4_VECTORS[1])
    tampered = bytearray(pi)
    tampered[48] ^= 1  # corrupt first byte of scalar

    assert (
        verifier.verify_vrf_proof(
            pi=bytes(tampered), public_key=public_key, alpha=alpha
        )
        is False
    )


def test_scalar_at_group_order_raises_stable_error() -> None:
    """pi with scalar == group_order must raise VRFVerificationError (out of range)."""
    public_key, alpha, pi, _beta = _vector_bytes(RFC_9381_APPENDIX_B4_VECTORS[0])
    # Build a pi with scalar = group_order in bytes 48-80 (little-endian)
    q = 2**252 + 27742317777372353535851937790883648493
    tampered = bytearray(pi)
    tampered[48:] = q.to_bytes(32, "little")

    with pytest.raises(
        verifier.VRFVerificationError, match="vrf_scalar_out_of_range"
    ):
        verifier.verify_vrf_proof(
            pi=bytes(tampered), public_key=public_key, alpha=alpha
        )


def test_pynacl_1_6_2_low_level_bindings_are_available() -> None:
    import nacl

    assert nacl.__version__ == "1.6.2"
    assert verifier.PYNACL_LOW_LEVEL_BINDINGS_AVAILABLE is True
    assert "rfc9380_reference_arithmetic" in verifier.PYNACL_BINDING_DISPOSITION


def test_vrf_proof_verifier_has_no_random_or_private_key_operations() -> None:
    source = Path(verifier.__file__).read_text(encoding="utf-8")

    assert "import random" not in source
    assert "secrets.SystemRandom" not in source
    assert "Signing" + "Key" not in source
    assert "Private" + "Key" not in source
    assert "crypto_" + "sign" not in source


def test_phase_1411_tests_do_not_generate_vrf_proofs() -> None:
    source = Path(__file__).read_text(encoding="utf-8")

    assert "Signing" + "Key" not in source
    assert "ECVRF_" + "prove" not in source
    assert "nonce_" + "generation" not in source
