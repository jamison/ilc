from dataclasses import dataclass, field
from typing import List, Dict, Any, Mapping, Optional, Tuple
from pathlib import Path

from ilc_core.network.topology import (
    DevnetTopology, 
    build_star_topology, 
    NodeRole, 
    assign_agents_round_robin
)
from ilc_core.analysis.agent_profiles import (
    AgentProfile
)
from ilc_core.analysis.namespace_health import NamespaceHealthSnapshot
from ilc_core.analysis.task_routing_suggestions import ProblemSpace
from ilc_core.sim.devnet_multi_epoch import (
    run_devnet_multi_epoch, 
    DevnetMultiEpochResult
)
from ilc_core.sim.devnet_experiments import (
    summarize_multi_epoch_run, 
    DevnetExperimentSummary
)

@dataclass
class DevnetScenarioConfig:
    label: str
    stress_schedule: List[float]
    namespace_id: str = "ns_scenario"
    num_agents: int = 3
    topology_kind: str = "star"
    center_id: str = "orch"
    worker_ids: Optional[List[str]] = None

def scenario_from_dict(data: Mapping[str, Any]) -> DevnetScenarioConfig:
    """
    Build a DevnetScenarioConfig from a dictionary.
    
    Expected keys:
      - label (required)
      - stress_schedule (required)
      - namespace_id (optional)
      - num_agents (optional)
      - topology_kind (optional)
      - center_id (optional)
      - worker_ids (optional)
    """
    # Required fields
    label = data["label"]
    stress_schedule = data["stress_schedule"]
    
    # Optional fields with defaults handled by dataclass if not present
    # But we need to pass only what's in data or let dataclass default take over.
    # We can explicitly pluck them to allow override.
    
    kwargs = {
        "label": label,
        "stress_schedule": stress_schedule,
    }
    
    for key in ["namespace_id", "num_agents", "topology_kind", "center_id", "worker_ids"]:
        if key in data:
            kwargs[key] = data[key]
            
    return DevnetScenarioConfig(**kwargs)

def scenarios_from_config(config: Mapping[str, Any]) -> List[DevnetScenarioConfig]:
    """
    Parse a top-level config dict into a list of scenario objects.
    
    Global settings in `config` (outside `scenarios` list) are used as defaults
    if not specified in the individual scenario entry.
    """
    scenarios_list = []
    raw_scenarios = config.get("scenarios", [])
    
    # Defaults from top-level
    defaults = {}
    for key in ["namespace_id", "num_agents", "topology_kind", "center_id", "worker_ids"]:
        if key in config:
            defaults[key] = config[key]
            
    for item in raw_scenarios:
        # Merge defaults with item (item wins)
        # We construct a merged dict
        merged = defaults.copy()
        merged.update(item)
        
        scenarios_list.append(scenario_from_dict(merged))
        
    return scenarios_list

def build_topology_and_profiles(
    scenario: DevnetScenarioConfig,
) -> Tuple[DevnetTopology, Dict[str, AgentProfile]]:
    """
    Construct topology and agent profiles for a given scenario.
    MVP: always builds a star topology.
    """
    # 1. Topology
    center_id = scenario.center_id
    worker_ids = scenario.worker_ids
    
    if not worker_ids:
        # If not provided, derive minimally to support num_agents?
        # Or just fixed 2? The prompt suggested: "Else, derive at least 2 workers"
        # Let's make enough workers so agents can spread out, or just defaults.
        # Minimal default is 2 workers standard in our demos.
        worker_ids = ["w1", "w2"]
        
    topo = build_star_topology(center_id, worker_ids)
    
    # 2. Profiles
    # Assign num_agents to these nodes
    # Fixed: Use topology=topo instead of node_ids=worker_ids
    assignments = assign_agents_round_robin(
        agent_ids=[f"a{i}" for i in range(scenario.num_agents)],
        topology=topo
    )
    
    profiles = {}
    for agent_id, node_id in assignments.items():
        # Generic profile construction (MVP style)
        prof = AgentProfile(
            agent_id=agent_id,
            node_id=node_id,
            competency={
                "LOCAL_CONSISTENCY": {"score": 0.8, "experience": 10},
                "PLANNING": {"score": 0.5, "experience": 5},
            },
            stress_response={
                "resilience": 0.5,
                "plasticity": 0.1,
                "prefers_low": (agent_id == "a0") # Varied pref
            }
        )
        profiles[agent_id] = prof
        
    return topo, profiles

def build_snapshots_for_scenario(
    scenario: DevnetScenarioConfig,
) -> List[NamespaceHealthSnapshot]:
    """
    Create a sequence of snapshots based on the stress_schedule.
    """
    snapshots = []
    for idx, stress_val in enumerate(scenario.stress_schedule):
        # 1-based epoch index
        epoch_idx = idx + 1
        
        snap = NamespaceHealthSnapshot(
            namespace_id=scenario.namespace_id,
            total_stress=float(stress_val),
            epoch_index=epoch_idx,
            # Reasonable defaults
            cohesion_score=0.8,
            contradiction_overflow=0.0,
            validation_depth_error=0.0,
            mean_abs_influence=0.5,
            # Phase 60 Fix: Add missing required fields
            crosslink_deficit=0.0,
            support_ratio=0.9,
            controversy_ratio=0.1
        )
        snapshots.append(snap)
        
    return snapshots

def run_scenario(
    scenario: DevnetScenarioConfig,
) -> DevnetExperimentSummary:
    """
    Execute a single scenario end-to-end.
    """
    topo, profiles = build_topology_and_profiles(scenario)
    snapshots = build_snapshots_for_scenario(scenario)
    
    # Run multi-epoch (no export root for now, keeping it in-memory unless we add config for it)
    # The prompt doesn't explicitly ask to expose export_root in config, devnet_config_runner_demo might use it though?
    # "Run run_devnet_multi_epoch(topology, snapshots, profiles, export_root=None)"
    multi_result = run_devnet_multi_epoch(
        topology=topo,
        snapshots=snapshots,
        profiles=profiles,
        export_root=None
    )
    
    # Summarize
    summary = summarize_multi_epoch_run(
        label=scenario.label,
        multi=multi_result
    )
    
    return summary

def run_scenarios_from_config(
    config: Mapping[str, Any],
) -> List[DevnetExperimentSummary]:
    """
    Parse and run all scenarios in the config.
    """
    scenarios = scenarios_from_config(config)
    results = []
    
    for scen in scenarios:
        summary = run_scenario(scen)
        results.append(summary)
        
    return results
