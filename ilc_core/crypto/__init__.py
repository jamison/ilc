"""
ILC Crypto module - COSE signing and verification.

This module provides cryptographic primitives for ILC attestations:
- COSE_Sign1 attestation blocks (Ed25519)
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

__all__ = [
    "cose_sign1_sign",
    "cose_sign1_decode",
    "cose_sign1_verify",
    "validate_canonical_cose_sign1_bytes",
    "COSE_TAG_SIGN1",
    "COSE_HDR_ALG",
    "COSE_HDR_KID",
    "COSE_ALG_EDDSA",
]
