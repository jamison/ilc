# SPDX-License-Identifier: AGPL-3.0-only
"""AgentID-linked validator key derivation helpers for CDL-017 public RC.

The Python layer derives only the deterministic 32-byte IKM for the Rust BLS
key generator and the non-secret ADR-0038 identity seed commitment. It never
creates or persists a validator BLS private key.
"""

from __future__ import annotations

import hashlib

from ilc_core.identity.genesis_record_schema import compute_identity_seed_commitment

VALIDATOR_KEY_DERIVATION_VERSION = (
    "validator_key_derivation_GAP_CDL017_IMPL_DELTA_00.v0.1"
)
VALIDATOR_KEY_DERIVATION_DOMAIN: bytes = b"ilc-validator-key-v1:"
IDENTITY_LINEAGE_REF_VERSION = "adr0038_identity_seed_commitment.v0.1"

_IDENTITY_SEED_LENGTH = 32
_VALIDATOR_IKM_LENGTH = 32


def _require_identity_seed(identity_seed: bytes) -> bytes:
    if not isinstance(identity_seed, bytes):
        raise ValueError("validator_key_identity_seed_must_be_bytes")
    if len(identity_seed) != _IDENTITY_SEED_LENGTH:
        raise ValueError("validator_key_identity_seed_must_be_32_bytes")
    if identity_seed == bytes(_IDENTITY_SEED_LENGTH):
        raise ValueError("validator_key_identity_seed_must_not_be_all_zero")
    return identity_seed


def derive_validator_key_ikm(identity_seed: bytes) -> bytes:
    """Derive ILC-specific BLS12-381 IETF keygen IKM from identity seed.

    The SHA-384 domain-separated digest is intentionally truncated to 32 bytes
    before Rust/blst `key_gen`; this is an ILC-specific sub-key derivation step,
    not a generic BLS key-derivation standard.
    """

    seed = _require_identity_seed(identity_seed)
    digest = hashlib.sha384(VALIDATOR_KEY_DERIVATION_DOMAIN + seed).digest()
    return digest[:_VALIDATOR_IKM_LENGTH]


def derive_validator_key_ikm_hex(identity_seed: bytes) -> str:
    """Return the deterministic validator key IKM as lower-hex for test vectors."""

    return derive_validator_key_ikm(identity_seed).hex()


def build_validator_key_derivation_record(identity_seed: bytes) -> dict[str, str]:
    """Build the non-secret public linkage record for a validator sub-key."""

    seed = _require_identity_seed(identity_seed)
    return {
        "identity_lineage_ref_version": IDENTITY_LINEAGE_REF_VERSION,
        "identity_seed_commitment": compute_identity_seed_commitment(seed),
        "validator_key_derivation_domain": VALIDATOR_KEY_DERIVATION_DOMAIN.decode(
            "ascii"
        ),
        "validator_key_derivation_version": VALIDATOR_KEY_DERIVATION_VERSION,
    }


__all__ = [
    "IDENTITY_LINEAGE_REF_VERSION",
    "VALIDATOR_KEY_DERIVATION_DOMAIN",
    "VALIDATOR_KEY_DERIVATION_VERSION",
    "build_validator_key_derivation_record",
    "derive_validator_key_ikm",
    "derive_validator_key_ikm_hex",
]
