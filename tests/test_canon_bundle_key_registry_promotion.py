"""Tests for canon bundle key registry promotion."""

import json
import os
import pytest
from pathlib import Path

from ilc_core.ledger.canon_bundle_key_registry_bundle import build_registry_bundle
from ilc_core.ledger.canon_bundle_key_registry_promotion import promote_bundle


class TestPromoteBundle:
    """Tests for promote_bundle helper."""
    
    def _create_bundle_and_channel(self, tmp_path, channel_name="test"):
        """Create a valid bundle and channel file."""
        # Create registry
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
        
        # Build bundle
        src_dir = tmp_path / channel_name
        build_registry_bundle(registry_path, key, src_dir)
        
        # Create channel file
        channel_file = tmp_path / "channel.json"
        channel_file.write_text(json.dumps({
            "channel_version": "v0.1",
            "updated_at": "2026-02-07T10:00:00Z",
            "current_channel": channel_name,
            "channels": ["experimental", "main", "test"],
            "channel_order": ["experimental", "test", "main"],
        }, indent=2))
        
        return src_dir, channel_file, key
    
    def test_promotion_succeeds_between_valid_channels(self, tmp_path):
        """Promotion succeeds between valid channels."""
        src_dir, channel_file, key = self._create_bundle_and_channel(tmp_path, "test")
        dest_dir = tmp_path / "main_dest"
        
        result = promote_bundle(
            src_dir, dest_dir, channel_file, "test", "main", key
        )
        
        assert result["ok"] is True
        assert (dest_dir / "canon_key_registry_bundle_v0.1").exists()
        assert result["last_promotion"]["from"] == "test"
        assert result["last_promotion"]["to"] == "main"
    
    def test_promotion_fails_if_src_bundle_invalid(self, tmp_path):
        """Promotion fails if source bundle is invalid."""
        # Create invalid bundle
        src_dir = tmp_path / "test"
        (src_dir / "canon_key_registry_bundle_v0.1").mkdir(parents=True)
        (src_dir / "canon_key_registry_bundle_v0.1" / "junk.txt").write_text("noise")
        
        channel_file = tmp_path / "channel.json"
        channel_file.write_text(json.dumps({
            "channel_version": "v0.1",
            "updated_at": "2026-02-07T10:00:00Z",
            "current_channel": "test",
            "channels": ["main", "test"],
        }))
        
        dest_dir = tmp_path / "main_dest"
        key = b"test-signing-key"
        
        result = promote_bundle(
            src_dir, dest_dir, channel_file, "test", "main", key
        )
        
        assert result["ok"] is False
        assert "bundle_verify_failed" in result["errors"]
    
    def test_promotion_respects_channel_order(self, tmp_path):
        """Promotion respects channel_order (cannot promote backwards)."""
        src_dir, channel_file, key = self._create_bundle_and_channel(tmp_path, "test")
        dest_dir = tmp_path / "exp_dest"
        
        # Try to promote backwards: test -> experimental
        result = promote_bundle(
            src_dir, dest_dir, channel_file, "test", "experimental", key
        )
        
        assert result["ok"] is False
        assert "channel_order_violation" in result["errors"]
    
    def test_dry_run_returns_plan_without_modifications(self, tmp_path):
        """Dry run returns plan without making changes."""
        src_dir, channel_file, key = self._create_bundle_and_channel(tmp_path, "test")
        dest_dir = tmp_path / "main_dest"
        
        result = promote_bundle(
            src_dir, dest_dir, channel_file, "test", "main", key, dry_run=True
        )
        
        assert result["ok"] is True
        assert result["dry_run"] is True
        assert len(result["actions"]) > 0
        assert not (dest_dir / "canon_key_registry_bundle_v0.1").exists()
    
    def test_switch_flag_updates_current_channel(self, tmp_path):
        """Switch flag updates current_channel."""
        src_dir, channel_file, key = self._create_bundle_and_channel(tmp_path, "test")
        dest_dir = tmp_path / "main_dest"
        
        result = promote_bundle(
            src_dir, dest_dir, channel_file, "test", "main", key, switch=True
        )
        
        assert result["ok"] is True
        
        # Verify channel file updated
        data = json.loads(channel_file.read_text())
        assert data["current_channel"] == "main"
    
    def test_promotion_rejects_same_channel_without_force(self, tmp_path):
        """Promotion rejects src == dest without force."""
        src_dir, channel_file, key = self._create_bundle_and_channel(tmp_path, "test")
        dest_dir = tmp_path / "test_dest"
        
        result = promote_bundle(
            src_dir, dest_dir, channel_file, "test", "test", key
        )
        
        assert result["ok"] is False
        assert "channel_same_as_source" in result["errors"]
    
    def test_promotion_warns_when_channel_order_missing(self, tmp_path):
        """Promotion warns when channel_order is missing."""
        src_dir, channel_file, key = self._create_bundle_and_channel(tmp_path, "test")
        
        # Remove channel_order
        data = json.loads(channel_file.read_text())
        del data["channel_order"]
        channel_file.write_text(json.dumps(data))
        
        dest_dir = tmp_path / "main_dest"
        
        result = promote_bundle(
            src_dir, dest_dir, channel_file, "test", "main", key
        )
        
        assert result["ok"] is True
        assert "channel_order_missing" in result["warnings"]

    def test_promotion_fails_when_channel_order_incomplete(self, tmp_path):
        """Promotion fails when channel_order is missing src/dest entries."""
        src_dir, channel_file, key = self._create_bundle_and_channel(tmp_path, "test")

        data = json.loads(channel_file.read_text())
        data["channel_order"] = ["experimental", "main"]
        channel_file.write_text(json.dumps(data))

        dest_dir = tmp_path / "main_dest"
        result = promote_bundle(
            src_dir, dest_dir, channel_file, "test", "main", key
        )

        assert result["ok"] is False
        assert "channel_order_incomplete" in result["errors"]

    def test_promotion_updates_last_promotion_in_channel_file(self, tmp_path):
        """Promotion updates last_promotion in channel file."""
        src_dir, channel_file, key = self._create_bundle_and_channel(tmp_path, "test")
        dest_dir = tmp_path / "main_dest"
        
        result = promote_bundle(
            src_dir, dest_dir, channel_file, "test", "main", key
        )
        
        assert result["ok"] is True
        
        data = json.loads(channel_file.read_text())
        assert "last_promotion" in data
        assert data["last_promotion"]["from"] == "test"
        assert data["last_promotion"]["to"] == "main"

    def test_promotion_accepts_explicit_timestamp(self, tmp_path):
        src_dir, channel_file, key = self._create_bundle_and_channel(tmp_path, "test")
        dest_dir = tmp_path / "main_dest"

        result = promote_bundle(
            src_dir,
            dest_dir,
            channel_file,
            "test",
            "main",
            key,
            timestamp="2026-04-14T13:15:00Z",
        )

        assert result["ok"] is True
        assert result["last_promotion"]["timestamp"] == "2026-04-14T13:15:00Z"
        data = json.loads(channel_file.read_text(encoding="utf-8"))
        assert data["updated_at"] == "2026-04-14T13:15:00Z"
    
    def test_promotion_fails_if_bundle_missing(self, tmp_path):
        """Promotion fails if bundle is missing."""
        src_dir = tmp_path / "test"
        src_dir.mkdir()
        
        channel_file = tmp_path / "channel.json"
        channel_file.write_text(json.dumps({
            "channel_version": "v0.1",
            "updated_at": "2026-02-07T10:00:00Z",
            "current_channel": "test",
            "channels": ["main", "test"],
        }))
        
        dest_dir = tmp_path / "main_dest"
        key = b"test-signing-key"
        
        result = promote_bundle(
            src_dir, dest_dir, channel_file, "test", "main", key
        )
        
        assert result["ok"] is False
        assert "bundle_missing" in result["errors"]

    def test_promotion_fails_when_src_not_readable(self, tmp_path, monkeypatch):
        """Promotion fails when src is not readable."""
        src_dir, channel_file, key = self._create_bundle_and_channel(tmp_path, "test")
        dest_dir = tmp_path / "main_dest"

        def fake_access(path, mode):
            if Path(path) == src_dir and mode == os.R_OK:
                return False
            return True

        monkeypatch.setattr(
            "ilc_core.ledger.canon_bundle_key_registry_promotion.os.access",
            fake_access,
        )

        result = promote_bundle(
            src_dir, dest_dir, channel_file, "test", "main", key
        )

        assert result["ok"] is False
        assert "src_not_readable" in result["errors"]

    def test_promotion_fails_when_dest_not_writable(self, tmp_path, monkeypatch):
        """Promotion fails when dest is not writable."""
        src_dir, channel_file, key = self._create_bundle_and_channel(tmp_path, "test")
        dest_dir = tmp_path / "main_dest"

        def fake_access(path, mode):
            if Path(path) == dest_dir.parent and mode == os.W_OK:
                return False
            return True

        monkeypatch.setattr(
            "ilc_core.ledger.canon_bundle_key_registry_promotion.os.access",
            fake_access,
        )

        result = promote_bundle(
            src_dir, dest_dir, channel_file, "test", "main", key
        )

        assert result["ok"] is False
        assert "dest_not_writable" in result["errors"]


class TestPromotionCli:
    """Tests for promotion CLI."""
    
    def _create_bundle_and_channel(self, tmp_path, channel_name="test"):
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
        
        src_dir = tmp_path / channel_name
        build_registry_bundle(registry_path, key, src_dir)
        
        channel_file = tmp_path / "channel.json"
        channel_file.write_text(json.dumps({
            "channel_version": "v0.1",
            "updated_at": "2026-02-07T10:00:00Z",
            "current_channel": channel_name,
            "channels": ["main", "test"],
        }, indent=2))
        
        key_file = tmp_path / "key.txt"
        key_file.write_bytes(key)
        
        return src_dir, channel_file, key_file
    
    def _run_cli(self, args):
        import subprocess
        return subprocess.run(
            ["python3", "-m", "ilc_core.cli.canon_bundle_key_registry_promotion"] + args,
            capture_output=True,
            text=True,
            cwd="/Users/jamstar/Documents/ILC_Main/01_Current"
        )
    
    def test_cli_promotion_succeeds(self, tmp_path):
        """CLI promotion succeeds."""
        src_dir, channel_file, key_file = self._create_bundle_and_channel(tmp_path)
        dest_dir = tmp_path / "main_dest"
        
        result = self._run_cli([
            "--src", str(src_dir),
            "--dest", str(dest_dir),
            "--channel-file", str(channel_file),
            "--from", "test",
            "--to", "main",
            "--key-file", str(key_file),
        ])
        
        assert result.returncode == 0
        output = json.loads(result.stdout)
        assert output["ok"] is True
    
    def test_cli_dry_run(self, tmp_path):
        """CLI dry run works."""
        src_dir, channel_file, key_file = self._create_bundle_and_channel(tmp_path)
        dest_dir = tmp_path / "main_dest"
        
        result = self._run_cli([
            "--src", str(src_dir),
            "--dest", str(dest_dir),
            "--channel-file", str(channel_file),
            "--from", "test",
            "--to", "main",
            "--key-file", str(key_file),
            "--dry-run",
        ])
        
        assert result.returncode == 0
        output = json.loads(result.stdout)
        assert output["dry_run"] is True
