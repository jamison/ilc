"""Phase 284 regression tests for bundle/registry fingerprint hardening."""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
from pathlib import Path

import pytest

from ilc_core.ledger.canon_bundle_key_registry import (
    sign_registry_file,
    verify_registry_file_signature,
)
from ilc_core.ledger.canon_export_bundle import write_canon_export_bundle
from ilc_core.ledger.canon_export_bundle_sign import sign_manifest
from ilc_core.ledger.canon_export_bundle_verify_sig import verify_manifest_signature


@pytest.fixture(autouse=True)
def _allow_empty_key_registry(monkeypatch: pytest.MonkeyPatch) -> None:
    """Allow empty key registry to isolate fingerprint compatibility behavior."""
    monkeypatch.setenv("ILC_ALLOW_EMPTY_KEY_REGISTRY", "1")


def test_bundle_signing_emits_key_fingerprint(tmp_path: Path) -> None:
    bundle = tmp_path / "bundle"
    write_canon_export_bundle({"canon_hash": "abc"}, {"ok": True}, bundle)

    sign_manifest(bundle, b"secret_key")

    manifest = json.loads((bundle / "manifest.json").read_text(encoding="utf-8"))
    assert "key_fingerprint" in manifest
    assert len(manifest["key_fingerprint"]) == 64


def test_bundle_verification_fails_on_fingerprint_mismatch(tmp_path: Path) -> None:
    key = b"secret_key"
    bundle = tmp_path / "bundle"
    write_canon_export_bundle({"canon_hash": "abc"}, {"ok": True}, bundle)
    sign_manifest(bundle, key)

    manifest_path = bundle / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["key_fingerprint"] = "f" * 64
    manifest_path.write_text(json.dumps(manifest, separators=(",", ":"), sort_keys=False), encoding="utf-8")

    assert verify_manifest_signature(bundle, key) is False


def test_bundle_legacy_manifest_without_fingerprint_still_verifies(tmp_path: Path) -> None:
    key = b"secret_key"
    bundle = tmp_path / "bundle"
    write_canon_export_bundle({"canon_hash": "abc"}, {"ok": True}, bundle)
    sign_manifest(bundle, key)

    manifest_path = bundle / "manifest.json"
    sig_path = bundle / "manifest.sig"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest.pop("key_fingerprint", None)
    manifest_bytes = json.dumps(manifest, separators=(",", ":"), sort_keys=False).encode("utf-8")
    manifest_path.write_bytes(manifest_bytes)
    sig = hmac.new(key, manifest_bytes, hashlib.sha256).digest()
    sig_path.write_bytes(base64.b64encode(sig) + b"\n")

    assert verify_manifest_signature(bundle, key) is True


def test_registry_signing_emits_key_fingerprint(tmp_path: Path) -> None:
    registry_path = tmp_path / "registry.json"
    registry_path.write_text(
        json.dumps(
            {
                "registry_version": "v0.1",
                "updated_at": "2026-02-24T00:00:00Z",
                "current_keys": ["a1b2c3d4e5f6a7b8"],
                "previous_keys": [],
                "deprecated_keys": [],
            }
        ),
        encoding="utf-8",
    )

    result = sign_registry_file(registry_path, b"phase-284-registry-key")
    assert result["ok"] is True

    sig_data = json.loads(Path(result["sig_path"]).read_text(encoding="utf-8"))
    assert "key_fingerprint" in sig_data
    assert len(sig_data["key_fingerprint"]) == 64


def test_registry_verification_fails_on_fingerprint_mismatch(tmp_path: Path) -> None:
    key = b"phase-284-registry-key"
    registry_path = tmp_path / "registry.json"
    registry_path.write_text(
        json.dumps(
            {
                "registry_version": "v0.1",
                "updated_at": "2026-02-24T00:00:00Z",
                "current_keys": ["a1b2c3d4e5f6a7b8"],
                "previous_keys": [],
                "deprecated_keys": [],
            }
        ),
        encoding="utf-8",
    )

    result = sign_registry_file(registry_path, key)
    sig_path = Path(result["sig_path"])
    sig_data = json.loads(sig_path.read_text(encoding="utf-8"))
    sig_data["key_fingerprint"] = "f" * 64
    sig_path.write_text(json.dumps(sig_data), encoding="utf-8")

    verify = verify_registry_file_signature(registry_path, key)
    assert verify["ok"] is False
    assert "signature_fingerprint_mismatch" in verify["errors"]


def test_registry_legacy_sidecar_without_fingerprint_still_verifies(tmp_path: Path) -> None:
    key = b"phase-284-registry-key"
    registry_path = tmp_path / "registry.json"
    registry_path.write_text(
        json.dumps(
            {
                "registry_version": "v0.1",
                "updated_at": "2026-02-24T00:00:00Z",
                "current_keys": ["a1b2c3d4e5f6a7b8"],
                "previous_keys": [],
                "deprecated_keys": [],
            }
        ),
        encoding="utf-8",
    )

    result = sign_registry_file(registry_path, key)
    sig_path = Path(result["sig_path"])
    sig_data = json.loads(sig_path.read_text(encoding="utf-8"))
    sig_data.pop("key_fingerprint", None)
    sig_path.write_text(json.dumps(sig_data), encoding="utf-8")

    verify = verify_registry_file_signature(registry_path, key)
    assert verify["ok"] is True
