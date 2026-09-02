# SPDX-License-Identifier: AGPL-3.0-only
"""CDL-069 epoch endorsement packet schema.

Implements the concrete field names, required/optional field validation,
COSE_Sign1 signing payload construction, and agent_state_root specification
for the epoch endorsement packet defined in CDL-069 §2b.

**Required fields (all endorsement packets):**
  1. protocol_version  — u32, currently 1
  2. agent_id          — 96-char SHA-384 hex (CDL-069 identity_seed derivation)
  3. epoch_id          — u64, epoch at which endorsement begins
  4. sequence_number   — u64, monotonically increasing per agent
  5. ephemeral_signing_pk — BLS12-381 G1 public key hex (48 bytes = 96 hex chars)
  6. valid_epochs      — u32 ∈ [1, MAX_ENDORSEMENT_WINDOW_EPOCHS]
  7. liveness_assertion — sha256(domain || agent_id || epoch_id) as 64-char hex
  8. agent_state_root  — CID of prior epoch-close attestation (string)

**Optional fields:**
  - supersedes_epoch_id — u64, present when overriding a prior packet
  - canonical_root_pk   — ML-DSA-65 pk hex (3904 chars); included for new agents
                          or after rotation; validators cache from prior packet
  - capability_declaration — str, what agent offers this epoch
  - stake_position      — str, current stake (avoids separate validator lookup)
  - next_epoch_intent   — str, capability hint for epoch N+1

**COSE_Sign1 encoding:**
The packet is signed as a COSE_Sign1 block (RFC 9052). This module produces
the signing payload bytes using canonical JSON; actual COSE serialization
is performed by the signing layer. The signing payload excludes the signature
field and includes all other fields in sorted-key canonical JSON encoding.

**Governed constant:**
  MAX_ENDORSEMENT_WINDOW_EPOCHS = 1440  (opening candidate; ratification decision)

`endorsement_packet_schema_838f_present`
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Optional

ENDORSEMENT_PACKET_SCHEMA_VERSION = "endorsement_packet_schema_838f.v0.1"
CDL_069_DEPENDENCY = "cdl_069_opens_phase_838"

# Governed constant (ratification decision) — opening candidate: 1440
MAX_ENDORSEMENT_WINDOW_EPOCHS: int = 1440

# Protocol version constant
CURRENT_PROTOCOL_VERSION: int = 1

# Field length constants
_AGENT_ID_HEX_LENGTH: int = 96         # SHA-384 = 48 bytes = 96 hex chars
_MLDSA_PK_HEX_LENGTH: int = 3904       # ML-DSA-65 pk = 1952 bytes = 3904 hex chars
_BLS_PK_HEX_LENGTH: int = 96           # BLS12-381 G1 pk = 48 bytes = 96 hex chars
_SHA256_HEX_LENGTH: int = 64           # SHA-256 = 32 bytes = 64 hex chars

# Domain separator for liveness assertion (CDL-069 §2b Fix I2)
_LIVENESS_DOMAIN: bytes = b"ilc-liveness-v1:"


class EndorsementPacketSchemaError(ValueError):
    """Deterministic validation error with machine-auditable token."""

    def __init__(self, token: str, message: str) -> None:
        super().__init__(message)
        self.token = token


# ---------------------------------------------------------------------------
# Liveness assertion
# ---------------------------------------------------------------------------

def derive_liveness_assertion(agent_id: str, epoch_id: int) -> str:
    """sha256(domain || agent_id_bytes || epoch_id_bytes) → 64-char hex.

    Deterministic and epoch-bound. Proves the packet was freshly generated
    for this specific epoch, not replayed from a prior endorsement.
    CDL-069 §2b Fix I2.
    """
    if not isinstance(agent_id, str) or len(agent_id) != _AGENT_ID_HEX_LENGTH:
        raise EndorsementPacketSchemaError(
            "cdl_069_endorsement_invalid_agent_id_for_liveness",
            f"agent_id must be {_AGENT_ID_HEX_LENGTH}-char hex string",
        )
    if not isinstance(epoch_id, int) or isinstance(epoch_id, bool) or epoch_id < 0:
        raise EndorsementPacketSchemaError(
            "cdl_069_endorsement_invalid_epoch_id_for_liveness",
            "epoch_id must be a non-negative integer",
        )
    return hashlib.sha256(
        _LIVENESS_DOMAIN + agent_id.encode() + epoch_id.to_bytes(8, "big")
    ).hexdigest()


def verify_liveness_assertion(liveness_assertion: str, agent_id: str, epoch_id: int) -> bool:
    """Verify liveness_assertion against agent_id and epoch_id.

    Returns False (not raises) on any invalid input — this is a predicate,
    not a validator. Callers that need error tokens should use derive_liveness_assertion
    directly and compare.
    """
    if not isinstance(liveness_assertion, str) or len(liveness_assertion) != _SHA256_HEX_LENGTH:
        return False
    try:
        expected = derive_liveness_assertion(agent_id, epoch_id)
    except EndorsementPacketSchemaError:
        return False
    return liveness_assertion == expected


# ---------------------------------------------------------------------------
# Endorsement packet dataclass
# ---------------------------------------------------------------------------

@dataclass
class EndorsementPacket:
    """CDL-069 §2b epoch endorsement packet.

    Required fields are validated strictly. Optional fields may be None.
    The packet is signed as COSE_Sign1; this class produces the canonical
    signing payload bytes.
    """
    # Required fields
    protocol_version: int            # u32 = 1
    agent_id: str                    # 96-char SHA-384 hex
    epoch_id: int                    # u64, epoch endorsement begins
    sequence_number: int             # u64, monotonically increasing per agent
    ephemeral_signing_pk: str        # BLS12-381 G1 pk, 96 hex chars
    valid_epochs: int                # u32 ∈ [1, MAX_ENDORSEMENT_WINDOW_EPOCHS]
    liveness_assertion: str          # sha256(domain || agent_id || epoch_id)
    agent_state_root: str            # CID of prior epoch-close attestation

    # Optional fields
    supersedes_epoch_id: Optional[int] = None    # present when overriding prior packet
    canonical_root_pk: Optional[str] = None      # ML-DSA-65 pk hex, 3904 chars
    capability_declaration: Optional[str] = None # what agent offers this epoch
    stake_position: Optional[str] = None         # current stake
    next_epoch_intent: Optional[str] = None      # capability hint for epoch N+1

    def validate(self) -> None:
        """Validate all field constraints. Raises EndorsementPacketSchemaError on failure."""
        # protocol_version — bool is a subclass of int (True==1, False==0); reject explicitly
        # so callers cannot smuggle booleans which serialize as JSON true/false.
        if (
            isinstance(self.protocol_version, bool)
            or not isinstance(self.protocol_version, int)
            or self.protocol_version != CURRENT_PROTOCOL_VERSION
        ):
            raise EndorsementPacketSchemaError(
                "cdl_069_endorsement_invalid_protocol_version",
                f"protocol_version must be {CURRENT_PROTOCOL_VERSION}, "
                f"got {self.protocol_version!r}",
            )
        # agent_id
        _require_hex(
            "agent_id", self.agent_id, _AGENT_ID_HEX_LENGTH,
            "cdl_069_endorsement_invalid_agent_id",
        )
        # epoch_id
        _require_u64("epoch_id", self.epoch_id, "cdl_069_endorsement_invalid_epoch_id")
        # sequence_number
        _require_u64(
            "sequence_number", self.sequence_number,
            "cdl_069_endorsement_invalid_sequence_number",
        )
        # ephemeral_signing_pk
        _require_hex(
            "ephemeral_signing_pk", self.ephemeral_signing_pk, _BLS_PK_HEX_LENGTH,
            "cdl_069_endorsement_invalid_ephemeral_signing_pk",
        )
        # valid_epochs — also reject bool
        if (
            isinstance(self.valid_epochs, bool)
            or not isinstance(self.valid_epochs, int)
            or self.valid_epochs < 1
            or self.valid_epochs > MAX_ENDORSEMENT_WINDOW_EPOCHS
        ):
            raise EndorsementPacketSchemaError(
                "cdl_069_endorsement_invalid_valid_epochs",
                f"valid_epochs must be in [1, {MAX_ENDORSEMENT_WINDOW_EPOCHS}], "
                f"got {self.valid_epochs!r}",
            )
        # liveness_assertion
        _require_hex(
            "liveness_assertion", self.liveness_assertion, _SHA256_HEX_LENGTH,
            "cdl_069_endorsement_invalid_liveness_assertion",
        )
        if not verify_liveness_assertion(self.liveness_assertion, self.agent_id, self.epoch_id):
            raise EndorsementPacketSchemaError(
                "cdl_069_endorsement_liveness_assertion_mismatch",
                "liveness_assertion does not match sha256(domain || agent_id || epoch_id)",
            )
        # agent_state_root — CID string; non-empty
        if not isinstance(self.agent_state_root, str) or not self.agent_state_root:
            raise EndorsementPacketSchemaError(
                "cdl_069_endorsement_invalid_agent_state_root",
                "agent_state_root must be a non-empty CID string",
            )
        # Optional: supersedes_epoch_id
        if self.supersedes_epoch_id is not None:
            _require_u64(
                "supersedes_epoch_id", self.supersedes_epoch_id,
                "cdl_069_endorsement_invalid_supersedes_epoch_id",
            )
        # Optional: canonical_root_pk
        if self.canonical_root_pk is not None:
            _require_hex(
                "canonical_root_pk", self.canonical_root_pk, _MLDSA_PK_HEX_LENGTH,
                "cdl_069_endorsement_invalid_canonical_root_pk",
            )

    def is_active_at(self, current_epoch: int) -> bool:
        """Return True if this endorsement is active at current_epoch.

        Active condition: epoch_id ≤ current_epoch < epoch_id + valid_epochs.
        Validators reject packets where current_epoch ≥ epoch_id + valid_epochs.
        """
        return self.epoch_id <= current_epoch < self.epoch_id + self.valid_epochs

    def to_signing_payload(self) -> bytes:
        """Canonical JSON bytes for COSE_Sign1 signing.

        Excludes no signature field (COSE handles that separately).
        All present fields are included; None optional fields are omitted.
        Keys are sorted for deterministic encoding.
        """
        payload: dict = {
            "protocol_version": self.protocol_version,
            "agent_id": self.agent_id,
            "epoch_id": self.epoch_id,
            "sequence_number": self.sequence_number,
            "ephemeral_signing_pk": self.ephemeral_signing_pk,
            "valid_epochs": self.valid_epochs,
            "liveness_assertion": self.liveness_assertion,
            "agent_state_root": self.agent_state_root,
        }
        if self.supersedes_epoch_id is not None:
            payload["supersedes_epoch_id"] = self.supersedes_epoch_id
        if self.canonical_root_pk is not None:
            payload["canonical_root_pk"] = self.canonical_root_pk
        if self.capability_declaration is not None:
            payload["capability_declaration"] = self.capability_declaration
        if self.stake_position is not None:
            payload["stake_position"] = self.stake_position
        if self.next_epoch_intent is not None:
            payload["next_epoch_intent"] = self.next_epoch_intent
        return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()

    @classmethod
    def build(
        cls,
        agent_id: str,
        epoch_id: int,
        sequence_number: int,
        ephemeral_signing_pk: str,
        valid_epochs: int,
        agent_state_root: str,
        **kwargs: object,
    ) -> "EndorsementPacket":
        """Convenience constructor that auto-derives liveness_assertion.

        Computes liveness_assertion from agent_id + epoch_id automatically.
        All optional fields can be passed as kwargs.
        """
        liveness = derive_liveness_assertion(agent_id, epoch_id)
        return cls(
            protocol_version=CURRENT_PROTOCOL_VERSION,
            agent_id=agent_id,
            epoch_id=epoch_id,
            sequence_number=sequence_number,
            ephemeral_signing_pk=ephemeral_signing_pk,
            valid_epochs=valid_epochs,
            liveness_assertion=liveness,
            agent_state_root=agent_state_root,
            **kwargs,
        )


# ---------------------------------------------------------------------------
# COSE_Sign1 signing context (stub — actual COSE serialization is external)
# ---------------------------------------------------------------------------

# COSE header for ML-DSA-65 (IANA algorithm ID TBD; opening candidate: -48)
# This is a ratification decision; the algorithm ID must be registered.
COSE_ALG_MLDSA65_CANDIDATE: int = -48

def build_cose_tbs_bytes(signing_payload: bytes, external_aad: bytes = b"") -> bytes:
    """Build COSE_Sign1 To-Be-Signed (TBS) bytes per RFC 9052 §4.4.

    TBS = Sig_Structure = [
        "Signature1",
        protected_header_bytes,
        external_aad,
        payload
    ]

    protected_header encodes {"alg": COSE_ALG_MLDSA65_CANDIDATE} in CBOR.
    This is a stub: actual CBOR encoding is performed by the signing layer.
    This function returns the concatenated canonical bytes for reference
    implementations that assemble TBS manually.

    Returns the canonical signing input: domain || protected || aad || payload.
    Not a complete CBOR encoding — the signing layer must wrap this per RFC 9052.
    """
    # Canonical protected header for ML-DSA-65 endorsement packets
    # Full CBOR encoding is the signing layer's responsibility.
    # Domain tag for ILC endorsement packets prevents cross-protocol confusion.
    domain_tag: bytes = b"ILC-EndorsementPacket-v1:"
    return domain_tag + signing_payload + external_aad


# ---------------------------------------------------------------------------
# Validator-side endorsement window check
# ---------------------------------------------------------------------------

def check_endorsement_window(
    packet: EndorsementPacket,
    current_epoch: int,
) -> bool:
    """Return True if packet is within its valid endorsement window.

    Active window: epoch_id ≤ current_epoch < epoch_id + valid_epochs.
    Validators reject packets where current_epoch ≥ epoch_id + valid_epochs
    (i.e., the boundary epoch epoch_id + valid_epochs is already expired).
    """
    return packet.is_active_at(current_epoch)


# ---------------------------------------------------------------------------
# Validation helpers
# ---------------------------------------------------------------------------

def _require_hex(name: str, value: str, expected_len: int, token: str) -> None:
    if not isinstance(value, str) or len(value) != expected_len:
        raise EndorsementPacketSchemaError(
            token,
            f"{name} must be a {expected_len}-char hex string, "
            f"got {len(value) if isinstance(value, str) else type(value).__name__!r}",
        )
    if not all(c in "0123456789abcdef" for c in value):
        raise EndorsementPacketSchemaError(token, f"{name} must be lowercase hex")


def _require_u64(name: str, value: int, token: str) -> None:
    if not isinstance(value, int) or isinstance(value, bool) or value < 0 or value >= 2**64:
        raise EndorsementPacketSchemaError(
            token,
            f"{name} must be a non-negative integer (u64), got {value!r}",
        )
