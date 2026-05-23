"""ILC package profile constants (Gap 14, Phase 1436a).

These constants define canonical Python package profile names.
They are not ADR-0009 protocol-native bundle layers.
"""

from __future__ import annotations


PACKAGE_PROFILES_VERSION: str = "package_profiles_1436a.v0.1"

GAP_14_PHASE_1_TOKEN: str = (
    "gap_14_phase_1_package_profile_definition_complete_phase_1436a"
)

PROFILE_PROTOCOL_CORE: str = "protocol-core"
PROFILE_OPERATOR_NODE: str = "operator-node"
PROFILE_OPENCLAW_HOSTED: str = "openclaw-hosted"
PROFILE_DEV: str = "dev"

DEFINED_PROFILES: tuple[str, ...] = (
    PROFILE_PROTOCOL_CORE,
    PROFILE_OPERATOR_NODE,
    PROFILE_OPENCLAW_HOSTED,
    PROFILE_DEV,
)

PHASE_1436_NOT_ACTIVATED: bool = True
PUBLIC_RC_NOT_ACTIVATED: bool = True
