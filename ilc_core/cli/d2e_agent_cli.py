# SPDX-License-Identifier: AGPL-3.0-only
"""Phase 420 D2e agent identity CLI helpers."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any

from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives.serialization import Encoding, NoEncryption, PrivateFormat

from ilc_core.identity.agent_id_runtime import (
    CDL_042_DEPENDENCY as RUNTIME_CDL_042_DEPENDENCY,
    derive_agent_id,
)

D2E_AGENT_CLI_VERSION = "d2e_agent_cli_420.v0.1"
AGENT_KEYGEN_CLI_VERSION = "agent_keygen_cli_GAP_AGENT_KEYGEN_00.v0.1"
CDL_042_DEPENDENCY = RUNTIME_CDL_042_DEPENDENCY

if CDL_042_DEPENDENCY != "cdl_042_ratified_407.v0.1":
    raise ValueError("agent_cli_dependency_mismatch")


def handle_agent_derive(root_key_hex: str) -> dict[str, Any]:
    """Execute the derive subcommand given the hex-encoded root key string."""

    try:
        key_bytes = bytes.fromhex(root_key_hex)
    except ValueError as exc:
        raise ValueError("agent_derive_invalid_hex") from exc

    return {
        "subcommand": "derive",
        "agent_id": derive_agent_id(key_bytes),
        "agent_id_format": "legacy_agent_prefixed_sha256",
        "deprecated": True,
        "public_rc_submit_compatible": False,
        "version": D2E_AGENT_CLI_VERSION,
    }


def handle_agent_inspect(record_json: str) -> dict[str, Any]:
    """Execute the inspect subcommand given the record JSON file path string."""

    path = Path(record_json)
    if not path.exists():
        raise ValueError("agent_inspect_record_not_found")

    try:
        record = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError("agent_inspect_record_invalid_json") from exc

    if not isinstance(record, dict):
        raise ValueError("agent_inspect_record_not_object")

    return {
        "subcommand": "inspect",
        "record_path": str(path),
        "fields": sorted(record.keys()),
        "record": record,
        "version": D2E_AGENT_CLI_VERSION,
    }


def agent_hotkey_fingerprint(public_key_bytes: bytes) -> str:
    """Return the canonical hotkey fingerprint over raw 32-byte Ed25519 pubkey bytes."""

    if not isinstance(public_key_bytes, bytes) or len(public_key_bytes) != 32:
        raise ValueError("agent_keygen_invalid_public_key_bytes")
    return hashlib.sha256(public_key_bytes).hexdigest()


def _write_private_key_pem_atomic(final_path: Path, key_bytes: bytes) -> None:
    """Write private-key bytes with atomic replacement and owner-only permissions."""

    if final_path.exists():
        raise ValueError("agent_keygen_output_exists")

    try:
        final_path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    except OSError as exc:
        raise ValueError("agent_keygen_output_directory_unavailable") from exc

    tmp_path: str | None = None
    fd: int | None = None
    try:
        fd, tmp_path = tempfile.mkstemp(
            prefix=f".{final_path.name}.",
            suffix=".tmp",
            dir=str(final_path.parent),
        )
        os.fchmod(fd, 0o600)
        with os.fdopen(fd, "wb") as handle:
            fd = None
            handle.write(key_bytes)
            handle.flush()
            os.fsync(handle.fileno())
        # Atomic exclusive create: os.link fails with FileExistsError if
        # final_path already exists, closing the TOCTOU between the initial
        # existence check (line 80) and the write.  os.replace would silently
        # overwrite a concurrently created key file; os.link does not.
        try:
            os.link(tmp_path, str(final_path))
        except FileExistsError:
            raise ValueError("agent_keygen_output_exists")
        except OSError as exc:
            raise ValueError("agent_keygen_output_write_failed") from exc
        os.unlink(tmp_path)
        tmp_path = None
        os.chmod(final_path, 0o600)
    finally:
        if fd is not None:
            os.close(fd)
        if tmp_path is not None and os.path.exists(tmp_path):
            os.unlink(tmp_path)


def handle_agent_keygen(output: str | None = None) -> dict[str, Any]:
    """Generate a local Ed25519 action-signing hotkey PEM and return public metadata."""

    private_key = ed25519.Ed25519PrivateKey.generate()
    private_key_pem = private_key.private_bytes(
        encoding=Encoding.PEM,
        format=PrivateFormat.PKCS8,
        encryption_algorithm=NoEncryption(),
    )
    public_key_bytes = private_key.public_key().public_bytes_raw()
    fingerprint = agent_hotkey_fingerprint(public_key_bytes)

    final_path = Path(output).expanduser() if output else Path.home() / ".ilc" / "keys" / f"{fingerprint}.pem"
    _write_private_key_pem_atomic(final_path, private_key_pem)
    resolved_path = final_path.resolve()

    return {
        "subcommand": "keygen",
        "key_uri": resolved_path.as_uri(),
        "key_path": str(resolved_path),
        "public_key_fingerprint": fingerprint,
        "public_key_hex": public_key_bytes.hex(),
        "version": AGENT_KEYGEN_CLI_VERSION,
    }


def run_agent_command(args: argparse.Namespace) -> dict[str, Any]:
    """Dispatch agent subcommand from argparse Namespace. Called by main.py."""

    subcommand = getattr(args, "agent_subcommand", None)
    if subcommand == "derive":
        return handle_agent_derive(args.root_key_hex)
    if subcommand == "inspect":
        return handle_agent_inspect(args.record_json)
    if subcommand == "keygen":
        return handle_agent_keygen(getattr(args, "output", None))
    raise ValueError("agent_subcommand_missing")
