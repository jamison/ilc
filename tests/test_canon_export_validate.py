import pytest
import json
import tempfile
from pathlib import Path
from ilc_core.ledger.canon_export_validate import validate_canon_export_v0_1

class TestCanonExportValidate:
    
    def test_validate_valid_minimal(self):
        """Minimal valid export should pass."""
        doc = {
            "canon_export_format": "v0.1",
            "canon_hash": "h",
            "computed_hash": "h", # Optional but prevents warning
            "exported_at": "2026-02-05T00:00:00Z",
            "meta": {
                "canon_export_version": "v", 
                "epoch_count": 0, 
                "snapshot_count": 0, 
                "balance_count": 0
            },
            "epochs": [],
            "snapshots": [],
            "kpis": {} # Optional but prevents warning
        }
        res = validate_canon_export_v0_1(doc)
        assert res["ok"] is True
        assert res["errors"] == []
        assert "warnings" in res # Might still contain warning about empty epochs?

    def test_validate_missing_required(self):
        """Missing top-level keys must fail."""
        res = validate_canon_export_v0_1({})
        assert res["ok"] is False
        assert any("Missing required top-level key" in e for e in res["errors"])

    def test_validate_wrong_version(self):
        """Wrong version string must fail."""
        doc = {
            "canon_export_format": "v0.2",
            "canon_hash": "h", "exported_at": "t",
            "meta": {}, "epochs": [], "snapshots": []
        }
        res = validate_canon_export_v0_1(doc)
        assert res["ok"] is False
        assert any("Invalid format version" in e for e in res["errors"])

    def test_validate_bad_types(self):
        """Bad types for fields must fail."""
        doc = {
            "canon_export_format": "v0.1",
            "canon_hash": "h", "exported_at": "t",
            "meta": "not_a_dict",  # Error
            "epochs": "not_a_list", # Error
            "snapshots": []
        }
        res = validate_canon_export_v0_1(doc)
        assert res["ok"] is False
        assert any("meta" in e for e in res["errors"])
        assert any("epochs" in e for e in res["errors"])

    def test_validate_deep_snapshot_balances(self):
        """Balances values must be numbers."""
        doc = {
            "canon_export_format": "v0.1",
            "canon_hash": "h", "exported_at": "t",
            "meta": {"canon_export_version": "v", "epoch_count": 0, "snapshot_count": 0, "balance_count": 0},
            "epochs": [],
            "snapshots": [
                {
                    "epoch_id": "e1",
                    "balances": {
                        "alice": 100,
                        "bob": "not_a_number" # Error
                    }
                }
            ]
        }
        res = validate_canon_export_v0_1(doc)
        assert res["ok"] is False
        assert any("must be a number" in e for e in res["errors"])

    def test_validate_epoch_id_missing(self):
        """Epoch items must have epoch_id."""
        doc = {
            "canon_export_format": "v0.1",
            "canon_hash": "h", "exported_at": "t",
            "meta": {"canon_export_version": "v", "epoch_count": 0, "snapshot_count": 0, "balance_count": 0},
            "epochs": [{"no_id": True}], 
            "snapshots": []
        }
        res = validate_canon_export_v0_1(doc)
        assert res["ok"] is False
        assert any("missing 'epoch_id'" in e for e in res["errors"])

    def test_warnings(self):
        """Warnings should be reported but ok can still be True."""
        doc = {
            "canon_export_format": "v0.1",
            "canon_hash": "h", 
            "exported_at": "t",
            "meta": {"canon_export_version": "v", "epoch_count": 0, "snapshot_count": 0, "balance_count": 0},
            "epochs": [{"epoch_id": "e1"}], 
            "snapshots": [{"epoch_id": "e1"}]
            # kpis missing -> warning
            # computed_hash missing -> warning
        }
        res = validate_canon_export_v0_1(doc)
        assert res["ok"] is True
        assert len(res["warnings"]) >= 2
        assert any("Missing optional field 'computed_hash'" in w for w in res["warnings"])
