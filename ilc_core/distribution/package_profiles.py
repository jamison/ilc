# SPDX-License-Identifier: AGPL-3.0-or-later
"""ILC package profile constants (Gap 14, Phases 1436a-1436b).

These constants define canonical Python package profile names.
They are not ADR-0009 protocol-native bundle layers.
"""

from __future__ import annotations


PACKAGE_PROFILES_VERSION: str = "package_profiles_1436b.v0.1"

GAP_14_PHASE_1_TOKEN: str = (
    "gap_14_phase_1_package_profile_definition_complete_phase_1436a"
)

PROFILE_PROTOCOL_CORE: str = "protocol-core"
PROFILE_OPERATOR_NODE: str = "operator-node"
PROFILE_OPENCLAW_HOSTED: str = "openclaw-hosted"
PROFILE_PUBLIC_RC: str = "public-rc"
PROFILE_DEV: str = "dev"

DEFINED_PROFILES: tuple[str, ...] = (
    PROFILE_PROTOCOL_CORE,
    PROFILE_OPERATOR_NODE,
    PROFILE_OPENCLAW_HOSTED,
    PROFILE_PUBLIC_RC,
    PROFILE_DEV,
)

GAP_14_PHASE_2_TOKEN: str = "gap_14_phase_2_public_rc_profile_complete_phase_1436b"
GAP_14_CLOSED_TOKEN: str = "gap_14_closed_phase_1436b"
GAP_13_CLOSED_TOKEN: str = "gap_13_closed_phase_1441"
GAP_13_CLOSURE_VERDICT_PASS_TOKEN: str = "gap_13_closure_verdict_pass_phase_1441"

# phase_1436_not_activated_disposition_recorded_phase_1491p:
# intentionally maintained. This distribution-layer constant records that
# Phase 1436a/1436b package-profile artifacts did not themselves activate the
# Phase 1436 public path; runtime activation lives in sidecars/public_path_activation.py.
PHASE_1436_NOT_ACTIVATED: bool = True
PUBLIC_RC_NOT_ACTIVATED: bool = True
