# SPDX-License-Identifier: AGPL-3.0-only
"""GAP-OPERATOR-INIT-00 operator node init CLI tests."""

from __future__ import annotations

import json
import os
import shutil
import stat
import subprocess
import sys
import tomllib
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest
from cryptography import x509
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID

from ilc_core.consensus.validator_endpoint_assertion import ValidatorEndpointAssertion
from ilc_core.node.operator_init_runtime import (
    MLDSA65_PUBLIC_KEY_HEX_LENGTH,
    atomic_write_json,
    check_node_config,
    generate_node_init_material,
)


def _run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "ilc_core.cli", *args],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
        timeout=30,
    )


def _init_args(root: Path) -> list[str]:
    return [
        "node",
        "init",
        "--root",
        str(root),
        "--network-id",
        "ilc-rc01",
        "--host",
        "127.0.0.1",
        "--grpc-port",
        "50151",
        "--quic-port",
        "7101",
        "--peer-seed",
        "127.0.0.1:7102",
        "--allow-test-stub-crypto",
    ]


def _load_json(path: Path) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise AssertionError("expected JSON object")
    return payload


def test_node_init_help_discoverable() -> None:
    result = _run_cli("node", "init", "--help")
    assert result.returncode == 0
    assert "--root" in result.stdout
    assert "--allow-test-stub-crypto" in result.stdout


def test_node_check_help_discoverable() -> None:
    result = _run_cli("node", "check", "--help")
    assert result.returncode == 0
    assert "--config" in result.stdout


def test_node_init_generates_tls_cert_and_key(tmp_path: Path) -> None:
    result = generate_node_init_material(
        root=tmp_path / "node",
        network_id="ilc-rc01",
        host="127.0.0.1",
        grpc_port=50151,
        quic_port=7101,
        allow_test_stub_crypto=True,
    )
    cert = result.root / "certs" / "validator_tls_cert.pem"
    key = result.root / "certs" / "validator_tls_key.pem"
    assert cert.is_file()
    assert key.is_file()
    assert stat.S_IMODE(key.stat().st_mode) == 0o600
    assert x509.load_pem_x509_certificate(cert.read_bytes())


def test_node_init_generates_validator_keypair(tmp_path: Path) -> None:
    result = generate_node_init_material(
        root=tmp_path / "node",
        network_id="ilc-rc01",
        host="validator.example",
        grpc_port=50151,
        quic_port=7101,
        allow_test_stub_crypto=True,
    )
    public_key = result.root / "keys" / "validator_mldsa65_public.hex"
    secret_key = result.root / "keys" / "validator_mldsa65_secret.hex"
    bls_secret_key = result.root / "keys" / "validator_bls_secret.hex"
    assert public_key.is_file()
    assert secret_key.is_file()
    assert bls_secret_key.is_file()
    assert len(public_key.read_text(encoding="utf-8").strip()) == MLDSA65_PUBLIC_KEY_HEX_LENGTH
    assert stat.S_IMODE(secret_key.stat().st_mode) == 0o600
    assert stat.S_IMODE(bls_secret_key.stat().st_mode) == 0o600


def test_node_init_generates_endpoint_assertion(tmp_path: Path) -> None:
    result = generate_node_init_material(
        root=tmp_path / "node",
        network_id="ilc-rc01",
        host="validator.example",
        grpc_port=50151,
        quic_port=7101,
        allow_test_stub_crypto=True,
    )
    payload = _load_json(result.endpoint_assertion_path)
    assert "network_id" not in payload
    assert payload["grpc_endpoint"] == "validator.example:50151"
    assert len(str(payload["bls_public_key_hex"])) == 96
    assert len(str(payload["bls_signature_hex"])) == 192
    assert payload["validator_agent_id"] == payload["bls_public_key_hex"]
    ValidatorEndpointAssertion.from_dict(payload)


def test_node_init_generates_node_config_toml(tmp_path: Path) -> None:
    result = generate_node_init_material(
        root=tmp_path / "node",
        network_id="ilc-rc01",
        host="validator.example",
        grpc_port=50151,
        quic_port=7101,
        peer_seeds=["validator-two.example:7101"],
        allow_test_stub_crypto=True,
    )
    config = result.config_path.read_text(encoding="utf-8")
    assert 'network_id = "ilc-rc01"' in config
    assert 'grpc_listen_addr = "0.0.0.0:50151"' in config
    assert 'public_endpoint = "validator.example:7101"' in config
    assert "tls_cert_path" in config
    assert "validator-two.example:7101" in config


def test_node_init_toml_escapes_generated_paths(tmp_path: Path) -> None:
    result = generate_node_init_material(
        root=tmp_path / 'node "quoted"',
        network_id="ilc-rc01",
        host="validator.example",
        grpc_port=50151,
        quic_port=7101,
        allow_test_stub_crypto=True,
    )

    parsed = tomllib.loads(result.config_path.read_text(encoding="utf-8"))

    assert parsed["tls"]["tls_cert_path"].endswith('node "quoted"/certs/validator_tls_cert.pem')
    assert parsed["validator"]["endpoint_assertion_path"].endswith(
        'node "quoted"/out/node_init/validator_endpoint_assertion.json'
    )


def test_node_init_writes_receipt_atomically(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[tuple[str, str]] = []

    def fake_replace(src: str, dst: str) -> None:
        calls.append((src, dst))
        os.rename(src, dst)

    monkeypatch.setattr(os, "replace", fake_replace)
    output = tmp_path / "receipt.json"
    atomic_write_json(output, {"phase": "GAP-OPERATOR-INIT-00"})
    assert calls
    assert _load_json(output)["phase"] == "GAP-OPERATOR-INIT-00"


def test_node_check_passes_on_complete_config(tmp_path: Path) -> None:
    root = tmp_path / "node"
    result = _run_cli(*_init_args(root))
    assert result.returncode == 0, result.stderr
    config = root / "config" / "node_config.toml"
    check = _run_cli("node", "check", "--config", str(config))
    assert check.returncode == 0, check.stderr
    payload = json.loads(check.stdout)
    assert payload["data"]["verdict"] == "pass"


def test_node_check_fails_on_missing_cert(tmp_path: Path) -> None:
    generated = generate_node_init_material(
        root=tmp_path / "node",
        network_id="ilc-rc01",
        host="127.0.0.1",
        grpc_port=50151,
        quic_port=7101,
        allow_test_stub_crypto=True,
    )
    (generated.root / "certs" / "validator_tls_cert.pem").unlink()
    with pytest.raises(ValueError, match="node_check_tls_cert_missing"):
        check_node_config(generated.config_path)


def test_node_check_fails_on_expired_cert(tmp_path: Path) -> None:
    generated = generate_node_init_material(
        root=tmp_path / "node",
        network_id="ilc-rc01",
        host="validator.example",
        grpc_port=50151,
        quic_port=7101,
        allow_test_stub_crypto=True,
    )
    future = datetime.now(timezone.utc) + timedelta(days=400)
    with pytest.raises(ValueError, match="node_check_tls_cert_expired"):
        check_node_config(generated.config_path, now=future)


def test_node_check_fails_on_not_yet_valid_cert(tmp_path: Path) -> None:
    generated = generate_node_init_material(
        root=tmp_path / "node",
        network_id="ilc-rc01",
        host="validator.example",
        grpc_port=50151,
        quic_port=7101,
        allow_test_stub_crypto=True,
    )
    key_path = generated.root / "certs" / "validator_tls_key.pem"
    private_key = serialization.load_pem_private_key(key_path.read_bytes(), password=None)
    subject = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "validator.example")])
    now = datetime.now(timezone.utc)
    future_cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(subject)
        .public_key(private_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now + timedelta(days=1))
        .not_valid_after(now + timedelta(days=30))
        .sign(private_key, hashes.SHA256())
    )
    (generated.root / "certs" / "validator_tls_cert.pem").write_bytes(
        future_cert.public_bytes(serialization.Encoding.PEM)
    )

    with pytest.raises(ValueError, match="node_check_tls_cert_not_yet_valid"):
        check_node_config(generated.config_path, now=now)


def test_node_check_resolves_relative_paths_from_config_dir(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    generated = generate_node_init_material(
        root=tmp_path / "node",
        network_id="ilc-rc01",
        host="127.0.0.1",
        grpc_port=50151,
        quic_port=7101,
        allow_test_stub_crypto=True,
    )
    config = generated.config_path.read_text(encoding="utf-8")
    replacements = {
        str(generated.root / "certs" / "validator_tls_cert.pem"): "../certs/validator_tls_cert.pem",
        str(generated.root / "certs" / "validator_tls_key.pem"): "../certs/validator_tls_key.pem",
        str(generated.root / "keys" / "validator_bls_secret.hex"): "../keys/validator_bls_secret.hex",
        str(generated.root / "keys" / "validator_mldsa65_public.hex"): "../keys/validator_mldsa65_public.hex",
        str(generated.root / "keys" / "validator_mldsa65_secret.hex"): "../keys/validator_mldsa65_secret.hex",
        str(generated.root / "out" / "node_init" / "validator_endpoint_assertion.json"): "../out/node_init/validator_endpoint_assertion.json",
    }
    for absolute, relative in replacements.items():
        config = config.replace(absolute, relative)
    generated.config_path.write_text(config, encoding="utf-8")

    shadow = tmp_path / "shadow"
    (shadow / "certs").mkdir(parents=True)
    (shadow / "certs" / "validator_tls_cert.pem").write_text("not-a-cert", encoding="utf-8")
    monkeypatch.chdir(shadow)

    assert check_node_config(generated.config_path)["verdict"] == "pass"


def test_node_init_rejects_invalid_peer_seed(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="operator_init_peer_seed_invalid"):
        generate_node_init_material(
            root=tmp_path / "node",
            network_id="ilc-rc01",
            host="validator.example",
            grpc_port=50151,
            quic_port=7101,
            peer_seeds=["not-an-endpoint"],
            allow_test_stub_crypto=True,
        )


def test_node_check_detects_tls_key_cert_mismatch(tmp_path: Path) -> None:
    generated = generate_node_init_material(
        root=tmp_path / "node",
        network_id="ilc-rc01",
        host="validator.example",
        grpc_port=50151,
        quic_port=7101,
        allow_test_stub_crypto=True,
    )
    replacement_key = rsa.generate_private_key(public_exponent=65537, key_size=3072)
    subject = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "validator.example")])
    now = datetime.now(timezone.utc)
    replacement_cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(subject)
        .public_key(replacement_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - timedelta(minutes=1))
        .not_valid_after(now + timedelta(days=1))
        .sign(replacement_key, hashes.SHA256())
    )
    (generated.root / "certs" / "validator_tls_cert.pem").write_bytes(
        replacement_cert.public_bytes(serialization.Encoding.PEM)
    )
    with pytest.raises(ValueError, match="node_check_tls_key_cert_mismatch"):
        check_node_config(generated.config_path)


def test_stub_mode_does_not_require_oqs_or_cargo(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(shutil, "which", lambda _name: None)
    result = generate_node_init_material(
        root=tmp_path / "node",
        network_id="ilc-rc01",
        host="127.0.0.1",
        grpc_port=50151,
        quic_port=7101,
        allow_test_stub_crypto=True,
    )
    assert result.mldsa_keygen_mode == "test_stub"
    assert result.bls_keygen_mode == "test_stub"
    assert result.bls_signature_mode == "test_stub_not_production_valid"


def test_node_init_refuses_to_overwrite_existing_material(tmp_path: Path) -> None:
    root = tmp_path / "node"
    generate_node_init_material(
        root=root,
        network_id="ilc-rc01",
        host="127.0.0.1",
        grpc_port=50151,
        quic_port=7101,
        allow_test_stub_crypto=True,
    )
    with pytest.raises(ValueError, match="operator_init_refuses_to_overwrite_existing_material"):
        generate_node_init_material(
            root=root,
            network_id="ilc-rc01",
            host="127.0.0.1",
            grpc_port=50151,
            quic_port=7101,
            allow_test_stub_crypto=True,
        )


def test_node_init_rejects_toml_unsafe_network_and_host(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="operator_init_network_id_invalid"):
        generate_node_init_material(
            root=tmp_path / "network",
            network_id='ilc-"bad"',
            host="127.0.0.1",
            grpc_port=50151,
            quic_port=7101,
            allow_test_stub_crypto=True,
        )
    with pytest.raises(ValueError, match="operator_init_host_invalid"):
        generate_node_init_material(
            root=tmp_path / "host",
            network_id="ilc-rc01",
            host="bad/host",
            grpc_port=50151,
            quic_port=7101,
            allow_test_stub_crypto=True,
        )


def test_node_check_rejects_open_tls_key_permissions(tmp_path: Path) -> None:
    generated = generate_node_init_material(
        root=tmp_path / "node",
        network_id="ilc-rc01",
        host="127.0.0.1",
        grpc_port=50151,
        quic_port=7101,
        allow_test_stub_crypto=True,
    )
    key_path = generated.root / "certs" / "validator_tls_key.pem"
    key_path.chmod(0o644)
    with pytest.raises(ValueError, match="node_check_tls_key_permissions_too_open"):
        check_node_config(generated.config_path)


def test_node_check_rejects_open_validator_secret_key_permissions(tmp_path: Path) -> None:
    generated = generate_node_init_material(
        root=tmp_path / "node",
        network_id="ilc-rc01",
        host="127.0.0.1",
        grpc_port=50151,
        quic_port=7101,
        allow_test_stub_crypto=True,
    )
    bls_key_path = generated.root / "keys" / "validator_bls_secret.hex"
    bls_key_path.chmod(0o644)
    with pytest.raises(ValueError, match="node_check_bls_secret_key_permissions_too_open"):
        check_node_config(generated.config_path)


def test_node_check_rejects_corrupt_validator_key_files(tmp_path: Path) -> None:
    generated = generate_node_init_material(
        root=tmp_path / "node",
        network_id="ilc-rc01",
        host="127.0.0.1",
        grpc_port=50151,
        quic_port=7101,
        allow_test_stub_crypto=True,
    )
    (generated.root / "keys" / "validator_bls_secret.hex").write_text(
        "not-hex\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="node_check_bls_secret_key_invalid"):
        check_node_config(generated.config_path)


def test_node_check_detects_endpoint_assertion_cert_mismatch(tmp_path: Path) -> None:
    generated = generate_node_init_material(
        root=tmp_path / "node",
        network_id="ilc-rc01",
        host="validator.example",
        grpc_port=50151,
        quic_port=7101,
        allow_test_stub_crypto=True,
    )
    payload = _load_json(generated.endpoint_assertion_path)
    payload["tls_cert_sha256_fingerprint"] = "0" * 64
    generated.endpoint_assertion_path.write_text(
        json.dumps(payload, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="node_check_endpoint_assertion_cert_mismatch"):
        check_node_config(generated.config_path)
