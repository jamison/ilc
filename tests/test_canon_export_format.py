import pytest
from datetime import datetime
from ilc_core.ledger.canon_export_format import export_canon_format_v0_1

class TestCanonExportFormat:
    
    def test_export_format_minimal(self):
        """Verify minimal valid input produces compliant output."""
        canon_state = {
            "canon_hash": "hash_123",
            "canon_export_version": "v0.0.1",
            # Optional fields omitted implies empty defaults
        }
        
        export = export_canon_format_v0_1(canon_state, exported_at="2026-02-05T00:00:00+00:00")
        
        assert export["canon_export_format"] == "v0.1"
        assert export["canon_hash"] == "hash_123"
        assert export["exported_at"] == "2026-02-05T00:00:00+00:00"
        
        meta = export["meta"]
        assert meta["canon_export_version"] == "v0.0.1"
        assert meta["epoch_count"] == 0
        assert meta["snapshot_count"] == 0
        assert meta["balance_count"] == 0
        
        assert export["epochs"] == []
        assert export["snapshots"] == []
        assert export["kpis"]["epoch_count"] == 0

    def test_export_format_full_populated(self):
        """Verify fully populated input maps correctly."""
        canon_state = {
            "canon_hash": "hash_abc",
            "computed_hash": "hash_abc_comp",
            "canon_export_version": "v0.0.1",
            "epochs": [{"epoch_id": "e1"}],
            "snapshots": [{"epoch_id": "e1", "balances": {"a": 1}}],
            "balances": {"a": 100.0, "b": 200.0},
        }
        
        export = export_canon_format_v0_1(canon_state)
        
        assert export["canon_hash"] == "hash_abc"
        assert export["computed_hash"] == "hash_abc_comp"
        assert export["meta"]["epoch_count"] == 1
        assert export["meta"]["snapshot_count"] == 1
        assert export["meta"]["balance_count"] == 2
        
        assert export["epochs"][0]["epoch_id"] == "e1"
        assert export["snapshots"][0]["balances"]["a"] == 1
        assert export["kpis"]["balance_count"] == 2

    def test_export_missing_required_keys(self):
        """Should raise ValueError if canon_hash or version is missing."""
        with pytest.raises(ValueError, match="missing required keys"):
            export_canon_format_v0_1({"canon_hash": "h1"}) # missing version
            
        with pytest.raises(ValueError, match="missing required keys"):
            export_canon_format_v0_1({"canon_export_version": "v1"}) # missing hash

    def test_export_invalid_types(self):
        """Should raise ValueError if core lists are wrong types."""
        base = {"canon_hash": "h", "canon_export_version": "v"}
        
        with pytest.raises(ValueError, match="must be a list"):
            export_canon_format_v0_1({**base, "epochs": "not_a_list"})
            
        with pytest.raises(ValueError, match="must be a list"):
            export_canon_format_v0_1({**base, "snapshots": {}})
            
        with pytest.raises(ValueError, match="must be a dict"):
            export_canon_format_v0_1({**base, "balances": []})

    def test_default_timestamp(self):
        """Verify timestamp is generated if not provided."""
        canon_state = {"canon_hash": "h", "canon_export_version": "v"}
        export = export_canon_format_v0_1(canon_state)
        
        # Simple ISO check (e.g. 2026-...)
        assert "T" in export["exported_at"]
        assert "+00:00" in export["exported_at"] or "Z" in export["exported_at"]

    def test_ignores_unknown_top_level_keys(self):
        """Extra keys in canon_state should NOT appear in top-level output (unless logic changes)."""
        canon_state = {
            "canon_hash": "h", 
            "canon_export_version": "v",
            "secret_key": "should_not_be_exported"
        }
        export = export_canon_format_v0_1(canon_state)
        
        assert "secret_key" not in export
        assert "secret_key" not in export["meta"]
