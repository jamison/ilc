from __future__ import annotations

import ast
import copy
import json
from pathlib import Path

import pytest

from ilc_core.rc.package_profile_ci_gate import build_package_profile_ci_audit
from ilc_core.rc.package_profiles import (
    PROFILE_CONFIDENTIAL_COORDINATION_LOCAL_PREVIEW,
    PROFILE_OPENCLAW_SKILL_CLAIMABLE,
    PROFILE_OPENCLAW_SKILL_LOCAL,
    profile_manifest,
    validate_all_package_profiles,
)
from ilc_core.sidecars.registry_manifest import (
    CONFIDENTIAL_COORDINATION_LOCAL_PREVIEW_PROFILE_DECLARED_TOKEN,
    OPENCLAW_COMPATIBLE_LOCAL_BRIDGE_PROFILE_DECLARED_TOKEN,
    PACKAGE_PROFILE_INTEGRITY_HARDENED_TOKEN,
    PHASE_1308_NEXT_TOKEN,
    PUBLIC_RC_REMAINS_BLOCKED_AFTER_PHASE_1307_TOKEN,
    SIDECAR_MANIFEST_DETERMINISTIC_PROFILE_DECLARED_TOKEN,
    SIDECAR_REGISTRY_MANIFEST_VERSION,
    build_sidecar_registry_manifest,
    export_sidecar_registry_manifest_json,
    sidecar_registry_required_tokens,
    validate_sidecar_registry_manifest,
)


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "ilc_core/sidecars/registry_manifest.py"
PACKAGE_PROFILES_PATH = ROOT / "ilc_core/rc/package_profiles.py"
CI_GATE_PATH = ROOT / "ilc_core/rc/package_profile_ci_gate.py"
SPEC_PATH = ROOT / "docs/specs/ilc_graph_native_sidecar_registry_manifest_1307_v0.1.md"
WALKTHROUGH_PATH = (
    ROOT
    / "docs/phases/phase_1307_graph_native_sidecar_registry_manifest_profile_hardening_walkthrough.md"
)
STATUS_PATH = ROOT / "docs/phases/STATUS.md"
PLANNING_INDEX_PATH = ROOT / "docs/PLANNING_INDEX.md"
CAPSULE_PATH = ROOT / "docs/specs/ilc_antigravity_context_capsule_v5.53.md"
ROADMAP_PATH = ROOT / "docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md"

REQUIRED_TOKENS = [
    SIDECAR_REGISTRY_MANIFEST_VERSION,
    SIDECAR_MANIFEST_DETERMINISTIC_PROFILE_DECLARED_TOKEN,
    OPENCLAW_COMPATIBLE_LOCAL_BRIDGE_PROFILE_DECLARED_TOKEN,
    CONFIDENTIAL_COORDINATION_LOCAL_PREVIEW_PROFILE_DECLARED_TOKEN,
    PACKAGE_PROFILE_INTEGRITY_HARDENED_TOKEN,
    PHASE_1308_NEXT_TOKEN,
    PUBLIC_RC_REMAINS_BLOCKED_AFTER_PHASE_1307_TOKEN,
]


def _profiles_by_id() -> dict[str, dict]:
    return {profile["profile_id"]: profile for profile in build_sidecar_registry_manifest()["profiles"]}


def test_phase_1307_registry_manifest_is_canonical_local_metadata_only() -> None:
    manifest = build_sidecar_registry_manifest()
    exported_once = export_sidecar_registry_manifest_json()
    exported_twice = export_sidecar_registry_manifest_json()

    assert manifest["version"] == SIDECAR_REGISTRY_MANIFEST_VERSION
    assert manifest["required_tokens"] == REQUIRED_TOKENS
    assert sidecar_registry_required_tokens() == REQUIRED_TOKENS
    assert manifest["deterministic_manifest"] is True
    assert manifest["local_package_metadata_only"] is True
    assert manifest["public_serving_enabled"] is False
    assert manifest["public_rc_claimed"] is False
    assert manifest["public_package_publication_authorized"] is False
    assert manifest["public_confidential_messaging_claimed"] is False
    assert manifest["public_confidential_coordination_serving_enabled"] is False
    verifier_manifest = manifest["package_profile_integrity"][
        "offline_claimability_verifier_manifest"
    ]
    assert verifier_manifest["public_api_enabled"] is False
    assert verifier_manifest["public_claimability_activated"] is False
    assert verifier_manifest["receipt_verifier_public_serving_enabled"] is False
    assert exported_once == exported_twice
    assert exported_once == json.dumps(
        json.loads(exported_once),
        allow_nan=False,
        separators=(",", ":"),
        sort_keys=True,
    )


def test_phase_1307_declares_openclaw_claimable_bridge_without_activation() -> None:
    profiles = _profiles_by_id()
    claimable = profiles["openclaw_claimable_local_bridge"]

    assert claimable["package_profile_id"] == PROFILE_OPENCLAW_SKILL_CLAIMABLE
    assert claimable["package_profile"] == profile_manifest(PROFILE_OPENCLAW_SKILL_CLAIMABLE)
    assert "offline_claimability_receipt_verifier" in claimable["required_sidecars"]
    assert claimable["package_profile"]["public_claimability"] is True
    assert claimable["package_profile"]["public_p2p"] is False
    assert claimable["package_profile"]["public_rc_eligible"] is True
    assert claimable["public_claimability_runtime_activated"] is False
    assert claimable["public_p2p_activated"] is False
    assert claimable["public_serving_enabled"] is False


def test_phase_1307_declares_confidential_coordination_local_preview_private_only() -> None:
    profiles = _profiles_by_id()
    confidential = profiles[PROFILE_CONFIDENTIAL_COORDINATION_LOCAL_PREVIEW]

    assert confidential["package_profile_id"] == PROFILE_CONFIDENTIAL_COORDINATION_LOCAL_PREVIEW
    assert confidential["package_profile"]["public_claimability"] is False
    assert confidential["package_profile"]["public_p2p"] is False
    assert confidential["package_profile"]["public_rc_eligible"] is False
    assert "confidential_coordination_local_preview" in confidential["required_sidecars"]
    assert "private_loopback" in confidential["private_wiring_modes"]
    assert "private_overlay" in confidential["private_wiring_modes"]
    assert confidential["public_confidential_messaging_claimed"] is False
    assert confidential["public_serving_enabled"] is False


def test_phase_1307_package_profiles_and_ci_gate_include_sidecar_integrity() -> None:
    validate_all_package_profiles()
    local = profile_manifest(PROFILE_OPENCLAW_SKILL_LOCAL)
    claimable = profile_manifest(PROFILE_OPENCLAW_SKILL_CLAIMABLE)

    assert "graph_native_sidecar_registry_manifest" in local["components"]
    assert "openclaw_compatible_local_bridge" in local["components"]
    assert "offline_claimability_receipt_verifier_sidecar" in claimable["components"]
    assert "local_sidecar" in claimable["package_surfaces"]
    assert "ilc_core/sidecars" in CI_GATE_PATH.read_text(encoding="utf-8")

    audit = build_package_profile_ci_audit()
    local_sidecar = audit["profiles"][PROFILE_OPENCLAW_SKILL_CLAIMABLE][
        "surface_measurements"
    ]["local_sidecar"]
    measured_files = {record["path"] for record in local_sidecar["files"]}

    assert "ilc_core/sidecars/registry_manifest.py" in measured_files
    assert "ilc_core/sidecars/claimability_receipt_verifier.py" in measured_files
    assert local_sidecar["boundary_contract"]["status"] == "measurement_only"


def test_phase_1307_manifest_validation_fails_closed_on_public_or_mismatched_mutations() -> None:
    manifest = build_sidecar_registry_manifest()

    public_serving = copy.deepcopy(manifest)
    public_serving["profiles"][0]["public_serving_enabled"] = True
    with pytest.raises(ValueError, match="public_authority_forbidden"):
        validate_sidecar_registry_manifest(public_serving)

    package_mismatch = copy.deepcopy(manifest)
    package_mismatch["profiles"][0]["package_profile"] = profile_manifest(
        PROFILE_OPENCLAW_SKILL_LOCAL
    )
    with pytest.raises(ValueError, match="package_profile_mismatch"):
        validate_sidecar_registry_manifest(package_mismatch)

    duplicate_sidecar = copy.deepcopy(manifest)
    duplicate_sidecar["sidecars"].append(dict(duplicate_sidecar["sidecars"][0]))
    with pytest.raises(ValueError, match="sidecar_id_invalid"):
        validate_sidecar_registry_manifest(duplicate_sidecar)

    source_export = copy.deepcopy(manifest)
    source_export["source_allowlist_readiness"]["source_allowlist_export_executed"] = True
    with pytest.raises(ValueError, match="source_allowlist_export_forbidden"):
        validate_sidecar_registry_manifest(source_export)

    non_authorization_drift = copy.deepcopy(manifest)
    non_authorization_drift["non_authorization_boundary"].remove("no_public_rc_claim")
    with pytest.raises(ValueError, match="non_authorization_boundary_invalid"):
        validate_sidecar_registry_manifest(non_authorization_drift)

    readiness_drift = copy.deepcopy(manifest)
    readiness_drift["source_allowlist_readiness"][
        "phase_1308_public_rc_exclude_disposition_required"
    ] = False
    with pytest.raises(ValueError, match="source_allowlist_readiness_invalid"):
        validate_sidecar_registry_manifest(readiness_drift)


def test_phase_1307_registry_source_has_no_public_server_or_network_surface() -> None:
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


def test_phase_1307_docs_status_and_frontier_record_tokens_and_nonclaims() -> None:
    corpus = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (
            MODULE_PATH,
            PACKAGE_PROFILES_PATH,
            SPEC_PATH,
            WALKTHROUGH_PATH,
            STATUS_PATH,
            PLANNING_INDEX_PATH,
            CAPSULE_PATH,
            ROADMAP_PATH,
        )
    )

    for token in REQUIRED_TOKENS:
        assert token in corpus
    for non_claim in (
        "no public serving",
        "no public package publication",
        "no source allowlist export",
        "no public confidential messaging",
        "no wallet withdrawal",
        "no ECU minting",
        "no ILC settlement",
        "Phase 1308 is sensitive and requires explicit `GO Phase 1308`",
    ):
        assert non_claim in corpus
