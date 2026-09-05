# SPDX-License-Identifier: AGPL-3.0-only
"""Validator endpoint assertion rotation helpers."""

from __future__ import annotations

import hashlib
import json
import os
import shlex
import shutil
import stat
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from cryptography import x509
from cryptography.hazmat.primitives import serialization

from ilc_core.consensus.binary_paths import installed_consensus_binary_command
from ilc_core.consensus.validator_endpoint_assertion import (
    VALIDATOR_ENDPOINT_ASSERTION_NODE_KIND,
    VALIDATOR_ENDPOINT_ASSERTION_SCHEMA_VERSION,
    ValidatorEndpointAssertion,
    assertion_valid_at,
    assertion_content_sha256,
    canonical_assertion_payload,
    validator_assertion_candidate_id,
)
from ilc_core.validator.network_id_validation import require_validator_network_id


ENDPOINT_ROTATION_RUNTIME_VERSION = "validator_endpoint_rotation_gap_validator_ident_03.v0.1"
ENDPOINT_ROTATION_BLS_SIGN_COMMAND_ENV = "ILC_VALIDATOR_ENDPOINT_ROTATION_BLS_SIGN_COMMAND"
ENDPOINT_ROTATION_ALLOW_TEST_STUB_SIGNATURE_ENV = (
    "ILC_VALIDATOR_ENDPOINT_ROTATION_ALLOW_TEST_STUB_SIGNATURE"
)
BLS_SIGNATURE_HEX_LENGTH = 192
MAX_ASSERTION_JSON_BYTES = 1_048_576
MAX_BLS_SECRET_BYTES = 4096

_REPO_ROOT = Path(__file__).resolve().parents[2]
_LOWER_HEX = frozenset("0123456789abcdef")


def rotate_validator_endpoint_assertion(
    *,
    old_assertion_path: Path,
    new_endpoint: str,
    network_id: str,
    key_path: Path,
    output_path: Path,
    tls_cert_path: Path | None = None,
    asserted_at_epoch: int | None = None,
    now_utc: datetime | None = None,
    allow_test_stub_signature: bool = False,
) -> dict[str, Any]:
    """Create a new endpoint assertion and separate content-hash revision edge."""

    old_assertion_path = Path(old_assertion_path)
    output_path = Path(output_path)
    key_path = Path(key_path)
    checked_now_utc = _require_now_utc(now_utc)
    if old_assertion_path.resolve() == output_path.resolve():
        raise ValueError("validator_endpoint_rotation_output_must_not_equal_old_assertion")
    old_raw = _read_bounded_text(old_assertion_path, MAX_ASSERTION_JSON_BYTES)
    old_file_sha256_before_rotation = hashlib.sha256(old_assertion_path.read_bytes()).hexdigest()
    try:
        old_payload = _loads_json_no_constants(old_raw)
    except (json.JSONDecodeError, ValueError) as exc:
        raise ValueError("validator_endpoint_rotation_old_assertion_invalid_json") from exc
    old_assertion = ValidatorEndpointAssertion.from_dict(_require_mapping(old_payload))
    if old_assertion.revised_by is not None:
        raise ValueError("validator_endpoint_rotation_old_assertion_already_inline_superseded")

    network_id = _require_network_id(network_id)
    new_endpoint = _require_endpoint(new_endpoint)
    _require_private_key_file(key_path)
    asserted_epoch = (
        old_assertion.asserted_at_epoch
        if asserted_at_epoch is None
        else _require_uint64(asserted_at_epoch, "validator_endpoint_rotation_epoch_invalid")
    )
    cert_fields = (
        _cert_fields_from_path(tls_cert_path, now_utc=checked_now_utc)
        if tls_cert_path is not None
        else {
            "tls_cert_not_after_utc": old_assertion.tls_cert_not_after_utc,
            "tls_cert_not_before_utc": old_assertion.tls_cert_not_before_utc,
            "tls_cert_sha256_fingerprint": old_assertion.tls_cert_sha256_fingerprint,
        }
    )
    unsigned = ValidatorEndpointAssertion(
        asserted_at_epoch=asserted_epoch,
        bls_public_key_hex=old_assertion.bls_public_key_hex,
        bls_signature_hex="0" * BLS_SIGNATURE_HEX_LENGTH,
        genesis_witness=old_assertion.genesis_witness,
        grpc_endpoint=new_endpoint,
        node_kind=VALIDATOR_ENDPOINT_ASSERTION_NODE_KIND,
        schema_version=VALIDATOR_ENDPOINT_ASSERTION_SCHEMA_VERSION,
        tls_cert_not_after_utc=cert_fields["tls_cert_not_after_utc"],
        tls_cert_not_before_utc=cert_fields["tls_cert_not_before_utc"],
        tls_cert_sha256_fingerprint=cert_fields["tls_cert_sha256_fingerprint"],
        validator_agent_id=old_assertion.validator_agent_id,
        revised_by=None,
    )
    assertion_valid_at(unsigned, now_utc=checked_now_utc)
    signature, signature_mode = _sign_assertion_payload(
        payload=canonical_assertion_payload(unsigned),
        key_path=key_path,
        network_id=network_id,
        allow_test_stub_signature=allow_test_stub_signature,
    )
    new_assertion = ValidatorEndpointAssertion(
        **{
            **unsigned.to_dict(include_graph_metadata=False),
            "bls_signature_hex": signature,
        }
    )
    old_assertion_sha256 = assertion_content_sha256(old_assertion)
    new_assertion_sha256 = assertion_content_sha256(new_assertion)
    if old_assertion_sha256 == new_assertion_sha256:
        raise ValueError("validator_endpoint_rotation_no_content_change")
    old_candidate_id = validator_assertion_candidate_id(old_assertion.validator_agent_id)
    new_candidate_id = validator_assertion_candidate_id(new_assertion.validator_agent_id)
    revision_edge = {
        "edge_id": f"validator_endpoint_assertion_revision:{old_assertion_sha256}:{new_assertion_sha256}",
        "edge_type": "revised_by",
        "source_assertion_sha256": old_assertion_sha256,
        "source_candidate_id": old_candidate_id,
        "target_assertion_sha256": new_assertion_sha256,
        "target_candidate_id": new_candidate_id,
        "validator_agent_id": new_assertion.validator_agent_id,
    }
    atomic_write_json(output_path, new_assertion.to_dict(include_graph_metadata=False), mode=0o644)
    return {
        "cert_material_source": "tls_cert_path" if tls_cert_path is not None else "old_assertion_preserved",
        "new_assertion": new_assertion.to_dict(include_graph_metadata=False),
        "new_assertion_id": new_assertion_sha256,
        "new_candidate_id": new_candidate_id,
        "new_endpoint": new_endpoint,
        "network_id": network_id,
        "old_assertion_id": old_assertion_sha256,
        "old_candidate_id": old_candidate_id,
        "old_endpoint": old_assertion.grpc_endpoint,
        "old_file_sha256_before_rotation": old_file_sha256_before_rotation,
        "output_path": str(output_path),
        "revised_by_edge": revision_edge,
        "runtime_version": ENDPOINT_ROTATION_RUNTIME_VERSION,
        "signature_mode": signature_mode,
    }


def atomic_write_json(path: Path, payload: dict[str, Any], *, mode: int = 0o600) -> None:
    data = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        os.chmod(tmp_name, mode)
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            fd = -1
            handle.write(data)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp_name, path)
    except BaseException:
        if fd != -1:
            os.close(fd)
        try:
            os.unlink(tmp_name)
        except FileNotFoundError:
            pass
        raise


def _read_bounded_text(path: Path, max_bytes: int) -> str:
    if not path.is_file():
        raise ValueError("validator_endpoint_rotation_old_assertion_missing")
    size = path.stat().st_size
    if size > max_bytes:
        raise ValueError("validator_endpoint_rotation_old_assertion_too_large")
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError("validator_endpoint_rotation_old_assertion_invalid_json") from exc


def _cert_fields_from_path(path: Path, *, now_utc: datetime) -> dict[str, str | None]:
    if not path.is_file():
        raise ValueError("validator_endpoint_rotation_tls_cert_missing")
    data = path.read_bytes()
    try:
        certificate = x509.load_pem_x509_certificate(data)
        der = certificate.public_bytes(serialization.Encoding.DER)
    except ValueError:
        try:
            certificate = x509.load_der_x509_certificate(data)
            der = data
        except ValueError as exc:
            raise ValueError("validator_endpoint_rotation_tls_cert_invalid") from exc
    if certificate.not_valid_before_utc > now_utc:
        raise ValueError("validator_endpoint_rotation_tls_cert_not_yet_valid")
    if certificate.not_valid_after_utc <= now_utc:
        raise ValueError("validator_endpoint_rotation_tls_cert_expired")
    return {
        "tls_cert_not_after_utc": _to_iso_utc(certificate.not_valid_after_utc),
        "tls_cert_not_before_utc": _to_iso_utc(certificate.not_valid_before_utc),
        "tls_cert_sha256_fingerprint": hashlib.sha256(der).hexdigest(),
    }


def _sign_assertion_payload(
    *,
    payload: bytes,
    key_path: Path,
    network_id: str,
    allow_test_stub_signature: bool,
) -> tuple[str, str]:
    if allow_test_stub_signature:
        if os.environ.get(ENDPOINT_ROTATION_ALLOW_TEST_STUB_SIGNATURE_ENV) != "1":
            raise ValueError("validator_endpoint_rotation_test_stub_signature_not_authorized")
        key_bytes = _read_bounded_key_bytes(key_path)
        digest = hashlib.sha384(payload + network_id.encode("utf-8") + key_bytes).hexdigest()
        signature = (digest + hashlib.sha384(digest.encode("ascii")).hexdigest())[:BLS_SIGNATURE_HEX_LENGTH]
        _require_lower_hex_exact(signature, BLS_SIGNATURE_HEX_LENGTH, "validator_endpoint_rotation_signature_invalid")
        return signature, "test_stub_not_production_valid"
    key_bytes = _read_bounded_key_bytes(key_path)
    command = os.environ.get(ENDPOINT_ROTATION_BLS_SIGN_COMMAND_ENV)
    command_tuple = tuple(shlex.split(command)) if command is not None and command.strip() else _default_bls_sign_command()
    if command_tuple is None:
        raise ValueError("validator_endpoint_rotation_bls_sign_command_missing")
    try:
        result = subprocess.run(
            command_tuple
            + (
                "sign",
                "--secret-key",
                str(key_path),
                "--network-id",
                network_id,
            ),
            input=payload,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            timeout=120,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise ValueError("validator_endpoint_rotation_bls_sign_failed") from exc
    if result.returncode != 0:
        raise ValueError("validator_endpoint_rotation_bls_sign_failed")
    signature = result.stdout.decode("ascii").strip().lower()
    _require_lower_hex_exact(signature, BLS_SIGNATURE_HEX_LENGTH, "validator_endpoint_rotation_signature_invalid")
    return signature, "external_command"


def _read_bounded_key_bytes(path: Path) -> bytes:
    if not path.is_file():
        raise ValueError("validator_endpoint_rotation_key_missing")
    if stat.S_IMODE(path.stat().st_mode) & 0o077:
        raise ValueError("validator_endpoint_rotation_key_permissions_too_open")
    size = path.stat().st_size
    if size <= 0 or size > MAX_BLS_SECRET_BYTES:
        raise ValueError("validator_endpoint_rotation_key_size_invalid")
    try:
        key_text = path.read_text(encoding="ascii").strip()
    except UnicodeDecodeError as exc:
        raise ValueError("validator_endpoint_rotation_key_invalid") from exc
    _require_lower_hex_exact(key_text, 64, "validator_endpoint_rotation_key_invalid")
    return key_text.encode("ascii")


def _default_bls_sign_command() -> tuple[str, ...] | None:
    installed = installed_consensus_binary_command("validator_endpoint_assertion_bls")
    if installed is not None:
        return installed
    cargo = shutil.which("cargo")
    if cargo is None:
        home_cargo = Path.home() / ".cargo" / "bin" / "cargo"
        cargo = str(home_cargo) if home_cargo.exists() else None
    if cargo is None:
        return None
    return (
        cargo,
        "run",
        "--quiet",
        "--manifest-path",
        str(_REPO_ROOT / "ilc_consensus" / "Cargo.toml"),
        "--bin",
        "validator_endpoint_assertion_bls",
        "--",
    )


def _require_mapping(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError("validator_endpoint_rotation_old_assertion_not_object")
    return value


def _loads_json_no_constants(raw: str) -> Any:
    def _reject_constant(value: str) -> None:
        raise ValueError(f"json_non_finite_constant_not_allowed:{value}")

    return json.loads(raw, parse_constant=_reject_constant)


def _require_network_id(value: Any) -> str:
    return require_validator_network_id(
        value,
        token="validator_endpoint_rotation_network_id_invalid",
    )


def _require_now_utc(value: datetime | None) -> datetime:
    if value is None:
        raise ValueError("validator_endpoint_rotation_now_utc_required")
    if not isinstance(value, datetime) or value.tzinfo is None:
        raise ValueError("validator_endpoint_rotation_now_utc_invalid")
    return value.astimezone(timezone.utc)


def _require_endpoint(value: Any) -> str:
    if not isinstance(value, str) or not value or any(char.isspace() for char in value):
        raise ValueError("validator_endpoint_rotation_new_endpoint_invalid")
    host, sep, port_text = value.rpartition(":")
    if not sep or not host or not port_text or "://" in value or "/" in host:
        raise ValueError("validator_endpoint_rotation_new_endpoint_invalid")
    try:
        port = int(port_text, 10)
    except ValueError as exc:
        raise ValueError("validator_endpoint_rotation_new_endpoint_invalid") from exc
    if port < 1 or port > 65535:
        raise ValueError("validator_endpoint_rotation_new_endpoint_invalid")
    return value


def _require_uint64(value: Any, token: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0 or value > 2**64 - 1:
        raise ValueError(token)
    return value


def _require_private_key_file(path: Path) -> None:
    _read_bounded_key_bytes(path)


def _require_lower_hex_exact(value: Any, length: int, token: str) -> str:
    if not isinstance(value, str) or len(value) != length or any(char not in _LOWER_HEX for char in value):
        raise ValueError(token)
    return value


def _to_iso_utc(value: datetime) -> str:
    return value.astimezone(timezone.utc).replace(microsecond=0).strftime("%Y-%m-%dT%H:%M:%SZ")


__all__ = [
    "ENDPOINT_ROTATION_BLS_SIGN_COMMAND_ENV",
    "ENDPOINT_ROTATION_ALLOW_TEST_STUB_SIGNATURE_ENV",
    "ENDPOINT_ROTATION_RUNTIME_VERSION",
    "atomic_write_json",
    "rotate_validator_endpoint_assertion",
]
