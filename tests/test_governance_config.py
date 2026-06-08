import sys
import os
from decimal import Decimal

import pytest
from ilc_core.config import load_governance_config
from ilc_core.consensus.governance import Governance
from ilc_core.consensus.engine import ConsensusEngine
from ilc_core.graph import EpistemicGraph

def test_load_governance_config():
    """
    Verify that the config loader works and returns expected keys.
    """
    cfg = load_governance_config()
    assert isinstance(cfg, dict)
    
    # Check for key sections
    assert "ecu" in cfg
    assert "base_costs" in cfg["ecu"]
    assert "backlog_hotspot_pricing" in cfg
    assert "hardware" in cfg
    
    # Check specific values from MVP config
    assert cfg["ecu"]["base_costs"]["claim.submit"] == 0.05
    assert cfg["hardware"]["genesis_median_potential"] == 0.1

def test_governance_init_with_config():
    """
    Verify that Governance initializes correctly with a config dict.
    """
    cfg = load_governance_config()
    gov = Governance(cfg)
    
    # Verify values propagated
    assert gov.ecu_base_costs["claim.submit"] == Decimal("0.05")
    assert gov.genesis_median_potential == Decimal("0.1")
    assert gov.backlog_enabled is True
    assert gov.price_max == Decimal("1.5")

def test_consensus_engine_default_config():
    """
    Verify that ConsensusEngine loads the default config if none is provided.
    """
    graph = EpistemicGraph()
    engine = ConsensusEngine(graph)
    
    # Should have loaded the default config
    assert engine.governance.ecu_base_costs["claim.submit"] == Decimal("0.05")
    assert engine.governance.genesis_median_potential == Decimal("0.1")

def test_consensus_engine_custom_config():
    """
    Verify that ConsensusEngine accepts a custom config.
    """
    custom_cfg = {
        "ecu": {
            "base_costs": {
                "claim.submit": 0.99
            }
        },
        "hardware": {
            "genesis_median_potential": 0.5
        }
    }
    
    graph = EpistemicGraph()
    engine = ConsensusEngine(graph, governance_config=custom_cfg)
    
    assert engine.governance.ecu_base_costs["claim.submit"] == Decimal("0.99")
    assert engine.governance.genesis_median_potential == Decimal("0.5")
