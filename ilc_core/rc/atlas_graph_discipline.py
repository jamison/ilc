"""ATLAS-G graph-discipline helpers for public-RC package reachability.

This module is intentionally declarative and non-mutating. It validates the
phase-close ``graph_delta=...`` discipline and exports deterministic
package-profile reachability manifests that keep Genesis, ILC, ECU, canonical
JSON, protocol-bundle verification, Rust consensus binding, and the hypergraph
surface visible from public-RC packaging profiles.
"""

from __future__ import annotations

import json
import hashlib
from pathlib import Path, PurePosixPath
from typing import Any

from ilc_core.rc.package_boundary_inventory import (
    DEFAULT_IMPORT_BOUNDARY_SPECS,
    IMPORT_BOUNDARY_INVENTORY_VERSION,
    build_import_boundary_inventory,
)
from ilc_core.rc.package_profiles import (
    NON_EXCISABLE_COMPONENTS,
    PACKAGE_PROFILES,
    PROFILE_PACKAGE_SURFACES,
    PROFILE_OPENCLAW_SKILL_CLAIMABLE,
    PROFILE_OPENCLAW_SKILL_LOCAL,
    PUBLIC_RC_PACKAGE_PROFILES_VERSION,
    get_package_profile,
    profile_manifest,
    validate_package_profile,
)

ATLAS_GRAPH_DISCIPLINE_VERSION = "atlas_graph_discipline_1247.v0.1"
ATLAS_G_004_005_BRIDGE_VERSION = "atlas_g_004_005_dependency_bridge_1254.v0.1"
ATLAS_G_004_COMPLETION_TOKEN = "atlas_g_004_high_authority_gap_closure_committed_phase_1254"
ATLAS_G_005_COMPLETION_TOKEN = (
    "atlas_g_005_import_dependency_graph_bridge_committed_phase_1254"
)
ATLAS_G_006_PUBLIC_RC_GRAPH_REACHABILITY_GATE_VERSION = (
    "atlas_g_006_public_rc_graph_reachability_gate_phase_1271.v0.1"
)
ATLAS_G_006_PUBLIC_RC_GRAPH_REACHABILITY_VERDICT_TOKEN = (
    "public_rc_graph_reachability_verdict_recorded_phase_1271"
)
ATLAS_G_006_PUBLIC_RELEASE_ARTIFACT_NOT_AUTHORIZED_TOKEN = (
    "public_release_artifact_not_authorized_phase_1271"
)
ATLAS_G_006_NO_GENESIS_ATLAS_MUTATION_TOKEN = "no_genesis_atlas_mutation_phase_1271"
ATLAS_G_006_MANIFEST_PROFILE_CONSISTENCY_FIX1_TOKEN = (
    "atlas_g_006_manifest_profile_consistency_hardening_phase_1271_fix1.v0.1"
)
PHASE_1254_LEGACY_GRAPH_DELTA_DISPOSITION_TOKEN = (
    "phase_1254_legacy_graph_delta_gap_disposition_recorded"
)
PHASE_1254_COMPLETE_TOKEN = "phase_1254_atlas_g_004_005_complete"
HIGH_AUTHORITY_CLASSIFICATION_POLICY_TOKEN = (
    "high_authority_sources_must_be_core_support_or_archive_classified"
)
PACKAGE_MODULARITY_EDGE_POLICY_TOKEN = (
    "package_modularity_edges_required_for_public_rc_graph"
)

GRAPH_ANCHORS = frozenset({"ecu", "genesis", "hypergraph", "ilc"})
GRAPH_DELTA_SIMPLE_KINDS = frozenset({"deferred", "none", "support_only"})
GRAPH_DELTA_LOAD_BEARING_KINDS = frozenset(
    {"load_bearing_artifact_added", "load_bearing_artifact_changed"}
)
GRAPH_DELTA_KINDS = GRAPH_DELTA_SIMPLE_KINDS | GRAPH_DELTA_LOAD_BEARING_KINDS

PROFILE_REACHABILITY_MANIFEST_IDS = frozenset(
    {PROFILE_OPENCLAW_SKILL_CLAIMABLE, PROFILE_OPENCLAW_SKILL_LOCAL}
)
ATLAS_G_006_SELECTED_PUBLIC_RC_PROFILE = PROFILE_OPENCLAW_SKILL_CLAIMABLE
ATLAS_G_006_REQUIRED_EDGE_TYPES = frozenset(
    {
        "high_authority_source_classified_as",
        "package_component_reachable_from_anchor",
        "package_profile_exports_surface",
        "package_profile_requires_component",
        "python_cli_entrypoint",
        "python_surface_imports_root",
        "rust_binary_entrypoint",
        "rust_crate_dependency",
    }
)
ATLAS_G_006_REQUIRED_PROFILE_COMPONENTS = frozenset(
    {
        *NON_EXCISABLE_COMPONENTS,
        "ecu_to_ilc_conversion_runtime",
        "graph_native_sidecar_registry_manifest",
        "offline_claimability_receipt_verifier_sidecar",
        "openclaw_compatible_local_bridge",
        "public_claimability_runtime",
        "value_path_activation_boundary_preflight_sidecar",
        "wallet_action_semantics_preflight_sidecar",
    }
)
ATLAS_G_006_REQUIRED_PROFILE_SURFACES = frozenset(
    {"ilc_cli", "ilc_harness_adapters", "ilc_logic", "local_sidecar", "public_claimability"}
)

_REPO_ROOT = Path(__file__).resolve().parents[2]
MAX_ATLAS_G_1254_HIGH_AUTHORITY_SOURCES = 5_000
MAX_ATLAS_G_1254_DEPENDENCY_EDGES = 50_000

_CORE_HIGH_AUTHORITY_PATHS = frozenset(
    {
        "AGENTS.md",
        "docs/PLANNING_INDEX.md",
        "docs/specs/ilc_antigravity_context_capsule_v5.50.md",
        "docs/specs/ilc_atlas_g_1241_plus_candidate_phase_grouping_v0.1.md",
        "docs/specs/ilc_atlas_graph_integrated_phase_discipline_forward_planning_1241_v0.1.md",
        "docs/specs/ilc_gap13_public_claimability_resolution_boundary_1252_v0.1.md",
        "docs/specs/ilc_gap14_package_profile_audit_1251_v0.1.md",
        "docs/specs/ilc_gap14_package_profile_audit_1251_v0.1.json",
        "docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md",
        "docs/specs/ilc_phase_1249_1256_sequence_lock_v0.1.md",
        "docs/specs/ilc_public_rc_runway_pre_sequence_plan_1241_plus_v0.1.md",
        "docs/specs/ilc_rc_frontier_gap_audit_1250_fix1_v0.1.md",
        "docs/specs/ilc_rc_frontier_gap_audit_1250_fix1_v0.1.json",
        "docs/specs/ilc_transport_principal_identity_spec_1253_v0.1.md",
        "docs/specs/ilc_window_1241_1248_handoff_1248_v0.1.md",
        "docs/specs/ilc_window_1249_1256_candidate_phase_grouping_v0.1.md",
        "ilc_consensus/Cargo.toml",
        "ilc_core/rc/atlas_graph_discipline.py",
        "ilc_core/rc/package_boundary_inventory.py",
        "ilc_core/rc/package_profile_ci_gate.py",
        "ilc_core/rc/package_profiles.py",
        "pyproject.toml",
        "tools/compare_genesis_star_map_to_repo_graph.py",
    }
)

_SUPPORT_HIGH_AUTHORITY_PATHS = frozenset(
    {
        "docs/antigravity_tasks/antigravity_prompt__atlas_g_004_high_authority_gap_closure.md",
        "docs/antigravity_tasks/antigravity_prompt__atlas_g_005_import_dependency_graph_bridge.md",
        "docs/antigravity_tasks/antigravity_prompt__phase_1254_g8_atlas_g_004_005_high_authority_dependency_bridge.md",
        "docs/phases/STATUS.md",
        "docs/phases/phase_1250_fix1_rc_frontier_gap_audit_walkthrough.md",
        "docs/phases/phase_1251_gap14_package_ci_profile_audit_walkthrough.md",
        "docs/phases/phase_1252_gap13_claimability_resolution_boundary_walkthrough.md",
        "docs/phases/phase_1253_transport_principal_identity_spec_walkthrough.md",
        "tests/test_phase_1247_atlas_g_graph_discipline_slice.py",
        "tests/test_phase_1251_gap14_package_ci_gate.py",
        "tests/test_phase_1252_gap13_claimability_resolution_boundary.py",
        "tests/test_phase_1253_transport_principal_identity_spec.py",
    }
)

_ARCHIVE_HIGH_AUTHORITY_PATHS = frozenset(
    {
        "docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.0.md",
        "docs/specs/ilc_phase_1241_1248_sequence_lock_v0.1.md",
        "docs/specs/ilc_window_1241_1248_candidate_phase_grouping_v0.1.md",
        "docs/specs/ilc_window_1233_1240_handoff_1240_v0.1.md",
    }
)

_HIGH_AUTHORITY_REASONS = {
    "core": "current controlling canon, runtime contract, package profile, or active ATLAS-G compiler surface",
    "support": "phase evidence, prompt contract, validation, or status surface supporting current canon",
    "archive": "superseded or closed-window context retained for history but not controlling current execution",
}

_NON_AUTHORIZATION_BOUNDARY = (
    "no_signed_genesis_v0_1_mutation",
    "no_genesis_atlas_v0_2_regeneration",
    "no_v0_2_signing",
    "no_immutable_diagnostic_mutation",
    "no_public_rc_claim",
    "no_public_repository_publication",
    "no_public_p2p_exposure",
    "no_public_sidecar_projection_serving",
    "no_public_claimability_activation",
    "no_cdl_mutation",
)
_ATLAS_G_006_NON_AUTHORIZATION_BOUNDARY = (
    *_NON_AUTHORIZATION_BOUNDARY,
    ATLAS_G_006_PUBLIC_RELEASE_ARTIFACT_NOT_AUTHORIZED_TOKEN,
    ATLAS_G_006_NO_GENESIS_ATLAS_MUTATION_TOKEN,
    "no_release_artifact_production_phase_1271",
    "no_public_rc_claim_phase_1271",
    "no_public_repository_publication_phase_1271",
    "no_v0_2_signing_phase_1271",
    "no_cdl_mutation_phase_1271",
)

_COMPONENT_REACHABILITY: dict[str, dict[str, Any]] = {
    "canonical_json_policy": {
        "anchors": ("genesis", "hypergraph", "ilc"),
        "representative_paths": (
            "AGENTS.md",
            "ilc_core/crypto/cbor_canonical.py",
            "ilc_core/ledger/canon_bundle_utils.py",
        ),
        "relation": "canonical_json_keeps_graph_and_protocol_artifacts_replayable",
    },
    "cli_subprocess_surface": {
        "anchors": ("ilc",),
        "representative_paths": (
            "ilc_core/cli/main.py",
            "ilc_core/cli/canon_cli.py",
        ),
        "relation": "local_operator_or_harness_command_surface",
    },
    "ecu_ilc_economic_boundary": {
        "anchors": ("ecu", "ilc"),
        "representative_paths": (
            "ilc_core/rc/economic_cycle_runtime.py",
            "ilc_core/protocol/public_wallet_runtime.py",
        ),
        "relation": "economic_boundary_keeps_ecu_and_ilc_non_excisable",
    },
    "ecu_to_ilc_conversion_runtime": {
        "anchors": ("ecu", "ilc"),
        "representative_paths": (
            "ilc_core/rc/economic_cycle_runtime.py",
            "ilc_core/protocol/public_wallet_runtime.py",
        ),
        "relation": "claimability_profile_requires_conversion_surface",
    },
    "confidential_coordination_local_preview_profile": {
        "anchors": ("hypergraph", "ilc"),
        "representative_paths": (
            "docs/architecture/ilc_confidential_coordination_sidecar_suite_forward_plan_v0.1.md",
            "ilc_core/sidecars/registry_manifest.py",
        ),
        "relation": "confidential_coordination_profile_is_private_local_manifest_metadata",
    },
    "genesis_lineage_verification": {
        "anchors": ("genesis", "hypergraph"),
        "representative_paths": (
            "ilc_core/genesis/genesis_state_bundle_runtime.py",
            "ilc_core/identity/genesis_record_schema.py",
        ),
        "relation": "genesis_lineage_bounds_valid_ilc_identity",
    },
    "harness_adapter_contracts": {
        "anchors": ("hypergraph", "ilc"),
        "representative_paths": (
            "ilc_core/protocol/harness_interfaces.py",
            "ilc_core/rc/local_skill_preview.py",
        ),
        "relation": "external_harnesses_attach_without_owning_protocol_transport",
    },
    "graph_native_sidecar_registry_manifest": {
        "anchors": ("hypergraph", "ilc"),
        "representative_paths": (
            "docs/architecture/ilc_graph_native_sidecar_suite_architecture_v0.1.md",
            "ilc_core/sidecars/registry_manifest.py",
        ),
        "relation": "sidecar_registry_declares_harness_agnostic_graph_native_suite",
    },
    "ilc_identity_namespace": {
        "anchors": ("genesis", "ilc"),
        "representative_paths": (
            "ilc_core/identity/genesis_record_schema.py",
            "ilc_core/protocol/public_wallet_runtime.py",
        ),
        "relation": "identity_namespace_links_genesis_lineage_to_ilc_runtime",
    },
    "ilc_logic_import_surface": {
        "anchors": ("genesis", "hypergraph", "ilc"),
        "representative_paths": (
            "ilc_core/epistemic",
            "ilc_core/protocol",
            "ilc_core/graph/agent_graph_projection_runtime.py",
        ),
        "relation": "pure_logic_import_surface_for_harness_consumption",
    },
    "local_node_runtime": {
        "anchors": ("hypergraph", "ilc"),
        "representative_paths": (
            "ilc_core/node",
            "ilc_core/storage/interfaces.py",
        ),
        "relation": "local_runtime_surface_for_loopback_sidecar_profiles",
    },
    "local_sidecar_query_runtime": {
        "anchors": ("hypergraph", "ilc"),
        "representative_paths": (
            "ilc_core/graph/sidecar_query_runtime.py",
            "ilc_core/graph/agent_graph_projection_runtime.py",
        ),
        "relation": "local_read_only_graph_query_surface",
    },
    "offline_claimability_receipt_verifier_sidecar": {
        "anchors": ("ecu", "ilc"),
        "representative_paths": (
            "ilc_core/sidecars/claimability_receipt_verifier.py",
            "docs/specs/ilc_offline_claimability_receipt_verifier_sidecar_1305_v0.1.md",
        ),
        "relation": "claimability_profile_requires_local_receipt_and_proof_verifier",
    },
    "value_path_activation_boundary_preflight_sidecar": {
        "anchors": ("ecu", "ilc", "hypergraph"),
        "representative_paths": (
            "ilc_core/sidecars/value_path_activation_boundary_preflight.py",
            "docs/specs/ilc_ecu_minting_ilc_settlement_boundary_preflight_1315_v0.1.md",
        ),
        "relation": "claimable_profile_requires_ecu_ilc_value_path_activation_boundary_preflight",
    },
    "wallet_action_semantics_preflight_sidecar": {
        "anchors": ("ecu", "ilc", "hypergraph"),
        "representative_paths": (
            "ilc_core/sidecars/wallet_action_semantics_preflight.py",
            "docs/specs/ilc_wallet_withdrawal_transfer_spend_semantics_preflight_1314_v0.1.md",
        ),
        "relation": "claimable_profile_requires_wallet_facing_value_action_boundary_preflight",
    },
    "openclaw_compatible_local_bridge": {
        "anchors": ("hypergraph", "ilc"),
        "representative_paths": (
            "ilc_core/rc/local_skill_preview.py",
            "docs/architecture/ilc_graph_native_sidecar_suite_architecture_v0.1.md",
        ),
        "relation": "openclaw_nemoclaw_are_hosts_for_graph_native_sidecars_not_protocol_substrates",
    },
    "protocol_bundle_verification": {
        "anchors": ("genesis", "hypergraph", "ilc"),
        "representative_paths": (
            "ilc_core/protocol/bundle_verify.py",
            "ilc_core/protocol/ndjson_bundle.py",
            "ilc_core/ledger/canon_export_bundle_validate.py",
        ),
        "relation": "protocol_bundles_remain_machine_verifiable",
    },
    "public_claimability_runtime": {
        "anchors": ("ecu", "ilc"),
        "representative_paths": (
            "ilc_core/protocol/public_wallet_runtime.py",
            "ilc_core/rc/economic_cycle_runtime.py",
        ),
        "relation": "public_rc_claimable_profile_includes_claimability_surface",
    },
    "rust_consensus_core_binding": {
        "anchors": ("genesis", "hypergraph", "ilc"),
        "representative_paths": (
            "ilc_consensus/Cargo.toml",
            "ilc_consensus/src",
        ),
        "relation": "rust_consensus_core_is_load_bearing_not_optional",
    },
    "rust_public_p2p_node": {
        "anchors": ("hypergraph", "ilc"),
        "representative_paths": (
            "ilc_consensus/Cargo.toml",
            "ilc_core/network/d2d",
        ),
        "relation": "public_p2p_profile_surface_deferred_until_transportprincipal",
    },
    "storage_adapter_contracts": {
        "anchors": ("hypergraph", "ilc"),
        "representative_paths": (
            "ilc_core/protocol/harness_interfaces.py",
            "ilc_core/storage/interfaces.py",
        ),
        "relation": "storage_is_adapter_contract_for_harness_profiles",
    },
    "transport_harness_contracts": {
        "anchors": ("hypergraph", "ilc"),
        "representative_paths": (
            "ilc_core/protocol/harness_interfaces.py",
            "ilc_core/network/wire_transport_runtime.py",
        ),
        "relation": "transport_is_harness_contract_not_public_p2p_claim",
    },
    "transport_principal_identity": {
        "anchors": ("genesis", "hypergraph", "ilc"),
        "representative_paths": (
            "docs/specs/ilc_network_transport_identity_and_value_path_forward_planning_v0.1.md",
        ),
        "relation": "public_p2p_identity_gate_for_future_full_node_profile",
    },
}


def _split_anchor_text(text: str) -> list[str]:
    normalized = text.replace(",", "/").replace(" ", "/")
    anchors = sorted({part.strip().lower() for part in normalized.split("/") if part.strip()})
    if not anchors:
        raise ValueError("atlas_graph_delta_anchor_required")
    unknown = set(anchors) - GRAPH_ANCHORS
    if unknown:
        raise ValueError("atlas_graph_delta_unknown_anchor")
    return anchors


def _validate_load_bearing_path(path: str) -> str:
    if "\x00" in path or "\n" in path or "\r" in path:
        raise ValueError("atlas_graph_delta_path_invalid")
    candidate = PurePosixPath(path)
    if candidate.is_absolute() or ".." in candidate.parts:
        raise ValueError("atlas_graph_delta_path_must_be_repo_relative")
    normalized = candidate.as_posix()
    if normalized in {"", "."}:
        raise ValueError("atlas_graph_delta_path_required")
    return normalized


def _representative_path_exists(path: str) -> bool:
    candidate = PurePosixPath(path)
    if candidate.is_absolute() or ".." in candidate.parts:
        return False
    return (_REPO_ROOT / candidate.as_posix()).exists()


def validate_graph_delta(declaration: str) -> dict[str, Any]:
    """Validate and parse a phase-close graph delta declaration."""

    if not isinstance(declaration, str):
        raise ValueError("atlas_graph_delta_declaration_must_be_string")
    text = declaration.strip()
    if not text.startswith("graph_delta="):
        raise ValueError("atlas_graph_delta_missing_prefix")
    body = text.removeprefix("graph_delta=").strip()
    if ":" not in body:
        raise ValueError("atlas_graph_delta_missing_kind_separator")
    kind, remainder = body.split(":", 1)
    kind = kind.strip()
    remainder = remainder.strip()
    if kind not in GRAPH_DELTA_KINDS:
        raise ValueError("atlas_graph_delta_unknown_kind")
    if not remainder:
        raise ValueError("atlas_graph_delta_payload_required")

    parsed: dict[str, Any] = {
        "declaration": text,
        "kind": kind,
        "load_bearing": kind in GRAPH_DELTA_LOAD_BEARING_KINDS,
        "version": ATLAS_GRAPH_DISCIPLINE_VERSION,
    }
    if kind in GRAPH_DELTA_LOAD_BEARING_KINDS:
        if "->" not in remainder:
            raise ValueError("atlas_graph_delta_load_bearing_anchor_required")
        path_text, anchor_text = remainder.split("->", 1)
        path = path_text.strip()
        if not path:
            raise ValueError("atlas_graph_delta_path_required")
        path = _validate_load_bearing_path(path)
        parsed["anchors"] = _split_anchor_text(anchor_text)
        parsed["paths"] = [path]
    else:
        parsed["anchors"] = []
        parsed["paths"] = [item.strip() for item in remainder.split(",") if item.strip()]
        if not parsed["paths"]:
            raise ValueError("atlas_graph_delta_payload_required")
    return parsed


def _component_manifest(component: str) -> dict[str, Any]:
    try:
        reachability = _COMPONENT_REACHABILITY[component]
    except KeyError as exc:
        raise ValueError("atlas_profile_reachability_component_unmapped") from exc
    anchors = sorted(reachability["anchors"])
    representative_paths = sorted(reachability["representative_paths"])
    missing_representative_paths = sorted(
        path for path in representative_paths if not _representative_path_exists(path)
    )
    return {
        "anchors": anchors,
        "component": component,
        "missing_representative_paths": missing_representative_paths,
        "non_excisable": component in NON_EXCISABLE_COMPONENTS,
        "reachable_from_required_anchor": bool(set(anchors) & GRAPH_ANCHORS),
        "relation": reachability["relation"],
        "representative_paths": representative_paths,
        "representative_paths_present": not missing_representative_paths,
    }


def package_profile_reachability_manifest(profile_id: str) -> dict[str, Any]:
    """Build a deterministic reachability manifest for a public-RC package profile."""

    if profile_id not in PROFILE_REACHABILITY_MANIFEST_IDS:
        raise ValueError("atlas_profile_reachability_manifest_profile_not_in_scope")
    profile = get_package_profile(profile_id)
    validate_package_profile(profile)
    manifest = profile_manifest(profile_id)
    components = [_component_manifest(component) for component in manifest["components"]]
    reachable_anchors = sorted({anchor for item in components for anchor in item["anchors"]})
    missing_required_anchors = sorted(GRAPH_ANCHORS - set(reachable_anchors))
    missing_non_excisable = sorted(set(NON_EXCISABLE_COMPONENTS) - set(manifest["components"]))
    missing_representative_paths = sorted(
        {path for item in components for path in item["missing_representative_paths"]}
    )
    unreachable_components = sorted(
        item["component"] for item in components if not item["reachable_from_required_anchor"]
    )
    return {
        "anchor_policy": "public_rc_load_bearing_artifacts_must_be_reachable_from_genesis_ilc_ecu_hypergraph_anchors",
        "anchors": sorted(GRAPH_ANCHORS),
        "component_reachability": sorted(components, key=lambda item: item["component"]),
        "graph_delta_required_on_profile_change": True,
        "manifest_id": f"{profile_id}_reachability_manifest_1247.v0.1",
        "missing_non_excisable_components": missing_non_excisable,
        "missing_representative_paths": missing_representative_paths,
        "missing_required_anchors": missing_required_anchors,
        "non_excisable_components": sorted(NON_EXCISABLE_COMPONENTS),
        "package_profile": manifest,
        "profile_id": profile_id,
        "reachable_anchor_set": reachable_anchors,
        "status": "pass"
        if not missing_non_excisable
        and not missing_representative_paths
        and not missing_required_anchors
        and not unreachable_components
        else "fail",
        "unreachable_components": unreachable_components,
        "version": ATLAS_GRAPH_DISCIPLINE_VERSION,
    }


def export_package_profile_reachability_manifest_json(profile_id: str) -> str:
    return json.dumps(
        package_profile_reachability_manifest(profile_id),
        allow_nan=False,
        separators=(",", ":"),
        sort_keys=True,
    )


def _validate_phase_1254_limit(value: int, *, maximum: int, token: str) -> int:
    if not isinstance(value, int):
        raise ValueError(f"{token}_must_be_int")
    if value <= 0:
        raise ValueError(f"{token}_must_be_positive")
    if value > maximum:
        raise ValueError(f"{token}_exceeds_max")
    return value


def _validate_repo_relative_artifact_path(path: str) -> str:
    if not isinstance(path, str) or not path:
        raise ValueError("atlas_g_1254_path_required")
    if "\x00" in path or "\n" in path or "\r" in path:
        raise ValueError("atlas_g_1254_path_invalid")
    candidate = PurePosixPath(path)
    if candidate.is_absolute() or ".." in candidate.parts:
        raise ValueError("atlas_g_1254_path_must_be_repo_relative")
    normalized = candidate.as_posix()
    if normalized in {"", "."}:
        raise ValueError("atlas_g_1254_path_required")
    return normalized


def _source_kind(path: str) -> str:
    if path == "AGENTS.md":
        return "agent_guidance"
    if path == "pyproject.toml":
        return "python_package_config"
    if path == "ilc_consensus/Cargo.toml" or path.startswith("ilc_consensus/"):
        return "rust_consensus"
    if path.startswith("docs/antigravity_tasks/"):
        return "phase_prompt"
    if path.startswith("docs/phases/"):
        return "phase_walkthrough_or_status"
    if path.startswith("docs/specs/"):
        return "spec_or_planning_doc"
    if path.startswith("ilc_core/"):
        return "python_runtime_or_rc_module"
    if path.startswith("tests/"):
        return "test"
    if path.startswith("tools/"):
        return "tool"
    return "other"


def _authority_class_for_path(path: str) -> str:
    if path in _CORE_HIGH_AUTHORITY_PATHS:
        return "core"
    if path in _SUPPORT_HIGH_AUTHORITY_PATHS:
        return "support"
    if path in _ARCHIVE_HIGH_AUTHORITY_PATHS:
        return "archive"
    raise ValueError("atlas_g_1254_unclassified_high_authority_source")


def _repo_path_exists(path: str) -> bool:
    return (_REPO_ROOT / _validate_repo_relative_artifact_path(path)).exists()


def _load_phase_1250_fix1_legacy_scan() -> dict[str, Any]:
    audit_path = "docs/specs/ilc_rc_frontier_gap_audit_1250_fix1_v0.1.json"
    path = _REPO_ROOT / audit_path
    if not path.exists():
        raise ValueError("atlas_g_1254_fix1_audit_missing")
    if path.stat().st_size > 3_000_000:
        raise ValueError("atlas_g_1254_fix1_audit_too_large")
    payload = json.loads(path.read_text(encoding="utf-8"))
    legacy_scan = payload.get("legacy_phase_scan")
    if not isinstance(legacy_scan, dict):
        raise ValueError("atlas_g_1254_fix1_legacy_scan_missing")
    return legacy_scan


def _legacy_graph_delta_disposition() -> dict[str, Any]:
    legacy_scan = _load_phase_1250_fix1_legacy_scan()
    files = legacy_scan.get("missing_graph_delta_closure_or_handoff_files")
    count = legacy_scan.get("missing_graph_delta_closure_or_handoff_count")
    if not isinstance(files, list) or not all(isinstance(path, str) for path in files):
        raise ValueError("atlas_g_1254_legacy_graph_delta_files_invalid")
    if count != len(files):
        raise ValueError("atlas_g_1254_legacy_graph_delta_count_mismatch")
    safe_files = sorted(_validate_repo_relative_artifact_path(path) for path in files)
    return {
        "bulk_legacy_backfill_authorized": False,
        "finding_id": "RCGAP-1250-FIX1-002",
        "legacy_scan_classification": legacy_scan.get("classification"),
        "missing_legacy_graph_delta_count": count,
        "missing_legacy_graph_delta_files": safe_files,
        "priority_backfill_policy": [
            {
                "action": "enforce_graph_delta_on_current_and_future_phase_close",
                "priority": "P0",
                "scope": "new phase walkthroughs, current window handoffs, and live STATUS entries",
            },
            {
                "action": "backfill_only_when_a_legacy_file_becomes_current_authority_or_is_touched",
                "priority": "P1",
                "scope": "legacy closure and handoff files that are re-opened by future work",
            },
            {
                "action": "preserve_archive_classification_and_avoid_bulk_history_rewrites",
                "priority": "P2",
                "scope": "closed-window historical phase files listed by the Phase 1250 Fix1 scan",
            },
            {
                "action": "re-measure_before_any_bulk_edit_and_require_tests_for_scope",
                "priority": "P3",
                "scope": "any proposed historical graph_delta campaign",
            },
        ],
        "route_status": "closed_by_phase_1254_atlas_g_disposition_plan",
        "source_audit_path": "docs/specs/ilc_rc_frontier_gap_audit_1250_fix1_v0.1.json",
        "token": PHASE_1254_LEGACY_GRAPH_DELTA_DISPOSITION_TOKEN,
    }


def build_high_authority_source_classification(
    *, max_sources: int = MAX_ATLAS_G_1254_HIGH_AUTHORITY_SOURCES
) -> dict[str, Any]:
    """Classify current high-authority ATLAS-G sources as core/support/archive."""

    _validate_phase_1254_limit(
        max_sources,
        maximum=MAX_ATLAS_G_1254_HIGH_AUTHORITY_SOURCES,
        token="atlas_g_1254_high_authority_source_limit",
    )
    paths = sorted(
        _CORE_HIGH_AUTHORITY_PATHS
        | _SUPPORT_HIGH_AUTHORITY_PATHS
        | _ARCHIVE_HIGH_AUTHORITY_PATHS
    )
    if len(paths) > max_sources:
        raise ValueError("atlas_g_1254_high_authority_source_limit_exceeded")

    sources = []
    missing_paths = []
    for path in paths:
        normalized = _validate_repo_relative_artifact_path(path)
        authority_class = _authority_class_for_path(normalized)
        exists = _repo_path_exists(normalized)
        if not exists:
            missing_paths.append(normalized)
        sources.append(
            {
                "authority_class": authority_class,
                "exists": exists,
                "path": normalized,
                "reason": _HIGH_AUTHORITY_REASONS[authority_class],
                "source_kind": _source_kind(normalized),
            }
        )

    class_counts = {
        authority_class: sum(
            1 for source in sources if source["authority_class"] == authority_class
        )
        for authority_class in ("archive", "core", "support")
    }
    return {
        "classification_policy_token": HIGH_AUTHORITY_CLASSIFICATION_POLICY_TOKEN,
        "class_counts": class_counts,
        "legacy_graph_delta_gap_disposition": _legacy_graph_delta_disposition(),
        "max_sources": max_sources,
        "missing_paths": missing_paths,
        "source_count": len(sources),
        "sources": sources,
        "status": "pass" if not missing_paths else "missing_paths",
        "version": ATLAS_G_004_005_BRIDGE_VERSION,
    }


def _canonical_hash_payload(payload: dict[str, Any]) -> str:
    return json.dumps(
        payload,
        allow_nan=False,
        separators=(",", ":"),
        sort_keys=True,
    )


def _edge_id(edge: dict[str, Any]) -> str:
    digest = hashlib.sha256(_canonical_hash_payload(edge).encode("utf-8")).hexdigest()
    return f"atlas-g-1254:{digest}"


def _append_dependency_edge(
    edges: list[dict[str, Any]],
    edge: dict[str, Any],
    *,
    max_edges: int,
) -> None:
    if len(edges) >= max_edges:
        raise ValueError("atlas_g_1254_dependency_edge_limit_exceeded")
    for key in ("edge_type", "source", "target"):
        value = edge.get(key)
        if not isinstance(value, str) or not value:
            raise ValueError("atlas_g_1254_dependency_edge_invalid")
        if "\x00" in value or "\n" in value or "\r" in value:
            raise ValueError("atlas_g_1254_dependency_edge_invalid")
    evidence_paths = edge.get("evidence_paths", [])
    if not isinstance(evidence_paths, list):
        raise ValueError("atlas_g_1254_dependency_edge_evidence_invalid")
    edge["evidence_paths"] = sorted(
        _validate_repo_relative_artifact_path(path) for path in evidence_paths
    )
    edge["edge_id"] = _edge_id(edge)
    edges.append(edge)


def _python_import_boundary_edges(
    edges: list[dict[str, Any]], *, max_edges: int
) -> dict[str, Any]:
    surfaces = {}
    for surface_id, spec in sorted(DEFAULT_IMPORT_BOUNDARY_SPECS.items()):
        inventory = build_import_boundary_inventory(spec)
        surfaces[surface_id] = {
            "file_count": inventory["file_count"],
            "import_root_count": len(inventory["import_roots"]),
            "root_paths": list(spec.root_paths),
            "status": inventory["status"],
            "violation_count": len(inventory["violations"]),
        }
        for import_root in inventory["import_roots"]:
            _append_dependency_edge(
                edges,
                {
                    "edge_type": "python_surface_imports_root",
                    "evidence_paths": list(spec.root_paths),
                    "source": f"python_surface:{surface_id}",
                    "target": f"python_import_root:{import_root}",
                    "version": IMPORT_BOUNDARY_INVENTORY_VERSION,
                },
                max_edges=max_edges,
            )
    return surfaces


def _strip_inline_toml_comment(line: str) -> str:
    in_string = False
    quote = ""
    output = []
    for char in line:
        if char in {"'", '"'}:
            if not in_string:
                in_string = True
                quote = char
            elif quote == char:
                in_string = False
                quote = ""
        if char == "#" and not in_string:
            break
        output.append(char)
    return "".join(output).strip()


def _parse_key_value_line(line: str) -> tuple[str, str] | None:
    if "=" not in line:
        return None
    key, value = line.split("=", 1)
    key = key.strip().strip('"').strip("'")
    value = value.strip().strip('"').strip("'")
    if not key or not value:
        return None
    return key, value


def _rust_cargo_edges(edges: list[dict[str, Any]], *, max_edges: int) -> dict[str, Any]:
    cargo_path = "ilc_consensus/Cargo.toml"
    path = _REPO_ROOT / cargo_path
    section = ""
    dependency_sections = {"dependencies", "dev-dependencies", "build-dependencies"}
    dependency_counts = {name: 0 for name in sorted(dependency_sections)}
    binaries = []
    current_bin: dict[str, str] | None = None

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = _strip_inline_toml_comment(raw_line)
        if not line:
            continue
        if line == "[[bin]]":
            if current_bin:
                binaries.append(current_bin)
            current_bin = {}
            section = "bin"
            continue
        if line.startswith("[") and line.endswith("]"):
            if current_bin:
                binaries.append(current_bin)
                current_bin = None
            section = line.strip("[]")
            continue
        parsed = _parse_key_value_line(line)
        if parsed is None:
            continue
        key, value = parsed
        if section in dependency_sections:
            dependency_counts[section] += 1
            _append_dependency_edge(
                edges,
                {
                    "edge_type": "rust_crate_dependency",
                    "evidence_paths": [cargo_path],
                    "source": "rust_crate:ilc_consensus",
                    "target": f"rust_dependency:{key}",
                    "dependency_section": section,
                    "version": ATLAS_G_004_005_BRIDGE_VERSION,
                },
                max_edges=max_edges,
            )
        elif section == "bin" and current_bin is not None and key in {"name", "path"}:
            current_bin[key] = value

    if current_bin:
        binaries.append(current_bin)
    for binary in sorted(binaries, key=lambda item: (item.get("name", ""), item.get("path", ""))):
        name = binary.get("name")
        target_path = binary.get("path")
        if not name or not target_path:
            continue
        repo_path = _validate_repo_relative_artifact_path(f"ilc_consensus/{target_path}")
        _append_dependency_edge(
            edges,
            {
                "edge_type": "rust_binary_entrypoint",
                "evidence_paths": [cargo_path, repo_path],
                "source": f"rust_binary:{name}",
                "target": f"rust_source:{repo_path}",
                "version": ATLAS_G_004_005_BRIDGE_VERSION,
            },
            max_edges=max_edges,
        )
    return {
        "binary_count": len(binaries),
        "dependency_counts": dependency_counts,
        "path": cargo_path,
    }


def _python_cli_entrypoint_edges(
    edges: list[dict[str, Any]], *, max_edges: int
) -> dict[str, Any]:
    pyproject_path = "pyproject.toml"
    path = _REPO_ROOT / pyproject_path
    section = ""
    script_count = 0
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = _strip_inline_toml_comment(raw_line)
        if not line:
            continue
        if line.startswith("[") and line.endswith("]"):
            section = line.strip("[]")
            continue
        if section != "project.scripts":
            continue
        parsed = _parse_key_value_line(line)
        if parsed is None:
            continue
        script, target = parsed
        script_count += 1
        module = target.split(":", 1)[0]
        module_path = f"{module.replace('.', '/')}.py"
        evidence_paths = [pyproject_path]
        if _repo_path_exists(module_path):
            evidence_paths.append(module_path)
        _append_dependency_edge(
            edges,
            {
                "edge_type": "python_cli_entrypoint",
                "evidence_paths": evidence_paths,
                "source": f"python_console_script:{script}",
                "target": f"python_callable:{target}",
                "version": ATLAS_G_004_005_BRIDGE_VERSION,
            },
            max_edges=max_edges,
        )
    return {"path": pyproject_path, "script_count": script_count}


def _package_profile_edges(edges: list[dict[str, Any]], *, max_edges: int) -> dict[str, Any]:
    profile_summaries = {}
    for profile_id in sorted(PACKAGE_PROFILES):
        manifest = profile_manifest(profile_id)
        profile_summaries[profile_id] = {
            "component_count": len(manifest["components"]),
            "package_surface_count": len(manifest["package_surfaces"]),
            "public_p2p": manifest["public_p2p"],
            "public_rc_eligible": manifest["public_rc_eligible"],
        }
        for surface_id in manifest["package_surfaces"]:
            _append_dependency_edge(
                edges,
                {
                    "edge_type": "package_profile_exports_surface",
                    "evidence_paths": ["ilc_core/rc/package_profiles.py"],
                    "source": f"package_profile:{profile_id}",
                    "target": f"package_surface:{surface_id}",
                    "version": PUBLIC_RC_PACKAGE_PROFILES_VERSION,
                },
                max_edges=max_edges,
            )
        for component in manifest["components"]:
            _append_dependency_edge(
                edges,
                {
                    "edge_type": "package_profile_requires_component",
                    "evidence_paths": ["ilc_core/rc/package_profiles.py"],
                    "source": f"package_profile:{profile_id}",
                    "target": f"package_component:{component}",
                    "version": PUBLIC_RC_PACKAGE_PROFILES_VERSION,
                },
                max_edges=max_edges,
            )

    for component, reachability in sorted(_COMPONENT_REACHABILITY.items()):
        for anchor in sorted(reachability["anchors"]):
            _append_dependency_edge(
                edges,
                {
                    "edge_type": "package_component_reachable_from_anchor",
                    "evidence_paths": list(reachability["representative_paths"]),
                    "source": f"package_component:{component}",
                    "target": f"atlas_anchor:{anchor}",
                    "version": ATLAS_GRAPH_DISCIPLINE_VERSION,
                },
                max_edges=max_edges,
            )
    return {
        "non_excisable_components": sorted(NON_EXCISABLE_COMPONENTS),
        "package_profile_count": len(PACKAGE_PROFILES),
        "profile_package_surfaces": {
            profile_id: list(surfaces)
            for profile_id, surfaces in sorted(PROFILE_PACKAGE_SURFACES.items())
        },
        "profiles": profile_summaries,
    }


def _high_authority_source_edges(
    edges: list[dict[str, Any]],
    classification: dict[str, Any],
    *,
    max_edges: int,
) -> None:
    for source in classification["sources"]:
        _append_dependency_edge(
            edges,
            {
                "edge_type": "high_authority_source_classified_as",
                "evidence_paths": [source["path"]],
                "source": f"repo_source:{source['path']}",
                "target": f"authority_class:{source['authority_class']}",
                "version": ATLAS_G_004_005_BRIDGE_VERSION,
            },
            max_edges=max_edges,
        )


def build_import_dependency_graph_bridge(
    *,
    high_authority_classification: dict[str, Any] | None = None,
    max_edges: int = MAX_ATLAS_G_1254_DEPENDENCY_EDGES,
) -> dict[str, Any]:
    """Build a bounded deterministic bridge from package profiles to dependency edges."""

    _validate_phase_1254_limit(
        max_edges,
        maximum=MAX_ATLAS_G_1254_DEPENDENCY_EDGES,
        token="atlas_g_1254_dependency_edge_limit",
    )
    classification = (
        build_high_authority_source_classification()
        if high_authority_classification is None
        else high_authority_classification
    )
    edges: list[dict[str, Any]] = []
    python_surfaces = _python_import_boundary_edges(edges, max_edges=max_edges)
    rust = _rust_cargo_edges(edges, max_edges=max_edges)
    python_cli = _python_cli_entrypoint_edges(edges, max_edges=max_edges)
    packages = _package_profile_edges(edges, max_edges=max_edges)
    _high_authority_source_edges(edges, classification, max_edges=max_edges)
    edges = sorted(edges, key=lambda edge: edge["edge_id"])
    edge_types = sorted({edge["edge_type"] for edge in edges})
    return {
        "edge_count": len(edges),
        "edge_types": edge_types,
        "edges": edges,
        "max_edges": max_edges,
        "package_modularity_edge_policy_token": PACKAGE_MODULARITY_EDGE_POLICY_TOKEN,
        "packages": packages,
        "python_cli_entrypoints": python_cli,
        "python_import_surfaces": python_surfaces,
        "rust_consensus": rust,
        "status": "pass",
        "version": ATLAS_G_004_005_BRIDGE_VERSION,
    }


def build_atlas_g_004_005_artifact(
    *,
    max_sources: int = MAX_ATLAS_G_1254_HIGH_AUTHORITY_SOURCES,
    max_edges: int = MAX_ATLAS_G_1254_DEPENDENCY_EDGES,
) -> dict[str, Any]:
    """Build the combined Phase 1254 ATLAS-G-004/005 artifact."""

    classification = build_high_authority_source_classification(max_sources=max_sources)
    dependency_bridge = build_import_dependency_graph_bridge(
        high_authority_classification=classification,
        max_edges=max_edges,
    )
    return {
        "artifact_id": "ilc_atlas_g_004_005_high_authority_dependency_bridge_1254_v0.1",
        "dependency_graph_bridge": dependency_bridge,
        "high_authority_source_classification": classification,
        "non_authorization_boundary": list(_NON_AUTHORIZATION_BOUNDARY),
        "required_tokens": [
            ATLAS_G_004_COMPLETION_TOKEN,
            ATLAS_G_005_COMPLETION_TOKEN,
            PHASE_1254_LEGACY_GRAPH_DELTA_DISPOSITION_TOKEN,
            PHASE_1254_COMPLETE_TOKEN,
        ],
        "status": "pass"
        if classification["status"] == "pass" and dependency_bridge["status"] == "pass"
        else "fail",
        "version": ATLAS_G_004_005_BRIDGE_VERSION,
    }


def export_atlas_g_004_005_artifact_json(artifact: dict[str, Any] | None = None) -> str:
    active = build_atlas_g_004_005_artifact() if artifact is None else artifact
    return json.dumps(
        active,
        allow_nan=False,
        separators=(",", ":"),
        sort_keys=True,
    )


def _atlas_g_006_check(
    *,
    check_id: str,
    passed: bool,
    evidence: Any,
    fail_reason: str,
) -> dict[str, Any]:
    return {
        "check_id": check_id,
        "evidence": evidence,
        "fail_reason": "" if passed else fail_reason,
        "status": "pass" if passed else "fail",
    }


def _atlas_g_006_edge_pairs(
    dependency_bridge: dict[str, Any],
    *,
    edge_type: str,
) -> set[tuple[str, str]]:
    edges = dependency_bridge.get("edges")
    if not isinstance(edges, list):
        return set()
    return {
        (str(edge.get("source")), str(edge.get("target")))
        for edge in edges
        if isinstance(edge, dict) and edge.get("edge_type") == edge_type
    }


def _atlas_g_006_component_anchor_pairs(
    dependency_bridge: dict[str, Any],
) -> set[tuple[str, str]]:
    pairs = set()
    for source, target in _atlas_g_006_edge_pairs(
        dependency_bridge, edge_type="package_component_reachable_from_anchor"
    ):
        if source.startswith("package_component:") and target.startswith("atlas_anchor:"):
            pairs.add(
                (
                    source.removeprefix("package_component:"),
                    target.removeprefix("atlas_anchor:"),
                )
            )
    return pairs


def build_atlas_g_006_public_rc_graph_reachability_gate(
    *,
    profile_id: str = ATLAS_G_006_SELECTED_PUBLIC_RC_PROFILE,
    reachability_manifest: dict[str, Any] | None = None,
    bridge_artifact: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build the Phase 1271 ATLAS-G-006 graph gate verdict.

    The gate is evidence-only. A passing graph verdict means the selected
    public-RC package profile is reachable from the required graph anchors; it
    does not authorize a release artifact, Genesis Atlas mutation, signing, or
    public RC claim.
    """

    if profile_id not in PROFILE_REACHABILITY_MANIFEST_IDS:
        raise ValueError("atlas_g_006_profile_not_in_scope")
    manifest = (
        package_profile_reachability_manifest(profile_id)
        if reachability_manifest is None
        else reachability_manifest
    )
    bridge = build_atlas_g_004_005_artifact() if bridge_artifact is None else bridge_artifact
    dependency_bridge = bridge.get("dependency_graph_bridge", {})
    classification = bridge.get("high_authority_source_classification", {})
    package_profile = manifest.get("package_profile", {})

    components = set(package_profile.get("components", []))
    surfaces = set(package_profile.get("package_surfaces", []))
    reachable_anchors = set(manifest.get("reachable_anchor_set", []))
    manifest_profile_id = manifest.get("profile_id")
    package_profile_id = package_profile.get("profile_id")
    edge_types = set(dependency_bridge.get("edge_types", []))
    profile_component_pairs = _atlas_g_006_edge_pairs(
        dependency_bridge, edge_type="package_profile_requires_component"
    )
    profile_surface_pairs = _atlas_g_006_edge_pairs(
        dependency_bridge, edge_type="package_profile_exports_surface"
    )
    component_anchor_pairs = _atlas_g_006_component_anchor_pairs(dependency_bridge)
    source_prefix = f"package_profile:{profile_id}"

    required_component_pairs = {
        (source_prefix, f"package_component:{component}")
        for component in sorted(ATLAS_G_006_REQUIRED_PROFILE_COMPONENTS)
    }
    required_surface_pairs = {
        (source_prefix, f"package_surface:{surface}")
        for surface in sorted(ATLAS_G_006_REQUIRED_PROFILE_SURFACES)
    }
    required_anchor_pairs = {
        (component, anchor)
        for component in sorted(ATLAS_G_006_REQUIRED_PROFILE_COMPONENTS)
        for anchor in GRAPH_ANCHORS
        if anchor in _COMPONENT_REACHABILITY.get(component, {}).get("anchors", ())
    }

    checks = [
        _atlas_g_006_check(
            check_id="manifest_profile_matches_selected_profile",
            passed=manifest_profile_id == profile_id and package_profile_id == profile_id,
            evidence={
                "manifest_profile_id": manifest_profile_id,
                "package_profile_id": package_profile_id,
                "selected_profile_id": profile_id,
            },
            fail_reason="atlas_g_006_manifest_profile_mismatch",
        ),
        _atlas_g_006_check(
            check_id="selected_profile_is_public_rc_target",
            passed=profile_id == ATLAS_G_006_SELECTED_PUBLIC_RC_PROFILE
            and package_profile.get("public_rc_eligible") is True,
            evidence={
                "profile_id": profile_id,
                "public_rc_eligible": package_profile.get("public_rc_eligible"),
            },
            fail_reason="atlas_g_006_selected_profile_not_public_rc_eligible",
        ),
        _atlas_g_006_check(
            check_id="selected_profile_has_public_claimability_without_public_p2p",
            passed=package_profile.get("public_claimability") is True
            and package_profile.get("public_p2p") is False,
            evidence={
                "public_claimability": package_profile.get("public_claimability"),
                "public_p2p": package_profile.get("public_p2p"),
            },
            fail_reason="atlas_g_006_selected_profile_claimability_or_p2p_boundary_invalid",
        ),
        _atlas_g_006_check(
            check_id="package_reachability_manifest_passes",
            passed=manifest.get("status") == "pass",
            evidence={
                "missing_non_excisable_components": manifest.get(
                    "missing_non_excisable_components"
                ),
                "missing_representative_paths": manifest.get("missing_representative_paths"),
                "missing_required_anchors": manifest.get("missing_required_anchors"),
                "status": manifest.get("status"),
                "unreachable_components": manifest.get("unreachable_components"),
            },
            fail_reason="atlas_g_006_reachability_manifest_not_pass",
        ),
        _atlas_g_006_check(
            check_id="all_required_anchors_reachable",
            passed=GRAPH_ANCHORS <= reachable_anchors,
            evidence={"reachable_anchor_set": sorted(reachable_anchors)},
            fail_reason="atlas_g_006_required_anchor_missing",
        ),
        _atlas_g_006_check(
            check_id="required_components_present",
            passed=ATLAS_G_006_REQUIRED_PROFILE_COMPONENTS <= components,
            evidence={
                "missing_components": sorted(
                    ATLAS_G_006_REQUIRED_PROFILE_COMPONENTS - components
                ),
                "required_components": sorted(ATLAS_G_006_REQUIRED_PROFILE_COMPONENTS),
            },
            fail_reason="atlas_g_006_required_profile_component_missing",
        ),
        _atlas_g_006_check(
            check_id="required_surfaces_present",
            passed=ATLAS_G_006_REQUIRED_PROFILE_SURFACES <= surfaces,
            evidence={
                "missing_surfaces": sorted(ATLAS_G_006_REQUIRED_PROFILE_SURFACES - surfaces),
                "required_surfaces": sorted(ATLAS_G_006_REQUIRED_PROFILE_SURFACES),
            },
            fail_reason="atlas_g_006_required_profile_surface_missing",
        ),
        _atlas_g_006_check(
            check_id="dependency_bridge_passes",
            passed=bridge.get("status") == "pass"
            and dependency_bridge.get("status") == "pass"
            and classification.get("status") == "pass",
            evidence={
                "bridge_status": bridge.get("status"),
                "dependency_bridge_status": dependency_bridge.get("status"),
                "high_authority_classification_status": classification.get("status"),
            },
            fail_reason="atlas_g_006_dependency_bridge_not_pass",
        ),
        _atlas_g_006_check(
            check_id="required_dependency_edge_types_present",
            passed=ATLAS_G_006_REQUIRED_EDGE_TYPES <= edge_types,
            evidence={
                "edge_count": dependency_bridge.get("edge_count"),
                "missing_edge_types": sorted(ATLAS_G_006_REQUIRED_EDGE_TYPES - edge_types),
                "required_edge_types": sorted(ATLAS_G_006_REQUIRED_EDGE_TYPES),
            },
            fail_reason="atlas_g_006_required_dependency_edge_type_missing",
        ),
        _atlas_g_006_check(
            check_id="required_profile_component_edges_present",
            passed=required_component_pairs <= profile_component_pairs,
            evidence={
                "missing_component_edges": sorted(
                    f"{source}->{target}"
                    for source, target in required_component_pairs - profile_component_pairs
                )
            },
            fail_reason="atlas_g_006_required_profile_component_edge_missing",
        ),
        _atlas_g_006_check(
            check_id="required_profile_surface_edges_present",
            passed=required_surface_pairs <= profile_surface_pairs,
            evidence={
                "missing_surface_edges": sorted(
                    f"{source}->{target}"
                    for source, target in required_surface_pairs - profile_surface_pairs
                )
            },
            fail_reason="atlas_g_006_required_profile_surface_edge_missing",
        ),
        _atlas_g_006_check(
            check_id="required_component_anchor_edges_present",
            passed=required_anchor_pairs <= component_anchor_pairs,
            evidence={
                "missing_component_anchor_edges": sorted(
                    f"{component}->{anchor}"
                    for component, anchor in required_anchor_pairs - component_anchor_pairs
                )
            },
            fail_reason="atlas_g_006_required_component_anchor_edge_missing",
        ),
    ]
    failing_checks = [check["check_id"] for check in checks if check["status"] != "pass"]
    status = "pass" if not failing_checks else "fail"
    return {
        "artifact_id": "ilc_atlas_g_006_public_rc_graph_reachability_gate_1271_v0.1",
        "checks": checks,
        "failing_checks": failing_checks,
        "gate_status": status,
        "graph_reachability_verdict": (
            "pass_graph_gate_only_release_artifacts_blocked"
            if status == "pass"
            else "fail_closed_release_artifacts_blocked"
        ),
        "non_authorization_boundary": list(_ATLAS_G_006_NON_AUTHORIZATION_BOUNDARY),
        "open_public_rc_blockers": [
            "claimability_runtime_and_conversion_sweeper_implementation",
            "cdl_087_ratification",
            "public_sidecar_projection_serving_authorization",
            "transport_principal_public_path_adr_and_rust_m5_hardening",
            "counsel_ip_publication_authorization",
            "v0_2_signing_authorization",
            "release_manifest_and_allowlist_publication_authorization",
        ],
        "public_rc_claim_status": "not_authorized",
        "release_artifact_status": "not_authorized",
        "required_tokens": [
            ATLAS_G_006_PUBLIC_RC_GRAPH_REACHABILITY_GATE_VERSION,
            ATLAS_G_006_PUBLIC_RC_GRAPH_REACHABILITY_VERDICT_TOKEN,
            ATLAS_G_006_PUBLIC_RELEASE_ARTIFACT_NOT_AUTHORIZED_TOKEN,
            ATLAS_G_006_NO_GENESIS_ATLAS_MUTATION_TOKEN,
            ATLAS_G_006_MANIFEST_PROFILE_CONSISTENCY_FIX1_TOKEN,
        ],
        "selected_profile_id": profile_id,
        "status": status,
        "version": ATLAS_G_006_PUBLIC_RC_GRAPH_REACHABILITY_GATE_VERSION,
    }


def export_atlas_g_006_public_rc_graph_reachability_gate_json(
    artifact: dict[str, Any] | None = None,
) -> str:
    active = (
        build_atlas_g_006_public_rc_graph_reachability_gate()
        if artifact is None
        else artifact
    )
    return json.dumps(
        active,
        allow_nan=False,
        separators=(",", ":"),
        sort_keys=True,
    )


__all__ = [
    "ATLAS_G_004_005_BRIDGE_VERSION",
    "ATLAS_G_004_COMPLETION_TOKEN",
    "ATLAS_G_005_COMPLETION_TOKEN",
    "ATLAS_G_006_NO_GENESIS_ATLAS_MUTATION_TOKEN",
    "ATLAS_G_006_MANIFEST_PROFILE_CONSISTENCY_FIX1_TOKEN",
    "ATLAS_G_006_PUBLIC_RC_GRAPH_REACHABILITY_GATE_VERSION",
    "ATLAS_G_006_PUBLIC_RC_GRAPH_REACHABILITY_VERDICT_TOKEN",
    "ATLAS_G_006_PUBLIC_RELEASE_ARTIFACT_NOT_AUTHORIZED_TOKEN",
    "ATLAS_G_006_REQUIRED_EDGE_TYPES",
    "ATLAS_G_006_REQUIRED_PROFILE_COMPONENTS",
    "ATLAS_G_006_REQUIRED_PROFILE_SURFACES",
    "ATLAS_G_006_SELECTED_PUBLIC_RC_PROFILE",
    "ATLAS_GRAPH_DISCIPLINE_VERSION",
    "GRAPH_ANCHORS",
    "GRAPH_DELTA_KINDS",
    "GRAPH_DELTA_LOAD_BEARING_KINDS",
    "GRAPH_DELTA_SIMPLE_KINDS",
    "PROFILE_REACHABILITY_MANIFEST_IDS",
    "PHASE_1254_COMPLETE_TOKEN",
    "PHASE_1254_LEGACY_GRAPH_DELTA_DISPOSITION_TOKEN",
    "build_atlas_g_004_005_artifact",
    "build_atlas_g_006_public_rc_graph_reachability_gate",
    "build_high_authority_source_classification",
    "build_import_dependency_graph_bridge",
    "export_atlas_g_004_005_artifact_json",
    "export_atlas_g_006_public_rc_graph_reachability_gate_json",
    "export_package_profile_reachability_manifest_json",
    "package_profile_reachability_manifest",
    "validate_graph_delta",
]
