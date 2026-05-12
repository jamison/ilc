"""Public-RC package profile contracts.

This module defines code-level package profiles for OpenClaw/NemoClaw-first RC
work without opening a public P2P claim. It is intentionally declarative: the
profiles can be consumed by packaging, CI, or harness adapters without importing
network servers, LMDB, or wall-clock runtime surfaces.

``NON_EXCISABLE_COMPONENTS`` is a packaging integrity guard. It prevents declared
ILC package profiles from accidentally omitting Genesis, ILC, ECU, protocol
bundle, canonical JSON, or Rust consensus-core binding surfaces. It is not a
fork-prevention mechanism; adversarial forks are addressed by Genesis lineage,
ratified CDL authority, and license/IP policy.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

PUBLIC_RC_PACKAGE_PROFILES_VERSION = "public_rc_package_profiles_1307.v0.1"

PROFILE_OPENCLAW_SKILL_LOCAL = "openclaw_skill_local"
PROFILE_OPENCLAW_SKILL_CLAIMABLE = "openclaw_skill_claimable"
PROFILE_CONFIDENTIAL_COORDINATION_LOCAL_PREVIEW = (
    "confidential_coordination_local_preview"
)
PROFILE_ILC_LOGIC_LIBRARY = "ilc_logic_library"
PROFILE_ILC_CLI_LOCAL = "ilc_cli_local"
PROFILE_LOCAL_SIDECAR_DAEMON = "local_sidecar_daemon"
PROFILE_FULL_NODE_PUBLIC_P2P = "full_node_public_p2p"

NON_EXCISABLE_COMPONENTS = frozenset(
    {
        "canonical_json_policy",
        "ecu_ilc_economic_boundary",
        "genesis_lineage_verification",
        "ilc_identity_namespace",
        "protocol_bundle_verification",
        "rust_consensus_core_binding",
    }
)

PROFILE_COMPONENTS = frozenset(
    {
        *NON_EXCISABLE_COMPONENTS,
        "cli_subprocess_surface",
        "confidential_coordination_local_preview_profile",
        "ecu_to_ilc_conversion_runtime",
        "graph_native_sidecar_registry_manifest",
        "harness_adapter_contracts",
        "ilc_logic_import_surface",
        "local_node_runtime",
        "local_sidecar_query_runtime",
        "offline_claimability_receipt_verifier_sidecar",
        "openclaw_compatible_local_bridge",
        "public_claimability_runtime",
        "rust_consensus_core_binding",
        "rust_public_p2p_node",
        "storage_adapter_contracts",
        "transport_harness_contracts",
        "transport_principal_identity",
        "value_path_activation_boundary_preflight_sidecar",
        "wallet_action_semantics_preflight_sidecar",
    }
)

PROFILE_PACKAGE_SURFACES = {
    PROFILE_OPENCLAW_SKILL_LOCAL: (
        "ilc_logic",
        "ilc_cli",
        "ilc_harness_adapters",
        "local_sidecar",
    ),
    PROFILE_OPENCLAW_SKILL_CLAIMABLE: (
        "ilc_logic",
        "ilc_cli",
        "ilc_harness_adapters",
        "local_sidecar",
        "public_claimability",
    ),
    PROFILE_CONFIDENTIAL_COORDINATION_LOCAL_PREVIEW: (
        "ilc_logic",
        "ilc_cli",
        "ilc_harness_adapters",
        "local_sidecar",
    ),
    PROFILE_ILC_LOGIC_LIBRARY: ("ilc_logic",),
    PROFILE_ILC_CLI_LOCAL: ("ilc_logic", "ilc_cli"),
    PROFILE_LOCAL_SIDECAR_DAEMON: (
        "ilc_logic",
        "ilc_cli",
        "ilc_harness_adapters",
        "local_node_runtime",
        "local_sidecar",
    ),
    PROFILE_FULL_NODE_PUBLIC_P2P: (
        "ilc_logic",
        "ilc_cli",
        "ilc_harness_adapters",
        "local_node_runtime",
        "local_sidecar",
        "public_claimability",
        "rust_public_p2p",
    ),
}


@dataclass(frozen=True)
class PackageProfile:
    profile_id: str
    display_name: str
    description: str
    components: frozenset[str]
    public_p2p: bool
    public_claimability: bool
    local_preview_eligible: bool
    public_rc_eligible: bool
    notes: tuple[str, ...] = ()


PACKAGE_PROFILES = {
    PROFILE_OPENCLAW_SKILL_LOCAL: PackageProfile(
        profile_id=PROFILE_OPENCLAW_SKILL_LOCAL,
        display_name="OpenClaw/NemoClaw local skill",
        description=(
            "Local harness-consumable ILC package profile: importable logic, CLI subprocess "
            "surface, harness adapter contracts, and local sidecar query runtime. This profile "
            "does not make a public P2P claim."
        ),
        components=frozenset(
            {
                *NON_EXCISABLE_COMPONENTS,
                "cli_subprocess_surface",
                "graph_native_sidecar_registry_manifest",
                "harness_adapter_contracts",
                "ilc_logic_import_surface",
                "local_sidecar_query_runtime",
                "openclaw_compatible_local_bridge",
                "rust_consensus_core_binding",
                "storage_adapter_contracts",
                "transport_harness_contracts",
            }
        ),
        public_p2p=False,
        public_claimability=False,
        local_preview_eligible=True,
        public_rc_eligible=False,
        notes=(
            "Local preview path: OpenClaw/NemoClaw skill-first with no public P2P claim and no public claimability claim.",
            "Harnesses may route payloads over their own transport; ILC does not treat that transport as protocol law.",
        ),
    ),
    PROFILE_OPENCLAW_SKILL_CLAIMABLE: PackageProfile(
        profile_id=PROFILE_OPENCLAW_SKILL_CLAIMABLE,
        display_name="OpenClaw/NemoClaw claimable skill",
        description=(
            "Public-RC target profile for an OpenClaw/NemoClaw-consumable ILC skill: local "
            "harness integration, no ILC-owned public P2P claim, and public ECU-to-ILC "
            "claimability surfaces included."
        ),
        components=frozenset(
            {
                *NON_EXCISABLE_COMPONENTS,
                "cli_subprocess_surface",
                "ecu_to_ilc_conversion_runtime",
                "graph_native_sidecar_registry_manifest",
                "harness_adapter_contracts",
                "ilc_logic_import_surface",
                "local_sidecar_query_runtime",
                "offline_claimability_receipt_verifier_sidecar",
                "openclaw_compatible_local_bridge",
                "public_claimability_runtime",
                "storage_adapter_contracts",
                "transport_harness_contracts",
                "value_path_activation_boundary_preflight_sidecar",
                "wallet_action_semantics_preflight_sidecar",
            }
        ),
        public_p2p=False,
        public_claimability=True,
        local_preview_eligible=True,
        public_rc_eligible=True,
        notes=(
            "Default final public-RC target: OpenClaw/NemoClaw skill-first, public claimability present, no ILC public P2P claim.",
            "Requires Gap 13 conversion and public claimability gates before any public RC claim.",
        ),
    ),
    PROFILE_CONFIDENTIAL_COORDINATION_LOCAL_PREVIEW: PackageProfile(
        profile_id=PROFILE_CONFIDENTIAL_COORDINATION_LOCAL_PREVIEW,
        display_name="Confidential coordination local preview",
        description=(
            "Private/local graph-native coordination preview profile: sidecar registry, "
            "OpenClaw/NemoClaw-compatible harness bridge, local graph projection seams, "
            "and confidential-coordination manifest metadata. This profile is private "
            "by default and does not make a public confidential messaging claim."
        ),
        components=frozenset(
            {
                *NON_EXCISABLE_COMPONENTS,
                "cli_subprocess_surface",
                "confidential_coordination_local_preview_profile",
                "graph_native_sidecar_registry_manifest",
                "harness_adapter_contracts",
                "ilc_logic_import_surface",
                "local_sidecar_query_runtime",
                "openclaw_compatible_local_bridge",
                "storage_adapter_contracts",
                "transport_harness_contracts",
            }
        ),
        public_p2p=False,
        public_claimability=False,
        local_preview_eligible=True,
        public_rc_eligible=False,
        notes=(
            "Local/private preview only; no public confidential messaging or coordination claim.",
            "OpenClaw/NemoClaw, DigitalOcean droplets, and equivalent harnesses are hosts, not protocol substrates.",
        ),
    ),
    PROFILE_ILC_LOGIC_LIBRARY: PackageProfile(
        profile_id=PROFILE_ILC_LOGIC_LIBRARY,
        display_name="ILC logic library",
        description="Pure import surface for epistemic logic and canonical verification helpers.",
        components=frozenset(
            {
                *NON_EXCISABLE_COMPONENTS,
                "ilc_logic_import_surface",
                "rust_consensus_core_binding",
            }
        ),
        public_p2p=False,
        public_claimability=False,
        local_preview_eligible=True,
        public_rc_eligible=False,
    ),
    PROFILE_ILC_CLI_LOCAL: PackageProfile(
        profile_id=PROFILE_ILC_CLI_LOCAL,
        display_name="ILC local CLI",
        description="Local operator and harness subprocess interface; no public P2P service.",
        components=frozenset(
            {
                *NON_EXCISABLE_COMPONENTS,
                "cli_subprocess_surface",
                "ilc_logic_import_surface",
                "rust_consensus_core_binding",
            }
        ),
        public_p2p=False,
        public_claimability=False,
        local_preview_eligible=True,
        public_rc_eligible=False,
    ),
    PROFILE_LOCAL_SIDECAR_DAEMON: PackageProfile(
        profile_id=PROFILE_LOCAL_SIDECAR_DAEMON,
        display_name="ILC local sidecar daemon",
        description=(
            "Loopback-only sidecar profile for local graph projection/query consumption. "
            "Unlike openclaw_skill_local, this profile includes local node runtime wiring. "
            "Binding beyond loopback requires TransportPrincipal and public policy gates."
        ),
        components=frozenset(
            {
                *NON_EXCISABLE_COMPONENTS,
                "cli_subprocess_surface",
                "graph_native_sidecar_registry_manifest",
                "harness_adapter_contracts",
                "ilc_logic_import_surface",
                "local_node_runtime",
                "local_sidecar_query_runtime",
                "openclaw_compatible_local_bridge",
                "rust_consensus_core_binding",
                "storage_adapter_contracts",
                "transport_harness_contracts",
            }
        ),
        public_p2p=False,
        public_claimability=False,
        local_preview_eligible=True,
        public_rc_eligible=False,
        notes=("Loopback/local only; no public sidecar endpoint claim.",),
    ),
    PROFILE_FULL_NODE_PUBLIC_P2P: PackageProfile(
        profile_id=PROFILE_FULL_NODE_PUBLIC_P2P,
        display_name="Full node with public P2P",
        description=(
            "Complete node profile: local runtime, storage adapters, Rust public P2P node, "
            "TransportPrincipal identity, and claimability/conversion surfaces when authorized."
        ),
        components=frozenset(
            {
                *NON_EXCISABLE_COMPONENTS,
                "cli_subprocess_surface",
                "ecu_to_ilc_conversion_runtime",
                "graph_native_sidecar_registry_manifest",
                "harness_adapter_contracts",
                "ilc_logic_import_surface",
                "local_node_runtime",
                "local_sidecar_query_runtime",
                "offline_claimability_receipt_verifier_sidecar",
                "openclaw_compatible_local_bridge",
                "public_claimability_runtime",
                "rust_consensus_core_binding",
                "rust_public_p2p_node",
                "storage_adapter_contracts",
                "transport_harness_contracts",
                "transport_principal_identity",
                "value_path_activation_boundary_preflight_sidecar",
                "wallet_action_semantics_preflight_sidecar",
            }
        ),
        public_p2p=True,
        public_claimability=True,
        local_preview_eligible=False,
        public_rc_eligible=False,
        notes=(
            "Not eligible for public RC until TransportPrincipal, Rust P2P, ECU-to-ILC conversion, and public claimability gates close.",
        ),
    ),
}


def get_package_profile(profile_id: str) -> PackageProfile:
    try:
        return PACKAGE_PROFILES[profile_id]
    except KeyError as exc:
        raise ValueError("public_rc_package_profile_unknown") from exc


def validate_package_profile(profile: PackageProfile) -> None:
    if not isinstance(profile, PackageProfile):
        raise ValueError("public_rc_package_profile_must_be_package_profile")
    if type(profile.components) is not frozenset:
        raise ValueError("public_rc_package_profile_components_must_be_frozenset")
    if type(profile.public_p2p) is not bool:
        raise ValueError("public_rc_package_profile_public_p2p_must_be_bool")
    if type(profile.public_claimability) is not bool:
        raise ValueError("public_rc_package_profile_public_claimability_must_be_bool")
    if type(profile.local_preview_eligible) is not bool:
        raise ValueError("public_rc_package_profile_local_preview_eligible_must_be_bool")
    if type(profile.public_rc_eligible) is not bool:
        raise ValueError("public_rc_package_profile_public_rc_eligible_must_be_bool")

    unknown = profile.components - PROFILE_COMPONENTS
    if unknown:
        raise ValueError("public_rc_package_profile_unknown_component")

    missing_non_excisable = NON_EXCISABLE_COMPONENTS - profile.components
    if missing_non_excisable:
        raise ValueError("public_rc_package_profile_missing_non_excisable_component")

    if profile.public_p2p:
        required = frozenset({"rust_public_p2p_node", "transport_principal_identity"})
        if not required <= profile.components:
            raise ValueError("public_rc_public_p2p_profile_requires_transport_principal")

    if profile.public_claimability:
        required = frozenset(
            {
                "ecu_to_ilc_conversion_runtime",
                "offline_claimability_receipt_verifier_sidecar",
                "public_claimability_runtime",
                "value_path_activation_boundary_preflight_sidecar",
                "wallet_action_semantics_preflight_sidecar",
            }
        )
        if not required <= profile.components:
            raise ValueError("public_rc_claimability_profile_requires_conversion_and_claimability")

    if profile.public_rc_eligible and profile.public_p2p:
        raise ValueError("public_rc_skill_first_profile_must_not_claim_public_p2p")
    if profile.public_rc_eligible and not profile.public_claimability:
        raise ValueError("public_rc_profile_requires_public_claimability")
    if "confidential_coordination_local_preview_profile" in profile.components:
        if profile.public_claimability or profile.public_p2p or profile.public_rc_eligible:
            raise ValueError("confidential_coordination_local_preview_must_not_claim_public_rc")
        if not profile.local_preview_eligible:
            raise ValueError("confidential_coordination_local_preview_must_be_local_preview")


def validate_all_package_profiles() -> None:
    for profile in PACKAGE_PROFILES.values():
        validate_package_profile(profile)


def profile_manifest(profile: PackageProfile | str) -> dict[str, Any]:
    active = get_package_profile(profile) if isinstance(profile, str) else profile
    validate_package_profile(active)
    package_surfaces = PROFILE_PACKAGE_SURFACES.get(active.profile_id)
    if package_surfaces is None:
        raise ValueError("public_rc_package_profile_missing_surface_contract")
    return {
        "components": sorted(active.components),
        "description": active.description,
        "display_name": active.display_name,
        "local_preview_eligible": active.local_preview_eligible,
        "non_excisable_components": sorted(NON_EXCISABLE_COMPONENTS),
        "notes": list(active.notes),
        "package_surfaces": list(package_surfaces),
        "profile_id": active.profile_id,
        "public_claimability": active.public_claimability,
        "public_p2p": active.public_p2p,
        "public_rc_eligible": active.public_rc_eligible,
        "version": PUBLIC_RC_PACKAGE_PROFILES_VERSION,
    }


def export_profile_manifest_json(profile: PackageProfile | str) -> str:
    return json.dumps(
        profile_manifest(profile),
        allow_nan=False,
        separators=(",", ":"),
        sort_keys=True,
    )


__all__ = [
    "NON_EXCISABLE_COMPONENTS",
    "PACKAGE_PROFILES",
    "PROFILE_CONFIDENTIAL_COORDINATION_LOCAL_PREVIEW",
    "PROFILE_FULL_NODE_PUBLIC_P2P",
    "PROFILE_ILC_CLI_LOCAL",
    "PROFILE_ILC_LOGIC_LIBRARY",
    "PROFILE_LOCAL_SIDECAR_DAEMON",
    "PROFILE_OPENCLAW_SKILL_CLAIMABLE",
    "PROFILE_OPENCLAW_SKILL_LOCAL",
    "PROFILE_PACKAGE_SURFACES",
    "PUBLIC_RC_PACKAGE_PROFILES_VERSION",
    "PackageProfile",
    "export_profile_manifest_json",
    "get_package_profile",
    "profile_manifest",
    "validate_all_package_profiles",
    "validate_package_profile",
]
