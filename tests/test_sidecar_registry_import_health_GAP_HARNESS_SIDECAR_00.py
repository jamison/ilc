# SPDX-License-Identifier: AGPL-3.0-only
"""Regression tests for GAP-HARNESS-SIDECAR-00 sidecar import health."""

from ilc_core.economics import passive_ecu_attribution_runtime
from ilc_core.network.d2d import centrality_delta_gossip_constants
from ilc_core.network.d2d import centrality_delta_gossip_runtime
from ilc_core.sidecars.registry_manifest import (
    _NON_AUTHORIZATION_BOUNDARY,
    build_sidecar_registry_manifest,
)


def test_sidecar_registry_manifest_imports_and_builds_cleanly() -> None:
    manifest = build_sidecar_registry_manifest()

    assert manifest["version"] == "graph_native_sidecar_registry_manifest_phase_1307.v0.1"
    assert len(manifest["sidecars"]) == 15


def test_sidecar_registry_manifest_has_fifteen_sidecars() -> None:
    manifest = build_sidecar_registry_manifest()
    sidecar_ids = {sidecar["sidecar_id"] for sidecar in manifest["sidecars"]}

    assert sidecar_ids == {
        "confidential_coordination_capability_membership_boundary",
        "confidential_coordination_gossip_jitter_cover_policy",
        "confidential_coordination_local_preview",
        "confidential_coordination_private_gated_shard",
        "confidential_coordination_sealed_sender_local_delivery",
        "local_graph_memory_projection",
        "offline_claimability_receipt_verifier",
        "openclaw_nemoclaw_local_bridge",
        "public_fetch_p2p_readiness_candidate",
        "sidecar_registry_manifest",
        "transport_principal_admission",
        "truth_primitive_submission_boundary",
        "upnp-router-mapping",
        "value_path_activation_boundary_preflight",
        "wallet_action_semantics_preflight",
    }


def test_all_registry_sidecar_entries_remain_public_serving_disabled() -> None:
    manifest = build_sidecar_registry_manifest()

    assert all(sidecar["public_serving_enabled"] is False for sidecar in manifest["sidecars"])
    assert manifest["public_serving_enabled"] is False
    assert manifest["public_package_publication_authorized"] is False
    assert manifest["public_rc_claimed"] is False


def test_non_authorization_boundary_remains_present_and_broad() -> None:
    manifest = build_sidecar_registry_manifest()

    assert len(_NON_AUTHORIZATION_BOUNDARY) >= 21
    assert manifest["non_authorization_boundary"] == list(_NON_AUTHORIZATION_BOUNDARY)
    assert "no_public_sidecar_or_projection_serving" in _NON_AUTHORIZATION_BOUNDARY
    assert "no_wallet_signing_or_ledger_write" in _NON_AUTHORIZATION_BOUNDARY
    assert "no_value_path_activation" in _NON_AUTHORIZATION_BOUNDARY


def test_cdl060_constants_are_dependency_light_and_identical() -> None:
    assert (
        centrality_delta_gossip_constants.CDL_060_GOSSIP_RUNTIME_VERSION
        == centrality_delta_gossip_runtime.CDL_060_GOSSIP_RUNTIME_VERSION
        == "centrality_delta_gossip_runtime_GAP_CDL060.v0.2"
    )
    assert (
        centrality_delta_gossip_constants.CENTRALITY_QUANTUM
        == centrality_delta_gossip_runtime.CENTRALITY_QUANTUM
    )
    assert (
        passive_ecu_attribution_runtime.CDL_060_GOSSIP_RUNTIME_DEPENDENCY
        == centrality_delta_gossip_constants.CDL_060_GOSSIP_RUNTIME_VERSION
    )
