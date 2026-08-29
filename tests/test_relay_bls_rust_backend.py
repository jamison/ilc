from __future__ import annotations

import os
from pathlib import Path
import shutil
import subprocess

import pytest

from ilc_core.identity import bls_backend
from ilc_core.identity.bls_backend import (
    keypair_from_ikm_hex,
    sign_invite_pop_digest,
    sign_relay_bootstrap_capsule_digest,
    sign_relay_bootstrap_record_digest,
    verify_bls_signature_rust,
    verify_invite_pop_digest,
    verify_relay_bootstrap_capsule_digest,
    verify_relay_bootstrap_record_digest,
)
from ilc_core.network.relay.relay_server import (
    RelayServerConfig,
    build_relay_bootstrap_record,
    parse_relay_bootstrap_capsule,
    relay_bootstrap_capsule_payload_ref,
    relay_bootstrap_record_payload_ref,
    sign_relay_bootstrap_record,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
RUST_BINARY = REPO_ROOT / "ilc_consensus" / "target" / "debug" / "bls_verify_digest"
RUST_COMMAND = str(RUST_BINARY)


@pytest.fixture(scope="module", autouse=True)
def build_rust_bls_verify_helper() -> None:
    cargo = os.environ.get("CARGO") or shutil.which("cargo")
    if cargo is None:
        home_cargo = Path.home() / ".cargo" / "bin" / "cargo"
        cargo = str(home_cargo) if home_cargo.exists() else None
    if cargo is None:
        pytest.skip("Rust cargo binary unavailable")
    result = subprocess.run(
        [
            cargo,
            "build",
            "--quiet",
            "--manifest-path",
            str(REPO_ROOT / "ilc_consensus" / "Cargo.toml"),
            "--bin",
            "bls_verify_digest",
        ],
        check=False,
        capture_output=True,
        text=True,
        timeout=120,
    )
    if result.returncode != 0:
        pytest.skip(f"Rust bls_verify_digest helper unavailable: {result.stderr[-500:]}")


def _relay_keypair() -> tuple[str, str]:
    return keypair_from_ikm_hex("71" * 32)


def _genesis_keypair() -> tuple[str, str]:
    return keypair_from_ikm_hex("72" * 32)


def test_default_bls_backend_is_python(monkeypatch: pytest.MonkeyPatch) -> None:
    secret_key_hex, agent_id = _relay_keypair()
    digest_hex = "a1" * 48
    signature_hex = sign_relay_bootstrap_record_digest(secret_key_hex, digest_hex)
    monkeypatch.delenv("ILC_BLS_BACKEND", raising=False)

    def fail_if_rust_called(**_kwargs: str) -> bool | None:
        raise AssertionError("default backend must not invoke Rust helper")

    monkeypatch.setattr(bls_backend, "_try_verify_bls_signature_rust", fail_if_rust_called)

    assert verify_relay_bootstrap_record_digest(
        public_key_hex=agent_id,
        digest_hex=digest_hex,
        signature_hex=signature_hex,
    )


def test_rust_backend_verifies_valid_relay_record_signature(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    secret_key_hex, agent_id = _relay_keypair()
    digest_hex = "a2" * 48
    signature_hex = sign_relay_bootstrap_record_digest(secret_key_hex, digest_hex)
    monkeypatch.setenv("ILC_BLS_BACKEND", "rust")
    monkeypatch.setenv("ILC_BLS_VERIFY_COMMAND", RUST_COMMAND)

    assert verify_relay_bootstrap_record_digest(
        public_key_hex=agent_id,
        digest_hex=digest_hex,
        signature_hex=signature_hex,
    )


def test_rust_backend_rejects_wrong_dst_signature(monkeypatch: pytest.MonkeyPatch) -> None:
    secret_key_hex, agent_id = _relay_keypair()
    digest_hex = "a3" * 48
    wrong_signature_hex = sign_invite_pop_digest(secret_key_hex, digest_hex)
    monkeypatch.setenv("ILC_BLS_BACKEND", "rust")
    monkeypatch.setenv("ILC_BLS_VERIFY_COMMAND", RUST_COMMAND)

    assert not verify_relay_bootstrap_record_digest(
        public_key_hex=agent_id,
        digest_hex=digest_hex,
        signature_hex=wrong_signature_hex,
    )


def test_rust_backend_file_not_found_falls_back_to_python(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    secret_key_hex, agent_id = _relay_keypair()
    digest_hex = "a4" * 48
    signature_hex = sign_relay_bootstrap_record_digest(secret_key_hex, digest_hex)
    monkeypatch.setenv("ILC_BLS_BACKEND", "rust")
    monkeypatch.setenv("ILC_BLS_VERIFY_COMMAND", "/definitely/not/bls_verify_digest")

    assert verify_relay_bootstrap_record_digest(
        public_key_hex=agent_id,
        digest_hex=digest_hex,
        signature_hex=signature_hex,
    )


def test_rust_backend_blank_command_falls_back_to_python(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    secret_key_hex, agent_id = _relay_keypair()
    digest_hex = "aa" * 48
    signature_hex = sign_relay_bootstrap_record_digest(secret_key_hex, digest_hex)
    monkeypatch.setenv("ILC_BLS_BACKEND", "rust")
    monkeypatch.setenv("ILC_BLS_VERIFY_COMMAND", "   ")

    assert verify_relay_bootstrap_record_digest(
        public_key_hex=agent_id,
        digest_hex=digest_hex,
        signature_hex=signature_hex,
    )


def test_rust_backend_unexpected_output_fails_closed(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    secret_key_hex, agent_id = _relay_keypair()
    digest_hex = "a5" * 48
    signature_hex = sign_relay_bootstrap_record_digest(secret_key_hex, digest_hex)
    helper = tmp_path / "fake_bls_verify"
    helper.write_text("#!/bin/sh\nprintf 'maybe\\n'\n", encoding="utf-8")
    helper.chmod(0o700)
    monkeypatch.setenv("ILC_BLS_BACKEND", "rust")
    monkeypatch.setenv("ILC_BLS_VERIFY_COMMAND", str(helper))

    assert not verify_relay_bootstrap_record_digest(
        public_key_hex=agent_id,
        digest_hex=digest_hex,
        signature_hex=signature_hex,
    )


def test_python_backend_verifies_invite_pop(monkeypatch: pytest.MonkeyPatch) -> None:
    secret_key_hex, agent_id = _relay_keypair()
    digest_hex = "a6" * 48
    signature_hex = sign_invite_pop_digest(secret_key_hex, digest_hex)
    monkeypatch.setenv("ILC_BLS_BACKEND", "python")

    assert verify_invite_pop_digest(
        public_key_hex=agent_id,
        digest_hex=digest_hex,
        signature_hex=signature_hex,
    )


def test_relay_capsule_verifies_with_rust_backend(monkeypatch: pytest.MonkeyPatch) -> None:
    genesis_secret_key_hex, genesis_agent_id = _genesis_keypair()
    relay_secret_key_hex, relay_agent_id = _relay_keypair()
    unsigned_record = build_relay_bootstrap_record(
        RelayServerConfig(relay_agent_id=relay_agent_id, relay_host="127.0.0.1"),
        issued_epoch=0,
        expires_epoch=4,
    )
    signed_record = sign_relay_bootstrap_record(
        unsigned_record,
        relay_secret_key_hex=relay_secret_key_hex,
        signing_key_id=relay_agent_id,
    )
    capsule_payload = {
        "expires_epoch": 4,
        "issued_epoch": 0,
        "network_id": "public-rc",
        "relay_records": [signed_record],
        "schema_version": "relay_bootstrap_capsule_v0.1",
    }
    payload_ref = relay_bootstrap_capsule_payload_ref(capsule_payload)
    capsule = {
        **capsule_payload,
        "payload_sha384": payload_ref,
        "signature": sign_relay_bootstrap_capsule_digest(
            secret_key_hex=genesis_secret_key_hex,
            digest_hex=payload_ref,
        ),
        "signature_alg": "BLS12-381-G2-SHA-256-SSWU-RO",
        "signing_key_id": genesis_agent_id,
    }
    monkeypatch.setenv("ILC_BLS_BACKEND", "rust")
    monkeypatch.setenv("ILC_BLS_VERIFY_COMMAND", RUST_COMMAND)

    assert verify_relay_bootstrap_capsule_digest(
        public_key_hex=genesis_agent_id,
        digest_hex=payload_ref,
        signature_hex=capsule["signature"],
    )
    assert parse_relay_bootstrap_capsule(
        capsule,
        genesis_agent_id=genesis_agent_id,
        expected_network_id="public-rc",
        current_epoch=0,
    ) == (signed_record,)


def test_verify_bls_signature_rust_returns_false_when_helper_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _secret_key_hex, agent_id = _relay_keypair()
    monkeypatch.setenv("ILC_BLS_VERIFY_COMMAND", "/definitely/not/bls_verify_digest")

    assert not verify_bls_signature_rust(
        agent_id,
        "a7" * 48,
        "a8" * 96,
        suite="relay_bootstrap_record",
    )


def test_invalid_backend_name_is_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    secret_key_hex, agent_id = _relay_keypair()
    digest_hex = "a9" * 48
    signature_hex = sign_relay_bootstrap_record_digest(secret_key_hex, digest_hex)
    monkeypatch.setenv("ILC_BLS_BACKEND", "unknown")

    with pytest.raises(ValueError, match="bls_backend_invalid"):
        verify_relay_bootstrap_record_digest(
            public_key_hex=agent_id,
            digest_hex=digest_hex,
            signature_hex=signature_hex,
        )
