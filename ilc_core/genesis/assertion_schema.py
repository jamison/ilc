# SPDX-License-Identifier: AGPL-3.0-only
"""Phase 858 — HB-001 genesis assertion schema runtime.

Implements the genesis-authority `assert.truth` schema specified in:
  - Phase 855: truth primitive wire format spec
  - Phase 856: genesis assertion schema design

Provides:
  - GenesisAssertionContent — canonical field schema for genesis authority assertions
  - GenesisValidatorEntry   — per-validator record shape within an assertion
  - encode_genesis_assertion_payload() — canonical JSON bytes for ML-DSA-65 signing
  - verify_genesis_assertion_schema()  — structural validation without ML-DSA sig check
  - GenesisAssertionError              — deterministic validation exception

Note on signature verification:
  ML-DSA-65 signature verification requires the Rust pq_keygen/endorsement
  binary or an oqs-python binding. This module validates the schema structure
  and canonical encoding only. For cryptographic verification of the
  genesis assertion's ML-DSA-65 signature, use the Rust binary or the
  ilc_core/identity/epoch_endorsement_runtime.py verification path once
  the PQ Python binding is available.

Token: hb_001_genesis_authority_assertion_schema
Token: cdl_073_genesis_assertion_schema_implementation_858
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Optional

from ilc_core.ledger.exact_numeric import parse_non_negative_decimal

CDL_073_DEPENDENCY = "cdl_073_homoiconic_bootstrap_schema_ratified.v0.1"
GENESIS_ASSERTION_SCHEMA_VERSION = "genesis_assertion_schema_858.v0.1"

# Protocol constants — locked per Phase 855/856
ASSERTION_PROTOCOL_VERSION: int = 1
GENESIS_EPOCH: int = 0
GENESIS_AUTHORITY_ASSERTION_PRIMITIVE_TYPE: str = "genesis_authority_assertion"
GENESIS_AUTHORITY_ASSERTION_EPISTEMIC_TYPE: str = "objective"
GENESIS_AUTHORITY_KEY_ALGORITHM: str = "ML-DSA-65"

# ML-DSA-65 public key length (bytes and hex string)
_MLDSA_PK_BYTES: int = 1664
_MLDSA_PK_HEX_LENGTH: int = 3328   # 1664 bytes = 3328 hex chars

# key_id is derived as the first 16 hex chars of sha256(public_key_bytes)
_KEY_ID_HEX_LENGTH: int = 16


class GenesisAssertionError(ValueError):
    """Deterministic validation exception for genesis assertion schema errors.

    Token: hb_001_genesis_assertion_error
    """

    def __init__(self, token: str, message: str) -> None:
        super().__init__(message)
        self.token = token
        self.message = message

    def __str__(self) -> str:
        return self.message


# ---------------------------------------------------------------------------
# Field schemas
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class GenesisValidatorEntry:
    """Per-validator record within a genesis authority assertion.

    Token: hb_001_genesis_validator_entry_schema
    """
    validator_id: int           # sequential, starting at 1
    agent_id: str               # canonical agent_id (96-char hex = 48 bytes, CDL-069)
    validator_key: str          # BLS12-381 G1 compressed pubkey (96-char hex)
    stake_micro_ecu: str        # canonical decimal string (exact_numeric)
    role: str                   # "genesis_validator" | "bootstrap_validator"

    def validate(self) -> None:
        """Raise GenesisAssertionError if any field violates schema constraints."""
        if not isinstance(self.validator_id, int) or isinstance(self.validator_id, bool):
            raise GenesisAssertionError(
                "genesis_assertion_validator_id_must_be_int",
                f"validator_id must be a non-negative integer, got {type(self.validator_id)}",
            )
        if self.validator_id < 1:
            raise GenesisAssertionError(
                "genesis_assertion_validator_id_must_be_positive",
                f"validator_id must be >= 1, got {self.validator_id}",
            )
        if not isinstance(self.agent_id, str) or len(self.agent_id) != 96:
            raise GenesisAssertionError(
                "genesis_assertion_agent_id_must_be_96_char_hex",
                f"agent_id must be a 96-character hex string (48 bytes), "
                f"got length {len(self.agent_id) if isinstance(self.agent_id, str) else type(self.agent_id)}",
            )
        if not isinstance(self.validator_key, str) or len(self.validator_key) != 96:
            raise GenesisAssertionError(
                "genesis_assertion_validator_key_must_be_96_char_hex",
                f"validator_key must be a 96-character hex string (BLS12-381 G1 compressed), "
                f"got length {len(self.validator_key) if isinstance(self.validator_key, str) else type(self.validator_key)}",
            )
        # Validate stake_micro_ecu is a canonical non-negative decimal string.
        try:
            parse_non_negative_decimal(
                self.stake_micro_ecu,
                token="genesis_assertion_stake_micro_ecu_invalid",
            )
        except ValueError as exc:
            raise GenesisAssertionError(
                "genesis_assertion_stake_micro_ecu_invalid",
                f"stake_micro_ecu is not a valid non-negative decimal: {self.stake_micro_ecu!r}",
            ) from exc
        if self.role not in ("genesis_validator", "bootstrap_validator"):
            raise GenesisAssertionError(
                "genesis_assertion_validator_role_invalid",
                f"role must be 'genesis_validator' or 'bootstrap_validator', got {self.role!r}",
            )

    def to_dict(self) -> dict:
        """Canonical dict form for JSON serialization."""
        return {
            "validator_id": self.validator_id,
            "agent_id": self.agent_id,
            "validator_key": self.validator_key,
            "stake_micro_ecu": self.stake_micro_ecu,
            "role": self.role,
        }


@dataclass(frozen=True)
class GenesisAuthorityKey:
    """Genesis authority key record (ML-DSA-65).

    Token: hb_001_genesis_authority_key_schema
    """
    algorithm: str          # must be "ML-DSA-65"
    public_key_hex: str     # 3328-char hex (1664 bytes)
    key_id: str             # 16-char hex prefix of sha256(public_key_bytes)

    def validate(self) -> None:
        """Raise GenesisAssertionError if any field violates schema constraints."""
        if self.algorithm != GENESIS_AUTHORITY_KEY_ALGORITHM:
            raise GenesisAssertionError(
                "genesis_assertion_authority_key_algorithm_invalid",
                f"genesis authority key algorithm must be 'ML-DSA-65', got {self.algorithm!r}",
            )
        if not isinstance(self.public_key_hex, str) or len(self.public_key_hex) != _MLDSA_PK_HEX_LENGTH:
            raise GenesisAssertionError(
                "genesis_assertion_authority_key_hex_length_invalid",
                f"genesis authority public_key_hex must be {_MLDSA_PK_HEX_LENGTH} hex chars "
                f"({_MLDSA_PK_BYTES} bytes ML-DSA-65 pubkey), "
                f"got {len(self.public_key_hex) if isinstance(self.public_key_hex, str) else type(self.public_key_hex)}",
            )
        if not isinstance(self.key_id, str) or len(self.key_id) != _KEY_ID_HEX_LENGTH:
            raise GenesisAssertionError(
                "genesis_assertion_authority_key_id_length_invalid",
                f"key_id must be {_KEY_ID_HEX_LENGTH} hex chars, "
                f"got {len(self.key_id) if isinstance(self.key_id, str) else type(self.key_id)}",
            )

    def to_dict(self) -> dict:
        """Canonical dict form for JSON serialization."""
        return {
            "algorithm": self.algorithm,
            "public_key_hex": self.public_key_hex,
            "key_id": self.key_id,
        }


@dataclass(frozen=True)
class GenesisAssertionContent:
    """Content schema for a genesis-authority assert.truth object.

    This is the payload.content field of the GenesisAssertTruth submission
    (Phase 855 §4.1, Phase 856 §3.2).

    Immutable — all fields are set at construction and validated via validate().

    Token: hb_001_genesis_assertion_content_schema
    """
    kind: str                              # must be GENESIS_AUTHORITY_ASSERTION_PRIMITIVE_TYPE
    schema_version: int                    # must be ASSERTION_PROTOCOL_VERSION (1)
    network_id: str                        # canonical network identifier
    is_testnet: bool                       # true for testnet, false for mainnet
    real_ecu: bool                         # true when ECU has real economic weight
    genesis_epoch: int                     # must be GENESIS_EPOCH (0)
    genesis_authority_key: GenesisAuthorityKey
    validators: tuple[GenesisValidatorEntry, ...]
    f: int                                 # max faulty validators tolerated; quorum = 2f+1
    predecessor_genesis_cid: Optional[str] = None  # always None at genesis; non-None for upgrades

    def validate(self) -> None:
        """Full structural validation. Raises GenesisAssertionError on any violation."""
        if self.kind != GENESIS_AUTHORITY_ASSERTION_PRIMITIVE_TYPE:
            raise GenesisAssertionError(
                "genesis_assertion_content_kind_invalid",
                f"kind must be {GENESIS_AUTHORITY_ASSERTION_PRIMITIVE_TYPE!r}, got {self.kind!r}",
            )
        if self.schema_version != ASSERTION_PROTOCOL_VERSION:
            raise GenesisAssertionError(
                "genesis_assertion_content_schema_version_invalid",
                f"schema_version must be {ASSERTION_PROTOCOL_VERSION}, got {self.schema_version}",
            )
        if not isinstance(self.network_id, str) or not self.network_id:
            raise GenesisAssertionError(
                "genesis_assertion_content_network_id_empty",
                "network_id must be a non-empty string",
            )
        if isinstance(self.is_testnet, bool) is False:
            raise GenesisAssertionError(
                "genesis_assertion_content_is_testnet_must_be_bool",
                f"is_testnet must be a bool, got {type(self.is_testnet)}",
            )
        if isinstance(self.real_ecu, bool) is False:
            raise GenesisAssertionError(
                "genesis_assertion_content_real_ecu_must_be_bool",
                f"real_ecu must be a bool, got {type(self.real_ecu)}",
            )
        if self.genesis_epoch != GENESIS_EPOCH:
            raise GenesisAssertionError(
                "genesis_assertion_content_genesis_epoch_must_be_zero",
                f"genesis_epoch must be {GENESIS_EPOCH}, got {self.genesis_epoch}",
            )
        self.genesis_authority_key.validate()
        if not self.validators:
            raise GenesisAssertionError(
                "genesis_assertion_content_validators_empty",
                "validators must contain at least one entry",
            )
        validator_ids = []
        for v in self.validators:
            v.validate()
            validator_ids.append(v.validator_id)
        if len(validator_ids) != len(set(validator_ids)):
            raise GenesisAssertionError(
                "genesis_assertion_content_duplicate_validator_ids",
                "validators must have unique validator_id values",
            )
        if sorted(validator_ids) != list(range(1, len(validator_ids) + 1)):
            raise GenesisAssertionError(
                "genesis_assertion_content_validator_ids_not_sequential",
                "validator_id values must be sequential starting at 1",
            )
        n = len(self.validators)
        if isinstance(self.f, bool) or not isinstance(self.f, int) or self.f < 0:
            raise GenesisAssertionError(
                "genesis_assertion_content_f_must_be_non_negative_int",
                f"f must be a non-negative integer, got {self.f!r}",
            )
        # BFT constraint: 2f + 1 ≤ n (quorum must be achievable)
        if 2 * self.f + 1 > n:
            raise GenesisAssertionError(
                "genesis_assertion_content_f_too_large_for_validator_set",
                f"f={self.f} requires quorum of {2*self.f+1} but only {n} validators; "
                f"2f+1 must be ≤ n",
            )
        if self.predecessor_genesis_cid is not None and not isinstance(self.predecessor_genesis_cid, str):
            raise GenesisAssertionError(
                "genesis_assertion_content_predecessor_genesis_cid_must_be_string_or_none",
                "predecessor_genesis_cid must be a CIDv1 string or None",
            )

    def to_dict(self) -> dict:
        """Canonical dict form for JSON serialization (sort_keys applies at encode step)."""
        d: dict = {
            "kind": self.kind,
            "schema_version": self.schema_version,
            "network_id": self.network_id,
            "is_testnet": self.is_testnet,
            "real_ecu": self.real_ecu,
            "genesis_epoch": self.genesis_epoch,
            "genesis_authority_key": self.genesis_authority_key.to_dict(),
            "validators": [v.to_dict() for v in self.validators],
            "f": self.f,
        }
        if self.predecessor_genesis_cid is not None:
            d["predecessor_genesis_cid"] = self.predecessor_genesis_cid
        return d


# ---------------------------------------------------------------------------
# Encoding and verification
# ---------------------------------------------------------------------------

def encode_genesis_assertion_payload(content: GenesisAssertionContent) -> bytes:
    """Produce canonical JSON bytes of the genesis assertion payload for ML-DSA-65 signing.

    The bytes produced here are what the genesis authority's ML-DSA-65 key signs.
    The actual signing is performed by the Rust pq_keygen binary (CDL-069 §2a).

    Validates the content before encoding; raises GenesisAssertionError on failure.

    The canonical form is JSON with sort_keys=True and no whitespace, consistent
    with the ILC protocol canonical JSON discipline.

    Token: hb_001_encode_genesis_assertion_payload
    """
    content.validate()
    payload = {
        "v": ASSERTION_PROTOCOL_VERSION,
        "primitive": "assert.truth",
        "epoch": GENESIS_EPOCH,
        "payload": {
            "content": content.to_dict(),
            "primitive_type": GENESIS_AUTHORITY_ASSERTION_PRIMITIVE_TYPE,
            "epistemic_type": GENESIS_AUTHORITY_ASSERTION_EPISTEMIC_TYPE,
            "refutation_criterion": None,
            "parent_node_ids": [],
        },
    }
    # Note: `shard_id` is omitted (system-scope per Phase 856 §3.3).
    # Note: `agent_id` and `sig` are attached by the caller after ML-DSA signing.
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")


def verify_genesis_assertion_schema(data: dict, *, expected_network_id: str) -> GenesisAssertionContent:
    """Verify the structural schema of a genesis assertion object.

    Validates all required fields and constraints. Does NOT verify the
    ML-DSA-65 cryptographic signature — that requires the Rust PQ layer or
    an oqs-python binding.

    Parameters
    ----------
    data:
        The parsed genesis assertion dict (outer envelope: v, primitive, epoch,
        payload, agent_id, sig).
    expected_network_id:
        The network_id the caller expects. Raises if mismatch.

    Returns
    -------
    GenesisAssertionContent
        The validated content object.

    Raises
    ------
    GenesisAssertionError
        On any structural violation.

    Token: hb_001_verify_genesis_assertion_schema
    """
    if not isinstance(data, dict):
        raise GenesisAssertionError(
            "genesis_assertion_verify_data_must_be_dict",
            "genesis assertion data must be a dict",
        )

    # Outer envelope checks
    v = data.get("v")
    if v != ASSERTION_PROTOCOL_VERSION:
        raise GenesisAssertionError(
            "genesis_assertion_verify_version_mismatch",
            f"assertion envelope v must be {ASSERTION_PROTOCOL_VERSION}, got {v!r}",
        )
    primitive = data.get("primitive")
    if primitive != "assert.truth":
        raise GenesisAssertionError(
            "genesis_assertion_verify_primitive_mismatch",
            f"primitive must be 'assert.truth', got {primitive!r}",
        )
    epoch = data.get("epoch")
    if epoch != GENESIS_EPOCH:
        raise GenesisAssertionError(
            "genesis_assertion_verify_epoch_must_be_zero",
            f"genesis assertion epoch must be {GENESIS_EPOCH}, got {epoch!r}",
        )

    # Payload
    payload = data.get("payload")
    if not isinstance(payload, dict):
        raise GenesisAssertionError(
            "genesis_assertion_verify_payload_must_be_dict",
            "payload must be a dict",
        )
    primitive_type = payload.get("primitive_type")
    if primitive_type != GENESIS_AUTHORITY_ASSERTION_PRIMITIVE_TYPE:
        raise GenesisAssertionError(
            "genesis_assertion_verify_primitive_type_mismatch",
            f"payload.primitive_type must be {GENESIS_AUTHORITY_ASSERTION_PRIMITIVE_TYPE!r}, "
            f"got {primitive_type!r}",
        )

    # Content
    content_dict = payload.get("content")
    if not isinstance(content_dict, dict):
        raise GenesisAssertionError(
            "genesis_assertion_verify_content_must_be_dict",
            "payload.content must be a dict",
        )

    content = _content_from_dict(content_dict)
    content.validate()

    if content.network_id != expected_network_id:
        raise GenesisAssertionError(
            "genesis_assertion_verify_network_id_mismatch",
            f"genesis assertion network_id {content.network_id!r} does not match "
            f"expected {expected_network_id!r}",
        )

    return content


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _authority_key_from_dict(d: object) -> GenesisAuthorityKey:
    if not isinstance(d, dict):
        raise GenesisAssertionError(
            "genesis_assertion_authority_key_must_be_dict",
            "genesis_authority_key must be a dict",
        )
    return GenesisAuthorityKey(
        algorithm=d.get("algorithm", ""),
        public_key_hex=d.get("public_key_hex", ""),
        key_id=d.get("key_id", ""),
    )


def _validator_from_dict(d: object, index: int) -> GenesisValidatorEntry:
    if not isinstance(d, dict):
        raise GenesisAssertionError(
            "genesis_assertion_validator_entry_must_be_dict",
            f"validators[{index}] must be a dict",
        )
    return GenesisValidatorEntry(
        validator_id=d.get("validator_id", -1),
        agent_id=d.get("agent_id", ""),
        validator_key=d.get("validator_key", ""),
        stake_micro_ecu=d.get("stake_micro_ecu", ""),
        role=d.get("role", ""),
    )


def _content_from_dict(d: dict) -> GenesisAssertionContent:
    """Deserialize GenesisAssertionContent from a plain dict."""
    raw_validators = d.get("validators", [])
    if not isinstance(raw_validators, list):
        raise GenesisAssertionError(
            "genesis_assertion_validators_must_be_list",
            "content.validators must be a list",
        )
    validators = tuple(
        _validator_from_dict(v, i) for i, v in enumerate(raw_validators)
    )
    raw_key = d.get("genesis_authority_key")
    authority_key = _authority_key_from_dict(raw_key)

    f_val = d.get("f", -1)
    if isinstance(f_val, bool):
        f_val = -1  # reject bool (Python bool is subclass of int)

    return GenesisAssertionContent(
        kind=d.get("kind", ""),
        schema_version=d.get("schema_version", -1),
        network_id=d.get("network_id", ""),
        is_testnet=bool(d.get("is_testnet", False)),
        real_ecu=bool(d.get("real_ecu", False)),
        genesis_epoch=d.get("genesis_epoch", -1),
        genesis_authority_key=authority_key,
        validators=validators,
        f=f_val,
        predecessor_genesis_cid=d.get("predecessor_genesis_cid"),
    )
