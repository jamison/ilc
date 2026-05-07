"""Public-RC package profile contracts.

This module defines code-level package profiles for OpenClaw/NemoClaw-first RC
work without opening a public P2P claim. It is intentionally declarative: the
profiles can be consumed by packaging, CI, or harness adapters without importing
network servers, LMDB, or wall-clock runtime surfaces.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

PUBLIC_RC_PACKAGE_PROFILES_VERSION = "public_rc_package_profiles_1238.v0.1"

PROFILE_OPENCLAW_SKILL_LOCAL = "openclaw_skill_local"
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
    }
)

PROFILE_COMPONENTS = frozenset(
    {
        *NON_EXCISABLE_COMPONENTS,
        "cli_subprocess_surface",
        "ecu_to_ilc_conversion_runtime",
        "harness_adapter_contracts",
        "ilc_logic_import_surface",
        "local_node_runtime",
        "local_sidecar_query_runtime",
        "public_claimability_runtime",
        "rust_consensus_core_binding",
        "rust_public_p2p_node",
        "storage_adapter_contracts",
        "transport_harness_contracts",
        "transport_principal_identity",
    }
)


@dataclass(frozen=True)
class PackageProfile:
    profile_id: str
    display_name: str
    description: str
    components: frozenset[str]
    public_p2p: bool
    public_claimability: bool
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
                "harness_adapter_contracts",
                "ilc_logic_import_surface",
                "local_sidecar_query_runtime",
                "rust_consensus_core_binding",
                "storage_adapter_contracts",
                "transport_harness_contracts",
            }
        ),
        public_p2p=False,
        public_claimability=False,
        public_rc_eligible=True,
        notes=(
            "Default public-RC path: OpenClaw/NemoClaw skill-first with no public P2P claim.",
            "Harnesses may route payloads over their own transport; ILC does not treat that transport as protocol law.",
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
        public_rc_eligible=True,
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
        public_rc_eligible=True,
    ),
    PROFILE_LOCAL_SIDECAR_DAEMON: PackageProfile(
        profile_id=PROFILE_LOCAL_SIDECAR_DAEMON,
        display_name="ILC local sidecar daemon",
        description=(
            "Loopback-only sidecar profile for local graph projection/query consumption. "
            "Binding beyond loopback requires TransportPrincipal and public policy gates."
        ),
        components=frozenset(
            {
                *NON_EXCISABLE_COMPONENTS,
                "cli_subprocess_surface",
                "harness_adapter_contracts",
                "ilc_logic_import_surface",
                "local_node_runtime",
                "local_sidecar_query_runtime",
                "rust_consensus_core_binding",
                "storage_adapter_contracts",
                "transport_harness_contracts",
            }
        ),
        public_p2p=False,
        public_claimability=False,
        public_rc_eligible=True,
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
                "harness_adapter_contracts",
                "ilc_logic_import_surface",
                "local_node_runtime",
                "local_sidecar_query_runtime",
                "public_claimability_runtime",
                "rust_consensus_core_binding",
                "rust_public_p2p_node",
                "storage_adapter_contracts",
                "transport_harness_contracts",
                "transport_principal_identity",
            }
        ),
        public_p2p=True,
        public_claimability=True,
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
    if type(profile.public_p2p) is not bool:
        raise ValueError("public_rc_package_profile_public_p2p_must_be_bool")
    if type(profile.public_claimability) is not bool:
        raise ValueError("public_rc_package_profile_public_claimability_must_be_bool")
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
        required = frozenset({"ecu_to_ilc_conversion_runtime", "public_claimability_runtime"})
        if not required <= profile.components:
            raise ValueError("public_rc_claimability_profile_requires_conversion_and_claimability")

    if profile.public_rc_eligible and profile.public_p2p:
        raise ValueError("public_rc_skill_first_profile_must_not_claim_public_p2p")


def validate_all_package_profiles() -> None:
    for profile in PACKAGE_PROFILES.values():
        validate_package_profile(profile)


def profile_manifest(profile: PackageProfile | str) -> dict[str, Any]:
    active = get_package_profile(profile) if isinstance(profile, str) else profile
    validate_package_profile(active)
    return {
        "components": sorted(active.components),
        "description": active.description,
        "display_name": active.display_name,
        "non_excisable_components": sorted(NON_EXCISABLE_COMPONENTS),
        "notes": list(active.notes),
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
    "PROFILE_FULL_NODE_PUBLIC_P2P",
    "PROFILE_ILC_CLI_LOCAL",
    "PROFILE_ILC_LOGIC_LIBRARY",
    "PROFILE_LOCAL_SIDECAR_DAEMON",
    "PROFILE_OPENCLAW_SKILL_LOCAL",
    "PUBLIC_RC_PACKAGE_PROFILES_VERSION",
    "PackageProfile",
    "export_profile_manifest_json",
    "get_package_profile",
    "profile_manifest",
    "validate_all_package_profiles",
    "validate_package_profile",
]
