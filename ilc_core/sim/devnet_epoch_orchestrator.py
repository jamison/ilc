from dataclasses import dataclass, asdict
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
from ilc_core.protocol.params import ProtocolParams
from ilc_core.protocol.event_log import EventLogger
from ilc_core.analysis.routed_tasks_export import (
    export_routed_tasks_to_csv,
    export_routed_tasks_to_json,
)
from ilc_core.network.node_load_export import (
    export_node_load_to_csv,
    export_node_load_to_json,
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
    # Phase 64A: Backlog Signal
    num_suggestions: int = 0
    num_executed: int = 0
    backlog_count: int = 0  # max(0, suggestions - executed)

def run_devnet_epoch(
    epoch_index: int,
    topology: DevnetTopology,
    namespace_snapshot: NamespaceHealthSnapshot,
    profiles: Dict[str, AgentProfile],
    *,
    export_dir: Optional[PathLike] = None,
    event_logger: Optional["EventLogger"] = None,
    protocol_params: Optional[ProtocolParams] = None,
) -> DevnetEpochResult:
    """
    High-level in-process devnet epoch simulation.

    Steps:
      1) Compute routing suggestions via suggest_tasks_for_agents.
      2) Materialize RoutedTaskRow objects.
      3) Convert to task-row dicts.
      4) Build agent->node mapping from profiles (using profile.node_id, fallback "unassigned").
      5) Compute per-node load metrics via compute_node_load_metrics.
      6) If export_dir is provided:
           - Export agent dossiers to CSV/JSON.
           - Export a unified epoch report to CSV/JSON.
           - Export routed tasks and node load metrics (New in Phase 59).
      7) If event_logger is provided:
           - Emit TASK_OUTCOME event for each routed task.
           - Emit EPOCH_SUMMARY event.

    Returns:
      DevnetEpochResult with in-memory task rows and node load metrics.
    """
    # 1) Compute routing suggestions based on current namespace health
    suggestions = suggest_tasks_for_agents(
        profiles=profiles,
        namespace_health=namespace_snapshot,
    )
    
    # Phase 64A: Capture total suggestions
    total_suggestions = sum(len(s_list) for s_list in suggestions.values())

    # 2) Materialize RoutedTaskRow objects
    routed_rows = materialize_routed_tasks_for_epoch(
        epoch_index=epoch_index,
        namespace_snapshot=namespace_snapshot,
        profiles=profiles,
        suggestions=suggestions,
        topology=topology,
        protocol_params=protocol_params,
    )
    
    # Phase 64A: Capture total executed
    total_executed = len(routed_rows)
    # Backlog = dropped (QA) or unrouted (if any logic dropped them before materialization)
    backlog_count = max(0, total_suggestions - total_executed)

    # 3) Convert to task-row dicts
    routed_task_dicts = routed_tasks_to_task_rows_dicts(routed_rows)

    # 4) Build agent->node mapping
    # This might duplicates logic inside materialize, but needed for compute_node_load_metrics
    agent_to_node: Dict[str, str] = {}
    for agent_id, profile in profiles.items():
        # Fallback "unassigned" if None? compute_node_load_metrics tolerates missing keys but let's be safe
        agent_to_node[agent_id] = profile.node_id if profile.node_id else "unassigned"

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
        
        # Routed Tasks & Node Load (Phase 59)
        export_routed_tasks_to_csv(routed_task_dicts, p / "routed_tasks.csv")
        export_routed_tasks_to_json(routed_task_dicts, p / "routed_tasks.json")
        
        export_node_load_to_csv(node_load, p / "node_load.csv")
        export_node_load_to_json(node_load, p / "node_load.json")

    # 7) Emit Events if Logger provided
    if event_logger:
        # Emit EPOCH_CONFIG (Phase 63C)
        params_dict = asdict(protocol_params) if protocol_params else {}
        event_logger.emit(
            kind="epoch_config", 
            payload={"epoch_index": epoch_index, "protocol_params": params_dict}
        )
        
        # Emit TASK_OUTCOMEs
        for task in routed_task_dicts:
            # Minimal payload
            payload = {
                "agent_id": task.get("agent_id"),
                "node_id": task.get("node_id"),
                "namespace_id": task.get("namespace_id"),
                # Use the epoch_index argument, not the task dict
                "epoch_index": epoch_index,
                "task_type": task.get("task_type"),
                "problem_space": task.get("problem_space"),
                "reward": task.get("reward"),
                "success": task.get("success"),
                # RoutedTaskRow.as_dict() uses key "regime"
                "regime": task.get("regime"),
            }
            event_logger.emit(kind="task_outcome", payload=payload)
        
        # Emit EPOCH_SUMMARY
        total_tasks = sum(m.get("num_tasks", 0) for m in node_load.values())
        total_reward = sum(m.get("total_reward", 0.0) for m in node_load.values())
        
        # Simple regime inference
        stress = namespace_snapshot.total_stress
        regime = "low" if stress < 0.3 else "high" if stress >= 1.0 else "medium"
        
        summary_payload = {
            "namespace_id": namespace_snapshot.namespace_id,
            "epoch_index": epoch_index,
            "total_tasks": total_tasks,
            "total_reward": total_reward,
            "stress_regime": regime,
            # Phase 64A: Add backlog info to event log
            "backlog_count": backlog_count,
            "num_suggestions": total_suggestions,
            "num_executed": total_executed,
        }
        event_logger.emit(kind="epoch_summary", payload=summary_payload)

    return DevnetEpochResult(
        epoch_index=epoch_index,
        namespace_id=namespace_snapshot.namespace_id,
        routed_task_rows=routed_task_dicts,
        node_load_metrics=node_load,
        num_suggestions=total_suggestions,
        num_executed=total_executed,
        backlog_count=backlog_count,
    )
