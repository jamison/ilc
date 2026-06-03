# SPDX-License-Identifier: AGPL-3.0-only
"""Pure primitive-type registry shared by protocol and node runtimes."""

from __future__ import annotations

PRIMITIVE_TYPE_REGISTRY_VERSION = "primitive_type_registry_1250.v0.1"

ALLOWED_PRIMITIVE_TYPES = (
    "citation",
    "execution_descriptor",
    "governance_proposal",
    "knowledge_claim",
    "observation",
)

# System-scope primitive types are consensus/genesis layer only, not
# agent-issuable. Keeping this registry under protocol avoids importing node
# runtime from pure logic modules.
SYSTEM_PRIMITIVE_TYPES = frozenset({
    "genesis_authority_assertion",
    "epoch_record",
})

__all__ = [
    "ALLOWED_PRIMITIVE_TYPES",
    "PRIMITIVE_TYPE_REGISTRY_VERSION",
    "SYSTEM_PRIMITIVE_TYPES",
]
