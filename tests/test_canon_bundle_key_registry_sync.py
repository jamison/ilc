"""Tests for canon bundle key registry sync."""

import json
import pytest
from pathlib import Path

from ilc_core.ledger.canon_bundle_key_registry_bundle import build_registry_bundle
from ilc_core.ledger.canon_bundle_key_registry_sync import sync_channel_registry


class TestSyncChannelRegistry:
    """Tests for sync_channel_registry helper."""
    
    def _create_bundle_and_channel(self, tmp_path, channel_name="main"):
        """Create a valid bundle and v0.2 channel file with sources."""
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
        bundle_parent = tmp_path / "bundles" / channel_name
        build_registry_bundle(registry_path, key, bundle_parent)
        # The actual bundle is at bundle_parent / "canon_key_registry_bundle_v0.1"
        bundle_dir = bundle_parent / "canon_key_registry_bundle_v0.1"
        
        # Create channel file with sources pointing to actual bundle
        channel_file = tmp_path / "channel.json"
        channel_file.write_text(json.dumps({
            "channel_version": "v0.2",
            "updated_at": "2026-02-07T10:00:00Z",
            "current_channel": channel_name,
            "channels": ["experimental", "main", "test"],
            "sources": {
                "experimental": [str(bundle_dir)],
                "main": [str(bundle_dir)],
                "test": [str(bundle_dir)],
            },
        }, indent=2))
        
        return bundle_dir, channel_file, key
    
    def test_sync_succeeds_for_valid_channel_local_source(self, tmp_path):
        """Sync succeeds for valid channel with local source."""
        bundle_dir, channel_file, key = self._create_bundle_and_channel(tmp_path)
        dest_dir = tmp_path / "installed"
        
        result = sync_channel_registry(
            channel_file, key, dest_dir, channel="main"
        )
        
        assert result["ok"] is True
        assert result["channel"] == "main"
        assert (dest_dir / "canon_key_registry_bundle_v0.1").exists()
    
    def test_sync_fails_for_missing_sources_mapping(self, tmp_path):
        """Sync fails when sources mapping is missing."""
        channel_file = tmp_path / "channel.json"
        channel_file.write_text(json.dumps({
            "channel_version": "v0.2",
            "updated_at": "2026-02-07T10:00:00Z",
            "current_channel": "main",
            "channels": ["main"],
        }))
        
        key = b"test-signing-key"
        dest_dir = tmp_path / "installed"
        
        result = sync_channel_registry(
            channel_file, key, dest_dir, channel="main"
        )
        
        assert result["ok"] is False
        assert "sources_missing" in result["errors"]

        data = json.loads(channel_file.read_text())
        assert "last_sync" in data
        assert data["last_sync"]["ok"] is False
        assert "sources_missing" in data["last_sync"]["errors"]
    
    def test_sync_fails_for_source_index_out_of_range(self, tmp_path):
        """Sync fails when source_index is out of range."""
        bundle_dir, channel_file, key = self._create_bundle_and_channel(tmp_path)
        dest_dir = tmp_path / "installed"
        
        result = sync_channel_registry(
            channel_file, key, dest_dir, channel="main", source_index=5
        )
        
        assert result["ok"] is False
        assert "source_index_out_of_range" in result["errors"]
    
    def test_sync_respects_allow_network_flag(self, tmp_path):
        """Sync respects allow_network flag for https sources."""
        channel_file = tmp_path / "channel.json"
        channel_file.write_text(json.dumps({
            "channel_version": "v0.2",
            "updated_at": "2026-02-07T10:00:00Z",
            "current_channel": "main",
            "channels": ["main"],
            "sources": {
                "main": ["https://example.com/bundle.tar.gz"],
            },
        }))
        
        key = b"test-signing-key"
        dest_dir = tmp_path / "installed"
        
        result = sync_channel_registry(
            channel_file, key, dest_dir, channel="main", allow_network=False
        )
        
        assert result["ok"] is False
        assert "network_disabled" in result["errors"]
    
    def test_last_sync_updated_on_success(self, tmp_path):
        """last_sync is updated on successful sync."""
        bundle_dir, channel_file, key = self._create_bundle_and_channel(tmp_path)
        dest_dir = tmp_path / "installed"
        
        result = sync_channel_registry(
            channel_file, key, dest_dir, channel="main"
        )
        
        assert result["ok"] is True
        
        data = json.loads(channel_file.read_text())
        assert "last_sync" in data
        assert data["last_sync"]["ok"] is True
        assert data["last_sync"]["channel"] == "main"
    
    def test_last_sync_updated_on_failure(self, tmp_path):
        """last_sync is updated even on failed sync."""
        # Create channel with invalid bundle source (not a valid bundle dir)
        invalid_bundle_dir = tmp_path / "invalid" / "canon_key_registry_bundle_v0.1"
        invalid_bundle_dir.mkdir(parents=True)
        (invalid_bundle_dir / "junk.txt").write_text("x")
        
        channel_file = tmp_path / "channel.json"
        channel_file.write_text(json.dumps({
            "channel_version": "v0.2",
            "updated_at": "2026-02-07T10:00:00Z",
            "current_channel": "main",
            "channels": ["main"],
            "sources": {
                "main": [str(invalid_bundle_dir)],
            },
        }))
        
        key = b"test-signing-key"
        dest_dir = tmp_path / "installed"
        
        result = sync_channel_registry(
            channel_file, key, dest_dir, channel="main"
        )
        
        assert result["ok"] is False
        
        data = json.loads(channel_file.read_text())
        assert "last_sync" in data
        assert data["last_sync"]["ok"] is False
    
    def test_dry_run_returns_plan(self, tmp_path):
        """Dry run returns plan without modifications."""
        bundle_dir, channel_file, key = self._create_bundle_and_channel(tmp_path)
        dest_dir = tmp_path / "installed"
        
        result = sync_channel_registry(
            channel_file, key, dest_dir, channel="main", dry_run=True
        )
        
        assert result["ok"] is True
        assert result["dry_run"] is True
        assert "actions" in result
        assert not (dest_dir / "canon_key_registry_bundle_v0.1").exists()
    
    def test_force_required_when_dest_exists(self, tmp_path):
        """Force is required when dest already has bundle."""
        bundle_dir, channel_file, key = self._create_bundle_and_channel(tmp_path)
        dest_dir = tmp_path / "installed"
        
        # First sync
        result1 = sync_channel_registry(
            channel_file, key, dest_dir, channel="main"
        )
        assert result1["ok"] is True
        
        # Second sync without force should fail
        result2 = sync_channel_registry(
            channel_file, key, dest_dir, channel="main"
        )
        assert result2["ok"] is False
        assert "dest_exists" in result2["errors"]
    
    def test_sync_uses_current_channel_by_default(self, tmp_path):
        """Sync uses current_channel when channel not specified."""
        bundle_dir, channel_file, key = self._create_bundle_and_channel(tmp_path, "test")
        
        # Update current_channel
        data = json.loads(channel_file.read_text())
        data["current_channel"] = "test"
        channel_file.write_text(json.dumps(data))
        
        dest_dir = tmp_path / "installed"
        
        result = sync_channel_registry(
            channel_file, key, dest_dir
        )
        
        assert result["ok"] is True
        assert result["channel"] == "test"


class TestSyncCli:
    """Tests for sync CLI."""
    
    def _create_bundle_and_channel(self, tmp_path, channel_name="main"):
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
        
        bundle_parent = tmp_path / "bundles" / channel_name
        build_registry_bundle(registry_path, key, bundle_parent)
        bundle_dir = bundle_parent / "canon_key_registry_bundle_v0.1"
        
        channel_file = tmp_path / "channel.json"
        channel_file.write_text(json.dumps({
            "channel_version": "v0.2",
            "updated_at": "2026-02-07T10:00:00Z",
            "current_channel": channel_name,
            "channels": [channel_name],
            "sources": {
                channel_name: [str(bundle_dir)],
            },
        }, indent=2))
        
        key_file = tmp_path / "key.txt"
        key_file.write_bytes(key)
        
        return bundle_dir, channel_file, key_file
    
    def _run_cli(self, args):
        import subprocess
        return subprocess.run(
            ["python3", "-m", "ilc_core.cli.canon_bundle_key_registry_sync"] + args,
            capture_output=True,
            text=True,
            cwd="/Users/jamstar/Documents/ILC_Main/01_Current"
        )
    
    def test_cli_sync_succeeds(self, tmp_path):
        """CLI sync succeeds."""
        bundle_dir, channel_file, key_file = self._create_bundle_and_channel(tmp_path)
        dest_dir = tmp_path / "installed"
        
        result = self._run_cli([
            "--channel-file", str(channel_file),
            "--key-file", str(key_file),
            "--dest", str(dest_dir),
        ])
        
        assert result.returncode == 0
        output = json.loads(result.stdout)
        assert output["ok"] is True
    
    def test_cli_dry_run(self, tmp_path):
        """CLI dry run works."""
        bundle_dir, channel_file, key_file = self._create_bundle_and_channel(tmp_path)
        dest_dir = tmp_path / "installed"
        
        result = self._run_cli([
            "--channel-file", str(channel_file),
            "--key-file", str(key_file),
            "--dest", str(dest_dir),
            "--dry-run",
        ])
        
        assert result.returncode == 0
        output = json.loads(result.stdout)
        assert output["dry_run"] is True
    
    def test_cli_validation_error_returns_1(self, tmp_path):
        """CLI returns 1 for validation errors."""
        channel_file = tmp_path / "channel.json"
        channel_file.write_text(json.dumps({
            "channel_version": "v0.2",
            "updated_at": "2026-02-07T10:00:00Z",
            "current_channel": "main",
            "channels": ["main"],
        }))
        key_file = tmp_path / "key.txt"
        key_file.write_bytes(b"test-key")
        dest_dir = tmp_path / "installed"
        
        result = self._run_cli([
            "--channel-file", str(channel_file),
            "--key-file", str(key_file),
            "--dest", str(dest_dir),
        ])
        
        assert result.returncode == 1
        output = json.loads(result.stdout)
        assert "sources_missing" in output["errors"]
