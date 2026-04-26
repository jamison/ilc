"""CDL-069 genesis record schema runtime.

Implements the four-field genesis record structure specified in CDL-069 §2a,
the recovery_spec format for all supported types, and the recovery transaction
protocol including freeze_from_epoch clamping.

Genesis record fields (all SHA-384 commitments except canonical_root_pk):
  1. identity_seed_commitment  — sha384(identity_seed)
  2. canonical_root_pk         — ML-DSA-65 public key hex (necessarily public)
  3. recovery_commitment       — sha384(recovery_spec_bytes || blinding_factor)
  4. personhood_commitment     — sha384(personhood_proof || blinding_factor) [optional]

All commitment fields are Tier 3 (permanent) data — SHA-384 uniformly,
per CDL-069 §2g temporal data tier framework.

Blinding factor is derived deterministically:
  blinding_factor = sha384("ilc-recovery-blind-v1:" || identity_seed)

This eliminates the blinding factor as a separate cold storage item.

`genesis_record_schema_838e_present`
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from enum import Enum
from typing import Optional

GENESIS_RECORD_SCHEMA_VERSION = "genesis_record_schema_838e.v0.1"
CDL_069_DEPENDENCY = "cdl_069_opens_phase_838"

# Domain separators
_BLIND_DOMAIN: bytes = b"ilc-recovery-blind-v1:"
_AGENT_ID_DOMAIN: bytes = b"ilc-agent-id-v1:"

# Field length constants
_IDENTITY_SEED_LENGTH: int = 32
_COMMITMENT_HEX_LENGTH: int = 96    # SHA-384 = 48 bytes = 96 hex chars
_MLDSA_PK_HEX_LENGTH: int = 3328   # ML-DSA-65 pk = 1664 bytes = 3328 hex chars


class GenesisRecordError(ValueError):
    """Deterministic validation error with machine-auditable token."""

    def __init__(self, token: str, message: str) -> None:
        super().__init__(message)
        self.token = token


# ---------------------------------------------------------------------------
# Blinding factor derivation
# ---------------------------------------------------------------------------

def derive_blinding_factor(identity_seed: bytes) -> bytes:
    """Derive blinding_factor = sha384("ilc-recovery-blind-v1:" || identity_seed).

    Deterministic from identity_seed alone — no separate cold storage needed.
    """
    if not isinstance(identity_seed, bytes) or len(identity_seed) != _IDENTITY_SEED_LENGTH:
        raise GenesisRecordError(
            "cdl_069_genesis_invalid_identity_seed",
            f"identity_seed must be {_IDENTITY_SEED_LENGTH} bytes",
        )
    return hashlib.sha384(_BLIND_DOMAIN + identity_seed).digest()


def compute_identity_seed_commitment(identity_seed: bytes) -> str:
    """sha384(identity_seed) → 96-char hex."""
    if not isinstance(identity_seed, bytes) or len(identity_seed) != _IDENTITY_SEED_LENGTH:
        raise GenesisRecordError(
            "cdl_069_genesis_invalid_identity_seed",
            f"identity_seed must be {_IDENTITY_SEED_LENGTH} bytes",
        )
    return hashlib.sha384(identity_seed).hexdigest()


def compute_recovery_commitment(recovery_spec_bytes: bytes, blinding_factor: bytes) -> str:
    """sha384(recovery_spec_bytes || blinding_factor) → 96-char hex."""
    if not isinstance(recovery_spec_bytes, bytes):
        raise GenesisRecordError(
            "cdl_069_genesis_invalid_recovery_spec",
            "recovery_spec_bytes must be bytes",
        )
    if not isinstance(blinding_factor, bytes) or len(blinding_factor) != 48:
        raise GenesisRecordError(
            "cdl_069_genesis_invalid_blinding_factor",
            "blinding_factor must be 48 bytes (SHA-384 output)",
        )
    return hashlib.sha384(recovery_spec_bytes + blinding_factor).hexdigest()


def compute_personhood_commitment(personhood_proof_bytes: bytes, blinding_factor: bytes) -> str:
    """sha384(personhood_proof_bytes || blinding_factor) → 96-char hex."""
    if not isinstance(personhood_proof_bytes, bytes):
        raise GenesisRecordError(
            "cdl_069_genesis_invalid_personhood_proof",
            "personhood_proof_bytes must be bytes",
        )
    if not isinstance(blinding_factor, bytes) or len(blinding_factor) != 48:
        raise GenesisRecordError(
            "cdl_069_genesis_invalid_blinding_factor",
            "blinding_factor must be 48 bytes (SHA-384 output)",
        )
    return hashlib.sha384(personhood_proof_bytes + blinding_factor).hexdigest()


# ---------------------------------------------------------------------------
# Recovery spec types
# ---------------------------------------------------------------------------

class RecoverySpecType(str, Enum):
    SINGLE_KEY_MLDSA = "single_key_mldsa"
    SINGLE_KEY_SPHINCS = "single_key_sphincs"
    SHAMIR_SPHINCS = "shamir_sphincs"
    QUORUM_VALIDATOR = "quorum_validator"
    THRESHOLD_MULTIPARTY = "threshold_multiparty"
    HSM_ATTESTATION = "hsm_attestation"
    PERSONHOOD_BIOMETRIC = "personhood_biometric"


def encode_recovery_spec(spec_type: RecoverySpecType, **kwargs: object) -> bytes:
    """Encode a recovery_spec as canonical JSON bytes for commitment computation.

    The spec_type and parameters are entirely private until recovery is triggered.
    All agents look identical at the commitment level.

    Supported kwargs by type:
      single_key_mldsa:     pk_hex (str)
      single_key_sphincs:   pk_hex (str)
      shamir_sphincs:       pk_hex (str), threshold (int), total_shares (int)
      quorum_validator:     threshold (int), delay_epochs (int)
      threshold_multiparty: threshold (int), pk_hexes (list[str])
      hsm_attestation:      hsm_id (str)
      personhood_biometric: reserved (str)
    """
    payload = {"type": spec_type.value, **{k: v for k, v in kwargs.items()}}
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()


# ---------------------------------------------------------------------------
# Genesis record dataclass
# ---------------------------------------------------------------------------

@dataclass
class GenesisRecord:
    """CDL-069 §2a four-field genesis record.

    All commitment fields are 96-char SHA-384 hex strings (Tier 3, permanent).
    canonical_root_pk is the ML-DSA-65 public key hex (3328 chars).
    """
    identity_seed_commitment: str    # sha384(identity_seed)
    canonical_root_pk: str           # ML-DSA-65 pk hex — necessarily public
    recovery_commitment: str         # sha384(recovery_spec || blinding_factor)
    personhood_commitment: Optional[str] = None  # optional; omitted if not used

    def validate(self) -> None:
        """Validate all field constraints. Raises GenesisRecordError on failure."""
        _require_commitment(
            "identity_seed_commitment", self.identity_seed_commitment,
            "cdl_069_genesis_invalid_identity_seed_commitment",
        )
        _require_hex(
            "canonical_root_pk", self.canonical_root_pk,
            _MLDSA_PK_HEX_LENGTH,
            "cdl_069_genesis_invalid_canonical_root_pk",
        )
        _require_commitment(
            "recovery_commitment", self.recovery_commitment,
            "cdl_069_genesis_invalid_recovery_commitment",
        )
        if self.personhood_commitment is not None:
            _require_commitment(
                "personhood_commitment", self.personhood_commitment,
                "cdl_069_genesis_invalid_personhood_commitment",
            )

    def to_canonical_bytes(self) -> bytes:
        """Canonical JSON encoding for on-chain storage / CID computation."""
        payload: dict = {
            "identity_seed_commitment": self.identity_seed_commitment,
            "canonical_root_pk": self.canonical_root_pk,
            "recovery_commitment": self.recovery_commitment,
        }
        if self.personhood_commitment is not None:
            payload["personhood_commitment"] = self.personhood_commitment
        return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()

    @classmethod
    def from_identity_seed(
        cls,
        identity_seed: bytes,
        canonical_root_pk_hex: str,
        recovery_spec_bytes: bytes,
        personhood_proof_bytes: Optional[bytes] = None,
    ) -> "GenesisRecord":
        """Construct a genesis record from raw secret material.

        This is the ceremony-time constructor — call once during key generation.
        The identity_seed and recovery_spec_bytes are never stored in the record.
        """
        blinding_factor = derive_blinding_factor(identity_seed)
        id_commit = compute_identity_seed_commitment(identity_seed)
        rec_commit = compute_recovery_commitment(recovery_spec_bytes, blinding_factor)
        person_commit: Optional[str] = None
        if personhood_proof_bytes is not None:
            person_commit = compute_personhood_commitment(
                personhood_proof_bytes, blinding_factor,
            )
        return cls(
            identity_seed_commitment=id_commit,
            canonical_root_pk=canonical_root_pk_hex,
            recovery_commitment=rec_commit,
            personhood_commitment=person_commit,
        )


# ---------------------------------------------------------------------------
# Recovery transaction
# ---------------------------------------------------------------------------

@dataclass
class RecoveryTransaction:
    """CDL-069 §2a recovery transaction protocol.

    Reveals recovery_spec (pre-image of recovery_commitment) and proves
    authorization. freeze_from_epoch is clamped to max(current_epoch, value).
    """
    old_canonical_root_pk: str       # key being replaced
    new_canonical_root_pk: str       # new ML-DSA-65 key
    identity_seed_commitment: str    # must match genesis record
    recovery_spec: bytes             # pre-image of recovery_commitment
    authorization: bytes             # proof that recovery_spec is satisfied
    freeze_from_epoch: Optional[int] = None  # optional early freeze

    def validate_against_record(
        self,
        genesis_record: GenesisRecord,
        identity_seed: bytes,
        current_epoch: int,
    ) -> int:
        """Validate recovery transaction against the genesis record.

        Returns the effective_freeze_epoch (clamped per finding I4).
        Raises GenesisRecordError on any validation failure.
        """
        # 1. old_canonical_root_pk must match the genesis record's current key
        if self.old_canonical_root_pk != genesis_record.canonical_root_pk:
            raise GenesisRecordError(
                "cdl_069_recovery_old_pk_mismatch",
                "old_canonical_root_pk does not match genesis record canonical_root_pk",
            )
        # 2. identity_seed_commitment must match genesis record
        if self.identity_seed_commitment != genesis_record.identity_seed_commitment:
            raise GenesisRecordError(
                "cdl_069_recovery_identity_seed_commitment_mismatch",
                "identity_seed_commitment does not match genesis record",
            )
        # 3. Recompute recovery_commitment from presented recovery_spec
        blinding_factor = derive_blinding_factor(identity_seed)
        expected_rec_commit = compute_recovery_commitment(
            self.recovery_spec, blinding_factor,
        )
        if expected_rec_commit != genesis_record.recovery_commitment:
            raise GenesisRecordError(
                "cdl_069_recovery_commitment_mismatch",
                "recovery_spec does not match recovery_commitment in genesis record",
            )
        # 4. new key must be well-formed
        _require_hex(
            "new_canonical_root_pk", self.new_canonical_root_pk,
            _MLDSA_PK_HEX_LENGTH,
            "cdl_069_recovery_invalid_new_pk",
        )
        # 5. Clamp freeze_from_epoch (finding I4: no retroactive invalidation)
        if self.freeze_from_epoch is not None:
            return max(current_epoch, self.freeze_from_epoch)
        return current_epoch

    def to_canonical_bytes(self) -> bytes:
        payload: dict = {
            "old_canonical_root_pk": self.old_canonical_root_pk,
            "new_canonical_root_pk": self.new_canonical_root_pk,
            "identity_seed_commitment": self.identity_seed_commitment,
        }
        if self.freeze_from_epoch is not None:
            payload["freeze_from_epoch"] = self.freeze_from_epoch
        return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()


# ---------------------------------------------------------------------------
# Validation helpers
# ---------------------------------------------------------------------------

def _require_commitment(name: str, value: str, token: str) -> None:
    if not isinstance(value, str) or len(value) != _COMMITMENT_HEX_LENGTH:
        raise GenesisRecordError(
            token,
            f"{name} must be a {_COMMITMENT_HEX_LENGTH}-char SHA-384 hex string, "
            f"got length {len(value) if isinstance(value, str) else type(value).__name__!r}",
        )
    if not all(c in "0123456789abcdef" for c in value):
        raise GenesisRecordError(token, f"{name} must be lowercase hex")


def _require_hex(name: str, value: str, expected_len: int, token: str) -> None:
    if not isinstance(value, str) or len(value) != expected_len:
        raise GenesisRecordError(
            token,
            f"{name} must be a {expected_len}-char hex string, "
            f"got {len(value) if isinstance(value, str) else type(value).__name__!r}",
        )
    if not all(c in "0123456789abcdef" for c in value):
        raise GenesisRecordError(token, f"{name} must be lowercase hex")
