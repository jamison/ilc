import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ilc_core.graph import EpistemicGraph
from ilc_core.consensus.engine import ConsensusEngine
from ilc_core.agent import EveAgent
from ilc_core.hardware import (
    load_hardware_archetypes,
    configure_agent_from_archetype,
)


def _make_agent():
    graph = EpistemicGraph()
    graph.load_genesis()
    from ilc_core.config import load_governance_config
    cfg = load_governance_config()
    engine = ConsensusEngine(graph, governance_config=cfg)
    agent = EveAgent("agent:test:arch", graph, engine)
    return graph, engine, agent


def test_load_hardware_archetypes_basic():
    archetypes = load_hardware_archetypes()
    # We expect at least cpu/gpu to exist in the MVP config.
    assert "cpu" in archetypes
    assert "gpu" in archetypes

    cpu = archetypes["cpu"]
    assert 0.0 <= cpu.base_potential <= 1.0
    assert cpu.stake_fraction_min <= cpu.stake_fraction_max


def test_configure_agent_from_archetype_applies_strategy():
    graph, engine, agent = _make_agent()
    archetypes = load_hardware_archetypes()
    gpu = archetypes["gpu"]

    configure_agent_from_archetype(agent, gpu)

    assert agent.trust_vector["potential"] == gpu.base_potential
    assert getattr(agent, "strategy_stake_fraction_min") == gpu.stake_fraction_min
    assert getattr(agent, "strategy_stake_fraction_max") == gpu.stake_fraction_max


def test_auto_mine_uses_archetype_strategy():
    graph, engine, agent = _make_agent()
    archetypes = load_hardware_archetypes()
    asic = archetypes["asic"]

    agent.wallet_balance = 10.0
    configure_agent_from_archetype(agent, asic)

    parent = "axiom:math:01"
    node = agent.auto_mine_claim("asic-claim", parent)

    assert node is not None
    assert node.id in graph.nodes
    # Agent should have spent some stake according to its strategy.
    assert agent.wallet_balance < 10.0
