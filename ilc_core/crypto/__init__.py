# SPDX-License-Identifier: AGPL-3.0-or-later
"""
ILC Crypto module - COSE signing and verification.

This module provides cryptographic primitives for ILC attestations:
- COSE_Sign1 attestation blocks (Ed25519)
- Canonical CBOR encoding for COSE structures

Dependencies: cbor2>=5.0.0, cryptography>=41.0.0
"""

from .cose_sign1 import (
    cose_sign1_sign,
    cose_sign1_decode,
    cose_sign1_verify,
    validate_canonical_cose_sign1_bytes,
    COSE_TAG_SIGN1,
    COSE_HDR_ALG,
    COSE_HDR_KID,
    COSE_ALG_EDDSA,
)
from .cbor_canonical import (
    MAX_CANONICAL_CBOR_INPUT_BYTES,
    cbor_dumps_canonical,
    cbor_loads,
    validate_canonical_cbor_bytes,
    is_canonical_cbor,
)

__all__ = [
    "cose_sign1_sign",
    "cose_sign1_decode",
    "cose_sign1_verify",
    "validate_canonical_cose_sign1_bytes",
    "COSE_TAG_SIGN1",
    "COSE_HDR_ALG",
    "COSE_HDR_KID",
    "COSE_ALG_EDDSA",
    "MAX_CANONICAL_CBOR_INPUT_BYTES",
    "cbor_dumps_canonical",
    "cbor_loads",
    "validate_canonical_cbor_bytes",
    "is_canonical_cbor",
]
