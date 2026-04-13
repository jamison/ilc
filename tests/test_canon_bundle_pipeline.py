
import pytest
import subprocess
import sys
import base64
import json
from pathlib import Path

from ilc_core.ledger.canon_export_bundle_sign import sign_manifest, load_key_from_file

COMMAND = [sys.executable, "-m", "ilc_core.cli.canon_bundle_pipeline"]


@pytest.fixture(autouse=True)
def _allow_empty_key_registry(monkeypatch):
    monkeypatch.setenv("ILC_ALLOW_EMPTY_KEY_REGISTRY", "1")


class TestCanonBundlePipeline:
    
    @pytest.fixture
    def valid_bundle(self, tmp_path):
        from ilc_core.ledger.canon_export_bundle import write_canon_export_bundle
        bundle = tmp_path / "bundle"
        export = {
            "canon_export_format": "v0.1",
            "canon_hash": "abc123",
            "exported_at": "2026-04-14T00:00:00Z",
            "meta": {
                "canon_export_version": "v0.1",
                "epoch_count": 0,
                "snapshot_count": 1,
                "balance_count": 1,
            },
            "epochs": [],
            "snapshots": [
                {
                    "epoch_id": "epoch-0001",
                    "balances": {"agent:test": "1.0"},
                }
            ],
        }
        validation = {"ok": True, "errors": [], "warnings": []}
        write_canon_export_bundle(export, validation, bundle)
        return bundle

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

    def test_full_pipeline_success(self, valid_bundle, key_file, tmp_path):
        report_path = tmp_path / "report.md"
        result = self.run_cli([
            "--bundle", str(valid_bundle),
            "--key-file", str(key_file),
            "--report", str(report_path)
        ])
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["ok"] is True
        assert data["steps"]["validate"] is True
        assert data["steps"]["sign"] is True
        assert data["steps"]["verify"] is True
        # Note: steps["report"] is False in JSON because report is written after JSON output
        assert report_path.exists()
        assert (valid_bundle / "manifest.sig").exists()
        assert result.stderr == ""

    def test_pipeline_no_signing(self, valid_bundle):
        result = self.run_cli(["--bundle", str(valid_bundle)])
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["ok"] is True
        assert data["steps"]["validate"] is True
        assert data["steps"]["sign"] is False
        assert data["steps"]["verify"] is False
        assert "signature_verification_skipped" in data["warnings"]
        assert result.stderr == ""

    def test_bundle_missing(self, tmp_path, key_file):
        result = self.run_cli(["--bundle", str(tmp_path / "missing"), "--key-file", str(key_file)])
        assert result.returncode == 1
        data = json.loads(result.stdout)
        assert data["ok"] is False
        assert "bundle_missing" in data["errors"]
        assert result.stderr == ""

    def test_bundle_is_file(self, tmp_path, key_file):
        file_path = tmp_path / "notadir"
        file_path.write_text("oops")
        result = self.run_cli(["--bundle", str(file_path), "--key-file", str(key_file)])
        assert result.returncode == 1
        data = json.loads(result.stdout)
        assert "bundle_missing" in data["errors"]
        assert result.stderr == ""

    def test_manifest_missing(self, tmp_path, key_file):
        bundle = tmp_path / "empty_bundle"
        bundle.mkdir()
        result = self.run_cli(["--bundle", str(bundle), "--key-file", str(key_file)])
        assert result.returncode == 1
        data = json.loads(result.stdout)
        assert data["ok"] is False
        assert "manifest_missing" in data["errors"]
        assert result.stderr == ""

    def test_invalid_key_file(self, valid_bundle, tmp_path):
        bad_key = tmp_path / "bad.txt"
        bad_key.write_text("not-base64!!!")
        result = self.run_cli(["--bundle", str(valid_bundle), "--key-file", str(bad_key)])
        assert result.returncode == 1
        data = json.loads(result.stdout)
        assert "invalid_key_file" in data["errors"]
        assert result.stderr == ""

    def test_key_file_missing_path(self, valid_bundle, tmp_path):
        missing_key = tmp_path / "no_exist.txt"
        result = self.run_cli(["--bundle", str(valid_bundle), "--key-file", str(missing_key)])
        assert result.returncode == 1
        data = json.loads(result.stdout)
        assert "key_missing" in data["errors"]
        assert result.stderr == ""

    def test_signature_mismatch(self, valid_bundle, key_file):
        key = load_key_from_file(key_file)
        sign_manifest(valid_bundle, key)

        # Tamper manifest after signing so signature is stale.
        manifest = valid_bundle / "manifest.json"
        manifest.write_text(manifest.read_text() + " ")

        result = self.run_cli(["--bundle", str(valid_bundle), "--key-file", str(key_file)])
        assert result.returncode == 1
        data = json.loads(result.stdout)
        assert "signature_mismatch" in data["errors"]
        assert result.stderr == ""
    def test_signature_exists_no_overwrite(self, valid_bundle, key_file):
        key = load_key_from_file(key_file)
        sign_manifest(valid_bundle, key)
        
        result = self.run_cli(["--bundle", str(valid_bundle), "--key-file", str(key_file)])
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert "signature_exists" in data["warnings"]
        assert result.stderr == ""
