"""Tests for canon bundle key registry ops: rotate, backup, restore."""

import json
import pytest
from pathlib import Path

from ilc_core.ledger.canon_bundle_key_registry import (
    rotate_registry,
    backup_registry,
    restore_registry,
    validate_registry_file,
)


class TestRotateRegistry:
    """Tests for rotate_registry helper."""
    
    def _write_registry(self, tmp_path, data):
        path = tmp_path / "canon_key_registry_v0.1.json"
        path.write_text(json.dumps(data, indent=2))
        return path
    
    def test_basic_rotation(self, tmp_path):
        """Rotation moves keys correctly."""
        path = self._write_registry(tmp_path, {
            "registry_version": "v0.1",
            "updated_at": "2026-02-06T10:00:00Z",
            "current_keys": ["a1b2c3d4e5f6a7b8"],
            "previous_keys": ["1111111111111111"],
            "deprecated_keys": [],
        })
        
        result = rotate_registry(path, "ffffffffffffffff")
        assert result["ok"] is True
        assert result["old_current_keys"] == ["a1b2c3d4e5f6a7b8"]
        assert result["new_current_key"] == "ffffffffffffffff"
        
        # Verify file was updated
        data = json.loads(path.read_text())
        assert data["current_keys"] == ["ffffffffffffffff"]
        assert data["previous_keys"] == ["a1b2c3d4e5f6a7b8"]
        assert "1111111111111111" in data["deprecated_keys"]
    
    def test_invalid_new_key_id(self, tmp_path):
        """Rotation fails with invalid key format."""
        path = self._write_registry(tmp_path, {
            "registry_version": "v0.1",
            "updated_at": "2026-02-06T10:00:00Z",
            "current_keys": ["a1b2c3d4e5f6a7b8"],
            "previous_keys": [],
            "deprecated_keys": [],
        })
        
        result = rotate_registry(path, "invalid")
        assert result["ok"] is False
        assert result["error"] == "invalid_new_key_id"
    
    def test_key_already_exists(self, tmp_path):
        """Rotation fails if key already exists."""
        path = self._write_registry(tmp_path, {
            "registry_version": "v0.1",
            "updated_at": "2026-02-06T10:00:00Z",
            "current_keys": ["a1b2c3d4e5f6a7b8"],
            "previous_keys": [],
            "deprecated_keys": [],
        })
        
        result = rotate_registry(path, "a1b2c3d4e5f6a7b8")
        assert result["ok"] is False
        assert result["error"] == "key_already_exists"
    
    def test_validation_fails_without_force(self, tmp_path):
        """Rotation fails on invalid registry without --force."""
        path = self._write_registry(tmp_path, {
            "registry_version": "invalid",
            "updated_at": "2026-02-06T10:00:00Z",
            "current_keys": [],
            "previous_keys": [],
            "deprecated_keys": [],
        })
        
        result = rotate_registry(path, "ffffffffffffffff")
        assert result["ok"] is False
        assert result["error"] == "validation_failed"
    
    def test_validation_succeeds_with_force(self, tmp_path):
        """Rotation works on invalid registry with --force."""
        path = self._write_registry(tmp_path, {
            "registry_version": "invalid",
            "updated_at": "2026-02-06T10:00:00Z",
            "current_keys": [],
            "previous_keys": [],
            "deprecated_keys": [],
        })
        
        result = rotate_registry(path, "ffffffffffffffff", force=True)
        assert result["ok"] is True
        assert result["new_current_key"] == "ffffffffffffffff"
    
    def test_signature_invalidated(self, tmp_path):
        """Rotation deletes existing .sig file."""
        path = self._write_registry(tmp_path, {
            "registry_version": "v0.1",
            "updated_at": "2026-02-06T10:00:00Z",
            "current_keys": ["a1b2c3d4e5f6a7b8"],
            "previous_keys": [],
            "deprecated_keys": [],
        })
        sig_path = path.with_suffix(path.suffix + ".sig")
        sig_path.write_text("{}")
        
        result = rotate_registry(path, "ffffffffffffffff")
        assert result["ok"] is True
        assert "signature_invalidated" in result["warnings"]
        assert not sig_path.exists()
    
    def test_updated_at_is_updated(self, tmp_path):
        """Rotation updates updated_at timestamp."""
        path = self._write_registry(tmp_path, {
            "registry_version": "v0.1",
            "updated_at": "2020-01-01T00:00:00Z",
            "current_keys": ["a1b2c3d4e5f6a7b8"],
            "previous_keys": [],
            "deprecated_keys": [],
        })
        
        result = rotate_registry(path, "ffffffffffffffff")
        assert result["ok"] is True
        assert result["updated_at"] != "2020-01-01T00:00:00Z"
        assert "2026" in result["updated_at"]  # Current year


class TestBackupRegistry:
    """Tests for backup_registry helper."""
    
    def _write_registry(self, tmp_path, data):
        path = tmp_path / "canon_key_registry_v0.1.json"
        path.write_text(json.dumps(data, indent=2))
        return path
    
    def test_backup_creates_file(self, tmp_path):
        """Backup creates timestamped file."""
        path = self._write_registry(tmp_path, {
            "registry_version": "v0.1",
            "updated_at": "2026-02-06T10:00:00Z",
            "current_keys": ["a1b2c3d4e5f6a7b8"],
            "previous_keys": [],
            "deprecated_keys": [],
        })
        backup_dir = tmp_path / "backups"
        
        result = backup_registry(path, backup_dir)
        assert result["ok"] is True
        assert result["backup_path"]
        
        backup_path = Path(result["backup_path"])
        assert backup_path.exists()
        assert ".bak" in backup_path.name
    
    def test_backup_preserves_content(self, tmp_path):
        """Backup content matches original."""
        data = {
            "registry_version": "v0.1",
            "updated_at": "2026-02-06T10:00:00Z",
            "current_keys": ["a1b2c3d4e5f6a7b8"],
            "previous_keys": [],
            "deprecated_keys": [],
        }
        path = self._write_registry(tmp_path, data)
        backup_dir = tmp_path / "backups"
        
        result = backup_registry(path, backup_dir)
        backup_path = Path(result["backup_path"])
        backup_data = json.loads(backup_path.read_text())
        assert backup_data == data
    
    def test_backup_creates_directory(self, tmp_path):
        """Backup creates directory if needed."""
        path = self._write_registry(tmp_path, {
            "registry_version": "v0.1",
            "updated_at": "2026-02-06T10:00:00Z",
            "current_keys": [],
            "previous_keys": [],
            "deprecated_keys": [],
        })
        backup_dir = tmp_path / "nested" / "backup" / "dir"
        
        result = backup_registry(path, backup_dir)
        assert result["ok"] is True
        assert backup_dir.exists()


class TestRestoreRegistry:
    """Tests for restore_registry helper."""
    
    def _write_json(self, path, data):
        path.write_text(json.dumps(data, indent=2))
        return path
    
    def test_restore_replaces_content(self, tmp_path):
        """Restore replaces registry content."""
        registry_path = tmp_path / "registry.json"
        self._write_json(registry_path, {
            "registry_version": "v0.1",
            "updated_at": "2026-02-06T10:00:00Z",
            "current_keys": [],
            "previous_keys": [],
            "deprecated_keys": [],
        })
        
        backup_path = tmp_path / "backup.json"
        self._write_json(backup_path, {
            "registry_version": "v0.1",
            "updated_at": "2026-02-06T10:00:00Z",
            "current_keys": ["a1b2c3d4e5f6a7b8"],
            "previous_keys": [],
            "deprecated_keys": [],
        })
        
        result = restore_registry(backup_path, registry_path)
        assert result["ok"] is True
        
        data = json.loads(registry_path.read_text())
        assert data["current_keys"] == ["a1b2c3d4e5f6a7b8"]
    
    def test_restore_validates_backup(self, tmp_path):
        """Restore fails on invalid backup."""
        registry_path = tmp_path / "registry.json"
        self._write_json(registry_path, {
            "registry_version": "v0.1",
            "updated_at": "2026-02-06T10:00:00Z",
            "current_keys": [],
            "previous_keys": [],
            "deprecated_keys": [],
        })
        
        backup_path = tmp_path / "backup.json"
        self._write_json(backup_path, {"invalid": "data"})
        
        result = restore_registry(backup_path, registry_path)
        assert result["ok"] is False
        assert result["error"] == "backup_validation_failed"
    
    def test_restore_backup_not_found(self, tmp_path):
        """Restore fails when backup not found."""
        registry_path = tmp_path / "registry.json"
        backup_path = tmp_path / "nonexistent.json"
        
        result = restore_registry(backup_path, registry_path)
        assert result["ok"] is False
        assert result["error"] == "backup_not_found"
    
    def test_restore_deletes_sig(self, tmp_path):
        """Restore deletes existing .sig file."""
        registry_path = tmp_path / "registry.json"
        self._write_json(registry_path, {
            "registry_version": "v0.1",
            "updated_at": "2026-02-06T10:00:00Z",
            "current_keys": [],
            "previous_keys": [],
            "deprecated_keys": [],
        })
        sig_path = registry_path.with_suffix(registry_path.suffix + ".sig")
        sig_path.write_text("{}")
        
        backup_path = tmp_path / "backup.json"
        self._write_json(backup_path, {
            "registry_version": "v0.1",
            "updated_at": "2026-02-06T10:00:00Z",
            "current_keys": ["a1b2c3d4e5f6a7b8"],
            "previous_keys": [],
            "deprecated_keys": [],
        })
        
        result = restore_registry(backup_path, registry_path)
        assert result["ok"] is True
        assert not sig_path.exists()


class TestOpsCli:
    """Tests for CLI ops commands."""
    
    def _write_registry(self, tmp_path, data):
        path = tmp_path / "canon_key_registry_v0.1.json"
        path.write_text(json.dumps(data, indent=2))
        return path
    
    def _run_cli(self, args):
        import subprocess
        return subprocess.run(
            ["python3", "-m", "ilc_core.cli.canon_bundle_key_registry"] + args,
            capture_output=True,
            text=True,
            cwd="/Users/jamstar/Documents/ILC_Main/01_Current"
        )
    
    def test_cli_rotate(self, tmp_path):
        """CLI --rotate works."""
        path = self._write_registry(tmp_path, {
            "registry_version": "v0.1",
            "updated_at": "2026-02-06T10:00:00Z",
            "current_keys": ["a1b2c3d4e5f6a7b8"],
            "previous_keys": [],
            "deprecated_keys": [],
        })
        
        result = self._run_cli(["--registry", str(path), "--rotate", "--new-key-id", "ffffffffffffffff"])
        assert result.returncode == 0
        output = json.loads(result.stdout)
        assert output["ok"] is True
        assert output["rotation"] is True
        assert output["new_current_key"] == "ffffffffffffffff"
    
    def test_cli_rotate_missing_key_id(self, tmp_path):
        """CLI --rotate without --new-key-id fails."""
        path = self._write_registry(tmp_path, {
            "registry_version": "v0.1",
            "updated_at": "2026-02-06T10:00:00Z",
            "current_keys": ["a1b2c3d4e5f6a7b8"],
            "previous_keys": [],
            "deprecated_keys": [],
        })
        
        result = self._run_cli(["--registry", str(path), "--rotate"])
        assert result.returncode == 1
        output = json.loads(result.stdout)
        assert "new_key_id_required" in output["errors"]
    
    def test_cli_backup_dir(self, tmp_path):
        """CLI --backup-dir works."""
        path = self._write_registry(tmp_path, {
            "registry_version": "v0.1",
            "updated_at": "2026-02-06T10:00:00Z",
            "current_keys": ["a1b2c3d4e5f6a7b8"],
            "previous_keys": [],
            "deprecated_keys": [],
        })
        backup_dir = tmp_path / "backups"
        
        result = self._run_cli(["--registry", str(path), "--backup-dir", str(backup_dir)])
        assert result.returncode == 0
        output = json.loads(result.stdout)
        assert output["ok"] is True
        assert output["backup_path"]
    
    def test_cli_restore(self, tmp_path):
        """CLI --restore works."""
        path = self._write_registry(tmp_path, {
            "registry_version": "v0.1",
            "updated_at": "2026-02-06T10:00:00Z",
            "current_keys": [],
            "previous_keys": [],
            "deprecated_keys": [],
        })
        
        backup_path = tmp_path / "backup.json"
        backup_path.write_text(json.dumps({
            "registry_version": "v0.1",
            "updated_at": "2026-02-06T10:00:00Z",
            "current_keys": ["a1b2c3d4e5f6a7b8"],
            "previous_keys": [],
            "deprecated_keys": [],
        }))
        
        result = self._run_cli(["--registry", str(path), "--restore", str(backup_path)])
        assert result.returncode == 0
        output = json.loads(result.stdout)
        assert output["ok"] is True
    
    def test_cli_restore_prod_requires_force(self, tmp_path):
        """Prod restore fails on empty current_keys unless --force."""
        path = self._write_registry(tmp_path, {
            "registry_version": "v0.1",
            "updated_at": "2026-02-06T10:00:00Z",
            "current_keys": ["a1b2c3d4e5f6a7b8"],
            "previous_keys": [],
            "deprecated_keys": [],
        })
        
        backup_path = tmp_path / "backup.json"
        backup_path.write_text(json.dumps({
            "registry_version": "v0.1",
            "updated_at": "2026-02-06T10:00:00Z",
            "current_keys": [],
            "previous_keys": [],
            "deprecated_keys": [],
        }))
        
        result = self._run_cli([
            "--registry", str(path),
            "--restore", str(backup_path),
            "--prod",
        ])
        assert result.returncode == 1
        output = json.loads(result.stdout)
        assert output["ok"] is False
        assert (
            "backup_validation_failed" in output["errors"] or
            "prod_empty_registry" in output["errors"]
        )
        
        result = self._run_cli([
            "--registry", str(path),
            "--restore", str(backup_path),
            "--prod",
            "--force",
        ])
        assert result.returncode == 0
        output = json.loads(result.stdout)
        assert output["ok"] is True
        if "warnings" in output:
            assert "validation_bypassed" in output["warnings"]
    
    def test_cli_restore_prod_validation_error(self, tmp_path):
        """Prod restore rejects invalid backup."""
        path = self._write_registry(tmp_path, {
            "registry_version": "v0.1",
            "updated_at": "2026-02-06T10:00:00Z",
            "current_keys": ["a1b2c3d4e5f6a7b8"],
            "previous_keys": [],
            "deprecated_keys": [],
        })
        
        backup_path = tmp_path / "backup_invalid.json"
        backup_path.write_text(json.dumps({"invalid": "data"}))
        
        result = self._run_cli([
            "--registry", str(path),
            "--restore", str(backup_path),
        ])
        assert result.returncode == 1
        output = json.loads(result.stdout)
        assert output["ok"] is False
        assert (
            "backup_validation_failed" in output["errors"] or
            "backup_invalid" in output["errors"]
        )
        
        result = self._run_cli([
            "--registry", str(path),
            "--restore", str(backup_path),
            "--prod",
        ])
        assert result.returncode == 1
        output = json.loads(result.stdout)
        assert output["ok"] is False
        assert (
            "backup_validation_failed" in output["errors"] or
            "backup_invalid" in output["errors"]
        )
    
    def test_cli_prod_rotation_requires_force(self, tmp_path):
        """In prod mode, rotation requires --force."""
        path = self._write_registry(tmp_path, {
            "registry_version": "v0.1",
            "updated_at": "2026-02-06T10:00:00Z",
            "current_keys": ["a1b2c3d4e5f6a7b8"],
            "previous_keys": [],
            "deprecated_keys": [],
        })
        
        result = self._run_cli(["--registry", str(path), "--prod", "--rotate", "--new-key-id", "ffffffffffffffff"])
        assert result.returncode == 1
        output = json.loads(result.stdout)
        assert "prod_rotation_requires_force" in output["errors"]
    
    def test_cli_prod_rotation_with_force(self, tmp_path):
        """In prod mode, rotation works with --force."""
        path = self._write_registry(tmp_path, {
            "registry_version": "v0.1",
            "updated_at": "2026-02-06T10:00:00Z",
            "current_keys": ["a1b2c3d4e5f6a7b8"],
            "previous_keys": [],
            "deprecated_keys": [],
        })
        
        result = self._run_cli(["--registry", str(path), "--prod", "--rotate", "--new-key-id", "ffffffffffffffff", "--force"])
        assert result.returncode == 0
        output = json.loads(result.stdout)
        assert output["ok"] is True
    
    def test_cli_registry_dir_with_rotate(self, tmp_path):
        """CLI --registry-dir works with --rotate."""
        registry_dir = tmp_path / "config"
        registry_dir.mkdir()
        path = registry_dir / "canon_key_registry_v0.1.json"
        path.write_text(json.dumps({
            "registry_version": "v0.1",
            "updated_at": "2026-02-06T10:00:00Z",
            "current_keys": ["a1b2c3d4e5f6a7b8"],
            "previous_keys": [],
            "deprecated_keys": [],
        }))
        
        result = self._run_cli(["--registry-dir", str(registry_dir), "--rotate", "--new-key-id", "ffffffffffffffff"])
        assert result.returncode == 0
        output = json.loads(result.stdout)
        assert output["ok"] is True
