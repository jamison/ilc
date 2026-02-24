"""Phase 285 regression tests for dual-verify cutoff behavior."""

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
from ilc_core.ledger.canon_bundle_key_registry_channel_signing import (
    sign_channel_file,
    verify_channel_file_signature,
)
from ilc_core.ledger.canon_export_bundle import write_canon_export_bundle
from ilc_core.ledger.canon_export_bundle_sign import sign_manifest
from ilc_core.ledger.canon_export_bundle_verify_sig import verify_manifest_signature


@pytest.fixture(autouse=True)
def _allow_empty_key_registry(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ILC_ALLOW_EMPTY_KEY_REGISTRY", "1")


def _rewrite_manifest_and_resign(bundle_dir: Path, key: bytes, mutate_fn) -> None:
    manifest_path = bundle_dir / "manifest.json"
    sig_path = bundle_dir / "manifest.sig"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    mutate_fn(manifest)
    manifest_bytes = json.dumps(manifest, separators=(",", ":"), sort_keys=False).encode("utf-8")
    manifest_path.write_bytes(manifest_bytes)
    sig = hmac.new(key, manifest_bytes, hashlib.sha256).digest()
    sig_path.write_bytes(base64.b64encode(sig) + b"\n")


def test_bundle_mode_switch_enforces_fingerprint_presence() -> None:
    key = b"secret_key"

    from tempfile import TemporaryDirectory

    with TemporaryDirectory() as tmp:
        bundle = Path(tmp) / "bundle"
        write_canon_export_bundle({"canon_hash": "abc"}, {"ok": True}, bundle)
        sign_manifest(bundle, key)

        _rewrite_manifest_and_resign(bundle, key, lambda m: m.pop("key_fingerprint", None))

        assert verify_manifest_signature(bundle, key, mode="compatibility") is True
        assert verify_manifest_signature(bundle, key, mode="asymmetric_required") is False


def test_bundle_invalid_mode_rejected() -> None:
    key = b"secret_key"

    from tempfile import TemporaryDirectory

    with TemporaryDirectory() as tmp:
        bundle = Path(tmp) / "bundle"
        write_canon_export_bundle({"canon_hash": "abc"}, {"ok": True}, bundle)
        sign_manifest(bundle, key)

        assert verify_manifest_signature(bundle, key, mode="unsupported") is False


def test_registry_mode_switch_enforces_fingerprint_presence(tmp_path: Path) -> None:
    key = b"registry-key"
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

    compat = verify_registry_file_signature(registry_path, key, mode="compatibility")
    cutoff = verify_registry_file_signature(registry_path, key, mode="asymmetric_required")

    assert compat["ok"] is True
    assert cutoff["ok"] is False
    assert "signature_missing_fingerprint" in cutoff["errors"]


def test_registry_invalid_mode_rejected(tmp_path: Path) -> None:
    key = b"registry-key"
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

    sign_registry_file(registry_path, key)
    invalid = verify_registry_file_signature(registry_path, key, mode="asymmetric-required")
    assert invalid["ok"] is False
    assert "signature_invalid_mode" in invalid["errors"]


def test_channel_mode_switch_enforces_fingerprint_presence(tmp_path: Path) -> None:
    key = b"channel-key"
    channel_path = tmp_path / "channel.json"
    channel_path.write_text(
        json.dumps(
            {
                "channel_version": "v0.3",
                "updated_at": "2026-02-24T00:00:00Z",
                "current_channel": "main",
                "channels": ["main"],
                "sources": {"main": ["https://example.com"]},
            }
        ),
        encoding="utf-8",
    )

    sign_channel_file(channel_path, key)
    sig_path = channel_path.with_suffix(channel_path.suffix + ".sig")
    sig_data = json.loads(sig_path.read_text(encoding="utf-8"))
    sig_data.pop("key_fingerprint", None)
    sig_path.write_text(json.dumps(sig_data), encoding="utf-8")

    compat = verify_channel_file_signature(channel_path, key, mode="compatibility")
    cutoff = verify_channel_file_signature(channel_path, key, mode="asymmetric_required")

    assert compat["ok"] is True
    assert cutoff["ok"] is False
    assert "channel_signature_missing_fingerprint" in cutoff["errors"]


def test_channel_invalid_mode_rejected(tmp_path: Path) -> None:
    key = b"channel-key"
    channel_path = tmp_path / "channel.json"
    channel_path.write_text(
        json.dumps(
            {
                "channel_version": "v0.3",
                "updated_at": "2026-02-24T00:00:00Z",
                "current_channel": "main",
                "channels": ["main"],
                "sources": {"main": ["https://example.com"]},
            }
        ),
        encoding="utf-8",
    )

    sign_channel_file(channel_path, key)
    invalid = verify_channel_file_signature(channel_path, key, mode="asymmetric-required")
    assert invalid["ok"] is False
    assert "channel_signature_invalid_mode" in invalid["errors"]


def test_rollback_to_compatibility_is_explicit_behavior(tmp_path: Path) -> None:
    key = b"registry-key"
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

    cutoff = verify_registry_file_signature(registry_path, key, mode="asymmetric_required")
    rollback = verify_registry_file_signature(registry_path, key, mode="compatibility")

    assert cutoff["ok"] is False
    assert rollback["ok"] is True
