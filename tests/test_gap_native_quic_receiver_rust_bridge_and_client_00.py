from __future__ import annotations

import hashlib
import inspect
import json
import os
import socket
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone
from ipaddress import ip_address
from pathlib import Path

import pytest
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID

from ilc_core import bridge_submit_receiver
from ilc_core.cli.d2e_submit_cli import _build_native_submit_sig_object
from ilc_core.consensus import binary_paths
from ilc_core.identity.bls_backend import keypair_from_ikm_hex
from ilc_core.storage.truth_primitive_graph_lmdb_adapter import TruthPrimitiveGraphStore


ROOT = Path(__file__).resolve().parents[1]
CARGO_TOML = ROOT / "ilc_consensus" / "Cargo.toml"
RECEIVER_SOURCE = ROOT / "ilc_consensus" / "src" / "ilc_native_submit_receiver_bridge_main.rs"
CLIENT_SOURCE = ROOT / "ilc_consensus" / "src" / "ilc_native_submit_client_main.rs"
RECEIVER_BINARY = ROOT / "ilc_consensus" / "target" / "debug" / "ilc_native_submit_receiver_bridge"
CLIENT_BINARY = ROOT / "ilc_consensus" / "target" / "debug" / "ilc_native_submit_client"
TEST_SECRET_HEX, TEST_AGENT_ID = keypair_from_ikm_hex("5c" * 32)


def _signed_assertion(epoch: int = 7) -> dict:
    envelope = {
        "v": 1,
        "primitive": "assert.truth",
        "agent_id": TEST_AGENT_ID,
        "epoch": epoch,
        "payload": {
            "content": {"claim": "native QUIC bridge integration test"},
            "primitive_type": "observation",
            "epistemic_type": "objective",
            "parent_node_ids": [],
        },
        "sig": "UNSIGNED",
    }
    envelope["sig"] = _build_native_submit_sig_object(envelope, TEST_SECRET_HEX)
    return envelope


def _free_udp_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def _write_cert_pair(tmp_path: Path) -> tuple[Path, Path, str]:
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COMMON_NAME, "localhost"),
    ])
    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.now(timezone.utc) - timedelta(minutes=1))
        .not_valid_after(datetime.now(timezone.utc) + timedelta(days=1))
        .add_extension(
            x509.SubjectAlternativeName([
                x509.DNSName("localhost"),
                x509.IPAddress(ip_address("127.0.0.1")),
            ]),
            critical=False,
        )
        .sign(key, hashes.SHA256())
    )
    cert_pem = cert.public_bytes(serialization.Encoding.PEM)
    key_pem = key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    )
    cert_path = tmp_path / "receiver.crt"
    key_path = tmp_path / "receiver.key"
    cert_path.write_bytes(cert_pem)
    key_path.write_bytes(key_pem)
    cert_der = cert.public_bytes(serialization.Encoding.DER)
    return cert_path, key_path, hashlib.sha256(cert_der).hexdigest()


def test_worker_processes_signed_envelope_and_rejects_replay(tmp_path: Path) -> None:
    store = TruthPrimitiveGraphStore(tmp_path / "graph.lmdb")
    try:
        envelope = _signed_assertion()
        first = bridge_submit_receiver.process_submission(envelope, store=store)
        assert first["ok"] is True
        assert first["node_id"]

        second = bridge_submit_receiver.process_line(
            json.dumps(envelope, separators=(",", ":"), sort_keys=True).encode("utf-8"),
            store=store,
        )
        assert second == {
            "ok": False,
            "error": "native_submit_sig_replay_rejected_CDL_118",
        }
    finally:
        store.close()


def test_worker_error_receipts_are_tokenized() -> None:
    receipt = bridge_submit_receiver.process_line(b'{"sig":"UNSIGNED"}')

    assert receipt["ok"] is False
    assert "error" in receipt
    assert receipt["error"] != "native_submit_bridge_internal_error"


def test_worker_rejects_oversize_line_without_json_parse() -> None:
    receipt = bridge_submit_receiver.process_line(b"{" + b"x" * bridge_submit_receiver.MAX_WORKER_LINE_BYTES)

    assert receipt == {"ok": False, "error": "native_submit_worker_line_too_large"}


def test_cargo_declares_native_quic_receiver_binaries() -> None:
    text = CARGO_TOML.read_text(encoding="utf-8")

    assert 'name = "ilc_native_submit_receiver_bridge"' in text
    assert 'path = "src/ilc_native_submit_receiver_bridge_main.rs"' in text
    assert 'name = "ilc_native_submit_client"' in text
    assert 'path = "src/ilc_native_submit_client_main.rs"' in text
    assert 'rustls-pemfile = "2"' in text
    assert 'webpki-roots = "0.26"' in text
    assert RECEIVER_SOURCE.is_file()
    assert CLIENT_SOURCE.is_file()


def test_binary_resolver_allows_native_submit_helpers(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    receiver = tmp_path / "ilc_native_submit_receiver_bridge"
    receiver.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    receiver.chmod(0o700)
    client = tmp_path / "ilc_native_submit_client"
    client.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    client.chmod(0o700)
    monkeypatch.setenv("ILC_CONSENSUS_BIN_DIR", str(tmp_path))

    assert binary_paths.installed_consensus_binary_command(
        "ilc_native_submit_receiver_bridge"
    ) == (str(receiver),)
    assert binary_paths.installed_consensus_binary_command("ilc_native_submit_client") == (
        str(client),
    )


def test_source_preserves_rust_transport_python_semantics_boundary() -> None:
    worker_source = inspect.getsource(bridge_submit_receiver)
    receiver_source = RECEIVER_SOURCE.read_text(encoding="utf-8")

    assert "validate_truth_primitive_submission" in worker_source
    assert "write_truth_primitive_result" in worker_source
    assert "validate_truth_primitive_submission" not in receiver_source
    assert "ILC_SUBMIT_BRIDGE_SOCKET" in receiver_source
    assert "ilc-native-submit-v1" in receiver_source
    assert "MAX_FRAME_BYTES: usize = 1_048_576" in receiver_source
    assert "native_submit_frame_read_timeout" in receiver_source
    assert "native_submit_frame_trailing_bytes" in receiver_source
    assert "native_submit_frame_body_not_single_line_json" in receiver_source
    assert "native_submit_frame_body_json_invalid" in receiver_source
    assert "native_submit_client_response_trailing_bytes" in CLIENT_SOURCE.read_text(
        encoding="utf-8"
    )


def test_receiver_replenishes_worker_pool_after_worker_error() -> None:
    receiver_source = RECEIVER_SOURCE.read_text(encoding="utf-8")

    assert "struct WorkerPool" in receiver_source
    assert "socket_path: PathBuf" in receiver_source
    assert "async fn replenish_worker_pool" in receiver_source
    assert "connect_worker(&pool.socket_path).await" in receiver_source
    assert "native_submit_bridge_pool_replenish_failed" in receiver_source


def test_receiver_worker_response_read_is_bounded_before_newline() -> None:
    receiver_source = RECEIVER_SOURCE.read_text(encoding="utf-8")

    assert "async fn read_worker_response_line" in receiver_source
    assert ".read_until(" not in receiver_source
    assert "line.len().saturating_add(take) > MAX_WORKER_RESPONSE_BYTES" in receiver_source
    assert "native_submit_bridge_worker_response_too_large" in receiver_source


def test_frame_length_conversion_is_explicit_u32_try_from() -> None:
    receiver_source = RECEIVER_SOURCE.read_text(encoding="utf-8")
    client_source = CLIENT_SOURCE.read_text(encoding="utf-8")

    assert "u32::try_from(body.len()).expect(\"frame body exceeds u32 max\")" in receiver_source
    assert "u32::try_from(body.len()).expect(\"frame body exceeds u32 max\")" in client_source
    assert "(body.len() as u32)" not in receiver_source
    assert "(body.len() as u32)" not in client_source


def test_local_quic_roundtrip_to_python_worker_persists_node(tmp_path: Path) -> None:
    if not RECEIVER_BINARY.exists() or not CLIENT_BINARY.exists():
        pytest.skip("run cargo build for native QUIC receiver/client before integration test")

    store_path = tmp_path / "truth_graph.lmdb"
    cert_path, key_path, fingerprint = _write_cert_pair(tmp_path)
    port = _free_udp_port()
    socket_path = Path(f"/tmp/ilc_native_submit_bridge_test_{os.getpid()}_{port}.sock")
    if socket_path.exists():
        socket_path.unlink()

    worker_env = {
        **os.environ,
        "PYTHONPATH": str(ROOT),
        "ILC_SUBMIT_BRIDGE_SOCKET": str(socket_path),
        "ILC_TRUTH_GRAPH_STORE_PATH": str(store_path),
    }
    worker = subprocess.Popen(
        [sys.executable, "-m", "ilc_core.bridge_submit_receiver", "--worker"],
        cwd=ROOT,
        env=worker_env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    receiver_env = {
        **os.environ,
        "ILC_SUBMIT_RECEIVER_BIND_ADDR": f"127.0.0.1:{port}",
        "ILC_SUBMIT_RECEIVER_TLS_CERT": str(cert_path),
        "ILC_SUBMIT_RECEIVER_TLS_KEY": str(key_path),
        "ILC_SUBMIT_BRIDGE_SOCKET": str(socket_path),
        "ILC_SUBMIT_BRIDGE_POOL_SIZE": "1",
    }
    receiver = None
    try:
        deadline = time.time() + 10
        while not socket_path.exists() and time.time() < deadline:
            time.sleep(0.05)
        assert socket_path.exists()

        receiver = subprocess.Popen(
            [str(RECEIVER_BINARY)],
            cwd=ROOT,
            env=receiver_env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        envelope = json.dumps(_signed_assertion(epoch=11), separators=(",", ":"), sort_keys=True)
        client_cmd = [
            str(CLIENT_BINARY),
            "--endpoint",
            f"127.0.0.1:{port}",
            "--expected-tls-fingerprint",
            fingerprint,
            "--timeout-ms",
            "10000",
        ]
        result = None
        deadline = time.time() + 15
        while time.time() < deadline:
            result = subprocess.run(
                client_cmd,
                cwd=ROOT,
                input=envelope,
                capture_output=True,
                text=True,
                timeout=15,
            )
            if result.returncode == 0:
                break
            time.sleep(0.2)
        assert result is not None
        assert result.returncode == 0, result.stderr + result.stdout
        receipt = json.loads(result.stdout)
        assert receipt["ok"] is True
        assert receipt["node_id"]

        unsigned = _signed_assertion(epoch=12)
        unsigned["sig"] = "UNSIGNED"
        unsigned_result = subprocess.run(
            client_cmd,
            cwd=ROOT,
            input=json.dumps(unsigned, separators=(",", ":"), sort_keys=True),
            capture_output=True,
            text=True,
            timeout=15,
        )
        assert unsigned_result.returncode == 1
        unsigned_receipt = json.loads(unsigned_result.stdout)
        assert unsigned_receipt == {
            "ok": False,
            "error": "native_submit_sig_unsigned_placeholder_rejected",
        }
    finally:
        if receiver is not None:
            receiver.terminate()
            receiver.wait(timeout=5)
        worker.terminate()
        worker.wait(timeout=5)
        try:
            socket_path.unlink()
        except FileNotFoundError:
            pass
