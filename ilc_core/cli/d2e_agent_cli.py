# SPDX-License-Identifier: AGPL-3.0-only
"""Phase 420 D2e agent identity CLI helpers."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import secrets
import shutil
import stat
import subprocess
import tempfile
from pathlib import Path
from typing import Any

from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives.serialization import Encoding, NoEncryption, PrivateFormat

from ilc_core.identity.agent_id_runtime import (
    CDL_042_DEPENDENCY as RUNTIME_CDL_042_DEPENDENCY,
    derive_agent_id,
)
from ilc_core.identity.bls_backend import (
    keypair_from_ikm_hex,
    public_key_from_secret_key_hex,
)

D2E_AGENT_CLI_VERSION = "d2e_agent_cli_420.v0.1"
AGENT_KEYGEN_CLI_VERSION = "agent_keygen_cli_GAP_AGENT_KEYGEN_00.v0.1"
AGENT_GENERATE_CLI_VERSION = "agent_generate_cli_GAP_ECU_CLI_SURFACE_00.v0.1"
CDL_042_DEPENDENCY = RUNTIME_CDL_042_DEPENDENCY
_PUBLIC_RC_AGENT_ID_RE = re.compile(r"^[0-9a-f]{96}$")
_MAX_AGENT_RECORD_JSON_BYTES = 256 * 1024

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
        flags = os.O_RDONLY
        if hasattr(os, "O_NOFOLLOW"):
            flags |= os.O_NOFOLLOW
        fd = -1
        fd = os.open(path, flags)
        try:
            file_stat = os.fstat(fd)
            if not stat.S_ISREG(file_stat.st_mode):
                raise ValueError("agent_inspect_record_not_file")
            if file_stat.st_size > _MAX_AGENT_RECORD_JSON_BYTES:
                raise ValueError("agent_inspect_record_too_large")
            with os.fdopen(fd, "rb") as handle:
                fd = -1
                raw = handle.read(_MAX_AGENT_RECORD_JSON_BYTES + 1)
        finally:
            if fd >= 0:
                os.close(fd)
        if len(raw) > _MAX_AGENT_RECORD_JSON_BYTES:
            raise ValueError("agent_inspect_record_too_large")
        record = json.loads(raw.decode("utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
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


def _default_bls_signing_key_path() -> Path:
    return Path.home() / ".ilc" / "identity" / "signing_key.hex"


def _default_keygen_binary() -> Path:
    env_path = os.environ.get("ILC_AGENT_BLS_KEYGEN_BINARY", "").strip()
    if env_path:
        return Path(env_path).expanduser()
    helper_path = Path.home() / ".ilc" / "bin" / "keygen"
    if helper_path.exists():
        return helper_path
    return Path(__file__).resolve().parents[2] / "ilc_consensus" / "target" / "release" / "keygen"


def _cleanup_partial_agent_generate_key(path: Path, token: str) -> None:
    try:
        if path.exists():
            path.unlink()
    except OSError as exc:
        raise ValueError("agent_generate_cleanup_failed") from exc
    raise ValueError(token)


def _write_bls_secret_key_hex_atomic(final_path: Path, secret_key_hex: str) -> None:
    if not isinstance(secret_key_hex, str) or re.fullmatch(r"[0-9a-f]{64}", secret_key_hex) is None:
        raise ValueError("agent_generate_invalid_secret_key")
    try:
        _write_private_key_pem_atomic(final_path, f"{secret_key_hex}\n".encode("ascii"))
    except ValueError as exc:
        message = str(exc)
        if message == "agent_keygen_output_exists":
            raise ValueError("agent_generate_output_exists") from exc
        if message == "agent_keygen_output_directory_unavailable":
            raise ValueError("agent_generate_output_directory_unavailable") from exc
        raise ValueError("agent_generate_output_write_failed") from exc


def _generate_agent_id_with_python_backend(final_path: Path) -> str:
    for _ in range(8):
        ikm_hex = secrets.token_bytes(32).hex()
        try:
            secret_key_hex, public_key_hex = keypair_from_ikm_hex(ikm_hex)
        except ValueError:
            continue
        if _PUBLIC_RC_AGENT_ID_RE.fullmatch(public_key_hex) is None:
            continue
        _write_bls_secret_key_hex_atomic(final_path, secret_key_hex)
        return public_key_hex
    raise ValueError("agent_generate_python_bls_keygen_failed")


def handle_agent_generate(
    output: str | None = None,
    keygen_binary: str | None = None,
) -> dict[str, Any]:
    """Generate a public-RC CDL-017 BLS AgentID and persist its secret key.

    This deliberately does not reuse the Ed25519 action hotkey path.  Public-RC
    AgentIDs are 96-char lowercase hex BLS G1 public keys under CDL-017.
    """

    final_path = Path(output).expanduser() if output else _default_bls_signing_key_path()
    if final_path.exists():
        raise ValueError("agent_generate_output_exists")
    try:
        final_path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    except OSError as exc:
        raise ValueError("agent_generate_output_directory_unavailable") from exc

    if keygen_binary is None and not _default_keygen_binary().exists():
        agent_id = _generate_agent_id_with_python_backend(final_path)
        resolved_path = final_path.resolve()
        return {
            "_raw": agent_id,
            "subcommand": "generate",
            "agent_id": agent_id,
            "agent_id_format": "cdl-017-bls-g1-pubkey",
            "agent_id_namespace": "cdl-017",
            "agent_id_generation_backend": "python_py_ecc_bls_backend",
            "public_rc_submit_compatible": True,
            "signing_key_path": str(resolved_path),
            "version": AGENT_GENERATE_CLI_VERSION,
        }

    binary = Path(keygen_binary).expanduser() if keygen_binary else _default_keygen_binary()
    if not binary.exists() or not binary.is_file():
        raise ValueError("agent_generate_keygen_binary_missing")
    if not os.access(binary, os.X_OK):
        raise ValueError("agent_generate_keygen_binary_not_executable")

    try:
        proc = subprocess.run(
            [str(binary), "--out", str(final_path)],
            check=False,
            capture_output=True,
            text=True,
            timeout=30,
        )
    except subprocess.TimeoutExpired as exc:
        _cleanup_partial_agent_generate_key(final_path, "agent_generate_keygen_timeout")
        raise AssertionError("unreachable") from exc
    if proc.returncode != 0:
        _cleanup_partial_agent_generate_key(final_path, "agent_generate_keygen_failed")

    agent_id = proc.stdout.strip()
    if _PUBLIC_RC_AGENT_ID_RE.fullmatch(agent_id) is None:
        _cleanup_partial_agent_generate_key(final_path, "agent_generate_invalid_public_agent_id")
    try:
        secret_key_hex = final_path.read_text(encoding="utf-8").strip()
        derived_agent_id = public_key_from_secret_key_hex(secret_key_hex)
    except (OSError, ValueError) as exc:
        _cleanup_partial_agent_generate_key(final_path, "agent_generate_invalid_secret_key")
        raise AssertionError("unreachable") from exc
    if derived_agent_id != agent_id:
        _cleanup_partial_agent_generate_key(final_path, "agent_generate_secret_public_mismatch")

    resolved_path = final_path.resolve()
    return {
        "_raw": agent_id,
        "subcommand": "generate",
        "agent_id": agent_id,
        "agent_id_format": "cdl-017-bls-g1-pubkey",
        "agent_id_namespace": "cdl-017",
        "agent_id_generation_backend": "external_ilc_keygen",
        "public_rc_submit_compatible": True,
        "signing_key_path": str(resolved_path),
        "version": AGENT_GENERATE_CLI_VERSION,
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
    if subcommand == "generate":
        return handle_agent_generate(
            getattr(args, "output", None),
            getattr(args, "keygen_binary", None),
        )
    raise ValueError("agent_subcommand_missing")
