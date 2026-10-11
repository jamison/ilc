from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from ilc_core.release import upgrade_check
from ilc_core.release.installable_release_signature import (
    SIGNED_PREIMAGE_DOMAIN,
    compute_signed_preimage_sha256,
)
from ilc_core.release.upgrade_state import read_upgrade_state


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
    signed_preimage_sha256: str | None = None,
    signature_hex: str | None = None,
) -> dict[str, Any]:
    artifact_id = f"ilc-artifact:ilc-core-python-wheel-{version.replace('.', '')}@phase-1626"
    artifact_sha256 = "55" * 32
    signed_preimage_sha256 = signed_preimage_sha256 or compute_signed_preimage_sha256(
        release_id=f"ilc-core-{version}",
        artifact_id=artifact_id,
        artifact_sha256=artifact_sha256,
    )
    signature = signature_hex or private_key.sign(bytes.fromhex(signed_preimage_sha256)).hex()
    return {
        "assertion_cid": "bafy-upgrade-assertion-v1",
        "schema_version": "software_release_assertion.v0.1",
        "software_release_node": {
            "artifact_cids": ["bafy-artifact-wheel-v1"],
            "build_recipe_cid": "bafy-build-recipe-v1",
            "changelog_hash": "33" * 32,
            "cid": "bafy-release-node-v1",
            "node_kind": "SoftwareReleaseNode",
            "package_name": "ilc-core",
            "release_channel": "public_rc",
            "release_date": "2026-10-05T12:00:00Z",
            "release_key_pubkey": public_key_hex,
            "release_signature_ref": "release-attestation:wheel",
            "schema_version": "software_release_node.v0.1",
            "source_commit": "44" * 32,
            "version": version,
        },
        "release_attestation_edges": [
            {
                "artifact_id": artifact_id,
                "artifact_sha256": artifact_sha256,
                "attestation_date": "2026-10-05T12:00:00Z",
                "edge_type": "RELEASE_ATTESTS_ARTIFACT",
                "schema_version": "release_attestation_edge.v0.1",
                "signed_preimage_domain": SIGNED_PREIMAGE_DOMAIN,
                "signed_preimage_sha256": signed_preimage_sha256,
                "signer_public_key_hex": public_key_hex,
                "signature_hex": signature,
                "signing_algorithm": "Ed25519",
                "source": "bafy-release-node-v1",
                "target": "bafy-artifact-wheel-v1",
            }
        ],
    }


def _fixed_now() -> datetime:
    return datetime(2026, 10, 5, 12, 30, 0, tzinfo=timezone.utc)


def test_upgrade_check_outdated_writes_atomic_state(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    private_key, public_key_hex = _release_keypair()
    payload = _release_assertion_payload(private_key=private_key, public_key_hex=public_key_hex)
    monkeypatch.setattr(upgrade_check, "release_signer_public_key_hex", lambda: public_key_hex)

    result = upgrade_check.check_for_upgrade(
        endpoint="https://example.test/latest.json",
        fetcher=lambda endpoint, timeout: payload,
        installed_version_resolver=lambda: "0.4.32",
        now_fn=_fixed_now,
        state_path=tmp_path / "upgrade_state.json",
    )

    assert result["installed_version"] == "0.4.32"
    assert result["available_version"] == "0.4.33"
    assert result["upgrade_available"] is True
    assert result["release_signature_verified"] is True
    assert result["graph_provenance_verified"] is False
    assert result["graph_provenance_status"] == "not_present_read_only_phase"
    assert read_upgrade_state(tmp_path / "upgrade_state.json") == result


def test_upgrade_check_current_version_not_available(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    private_key, public_key_hex = _release_keypair()
    payload = _release_assertion_payload(
        private_key=private_key,
        public_key_hex=public_key_hex,
        version="0.4.32",
    )
    monkeypatch.setattr(upgrade_check, "release_signer_public_key_hex", lambda: public_key_hex)

    result = upgrade_check.check_for_upgrade(
        endpoint="https://example.test/latest.json",
        fetcher=lambda endpoint, timeout: payload,
        installed_version_resolver=lambda: "0.4.32",
        now_fn=_fixed_now,
        state_path=tmp_path / "upgrade_state.json",
    )

    assert result["upgrade_available"] is False


def test_upgrade_check_bad_release_signature_is_hard_error(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    private_key, public_key_hex = _release_keypair()
    payload = _release_assertion_payload(
        private_key=private_key,
        public_key_hex=public_key_hex,
        signature_hex="00" * 64,
    )
    monkeypatch.setattr(upgrade_check, "release_signer_public_key_hex", lambda: public_key_hex)

    with pytest.raises(upgrade_check.UpgradeCheckError) as excinfo:
        upgrade_check.check_for_upgrade(
            endpoint="https://example.test/latest.json",
            fetcher=lambda endpoint, timeout: payload,
            installed_version_resolver=lambda: "0.4.32",
            now_fn=_fixed_now,
            state_path=tmp_path / "upgrade_state.json",
        )

    assert excinfo.value.token == "upgrade_assertion_release_signature_verify_failed"


def test_upgrade_check_endpoint_unreachable_is_tokenized(tmp_path: Path) -> None:
    def _unreachable(endpoint: str, timeout: float) -> dict[str, Any]:
        raise upgrade_check.UpgradeCheckError("upgrade_check_endpoint_unreachable")

    with pytest.raises(upgrade_check.UpgradeCheckError) as excinfo:
        upgrade_check.check_for_upgrade(
            endpoint="https://example.test/latest.json",
            fetcher=_unreachable,
            installed_version_resolver=lambda: "0.4.32",
            now_fn=_fixed_now,
            state_path=tmp_path / "upgrade_state.json",
        )

    assert excinfo.value.token == "upgrade_check_endpoint_unreachable"


def test_upgrade_check_rejects_insecure_endpoint(tmp_path: Path) -> None:
    with pytest.raises(upgrade_check.UpgradeCheckError) as excinfo:
        upgrade_check.check_for_upgrade(
            endpoint="http://example.test/latest.json",
            fetcher=lambda endpoint, timeout: {},
            installed_version_resolver=lambda: "0.4.32",
            now_fn=_fixed_now,
            state_path=tmp_path / "upgrade_state.json",
        )

    assert excinfo.value.token == "upgrade_check_endpoint_insecure"


def test_upgrade_check_rejects_userinfo_in_explicit_endpoint(tmp_path: Path) -> None:
    with pytest.raises(upgrade_check.UpgradeCheckError) as excinfo:
        upgrade_check.check_for_upgrade(
            endpoint="https://user:pass@example.test/latest.json",
            fetcher=lambda endpoint, timeout: {},
            installed_version_resolver=lambda: "0.4.32",
            now_fn=_fixed_now,
            state_path=tmp_path / "upgrade_state.json",
        )

    assert excinfo.value.token == "upgrade_check_endpoint_userinfo_forbidden"


def test_upgrade_check_pads_mixed_component_versions(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    private_key, public_key_hex = _release_keypair()
    payload = _release_assertion_payload(
        private_key=private_key,
        public_key_hex=public_key_hex,
        version="0.4.0",
    )
    monkeypatch.setattr(upgrade_check, "release_signer_public_key_hex", lambda: public_key_hex)

    result = upgrade_check.check_for_upgrade(
        endpoint="https://example.test/latest.json",
        fetcher=lambda endpoint, timeout: payload,
        installed_version_resolver=lambda: "0.4",
        now_fn=_fixed_now,
        state_path=tmp_path / "upgrade_state.json",
    )

    assert result["upgrade_available"] is False
