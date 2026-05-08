from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

from ilc_core.protocol import StorageHarness, TransportHarness
from ilc_core.rc.local_skill_preview import (
    LOCAL_SKILL_PREVIEW_VERSION,
    LocalSkillPreviewRequest,
    build_local_skill_preview_manifest,
    execute_local_skill_preview,
    export_local_skill_preview_json,
)
from ilc_core.rc.package_profiles import PROFILE_OPENCLAW_SKILL_LOCAL


MODULE_PATH = Path("ilc_core/rc/local_skill_preview.py")


class _HarnessMemoryTransport:
    def __init__(self) -> None:
        self.payloads: dict[str, bytes] = {}

    def publish_payload(
        self,
        *,
        channel: str,
        payload: bytes,
        epoch: int,
        metadata: dict[str, str] | None = None,
    ) -> str:
        address = f"{channel}:{epoch}:{len(self.payloads)}"
        self.payloads[address] = payload
        return address

    def fetch_payload(
        self,
        *,
        address: str,
        max_bytes: int,
        epoch: int,
    ) -> bytes:
        return self.payloads[address][:max_bytes]


class _HarnessMemoryStorage:
    def __init__(self) -> None:
        self.payloads: dict[str, bytes] = {}

    def put_payload(
        self,
        *,
        key: str,
        payload: bytes,
        epoch: int,
        metadata: dict[str, str] | None = None,
    ) -> str:
        self.payloads[key] = payload
        return key

    def get_payload(
        self,
        *,
        key: str,
        max_bytes: int,
        epoch: int,
    ) -> bytes:
        return self.payloads[key][:max_bytes]

    def has_payload(
        self,
        *,
        key: str,
        epoch: int,
    ) -> bool:
        return key in self.payloads


def test_phase_1245_manifest_is_local_preview_not_public_rc() -> None:
    manifest = build_local_skill_preview_manifest()

    assert manifest["version"] == LOCAL_SKILL_PREVIEW_VERSION
    assert manifest["binding"] == "local_import_only"
    assert manifest["local_only"] is True
    assert manifest["loopback_or_subprocess_only"] is True
    assert manifest["openclaw_dependency_required"] is False
    assert manifest["nemoclaw_dependency_required"] is False
    assert manifest["public_p2p_enabled"] is False
    assert manifest["public_claimability_enabled"] is False
    assert manifest["final_public_rc_claim"] is False
    assert manifest["transport_principal_required_for_non_loopback"] is True
    assert manifest["package_profile"]["profile_id"] == PROFILE_OPENCLAW_SKILL_LOCAL
    assert manifest["package_profile"]["public_rc_eligible"] is False
    assert manifest["digitalocean_openclaw_droplet_private_target"] is True
    assert manifest["tailscale_private_harness_network_allowed"] is True


def test_phase_1245_local_skill_preview_runs_centrality_query() -> None:
    result = execute_local_skill_preview(
        LocalSkillPreviewRequest(action="fetch_incentive_centrality", top_k=3, epoch=12)
    )
    payload = json.loads(export_local_skill_preview_json(result))

    assert payload["action"] == "fetch_incentive_centrality"
    assert payload["manifest"]["local_only"] is True
    assert payload["query_result"]["query_type"] == "centrality_metrics"
    assert payload["query_result"]["top_k_applied"] == 3
    assert payload["transport_address"] is None
    assert payload["storage_key"] is None


def test_phase_1245_local_skill_preview_runs_ego_graph_query() -> None:
    result = execute_local_skill_preview({"action": "fetch_incentive_ego_graph", "epoch": 3})
    payload = json.loads(export_local_skill_preview_json(result))

    assert payload["action"] == "fetch_incentive_ego_graph"
    assert payload["query_result"]["query_type"] == "ego_graph"
    assert payload["query_result"]["node_count"] >= 1


def test_phase_1245_preview_uses_harness_owned_transport_and_storage() -> None:
    transport = _HarnessMemoryTransport()
    storage = _HarnessMemoryStorage()
    assert isinstance(transport, TransportHarness)
    assert isinstance(storage, StorageHarness)

    result = execute_local_skill_preview(
        {"action": "profile_manifest", "epoch": 9},
        transport=transport,
        storage=storage,
    )
    assert result["transport_address"] == "ilc-local-skill-preview:9:0"
    assert result["storage_key"] == "ilc-local-skill-preview:profile_manifest:9"
    assert storage.has_payload(key=result["storage_key"], epoch=9) is True

    transported = transport.fetch_payload(
        address=result["transport_address"],
        max_bytes=1_000_000,
        epoch=9,
    )
    stored = storage.get_payload(key=result["storage_key"], max_bytes=1_000_000, epoch=9)
    assert transported == stored
    assert json.loads(transported)["manifest"]["package_profile"]["profile_id"] == (
        PROFILE_OPENCLAW_SKILL_LOCAL
    )


def test_phase_1245_preview_rejects_invalid_requests() -> None:
    with pytest.raises(ValueError, match="local_skill_preview_action_unsupported"):
        execute_local_skill_preview({"action": "public_p2p"})
    with pytest.raises(ValueError, match="local_skill_preview_epoch_must_be_int"):
        execute_local_skill_preview({"action": "profile_manifest", "epoch": True})
    with pytest.raises(ValueError, match="local_skill_preview_max_bytes_must_be_int"):
        execute_local_skill_preview({"action": "profile_manifest", "max_bytes": True})
    with pytest.raises(ValueError, match="local_skill_preview_top_k_must_be_positive_int"):
        execute_local_skill_preview({"action": "fetch_incentive_centrality", "top_k": True})
    with pytest.raises(ValueError, match="local_skill_preview_top_k_must_be_positive_int"):
        execute_local_skill_preview({"action": "fetch_incentive_centrality", "top_k": 0})
    with pytest.raises(ValueError, match="local_skill_preview_top_k_limit_exceeded"):
        execute_local_skill_preview({"action": "fetch_incentive_centrality", "top_k": 101})
    with pytest.raises(ValueError, match="local_skill_preview_max_bytes_must_be_positive"):
        execute_local_skill_preview({"action": "profile_manifest", "max_bytes": 0})


def test_phase_1245_preview_imports_no_harness_network_or_storage_dependencies() -> None:
    tree = ast.parse(MODULE_PATH.read_text(encoding="utf-8"))
    forbidden_roots = {
        "aiohttp",
        "fastapi",
        "http",
        "lmdb",
        "nemoclaw",
        "openclaw",
        "requests",
        "socket",
        "urllib",
        "uvicorn",
    }
    imported_roots: set[str] = set()
    imported_modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported_roots.add(alias.name.split(".")[0])
                imported_modules.add(alias.name)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_roots.add(node.module.split(".")[0])
            imported_modules.add(node.module)

    assert imported_roots.isdisjoint(forbidden_roots)
    assert "ilc_core.storage" not in imported_modules
    assert "ilc_core.network" not in imported_modules
    assert "ilc_core.node" not in imported_modules


def test_phase_1245_preview_json_export_is_canonical() -> None:
    result = execute_local_skill_preview({"action": "profile_manifest"})
    payload_once = export_local_skill_preview_json(result)
    payload_twice = export_local_skill_preview_json(result)
    assert payload_once == payload_twice
    assert payload_once == json.dumps(
        json.loads(payload_once),
        allow_nan=False,
        separators=(",", ":"),
        sort_keys=True,
    )
