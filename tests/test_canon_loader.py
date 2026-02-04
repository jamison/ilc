
import pytest
import json
import tempfile
from pathlib import Path
from dataclasses import asdict

from ilc_core.ledger.backend import InMemoryLedgerBackend
from ilc_core.ledger.canon_export import export_canon_state_json
from ilc_core.ledger.canon_loader import (
    load_canon_state, load_canon_state_obj, verify_canon_hash, verify_canon_state, CanonVerificationError, CanonState
)

# Helper to generate a valid canon file
def create_valid_canon(tmpdir, filename="canon.json"):
    ledger = InMemoryLedgerBackend()
    ledger.balances = {"alice": 100.0}
    path = Path(tmpdir) / filename
    return export_canon_state_json(ledger, path)

def test_load_valid_canon():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "canon.json"
        
        # 1. Create valid export using actual export code
        ledger = InMemoryLedgerBackend()
        ledger.balances = {"alice": 100.0}
        export_canon_state_json(ledger, path)
        
        # 2. Load
        payload = load_canon_state(path)
        assert payload["balances"]["alice"] == 100.0
        
        # 3. Load Obj
        obj = load_canon_state_obj(path)
        assert isinstance(obj, CanonState)
        assert obj.balances["alice"] == 100.0
        assert obj.canon_hash != ""

def test_verify_tampered_payload():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "canon.json"
        create_valid_canon(tmpdir, "canon.json")
        
        # Read and modify
        with open(path) as f:
            data = json.load(f)
            
        # Tamper with balance
        data["balances"]["alice"] = 999.0
        
        # Overwrite file
        with open(path, "w") as f:
            json.dump(data, f)
            
        # Expect failure
        with pytest.raises(CanonVerificationError, match="Hash mismatch"):
            load_canon_state(path)

def test_verify_generated_at_ignored():
    """
    Test that changing 'generated_at' explicitly DOES NOT cause verification failure.
    (Because we exclude it from hash computation).
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "canon.json"
        create_valid_canon(tmpdir, "canon.json")
        
        with open(path) as f:
            data = json.load(f)
            
        # Modify generated_at
        data["generated_at"] = "2099-01-01T00:00:00+00:00"
        
        with open(path, "w") as f:
            json.dump(data, f)
            
        # Should SUCCEED
        payload = load_canon_state(path)
        assert payload["generated_at"] == "2099-01-01T00:00:00+00:00"

def test_verify_missing_hash():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "canon.json"
        create_valid_canon(tmpdir, "canon.json")
        
        with open(path) as f:
            data = json.load(f)
        
        del data["canon_hash"]
        
        with open(path, "w") as f:
            json.dump(data, f)
            
        with pytest.raises(CanonVerificationError, match="Missing required key: canon_hash"):
            load_canon_state(path)

def test_verify_bad_version():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "canon.json"
        create_valid_canon(tmpdir, "canon.json")
        
        with open(path) as f:
            data = json.load(f)
        
        data["canon_export_version"] = "v0.99"
        # Since hash includes version, this technically fails hash verify first unless we tamper hash too.
        # But load_canon_state checks version before hash? 
        # Actually in my implementation I checked version first. 
        # But changing version also changes the computed hash. 
        # So we might get HashMismatch OR Unsupported Version depending on implementation order.
        # Let's see code: Keys check -> Version check -> Verify Hash.
        
        with open(path, "w") as f:
            json.dump(data, f)
            
        with pytest.raises(CanonVerificationError, match="Unsupported version"):
            load_canon_state(path)

def test_schema_sanity():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "canon.json"
        
        # Missing key
        data = {
            "canon_export_version": "v0.1",
            "canon_hash": "deadbeef",
            "generated_at": "now",
            "stake_snapshots": {},
            "balances": {}
        }
        with open(path, "w") as f:
            json.dump(data, f)
            
        with pytest.raises(CanonVerificationError, match="Missing required key: epoch_records"):
            load_canon_state(path)
            
        # Wrong type (epoch_records should be dict)
        data["epoch_records"] = "invalid_string"
        with open(path, "w") as f:
            json.dump(data, f)
            
        with pytest.raises(CanonVerificationError, match="Invalid type for 'epoch_records': expected dict, got str"):
            load_canon_state(path)

def test_verify_canon_state_helper():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "canon.json"
        
        # 1. Valid
        create_valid_canon(tmpdir, "canon.json")
        report = verify_canon_state(path)
        assert report["ok"] is True
        assert report["canon_hash"] == report["computed_hash"]
        
        # 2. Tampered
        with open(path) as f:
            data = json.load(f)
        data["balances"]["alice"] = 0.0
        with open(path, "w") as f:
            json.dump(data, f)
            
        report = verify_canon_state(path)
        assert report["ok"] is False
        assert report["error"] == "Hash mismatch"
        assert report["canon_hash"] != report["computed_hash"]
        
        # 3. Missing File
        report = verify_canon_state(Path(tmpdir) / "nonexistent.json")
        assert report["ok"] is False
        assert "File not found" in report["error"]

def test_fixture_stability():
    """
    Ensure the static fixture validates correctly and deterministically.
    """
    fixture_path = Path("tests/fixtures/canon_state_v0.1.json")
    if not fixture_path.exists():
        pytest.skip("Fixture not found (run from project root)")
        
    # Should load without error
    payload = load_canon_state(fixture_path)
    assert payload["canon_export_version"] == "v0.1"
    
    # helper check
    report = verify_canon_state(fixture_path)
    assert report["ok"] is True
    
    # Explicit hash check
    # payload is the raw JSON which includes generated_at and canon_hash
    expected_hash = "36ba344f2741240329fb55d89c056db66a990a6c188bf978543ecd50d9e2a0e9"
    assert report["computed_hash"] == expected_hash

