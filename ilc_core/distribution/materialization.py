# SPDX-License-Identifier: AGPL-3.0-only
"""Public-RC reference implementation materialization helpers.

PUBLIC_RC_EXCLUDE: fix83_materialization_bootstrap_reference_impl
PUBLIC_RC_EXCLUDE_REASON: Pre-RC reference implementation materialization path.
It verifies identity and hashes for the Python reference implementation; it
does not sign Genesis material, activate public RC, or claim behavioral-spec
conformance.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from ilc_core.storage.genesis_atlas_lmdb_writer import repo_file_ref_id


PUBLIC_RC_PROFILE_SCHEMA_VERSION = "ilc_public_rc_package_profile_1545p_fix83.v0.1"
MATERIALIZATION_MANIFEST_SCHEMA_VERSION = (
    "ilc_public_rc_materialization_manifest_1545p_fix83.v0.1"
)
BUILD_RECIPE_SCHEMA_VERSION = "ilc_public_rc_build_recipe_1545p_fix83.v0.1"
RECONSTRUCTION_RECEIPT_SCHEMA_VERSION = (
    "ilc_public_rc_reconstruction_receipt_1545p_fix83.v0.1"
)
PROFILE_NAME = "ilc-public-rc"
GENESIS_ROOT = "artifact:genesis_intent_attestation_init_authority_map"
DEFAULT_GRAPH_ROOT = "out/genesis_base_graph_v0.4_unified.lmdb"
RECONSTRUCTION_NOTES = (
    "Reference implementation materialization only. Not a behavioral-spec conformance receipt."
)
DEFAULT_MAX_TOTAL_BYTES = 256 * 1024 * 1024
DEFAULT_HTTP_TIMEOUT_SECONDS = 30


class MaterializationError(ValueError):
    """Stable error type for Fix83 materialization failures."""


@dataclass(frozen=True)
class FetchSources:
    cache_dir: Path | None = None
    repo_root: Path | None = None
    tarball: Path | None = None
    http_base_url: str = ""
    timeout_seconds: int = DEFAULT_HTTP_TIMEOUT_SECONDS


def canonical_json(payload: Any, *, indent: int | None = None) -> str:
    if indent is None:
        return json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return json.dumps(payload, sort_keys=True, indent=indent, allow_nan=False)


def write_json_atomic(path: Path, payload: Any, *, indent: int | None = 2) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(
        dir=str(path.parent),
        prefix=f".{path.name}.",
        suffix=".tmp",
        text=True,
    )
    tmp_path = Path(tmp_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(canonical_json(payload, indent=indent))
            handle.write("\n")
        os.replace(tmp_path, path)
        path.chmod(0o644)
    except Exception:
        try:
            tmp_path.unlink()
        except FileNotFoundError:
            pass
        raise


def load_json_object(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise MaterializationError(f"json_not_object:{path}")
    return payload


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path, *, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_public_rc_profile(
    *,
    fix65_manifest: Mapping[str, Any],
    fix82_report: Mapping[str, Any] | None = None,
    graph_root: str = DEFAULT_GRAPH_ROOT,
) -> dict[str, Any]:
    members = fix65_manifest.get("members")
    if not isinstance(members, list):
        raise MaterializationError("fix65_manifest_members_missing")
    files: list[dict[str, Any]] = []
    for member in sorted(members, key=lambda item: str(item.get("source_path", ""))):
        source_path = _required_str(member, "source_path")
        source_sha256 = _required_sha256(member, "source_sha256")
        files.append(
            {
                "content_node_id": _required_str(member, "candidate_id"),
                "node_id": repo_file_ref_id(source_path),
                "package_membership": True,
                "size_bytes": _required_non_negative_int(member, "size_bytes"),
                "source_path": source_path,
                "source_sha256": source_sha256,
            }
        )
    report_summary = {}
    if fix82_report:
        report_summary = {
            "fix82_status": fix82_report.get("status", ""),
            "fix82_manifest_sha256": fix82_report.get("fix65_manifest_refresh", {}).get(
                "manifest_sha256", ""
            ),
        }
    profile = {
        "file_count": len(files),
        "files": files,
        "genesis_root": GENESIS_ROOT,
        "graph_root": graph_root,
        "non_claims": [
            "not_language_agnostic",
            "not_behavioral_spec_conformance",
            "not_genesis_signing",
            "not_public_rc_activation",
        ],
        "package_manifest_sha256": _required_sha256(fix65_manifest, "manifest_sha256"),
        "package_merkle_root_m0": _required_sha256(fix65_manifest, "merkle_root_m0"),
        "profile_name": PROFILE_NAME,
        "schema_version": PUBLIC_RC_PROFILE_SCHEMA_VERSION,
        "signed": False,
        "source_fix82": report_summary,
    }
    return profile


def generate_materialization_manifest(profile: Mapping[str, Any]) -> dict[str, Any]:
    if profile.get("profile_name") != PROFILE_NAME:
        raise MaterializationError("profile_name_invalid")
    if profile.get("signed") is not False:
        raise MaterializationError("profile_signed_false_required")
    files = profile.get("files")
    if not isinstance(files, list):
        raise MaterializationError("profile_files_missing")
    manifest_files = []
    total_size = 0
    for item in sorted(files, key=lambda row: str(row.get("source_path", ""))):
        source_path = _required_str(item, "source_path")
        source_sha256 = _required_sha256(item, "source_sha256")
        size_bytes = _required_non_negative_int(item, "size_bytes")
        total_size += size_bytes
        manifest_files.append(
            {
                "content_node_id": _required_str(item, "content_node_id"),
                "destination_path": source_path,
                "node_id": _required_str(item, "node_id"),
                "size_bytes": size_bytes,
                "source_path": source_path,
                "source_sha256": source_sha256,
            }
        )
    manifest = {
        "file_count": len(manifest_files),
        "files": manifest_files,
        "genesis_root": _required_str(profile, "genesis_root"),
        "graph_root": _required_str(profile, "graph_root"),
        "manifest_sha256": "",
        "profile_name": _required_str(profile, "profile_name"),
        "schema_version": MATERIALIZATION_MANIFEST_SCHEMA_VERSION,
        "signed": False,
        "total_size_bytes": total_size,
    }
    manifest["manifest_sha256"] = sha256_bytes(
        canonical_json({**manifest, "manifest_sha256": ""}).encode("utf-8")
    )
    return manifest


def validate_manifest(manifest: Mapping[str, Any], *, max_total_bytes: int) -> list[dict[str, Any]]:
    if manifest.get("signed") is not False:
        raise MaterializationError("manifest_signed_false_required")
    files = manifest.get("files")
    if not isinstance(files, list):
        raise MaterializationError("manifest_files_missing")
    total = 0
    validated = []
    seen: set[str] = set()
    for raw in files:
        if not isinstance(raw, dict):
            raise MaterializationError("manifest_file_entry_not_object")
        dest = _safe_relative_path(_required_str(raw, "destination_path"))
        if dest.as_posix() in seen:
            raise MaterializationError(f"duplicate_destination_path:{dest.as_posix()}")
        seen.add(dest.as_posix())
        size = _required_non_negative_int(raw, "size_bytes")
        total += size
        if total > max_total_bytes:
            raise MaterializationError("manifest_total_size_exceeds_cap")
        validated.append(
            {
                **raw,
                "destination_path": dest.as_posix(),
                "source_path": _safe_relative_path(_required_str(raw, "source_path")).as_posix(),
                "source_sha256": _required_sha256(raw, "source_sha256"),
                "size_bytes": size,
            }
        )
    return validated


def fetch_file_bytes(
    entry: Mapping[str, Any],
    *,
    sources: FetchSources,
    max_file_bytes: int,
) -> bytes:
    expected = _required_sha256(entry, "source_sha256")
    source_path = _safe_relative_path(_required_str(entry, "source_path")).as_posix()
    expected_size = _required_non_negative_int(entry, "size_bytes")
    if expected_size > max_file_bytes:
        raise MaterializationError(f"file_exceeds_size_cap:{source_path}")

    attempts: list[tuple[str, bytes | None]] = []
    if sources.cache_dir is not None:
        attempts.append(("cache", _read_cache_candidate(sources.cache_dir, expected, max_file_bytes)))
    if sources.repo_root is not None:
        attempts.append(("repo", _read_repo_candidate(sources.repo_root, source_path, max_file_bytes)))
    if sources.tarball is not None:
        attempts.append(("tarball", _read_tarball_candidate(sources.tarball, source_path, max_file_bytes)))
    if sources.http_base_url:
        attempts.append(
            (
                "http",
                _read_http_candidate(
                    sources.http_base_url,
                    source_path,
                    max_file_bytes,
                    timeout_seconds=sources.timeout_seconds,
                ),
            )
        )

    for _source_name, data in attempts:
        if data is None:
            continue
        if len(data) != expected_size:
            continue
        if sha256_bytes(data) == expected:
            return data
    raise MaterializationError(f"bytes_not_found_with_matching_hash:{source_path}")


def materialize_tree(
    manifest: Mapping[str, Any],
    *,
    out_dir: Path,
    sources: FetchSources,
    max_total_bytes: int = DEFAULT_MAX_TOTAL_BYTES,
    overwrite: bool = False,
) -> dict[str, Any]:
    entries = validate_manifest(manifest, max_total_bytes=max_total_bytes)
    _validate_output_root(out_dir)
    if out_dir.exists():
        if not overwrite:
            raise MaterializationError(f"output_exists:{out_dir}")
        if out_dir.is_symlink():
            raise MaterializationError(f"output_symlink_forbidden:{out_dir}")
        shutil.rmtree(out_dir)
    parent = out_dir.parent
    parent.mkdir(parents=True, exist_ok=True)
    tmp_root = Path(tempfile.mkdtemp(dir=str(parent), prefix=f".{out_dir.name}.tmp."))
    written = 0
    try:
        for entry in entries:
            relative = Path(str(entry["destination_path"]))
            target = _resolve_under_root(tmp_root, relative)
            data = fetch_file_bytes(
                entry,
                sources=sources,
                max_file_bytes=max_total_bytes,
            )
            _write_file_atomic(target, data)
            written += 1
        os.replace(tmp_root, out_dir)
    except Exception:
        shutil.rmtree(tmp_root, ignore_errors=True)
        raise
    return {
        "files_materialized": written,
        "output_dir": str(out_dir),
        "total_size_bytes": sum(int(entry["size_bytes"]) for entry in entries),
    }


def verify_materialized_tree(
    manifest: Mapping[str, Any],
    *,
    root: Path,
    max_total_bytes: int = DEFAULT_MAX_TOTAL_BYTES,
) -> dict[str, Any]:
    entries = validate_manifest(manifest, max_total_bytes=max_total_bytes)
    verified = 0
    missing = []
    mismatches = []
    for entry in entries:
        target = _resolve_under_root(root, Path(str(entry["destination_path"])))
        if not target.exists():
            missing.append(str(entry["destination_path"]))
            continue
        if target.is_symlink():
            mismatches.append({"path": str(entry["destination_path"]), "reason": "symlink_forbidden"})
            continue
        actual = sha256_file(target)
        if actual != entry["source_sha256"]:
            mismatches.append(
                {
                    "actual_sha256": actual,
                    "expected_sha256": entry["source_sha256"],
                    "path": str(entry["destination_path"]),
                }
            )
            continue
        verified += 1
    return {
        "files_failed": len(missing) + len(mismatches),
        "files_missing": len(missing),
        "files_mismatched": len(mismatches),
        "files_verified": verified,
        "missing": missing,
        "mismatches": mismatches,
        "ok": not missing and not mismatches,
    }


def run_build_recipe(
    recipe: Mapping[str, Any],
    *,
    cwd: Path,
    timeout_seconds: int = 120,
) -> dict[str, Any]:
    commands = recipe.get("commands")
    if not isinstance(commands, list):
        raise MaterializationError("build_recipe_commands_missing")
    results = []
    for command in commands:
        if not isinstance(command, dict):
            raise MaterializationError("build_recipe_command_not_object")
        argv = command.get("argv")
        if not isinstance(argv, list) or not all(isinstance(item, str) and item for item in argv):
            raise MaterializationError("build_recipe_argv_invalid")
        proc = subprocess.run(
            [sys.executable if item == "python" else item for item in argv],
            cwd=cwd,
            text=True,
            capture_output=True,
            timeout=timeout_seconds,
            check=False,
        )
        result = {
            "command_id": command.get("id", ""),
            "returncode": proc.returncode,
            "stderr_tail": proc.stderr[-1000:],
            "stdout_tail": proc.stdout[-1000:],
        }
        results.append(result)
        if proc.returncode != 0:
            return {"commands": results, "ok": False}
    return {"commands": results, "ok": True}


def build_reconstruction_receipt(
    *,
    profile: Mapping[str, Any],
    manifest: Mapping[str, Any],
    materialization: Mapping[str, Any],
    verification: Mapping[str, Any],
    recipe_result: Mapping[str, Any] | None,
) -> dict[str, Any]:
    recipe_ok = bool(recipe_result and recipe_result.get("ok") is True)
    receipt = {
        "build_recipe_passed": recipe_ok,
        "build_recipe_status": "passed" if recipe_ok else "not_run_or_failed",
        "files_failed": int(verification.get("files_failed", 0)),
        "files_materialized": int(materialization.get("files_materialized", 0)),
        "files_verified": int(verification.get("files_verified", 0)),
        "genesis_root": _required_str(profile, "genesis_root"),
        "graph_root_path": _required_str(profile, "graph_root"),
        "manifest_sha256": _required_sha256(manifest, "manifest_sha256"),
        "materialization_timestamp_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "notes": RECONSTRUCTION_NOTES,
        "profile_name": _required_str(profile, "profile_name"),
        "receipt_type": "reconstruction_receipt",
        "recipe_result": recipe_result or {"ok": False, "reason": "not_run"},
        "schema_version": RECONSTRUCTION_RECEIPT_SCHEMA_VERSION,
        "signed": False,
        "test_count_passed": _test_count_passed(recipe_result),
    }
    return receipt


def bootstrap(
    *,
    profile_path: Path,
    out_dir: Path,
    receipt_path: Path,
    verify: bool,
    repo_root: Path,
    cache_dir: Path | None = None,
    tarball: Path | None = None,
    http_base_url: str = "",
    max_total_bytes: int = DEFAULT_MAX_TOTAL_BYTES,
    recipe_path: Path | None = None,
    run_recipe: bool = False,
    recipe_timeout_seconds: int = 120,
    overwrite: bool = False,
) -> dict[str, Any]:
    profile = load_json_object(profile_path)
    manifest = generate_materialization_manifest(profile)
    sources = FetchSources(
        cache_dir=cache_dir,
        repo_root=repo_root,
        tarball=tarball,
        http_base_url=http_base_url,
    )
    materialization = materialize_tree(
        manifest,
        out_dir=out_dir,
        sources=sources,
        max_total_bytes=max_total_bytes,
        overwrite=overwrite,
    )
    verification = (
        verify_materialized_tree(manifest, root=out_dir, max_total_bytes=max_total_bytes)
        if verify
        else {"files_failed": 0, "files_verified": 0, "ok": True}
    )
    if not verification.get("ok"):
        raise MaterializationError("materialized_tree_hash_verification_failed")
    recipe_result = None
    if run_recipe:
        if recipe_path is None:
            raise MaterializationError("recipe_path_required_when_run_recipe")
        recipe_result = run_build_recipe(
            load_json_object(recipe_path),
            cwd=out_dir,
            timeout_seconds=recipe_timeout_seconds,
        )
        if not recipe_result.get("ok"):
            raise MaterializationError("build_recipe_failed")
    receipt = build_reconstruction_receipt(
        profile=profile,
        manifest=manifest,
        materialization=materialization,
        verification=verification,
        recipe_result=recipe_result,
    )
    write_json_atomic(receipt_path, receipt, indent=2)
    return {
        "manifest": {
            "file_count": manifest["file_count"],
            "manifest_sha256": manifest["manifest_sha256"],
            "total_size_bytes": manifest["total_size_bytes"],
        },
        "materialization": materialization,
        "receipt_path": str(receipt_path),
        "verification": verification,
    }


def _read_cache_candidate(cache_dir: Path, expected_sha256: str, max_bytes: int) -> bytes | None:
    for candidate in (cache_dir / expected_sha256, cache_dir / expected_sha256[:2] / expected_sha256):
        if candidate.is_file():
            if candidate.is_symlink():
                raise MaterializationError(f"cache_symlink_forbidden:{candidate}")
            return _read_bounded(candidate, max_bytes)
    return None


def _read_repo_candidate(repo_root: Path, source_path: str, max_bytes: int) -> bytes | None:
    path = _resolve_under_root(repo_root, Path(source_path))
    if not path.exists():
        return None
    if not path.is_file() or path.is_symlink():
        raise MaterializationError(f"repo_source_invalid:{source_path}")
    return _read_bounded(path, max_bytes)


def _read_tarball_candidate(tarball: Path, source_path: str, max_bytes: int) -> bytes | None:
    if tarball.is_symlink() or not tarball.is_file():
        raise MaterializationError(f"tarball_invalid:{tarball}")
    with tarfile.open(tarball, "r:*") as archive:
        for member in archive.getmembers():
            normalized = member.name.removeprefix("./")
            if normalized == source_path or normalized.endswith("/" + source_path):
                if not member.isfile():
                    raise MaterializationError(f"tarball_member_not_file:{member.name}")
                if member.size > max_bytes:
                    raise MaterializationError(f"tarball_member_too_large:{member.name}")
                extracted = archive.extractfile(member)
                if extracted is None:
                    return None
                data = extracted.read(max_bytes + 1)
                if len(data) > max_bytes:
                    raise MaterializationError(f"tarball_member_too_large:{member.name}")
                return data
    return None


def _read_http_candidate(
    base_url: str,
    source_path: str,
    max_bytes: int,
    *,
    timeout_seconds: int,
) -> bytes | None:
    url = urllib.parse.urljoin(base_url.rstrip("/") + "/", urllib.parse.quote(source_path))
    request = urllib.request.Request(url, headers={"User-Agent": "ilc-fix83-materializer/0.1"})
    try:
        with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
            data = response.read(max_bytes + 1)
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return None
        raise MaterializationError(f"http_fetch_failed:{exc.code}:{source_path}") from exc
    except urllib.error.URLError as exc:
        raise MaterializationError(f"http_fetch_failed:{source_path}") from exc
    if len(data) > max_bytes:
        raise MaterializationError(f"http_response_too_large:{source_path}")
    return data


def _read_bounded(path: Path, max_bytes: int) -> bytes:
    if path.stat().st_size > max_bytes:
        raise MaterializationError(f"file_too_large:{path}")
    return path.read_bytes()


def _write_file_atomic(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.parent.is_symlink():
        raise MaterializationError(f"destination_parent_symlink_forbidden:{path.parent}")
    fd, tmp_name = tempfile.mkstemp(dir=str(path.parent), prefix=f".{path.name}.", suffix=".tmp")
    tmp_path = Path(tmp_name)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
        os.replace(tmp_path, path)
    except Exception:
        try:
            tmp_path.unlink()
        except FileNotFoundError:
            pass
        raise


def _safe_relative_path(raw: str) -> Path:
    if raw.startswith("~"):
        raise MaterializationError(f"path_home_forbidden:{raw}")
    path = Path(raw)
    if path.is_absolute():
        raise MaterializationError(f"path_absolute_forbidden:{raw}")
    if ".." in path.parts:
        raise MaterializationError(f"path_traversal_forbidden:{raw}")
    if not raw or raw in {".", "./"}:
        raise MaterializationError("path_empty_forbidden")
    return path


def _validate_output_root(root: Path) -> None:
    if root.is_absolute():
        return
    if ".." in root.parts:
        raise MaterializationError(f"output_path_traversal_forbidden:{root}")


def _resolve_under_root(root: Path, relative: Path) -> Path:
    safe = _safe_relative_path(relative.as_posix())
    root_resolved = root.resolve()
    candidate = (root_resolved / safe).resolve()
    try:
        candidate.relative_to(root_resolved)
    except ValueError as exc:
        raise MaterializationError(f"path_escape_forbidden:{relative}") from exc
    return candidate


def _required_str(payload: Mapping[str, Any], key: str) -> str:
    value = payload.get(key)
    if not isinstance(value, str) or not value:
        raise MaterializationError(f"required_string_missing:{key}")
    return value


def _required_sha256(payload: Mapping[str, Any], key: str) -> str:
    value = _required_str(payload, key)
    if len(value) != 64 or any(char not in "0123456789abcdef" for char in value):
        raise MaterializationError(f"sha256_invalid:{key}")
    return value


def _required_non_negative_int(payload: Mapping[str, Any], key: str) -> int:
    value = payload.get(key)
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise MaterializationError(f"non_negative_int_invalid:{key}")
    return value


def _test_count_passed(recipe_result: Mapping[str, Any] | None) -> int:
    if not recipe_result or recipe_result.get("ok") is not True:
        return 0
    return sum(1 for command in recipe_result.get("commands", []) if command.get("returncode") == 0)


def cli_generate_manifest(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate an ILC materialization manifest")
    parser.add_argument("--profile", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args(argv)
    manifest = generate_materialization_manifest(load_json_object(Path(args.profile)))
    write_json_atomic(Path(args.out), manifest, indent=2)
    return 0


def cli_verify(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Verify an ILC materialized tree")
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--root", required=True)
    parser.add_argument("--max-total-bytes", type=int, default=DEFAULT_MAX_TOTAL_BYTES)
    args = parser.parse_args(argv)
    result = verify_materialized_tree(
        load_json_object(Path(args.manifest)),
        root=Path(args.root),
        max_total_bytes=args.max_total_bytes,
    )
    print(canonical_json(result))
    return 0 if result["ok"] else 1


__all__ = [
    "BUILD_RECIPE_SCHEMA_VERSION",
    "DEFAULT_MAX_TOTAL_BYTES",
    "GENESIS_ROOT",
    "MATERIALIZATION_MANIFEST_SCHEMA_VERSION",
    "PROFILE_NAME",
    "PUBLIC_RC_PROFILE_SCHEMA_VERSION",
    "RECONSTRUCTION_NOTES",
    "RECONSTRUCTION_RECEIPT_SCHEMA_VERSION",
    "FetchSources",
    "MaterializationError",
    "bootstrap",
    "build_public_rc_profile",
    "generate_materialization_manifest",
    "materialize_tree",
    "verify_materialized_tree",
    "write_json_atomic",
]
