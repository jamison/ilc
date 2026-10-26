#!/usr/bin/env python3
"""Verify the signed Genesis artifacts needed by sufficiency lineage research."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Mapping


SCHEMA = "ILCSufficiencyGenesisLineageAuditV1"
EXPECTED_KEY_RECORD = "docs/genesis/genesis_agent1_pubkey_record_838a.txt"
EXPECTED_KEY_RECORD_SHA256 = (
    "d486a93065d88e68ff8adef35c87fc1729d8f256b80132b1db313ee177e4aa53"
)
EXPECTED_GENESIS_AGENT_ID = (
    "c43f69fcc4dfd021f5e468824c9560c03c45c601f8d004be4d244356ce604384"
    "9b9cf2af38bc51a40c1c4bc3e71b04d9"
)
EXPECTED_MLDSA_PUBLIC_KEY_SHA256 = (
    "228a9d27ef0fa1dcb0607ca06a157733ff3f3a821304687670af9b0775deefd8"
)
EXPECTED_SIGNING_DOMAINS = {
    "core_slice_0": "ilc-genesis-core-slice-0-authority-package",
    "slice_1": "ilc-genesis-public-rc-baseline-slice-1",
}
EXPECTED_CORE_SLICE_0_HASH = (
    "38a9f7351d00a1b92b6476c894552d78936400cf707076ccb6967fb5af5541e1"
)
EXPECTED_ROOT_HASH = (
    "ddc686019018e05f3d88be1a879663c7c2756823bf8bc7fbf980743a92fc6c3c"
)
EXPECTED_NODE_0 = "artifact:genesis_intent_attestation_init_authority_map"
MAX_JSON_BYTES = 16 * 1024 * 1024
MAX_SIGNATURE_TEXT_BYTES = 16 * 1024
MAX_KEY_RECORD_BYTES = 64 * 1024
MAX_VERIFIER_OUTPUT_BYTES = 16 * 1024
VERIFIER_TIMEOUT_SECONDS = 30
REQUEST_KEYS = {
    "domain_separator",
    "operator_command",
    "package_path",
    "package_sha256",
    "phase",
    "secret_material_handled_by_codex",
    "signature_path",
    "signature_payload_path",
    "signature_payload_sha256",
    "signer_public_key_record",
    "tool_version",
    "verification_command",
}
VERIFICATION_KEYS = {
    "phase",
    "returncode",
    "secret_material_handled_by_codex",
    "signature_path",
    "signature_payload_sha256",
    "signature_sha256",
    "stderr",
    "stdout",
    "verification_result",
}
ROOT_KEYS = {
    "envelope_created",
    "envelope_hash",
    "envelope_type",
    "envelope_version",
    "issuer",
    "manifests",
    "public_key_ref",
    "signing_algorithm",
    "signing_context",
    "star_map_node_count",
    "star_map_version",
}


class LineageVerificationError(ValueError):
    """A signed lineage artifact failed a required verification."""


@dataclass(frozen=True)
class ArtifactPaths:
    repo_root: Path
    pq_sign: Path
    key_record: Path
    core_package: Path
    core_request: Path
    core_verification: Path
    core_payload: Path
    core_signature: Path
    slice_package: Path
    slice_request: Path
    slice_verification: Path
    slice_payload: Path
    slice_signature: Path
    root_envelope: Path
    root_signature: Path


@dataclass(frozen=True)
class VerifyResult:
    returncode: int
    stdout: str
    stderr: str


VerifyRunner = Callable[[Path, Path, Path, Path], VerifyResult]


def default_paths(repo_root: Path) -> ArtifactPaths:
    core = repo_root / "release_artifacts/genesis_v05/core_slice_0"
    slice_1 = repo_root / "release_artifacts/genesis_v05/public_rc_baseline_slice_1"
    return ArtifactPaths(
        repo_root=repo_root,
        pq_sign=repo_root / "ilc_consensus/target/debug/pq_sign",
        key_record=repo_root / EXPECTED_KEY_RECORD,
        core_package=core / "genesis_core_slice_0_authority_package.json",
        core_request=core / "genesis_core_slice_0_authority_package.signing_request.json",
        core_verification=core / "genesis_core_slice_0_authority_package.verification.json",
        core_payload=core / "genesis_core_slice_0_authority_package.signature_payload.bin",
        core_signature=core / "genesis_core_slice_0_authority_package.signature.hex",
        slice_package=slice_1 / "genesis_v05_public_rc_baseline_slice_1.json",
        slice_request=slice_1 / "genesis_v05_public_rc_baseline_slice_1.signing_request.json",
        slice_verification=slice_1 / "genesis_v05_public_rc_baseline_slice_1.verification.json",
        slice_payload=slice_1 / "genesis_v05_public_rc_baseline_slice_1.signature_payload.bin",
        slice_signature=slice_1 / "genesis_v05_public_rc_baseline_slice_1.signature.hex",
        root_envelope=repo_root / "out/genesis_signing_root_envelope_v0.1.json",
        root_signature=repo_root / "out/genesis_signing_root_envelope_v0.1.sig",
    )


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise LineageVerificationError(f"duplicate_json_key:{key}")
        result[key] = value
    return result


def _reject_constant(value: str) -> None:
    raise LineageVerificationError(f"non_finite_json_number:{value}")


def load_json(path: Path) -> dict[str, Any]:
    try:
        size = path.stat().st_size
    except OSError as exc:
        raise LineageVerificationError(f"artifact_unreadable:{path}") from exc
    if size > MAX_JSON_BYTES:
        raise LineageVerificationError(f"json_size_limit_exceeded:{path}:{size}")
    try:
        value = json.loads(
            path.read_text(encoding="utf-8"),
            object_pairs_hook=_reject_duplicate_keys,
            parse_constant=_reject_constant,
        )
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise LineageVerificationError(f"invalid_json:{path}") from exc
    if type(value) is not dict:
        raise LineageVerificationError(f"json_root_not_object:{path}")
    return value


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    try:
        with path.open("rb") as handle:
            for block in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(block)
    except OSError as exc:
        raise LineageVerificationError(f"artifact_unreadable:{path}") from exc
    return digest.hexdigest()


def normalized_signature_sha256(path: Path) -> str:
    try:
        if path.stat().st_size > MAX_SIGNATURE_TEXT_BYTES:
            raise LineageVerificationError(f"signature_size_limit_exceeded:{path}")
        signature_hex = "".join(path.read_text(encoding="ascii").split())
    except (OSError, UnicodeError) as exc:
        raise LineageVerificationError(f"signature_unreadable:{path}") from exc
    if not signature_hex:
        raise LineageVerificationError(f"signature_empty:{path}")
    if len(signature_hex) % 2:
        raise LineageVerificationError(f"signature_hex_length_invalid:{path}")
    try:
        int(signature_hex, 16)
    except ValueError as exc:
        raise LineageVerificationError(f"signature_not_hex:{path}") from exc
    return hashlib.sha256(signature_hex.encode("ascii")).hexdigest()


def canonical_root_hash(envelope: Mapping[str, Any]) -> str:
    preimage = dict(envelope)
    preimage["envelope_hash"] = None
    try:
        encoded = json.dumps(
            preimage,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise LineageVerificationError("root_envelope_not_canonicalizable") from exc
    return hashlib.sha256(encoded).hexdigest()


def subprocess_runner(
    pq_sign: Path, payload: Path, signature: Path, key_record: Path
) -> VerifyResult:
    try:
        if signature.stat().st_size > MAX_SIGNATURE_TEXT_BYTES:
            raise LineageVerificationError(f"signature_too_large:{signature}")
        signature_hex = "".join(signature.read_text(encoding="ascii").split())
    except (OSError, UnicodeError) as exc:
        raise LineageVerificationError(f"signature_unreadable:{signature}") from exc
    if not signature_hex:
        raise LineageVerificationError(f"signature_empty:{signature}")
    try:
        int(signature_hex, 16)
    except ValueError as exc:
        raise LineageVerificationError(f"signature_not_hex:{signature}") from exc
    try:
        completed = subprocess.run(
            [
                str(pq_sign),
                "verify",
                "--input-file",
                str(payload),
                "--pubkey-record",
                str(key_record),
                "--signature-hex",
                signature_hex,
            ],
            cwd=pq_sign.parents[3],
            capture_output=True,
            text=True,
            check=False,
            timeout=VERIFIER_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired as exc:
        raise LineageVerificationError("pq_sign_verification_timeout") from exc
    except OSError as exc:
        raise LineageVerificationError("pq_sign_verifier_unavailable") from exc
    if (
        len(completed.stdout.encode("utf-8")) > MAX_VERIFIER_OUTPUT_BYTES
        or len(completed.stderr.encode("utf-8")) > MAX_VERIFIER_OUTPUT_BYTES
    ):
        raise LineageVerificationError("pq_sign_output_too_large")
    return VerifyResult(
        returncode=completed.returncode,
        stdout=completed.stdout.strip(),
        stderr=completed.stderr.strip(),
    )


def _expect_equal(actual: Any, expected: Any, token: str) -> None:
    if type(actual) is not type(expected) or actual != expected:
        raise LineageVerificationError(f"{token}:actual={actual!r}:expected={expected!r}")


def _expect_keys(record: Mapping[str, Any], expected: set[str], token: str) -> None:
    actual = set(record)
    if actual != expected:
        raise LineageVerificationError(
            f"{token}:missing={sorted(expected - actual)!r}:unknown={sorted(actual - expected)!r}"
        )


def _verify_key_record(paths: ArtifactPaths) -> dict[str, str]:
    expected_path = (paths.repo_root / EXPECTED_KEY_RECORD).resolve()
    if paths.key_record.resolve() != expected_path:
        raise LineageVerificationError("genesis_key_record_path_invalid")
    try:
        if paths.key_record.stat().st_size > MAX_KEY_RECORD_BYTES:
            raise LineageVerificationError("genesis_key_record_too_large")
        text = paths.key_record.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise LineageVerificationError("genesis_key_record_unreadable") from exc
    _expect_equal(
        sha256_file(paths.key_record),
        EXPECTED_KEY_RECORD_SHA256,
        "genesis_key_record_sha256",
    )
    agent_match = re.search(r"^agent_id:\s+([0-9a-f]+)$", text, re.MULTILINE)
    key_match = re.search(r"^mldsa_pk_hex:\s+([0-9a-f]+)$", text, re.MULTILINE)
    if agent_match is None or key_match is None:
        raise LineageVerificationError("genesis_key_record_fields_missing")
    _expect_equal(
        agent_match.group(1), EXPECTED_GENESIS_AGENT_ID, "genesis_key_record_agent_id"
    )
    try:
        public_key = bytes.fromhex(key_match.group(1))
    except ValueError as exc:
        raise LineageVerificationError("genesis_mldsa_public_key_invalid") from exc
    public_key_sha256 = hashlib.sha256(public_key).hexdigest()
    _expect_equal(
        public_key_sha256,
        EXPECTED_MLDSA_PUBLIC_KEY_SHA256,
        "genesis_mldsa_public_key_sha256",
    )
    return {
        "key_record_path": EXPECTED_KEY_RECORD,
        "key_record_sha256": EXPECTED_KEY_RECORD_SHA256,
        "agent_id": EXPECTED_GENESIS_AGENT_ID,
        "mldsa_public_key_sha256": public_key_sha256,
    }


def _verify_result(result: VerifyResult, token: str) -> dict[str, Any]:
    _expect_equal(result.returncode, 0, f"{token}_returncode")
    _expect_equal(result.stdout, "signature_verified", f"{token}_stdout")
    _expect_equal(result.stderr, "", f"{token}_stderr")
    return {
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }


def _verify_signed_package(
    *,
    name: str,
    package_path: Path,
    request_path: Path,
    verification_path: Path,
    payload_path: Path,
    signature_path: Path,
    expected_package_hash: str | None,
    paths: ArtifactPaths,
    runner: VerifyRunner,
) -> tuple[dict[str, Any], dict[str, Any]]:
    package = load_json(package_path)
    request = load_json(request_path)
    verification = load_json(verification_path)
    _expect_keys(request, REQUEST_KEYS, f"{name}_request_schema")
    _expect_keys(verification, VERIFICATION_KEYS, f"{name}_verification_schema")

    _expect_equal(
        request.get("signer_public_key_record"),
        EXPECTED_KEY_RECORD,
        f"{name}_signer_public_key_record",
    )
    _expect_equal(request.get("secret_material_handled_by_codex"), False, f"{name}_secret_boundary")
    _expect_equal(
        request.get("domain_separator"),
        EXPECTED_SIGNING_DOMAINS[name],
        f"{name}_signing_domain",
    )

    package_hash = sha256_file(package_path)
    _expect_equal(package_hash, request.get("package_sha256"), f"{name}_package_sha256")
    if expected_package_hash is not None:
        _expect_equal(package_hash, expected_package_hash, f"{name}_frozen_package_sha256")

    payload_hash = sha256_file(payload_path)
    _expect_equal(payload_hash, request.get("signature_payload_sha256"), f"{name}_payload_request")
    _expect_equal(
        payload_hash,
        verification.get("signature_payload_sha256"),
        f"{name}_payload_verification",
    )
    try:
        package_bytes = package_path.read_bytes()
        payload_bytes = payload_path.read_bytes()
    except OSError as exc:
        raise LineageVerificationError(f"{name}_signed_preimage_unreadable") from exc
    expected_payload = request["domain_separator"].encode("utf-8") + package_bytes
    if payload_bytes != expected_payload:
        raise LineageVerificationError(f"{name}_signed_payload_package_mismatch")

    signature_file_hash = sha256_file(signature_path)
    signature_hash = normalized_signature_sha256(signature_path)
    _expect_equal(
        signature_hash,
        verification.get("signature_sha256"),
        f"{name}_signature_verification",
    )
    _expect_equal(verification.get("verification_result"), "signature_verified", f"{name}_receipt_result")
    _expect_equal(verification.get("returncode"), 0, f"{name}_receipt_returncode")
    _expect_equal(verification.get("stdout"), "signature_verified", f"{name}_receipt_stdout")
    _expect_equal(verification.get("stderr"), "", f"{name}_receipt_stderr")

    result = runner(paths.pq_sign, payload_path, signature_path, paths.key_record)
    return package, {
        "package_path": str(package_path.relative_to(paths.repo_root)),
        "package_sha256": package_hash,
        "signature_payload_path": str(payload_path.relative_to(paths.repo_root)),
        "signature_payload_sha256": payload_hash,
        "signature_path": str(signature_path.relative_to(paths.repo_root)),
        "signature_file_sha256": signature_file_hash,
        "signature_sha256": signature_hash,
        "signer_public_key_record": EXPECTED_KEY_RECORD,
        "detached_verification_record": str(verification_path.relative_to(paths.repo_root)),
        "signature_verification_command": [
            str(paths.pq_sign.relative_to(paths.repo_root)),
            "verify",
            "--input-file",
            str(payload_path.relative_to(paths.repo_root)),
            "--pubkey-record",
            EXPECTED_KEY_RECORD,
            "--signature-hex",
            f"<normalized contents of {signature_path.relative_to(paths.repo_root)}>",
        ],
        "signature_verification": _verify_result(result, f"{name}_pq_sign"),
    }


def verify_node_zero(core_package: Mapping[str, Any]) -> Mapping[str, Any]:
    _expect_equal(core_package.get("node_count"), 58, "core_slice_0_node_count")
    nodes = core_package.get("nodes")
    if type(nodes) is not list:
        raise LineageVerificationError("core_slice_0_nodes_not_list")
    _expect_equal(len(nodes), 58, "core_slice_0_nodes_length")
    node_0 = [
        node
        for node in nodes
        if type(node) is dict and node.get("candidate_id") == EXPECTED_NODE_0
    ]
    _expect_equal(len(node_0), 1, "core_slice_0_node_0_count")
    node = node_0[0]
    _expect_equal(node.get("node_kind"), "authority_map", "node_0_kind")
    _expect_equal(node.get("genesis_attested"), True, "node_0_genesis_attested")
    _expect_equal(
        node.get("signature_envelope_ref"),
        "out/genesis_signing_root_envelope_v0.1.json",
        "node_0_signature_envelope_ref",
    )
    _expect_equal(
        node.get("signature_file_ref"),
        "out/genesis_signing_root_envelope_v0.1.sig",
        "node_0_signature_file_ref",
    )
    return node


def verify_artifacts(
    paths: ArtifactPaths,
    *,
    runner: VerifyRunner = subprocess_runner,
) -> dict[str, Any]:
    key_record = _verify_key_record(paths)
    core_package, core = _verify_signed_package(
        name="core_slice_0",
        package_path=paths.core_package,
        request_path=paths.core_request,
        verification_path=paths.core_verification,
        payload_path=paths.core_payload,
        signature_path=paths.core_signature,
        expected_package_hash=EXPECTED_CORE_SLICE_0_HASH,
        paths=paths,
        runner=runner,
    )
    verify_node_zero(core_package)
    core["node_count"] = 58
    core["node_0_candidate_id"] = EXPECTED_NODE_0

    slice_package, slice_1 = _verify_signed_package(
        name="slice_1",
        package_path=paths.slice_package,
        request_path=paths.slice_request,
        verification_path=paths.slice_verification,
        payload_path=paths.slice_payload,
        signature_path=paths.slice_signature,
        expected_package_hash=None,
        paths=paths,
        runner=runner,
    )
    anchor = slice_package.get("core_slice_0_authority_package_sha256")
    _expect_equal(anchor, core["package_sha256"], "slice_1_core_slice_0_anchor")
    slice_1["node_count"] = slice_package.get("node_count")
    slice_nodes = slice_package.get("nodes")
    if type(slice_1["node_count"]) is not int or type(slice_nodes) is not list:
        raise LineageVerificationError("slice_1_nodes_shape_invalid")
    _expect_equal(len(slice_nodes), slice_1["node_count"], "slice_1_nodes_length")
    slice_1["core_slice_0_authority_package_sha256"] = anchor

    root = load_json(paths.root_envelope)
    _expect_keys(root, ROOT_KEYS, "root_envelope_schema")
    root_hash = canonical_root_hash(root)
    _expect_equal(root.get("envelope_hash"), EXPECTED_ROOT_HASH, "root_envelope_recorded_hash")
    _expect_equal(root_hash, EXPECTED_ROOT_HASH, "root_envelope_recomputed_hash")
    _expect_equal(root.get("issuer"), "genesis_agent:01", "root_envelope_issuer")
    _expect_equal(
        root.get("public_key_ref"),
        "artifact:genesis_agent1_pubkey_record_838a",
        "root_envelope_public_key_ref",
    )
    _expect_equal(root.get("signing_context"), "ILC_GENESIS_ROOT_ENVELOPE_V1", "root_context")
    root_result = runner(paths.pq_sign, paths.root_envelope, paths.root_signature, paths.key_record)
    signed_root = {
        "envelope_path": str(paths.root_envelope.relative_to(paths.repo_root)),
        "envelope_file_sha256": sha256_file(paths.root_envelope),
        "envelope_hash": root_hash,
        "envelope_hash_preimage_rule": "canonical_json_with_envelope_hash_null",
        "signature_path": str(paths.root_signature.relative_to(paths.repo_root)),
        "signature_file_sha256": sha256_file(paths.root_signature),
        "signature_sha256": normalized_signature_sha256(paths.root_signature),
        "signer_public_key_record": EXPECTED_KEY_RECORD,
        "signature_verification_command": [
            str(paths.pq_sign.relative_to(paths.repo_root)),
            "verify",
            "--input-file",
            str(paths.root_envelope.relative_to(paths.repo_root)),
            "--pubkey-record",
            EXPECTED_KEY_RECORD,
            "--signature-hex",
            f"<normalized contents of {paths.root_signature.relative_to(paths.repo_root)}>",
        ],
        "signature_verification": _verify_result(root_result, "signed_root_pq_sign"),
    }

    return {
        "schema": SCHEMA,
        "phase": "GAP-SUFFICIENCY-GENESIS-LINEAGE-INTEGRATION-00",
        "overall_result": "verified",
        "core_slice_0": core,
        "slice_1": slice_1,
        "signed_root": signed_root,
        "genesis_key_record": key_record,
        "non_claims": [
            "no_signed_artifact_modified",
            "no_live_graph_write",
            "no_canonical_sufficiency_object_materialized",
            "no_cdl_opened",
        ],
    }


def atomic_write_json(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(value, handle, sort_keys=True, indent=2, allow_nan=False)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_name, path)
    except BaseException:
        try:
            os.unlink(temp_name)
        except FileNotFoundError:
            pass
        raise


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    repo_root = Path(__file__).resolve().parents[2]
    try:
        audit = verify_artifacts(default_paths(repo_root))
        atomic_write_json(args.output, audit)
    except LineageVerificationError as exc:
        print(f"FAIL: {exc}")
        return 1
    for name in ("core_slice_0", "slice_1", "signed_root"):
        result = audit[name]["signature_verification"]
        print(
            f"{name}: returncode={result['returncode']} "
            f"stdout={result['stdout']!r} stderr={result['stderr']!r}"
        )
    print("OK: Core Slice 0, Slice 1, and signed Genesis root verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
