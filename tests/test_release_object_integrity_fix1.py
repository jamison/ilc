# SPDX-License-Identifier: AGPL-3.0-only
from __future__ import annotations

import hashlib
import json
import subprocess
from copy import deepcopy
from pathlib import Path

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from ilc_core.cli import upgrade_cli
from ilc_core.encoding.cidv1 import node_id_from_obj
from ilc_core.identity.bls_backend import keypair_from_ikm_hex, sign_native_submit_bytes
from ilc_core.release import artifact_fetch, upgrade_check
from ilc_core.release.current_policy import CurrentPolicyEvaluationInput
from ilc_core.release.installable_release_signature import (
    DEFAULT_GENESIS_LINEAGE_REF,
    DEFAULT_PRIOR_RELEASE_ENVELOPE_REF,
    DEFAULT_RELEASE_KEY_REGISTRATION_REF,
    SIGNED_PREIMAGE_DOMAIN,
    compute_signed_preimage_sha256,
)
from ilc_core.release.upgrade_state import MAX_UPGRADE_STATE_BYTES, write_upgrade_state
from ilc_core.storage.truth_primitive_graph_lmdb_adapter import TruthPrimitiveGraphStore


NETWORK_ID = "ilc-public-rc-01-testnet-harness"
WHEEL_BYTES = b"fixture wheel for Fix1"
BLS_SECRET_KEY_HEX, BLS_PUBLIC_KEY_HEX = keypair_from_ikm_hex("42" * 32)
OTHER_BLS_SECRET_KEY_HEX, OTHER_BLS_PUBLIC_KEY_HEX = keypair_from_ikm_hex("43" * 32)


class _Response:
    status_code = 200

    def __init__(self, body: bytes) -> None:
        self.body = body
        self.headers = {"Content-Length": str(len(body))}

    def iter_content(self, *, chunk_size: int):
        yield self.body

    def close(self) -> None:
        return None


def _canonical(value: dict) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("utf-8")


def _fixture_assertion(
    *,
    private_key: Ed25519PrivateKey,
    public_key_hex: str,
    version: str = "9.9.9",
    wheel_bytes: bytes = WHEEL_BYTES,
) -> dict:
    artifact_id = f"ilc-artifact:ilc-core-python-wheel-{version.replace('.', '')}@phase-9999"
    artifact_sha256 = hashlib.sha256(wheel_bytes).hexdigest()
    artifact_body = {
        "artifact_id": artifact_id,
        "artifact_type": "wheel",
        "filename": f"ilc_core-{version}-py3-none-any.whl",
        "node_kind": "ArtifactNode",
        "package_name": "ilc-core",
        "package_version": version,
        "pypi_url": "https://example.test/fixture.whl",
        "schema_version": "artifact_node.v0.1",
        "sha256": artifact_sha256,
        "size_bytes": len(wheel_bytes),
    }
    artifact_node = {**artifact_body, "cid": node_id_from_obj(artifact_body)}
    source_commit = "12" * 32
    recipe_body = {
        "build_command": "python -m build",
        "build_date": "2026-10-15T08:00:00Z",
        "build_env_hash": "23" * 32,
        "build_toolchain": "python-build",
        "builder_agent_id": "phase:GAP-RELEASE-OBJECT-CDL-RATIFY-00-FIX1",
        "node_kind": "BuildRecipeNode",
        "reproducibility_hash": "34" * 32,
        "schema_version": "build_recipe_node.v0.1",
        "source_commit": source_commit,
    }
    recipe_node = {**recipe_body, "cid": node_id_from_obj(recipe_body)}
    release_body = {
        "artifact_cids": [artifact_node["cid"]],
        "build_recipe_cid": recipe_node["cid"],
        "changelog_hash": "45" * 32,
        "node_kind": "SoftwareReleaseNode",
        "package_name": "ilc-core",
        "release_channel": "public_rc",
        "release_date": "2026-10-15T08:00:00Z",
        "release_key_pubkey": public_key_hex,
        "release_signature_ref": "fixture:fix1",
        "schema_version": "software_release_node.v0.1",
        "source_commit": source_commit,
        "version": version,
    }
    release_node = {**release_body, "cid": node_id_from_obj(release_body)}
    preimage = compute_signed_preimage_sha256(
        release_id=f"ilc-core-{version}",
        artifact_id=artifact_id,
        artifact_sha256=artifact_sha256,
    )
    edge = {
        "artifact_id": artifact_id,
        "artifact_sha256": artifact_sha256,
        "attestation_date": "2026-10-15T08:00:00Z",
        "edge_type": "RELEASE_ATTESTS_ARTIFACT",
        "genesis_lineage_ref": DEFAULT_GENESIS_LINEAGE_REF,
        "prior_release_envelope_ref": DEFAULT_PRIOR_RELEASE_ENVELOPE_REF,
        "release_key_registration_ref": DEFAULT_RELEASE_KEY_REGISTRATION_REF,
        "schema_version": "release_attestation_edge.v0.1",
        "signature_hex": private_key.sign(bytes.fromhex(preimage)).hex(),
        "signed_preimage_domain": SIGNED_PREIMAGE_DOMAIN,
        "signed_preimage_sha256": preimage,
        "signer_public_key_hex": public_key_hex,
        "signing_algorithm": "Ed25519",
        "source": release_node["cid"],
        "target": artifact_node["cid"],
    }
    body = {
        "artifact_nodes": [artifact_node],
        "build_recipe_nodes": [recipe_node],
        "release_attestation_edges": [edge],
        "schema_version": "software_release_assertion.v0.1",
        "software_release_node": release_node,
    }
    return {**body, "assertion_cid": node_id_from_obj(body)}


def _keypair() -> tuple[Ed25519PrivateKey, str]:
    private_key = Ed25519PrivateKey.generate()
    public_key = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    ).hex()
    return private_key, public_key


def _attach_native_envelope(
    assertion: dict,
    *,
    secret_key_hex: str = BLS_SECRET_KEY_HEX,
    public_key_hex: str = BLS_PUBLIC_KEY_HEX,
) -> dict:
    result = deepcopy(assertion)
    envelope = {
        "v": 1,
        "primitive": "assert.truth",
        "agent_id": public_key_hex,
        "epoch": 7,
        "payload": {
            "content": {
                "phase": "GAP-RELEASE-OBJECT-CDL-RATIFY-00-FIX1-fixture",
                "software_release_assertion": deepcopy(assertion),
            },
            "primitive_type": "observation",
            "epistemic_type": "objective",
            "parent_node_ids": [],
        },
    }
    canonical = _canonical(envelope)
    envelope["sig"] = {
        "schema_version": "native_submit_sig.v0.1",
        "verifier_profile": "native_submit_sig_profile.v0.1",
        "dst": f"ILC_NATIVE_TRUTH_SUBMIT_V1:{NETWORK_ID}",
        "payload_sha256": hashlib.sha256(canonical).hexdigest(),
        "signature_hex": sign_native_submit_bytes(secret_key_hex, canonical, NETWORK_ID),
        "key_ref": public_key_hex,
    }
    result["native_submit_envelope"] = envelope
    return result


def _delegation_resolver(context: dict) -> dict:
    return {
        **context,
        "status": "verified_valid_at_submission",
        "valid_at_submission": True,
        "policy_ref": "fixture:direct-release-submit-delegation",
        "mldsa_evidence_verified": True,
        "revocation_resolver_available": True,
        "revoked_at_submission": False,
    }


def _current_policy_input(payload: dict, **changes: object) -> CurrentPolicyEvaluationInput:
    release_node = payload["software_release_node"]
    values: dict[str, object] = {
        "release_assertion_cid": upgrade_check._verify_assertion_cid(payload),
        "software_release_cid": release_node["cid"],
        "artifact_cids": tuple(release_node["artifact_cids"]),
        "network_id": NETWORK_ID,
        "channel": "public_rc",
        "policy_id": "ilc-public-rc-current-policy-v1",
        "policy_public_key_hex": "00" * 1952,
        "policy_claims": (),
        "authoritative_policy_head_cid": release_node["cid"],
        "authoritative_validation_epoch": 0,
        "observer_validation_epoch": 0,
        "observer_highest_seen_sequence": 0,
        "bootstrap_policy_head_cid": release_node["cid"],
        "bootstrap_binding_evidence_cid": release_node["cid"],
        "bootstrap_binding_bundle_json": b"{}",
    }
    values.update(changes)
    return CurrentPolicyEvaluationInput(**values)  # type: ignore[arg-type]


def _opaque_policy_input() -> CurrentPolicyEvaluationInput:
    """Typed placeholder for tests that replace the policy verifier itself."""

    return CurrentPolicyEvaluationInput(
        release_assertion_cid="fixture-assertion",
        software_release_cid="fixture-release",
        artifact_cids=("fixture-artifact",),
        network_id=NETWORK_ID,
        channel="public_rc",
        policy_id="fixture-policy",
        policy_public_key_hex="00",
        policy_claims=(),
        authoritative_policy_head_cid="fixture-head",
        authoritative_validation_epoch=0,
        observer_validation_epoch=0,
        observer_highest_seen_sequence=0,
        bootstrap_policy_head_cid="fixture-head",
        bootstrap_binding_evidence_cid="fixture-binding",
        bootstrap_binding_bundle_json=b"{}",
    )


def test_fixture_composed_path_binds_all_layers(monkeypatch: pytest.MonkeyPatch) -> None:
    private_key, public_key = _keypair()
    payload = _attach_native_envelope(
        _fixture_assertion(private_key=private_key, public_key_hex=public_key)
    )
    monkeypatch.setattr(upgrade_check, "release_signer_public_key_hex", lambda: public_key)

    result = upgrade_check.validate_release_assertion(
        payload,
        delegation_policy_resolver=_delegation_resolver,
        current_policy_evaluation_input=_current_policy_input(payload),
    )

    assert result["artifact_release_authority_verified"] is True
    assert result["graph_submission_provenance_verified"] is True
    assert result["graph_provenance_delegation_valid_at_submission"] is True
    assert result["full_release_graph_binding_verified"] is True
    assert result["current_release_eligibility_status"] == "unresolved"
    with pytest.raises(upgrade_check.UpgradeCheckError, match="arbitrary_source_current"):
        upgrade_check.require_arbitrary_source_release_authorized(result)


def test_cross_spliced_native_assertion_core_is_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    private_key, public_key = _keypair()
    first = _fixture_assertion(private_key=private_key, public_key_hex=public_key, version="9.9.8")
    second = _fixture_assertion(private_key=private_key, public_key_hex=public_key, version="9.9.9")
    payload = _attach_native_envelope(first)
    payload.update(second)
    monkeypatch.setattr(upgrade_check, "release_signer_public_key_hex", lambda: public_key)

    with pytest.raises(upgrade_check.UpgradeCheckError) as exc:
        upgrade_check.validate_release_assertion(payload)

    assert exc.value.token == "release_graph_provenance_assertion_core_mismatch"


def test_current_policy_receipt_cannot_cross_bind_artifacts(monkeypatch: pytest.MonkeyPatch) -> None:
    private_key, public_key = _keypair()
    payload = _attach_native_envelope(
        _fixture_assertion(private_key=private_key, public_key_hex=public_key)
    )
    monkeypatch.setattr(upgrade_check, "release_signer_public_key_hex", lambda: public_key)

    with pytest.raises(upgrade_check.UpgradeCheckError) as exc:
        upgrade_check.validate_release_assertion(
            payload,
            current_policy_evaluation_input=_current_policy_input(
                payload, artifact_cids=(node_id_from_obj({"wrong": "artifact"}),)
            ),
        )

    assert exc.value.token == "release_current_policy_artifacts_mismatch"


@pytest.mark.parametrize(
    ("field", "value", "token"),
    [
        ("mldsa_evidence_verified", False, "release_graph_delegation_mldsa_unverified"),
        (
            "revocation_resolver_available",
            False,
            "release_graph_delegation_revocation_unavailable",
        ),
        ("revoked_at_submission", True, "release_graph_delegation_revoked_at_submission"),
    ],
)
def test_delegation_positive_result_requires_full_historical_evidence(
    monkeypatch: pytest.MonkeyPatch,
    field: str,
    value: object,
    token: str,
) -> None:
    private_key, public_key = _keypair()
    payload = _attach_native_envelope(
        _fixture_assertion(private_key=private_key, public_key_hex=public_key)
    )
    monkeypatch.setattr(upgrade_check, "release_signer_public_key_hex", lambda: public_key)

    def resolver(context: dict) -> dict:
        result = _delegation_resolver(context)
        result[field] = value
        return result

    with pytest.raises(upgrade_check.UpgradeCheckError) as exc:
        upgrade_check.validate_release_assertion(payload, delegation_policy_resolver=resolver)

    assert exc.value.token == token


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("key_ref", "aa" * 48),
        ("network_id", "wrong-network"),
        ("epoch", 8),
    ],
)
def test_delegation_evidence_must_bind_exact_envelope_context(
    monkeypatch: pytest.MonkeyPatch,
    field: str,
    value: object,
) -> None:
    private_key, public_key = _keypair()
    payload = _attach_native_envelope(
        _fixture_assertion(private_key=private_key, public_key_hex=public_key)
    )
    monkeypatch.setattr(upgrade_check, "release_signer_public_key_hex", lambda: public_key)

    def resolver(context: dict) -> dict:
        result = _delegation_resolver(context)
        result[field] = value
        return result

    with pytest.raises(upgrade_check.UpgradeCheckError) as exc:
        upgrade_check.validate_release_assertion(payload, delegation_policy_resolver=resolver)

    assert exc.value.token == "release_graph_delegation_evidence_mismatch"


def test_core_only_cannot_claim_verified_current_policy(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    private_key, public_key = _keypair()
    payload = _fixture_assertion(private_key=private_key, public_key_hex=public_key)
    monkeypatch.setattr(upgrade_check, "release_signer_public_key_hex", lambda: public_key)

    result = upgrade_check.validate_release_assertion(
        payload,
        current_policy_evaluation_input=_current_policy_input(payload),
    )
    assert result["artifact_release_authority_verified"] is True
    assert result["current_release_eligibility_status"] == "unresolved"


def test_ceremony_envelope_full_binding_without_role_policy() -> None:
    live_core = json.loads(
        Path("out/gap_release_assertion_publish_ceremony_00/release_assertion_core.json").read_text()
    )
    live_envelope = json.loads(
        Path("out/gap_release_assertion_publish_ceremony_00/native_submit_envelope.json").read_text()
    )
    core_result = upgrade_check.validate_release_assertion(live_core)
    assert core_result["artifact_release_authority_verified"] is True
    assert core_result["graph_submission_provenance_verified"] is False
    assert core_result["full_release_graph_binding_verified"] is False

    live_core["native_submit_envelope"] = live_envelope
    composed = upgrade_check.validate_release_assertion(live_core)
    assert composed["graph_submission_provenance_verified"] is True
    assert composed["graph_provenance_delegation_valid_at_submission"] is False
    assert composed["graph_provenance_delegation_status"] == (
        "graph_submitter_policy_not_evaluated_permissionless_ingress"
    )
    assert "required_role" not in composed["graph_provenance_delegation_evidence"]
    assert composed["full_release_graph_binding_verified"] is True


def test_non_genesis_valid_cdl118_submitter_can_full_bind(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    private_key, public_key = _keypair()
    payload = _attach_native_envelope(
        _fixture_assertion(private_key=private_key, public_key_hex=public_key),
        secret_key_hex=OTHER_BLS_SECRET_KEY_HEX,
        public_key_hex=OTHER_BLS_PUBLIC_KEY_HEX,
    )
    monkeypatch.setattr(upgrade_check, "release_signer_public_key_hex", lambda: public_key)

    result = upgrade_check.validate_release_assertion(payload)

    assert result["artifact_release_authority_verified"] is True
    assert result["graph_submission_provenance_verified"] is True
    assert result["graph_provenance_delegation_valid_at_submission"] is False
    assert result["graph_provenance_delegation_status"] == (
        "graph_submitter_policy_not_evaluated_permissionless_ingress"
    )
    assert result["full_release_graph_binding_verified"] is True


def test_negative_optional_submitter_policy_does_not_gate_full_binding(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    private_key, public_key = _keypair()
    payload = _attach_native_envelope(
        _fixture_assertion(private_key=private_key, public_key_hex=public_key)
    )
    monkeypatch.setattr(upgrade_check, "release_signer_public_key_hex", lambda: public_key)

    def negative_policy(context: dict) -> dict:
        return {
            **context,
            "status": "supplemental_policy_not_satisfied",
            "valid_at_submission": False,
        }

    result = upgrade_check.validate_release_assertion(
        payload,
        delegation_policy_resolver=negative_policy,
    )

    assert result["graph_provenance_delegation_valid_at_submission"] is False
    assert result["graph_provenance_delegation_status"] == (
        "supplemental_policy_not_satisfied"
    )
    assert result["full_release_graph_binding_verified"] is True


def test_core_only_assertion_does_not_full_bind(monkeypatch: pytest.MonkeyPatch) -> None:
    private_key, public_key = _keypair()
    payload = _fixture_assertion(private_key=private_key, public_key_hex=public_key)
    monkeypatch.setattr(upgrade_check, "release_signer_public_key_hex", lambda: public_key)

    result = upgrade_check.validate_release_assertion(payload)

    assert result["artifact_release_authority_verified"] is True
    assert result["graph_submission_provenance_verified"] is False
    assert result["full_release_graph_binding_verified"] is False


def test_invalid_native_envelope_fails_closed(monkeypatch: pytest.MonkeyPatch) -> None:
    private_key, public_key = _keypair()
    payload = _attach_native_envelope(
        _fixture_assertion(private_key=private_key, public_key_hex=public_key)
    )
    payload["native_submit_envelope"]["sig"]["signature_hex"] = "00" * 96
    monkeypatch.setattr(upgrade_check, "release_signer_public_key_hex", lambda: public_key)

    with pytest.raises(upgrade_check.UpgradeCheckError) as exc:
        upgrade_check.validate_release_assertion(payload)

    assert exc.value.token == "release_graph_provenance_bls_verify_failed"


def test_current_policy_still_required_for_arbitrary_source(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    private_key, public_key = _keypair()
    payload = _attach_native_envelope(
        _fixture_assertion(private_key=private_key, public_key_hex=public_key)
    )
    monkeypatch.setattr(upgrade_check, "release_signer_public_key_hex", lambda: public_key)

    result = upgrade_check.validate_release_assertion(payload)

    assert result["full_release_graph_binding_verified"] is True
    assert result["current_release_eligibility_status"] == "unresolved"
    with pytest.raises(upgrade_check.UpgradeCheckError) as exc:
        upgrade_check.require_arbitrary_source_release_authorized(result)
    assert exc.value.token == "arbitrary_source_current_release_eligibility_required"


def test_graph_store_reconstructs_only_complete_verified_envelope(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    private_key, public_key = _keypair()
    assertion = _fixture_assertion(private_key=private_key, public_key_hex=public_key)
    payload = _attach_native_envelope(assertion)
    envelope = payload["native_submit_envelope"]
    monkeypatch.setattr(upgrade_check, "release_signer_public_key_hex", lambda: public_key)
    store = TruthPrimitiveGraphStore(tmp_path / "graph.lmdb")
    try:
        store.put_node_if_absent(
            "complete",
            {
                "v": envelope["v"],
                "primitive": envelope["primitive"],
                "agent_id": envelope["agent_id"],
                "epoch": envelope["epoch"],
                "payload": envelope["payload"],
                "native_submit_sig": envelope["sig"],
            },
        )
        observed = store.get_latest_release_assertion("public_rc")
    finally:
        store.close()

    assert observed is not None
    assert observed["native_submit_envelope"] == envelope


def test_composed_graph_remains_blocked_until_policy_activation(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    private_key, public_key = _keypair()
    assertion = _fixture_assertion(private_key=private_key, public_key_hex=public_key)
    payload = _attach_native_envelope(assertion)
    envelope = payload["native_submit_envelope"]
    monkeypatch.setattr(upgrade_check, "release_signer_public_key_hex", lambda: public_key)
    store = TruthPrimitiveGraphStore(tmp_path / "composed.lmdb")
    try:
        store.put_node_if_absent(
            "composed",
            {
                "v": envelope["v"],
                "primitive": envelope["primitive"],
                "agent_id": envelope["agent_id"],
                "epoch": envelope["epoch"],
                "payload": envelope["payload"],
                "native_submit_sig": envelope["sig"],
            },
        )
        observed = store.get_latest_release_assertion("public_rc")
    finally:
        store.close()
    assert observed is not None

    validation = upgrade_check.validate_release_assertion(
        observed,
        delegation_policy_resolver=_delegation_resolver,
        current_policy_evaluation_input=_current_policy_input(observed),
    )
    assert validation["current_release_eligibility_status"] == "unresolved"
    with pytest.raises(upgrade_check.UpgradeCheckError) as exc:
        upgrade_check.require_arbitrary_source_release_authorized(validation)
    assert exc.value.token == "arbitrary_source_current_release_eligibility_required"


def test_graph_candidate_overflow_fails_closed(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    private_key, public_key = _keypair()
    monkeypatch.setattr(upgrade_check, "release_signer_public_key_hex", lambda: public_key)
    monkeypatch.setattr(
        "ilc_core.storage.truth_primitive_graph_lmdb_adapter.MAX_RELEASE_ASSERTION_CANDIDATES",
        1,
    )
    first = _fixture_assertion(
        private_key=private_key,
        public_key_hex=public_key,
        version="9.9.8",
    )
    second = _fixture_assertion(
        private_key=private_key,
        public_key_hex=public_key,
        version="9.9.9",
    )
    store = TruthPrimitiveGraphStore(tmp_path / "overflow.lmdb")
    try:
        store.put_node_if_absent("first", first)
        store.put_node_if_absent("second", second)
        observed = store.get_latest_release_assertion("public_rc")
    finally:
        store.close()

    assert observed is None


def test_absolute_size_and_free_space_guards_run_before_network(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    artifact_body = {
        "artifact_type": "wheel",
        "filename": "fixture.whl",
        "package_name": "ilc-core",
        "package_version": "9.9.9",
        "pypi_url": "https://example.test/fixture.whl",
        "sha256": "00" * 32,
        "size_bytes": artifact_fetch.MAX_ARTIFACT_DOWNLOAD_BYTES + 1,
    }
    artifact = {**artifact_body, "cid": node_id_from_obj(artifact_body)}
    payload = {
        "artifact_nodes": [artifact],
        "release_attestation_edges": [
            {"target": artifact["cid"], "artifact_sha256": artifact["sha256"]}
        ],
        "software_release_node": {"package_name": "ilc-core", "version": "9.9.9"},
    }
    monkeypatch.setattr(
        artifact_fetch,
        "validate_release_assertion",
        lambda payload, **kwargs: {
            "package_name": "ilc-core",
            "available_version": "9.9.9",
            "full_release_graph_binding_verified": True,
            "current_release_eligibility_status": "verified_current_policy",
        },
    )
    called = False

    def should_not_fetch(*args, **kwargs):
        nonlocal called
        called = True

    monkeypatch.setattr(artifact_fetch.requests, "get", should_not_fetch)
    with pytest.raises(artifact_fetch.ArtifactFetchError) as exc:
        artifact_fetch.fetch_and_verify(
            payload,
            policy_evaluation_input=_opaque_policy_input(),
        )
    assert exc.value.token == "artifact_fetch_size_exceeds_absolute_max"
    assert called is False


def test_insufficient_free_space_fails_before_temp_creation_or_network(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    private_key, public_key = _keypair()
    payload = _fixture_assertion(private_key=private_key, public_key_hex=public_key)
    monkeypatch.setattr(upgrade_check, "release_signer_public_key_hex", lambda: public_key)
    monkeypatch.setattr(
        artifact_fetch.shutil,
        "disk_usage",
        lambda _: type("Usage", (), {"free": 0})(),
    )
    monkeypatch.setattr(
        artifact_fetch.tempfile,
        "mkdtemp",
        lambda **_: pytest.fail("temporary directory created before free-space gate"),
    )
    monkeypatch.setattr(
        artifact_fetch.requests,
        "get",
        lambda *_, **__: pytest.fail("network called before free-space gate"),
    )
    monkeypatch.setattr(
        artifact_fetch,
        "validate_release_assertion",
        lambda payload, **kwargs: {
            "package_name": "ilc-core",
            "available_version": "9.9.9",
            "full_release_graph_binding_verified": True,
            "current_release_eligibility_status": "verified_current_policy",
        },
    )

    with pytest.raises(artifact_fetch.ArtifactFetchError) as exc:
        artifact_fetch.fetch_and_verify(
            payload,
            policy_evaluation_input=_current_policy_input(payload),
        )

    assert exc.value.token == "artifact_fetch_insufficient_free_space"


@pytest.mark.parametrize(
    ("returncode", "token"),
    [
        (21, "upgrade_apply_installed_version_mismatch"),
        (22, "upgrade_apply_post_install_import_failed"),
        (1, "upgrade_apply_post_install_import_failed"),
    ],
)
def test_post_install_child_verification_failures_are_tokenized(
    monkeypatch: pytest.MonkeyPatch,
    returncode: int,
    token: str,
) -> None:
    def fail(args, *, check, timeout):
        raise subprocess.CalledProcessError(returncode, args)

    monkeypatch.setattr(upgrade_cli.subprocess, "run", fail)

    with pytest.raises(upgrade_cli.UpgradeCliError) as exc:
        upgrade_cli._verify_installed_release("9.9.9")

    assert exc.value.token == token


def test_present_policy_rejection_blocks_apply_without_rewriting_history(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    private_key, public_key = _keypair()
    payload = _attach_native_envelope(
        _fixture_assertion(private_key=private_key, public_key_hex=public_key)
    )
    monkeypatch.setattr(upgrade_check, "release_signer_public_key_hex", lambda: public_key)
    historical = upgrade_check.validate_release_assertion(
        payload,
        delegation_policy_resolver=_delegation_resolver,
    )
    assert historical["artifact_release_authority_verified"] is True
    assert historical["full_release_graph_binding_verified"] is True

    monkeypatch.setattr(
        upgrade_cli,
        "check_for_upgrade",
        lambda **_: {
            "available_version": "9.9.9",
            "release_assertion_payload": payload,
            "authorized_upgrade_available": False,
            "current_release_eligibility_status": "rejected_by_current_policy",
        },
    )
    monkeypatch.setattr(
        upgrade_cli,
        "_load_apply_policy_input",
        lambda **_: _current_policy_input(payload),
    )
    with pytest.raises(upgrade_cli.UpgradeCliError) as exc:
        upgrade_cli.run_upgrade_command(
            type(
                "Args",
                (),
                {
                    "upgrade_subcommand": "apply",
                    "endpoint": "",
                    "state_path": str(tmp_path / "state.json"),
                    "dry_run": True,
                },
            )()
        )

    assert exc.value.token == "upgrade_apply_release_rejected_current_policy"
    assert historical["artifact_release_authority_verified"] is True
    assert historical["full_release_graph_binding_verified"] is True


def test_upgrade_state_writer_rejects_oversize_before_temp_creation(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="upgrade_state_payload_too_large"):
        write_upgrade_state(
            {"padding": "x" * (MAX_UPGRADE_STATE_BYTES + 1)},
            path=tmp_path / "state.json",
        )
    assert not (tmp_path / "state.json").exists()


def test_watcher_retries_transient_but_fails_closed_on_permanent(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    sleeps: list[int] = []
    attempts = 0

    def transient_then_ok(**kwargs):
        nonlocal attempts
        attempts += 1
        if attempts == 1:
            raise upgrade_check.UpgradeCheckError("upgrade_check_endpoint_unreachable")
        return {
            "checked_at_utc": "2026-10-15T08:00:00Z",
            "candidate_upgrade_available": False,
        }

    result = upgrade_cli._run_watch_loop(
        endpoint=None,
        state_path=tmp_path / "state.json",
        interval_seconds=60,
        daemon=False,
        sleep_fn=sleeps.append,
        check_fn=transient_then_ok,
        max_cycles=2,
    )
    assert result["cycles"] == 2
    assert sleeps == [1]

    with pytest.raises(upgrade_check.UpgradeCheckError):
        upgrade_cli._run_watch_loop(
            endpoint=None,
            state_path=tmp_path / "state2.json",
            interval_seconds=60,
            daemon=False,
            sleep_fn=sleeps.append,
            check_fn=lambda **_: (_ for _ in ()).throw(
                upgrade_check.UpgradeCheckError("upgrade_assertion_unknown_field")
            ),
            max_cycles=1,
        )
