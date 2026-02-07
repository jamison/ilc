"""Tests for canon bundle key registry fetch."""

import json
import pytest
import shutil
import tarfile
import zipfile
from pathlib import Path

from ilc_core.ledger.canon_bundle_key_registry_bundle import (
    build_registry_bundle,
    BUNDLE_DIR_NAME,
)
from ilc_core.ledger.canon_bundle_key_registry_fetch import fetch_registry_bundle


class TestFetchRegistryBundle:
    """Tests for fetch_registry_bundle helper."""
    
    def _create_valid_bundle(self, tmp_path):
        """Create a valid bundle for testing."""
        registry_path = tmp_path / "source" / "canon_key_registry_v0.1.json"
        registry_path.parent.mkdir(parents=True)
        registry_path.write_text(json.dumps({
            "registry_version": "v0.1",
            "updated_at": "2026-02-07T10:00:00Z",
            "current_keys": ["a1b2c3d4e5f6a7b8"],
            "previous_keys": [],
            "deprecated_keys": [],
        }))
        key = b"test-signing-key"
        
        build_result = build_registry_bundle(
            registry_path, key, tmp_path / "bundles"
        )
        return Path(build_result["bundle_dir"]), key
    
    def test_fetch_from_local_dir_succeeds(self, tmp_path):
        """Fetch from local directory works."""
        bundle_dir, key = self._create_valid_bundle(tmp_path)
        dest_dir = tmp_path / "installed"
        
        result = fetch_registry_bundle(str(bundle_dir), key, dest_dir)
        
        assert result["ok"] is True
        assert (dest_dir / BUNDLE_DIR_NAME).exists()
    
    def test_fetch_from_file_url_succeeds(self, tmp_path):
        """Fetch from file:// URL works."""
        bundle_dir, key = self._create_valid_bundle(tmp_path)
        dest_dir = tmp_path / "installed"
        source = f"file://{bundle_dir}"
        
        result = fetch_registry_bundle(source, key, dest_dir)
        
        assert result["ok"] is True
        assert (dest_dir / BUNDLE_DIR_NAME).exists()
    
    def test_fetch_fails_on_invalid_bundle(self, tmp_path):
        """Fetch fails on invalid bundle."""
        # Create invalid bundle directory
        invalid_dir = tmp_path / "invalid_bundle"
        invalid_dir.mkdir()
        (invalid_dir / "random.txt").write_text("noise")
        
        key = b"test-signing-key"
        dest_dir = tmp_path / "installed"
        
        result = fetch_registry_bundle(str(invalid_dir), key, dest_dir)
        
        assert result["ok"] is False
        assert "bundle_verify_failed" in result["errors"]
    
    def test_fetch_fails_if_dest_exists_without_force(self, tmp_path):
        """Fetch fails if destination exists without --force."""
        bundle_dir, key = self._create_valid_bundle(tmp_path)
        dest_dir = tmp_path / "installed"
        
        # First fetch
        result1 = fetch_registry_bundle(str(bundle_dir), key, dest_dir)
        assert result1["ok"] is True
        
        # Re-create source bundle (since it was moved)
        bundle_dir2, key2 = self._create_valid_bundle(tmp_path / "second")
        
        # Second fetch without force
        result2 = fetch_registry_bundle(str(bundle_dir2), key2, dest_dir)
        assert result2["ok"] is False
        assert "bundle_exists" in result2["errors"]
    
    def test_fetch_succeeds_with_force(self, tmp_path):
        """Fetch succeeds with --force when destination exists."""
        bundle_dir, key = self._create_valid_bundle(tmp_path)
        dest_dir = tmp_path / "installed"
        
        # First fetch
        result1 = fetch_registry_bundle(str(bundle_dir), key, dest_dir)
        assert result1["ok"] is True
        
        # Re-create source bundle
        bundle_dir2, key2 = self._create_valid_bundle(tmp_path / "second")
        
        # Second fetch with force
        result2 = fetch_registry_bundle(str(bundle_dir2), key2, dest_dir, force=True)
        assert result2["ok"] is True
    
    def test_fetch_fails_on_source_not_found(self, tmp_path):
        """Fetch fails when source doesn't exist."""
        key = b"test-signing-key"
        dest_dir = tmp_path / "installed"
        
        result = fetch_registry_bundle(str(tmp_path / "nonexistent"), key, dest_dir)
        
        assert result["ok"] is False
        assert "source_not_found" in result["errors"]
    
    def test_fetch_requires_allow_network_for_https(self, tmp_path):
        """Fetch requires --allow-network for https URLs."""
        key = b"test-signing-key"
        dest_dir = tmp_path / "installed"
        
        result = fetch_registry_bundle(
            "https://example.com/bundle.tar.gz",
            key, dest_dir, allow_network=False
        )
        
        assert result["ok"] is False
        assert "network_not_allowed" in result["errors"]

    def test_fetch_defaults_to_strict(self, tmp_path):
        """Fetch defaults to strict validation."""
        registry_path = tmp_path / "source" / "canon_key_registry_v0.1.json"
        registry_path.parent.mkdir(parents=True)
        registry_path.write_text(json.dumps({
            "registry_version": "v0.1",
            "updated_at": "2026-02-07T10:00:00Z",
            "current_keys": [],
            "previous_keys": [],
            "deprecated_keys": [],
        }))
        key = b"test-signing-key"

        build_result = build_registry_bundle(
            registry_path, key, tmp_path / "bundles"
        )
        bundle_dir = Path(build_result["bundle_dir"])
        dest_dir = tmp_path / "installed"

        result = fetch_registry_bundle(str(bundle_dir), key, dest_dir)

        assert result["ok"] is False
        assert "bundle_verify_failed" in result["errors"]
    
    def test_fetch_from_tar_archive(self, tmp_path):
        """Fetch from tar archive works."""
        bundle_dir, key = self._create_valid_bundle(tmp_path)
        
        # Create tar archive
        archive_path = tmp_path / "bundle.tar.gz"
        with tarfile.open(archive_path, "w:gz") as tf:
            tf.add(bundle_dir, arcname=bundle_dir.name)
        
        # Remove original bundle
        shutil.rmtree(bundle_dir)
        
        dest_dir = tmp_path / "installed"
        result = fetch_registry_bundle(str(archive_path), key, dest_dir)
        
        assert result["ok"] is True
        assert (dest_dir / BUNDLE_DIR_NAME).exists()
    
    def test_fetch_from_zip_archive(self, tmp_path):
        """Fetch from zip archive works."""
        bundle_dir, key = self._create_valid_bundle(tmp_path)
        
        # Create zip archive
        archive_path = tmp_path / "bundle.zip"
        with zipfile.ZipFile(archive_path, "w") as zf:
            for file in bundle_dir.rglob("*"):
                if file.is_file():
                    arcname = str(file.relative_to(bundle_dir.parent))
                    zf.write(file, arcname)
        
        # Remove original bundle
        shutil.rmtree(bundle_dir)
        
        dest_dir = tmp_path / "installed"
        result = fetch_registry_bundle(str(archive_path), key, dest_dir)
        
        assert result["ok"] is True
        assert (dest_dir / BUNDLE_DIR_NAME).exists()
    
    def test_fetch_rejects_path_traversal_in_tar(self, tmp_path):
        """Fetch rejects path traversal in tar archive."""
        # Create malicious tar
        archive_path = tmp_path / "evil.tar.gz"
        with tarfile.open(archive_path, "w:gz") as tf:
            # Create member with path traversal
            info = tarfile.TarInfo(name="../../../etc/passwd")
            info.size = 0
            tf.addfile(info)
        
        key = b"test-signing-key"
        dest_dir = tmp_path / "installed"
        
        result = fetch_registry_bundle(str(archive_path), key, dest_dir)
        
        assert result["ok"] is False
        assert "archive_path_traversal" in result["errors"]
    
    def test_fetch_rejects_invalid_archive_layout(self, tmp_path):
        """Fetch rejects archive with multiple top-level entries."""
        # Create tar with multiple top-level directories
        archive_path = tmp_path / "multi.tar.gz"
        with tarfile.open(archive_path, "w:gz") as tf:
            info1 = tarfile.TarInfo(name="dir1/file.txt")
            info1.size = 0
            tf.addfile(info1)
            info2 = tarfile.TarInfo(name="dir2/file.txt")
            info2.size = 0
            tf.addfile(info2)
        
        key = b"test-signing-key"
        dest_dir = tmp_path / "installed"
        
        result = fetch_registry_bundle(str(archive_path), key, dest_dir)
        
        assert result["ok"] is False
        assert "bundle_layout_invalid" in result["errors"]


class TestFetchCli:
    """Tests for fetch CLI."""
    
    def _create_valid_bundle(self, tmp_path):
        registry_path = tmp_path / "source" / "canon_key_registry_v0.1.json"
        registry_path.parent.mkdir(parents=True)
        registry_path.write_text(json.dumps({
            "registry_version": "v0.1",
            "updated_at": "2026-02-07T10:00:00Z",
            "current_keys": ["a1b2c3d4e5f6a7b8"],
            "previous_keys": [],
            "deprecated_keys": [],
        }))
        key = b"test-signing-key"
        
        build_result = build_registry_bundle(
            registry_path, key, tmp_path / "bundles"
        )
        return Path(build_result["bundle_dir"]), key
    
    def _run_cli(self, args):
        import subprocess
        return subprocess.run(
            ["python3", "-m", "ilc_core.cli.canon_bundle_key_registry_fetch"] + args,
            capture_output=True,
            text=True,
            cwd="/Users/jamstar/Documents/ILC_Main/01_Current"
        )
    
    def test_cli_fetch_local(self, tmp_path):
        """CLI fetch from local directory works."""
        bundle_dir, key = self._create_valid_bundle(tmp_path)
        key_path = tmp_path / "key.txt"
        key_path.write_bytes(key)
        dest_dir = tmp_path / "installed"
        
        result = self._run_cli([
            "--source", str(bundle_dir),
            "--key-file", str(key_path),
            "--dest", str(dest_dir),
        ])
        
        assert result.returncode == 0
        output = json.loads(result.stdout)
        assert output["ok"] is True
    
    def test_cli_fetch_missing_source(self, tmp_path):
        """CLI fetch fails on missing source."""
        key_path = tmp_path / "key.txt"
        key_path.write_bytes(b"test-key")
        dest_dir = tmp_path / "installed"
        
        result = self._run_cli([
            "--source", str(tmp_path / "nonexistent"),
            "--key-file", str(key_path),
            "--dest", str(dest_dir),
        ])
        
        assert result.returncode == 2
        output = json.loads(result.stdout)
        assert "source_not_found" in output["errors"]
    
    def test_cli_fetch_https_requires_allow_network(self, tmp_path):
        """CLI fetch requires --allow-network for https."""
        key_path = tmp_path / "key.txt"
        key_path.write_bytes(b"test-key")
        dest_dir = tmp_path / "installed"
        
        result = self._run_cli([
            "--source", "https://example.com/bundle.tar.gz",
            "--key-file", str(key_path),
            "--dest", str(dest_dir),
        ])
        
        assert result.returncode == 2
        output = json.loads(result.stdout)
        assert "network_not_allowed" in output["errors"]

    def test_cli_fetch_defaults_to_strict(self, tmp_path):
        """CLI fetch defaults to strict validation."""
        registry_path = tmp_path / "source" / "canon_key_registry_v0.1.json"
        registry_path.parent.mkdir(parents=True)
        registry_path.write_text(json.dumps({
            "registry_version": "v0.1",
            "updated_at": "2026-02-07T10:00:00Z",
            "current_keys": [],
            "previous_keys": [],
            "deprecated_keys": [],
        }))
        key = b"test-signing-key"

        build_result = build_registry_bundle(
            registry_path, key, tmp_path / "bundles"
        )
        bundle_dir = Path(build_result["bundle_dir"])
        key_path = tmp_path / "key.txt"
        key_path.write_bytes(key)
        dest_dir = tmp_path / "installed"

        result = self._run_cli([
            "--source", str(bundle_dir),
            "--key-file", str(key_path),
            "--dest", str(dest_dir),
        ])

        assert result.returncode == 1
        output = json.loads(result.stdout)
        assert "bundle_verify_failed" in output["errors"]
