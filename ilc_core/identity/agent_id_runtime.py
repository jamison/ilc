"""CDL-042 agent identity namespace runtime.

Deterministic key-derived agent_id helpers with CDL-001 trust-root anchoring
and machine-auditable validation tokens.
"""

from __future__ import annotations

import hashlib

from ilc_core.node.promotion_continuity_runtime_364 import CDL_038_DEPENDENCY

AGENT_ID_RUNTIME_VERSION = "agent_id_runtime_410.v0.1"
CDL_042_DEPENDENCY = "cdl_042_ratified_407.v0.1"
NODE_SCHEMA_DEPENDENCY = CDL_038_DEPENDENCY

_AGENT_ID_DOMAIN_PREFIX = b"ilc-agent-id-v1:"


class AgentIdentityError(ValueError):
    """Deterministic validation error with machine-auditable token."""

    def __init__(self, token: str, message: str) -> None:
        super().__init__(message)
        self.token = token


def derive_agent_id(canonical_root_key_bytes: bytes) -> str:
    """Derive agent_id deterministically from canonical_root_key public bytes."""

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

    digest = hashlib.sha256(_AGENT_ID_DOMAIN_PREFIX + canonical_root_key_bytes).hexdigest()
    return f"agent-{digest}"


def verify_agent_id(agent_id: str, canonical_root_key_bytes: bytes) -> bool:
    """Verify that agent_id matches the deterministic root-key derivation."""

    if not isinstance(agent_id, str):
        raise AgentIdentityError(
            "cdl_042_agent_id_invalid_id_type",
            "agent_id must be a string",
        )
    expected = derive_agent_id(canonical_root_key_bytes)
    return agent_id == expected
