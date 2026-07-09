# SPDX-License-Identifier: AGPL-3.0-only
"""RFC 9381 ECVRF verifier for ADR-0042.

PUBLIC_RC_EXCLUDE: phase_1411_verifier_pre_integration
PUBLIC_RC_EXCLUDE_REASON: verifier is implemented before Phase 1412 jury
assignment integration and before the J-008 production activation gate.
"""

from __future__ import annotations

import hashlib

try:
    import nacl.bindings as _nacl_bindings
except ImportError:  # pragma: no cover - dependency tests cover normal path.
    _nacl_bindings = None


VRF_PROOF_VERIFIER_VERSION = "vrf_proof_verifier_phase_1411.v0.1"
_TOKEN_VRF_IMPLEMENTED = "vrf_proof_verifier_implemented_phase_1411"
_TOKEN_VRF_NOT_ACTIVATED = "vrf_proof_verifier_not_activated_phase_1410"

ALGORITHM = "ECVRF-EDWARDS25519-SHA512-ELL2"
PUBLIC_KEY_LENGTH = 32
PROOF_LENGTH = 80
BETA_LENGTH = 64
MAX_ALPHA_LENGTH = 4096

_SUITE_STRING = b"\x04"
_POINT_LENGTH = 32
_CHALLENGE_LENGTH = 16
_SCALAR_LENGTH = 32
_HASH_TO_CURVE_DST = (
    b"ECVRF_edwards25519_XMD:SHA-512_ELL2_NU_" + _SUITE_STRING
)

_FIELD_PRIME = 2**255 - 19
_GROUP_ORDER = 2**252 + 27742317777372353535851937790883648493
_COFACTOR = 8
_CURVE25519_J = 486662
_SQRT_MINUS_ONE = pow(2, (_FIELD_PRIME - 1) // 4, _FIELD_PRIME)
_EDWARDS_D = (-121665 * pow(121666, _FIELD_PRIME - 2, _FIELD_PRIME)) % _FIELD_PRIME
_IDENTITY: tuple[int, int] = (0, 1)
_BASE_POINT: tuple[int, int] = (
    15112221349535400772501151409588531511454012693041857206046113283949847762202,
    46316835694926478169428394003475163141307993866256225615783033603165251855960,
)

_PYNACL_REQUIRED_BINDINGS = (
    "crypto_core_ed25519_add",
    "crypto_core_ed25519_sub",
    "crypto_core_ed25519_from_uniform",
    "crypto_scalarmult_ed25519_noclamp",
    "crypto_scalarmult_ed25519_base_noclamp",
)
PYNACL_LOW_LEVEL_BINDINGS_AVAILABLE = (
    _nacl_bindings is not None
    and all(hasattr(_nacl_bindings, name) for name in _PYNACL_REQUIRED_BINDINGS)
)
PYNACL_BINDING_DISPOSITION = (
    "pynacl_1_6_2_low_level_bindings_present_but_phase_1411_uses_"
    "rfc9380_reference_arithmetic_for_appendix_b4_exactness"
)


class VRFVerificationError(Exception):
    """Raised for malformed VRF inputs or failed beta extraction."""


class _InvalidVRFProof(Exception):
    """Internal marker for well-formed proofs that fail verification."""


def verify_vrf_proof(*, pi: bytes, public_key: bytes, alpha: bytes) -> bool:
    """Return True only when the RFC 9381 VRF proof verifies."""

    try:
        _verify_and_beta(pi=pi, public_key=public_key, alpha=alpha)
    except _InvalidVRFProof:
        return False
    return True


def vrf_beta_from_proof(*, pi: bytes, public_key: bytes, alpha: bytes) -> bytes:
    """Return beta bytes for a valid proof or raise a stable error."""

    try:
        return _verify_and_beta(pi=pi, public_key=public_key, alpha=alpha)
    except _InvalidVRFProof as exc:
        raise VRFVerificationError("vrf_proof_invalid_phase_1411") from exc


def _verify_and_beta(*, pi: bytes, public_key: bytes, alpha: bytes) -> bytes:
    _validate_inputs(pi=pi, public_key=public_key, alpha=alpha)

    public_point = _decode_point(public_key, token="vrf_public_key_invalid_phase_1411")
    _validate_public_key(public_point)
    gamma, challenge, scalar = _decode_proof(pi)
    hashed_point = _encode_to_curve(public_key, alpha)

    u_point = _point_subtract(
        _scalar_multiply(scalar, _BASE_POINT),
        _scalar_multiply(challenge, public_point),
    )
    v_point = _point_subtract(
        _scalar_multiply(scalar, hashed_point),
        _scalar_multiply(challenge, gamma),
    )
    expected_challenge = _challenge_generation(
        public_point, hashed_point, gamma, u_point, v_point
    )
    if challenge != expected_challenge:
        raise _InvalidVRFProof
    return _proof_to_hash(gamma)


def _validate_inputs(*, pi: bytes, public_key: bytes, alpha: bytes) -> None:
    _require_exact_bytes("pi", pi, PROOF_LENGTH)
    _require_exact_bytes("public_key", public_key, PUBLIC_KEY_LENGTH)
    if type(alpha) is not bytes:
        raise VRFVerificationError("vrf_alpha_must_be_bytes_phase_1411")
    if len(alpha) > MAX_ALPHA_LENGTH:
        raise VRFVerificationError("vrf_alpha_too_long_phase_1411")


def _require_exact_bytes(name: str, value: bytes, expected_length: int) -> None:
    if type(value) is not bytes:
        raise VRFVerificationError(f"vrf_{name}_must_be_bytes_phase_1411")
    if len(value) != expected_length:
        raise VRFVerificationError(f"vrf_{name}_wrong_length_phase_1411")


def _decode_proof(pi: bytes) -> tuple[tuple[int, int], int, int]:
    gamma_string = pi[:_POINT_LENGTH]
    c_string = pi[_POINT_LENGTH : _POINT_LENGTH + _CHALLENGE_LENGTH]
    s_string = pi[_POINT_LENGTH + _CHALLENGE_LENGTH :]
    gamma = _decode_point(gamma_string, token="vrf_gamma_invalid_phase_1411")
    challenge = int.from_bytes(c_string, "little")
    scalar = int.from_bytes(s_string, "little")
    if scalar >= _GROUP_ORDER:
        raise VRFVerificationError("vrf_scalar_out_of_range_phase_1411")
    return gamma, challenge, scalar


def _validate_public_key(point: tuple[int, int]) -> None:
    if _scalar_multiply(_COFACTOR, point) == _IDENTITY:
        raise VRFVerificationError("vrf_public_key_low_order_phase_1411")


def _proof_to_hash(gamma: tuple[int, int]) -> bytes:
    return hashlib.sha512(
        _SUITE_STRING
        + b"\x03"
        + _encode_point(_scalar_multiply(_COFACTOR, gamma))
        + b"\x00"
    ).digest()


def _challenge_generation(*points: tuple[int, int]) -> int:
    material = _SUITE_STRING + b"\x02" + b"".join(_encode_point(point) for point in points)
    c_string = hashlib.sha512(material + b"\x00").digest()[:_CHALLENGE_LENGTH]
    return int.from_bytes(c_string, "little")


def _encode_to_curve(public_key: bytes, alpha: bytes) -> tuple[int, int]:
    uniform_bytes = _expand_message_xmd(public_key + alpha, _HASH_TO_CURVE_DST, 48)
    field_element = int.from_bytes(uniform_bytes, "big") % _FIELD_PRIME
    mapped_point = _map_to_curve_elligator2_edwards25519(field_element)
    return _scalar_multiply(_COFACTOR, mapped_point)


def _expand_message_xmd(message: bytes, dst: bytes, length: int) -> bytes:
    if len(dst) > 255:
        raise VRFVerificationError("vrf_dst_too_long_phase_1411")
    b_in_bytes = 64
    s_in_bytes = 128
    ell = (length + b_in_bytes - 1) // b_in_bytes
    if ell > 255 or length > 65535:
        raise VRFVerificationError("vrf_expand_message_length_invalid_phase_1411")
    dst_prime = dst + bytes([len(dst)])
    b_0 = hashlib.sha512(
        bytes(s_in_bytes) + message + length.to_bytes(2, "big") + b"\x00" + dst_prime
    ).digest()
    b_i = hashlib.sha512(b_0 + b"\x01" + dst_prime).digest()
    uniform_bytes = b_i
    for index in range(2, ell + 1):
        b_i = hashlib.sha512(_xor_bytes(b_0, b_i) + bytes([index]) + dst_prime).digest()
        uniform_bytes += b_i
    return uniform_bytes[:length]


def _map_to_curve_elligator2_edwards25519(field_element: int) -> tuple[int, int]:
    x_m_num, x_m_den, y_m_num, y_m_den = _map_to_curve_elligator2_curve25519(
        field_element
    )
    c_1 = _sqrt_mod(-486664)
    if c_1 is None:
        raise VRFVerificationError("vrf_map_constant_invalid_phase_1411")
    if _sgn0(c_1) != 0:
        c_1 = (-c_1) % _FIELD_PRIME

    x_num = x_m_num * y_m_den % _FIELD_PRIME
    x_num = x_num * c_1 % _FIELD_PRIME
    x_den = x_m_den * y_m_num % _FIELD_PRIME
    y_num = (x_m_num - x_m_den) % _FIELD_PRIME
    y_den = (x_m_num + x_m_den) % _FIELD_PRIME
    exceptional = x_den * y_den % _FIELD_PRIME == 0
    if exceptional:
        x_num = 0
        x_den = 1
        y_num = 1
        y_den = 1
    return (
        x_num * _inverse(x_den) % _FIELD_PRIME,
        y_num * _inverse(y_den) % _FIELD_PRIME,
    )


def _map_to_curve_elligator2_curve25519(field_element: int) -> tuple[int, int, int, int]:
    c_1 = (_FIELD_PRIME + 3) // 8
    c_2 = pow(2, c_1, _FIELD_PRIME)
    c_3 = _SQRT_MINUS_ONE
    c_4 = (_FIELD_PRIME - 5) // 8

    tv1 = field_element * field_element % _FIELD_PRIME
    tv1 = 2 * tv1 % _FIELD_PRIME
    x_den = (tv1 + 1) % _FIELD_PRIME
    x1_num = (-_CURVE25519_J) % _FIELD_PRIME
    tv2 = x_den * x_den % _FIELD_PRIME
    gx_den = tv2 * x_den % _FIELD_PRIME
    gx1 = _CURVE25519_J * tv1 % _FIELD_PRIME
    gx1 = gx1 * x1_num % _FIELD_PRIME
    gx1 = (gx1 + tv2) % _FIELD_PRIME
    gx1 = gx1 * x1_num % _FIELD_PRIME
    tv3 = gx_den * gx_den % _FIELD_PRIME
    tv2 = tv3 * tv3 % _FIELD_PRIME
    tv3 = tv3 * gx_den % _FIELD_PRIME
    tv3 = tv3 * gx1 % _FIELD_PRIME
    tv2 = tv2 * tv3 % _FIELD_PRIME
    y_11 = pow(tv2, c_4, _FIELD_PRIME)
    y_11 = y_11 * tv3 % _FIELD_PRIME
    y_12 = y_11 * c_3 % _FIELD_PRIME
    tv2 = y_11 * y_11 % _FIELD_PRIME
    tv2 = tv2 * gx_den % _FIELD_PRIME
    e_1 = tv2 == gx1
    y_1 = _cmov(y_12, y_11, e_1)
    x2_num = x1_num * tv1 % _FIELD_PRIME
    y_21 = y_11 * field_element % _FIELD_PRIME
    y_21 = y_21 * c_2 % _FIELD_PRIME
    y_22 = y_21 * c_3 % _FIELD_PRIME
    gx2 = gx1 * tv1 % _FIELD_PRIME
    tv2 = y_21 * y_21 % _FIELD_PRIME
    tv2 = tv2 * gx_den % _FIELD_PRIME
    e_2 = tv2 == gx2
    y_2 = _cmov(y_22, y_21, e_2)
    tv2 = y_1 * y_1 % _FIELD_PRIME
    tv2 = tv2 * gx_den % _FIELD_PRIME
    e_3 = tv2 == gx1
    x_num = _cmov(x2_num, x1_num, e_3)
    y = _cmov(y_2, y_1, e_3)
    e_4 = _sgn0(y) == 1
    y = _cmov(y, (-y) % _FIELD_PRIME, e_3 ^ e_4)
    return x_num, x_den, y, 1


def _decode_point(encoded: bytes, *, token: str) -> tuple[int, int]:
    if len(encoded) != _POINT_LENGTH:
        raise VRFVerificationError(token)
    y = int.from_bytes(encoded, "little") & ((1 << 255) - 1)
    sign = encoded[31] >> 7
    if y >= _FIELD_PRIME:
        raise VRFVerificationError(token)
    y_squared = y * y % _FIELD_PRIME
    x_squared = (y_squared - 1) * _inverse(_EDWARDS_D * y_squared + 1) % _FIELD_PRIME
    x = _sqrt_mod(x_squared)
    if x is None:
        raise VRFVerificationError(token)
    if (x & 1) != sign:
        x = (-x) % _FIELD_PRIME
    if x == 0 and sign:
        raise VRFVerificationError(token)
    return x, y


def _encode_point(point: tuple[int, int]) -> bytes:
    x, y = point
    encoded = bytearray(y.to_bytes(_POINT_LENGTH, "little"))
    encoded[31] |= (x & 1) << 7
    return bytes(encoded)


def _point_add(point_a: tuple[int, int], point_b: tuple[int, int]) -> tuple[int, int]:
    # Complete twisted Edwards addition formula. The denominators (1 ± d·x1·x2·y1·y2)
    # are never zero over GF(p) because d = -121665/121666 is a non-square mod p.
    # A zero denominator would require d·x1·x2·y1·y2 = ±1, i.e. d = (x1·x2·y1·y2)^{-1},
    # meaning d is a square — contradiction. This guarantees the formula is complete
    # (no exceptional inputs) for all valid Edwards25519 points.
    x1, y1 = point_a
    x2, y2 = point_b
    product = x1 * x2 * y1 * y2 % _FIELD_PRIME
    x3 = (x1 * y2 + x2 * y1) * _inverse(1 + _EDWARDS_D * product) % _FIELD_PRIME
    y3 = (y1 * y2 + x1 * x2) * _inverse(1 - _EDWARDS_D * product) % _FIELD_PRIME
    return x3, y3


def _point_subtract(point_a: tuple[int, int], point_b: tuple[int, int]) -> tuple[int, int]:
    return _point_add(point_a, ((-point_b[0]) % _FIELD_PRIME, point_b[1]))


def _scalar_multiply(scalar: int, point: tuple[int, int]) -> tuple[int, int]:
    result = _IDENTITY
    addend = point
    while scalar:
        if scalar & 1:
            result = _point_add(result, addend)
        addend = _point_add(addend, addend)
        scalar >>= 1
    return result


def _sqrt_mod(value: int) -> int | None:
    value %= _FIELD_PRIME
    root = pow(value, (_FIELD_PRIME + 3) // 8, _FIELD_PRIME)
    if (root * root - value) % _FIELD_PRIME == 0:
        return root
    root = root * _SQRT_MINUS_ONE % _FIELD_PRIME
    if (root * root - value) % _FIELD_PRIME == 0:
        return root
    return None


def _inverse(value: int) -> int:
    return pow(value % _FIELD_PRIME, _FIELD_PRIME - 2, _FIELD_PRIME)


def _sgn0(value: int) -> int:
    return value & 1


def _cmov(first: int, second: int, condition: bool) -> int:
    return second if condition else first


def _xor_bytes(first: bytes, second: bytes) -> bytes:
    return bytes(left ^ right for left, right in zip(first, second))
