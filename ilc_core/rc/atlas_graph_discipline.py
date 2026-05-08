"""ATLAS-G graph-discipline helpers for public-RC package reachability.

This module is intentionally declarative and non-mutating. It validates the
phase-close ``graph_delta=...`` discipline and exports deterministic
package-profile reachability manifests that keep Genesis, ILC, ECU, canonical
JSON, protocol-bundle verification, Rust consensus binding, and the hypergraph
surface visible from public-RC packaging profiles.
"""

from __future__ import annotations

import json
from typing import Any

from ilc_core.rc.package_profiles import (
    NON_EXCISABLE_COMPONENTS,
    PROFILE_OPENCLAW_SKILL_CLAIMABLE,
    PROFILE_OPENCLAW_SKILL_LOCAL,
    get_package_profile,
    profile_manifest,
    validate_package_profile,
)

ATLAS_GRAPH_DISCIPLINE_VERSION = "atlas_graph_discipline_1247.v0.1"

GRAPH_ANCHORS = frozenset({"ecu", "genesis", "hypergraph", "ilc"})
GRAPH_DELTA_SIMPLE_KINDS = frozenset({"deferred", "none", "support_only"})
GRAPH_DELTA_LOAD_BEARING_KINDS = frozenset(
    {"load_bearing_artifact_added", "load_bearing_artifact_changed"}
)
GRAPH_DELTA_KINDS = GRAPH_DELTA_SIMPLE_KINDS | GRAPH_DELTA_LOAD_BEARING_KINDS

PROFILE_REACHABILITY_MANIFEST_IDS = frozenset(
    {PROFILE_OPENCLAW_SKILL_CLAIMABLE, PROFILE_OPENCLAW_SKILL_LOCAL}
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
    return {
        "anchors": anchors,
        "component": component,
        "non_excisable": component in NON_EXCISABLE_COMPONENTS,
        "reachable_from_required_anchor": bool(set(anchors) & GRAPH_ANCHORS),
        "relation": reachability["relation"],
        "representative_paths": sorted(reachability["representative_paths"]),
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
    missing_non_excisable = sorted(set(NON_EXCISABLE_COMPONENTS) - set(manifest["components"]))
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
        "non_excisable_components": sorted(NON_EXCISABLE_COMPONENTS),
        "package_profile": manifest,
        "profile_id": profile_id,
        "reachable_anchor_set": reachable_anchors,
        "status": "pass" if not missing_non_excisable and not unreachable_components else "fail",
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


__all__ = [
    "ATLAS_GRAPH_DISCIPLINE_VERSION",
    "GRAPH_ANCHORS",
    "GRAPH_DELTA_KINDS",
    "GRAPH_DELTA_LOAD_BEARING_KINDS",
    "GRAPH_DELTA_SIMPLE_KINDS",
    "PROFILE_REACHABILITY_MANIFEST_IDS",
    "export_package_profile_reachability_manifest_json",
    "package_profile_reachability_manifest",
    "validate_graph_delta",
]
