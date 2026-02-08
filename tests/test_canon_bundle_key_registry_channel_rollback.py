"""
Tests for Canon Bundle Key Registry Channel Rollback Protection (Phase 131).
"""

import json
import pytest
import hashlib
from pathlib import Path
from unittest.mock import patch, MagicMock

from ilc_core.ledger.canon_bundle_key_registry_sync_state import (
    evaluate_channel_freshness,
    load_sync_state,
    write_sync_state,
    ChannelFreshnessState,
)
from ilc_core.ledger.canon_bundle_key_registry_sync import (
    sync_channel_registry,
    SyncContext,
)
from ilc_core.ledger.canon_bundle_key_registry_channel_signing import sign_channel_file

# Test Data Helpers
def create_v04_channel(path: Path, seq: int, published_at: str = "2026-02-08T12:00:00Z"):
    data = {
        "channel_version": "v0.4",
        "updated_at": published_at,
        "published_at": published_at,
        "channel_seq": seq,
        "current_channel": "main",
        "channels": ["main"],
        "sources": {"main": ["https://example.com"]},
    }
    path.write_text(json.dumps(data), encoding="utf-8")
    return data

def get_channel_hash(path: Path) -> str:
    from ilc_core.ledger.canon_bundle_key_registry_channel_signing import canonical_channel_bytes
    return hashlib.sha256(canonical_channel_bytes(path)).hexdigest()


class TestFreshnessEvaluation:
    def test_accepts_first_seen(self):
        ok, code = evaluate_channel_freshness(None, None, 10, "abc")
        assert ok is True
        assert code is None

    def test_accepts_higher_seq(self):
        ok, code = evaluate_channel_freshness(10, "abc", 11, "def")
        assert ok is True
        assert code is None

    def test_rejects_lower_seq(self):
        ok, code = evaluate_channel_freshness(10, "abc", 9, "def")
        assert ok is False
        assert code == "channel_rollback_detected"

    def test_rejects_equal_seq_hash_conflict(self):
        ok, code = evaluate_channel_freshness(10, "abc", 10, "def")
        assert ok is False
        assert code == "channel_seq_hash_conflict"

    def test_accepts_equal_seq_same_hash(self):
        ok, code = evaluate_channel_freshness(10, "abc", 10, "abc")
        assert ok is True
        assert code is None


class TestSyncStatePersistence:
    def test_write_and_load_state(self, tmp_path):
        state_path = tmp_path / "test.sync_state.json"
        state = ChannelFreshnessState(seen_seq=42, seen_hash="hash123", updated_at="2026-01-01T00:00:00Z")
        
        write_sync_state(state_path, state)
        loaded = load_sync_state(state_path)
        
        assert loaded == state
        assert loaded.seen_seq == 42
        
    def test_load_nonexistent_returns_none(self, tmp_path):
        assert load_sync_state(tmp_path / "missing.json") is None

    def test_load_corrupt_returns_none(self, tmp_path):
        p = tmp_path / "corrupt.json"
        p.write_text("{invalid_json", encoding="utf-8")
        assert load_sync_state(p) is None


class TestSyncIntegrationRollback:
    @pytest.fixture
    def ctx(self, tmp_path):
        channel_file = tmp_path / "channel.json"
        dest_dir = tmp_path / "installed"
        dest_dir.mkdir()
        return SyncContext(
            channel_file=channel_file,
            key=bytes.fromhex("00" * 32), # Use valid-length key to avoid other errors if meaningful
            dest_dir=dest_dir,
            allow_network=True, # Allow skipping validation check so we reach fetch
            channel_key=b"channel-key",
            prod=True,
        )

    def test_sync_updates_state_on_success(self, ctx, tmp_path):
        # 1. First sync with seq=1
        create_v04_channel(ctx.channel_file, seq=1)
        sign_channel_file(ctx.channel_file, ctx.channel_key)
        
        with patch("ilc_core.ledger.canon_bundle_key_registry_sync.fetch_registry_bundle") as mock_fetch:
             mock_fetch.return_value = {"ok": True, "registry_hash": "bundle1"}
             res = sync_channel_registry(ctx)
             
        assert res["ok"] is True
        assert res["seen_seq"] is None # First time
        
        # Verify state file written
        state = load_sync_state(ctx.channel_file.with_suffix(".json.sync_state.json"))
        assert state is not None
        assert state.seen_seq == 1
        
    def test_sync_rejects_rollback(self, ctx, tmp_path):
        # 1. Establish state seq=10
        state_path = ctx.channel_file.with_suffix(".json.sync_state.json")
        write_sync_state(state_path, ChannelFreshnessState(10, "hash_old", "time"))
        
        # 2. Try sync seq=5
        create_v04_channel(ctx.channel_file, seq=5)
        sign_channel_file(ctx.channel_file, ctx.channel_key)
        
        res = sync_channel_registry(ctx)
        assert res["ok"] is False
        assert "channel_rollback_detected" in res["errors"]
        assert res["rollback_check_applied"] is True
        
        # Verify state NOT updated
        state = load_sync_state(state_path)
        assert state.seen_seq == 10

    def test_sync_allows_rollback_with_override_nonprod(self, ctx, tmp_path):
        # Establish state seq=10
        state_path = ctx.channel_file.with_suffix(".json.sync_state.json")
        write_sync_state(state_path, ChannelFreshnessState(10, "hash_old", "time"))
        
        # Try sync seq=5 with override, NON-PROD
        create_v04_channel(ctx.channel_file, seq=5)
        sign_channel_file(ctx.channel_file, ctx.channel_key)
        ctx.allow_channel_rollback = True
        ctx.prod = False
        
        with patch("ilc_core.ledger.canon_bundle_key_registry_sync.fetch_registry_bundle") as mock_fetch:
             mock_fetch.return_value = {"ok": True}
             res = sync_channel_registry(ctx)

        assert res["ok"] is True
        assert res["rollback_override"] is True
        assert "channel_rollback_override_used" in res["warnings"]
        
        # Verify state UPDATED to lower seq (re-accepted)
        state = load_sync_state(state_path)
        assert state.seen_seq == 5
        
    def test_sync_rejects_override_without_force_in_prod(self, ctx, tmp_path):
        # Establish state seq=10
        state_path = ctx.channel_file.with_suffix(".json.sync_state.json")
        write_sync_state(state_path, ChannelFreshnessState(10, "hash_old", "time"))
        
        # Try sync seq=5 with override, PROD, NO FORCE
        create_v04_channel(ctx.channel_file, seq=5)
        sign_channel_file(ctx.channel_file, ctx.channel_key)
        ctx.allow_channel_rollback = True
        ctx.prod = True
        ctx.force = False
        
        res = sync_channel_registry(ctx)
        
        assert res["ok"] is False
        assert "rollback_override_requires_force_in_prod" in res["errors"]
        
    def test_sync_allows_override_with_force_in_prod(self, ctx, tmp_path):
         # Establish state seq=10
        state_path = ctx.channel_file.with_suffix(".json.sync_state.json")
        write_sync_state(state_path, ChannelFreshnessState(10, "hash_old", "time"))
        
        # Try sync seq=5 with override, PROD, FORCE
        create_v04_channel(ctx.channel_file, seq=5)
        sign_channel_file(ctx.channel_file, ctx.channel_key)
        ctx.allow_channel_rollback = True
        ctx.prod = True
        ctx.force = True
        
        with patch("ilc_core.ledger.canon_bundle_key_registry_sync.fetch_registry_bundle") as mock_fetch:
             mock_fetch.return_value = {"ok": True}
             res = sync_channel_registry(ctx)

        assert res["ok"] is True
        assert "channel_rollback_override_used" in res["warnings"]

    def test_v03_compatibility_warning(self, ctx):
        # v0.3 channel
        data = {
            "channel_version": "v0.3",
            "updated_at": "2026-01-01T00:00:00Z",
            "current_channel": "main",
            "channels": ["main"],
            "sources": {"main": ["https://ex.com"]}
        }
        ctx.channel_file.write_text(json.dumps(data))
        ctx.prod = False
        
        with patch("ilc_core.ledger.canon_bundle_key_registry_sync.fetch_registry_bundle") as mock_fetch:
             mock_fetch.return_value = {"ok": True}
             res = sync_channel_registry(ctx)
             
        assert res["ok"] is True
        assert "channel_version_v03_no_rollback_protection" in res["warnings"]
        assert res.get("rollback_check_applied") is False
