# SPDX-License-Identifier: AGPL-3.0-only
"""Operator node initialization tooling for fresh validator installs."""

from __future__ import annotations

import hashlib
import ipaddress
import json
import os
import re
import secrets
import shlex
import shutil
import stat
import subprocess
import tempfile
import tomllib
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID

from ilc_core.consensus.validator_endpoint_assertion import (
    VALIDATOR_ENDPOINT_ASSERTION_NODE_KIND,
    VALIDATOR_ENDPOINT_ASSERTION_SCHEMA_VERSION,
    ValidatorEndpointAssertion,
    canonical_assertion_payload,
)
from ilc_core.node.readiness_runtime import extended_local_check_fields


OPERATOR_INIT_RUNTIME_VERSION = "operator_init_runtime_gap_operator_init_00.v0.1"
OPERATOR_INIT_BLS_KEYGEN_COMMAND_ENV = "ILC_OPERATOR_INIT_BLS_KEYGEN_COMMAND"
OPERATOR_INIT_BLS_SIGN_COMMAND_ENV = "ILC_OPERATOR_INIT_BLS_SIGN_COMMAND"
MLDSA65_PUBLIC_KEY_HEX_LENGTH = 3904
MLDSA65_TEST_SECRET_KEY_HEX_LENGTH = 8064
BLS_PUBLIC_KEY_HEX_LENGTH = 96
BLS_SECRET_KEY_HEX_LENGTH = 64
BLS_SIGNATURE_HEX_LENGTH = 192
DEFAULT_TLS_VALID_DAYS = 365
MAX_NETWORK_ID_CHARS = 64
MAX_HOST_CHARS = 253
MAX_PEER_SEEDS = 128

_REPO_ROOT = Path(__file__).resolve().parents[2]
_LOWER_HEX = frozenset("0123456789abcdef")
_NETWORK_ID_RE = re.compile(r"^[A-Za-z0-9_.-]+$")
_DNS_HOST_RE = re.compile(r"^[A-Za-z0-9.-]+$")


@dataclass(frozen=True)
class NodeInitResult:
    """Paths and metadata produced by `ilc node init`."""

    root: Path
    config_path: Path
    receipt_path: Path
    endpoint_assertion_path: Path
    validator_agent_id: str
    network_id: str
    grpc_endpoint: str
    tls_cert_sha256_fingerprint: str
    mldsa_keygen_mode: str
    bls_keygen_mode: str
    bls_signature_mode: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "bls_keygen_mode": self.bls_keygen_mode,
            "bls_signature_mode": self.bls_signature_mode,
            "config_path": str(self.config_path),
            "endpoint_assertion_path": str(self.endpoint_assertion_path),
            "grpc_endpoint": self.grpc_endpoint,
            "mldsa_keygen_mode": self.mldsa_keygen_mode,
            "network_id": self.network_id,
            "receipt_path": str(self.receipt_path),
            "root": str(self.root),
            "runtime_version": OPERATOR_INIT_RUNTIME_VERSION,
            "tls_cert_sha256_fingerprint": self.tls_cert_sha256_fingerprint,
            "validator_agent_id": self.validator_agent_id,
        }


def generate_node_init_material(
    *,
    root: Path,
    network_id: str,
    host: str,
    grpc_port: int,
    quic_port: int,
    peer_seeds: list[str] | None = None,
    valid_days: int = DEFAULT_TLS_VALID_DAYS,
    allow_test_stub_crypto: bool = False,
    genesis_witness: bool = False,
    asserted_at_epoch: int = 0,
) -> NodeInitResult:
    """Generate local validator operator material without starting services."""

    root = Path(root)
    _require_safe_root(root)
    network_id = _require_network_id(network_id)
    host = _require_host(host)
    grpc_port = _require_port(grpc_port, "operator_init_grpc_port_invalid")
    quic_port = _require_port(quic_port, "operator_init_quic_port_invalid")
    valid_days = _require_positive_int(valid_days, "operator_init_valid_days_invalid")
    asserted_at_epoch = _require_uint64(asserted_at_epoch, "operator_init_asserted_epoch_invalid")
    peer_seeds = _require_peer_seeds(peer_seeds or [])

    certs_dir = root / "certs"
    keys_dir = root / "keys"
    config_dir = root / "config"
    out_dir = root / "out" / "node_init"
    for directory in (certs_dir, keys_dir, config_dir, out_dir):
        directory.mkdir(parents=True, exist_ok=True)

    tls_key_path = certs_dir / "validator_tls_key.pem"
    tls_cert_path = certs_dir / "validator_tls_cert.pem"
    tls_cert_der_path = certs_dir / "validator_tls_cert.der"
    _require_paths_absent(
        [
            tls_key_path,
            tls_cert_path,
            tls_cert_der_path,
            keys_dir / "validator_mldsa65_public.hex",
            keys_dir / "validator_mldsa65_secret.hex",
            keys_dir / "validator_bls_secret.hex",
            config_dir / "node_config.toml",
            out_dir / "validator_endpoint_assertion.json",
            out_dir / "init_receipt.json",
        ]
    )
    cert_info = _generate_tls_certificate(
        host=host,
        key_path=tls_key_path,
        cert_path=tls_cert_path,
        der_path=tls_cert_der_path,
        valid_days=valid_days,
    )

    mldsa_public_path = keys_dir / "validator_mldsa65_public.hex"
    mldsa_secret_path = keys_dir / "validator_mldsa65_secret.hex"
    mldsa_public_key_hex, mldsa_keygen_mode = _generate_mldsa65_keypair(
        public_path=mldsa_public_path,
        secret_path=mldsa_secret_path,
        allow_test_stub_crypto=allow_test_stub_crypto,
    )

    bls_secret_path = keys_dir / "validator_bls_secret.hex"
    bls_public_key_hex, bls_keygen_mode = _generate_bls_keypair(
        secret_path=bls_secret_path,
        allow_test_stub_crypto=allow_test_stub_crypto,
    )
    validator_agent_id = bls_public_key_hex
    grpc_endpoint = f"{host}:{grpc_port}"
    unsigned = ValidatorEndpointAssertion(
        asserted_at_epoch=asserted_at_epoch,
        bls_public_key_hex=bls_public_key_hex,
        bls_signature_hex="0" * BLS_SIGNATURE_HEX_LENGTH,
        genesis_witness=bool(genesis_witness),
        grpc_endpoint=grpc_endpoint,
        node_kind=VALIDATOR_ENDPOINT_ASSERTION_NODE_KIND,
        schema_version=VALIDATOR_ENDPOINT_ASSERTION_SCHEMA_VERSION,
        tls_cert_not_after_utc=cert_info["not_after_utc"],
        tls_cert_not_before_utc=cert_info["not_before_utc"],
        tls_cert_sha256_fingerprint=cert_info["fingerprint"],
        validator_agent_id=validator_agent_id,
    )
    bls_signature_hex, bls_signature_mode = _sign_endpoint_assertion(
        payload=canonical_assertion_payload(unsigned),
        secret_key_path=bls_secret_path,
        network_id=network_id,
        allow_test_stub_crypto=allow_test_stub_crypto,
    )
    assertion = ValidatorEndpointAssertion(
        **{
            **unsigned.to_dict(include_graph_metadata=False),
            "bls_signature_hex": bls_signature_hex,
        }
    )
    endpoint_assertion_path = out_dir / "validator_endpoint_assertion.json"
    atomic_write_json(
        endpoint_assertion_path,
        assertion.to_dict(include_graph_metadata=False),
        mode=0o644,
    )

    config_path = config_dir / "node_config.toml"
    atomic_write_text(
        config_path,
        _render_node_config(
            network_id=network_id,
            grpc_endpoint=grpc_endpoint,
            host=host,
            grpc_port=grpc_port,
            quic_port=quic_port,
            peer_seeds=peer_seeds,
            tls_cert_path=tls_cert_path,
            tls_key_path=tls_key_path,
            endpoint_assertion_path=endpoint_assertion_path,
            bls_public_key_hex=bls_public_key_hex,
            bls_secret_key_path=bls_secret_path,
            mldsa_public_key_hex=mldsa_public_key_hex,
            mldsa_public_key_path=mldsa_public_path,
            mldsa_secret_key_path=mldsa_secret_path,
        ),
        mode=0o644,
    )

    receipt_path = out_dir / "init_receipt.json"
    result = NodeInitResult(
        root=root,
        config_path=config_path,
        receipt_path=receipt_path,
        endpoint_assertion_path=endpoint_assertion_path,
        validator_agent_id=validator_agent_id,
        network_id=network_id,
        grpc_endpoint=grpc_endpoint,
        tls_cert_sha256_fingerprint=cert_info["fingerprint"],
        mldsa_keygen_mode=mldsa_keygen_mode,
        bls_keygen_mode=bls_keygen_mode,
        bls_signature_mode=bls_signature_mode,
    )
    receipt = {
        **result.to_dict(),
        "created_at_utc": _now_utc(),
        "generated_paths": {
            "bls_secret_key_path": str(bls_secret_path),
            "mldsa_public_key_path": str(mldsa_public_path),
            "mldsa_secret_key_path": str(mldsa_secret_path),
            "tls_cert_der_path": str(tls_cert_der_path),
            "tls_cert_path": str(tls_cert_path),
            "tls_key_path": str(tls_key_path),
        },
        "next_actions": [
            "publish validator_endpoint_assertion.json to the graph",
            "configure peer seeds",
            "start the Rust validator binary outside this command",
        ],
        "non_claims": [
            "no_rust_validator_started",
            "no_peer_connection_attempted",
            "no_graph_write",
            "no_guard_mutation",
            "no_cdl_mutation",
        ],
        "peer_seed_count": len(peer_seeds),
    }
    atomic_write_json(receipt_path, receipt, mode=0o644)
    return result


def check_node_config(config_path: Path, *, now: datetime | None = None) -> dict[str, Any]:
    """Validate local node config completeness and certificate freshness."""

    config_path = Path(config_path)
    if not config_path.is_file():
        raise ValueError("node_check_config_missing")
    try:
        config = tomllib.loads(config_path.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError) as exc:
        raise ValueError("node_check_config_invalid_toml") from exc
    if not isinstance(config, dict):
        raise ValueError("node_check_config_invalid")

    network = _require_section(config, "network")
    grpc = _require_section(config, "grpc")
    tls = _require_section(config, "tls")
    validator = _require_section(config, "validator")

    network_id = _require_network_id(network.get("network_id"))
    grpc_listen_addr = _require_string(grpc.get("grpc_listen_addr"), "node_check_grpc_listen_addr_missing")
    _parse_endpoint(grpc_listen_addr, "node_check_grpc_listen_addr_invalid")
    cert_path = _resolve_config_path(config_path, _require_string(tls.get("tls_cert_path"), "node_check_tls_cert_path_missing"))
    key_path = _resolve_config_path(config_path, _require_string(tls.get("tls_key_path"), "node_check_tls_key_path_missing"))
    assertion_path = _resolve_config_path(
        config_path,
        _require_string(
            validator.get("endpoint_assertion_path"),
            "node_check_endpoint_assertion_path_missing",
        ),
    )
    bls_secret_key_path = _resolve_config_path(
        config_path,
        _require_string(
            validator.get("bls_secret_key_path"),
            "node_check_bls_secret_key_path_missing",
        ),
    )
    mldsa_public_key_path = _resolve_config_path(
        config_path,
        _require_string(
            validator.get("mldsa65_public_key_path"),
            "node_check_mldsa65_public_key_path_missing",
        ),
    )
    mldsa_secret_key_path = _resolve_config_path(
        config_path,
        _require_string(
            validator.get("mldsa65_secret_key_path"),
            "node_check_mldsa65_secret_key_path_missing",
        ),
    )
    for path, token in (
        (cert_path, "node_check_tls_cert_missing"),
        (key_path, "node_check_tls_key_missing"),
        (assertion_path, "node_check_endpoint_assertion_missing"),
        (bls_secret_key_path, "node_check_bls_secret_key_missing"),
        (mldsa_public_key_path, "node_check_mldsa65_public_key_missing"),
        (mldsa_secret_key_path, "node_check_mldsa65_secret_key_missing"),
    ):
        if not path.is_file():
            raise ValueError(token)
    if stat.S_IMODE(key_path.stat().st_mode) & 0o077:
        raise ValueError("node_check_tls_key_permissions_too_open")
    if stat.S_IMODE(bls_secret_key_path.stat().st_mode) & 0o077:
        raise ValueError("node_check_bls_secret_key_permissions_too_open")
    if stat.S_IMODE(mldsa_secret_key_path.stat().st_mode) & 0o077:
        raise ValueError("node_check_mldsa65_secret_key_permissions_too_open")
    bls_secret_hex = bls_secret_key_path.read_text(encoding="utf-8").strip()
    _require_lower_hex_exact(
        bls_secret_hex,
        BLS_SECRET_KEY_HEX_LENGTH,
        "node_check_bls_secret_key_invalid",
    )
    mldsa_public_hex = mldsa_public_key_path.read_text(encoding="utf-8").strip()
    _require_lower_hex_exact(
        mldsa_public_hex,
        MLDSA65_PUBLIC_KEY_HEX_LENGTH,
        "node_check_mldsa65_public_key_invalid",
    )

    cert = x509.load_pem_x509_certificate(cert_path.read_bytes())
    try:
        private_key = serialization.load_pem_private_key(key_path.read_bytes(), password=None)
    except (TypeError, ValueError) as exc:
        raise ValueError("node_check_tls_key_invalid") from exc
    if private_key.public_key().public_bytes(
        serialization.Encoding.DER,
        serialization.PublicFormat.SubjectPublicKeyInfo,
    ) != cert.public_key().public_bytes(
        serialization.Encoding.DER,
        serialization.PublicFormat.SubjectPublicKeyInfo,
    ):
        raise ValueError("node_check_tls_key_cert_mismatch")
    current = now or datetime.now(timezone.utc)
    if current.tzinfo is None:
        raise ValueError("node_check_now_must_be_timezone_aware")
    not_before = cert.not_valid_before_utc
    not_after = cert.not_valid_after_utc
    if current < not_before:
        raise ValueError("node_check_tls_cert_not_yet_valid")
    if current > not_after:
        raise ValueError("node_check_tls_cert_expired")

    assertion = ValidatorEndpointAssertion.from_dict(_load_json_object(assertion_path))
    if assertion.grpc_endpoint != _require_string(
        validator.get("grpc_endpoint"),
        "node_check_validator_grpc_endpoint_missing",
    ):
        raise ValueError("node_check_endpoint_assertion_grpc_mismatch")
    if assertion.bls_public_key_hex != _require_string(
        validator.get("bls_public_key_hex"),
        "node_check_bls_public_key_missing",
    ):
        raise ValueError("node_check_endpoint_assertion_bls_mismatch")
    if assertion.tls_cert_sha256_fingerprint != hashlib.sha256(
        cert.public_bytes(serialization.Encoding.DER)
    ).hexdigest():
        raise ValueError("node_check_endpoint_assertion_cert_mismatch")

    readiness_fields = extended_local_check_fields(
        grpc_listen_addr=grpc_listen_addr,
        endpoint_assertion_grpc_endpoint=assertion.grpc_endpoint,
        tls_cert_not_after_utc=not_after,
        now=current,
    )
    return {
        "config_path": str(config_path),
        "endpoint_assertion_path": str(assertion_path),
        "grpc_endpoint": assertion.grpc_endpoint,
        "grpc_listen_addr": grpc_listen_addr,
        "network_id": network_id,
        "runtime_version": OPERATOR_INIT_RUNTIME_VERSION,
        "tls_cert_not_after_utc": _to_iso_utc(not_after),
        "tls_cert_sha256_fingerprint": assertion.tls_cert_sha256_fingerprint,
        "validator_agent_id": assertion.validator_agent_id,
        "verdict": "pass",
        **readiness_fields,
    }


def atomic_write_json(path: Path, payload: dict[str, Any], *, mode: int = 0o600) -> None:
    data = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    )
    atomic_write_text(path, data + "\n", mode=mode)


def atomic_write_text(path: Path, data: str, *, mode: int = 0o600) -> None:
    if not isinstance(data, str):
        raise ValueError("operator_init_atomic_write_data_invalid")
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        os.chmod(tmp_name, mode)
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp_name, path)
    except BaseException:
        try:
            os.unlink(tmp_name)
        except FileNotFoundError:
            pass
        raise


def atomic_write_bytes(path: Path, data: bytes, *, mode: int = 0o600) -> None:
    if not isinstance(data, bytes):
        raise ValueError("operator_init_atomic_write_bytes_invalid")
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        os.chmod(tmp_name, mode)
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp_name, path)
    except BaseException:
        try:
            os.unlink(tmp_name)
        except FileNotFoundError:
            pass
        raise


def _generate_tls_certificate(
    *,
    host: str,
    key_path: Path,
    cert_path: Path,
    der_path: Path,
    valid_days: int,
) -> dict[str, str]:
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=3072)
    subject = issuer = x509.Name(
        [
            x509.NameAttribute(NameOID.COMMON_NAME, host),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Intelligent Labor Coin"),
        ]
    )
    not_before = datetime.now(timezone.utc).replace(microsecond=0) - timedelta(minutes=1)
    not_after = not_before + timedelta(days=valid_days)
    builder = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(private_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(not_before)
        .not_valid_after(not_after)
        .add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True)
        .add_extension(
            x509.SubjectAlternativeName(_san_entries(host)),
            critical=False,
        )
    )
    certificate = builder.sign(private_key=private_key, algorithm=hashes.SHA256())
    key_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption(),
    )
    cert_pem = certificate.public_bytes(serialization.Encoding.PEM)
    cert_der = certificate.public_bytes(serialization.Encoding.DER)
    atomic_write_bytes(key_path, key_pem, mode=0o600)
    atomic_write_bytes(cert_path, cert_pem, mode=0o644)
    atomic_write_bytes(der_path, cert_der, mode=0o644)
    return {
        "fingerprint": hashlib.sha256(cert_der).hexdigest(),
        "not_after_utc": _to_iso_utc(certificate.not_valid_after_utc),
        "not_before_utc": _to_iso_utc(certificate.not_valid_before_utc),
    }


def _san_entries(host: str) -> list[x509.GeneralName]:
    try:
        return [x509.IPAddress(ipaddress.ip_address(host))]
    except ValueError:
        return [x509.DNSName(host)]


def _generate_mldsa65_keypair(
    *,
    public_path: Path,
    secret_path: Path,
    allow_test_stub_crypto: bool,
) -> tuple[str, str]:
    if allow_test_stub_crypto:
        public_hex = secrets.token_hex(MLDSA65_PUBLIC_KEY_HEX_LENGTH // 2)
        secret_hex = secrets.token_hex(MLDSA65_TEST_SECRET_KEY_HEX_LENGTH // 2)
        atomic_write_text(public_path, public_hex + "\n", mode=0o644)
        atomic_write_text(secret_path, secret_hex + "\n", mode=0o600)
        return public_hex, "test_stub"

    try:
        import oqs  # type: ignore[import]
    except (ImportError, RuntimeError, SystemExit):
        raise ValueError("operator_init_mldsa65_keygen_unavailable")

    try:
        signer = oqs.Signature("ML-DSA-65")
        public_key = signer.generate_keypair()
        secret_key = signer.export_secret_key()
    except Exception as exc:  # noqa: BLE001
        raise ValueError("operator_init_mldsa65_keygen_failed") from exc
    public_hex = public_key.hex()
    secret_hex = secret_key.hex()
    _require_lower_hex_exact(public_hex, MLDSA65_PUBLIC_KEY_HEX_LENGTH, "operator_init_mldsa65_public_key_invalid")
    atomic_write_text(public_path, public_hex + "\n", mode=0o644)
    atomic_write_text(secret_path, secret_hex + "\n", mode=0o600)
    return public_hex, "python_oqs"


def _generate_bls_keypair(
    *,
    secret_path: Path,
    allow_test_stub_crypto: bool,
) -> tuple[str, str]:
    if allow_test_stub_crypto:
        return _generate_bls_keypair_stub(secret_path)

    command = os.environ.get(OPERATOR_INIT_BLS_KEYGEN_COMMAND_ENV)
    if command is not None and command.strip():
        return _generate_bls_keypair_external(
            command=tuple(shlex.split(command)),
            secret_path=secret_path,
        )
    default_command = _default_bls_keygen_command()
    if default_command is not None:
        try:
            return _generate_bls_keypair_external(command=default_command, secret_path=secret_path)
        except ValueError:
            if not allow_test_stub_crypto:
                raise
            return _generate_bls_keypair_stub(secret_path)
    raise ValueError("operator_init_bls_keygen_unavailable")


def _generate_bls_keypair_stub(secret_path: Path) -> tuple[str, str]:
    secret_hex = secrets.token_hex(BLS_SECRET_KEY_HEX_LENGTH // 2)
    public_hex = secrets.token_hex(BLS_PUBLIC_KEY_HEX_LENGTH // 2)
    atomic_write_text(secret_path, secret_hex + "\n", mode=0o600)
    return public_hex, "test_stub"


def _generate_bls_keypair_external(
    *,
    command: tuple[str, ...],
    secret_path: Path,
) -> tuple[str, str]:
    if not command:
        raise ValueError("operator_init_bls_keygen_command_missing")
    secret_path.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(str(secret_path), os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    os.close(fd)
    try:
        result = subprocess.run(
            command + ("--out", str(secret_path)),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
            timeout=120,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise ValueError("operator_init_bls_keygen_failed") from exc
    if result.returncode != 0:
        raise ValueError("operator_init_bls_keygen_failed")
    os.chmod(secret_path, 0o600)
    public_hex = result.stdout.strip().splitlines()[-1].strip().lower()
    _require_lower_hex_exact(public_hex, BLS_PUBLIC_KEY_HEX_LENGTH, "operator_init_bls_public_key_invalid")
    secret_hex = secret_path.read_text(encoding="utf-8").strip().lower()
    _require_lower_hex_exact(secret_hex, BLS_SECRET_KEY_HEX_LENGTH, "operator_init_bls_secret_key_invalid")
    return public_hex, "external_command"


def _sign_endpoint_assertion(
    *,
    payload: bytes,
    secret_key_path: Path,
    network_id: str,
    allow_test_stub_crypto: bool,
) -> tuple[str, str]:
    if allow_test_stub_crypto:
        secret = secret_key_path.read_text(encoding="utf-8").strip().encode("ascii")
        digest = hashlib.sha384(payload + network_id.encode("utf-8") + secret).hexdigest()
        signature = (digest + hashlib.sha384(digest.encode("ascii")).hexdigest())[:BLS_SIGNATURE_HEX_LENGTH]
        _require_lower_hex_exact(signature, BLS_SIGNATURE_HEX_LENGTH, "operator_init_bls_signature_invalid")
        return signature, "test_stub_not_production_valid"

    command = os.environ.get(OPERATOR_INIT_BLS_SIGN_COMMAND_ENV)
    command_tuple = tuple(shlex.split(command)) if command is not None and command.strip() else _default_bls_sign_command()
    if command_tuple is not None:
        signature = _sign_endpoint_assertion_external(
            command=command_tuple,
            payload=payload,
            secret_key_path=secret_key_path,
            network_id=network_id,
        )
        return signature, "external_command"
    raise ValueError("operator_init_bls_sign_unavailable")


def _sign_endpoint_assertion_external(
    *,
    command: tuple[str, ...],
    payload: bytes,
    secret_key_path: Path,
    network_id: str,
) -> str:
    if not command:
        raise ValueError("operator_init_bls_sign_command_missing")
    try:
        result = subprocess.run(
            command
            + (
                "sign",
                "--secret-key",
                str(secret_key_path),
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
        raise ValueError("operator_init_bls_sign_failed") from exc
    if result.returncode != 0:
        raise ValueError("operator_init_bls_sign_failed")
    signature = result.stdout.decode("ascii").strip().lower()
    _require_lower_hex_exact(signature, BLS_SIGNATURE_HEX_LENGTH, "operator_init_bls_signature_invalid")
    return signature


def _default_bls_keygen_command() -> tuple[str, ...] | None:
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
        "keygen",
        "--",
    )


def _default_bls_sign_command() -> tuple[str, ...] | None:
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


def _render_node_config(
    *,
    network_id: str,
    grpc_endpoint: str,
    host: str,
    grpc_port: int,
    quic_port: int,
    peer_seeds: list[str],
    tls_cert_path: Path,
    tls_key_path: Path,
    endpoint_assertion_path: Path,
    bls_public_key_hex: str,
    bls_secret_key_path: Path,
    mldsa_public_key_hex: str,
    mldsa_public_key_path: Path,
    mldsa_secret_key_path: Path,
) -> str:
    peers = ", ".join(_toml_string(seed) for seed in peer_seeds)
    return "\n".join(
        (
            "[network]",
            f"network_id = {_toml_string(network_id)}",
            'settlement_path = "mysticeti_fast_path"',
            f"peer_seeds = [{peers}]",
            "",
            "[grpc]",
            f'grpc_listen_addr = "0.0.0.0:{grpc_port}"',
            "",
            "[p2p]",
            f'p2p_listen_addr = "0.0.0.0:{quic_port}"',
            f"public_endpoint = {_toml_string(f'{host}:{quic_port}')}",
            "",
            "[tls]",
            f"tls_cert_path = {_toml_string(str(tls_cert_path))}",
            f"tls_key_path = {_toml_string(str(tls_key_path))}",
            f"peer_ca_cert_path = {_toml_string(str(tls_cert_path))}",
            "",
            "[validator]",
            f"validator_agent_id = {_toml_string(bls_public_key_hex)}",
            f"grpc_endpoint = {_toml_string(grpc_endpoint)}",
            f"bls_public_key_hex = {_toml_string(bls_public_key_hex)}",
            f"bls_secret_key_path = {_toml_string(str(bls_secret_key_path))}",
            f"mldsa65_public_key_hex = {_toml_string(mldsa_public_key_hex)}",
            f"mldsa65_public_key_path = {_toml_string(str(mldsa_public_key_path))}",
            f"mldsa65_secret_key_path = {_toml_string(str(mldsa_secret_key_path))}",
            f"endpoint_assertion_path = {_toml_string(str(endpoint_assertion_path))}",
            "",
        )
    )


def _toml_string(value: str) -> str:
    return json.dumps(value, ensure_ascii=True, allow_nan=False)


def _require_section(config: dict[str, Any], name: str) -> dict[str, Any]:
    value = config.get(name)
    if not isinstance(value, dict):
        raise ValueError(f"node_check_{name}_section_missing")
    return value


def _resolve_config_path(config_path: Path, value: str) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    return (config_path.parent / path).resolve()


def _load_json_object(path: Path) -> dict[str, Any]:
    try:
        payload = _loads_json_no_constants(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        raise ValueError("node_check_json_invalid") from exc
    if not isinstance(payload, dict):
        raise ValueError("node_check_json_not_object")
    return payload


def _loads_json_no_constants(raw: str) -> Any:
    def _reject_constant(value: str) -> None:
        raise ValueError(f"json_non_finite_constant_not_allowed:{value}")

    return json.loads(raw, parse_constant=_reject_constant)


def _require_safe_root(path: Path) -> None:
    if path.exists() and not path.is_dir():
        raise ValueError("operator_init_root_not_directory")


def _require_paths_absent(paths: list[Path]) -> None:
    for path in paths:
        if path.exists():
            raise ValueError("operator_init_refuses_to_overwrite_existing_material")


def _require_string(value: Any, token: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(token)
    return value


def _require_network_id(value: Any) -> str:
    network_id = _require_string(value, "operator_init_network_id_invalid")
    if len(network_id) > MAX_NETWORK_ID_CHARS or not _NETWORK_ID_RE.fullmatch(network_id):
        raise ValueError("operator_init_network_id_invalid")
    return network_id


def _require_host(value: Any) -> str:
    host = _require_string(value, "operator_init_host_invalid")
    if len(host) > MAX_HOST_CHARS or ":" in host or not _host_is_valid(host):
        raise ValueError("operator_init_host_invalid")
    return host


def _require_port(value: Any, token: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 1 or value > 65535:
        raise ValueError(token)
    return value


def _require_positive_int(value: Any, token: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ValueError(token)
    return value


def _require_uint64(value: Any, token: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0 or value > 2**64 - 1:
        raise ValueError(token)
    return value


def _require_peer_seeds(values: list[str]) -> list[str]:
    if len(values) > MAX_PEER_SEEDS:
        raise ValueError("operator_init_peer_seed_limit_exceeded")
    seeds: list[str] = []
    seen: set[str] = set()
    for value in values:
        seed = _require_string(value, "operator_init_peer_seed_invalid")
        _parse_endpoint(seed, "operator_init_peer_seed_invalid")
        if seed not in seen:
            seeds.append(seed)
            seen.add(seed)
    return seeds


def _parse_endpoint(value: str, token: str) -> tuple[str, int]:
    if ":" not in value:
        raise ValueError(token)
    host, port_text = value.rsplit(":", 1)
    _require_host(host)
    try:
        port = int(port_text)
    except ValueError as exc:
        raise ValueError(token) from exc
    return host, _require_port(port, token)


def _host_is_valid(value: str) -> bool:
    try:
        ipaddress.ip_address(value)
        return True
    except ValueError:
        return bool(_DNS_HOST_RE.fullmatch(value)) and ".." not in value


def _require_lower_hex_exact(value: Any, length: int, token: str) -> str:
    if not isinstance(value, str) or len(value) != length or any(char not in _LOWER_HEX for char in value):
        raise ValueError(token)
    return value


def _now_utc() -> str:
    return _to_iso_utc(datetime.now(timezone.utc).replace(microsecond=0))


def _to_iso_utc(value: datetime) -> str:
    normalized = value.astimezone(timezone.utc).replace(microsecond=0)
    return normalized.strftime("%Y-%m-%dT%H:%M:%SZ")


__all__ = [
    "OPERATOR_INIT_BLS_KEYGEN_COMMAND_ENV",
    "OPERATOR_INIT_BLS_SIGN_COMMAND_ENV",
    "OPERATOR_INIT_RUNTIME_VERSION",
    "NodeInitResult",
    "atomic_write_json",
    "check_node_config",
    "generate_node_init_material",
]
