#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
"""Build and verify the unsigned v0.4.35 reconciliation attestation."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import re
import stat
import subprocess
import sys
import tarfile
import tempfile
import warnings
import zipfile
from pathlib import Path, PurePosixPath
from typing import Any, Iterable, Mapping

from ilc_core.encoding.cidv1 import node_id_from_obj
from ilc_core.release.release_assertion_schema import (
    ARTIFACT_NODE_FIELDS,
    ASSERTION_REQUIRED_FIELDS,
    BUILD_RECIPE_NODE_FIELDS,
    SOFTWARE_RELEASE_NODE_FIELDS,
)


SCHEMA_VERSION = "ilc.reconciliation.v0435.build_attestation.v0.1"
PHASE = "GAP-RC-NATIVE-DISTRIBUTION-CLOSURE-RECONCILIATION-SOURCE-FREEZE-BUILD-00"
VERSION = "0.4.35"
SOURCE_COMMIT = "c91bae2d0c03aeaebe7c902b848634bf4abfd297"
SOURCE_DATE = "2026-10-28T00:24:15Z"
MANIFEST_SHA256 = "b35db1f0d76a763d51be605822ed40a87c63a684425c342015f6e91ccf174497"
R4_SHA256 = "61e8c15c397a09852346c82c7254242485a0fa9fbe11565c537c6ca2488ac951"
CONSENSUS_SHA256 = "9e7bcc2a8737a785e6ad69b9abcafc4788bc0e73150c0a82d6e51d84a8473f9f"
CONSENSUS_TREE_OID = "db9fa9bb013a06fec07ab2d359a3e7b1ebb44a93"
PRIOR_RELEASE_SOURCE_COMMIT = "63b4d8db9313250d9ccd20bef91501732f32177f"
MAX_ARCHIVE_BYTES = 20 * 1024 * 1024
MAX_MEMBER_BYTES = 20 * 1024 * 1024
MAX_TOTAL_BYTES = 100 * 1024 * 1024
MAX_MEMBERS = 10_000
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")
ARTIFACT_ID_RE = re.compile(r"^ilc-artifact:[a-z0-9][a-z0-9-]*@phase-[1-9][0-9]*$")
REQUIRED_SUFFICIENCY_MEMBERS = {
    "ilc_core/sufficiency/__init__.py",
    "ilc_core/sufficiency/local_interp.py",
    "ilc_core/sufficiency/model_selector.py",
}


class AttestationError(ValueError):
    """Stable-token validation failure."""

    def __init__(self, token: str) -> None:
        super().__init__(token)
        self.token = token


def _require(condition: bool, token: str) -> None:
    if not condition:
        raise AttestationError(token)


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def _canonical_bytes(value: Mapping[str, Any]) -> bytes:
    return json.dumps(
        dict(value), sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False
    ).encode("utf-8")


def _git_paths(*args: str) -> list[str]:
    output = subprocess.check_output(
        ["git", *args], text=True, stderr=subprocess.DEVNULL
    )
    return sorted(line for line in output.splitlines() if line)


def _git_output(*args: str) -> str:
    return subprocess.check_output(
        ["git", *args], text=True, stderr=subprocess.DEVNULL
    ).strip()


def _atomic_json(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    encoded = json.dumps(dict(value), sort_keys=True, indent=2, allow_nan=False) + "\n"
    fd, name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(encoded)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(name, path)
    except Exception:
        try:
            Path(name).unlink()
        except FileNotFoundError:
            pass
        raise


def _safe_name(raw: str) -> str:
    _require(isinstance(raw, str) and raw != "", "archive_member_name_invalid")
    _require("\\" not in raw, "archive_member_backslash")
    path = PurePosixPath(raw)
    _require(not path.is_absolute(), "archive_member_absolute")
    _require(all(part not in {"", ".", ".."} for part in path.parts), "archive_member_unsafe")
    return path.as_posix()


def _bounded_path(path: Path) -> Path:
    path = path.resolve(strict=True)
    _require(path.is_file(), "archive_not_regular_file")
    _require(path.stat().st_size <= MAX_ARCHIVE_BYTES, "archive_size_limit_exceeded")
    return path


def _hash_stream(chunks: Iterable[bytes], expected_size: int) -> str:
    digest = hashlib.sha256()
    total = 0
    for chunk in chunks:
        total += len(chunk)
        _require(total <= MAX_MEMBER_BYTES, "archive_member_size_limit_exceeded")
        digest.update(chunk)
    _require(total == expected_size, "archive_member_size_mismatch")
    return digest.hexdigest()


def inspect_zip(path: Path) -> dict[str, Any]:
    path = _bounded_path(path)
    members: dict[str, dict[str, Any]] = {}
    total = 0
    with zipfile.ZipFile(path) as archive:
        infos = archive.infolist()
        _require(len(infos) <= MAX_MEMBERS, "archive_member_count_limit_exceeded")
        for info in infos:
            name = _safe_name(info.filename.rstrip("/") if info.is_dir() else info.filename)
            _require(name not in members, "archive_duplicate_member")
            mode = (info.external_attr >> 16) & 0xFFFF
            if mode:
                _require(not stat.S_ISLNK(mode), "archive_link_not_allowed")
                file_type = stat.S_IFMT(mode)
                _require(
                    file_type == 0 or info.is_dir() or stat.S_ISREG(mode),
                    "archive_member_type_not_allowed",
                )
            _require(info.file_size <= MAX_MEMBER_BYTES, "archive_member_size_limit_exceeded")
            total += info.file_size
            _require(total <= MAX_TOTAL_BYTES, "archive_total_size_limit_exceeded")
            digest = None
            if not info.is_dir():
                with archive.open(info, "r") as handle:
                    digest = _hash_stream(iter(lambda: handle.read(1024 * 1024), b""), info.file_size)
            members[name] = {
                "type": "directory" if info.is_dir() else "file",
                "size": info.file_size,
                "sha256": digest,
                "mode": mode & 0o7777,
            }
    return {
        "path": str(path),
        "filename": path.name,
        "sha256": _sha256_path(path),
        "size_bytes": path.stat().st_size,
        "member_count": len(members),
        "members": members,
    }


def inspect_tar(path: Path, *, single_root: bool) -> dict[str, Any]:
    path = _bounded_path(path)
    members: dict[str, dict[str, Any]] = {}
    total = 0
    roots: set[str] = set()
    with tarfile.open(path, "r:gz") as archive:
        infos = archive.getmembers()
        _require(len(infos) <= MAX_MEMBERS, "archive_member_count_limit_exceeded")
        for info in infos:
            name = _safe_name(info.name.rstrip("/") if info.isdir() else info.name)
            _require(name not in members, "archive_duplicate_member")
            roots.add(PurePosixPath(name).parts[0])
            _require(not (info.issym() or info.islnk()), "archive_link_not_allowed")
            _require(info.isfile() or info.isdir(), "archive_member_type_not_allowed")
            _require(info.size <= MAX_MEMBER_BYTES, "archive_member_size_limit_exceeded")
            total += info.size
            _require(total <= MAX_TOTAL_BYTES, "archive_total_size_limit_exceeded")
            digest = None
            if info.isfile():
                handle = archive.extractfile(info)
                _require(handle is not None, "archive_member_unreadable")
                with handle:
                    digest = _hash_stream(iter(lambda: handle.read(1024 * 1024), b""), info.size)
            members[name] = {
                "type": "directory" if info.isdir() else "file",
                "size": info.size,
                "sha256": digest,
                "mode": info.mode,
                "uid": info.uid,
                "gid": info.gid,
                "uname": info.uname,
                "gname": info.gname,
                "linkname": info.linkname,
                "mtime": info.mtime,
            }
    if single_root:
        _require(len(roots) == 1, "sdist_single_root_required")
    return {
        "path": str(path),
        "filename": path.name,
        "sha256": _sha256_path(path),
        "size_bytes": path.stat().st_size,
        "member_count": len(members),
        "members": members,
    }


def _normalized_sdist_members(inspection: Mapping[str, Any]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    members = inspection["members"]
    _require(isinstance(members, dict), "sdist_members_invalid")
    for name, entry in members.items():
        parts = PurePosixPath(name).parts
        _require(len(parts) >= 1, "sdist_member_name_invalid")
        key = PurePosixPath(*parts[1:]).as_posix() if len(parts) > 1 else "."
        _require(key not in result, "sdist_normalized_member_duplicate")
        result[key] = {k: v for k, v in entry.items() if k != "mtime"}
    return result


def compare_builds(wheel1: Path, wheel2: Path, sdist1: Path, sdist2: Path) -> dict[str, Any]:
    w1, w2 = inspect_zip(wheel1), inspect_zip(wheel2)
    s1, s2 = inspect_tar(sdist1, single_root=True), inspect_tar(sdist2, single_root=True)
    wheel_equal = w1["sha256"] == w2["sha256"]
    _require(wheel_equal, "wheel_not_byte_identical")
    _require(w1["members"] == w2["members"], "wheel_member_map_mismatch")
    ns1, ns2 = _normalized_sdist_members(s1), _normalized_sdist_members(s2)
    _require(ns1 == ns2, "sdist_content_or_structure_mismatch")
    required_wheel = REQUIRED_SUFFICIENCY_MEMBERS
    required_sdist = {f"ilc_core-0.4.35/{name}" for name in REQUIRED_SUFFICIENCY_MEMBERS}
    _require(required_wheel <= set(w1["members"]), "wheel_sufficiency_members_missing")
    _require(required_sdist <= set(s1["members"]), "sdist_sufficiency_members_missing")
    sdist_equal = s1["sha256"] == s2["sha256"]
    return {
        "wheel": {"byte_identical": wheel_equal, "run1": w1, "run2": w2},
        "sdist": {
            "byte_identical": sdist_equal,
            "classification": "byte_reproducible" if sdist_equal else "content_equal_archive_not_reproducible",
            "member_names_equal": set(s1["members"]) == set(s2["members"]),
            "member_payloads_and_non_time_metadata_equal": True,
            "run1": s1,
            "run2": s2,
        },
    }


def _module_path(module: Any) -> str:
    value = getattr(module, "__file__", None)
    _require(isinstance(value, str) and value != "", "smoke_module_path_missing")
    return str(Path(value).resolve(strict=True))


def run_smoke(output: Path) -> dict[str, Any]:
    import ilc_core
    import ilc_core.sufficiency as sufficiency
    import ilc_core.sufficiency.local_interp as local_interp
    import ilc_core.sufficiency.model_selector as model_selector

    prefix = Path(sys.prefix).resolve(strict=True)
    module_paths = {
        "ilc_core": _module_path(ilc_core),
        "sufficiency": _module_path(sufficiency),
        "local_interp": _module_path(local_interp),
        "model_selector": _module_path(model_selector),
    }
    for path in module_paths.values():
        _require(Path(path).is_relative_to(prefix), "smoke_workspace_import_detected")

    def add(left: int, right: int) -> dict[str, int]:
        return {"result": left + right}

    operation = sufficiency.OperationDefinition(
        "add", "1", "fixture:r5a:add:v1", (("left", 0), ("right", 1)), ("result",), add
    )
    recipe = {
        "schema_version": local_interp.RECIPE_SCHEMA_VERSION,
        "recipe_version": "r5a-smoke",
        "execution_profile": local_interp.EXECUTION_PROFILE,
        "inputs": [{"name": "a", "type": "integer"}, {"name": "b", "type": "integer"}],
        "steps": [{
            "step_id": "sum",
            "operation_ref": {"operation_id": "add", "operation_version": "1", "implementation_ref": "fixture:r5a:add:v1"},
            "bindings": [
                {"role_name": "left", "ordinal": 0, "value_ref": "input:a"},
                {"role_name": "right", "ordinal": 1, "value_ref": "input:b"},
            ],
            "outputs": ["result"],
            "effects": [],
        }],
        "outputs": [{"name": "value", "value_ref": "value:result"}],
        "effects": [],
        "limits": {"expanded_steps": 1},
    }
    receipt = sufficiency.execute_recipe(
        store=sufficiency.LocalFixtureStore((operation,)),
        recipe=recipe,
        inputs={"a": 2, "b": 3},
        root_invocation_id="fixture:r5a:installed-smoke",
        completed_at="2026-10-27T00:00:00Z",
    )
    _require(receipt["output_values"] == {"value": 5}, "smoke_local_fixture_failed")
    try:
        sufficiency.execute_recipe(
            store=object(), recipe={"malformed": True}, inputs={}, root_invocation_id="fixture:r5a:guard"
        )
    except sufficiency.InterpGuardError:
        interp_guard = True
    else:
        interp_guard = False
    _require(interp_guard, "smoke_interp_guard_failed")

    class ExternalBackend:
        calls = 0

        def propose(self, candidates: Any, request: Any) -> Any:
            del candidates, request
            self.calls += 1
            return sufficiency.ModelProposal("candidate", "1")

    candidate = sufficiency.Candidate(
        "candidate", "1", "fixture:r5a:operation", "fixture:r5a:policy"
    )
    request = sufficiency.SelectionRequest(
        "fixture:r5a:request", candidate.operation_ref, candidate.policy_ref, 0
    )
    backend = ExternalBackend()
    try:
        sufficiency.select_candidate(
            candidates=(candidate,),
            request=request,
            backend=backend,
            evaluate_eligibility=lambda item, req: sufficiency.EligibilityDecision(True, "ok", (), 0),
        )
    except sufficiency.ModelSelectorGuardError:
        selector_guard = backend.calls == 0
    else:
        selector_guard = False
    _require(selector_guard, "smoke_model_selector_guard_failed")
    result = {
        "schema_version": "ilc.reconciliation.v0435.installed_smoke.v0.1",
        "version": ilc_core.__version__,
        "python_prefix": str(prefix),
        "module_paths": module_paths,
        "sufficiency_public_exports": sorted(sufficiency.__all__),
        "local_fixture_output": receipt["output_values"],
        "local_interp_guard_false": sufficiency.SUFFICIENCY_LOCAL_INTERP_ENABLED is False,
        "model_selector_guard_false": sufficiency.MODEL_SELECTOR_ENABLED is False,
        "nonfixture_interp_denied": interp_guard,
        "nonfixture_model_backend_denied": selector_guard,
    }
    verify_smoke(result)
    _atomic_json(output, result)
    return result


def verify_smoke(value: Mapping[str, Any]) -> None:
    _require(value.get("version") == VERSION, "smoke_version_mismatch")
    for field in (
        "local_interp_guard_false", "model_selector_guard_false",
        "nonfixture_interp_denied", "nonfixture_model_backend_denied",
    ):
        _require(value.get(field) is True, f"smoke_boolean_invalid:{field}")
    paths = value.get("module_paths")
    _require(isinstance(paths, dict) and set(paths) == {"ilc_core", "sufficiency", "local_interp", "model_selector"}, "smoke_module_paths_invalid")
    prefix = Path(str(value.get("python_prefix", ""))).resolve(strict=True)
    for path in paths.values():
        _require(Path(str(path)).resolve(strict=True).is_relative_to(prefix), "smoke_workspace_import_detected")


def _artifact_node(*, artifact_type: str, filename: str, sha256: str, size_bytes: int, version: str) -> dict[str, Any]:
    body = {
        "artifact_id": f"ilc-artifact:{artifact_type.replace('_', '-')}-{version.replace('.', '')}@phase-1628",
        "artifact_type": artifact_type,
        "filename": filename,
        "node_kind": "ArtifactNode",
        "package_name": "ilc-core",
        "package_version": version,
        "pypi_url": f"pending-r5b:{filename}",
        "schema_version": "artifact_node.v0.1",
        "sha256": sha256,
        "size_bytes": size_bytes,
    }
    return {**body, "cid": node_id_from_obj(body)}


def _read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    _require(isinstance(value, dict), "json_root_not_object")
    return value


def _suite_record(root: Path) -> dict[str, Any]:
    exit_status = int((root / "exit_status.txt").read_text(encoding="utf-8").strip())
    _require(exit_status == 0, "full_suite_nonzero")
    junit = root / "junit.xml"
    stdout = root / "stdout.txt"
    freeze = root / "pip_freeze.txt"
    for path in (junit, stdout, freeze):
        _require(path.is_file(), "suite_artifact_missing")
    freeze_text = freeze.read_text(encoding="utf-8")
    _require(
        f"@{SOURCE_COMMIT}#egg=ilc_core" in freeze_text,
        "full_suite_source_commit_unbound",
    )
    sidecar_matches = re.findall(
        r"ilc-graphics-sidecar\.git@([0-9a-f]{40})#egg=ilc_graphics_sidecar",
        freeze_text,
    )
    _require(len(sidecar_matches) == 1, "full_suite_sidecar_commit_unbound")
    import xml.etree.ElementTree as ET

    tree = ET.parse(junit)
    suites = [tree.getroot()] if tree.getroot().tag == "testsuite" else list(tree.getroot().iter("testsuite"))
    counts = {key: sum(int(s.attrib.get(key, "0")) for s in suites) for key in ("tests", "failures", "errors", "skipped")}
    _require(counts["failures"] == 0 and counts["errors"] == 0, "full_suite_junit_failure")
    return {
        "exit_status": exit_status,
        "counts": counts,
        "stdout_sha256": _sha256_path(stdout),
        "junit_sha256": _sha256_path(junit),
        "pip_freeze_sha256": _sha256_path(freeze),
        "command": "python -m pytest -p no:cacheprovider -q",
        "source_commit": SOURCE_COMMIT,
        "sidecar_source_commit": sidecar_matches[0],
        "isolated_checkout": True,
        "workspace_imports": False,
        "environment_note": "Python 3.14 profile installs pytest 9.1.1 and scipy 1.18.1 explicitly; the aggregate dev extra is unavailable because its Torch requirement has no Python 3.14 distribution.",
    }


def _toolchain(root: Path) -> dict[str, Any]:
    python = root / "venv/bin/python"
    _require(python.is_file(), "build_python_missing")
    code = "import build,setuptools,wheel,sys; print(sys.version.split()[0],build.__version__,setuptools.__version__,wheel.__version__)"
    parts = subprocess.check_output([str(python), "-c", code], text=True).strip().split()
    _require(parts == ["3.14.3", "1.5.0", "84.2.1", "0.48.0"], "build_toolchain_mismatch")
    freeze_path = root / "pip_freeze.txt"
    with freeze_path.open("w", encoding="utf-8") as handle:
        subprocess.run([str(python), "-m", "pip", "freeze"], check=True, stdout=handle)
    return {
        "python": parts[0], "build": parts[1], "setuptools": parts[2], "wheel": parts[3],
        "pip_freeze_sha256": _sha256_path(freeze_path),
        "environment": {"SOURCE_DATE_EPOCH": "0", "PYTHONHASHSEED": "0", "TZ": "UTC", "LC_ALL": "C"},
    }


def build_attestation(args: argparse.Namespace) -> dict[str, Any]:
    comparison = compare_builds(args.wheel1, args.wheel2, args.sdist1, args.sdist2)
    wheel = comparison["wheel"]["run1"]
    sdist = comparison["sdist"]["run1"]
    consensus = inspect_tar(args.consensus, single_root=False)
    _require(consensus["sha256"] == CONSENSUS_SHA256, "consensus_sha256_mismatch")
    _require(consensus["member_count"] == 7, "consensus_member_count_mismatch")
    current_consensus_tree = _git_output("rev-parse", f"{SOURCE_COMMIT}:ilc_consensus")
    prior_consensus_tree = _git_output(
        "rev-parse", f"{PRIOR_RELEASE_SOURCE_COMMIT}:ilc_consensus"
    )
    _require(
        current_consensus_tree == prior_consensus_tree == CONSENSUS_TREE_OID,
        "consensus_source_tree_changed",
    )
    wheel_smoke, sdist_smoke = _read_json(args.wheel_smoke), _read_json(args.sdist_smoke)
    verify_smoke(wheel_smoke)
    verify_smoke(sdist_smoke)
    build_toolchains = {"run1": _toolchain(args.build1_root), "run2": _toolchain(args.build2_root)}
    _require(build_toolchains["run1"] == build_toolchains["run2"], "build_toolchains_not_equal")
    artifacts = [
        _artifact_node(artifact_type="wheel", filename=wheel["filename"], sha256=wheel["sha256"], size_bytes=wheel["size_bytes"], version=VERSION),
        _artifact_node(artifact_type="sdist", filename=sdist["filename"], sha256=sdist["sha256"], size_bytes=sdist["size_bytes"], version=VERSION),
    ]
    old = _read_json(Path("docs/specs/ilc_rc_native_distribution_vnext_build_evidence_GAP_RC_NATIVE_DISTRIBUTION_VNEXT_BUILD_00_v0.1.json"))
    prior_consensus_node = next(x for x in old["artifact_inventory"] if x["artifact_type"] == "binary_tarball")
    _require(prior_consensus_node["sha256"] == CONSENSUS_SHA256, "consensus_node_sha256_mismatch")
    # The consensus bytes did not change. Reuse the complete v0.4.34 node;
    # manufacturing a v0.4.35 label would create a false artifact identity.
    consensus_node = copy.deepcopy(prior_consensus_node)
    _require(
        consensus_node["filename"] == "ilc-consensus-linux-x86_64-v0.4.34.tar.gz",
        "consensus_filename_relabelled",
    )
    _require(consensus_node["package_version"] == "0.4.34", "consensus_version_relabelled")
    _require(consensus_node["size_bytes"] == consensus["size_bytes"], "consensus_node_size_mismatch")
    consensus_body = {k: v for k, v in consensus_node.items() if k != "cid"}
    _require(consensus_node["cid"] == node_id_from_obj(consensus_body), "consensus_node_cid_mismatch")
    artifacts.append(consensus_node)
    build_environment = build_toolchains["run1"]
    reproducibility_material = {
        "wheel_run1_sha256": comparison["wheel"]["run1"]["sha256"],
        "wheel_run2_sha256": comparison["wheel"]["run2"]["sha256"],
        "wheel_byte_identical": comparison["wheel"]["byte_identical"],
        "sdist_run1_sha256": comparison["sdist"]["run1"]["sha256"],
        "sdist_run2_sha256": comparison["sdist"]["run2"]["sha256"],
        "sdist_classification": comparison["sdist"]["classification"],
        "sdist_member_payloads_and_non_time_metadata_equal": comparison["sdist"]["member_payloads_and_non_time_metadata_equal"],
    }
    build_recipe_body = {
        "build_command": "python -m build --no-isolation --wheel --sdist",
        "build_date": SOURCE_DATE,
        "build_env_hash": _sha256_bytes(_canonical_bytes(build_environment)),
        "build_toolchain": "python-3.14.3/build-1.5.0/setuptools-84.2.1/wheel-0.48.0",
        "builder_agent_id": old["builder_execution_context"]["agent_id"],
        "node_kind": "BuildRecipeNode",
        "reproducibility_hash": _sha256_bytes(_canonical_bytes(reproducibility_material)),
        "schema_version": "build_recipe_node.v0.1",
        "source_commit": SOURCE_COMMIT,
    }
    build_recipe = {**build_recipe_body, "cid": node_id_from_obj(build_recipe_body)}
    release_body = {
        "artifact_cids": sorted(a["cid"] for a in artifacts),
        "build_recipe_cid": build_recipe["cid"],
        "changelog_hash": _sha256_bytes(b"v0.4.35 reconciliation source freeze"),
        "node_kind": "SoftwareReleaseNode",
        "package_name": "ilc-core",
        "release_channel": "public_rc",
        "release_date": SOURCE_DATE,
        "release_key_pubkey": old["candidate_release_assertion"]["software_release_node"]["release_key_pubkey"],
        "release_signature_ref": "pending-r5b:release-envelope-set",
        "schema_version": "software_release_node.v0.1",
        "source_commit": SOURCE_COMMIT,
        "version": VERSION,
    }
    release = {**release_body, "cid": node_id_from_obj(release_body)}
    assertion_body = {
        "artifact_nodes": artifacts,
        "build_recipe_nodes": [build_recipe],
        "release_attestation_edges": [],
        "schema_version": "software_release_assertion.v0.1",
        "software_release_node": release,
    }
    assertion = {**assertion_body, "assertion_cid": node_id_from_obj(assertion_body)}
    changed_since_r4 = _git_paths(
        "diff", "--name-only", "66685f19baa1847e394b1092a516c7f919ec66ef", SOURCE_COMMIT
    )
    package_changes_after_freeze = _git_paths(
        "diff", "--name-only", SOURCE_COMMIT, "HEAD", "--", "pyproject.toml", "ilc_core"
    )
    _require(not package_changes_after_freeze, "package_source_changed_after_freeze")
    result = {
        "PUBLIC_RC_EXCLUDE": "unsigned_reconciliation_build_candidate",
        "schema_version": SCHEMA_VERSION,
        "phase": PHASE,
        "source_freeze_commit": SOURCE_COMMIT,
        "source_change_allowlist": changed_since_r4,
        "package_changes_after_freeze": package_changes_after_freeze,
        "package_member_source_immutable_after_freeze": True,
        "reconciliation_manifest_sha256": MANIFEST_SHA256,
        "r4_result_sha256": R4_SHA256,
        "build_environment": build_environment,
        "build_runs": comparison,
        "retained_artifacts": {"wheel": artifacts[0], "sdist": artifacts[1]},
        "consensus_tarball_reuse": {
            "artifact": consensus_node,
            "inspection": consensus,
            "prior_release_source_commit": PRIOR_RELEASE_SOURCE_COMMIT,
            "prior_source_tree_git_oid": prior_consensus_tree,
            "source_tree_git_oid": current_consensus_tree,
            "source_tree_unchanged": True,
            "prior_v0434_artifact_cid": prior_consensus_node["cid"],
            "reused_unchanged": True,
            "r5c_skipped": True,
        },
        "installed_artifact_smokes": {"wheel": wheel_smoke, "sdist": sdist_smoke},
        "full_suite": _suite_record(args.suite_root),
        "installer_counterpart_pending_r5b": True,
        "candidate_release_assertion": assertion,
        "sensitive_actions_performed": False,
        "non_claims": [
            "unsigned_candidate_not_authoritative", "no_signing_or_key_access",
            "no_upload_or_publication", "no_policy_or_graph_write", "no_public_mirror_push",
            "no_live_host_or_store_mutation", "no_guard_activation", "no_epoch_or_economic_transition",
            "no_new_consensus_build",
        ],
    }
    verify_attestation(result)
    _atomic_json(args.output, result)
    return result


def verify_attestation(value: Mapping[str, Any]) -> None:
    _require(value.get("schema_version") == SCHEMA_VERSION, "attestation_schema_invalid")
    _require(value.get("phase") == PHASE, "attestation_phase_invalid")
    _require(value.get("source_freeze_commit") == SOURCE_COMMIT, "attestation_source_commit_invalid")
    _require(COMMIT_RE.fullmatch(str(value.get("source_freeze_commit"))) is not None, "attestation_commit_format_invalid")
    _require(value.get("reconciliation_manifest_sha256") == MANIFEST_SHA256, "attestation_manifest_hash_invalid")
    _require(value.get("r4_result_sha256") == R4_SHA256, "attestation_r4_hash_invalid")
    _require(value.get("package_member_source_immutable_after_freeze") is True, "attestation_source_immutability_false")
    source_allowlist = value.get("source_change_allowlist")
    _require(isinstance(source_allowlist, list) and source_allowlist, "attestation_source_allowlist_invalid")
    _require(len(source_allowlist) == len(set(source_allowlist)), "attestation_source_allowlist_duplicate")
    for raw_path in source_allowlist:
        _require(isinstance(raw_path, str), "attestation_source_allowlist_path_invalid")
        path = PurePosixPath(raw_path)
        _require(
            raw_path == path.as_posix()
            and not path.is_absolute()
            and all(part not in {"", ".", ".."} for part in path.parts),
            "attestation_source_allowlist_path_invalid",
        )
    _require(value.get("package_changes_after_freeze") == [], "attestation_package_changed_after_freeze")
    _require(value.get("installer_counterpart_pending_r5b") is True, "attestation_installer_pending_false")
    _require(value.get("sensitive_actions_performed") is False, "attestation_sensitive_action_true")
    runs = value.get("build_runs")
    _require(isinstance(runs, dict), "attestation_build_runs_invalid")
    _require(runs.get("wheel", {}).get("byte_identical") is True, "attestation_wheel_not_reproducible")
    _require(runs.get("sdist", {}).get("member_payloads_and_non_time_metadata_equal") is True, "attestation_sdist_content_mismatch")
    _require(value.get("consensus_tarball_reuse", {}).get("reused_unchanged") is True, "attestation_consensus_not_reused")
    _require(value.get("consensus_tarball_reuse", {}).get("r5c_skipped") is True, "attestation_r5c_not_skipped")
    _require(value.get("consensus_tarball_reuse", {}).get("source_tree_unchanged") is True, "attestation_consensus_source_changed")
    _require(value.get("consensus_tarball_reuse", {}).get("source_tree_git_oid") == CONSENSUS_TREE_OID, "attestation_consensus_tree_oid_invalid")
    _require(value.get("consensus_tarball_reuse", {}).get("prior_source_tree_git_oid") == CONSENSUS_TREE_OID, "attestation_prior_consensus_tree_oid_invalid")
    suite = value.get("full_suite", {})
    _require(type(suite.get("exit_status")) is int and suite.get("exit_status") == 0, "attestation_suite_exit_invalid")
    counts = suite.get("counts", {})
    _require(isinstance(counts, dict), "attestation_suite_counts_invalid")
    for field in ("tests", "failures", "errors", "skipped"):
        _require(type(counts.get(field)) is int and counts[field] >= 0, f"attestation_suite_count_invalid:{field}")
    _require(counts["failures"] == 0 and counts["errors"] == 0, "attestation_suite_not_clean")
    for smoke in value.get("installed_artifact_smokes", {}).values():
        verify_smoke(smoke)
    assertion = value.get("candidate_release_assertion")
    _require(isinstance(assertion, dict), "attestation_assertion_invalid")
    _require(set(assertion) == set(ASSERTION_REQUIRED_FIELDS), "attestation_assertion_fields_invalid")
    assertion_body = {k: v for k, v in assertion.items() if k != "assertion_cid"}
    _require(assertion.get("assertion_cid") == node_id_from_obj(assertion_body), "attestation_assertion_cid_mismatch")
    artifact_nodes = assertion.get("artifact_nodes", [])
    _require(isinstance(artifact_nodes, list) and len(artifact_nodes) == 3, "attestation_artifact_count_invalid")
    by_type: dict[str, Mapping[str, Any]] = {}
    for node in artifact_nodes:
        _require(set(node) == set(ARTIFACT_NODE_FIELDS), "attestation_artifact_fields_invalid")
        _require(ARTIFACT_ID_RE.fullmatch(str(node.get("artifact_id"))) is not None, "attestation_artifact_id_invalid")
        artifact_type = node.get("artifact_type")
        _require(artifact_type in {"wheel", "sdist", "binary_tarball"} and artifact_type not in by_type, "attestation_artifact_type_invalid")
        expected_version = "0.4.34" if artifact_type == "binary_tarball" else VERSION
        _require(node.get("package_version") == expected_version, "attestation_artifact_version_invalid")
        by_type[str(artifact_type)] = node
        body = {k: v for k, v in node.items() if k != "cid"}
        _require(node.get("cid") == node_id_from_obj(body), "attestation_artifact_cid_mismatch")
    retained = value.get("retained_artifacts", {})
    _require(retained.get("wheel") == by_type["wheel"], "attestation_retained_wheel_mismatch")
    _require(retained.get("sdist") == by_type["sdist"], "attestation_retained_sdist_mismatch")
    _require(by_type["wheel"].get("sha256") == runs["wheel"]["run1"]["sha256"], "attestation_wheel_hash_unbound")
    _require(by_type["sdist"].get("sha256") == runs["sdist"]["run1"]["sha256"], "attestation_sdist_hash_unbound")
    consensus = value.get("consensus_tarball_reuse", {})
    _require(consensus.get("artifact") == by_type["binary_tarball"], "attestation_consensus_artifact_mismatch")
    _require(by_type["binary_tarball"].get("sha256") == consensus.get("inspection", {}).get("sha256") == CONSENSUS_SHA256, "attestation_consensus_hash_unbound")
    _require(by_type["binary_tarball"].get("filename") == "ilc-consensus-linux-x86_64-v0.4.34.tar.gz", "attestation_consensus_filename_relabelled")
    _require(consensus.get("prior_v0434_artifact_cid") == by_type["binary_tarball"].get("cid"), "attestation_consensus_prior_cid_mismatch")
    _require(by_type["binary_tarball"].get("filename") == "ilc-consensus-linux-x86_64-v0.4.34.tar.gz", "attestation_consensus_filename_relabelled")
    recipes = assertion.get("build_recipe_nodes", [])
    _require(isinstance(recipes, list) and len(recipes) == 1, "attestation_recipe_count_invalid")
    for node in recipes:
        _require(set(node) == set(BUILD_RECIPE_NODE_FIELDS), "attestation_recipe_fields_invalid")
        _require(node.get("source_commit") == SOURCE_COMMIT, "attestation_recipe_source_commit_invalid")
        body = {k: v for k, v in node.items() if k != "cid"}
        _require(node.get("cid") == node_id_from_obj(body), "attestation_recipe_cid_mismatch")
    release = assertion.get("software_release_node", {})
    _require(set(release) == set(SOFTWARE_RELEASE_NODE_FIELDS), "attestation_release_fields_invalid")
    release_body = {k: v for k, v in release.items() if k != "cid"}
    _require(release.get("cid") == node_id_from_obj(release_body), "attestation_release_cid_mismatch")
    _require(release.get("version") == VERSION, "attestation_release_version_invalid")
    _require(release.get("source_commit") == SOURCE_COMMIT, "attestation_release_source_commit_invalid")
    _require(release.get("artifact_cids") == sorted(node["cid"] for node in artifact_nodes), "attestation_release_artifact_cids_mismatch")
    _require(release.get("build_recipe_cid") == assertion["build_recipe_nodes"][0]["cid"], "attestation_release_recipe_cid_mismatch")
    for digest in (value.get("reconciliation_manifest_sha256"), value.get("r4_result_sha256")):
        _require(SHA256_RE.fullmatch(str(digest)) is not None, "attestation_sha256_format_invalid")
    serialized = json.dumps(value, sort_keys=True)
    _require("signature_hex" not in serialized and "native_submit_sig" not in serialized, "attestation_contains_signature_material")


def negative_probes(value: Mapping[str, Any]) -> None:
    probes: list[tuple[str, Any]] = []
    bad = copy.deepcopy(dict(value))
    bad["sensitive_actions_performed"] = 0
    probes.append(("typed_sensitive_boolean", bad))
    bad = copy.deepcopy(dict(value))
    bad["full_suite"]["exit_status"] = False
    probes.append(("typed_suite_exit", bad))
    bad = copy.deepcopy(dict(value))
    bad["candidate_release_assertion"]["artifact_nodes"][0]["cid"] = "bafyreiaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    probes.append(("artifact_cid_binding", bad))
    bad = copy.deepcopy(dict(value))
    bad["retained_artifacts"]["wheel"]["sha256"] = "0" * 64
    probes.append(("retained_hash_binding", bad))
    bad = copy.deepcopy(dict(value))
    bad["package_changes_after_freeze"] = ["ilc_core/unexpected.py"]
    probes.append(("post_freeze_package_change", bad))
    bad = copy.deepcopy(dict(value))
    bad["candidate_release_assertion"]["artifact_nodes"][2]["filename"] = "ilc-consensus-linux-x86_64-v0.4.35.tar.gz"
    probes.append(("consensus_relabel", bad))
    bad = copy.deepcopy(dict(value))
    bad["candidate_release_assertion"]["build_recipe_nodes"] = []
    probes.append(("missing_build_recipe", bad))
    for name, candidate in probes:
        try:
            verify_attestation(candidate)
        except AttestationError:
            continue
        raise AttestationError(f"negative_probe_accepted:{name}")


def self_test() -> None:
    with tempfile.TemporaryDirectory() as raw:
        root = Path(raw)
        duplicate = root / "duplicate.zip"
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            with zipfile.ZipFile(duplicate, "w") as archive:
                archive.writestr("a", b"1")
                archive.writestr("a", b"2")
        try:
            inspect_zip(duplicate)
        except AttestationError as exc:
            _require(exc.token == "archive_duplicate_member", "self_test_duplicate_wrong_token")
        else:
            raise AttestationError("self_test_duplicate_not_rejected")
        unsafe = root / "unsafe.tar.gz"
        with tarfile.open(unsafe, "w:gz") as archive:
            info = tarfile.TarInfo("../escape")
            info.size = 0
            archive.addfile(info)
        try:
            inspect_tar(unsafe, single_root=False)
        except AttestationError as exc:
            _require(exc.token == "archive_member_unsafe", "self_test_unsafe_wrong_token")
        else:
            raise AttestationError("self_test_unsafe_not_rejected")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    smoke = sub.add_parser("smoke")
    smoke.add_argument("--output", type=Path, required=True)
    verify = sub.add_parser("verify")
    verify.add_argument("--input", type=Path, required=True)
    sub.add_parser("self-test")
    attest = sub.add_parser("attest")
    for name in ("wheel1", "wheel2", "sdist1", "sdist2", "consensus", "wheel-smoke", "sdist-smoke"):
        attest.add_argument(f"--{name}", type=Path, required=True)
    attest.add_argument("--build1-root", type=Path, required=True)
    attest.add_argument("--build2-root", type=Path, required=True)
    attest.add_argument("--suite-root", type=Path, required=True)
    attest.add_argument("--output", type=Path, required=True)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    try:
        args = parse_args(argv)
        if args.command == "smoke":
            run_smoke(args.output)
            print("SMOKE_VALID")
        elif args.command == "verify":
            value = _read_json(args.input)
            verify_attestation(value)
            negative_probes(value)
            print("ATTESTATION_VALID")
        elif args.command == "self-test":
            self_test()
            print("SELF_TEST_VALID")
        else:
            value = build_attestation(args)
            negative_probes(value)
            print("ATTESTATION_WRITTEN")
    except (AttestationError, OSError, ValueError, json.JSONDecodeError, tarfile.TarError, zipfile.BadZipFile, subprocess.SubprocessError) as exc:
        print(exc.token if isinstance(exc, AttestationError) else f"attestation_error:{type(exc).__name__}")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
