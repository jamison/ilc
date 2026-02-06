"""Tests for canon bundle key registry signing and verification."""

import json
import pytest
from pathlib import Path

from ilc_core.ledger.canon_bundle_key_registry import (
    canonical_registry_bytes,
    sign_registry_file,
    verify_registry_file_signature,
)


class TestRegistrySigningVerification:
    
    @pytest.fixture
    def test_key(self):
        return b"test-signing-key-for-registry"
    
    @pytest.fixture
    def valid_registry(self, tmp_path):
        path = tmp_path / "registry.json"
        data = {
            "registry_version": "v0.1",
            "updated_at": "2026-02-06T21:30:00Z",
            "current_keys": ["a1b2c3d4e5f6a7b8"],
            "previous_keys": [],
            "deprecated_keys": [],
        }
        path.write_text(json.dumps(data), encoding="utf-8")
        return path
    
    def test_canonical_bytes_deterministic(self, valid_registry):
        """Canonical bytes are deterministic regardless of key order."""
        bytes1 = canonical_registry_bytes(valid_registry)
        bytes2 = canonical_registry_bytes(valid_registry)
        assert bytes1 == bytes2
    
    def test_canonical_bytes_sorted_keys(self, tmp_path):
        """Canonical bytes have sorted keys."""
        path = tmp_path / "registry.json"
        data = {
            "z_field": "last",
            "a_field": "first",
            "registry_version": "v0.1",
        }
        path.write_text(json.dumps(data), encoding="utf-8")
        canonical = canonical_registry_bytes(path)
        parsed = json.loads(canonical)
        keys = list(parsed.keys())
        assert keys == sorted(keys)
    
    def test_sign_creates_sig_file(self, valid_registry, test_key):
        """Signing creates a .sig file."""
        result = sign_registry_file(valid_registry, test_key)
        assert result["ok"]
        sig_path = Path(result["sig_path"])
        assert sig_path.exists()
        sig_data = json.loads(sig_path.read_text())
        assert sig_data["sig_alg"] == "hmac-sha256"
        assert "signature_hex" in sig_data
        assert "registry_hash" in sig_data
    
    def test_sign_and_verify_success(self, valid_registry, test_key):
        """Signed registry verifies successfully with correct key."""
        sign_result = sign_registry_file(valid_registry, test_key)
        assert sign_result["ok"]
        
        verify_result = verify_registry_file_signature(valid_registry, test_key)
        assert verify_result["ok"]
        assert verify_result["errors"] == []
    
    def test_verify_wrong_key_fails(self, valid_registry, test_key):
        """Verification fails with wrong key."""
        sign_registry_file(valid_registry, test_key)
        
        wrong_key = b"wrong-key-for-verification"
        verify_result = verify_registry_file_signature(valid_registry, wrong_key)
        assert not verify_result["ok"]
        assert any("signature_mismatch" in e for e in verify_result["errors"])
        assert "signature_key_unknown" in verify_result["errors"]
    
    def test_verify_missing_sig_fails(self, valid_registry, test_key):
        """Verification fails when signature file is missing."""
        verify_result = verify_registry_file_signature(valid_registry, test_key)
        assert not verify_result["ok"]
        assert "signature_missing" in verify_result["errors"]
    
    def test_verify_tampered_registry_fails(self, valid_registry, test_key):
        """Verification fails when registry is tampered after signing."""
        sign_registry_file(valid_registry, test_key)
        
        # Tamper with registry
        data = json.loads(valid_registry.read_text())
        data["current_keys"].append("0000111122223333")
        valid_registry.write_text(json.dumps(data))
        
        verify_result = verify_registry_file_signature(valid_registry, test_key)
        assert not verify_result["ok"]
        assert any("mismatch" in e for e in verify_result["errors"])
    
    def test_verify_tampered_sig_fails(self, valid_registry, test_key):
        """Verification fails when signature file is tampered."""
        sign_registry_file(valid_registry, test_key)
        
        sig_path = valid_registry.with_suffix(valid_registry.suffix + ".sig")
        sig_data = json.loads(sig_path.read_text())
        sig_data["signature_hex"] = "0" * 64
        sig_path.write_text(json.dumps(sig_data))
        
        verify_result = verify_registry_file_signature(valid_registry, test_key)
        assert not verify_result["ok"]
        assert "signature_mismatch" in verify_result["errors"]
    
    def test_custom_sig_path(self, valid_registry, test_key, tmp_path):
        """Custom signature path works."""
        custom_sig = tmp_path / "custom.sig"
        
        sign_result = sign_registry_file(valid_registry, test_key, custom_sig)
        assert sign_result["ok"]
        assert custom_sig.exists()
        
        verify_result = verify_registry_file_signature(valid_registry, test_key, custom_sig)
        assert verify_result["ok"]
    
    def test_signed_at_strict_iso8601(self, valid_registry, test_key):
        """Signature file has strict ISO-8601 timestamp."""
        sign_registry_file(valid_registry, test_key)
        
        sig_path = valid_registry.with_suffix(valid_registry.suffix + ".sig")
        sig_data = json.loads(sig_path.read_text())
        signed_at = sig_data["signed_at"]
        
        # Must end with Z (UTC)
        assert signed_at.endswith("Z")
        # Must be valid ISO-8601
        from datetime import datetime
        datetime.fromisoformat(signed_at.replace("Z", "+00:00"))
