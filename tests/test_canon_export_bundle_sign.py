
import pytest
import base64
import hmac
import hashlib
from pathlib import Path
from ilc_core.ledger.canon_export_bundle_sign import sign_manifest, load_key_from_file

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
