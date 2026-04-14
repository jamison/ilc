"""Tests for canon bundle key registry channel signing."""

import hashlib
import hmac
import json
import time
from datetime import datetime, timezone
import pytest
from ilc_core.ledger.canon_bundle_key_registry_channel_signing import (
    sign_channel_file,
    verify_channel_file_signature,
    canonical_channel_bytes,
)


class TestChannelSigning:
    
    @pytest.fixture
    def setup_channel(self, tmp_path):
        channel_file = tmp_path / "channel.json"
        data = {
            "channel_version": "v0.3",
            "updated_at": "2026-02-07T12:00:00Z",
            "current_channel": "main",
            "channels": ["main"],
            "sources": {"main": ["https://example.com"]},
        }
        channel_file.write_text(json.dumps(data, indent=2))
        key = b"test-signing-key"
        return channel_file, key

    def test_canonical_bytes_sorting(self, tmp_path):
        """Test canonical bytes are sorted and minimal."""
        f = tmp_path / "test.json"
        f.write_text('{"b": 1, "a": 2}')
        
        canonical = canonical_channel_bytes(f)
        assert canonical == b'{"a":2,"b":1}'

    def test_sign_verify_roundtrip_ok(self, setup_channel):
        """Sign and verify roundtrip succeeds."""
        channel_file, key = setup_channel
        
        # Sign
        res_sign = sign_channel_file(channel_file, key)
        assert res_sign["ok"] is True
        assert "sig_path" in res_sign
        
        # Verify
        res_verify = verify_channel_file_signature(channel_file, key)
        assert res_verify["ok"] is True
        assert res_verify["channel_hash"] == res_sign["channel_hash"]
        assert "key_fingerprint" in res_sign
        assert len(res_sign["key_fingerprint"]) == 64

    def test_sign_channel_file_explicit_timestamp_is_reproducible(self, setup_channel):
        channel_file, key = setup_channel
        signed_at = "2026-04-14T13:00:00Z"

        first = sign_channel_file(channel_file, key, signed_at=signed_at)
        assert first["ok"] is True
        sig_path = channel_file.with_suffix(channel_file.suffix + ".sig")
        sidecar_once = sig_path.read_text(encoding="utf-8")

        second = sign_channel_file(channel_file, key, signed_at=signed_at)
        assert second["ok"] is True
        sidecar_twice = sig_path.read_text(encoding="utf-8")

        assert sidecar_once == sidecar_twice

    def test_sign_channel_file_uses_updated_at_as_fallback(self, setup_channel):
        channel_file, key = setup_channel
        res = sign_channel_file(channel_file, key)
        assert res["ok"] is True
        sig_path = channel_file.with_suffix(channel_file.suffix + ".sig")
        sig_data = json.loads(sig_path.read_text(encoding="utf-8"))
        assert sig_data["signed_at"] == "2026-02-07T12:00:00Z"

    def test_sign_sidecar_includes_key_fingerprint(self, setup_channel):
        """Signed sidecar includes canonical key fingerprint field."""
        channel_file, key = setup_channel
        sign_channel_file(channel_file, key)

        sig_path = channel_file.with_suffix(channel_file.suffix + ".sig")
        sig_data = json.loads(sig_path.read_text())
        assert "key_fingerprint" in sig_data
        assert len(sig_data["key_fingerprint"]) == 64

    def test_verify_fails_on_channel_tamper(self, setup_channel):
        """Verify fails if channel file modified."""
        channel_file, key = setup_channel
        sign_channel_file(channel_file, key)
        
        # Tamper
        data = json.loads(channel_file.read_text())
        data["current_channel"] = "malicious"
        channel_file.write_text(json.dumps(data))
        
        res = verify_channel_file_signature(channel_file, key)
        assert res["ok"] is False
        assert "channel_hash_mismatch" in res["errors"]
        assert "channel_signature_mismatch" in res["errors"]

    def test_verify_fails_on_sidecar_tamper(self, setup_channel):
        """Verify fails if sidecar modified."""
        channel_file, key = setup_channel
        sign_channel_file(channel_file, key)
        
        sig_path = channel_file.with_suffix(channel_file.suffix + ".sig")
        sig_data = json.loads(sig_path.read_text())
        
        # Tamper hash
        sig_data["channel_hash"] = "a" * 64
        sig_path.write_text(json.dumps(sig_data))
        
        res = verify_channel_file_signature(channel_file, key)
        assert res["ok"] is False
        assert "channel_hash_mismatch" in res["errors"]

    def test_verify_missing_sidecar(self, setup_channel):
        """Verify fails if sidecar missing."""
        channel_file, key = setup_channel
        
        res = verify_channel_file_signature(channel_file, key)
        assert res["ok"] is False
        assert "channel_signature_missing" in res["errors"]

    def test_verify_bad_sig_alg(self, setup_channel):
        """Verify fails on unsupported alg."""
        channel_file, key = setup_channel
        sign_channel_file(channel_file, key)
        
        sig_path = channel_file.with_suffix(".json.sig")
        sig_data = json.loads(sig_path.read_text())
        sig_data["sig_alg"] = "md5"
        sig_path.write_text(json.dumps(sig_data))
        
        res = verify_channel_file_signature(channel_file, key)
        assert res["ok"] is False
        assert "channel_signature_unsupported_sig_alg" in res["errors"]

    def test_verify_bad_signed_at(self, setup_channel):
        """Verify fails on invalid timestamp format."""
        channel_file, key = setup_channel
        sign_channel_file(channel_file, key)
        
        sig_path = channel_file.with_suffix(".json.sig")
        sig_data = json.loads(sig_path.read_text())
        sig_data["signed_at"] = "2026/02/07"
        sig_path.write_text(json.dumps(sig_data))
        
        res = verify_channel_file_signature(channel_file, key)
        assert res["ok"] is False
        assert "channel_signature_invalid_signed_at" in res["errors"]

    def test_sign_channel_file_rejects_invalid_explicit_signed_at(self, setup_channel):
        channel_file, key = setup_channel
        res = sign_channel_file(channel_file, key, signed_at="2026-04-14 13:00:00")
        assert res["ok"] is False
        assert "channel_signature_invalid_signed_at" in res["errors"]

    def test_verify_fails_on_missing_required_fields(self, setup_channel):
        """Verify fails if fields missing."""
        channel_file, key = setup_channel
        sign_channel_file(channel_file, key)
        
        sig_path = channel_file.with_suffix(".json.sig")
        sig_data = json.loads(sig_path.read_text())
        del sig_data["signature_hex"]
        sig_path.write_text(json.dumps(sig_data))
        
        res = verify_channel_file_signature(channel_file, key)
        assert res["ok"] is False
        assert "channel_signature_missing_field:signature_hex" in res["errors"]

    def test_verify_fails_on_key_id_mismatch(self, setup_channel):
        """Verify fails if key ID doesn't match provided key."""
        channel_file, key = setup_channel
        sign_channel_file(channel_file, key)
        
        # Verify with different key
        other_key = b"other-key"
        res = verify_channel_file_signature(channel_file, other_key)
        
        assert res["ok"] is False
        assert "channel_signature_key_unknown" in res["errors"]
        # And signature mismatch likely too
        assert "channel_signature_mismatch" in res["errors"]

    def test_sign_does_not_modify_channel_on_failure(self, setup_channel):
        """Sign doesn't write sidecar if channel invalid."""
        channel_file, key = setup_channel
        
        # Make channel invalid
        channel_file.write_text("invalid json")
        
        res = sign_channel_file(channel_file, key)
        assert res["ok"] is False
        assert not (channel_file.with_suffix(".json.sig")).exists()

    def test_cli_sign_verify_flow(self, setup_channel, tmp_path):
        """Test sign and verify CLIs."""
        channel_file, key = setup_channel
        key_file = tmp_path / "key.txt"
        key_file.write_bytes(key)
        
        # Sign CLI
        import subprocess
        res_sign = subprocess.run(
            [
                "python3", "-m", "ilc_core.cli.canon_bundle_key_registry_channel_sign",
                "--channel-file", str(channel_file),
                "--key-file", str(key_file),
            ],
            capture_output=True,
            text=True,
            cwd="/Users/jamstar/Documents/ILC_Main/01_Current"
        )
        assert res_sign.returncode == 0
        out_sign = json.loads(res_sign.stdout)
        assert out_sign["ok"] is True
        
        # Verify CLI
        res_verify = subprocess.run(
            [
                "python3", "-m", "ilc_core.cli.canon_bundle_key_registry_channel_verify",
                "--channel-file", str(channel_file),
                "--key-file", str(key_file),
            ],
            capture_output=True,
            text=True,
            cwd="/Users/jamstar/Documents/ILC_Main/01_Current"
        )
        assert res_verify.returncode == 0
        out_verify = json.loads(res_verify.stdout)
        assert out_verify["ok"] is True
        
        # Verify CLI missing key
        res_missing = subprocess.run(
            [
                "python3", "-m", "ilc_core.cli.canon_bundle_key_registry_channel_verify",
                "--channel-file", str(channel_file),
                "--key-file", str(tmp_path / "missing"),
            ],
            capture_output=True,
            text=True,
            cwd="/Users/jamstar/Documents/ILC_Main/01_Current"
        )
        assert res_missing.returncode == 2
