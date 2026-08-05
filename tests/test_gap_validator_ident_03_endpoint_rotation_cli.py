# SPDX-License-Identifier: AGPL-3.0-only
"""GAP-VALIDATOR-IDENT-03 endpoint assertion rotation CLI tests."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID

from ilc_core.consensus.validator_endpoint_assertion import (
    VALIDATOR_ENDPOINT_ASSERTION_NODE_KIND,
    VALIDATOR_ENDPOINT_ASSERTION_SCHEMA_VERSION,
    ValidatorEndpointAssertion,
    assertion_content_sha256,
    assertion_is_superseded,
    validator_assertion_candidate_id,
)
from ilc_core.validator import endpoint_rotation_runtime
from ilc_core.validator.endpoint_rotation_runtime import (
    atomic_write_json,
    rotate_validator_endpoint_assertion,
)


AGENT = "a" * 96
BLS_KEY = "b" * 96
SIGNATURE = "c" * 192
FINGERPRINT = hashlib.sha256(b"validator-cert").hexdigest()


class EdgeAtlas:
    def __init__(self, edges: list[dict[str, object]]) -> None:
        self.edges = edges

    def iter_edges(self) -> list[dict[str, object]]:
        return self.edges


def _run_cli(*args: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "ilc_core.cli", *args],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
        timeout=30,
        cwd=cwd,
    )


def _old_assertion(**overrides: object) -> ValidatorEndpointAssertion:
    payload = {
        "asserted_at_epoch": 0,
        "bls_public_key_hex": BLS_KEY,
        "bls_signature_hex": SIGNATURE,
        "genesis_witness": True,
        "grpc_endpoint": "old-validator.example:7101",
        "node_kind": VALIDATOR_ENDPOINT_ASSERTION_NODE_KIND,
        "schema_version": VALIDATOR_ENDPOINT_ASSERTION_SCHEMA_VERSION,
        "tls_cert_not_after_utc": "2030-01-01T00:00:00Z",
        "tls_cert_not_before_utc": "2026-01-01T00:00:00Z",
        "tls_cert_sha256_fingerprint": FINGERPRINT,
        "validator_agent_id": AGENT,
        "revised_by": None,
    }
    payload.update(overrides)
    return ValidatorEndpointAssertion(**payload)


def _write_old_assertion(tmp_path: Path, assertion: ValidatorEndpointAssertion | None = None) -> Path:
    path = tmp_path / "old_assertion.json"
    path.write_text(
        json.dumps((assertion or _old_assertion()).to_dict(include_graph_metadata=False), sort_keys=True)
        + "\n",
        encoding="utf-8",
    )
    return path


def _write_key(tmp_path: Path, *, chmod: int = 0o600) -> Path:
    path = tmp_path / "validator_bls_secret.hex"
    path.write_text("1" * 64 + "\n", encoding="utf-8")
    path.chmod(chmod)
    return path


def _write_test_cert(tmp_path: Path, *, not_before: datetime, not_after: datetime) -> Path:
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    subject = issuer = x509.Name(
        [x509.NameAttribute(NameOID.COMMON_NAME, "validator-rotation.example")]
    )
    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(not_before)
        .not_valid_after(not_after)
        .sign(key, hashes.SHA256())
    )
    path = tmp_path / "validator-cert.pem"
    path.write_bytes(cert.public_bytes(serialization.Encoding.PEM))
    return path


def test_rotate_endpoint_help_discoverable() -> None:
    result = _run_cli("validator", "rotate-endpoint", "--help")
    assert result.returncode == 0
    assert "--old-assertion" in result.stdout
    assert "--new-endpoint" in result.stdout
    assert "--allow-test-stub-signature" in result.stdout


def test_rotate_endpoint_missing_old_assertion_exits_error() -> None:
    result = _run_cli("validator", "rotate-endpoint")
    assert result.returncode == 2
    assert "old-assertion" in result.stderr


def test_rotate_endpoint_invalid_old_assertion_json_exits_error(tmp_path: Path) -> None:
    bad = tmp_path / "bad.json"
    bad.write_text("{not json", encoding="utf-8")
    key = _write_key(tmp_path)
    result = _run_cli(
        "validator",
        "rotate-endpoint",
        "--old-assertion",
        str(bad),
        "--new-endpoint",
        "new-validator.example:7101",
        "--network-id",
        "ilc-rc01",
        "--key",
        str(key),
        "--output",
        str(tmp_path / "new.json"),
        "--allow-test-stub-signature",
    )
    assert result.returncode == 1
    assert "validator_endpoint_rotation_old_assertion_invalid_json" in result.stderr


def test_rotate_endpoint_generates_new_assertion_and_separate_revised_by_edge(tmp_path: Path) -> None:
    old_path = _write_old_assertion(tmp_path)
    key = _write_key(tmp_path)
    result = rotate_validator_endpoint_assertion(
        old_assertion_path=old_path,
        new_endpoint="new-validator.example:7101",
        network_id="ilc-rc01",
        key_path=key,
        output_path=tmp_path / "new.json",
        allow_test_stub_signature=True,
    )
    new_assertion = ValidatorEndpointAssertion.from_dict(result["new_assertion"])
    assert new_assertion.revised_by is None
    edge = result["revised_by_edge"]
    assert edge["edge_type"] == "revised_by"
    assert edge["source_assertion_sha256"] == assertion_content_sha256(_old_assertion())
    assert edge["target_assertion_sha256"] == assertion_content_sha256(new_assertion)
    assert assertion_is_superseded(EdgeAtlas([edge]), _old_assertion()) is True
    assert assertion_is_superseded(EdgeAtlas([edge]), new_assertion) is False


def test_rotate_endpoint_new_assertion_has_new_endpoint(tmp_path: Path) -> None:
    old_path = _write_old_assertion(tmp_path)
    key = _write_key(tmp_path)
    result = rotate_validator_endpoint_assertion(
        old_assertion_path=old_path,
        new_endpoint="new-validator.example:50151",
        network_id="ilc-rc01",
        key_path=key,
        output_path=tmp_path / "new.json",
        allow_test_stub_signature=True,
    )
    assert result["new_assertion"]["grpc_endpoint"] == "new-validator.example:50151"
    assert result["old_endpoint"] == "old-validator.example:7101"


def test_rotate_endpoint_reports_pre_rotation_old_file_hash(tmp_path: Path) -> None:
    old_path = _write_old_assertion(tmp_path)
    before_bytes = old_path.read_bytes()
    before_hash = hashlib.sha256(old_path.read_bytes()).hexdigest()

    result = rotate_validator_endpoint_assertion(
        old_assertion_path=old_path,
        new_endpoint="new-validator.example:50151",
        network_id="ilc-rc01",
        key_path=_write_key(tmp_path),
        output_path=tmp_path / "new.json",
        allow_test_stub_signature=True,
    )

    assert result["old_file_sha256_before_rotation"] == before_hash
    assert old_path.read_bytes() == before_bytes


def test_rotate_endpoint_output_is_atomic_write(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[tuple[str, str]] = []

    def fake_replace(src: str, dst: str) -> None:
        calls.append((src, dst))
        os.rename(src, dst)

    monkeypatch.setattr(os, "replace", fake_replace)
    output = tmp_path / "atomic.json"
    atomic_write_json(output, {"phase": "GAP-VALIDATOR-IDENT-03"})
    assert calls
    assert json.loads(output.read_text(encoding="utf-8"))["phase"] == "GAP-VALIDATOR-IDENT-03"


def test_rotate_endpoint_output_json_has_required_fields(tmp_path: Path) -> None:
    old_path = _write_old_assertion(tmp_path)
    key = _write_key(tmp_path)
    output = tmp_path / "new_assertion.json"
    result = _run_cli(
        "validator",
        "rotate-endpoint",
        "--old-assertion",
        str(old_path),
        "--new-endpoint",
        "new-validator.example:7101",
        "--network-id",
        "ilc-rc01",
        "--key",
        str(key),
        "--output",
        str(output),
        "--allow-test-stub-signature",
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    data = payload["data"]
    assert data["old_assertion_id"]
    assert data["new_assertion_id"]
    assert data["revised_by_edge"]["edge_type"] == "revised_by"
    assert output.is_file()
    ValidatorEndpointAssertion.from_dict(json.loads(output.read_text(encoding="utf-8")))


def test_rotate_endpoint_default_output_path_is_under_cwd(tmp_path: Path) -> None:
    old_path = _write_old_assertion(tmp_path)
    key = _write_key(tmp_path)
    result = _run_cli(
        "validator",
        "rotate-endpoint",
        "--old-assertion",
        str(old_path),
        "--new-endpoint",
        "new-validator.example:7101",
        "--network-id",
        "ilc-rc01",
        "--key",
        str(key),
        "--allow-test-stub-signature",
        cwd=tmp_path,
    )

    assert result.returncode == 0, result.stderr
    assert (tmp_path / "out" / "validator_endpoint_rotation" / "new_assertion.json").is_file()


def test_rotate_endpoint_old_assertion_not_modified(tmp_path: Path) -> None:
    old_path = _write_old_assertion(tmp_path)
    before = old_path.read_bytes()
    rotate_validator_endpoint_assertion(
        old_assertion_path=old_path,
        new_endpoint="new-validator.example:7101",
        network_id="ilc-rc01",
        key_path=_write_key(tmp_path),
        output_path=tmp_path / "new.json",
        allow_test_stub_signature=True,
    )
    assert old_path.read_bytes() == before


def test_rotate_endpoint_rejects_same_endpoint_when_content_unchanged(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    old_path = _write_old_assertion(tmp_path)
    monkeypatch.setattr(
        endpoint_rotation_runtime,
        "_sign_assertion_payload",
        lambda **_kwargs: (SIGNATURE, "test_stub_not_production_valid"),
    )

    with pytest.raises(ValueError, match="validator_endpoint_rotation_no_content_change"):
        rotate_validator_endpoint_assertion(
            old_assertion_path=old_path,
            new_endpoint="old-validator.example:7101",
            network_id="ilc-rc01",
            key_path=_write_key(tmp_path),
            output_path=tmp_path / "new.json",
            allow_test_stub_signature=True,
        )


def test_rotate_endpoint_rejects_output_equal_to_old_assertion(tmp_path: Path) -> None:
    old_path = _write_old_assertion(tmp_path)
    with pytest.raises(ValueError, match="validator_endpoint_rotation_output_must_not_equal_old_assertion"):
        rotate_validator_endpoint_assertion(
            old_assertion_path=old_path,
            new_endpoint="new-validator.example:7101",
            network_id="ilc-rc01",
            key_path=_write_key(tmp_path),
            output_path=old_path,
            allow_test_stub_signature=True,
        )


def test_rotate_endpoint_rejects_too_open_key_permissions(tmp_path: Path) -> None:
    old_path = _write_old_assertion(tmp_path)
    with pytest.raises(ValueError, match="validator_endpoint_rotation_key_permissions_too_open"):
        rotate_validator_endpoint_assertion(
            old_assertion_path=old_path,
            new_endpoint="new-validator.example:7101",
            network_id="ilc-rc01",
            key_path=_write_key(tmp_path, chmod=0o644),
            output_path=tmp_path / "new.json",
            allow_test_stub_signature=True,
        )


def test_rotate_endpoint_rejects_malformed_key_hex(tmp_path: Path) -> None:
    old_path = _write_old_assertion(tmp_path)
    key = tmp_path / "validator_bls_secret.hex"
    key.write_text("not-hex\n", encoding="utf-8")
    key.chmod(0o600)
    with pytest.raises(ValueError, match="validator_endpoint_rotation_key_invalid"):
        rotate_validator_endpoint_assertion(
            old_assertion_path=old_path,
            new_endpoint="new-validator.example:7101",
            network_id="ilc-rc01",
            key_path=key,
            output_path=tmp_path / "new.json",
            allow_test_stub_signature=True,
        )


def test_rotate_endpoint_rejects_old_inline_superseded_assertion(tmp_path: Path) -> None:
    assertion = _old_assertion(revised_by="already-superseded")
    old_path = tmp_path / "old_assertion.json"
    old_path.write_text(
        json.dumps(assertion.to_dict(include_graph_metadata=True), sort_keys=True) + "\n",
        encoding="utf-8",
    )
    with pytest.raises(
        ValueError,
        match="validator_endpoint_rotation_old_assertion_already_inline_superseded",
    ):
        rotate_validator_endpoint_assertion(
            old_assertion_path=old_path,
            new_endpoint="new-validator.example:7101",
            network_id="ilc-rc01",
            key_path=_write_key(tmp_path),
            output_path=tmp_path / "new.json",
            allow_test_stub_signature=True,
        )


def test_rotate_endpoint_rejects_invalid_new_endpoint(tmp_path: Path) -> None:
    old_path = _write_old_assertion(tmp_path)
    with pytest.raises(ValueError, match="validator_endpoint_rotation_new_endpoint_invalid"):
        rotate_validator_endpoint_assertion(
            old_assertion_path=old_path,
            new_endpoint="https://new-validator.example:7101",
            network_id="ilc-rc01",
            key_path=_write_key(tmp_path),
            output_path=tmp_path / "new.json",
            allow_test_stub_signature=True,
        )


def test_rotate_endpoint_preserves_candidate_id_for_same_validator(tmp_path: Path) -> None:
    old_path = _write_old_assertion(tmp_path)
    result = rotate_validator_endpoint_assertion(
        old_assertion_path=old_path,
        new_endpoint="new-validator.example:7101",
        network_id="ilc-rc01",
        key_path=_write_key(tmp_path),
        output_path=tmp_path / "new.json",
        allow_test_stub_signature=True,
    )
    expected = validator_assertion_candidate_id(AGENT)
    assert result["old_candidate_id"] == expected
    assert result["new_candidate_id"] == expected


def test_rotate_endpoint_rejects_expired_tls_cert(tmp_path: Path) -> None:
    old_path = _write_old_assertion(tmp_path)
    now = datetime.now(timezone.utc)
    expired = _write_test_cert(
        tmp_path,
        not_before=now - timedelta(days=30),
        not_after=now - timedelta(days=1),
    )
    with pytest.raises(ValueError, match="validator_endpoint_rotation_tls_cert_expired"):
        rotate_validator_endpoint_assertion(
            old_assertion_path=old_path,
            new_endpoint="new-validator.example:7101",
            network_id="ilc-rc01",
            key_path=_write_key(tmp_path),
            output_path=tmp_path / "new.json",
            tls_cert_path=expired,
            allow_test_stub_signature=True,
        )


def test_rotate_endpoint_rejects_preserved_expired_cert_metadata(tmp_path: Path) -> None:
    old_path = _write_old_assertion(
        tmp_path,
        _old_assertion(
            tls_cert_not_before_utc="2020-01-01T00:00:00Z",
            tls_cert_not_after_utc="2021-01-01T00:00:00Z",
        ),
    )
    with pytest.raises(ValueError, match="validator_cert_assertion_expired"):
        rotate_validator_endpoint_assertion(
            old_assertion_path=old_path,
            new_endpoint="new-validator.example:7101",
            network_id="ilc-rc01",
            key_path=_write_key(tmp_path),
            output_path=tmp_path / "new.json",
            allow_test_stub_signature=True,
        )


def test_rotate_endpoint_rejects_not_yet_valid_tls_cert(tmp_path: Path) -> None:
    old_path = _write_old_assertion(tmp_path)
    now = datetime.now(timezone.utc)
    future = _write_test_cert(
        tmp_path,
        not_before=now + timedelta(days=1),
        not_after=now + timedelta(days=30),
    )
    with pytest.raises(ValueError, match="validator_endpoint_rotation_tls_cert_not_yet_valid"):
        rotate_validator_endpoint_assertion(
            old_assertion_path=old_path,
            new_endpoint="new-validator.example:7101",
            network_id="ilc-rc01",
            key_path=_write_key(tmp_path),
            output_path=tmp_path / "new.json",
            tls_cert_path=future,
            allow_test_stub_signature=True,
        )
