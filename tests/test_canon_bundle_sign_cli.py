
import pytest
import subprocess
import sys
import base64
from pathlib import Path

COMMAND = [sys.executable, "-m", "ilc_core.cli.canon_bundle_sign"]

class TestCanonBundleSignCLI:
    
    @pytest.fixture
    def bundle_dir(self, tmp_path):
        d = tmp_path / "bundle"
        d.mkdir()
        (d / "manifest.json").write_text("{}")
        return d

    @pytest.fixture
    def key_file(self, tmp_path):
        p = tmp_path / "key.txt"
        p.write_text(base64.b64encode(b"secret").decode())
        return p

    def run_cli(self, args):
        return subprocess.run(
            COMMAND + args,
            capture_output=True,
            text=True
        )

    def test_success_sign(self, bundle_dir, key_file):
        result = self.run_cli(["--bundle", str(bundle_dir), "--key-file", str(key_file)])
        assert result.returncode == 0
        assert '"ok":true' in result.stdout
        assert (bundle_dir / "manifest.sig").exists()
        assert result.stderr == ""

    def test_bundle_missing(self, tmp_path, key_file):
        result = self.run_cli(["--bundle", str(tmp_path / "missing"), "--key-file", str(key_file)])
        assert result.returncode == 1
        assert '"ok":false' in result.stdout
        assert "bundle_missing" in result.stdout
        assert result.stderr == ""

    def test_manifest_missing(self, bundle_dir, key_file):
        (bundle_dir / "manifest.json").unlink()
        result = self.run_cli(["--bundle", str(bundle_dir), "--key-file", str(key_file)])
        assert result.returncode == 1
        assert "manifest_missing" in result.stdout
        assert result.stderr == ""

    def test_signature_exists_no_overwrite(self, bundle_dir, key_file):
        (bundle_dir / "manifest.sig").write_text("old")
        result = self.run_cli(["--bundle", str(bundle_dir), "--key-file", str(key_file)])
        assert result.returncode == 1
        assert "signature_exists" in result.stdout
        assert (bundle_dir / "manifest.sig").read_text() == "old"
        assert result.stderr == ""

    def test_signature_exists_overwrite(self, bundle_dir, key_file):
        (bundle_dir / "manifest.sig").write_text("old")
        result = self.run_cli(["--bundle", str(bundle_dir), "--key-file", str(key_file), "--overwrite"])
        assert result.returncode == 0
        assert '"ok":true' in result.stdout
        assert (bundle_dir / "manifest.sig").read_text() != "old"
        assert result.stderr == ""

    def test_invalid_key_file(self, bundle_dir, tmp_path):
        bad_key = tmp_path / "bad.txt"
        bad_key.write_text("not-base64")
        result = self.run_cli(["--bundle", str(bundle_dir), "--key-file", str(bad_key)])
        assert result.returncode == 1
        assert "invalid_key_file" in result.stdout
        assert result.stderr == ""

    def test_key_missing_flag(self, bundle_dir):
        result = self.run_cli(["--bundle", str(bundle_dir)])
        assert result.returncode == 1
        assert "key_missing" in result.stdout
        assert result.stderr == ""

    def test_key_file_missing_path(self, bundle_dir, tmp_path):
        # Path provided but file doesn't exist
        missing_key = tmp_path / "no_exist.txt"
        result = self.run_cli(["--bundle", str(bundle_dir), "--key-file", str(missing_key)])
        assert result.returncode == 1
        assert "key_missing" in result.stdout
        assert result.stderr == ""
