from dataclasses import dataclass
from typing import Dict, Any, List, Optional
from os import PathLike
from pathlib import Path

from ilc_core.network.topology import DevnetTopology, compute_node_load_metrics
from ilc_core.analysis.namespace_health import NamespaceHealthSnapshot
from ilc_core.analysis.agent_profiles import AgentProfile
from ilc_core.analysis.task_routing_suggestions import suggest_tasks_for_agents
from ilc_core.analysis.routed_tasks import (
    materialize_routed_tasks_for_epoch,
    routed_tasks_to_task_rows_dicts,
)
from ilc_core.analysis.agent_dossier_export import (
    export_agent_dossiers_to_csv,
    export_agent_dossiers_to_json,
)
from ilc_core.analysis.epoch_report_export import (
    export_epoch_report_to_csv,
    export_epoch_report_to_json,
)

@dataclass
class DevnetEpochResult:
    epoch_index: int
    namespace_id: str
    routed_task_rows: List[Dict[str, Any]]
    node_load_metrics: Dict[str, Dict[str, float]]

def run_devnet_epoch(
    epoch_index: int,
    topology: DevnetTopology,
    namespace_snapshot: NamespaceHealthSnapshot,
    profiles: Dict[str, AgentProfile],
    *,
    export_dir: Optional[PathLike] = None,
) -> DevnetEpochResult:
    """
    High-level in-process devnet epoch simulation.

    Steps:
      1) Compute routing suggestions via suggest_tasks_for_agents.
      2) Materialize RoutedTaskRow objects.
      3) Convert to task-row dicts.
      4) Build agent->node mapping from profiles (using profile.node_id, fallback "unknown").
      5) Compute per-node load metrics via compute_node_load_metrics.
      6) If export_dir is provided:
           - Export agent dossiers to CSV/JSON.
           - Export a unified epoch report to CSV/JSON.

    Returns:
      DevnetEpochResult with in-memory task rows and node load metrics.
    """
    # 1) Compute routing suggestions
    # We pass explicit None for tasks_history (not used in current MVP heuristic default)
    # or empty dict if required. suggest_tasks_for_agents sig:
    # (profiles, namespace_health, *, max_suggestions_per_agent=3)
    suggestions = suggest_tasks_for_agents(
        profiles=profiles,
        namespace_health=namespace_snapshot,
    )

    # 2) Materialize RoutedTaskRow objects
    routed_rows = materialize_routed_tasks_for_epoch(
        epoch_index=epoch_index,
        namespace_snapshot=namespace_snapshot,
        profiles=profiles,
        suggestions=suggestions,
        topology=topology,
    )

    # 3) Convert to task-row dicts
    routed_task_dicts = routed_tasks_to_task_rows_dicts(routed_rows)

    # 4) Build agent->node mapping
    # This might duplicates logic inside materialize, but needed for compute_node_load_metrics
    agent_to_node: Dict[str, str] = {}
    for agent_id, profile in profiles.items():
        # Fallback "unknown" if None? compute_node_load_metrics tolerates missing keys but let's be safe
        agent_to_node[agent_id] = profile.node_id if profile.node_id else "unknown"

    # 5) Compute per-node load metrics
    node_load = compute_node_load_metrics(
        task_rows=routed_task_dicts,
        agent_to_node=agent_to_node,
    )

    # 6) Export if requested
    if export_dir:
        p = Path(export_dir)
        p.mkdir(parents=True, exist_ok=True)
        
        # Agent Dossiers
        export_agent_dossiers_to_csv(profiles, p / "agent_dossiers.csv")
        export_agent_dossiers_to_json(profiles, p / "agent_dossiers.json")

        # Epoch Report
        export_epoch_report_to_csv(
            epoch_index, namespace_snapshot, profiles, p / "epoch_report.csv"
        )
        export_epoch_report_to_json(
            epoch_index, namespace_snapshot, profiles, p / "epoch_report.json"
        )

    return DevnetEpochResult(
        epoch_index=epoch_index,
        namespace_id=namespace_snapshot.namespace_id,
        routed_task_rows=routed_task_dicts,
        node_load_metrics=node_load,
    )
