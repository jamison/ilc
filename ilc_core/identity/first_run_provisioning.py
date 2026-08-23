# SPDX-License-Identifier: AGPL-3.0-only
"""First-run AgentID provisioning for public-RC onboarding.

This module creates the local identity store used by ``ilc install
--from-invite``. It deliberately stops before proof-of-possession and durable
invite-nullifier binding; those sensitive surfaces are owned by
GAP-AGENT-ONBOARDING-00d.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import secrets  # OS CSPRNG; no private graph entropy.
import shlex
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

from ilc_core.validator.validator_key_derivation import (
    build_validator_key_derivation_record,
    derive_validator_key_ikm,
)

FIRST_RUN_PROVISIONING_VERSION = "gap_agent_onboarding_00c.v0.1"
KEY_STORE_PROFILE_FILE_0600 = "file_0600_unencrypted"
ONBOARDING_SOFTWARE_VERSION = "0.4.0"
GENESIS_ROOT_ENVELOPE_HASH = (
    "sha256:ddc686019018e05f3d88be1a879663c7c2756823bf8bc7fbf980743a92fc6c3c"
)
ONBOARDING_BLS_KEYGEN_COMMAND_ENV = "ILC_ONBOARDING_BLS_KEYGEN_COMMAND"

_AGENT_ID_RE = re.compile(r"^[0-9a-f]{96}$")
_PRIVATE_KEY_RE = re.compile(rb"^[0-9a-f]{64}\n?$")


class IdentityAlreadyExistsError(ValueError):
    """Raised when provisioning would overwrite an existing local identity."""


def identity_root(install_dir: Path | str) -> Path:
    """Return the identity directory rooted under ``install_dir/.ilc``."""

    return Path(install_dir).expanduser().resolve() / ".ilc" / "identity"


def provision_new_identity(
    install_dir: Path,
    *,
    invite_id: str | None = None,
    epoch: int = 0,
    force_reprovision: bool = False,
    keygen_command: list[str] | None = None,
    emit_warning: bool = True,
) -> dict[str, str]:
    """Create a new local BLS-backed AgentID identity store.

    Returns only public-safe metadata. The 32-byte identity seed is never
    written to disk or returned. The derived BLS signing key is written to
    the local key file via same-directory temp file and ``os.replace``.
    """

    if isinstance(epoch, bool) or not isinstance(epoch, int) or epoch < 0:
        raise ValueError("onboarding_epoch_invalid")

    root = identity_root(install_dir)
    signing_key_path = root / "signing_key.hex"
    if signing_key_path.exists() and not force_reprovision:
        raise IdentityAlreadyExistsError("identity_signing_key_already_exists")

    root.mkdir(parents=True, exist_ok=True)
    os.chmod(root.parent, 0o700)
    os.chmod(root, 0o700)

    identity_seed_buf = bytearray(secrets.token_bytes(32))  # OS CSPRNG
    validator_ikm_buf: bytearray | None = None
    try:
        identity_seed = bytes(identity_seed_buf)
        derivation_record = build_validator_key_derivation_record(identity_seed)
        validator_ikm = derive_validator_key_ikm(identity_seed)
        validator_ikm_buf = bytearray(validator_ikm)
        agent_id = _write_private_key_from_ikm(
            root,
            validator_ikm.hex(),
            signing_key_path,
            keygen_command=keygen_command,
        )
    finally:
        _zero_bytearray(identity_seed_buf)
        if validator_ikm_buf is not None:
            _zero_bytearray(validator_ikm_buf)

    if force_reprovision:
        _remove_stale_identity_metadata(root)

    _atomic_write_text(root / "agent_id", f"{agent_id}\n", mode=0o644)
    recovery_policy = _build_recovery_policy()
    birth_attestation = _build_birth_attestation(
        agent_id,
        identity_seed_commitment=derivation_record["identity_seed_commitment"],
    )
    _atomic_write_json(root / "recovery_policy.json", recovery_policy, mode=0o644)
    _atomic_write_json(root / "birth_attestation.json", birth_attestation, mode=0o644)

    receipt = _build_onboarding_receipt(
        agent_id,
        invite_id=invite_id,
        epoch=epoch,
        birth_attestation=birth_attestation,
        recovery_policy=recovery_policy,
    )
    _atomic_write_json(root / "onboarding_receipt.json", receipt, mode=0o644)

    if emit_warning:
        print(
            "key_store_profile=file_0600_unencrypted: signing key is in plaintext. "
            "Upgrade key store post-RC for production use.",
            file=sys.stderr,
        )

    return {
        "agent_id": agent_id,
        "identity_dir": str(root),
        "key_store_profile": KEY_STORE_PROFILE_FILE_0600,
        "status": "provisioned",
    }


def existing_identity_summary(install_dir: Path | str) -> dict[str, str]:
    """Return public-safe metadata for an already-provisioned identity."""

    root = identity_root(install_dir)
    agent_id = _read_agent_id(root / "agent_id")
    return {
        "agent_id": agent_id,
        "identity_dir": str(root),
        "key_store_profile": KEY_STORE_PROFILE_FILE_0600,
        "status": "existing_identity_reused",
    }


def migrate_identity_schema_if_needed(install_dir: Path | str) -> dict[str, Any]:
    """Apply the 00b D5 update migration contract to an existing identity dir."""

    root = identity_root(install_dir)
    if not root.exists():
        return {"migration_status": "not_needed_identity_dir_absent"}

    agent_id = _read_agent_id(root / "agent_id")
    recovery_path = root / "recovery_policy.json"
    if not recovery_path.is_file():
        raise ValueError("identity_migration_recovery_policy_missing")

    birth_path = root / "birth_attestation.json"
    if not birth_path.is_file():
        raise ValueError("identity_migration_birth_attestation_missing")

    birth = _read_json_object(birth_path, "identity_migration_birth_attestation_invalid")
    if birth.get("agent_id") != agent_id:
        raise ValueError("identity_migration_agent_id_mismatch")

    changed = False
    if birth.get("key_store_profile") is None:
        birth["key_store_profile"] = KEY_STORE_PROFILE_FILE_0600
        _atomic_write_json(birth_path, birth, mode=0o644)
        changed = True

    receipt = {
        "agent_id": agent_id,
        "migration_changed": changed,
        "migration_status": "updated" if changed else "not_needed",
        "migration_version": "gap_agent_onboarding_00c_update_migration.v0.1",
    }
    _atomic_write_json(root / "migration_receipt.json", receipt, mode=0o644)
    return receipt


def _build_birth_attestation(
    agent_id: str,
    *,
    identity_seed_commitment: str,
) -> dict[str, str]:
    _require_agent_id(agent_id)
    return {
        "agent_id": agent_id,
        "agent_id_derivation_ref": "cdl-017-bls-g1-pubkey",
        "attestation_signature_ref": "not_yet_implemented_cdl_090_pending",
        "attestation_version": "ilc-birth-attestation-v1",
        "ceremony_mode": "agent_mode",
        "custody_statement": "non_custodial_default_adr_0038",
        "entropy_source_statement": "getrandom_os_csprng_no_private_graph_content",
        "genesis_lineage_anchor": GENESIS_ROOT_ENVELOPE_HASH,
        "identity_seed_commitment_ref": identity_seed_commitment,
        "key_store_profile": KEY_STORE_PROFILE_FILE_0600,
        "lineage_proof_ref": "adr-0037",
        "recovery_policy_ref": "~/.ilc/identity/recovery_policy.json",
        "seed_output_target_ref": "~/.ilc/identity/signing_key.hex",
    }


def _build_recovery_policy() -> dict[str, Any]:
    return {
        "cdl_authority": "cdl-002-section-0a",
        "credentials": [],
        "policy_version": "ilc-recovery-policy-v1",
        "precommitted_at_epoch": None,
        "statement": "no_recovery_path_precommitted_lost_key_equals_lost_agent_id",
        "type": "none",
    }


def _build_onboarding_receipt(
    agent_id: str,
    *,
    invite_id: str | None,
    epoch: int,
    birth_attestation: dict[str, Any],
    recovery_policy: dict[str, Any],
) -> dict[str, Any]:
    transcript = {
        "agent_id": agent_id,
        "birth_attestation_sha384": _canonical_sha384(birth_attestation),
        "recovery_policy_sha384": _canonical_sha384(recovery_policy),
        "software_version": ONBOARDING_SOFTWARE_VERSION,
    }
    return {
        "agent_id": agent_id,
        "birth_attestation_path": "~/.ilc/identity/birth_attestation.json",
        "invite_id": invite_id or "not_recorded",
        "invite_nullifier": "not_yet_bound_00d",
        "key_store_profile": KEY_STORE_PROFILE_FILE_0600,
        "key_store_warning": "signing_key_is_in_plaintext_0600_file_upgrade_key_store_post_rc",
        "onboarded_at_epoch": epoch,
        "receipt_version": "ilc-onboarding-receipt-v1",
        "recovery_policy_path": "~/.ilc/identity/recovery_policy.json",
        "restart_verification_token": hashlib.sha384(
            _canonical_json_bytes(transcript)
        ).hexdigest(),
        "software_version": ONBOARDING_SOFTWARE_VERSION,
    }


def _write_private_key_from_ikm(
    identity_dir: Path,
    ikm_hex: str,
    final_path: Path,
    *,
    keygen_command: list[str] | None,
) -> str:
    command = list(keygen_command or _default_keygen_command())
    fd, temp_name = tempfile.mkstemp(
        prefix=f".{final_path.name}.", suffix=".tmp", dir=identity_dir
    )
    os.close(fd)
    temp_path = Path(temp_name)
    temp_path.unlink()
    try:
        result = subprocess.run(
            [
                *command,
                "--keypair-from-ikm-hex-stdin",
                "--out",
                str(temp_path),
            ],
            input=f"{ikm_hex}\n",
            check=False,
            capture_output=True,
            text=True,
            timeout=120,
        )
    except FileNotFoundError as exc:
        raise ValueError("onboarding_bls_keygen_unavailable") from exc
    except subprocess.TimeoutExpired as exc:
        raise ValueError("onboarding_bls_keygen_timed_out") from exc

    try:
        if result.returncode != 0:
            raise ValueError("onboarding_bls_keygen_failed")

        agent_id = result.stdout.strip()
        _require_agent_id(agent_id)
        try:
            private_payload = temp_path.read_bytes()
        except OSError as exc:
            raise ValueError("onboarding_bls_private_key_unreadable") from exc
        if _PRIVATE_KEY_RE.fullmatch(private_payload) is None:
            raise ValueError("onboarding_bls_private_key_invalid")
        os.chmod(temp_path, 0o600)
        os.replace(temp_path, final_path)
        os.chmod(final_path, 0o600)
        return agent_id
    except BaseException:
        try:
            temp_path.unlink()
        except FileNotFoundError:
            pass
        raise


def _default_keygen_command() -> list[str]:
    env_command = os.environ.get(ONBOARDING_BLS_KEYGEN_COMMAND_ENV)
    if env_command:
        return shlex.split(env_command)

    repo_root = Path(__file__).resolve().parents[2]
    for candidate in (
        repo_root / "ilc_consensus" / "target" / "release" / "keygen",
        repo_root / "ilc_consensus" / "target" / "debug" / "keygen",
    ):
        if candidate.exists():
            return [str(candidate)]

    cargo = shutil.which("cargo")
    if cargo is None:
        user_cargo = Path.home() / ".cargo" / "bin" / "cargo"
        cargo = str(user_cargo) if user_cargo.exists() else None
    if cargo is None:
        raise ValueError("onboarding_bls_keygen_unavailable")
    return [
        cargo,
        "run",
        "--quiet",
        "--manifest-path",
        str(repo_root / "ilc_consensus" / "Cargo.toml"),
        "--bin",
        "keygen",
        "--",
    ]


def _remove_stale_identity_metadata(root: Path) -> None:
    for name in (
        "migration_receipt.json",
    ):
        try:
            (root / name).unlink()
        except FileNotFoundError:
            pass


def _read_agent_id(path: Path) -> str:
    try:
        value = path.read_text(encoding="utf-8").strip()
    except OSError as exc:
        raise ValueError("identity_agent_id_unreadable") from exc
    return _require_agent_id(value)


def _require_agent_id(value: str) -> str:
    if not isinstance(value, str) or _AGENT_ID_RE.fullmatch(value) is None:
        raise ValueError("identity_agent_id_invalid")
    return value


def _read_json_object(path: Path, token: str) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(token) from exc
    if not isinstance(payload, dict):
        raise ValueError(token)
    return payload


def _atomic_write_json(path: Path, payload: dict[str, Any], *, mode: int) -> None:
    _atomic_write_text(
        path,
        json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False)
        + "\n",
        mode=mode,
    )


def _atomic_write_text(path: Path, payload: str, *, mode: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    try:
        os.chmod(temp_name, mode)
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            fd = -1
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_name, path)
        os.chmod(path, mode)
    except BaseException:
        if fd != -1:
            os.close(fd)
        try:
            os.unlink(temp_name)
        except FileNotFoundError:
            pass
        raise


def _canonical_json_bytes(payload: dict[str, Any]) -> bytes:
    return json.dumps(
        payload, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")


def _canonical_sha384(payload: dict[str, Any]) -> str:
    return hashlib.sha384(_canonical_json_bytes(payload)).hexdigest()


def _zero_bytearray(value: bytearray) -> None:
    for index in range(len(value)):
        value[index] = 0


__all__ = [
    "FIRST_RUN_PROVISIONING_VERSION",
    "IdentityAlreadyExistsError",
    "existing_identity_summary",
    "identity_root",
    "migrate_identity_schema_if_needed",
    "provision_new_identity",
]
