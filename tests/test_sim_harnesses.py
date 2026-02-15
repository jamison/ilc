"""
Tests for Phase 64C Harness Parsing & Normalization
"""
import pytest
import logging
from ilc_core.sim.harness_econ_scenarios import default_apply_econ
from ilc_core.protocol.params import ProtocolParams

def test_default_apply_econ_normalizes_legacy_keys(caplog):
    # Ensure warnings are captured
    with caplog.at_level(logging.WARNING):
        # 1. Pass legacy keys
        overrides = {
            "ce_enabled": "false",
            "toll": "0.1",
            "kappa": 0.2,
            "qa": "0.9",
        }
        
        # 2. Call handler
        default_apply_econ(overrides)
        
        # 3. Assert no unknown-key warning token for normalized keys.
        for record in caplog.records:
            assert "econ_override_unknown_key" not in record.message
            
        # 4. (Optional) Verify they would have warned if not normalized?
        # A bad key should still warn
        default_apply_econ({"bad_key_xyz": 123})
        found = False
        for record in caplog.records:
            if "econ_override_unknown_key key=bad_key_xyz" in record.message:
                found = True
        assert found
