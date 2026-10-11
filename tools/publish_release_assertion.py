#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
"""Build dry-run ILC software release assertions.

This tooling phase deliberately does not submit to the native QUIC receiver and
does not read Genesis key material. It constructs verifier-compatible release
assertion JSON using fixture signing keys only.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import stat
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from ilc_core.cli.d2e_submit_cli import _build_native_submit_sig_object
from ilc_core.encoding.cidv1 import node_id_from_obj
from ilc_core.identity.bls_backend import public_key_from_secret_key_hex
from ilc_core.release.installable_release_signature import (
    DEFAULT_GENESIS_LINEAGE_REF,
    DEFAULT_PRIOR_RELEASE_ENVELOPE_REF,
    DEFAULT_RELEASE_KEY_REGISTRATION_REF,
    SIGNED_PREIMAGE_DOMAIN,
    compute_signed_preimage_sha256,
)


_HEX_32_RE = re.compile(r"^[0-9a-f]{64}$")
_VERSION_RE = re.compile(r"^[0-9]+(?:\.[0-9]+){1,3}$")
_GIT_SHA_RE = re.compile(r"^(?:[0-9a-f]{40}|[0-9a-f]{64})$")
_ARTIFACT_ID_RE = re.compile(r"^ilc-artifact:[a-z0-9][a-z0-9-]*@phase-[1-9][0-9]*$")
_ALLOWED_CHANNELS = frozenset({"public_rc", "testnet", "mainnet", "dev", "stable", "rc", "beta"})
_DEFAULT_FIXTURE_BLS_SECRET_HEX = "11" * 32
_DEFAULT_FIXTURE_RELEASE_SECRET_HEX = "22" * 32
_DEFAULT_RELEASE_EPOCH = 1
_DEFAULT_ARTIFACT_PHASE = 1626


class ReleaseAssertionToolingError(ValueError):
    """Stable-token error for release assertion tooling."""

    def __init__(self, token: str, message: str | None = None) -> None:
        super().__init__(message or token)
        self.token = token


def _require_match(value: str, pattern: re.Pattern[str], token: str) -> str:
    if pattern.fullmatch(value) is None:
        raise ReleaseAssertionToolingError(token)
    return value


def _require_positive_int(value: str, token: str) -> int:
    try:
        parsed = int(value)
    except ValueError as exc:
        raise ReleaseAssertionToolingError(token) from exc
    if parsed <= 0:
        raise ReleaseAssertionToolingError(token)
    return parsed


def _utc_now_z() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _canonical_json_bytes(payload: Mapping[str, Any]) -> bytes:
    return json.dumps(
        dict(payload),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("utf-8")


def _atomic_write_json(path: Path, payload: Mapping[str, Any]) -> Path:
    target = path.expanduser()
    parent = target.parent
    parent.mkdir(parents=True, exist_ok=True)
    encoded = json.dumps(dict(payload), sort_keys=True, indent=2, allow_nan=False) + "\n"
    fd, tmp_name = tempfile.mkstemp(prefix=f".{target.name}.", suffix=".tmp", dir=str(parent))
    tmp_path = Path(tmp_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(encoded)
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(tmp_path, stat.S_IRUSR | stat.S_IWUSR)
        os.replace(tmp_path, target)
    except Exception:
        try:
            tmp_path.unlink()
        except FileNotFoundError:
            pass
        raise
    return target


def _release_public_key_hex(secret_hex: str) -> str:
    secret_hex = _require_match(secret_hex, _HEX_32_RE, "fixture_release_signing_key_invalid")
    key = Ed25519PrivateKey.from_private_bytes(bytes.fromhex(secret_hex)).public_key()
    return key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    ).hex()


def _sign_release_preimage(secret_hex: str, preimage_sha256: str) -> str:
    secret_hex = _require_match(secret_hex, _HEX_32_RE, "fixture_release_signing_key_invalid")
    _require_match(preimage_sha256, _HEX_32_RE, "signed_preimage_sha256_invalid")
    key = Ed25519PrivateKey.from_private_bytes(bytes.fromhex(secret_hex))
    return key.sign(bytes.fromhex(preimage_sha256)).hex()


def default_artifact_id(version: str) -> str:
    version_token = version.replace(".", "")
    return f"ilc-artifact:ilc-core-python-wheel-{version_token}@phase-{_DEFAULT_ARTIFACT_PHASE}"


def build_release_assertion(
    *,
    version: str,
    artifact_sha256: str,
    artifact_cid: str,
    artifact_size: int,
    source_commit: str,
    channel: str = "stable",
    artifact_id: str | None = None,
    build_recipe_cid: str | None = None,
    changelog_hash: str | None = None,
    release_date: str | None = None,
    fixture_release_signing_key_hex: str = _DEFAULT_FIXTURE_RELEASE_SECRET_HEX,
    fixture_bls_signing_key_hex: str = _DEFAULT_FIXTURE_BLS_SECRET_HEX,
    epoch: int = _DEFAULT_RELEASE_EPOCH,
) -> dict[str, Any]:
    """Return a dry-run release assertion payload with fixture signatures."""

    version = _require_match(version, _VERSION_RE, "release_version_invalid")
    artifact_sha256 = _require_match(artifact_sha256, _HEX_32_RE, "artifact_sha256_invalid")
    source_commit = _require_match(source_commit, _GIT_SHA_RE, "source_commit_invalid")
    if channel not in _ALLOWED_CHANNELS:
        raise ReleaseAssertionToolingError("release_channel_invalid")
    if artifact_size <= 0:
        raise ReleaseAssertionToolingError("artifact_size_invalid")
    artifact_id = artifact_id or default_artifact_id(version)
    artifact_id = _require_match(artifact_id, _ARTIFACT_ID_RE, "artifact_id_invalid")
    release_date = release_date or _utc_now_z()
    changelog_hash = changelog_hash or ("0" * 64)
    changelog_hash = _require_match(changelog_hash, _HEX_32_RE, "changelog_hash_invalid")
    release_pubkey = _release_public_key_hex(fixture_release_signing_key_hex)
    release_id = f"ilc-core-{version}"
    signed_preimage_sha256 = compute_signed_preimage_sha256(
        release_id=release_id,
        artifact_id=artifact_id,
        artifact_sha256=artifact_sha256,
        release_key_registration_ref=DEFAULT_RELEASE_KEY_REGISTRATION_REF,
        genesis_lineage_ref=DEFAULT_GENESIS_LINEAGE_REF,
        prior_release_envelope_ref=DEFAULT_PRIOR_RELEASE_ENVELOPE_REF,
    )
    signature_hex = _sign_release_preimage(
        fixture_release_signing_key_hex,
        signed_preimage_sha256,
    )
    artifact_node = {
        "artifact_type": "wheel",
        "cid": artifact_cid,
        "node_kind": "ArtifactNode",
        "package_name": "ilc-core",
        "package_version": version,
        "schema_version": "artifact_node.v0.1",
        "sha256": artifact_sha256,
        "size_bytes": artifact_size,
    }
    build_recipe = {
        "build_command": "python -m build",
        "build_date": release_date,
        "build_env_hash": "0" * 64,
        "build_toolchain": "python-build",
        "builder_agent_id": "fixture-release-tooling",
        "node_kind": "BuildRecipeNode",
        "reproducibility_hash": "0" * 64,
        "schema_version": "build_recipe_node.v0.1",
        "source_commit": source_commit,
    }
    build_recipe_cid = build_recipe_cid or node_id_from_obj(build_recipe)
    release_node_body = {
        "artifact_cids": [artifact_cid],
        "build_recipe_cid": build_recipe_cid,
        "changelog_hash": changelog_hash,
        "node_kind": "SoftwareReleaseNode",
        "package_name": "ilc-core",
        "release_channel": channel,
        "release_date": release_date,
        "release_key_pubkey": release_pubkey,
        "release_signature_ref": f"release-attestation:{artifact_id}",
        "schema_version": "software_release_node.v0.1",
        "source_commit": source_commit,
        "version": version,
    }
    release_node = dict(release_node_body)
    release_node["cid"] = node_id_from_obj(release_node_body)
    attestation_edge = {
        "artifact_id": artifact_id,
        "artifact_sha256": artifact_sha256,
        "attestation_date": release_date,
        "edge_type": "RELEASE_ATTESTS_ARTIFACT",
        "genesis_lineage_ref": DEFAULT_GENESIS_LINEAGE_REF,
        "prior_release_envelope_ref": DEFAULT_PRIOR_RELEASE_ENVELOPE_REF,
        "release_key_registration_ref": DEFAULT_RELEASE_KEY_REGISTRATION_REF,
        "schema_version": "release_attestation_edge.v0.1",
        "signed_preimage_domain": SIGNED_PREIMAGE_DOMAIN,
        "signed_preimage_sha256": signed_preimage_sha256,
        "signer_public_key_hex": release_pubkey,
        "signature_hex": signature_hex,
        "signing_algorithm": "Ed25519",
        "source": release_node["cid"],
        "target": artifact_cid,
    }
    assertion_core = {
        "artifact_nodes": [artifact_node],
        "build_recipe_nodes": [{**build_recipe, "cid": build_recipe_cid}],
        "release_attestation_edges": [attestation_edge],
        "schema_version": "software_release_assertion.v0.1",
        "software_release_node": release_node,
    }
    assertion_core["assertion_cid"] = node_id_from_obj(assertion_core)
    native_envelope = build_fixture_native_submit_envelope(
        assertion_core=assertion_core,
        fixture_bls_signing_key_hex=fixture_bls_signing_key_hex,
        epoch=epoch,
    )
    return {
        **assertion_core,
        "fixture_release_authority": True,
        "native_submit_envelope": native_envelope,
        "non_claims": [
            "fixture_signatures_only",
            "no_genesis_key_use",
            "no_live_native_quic_submit",
            "no_lmdb_write",
            "no_public_cache_update",
        ],
    }


def build_fixture_native_submit_envelope(
    *,
    assertion_core: Mapping[str, Any],
    fixture_bls_signing_key_hex: str,
    epoch: int,
) -> dict[str, Any]:
    """Build a fixture-signed native submit envelope around a release assertion."""

    _require_match(fixture_bls_signing_key_hex, _HEX_32_RE, "fixture_bls_signing_key_invalid")
    if epoch < 0:
        raise ReleaseAssertionToolingError("epoch_invalid")
    agent_id = public_key_from_secret_key_hex(fixture_bls_signing_key_hex)
    envelope: dict[str, Any] = {
        "agent_id": agent_id,
        "epoch": epoch,
        "payload": {
            "content": {"software_release_assertion": dict(assertion_core)},
            "epistemic_type": "objective",
            "parent_node_ids": [],
            "primitive_type": "observation",
        },
        "primitive": "assert.truth",
        "sig": "UNSIGNED",
        "v": 1,
    }
    envelope["sig"] = _build_native_submit_sig_object(envelope, fixture_bls_signing_key_hex)
    return envelope


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build dry-run ILC SoftwareReleaseNode assertion JSON.",
    )
    parser.add_argument("--version", required=True)
    parser.add_argument("--artifact-sha256", required=True)
    parser.add_argument("--artifact-cid", required=True)
    parser.add_argument("--artifact-size", required=True)
    parser.add_argument("--source-commit", required=True)
    parser.add_argument("--artifact-id", default="")
    parser.add_argument("--build-recipe-cid", default="")
    parser.add_argument("--changelog-hash", default="")
    parser.add_argument("--release-date", default="")
    parser.add_argument("--channel", default="stable")
    parser.add_argument("--epoch", type=int, default=_DEFAULT_RELEASE_EPOCH)
    parser.add_argument("--fixture-signing-key-hex", default=_DEFAULT_FIXTURE_BLS_SECRET_HEX)
    parser.add_argument(
        "--fixture-release-signing-key-hex",
        default=_DEFAULT_FIXTURE_RELEASE_SECRET_HEX,
    )
    parser.add_argument("--output", default="")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    if not args.dry_run:
        raise ReleaseAssertionToolingError("live_publish_not_authorized_in_tooling_phase")
    return args


def main(argv: list[str] | None = None) -> int:
    try:
        args = parse_args(argv)
        payload = build_release_assertion(
            version=str(args.version),
            artifact_sha256=str(args.artifact_sha256),
            artifact_cid=str(args.artifact_cid),
            artifact_size=_require_positive_int(str(args.artifact_size), "artifact_size_invalid"),
            source_commit=str(args.source_commit),
            channel=str(args.channel),
            artifact_id=str(args.artifact_id or "") or None,
            build_recipe_cid=str(args.build_recipe_cid or "") or None,
            changelog_hash=str(args.changelog_hash or "") or None,
            release_date=str(args.release_date or "") or None,
            fixture_release_signing_key_hex=str(args.fixture_release_signing_key_hex),
            fixture_bls_signing_key_hex=str(args.fixture_signing_key_hex),
            epoch=int(args.epoch),
        )
        if args.output:
            _atomic_write_json(Path(args.output), payload)
        print(json.dumps(payload, sort_keys=True, indent=2, allow_nan=False))
    except ReleaseAssertionToolingError as exc:
        print(exc.token)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
