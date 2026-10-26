# SPDX-License-Identifier: AGPL-3.0-only
"""Authorized fetch and transactional local deployment of consensus helpers.

This module installs bytes only. It never executes a helper, emits serving
credit, mutates economic state, or changes a remote host.
"""

from __future__ import annotations

import fcntl
import hashlib
import os
import shutil
import stat
import tarfile
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping

from ilc_core.release.artifact_fetch import (
    ARTIFACT_DOWNLOAD_CHUNK_BYTES,
    ArtifactFetchError,
    fetch_and_verify_binary_tarball,
)
from ilc_core.release.current_policy import CurrentPolicyEvaluationInput
from ilc_core.release.upgrade_check import (
    UpgradeCheckError,
    require_arbitrary_source_release_authorized,
    validate_release_assertion,
)


CONSENSUS_BINARY_MEMBERS = (
    "attribution_batch_ingest",
    "bls_verify_digest",
    "ilc_p2p_bridge",
    "invite_pop_bls",
    "keygen",
    "validator_endpoint_assertion_bls",
    "validator_harness",
)
CONSENSUS_BINARY_MODE = 0o755
MAX_CONSENSUS_BINARY_MEMBER_BYTES = 50_000_000
MAX_CONSENSUS_BINARY_EXPANDED_BYTES = (
    len(CONSENSUS_BINARY_MEMBERS) * MAX_CONSENSUS_BINARY_MEMBER_BYTES
)
CONSENSUS_BINARY_DEPLOY_LOCK = ".ilc-consensus-binary-deploy.lock"
_VERIFIED_BUNDLE_TOKEN = object()


class ConsensusBinaryDeployError(ValueError):
    """Stable-token error for consensus archive or deployment failures."""

    def __init__(self, token: str, message: str | None = None) -> None:
        super().__init__(message or token)
        self.token = token
        self.message = message or token


@dataclass(frozen=True)
class VerifiedConsensusBinaryBundle:
    """Capability returned only after release authorization and byte checks."""

    path: Path
    artifact_cid: str
    artifact_sha256: str
    artifact_size_bytes: int
    filename: str
    _verification_token: object = field(repr=False, compare=False)

    def __post_init__(self) -> None:
        if self._verification_token is not _VERIFIED_BUNDLE_TOKEN:
            raise ConsensusBinaryDeployError(
                "consensus_binary_bundle_verification_capability_required"
            )


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    try:
        with path.open("rb") as handle:
            while True:
                chunk = handle.read(ARTIFACT_DOWNLOAD_CHUNK_BYTES)
                if not chunk:
                    break
                digest.update(chunk)
    except OSError as exc:
        raise ConsensusBinaryDeployError(
            "consensus_binary_bundle_read_failed"
        ) from exc
    return digest.hexdigest()


def _binary_tarball_node(release_assertion: Mapping[str, Any]) -> Mapping[str, Any]:
    nodes = release_assertion.get("artifact_nodes")
    if not isinstance(nodes, list):
        raise ConsensusBinaryDeployError("consensus_binary_artifact_nodes_missing")
    matches = [
        node
        for node in nodes
        if isinstance(node, Mapping) and node.get("artifact_type") == "binary_tarball"
    ]
    if len(matches) != 1:
        raise ConsensusBinaryDeployError(
            "consensus_binary_artifact_count_invalid"
        )
    return matches[0]


def fetch_verified_consensus_binary_bundle(
    release_assertion: Mapping[str, Any],
    *,
    policy_evaluation_input: CurrentPolicyEvaluationInput | None,
) -> VerifiedConsensusBinaryBundle:
    """Authorize the release, fetch its sole tarball, and bind a capability."""

    path = fetch_and_verify_binary_tarball(
        release_assertion,
        policy_evaluation_input=policy_evaluation_input,
    )
    try:
        node = _binary_tarball_node(release_assertion)
        cid = node.get("cid")
        digest = node.get("sha256")
        size = node.get("size_bytes")
        filename = node.get("filename")
        if not isinstance(cid, str) or not cid:
            raise ConsensusBinaryDeployError("consensus_binary_artifact_cid_missing")
        if not isinstance(digest, str) or len(digest) != 64:
            raise ConsensusBinaryDeployError("consensus_binary_artifact_sha256_invalid")
        if not isinstance(size, int) or isinstance(size, bool) or size <= 0:
            raise ConsensusBinaryDeployError("consensus_binary_artifact_size_invalid")
        if not isinstance(filename, str) or path.name != filename:
            raise ConsensusBinaryDeployError("consensus_binary_artifact_filename_mismatch")
        return VerifiedConsensusBinaryBundle(
            path=path,
            artifact_cid=cid,
            artifact_sha256=digest,
            artifact_size_bytes=size,
            filename=filename,
            _verification_token=_VERIFIED_BUNDLE_TOKEN,
        )
    except Exception:
        shutil.rmtree(path.parent, ignore_errors=True)
        raise


def _fsync_directory(path: Path) -> None:
    flags = os.O_RDONLY
    if hasattr(os, "O_DIRECTORY"):
        flags |= os.O_DIRECTORY
    try:
        descriptor = os.open(path, flags)
        try:
            os.fsync(descriptor)
        finally:
            os.close(descriptor)
    except OSError as exc:
        raise ConsensusBinaryDeployError("consensus_binary_directory_fsync_failed") from exc


def _open_lock(install_dir: Path) -> int:
    flags = os.O_RDWR | os.O_CREAT
    if hasattr(os, "O_CLOEXEC"):
        flags |= os.O_CLOEXEC
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        descriptor = os.open(install_dir / CONSENSUS_BINARY_DEPLOY_LOCK, flags, 0o600)
        fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError as exc:
        try:
            os.close(descriptor)
        except (OSError, UnboundLocalError):
            pass
        raise ConsensusBinaryDeployError("consensus_binary_deploy_locked") from exc
    except OSError as exc:
        try:
            os.close(descriptor)
        except (OSError, UnboundLocalError):
            pass
        raise ConsensusBinaryDeployError("consensus_binary_deploy_lock_failed") from exc
    return descriptor


def _validate_bundle_file(bundle: VerifiedConsensusBinaryBundle) -> None:
    if bundle._verification_token is not _VERIFIED_BUNDLE_TOKEN:
        raise ConsensusBinaryDeployError(
            "consensus_binary_bundle_verification_capability_required"
        )
    try:
        metadata = bundle.path.lstat()
    except OSError as exc:
        raise ConsensusBinaryDeployError("consensus_binary_bundle_missing") from exc
    if not stat.S_ISREG(metadata.st_mode) or bundle.path.is_symlink():
        raise ConsensusBinaryDeployError("consensus_binary_bundle_not_regular")
    if metadata.st_size != bundle.artifact_size_bytes:
        raise ConsensusBinaryDeployError("consensus_binary_bundle_size_changed")
    if _sha256_file(bundle.path) != bundle.artifact_sha256:
        raise ConsensusBinaryDeployError("consensus_binary_bundle_hash_changed")


def _revalidate_bundle_authority(
    bundle: VerifiedConsensusBinaryBundle,
    release_assertion: Mapping[str, Any],
    policy_evaluation_input: CurrentPolicyEvaluationInput | None,
) -> None:
    if policy_evaluation_input is None:
        raise ConsensusBinaryDeployError("consensus_binary_deploy_eligibility_unresolved")
    try:
        validation = validate_release_assertion(
            release_assertion,
            current_policy_evaluation_input=policy_evaluation_input,
        )
        require_arbitrary_source_release_authorized(validation)
    except UpgradeCheckError as exc:
        raise ConsensusBinaryDeployError(
            "consensus_binary_deploy_eligibility_gate_failed",
            f"consensus_binary_deploy_eligibility_gate_failed:{exc.token}",
        ) from exc
    node = _binary_tarball_node(release_assertion)
    if (
        node.get("cid") != bundle.artifact_cid
        or node.get("sha256") != bundle.artifact_sha256
        or node.get("size_bytes") != bundle.artifact_size_bytes
        or node.get("filename") != bundle.filename
    ):
        raise ConsensusBinaryDeployError("consensus_binary_bundle_release_mismatch")


def _write_member(
    archive: tarfile.TarFile,
    member: tarfile.TarInfo,
    destination: Path,
) -> str:
    source = archive.extractfile(member)
    if source is None:
        raise ConsensusBinaryDeployError("consensus_binary_archive_member_unreadable")
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    if hasattr(os, "O_CLOEXEC"):
        flags |= os.O_CLOEXEC
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    digest = hashlib.sha256()
    total = 0
    try:
        descriptor = os.open(destination, flags, 0o700)
        with source, os.fdopen(descriptor, "wb") as handle:
            while True:
                chunk = source.read(ARTIFACT_DOWNLOAD_CHUNK_BYTES)
                if not chunk:
                    break
                total += len(chunk)
                if total > member.size or total > MAX_CONSENSUS_BINARY_MEMBER_BYTES:
                    raise ConsensusBinaryDeployError(
                        "consensus_binary_archive_member_expansion_exceeded"
                    )
                digest.update(chunk)
                handle.write(chunk)
            if total != member.size:
                raise ConsensusBinaryDeployError(
                    "consensus_binary_archive_member_size_mismatch"
                )
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(destination, CONSENSUS_BINARY_MODE, follow_symlinks=False)
    except ConsensusBinaryDeployError:
        destination.unlink(missing_ok=True)
        raise
    except (OSError, tarfile.TarError) as exc:
        destination.unlink(missing_ok=True)
        raise ConsensusBinaryDeployError("consensus_binary_archive_stage_failed") from exc
    return digest.hexdigest()


def _stage_archive(bundle: VerifiedConsensusBinaryBundle, stage_dir: Path) -> dict[str, str]:
    member_hashes: dict[str, str] = {}
    expanded = 0
    expected = set(CONSENSUS_BINARY_MEMBERS)
    try:
        with tarfile.open(bundle.path, mode="r:gz") as archive:
            for member in archive:
                if len(member_hashes) >= len(CONSENSUS_BINARY_MEMBERS):
                    raise ConsensusBinaryDeployError(
                        "consensus_binary_archive_member_count_invalid"
                    )
                name = member.name
                if name not in expected:
                    raise ConsensusBinaryDeployError(
                        "consensus_binary_archive_members_invalid"
                    )
                if name in member_hashes:
                    raise ConsensusBinaryDeployError(
                        "consensus_binary_archive_member_duplicate"
                    )
                if not member.isfile():
                    raise ConsensusBinaryDeployError(
                        "consensus_binary_archive_member_type_invalid"
                    )
                if member.size <= 0 or member.size > MAX_CONSENSUS_BINARY_MEMBER_BYTES:
                    raise ConsensusBinaryDeployError(
                        "consensus_binary_archive_member_size_invalid"
                    )
                expanded += member.size
                if expanded > MAX_CONSENSUS_BINARY_EXPANDED_BYTES:
                    raise ConsensusBinaryDeployError(
                        "consensus_binary_archive_expanded_size_exceeded"
                    )
                member_hashes[name] = _write_member(
                    archive,
                    member,
                    stage_dir / name,
                )
    except ConsensusBinaryDeployError:
        raise
    except (OSError, tarfile.TarError, EOFError) as exc:
        raise ConsensusBinaryDeployError("consensus_binary_archive_invalid") from exc
    if set(member_hashes) != expected:
        raise ConsensusBinaryDeployError("consensus_binary_archive_members_invalid")
    _fsync_directory(stage_dir)
    return member_hashes


def _preflight_targets(install_dir: Path) -> set[str]:
    existing: set[str] = set()
    for name in CONSENSUS_BINARY_MEMBERS:
        target = install_dir / name
        try:
            metadata = target.lstat()
        except FileNotFoundError:
            continue
        except OSError as exc:
            raise ConsensusBinaryDeployError(
                "consensus_binary_target_inspection_failed"
            ) from exc
        if not stat.S_ISREG(metadata.st_mode) or target.is_symlink():
            raise ConsensusBinaryDeployError("consensus_binary_target_not_regular")
        existing.add(name)
    return existing


def _rollback(
    install_dir: Path,
    backup_dir: Path,
    installed: list[str],
    backed_up: list[str],
) -> None:
    try:
        for name in reversed(installed):
            (install_dir / name).unlink(missing_ok=True)
        for name in reversed(backed_up):
            os.replace(backup_dir / name, install_dir / name)
        _fsync_directory(install_dir)
        installed.clear()
        backed_up.clear()
    except (OSError, ConsensusBinaryDeployError) as exc:
        raise ConsensusBinaryDeployError("consensus_binary_rollback_failed") from exc


def deploy_verified_consensus_binary_bundle(
    bundle: VerifiedConsensusBinaryBundle,
    *,
    release_assertion: Mapping[str, Any],
    policy_evaluation_input: CurrentPolicyEvaluationInput | None,
    install_dir: str | os.PathLike[str],
) -> dict[str, Any]:
    """Install exactly seven verified helpers without executing them."""

    if not isinstance(bundle, VerifiedConsensusBinaryBundle):
        raise ConsensusBinaryDeployError(
            "consensus_binary_bundle_verification_capability_required"
        )
    _validate_bundle_file(bundle)
    _revalidate_bundle_authority(bundle, release_assertion, policy_evaluation_input)
    destination = Path(install_dir).expanduser()
    try:
        if destination.is_symlink():
            raise ConsensusBinaryDeployError("consensus_binary_install_dir_symlink")
        destination.mkdir(mode=0o700, parents=True, exist_ok=True)
        if not destination.is_dir():
            raise ConsensusBinaryDeployError("consensus_binary_install_dir_invalid")
    except ConsensusBinaryDeployError:
        raise
    except OSError as exc:
        raise ConsensusBinaryDeployError("consensus_binary_install_dir_unavailable") from exc

    lock_descriptor = _open_lock(destination)
    stage_dir: Path | None = None
    backup_dir: Path | None = None
    installed: list[str] = []
    backed_up: list[str] = []
    committed = False
    receipt: dict[str, Any] | None = None
    try:
        stage_dir = Path(tempfile.mkdtemp(prefix=".ilc-consensus-stage-", dir=destination))
        backup_dir = Path(tempfile.mkdtemp(prefix=".ilc-consensus-backup-", dir=destination))
        member_hashes = _stage_archive(bundle, stage_dir)
        existing = _preflight_targets(destination)
        try:
            for name in CONSENSUS_BINARY_MEMBERS:
                target = destination / name
                if name in existing:
                    os.replace(target, backup_dir / name)
                    backed_up.append(name)
                os.replace(stage_dir / name, target)
                installed.append(name)
            _fsync_directory(destination)
            observed_hashes = {
                name: _sha256_file(destination / name)
                for name in CONSENSUS_BINARY_MEMBERS
            }
            if observed_hashes != member_hashes:
                raise ConsensusBinaryDeployError(
                    "consensus_binary_post_install_hash_mismatch"
                )
            for name in CONSENSUS_BINARY_MEMBERS:
                metadata = (destination / name).lstat()
                if not stat.S_ISREG(metadata.st_mode):
                    raise ConsensusBinaryDeployError(
                        "consensus_binary_post_install_type_invalid"
                    )
                if stat.S_IMODE(metadata.st_mode) != CONSENSUS_BINARY_MODE:
                    raise ConsensusBinaryDeployError(
                        "consensus_binary_post_install_mode_invalid"
                    )
            _fsync_directory(destination)
            committed = True
        except ConsensusBinaryDeployError:
            _rollback(destination, backup_dir, installed, backed_up)
            raise
        except OSError as exc:
            _rollback(destination, backup_dir, installed, backed_up)
            raise ConsensusBinaryDeployError("consensus_binary_replace_failed") from exc

        receipt = {
            "artifact_cid": bundle.artifact_cid,
            "artifact_sha256": bundle.artifact_sha256,
            "artifact_size_bytes": bundle.artifact_size_bytes,
            "deployment_status": "installed_not_executed",
            "economic_mutation": False,
            "install_dir": str(destination),
            "installed_members": list(CONSENSUS_BINARY_MEMBERS),
            "member_sha256": observed_hashes,
            "no_helper_executed": True,
            "serving_receipt_written": False,
        }
        return receipt
    finally:
        if stage_dir is not None:
            shutil.rmtree(stage_dir, ignore_errors=True)
        if backup_dir is not None:
            if committed:
                shutil.rmtree(backup_dir, ignore_errors=True)
                cleanup_status = (
                    "installed_backup_retained"
                    if backup_dir.exists()
                    else "cleanup_complete"
                )
                if receipt is not None:
                    receipt["backup_cleanup_status"] = cleanup_status
            elif not backed_up:
                shutil.rmtree(backup_dir, ignore_errors=True)
        try:
            fcntl.flock(lock_descriptor, fcntl.LOCK_UN)
        finally:
            os.close(lock_descriptor)


def fetch_verify_and_deploy_consensus_binary_bundle(
    release_assertion: Mapping[str, Any],
    *,
    policy_evaluation_input: CurrentPolicyEvaluationInput | None,
    install_dir: str | os.PathLike[str],
) -> dict[str, Any]:
    """Production composition: authorize, fetch, verify, deploy, and clean up."""

    bundle = fetch_verified_consensus_binary_bundle(
        release_assertion,
        policy_evaluation_input=policy_evaluation_input,
    )
    try:
        return deploy_verified_consensus_binary_bundle(
            bundle,
            release_assertion=release_assertion,
            policy_evaluation_input=policy_evaluation_input,
            install_dir=install_dir,
        )
    finally:
        shutil.rmtree(bundle.path.parent, ignore_errors=True)


__all__ = [
    "CONSENSUS_BINARY_MEMBERS",
    "ConsensusBinaryDeployError",
    "VerifiedConsensusBinaryBundle",
    "deploy_verified_consensus_binary_bundle",
    "fetch_verified_consensus_binary_bundle",
    "fetch_verify_and_deploy_consensus_binary_bundle",
]
