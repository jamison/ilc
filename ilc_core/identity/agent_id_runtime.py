# SPDX-License-Identifier: AGPL-3.0-only
"""CDL-042 / CDL-069 agent identity namespace runtime.

CDL-042 (ratified Phase 407): key-derived agent_id via SHA-256.
CDL-069 (open Phase 838): identity_seed-derived agent_id via SHA-384 (Tier 3).

CDL-069 amends CDL-042.  From Genesis forward the canonical derivation is:

    agent_id = sha384("ilc-agent-id-v1:" || identity_seed)   [96 hex chars]

The legacy BLS-key-derived path (sha256, "agent-{hex}") is retained for
backward compatibility with pre-Genesis testnet agents and tests.  It is
explicitly deprecated: no new agent should be created with the legacy path.

CDL-042 continuity guarantee (preserved): no key event — rotation, recovery,
algorithm migration — changes agent_id, because agent_id is now derived from
the permanent identity_seed, not from any key material.
"""

from __future__ import annotations

import hashlib

from ilc_core.node.promotion_continuity_runtime_364 import CDL_038_DEPENDENCY

# Bumped to v0.2 to reflect CDL-069 amendment (identity_seed + SHA-384 path).
AGENT_ID_RUNTIME_VERSION = "agent_id_runtime_838d.v0.2"
CDL_042_DEPENDENCY = "cdl_042_ratified_407.v0.1"
CDL_069_AMENDMENT = "cdl_069_opens_phase_838"
NODE_SCHEMA_DEPENDENCY = CDL_038_DEPENDENCY

# CDL-042 legacy domain (BLS key bytes input).  Deprecated from Genesis forward.
_AGENT_ID_DOMAIN_V1: bytes = b"ilc-agent-id-v1:"

# CDL-069 §2a: SHA-384 uniform for all Tier 3 (permanent) data.
# Domain separator is stable — changing it invalidates all agent_ids.
# V2 intentionally aliases the CDL-042 byte prefix; v1/v2 separation is by
# hash algorithm, input material, output length, and legacy "agent-" prefix,
# not by domain bytes. Do not change without a migration phase.
_AGENT_ID_DOMAIN_V2: bytes = _AGENT_ID_DOMAIN_V1

_IDENTITY_SEED_LENGTH: int = 32  # bytes
_AGENT_ID_LENGTH_V2: int = 96    # hex chars (SHA-384 = 48 bytes)
_AGENT_ID_PREFIX_V1: str = "agent-"


class AgentIdentityError(ValueError):
    """Deterministic validation error with machine-auditable token."""

    def __init__(self, token: str, message: str) -> None:
        super().__init__(message)
        self.token = token


# ---------------------------------------------------------------------------
# CDL-069 canonical path (identity_seed, SHA-384, Tier 3)
# ---------------------------------------------------------------------------

def derive_agent_id_v2(identity_seed: bytes) -> str:
    """Derive agent_id from a 32-byte identity_seed using SHA-384 (CDL-069).

    This is the canonical derivation from Genesis forward.

    agent_id = sha384("ilc-agent-id-v1:" || identity_seed)

    Returns a 96-character lowercase hex string.  The identity_seed is
    permanent — no key event ever changes the agent_id derived from it.
    """
    if not isinstance(identity_seed, bytes):
        raise AgentIdentityError(
            "cdl_069_agent_id_invalid_seed_type",
            "identity_seed must be bytes",
        )
    if len(identity_seed) != _IDENTITY_SEED_LENGTH:
        raise AgentIdentityError(
            "cdl_069_agent_id_invalid_seed_length",
            f"identity_seed must be exactly {_IDENTITY_SEED_LENGTH} bytes, "
            f"got {len(identity_seed)}",
        )
    digest = hashlib.sha384(_AGENT_ID_DOMAIN_V2 + identity_seed).hexdigest()
    if len(digest) != _AGENT_ID_LENGTH_V2:
        raise AgentIdentityError(
            "cdl_069_agent_id_digest_length_invariant_failed",
            "agent_id digest length invariant failed",
        )
    return digest


def verify_agent_id_v2(agent_id: str, identity_seed: bytes) -> bool:
    """Verify agent_id against an identity_seed using CDL-069 derivation."""
    if not isinstance(agent_id, str):
        raise AgentIdentityError(
            "cdl_069_agent_id_invalid_id_type",
            "agent_id must be a str",
        )
    if len(agent_id) != _AGENT_ID_LENGTH_V2:
        return False
    return agent_id == derive_agent_id_v2(identity_seed)


def is_v2_agent_id(agent_id: str) -> bool:
    """Return True if agent_id looks like a CDL-069 v2 id (96 hex chars, no prefix)."""
    if not isinstance(agent_id, str):
        return False
    return (
        len(agent_id) == _AGENT_ID_LENGTH_V2
        and all(c in "0123456789abcdef" for c in agent_id)
    )


# ---------------------------------------------------------------------------
# CDL-042 legacy path (BLS public key bytes, SHA-256) — DEPRECATED
# ---------------------------------------------------------------------------

def derive_agent_id(canonical_root_key_bytes: bytes) -> str:
    """[DEPRECATED — CDL-042 legacy path]

    Derive agent_id from BLS public key bytes using SHA-256.
    Returns "agent-{sha256hex}".

    Retained for backward compatibility with pre-Genesis testnet agents.
    Do NOT use for any agent created from Genesis forward.
    Use derive_agent_id_v2(identity_seed) instead.
    """
    if not isinstance(canonical_root_key_bytes, bytes):
        raise AgentIdentityError(
            "cdl_042_agent_id_invalid_key_type",
            "canonical_root_key_bytes must be bytes",
        )
    if len(canonical_root_key_bytes) == 0:
        raise AgentIdentityError(
            "cdl_042_agent_id_empty_key",
            "canonical_root_key_bytes must not be empty",
        )
    digest = hashlib.sha256(_AGENT_ID_DOMAIN_V1 + canonical_root_key_bytes).hexdigest()
    return f"agent-{digest}"


def verify_agent_id(agent_id: str, canonical_root_key_bytes: bytes) -> bool:
    """[DEPRECATED — CDL-042 legacy path] Verify legacy agent_id."""
    if not isinstance(agent_id, str):
        raise AgentIdentityError(
            "cdl_042_agent_id_invalid_id_type",
            "agent_id must be a string",
        )
    expected = derive_agent_id(canonical_root_key_bytes)
    return agent_id == expected


def is_legacy_agent_id(agent_id: str) -> bool:
    """Return True if agent_id is a CDL-042 legacy id ("agent-{64hex}")."""
    if not isinstance(agent_id, str):
        return False
    return agent_id.startswith(_AGENT_ID_PREFIX_V1) and len(agent_id) == 70
