"""
Tests for EVE capsule verification utilities.
"""

import pytest
import json
import base64
from pathlib import Path
from tempfile import NamedTemporaryFile

from cryptography.hazmat.primitives.asymmetric import ed25519

from ilc_core.eve.capsule import (
    load_capsule_manifest,
    validate_capsule_manifest,
    verify_capsule_signature,
    REQUIRED_MANIFEST_FIELDS,
    REQUIRED_ENTRY_FIELDS,
)
from ilc_core.crypto.cose_sign1 import cose_sign1_sign
from ilc_core.crypto.cbor_canonical import cbor_dumps_canonical


class TestValidateCapsuleManifest:
    """Tests for validate_capsule_manifest."""
    
    def test_valid_manifest(self):
        """Valid manifest passes validation."""
        manifest = {
            "capsule_id": "bafyreif...",
            "version": 1,
            "predecessor": None,
            "publisher_key_id": "did:key:z6Mk...",
            "created_at": "2026-01-31T22:00:00Z",
            "entries": [
                {
                    "kind": "document",
                    "cid": "bafyreig...",
                    "content_type": "text/markdown",
                }
            ],
        }
        # Should not raise
        validate_capsule_manifest(manifest)
    
    def test_missing_required_field(self):
        """Missing required field raises ValueError."""
        manifest = {
            "capsule_id": "bafyreif...",
            "version": 1,
            # Missing: predecessor, publisher_key_id, created_at, entries
        }
        with pytest.raises(ValueError, match="missing required fields"):
            validate_capsule_manifest(manifest)
    
    def test_invalid_version(self):
        """Non-positive version raises ValueError."""
        manifest = {
            "capsule_id": "bafyreif...",
            "version": 0,  # Invalid
            "predecessor": None,
            "publisher_key_id": "did:key:z6Mk...",
            "created_at": "2026-01-31T22:00:00Z",
            "entries": [{"kind": "doc", "cid": "baf...", "content_type": "text/plain"}],
        }
        with pytest.raises(ValueError, match="positive integer"):
            validate_capsule_manifest(manifest)
    
    def test_empty_entries(self):
        """Empty entries list raises ValueError."""
        manifest = {
            "capsule_id": "bafyreif...",
            "version": 1,
            "predecessor": None,
            "publisher_key_id": "did:key:z6Mk...",
            "created_at": "2026-01-31T22:00:00Z",
            "entries": [],  # Empty
        }
        with pytest.raises(ValueError, match="must not be empty"):
            validate_capsule_manifest(manifest)
    
    def test_entry_missing_required_field(self):
        """Entry missing required field raises ValueError."""
        manifest = {
            "capsule_id": "bafyreif...",
            "version": 1,
            "predecessor": None,
            "publisher_key_id": "did:key:z6Mk...",
            "created_at": "2026-01-31T22:00:00Z",
            "entries": [
                {"kind": "document"}  # Missing cid, content_type
            ],
        }
        with pytest.raises(ValueError, match="Entry 0 missing required fields"):
            validate_capsule_manifest(manifest)


class TestLoadCapsuleManifest:
    """Tests for load_capsule_manifest."""
    
    def test_load_valid_json(self, tmp_path):
        """Load valid JSON manifest."""
        manifest = {
            "capsule_id": "bafyreif...",
            "version": 1,
            "predecessor": None,
            "publisher_key_id": "did:key:z6Mk...",
            "created_at": "2026-01-31T22:00:00Z",
            "entries": [{"kind": "doc", "cid": "baf...", "content_type": "text/plain"}],
        }
        path = tmp_path / "manifest.json"
        path.write_text(json.dumps(manifest))
        
        loaded = load_capsule_manifest(path)
        assert loaded == manifest
    
    def test_load_invalid_json(self, tmp_path):
        """Invalid JSON raises ValueError."""
        path = tmp_path / "bad.json"
        path.write_text("not json")
        
        with pytest.raises(ValueError, match="Invalid JSON"):
            load_capsule_manifest(path)


class TestVerifyCapsuleSignature:
    """Tests for verify_capsule_signature."""
    
    def test_verify_valid_signature(self):
        """Valid signature returns True."""
        # Generate test key pair
        private_key = ed25519.Ed25519PrivateKey.generate()
        public_key = private_key.public_key()
        public_key_bytes = public_key.public_bytes_raw()
        
        # Create minimal valid DAG-CBOR payload
        # Using a simple map that satisfies ILC DAG-CBOR requirements
        payload = cbor_dumps_canonical({"test": "data", "version": 1})
        
        # Sign the payload
        cose_bytes = cose_sign1_sign(payload, private_key)
        
        # Encode as base64url (no padding)
        cose_b64u = base64.urlsafe_b64encode(cose_bytes).decode().rstrip("=")
        
        # Create corresponding manifest
        manifest = {"test": "manifest"}
        
        # Verify
        result = verify_capsule_signature(manifest, cose_b64u, public_key_bytes)
        assert result is True
    
    def test_verify_invalid_signature(self):
        """Invalid signature returns False."""
        # Generate two different key pairs
        private_key1 = ed25519.Ed25519PrivateKey.generate()
        private_key2 = ed25519.Ed25519PrivateKey.generate()
        public_key2 = private_key2.public_key()
        public_key2_bytes = public_key2.public_bytes_raw()
        
        # Sign with key1
        payload = cbor_dumps_canonical({"test": "data"})
        cose_bytes = cose_sign1_sign(payload, private_key1)
        cose_b64u = base64.urlsafe_b64encode(cose_bytes).decode().rstrip("=")
        
        # Try to verify with key2 (should fail)
        manifest = {}
        result = verify_capsule_signature(manifest, cose_b64u, public_key2_bytes)
        assert result is False
    
    def test_verify_malformed_b64u(self):
        """Malformed base64url returns False."""
        private_key = ed25519.Ed25519PrivateKey.generate()
        public_key_bytes = private_key.public_key().public_bytes_raw()
        
        result = verify_capsule_signature({}, "not-valid-base64!", public_key_bytes)
        assert result is False
