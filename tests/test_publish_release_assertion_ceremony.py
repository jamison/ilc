from __future__ import annotations

import json
from pathlib import Path

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from ilc_core.identity.bls_backend import public_key_from_secret_key_hex
from ilc_core.release import upgrade_check
from tools import publish_release_assertion_ceremony as ceremony


def _receipt(path: Path) -> Path:
    payload = {
        "published_artifacts": {
            "sdist": {
                "filename": "ilc_core-0.4.32.tar.gz",
                "sha256": "17" * 32,
                "size": 123,
                "url": "https://example.invalid/ilc_core-0.4.32.tar.gz",
            },
            "wheel": {
                "filename": "ilc_core-0.4.32-py3-none-any.whl",
                "sha256": "f5" * 32,
                "size": 456,
                "url": "https://example.invalid/ilc_core-0.4.32-py3-none-any.whl",
            },
        },
        "release_id": "ilc-core-0.4.32",
        "source_private_commit_at_upload": "a" * 40,
    }
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def _ed25519_fixture() -> tuple[Ed25519PrivateKey, str]:
    key = Ed25519PrivateKey.from_private_bytes(bytes.fromhex("22" * 32))
    public = key.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    ).hex()
    return key, public


def _operator_signatures(signing_request: dict, *, private_key: Ed25519PrivateKey, public_hex: str) -> dict:
    return {
        "signer_public_key_hex": public_hex,
        "signatures": {
            row["artifact_id"]: private_key.sign(bytes.fromhex(row["signed_preimage_sha256"])).hex()
            for row in signing_request["signing_inputs"]
        },
    }


def test_prepare_writes_unsigned_skeleton_with_placeholders_without_key_presence(
    tmp_path: Path,
) -> None:
    request = ceremony.prepare_signing_request(
        package_receipt_path=_receipt(tmp_path / "receipt.json"),
        out_dir=tmp_path / "out",
        production_execute=True,
        confirm=True,
    )

    assert request["expected_signer_public_key_hex"] == ceremony.release_signer_public_key_hex()
    assert len(request["signing_inputs"]) == 2
    for envelope in request["unsigned_envelopes"].values():
        assert envelope["signature_hex"] == ""
        assert envelope["signer_public_key_hex"] == ""
    assert (tmp_path / "out" / "signing_request.json").exists()


def test_cli_prepare_writes_signing_request_without_key_path(tmp_path: Path) -> None:
    exit_code = ceremony.main(
        [
            "prepare",
            "--package-receipt",
            str(_receipt(tmp_path / "receipt.json")),
            "--out-dir",
            str(tmp_path / "out"),
            "--production-execute",
            "--confirm-release-assertion-publish-ceremony",
        ]
    )

    assert exit_code == 0
    assert (tmp_path / "out" / "signing_request.json").exists()


def test_finalize_rejects_operator_pubkey_mismatch(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    private_key, public_hex = _ed25519_fixture()
    monkeypatch.setattr(ceremony, "EXPECTED_RELEASE_SIGNER_PUBLIC_KEY_HEX", public_hex)
    monkeypatch.setattr(ceremony, "release_signer_public_key_hex", lambda: public_hex)
    request = ceremony.prepare_signing_request(
        package_receipt_path=_receipt(tmp_path / "receipt.json"),
        out_dir=tmp_path / "out",
        production_execute=True,
        confirm=True,
    )
    signatures = _operator_signatures(request, private_key=private_key, public_hex="33" * 32)
    sig_path = tmp_path / "operator_signatures.json"
    sig_path.write_text(json.dumps(signatures), encoding="utf-8")

    with pytest.raises(ceremony.ReleaseAssertionCeremonyError) as excinfo:
        ceremony._load_operator_signatures(sig_path)

    assert excinfo.value.token == "operator_signature_embedded_pubkey_mismatch"


def test_finalize_builds_valid_assertion_and_well_known_without_stub_signatures(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    private_key, public_hex = _ed25519_fixture()
    bls_secret = "11" * 32
    bls_public = public_key_from_secret_key_hex(bls_secret)
    monkeypatch.setattr(ceremony, "EXPECTED_RELEASE_SIGNER_PUBLIC_KEY_HEX", public_hex)
    monkeypatch.setattr(ceremony, "release_signer_public_key_hex", lambda: public_hex)
    monkeypatch.setattr(upgrade_check, "release_signer_public_key_hex", lambda: public_hex)
    monkeypatch.setattr(ceremony, "GENESIS_PUBLIC_SUBMIT_INGRESS_BLS_PK_HEX", bls_public)
    monkeypatch.setattr(
        ceremony,
        "_run_client",
        lambda **_: {
            "argv": ["ilc_native_submit_client"],
            "exit_code": 0,
            "response": {"ok": True, "node_id": "bafyreibbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb", "receiver_profile": "native_quic_full_rust"},
            "stderr": "",
            "stdout": '{"ok":true}',
        },
    )
    receipt_path = _receipt(tmp_path / "receipt.json")
    request = ceremony.prepare_signing_request(
        package_receipt_path=receipt_path,
        out_dir=tmp_path / "out",
        production_execute=True,
        confirm=True,
    )
    sig_path = tmp_path / "operator_signatures.json"
    sig_path.write_text(
        json.dumps(_operator_signatures(request, private_key=private_key, public_hex=public_hex)),
        encoding="utf-8",
    )
    receiver_path = tmp_path / "receiver.json"
    receiver_path.write_text(
        json.dumps(
            {
                "bridge_permanent": False,
                "endpoint": "quic://127.0.0.1:52080",
                "tls_fingerprint_sha256_der": "aa" * 32,
                "transport_profile": "native_quic_full_rust",
            }
        ),
        encoding="utf-8",
    )
    bls_path = tmp_path / "bls.hex"
    bls_path.write_text(bls_secret + "\n", encoding="utf-8")
    bls_path.chmod(0o600)
    well_known = tmp_path / "www/.well-known/ilc/software-release/latest.json"

    exit_code = ceremony.main(
        [
            "assemble",
            "--signing-request",
            str(tmp_path / "out/signing_request.json"),
            "--operator-signatures",
            str(sig_path),
            "--package-receipt",
            str(receipt_path),
            "--receiver-evidence",
            str(receiver_path),
            "--public-submit-secret",
            str(bls_path),
            "--out-dir",
            str(tmp_path / "out"),
            "--nginx-well-known-path",
            str(well_known),
            "--production-execute",
            "--confirm-release-assertion-publish-ceremony",
        ]
    )
    assert exit_code == 0

    assembled_payload = json.loads((tmp_path / "out/release_assertion_core.json").read_text(encoding="utf-8"))
    assembled_result = upgrade_check.validate_release_assertion(assembled_payload)
    assert assembled_result["release_signature_verified"] is True
    evidence = json.loads((tmp_path / "out/publish_evidence.json").read_text(encoding="utf-8"))

    assert evidence["tokens"] == [
        "release_assertion_publish_ceremony_complete_GAP_RELEASE_ASSERTION_PUBLISH_CEREMONY_00"
    ]
    payload = json.loads(well_known.read_text(encoding="utf-8"))
    assert all(
        edge["signature_hex"] and edge["signer_public_key_hex"] == public_hex
        for edge in payload["release_attestation_edges"]
    )
    result = upgrade_check.validate_release_assertion(payload)
    assert result["release_signature_verified"] is True
    assert result["verified_attestation_count"] == 2


def test_publish_can_defer_https_mirror_under_cdl_121(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    private_key, public_hex = _ed25519_fixture()
    bls_secret = "11" * 32
    bls_public = public_key_from_secret_key_hex(bls_secret)
    monkeypatch.setattr(ceremony, "EXPECTED_RELEASE_SIGNER_PUBLIC_KEY_HEX", public_hex)
    monkeypatch.setattr(ceremony, "release_signer_public_key_hex", lambda: public_hex)
    monkeypatch.setattr(upgrade_check, "release_signer_public_key_hex", lambda: public_hex)
    monkeypatch.setattr(ceremony, "GENESIS_PUBLIC_SUBMIT_INGRESS_BLS_PK_HEX", bls_public)
    monkeypatch.setattr(
        ceremony,
        "_run_client",
        lambda **_: {
            "argv": ["ilc_native_submit_client"],
            "exit_code": 0,
            "response": {
                "ok": True,
                "node_id": "bafyreibbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
                "receiver_profile": "native_quic_full_rust",
            },
            "stderr": "",
            "stdout": '{"ok":true}',
        },
    )
    receipt_path = _receipt(tmp_path / "receipt.json")
    request = ceremony.prepare_signing_request(
        package_receipt_path=receipt_path,
        out_dir=tmp_path / "out",
        production_execute=True,
        confirm=True,
    )
    sig_path = tmp_path / "operator_signatures.json"
    sig_path.write_text(
        json.dumps(_operator_signatures(request, private_key=private_key, public_hex=public_hex)),
        encoding="utf-8",
    )
    assembly = ceremony.assemble_signed_assertion(
        signing_request_path=tmp_path / "out/signing_request.json",
        operator_signatures_path=sig_path,
        package_receipt_path=receipt_path,
        out_dir=tmp_path / "out",
        production_execute=True,
        confirm=True,
    )
    receiver_path = tmp_path / "receiver.json"
    receiver_path.write_text(
        json.dumps(
            {
                "bridge_permanent": False,
                "endpoint": "quic://127.0.0.1:52080",
                "tls_fingerprint_sha256_der": "aa" * 32,
                "transport_profile": "native_quic_full_rust",
            }
        ),
        encoding="utf-8",
    )
    bls_path = tmp_path / "bls.hex"
    bls_path.write_text(bls_secret + "\n", encoding="utf-8")
    bls_path.chmod(0o600)

    evidence = ceremony.publish_assembled_assertion(
        assertion_core_path=Path(str(assembly["release_assertion_core_path"])),
        receiver_evidence_path=receiver_path,
        public_submit_secret_path=bls_path,
        out_dir=tmp_path / "out",
        nginx_well_known_path=None,
        epoch=1,
        production_execute=True,
        confirm=True,
    )

    assert evidence["https_well_known_endpoint"]["disposition"] == "deferred_mirror"
    assert evidence["nginx_well_known_path"] is None
    assert evidence["post_write_validation_result"]["release_signature_verified"] is True
    assert (tmp_path / "out/well_known_latest.json").is_file()
