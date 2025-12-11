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

# Synthetic defaults for devnet scenario simulations.
# These are not normative protocol thresholds; they just give
# a stable, "healthy-ish" namespace for stress-sweep experiments.
DEFAULT_COHESION_SCORE = 0.8
DEFAULT_CROSSLINK_DEFICIT = 0.0
DEFAULT_SUPPORT_RATIO = 0.9
DEFAULT_CONTROVERSY_RATIO = 0.1
DEFAULT_VALIDATION_DEPTH_ERROR = 0.0
DEFAULT_MEAN_ABS_INFLUENCE = 0.5

@dataclass
class DevnetScenarioConfig:
    """
    Configuration for a single devnet scenario.

    Fields:
      - label: Human-readable label for the scenario (used in summaries/CSV).
      - stress_schedule: List of total_stress values, one per epoch.
      - namespace_id: Namespace identifier used in NamespaceHealthSnapshot
        (defaults to "ns_scenario" unless overridden or inherited from config).
      - num_agents: Number of synthetic agents to create for this scenario.
      - topology_kind: Topology type ("star" for now; other values are not yet supported).
      - center_id: Node ID for the orchestration/center node in a star topology.
      - worker_ids: Optional explicit worker node IDs; if None or empty, a minimal
        default like ["w1", "w2"] is used.
    """
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

    MVP: only supports a star topology (center_id + worker_ids).
    """
    # 1. Topology
    if scenario.topology_kind != "star":
        # MVP limitation: we only support star topology in Phase 60.
        # Raise a clear error so configs don't silently do the wrong thing.
        raise ValueError(
            f"Unsupported topology_kind={scenario.topology_kind!r}; "
            f"only 'star' is supported in this MVP."
        )

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
                "by_space": {
                    "LOCAL_CONSISTENCY": {"success_rate": 0.8, "tasks": 10},
                    "PLANNING": {"success_rate": 0.5, "tasks": 5},
                }
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
            cohesion_score=DEFAULT_COHESION_SCORE,
            contradiction_overflow=0.0,
            validation_depth_error=DEFAULT_VALIDATION_DEPTH_ERROR,
            mean_abs_influence=DEFAULT_MEAN_ABS_INFLUENCE,
            # Phase 60 Fix: Add missing required fields
            crosslink_deficit=DEFAULT_CROSSLINK_DEFICIT,
            support_ratio=DEFAULT_SUPPORT_RATIO,
            controversy_ratio=DEFAULT_CONTROVERSY_RATIO
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
    Parse and run all scenarios in a config dictionary.

    Expected config shape (MVP):

      {
        "namespace_id": "ns_sweep_auto",       # optional global default
        "num_agents": 3,                       # optional global default
        "topology_kind": "star",               # optional, only "star" supported
        "center_id": "orch",                   # optional, default center node
        "worker_ids": ["w1", "w2", ...],       # optional; if omitted, defaults apply
        "scenarios": [
          {"label": "demo_low", "stress_schedule": [0.1, 0.2, 0.3]},
          {"label": "demo_high", "stress_schedule": [0.8, 1.2, 1.5], "num_agents": 10},
        ]
      }

    Top-level keys act as defaults and can be overridden per scenario.
    """
    scenarios = scenarios_from_config(config)
    results = []
    
    for scen in scenarios:
        summary = run_scenario(scen)
        results.append(summary)
        
    return results
