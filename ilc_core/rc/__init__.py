# SPDX-License-Identifier: AGPL-3.0-or-later
from .atlas_graph_discipline import (
    ATLAS_G_004_005_BRIDGE_VERSION,
    ATLAS_G_006_MANIFEST_PROFILE_CONSISTENCY_FIX1_TOKEN,
    ATLAS_G_006_PUBLIC_RC_GRAPH_REACHABILITY_GATE_VERSION,
    build_atlas_g_004_005_artifact,
    build_atlas_g_006_public_rc_graph_reachability_gate,
    build_high_authority_source_classification,
    build_import_dependency_graph_bridge,
    ATLAS_GRAPH_DISCIPLINE_VERSION,
    export_atlas_g_004_005_artifact_json,
    export_atlas_g_006_public_rc_graph_reachability_gate_json,
    export_package_profile_reachability_manifest_json,
    package_profile_reachability_manifest,
    validate_graph_delta,
)
from .package_profiles import (
    NON_EXCISABLE_COMPONENTS,
    PACKAGE_PROFILES,
    PROFILE_CONFIDENTIAL_COORDINATION_LOCAL_PREVIEW,
    PROFILE_FULL_NODE_PUBLIC_P2P,
    PROFILE_OPENCLAW_SKILL_CLAIMABLE,
    PROFILE_OPENCLAW_SKILL_LOCAL,
    PUBLIC_RC_PACKAGE_PROFILES_VERSION,
    export_profile_manifest_json,
    get_package_profile,
    profile_manifest,
    validate_all_package_profiles,
    validate_package_profile,
)

_ECONOMIC_CYCLE_EXPORTS = frozenset(
    {
        "export_wallet_state",
        "materialize_economic_cycle",
        "materialize_graph_state",
        "settle_economic_cycle",
    }
)


def __getattr__(name: str):
    """Lazy-load heavyweight RC runtime helpers on demand.

    The package-profile and harness-adapter modules are intentionally lightweight
    OpenClaw/NemoClaw-facing surfaces. Importing ``ilc_core.rc`` must not
    eagerly import LMDB, storage runtimes, or wall-clock runtime helpers just to
    access declarative profile contracts.
    """

    if name in _ECONOMIC_CYCLE_EXPORTS:
        from . import economic_cycle_runtime as runtime

        value = getattr(runtime, name)
        globals()[name] = value
        return value
    raise AttributeError(f"module 'ilc_core.rc' has no attribute {name!r}")


__all__ = [
    "ATLAS_G_004_005_BRIDGE_VERSION",
    "ATLAS_G_006_MANIFEST_PROFILE_CONSISTENCY_FIX1_TOKEN",
    "ATLAS_G_006_PUBLIC_RC_GRAPH_REACHABILITY_GATE_VERSION",
    "ATLAS_GRAPH_DISCIPLINE_VERSION",
    "NON_EXCISABLE_COMPONENTS",
    "PACKAGE_PROFILES",
    "PROFILE_CONFIDENTIAL_COORDINATION_LOCAL_PREVIEW",
    "PROFILE_FULL_NODE_PUBLIC_P2P",
    "PROFILE_OPENCLAW_SKILL_CLAIMABLE",
    "PROFILE_OPENCLAW_SKILL_LOCAL",
    "PUBLIC_RC_PACKAGE_PROFILES_VERSION",
    "build_atlas_g_004_005_artifact",
    "build_atlas_g_006_public_rc_graph_reachability_gate",
    "build_high_authority_source_classification",
    "build_import_dependency_graph_bridge",
    "export_atlas_g_004_005_artifact_json",
    "export_atlas_g_006_public_rc_graph_reachability_gate_json",
    "export_package_profile_reachability_manifest_json",
    "export_profile_manifest_json",
    "export_wallet_state",
    "get_package_profile",
    "materialize_economic_cycle",
    "materialize_graph_state",
    "package_profile_reachability_manifest",
    "profile_manifest",
    "settle_economic_cycle",
    "validate_all_package_profiles",
    "validate_graph_delta",
    "validate_package_profile",
]
