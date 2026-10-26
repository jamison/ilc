#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
"""Two-step live ILC software release assertion publish ceremony.

Step 1 prepares unsigned release-envelope skeletons and the raw 32-byte digest
values the human operator signs offline. Step 2 accepts those signatures and
uses their public-key/signature verification as the authority gate before
publishing through native QUIC. A well-known HTTPS JSON payload may be written
as a compatibility mirror, but CDL-121 makes transport URLs retrieval hints
only; native graph publication plus release-signing evidence is the authority.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import stat
import subprocess
import tempfile
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Mapping
from urllib.parse import urlparse

from ilc_core.cli.d2e_submit_cli import _build_native_submit_sig_object
from ilc_core.consensus.binary_paths import installed_consensus_binary_command
from ilc_core.encoding.cidv1 import node_id_from_obj
from ilc_core.epoch.genesis_settlement_destination import (
    GENESIS_PUBLIC_SUBMIT_INGRESS_BLS_PK_HEX,
)
from ilc_core.identity.bls_backend import public_key_from_secret_key_hex
from ilc_core.release.installable_release_signature import (
    DEFAULT_GENESIS_LINEAGE_REF,
    DEFAULT_PRIOR_RELEASE_ENVELOPE_REF,
    DEFAULT_RELEASE_KEY_REGISTRATION_REF,
    build_envelope_skeleton,
    validate_envelope,
    validate_envelope_set,
)
from ilc_core.release.release_authority import release_signer_public_key_hex
from ilc_core.release.update_signature_verifier import verify_artifact_signature
from ilc_core.release.upgrade_check import validate_release_assertion


PHASE = "GAP-RELEASE-ASSERTION-PUBLISH-CEREMONY-00"
NETWORK_ID = "ilc-public-rc-01-testnet-harness"
DEFAULT_OUT_DIR = Path("out/gap_release_assertion_publish_ceremony_00")
DEFAULT_PACKAGE_RECEIPT = Path(
    "docs/specs/ilc_pypi_upload_receipt_GAP_PACKAGE_V0432_00b_v0.1.json"
)
DEFAULT_RECEIVER_EVIDENCE = Path(
    "out/gap_native_quic_receiver_rust_switchover_00/switchover_evidence.json"
)
DEFAULT_PUBLIC_SUBMIT_SECRET = Path.home() / ".ilc/genesis_public_submit_ingress_bls_sk.hex"
EXPECTED_RELEASE_SIGNER_PUBLIC_KEY_HEX = "5bf71c1e0ac93f2d7414b0dc315161fc4a57462c198ba1618e2890ec89a5b15a"

_HEX_32_RE = re.compile(r"^[0-9a-f]{64}$")
_HEX_64_RE = re.compile(r"^[0-9a-f]{128}$")
_HEX_48_RE = re.compile(r"^[0-9a-f]{96}$")
_SHA_RE = re.compile(r"^(?:[0-9a-f]{40}|[0-9a-f]{64})$")
_MAX_CLIENT_STDOUT = 65536
_MAX_CLIENT_STDERR = 8192


class ReleaseAssertionCeremonyError(ValueError):
    """Stable-token error for live release assertion ceremony failures."""

    def __init__(self, token: str, message: str | None = None) -> None:
        super().__init__(message or token)
        self.token = token


def _utc_now_z() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _load_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ReleaseAssertionCeremonyError(f"json_load_failed:{path}") from exc
    if not isinstance(payload, dict):
        raise ReleaseAssertionCeremonyError(f"json_not_object:{path}")
    return payload


def _atomic_write_json(path: Path, payload: Mapping[str, Any], *, mode: int = 0o644) -> Path:
    target = path.expanduser()
    target.parent.mkdir(parents=True, exist_ok=True)
    encoded = json.dumps(dict(payload), sort_keys=True, indent=2, allow_nan=False) + "\n"
    fd, tmp_name = tempfile.mkstemp(prefix=f".{target.name}.", suffix=".tmp", dir=str(target.parent))
    tmp_path = Path(tmp_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(encoded)
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(tmp_path, mode)
        os.replace(tmp_path, target)
    except Exception:
        try:
            tmp_path.unlink()
        except FileNotFoundError:
            pass
        raise
    return target


def _require_flags(production_execute: bool, confirm: bool) -> None:
    if not production_execute or not confirm:
        raise ReleaseAssertionCeremonyError("release_assertion_publish_ceremony_flags_required")


def _published_artifact_rows(package_receipt: Mapping[str, Any]) -> list[dict[str, Any]]:
    if package_receipt.get("release_id") != "ilc-core-0.4.32":
        raise ReleaseAssertionCeremonyError("package_receipt_release_id_unexpected")
    artifacts = package_receipt.get("published_artifacts")
    if not isinstance(artifacts, Mapping):
        raise ReleaseAssertionCeremonyError("package_receipt_artifacts_missing")
    rows: list[dict[str, Any]] = []
    for artifact_type, artifact_id in (
        ("wheel", "ilc-artifact:ilc-core-python-wheel-0432@phase-1628"),
        ("sdist", "ilc-artifact:ilc-core-python-sdist-0432@phase-1628"),
    ):
        artifact = artifacts.get(artifact_type)
        if not isinstance(artifact, Mapping):
            raise ReleaseAssertionCeremonyError("package_receipt_artifact_missing")
        sha256 = str(artifact.get("sha256", ""))
        if _HEX_32_RE.fullmatch(sha256) is None:
            raise ReleaseAssertionCeremonyError("package_receipt_artifact_sha_invalid")
        rows.append(
            {
                "artifact": dict(artifact),
                "artifact_id": artifact_id,
                "artifact_type": artifact_type,
                "artifact_sha256": sha256,
            }
        )
    return rows


def prepare_signing_request(
    *,
    package_receipt_path: Path,
    out_dir: Path,
    production_execute: bool,
    confirm: bool,
) -> dict[str, Any]:
    """Write unsigned envelope skeletons and offline signing instructions."""

    _require_flags(production_execute, confirm)
    receipt = _load_json(package_receipt_path)
    artifacts = _published_artifact_rows(receipt)
    envelopes: dict[str, dict[str, str]] = {}
    for row in artifacts:
        skeleton = build_envelope_skeleton(
            release_id="ilc-core-0.4.32",
            artifact_id=row["artifact_id"],
            artifact_sha256=row["artifact_sha256"],
            release_key_registration_ref=DEFAULT_RELEASE_KEY_REGISTRATION_REF,
            genesis_lineage_ref=DEFAULT_GENESIS_LINEAGE_REF,
            prior_release_envelope_ref=DEFAULT_PRIOR_RELEASE_ENVELOPE_REF,
        )
        validate_envelope(skeleton, allow_unsigned_placeholders=True)
        envelopes[row["artifact_id"]] = skeleton
    signing_request = {
        "ceremony_instruction": (
            "Human operator signs each signed_preimage_sha256 as raw 32 bytes "
            "with the Phase 1335 Ed25519 release key. Do not sign printable hex."
        ),
        "expected_signer_public_key_hex": release_signer_public_key_hex(),
        "generated_at_utc": _utc_now_z(),
        "non_claims": [
            "unsigned_skeleton_only",
            "no_native_quic_submit",
            "no_nginx_endpoint_update",
            "no_signature_stub_authorized",
            "no_private_key_read",
        ],
        "phase": PHASE,
        "release_id": "ilc-core-0.4.32",
        "signing_algorithm": "Ed25519",
        "signing_inputs": [
            {
                "artifact_id": artifact_id,
                "artifact_sha256": envelope["artifact_sha256"],
                "signed_preimage_sha256": envelope["signed_preimage_sha256"],
            }
            for artifact_id, envelope in sorted(envelopes.items())
        ],
        "unsigned_envelopes": envelopes,
    }
    _atomic_write_json(out_dir / "signing_request.json", signing_request)
    return signing_request


def _load_operator_signatures(path: Path) -> dict[str, Any]:
    payload = _load_json(path)
    signer = payload.get("signer_public_key_hex")
    if not isinstance(signer, str) or _HEX_32_RE.fullmatch(signer) is None:
        raise ReleaseAssertionCeremonyError("operator_signature_pubkey_invalid")
    if signer != EXPECTED_RELEASE_SIGNER_PUBLIC_KEY_HEX:
        raise ReleaseAssertionCeremonyError("operator_signature_embedded_pubkey_mismatch")
    if signer != release_signer_public_key_hex():
        raise ReleaseAssertionCeremonyError("operator_signature_pubkey_mismatch")
    signatures = payload.get("signatures")
    if not isinstance(signatures, Mapping) or not signatures:
        raise ReleaseAssertionCeremonyError("operator_signatures_missing")
    for artifact_id, signature in signatures.items():
        if not isinstance(artifact_id, str) or not isinstance(signature, str):
            raise ReleaseAssertionCeremonyError("operator_signature_invalid")
        if _HEX_64_RE.fullmatch(signature) is None:
            raise ReleaseAssertionCeremonyError("operator_signature_hex_invalid")
    return payload


def _complete_envelope_set(
    *,
    signing_request: Mapping[str, Any],
    operator_signatures: Mapping[str, Any],
) -> dict[str, Any]:
    signer = str(operator_signatures["signer_public_key_hex"])
    signatures = operator_signatures["signatures"]
    unsigned = signing_request.get("unsigned_envelopes")
    if not isinstance(unsigned, Mapping):
        raise ReleaseAssertionCeremonyError("signing_request_unsigned_envelopes_missing")
    envelopes: dict[str, dict[str, str]] = {}
    for artifact_id, skeleton in unsigned.items():
        if not isinstance(skeleton, Mapping):
            raise ReleaseAssertionCeremonyError("signing_request_envelope_invalid")
        signature_hex = signatures.get(artifact_id)
        if not isinstance(signature_hex, str):
            raise ReleaseAssertionCeremonyError("operator_signature_missing_for_artifact")
        envelope = {str(key): str(value) for key, value in skeleton.items()}
        envelope["signer_public_key_hex"] = signer
        envelope["signature_hex"] = signature_hex
        validate_envelope(envelope, allow_unsigned_placeholders=False)
        envelopes[str(artifact_id)] = envelope
    envelope_set = {
        "envelopes": envelopes,
        "schema_version": "GAP_RELEASE_SIGN_00b_v0.2",
        "version": "0.4.32",
    }
    try:
        validate_envelope_set(envelope_set)
    except Exception as exc:
        raise ReleaseAssertionCeremonyError("release_envelope_set_invalid") from exc
    for artifact_id, envelope in envelopes.items():
        try:
            verify_artifact_signature(
                artifact_id,
                envelope["artifact_sha256"],
                envelope_set,
                release_id="ilc-core-0.4.32",
                expected_signer_public_key_hex=signer,
            )
        except Exception as exc:
            raise ReleaseAssertionCeremonyError("release_envelope_signature_invalid") from exc
    return envelope_set


def _require_public_submit_secret(path: Path) -> str:
    if not path.is_file():
        raise ReleaseAssertionCeremonyError("public_submit_bls_secret_missing")
    mode = stat.S_IMODE(path.stat().st_mode)
    if mode & 0o077:
        raise ReleaseAssertionCeremonyError("public_submit_bls_secret_mode_insecure")
    secret = path.read_text(encoding="utf-8").strip()
    if _HEX_32_RE.fullmatch(secret) is None:
        raise ReleaseAssertionCeremonyError("public_submit_bls_secret_invalid")
    derived = public_key_from_secret_key_hex(secret)
    if derived != GENESIS_PUBLIC_SUBMIT_INGRESS_BLS_PK_HEX:
        raise ReleaseAssertionCeremonyError("public_submit_bls_public_key_mismatch")
    return secret


def build_release_assertion(
    *,
    envelope_set: Mapping[str, Any],
    package_receipt_path: Path,
    release_date: str,
) -> dict[str, Any]:
    """Build an upgrade-check-compatible SoftwareReleaseNode assertion."""

    package_receipt = _load_json(package_receipt_path)
    source_commit = str(package_receipt.get("source_private_commit_at_upload", ""))
    if _SHA_RE.fullmatch(source_commit) is None:
        raise ReleaseAssertionCeremonyError("package_receipt_source_commit_invalid")
    published = {row["artifact_id"]: row for row in _published_artifact_rows(package_receipt)}
    envelopes = envelope_set.get("envelopes")
    if not isinstance(envelopes, Mapping):
        raise ReleaseAssertionCeremonyError("release_envelopes_missing")

    artifact_nodes: list[dict[str, Any]] = []
    for artifact_id in sorted(envelopes):
        row = published.get(str(artifact_id))
        if row is None:
            raise ReleaseAssertionCeremonyError("release_envelope_unknown_artifact_id")
        artifact = row["artifact"]
        body = {
            "artifact_id": artifact_id,
            "artifact_type": row["artifact_type"],
            "filename": artifact.get("filename"),
            "node_kind": "ArtifactNode",
            "package_name": "ilc-core",
            "package_version": "0.4.32",
            "pypi_url": artifact.get("url"),
            "schema_version": "artifact_node.v0.1",
            "sha256": artifact.get("sha256"),
            "size_bytes": artifact.get("size"),
        }
        artifact_nodes.append({**body, "cid": node_id_from_obj(body)})

    artifact_cid_by_id = {str(row["artifact_id"]): row["cid"] for row in artifact_nodes}
    build_recipe_body = {
        "build_command": "python -m build",
        "build_date": release_date,
        "build_env_hash": _sha256_file(package_receipt_path),
        "build_toolchain": "python-build",
        "builder_agent_id": "phase:GAP-PACKAGE-V0432-00a",
        "node_kind": "BuildRecipeNode",
        "reproducibility_hash": hashlib.sha256(
            json.dumps(dict(envelope_set), sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest(),
        "schema_version": "build_recipe_node.v0.1",
        "source_commit": source_commit,
    }
    build_recipe_cid = node_id_from_obj(build_recipe_body)
    release_node_body = {
        "artifact_cids": [row["cid"] for row in artifact_nodes],
        "build_recipe_cid": build_recipe_cid,
        "changelog_hash": _sha256_file(package_receipt_path),
        "node_kind": "SoftwareReleaseNode",
        "package_name": "ilc-core",
        "release_channel": "public_rc",
        "release_date": release_date,
        "release_key_pubkey": release_signer_public_key_hex(),
        "release_signature_ref": "docs/specs/ilc_core_0432_release_envelopes_GAP_RELEASE_ASSERTION_PUBLISH_CEREMONY_00_v0.1.json",
        "schema_version": "software_release_node.v0.1",
        "source_commit": source_commit,
        "version": "0.4.32",
    }
    release_node = {**release_node_body, "cid": node_id_from_obj(release_node_body)}
    attestation_edges = []
    for artifact_id in sorted(envelopes):
        envelope = envelopes[artifact_id]
        if not isinstance(envelope, Mapping):
            raise ReleaseAssertionCeremonyError("release_envelope_not_object")
        attestation_edges.append(
            {
                "artifact_id": envelope["artifact_id"],
                "artifact_sha256": envelope["artifact_sha256"],
                "attestation_date": release_date,
                "edge_type": "RELEASE_ATTESTS_ARTIFACT",
                "genesis_lineage_ref": envelope["genesis_lineage_ref"],
                "prior_release_envelope_ref": envelope["prior_release_envelope_ref"],
                "release_key_registration_ref": envelope["release_key_registration_ref"],
                "schema_version": "release_attestation_edge.v0.1",
                "signed_preimage_domain": envelope["signed_preimage_domain"],
                "signed_preimage_sha256": envelope["signed_preimage_sha256"],
                "signer_public_key_hex": envelope["signer_public_key_hex"],
                "signature_hex": envelope["signature_hex"],
                "signing_algorithm": envelope["signing_algorithm"],
                "source": release_node["cid"],
                "target": artifact_cid_by_id[str(artifact_id)],
            }
        )
    assertion_core: dict[str, Any] = {
        "artifact_nodes": artifact_nodes,
        "build_recipe_nodes": [{**build_recipe_body, "cid": build_recipe_cid}],
        "release_attestation_edges": attestation_edges,
        "schema_version": "software_release_assertion.v0.1",
        "software_release_node": release_node,
    }
    assertion_core["assertion_cid"] = node_id_from_obj(assertion_core)
    try:
        validate_release_assertion(assertion_core)
    except Exception as exc:
        raise ReleaseAssertionCeremonyError("release_assertion_upgrade_check_invalid") from exc
    return assertion_core


def build_native_submit_envelope(
    *,
    assertion_core: Mapping[str, Any],
    public_submit_bls_secret_hex: str,
    epoch: int,
) -> dict[str, Any]:
    if epoch < 0:
        raise ReleaseAssertionCeremonyError("epoch_invalid")
    public_key_hex = public_key_from_secret_key_hex(public_submit_bls_secret_hex)
    envelope: dict[str, Any] = {
        "agent_id": public_key_hex,
        "epoch": epoch,
        "payload": {
            "content": {
                "phase": PHASE,
                "software_release_assertion": dict(assertion_core),
            },
            "epistemic_type": "objective",
            "parent_node_ids": [],
            "primitive_type": "observation",
        },
        "primitive": "assert.truth",
        "v": 1,
    }
    envelope["sig"] = _build_native_submit_sig_object(
        envelope,
        public_submit_bls_secret_hex,
        network_id=NETWORK_ID,
    )
    return envelope


def _load_receiver(path: Path) -> dict[str, str]:
    data = _load_json(path)
    if data.get("transport_profile") != "native_quic_full_rust":
        raise ReleaseAssertionCeremonyError("receiver_not_full_rust_native_quic")
    if data.get("bridge_permanent") is not False:
        raise ReleaseAssertionCeremonyError("receiver_bridge_permanent_not_false")
    endpoint = data.get("endpoint")
    if not isinstance(endpoint, str):
        raise ReleaseAssertionCeremonyError("receiver_endpoint_missing")
    parsed = urlparse(endpoint)
    if parsed.scheme != "quic" or not parsed.hostname or parsed.port is None:
        raise ReleaseAssertionCeremonyError("receiver_endpoint_invalid")
    fingerprint = data.get("tls_fingerprint_sha256_der")
    if not isinstance(fingerprint, str) or _HEX_32_RE.fullmatch(fingerprint) is None:
        raise ReleaseAssertionCeremonyError("receiver_tls_fingerprint_invalid")
    return {
        "endpoint": f"{parsed.hostname}:{parsed.port}",
        "endpoint_uri": endpoint,
        "tls_fingerprint_sha256_der": fingerprint,
    }


def _client_command() -> list[str]:
    installed = installed_consensus_binary_command("ilc_native_submit_client")
    if installed is not None:
        return list(installed)
    for candidate in (
        Path("ilc_consensus/target/release/ilc_native_submit_client"),
        Path("ilc_consensus/target/debug/ilc_native_submit_client"),
    ):
        if candidate.is_file() and os.access(candidate, os.X_OK):
            return [str(candidate)]
    found = shutil.which("ilc_native_submit_client")
    if found:
        return [found]
    raise ReleaseAssertionCeremonyError("ilc_native_submit_client_not_found")


def _run_client(*, endpoint: str, fingerprint: str, envelope: Mapping[str, Any]) -> dict[str, Any]:
    argv = [
        *_client_command(),
        "--endpoint",
        endpoint,
        "--expected-tls-fingerprint",
        fingerprint,
    ]
    body = json.dumps(
        dict(envelope),
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    completed = subprocess.run(
        argv,
        input=body,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
        timeout=30,
    )
    if len(completed.stdout) > _MAX_CLIENT_STDOUT:
        raise ReleaseAssertionCeremonyError("native_submit_stdout_too_large")
    if len(completed.stderr) > _MAX_CLIENT_STDERR:
        raise ReleaseAssertionCeremonyError("native_submit_stderr_too_large")
    stdout = completed.stdout.decode("utf-8", errors="replace").strip()
    stderr = completed.stderr.decode("utf-8", errors="replace").strip()
    response: Any = None
    if stdout:
        try:
            response = json.loads(stdout)
        except json.JSONDecodeError as exc:
            raise ReleaseAssertionCeremonyError("native_submit_stdout_invalid_json") from exc
    return {
        "argv": [Path(argv[0]).name, *argv[1:]],
        "exit_code": completed.returncode,
        "response": response,
        "stderr": stderr,
        "stdout": stdout,
    }


def finalize_and_publish(
    *,
    signing_request_path: Path,
    operator_signatures_path: Path,
    package_receipt_path: Path,
    receiver_evidence_path: Path,
    public_submit_secret_path: Path,
    out_dir: Path,
    nginx_well_known_path: Path | None,
    epoch: int,
    production_execute: bool,
    confirm: bool,
) -> dict[str, Any]:
    """Compatibility wrapper: assemble, then publish."""

    assembly = assemble_signed_assertion(
        signing_request_path=signing_request_path,
        operator_signatures_path=operator_signatures_path,
        package_receipt_path=package_receipt_path,
        out_dir=out_dir,
        production_execute=production_execute,
        confirm=confirm,
    )
    return publish_assembled_assertion(
        assertion_core_path=Path(str(assembly["release_assertion_core_path"])),
        receiver_evidence_path=receiver_evidence_path,
        public_submit_secret_path=public_submit_secret_path,
        out_dir=out_dir,
        nginx_well_known_path=nginx_well_known_path,
        epoch=epoch,
        production_execute=production_execute,
        confirm=confirm,
    )


def assemble_signed_assertion(
    *,
    signing_request_path: Path,
    operator_signatures_path: Path,
    package_receipt_path: Path,
    out_dir: Path,
    production_execute: bool,
    confirm: bool,
) -> dict[str, Any]:
    """Verify human signatures and write the local release assertion JSON."""

    _require_flags(production_execute, confirm)
    signing_request = _load_json(signing_request_path)
    operator_signatures = _load_operator_signatures(operator_signatures_path)
    envelope_set = _complete_envelope_set(
        signing_request=signing_request,
        operator_signatures=operator_signatures,
    )
    release_date = _utc_now_z()
    assertion_core = build_release_assertion(
        envelope_set=envelope_set,
        package_receipt_path=package_receipt_path,
        release_date=release_date,
    )
    validation_result = validate_release_assertion(assertion_core)
    envelope_path = _atomic_write_json(
        out_dir / "release_envelope_set_ceremony.json",
        envelope_set,
    )
    assertion_path = _atomic_write_json(out_dir / "release_assertion_core.json", assertion_core)
    evidence = {
        "assertion_cid": assertion_core["assertion_cid"],
        "date": release_date,
        "expected_release_signer_public_key_hex": EXPECTED_RELEASE_SIGNER_PUBLIC_KEY_HEX,
        "non_claims": [
            "no_native_quic_submit",
            "no_nginx_endpoint_update",
            "no_package_upload",
            "no_pypi_mutation",
            "no_cdl_mutation",
        ],
        "phase": PHASE,
        "release_assertion_core_path": str(assertion_path),
        "release_envelope_set_path": str(envelope_path),
        "release_signer_public_key_hex": release_signer_public_key_hex(),
        "validation_result": validation_result,
    }
    _atomic_write_json(out_dir / "assembly_evidence.json", evidence)
    return evidence


def publish_assembled_assertion(
    *,
    assertion_core_path: Path,
    receiver_evidence_path: Path,
    public_submit_secret_path: Path,
    out_dir: Path,
    nginx_well_known_path: Path | None,
    epoch: int,
    production_execute: bool,
    confirm: bool,
) -> dict[str, Any]:
    """Live-submit an already assembled assertion and optionally write mirror JSON."""

    _require_flags(production_execute, confirm)
    assertion_core = _load_json(assertion_core_path)
    try:
        pre_submit_validation = validate_release_assertion(assertion_core)
    except Exception as exc:
        raise ReleaseAssertionCeremonyError("release_assertion_upgrade_check_invalid") from exc
    public_submit_secret = _require_public_submit_secret(public_submit_secret_path)
    receiver = _load_receiver(receiver_evidence_path)
    native_envelope = build_native_submit_envelope(
        assertion_core=assertion_core,
        public_submit_bls_secret_hex=public_submit_secret,
        epoch=epoch,
    )
    submit_result = _run_client(
        endpoint=receiver["endpoint"],
        fingerprint=receiver["tls_fingerprint_sha256_der"],
        envelope=native_envelope,
    )
    response = submit_result.get("response")
    if not isinstance(response, Mapping) or response.get("ok") is not True:
        raise ReleaseAssertionCeremonyError("native_submit_live_publish_failed")
    release_date = _utc_now_z()
    graph_publication = {
        "native_submit_node_id": response.get("node_id"),
        "receiver_profile": response.get("receiver_profile"),
        "submitted_at_utc": release_date,
        "target_receiver_uri": receiver["endpoint_uri"],
        "transport_profile": "native_quic_full_rust",
    }
    # Publication receipts are evidence about transport execution, not fields
    # of the immutable software_release_assertion.v0.1 wire object.
    well_known_latest = {**assertion_core, "native_submit_envelope": native_envelope}
    _atomic_write_json(out_dir / "native_submit_envelope.json", native_envelope, mode=0o600)
    _atomic_write_json(out_dir / "native_submit_result.json", submit_result)
    local_well_known = _atomic_write_json(out_dir / "well_known_latest.json", well_known_latest)
    post_write_validation = validate_release_assertion(well_known_latest)
    https_well_known_endpoint: dict[str, Any]
    nginx_written: str | None = None
    if nginx_well_known_path is None:
        https_well_known_endpoint = {
            "disposition": "deferred_mirror",
            "reason": (
                "CDL-121 prelocks transport URLs as retrieval hints only; "
                "native QUIC graph publication plus Phase 1335 release-signing "
                "evidence is the release authority."
            ),
            "retroactive_correction": (
                "Supersedes the Window 1625-1632 Phase 2 assumption that the "
                "HTTPS well-known endpoint is a ceremony completion gate."
            ),
        }
    else:
        nginx_written = str(_atomic_write_json(nginx_well_known_path, well_known_latest))
        nginx_payload = _load_json(Path(nginx_written))
        post_write_validation = validate_release_assertion(nginx_payload)
        https_well_known_endpoint = {
            "disposition": "written_and_validated",
            "nginx_well_known_path": nginx_written,
        }
    evidence = {
        "assertion_cid": assertion_core["assertion_cid"],
        "date": release_date,
        "epoch": epoch,
        "graph_publication": graph_publication,
        "https_well_known_endpoint": https_well_known_endpoint,
        "nginx_well_known_path": nginx_written,
        "non_claims": [
            "no_package_upload",
            "no_pypi_mutation",
            "no_new_ilc_core_runtime_code",
            "no_lmdb_schema_change",
            "no_cdl_mutation",
            "no_wallet_ecu_ilc_settlement_path",
            "no_epoch_transition",
        ],
        "phase": PHASE,
        "pre_submit_validation_result": pre_submit_validation,
        "post_write_validation_result": post_write_validation,
        "release_signer_public_key_hex": release_signer_public_key_hex(),
        "submit_result": submit_result,
        "target_receiver_uri": receiver["endpoint_uri"],
        "tokens": ["release_assertion_publish_ceremony_complete_GAP_RELEASE_ASSERTION_PUBLISH_CEREMONY_00"],
        "transport_profile": "native_quic_full_rust",
        "well_known_latest_path": str(local_well_known),
    }
    _atomic_write_json(out_dir / "publish_evidence.json", evidence)
    return evidence


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the live release assertion publish ceremony.")
    parser.add_argument("mode", choices=["prepare", "assemble", "publish", "finalize"])
    parser.add_argument("--package-receipt", default=str(DEFAULT_PACKAGE_RECEIPT))
    parser.add_argument("--receiver-evidence", default=str(DEFAULT_RECEIVER_EVIDENCE))
    parser.add_argument("--public-submit-secret", default=str(DEFAULT_PUBLIC_SUBMIT_SECRET))
    parser.add_argument("--signing-request", default=str(DEFAULT_OUT_DIR / "signing_request.json"))
    parser.add_argument("--assertion-core", default=str(DEFAULT_OUT_DIR / "release_assertion_core.json"))
    parser.add_argument("--operator-signatures", default="")
    parser.add_argument("--nginx-well-known-path", default="")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    parser.add_argument("--epoch", type=int, default=1)
    parser.add_argument("--production-execute", action="store_true")
    parser.add_argument("--confirm-release-assertion-publish-ceremony", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    try:
        args = parse_args(argv)
        if args.mode == "prepare":
            payload = prepare_signing_request(
                package_receipt_path=Path(args.package_receipt),
                out_dir=Path(args.out_dir),
                production_execute=bool(args.production_execute),
                confirm=bool(args.confirm_release_assertion_publish_ceremony),
            )
        elif args.mode == "assemble":
            if not args.operator_signatures:
                raise ReleaseAssertionCeremonyError("operator_signatures_path_required")
            nginx_path = Path(args.nginx_well_known_path) if args.nginx_well_known_path else None
            payload = finalize_and_publish(
                signing_request_path=Path(args.signing_request),
                operator_signatures_path=Path(args.operator_signatures),
                package_receipt_path=Path(args.package_receipt),
                receiver_evidence_path=Path(args.receiver_evidence),
                public_submit_secret_path=Path(args.public_submit_secret),
                out_dir=Path(args.out_dir),
                nginx_well_known_path=nginx_path,
                epoch=int(args.epoch),
                production_execute=bool(args.production_execute),
                confirm=bool(args.confirm_release_assertion_publish_ceremony),
            )
        elif args.mode == "publish":
            nginx_path = Path(args.nginx_well_known_path) if args.nginx_well_known_path else None
            payload = publish_assembled_assertion(
                assertion_core_path=Path(args.assertion_core),
                receiver_evidence_path=Path(args.receiver_evidence),
                public_submit_secret_path=Path(args.public_submit_secret),
                out_dir=Path(args.out_dir),
                nginx_well_known_path=nginx_path,
                epoch=int(args.epoch),
                production_execute=bool(args.production_execute),
                confirm=bool(args.confirm_release_assertion_publish_ceremony),
            )
        else:
            if not args.operator_signatures:
                raise ReleaseAssertionCeremonyError("operator_signatures_path_required")
            nginx_path = Path(args.nginx_well_known_path) if args.nginx_well_known_path else None
            payload = finalize_and_publish(
                signing_request_path=Path(args.signing_request),
                operator_signatures_path=Path(args.operator_signatures),
                package_receipt_path=Path(args.package_receipt),
                receiver_evidence_path=Path(args.receiver_evidence),
                public_submit_secret_path=Path(args.public_submit_secret),
                out_dir=Path(args.out_dir),
                nginx_well_known_path=nginx_path,
                epoch=int(args.epoch),
                production_execute=bool(args.production_execute),
                confirm=bool(args.confirm_release_assertion_publish_ceremony),
            )
        print(json.dumps(payload, sort_keys=True, indent=2, allow_nan=False))
    except ReleaseAssertionCeremonyError as exc:
        print(exc.token)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
