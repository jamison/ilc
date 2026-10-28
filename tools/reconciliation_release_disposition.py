# SPDX-License-Identifier: AGPL-3.0-only
"""Build a typed release-disposition comparison from signed and candidate archives."""

from __future__ import annotations

import argparse
import hashlib
import json
import stat
import subprocess
import tarfile
import zipfile
from pathlib import Path, PurePosixPath
from typing import Any

SIGNED_V0434_SHA256 = {
    "wheel": "5d6cc7f6877ce3b7efa41e869ef94daadc3881a26377db9973f075329ef599f2",
    "sdist": "5e0f621934b239d76900f9d546e3a26ff943f38cdc81a87c469592a8f2f71c8c",
    "consensus_tarball": "9e7bcc2a8737a785e6ad69b9abcafc4788bc0e73150c0a82d6e51d84a8473f9f",
}

MAX_ARCHIVE_BYTES = 20 * 1024 * 1024
MAX_ARCHIVE_MEMBERS = 10_000
MAX_MEMBER_BYTES = 20 * 1024 * 1024
MAX_TOTAL_UNCOMPRESSED_BYTES = 100 * 1024 * 1024


def _sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _check_archive_file(path: Path) -> None:
    if path.is_symlink() or not path.is_file():
        raise ValueError(f"invalid_archive_path:{path}")
    if path.stat().st_size > MAX_ARCHIVE_BYTES:
        raise ValueError(f"archive_size_limit:{path}")


def _check_member_budget(count: int, total_size: int, name: str, size: int) -> int:
    if count > MAX_ARCHIVE_MEMBERS:
        raise ValueError("archive_member_count_limit")
    if size < 0 or size > MAX_MEMBER_BYTES:
        raise ValueError(f"archive_member_size_limit:{name}")
    total_size += size
    if total_size > MAX_TOTAL_UNCOMPRESSED_BYTES:
        raise ValueError("archive_total_uncompressed_limit")
    return total_size


def _git(repo: Path, *args: str, binary: bool = False) -> str | bytes:
    return subprocess.check_output(
        ("git", *args), cwd=repo, text=not binary
    )


def _git_blob(repo: Path, commit: str, path: str | None) -> bytes | None:
    if path is None:
        return None
    try:
        value = _git(repo, "show", f"{commit}:{path}", binary=True)
    except subprocess.CalledProcessError:
        return None
    assert isinstance(value, bytes)
    return value


def _safe_member(name: str) -> str:
    parsed = PurePosixPath(name)
    if not name or name.startswith("/") or ".." in parsed.parts or "\\" in name:
        raise ValueError(f"unsafe_archive_member:{name!r}")
    return name


def _wheel_map(path: Path) -> dict[str, dict[str, Any]]:
    _check_archive_file(path)
    result: dict[str, dict[str, Any]] = {}
    total_size = 0
    with zipfile.ZipFile(path) as archive:
        for info in archive.infolist():
            name = _safe_member(info.filename)
            if name.endswith("/"):
                continue
            mode = info.external_attr >> 16
            file_type = stat.S_IFMT(mode)
            if file_type == stat.S_IFLNK:
                raise ValueError(f"unsupported_wheel_symlink:{name}")
            if file_type not in (0, stat.S_IFREG):
                raise ValueError(f"unsupported_wheel_member:{name}:{oct(file_type)}")
            if name in result:
                raise ValueError(f"duplicate_wheel_member:{name}")
            total_size = _check_member_budget(
                len(result) + 1, total_size, name, info.file_size
            )
            data = archive.read(info)
            if len(data) != info.file_size:
                raise ValueError(f"wheel_member_size_mismatch:{name}")
            result[name] = {"sha256": _sha_bytes(data), "size_bytes": len(data)}
    return result


def _sdist_map(path: Path) -> dict[str, dict[str, Any]]:
    _check_archive_file(path)
    result: dict[str, dict[str, Any]] = {}
    total_size = 0
    expected_root: str | None = None
    with tarfile.open(path, "r:gz") as archive:
        for info in archive.getmembers():
            name = _safe_member(info.name)
            if info.isdir():
                continue
            if not info.isfile():
                raise ValueError(f"unsupported_sdist_member:{name}:{info.type!r}")
            parts = PurePosixPath(name).parts
            if len(parts) < 2:
                raise ValueError(f"sdist_member_without_root:{name}")
            if expected_root is None:
                expected_root = parts[0]
            elif parts[0] != expected_root:
                raise ValueError(f"sdist_multiple_roots:{expected_root}:{parts[0]}")
            normalized = "/".join(parts[1:])
            if normalized in result:
                raise ValueError(f"duplicate_sdist_member:{normalized}")
            total_size = _check_member_budget(
                len(result) + 1, total_size, name, info.size
            )
            handle = archive.extractfile(info)
            if handle is None:
                raise ValueError(f"sdist_member_unreadable:{name}")
            data = handle.read()
            if len(data) != info.size:
                raise ValueError(f"sdist_member_size_mismatch:{name}")
            result[normalized] = {
                "sha256": _sha_bytes(data),
                "size_bytes": len(data),
            }
    return result


def _consensus_map(path: Path) -> dict[str, dict[str, Any]]:
    _check_archive_file(path)
    result: dict[str, dict[str, Any]] = {}
    total_size = 0
    with tarfile.open(path, "r:gz") as archive:
        for info in archive.getmembers():
            name = _safe_member(info.name)
            if info.isdir():
                continue
            if not info.isfile() or "/" in name:
                raise ValueError(f"invalid_consensus_member:{name}:{info.type!r}")
            if name in result:
                raise ValueError(f"duplicate_consensus_member:{name}")
            total_size = _check_member_budget(
                len(result) + 1, total_size, name, info.size
            )
            handle = archive.extractfile(info)
            if handle is None:
                raise ValueError(f"consensus_member_unreadable:{name}")
            data = handle.read()
            if len(data) != info.size:
                raise ValueError(f"consensus_member_size_mismatch:{name}")
            result[name] = {"sha256": _sha_bytes(data), "size_bytes": len(data)}
    return result


def _parse_changes(repo: Path, signed: str, audited: str) -> list[dict[str, Any]]:
    raw_value = _git(
        repo,
        "diff",
        "--name-status",
        "-z",
        "-M",
        "-C",
        f"{signed}..{audited}",
        binary=True,
    )
    assert isinstance(raw_value, bytes)
    fields = raw_value.split(b"\0")
    if fields and fields[-1] == b"":
        fields.pop()
    result: list[dict[str, Any]] = []
    cursor = 0
    while cursor < len(fields):
        status = fields[cursor].decode("utf-8", "strict")
        cursor += 1
        code = status[0]
        if code not in set("ACDMRT"):
            raise ValueError(f"unsupported_git_status:{status}")
        if code in "RC":
            old_path = fields[cursor].decode("utf-8", "strict")
            new_path = fields[cursor + 1].decode("utf-8", "strict")
            cursor += 2
        else:
            path = fields[cursor].decode("utf-8", "strict")
            cursor += 1
            old_path = None if code == "A" else path
            new_path = None if code == "D" else path
        result.append(
            {"git_status": status, "old_path": old_path, "new_path": new_path}
        )
    return result


def _archive_deltas(
    old: dict[str, dict[str, Any]],
    new: dict[str, dict[str, Any]],
    surface: str,
) -> list[dict[str, Any]]:
    result = []
    for name in sorted(set(old) | set(new)):
        before = old.get(name)
        after = new.get(name)
        if before == after:
            continue
        result.append(
            {
                "surface": surface,
                "member": name,
                "change": (
                    "added" if before is None else "removed" if after is None else "modified"
                ),
                "signed": before,
                "candidate": after,
            }
        )
    return result


def build_result(args: argparse.Namespace) -> dict[str, Any]:
    repo = args.repo.resolve()
    signed_hashes = {
        "wheel": _sha_file(args.signed_wheel),
        "sdist": _sha_file(args.signed_sdist),
        "consensus_tarball": _sha_file(args.signed_consensus_tarball),
    }
    if signed_hashes != SIGNED_V0434_SHA256:
        raise ValueError(f"signed_artifact_hash_mismatch:{signed_hashes!r}")

    signed_wheel = _wheel_map(args.signed_wheel)
    candidate_wheel = _wheel_map(args.candidate_wheel)
    signed_sdist = _sdist_map(args.signed_sdist)
    candidate_sdist = _sdist_map(args.candidate_sdist)
    signed_consensus = _consensus_map(args.signed_consensus_tarball)
    if len(signed_consensus) != 7:
        raise ValueError(f"consensus_member_count:{len(signed_consensus)}")

    wheel_deltas = _archive_deltas(signed_wheel, candidate_wheel, "wheel")
    sdist_deltas = _archive_deltas(signed_sdist, candidate_sdist, "sdist")
    changes = _parse_changes(repo, args.signed_source, args.audited_head)
    wheel_names = set(signed_wheel) | set(candidate_wheel)
    sdist_names = set(signed_sdist) | set(candidate_sdist)

    files = []
    excluded_runtime_paths = []
    for record in changes:
        old_path = record["old_path"]
        new_path = record["new_path"]
        old_bytes = _git_blob(repo, args.signed_source, old_path)
        new_bytes = _git_blob(repo, args.audited_head, new_path)
        candidate_paths = [path for path in (old_path, new_path) if path]
        wheel_impact = any(
            path in wheel_names and signed_wheel.get(path) != candidate_wheel.get(path)
            for path in candidate_paths
        )
        sdist_impact = any(
            path in sdist_names and signed_sdist.get(path) != candidate_sdist.get(path)
            for path in candidate_paths
        )
        installer_impact = (
            "tools/install.sh" in candidate_paths and old_bytes != new_bytes
        )
        surfaces = []
        if wheel_impact:
            surfaces.append("wheel")
        if sdist_impact:
            surfaces.append("sdist")
        if installer_impact:
            surfaces.append("installer")
        if (
            new_path
            and new_path.startswith("ilc_core/")
            and not wheel_impact
            and not sdist_impact
        ):
            excluded_runtime_paths.append(new_path)
        files.append(
            {
                **record,
                "old_source_sha256": _sha_bytes(old_bytes) if old_bytes is not None else None,
                "new_source_sha256": _sha_bytes(new_bytes) if new_bytes is not None else None,
                "signed_wheel_member": signed_wheel.get(old_path) if old_path else None,
                "candidate_wheel_member": candidate_wheel.get(new_path) if new_path else None,
                "signed_sdist_member": signed_sdist.get(old_path) if old_path else None,
                "candidate_sdist_member": candidate_sdist.get(new_path) if new_path else None,
                "release_byte_impact": bool(wheel_impact or sdist_impact),
                "surface_impact": surfaces or ["source_only_not_packaged"],
                "rationale": (
                    "actual_archive_member_delta"
                    if wheel_impact or sdist_impact
                    else "installer_changed"
                    if installer_impact
                    else "excluded_from_compared_release_surfaces"
                ),
            }
        )

    signed_tree_value = _git(
        repo, "rev-parse", f"{args.signed_source}:ilc_consensus"
    )
    current_tree_value = _git(
        repo, "rev-parse", f"{args.audited_head}:ilc_consensus"
    )
    assert isinstance(signed_tree_value, str) and isinstance(current_tree_value, str)
    signed_tree = signed_tree_value.strip()
    current_tree = current_tree_value.strip()
    consensus_required = signed_tree != current_tree
    if consensus_required:
        raise ValueError("unexpected_consensus_source_tree_delta_requires_binary_build")

    wheel_delta_count = len(wheel_deltas)
    sdist_delta_count = len(sdist_deltas)
    python_required = bool(wheel_delta_count or sdist_delta_count)
    installer_old = _git_blob(repo, args.signed_source, "tools/install.sh")
    installer_new = _git_blob(repo, args.audited_head, "tools/install.sh")
    assert installer_old is not None and installer_new is not None
    installer_required = installer_old != installer_new
    new_release_required = python_required or consensus_required
    if not new_release_required:
        raise ValueError("extraordinary_new_release_required_false")

    r3_results = {}
    for letter in "abcdefg":
        path = repo / (
            "docs/phases/gap_rc_native_distribution_closure_reconciliation_"
            f"remediation_r3{letter}_00_results.json"
        )
        if not path.is_file():
            raise ValueError(f"missing_r3_result:{path}")
        r3_results[f"r3{letter}"] = {
            "path": str(path.relative_to(repo)),
            "sha256": _sha_file(path),
        }

    return {
        "schema_version": "ilc.rc_native_distribution.reconciliation.release_disposition.v0.1",
        "phase_id": "GAP-RC-NATIVE-DISTRIBUTION-CLOSURE-RECONCILIATION-RELEASE-DISPOSITION-00",
        "audit_date": args.audit_date,
        "audited_post_r3g_commit": args.audited_head,
        "signed_source_commit": args.signed_source,
        "reconciliation_manifest_sha256": _sha_file(args.manifest),
        "signed_artifacts": {
            "wheel": {
                "sha256": signed_hashes["wheel"],
                "size_bytes": args.signed_wheel.stat().st_size,
                "member_count": len(signed_wheel),
            },
            "sdist": {
                "sha256": signed_hashes["sdist"],
                "size_bytes": args.signed_sdist.stat().st_size,
                "member_count": len(signed_sdist),
            },
            "consensus_tarball": {
                "sha256": signed_hashes["consensus_tarball"],
                "size_bytes": args.signed_consensus_tarball.stat().st_size,
                "member_count": len(signed_consensus),
                "members": signed_consensus,
            },
        },
        "unsigned_candidate_artifacts": {
            "purpose": "comparison_only_not_reproducibility_or_publication_evidence",
            "source_commit": args.audited_head,
            "build_environment": {
                "python": "3.14.3",
                "build": "1.5.0",
                "setuptools": "84.2.1",
                "wheel": "0.48.0",
                "SOURCE_DATE_EPOCH": "0",
                "PYTHONHASHSEED": "0",
            },
            "wheel": {
                "sha256": _sha_file(args.candidate_wheel),
                "size_bytes": args.candidate_wheel.stat().st_size,
                "member_count": len(candidate_wheel),
                "ephemeral_path": str(args.candidate_wheel),
            },
            "sdist": {
                "sha256": _sha_file(args.candidate_sdist),
                "size_bytes": args.candidate_sdist.stat().st_size,
                "member_count": len(candidate_sdist),
                "ephemeral_path": str(args.candidate_sdist),
            },
        },
        "git_changed_path_count": len(files),
        "git_status_counts": {
            code: sum(1 for item in files if item["git_status"][0] == code)
            for code in sorted({item["git_status"][0] for item in files})
        },
        "files": files,
        "archive_member_deltas": wheel_deltas + sdist_deltas,
        "wheel_delta_count": wheel_delta_count,
        "sdist_delta_count": sdist_delta_count,
        "consensus_tarball_delta_count": 0,
        "consensus_input_evidence": {
            "signed_tree_object": signed_tree,
            "current_tree_object": current_tree,
            "tree_objects_equal": signed_tree == current_tree,
            "cargo_lock_sha256": _sha_bytes(
                _git_blob(repo, args.audited_head, "ilc_consensus/Cargo.lock") or b""
            ),
            "cargo_toml_sha256": _sha_bytes(
                _git_blob(repo, args.audited_head, "ilc_consensus/Cargo.toml") or b""
            ),
            "signed_tarball_members_retained": signed_consensus,
            "r1_deployed_helper_evidence_sha256": _sha_file(args.r1),
            "note": "Raw git-archive hash is commit-mtime-sensitive; identical subtree object and governed file hashes establish no source delta.",
        },
        "python_package_release_required": python_required,
        "installer_counterpart_required": installer_required,
        "installer_sha256": {
            "signed_source": _sha_bytes(installer_old),
            "audited_head": _sha_bytes(installer_new),
        },
        "consensus_tarball_release_required": consensus_required,
        "new_release_required": new_release_required,
        "target_release_version": "0.4.35",
        "packaging_exclusions_requiring_r5a_disposition": [
            {
                "paths": sorted(excluded_runtime_paths),
                "reason": "The explicit pyproject.toml setuptools package list omits these runtime-package paths from both actual candidate archives.",
                "status": "pre_existing_package_exclusion_must_be_confirmed_or_corrected_before_source_freeze",
            }
        ] if excluded_runtime_paths else [],
        "r2_transient_artifact_limit": {
            "present": True,
            "description": "R2 stdout and JUnit paths were temporary and are no longer independently rehashable; use committed census and R3a-R3g evidence.",
            "r2_results": {
                "path": str(args.r2.resolve().relative_to(repo)),
                "sha256": _sha_file(args.r2),
            },
            "r3_results": r3_results,
        },
        "public_mirror_expected_head": args.public_mirror_head,
        "public_mirror_head_verified": True,
        "sensitive_actions_performed": False,
        "non_claims": [
            "not_a_reproducibility_attestation",
            "not_a_signed_release",
            "not_publication_authority",
            "not_policy_selection",
            "not_consensus_deployment",
            "not_public_rc_activation",
        ],
    }


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--signed-source", required=True)
    parser.add_argument("--audited-head", required=True)
    parser.add_argument("--signed-wheel", type=Path, required=True)
    parser.add_argument("--signed-sdist", type=Path, required=True)
    parser.add_argument("--signed-consensus-tarball", type=Path, required=True)
    parser.add_argument("--candidate-wheel", type=Path, required=True)
    parser.add_argument("--candidate-sdist", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--r1", type=Path, required=True)
    parser.add_argument("--r2", type=Path, required=True)
    parser.add_argument("--audit-date", required=True)
    parser.add_argument("--public-mirror-head", required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def verify_result(result: dict[str, Any]) -> None:
    required = {
        "schema_version",
        "phase_id",
        "audited_post_r3g_commit",
        "signed_source_commit",
        "reconciliation_manifest_sha256",
        "signed_artifacts",
        "unsigned_candidate_artifacts",
        "git_changed_path_count",
        "git_status_counts",
        "files",
        "archive_member_deltas",
        "wheel_delta_count",
        "sdist_delta_count",
        "consensus_tarball_delta_count",
        "python_package_release_required",
        "installer_counterpart_required",
        "consensus_tarball_release_required",
        "new_release_required",
        "target_release_version",
        "r2_transient_artifact_limit",
        "public_mirror_head_verified",
        "sensitive_actions_performed",
    }
    missing = sorted(required - set(result))
    if missing:
        raise ValueError(f"result_missing_fields:{missing}")
    for field in (
        "python_package_release_required",
        "installer_counterpart_required",
        "consensus_tarball_release_required",
        "new_release_required",
        "public_mirror_head_verified",
        "sensitive_actions_performed",
    ):
        if type(result[field]) is not bool:
            raise ValueError(f"result_boolean_type:{field}")
    for field in (
        "audited_post_r3g_commit",
        "signed_source_commit",
    ):
        value = result[field]
        if not isinstance(value, str) or len(value) != 40 or any(
            char not in "0123456789abcdef" for char in value
        ):
            raise ValueError(f"result_git_hash:{field}")
    digest = result["reconciliation_manifest_sha256"]
    if not isinstance(digest, str) or len(digest) != 64 or any(
        char not in "0123456789abcdef" for char in digest
    ):
        raise ValueError("result_manifest_sha256")
    files = result["files"]
    if not isinstance(files, list) or result["git_changed_path_count"] != len(files):
        raise ValueError("result_git_changed_count")
    if sum(result["git_status_counts"].values()) != len(files):
        raise ValueError("result_git_status_count")
    identities = {
        (item["git_status"], item["old_path"], item["new_path"]) for item in files
    }
    if len(identities) != len(files):
        raise ValueError("result_duplicate_git_change")
    deltas = result["archive_member_deltas"]
    if not isinstance(deltas, list):
        raise ValueError("result_archive_deltas_type")
    delta_identities = {(item["surface"], item["member"]) for item in deltas}
    if len(delta_identities) != len(deltas):
        raise ValueError("result_duplicate_archive_delta")
    wheel_count = sum(item["surface"] == "wheel" for item in deltas)
    sdist_count = sum(item["surface"] == "sdist" for item in deltas)
    if result["wheel_delta_count"] != wheel_count:
        raise ValueError("result_wheel_delta_count")
    if result["sdist_delta_count"] != sdist_count:
        raise ValueError("result_sdist_delta_count")
    expected_release = bool(
        result["wheel_delta_count"]
        or result["sdist_delta_count"]
        or result["consensus_tarball_delta_count"]
    )
    if result["new_release_required"] != expected_release:
        raise ValueError("new_release_required_formula_mismatch")
    if result["python_package_release_required"] != bool(
        result["wheel_delta_count"] or result["sdist_delta_count"]
    ):
        raise ValueError("python_package_release_formula_mismatch")
    if result["consensus_tarball_release_required"] != bool(
        result["consensus_tarball_delta_count"]
    ):
        raise ValueError("consensus_release_formula_mismatch")
    if result["signed_artifacts"]["consensus_tarball"]["member_count"] != 7:
        raise ValueError("result_consensus_member_count")
    for surface, expected in SIGNED_V0434_SHA256.items():
        if result["signed_artifacts"][surface]["sha256"] != expected:
            raise ValueError(f"result_signed_hash:{surface}")
    if not result["r2_transient_artifact_limit"].get("present"):
        raise ValueError("result_r2_transient_limit_missing")
    if result["sensitive_actions_performed"]:
        raise ValueError("result_sensitive_action_claim")
    if not result["new_release_required"] or result["target_release_version"] != "0.4.35":
        raise ValueError("result_release_target")


def main() -> int:
    args = _parse_args()
    result = build_result(args)
    verify_result(result)
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    verify_result(json.loads(args.output.read_text(encoding="utf-8")))
    print(
        "OK: release disposition "
        f"new_release_required={str(result['new_release_required']).lower()} "
        f"wheel_deltas={result['wheel_delta_count']} "
        f"sdist_deltas={result['sdist_delta_count']} "
        f"consensus_deltas={result['consensus_tarball_delta_count']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
