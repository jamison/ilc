from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from ilc_core.encoding.cidv1 import node_id_from_obj
from ilc_core.release import upgrade_check
from ilc_core.release.installable_release_signature import (
    DEFAULT_GENESIS_LINEAGE_REF,
    DEFAULT_PRIOR_RELEASE_ENVELOPE_REF,
    DEFAULT_RELEASE_KEY_REGISTRATION_REF,
    SIGNED_PREIMAGE_DOMAIN,
    compute_signed_preimage_sha256,
)
from ilc_core.release.upgrade_state import MAX_UPGRADE_STATE_BYTES, read_upgrade_state


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
    signature_scheme: str | None = None,
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
    artifact_body = {
        "artifact_id": artifact_id,
        "artifact_type": "wheel",
        "filename": f"ilc_core-{version}-py3-none-any.whl",
        "node_kind": "ArtifactNode",
        "package_name": "ilc-core",
        "package_version": version,
        "pypi_url": "https://example.test/ilc-core.whl",
        "schema_version": "artifact_node.v0.1",
        "sha256": artifact_sha256,
        "size_bytes": 1234,
    }
    artifact_node = {**artifact_body, "cid": node_id_from_obj(artifact_body)}
    source_commit = "44" * 32
    build_recipe_body = {
        "build_command": "python -m build",
        "build_date": "2026-10-05T12:00:00Z",
        "build_env_hash": "66" * 32,
        "build_toolchain": "python-build",
        "builder_agent_id": "phase:test",
        "node_kind": "BuildRecipeNode",
        "reproducibility_hash": "77" * 32,
        "schema_version": "build_recipe_node.v0.1",
        "source_commit": source_commit,
    }
    build_recipe_node = {
        **build_recipe_body,
        "cid": node_id_from_obj(build_recipe_body),
    }
    release_body = {
        "artifact_cids": [artifact_node["cid"]],
        "build_recipe_cid": build_recipe_node["cid"],
        "changelog_hash": "33" * 32,
        "node_kind": "SoftwareReleaseNode",
        "package_name": "ilc-core",
        "release_channel": "public_rc",
        "release_date": "2026-10-05T12:00:00Z",
        "release_key_pubkey": public_key_hex,
        "release_signature_ref": "release-attestation:wheel",
        "schema_version": "software_release_node.v0.1",
        "source_commit": source_commit,
        "version": version,
    }
    release_node = {**release_body, "cid": node_id_from_obj(release_body)}
    edge = {
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
        "genesis_lineage_ref": DEFAULT_GENESIS_LINEAGE_REF,
        "prior_release_envelope_ref": DEFAULT_PRIOR_RELEASE_ENVELOPE_REF,
        "release_key_registration_ref": DEFAULT_RELEASE_KEY_REGISTRATION_REF,
        "source": release_node["cid"],
        "target": artifact_node["cid"],
    }
    if signature_scheme is not None:
        edge["signature_scheme"] = signature_scheme
    assertion_body = {
        "artifact_nodes": [artifact_node],
        "build_recipe_nodes": [build_recipe_node],
        "release_attestation_edges": [edge],
        "schema_version": "software_release_assertion.v0.1",
        "software_release_node": release_node,
    }
    return {**assertion_body, "assertion_cid": node_id_from_obj(assertion_body)}


def _fixed_now() -> datetime:
    return datetime(2026, 10, 5, 12, 30, 0, tzinfo=timezone.utc)


def test_upgrade_check_outdated_writes_atomic_state(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    private_key, public_key_hex = _release_keypair()
    payload = _release_assertion_payload(private_key=private_key, public_key_hex=public_key_hex)
    monkeypatch.setattr(upgrade_check, "release_signer_public_key_hex", lambda: public_key_hex)

    result = upgrade_check.check_for_upgrade(
        endpoint="https://example.test/latest.json",
        fetcher=lambda endpoint, timeout: payload,
        evaluation_runtime=upgrade_check.UpgradeEvaluationRuntime(
            installed_version_resolver=lambda: "0.4.32",
            now_fn=_fixed_now,
        ),
        state_path=tmp_path / "upgrade_state.json",
    )

    assert result["installed_version"] == "0.4.32"
    assert result["available_version"] == "0.4.33"
    assert result["candidate_version_relation"] == "newer"
    assert result["candidate_upgrade_available"] is True
    assert result["authorized_upgrade_available"] is False
    assert result["release_signature_verified"] is True
    assert result["signature_scheme"] == "ed25519_phase_1335"
    assert result["graph_provenance_verified"] is False
    assert result["graph_provenance_status"] == "not_present_core_only"
    assert read_upgrade_state(tmp_path / "upgrade_state.json") == result


def test_release_assertion_without_signature_scheme_defaults_to_ed25519(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    private_key, public_key_hex = _release_keypair()
    payload = _release_assertion_payload(private_key=private_key, public_key_hex=public_key_hex)
    monkeypatch.setattr(upgrade_check, "release_signer_public_key_hex", lambda: public_key_hex)

    result = upgrade_check.validate_release_assertion(payload)

    assert result["release_signature_verified"] is True
    assert result["signature_scheme"] == "ed25519_phase_1335"


def test_release_assertion_explicit_ed25519_signature_scheme_validates(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    private_key, public_key_hex = _release_keypair()
    payload = _release_assertion_payload(
        private_key=private_key,
        public_key_hex=public_key_hex,
        signature_scheme="ed25519_phase_1335",
    )
    monkeypatch.setattr(upgrade_check, "release_signer_public_key_hex", lambda: public_key_hex)

    result = upgrade_check.validate_release_assertion(payload)

    assert result["release_signature_verified"] is True
    assert result["signature_scheme"] == "ed25519_phase_1335"


def test_release_assertion_binary_tarball_artifact_validates(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    private_key, public_key_hex = _release_keypair()
    payload = _release_assertion_payload(
        private_key=private_key,
        public_key_hex=public_key_hex,
    )
    artifact = payload["artifact_nodes"][0]
    artifact["artifact_type"] = "binary_tarball"
    artifact["filename"] = "ilc-consensus-linux-x86_64-v0.4.33.tar.gz"
    artifact_body = {key: value for key, value in artifact.items() if key != "cid"}
    artifact["cid"] = node_id_from_obj(artifact_body)
    payload["software_release_node"]["artifact_cids"] = [artifact["cid"]]
    release_body = {
        key: value
        for key, value in payload["software_release_node"].items()
        if key != "cid"
    }
    payload["software_release_node"]["cid"] = node_id_from_obj(release_body)
    edge = payload["release_attestation_edges"][0]
    edge["source"] = payload["software_release_node"]["cid"]
    edge["target"] = artifact["cid"]
    assertion_body = {key: value for key, value in payload.items() if key != "assertion_cid"}
    payload["assertion_cid"] = node_id_from_obj(assertion_body)
    monkeypatch.setattr(upgrade_check, "release_signer_public_key_hex", lambda: public_key_hex)

    result = upgrade_check.validate_release_assertion(payload)

    assert result["release_signature_verified"] is True
    assert result["artifact_cids"] == [artifact["cid"]]


def test_release_assertion_unknown_artifact_type_fails_closed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    private_key, public_key_hex = _release_keypair()
    payload = _release_assertion_payload(
        private_key=private_key,
        public_key_hex=public_key_hex,
    )
    payload["artifact_nodes"][0]["artifact_type"] = "unknown"
    monkeypatch.setattr(upgrade_check, "release_signer_public_key_hex", lambda: public_key_hex)

    with pytest.raises(upgrade_check.UpgradeCheckError) as excinfo:
        upgrade_check.validate_release_assertion(payload)

    assert excinfo.value.token == "upgrade_assertion_artifact_type_invalid"


def test_release_assertion_threshold_bls_signature_scheme_fails_closed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    private_key, public_key_hex = _release_keypair()
    payload = _release_assertion_payload(
        private_key=private_key,
        public_key_hex=public_key_hex,
        signature_scheme="threshold_bls_v1",
    )
    monkeypatch.setattr(upgrade_check, "release_signer_public_key_hex", lambda: public_key_hex)

    with pytest.raises(upgrade_check.UpgradeCheckError) as excinfo:
        upgrade_check.validate_release_assertion(payload)

    assert excinfo.value.token == "release_assertion_signature_scheme_not_active"


def test_release_assertion_unknown_signature_scheme_fails_closed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    private_key, public_key_hex = _release_keypair()
    payload = _release_assertion_payload(
        private_key=private_key,
        public_key_hex=public_key_hex,
        signature_scheme="unknown_scheme_xyz",
    )
    monkeypatch.setattr(upgrade_check, "release_signer_public_key_hex", lambda: public_key_hex)

    with pytest.raises(upgrade_check.UpgradeCheckError) as excinfo:
        upgrade_check.validate_release_assertion(payload)

    assert excinfo.value.token == "release_assertion_unknown_signature_scheme"


def test_release_assertion_mixed_active_signature_schemes_fail_closed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    private_key, public_key_hex = _release_keypair()
    first_payload = _release_assertion_payload(
        private_key=private_key,
        public_key_hex=public_key_hex,
        signature_scheme="ed25519_phase_1335",
    )
    second_payload = _release_assertion_payload(
        private_key=private_key,
        public_key_hex=public_key_hex,
        signature_scheme="test_active_scheme_v1",
    )
    first_payload["release_attestation_edges"].append(second_payload["release_attestation_edges"][0])
    monkeypatch.setattr(upgrade_check, "release_signer_public_key_hex", lambda: public_key_hex)
    monkeypatch.setattr(
        upgrade_check,
        "_ACTIVE_SIGNATURE_SCHEMES",
        frozenset({"ed25519_phase_1335", "test_active_scheme_v1"}),
    )
    monkeypatch.setattr(upgrade_check, "_verify_release_attestation_signature", lambda **_: None)
    monkeypatch.setattr(upgrade_check, "_require_all_artifacts_attested", lambda **_: None)

    with pytest.raises(upgrade_check.UpgradeCheckError) as excinfo:
        upgrade_check.validate_release_assertion(first_payload)

    assert excinfo.value.token == "release_assertion_signature_scheme_mismatch"


def test_release_assertion_rejects_unattested_artifact_cids(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    private_key, public_key_hex = _release_keypair()
    payload = _release_assertion_payload(private_key=private_key, public_key_hex=public_key_hex)
    extra_body = {
        **{key: value for key, value in payload["artifact_nodes"][0].items() if key != "cid"},
        "artifact_id": "ilc-artifact:ilc-core-python-sdist-0433@phase-1626",
        "artifact_type": "sdist",
        "filename": "ilc_core-0.4.33.tar.gz",
    }
    extra_node = {**extra_body, "cid": node_id_from_obj(extra_body)}
    payload["artifact_nodes"].append(extra_node)
    release_node = payload["software_release_node"]
    release_node["artifact_cids"].append(extra_node["cid"])
    release_body = {key: value for key, value in release_node.items() if key != "cid"}
    release_node["cid"] = node_id_from_obj(release_body)
    payload["release_attestation_edges"][0]["source"] = release_node["cid"]
    assertion_body = {key: value for key, value in payload.items() if key != "assertion_cid"}
    payload["assertion_cid"] = node_id_from_obj(assertion_body)
    monkeypatch.setattr(upgrade_check, "release_signer_public_key_hex", lambda: public_key_hex)

    with pytest.raises(upgrade_check.UpgradeCheckError) as excinfo:
        upgrade_check.validate_release_assertion(payload)

    assert excinfo.value.token == "upgrade_assertion_unattested_artifacts_present"


def test_release_assertion_active_but_undispatched_signature_scheme_fails_closed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    private_key, public_key_hex = _release_keypair()
    payload = _release_assertion_payload(
        private_key=private_key,
        public_key_hex=public_key_hex,
        signature_scheme="test_active_scheme_v1",
    )
    monkeypatch.setattr(upgrade_check, "release_signer_public_key_hex", lambda: public_key_hex)
    monkeypatch.setattr(
        upgrade_check,
        "_ACTIVE_SIGNATURE_SCHEMES",
        frozenset({"ed25519_phase_1335", "test_active_scheme_v1"}),
    )

    with pytest.raises(upgrade_check.UpgradeCheckError) as excinfo:
        upgrade_check.validate_release_assertion(payload)

    assert excinfo.value.token == "release_assertion_signature_scheme_not_dispatched"


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
        evaluation_runtime=upgrade_check.UpgradeEvaluationRuntime(
            installed_version_resolver=lambda: "0.4.32",
            now_fn=_fixed_now,
        ),
        state_path=tmp_path / "upgrade_state.json",
    )

    assert result["candidate_version_relation"] == "same"
    assert result["candidate_upgrade_available"] is False
    assert result["authorized_upgrade_available"] is False


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
            evaluation_runtime=upgrade_check.UpgradeEvaluationRuntime(
                installed_version_resolver=lambda: "0.4.32",
                now_fn=_fixed_now,
            ),
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
            evaluation_runtime=upgrade_check.UpgradeEvaluationRuntime(
                installed_version_resolver=lambda: "0.4.32",
                now_fn=_fixed_now,
            ),
            state_path=tmp_path / "upgrade_state.json",
        )

    assert excinfo.value.token == "upgrade_check_endpoint_unreachable"


def test_upgrade_check_rejects_insecure_endpoint(tmp_path: Path) -> None:
    with pytest.raises(upgrade_check.UpgradeCheckError) as excinfo:
        upgrade_check.check_for_upgrade(
            endpoint="http://example.test/latest.json",
            fetcher=lambda endpoint, timeout: {},
            evaluation_runtime=upgrade_check.UpgradeEvaluationRuntime(
                installed_version_resolver=lambda: "0.4.32",
                now_fn=_fixed_now,
            ),
            state_path=tmp_path / "upgrade_state.json",
        )

    assert excinfo.value.token == "upgrade_check_endpoint_insecure"


def test_upgrade_check_rejects_userinfo_in_explicit_endpoint(tmp_path: Path) -> None:
    with pytest.raises(upgrade_check.UpgradeCheckError) as excinfo:
        upgrade_check.check_for_upgrade(
            endpoint="https://user:pass@example.test/latest.json",
            fetcher=lambda endpoint, timeout: {},
            evaluation_runtime=upgrade_check.UpgradeEvaluationRuntime(
                installed_version_resolver=lambda: "0.4.32",
                now_fn=_fixed_now,
            ),
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
        evaluation_runtime=upgrade_check.UpgradeEvaluationRuntime(
            installed_version_resolver=lambda: "0.4",
            now_fn=_fixed_now,
        ),
        state_path=tmp_path / "upgrade_state.json",
    )

    assert result["candidate_version_relation"] == "same"
    assert result["candidate_upgrade_available"] is False
    assert result["authorized_upgrade_available"] is False


def test_upgrade_check_treats_unrecognized_installed_version_as_unknown(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    private_key, public_key_hex = _release_keypair()
    payload = _release_assertion_payload(private_key=private_key, public_key_hex=public_key_hex)
    monkeypatch.setattr(upgrade_check, "release_signer_public_key_hex", lambda: public_key_hex)

    result = upgrade_check.check_for_upgrade(
        endpoint="https://example.test/latest.json",
        fetcher=lambda endpoint, timeout: payload,
        evaluation_runtime=upgrade_check.UpgradeEvaluationRuntime(
            installed_version_resolver=lambda: "0.4.33.dev3",
            now_fn=_fixed_now,
        ),
        state_path=tmp_path / "upgrade_state.json",
    )

    assert result["installed_version"] == "0.4.33.dev3"
    assert result["candidate_version_relation"] == "unknown"
    assert result["candidate_upgrade_available"] is False
    assert result["authorized_upgrade_available"] is False


def test_no_redirect_handler_raises_stable_token() -> None:
    handler = upgrade_check._NoRedirectHandler()

    with pytest.raises(upgrade_check.UpgradeCheckError) as excinfo:
        handler.redirect_request(
            None,  # type: ignore[arg-type]
            None,
            302,
            "Found",
            {},
            "https://example.test/redirected.json",
        )

    assert excinfo.value.token == "upgrade_check_endpoint_redirect_forbidden"


def test_upgrade_state_read_rejects_oversized_file(tmp_path: Path) -> None:
    state_path = tmp_path / "upgrade_state.json"
    state_path.write_bytes(b"{" + (b" " * MAX_UPGRADE_STATE_BYTES) + b"}")

    with pytest.raises(ValueError) as excinfo:
        read_upgrade_state(state_path)

    assert str(excinfo.value) == "upgrade_state_corrupt"
