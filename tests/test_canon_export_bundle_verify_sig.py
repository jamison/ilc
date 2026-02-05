
import pytest
import base64
import subprocess
import sys
from pathlib import Path
from ilc_core.ledger.canon_export_bundle_verify_sig import verify_manifest_signature

COMMAND = [sys.executable, "-m", "ilc_core.cli.canon_bundle_validate"]

class TestCanonExportBundleVerifySig:
    
    @pytest.fixture
    def test_key(self):
        return b"secret_key"

    @pytest.fixture
    def signed_bundle(self, tmp_path, test_key):
        from ilc_core.ledger.canon_export_bundle import write_canon_export_bundle
        from ilc_core.ledger.canon_export_bundle_sign import sign_manifest
        
        bundle = tmp_path / "bundle"
        write_canon_export_bundle({"canon_hash": "foo"}, {"ok": True}, bundle)
        sign_manifest(bundle, test_key)
        return bundle

    def test_verify_success(self, signed_bundle, test_key):
        assert verify_manifest_signature(signed_bundle, test_key) is True

    def test_verify_tamper(self, signed_bundle, test_key):
        # Tamper manifest
        manifest = signed_bundle / "manifest.json"
        data = manifest.read_text()
        manifest.write_text(data + " ") # slight change
        
        assert verify_manifest_signature(signed_bundle, test_key) is False

    def test_verify_bad_key(self, signed_bundle):
        assert verify_manifest_signature(signed_bundle, b"wrong_key") is False

    def test_verify_missing_sig(self, tmp_path):
        from ilc_core.ledger.canon_export_bundle import write_canon_export_bundle
        bundle = tmp_path / "unsigned"
        write_canon_export_bundle({"canon_hash": "bar"}, {}, bundle)
        
        with pytest.raises(FileNotFoundError):
            verify_manifest_signature(bundle, b"key")

    def test_verify_multiline_sig_fails(self, signed_bundle, test_key):
        sig_path = signed_bundle / "manifest.sig"
        content = sig_path.read_bytes()
        # Create a "valid" looking base64 string but split across lines
        # This validator strictly rejects it
        sig_path.write_bytes(content + b"\n" + content)
        
        assert verify_manifest_signature(signed_bundle, test_key) is False

    def test_cli_integration(self, signed_bundle, tmp_path):
        # Write key file
        key_file = tmp_path / "key.txt"
        key_file.write_text(base64.b64encode(b"secret_key").decode())
        
        # 1. Success case
        result = subprocess.run(
            COMMAND + ["--bundle", str(signed_bundle), "--verify-signature", "--key-file", str(key_file)],
            capture_output=True, text=True
        )
        assert result.returncode == 0
        assert '"ok":true' in result.stdout
        assert result.stderr == ""

        # 2. Skip case (warning)
        result = subprocess.run(
            COMMAND + ["--bundle", str(signed_bundle)],
            capture_output=True, text=True
        )
        assert result.returncode == 0
        assert "Signature verification skipped" in result.stdout
        assert result.stderr == ""

        # 3. Mismatch case
        (signed_bundle / "manifest.json").write_text("{}") # Destroy manifest
        result = subprocess.run(
            COMMAND + ["--bundle", str(signed_bundle), "--verify-signature", "--key-file", str(key_file)],
            capture_output=True, text=True
        )
        assert '"ok":false' in result.stdout
        assert "signature_mismatch" in result.stdout
        assert result.stderr == ""

    def test_cli_invalid_key_file(self, signed_bundle, tmp_path):
        bad_key_file = tmp_path / "bad_key.txt"
        bad_key_file.write_text("not-base64@@@")
        result = subprocess.run(
            COMMAND + ["--bundle", str(signed_bundle), "--verify-signature", "--key-file", str(bad_key_file)],
            capture_output=True, text=True
        )
        assert result.returncode == 1
        assert '"ok":false' in result.stdout
        assert "invalid_key_file" in result.stdout
        assert result.stderr == ""
