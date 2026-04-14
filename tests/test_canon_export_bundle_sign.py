
import pytest
import base64
import hmac
import hashlib
import json
from pathlib import Path
from ilc_core.ledger.canon_export_bundle_sign import sign_manifest, load_key_from_file
from ilc_core.ledger.canon_bundle_utils import derive_key_fingerprint, derive_key_id

class TestCanonExportBundleSign:
    
    @pytest.fixture
    def test_key(self):
        return b"secret_key_123"
        
    @pytest.fixture
    def valid_bundle(self, tmp_path):
        bundle = tmp_path / "bundle"
        bundle.mkdir()
        (bundle / "manifest.json").write_text('{"foo": "bar"}')
        return bundle

    def test_sign_manifest_success(self, valid_bundle, test_key):
        sig_path = sign_manifest(valid_bundle, test_key)
        assert sig_path.exists()
        assert sig_path.name == "manifest.sig"
        content = sig_path.read_bytes().strip()
        assert len(base64.b64decode(content)) == 32 # SHA256 size

    def test_sign_manifest_integrity(self, valid_bundle, test_key):
        """Verify the signature is actually correct."""
        sig_path = sign_manifest(valid_bundle, test_key)
        
        manifest_data = (valid_bundle / "manifest.json").read_bytes()
        expected = hmac.new(test_key, manifest_data, hashlib.sha256).digest()
        actual = base64.b64decode(sig_path.read_bytes().strip())
        
        assert actual == expected

    def test_sign_manifest_no_manifest(self, tmp_path, test_key):
        with pytest.raises(FileNotFoundError):
            sign_manifest(tmp_path, test_key)

    def test_sign_manifest_overwrite_protection(self, valid_bundle, test_key):
        sign_manifest(valid_bundle, test_key)
        
        with pytest.raises(FileExistsError):
            sign_manifest(valid_bundle, test_key, overwrite=False)
            
        # Should succeed with overwrite
        sign_manifest(valid_bundle, test_key, overwrite=True)

    def test_sign_manifest_different_keys(self, valid_bundle):
        # Different keys produce different sigs
        k1 = b"key1"
        k2 = b"key2"
        
        sign_manifest(valid_bundle, k1)
        sig1 = (valid_bundle / "manifest.sig").read_bytes()
        
        sign_manifest(valid_bundle, k2, overwrite=True)
        sig2 = (valid_bundle / "manifest.sig").read_bytes()
        
        assert sig1 != sig2

    def test_load_key_from_file(self, tmp_path):
        key = b"secret_key_123"
        key_b64 = base64.b64encode(key).decode("utf-8")
        key_path = tmp_path / "key.txt"
        key_path.write_text(key_b64)

        loaded = load_key_from_file(key_path)
        assert loaded == key

    def test_manifest_has_key_metadata(self, valid_bundle, test_key):
        """Manifest includes key_id, sig_alg, signed_at after signing."""
        sign_manifest(valid_bundle, test_key, overwrite=True)
        manifest = json.loads((valid_bundle / "manifest.json").read_text())
        assert "key_id" in manifest
        assert "key_fingerprint" in manifest
        assert len(manifest["key_fingerprint"]) == 64
        assert manifest["sig_alg"] == "hmac-sha256"
        assert manifest["signed_at"].endswith("Z")

    def test_key_id_derived_from_key_bytes(self, valid_bundle, test_key):
        """key_id should be derived from sha256(key)[:16]."""
        sign_manifest(valid_bundle, test_key, overwrite=True)
        manifest = json.loads((valid_bundle / "manifest.json").read_text())
        expected_key_id = derive_key_id(test_key)
        assert manifest["key_id"] == expected_key_id
        assert len(manifest["key_id"]) == 16

    def test_key_fingerprint_derived_from_key_bytes(self, valid_bundle, test_key):
        """key_fingerprint should be derived from full sha256(key)."""
        sign_manifest(valid_bundle, test_key, overwrite=True)
        manifest = json.loads((valid_bundle / "manifest.json").read_text())
        expected_key_fingerprint = derive_key_fingerprint(test_key)
        assert manifest["key_fingerprint"] == expected_key_fingerprint

    def test_manifest_is_rewritten_in_canonical_json_form(self, valid_bundle, test_key):
        sign_manifest(valid_bundle, test_key, overwrite=True)
        text = (valid_bundle / "manifest.json").read_text(encoding="utf-8")
        assert ": " not in text
        loaded = json.loads(text)
        assert text == json.dumps(loaded, sort_keys=True, separators=(",", ":"), allow_nan=False)

    def test_sign_manifest_rejects_non_finite_manifest_constants(self, valid_bundle, test_key):
        (valid_bundle / "manifest.json").write_text('{"foo":NaN}', encoding="utf-8")
        with pytest.raises(Exception) as excinfo:
            sign_manifest(valid_bundle, test_key, overwrite=True)
        assert "invalid_manifest_non_finite" in str(excinfo.value)

    def test_sign_manifest_explicit_signed_at_is_reproducible(self, valid_bundle, test_key):
        signed_at = "2026-04-14T10:00:00Z"
        sign_manifest(valid_bundle, test_key, overwrite=True, signed_at=signed_at)
        manifest_once = (valid_bundle / "manifest.json").read_text(encoding="utf-8")
        sig_once = (valid_bundle / "manifest.sig").read_bytes()

        sign_manifest(valid_bundle, test_key, overwrite=True, signed_at=signed_at)
        manifest_twice = (valid_bundle / "manifest.json").read_text(encoding="utf-8")
        sig_twice = (valid_bundle / "manifest.sig").read_bytes()

        assert manifest_once == manifest_twice
        assert sig_once == sig_twice

    def test_sign_manifest_uses_created_at_as_deterministic_fallback(self, valid_bundle, test_key):
        manifest_path = valid_bundle / "manifest.json"
        manifest_path.write_text(
            json.dumps({"foo": "bar", "created_at": "2026-04-14T09:30:00Z"}),
            encoding="utf-8",
        )
        sign_manifest(valid_bundle, test_key, overwrite=True)
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        assert manifest["signed_at"] == "2026-04-14T09:30:00Z"

    def test_sign_manifest_rejects_invalid_explicit_signed_at(self, valid_bundle, test_key):
        with pytest.raises(Exception) as excinfo:
            sign_manifest(
                valid_bundle,
                test_key,
                overwrite=True,
                signed_at="2026-04-14 10:00:00",
            )
        assert "invalid_signed_at" in str(excinfo.value)
