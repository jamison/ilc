"""CDL-069 epoch endorsement protocol runtime.

Implements the validator-side and agent-side logic for the epoch endorsement
packet and epoch close attestation as specified in CDL-069 §2b.

This module covers:
  - EpochEndorsementPacket dataclass (all required fields from CDL-069 audit)
  - EpochCloseAttestation dataclass
  - liveness_assertion derivation (sha256(agent_id || epoch_id))
  - ecu_commitment construction with nonce (sha256(total || epoch_nonce))
  - epoch_nonce derivation (sha256(identity_seed_commitment || epoch_id))
  - Validator-side endorsement cache (EndorsementCache)
  - Validator acceptance rules: sequence_number ordering, valid_epochs window,
    supersedes_epoch_id distributed-atomicity enforcement
  - freeze_from_epoch clamping (no retroactive invalidation)

ML-DSA-65 signing is performed by the Rust pq_keygen/endorsement binary
and is NOT implemented here. This module handles the protocol logic layer:
packet construction, field validation, caching, and rule enforcement.

`epoch_endorsement_runtime_838c_present`
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Optional

EPOCH_ENDORSEMENT_RUNTIME_VERSION = "epoch_endorsement_runtime_838c.v0.1"
CDL_069_DEPENDENCY = "cdl_069_opens_phase_838"

PROTOCOL_VERSION: int = 1
MAX_ENDORSEMENT_WINDOW_EPOCHS_DEFAULT: int = 1440  # 24 h of 1-min epochs; ratification decision

# Field length constants
_AGENT_ID_HEX_LENGTH: int = 96       # SHA-384 = 48 bytes = 96 hex chars
_BLS_PK_HEX_LENGTH: int = 96         # BLS12-381 G1 pk = 48 bytes = 96 hex chars

# Domain separators
_LIVENESS_DOMAIN: bytes = b"ilc-liveness-v1:"
_EPOCH_NONCE_DOMAIN: bytes = b"ilc-epoch-nonce-v1:"
_ECU_COMMIT_DOMAIN: bytes = b"ilc-ecu-commit-v1:"


class EndorsementError(ValueError):
    """Protocol validation error with machine-auditable token."""

    def __init__(self, token: str, message: str) -> None:
        super().__init__(message)
        self.token = token


# ---------------------------------------------------------------------------
# Cryptographic helpers
# ---------------------------------------------------------------------------

def derive_liveness_assertion(agent_id: str, epoch_id: int) -> str:
    """Compute liveness_assertion = sha256(domain || agent_id || epoch_id).

    Deterministic and epoch-bound.  Any validator can verify without state.
    Proves the packet was freshly generated for this epoch, not replayed.
    CDL-069 §2b finding I2.
    """
    if not isinstance(agent_id, str) or len(agent_id) != _AGENT_ID_HEX_LENGTH:
        raise EndorsementError(
            "cdl_069_endorsement_invalid_agent_id_for_liveness",
            f"agent_id must be a {_AGENT_ID_HEX_LENGTH}-char string",
        )
    if not isinstance(epoch_id, int) or isinstance(epoch_id, bool) or epoch_id < 0:
        raise EndorsementError(
            "cdl_069_endorsement_invalid_epoch_id",
            "epoch_id must be a non-negative integer",
        )
    payload = _LIVENESS_DOMAIN + agent_id.encode() + epoch_id.to_bytes(8, "big")
    return hashlib.sha256(payload).hexdigest()


def derive_epoch_nonce(identity_seed_commitment: str, epoch_id: int) -> str:
    """Compute epoch_nonce = sha256(domain || identity_seed_commitment || epoch_id).

    Derived from public data already known to the agent.  No additional
    storage required.  CDL-069 §2b finding C2.
    """
    if not isinstance(identity_seed_commitment, str) or len(identity_seed_commitment) != 96:
        raise EndorsementError(
            "cdl_069_epoch_nonce_invalid_commitment",
            "identity_seed_commitment must be a 96-char SHA-384 hex string",
        )
    if not isinstance(epoch_id, int) or isinstance(epoch_id, bool) or epoch_id < 0:
        raise EndorsementError(
            "cdl_069_epoch_nonce_invalid_epoch_id",
            "epoch_id must be a non-negative integer",
        )
    payload = (
        _EPOCH_NONCE_DOMAIN
        + identity_seed_commitment.encode()
        + epoch_id.to_bytes(8, "big")
    )
    return hashlib.sha256(payload).hexdigest()


def compute_ecu_commitment(
    ecu_total_str: str,
    identity_seed_commitment: str,
    epoch_id: int,
) -> str:
    """Compute sha256(domain || ecu_total || epoch_nonce).

    Protects Row 5 anonymity: without the nonce, low-entropy amounts
    (e.g. '50') are trivially brute-forced within the one-epoch reveal window.
    The nonce adds full SHA-256 preimage resistance regardless of amount.
    CDL-069 §2b finding C2.

    ecu_total_str: canonical string representation of the ECU amount
        (e.g. decimal integer string; encoding is a ratification decision).
    """
    if not isinstance(ecu_total_str, str) or not ecu_total_str:
        raise EndorsementError(
            "cdl_069_ecu_commit_invalid_total",
            "ecu_total_str must be a non-empty string",
        )
    epoch_nonce = derive_epoch_nonce(identity_seed_commitment, epoch_id)
    payload = (
        _ECU_COMMIT_DOMAIN
        + ecu_total_str.encode()
        + epoch_nonce.encode()
    )
    return hashlib.sha256(payload).hexdigest()


def verify_ecu_commitment(
    commitment: str,
    ecu_total_str: str,
    identity_seed_commitment: str,
    epoch_id: int,
) -> bool:
    """Verify a deferred-reveal ECU commitment.

    Returns False (not raises) on any invalid input — this is a predicate.
    Callers that need error tokens should use compute_ecu_commitment directly.
    """
    try:
        expected = compute_ecu_commitment(ecu_total_str, identity_seed_commitment, epoch_id)
    except EndorsementError:
        return False
    return commitment == expected


# ---------------------------------------------------------------------------
# Epoch endorsement packet
# ---------------------------------------------------------------------------

@dataclass
class EpochEndorsementPacket:
    """CDL-069 §2b — all required fields post security audit.

    ML-DSA-65 signature bytes are stored separately (mldsa_signature field)
    and are not part of the signed payload (COSE_Sign1 envelope handles this).
    This dataclass represents the payload fields only.
    """
    # Required fields (CDL-069 §2b, post-audit)
    protocol_version: int           # Must equal PROTOCOL_VERSION (finding I5)
    agent_id: str                   # 96-char SHA-384 hex (finding C1)
    epoch_id: int                   # Epoch at which endorsement begins
    sequence_number: int            # u64 monotonic per agent (finding I3)
    ephemeral_signing_pk: str       # BLS12-381 G1 pk hex, authorized for window
    valid_epochs: int               # 1 .. MAX_ENDORSEMENT_WINDOW_EPOCHS
    liveness_assertion: str         # sha256(agent_id || epoch_id) hex (finding I2)
    agent_state_root: str           # CID of last epoch-close attestation (snapshot)

    # Override / restart fields (present when superseding a prior packet)
    supersedes_epoch_id: Optional[int] = None  # Finding C3; absent for first packet

    # Optional fields (ratification decisions)
    capability_declaration: Optional[str] = None
    stake_position: Optional[str] = None
    next_epoch_intent: Optional[str] = None

    # Detached signature (set after ML-DSA signing; not part of signed payload)
    mldsa_signature: Optional[bytes] = field(default=None, repr=False)

    def validate(
        self,
        *,
        max_window: int = MAX_ENDORSEMENT_WINDOW_EPOCHS_DEFAULT,
    ) -> None:
        """Validate all field constraints from CDL-069 §2b.

        Raises EndorsementError with a machine-auditable token on any failure.
        Does NOT verify the ML-DSA signature — that requires the canonical_root_pk
        and must be done by the caller with the Rust crypto layer.
        """
        # bool is a subclass of int in Python (True==1, False==0). Reject bools
        # explicitly so callers cannot smuggle boolean values into numeric fields,
        # which would serialize as JSON "true"/"false" instead of integers.
        if (
            isinstance(self.protocol_version, bool)
            or not isinstance(self.protocol_version, int)
            or self.protocol_version != PROTOCOL_VERSION
        ):
            raise EndorsementError(
                "cdl_069_endorsement_unknown_protocol_version",
                f"Expected protocol_version={PROTOCOL_VERSION}, "
                f"got {self.protocol_version!r}",
            )
        if not isinstance(self.agent_id, str) or len(self.agent_id) != 96:
            raise EndorsementError(
                "cdl_069_endorsement_invalid_agent_id",
                f"agent_id must be 96-char hex string, got length {len(self.agent_id)!r}",
            )
        if not all(c in "0123456789abcdef" for c in self.agent_id):
            raise EndorsementError(
                "cdl_069_endorsement_agent_id_not_hex",
                "agent_id must be lowercase hex",
            )
        if isinstance(self.epoch_id, bool) or not isinstance(self.epoch_id, int) or self.epoch_id < 0:
            raise EndorsementError(
                "cdl_069_endorsement_invalid_epoch_id",
                "epoch_id must be a non-negative integer",
            )
        if (
            isinstance(self.sequence_number, bool)
            or not isinstance(self.sequence_number, int)
            or self.sequence_number < 0
        ):
            raise EndorsementError(
                "cdl_069_endorsement_invalid_sequence_number",
                "sequence_number must be a non-negative integer",
            )
        if not isinstance(self.ephemeral_signing_pk, str) or len(self.ephemeral_signing_pk) != _BLS_PK_HEX_LENGTH:
            raise EndorsementError(
                "cdl_069_endorsement_invalid_ephemeral_signing_pk",
                f"ephemeral_signing_pk must be {_BLS_PK_HEX_LENGTH}-char BLS G1 hex string",
            )
        if not all(c in "0123456789abcdef" for c in self.ephemeral_signing_pk):
            raise EndorsementError(
                "cdl_069_endorsement_ephemeral_signing_pk_not_hex",
                "ephemeral_signing_pk must be lowercase hex",
            )
        if isinstance(self.valid_epochs, bool) or not isinstance(self.valid_epochs, int) or not (1 <= self.valid_epochs <= max_window):
            raise EndorsementError(
                "cdl_069_endorsement_invalid_valid_epochs",
                f"valid_epochs must be in [1, {max_window}], got {self.valid_epochs}",
            )
        if not isinstance(self.liveness_assertion, str) or len(self.liveness_assertion) != 64:
            raise EndorsementError(
                "cdl_069_endorsement_invalid_liveness_assertion",
                "liveness_assertion must be 64-char hex string",
            )
        expected_liveness = derive_liveness_assertion(self.agent_id, self.epoch_id)
        if self.liveness_assertion != expected_liveness:
            raise EndorsementError(
                "cdl_069_endorsement_liveness_mismatch",
                "liveness_assertion does not match sha256(agent_id || epoch_id)",
            )
        if not isinstance(self.agent_state_root, str) or not self.agent_state_root:
            raise EndorsementError(
                "cdl_069_endorsement_missing_agent_state_root",
                "agent_state_root must be a non-empty CID string",
            )
        if self.supersedes_epoch_id is not None:
            if not isinstance(self.supersedes_epoch_id, int) or self.supersedes_epoch_id < 0:
                raise EndorsementError(
                    "cdl_069_endorsement_invalid_supersedes_epoch_id",
                    "supersedes_epoch_id must be a non-negative integer when present",
                )

    def is_active_at(self, current_epoch: int) -> bool:
        """True if this endorsement is valid at current_epoch."""
        return self.epoch_id <= current_epoch < self.epoch_id + self.valid_epochs

    def to_signing_payload(self) -> bytes:
        """Canonical JSON bytes for ML-DSA signing (mldsa_signature excluded)."""
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
        if self.capability_declaration is not None:
            payload["capability_declaration"] = self.capability_declaration
        if self.stake_position is not None:
            payload["stake_position"] = self.stake_position
        if self.next_epoch_intent is not None:
            payload["next_epoch_intent"] = self.next_epoch_intent
        return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()


# ---------------------------------------------------------------------------
# Epoch close attestation
# ---------------------------------------------------------------------------

@dataclass
class EpochCloseAttestation:
    """CDL-069 §2b — epoch-close attestation fields.

    Signed by the ephemeral BLS key (not ML-DSA).
    ECU totals are committed with per-epoch nonce (finding C2).
    """
    epoch_id: int
    agent_id: str
    actions_root: str               # CID of all claims/actions this epoch
    ecu_sent_commitment: str        # sha256(sent_total || epoch_nonce)
    ecu_received_commitment: str    # sha256(received_total || epoch_nonce)
    reputation_delta: int           # Signed integer

    # Optional
    next_epoch_intent: Optional[str] = None

    # Detached BLS signature bytes
    bls_signature: Optional[bytes] = field(default=None, repr=False)

    def validate(self) -> None:
        # bool is a subclass of int — reject explicitly (serializes as JSON true/false)
        if isinstance(self.epoch_id, bool) or not isinstance(self.epoch_id, int) or self.epoch_id < 0:
            raise EndorsementError(
                "cdl_069_attest_invalid_epoch_id",
                "epoch_id must be a non-negative integer",
            )
        if not isinstance(self.agent_id, str) or len(self.agent_id) != 96:
            raise EndorsementError(
                "cdl_069_attest_invalid_agent_id",
                "agent_id must be 96-char hex string",
            )
        if not all(c in "0123456789abcdef" for c in self.agent_id):
            raise EndorsementError(
                "cdl_069_attest_agent_id_not_hex",
                "agent_id must be lowercase hex",
            )
        if not isinstance(self.actions_root, str) or not self.actions_root:
            raise EndorsementError(
                "cdl_069_attest_missing_actions_root",
                "actions_root must be a non-empty CID string",
            )
        if not isinstance(self.ecu_sent_commitment, str) or len(self.ecu_sent_commitment) != 64:
            raise EndorsementError(
                "cdl_069_attest_invalid_ecu_sent_commitment",
                "ecu_sent_commitment must be 64-char sha256 hex",
            )
        if not all(c in "0123456789abcdef" for c in self.ecu_sent_commitment):
            raise EndorsementError(
                "cdl_069_attest_ecu_sent_commitment_not_hex",
                "ecu_sent_commitment must be lowercase hex",
            )
        if not isinstance(self.ecu_received_commitment, str) or len(self.ecu_received_commitment) != 64:
            raise EndorsementError(
                "cdl_069_attest_invalid_ecu_received_commitment",
                "ecu_received_commitment must be 64-char sha256 hex",
            )
        if not all(c in "0123456789abcdef" for c in self.ecu_received_commitment):
            raise EndorsementError(
                "cdl_069_attest_ecu_received_commitment_not_hex",
                "ecu_received_commitment must be lowercase hex",
            )
        if isinstance(self.reputation_delta, bool) or not isinstance(self.reputation_delta, int):
            raise EndorsementError(
                "cdl_069_attest_invalid_reputation_delta",
                "reputation_delta must be an integer",
            )

    def to_signing_payload(self) -> bytes:
        payload: dict = {
            "epoch_id": self.epoch_id,
            "agent_id": self.agent_id,
            "actions_root": self.actions_root,
            "ecu_sent_commitment": self.ecu_sent_commitment,
            "ecu_received_commitment": self.ecu_received_commitment,
            "reputation_delta": self.reputation_delta,
        }
        if self.next_epoch_intent is not None:
            payload["next_epoch_intent"] = self.next_epoch_intent
        return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()


# ---------------------------------------------------------------------------
# Validator-side endorsement cache
# ---------------------------------------------------------------------------

@dataclass
class _CachedEndorsement:
    packet: EpochEndorsementPacket
    # epoch_id values from which the old ephemeral key is rejected
    # (populated when this packet supersedes a prior one)
    superseded_keys: dict[str, int] = field(default_factory=dict)
    # ephemeral_pk -> supersedes_epoch_id


class EndorsementCache:
    """Validator-side cache of verified endorsement packets.

    Enforces all CDL-069 §2b acceptance rules:
      - sequence_number total ordering (finding I3)
      - valid_epochs window expiry (finding I1)
      - supersedes_epoch_id distributed-atomicity rejection (finding C3)
      - freeze_from_epoch clamping (recovery transactions, finding I4)

    ML-DSA signature verification is NOT performed here — the caller must
    verify the signature before calling accept_packet().
    """

    def __init__(self, max_window: int = MAX_ENDORSEMENT_WINDOW_EPOCHS_DEFAULT) -> None:
        self._max_window = max_window
        # agent_id -> _CachedEndorsement
        self._cache: dict[str, _CachedEndorsement] = {}
        # agent_id -> set of frozen (old_pk, effective_freeze_epoch) from recovery
        self._frozen: dict[str, list[tuple[str, int]]] = {}

    def accept_packet(self, packet: EpochEndorsementPacket) -> None:
        """Accept a pre-verified endorsement packet into the cache.

        Raises EndorsementError if the packet is rejected by any acceptance rule.
        The caller MUST have verified the ML-DSA signature before calling this.
        """
        packet.validate(max_window=self._max_window)
        agent = packet.agent_id
        existing = self._cache.get(agent)

        if existing is not None:
            prev = existing.packet
            # Rule: higher sequence_number wins (finding I3)
            if packet.sequence_number < prev.sequence_number:
                raise EndorsementError(
                    "cdl_069_endorsement_stale_sequence_number",
                    f"Packet sequence_number {packet.sequence_number} is lower than "
                    f"cached {prev.sequence_number} for agent {agent[:16]}...",
                )
            if packet.sequence_number == prev.sequence_number:
                raise EndorsementError(
                    "cdl_069_endorsement_duplicate_sequence_number",
                    f"Duplicate sequence_number {packet.sequence_number} for agent {agent[:16]}...",
                )

        # Build superseded_keys mapping from this packet
        superseded_keys: dict[str, int] = {}
        if existing is not None:
            # Carry forward any prior supersession records
            superseded_keys.update(existing.superseded_keys)

        if packet.supersedes_epoch_id is not None:
            if existing is not None:
                old_pk = existing.packet.ephemeral_signing_pk
                superseded_keys[old_pk] = packet.supersedes_epoch_id

        self._cache[agent] = _CachedEndorsement(
            packet=packet,
            superseded_keys=superseded_keys,
        )

    def get_packet(self, agent_id: str, current_epoch: int) -> Optional[EpochEndorsementPacket]:
        """Return the cached endorsement packet for an agent if valid at current_epoch.

        Returns None if no packet cached, or if the window has expired.
        """
        entry = self._cache.get(agent_id)
        if entry is None:
            return None
        if not entry.packet.is_active_at(current_epoch):
            return None
        return entry.packet

    def is_ephemeral_key_valid(
        self,
        agent_id: str,
        ephemeral_pk: str,
        current_epoch: int,
    ) -> bool:
        """True if ephemeral_pk is currently authorized for agent_id at current_epoch.

        Enforces:
          - Valid endorsement window (finding I1)
          - Supersession rejection: if ephemeral_pk was superseded at epoch E,
            reject for all current_epoch >= E (finding C3)
          - Freeze rejection from recovery transactions (finding I4)
        """
        entry = self._cache.get(agent_id)
        if entry is None:
            return False

        packet = entry.packet

        # Check window validity
        if not packet.is_active_at(current_epoch):
            return False

        # Check the key in the current packet matches
        if packet.ephemeral_signing_pk != ephemeral_pk:
            # Could be a superseded key — check supersession records.
            # Per CDL-069 §2b: reject for all epochs >= supersedes_epoch_id.
            # Epochs BEFORE supersedes_epoch_id remain valid (no retroactive rejection).
            supersede_epoch = entry.superseded_keys.get(ephemeral_pk)
            if supersede_epoch is not None:
                # Key was superseded: valid only for epochs strictly before supersede_epoch
                return current_epoch < supersede_epoch
            # Key is neither current nor a known superseded key
            return False

        # Check recovery freeze (finding I4)
        for frozen_pk, freeze_epoch in self._frozen.get(agent_id, []):
            if frozen_pk == ephemeral_pk and current_epoch >= freeze_epoch:
                return False

        return True

    def apply_recovery_freeze(
        self,
        agent_id: str,
        old_canonical_root_pk: str,  # noqa: ARG002 — reserved for future pk-keyed freeze
        freeze_from_epoch: int,
        current_epoch: int,
    ) -> int:
        """Apply a freeze_from_epoch from a recovery transaction.

        Per CDL-069 §2a finding I4: effective_freeze_epoch is clamped to
        max(current_epoch, freeze_from_epoch).  No confirmed transaction
        from any epoch before effective_freeze_epoch is ever invalidated.

        Returns the effective_freeze_epoch applied.
        """
        effective = max(current_epoch, freeze_from_epoch)
        entry = self._cached_entry_for(agent_id)
        if entry is not None:
            # Mark the current ephemeral key as frozen from effective epoch
            ephemeral_pk = entry.packet.ephemeral_signing_pk
            if agent_id not in self._frozen:
                self._frozen[agent_id] = []
            self._frozen[agent_id].append((ephemeral_pk, effective))
        return effective

    def evict_expired(self, current_epoch: int) -> int:
        """Remove cache entries whose valid_epochs window has expired.

        Also removes corresponding _frozen entries to avoid unbounded memory
        growth on long-running validators. Returns count of evicted entries.
        """
        expired = [
            aid for aid, entry in self._cache.items()
            if not entry.packet.is_active_at(current_epoch)
        ]
        for aid in expired:
            del self._cache[aid]
            self._frozen.pop(aid, None)
        return len(expired)

    def _cached_entry_for(self, agent_id: str) -> Optional[_CachedEndorsement]:
        return self._cache.get(agent_id)

    def __len__(self) -> int:
        return len(self._cache)
