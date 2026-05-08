"""Local OpenClaw/NemoClaw-style skill preview adapter.

This module is a local/private harness seam. It proves that a harness can call
ILC through imports and harness-owned transport/storage interfaces without
making OpenClaw, NemoClaw, public P2P, or public claimability a protocol
dependency.
"""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

from ilc_core.graph.agent_graph_projection_runtime import (
    build_fetch_incentive_hypergraph_slice,
)
from ilc_core.graph.sidecar_query_runtime import (
    SidecarQueryBounds,
    execute_sidecar_query,
    export_sidecar_query_json,
)
from ilc_core.protocol.harness_interfaces import (
    StorageHarness,
    TransportHarness,
)
from ilc_core.rc.package_profiles import (
    PROFILE_OPENCLAW_SKILL_LOCAL,
    profile_manifest,
)

LOCAL_SKILL_PREVIEW_VERSION = "local_skill_preview_1245.v0.1"
LOCAL_SKILL_PREVIEW_BINDING = "local_import_only"
LOCAL_SKILL_PREVIEW_PROFILE = PROFILE_OPENCLAW_SKILL_LOCAL
MAX_SKILL_PREVIEW_BYTES = 1_000_000
ALLOWED_SKILL_PREVIEW_ACTIONS = frozenset(
    {
        "profile_manifest",
        "fetch_incentive_centrality",
        "fetch_incentive_ego_graph",
    }
)


@dataclass(frozen=True)
class LocalSkillPreviewRequest:
    action: str
    root_id: str | None = None
    top_k: int | None = None
    epoch: int = 0
    max_bytes: int = MAX_SKILL_PREVIEW_BYTES

    def validate(self) -> None:
        if self.action not in ALLOWED_SKILL_PREVIEW_ACTIONS:
            raise ValueError("local_skill_preview_action_unsupported")
        if type(self.epoch) is not int:
            raise ValueError("local_skill_preview_epoch_must_be_int")
        if self.epoch < 0:
            raise ValueError("local_skill_preview_epoch_must_be_non_negative")
        if type(self.max_bytes) is not int:
            raise ValueError("local_skill_preview_max_bytes_must_be_int")
        if self.max_bytes <= 0:
            raise ValueError("local_skill_preview_max_bytes_must_be_positive")
        if self.top_k is not None:
            if type(self.top_k) is not int:
                raise ValueError("local_skill_preview_top_k_must_be_positive_int")
            if self.top_k <= 0:
                raise ValueError("local_skill_preview_top_k_must_be_positive_int")
        if self.root_id is not None and (type(self.root_id) is not str or not self.root_id):
            raise ValueError("local_skill_preview_root_id_invalid")


def build_local_skill_preview_manifest() -> dict[str, Any]:
    package_manifest = profile_manifest(LOCAL_SKILL_PREVIEW_PROFILE)
    return {
        "binding": LOCAL_SKILL_PREVIEW_BINDING,
        "digitalocean_openclaw_droplet_private_target": True,
        "final_public_rc_claim": False,
        "local_only": True,
        "loopback_or_subprocess_only": True,
        "openclaw_dependency_required": False,
        "nemoclaw_dependency_required": False,
        "package_profile": package_manifest,
        "public_claimability_enabled": False,
        "public_p2p_enabled": False,
        "tailscale_private_harness_network_allowed": True,
        "transport_principal_required_for_non_loopback": True,
        "version": LOCAL_SKILL_PREVIEW_VERSION,
    }


def execute_local_skill_preview(
    request: LocalSkillPreviewRequest | Mapping[str, Any],
    *,
    transport: TransportHarness | None = None,
    storage: StorageHarness | None = None,
) -> dict[str, Any]:
    active_request = _coerce_request(request)
    active_request.validate()

    if active_request.action == "profile_manifest":
        result = {
            "action": active_request.action,
            "manifest": build_local_skill_preview_manifest(),
        }
        return _finalize_result(result, active_request, transport=transport, storage=storage)

    projection = build_fetch_incentive_hypergraph_slice()
    if active_request.action == "fetch_incentive_centrality":
        query_result = execute_sidecar_query(
            query_type="centrality_metrics",
            projection=projection,
            bounds=SidecarQueryBounds(max_results=active_request.top_k or 10),
            top_k=active_request.top_k or 10,
        )
    else:
        root_id = active_request.root_id or _first_projection_node_id(projection)
        query_result = execute_sidecar_query(
            query_type="ego_graph",
            projection=projection,
            bounds=SidecarQueryBounds(max_hops=1, max_nodes=50, max_results=50),
            root_id=root_id,
            hops=1,
        )

    result = {
        "action": active_request.action,
        "manifest": build_local_skill_preview_manifest(),
        "query_result": query_result,
    }
    return _finalize_result(result, active_request, transport=transport, storage=storage)


def export_local_skill_preview_json(
    result: Mapping[str, Any],
    *,
    max_bytes: int = MAX_SKILL_PREVIEW_BYTES,
) -> str:
    if type(max_bytes) is not int:
        raise ValueError("local_skill_preview_max_bytes_must_be_int")
    if max_bytes <= 0:
        raise ValueError("local_skill_preview_max_bytes_must_be_positive")
    payload = export_sidecar_query_json(result, max_bytes=max_bytes)
    # Round-trip through JSON to ensure callers never receive Decimal objects.
    return json.dumps(
        json.loads(payload),
        allow_nan=False,
        separators=(",", ":"),
        sort_keys=True,
    )


def _finalize_result(
    result: dict[str, Any],
    request: LocalSkillPreviewRequest,
    *,
    transport: TransportHarness | None,
    storage: StorageHarness | None,
) -> dict[str, Any]:
    payload = export_local_skill_preview_json(result, max_bytes=request.max_bytes).encode("utf-8")
    transport_address = None
    storage_key = None
    if transport is not None:
        transport_address = transport.publish_payload(
            channel="ilc-local-skill-preview",
            payload=payload,
            epoch=request.epoch,
            metadata={"version": LOCAL_SKILL_PREVIEW_VERSION},
        )
    if storage is not None:
        storage_key = storage.put_payload(
            key=f"ilc-local-skill-preview:{request.action}:{request.epoch}",
            payload=payload,
            epoch=request.epoch,
            metadata={"version": LOCAL_SKILL_PREVIEW_VERSION},
        )
    result["transport_address"] = transport_address
    result["storage_key"] = storage_key
    return result


def _coerce_request(request: LocalSkillPreviewRequest | Mapping[str, Any]) -> LocalSkillPreviewRequest:
    if isinstance(request, LocalSkillPreviewRequest):
        return request
    if not isinstance(request, Mapping):
        raise ValueError("local_skill_preview_request_must_be_mapping")
    return LocalSkillPreviewRequest(
        action=str(request.get("action", "")),
        epoch=request.get("epoch", 0),
        max_bytes=request.get("max_bytes", MAX_SKILL_PREVIEW_BYTES),
        root_id=request.get("root_id"),
        top_k=request.get("top_k"),
    )


def _first_projection_node_id(projection: Mapping[str, Any]) -> str:
    nodes = projection.get("nodes", ())
    if not isinstance(nodes, Sequence) or not nodes:
        raise ValueError("local_skill_preview_projection_has_no_nodes")
    first = nodes[0]
    if not isinstance(first, Mapping):
        raise ValueError("local_skill_preview_projection_node_invalid")
    node_id = first.get("canonical_id")
    if type(node_id) is not str or not node_id:
        raise ValueError("local_skill_preview_projection_node_invalid")
    return node_id


__all__ = [
    "ALLOWED_SKILL_PREVIEW_ACTIONS",
    "LOCAL_SKILL_PREVIEW_BINDING",
    "LOCAL_SKILL_PREVIEW_PROFILE",
    "LOCAL_SKILL_PREVIEW_VERSION",
    "LocalSkillPreviewRequest",
    "build_local_skill_preview_manifest",
    "execute_local_skill_preview",
    "export_local_skill_preview_json",
]
