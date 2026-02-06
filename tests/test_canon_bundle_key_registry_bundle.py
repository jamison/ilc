"""Tests for canon bundle key registry bundle creation and verification."""

import json
import pytest
from pathlib import Path

from ilc_core.ledger.canon_bundle_key_registry_bundle import (
    build_registry_bundle,
    verify_registry_bundle,
    BUNDLE_DIR_NAME,
    REGISTRY_FILENAME,
    SIG_FILENAME,
    MANIFEST_FILENAME,
)


class TestBuildRegistryBundle:
    """Tests for build_registry_bundle helper."""
    
    def _write_registry(self, tmp_path, data):
        path = tmp_path / "canon_key_registry_v0.1.json"
        path.write_text(json.dumps(data, indent=2))
        return path
    
    def test_build_creates_all_files(self, tmp_path):
        """Bundle creation creates all required files."""
        registry_path = self._write_registry(tmp_path, {
            "registry_version": "v0.1",
            "updated_at": "2026-02-06T10:00:00Z",
            "current_keys": ["a1b2c3d4e5f6a7b8"],
            "previous_keys": [],
            "deprecated_keys": [],
        })
        key = b"test-signing-key"
        out_dir = tmp_path / "output"
        
        result = build_registry_bundle(registry_path, key, out_dir)
        
        assert result["ok"] is True
        bundle_dir = Path(result["bundle_dir"])
        assert bundle_dir.exists()
        assert (bundle_dir / REGISTRY_FILENAME).exists()
        assert (bundle_dir / SIG_FILENAME).exists()
        assert (bundle_dir / MANIFEST_FILENAME).exists()
    
    def test_build_manifest_has_required_fields(self, tmp_path):
        """Manifest contains all required fields."""
        registry_path = self._write_registry(tmp_path, {
            "registry_version": "v0.1",
            "updated_at": "2026-02-06T10:00:00Z",
            "current_keys": ["a1b2c3d4e5f6a7b8"],
            "previous_keys": [],
            "deprecated_keys": [],
        })
        key = b"test-signing-key"
        out_dir = tmp_path / "output"
        
        result = build_registry_bundle(registry_path, key, out_dir)
        manifest = result["manifest"]
        
        assert manifest["bundle_version"] == "v0.1"
        assert "created_at" in manifest
        assert manifest["registry_path"] == REGISTRY_FILENAME
        assert "registry_hash" in manifest
        assert "registry_size_bytes" in manifest
        assert manifest["sig_path"] == SIG_FILENAME
        assert "sig_alg" in manifest
        assert "key_id" in manifest
        assert manifest["registry_version"] == "v0.1"
        assert "sig_hash" in manifest
    
    def test_build_fails_without_force_if_exists(self, tmp_path):
        """Build fails if bundle exists and --force not set."""
        registry_path = self._write_registry(tmp_path, {
            "registry_version": "v0.1",
            "updated_at": "2026-02-06T10:00:00Z",
            "current_keys": ["a1b2c3d4e5f6a7b8"],
            "previous_keys": [],
            "deprecated_keys": [],
        })
        key = b"test-signing-key"
        out_dir = tmp_path / "output"
        
        # First build
        result1 = build_registry_bundle(registry_path, key, out_dir)
        assert result1["ok"] is True
        
        # Second build without force
        result2 = build_registry_bundle(registry_path, key, out_dir)
        assert result2["ok"] is False
        assert result2["error"] == "bundle_exists"
    
    def test_build_succeeds_with_force(self, tmp_path):
        """Build succeeds with --force even if bundle exists."""
        registry_path = self._write_registry(tmp_path, {
            "registry_version": "v0.1",
            "updated_at": "2026-02-06T10:00:00Z",
            "current_keys": ["a1b2c3d4e5f6a7b8"],
            "previous_keys": [],
            "deprecated_keys": [],
        })
        key = b"test-signing-key"
        out_dir = tmp_path / "output"
        
        result1 = build_registry_bundle(registry_path, key, out_dir)
        assert result1["ok"] is True
        
        result2 = build_registry_bundle(registry_path, key, out_dir, force=True)
        assert result2["ok"] is True
    
    def test_build_fails_on_invalid_registry(self, tmp_path):
        """Build fails on invalid registry."""
        registry_path = self._write_registry(tmp_path, {"invalid": "data"})
        key = b"test-signing-key"
        out_dir = tmp_path / "output"
        
        result = build_registry_bundle(registry_path, key, out_dir)
        assert result["ok"] is False
        assert result["error"] == "registry_invalid"


class TestVerifyRegistryBundle:
    """Tests for verify_registry_bundle helper."""
    
    def _create_valid_bundle(self, tmp_path):
        registry_path = tmp_path / "source" / "canon_key_registry_v0.1.json"
        registry_path.parent.mkdir(parents=True)
        registry_path.write_text(json.dumps({
            "registry_version": "v0.1",
            "updated_at": "2026-02-06T10:00:00Z",
            "current_keys": ["a1b2c3d4e5f6a7b8"],
            "previous_keys": [],
            "deprecated_keys": [],
        }))
        key = b"test-signing-key"
        out_dir = tmp_path / "bundles"
        
        result = build_registry_bundle(registry_path, key, out_dir)
        return Path(result["bundle_dir"]), key
    
    def test_verify_succeeds_on_valid_bundle(self, tmp_path):
        """Verify succeeds on valid bundle."""
        bundle_dir, key = self._create_valid_bundle(tmp_path)
        
        result = verify_registry_bundle(bundle_dir, key)
        assert result["ok"] is True
        assert len(result["errors"]) == 0
    
    def test_verify_fails_on_missing_bundle(self, tmp_path):
        """Verify fails on missing bundle."""
        bundle_dir = tmp_path / "nonexistent"
        key = b"test-signing-key"
        
        result = verify_registry_bundle(bundle_dir, key)
        assert result["ok"] is False
        assert "bundle_missing" in result["errors"]
    
    def test_verify_fails_on_missing_manifest(self, tmp_path):
        """Verify fails on missing manifest."""
        bundle_dir, key = self._create_valid_bundle(tmp_path)
        (bundle_dir / MANIFEST_FILENAME).unlink()
        
        result = verify_registry_bundle(bundle_dir, key)
        assert result["ok"] is False
        assert "manifest_missing" in result["errors"]
    
    def test_verify_fails_on_hash_mismatch(self, tmp_path):
        """Verify fails when registry hash doesn't match."""
        bundle_dir, key = self._create_valid_bundle(tmp_path)
        
        # Tamper with manifest hash
        manifest_path = bundle_dir / MANIFEST_FILENAME
        manifest = json.loads(manifest_path.read_text())
        manifest["registry_hash"] = "0" * 64
        manifest_path.write_text(json.dumps(manifest))
        
        result = verify_registry_bundle(bundle_dir, key)
        assert result["ok"] is False
        assert "hash_mismatch" in result["errors"]
    
    def test_verify_fails_on_sig_hash_mismatch(self, tmp_path):
        """Verify fails when sig hash doesn't match."""
        bundle_dir, key = self._create_valid_bundle(tmp_path)
        
        # Tamper with manifest sig hash
        manifest_path = bundle_dir / MANIFEST_FILENAME
        manifest = json.loads(manifest_path.read_text())
        manifest["sig_hash"] = "0" * 64
        manifest_path.write_text(json.dumps(manifest))
        
        result = verify_registry_bundle(bundle_dir, key)
        assert result["ok"] is False
        assert "sig_hash_mismatch" in result["errors"]
    
    def test_verify_fails_on_wrong_key(self, tmp_path):
        """Verify fails with wrong verification key."""
        bundle_dir, _ = self._create_valid_bundle(tmp_path)
        wrong_key = b"wrong-key-12345"
        
        result = verify_registry_bundle(bundle_dir, wrong_key)
        assert result["ok"] is False
        assert "signature_invalid" in result["errors"]
    
    def test_verify_fails_on_bundle_version_mismatch(self, tmp_path):
        """Verify fails on bundle_version mismatch."""
        bundle_dir, key = self._create_valid_bundle(tmp_path)
        
        manifest_path = bundle_dir / MANIFEST_FILENAME
        manifest = json.loads(manifest_path.read_text())
        manifest["bundle_version"] = "v999"
        manifest_path.write_text(json.dumps(manifest))
        
        result = verify_registry_bundle(bundle_dir, key)
        assert result["ok"] is False
        assert "bundle_version_mismatch" in result["errors"]
    
    def test_verify_rejects_path_traversal(self, tmp_path):
        """Verify rejects path traversal in manifest."""
        bundle_dir, key = self._create_valid_bundle(tmp_path)
        
        manifest_path = bundle_dir / MANIFEST_FILENAME
        manifest = json.loads(manifest_path.read_text())
        manifest["registry_path"] = "../../../etc/passwd"
        manifest_path.write_text(json.dumps(manifest))
        
        result = verify_registry_bundle(bundle_dir, key)
        assert result["ok"] is False
        assert any("path_traversal" in e for e in result["errors"])

    def test_verify_rejects_sig_path_traversal(self, tmp_path):
        """Verify rejects path traversal in sig_path."""
        bundle_dir, key = self._create_valid_bundle(tmp_path)
        
        manifest_path = bundle_dir / MANIFEST_FILENAME
        manifest = json.loads(manifest_path.read_text())
        manifest["sig_path"] = "../canon_key_registry_v0.1.json.sig"
        manifest_path.write_text(json.dumps(manifest))
        
        result = verify_registry_bundle(bundle_dir, key)
        assert result["ok"] is False
        assert any("path_traversal" in e for e in result["errors"])

    def test_verify_rejects_extra_files(self, tmp_path):
        """Verify fails when bundle contains extra files."""
        bundle_dir, key = self._create_valid_bundle(tmp_path)
        extra_path = bundle_dir / "extra.txt"
        extra_path.write_text("noise")
        
        result = verify_registry_bundle(bundle_dir, key)
        assert result["ok"] is False
        assert "bundle_extra_files" in result["errors"]


class TestBundleCli:
    """Tests for bundle CLI."""
    
    def _write_registry(self, tmp_path, data):
        path = tmp_path / "canon_key_registry_v0.1.json"
        path.write_text(json.dumps(data, indent=2))
        return path
    
    def _run_cli(self, args):
        import subprocess
        return subprocess.run(
            ["python3", "-m", "ilc_core.cli.canon_bundle_key_registry_bundle"] + args,
            capture_output=True,
            text=True,
            cwd="/Users/jamstar/Documents/ILC_Main/01_Current"
        )
    
    def test_cli_build(self, tmp_path):
        """CLI --build works."""
        registry_path = self._write_registry(tmp_path, {
            "registry_version": "v0.1",
            "updated_at": "2026-02-06T10:00:00Z",
            "current_keys": ["a1b2c3d4e5f6a7b8"],
            "previous_keys": [],
            "deprecated_keys": [],
        })
        key_path = tmp_path / "key.txt"
        key_path.write_bytes(b"test-signing-key")
        out_dir = tmp_path / "bundles"
        
        result = self._run_cli([
            "--build",
            "--registry", str(registry_path),
            "--key-file", str(key_path),
            "--out-dir", str(out_dir),
        ])
        
        assert result.returncode == 0
        output = json.loads(result.stdout)
        assert output["ok"] is True
        assert "bundle_dir" in output
    
    def test_cli_verify(self, tmp_path):
        """CLI --verify works."""
        # First build a bundle
        registry_path = self._write_registry(tmp_path, {
            "registry_version": "v0.1",
            "updated_at": "2026-02-06T10:00:00Z",
            "current_keys": ["a1b2c3d4e5f6a7b8"],
            "previous_keys": [],
            "deprecated_keys": [],
        })
        key_path = tmp_path / "key.txt"
        key_path.write_bytes(b"test-signing-key")
        out_dir = tmp_path / "bundles"
        
        build_result = self._run_cli([
            "--build",
            "--registry", str(registry_path),
            "--key-file", str(key_path),
            "--out-dir", str(out_dir),
        ])
        assert build_result.returncode == 0
        build_output = json.loads(build_result.stdout)
        bundle_dir = build_output["bundle_dir"]
        
        # Now verify
        verify_result = self._run_cli([
            "--verify",
            "--bundle", bundle_dir,
            "--key-file", str(key_path),
        ])
        
        assert verify_result.returncode == 0
        verify_output = json.loads(verify_result.stdout)
        assert verify_output["ok"] is True
    
    def test_cli_build_missing_registry(self, tmp_path):
        """CLI --build fails on missing registry."""
        key_path = tmp_path / "key.txt"
        key_path.write_bytes(b"test-signing-key")
        out_dir = tmp_path / "bundles"
        
        result = self._run_cli([
            "--build",
            "--registry", str(tmp_path / "nonexistent.json"),
            "--key-file", str(key_path),
            "--out-dir", str(out_dir),
        ])
        
        assert result.returncode == 2
        output = json.loads(result.stdout)
        assert "registry_not_found" in output["errors"]
