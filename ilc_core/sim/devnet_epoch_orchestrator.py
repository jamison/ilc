from dataclasses import dataclass, asdict
from datetime import datetime, timezone
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

def _compute_suggestions(
    profiles: Dict[str, AgentProfile],
    namespace_snapshot: NamespaceHealthSnapshot
) -> Dict[str, Any]:
    return suggest_tasks_for_agents(
        profiles=profiles,
        namespace_health=namespace_snapshot,
    )

def _materialize_tasks(
    epoch_index: int,
    topology: DevnetTopology,
    namespace_snapshot: NamespaceHealthSnapshot,
    profiles: Dict[str, AgentProfile],
    suggestions: Dict[str, Any],
    protocol_params: Optional[ProtocolParams]
) -> List[Any]:
    return materialize_routed_tasks_for_epoch(
        epoch_index=epoch_index,
        namespace_snapshot=namespace_snapshot,
        profiles=profiles,
        suggestions=suggestions,
        topology=topology,
        protocol_params=protocol_params,
    )

def _compute_load_metrics(
    routed_task_dicts: List[Dict[str, Any]],
    profiles: Dict[str, AgentProfile]
) -> Dict[str, Dict[str, float]]:
    # Build agent->node mapping
    agent_to_node: Dict[str, str] = {}
    for agent_id, profile in profiles.items():
        agent_to_node[agent_id] = profile.node_id if profile.node_id else "unassigned"

    return compute_node_load_metrics(
        task_rows=routed_task_dicts,
        agent_to_node=agent_to_node,
    )

def _export_epoch_artifacts(
    export_dir: PathLike,
    epoch_index: int,
    namespace_snapshot: NamespaceHealthSnapshot,
    profiles: Dict[str, AgentProfile],
    routed_task_dicts: List[Dict[str, Any]],
    node_load: Dict[str, Dict[str, float]]
) -> None:
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
    
    # Routed Tasks & Node Load
    export_routed_tasks_to_csv(routed_task_dicts, p / "routed_tasks.csv")
    export_routed_tasks_to_json(routed_task_dicts, p / "routed_tasks.json")
    
    export_node_load_to_csv(node_load, p / "node_load.csv")
    export_node_load_to_json(node_load, p / "node_load.json")

def _emit_epoch_events(
    event_logger: "EventLogger",
    epoch_index: int,
    namespace_snapshot: NamespaceHealthSnapshot,
    routed_task_dicts: List[Dict[str, Any]],
    node_load: Dict[str, Dict[str, float]],
    protocol_params: Optional[ProtocolParams],
    total_suggestions: int,
    total_executed: int,
    backlog_count: int
) -> None:
    # Emit EPOCH_CONFIG
    params_dict = asdict(protocol_params) if protocol_params else {}
    event_logger.emit(
        kind="epoch_config", 
        payload={
            "epoch_index": epoch_index,
            "benchmark_suite_id": "devnet_synthetic_v0.1",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "namespace_id": namespace_snapshot.namespace_id,
            "protocol_params": params_dict,
        }
    )
    
    # Emit TASK_OUTCOMEs
    for task in routed_task_dicts:
        payload = {
            "agent_id": task.get("agent_id"),
            "node_id": task.get("node_id"),
            "namespace_id": task.get("namespace_id"),
            "epoch_index": epoch_index,
            "task_type": task.get("task_type"),
            "problem_space": task.get("problem_space"),
            "reward": task.get("reward"),
            "success": task.get("success"),
            "regime": task.get("regime"),
        }
        event_logger.emit(kind="task_outcome", payload=payload)
    
    # Emit EPOCH_SUMMARY
    total_tasks = int(sum(m.get("num_tasks", 0) for m in node_load.values()))
    total_reward = sum(m.get("total_reward", 0.0) for m in node_load.values())
    
    stress = namespace_snapshot.total_stress
    regime = "low" if stress < 0.3 else "high" if stress >= 1.0 else "medium"
    
    summary_payload = {
        "namespace_id": namespace_snapshot.namespace_id,
        "epoch_index": epoch_index,
        "total_tasks": total_tasks,
        "total_reward": total_reward,
        "stress_regime": regime,
        "backlog_count": backlog_count,
        "num_suggestions": total_suggestions,
        "num_executed": total_executed,
    }
    event_logger.emit(kind="epoch_summary", payload=summary_payload)


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
      4) Build agent->node mapping and compute load metrics.
      5) If export_dir is provided, export artifacts.
      6) If event_logger is provided, emit events.

    Returns:
      DevnetEpochResult with in-memory task rows and node load metrics.
    """
    # 1) Compute routing suggestions
    suggestions = _compute_suggestions(profiles, namespace_snapshot)
    
    total_suggestions = sum(len(s_list) for s_list in suggestions.values())

    # 2) Materialize RoutedTaskRow objects
    routed_rows = _materialize_tasks(
        epoch_index, topology, namespace_snapshot, profiles, suggestions, protocol_params
    )
    
    total_executed = len(routed_rows)
    backlog_count = max(0, total_suggestions - total_executed)

    # 3) Convert to task-row dicts
    routed_task_dicts = routed_tasks_to_task_rows_dicts(routed_rows)

    # 4) Compute per-node load metrics
    node_load = _compute_load_metrics(routed_task_dicts, profiles)

    # 5) Export if requested
    if export_dir:
        _export_epoch_artifacts(
            export_dir, epoch_index, namespace_snapshot, profiles, 
            routed_task_dicts, node_load
        )

    # 6) Emit Events if Logger provided
    if event_logger:
        _emit_epoch_events(
            event_logger, epoch_index, namespace_snapshot, routed_task_dicts, 
            node_load, protocol_params, total_suggestions, total_executed, backlog_count
        )

    return DevnetEpochResult(
        epoch_index=epoch_index,
        namespace_id=namespace_snapshot.namespace_id,
        routed_task_rows=routed_task_dicts,
        node_load_metrics=node_load,
        num_suggestions=total_suggestions,
        num_executed=total_executed,
        backlog_count=backlog_count,
    )
