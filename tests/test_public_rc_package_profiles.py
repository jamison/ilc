from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

from ilc_core.rc.package_profiles import (
    NON_EXCISABLE_COMPONENTS,
    PACKAGE_PROFILES,
    PROFILE_FULL_NODE_PUBLIC_P2P,
    PROFILE_OPENCLAW_SKILL_LOCAL,
    PUBLIC_RC_PACKAGE_PROFILES_VERSION,
    PackageProfile,
    export_profile_manifest_json,
    get_package_profile,
    profile_manifest,
    validate_all_package_profiles,
    validate_package_profile,
)

MODULE_PATH = Path("ilc_core/rc/package_profiles.py")


def test_all_committed_package_profiles_validate() -> None:
    validate_all_package_profiles()
    assert PUBLIC_RC_PACKAGE_PROFILES_VERSION == "public_rc_package_profiles_1238.v0.1"


def test_openclaw_skill_profile_is_local_first_and_not_public_p2p() -> None:
    profile = get_package_profile(PROFILE_OPENCLAW_SKILL_LOCAL)
    assert profile.public_rc_eligible is True
    assert profile.public_p2p is False
    assert profile.public_claimability is False
    assert "harness_adapter_contracts" in profile.components
    assert "transport_harness_contracts" in profile.components
    assert "rust_public_p2p_node" not in profile.components


def test_full_node_profile_definition_includes_public_p2p_and_claimability_gates() -> None:
    profile = get_package_profile(PROFILE_FULL_NODE_PUBLIC_P2P)
    assert profile.public_p2p is True
    assert profile.public_claimability is True
    assert profile.public_rc_eligible is False
    assert "rust_public_p2p_node" in profile.components
    assert "transport_principal_identity" in profile.components
    assert "ecu_to_ilc_conversion_runtime" in profile.components
    assert "public_claimability_runtime" in profile.components


def test_profiles_cannot_exclude_genesis_ilc_or_ecu_components() -> None:
    profile = PackageProfile(
        profile_id="bad",
        display_name="Bad",
        description="Invalid profile",
        components=frozenset({"ilc_logic_import_surface"}),
        public_p2p=False,
        public_claimability=False,
        public_rc_eligible=True,
    )
    with pytest.raises(ValueError, match="missing_non_excisable_component"):
        validate_package_profile(profile)


def test_public_p2p_profile_requires_transport_principal() -> None:
    profile = PackageProfile(
        profile_id="bad_public_p2p",
        display_name="Bad public P2P",
        description="Invalid public P2P profile",
        components=frozenset({*NON_EXCISABLE_COMPONENTS, "rust_public_p2p_node"}),
        public_p2p=True,
        public_claimability=False,
        public_rc_eligible=False,
    )
    with pytest.raises(ValueError, match="requires_transport_principal"):
        validate_package_profile(profile)


def test_public_claimability_profile_requires_conversion_and_claimability_runtime() -> None:
    profile = PackageProfile(
        profile_id="bad_claimability",
        display_name="Bad claimability",
        description="Invalid claimability profile",
        components=frozenset({*NON_EXCISABLE_COMPONENTS, "ilc_logic_import_surface"}),
        public_p2p=False,
        public_claimability=True,
        public_rc_eligible=False,
    )
    with pytest.raises(ValueError, match="requires_conversion_and_claimability"):
        validate_package_profile(profile)


def test_profile_manifest_json_is_canonical_and_round_trips() -> None:
    payload_once = export_profile_manifest_json(PROFILE_OPENCLAW_SKILL_LOCAL)
    payload_twice = export_profile_manifest_json(PROFILE_OPENCLAW_SKILL_LOCAL)
    assert payload_once == payload_twice
    assert payload_once == json.dumps(
        json.loads(payload_once),
        allow_nan=False,
        separators=(",", ":"),
        sort_keys=True,
    )
    parsed = json.loads(payload_once)
    assert parsed == profile_manifest(PROFILE_OPENCLAW_SKILL_LOCAL)
    assert parsed["non_excisable_components"] == sorted(NON_EXCISABLE_COMPONENTS)


def test_package_profile_runtime_has_no_server_storage_network_or_wall_clock_imports() -> None:
    tree = ast.parse(MODULE_PATH.read_text(encoding="utf-8"))
    forbidden_roots = {
        "aiohttp",
        "datetime",
        "fastapi",
        "http",
        "lmdb",
        "random",
        "requests",
        "socket",
        "time",
        "urllib",
        "uvicorn",
    }
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                assert alias.name.split(".")[0] not in forbidden_roots
        if isinstance(node, ast.ImportFrom):
            assert (node.module or "").split(".")[0] not in forbidden_roots


def test_package_profile_registry_names_are_stable() -> None:
    assert sorted(PACKAGE_PROFILES) == [
        "full_node_public_p2p",
        "ilc_cli_local",
        "ilc_logic_library",
        "local_sidecar_daemon",
        "openclaw_skill_local",
    ]
