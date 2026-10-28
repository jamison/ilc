from __future__ import annotations

import inspect
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Mapping

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from ilc_core.encoding.cidv1 import node_id_from_obj
from ilc_core.release import upgrade_check
from ilc_core.release.constants import UPGRADE_CHECK_D2D_HOP_COUNT_HEADER
from ilc_core.release.installable_release_signature import (
    DEFAULT_GENESIS_LINEAGE_REF,
    DEFAULT_PRIOR_RELEASE_ENVELOPE_REF,
    DEFAULT_RELEASE_KEY_REGISTRATION_REF,
    SIGNED_PREIMAGE_DOMAIN,
    compute_signed_preimage_sha256,
)
from ilc_core.release.upgrade_state import write_upgrade_state


def _release_keypair() -> tuple[Ed25519PrivateKey, str]:
    private_key = Ed25519PrivateKey.generate()
    public_key_hex = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    ).hex()
    return private_key, public_key_hex


def _release_assertion_payload(
    *,
    private_key: Ed25519PrivateKey,
    public_key_hex: str,
    version: str = "0.4.33",
) -> dict[str, Any]:
    artifact_id = f"ilc-artifact:ilc-core-python-wheel-{version.replace('.', '')}@phase-1628"
    artifact_sha256 = "55" * 32
    signed_preimage_sha256 = compute_signed_preimage_sha256(
        release_id=f"ilc-core-{version}",
        artifact_id=artifact_id,
        artifact_sha256=artifact_sha256,
    )
    artifact_body = {
        "artifact_id": artifact_id,
        "artifact_type": "wheel",
        "filename": f"ilc_core-{version}-py3-none-any.whl",
        "node_kind": "ArtifactNode",
        "package_name": "ilc-core",
        "package_version": version,
        "pypi_url": "https://example.test/release.whl",
        "schema_version": "artifact_node.v0.1",
        "sha256": artifact_sha256,
        "size_bytes": 1234,
    }
    artifact = {**artifact_body, "cid": node_id_from_obj(artifact_body)}
    recipe_body = {
        "build_command": "python -m build",
        "build_date": "2026-10-05T12:00:00Z",
        "build_env_hash": "66" * 32,
        "build_toolchain": "python-build",
        "builder_agent_id": "phase:native-discovery-test",
        "node_kind": "BuildRecipeNode",
        "reproducibility_hash": "77" * 32,
        "schema_version": "build_recipe_node.v0.1",
        "source_commit": "44" * 32,
    }
    recipe = {**recipe_body, "cid": node_id_from_obj(recipe_body)}
    release_body = {
        "artifact_cids": [artifact["cid"]],
        "build_recipe_cid": recipe["cid"],
        "changelog_hash": "33" * 32,
        "node_kind": "SoftwareReleaseNode",
        "package_name": "ilc-core",
        "release_channel": "public_rc",
        "release_date": "2026-10-05T12:00:00Z",
        "release_key_pubkey": public_key_hex,
        "release_signature_ref": "release-attestation:wheel",
        "schema_version": "software_release_node.v0.1",
        "source_commit": "44" * 32,
        "version": version,
    }
    release = {**release_body, "cid": node_id_from_obj(release_body)}
    edge = {
        "artifact_id": artifact_id,
        "artifact_sha256": artifact_sha256,
        "attestation_date": "2026-10-05T12:00:00Z",
        "edge_type": "RELEASE_ATTESTS_ARTIFACT",
        "genesis_lineage_ref": DEFAULT_GENESIS_LINEAGE_REF,
        "prior_release_envelope_ref": DEFAULT_PRIOR_RELEASE_ENVELOPE_REF,
        "release_key_registration_ref": DEFAULT_RELEASE_KEY_REGISTRATION_REF,
        "schema_version": "release_attestation_edge.v0.1",
        "signed_preimage_domain": SIGNED_PREIMAGE_DOMAIN,
        "signed_preimage_sha256": signed_preimage_sha256,
        "signer_public_key_hex": public_key_hex,
        "signature_hex": private_key.sign(bytes.fromhex(signed_preimage_sha256)).hex(),
        "signing_algorithm": "Ed25519",
        "source": release["cid"],
        "target": artifact["cid"],
    }
    body = {
        "artifact_nodes": [artifact],
        "build_recipe_nodes": [recipe],
        "release_attestation_edges": [edge],
        "schema_version": "software_release_assertion.v0.1",
        "software_release_node": release,
    }
    return {**body, "assertion_cid": node_id_from_obj(body)}


def _fixed_now() -> datetime:
    return datetime(2026, 10, 6, 12, 0, 0, tzinfo=timezone.utc)


def _write_peer_hints(path: Path, endpoint: str = "https://peer-one.example") -> None:
    path.write_text(
        json.dumps(
            {
                "known_peer_hint_key_bindings": {},
                "known_peer_hints": [
                    {
                        "body": {
                            "transport_endpoint": {
                                "host": endpoint.removeprefix("https://"),
                                "port": 443,
                                "scheme": "https",
                            }
                        }
                    }
                ],
                "schema_version": "bootstrap_peer_hints.v0.1",
            },
            sort_keys=True,
        ),
        encoding="utf-8",
    )


def test_local_graph_cache_hit_uses_cached_raw_assertion_without_network(
    monkeypatch,
    tmp_path: Path,
) -> None:
    private_key, public_key_hex = _release_keypair()
    payload = _release_assertion_payload(private_key=private_key, public_key_hex=public_key_hex)
    monkeypatch.setattr(upgrade_check, "release_signer_public_key_hex", lambda: public_key_hex)
    state_path = tmp_path / "upgrade_state.json"
    write_upgrade_state(
        {
            "checked_at_utc": "2026-10-06T11:45:00Z",
            "release_assertion_payload": payload,
        },
        path=state_path,
    )

    def _network_forbidden(*args: object, **kwargs: object) -> Mapping[str, Any]:
        raise AssertionError("network path should not be called")

    result = upgrade_check.check_for_upgrade(
        fetcher=_network_forbidden,
        peer_fetcher=_network_forbidden,
        bootstrap_peer_hints_paths=[],
        evaluation_runtime=upgrade_check.UpgradeEvaluationRuntime(
            installed_version_resolver=lambda: "0.4.32",
            now_fn=_fixed_now,
        ),
        state_path=state_path,
    )

    assert result["discovery_source"] == "local_graph_cache"
    assert result["available_version"] == "0.4.33"


def test_result_only_state_is_cache_miss_and_peer_hint_can_succeed(
    monkeypatch,
    tmp_path: Path,
) -> None:
    private_key, public_key_hex = _release_keypair()
    payload = _release_assertion_payload(private_key=private_key, public_key_hex=public_key_hex)
    monkeypatch.setattr(upgrade_check, "release_signer_public_key_hex", lambda: public_key_hex)
    state_path = tmp_path / "upgrade_state.json"
    write_upgrade_state({"checked_at_utc": "2026-10-06T11:45:00Z"}, path=state_path)
    hints_path = tmp_path / "bootstrap_peer_hints.json"
    _write_peer_hints(hints_path)
    observed: dict[str, Any] = {}

    def _peer_fetch(endpoint: str, timeout: float, headers: Mapping[str, str]) -> Mapping[str, Any]:
        observed["endpoint"] = endpoint
        observed["headers"] = dict(headers)
        return payload

    result = upgrade_check.check_for_upgrade(
        peer_fetcher=_peer_fetch,
        bootstrap_peer_hints_paths=[hints_path],
        fetcher=lambda endpoint, timeout: (_ for _ in ()).throw(AssertionError("fallback unused")),
        evaluation_runtime=upgrade_check.UpgradeEvaluationRuntime(
            installed_version_resolver=lambda: "0.4.32",
            now_fn=_fixed_now,
        ),
        state_path=state_path,
    )

    assert result["discovery_source"] == "bootstrap_peer_hint"
    assert observed["endpoint"] == "https://peer-one.example:443/.well-known/ilc/software-release/latest.json"
    assert observed["headers"][UPGRADE_CHECK_D2D_HOP_COUNT_HEADER] == "1"


def test_peer_hint_fail_falls_back_to_https(monkeypatch, tmp_path: Path) -> None:
    private_key, public_key_hex = _release_keypair()
    payload = _release_assertion_payload(private_key=private_key, public_key_hex=public_key_hex)
    monkeypatch.setattr(upgrade_check, "release_signer_public_key_hex", lambda: public_key_hex)
    hints_path = tmp_path / "bootstrap_peer_hints.json"
    _write_peer_hints(hints_path)

    result = upgrade_check.check_for_upgrade(
        peer_fetcher=lambda endpoint, timeout, headers: {"bad": "payload"},
        bootstrap_peer_hints_paths=[hints_path],
        fetcher=lambda endpoint, timeout: payload,
        evaluation_runtime=upgrade_check.UpgradeEvaluationRuntime(
            installed_version_resolver=lambda: "0.4.32",
            now_fn=_fixed_now,
        ),
        state_path=tmp_path / "upgrade_state.json",
    )

    assert result["discovery_source"] == "https_fallback"
    assert result["endpoint"] == "https://ilc.network/.well-known/ilc/software-release/latest.json"


def test_single_hop_d2d_registry_used_after_bootstrap_hints(monkeypatch, tmp_path: Path) -> None:
    private_key, public_key_hex = _release_keypair()
    payload = _release_assertion_payload(private_key=private_key, public_key_hex=public_key_hex)
    monkeypatch.setattr(upgrade_check, "release_signer_public_key_hex", lambda: public_key_hex)
    observed: dict[str, Any] = {}

    class _Registry:
        def get_peers(self) -> list[str]:
            return ["https://registry-peer.example"]

    def _peer_fetch(endpoint: str, timeout: float, headers: Mapping[str, str]) -> Mapping[str, Any]:
        observed["endpoint"] = endpoint
        observed["headers"] = dict(headers)
        return payload

    result = upgrade_check.check_for_upgrade(
        peer_registry=_Registry(),
        peer_fetcher=_peer_fetch,
        bootstrap_peer_hints_paths=[],
        fetcher=lambda endpoint, timeout: (_ for _ in ()).throw(AssertionError("fallback unused")),
        evaluation_runtime=upgrade_check.UpgradeEvaluationRuntime(
            installed_version_resolver=lambda: "0.4.32",
            now_fn=_fixed_now,
        ),
        state_path=tmp_path / "upgrade_state.json",
    )

    assert result["discovery_source"] == "single_hop_d2d"
    assert (
        observed["endpoint"]
        == "https://registry-peer.example/.well-known/ilc/software-release/latest.json"
    )
    assert observed["headers"][UPGRADE_CHECK_D2D_HOP_COUNT_HEADER] == "1"


def test_explicit_endpoint_override_bypasses_cache_and_peer_hints(monkeypatch, tmp_path: Path) -> None:
    private_key, public_key_hex = _release_keypair()
    payload = _release_assertion_payload(private_key=private_key, public_key_hex=public_key_hex)
    monkeypatch.setattr(upgrade_check, "release_signer_public_key_hex", lambda: public_key_hex)
    state_path = tmp_path / "upgrade_state.json"
    write_upgrade_state(
        {
            "checked_at_utc": "2026-10-06T11:45:00Z",
            "release_assertion_payload": payload,
        },
        path=state_path,
    )

    result = upgrade_check.check_for_upgrade(
        endpoint="https://operator.example/latest.json",
        fetcher=lambda endpoint, timeout: payload,
        peer_fetcher=lambda endpoint, timeout, headers: (_ for _ in ()).throw(
            AssertionError("peer discovery bypassed")
        ),
        bootstrap_peer_hints_paths=[tmp_path / "missing.json"],
        evaluation_runtime=upgrade_check.UpgradeEvaluationRuntime(
            installed_version_resolver=lambda: "0.4.32",
            now_fn=_fixed_now,
        ),
        state_path=state_path,
    )

    assert result["discovery_source"] == "explicit_endpoint"
    assert result["endpoint"] == "https://operator.example/latest.json"


def test_invalid_peer_assertion_is_not_returned(monkeypatch, tmp_path: Path) -> None:
    private_key, public_key_hex = _release_keypair()
    payload = _release_assertion_payload(private_key=private_key, public_key_hex=public_key_hex)
    monkeypatch.setattr(upgrade_check, "release_signer_public_key_hex", lambda: public_key_hex)
    hints_path = tmp_path / "bootstrap_peer_hints.json"
    _write_peer_hints(hints_path)

    result = upgrade_check.check_for_upgrade(
        peer_fetcher=lambda endpoint, timeout, headers: {"software_release_node": {"bad": True}},
        bootstrap_peer_hints_paths=[hints_path],
        fetcher=lambda endpoint, timeout: payload,
        evaluation_runtime=upgrade_check.UpgradeEvaluationRuntime(
            installed_version_resolver=lambda: "0.4.32",
            now_fn=_fixed_now,
        ),
        state_path=tmp_path / "upgrade_state.json",
    )

    assert result["discovery_source"] == "https_fallback"
    assert result["assertion_cid"] == payload["assertion_cid"]


def test_stale_local_cache_is_ignored(monkeypatch, tmp_path: Path) -> None:
    private_key, public_key_hex = _release_keypair()
    cached = _release_assertion_payload(
        private_key=private_key,
        public_key_hex=public_key_hex,
        version="0.4.33",
    )
    fresh = _release_assertion_payload(
        private_key=private_key,
        public_key_hex=public_key_hex,
        version="0.4.34",
    )
    monkeypatch.setattr(upgrade_check, "release_signer_public_key_hex", lambda: public_key_hex)
    state_path = tmp_path / "upgrade_state.json"
    write_upgrade_state(
        {
            "checked_at_utc": (_fixed_now() - timedelta(hours=3)).isoformat().replace("+00:00", "Z"),
            "release_assertion_payload": cached,
        },
        path=state_path,
    )

    result = upgrade_check.check_for_upgrade(
        bootstrap_peer_hints_paths=[],
        fetcher=lambda endpoint, timeout: fresh,
        evaluation_runtime=upgrade_check.UpgradeEvaluationRuntime(
            installed_version_resolver=lambda: "0.4.32",
            now_fn=_fixed_now,
        ),
        state_path=state_path,
    )

    assert result["discovery_source"] == "https_fallback"
    assert result["available_version"] == "0.4.34"


def test_upgrade_check_does_not_import_invite_time_fetch_helper() -> None:
    source = inspect.getsource(upgrade_check)
    assert "fetch_distributed_release_peers" not in source
