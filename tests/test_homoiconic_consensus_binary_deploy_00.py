from __future__ import annotations

import fcntl
import hashlib
import io
import os
import stat
import tarfile
from pathlib import Path

import pytest

from ilc_core.encoding.cidv1 import node_id_from_obj
from ilc_core.release import artifact_fetch, consensus_binary_deploy as deploy
from ilc_core.release.consensus_binary_deploy import (
    CONSENSUS_BINARY_DEPLOY_LOCK,
    CONSENSUS_BINARY_MEMBERS,
    ConsensusBinaryDeployError,
    VerifiedConsensusBinaryBundle,
    deploy_verified_consensus_binary_bundle,
    fetch_verified_consensus_binary_bundle,
    fetch_verify_and_deploy_consensus_binary_bundle,
)
from ilc_core.release.current_policy import CurrentPolicyEvaluationInput
from ilc_core.release.upgrade_check import UpgradeCheckError


POLICY_INPUT = CurrentPolicyEvaluationInput(
    release_assertion_cid="fixture-assertion",
    software_release_cid="fixture-release",
    artifact_cids=("fixture-artifact",),
    network_id="fixture-network",
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


class FakeResponse:
    def __init__(self, body: bytes, status_code: int = 200) -> None:
        self.body = body
        self.status_code = status_code
        self.headers = {"Content-Length": str(len(body))}

    def iter_content(self, *, chunk_size: int):
        for index in range(0, len(self.body), chunk_size):
            yield self.body[index : index + chunk_size]

    def close(self) -> None:
        return None


def _regular_tar_bytes(
    overrides: dict[str, bytes] | None = None,
    *,
    omitted: set[str] | None = None,
    extra: dict[str, bytes] | None = None,
    duplicate: str | None = None,
    special: tuple[str, bytes] | None = None,
) -> bytes:
    buffer = io.BytesIO()
    override_values = overrides or {}
    omitted_values = omitted or set()
    with tarfile.open(fileobj=buffer, mode="w:gz", format=tarfile.PAX_FORMAT) as archive:
        for name in CONSENSUS_BINARY_MEMBERS:
            if name in omitted_values:
                continue
            payload = override_values.get(name, f"binary:{name}".encode("ascii"))
            info = tarfile.TarInfo(name)
            info.size = len(payload)
            info.mode = 0o600
            info.mtime = 0
            archive.addfile(info, io.BytesIO(payload))
        for name, payload in (extra or {}).items():
            info = tarfile.TarInfo(name)
            info.size = len(payload)
            info.mtime = 0
            archive.addfile(info, io.BytesIO(payload))
        if duplicate is not None:
            payload = b"duplicate"
            info = tarfile.TarInfo(duplicate)
            info.size = len(payload)
            info.mtime = 0
            archive.addfile(info, io.BytesIO(payload))
        if special is not None:
            name, member_type = special
            # The regular entry with this name must be omitted by the caller.
            info = tarfile.TarInfo(name)
            info.type = member_type
            info.linkname = CONSENSUS_BINARY_MEMBERS[0]
            info.mtime = 0
            archive.addfile(info)
    return buffer.getvalue()


def _assertion(tar_bytes: bytes) -> dict[str, object]:
    body = {
        "artifact_id": "ilc-artifact:consensus-linux-x86_64@fixture",
        "artifact_type": "binary_tarball",
        "filename": "ilc-consensus-linux-x86_64.tar.gz",
        "node_kind": "ArtifactNode",
        "package_name": "ilc-consensus",
        "package_version": "9.9.9",
        "pypi_url": "https://example.test/ilc-consensus.tar.gz",
        "schema_version": "artifact_node.v0.1",
        "sha256": hashlib.sha256(tar_bytes).hexdigest(),
        "size_bytes": len(tar_bytes),
    }
    node = {**body, "cid": node_id_from_obj(body)}
    return {
        "artifact_nodes": [node],
        "release_attestation_edges": [
            {"artifact_sha256": node["sha256"], "target": node["cid"]}
        ],
        "software_release_node": {
            "artifact_cids": [node["cid"]],
            "package_name": "ilc-core",
            "version": "9.9.9",
        },
    }


def _authorize(monkeypatch: pytest.MonkeyPatch, body: bytes) -> None:
    validation = {
        "full_release_graph_binding_verified": True,
        "current_release_eligibility_status": "verified_current_policy",
    }
    monkeypatch.setattr(
        artifact_fetch,
        "validate_release_assertion",
        lambda *args, **kwargs: dict(validation),
    )
    monkeypatch.setattr(
        deploy,
        "validate_release_assertion",
        lambda *args, **kwargs: dict(validation),
    )
    monkeypatch.setattr(
        artifact_fetch.requests,
        "get",
        lambda *args, **kwargs: FakeResponse(body),
    )


def _bundle(monkeypatch: pytest.MonkeyPatch, body: bytes):
    _authorize(monkeypatch, body)
    return fetch_verified_consensus_binary_bundle(
        _assertion(body),
        policy_evaluation_input=POLICY_INPUT,
    )


def _cleanup_bundle(bundle) -> None:
    import shutil

    shutil.rmtree(bundle.path.parent, ignore_errors=True)


def _deploy(bundle, install_dir: Path):
    return deploy_verified_consensus_binary_bundle(
        bundle,
        release_assertion=_assertion(bundle.path.read_bytes()),
        policy_evaluation_input=POLICY_INPUT,
        install_dir=install_dir,
    )


def test_happy_path_installs_exact_members_without_execution(monkeypatch, tmp_path):
    body = _regular_tar_bytes()
    _authorize(monkeypatch, body)
    install_dir = tmp_path / "bin"

    receipt = fetch_verify_and_deploy_consensus_binary_bundle(
        _assertion(body),
        policy_evaluation_input=POLICY_INPUT,
        install_dir=install_dir,
    )

    assert receipt["deployment_status"] == "installed_not_executed"
    assert receipt["no_helper_executed"] is True
    assert receipt["economic_mutation"] is False
    assert receipt["serving_receipt_written"] is False
    assert receipt["backup_cleanup_status"] == "cleanup_complete"
    assert tuple(receipt["installed_members"]) == CONSENSUS_BINARY_MEMBERS
    for name in CONSENSUS_BINARY_MEMBERS:
        path = install_dir / name
        assert path.read_bytes() == f"binary:{name}".encode("ascii")
        assert stat.S_IMODE(path.stat().st_mode) == 0o755


def test_missing_policy_precedes_artifact_selection_allocation_and_network(monkeypatch):
    calls: list[str] = []
    monkeypatch.setattr(
        artifact_fetch.requests,
        "get",
        lambda *args, **kwargs: calls.append("network"),
    )
    monkeypatch.setattr(
        artifact_fetch.tempfile,
        "mkdtemp",
        lambda *args, **kwargs: calls.append("allocation"),
    )

    with pytest.raises(artifact_fetch.ArtifactFetchError) as exc:
        fetch_verified_consensus_binary_bundle(
            {"artifact_nodes": "malformed"},
            policy_evaluation_input=None,
        )

    assert exc.value.token == "artifact_fetch_eligibility_unresolved"
    assert calls == []


def test_rejected_policy_precedes_network(monkeypatch):
    calls: list[str] = []
    monkeypatch.setattr(
        artifact_fetch,
        "validate_release_assertion",
        lambda *args, **kwargs: (_ for _ in ()).throw(
            UpgradeCheckError("fixture_policy_rejected")
        ),
    )
    monkeypatch.setattr(
        artifact_fetch.requests,
        "get",
        lambda *args, **kwargs: calls.append("network"),
    )

    with pytest.raises(artifact_fetch.ArtifactFetchError) as exc:
        fetch_verified_consensus_binary_bundle(
            _assertion(_regular_tar_bytes()),
            policy_evaluation_input=POLICY_INPUT,
        )

    assert exc.value.token == "artifact_fetch_eligibility_gate_failed"
    assert calls == []


def test_policy_is_rechecked_before_local_target_mutation(monkeypatch, tmp_path):
    body = _regular_tar_bytes()
    bundle = _bundle(monkeypatch, body)
    install_dir = tmp_path / "bin"
    monkeypatch.setattr(
        deploy,
        "validate_release_assertion",
        lambda *args, **kwargs: (_ for _ in ()).throw(
            UpgradeCheckError("fixture_policy_replaced")
        ),
    )
    try:
        with pytest.raises(ConsensusBinaryDeployError) as exc:
            deploy_verified_consensus_binary_bundle(
                bundle,
                release_assertion=_assertion(body),
                policy_evaluation_input=POLICY_INPUT,
                install_dir=install_dir,
            )
        assert exc.value.token == "consensus_binary_deploy_eligibility_gate_failed"
        assert not install_dir.exists()
    finally:
        _cleanup_bundle(bundle)


def test_bundle_must_match_revalidated_release(monkeypatch, tmp_path):
    body = _regular_tar_bytes()
    bundle = _bundle(monkeypatch, body)
    different = _regular_tar_bytes(
        overrides={CONSENSUS_BINARY_MEMBERS[0]: b"different"}
    )
    try:
        with pytest.raises(ConsensusBinaryDeployError) as exc:
            deploy_verified_consensus_binary_bundle(
                bundle,
                release_assertion=_assertion(different),
                policy_evaluation_input=POLICY_INPUT,
                install_dir=tmp_path / "bin",
            )
        assert exc.value.token == "consensus_binary_bundle_release_mismatch"
        assert not (tmp_path / "bin").exists()
    finally:
        _cleanup_bundle(bundle)


def test_missing_and_duplicate_binary_artifacts_reject(monkeypatch):
    body = _regular_tar_bytes()
    _authorize(monkeypatch, body)
    missing = _assertion(body)
    missing["artifact_nodes"] = []
    with pytest.raises(artifact_fetch.ArtifactFetchError) as exc:
        fetch_verified_consensus_binary_bundle(
            missing,
            policy_evaluation_input=POLICY_INPUT,
        )
    assert exc.value.token == "artifact_fetch_artifact_nodes_missing"

    duplicate = _assertion(body)
    duplicate["artifact_nodes"] = duplicate["artifact_nodes"] * 2
    with pytest.raises(artifact_fetch.ArtifactFetchError) as exc:
        fetch_verified_consensus_binary_bundle(
            duplicate,
            policy_evaluation_input=POLICY_INPUT,
        )
    assert exc.value.token == "artifact_fetch_multiple_binary_tarballs"


@pytest.mark.parametrize(
    ("mutation", "token"),
    [
        ("cid", "artifact_fetch_artifact_cid_mismatch"),
        ("attestation", "artifact_fetch_artifact_not_attested"),
        ("filename", "artifact_fetch_filename_invalid"),
        ("url", "artifact_fetch_source_url_invalid"),
    ],
)
def test_binary_artifact_metadata_guards(monkeypatch, mutation, token):
    body = _regular_tar_bytes()
    payload = _assertion(body)
    node = payload["artifact_nodes"][0]
    if mutation == "cid":
        node["cid"] = node_id_from_obj({"different": "artifact"})
        payload["release_attestation_edges"][0]["target"] = node["cid"]
    elif mutation == "attestation":
        payload["release_attestation_edges"] = []
    elif mutation == "filename":
        node["filename"] = "../consensus.tar.gz"
        artifact_body = {key: value for key, value in node.items() if key != "cid"}
        node["cid"] = node_id_from_obj(artifact_body)
        payload["release_attestation_edges"][0]["target"] = node["cid"]
    else:
        node["pypi_url"] = "http://example.test/consensus.tar.gz"
        artifact_body = {key: value for key, value in node.items() if key != "cid"}
        node["cid"] = node_id_from_obj(artifact_body)
        payload["release_attestation_edges"][0]["target"] = node["cid"]
    _authorize(monkeypatch, body)
    with pytest.raises(artifact_fetch.ArtifactFetchError) as exc:
        fetch_verified_consensus_binary_bundle(
            payload,
            policy_evaluation_input=POLICY_INPUT,
        )
    assert exc.value.token == token


@pytest.mark.parametrize(
    "member_type",
    [tarfile.SYMTYPE, tarfile.LNKTYPE, tarfile.DIRTYPE, tarfile.CHRTYPE, tarfile.FIFOTYPE],
)
def test_special_archive_member_types_reject(monkeypatch, tmp_path, member_type):
    name = CONSENSUS_BINARY_MEMBERS[-1]
    body = _regular_tar_bytes(omitted={name}, special=(name, member_type))
    bundle = _bundle(monkeypatch, body)
    try:
        with pytest.raises(ConsensusBinaryDeployError) as exc:
            _deploy(bundle, tmp_path / "bin")
        assert exc.value.token == "consensus_binary_archive_member_type_invalid"
    finally:
        _cleanup_bundle(bundle)


@pytest.mark.parametrize(
    ("body", "token"),
    [
        (
            _regular_tar_bytes(omitted={CONSENSUS_BINARY_MEMBERS[-1]}),
            "consensus_binary_archive_members_invalid",
        ),
        (
            _regular_tar_bytes(extra={"unexpected": b"x"}),
            "consensus_binary_archive_member_count_invalid",
        ),
        (
            _regular_tar_bytes(duplicate=CONSENSUS_BINARY_MEMBERS[0]),
            "consensus_binary_archive_member_count_invalid",
        ),
        (
            _regular_tar_bytes(
                omitted={CONSENSUS_BINARY_MEMBERS[-1]},
                extra={"../validator_harness": b"x"},
            ),
            "consensus_binary_archive_members_invalid",
        ),
        (
            _regular_tar_bytes(overrides={CONSENSUS_BINARY_MEMBERS[0]: b""}),
            "consensus_binary_archive_member_size_invalid",
        ),
    ],
)
def test_archive_shape_rejections(monkeypatch, tmp_path, body, token):
    bundle = _bundle(monkeypatch, body)
    try:
        with pytest.raises(ConsensusBinaryDeployError) as exc:
            _deploy(bundle, tmp_path / "bin")
        assert exc.value.token == token
    finally:
        _cleanup_bundle(bundle)


def test_member_and_total_expansion_bounds(monkeypatch, tmp_path):
    body = _regular_tar_bytes(
        overrides={name: b"1234" for name in CONSENSUS_BINARY_MEMBERS}
    )
    bundle = _bundle(monkeypatch, body)
    try:
        monkeypatch.setattr(deploy, "MAX_CONSENSUS_BINARY_MEMBER_BYTES", 3)
        with pytest.raises(ConsensusBinaryDeployError) as exc:
            _deploy(bundle, tmp_path / "member")
        assert exc.value.token == "consensus_binary_archive_member_size_invalid"

        monkeypatch.setattr(deploy, "MAX_CONSENSUS_BINARY_MEMBER_BYTES", 10)
        monkeypatch.setattr(deploy, "MAX_CONSENSUS_BINARY_EXPANDED_BYTES", 20)
        with pytest.raises(ConsensusBinaryDeployError) as exc:
            _deploy(bundle, tmp_path / "total")
        assert exc.value.token == "consensus_binary_archive_expanded_size_exceeded"
    finally:
        _cleanup_bundle(bundle)


def test_invalid_and_tampered_bundle_reject(monkeypatch, tmp_path):
    with pytest.raises(ConsensusBinaryDeployError) as exc:
        VerifiedConsensusBinaryBundle(
            path=tmp_path / "forged",
            artifact_cid="cid",
            artifact_sha256="0" * 64,
            artifact_size_bytes=1,
            filename="forged",
            _verification_token=object(),
        )
    assert exc.value.token == "consensus_binary_bundle_verification_capability_required"

    body = _regular_tar_bytes()
    bundle = _bundle(monkeypatch, body)
    try:
        bundle.path.write_bytes(b"tampered")
        with pytest.raises(ConsensusBinaryDeployError) as exc:
            _deploy(bundle, tmp_path / "bin")
        assert exc.value.token in {
            "consensus_binary_bundle_size_changed",
            "consensus_binary_bundle_hash_changed",
        }
    finally:
        _cleanup_bundle(bundle)


def test_install_dir_and_target_symlinks_reject(monkeypatch, tmp_path):
    body = _regular_tar_bytes()
    bundle = _bundle(monkeypatch, body)
    try:
        real_dir = tmp_path / "real"
        real_dir.mkdir()
        link_dir = tmp_path / "link"
        link_dir.symlink_to(real_dir, target_is_directory=True)
        with pytest.raises(ConsensusBinaryDeployError) as exc:
            _deploy(bundle, link_dir)
        assert exc.value.token == "consensus_binary_install_dir_symlink"

        target_dir = tmp_path / "targets"
        target_dir.mkdir()
        outside = tmp_path / "outside"
        outside.write_bytes(b"outside")
        (target_dir / CONSENSUS_BINARY_MEMBERS[0]).symlink_to(outside)
        with pytest.raises(ConsensusBinaryDeployError) as exc:
            _deploy(bundle, target_dir)
        assert exc.value.token == "consensus_binary_target_not_regular"
        assert outside.read_bytes() == b"outside"
    finally:
        _cleanup_bundle(bundle)


def test_lock_contention_rejects(monkeypatch, tmp_path):
    body = _regular_tar_bytes()
    bundle = _bundle(monkeypatch, body)
    install_dir = tmp_path / "bin"
    install_dir.mkdir()
    descriptor = os.open(install_dir / CONSENSUS_BINARY_DEPLOY_LOCK, os.O_RDWR | os.O_CREAT, 0o600)
    fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
    try:
        with pytest.raises(ConsensusBinaryDeployError) as exc:
            _deploy(bundle, install_dir)
        assert exc.value.token == "consensus_binary_deploy_locked"
    finally:
        fcntl.flock(descriptor, fcntl.LOCK_UN)
        os.close(descriptor)
        _cleanup_bundle(bundle)


def test_replace_failure_rolls_back_exact_prior_state(monkeypatch, tmp_path):
    body = _regular_tar_bytes()
    bundle = _bundle(monkeypatch, body)
    install_dir = tmp_path / "bin"
    install_dir.mkdir()
    old = {name: f"old:{name}".encode("ascii") for name in CONSENSUS_BINARY_MEMBERS}
    for name, payload in old.items():
        (install_dir / name).write_bytes(payload)
    unrelated = install_dir / "operator-note"
    unrelated.write_bytes(b"preserve")
    real_replace = deploy.os.replace
    failed = False

    def fail_second_stage(source, destination):
        nonlocal failed
        source_path = Path(source)
        if (
            not failed
            and source_path.name == CONSENSUS_BINARY_MEMBERS[1]
            and source_path.parent.name.startswith(".ilc-consensus-stage-")
        ):
            failed = True
            raise OSError("injected replace failure")
        return real_replace(source, destination)

    monkeypatch.setattr(deploy.os, "replace", fail_second_stage)
    try:
        with pytest.raises(ConsensusBinaryDeployError) as exc:
            _deploy(bundle, install_dir)
        assert exc.value.token == "consensus_binary_replace_failed"
        for name, payload in old.items():
            assert (install_dir / name).read_bytes() == payload
        assert unrelated.read_bytes() == b"preserve"
    finally:
        _cleanup_bundle(bundle)


def test_destination_fsync_failure_rolls_back(monkeypatch, tmp_path):
    body = _regular_tar_bytes()
    bundle = _bundle(monkeypatch, body)
    install_dir = tmp_path / "bin"
    install_dir.mkdir()
    old = {name: f"old:{name}".encode("ascii") for name in CONSENSUS_BINARY_MEMBERS}
    for name, payload in old.items():
        (install_dir / name).write_bytes(payload)
    real_fsync = deploy._fsync_directory
    failed = False

    def fail_destination_once(path: Path) -> None:
        nonlocal failed
        if path == install_dir and not failed:
            failed = True
            raise ConsensusBinaryDeployError("consensus_binary_directory_fsync_failed")
        real_fsync(path)

    monkeypatch.setattr(deploy, "_fsync_directory", fail_destination_once)
    try:
        with pytest.raises(ConsensusBinaryDeployError) as exc:
            _deploy(bundle, install_dir)
        assert exc.value.token == "consensus_binary_directory_fsync_failed"
        for name, payload in old.items():
            assert (install_dir / name).read_bytes() == payload
    finally:
        _cleanup_bundle(bundle)


def test_stage_permission_failure_leaves_targets_untouched(monkeypatch, tmp_path):
    body = _regular_tar_bytes()
    bundle = _bundle(monkeypatch, body)
    install_dir = tmp_path / "bin"
    install_dir.mkdir()
    target = install_dir / CONSENSUS_BINARY_MEMBERS[0]
    target.write_bytes(b"old")
    monkeypatch.setattr(
        deploy.os,
        "chmod",
        lambda *args, **kwargs: (_ for _ in ()).throw(PermissionError("injected")),
    )
    try:
        with pytest.raises(ConsensusBinaryDeployError) as exc:
            _deploy(bundle, install_dir)
        assert exc.value.token == "consensus_binary_archive_stage_failed"
        assert target.read_bytes() == b"old"
    finally:
        _cleanup_bundle(bundle)


def test_post_install_hash_failure_rolls_back(monkeypatch, tmp_path):
    body = _regular_tar_bytes()
    bundle = _bundle(monkeypatch, body)
    install_dir = tmp_path / "bin"
    install_dir.mkdir()
    old = {name: f"old:{name}".encode("ascii") for name in CONSENSUS_BINARY_MEMBERS}
    for name, payload in old.items():
        (install_dir / name).write_bytes(payload)
    real_sha = deploy._sha256_file

    def wrong_installed_hash(path: Path) -> str:
        if path.parent == install_dir:
            return "0" * 64
        return real_sha(path)

    monkeypatch.setattr(deploy, "_sha256_file", wrong_installed_hash)
    try:
        with pytest.raises(ConsensusBinaryDeployError) as exc:
            _deploy(bundle, install_dir)
        assert exc.value.token == "consensus_binary_post_install_hash_mismatch"
        for name, payload in old.items():
            assert (install_dir / name).read_bytes() == payload
    finally:
        _cleanup_bundle(bundle)


def test_unrelated_files_are_preserved(monkeypatch, tmp_path):
    body = _regular_tar_bytes()
    bundle = _bundle(monkeypatch, body)
    install_dir = tmp_path / "bin"
    install_dir.mkdir()
    unrelated = install_dir / "custom-helper"
    unrelated.write_bytes(b"operator-owned")
    try:
        _deploy(bundle, install_dir)
        assert unrelated.read_bytes() == b"operator-owned"
    finally:
        _cleanup_bundle(bundle)


def test_post_commit_backup_cleanup_failure_is_reported(monkeypatch, tmp_path):
    body = _regular_tar_bytes()
    bundle = _bundle(monkeypatch, body)
    install_dir = tmp_path / "bin"
    install_dir.mkdir()
    for name in CONSENSUS_BINARY_MEMBERS:
        (install_dir / name).write_bytes(f"old:{name}".encode("ascii"))
    real_rmtree = deploy.shutil.rmtree

    def retain_backups(path, *args, **kwargs):
        if Path(path).name.startswith(".ilc-consensus-backup-"):
            return None
        return real_rmtree(path, *args, **kwargs)

    monkeypatch.setattr(deploy.shutil, "rmtree", retain_backups)
    try:
        receipt = _deploy(bundle, install_dir)
        assert receipt["deployment_status"] == "installed_not_executed"
        assert receipt["backup_cleanup_status"] == "installed_backup_retained"
        assert list(install_dir.glob(".ilc-consensus-backup-*"))
    finally:
        monkeypatch.setattr(deploy.shutil, "rmtree", real_rmtree)
        for path in install_dir.glob(".ilc-consensus-backup-*"):
            real_rmtree(path)
        _cleanup_bundle(bundle)


def test_module_has_no_helper_execution_surface():
    import inspect
    from ilc_core.release import consensus_binary_deploy as deploy

    source = inspect.getsource(deploy)
    assert "subprocess" not in source
    assert "os.system" not in source
    assert "exec(" not in source
